from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Any, Mapping


POLICY_RESOURCE = "data/public-data-isolation-policy.json"


@lru_cache(maxsize=1)
def load_public_data_isolation_policy() -> dict[str, Any]:
    resource = files("almas_tfa").joinpath(POLICY_RESOURCE)
    return json.loads(resource.read_text(encoding="utf-8"))


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and bool(item) for item in value
    )


def _iter_keys(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text
            yield from _iter_keys(nested, path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            yield from _iter_keys(nested, path)


def forbidden_public_payload_paths(
    payload: Any,
    *,
    policy: Mapping[str, Any] | None = None,
) -> list[str]:
    policy = policy or load_public_data_isolation_policy()
    forbidden = {
        str(item).strip().lower()
        for item in policy.get("forbidden_public_payload_keys", [])
    }
    return [
        path
        for path, key in _iter_keys(payload)
        if key.strip().lower() in forbidden
    ]


def validate_public_artifact_metadata(
    artifact: Mapping[str, Any],
    *,
    allowed_classifications: set[str] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> None:
    policy = policy or load_public_data_isolation_policy()
    classification = artifact.get("classification")
    allowed_global = set(policy.get("allowed_public_classifications", []))
    forbidden = set(policy.get("forbidden_public_classifications", []))

    if classification in forbidden:
        raise ValueError(
            f"PRIVACY_BREACH: clasificación privada prohibida: {classification}"
        )
    if classification not in allowed_global:
        raise ValueError(
            f"Clasificación pública desconocida/no permitida: {classification}"
        )
    if (
        allowed_classifications is not None
        and classification not in allowed_classifications
    ):
        raise ValueError(
            f"Clasificación {classification} no permitida en este scope."
        )

    for key in (
        "contains_real_person_data",
        "contains_nonpublic_material",
        "derived_from_private_case",
        "reversible_from_private_case",
        "independently_verifiable",
    ):
        if not isinstance(artifact.get(key), bool):
            raise ValueError(f"Metadato de privacidad inválido: {key}")

    refs = artifact.get("public_source_refs")
    if not _string_list(refs):
        raise ValueError("public_source_refs debe ser una lista de strings.")

    if classification == "SYNTHETIC":
        for key in (
            "contains_real_person_data",
            "contains_nonpublic_material",
            "derived_from_private_case",
            "reversible_from_private_case",
        ):
            if artifact.get(key) is not False:
                raise ValueError(
                    f"PRIVACY_BREACH: fixture sintético viola {key}=false."
                )
        if refs:
            raise ValueError(
                "Un artefacto SYNTHETIC no debe depender de fuentes de caso real."
            )

    if classification == "PUBLIC_VERIFIABLE":
        for key in (
            "contains_nonpublic_material",
            "derived_from_private_case",
            "reversible_from_private_case",
        ):
            if artifact.get(key) is not False:
                raise ValueError(
                    f"PRIVACY_BREACH: caso público viola {key}=false."
                )
        if artifact.get("independently_verifiable") is not True:
            raise ValueError(
                "PUBLIC_VERIFIABLE exige independently_verifiable=true."
            )
        if not refs:
            raise ValueError(
                "PUBLIC_VERIFIABLE exige public_source_refs no vacío."
            )

    if classification == "PUBLIC_METADATA_ONLY":
        if artifact.get("contains_nonpublic_material") is not False:
            raise ValueError(
                "PUBLIC_METADATA_ONLY no puede contener material no público."
            )
        if artifact.get("derived_from_private_case") is not False:
            raise ValueError(
                "PUBLIC_METADATA_ONLY no puede derivar datos identificables del caso."
            )
        if artifact.get("reversible_from_private_case") is not False:
            raise ValueError(
                "PUBLIC_METADATA_ONLY no puede ser reversible al caso privado."
            )


def validate_public_artifact_payload(
    payload: Any,
    *,
    policy: Mapping[str, Any] | None = None,
) -> None:
    hits = forbidden_public_payload_paths(payload, policy=policy)
    if hits:
        raise ValueError(
            "PRIVACY_BREACH: payload público contiene claves privadas prohibidas: "
            + ", ".join(hits)
        )


def validate_public_manifest(
    manifest: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> None:
    policy = policy or load_public_data_isolation_policy()
    if manifest.get("policy_id") != policy.get("policy_id"):
        raise ValueError("Manifest no usa la política pública canónica.")

    scope = manifest.get("scope")
    scope_policy = policy.get("governed_scopes", {}).get(scope)
    if not isinstance(scope_policy, Mapping):
        raise ValueError(f"Scope público desconocido: {scope}")

    if manifest.get("root") != scope_policy.get("root"):
        raise ValueError("Root del manifiesto no coincide con la política.")

    allowed = set(scope_policy.get("allowed_classifications", []))
    if set(manifest.get("allowed_classifications", [])) != allowed:
        raise ValueError("Clasificaciones del manifiesto divergen de la política.")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("artifacts debe ser una lista.")

    seen: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            raise ValueError("Artefacto de manifiesto inválido.")
        path = artifact.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError("Artefacto sin path.")
        if path in seen:
            raise ValueError(f"Path duplicado en manifiesto: {path}")
        seen.add(path)
        root = str(scope_policy.get("root"))
        if not path.startswith(root + "/"):
            raise ValueError(
                f"Artefacto fuera del scope {root}: {path}"
            )
        validate_public_artifact_metadata(
            artifact,
            allowed_classifications=allowed,
            policy=policy,
        )


def audit_public_repository(
    root: str | Path,
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or load_public_data_isolation_policy()
    root_path = Path(root)

    for forbidden in policy.get("forbidden_repository_paths", []):
        if (root_path / str(forbidden)).exists():
            raise ValueError(
                f"PRIVACY_BREACH: ruta privada presente en repositorio: {forbidden}"
            )

    audited: dict[str, Any] = {"policy_id": policy.get("policy_id"), "scopes": {}}

    for scope, scope_policy in policy.get("governed_scopes", {}).items():
        manifest_path = root_path / str(scope_policy["manifest"])
        if not manifest_path.is_file():
            raise ValueError(
                f"Falta manifiesto público para scope {scope}: {manifest_path}"
            )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        validate_public_manifest(manifest, policy=policy)

        scope_root = root_path / str(scope_policy["root"])
        actual = set()
        if scope_root.exists():
            for path in scope_root.rglob("*.json"):
                rel = path.relative_to(root_path).as_posix()
                if rel == str(scope_policy["manifest"]):
                    continue
                actual.add(rel)

        declared = {
            str(item["path"])
            for item in manifest.get("artifacts", [])
        }
        if actual != declared:
            missing = sorted(actual - declared)
            stale = sorted(declared - actual)
            raise ValueError(
                f"Manifest coverage mismatch en {scope}; "
                f"no_registrados={missing}; inexistentes={stale}"
            )

        by_path = {
            str(item["path"]): item
            for item in manifest.get("artifacts", [])
        }
        for rel in sorted(actual):
            payload = json.loads(
                (root_path / rel).read_text(encoding="utf-8")
            )
            validate_public_artifact_payload(payload, policy=policy)
            validate_public_artifact_metadata(
                by_path[rel],
                allowed_classifications=set(
                    scope_policy.get("allowed_classifications", [])
                ),
                policy=policy,
            )

        audited["scopes"][scope] = {
            "artifact_count": len(actual),
            "manifest": str(scope_policy["manifest"]),
            "status": "PASS",
        }

    return audited
