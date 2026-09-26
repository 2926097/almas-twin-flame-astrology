from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from importlib.resources import files
from typing import Any, Mapping, Sequence


POLICY_RESOURCE = "data/blinding-leakage-policy.json"
POLICY_ID = "ALMAS_BLINDING_LEAKAGE_V1"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@lru_cache(maxsize=1)
def load_blinding_leakage_policy() -> dict[str, Any]:
    resource = files("almas_tfa").joinpath(POLICY_RESOURCE)
    return json.loads(resource.read_text(encoding="utf-8"))


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _iter_mapping_keys(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text
            yield from _iter_mapping_keys(nested, path)
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            yield from _iter_mapping_keys(nested, path)


def forbidden_structural_field_paths(
    payload: Any,
    *,
    policy: Mapping[str, Any] | None = None,
) -> list[str]:
    policy = policy or load_blinding_leakage_policy()
    forbidden = {
        str(key).strip().lower()
        for key in policy.get("forbidden_structural_keys", [])
    }
    return [
        path
        for path, key in _iter_mapping_keys(payload)
        if key.strip().lower() in forbidden
    ]


def assert_no_forbidden_structural_fields(
    payload: Any,
    *,
    policy: Mapping[str, Any] | None = None,
) -> None:
    hits = forbidden_structural_field_paths(payload, policy=policy)
    if hits:
        raise ValueError(
            "BLINDING_LEAKAGE: la entrada estructural contiene campos prohibidos: "
            + ", ".join(hits)
        )


def assert_late_reveal_invariance(
    pre_reveal_structural_output: Any,
    post_reveal_structural_output: Any,
) -> str:
    before = canonical_sha256(pre_reveal_structural_output)
    after = canonical_sha256(post_reveal_structural_output)
    if before != after:
        raise ValueError(
            "NARRATIVE_LEAKAGE: la salida estructural cambió tras el revelado documental."
        )
    return before


def _nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item) for item in value)
    )


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


def _zero_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value == 0


def evaluate_blinding_audit(
    audit: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or load_blinding_leakage_policy()

    if audit.get("policy_id") != policy.get("policy_id"):
        raise ValueError("blinding_audit: policy_id no coincide con la política canónica.")

    for key in ("audit_refs", "structural_input_refs"):
        if not _nonempty_string_list(audit.get(key)):
            raise ValueError(f"blinding_audit: {key} no vacío es obligatorio.")

    for key in (
        "structural_input_sha256",
        "pre_reveal_output_sha256",
        "post_reveal_structural_output_sha256",
    ):
        if not _valid_sha256(audit.get(key)):
            raise ValueError(f"blinding_audit: {key} debe ser SHA-256 hexadecimal.")

    for key in policy.get("required_true_flags", []):
        if audit.get(key) is not True:
            raise ValueError(f"blinding_audit: {key}=true es obligatorio.")

    for key in policy.get("required_zero_counts", []):
        if not _zero_int(audit.get(key)):
            raise ValueError(f"blinding_audit: {key} debe ser exactamente 0.")

    before = audit.get("pre_reveal_output_sha256")
    after = audit.get("post_reveal_structural_output_sha256")
    if before != after:
        raise ValueError(
            "blinding_audit: fingerprint estructural pre/post revelado no coincide."
        )

    identity_visibility = audit.get("identity_visibility")
    if identity_visibility not in {"HIDDEN", "PSEUDONYMIZED", "UNAVOIDABLE_PUBLIC"}:
        raise ValueError("blinding_audit: identity_visibility inválido.")

    risk_refs = audit.get("identity_risk_refs")
    if not isinstance(risk_refs, list) or not all(
        isinstance(item, str) and bool(item) for item in risk_refs
    ):
        raise ValueError("blinding_audit: identity_risk_refs inválido.")
    if identity_visibility == "UNAVOIDABLE_PUBLIC" and not risk_refs:
        raise ValueError(
            "blinding_audit: identidad pública inevitable requiere identity_risk_refs."
        )

    return {
        "policy_id": policy.get("policy_id"),
        "structural_input_sha256": audit.get("structural_input_sha256"),
        "structural_output_sha256": before,
        "identity_visibility": identity_visibility,
        "late_reveal_invariant": True,
        "label_leakage_count": 0,
        "narrative_leakage_count": 0,
        "case_fitting_count": 0,
    }


def has_complete_blinding_audit(
    audit: Any,
    *,
    policy: Mapping[str, Any] | None = None,
) -> bool:
    if not isinstance(audit, Mapping):
        return False
    try:
        evaluate_blinding_audit(audit, policy=policy)
    except (TypeError, ValueError):
        return False
    return True
