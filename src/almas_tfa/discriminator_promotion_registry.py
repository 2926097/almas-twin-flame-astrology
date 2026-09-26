from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any, Mapping, Sequence

from almas_tfa.discriminant_validation import has_complete_discriminant_validation
from almas_tfa.blinding_leakage import has_complete_blinding_audit


REGISTRY_RESOURCE = "data/discriminator-promotion-registry.json"
VALIDATED_STATUS = "VALIDATED_DISCRIMINATOR"

ASTROLOGY_VALIDATION_KEYS = (
    "non_astrological_criterion_refs",
    "astrology_ablation_refs",
    "matched_control_refs",
    "dependency_audit_refs",
    "out_of_sample_refs",
    "astrology_specific_replication_refs",
)


@lru_cache(maxsize=1)
def load_discriminator_promotion_registry() -> dict[str, Any]:
    resource = files("almas_tfa").joinpath(REGISTRY_RESOURCE)
    return json.loads(resource.read_text(encoding="utf-8"))


def _record_map(registry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    records = registry.get("records")
    if not isinstance(records, list):
        raise ValueError("Registro de promoción inválido: records debe ser una lista.")

    result: dict[str, Mapping[str, Any]] = {}
    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("Registro de promoción inválido: record no es objeto.")
        discriminator_id = record.get("discriminator_id")
        if not isinstance(discriminator_id, str) or not discriminator_id:
            raise ValueError("Registro de promoción inválido: discriminator_id ausente.")
        if discriminator_id in result:
            raise ValueError(
                f"Registro de promoción inválido: discriminator_id duplicado {discriminator_id}."
            )
        result[discriminator_id] = record
    return result


def _nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item) for item in value)
    )


def _record_has_complete_astrology_validation(
    record: Mapping[str, Any],
) -> bool:
    if record.get("uses_astrology") is not True:
        return True

    validation = record.get("astrology_validation")
    if not isinstance(validation, Mapping):
        return False

    for key in ASTROLOGY_VALIDATION_KEYS:
        if not _nonempty_string_list(validation.get(key)):
            return False

    if validation.get("single_feature_prohibition_acknowledged") is not True:
        return False
    if validation.get("null_rarity_not_ontological") is not True:
        return False
    if validation.get("temporal_activation_not_origin_proof") is not True:
        return False

    return True


def _record_has_complete_l3_evidence(record: Mapping[str, Any]) -> bool:
    if record.get("current_status") != VALIDATED_STATUS:
        return False
    if record.get("l3_authorized") is not True:
        return False
    if not isinstance(record.get("promotion_ref"), str) or not record["promotion_ref"]:
        return False
    if not isinstance(record.get("promoted_at"), str) or not record["promoted_at"]:
        return False
    if not isinstance(record.get("root_key_prefix"), str) or not record["root_key_prefix"]:
        return False

    pairs = record.get("validated_pairs")
    if not isinstance(pairs, list) or not pairs:
        return False
    if not all(
        isinstance(pair, list)
        and len(pair) == 2
        and all(isinstance(model, str) and model for model in pair)
        and pair[0] != pair[1]
        for pair in pairs
    ):
        return False

    frozen = record.get("frozen")
    if not isinstance(frozen, Mapping):
        return False
    for key in ("almas_version", "commit_sha", "rule_ref"):
        if not isinstance(frozen.get(key), str) or not frozen[key]:
            return False
    if not _nonempty_string_list(frozen.get("schema_refs")):
        return False

    discriminant_validation = record.get("discriminant_validation")
    if not has_complete_discriminant_validation(
        discriminant_validation,
        validated_pairs=pairs,
    ):
        return False

    blinding_audit = record.get("blinding_audit")
    if not has_complete_blinding_audit(blinding_audit):
        return False

    evidence = record.get("validation_evidence")
    if not isinstance(evidence, Mapping):
        return False
    for key in (
        "preregistration_refs",
        "independent_replication_refs",
        "external_holdout_refs",
        "negative_control_refs",
        "leakage_audit_refs",
    ):
        if not _nonempty_string_list(evidence.get(key)):
            return False

    if not _record_has_complete_astrology_validation(record):
        return False

    return True


def has_complete_l3_record(record: Mapping[str, Any]) -> bool:
    """Devuelve True sólo si el registro satisface todos los gates L3 vigentes."""
    return _record_has_complete_l3_evidence(record)


def _canonical_pair(pair: Sequence[str]) -> tuple[str, str]:
    if len(pair) != 2:
        raise ValueError("El par de modelos debe contener exactamente dos elementos.")
    a, b = str(pair[0]), str(pair[1])
    if a == b:
        raise ValueError("El par de modelos no puede repetir el mismo modelo.")
    return tuple(sorted((a, b)))


def authorize_l3_observation(
    observation: Mapping[str, Any],
    *,
    registry: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    registry = registry or load_discriminator_promotion_registry()
    records = _record_map(registry)

    discriminator_id = observation.get("discriminator_id")
    if not isinstance(discriminator_id, str) or not discriminator_id:
        raise ValueError("Observación L3 sin discriminator_id.")

    record = records.get(discriminator_id)
    if record is None:
        raise ValueError(
            f"{discriminator_id}: no existe en el registro canónico de promoción."
        )
    if not _record_has_complete_l3_evidence(record):
        raise ValueError(
            f"{discriminator_id}: no está promovido canónicamente a L3_VALIDATED."
        )

    promotion_ref = observation.get("promotion_ref")
    if promotion_ref != record.get("promotion_ref"):
        raise ValueError(
            f"{discriminator_id}: promotion_ref no coincide con el registro canónico."
        )

    pair = observation.get("pair")
    if not isinstance(pair, (list, tuple)):
        raise ValueError(f"{discriminator_id}: pair ausente o inválido.")
    requested_pair = _canonical_pair(pair)

    validated_pairs = {
        _canonical_pair(item)
        for item in record.get("validated_pairs", [])
    }
    if requested_pair not in validated_pairs:
        raise ValueError(
            f"{discriminator_id}: el par {requested_pair} queda fuera del alcance L3 validado."
        )

    root_key = observation.get("root_key")
    prefix = record.get("root_key_prefix")
    if not isinstance(root_key, str) or not root_key:
        raise ValueError(f"{discriminator_id}: root_key es obligatorio para L3.")
    if not root_key.startswith(str(prefix)):
        raise ValueError(
            f"{discriminator_id}: root_key no pertenece a la familia registrada {prefix!r}."
        )

    return record


def validate_l3_observations(
    observations: Sequence[Mapping[str, Any] | Any],
    *,
    registry: Mapping[str, Any] | None = None,
) -> None:
    for observation in observations:
        if isinstance(observation, Mapping):
            if observation.get("validation_level") == "L3_VALIDATED":
                authorize_l3_observation(observation, registry=registry)
            continue

        if getattr(observation, "validation_level", None) == "L3_VALIDATED":
            raise ValueError(
                "Las observaciones L3 deben ser objetos trazables con promotion_ref."
            )


def authorize_promoted_discriminator_component(
    *,
    discriminator_id: str,
    promotion_ref: str,
    pair: Sequence[str],
    root_key: str,
    registry: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    observation = {
        "discriminator_id": discriminator_id,
        "validation_level": "L3_VALIDATED",
        "promotion_ref": promotion_ref,
        "pair": list(pair),
        "root_key": root_key,
    }
    return authorize_l3_observation(observation, registry=registry)
