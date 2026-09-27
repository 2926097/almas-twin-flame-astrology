from __future__ import annotations

from hashlib import sha256
from importlib import resources
import json
from typing import Any, Mapping, Sequence

from .px_v3_candidates import (
    evaluate_px_v3_candidate,
    load_px_v3_candidate_freeze_policy,
)


POLICY_RESOURCE = "validation-preregistration-bundle-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_validation_preregistration_bundle_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data", POLICY_RESOURCE
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != "ALMAS_VALIDATION_PREREGISTRATION_BUNDLE_V1":
        raise ValueError("Política de preregistro de validación desconocida.")
    return policy


def _nonempty_string(obj: Mapping[str, Any], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} debe ser string no vacío.")
    return value.strip()


def _unique_strings(obj: Mapping[str, Any], key: str) -> list[str]:
    raw = obj.get(key)
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{key} debe ser lista no vacía.")
    output = []
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{key} contiene un valor inválido.")
        output.append(item.strip())
    if len(set(output)) != len(output):
        raise ValueError(f"{key} contiene duplicados.")
    return output


def _recursive_keys(value: Any) -> set[str]:
    output: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            output.add(str(key))
            output |= _recursive_keys(child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            output |= _recursive_keys(child)
    return output


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _fingerprint(value: Mapping[str, Any]) -> str:
    return sha256(_canonical_json(value)).hexdigest()


def build_validation_preregistration_bundle(
    candidate: Mapping[str, Any],
    plan: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Congela un plan de validación antes de observar el holdout.

    No evalúa resultados ni activa scoring. Rechaza datos de muestra,
    resultados observados y claves de leakage.
    """

    if policy is None:
        policy = load_validation_preregistration_bundle_policy()

    candidate_eval = evaluate_px_v3_candidate(
        candidate,
        policy=load_px_v3_candidate_freeze_policy(),
    )
    if not candidate_eval["frozen_for_validation"]:
        return {
            "state": "NOT_EVALUABLE",
            "reason": "CANDIDATE_NOT_FROZEN_FOR_VALIDATION",
            "candidate_id": candidate_eval["candidate_id"],
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }
    if candidate_eval["holdout_ref_count"] != 0:
        return {
            "state": "NOT_EVALUABLE",
            "reason": "HOLDOUT_ALREADY_OBSERVED_AT_PREREGISTRATION",
            "candidate_id": candidate_eval["candidate_id"],
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    forbidden = set(policy["forbidden_bundle_keys"])
    present_keys = _recursive_keys(plan)
    forbidden_hits = sorted(forbidden & present_keys)
    if forbidden_hits:
        return {
            "state": "NOT_EVALUABLE",
            "reason": "FORBIDDEN_PREREGISTRATION_KEYS",
            "forbidden_keys": forbidden_hits,
            "candidate_id": candidate_eval["candidate_id"],
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    try:
        validation_id = _nonempty_string(plan, "validation_id")
        preregistration_ref = _nonempty_string(plan, "preregistration_ref")
        frozen_almas_version = _nonempty_string(plan, "frozen_almas_version")
        frozen_commit_sha = _nonempty_string(plan, "frozen_commit_sha")
        if len(frozen_commit_sha) < 7:
            raise ValueError("frozen_commit_sha debe tener al menos 7 caracteres.")

        cohort = plan.get("cohort_plan")
        if not isinstance(cohort, Mapping):
            raise ValueError("cohort_plan obligatorio.")
        cohort_id = _nonempty_string(cohort, "cohort_id")
        null_model = _nonempty_string(cohort, "null_model")
        if null_model not in policy["allowed_null_models"]:
            raise ValueError("null_model no admitido.")
        feature_set_ref = _nonempty_string(cohort, "feature_set_ref")
        orb_policy_ref = _nonempty_string(cohort, "orb_policy_ref")
        pairing_rule_ref = _nonempty_string(cohort, "pairing_rule_ref")
        inclusion_rule_ref = _nonempty_string(cohort, "inclusion_rule_ref")
        planned_min_samples = cohort.get("planned_min_samples")
        if (
            isinstance(planned_min_samples, bool)
            or not isinstance(planned_min_samples, int)
            or planned_min_samples <= 0
        ):
            raise ValueError("planned_min_samples debe ser entero positivo.")

        blinding_plan_ref = _nonempty_string(plan, "blinding_plan_ref")
        leakage_audit_plan_ref = _nonempty_string(
            plan, "leakage_audit_plan_ref"
        )
        independent_replication_plan_refs = _unique_strings(
            plan, "independent_replication_plan_refs"
        )
        negative_control_refs = _unique_strings(
            plan, "negative_control_refs"
        )
        ablation_refs = _unique_strings(plan, "ablation_refs")

        endpoints = plan.get("endpoints")
        if not isinstance(endpoints, list) or not endpoints:
            raise ValueError("endpoints debe ser lista no vacía.")
        endpoint_ids = []
        normalized_endpoints = []
        for item in endpoints:
            if not isinstance(item, Mapping):
                raise ValueError("Cada endpoint debe ser objeto.")
            endpoint_id = _nonempty_string(item, "endpoint_id")
            success_criterion = _nonempty_string(item, "success_criterion")
            failure_criterion = _nonempty_string(item, "failure_criterion")
            endpoint_ids.append(endpoint_id)
            normalized_endpoints.append({
                "endpoint_id": endpoint_id,
                "success_criterion": success_criterion,
                "failure_criterion": failure_criterion,
            })
        if len(set(endpoint_ids)) != len(endpoint_ids):
            raise ValueError("endpoint_id duplicado.")

        required = set(policy["required_endpoint_ids"])
        missing = sorted(required - set(endpoint_ids))
        if missing:
            raise ValueError(
                "Faltan endpoints requeridos: " + ",".join(missing)
            )

        development_case_refs = list(candidate.get("development_case_refs", []))
        planned_holdout_refs = plan.get("planned_holdout_refs", [])
        if not isinstance(planned_holdout_refs, list):
            raise ValueError("planned_holdout_refs debe ser lista.")
        for item in planned_holdout_refs:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("planned_holdout_refs contiene valor inválido.")
        if len(set(planned_holdout_refs)) != len(planned_holdout_refs):
            raise ValueError("planned_holdout_refs contiene duplicados.")
        overlap = sorted(
            set(development_case_refs) & set(planned_holdout_refs)
        )
        if overlap:
            return {
                "state": "NOT_EVALUABLE",
                "reason": "DEVELOPMENT_HOLDOUT_OVERLAP",
                "overlap_refs": overlap,
                "candidate_id": candidate_eval["candidate_id"],
                "scoring_enabled": False,
                "weighting_enabled": False,
                "ontology_enabled": False,
                "l3_validation": False,
                "metaphysical_probability": False,
            }
    except ValueError as exc:
        return {
            "state": "NOT_EVALUABLE",
            "reason": str(exc),
            "candidate_id": candidate_eval["candidate_id"],
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    frozen_bundle = {
        "schema_version": "1.0.0",
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "validation_id": validation_id,
        "preregistration_ref": preregistration_ref,
        "frozen_almas_version": frozen_almas_version,
        "frozen_commit_sha": frozen_commit_sha,
        "candidate": {
            "candidate_id": candidate_eval["candidate_id"],
            "target": candidate_eval["target"],
            "descriptor_ids": candidate_eval["descriptor_ids"],
            "formula_ref": candidate_eval["formula_ref"],
            "expected_direction": candidate_eval["expected_direction"],
            "development_case_refs": sorted(development_case_refs),
            "frozen_for_validation": True,
        },
        "cohort_plan": {
            "cohort_id": cohort_id,
            "null_model": null_model,
            "feature_set_ref": feature_set_ref,
            "orb_policy_ref": orb_policy_ref,
            "pairing_rule_ref": pairing_rule_ref,
            "inclusion_rule_ref": inclusion_rule_ref,
            "planned_min_samples": planned_min_samples,
        },
        "blinding_plan_ref": blinding_plan_ref,
        "leakage_audit_plan_ref": leakage_audit_plan_ref,
        "independent_replication_plan_refs": sorted(
            independent_replication_plan_refs
        ),
        "negative_control_refs": sorted(negative_control_refs),
        "ablation_refs": sorted(ablation_refs),
        "planned_holdout_refs": sorted(planned_holdout_refs),
        "endpoints": sorted(
            normalized_endpoints,
            key=lambda item: item["endpoint_id"],
        ),
        "holdout_opened": False,
        "observed_results_present": False,
        "raw_samples_present": False,
        "automatic_registry_mutation": False,
        "scoring_enabled": False,
        "weighting_enabled": False,
        "ontology_enabled": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
    fingerprint = _fingerprint(frozen_bundle)

    return {
        "state": "PREREGISTERED_READY",
        "bundle": frozen_bundle,
        "bundle_sha256": fingerprint,
        "candidate_id": candidate_eval["candidate_id"],
        "holdout_opened": False,
        "scoring_enabled": False,
        "weighting_enabled": False,
        "ontology_enabled": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
