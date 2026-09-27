from __future__ import annotations

from hashlib import sha256
from importlib import resources
import json
import re
from typing import Any, Mapping

from .px_v3_promotion import evaluate_px_v3_promotion
from .validation_ledger import audit_validation_ledger


POLICY_RESOURCE = "validation-continuity-gate-policy.json"
POLICY_PACKAGE = "almas_tfa"
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def load_validation_continuity_gate_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data", POLICY_RESOURCE
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != "ALMAS_VALIDATION_CONTINUITY_GATE_V1":
        raise ValueError("Política de continuidad de validación desconocida.")
    return policy


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha(value: Mapping[str, Any]) -> str:
    return sha256(_canonical_json(value)).hexdigest()


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and _SHA_RE.fullmatch(value) is not None


def _blocked(reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "state": "BLOCKED_VALIDATION_CONTINUITY",
        "reason": reason,
        **extra,
        "promotion_bridge_permitted": False,
        "automatic_registry_mutation": False,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }


def evaluate_validation_continuity(
    preregistration: Mapping[str, Any],
    opening: Mapping[str, Any],
    holdout_evaluation: Mapping[str, Any],
    ledger: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verifica V1→V2→S7→V3 sin exponer muestras ni scores."""

    if policy is None:
        policy = load_validation_continuity_gate_policy()

    if preregistration.get("state") != "PREREGISTERED_READY":
        return _blocked("PREREGISTRATION_NOT_READY")
    bundle = preregistration.get("bundle")
    bundle_sha = preregistration.get("bundle_sha256")
    if not isinstance(bundle, Mapping) or not _valid_sha(bundle_sha):
        return _blocked("INVALID_PREREGISTRATION_ARTIFACT")
    if bundle.get("policy_id") != policy["required_preregistration_policy_id"]:
        return _blocked("PREREGISTRATION_POLICY_MISMATCH")
    if _sha(bundle) != bundle_sha:
        return _blocked("PREREGISTRATION_FINGERPRINT_MISMATCH")

    if opening.get("state") != "HOLDOUT_OPENED":
        return _blocked("HOLDOUT_NOT_OPENED")
    opening_record = opening.get("opening_record")
    opening_sha = opening.get("opening_sha256")
    if not isinstance(opening_record, Mapping) or not _valid_sha(opening_sha):
        return _blocked("INVALID_OPENING_ARTIFACT")
    if opening_record.get("policy_id") != policy["required_open_policy_id"]:
        return _blocked("OPENING_POLICY_MISMATCH")
    if _sha(opening_record) != opening_sha:
        return _blocked("OPENING_FINGERPRINT_MISMATCH")
    if opening_record.get("preregistration_sha256") != bundle_sha:
        return _blocked("OPENING_PREREGISTRATION_LINK_MISMATCH")

    candidate = bundle.get("candidate")
    cohort_plan = bundle.get("cohort_plan")
    cohort_header = opening_record.get("cohort_header")
    if not isinstance(candidate, Mapping):
        return _blocked("MISSING_FROZEN_CANDIDATE")
    if not isinstance(cohort_plan, Mapping) or not isinstance(
        cohort_header, Mapping
    ):
        return _blocked("MISSING_COHORT_METADATA")

    if opening_record.get("validation_id") != bundle.get("validation_id"):
        return _blocked("VALIDATION_ID_MISMATCH")
    if opening_record.get("candidate_id") != candidate.get("candidate_id"):
        return _blocked("OPENING_CANDIDATE_ID_MISMATCH")
    if opening_record.get("formula_ref") != candidate.get("formula_ref"):
        return _blocked("OPENING_FORMULA_REF_MISMATCH")
    if opening_record.get("runtime_almas_version") != bundle.get(
        "frozen_almas_version"
    ):
        return _blocked("RUNTIME_VERSION_CONTINUITY_MISMATCH")
    if opening_record.get("runtime_commit_sha") != bundle.get(
        "frozen_commit_sha"
    ):
        return _blocked("RUNTIME_COMMIT_CONTINUITY_MISMATCH")

    for field in (
        "cohort_id",
        "null_model",
        "feature_set_ref",
        "orb_policy_ref",
        "pairing_rule_ref",
        "inclusion_rule_ref",
    ):
        if cohort_header.get(field) != cohort_plan.get(field):
            return _blocked(
                "COHORT_PLAN_CONTINUITY_MISMATCH",
                mismatch_field=field,
            )

    if (
        holdout_evaluation.get("state")
        != "HOLDOUT_EVALUATED_DIAGNOSTIC_ONLY"
    ):
        return _blocked("HOLDOUT_NOT_DIAGNOSTIC_EVALUATED")
    if holdout_evaluation.get("policy_id") not in (
        None,
        policy["required_holdout_policy_id"],
    ):
        return _blocked("HOLDOUT_POLICY_MISMATCH")
    if holdout_evaluation.get("candidate_id") != candidate.get("candidate_id"):
        return _blocked("HOLDOUT_CANDIDATE_ID_MISMATCH")
    if holdout_evaluation.get("formula_ref") != candidate.get("formula_ref"):
        return _blocked("HOLDOUT_FORMULA_REF_MISMATCH")
    if holdout_evaluation.get("cohort_id") != cohort_plan.get("cohort_id"):
        return _blocked("HOLDOUT_COHORT_ID_MISMATCH")
    if holdout_evaluation.get("null_model") != cohort_plan.get("null_model"):
        return _blocked("HOLDOUT_NULL_MODEL_MISMATCH")

    distribution_sha = holdout_evaluation.get(
        "distribution_fingerprint_sha256"
    )
    if not _valid_sha(distribution_sha):
        return _blocked("HOLDOUT_DISTRIBUTION_FINGERPRINT_INVALID")

    clean_count = holdout_evaluation.get("clean_holdout_sample_count")
    opened_count = cohort_header.get("sample_count")
    if (
        isinstance(clean_count, bool)
        or not isinstance(clean_count, int)
        or clean_count <= 0
    ):
        return _blocked("INVALID_CLEAN_HOLDOUT_SAMPLE_COUNT")
    if (
        isinstance(opened_count, bool)
        or not isinstance(opened_count, int)
        or opened_count <= 0
        or clean_count > opened_count
    ):
        return _blocked("HOLDOUT_SAMPLE_COUNT_CONTINUITY_MISMATCH")

    if any(
        holdout_evaluation.get(key) not in (False, None)
        for key in (
            "candidate_validated",
            "scoring_enabled",
            "weighting_enabled",
            "ontology_enabled",
            "l3_validation",
            "metaphysical_probability",
        )
    ):
        return _blocked("ILLEGAL_HOLDOUT_ACTIVATION_FLAG")
    if holdout_evaluation.get("promotion_decision") not in (
        None,
        "FORBIDDEN",
    ):
        return _blocked("ILLEGAL_HOLDOUT_PROMOTION_DECISION")

    holdout_sha = _sha(holdout_evaluation)

    ledger_audit = audit_validation_ledger(ledger)
    if ledger_audit.get("state") != "LEDGER_VALID":
        return _blocked(
            "LEDGER_INTEGRITY_FAILURE",
            ledger_reason=ledger_audit.get("reason"),
        )
    if ledger.get("policy_id") != policy["required_ledger_policy_id"]:
        return _blocked("LEDGER_POLICY_MISMATCH")
    if ledger.get("validation_id") != bundle.get("validation_id"):
        return _blocked("LEDGER_VALIDATION_ID_MISMATCH")

    entries = ledger.get("entries")
    if not isinstance(entries, list) or len(entries) < 3:
        return _blocked("LEDGER_MISSING_REQUIRED_EVENTS")

    required_events = list(policy["required_ledger_events"])
    for index, event_type in enumerate(required_events):
        if entries[index].get("event_type") != event_type:
            return _blocked(
                "LEDGER_REQUIRED_EVENT_MISMATCH",
                sequence=index + 1,
                expected_event=event_type,
            )

    expected_hashes = (bundle_sha, opening_sha, holdout_sha)
    for index, expected_hash in enumerate(expected_hashes):
        if entries[index].get("artifact_sha256") != expected_hash:
            return _blocked(
                "LEDGER_ARTIFACT_CONTINUITY_MISMATCH",
                sequence=index + 1,
            )

    certificate = {
        "schema_version": "1.0.0",
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "validation_id": str(bundle["validation_id"]),
        "candidate_id": str(candidate["candidate_id"]),
        "formula_ref": str(candidate["formula_ref"]),
        "cohort_id": str(cohort_plan["cohort_id"]),
        "null_model": str(cohort_plan["null_model"]),
        "preregistration_sha256": str(bundle_sha),
        "opening_sha256": str(opening_sha),
        "holdout_evaluation_sha256": holdout_sha,
        "holdout_distribution_fingerprint_sha256": str(distribution_sha),
        "ledger_chain_head_sha256": str(ledger["chain_head_sha256"]),
        "ledger_entry_count": int(ledger["entry_count"]),
        "required_ledger_events_verified": True,
        "continuity_verified": True,
        "promotion_bridge_permitted": True,
        "private_payloads_exposed": False,
        "automatic_registry_mutation": False,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
    certificate_sha = _sha(certificate)
    return {
        "state": "CONTINUITY_VERIFIED",
        "certificate": certificate,
        "certificate_sha256": certificate_sha,
        "promotion_bridge_permitted": True,
        "automatic_registry_mutation": False,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }


def evaluate_px_v3_promotion_with_continuity(
    evidence: Mapping[str, Any],
    continuity: Mapping[str, Any],
) -> dict[str, Any]:
    """Ruta 1.16 hacia S8: exige certificado V4 válido antes del gate."""

    if continuity.get("state") != "CONTINUITY_VERIFIED":
        return {
            "state": "NOT_ELIGIBLE",
            "reasons": ["VALIDATION_CONTINUITY_REQUIRED"],
            "validation_continuity_verified": False,
            "automatic_registry_mutation": False,
            "active_in_scoring": False,
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    certificate = continuity.get("certificate")
    certificate_sha = continuity.get("certificate_sha256")
    if (
        not isinstance(certificate, Mapping)
        or not _valid_sha(certificate_sha)
        or _sha(certificate) != certificate_sha
        or certificate.get("continuity_verified") is not True
        or certificate.get("promotion_bridge_permitted") is not True
    ):
        return {
            "state": "NOT_ELIGIBLE",
            "reasons": ["VALIDATION_CONTINUITY_CERTIFICATE_INVALID"],
            "validation_continuity_verified": False,
            "automatic_registry_mutation": False,
            "active_in_scoring": False,
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    candidate = evidence.get("candidate")
    if not isinstance(candidate, Mapping):
        raise ValueError("candidate debe ser un objeto.")

    if candidate.get("candidate_id") != certificate.get("candidate_id"):
        return {
            "state": "NOT_ELIGIBLE",
            "reasons": ["CONTINUITY_CANDIDATE_ID_MISMATCH"],
            "validation_continuity_verified": False,
            "automatic_registry_mutation": False,
            "active_in_scoring": False,
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }
    if candidate.get("formula_ref") != certificate.get("formula_ref"):
        return {
            "state": "NOT_ELIGIBLE",
            "reasons": ["CONTINUITY_FORMULA_REF_MISMATCH"],
            "validation_continuity_verified": False,
            "automatic_registry_mutation": False,
            "active_in_scoring": False,
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    holdouts = evidence.get("holdout_evaluations")
    if not isinstance(holdouts, list):
        raise ValueError("holdout_evaluations debe ser una lista.")

    fingerprint = certificate.get(
        "holdout_distribution_fingerprint_sha256"
    )
    matching_holdout = any(
        isinstance(item, Mapping)
        and item.get("candidate_id") == certificate.get("candidate_id")
        and item.get("formula_ref") == certificate.get("formula_ref")
        and item.get("distribution_fingerprint_sha256") == fingerprint
        for item in holdouts
    )
    if not matching_holdout:
        return {
            "state": "NOT_ELIGIBLE",
            "reasons": ["CONTINUITY_HOLDOUT_FINGERPRINT_NOT_IN_EVIDENCE"],
            "validation_continuity_verified": False,
            "automatic_registry_mutation": False,
            "active_in_scoring": False,
            "scoring_enabled": False,
            "weighting_enabled": False,
            "ontology_enabled": False,
            "l3_validation": False,
            "metaphysical_probability": False,
        }

    result = evaluate_px_v3_promotion(evidence)
    return {
        **result,
        "validation_continuity_verified": True,
        "validation_continuity_policy_id": certificate["policy_id"],
        "validation_continuity_certificate_sha256": certificate_sha,
    }
