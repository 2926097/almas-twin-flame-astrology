from __future__ import annotations

from hashlib import sha256
from importlib import resources
import json
import re
from typing import Any, Mapping

from .validation_ledger import (
    append_validation_event,
    audit_validation_ledger,
)


POLICY_RESOURCE = "validation-closure-release-audit-policy.json"
POLICY_PACKAGE = "almas_tfa"
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def load_validation_closure_release_audit_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath(
        "data", POLICY_RESOURCE
    )
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if (
        policy.get("policy_id")
        != "ALMAS_VALIDATION_CLOSURE_RELEASE_AUDIT_V1"
    ):
        raise ValueError("Política V5 de cierre de validación desconocida.")
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


def _string(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _string_list(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    output: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            return None
        output.append(item)
    if len(set(output)) != len(output):
        return None
    return output


def _blocked(reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "state": "BLOCKED_VALIDATION_CLOSURE",
        "reason": reason,
        **extra,
        "automatic_registry_mutation": False,
        "manual_release_review_required": True,
        "same_release_activation_forbidden": True,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }


def _validated_continuity(
    continuity: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> tuple[dict[str, Any] | None, str | None, dict[str, Any] | None]:
    if continuity.get("state") != "CONTINUITY_VERIFIED":
        return None, None, _blocked("VALIDATION_CONTINUITY_REQUIRED")

    certificate = continuity.get("certificate")
    certificate_sha = continuity.get("certificate_sha256")
    if not isinstance(certificate, Mapping) or not _valid_sha(certificate_sha):
        return None, None, _blocked("INVALID_CONTINUITY_CERTIFICATE")
    certificate_dict = dict(certificate)
    if _sha(certificate_dict) != certificate_sha:
        return None, None, _blocked("CONTINUITY_FINGERPRINT_MISMATCH")
    if (
        certificate.get("policy_id")
        != policy["required_continuity_policy_id"]
        or certificate.get("continuity_verified") is not True
        or certificate.get("promotion_bridge_permitted") is not True
    ):
        return None, None, _blocked("CONTINUITY_CERTIFICATE_NOT_AUTHORIZED")
    return certificate_dict, str(certificate_sha), None


def _validated_ledger(
    ledger: Mapping[str, Any],
    *,
    policy: Mapping[str, Any],
    expected_event: str,
    validation_id: str,
) -> dict[str, Any] | None:
    audit = audit_validation_ledger(ledger)
    if audit.get("state") != "LEDGER_VALID":
        return _blocked(
            "LEDGER_INTEGRITY_FAILURE",
            ledger_reason=audit.get("reason"),
        )
    if ledger.get("policy_id") != policy["required_ledger_policy_id"]:
        return _blocked("LEDGER_POLICY_MISMATCH")
    if ledger.get("validation_id") != validation_id:
        return _blocked("LEDGER_VALIDATION_ID_MISMATCH")
    if ledger.get("current_event") != expected_event:
        return _blocked(
            "LEDGER_EVENT_MISMATCH",
            expected_event=expected_event,
            supplied_event=ledger.get("current_event"),
        )
    return None


def build_documentary_reveal_record(
    continuity: Mapping[str, Any],
    ledger: Mapping[str, Any],
    reveal: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Construye el artefacto de revelado tardío sin aceptar narrativa cruda."""

    if policy is None:
        policy = load_validation_closure_release_audit_policy()

    certificate, certificate_sha, error = _validated_continuity(
        continuity, policy
    )
    if error is not None:
        return error
    assert certificate is not None
    assert certificate_sha is not None

    ledger_error = _validated_ledger(
        ledger,
        policy=policy,
        expected_event="HOLDOUT_EVALUATED",
        validation_id=str(certificate["validation_id"]),
    )
    if ledger_error is not None:
        return ledger_error

    entries = ledger.get("entries")
    if not isinstance(entries, list) or len(entries) != 3:
        return _blocked("LEDGER_NOT_AT_REVEAL_BOUNDARY")
    expected_hashes = (
        certificate.get("preregistration_sha256"),
        certificate.get("opening_sha256"),
        certificate.get("holdout_evaluation_sha256"),
    )
    for index, expected_hash in enumerate(expected_hashes):
        if entries[index].get("artifact_sha256") != expected_hash:
            return _blocked(
                "PRE_REVEAL_ARTIFACT_CONTINUITY_MISMATCH",
                sequence=index + 1,
            )

    allowed = {
        "documentary_reveal_ref",
        "documentary_source_refs",
        "blinding_audit_ref",
        "leakage_audit_ref",
        "pre_reveal_structural_output_sha256",
        "post_reveal_structural_output_sha256",
        "identity_blinding_state",
        "identity_risk_refs",
        "forbidden_field_hits",
        "label_leakage_count",
        "narrative_leakage_count",
        "case_fitting_count",
        "post_holdout_rule_change_count",
    }
    unexpected = sorted(set(reveal) - allowed)
    if unexpected:
        return _blocked(
            "UNEXPECTED_REVEAL_FIELDS",
            unexpected_fields=unexpected,
        )

    reveal_ref = _string(reveal.get("documentary_reveal_ref"))
    source_refs = _string_list(reveal.get("documentary_source_refs"))
    blinding_ref = _string(reveal.get("blinding_audit_ref"))
    leakage_ref = _string(reveal.get("leakage_audit_ref"))
    identity_state = reveal.get("identity_blinding_state")
    identity_risk_refs = _string_list(reveal.get("identity_risk_refs"))
    pre_sha = reveal.get("pre_reveal_structural_output_sha256")
    post_sha = reveal.get("post_reveal_structural_output_sha256")

    if reveal_ref is None:
        return _blocked("DOCUMENTARY_REVEAL_REF_REQUIRED")
    if not source_refs:
        return _blocked("DOCUMENTARY_SOURCE_REFS_REQUIRED")
    if blinding_ref is None:
        return _blocked("BLINDING_AUDIT_REF_REQUIRED")
    if leakage_ref is None:
        return _blocked("LEAKAGE_AUDIT_REF_REQUIRED")
    if not _valid_sha(pre_sha) or not _valid_sha(post_sha):
        return _blocked("STRUCTURAL_OUTPUT_FINGERPRINT_INVALID")
    if pre_sha != post_sha:
        return _blocked("POST_REVEAL_STRUCTURAL_MUTATION")
    if identity_state not in ("BLINDED", "UNAVOIDABLE_PUBLIC"):
        return _blocked("INVALID_IDENTITY_BLINDING_STATE")
    if identity_risk_refs is None:
        return _blocked("IDENTITY_RISK_REFS_INVALID")
    if identity_state == "UNAVOIDABLE_PUBLIC" and not identity_risk_refs:
        return _blocked("PUBLIC_IDENTITY_RISK_REF_REQUIRED")

    counts: dict[str, int] = {}
    for key in (
        "forbidden_field_hits",
        "label_leakage_count",
        "narrative_leakage_count",
        "case_fitting_count",
        "post_holdout_rule_change_count",
    ):
        value = reveal.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            return _blocked("INVALID_LEAKAGE_COUNT", count_field=key)
        counts[key] = int(value)
        if value != 0:
            return _blocked("LEAKAGE_OR_CASE_FITTING_DETECTED", count_field=key)

    record = {
        "schema_version": "1.0.0",
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "validation_id": str(certificate["validation_id"]),
        "candidate_id": str(certificate["candidate_id"]),
        "formula_ref": str(certificate["formula_ref"]),
        "cohort_id": str(certificate["cohort_id"]),
        "documentary_reveal_ref": reveal_ref,
        "documentary_source_refs": source_refs,
        "documentary_source_count": len(source_refs),
        "blinding_audit_ref": blinding_ref,
        "leakage_audit_ref": leakage_ref,
        "continuity_certificate_sha256": certificate_sha,
        "holdout_distribution_fingerprint_sha256": str(
            certificate["holdout_distribution_fingerprint_sha256"]
        ),
        "pre_reveal_structural_output_sha256": str(pre_sha),
        "post_reveal_structural_output_sha256": str(post_sha),
        "structural_output_invariant": True,
        "identity_blinding_state": str(identity_state),
        "identity_risk_refs": identity_risk_refs,
        **counts,
        "private_payloads_exposed": False,
        "promotion_decision": "FORBIDDEN",
        "automatic_registry_mutation": False,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
    record_sha = _sha(record)
    return {
        "state": "DOCUMENTARY_REVEAL_READY",
        "record": record,
        "record_sha256": record_sha,
    }


def record_documentary_reveal(
    continuity: Mapping[str, Any],
    ledger: Mapping[str, Any],
    reveal: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Genera V5-A y lo enlaza como cuarto evento del ledger."""

    if policy is None:
        policy = load_validation_closure_release_audit_policy()

    built = build_documentary_reveal_record(
        continuity,
        ledger,
        reveal,
        policy=policy,
    )
    if built.get("state") != "DOCUMENTARY_REVEAL_READY":
        return built

    record = built["record"]
    appended = append_validation_event(
        ledger,
        event_type="DOCUMENTARY_REVEALED",
        artifact_ref=str(record["documentary_reveal_ref"]),
        artifact_sha256=str(built["record_sha256"]),
    )
    if appended.get("state") != "LEDGER_ACTIVE":
        return _blocked(
            "DOCUMENTARY_REVEAL_LEDGER_APPEND_FAILED",
            ledger_reason=appended.get("reason"),
        )

    return {
        "state": "DOCUMENTARY_REVEALED",
        "record": record,
        "record_sha256": built["record_sha256"],
        "ledger": appended["ledger"],
        "automatic_registry_mutation": False,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }


def close_validation_cycle(
    continuity: Mapping[str, Any],
    promotion_result: Mapping[str, Any],
    reveal_result: Mapping[str, Any],
    ledger: Mapping[str, Any],
    closure_request: Mapping[str, Any],
    *,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Cierra V5 y produce un paquete agregado para auditoría de release."""

    if policy is None:
        policy = load_validation_closure_release_audit_policy()

    certificate, certificate_sha, error = _validated_continuity(
        continuity, policy
    )
    if error is not None:
        return error
    assert certificate is not None
    assert certificate_sha is not None

    if reveal_result.get("state") != "DOCUMENTARY_REVEALED":
        return _blocked("DOCUMENTARY_REVEAL_REQUIRED")
    reveal_record = reveal_result.get("record")
    reveal_sha = reveal_result.get("record_sha256")
    if not isinstance(reveal_record, Mapping) or not _valid_sha(reveal_sha):
        return _blocked("INVALID_DOCUMENTARY_REVEAL_ARTIFACT")
    if _sha(dict(reveal_record)) != reveal_sha:
        return _blocked("DOCUMENTARY_REVEAL_FINGERPRINT_MISMATCH")
    if reveal_record.get("validation_id") != certificate.get("validation_id"):
        return _blocked("REVEAL_VALIDATION_ID_MISMATCH")
    if (
        reveal_record.get("continuity_certificate_sha256")
        != certificate_sha
    ):
        return _blocked("REVEAL_CONTINUITY_LINK_MISMATCH")

    ledger_error = _validated_ledger(
        ledger,
        policy=policy,
        expected_event="DOCUMENTARY_REVEALED",
        validation_id=str(certificate["validation_id"]),
    )
    if ledger_error is not None:
        return ledger_error
    entries = ledger.get("entries")
    if not isinstance(entries, list) or len(entries) != 4:
        return _blocked("LEDGER_NOT_AT_CLOSURE_BOUNDARY")
    if entries[3].get("artifact_sha256") != reveal_sha:
        return _blocked("REVEAL_LEDGER_ARTIFACT_MISMATCH")

    promotion_state = promotion_result.get("state")
    if promotion_state not in ("PROMOTION_ELIGIBLE", "NOT_ELIGIBLE"):
        return _blocked("S8_RESULT_REQUIRED")
    if (
        promotion_result.get("candidate_id") != certificate.get("candidate_id")
        or promotion_result.get("formula_ref") != certificate.get("formula_ref")
    ):
        return _blocked("S8_CANDIDATE_CONTINUITY_MISMATCH")
    if promotion_result.get("validation_continuity_verified") is not True:
        return _blocked("S8_CONTINUITY_NOT_VERIFIED")
    if (
        promotion_result.get("validation_continuity_certificate_sha256")
        != certificate_sha
    ):
        return _blocked("S8_CONTINUITY_CERTIFICATE_MISMATCH")

    illegal_flags = (
        "automatic_registry_mutation",
        "active_in_scoring",
        "scoring_enabled",
        "weighting_enabled",
        "ontology_enabled",
        "l3_validation",
        "metaphysical_probability",
    )
    if any(
        promotion_result.get(key) not in (False, None)
        for key in illegal_flags
    ):
        return _blocked("ILLEGAL_S8_ACTIVATION_FLAG")

    allowed_closure = {
        "closure_ref",
        "release_audit_ref",
        "reviewer_refs",
    }
    unexpected = sorted(set(closure_request) - allowed_closure)
    if unexpected:
        return _blocked(
            "UNEXPECTED_CLOSURE_FIELDS",
            unexpected_fields=unexpected,
        )
    closure_ref = _string(closure_request.get("closure_ref"))
    release_audit_ref = _string(closure_request.get("release_audit_ref"))
    reviewer_refs = _string_list(closure_request.get("reviewer_refs"))
    if closure_ref is None:
        return _blocked("CLOSURE_REF_REQUIRED")
    if release_audit_ref is None:
        return _blocked("RELEASE_AUDIT_REF_REQUIRED")
    if reviewer_refs is None:
        return _blocked("REVIEWER_REFS_INVALID")

    validation_outcome = (
        "PROMOTION_ELIGIBLE_AWAITING_VERSIONED_ACTIVATION"
        if promotion_state == "PROMOTION_ELIGIBLE"
        else "CLOSED_NOT_ELIGIBLE"
    )
    reasons = promotion_result.get("reasons")
    if not isinstance(reasons, list):
        reasons = []
    reason_codes = sorted(
        {
            str(reason)
            for reason in reasons
            if isinstance(reason, str) and reason
        }
    )

    promotion_result_sha = _sha(dict(promotion_result))
    closure_record = {
        "schema_version": "1.0.0",
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "validation_id": str(certificate["validation_id"]),
        "candidate_id": str(certificate["candidate_id"]),
        "formula_ref": str(certificate["formula_ref"]),
        "cohort_id": str(certificate["cohort_id"]),
        "closure_ref": closure_ref,
        "continuity_certificate_sha256": certificate_sha,
        "documentary_reveal_sha256": str(reveal_sha),
        "promotion_result_sha256": promotion_result_sha,
        "promotion_state": str(promotion_state),
        "promotion_reason_codes": reason_codes,
        "validation_outcome": validation_outcome,
        "confirmatory_cycle_closed": True,
        "manual_new_version_required_for_activation": True,
        "manual_release_review_required": True,
        "same_release_activation_forbidden": True,
        "automatic_registry_mutation": False,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
    closure_sha = _sha(closure_record)

    appended = append_validation_event(
        ledger,
        event_type="VALIDATION_CLOSED",
        artifact_ref=closure_ref,
        artifact_sha256=closure_sha,
    )
    if appended.get("state") != "LEDGER_CLOSED":
        return _blocked(
            "VALIDATION_CLOSE_LEDGER_APPEND_FAILED",
            ledger_reason=appended.get("reason"),
        )
    closed_ledger = appended["ledger"]
    closed_audit = audit_validation_ledger(closed_ledger)
    if (
        closed_audit.get("state") != "LEDGER_VALID"
        or closed_audit.get("current_event") != "VALIDATION_CLOSED"
        or closed_audit.get("entry_count") != 5
    ):
        return _blocked("FINAL_LEDGER_AUDIT_FAILED")

    release_package = {
        "schema_version": "1.0.0",
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "epistemic_class": policy["epistemic_class"],
        "validation_id": str(certificate["validation_id"]),
        "candidate_id": str(certificate["candidate_id"]),
        "formula_ref": str(certificate["formula_ref"]),
        "cohort_id": str(certificate["cohort_id"]),
        "release_audit_ref": release_audit_ref,
        "reviewer_refs": reviewer_refs,
        "preregistration_sha256": str(
            certificate["preregistration_sha256"]
        ),
        "opening_sha256": str(certificate["opening_sha256"]),
        "holdout_evaluation_sha256": str(
            certificate["holdout_evaluation_sha256"]
        ),
        "holdout_distribution_fingerprint_sha256": str(
            certificate["holdout_distribution_fingerprint_sha256"]
        ),
        "continuity_certificate_sha256": certificate_sha,
        "documentary_reveal_sha256": str(reveal_sha),
        "promotion_result_sha256": promotion_result_sha,
        "validation_closure_sha256": closure_sha,
        "closed_ledger_chain_head_sha256": str(
            closed_ledger["chain_head_sha256"]
        ),
        "closed_ledger_entry_count": int(closed_ledger["entry_count"]),
        "validation_outcome": validation_outcome,
        "release_audit_ready": True,
        "private_payloads_exposed": False,
        "manual_release_review_required": True,
        "manual_new_version_required_for_activation": True,
        "same_release_activation_forbidden": True,
        "automatic_registry_mutation": False,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
    package_sha = _sha(release_package)

    return {
        "state": "VALIDATION_CLOSED_AUDIT_READY",
        "closure_record": closure_record,
        "closure_sha256": closure_sha,
        "ledger": closed_ledger,
        "release_audit_package": release_package,
        "release_audit_package_sha256": package_sha,
        "automatic_registry_mutation": False,
        "manual_release_review_required": True,
        "same_release_activation_forbidden": True,
        "scoring_activation": False,
        "weighting_activation": False,
        "ontology_activation": False,
        "l3_validation": False,
        "metaphysical_probability": False,
    }
