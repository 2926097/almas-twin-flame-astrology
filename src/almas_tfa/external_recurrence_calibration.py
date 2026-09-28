from __future__ import annotations

from importlib import resources
import json
from typing import Any, Mapping

from .external_control_cohorts import (
    extract_clean_external_candidate_snapshots,
    load_external_recurrence_cohort_policy,
    validate_external_recurrence_cohort,
)
from .null_calibration import derive_recurrence_calibration_payload


POLICY_RESOURCE = "external-recurrence-calibration-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_external_recurrence_calibration_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data",
        POLICY_RESOURCE,
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)

    if policy.get("policy_id") != "ALMAS_EXTERNAL_RECURRENCE_CALIBRATION_V1":
        raise ValueError("Política de calibración externa desconocida.")
    return policy


def _invariant_tail() -> dict[str, Any]:
    return {
        "used_for_weighting": False,
        "used_in_px_score": False,
        "used_in_ps_score": False,
        "used_in_iem": False,
        "used_in_idd": False,
        "used_in_irc": False,
        "used_in_ontology": False,
        "candidate_freeze_enabled": False,
        "l3_validation": False,
        "metaphysical_probability": False,
        "population_probability_claim": False,
        "combined_p_value": None,
        "combined_p_value_state": "FORBIDDEN",
        "multiple_testing_correction_state": "NOT_CLAIMED",
        "sample_identifiers_exposed": False,
        "sample_snapshots_exposed": False,
    }


def derive_external_recurrence_calibration(
    baseline_snapshot: Mapping[str, Any],
    cohort: Mapping[str, Any],
    *,
    cohort_policy: Mapping[str, Any] | None = None,
    calibration_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Calibra contra holdouts externos limpios sin habilitar weighting."""

    if cohort_policy is None:
        cohort_policy = load_external_recurrence_cohort_policy()
    if calibration_policy is None:
        calibration_policy = load_external_recurrence_calibration_policy()

    summary = validate_external_recurrence_cohort(
        cohort,
        policy=cohort_policy,
    )
    null_model = str(cohort.get("null_model") or "")

    if null_model not in calibration_policy["allowed_null_models"]:
        return {
            "state": "NOT_EVALUABLE",
            "policy_id": calibration_policy["policy_id"],
            "reason": "null_model externo no admitido por S5.",
            "cohort_summary": summary,
            **_invariant_tail(),
        }

    if summary.get("state") != "PROTOCOL_READY":
        return {
            "state": "NOT_EVALUABLE",
            "policy_id": calibration_policy["policy_id"],
            "reason": "La cohorte no supera el firewall S4.",
            "cohort_summary": summary,
            **_invariant_tail(),
        }

    snapshots = extract_clean_external_candidate_snapshots(
        cohort,
        policy=cohort_policy,
    )
    minimum = int(calibration_policy["minimum_clean_external_samples"])
    if len(snapshots) < minimum:
        return {
            "state": "NOT_EVALUABLE",
            "policy_id": calibration_policy["policy_id"],
            "reason": (
                f"Se requieren al menos {minimum} controles externos limpios; "
                f"disponibles={len(snapshots)}."
            ),
            "cohort_summary": summary,
            "clean_external_sample_count": len(snapshots),
            **_invariant_tail(),
        }

    core = derive_recurrence_calibration_payload(
        baseline_snapshot,
        snapshots,
        minimum_samples=minimum,
        confidence_level=float(calibration_policy["confidence_level"]),
    )
    if core.get("state") != "DIAGNOSTIC_ONLY":
        return {
            **core,
            "policy_id": calibration_policy["policy_id"],
            "policy_status": calibration_policy["status"],
            "epistemic_class": calibration_policy["epistemic_class"],
            "cohort_policy_id": cohort_policy["policy_id"],
            "cohort_summary": summary,
            "clean_external_sample_count": len(snapshots),
            **_invariant_tail(),
        }

    return {
        **core,
        "policy_id": calibration_policy["policy_id"],
        "policy_status": calibration_policy["status"],
        "epistemic_class": calibration_policy["epistemic_class"],
        "cohort_policy_id": cohort_policy["policy_id"],
        "cohort_id": str(cohort["cohort_id"]),
        "preregistration_ref": str(cohort["preregistration_ref"]),
        "null_model": null_model,
        "clean_external_sample_count": len(snapshots),
        "cohort_summary": summary,
        "external_control_evidence": True,
        "interpretation_scope": "EXTERNAL_CONTROL_COHORT_RECURRENCE_FREQUENCY",
        **_invariant_tail(),
    }
