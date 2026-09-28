from __future__ import annotations

from hashlib import sha256
from importlib import resources
import json
from typing import Any, Mapping, Sequence


POLICY_RESOURCE = "holdout-open-gate-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_holdout_open_gate_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data", POLICY_RESOURCE
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != "ALMAS_HOLDOUT_OPEN_GATE_V1":
        raise ValueError("Política de apertura holdout desconocida.")
    return policy


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(value: Mapping[str, Any]) -> str:
    return sha256(_canonical_json(value)).hexdigest()


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


def evaluate_holdout_open(
    preregistration: Mapping[str, Any],
    request: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Abre un holdout preregistrado sin evaluar ningún resultado."""

    if policy is None:
        policy = load_holdout_open_gate_policy()

    bundle = preregistration.get("bundle")
    declared_sha = preregistration.get("bundle_sha256")
    if not isinstance(bundle, Mapping):
        return _blocked("MISSING_PREREGISTRATION_BUNDLE")
    if not isinstance(declared_sha, str) or len(declared_sha) != 64:
        return _blocked("INVALID_PREREGISTRATION_FINGERPRINT")
    if bundle.get("policy_id") != policy["required_preregistration_policy_id"]:
        return _blocked("PREREGISTRATION_POLICY_MISMATCH")

    actual_sha = _sha256(bundle)
    if actual_sha != declared_sha:
        return _blocked(
            "PREREGISTRATION_FINGERPRINT_MISMATCH",
            expected_sha256=declared_sha,
            actual_sha256=actual_sha,
        )

    forbidden = set(policy["forbidden_open_request_keys"])
    hits = sorted(forbidden & _recursive_keys(request))
    if hits:
        return _blocked(
            "OBSERVED_OR_FORBIDDEN_DATA_PRESENT_AT_OPEN",
            forbidden_keys=hits,
        )

    runtime_version = request.get("runtime_almas_version")
    runtime_commit = request.get("runtime_commit_sha")
    if runtime_version != bundle.get("frozen_almas_version"):
        return _blocked("RUNTIME_VERSION_MISMATCH")
    if runtime_commit != bundle.get("frozen_commit_sha"):
        return _blocked("RUNTIME_COMMIT_MISMATCH")

    candidate = bundle.get("candidate")
    if not isinstance(candidate, Mapping):
        return _blocked("MISSING_FROZEN_CANDIDATE")
    if request.get("candidate_id") != candidate.get("candidate_id"):
        return _blocked("CANDIDATE_ID_MISMATCH")
    if request.get("formula_ref") != candidate.get("formula_ref"):
        return _blocked("FORMULA_REF_MISMATCH")

    frozen_cohort = bundle.get("cohort_plan")
    supplied_cohort = request.get("cohort_header")
    if not isinstance(frozen_cohort, Mapping):
        return _blocked("MISSING_FROZEN_COHORT_PLAN")
    if not isinstance(supplied_cohort, Mapping):
        return _blocked("MISSING_COHORT_HEADER")

    for key in (
        "cohort_id",
        "null_model",
        "feature_set_ref",
        "orb_policy_ref",
        "pairing_rule_ref",
        "inclusion_rule_ref",
    ):
        if supplied_cohort.get(key) != frozen_cohort.get(key):
            return _blocked(
                "COHORT_METADATA_MISMATCH",
                mismatch_field=key,
            )

    sample_count = supplied_cohort.get("sample_count")
    if (
        isinstance(sample_count, bool)
        or not isinstance(sample_count, int)
        or sample_count <= 0
    ):
        return _blocked("INVALID_SAMPLE_COUNT")
    minimum = frozen_cohort.get("planned_min_samples")
    if (
        isinstance(minimum, bool)
        or not isinstance(minimum, int)
        or minimum <= 0
    ):
        return _blocked("INVALID_FROZEN_MINIMUM_SAMPLE_COUNT")
    if sample_count < minimum:
        return _blocked(
            "PLANNED_MINIMUM_SAMPLE_COUNT_NOT_MET",
            sample_count=sample_count,
            planned_min_samples=minimum,
        )

    opening_record = {
        "schema_version": "1.0.0",
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "validation_id": bundle.get("validation_id"),
        "preregistration_ref": bundle.get("preregistration_ref"),
        "preregistration_sha256": declared_sha,
        "runtime_almas_version": runtime_version,
        "runtime_commit_sha": runtime_commit,
        "candidate_id": candidate.get("candidate_id"),
        "formula_ref": candidate.get("formula_ref"),
        "cohort_header": {
            "cohort_id": supplied_cohort.get("cohort_id"),
            "null_model": supplied_cohort.get("null_model"),
            "feature_set_ref": supplied_cohort.get("feature_set_ref"),
            "orb_policy_ref": supplied_cohort.get("orb_policy_ref"),
            "pairing_rule_ref": supplied_cohort.get("pairing_rule_ref"),
            "inclusion_rule_ref": supplied_cohort.get("inclusion_rule_ref"),
            "sample_count": sample_count,
        },
        "holdout_opened": True,
        "holdout_evaluation_permitted": True,
        "holdout_evaluated": False,
        "promotion_permitted": False,
        "automatic_registry_mutation": False,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
    open_sha = _sha256(opening_record)
    return {
        "state": "HOLDOUT_OPENED",
        "opening_record": opening_record,
        "opening_sha256": open_sha,
        "holdout_evaluation_permitted": True,
        "promotion_permitted": False,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }


def _blocked(reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "state": "BLOCKED_HOLDOUT_OPEN",
        "reason": reason,
        **extra,
        "holdout_evaluation_permitted": False,
        "promotion_permitted": False,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
