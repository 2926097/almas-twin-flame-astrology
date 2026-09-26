from __future__ import annotations

from importlib import resources
import json
from typing import Any, Mapping, Sequence

from .px_v3_candidates import (
    evaluate_px_v3_candidate,
    load_px_v3_candidate_freeze_policy,
)


POLICY_RESOURCE = "px-v3-promotion-gate-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_px_v3_promotion_gate_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data",
        POLICY_RESOURCE,
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_PX_V3_PROMOTION_GATE_V1":
        raise ValueError("Política S8 de promoción PX v3 desconocida.")
    return policy


def _string_list(bundle: Mapping[str, Any], key: str) -> list[str]:
    value = bundle.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} debe ser una lista.")
    output = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError(f"{key} contiene un valor inválido.")
        output.append(item)
    if len(set(output)) != len(output):
        raise ValueError(f"{key} contiene duplicados.")
    return output


def _nonnegative_int(bundle: Mapping[str, Any], key: str) -> int:
    value = bundle.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{key} debe ser entero >= 0.")
    return int(value)


def evaluate_px_v3_promotion(
    evidence: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
    candidate_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evalúa elegibilidad metodológica sin activar el candidato."""

    if policy is None:
        policy = load_px_v3_promotion_gate_policy()
    if candidate_policy is None:
        candidate_policy = load_px_v3_candidate_freeze_policy()

    candidate = evidence.get("candidate")
    if not isinstance(candidate, Mapping):
        raise ValueError("candidate debe ser un objeto.")
    candidate_eval = evaluate_px_v3_candidate(
        candidate,
        policy=candidate_policy,
    )

    reasons: list[str] = []
    if not candidate_eval["frozen_for_validation"]:
        reasons.append("CANDIDATE_NOT_FROZEN_FOR_VALIDATION")

    holdouts = evidence.get("holdout_evaluations")
    if not isinstance(holdouts, list):
        raise ValueError("holdout_evaluations debe ser una lista.")

    valid_holdout_count = 0
    holdout_fingerprints: list[str] = []
    for index, item in enumerate(holdouts):
        if not isinstance(item, Mapping):
            raise ValueError(
                f"holdout_evaluations[{index}] debe ser un objeto."
            )
        if item.get("candidate_id") != candidate_eval["candidate_id"]:
            reasons.append("HOLDOUT_CANDIDATE_ID_MISMATCH")
            continue
        if item.get("formula_ref") != candidate_eval["formula_ref"]:
            reasons.append("HOLDOUT_FORMULA_REF_MISMATCH")
            continue
        if item.get("state") != "HOLDOUT_EVALUATED_DIAGNOSTIC_ONLY":
            reasons.append("HOLDOUT_NOT_DIAGNOSTIC_EVALUATED")
            continue
        if item.get("promotion_decision") != "FORBIDDEN":
            reasons.append("HOLDOUT_ILLEGAL_PROMOTION_DECISION")
            continue
        if item.get("candidate_validated") is not False:
            reasons.append("HOLDOUT_ILLEGAL_VALIDATED_FLAG")
            continue
        fingerprint = item.get("distribution_fingerprint_sha256")
        if not isinstance(fingerprint, str) or not fingerprint:
            reasons.append("HOLDOUT_FINGERPRINT_MISSING")
            continue
        valid_holdout_count += 1
        holdout_fingerprints.append(fingerprint)

    req = policy["required_evidence"]
    if valid_holdout_count < int(req["holdout_evaluations_min"]):
        reasons.append("INSUFFICIENT_HOLDOUT_EVALUATIONS")

    ext_refs = _string_list(evidence, "external_calibration_refs")
    rep_refs = _string_list(evidence, "independent_replication_refs")
    leakage_refs = _string_list(evidence, "leakage_audit_refs")

    if len(ext_refs) < int(req["external_calibration_refs_min"]):
        reasons.append("INSUFFICIENT_EXTERNAL_CALIBRATION_REFS")
    if len(rep_refs) < int(req["independent_replication_refs_min"]):
        reasons.append("INSUFFICIENT_INDEPENDENT_REPLICATION_REFS")
    if len(leakage_refs) < int(req["leakage_audit_refs_min"]):
        reasons.append("INSUFFICIENT_LEAKAGE_AUDIT_REFS")

    criteria = evidence.get("criterion_results")
    if not isinstance(criteria, list):
        raise ValueError("criterion_results debe ser una lista.")
    valid_criteria = 0
    failed_criteria = 0
    criterion_ids: set[str] = set()
    for index, item in enumerate(criteria):
        if not isinstance(item, Mapping):
            raise ValueError(f"criterion_results[{index}] debe ser objeto.")
        criterion_id = item.get("criterion_id")
        prereg_ref = item.get("preregistration_ref")
        evaluation_ref = item.get("evaluation_ref")
        passed = item.get("passed")
        if not isinstance(criterion_id, str) or not criterion_id:
            raise ValueError("criterion_id obligatorio.")
        if criterion_id in criterion_ids:
            raise ValueError(f"criterion_id duplicado: {criterion_id}.")
        criterion_ids.add(criterion_id)
        if not isinstance(prereg_ref, str) or not prereg_ref:
            raise ValueError(f"{criterion_id}: preregistration_ref obligatorio.")
        if not isinstance(evaluation_ref, str) or not evaluation_ref:
            raise ValueError(f"{criterion_id}: evaluation_ref obligatorio.")
        if not isinstance(passed, bool):
            raise ValueError(f"{criterion_id}: passed debe ser boolean.")
        valid_criteria += 1
        if not passed:
            failed_criteria += 1

    if valid_criteria < int(req["preregistered_criterion_results_min"]):
        reasons.append("INSUFFICIENT_PREREGISTERED_CRITERIA")
    if failed_criteria:
        reasons.append("PREREGISTERED_CRITERION_FAILED")

    counts = {}
    for key in (
        "negative_control_failure_count",
        "ablation_failure_count",
        "case_fitting_count",
        "label_leakage_count",
        "narrative_leakage_count",
        "post_holdout_rule_change_count",
    ):
        counts[key] = _nonnegative_int(evidence, key)
        expected = int(req[key])
        if counts[key] != expected:
            reasons.append(key.upper())

    reasons = sorted(set(reasons))
    eligible = not reasons

    return {
        "state": "PROMOTION_ELIGIBLE" if eligible else "NOT_ELIGIBLE",
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "candidate_id": candidate_eval["candidate_id"],
        "formula_ref": candidate_eval["formula_ref"],
        "valid_holdout_evaluation_count": valid_holdout_count,
        "holdout_distribution_fingerprints": sorted(
            set(holdout_fingerprints)
        ),
        "external_calibration_ref_count": len(ext_refs),
        "independent_replication_ref_count": len(rep_refs),
        "leakage_audit_ref_count": len(leakage_refs),
        "criterion_result_count": valid_criteria,
        "failed_criterion_count": failed_criteria,
        "failure_counts": counts,
        "reasons": reasons,
        "automatic_registry_mutation": False,
        "manual_new_version_required_for_activation": True,
        "active_in_scoring": False,
        "scoring_enabled": False,
        "weighting_enabled": False,
        "ontology_enabled": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
