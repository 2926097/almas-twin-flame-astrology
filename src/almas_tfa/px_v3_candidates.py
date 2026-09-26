from __future__ import annotations

from importlib import resources
import json
from typing import Any, Mapping


POLICY_RESOURCE = "px-v3-candidate-freeze-policy.json"
REGISTRY_RESOURCE = "px-v3-candidate-registry.json"
POLICY_PACKAGE = "almas_tfa"


def load_px_v3_candidate_freeze_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data",
        POLICY_RESOURCE,
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_PX_V3_CANDIDATE_FREEZE_V1":
        raise ValueError("Política de candidatos PX v3 desconocida.")
    return policy


def load_px_v3_candidate_registry() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data",
        REGISTRY_RESOURCE,
    )
    with resource.open("r", encoding="utf-8") as handle:
        registry = json.load(handle)

    if registry.get("registry_id") != "ALMAS_PX_V3_CANDIDATES":
        raise ValueError("Registro PX v3 desconocido.")
    return registry


def _nonempty_list(record: Mapping[str, Any], key: str) -> list[str]:
    value = record.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} debe ser lista no vacía.")
    output = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{key} contiene un valor inválido.")
        output.append(item.strip())
    if len(set(output)) != len(output):
        raise ValueError(f"{key} contiene duplicados.")
    return output


def evaluate_px_v3_candidate(
    record: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evalúa si un candidato está congelado para validación, no para scoring."""

    if policy is None:
        policy = load_px_v3_candidate_freeze_policy()

    candidate_id = record.get("candidate_id")
    if not isinstance(candidate_id, str) or not candidate_id:
        raise ValueError("candidate_id obligatorio.")

    status = record.get("status")
    if status not in policy["allowed_statuses"]:
        raise ValueError(f"{candidate_id}: status inválido.")
    if record.get("target") not in policy["allowed_targets"]:
        raise ValueError(f"{candidate_id}: target inválido.")

    descriptors = _nonempty_list(record, "descriptor_ids")
    unknown = sorted(
        set(descriptors) - set(policy["allowed_descriptors"])
    )
    if unknown:
        raise ValueError(
            f"{candidate_id}: descriptors no admitidos: {unknown}."
        )

    for key in (
        "formula_ref",
        "expected_direction",
    ):
        value = record.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{candidate_id}: {key} obligatorio.")

    development_refs = _nonempty_list(record, "development_case_refs")
    s2_refs = _nonempty_list(record, "s2_refs")
    s3_refs = _nonempty_list(record, "s3_refs")
    ablation_refs = _nonempty_list(record, "ablation_refs")
    negative_refs = _nonempty_list(record, "negative_control_refs")
    falsifiers = _nonempty_list(record, "falsification_criteria")

    holdout_refs = record.get("holdout_refs")
    if not isinstance(holdout_refs, list):
        raise ValueError(f"{candidate_id}: holdout_refs debe ser lista.")

    frozen_before_holdout = record.get("formula_frozen_before_holdout")
    if not isinstance(frozen_before_holdout, bool):
        raise ValueError(
            f"{candidate_id}: formula_frozen_before_holdout debe ser boolean."
        )
    fitted = record.get("holdout_fitted_thresholds")
    if not isinstance(fitted, bool):
        raise ValueError(
            f"{candidate_id}: holdout_fitted_thresholds debe ser boolean."
        )

    scoring_enabled = record.get("scoring_enabled")
    ontology_enabled = record.get("ontology_enabled")
    if scoring_enabled is not False or ontology_enabled is not False:
        raise ValueError(
            f"{candidate_id}: S6 prohíbe scoring/ontology habilitados."
        )

    freeze_violations = []
    if not frozen_before_holdout:
        freeze_violations.append("FORMULA_NOT_FROZEN_BEFORE_HOLDOUT")
    if fitted:
        freeze_violations.append("HOLDOUT_FITTED_THRESHOLDS")
    if holdout_refs:
        freeze_violations.append("HOLDOUT_ALREADY_OBSERVED_AT_FREEZE")

    frozen_ready = (
        status == "FROZEN_FOR_VALIDATION"
        and not freeze_violations
    )

    return {
        "candidate_id": candidate_id,
        "status": status,
        "target": record["target"],
        "descriptor_ids": descriptors,
        "formula_ref": str(record["formula_ref"]),
        "expected_direction": str(record["expected_direction"]),
        "development_case_ref_count": len(development_refs),
        "s2_ref_count": len(s2_refs),
        "s3_ref_count": len(s3_refs),
        "ablation_ref_count": len(ablation_refs),
        "negative_control_ref_count": len(negative_refs),
        "falsification_criterion_count": len(falsifiers),
        "holdout_ref_count": len(holdout_refs),
        "freeze_violations": freeze_violations,
        "frozen_for_validation": frozen_ready,
        "scoring_enabled": False,
        "weighting_enabled": False,
        "ontology_enabled": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }


def evaluate_px_v3_candidate_registry(
    registry: Mapping[str, Any] | None = None,
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Audita el registro canónico sin activar ningún candidato."""

    if policy is None:
        policy = load_px_v3_candidate_freeze_policy()
    if registry is None:
        registry = load_px_v3_candidate_registry()

    if registry.get("policy_id") != policy["policy_id"]:
        raise ValueError("Registry/policy PX v3 incompatibles.")
    if registry.get("scoring_enabled") is not False:
        raise ValueError("El registro PX v3 no puede habilitar scoring en S6.")
    if registry.get("weighting_enabled") is not False:
        raise ValueError("El registro PX v3 no puede habilitar weighting en S6.")
    if registry.get("ontology_enabled") is not False:
        raise ValueError("El registro PX v3 no puede habilitar ontología en S6.")
    if registry.get("validated_candidate_ids") not in ([], tuple()):
        raise ValueError("S6 no admite candidatos validados.")

    records = registry.get("records")
    if not isinstance(records, list):
        raise ValueError("records debe ser una lista.")

    seen: set[str] = set()
    evaluated = []
    for raw in records:
        if not isinstance(raw, Mapping):
            raise ValueError("Cada candidato debe ser un objeto.")
        item = evaluate_px_v3_candidate(raw, policy=policy)
        if item["candidate_id"] in seen:
            raise ValueError(
                f"candidate_id duplicado: {item['candidate_id']}."
            )
        seen.add(item["candidate_id"])
        evaluated.append(item)

    frozen = [
        item["candidate_id"]
        for item in evaluated
        if item["frozen_for_validation"]
    ]

    return {
        "state": "REGISTRY_AUDITED",
        "policy_id": policy["policy_id"],
        "registry_id": str(registry.get("registry_id") or ""),
        "record_count": len(evaluated),
        "frozen_for_validation_ids": frozen,
        "scoring_candidate_count": 0,
        "validated_candidate_count": 0,
        "scoring_enabled": False,
        "weighting_enabled": False,
        "ontology_enabled": False,
        "l3_validation": False,
        "metaphysical_probability": False,
        "records": evaluated,
    }
