from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import unittest

from almas_tfa.holdout_open import evaluate_holdout_open
from almas_tfa.validation_closure import (
    build_documentary_reveal_record,
    close_validation_cycle,
    load_validation_closure_release_audit_policy,
    record_documentary_reveal,
)
from almas_tfa.validation_continuity import (
    evaluate_px_v3_promotion_with_continuity,
    evaluate_validation_continuity,
)
from almas_tfa.validation_ledger import (
    append_validation_event,
    initialize_validation_ledger,
)
from almas_tfa.validation_preregistration import (
    build_validation_preregistration_bundle,
)


def _sha(value):
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(raw).hexdigest()


def candidate():
    return {
        "candidate_id": "PX3-V5",
        "status": "FROZEN_FOR_VALIDATION",
        "target": "PX",
        "descriptor_ids": ["NON_DRACONIC_RECURRENCE"],
        "formula_ref": "FORMULA:PX3-V5:v1",
        "expected_direction": "HIGHER_IS_MORE_SPECIFIC",
        "development_case_refs": ["DEV-A"],
        "s2_refs": ["S2-A"],
        "s3_refs": ["S3-A"],
        "ablation_refs": ["AB-A"],
        "negative_control_refs": ["NEG-A"],
        "falsification_criteria": ["Retirar si falla holdout."],
        "holdout_refs": [],
        "formula_frozen_before_holdout": True,
        "holdout_fitted_thresholds": False,
        "scoring_enabled": False,
        "ontology_enabled": False,
        "notes": [],
    }


def plan():
    return {
        "validation_id": "VAL-V5",
        "preregistration_ref": "PREREG-V5",
        "frozen_almas_version": "1.16.0",
        "frozen_commit_sha": "abcdef1234567890",
        "cohort_plan": {
            "cohort_id": "HOLDOUT-V5",
            "null_model": "PAIR_SHUFFLE",
            "feature_set_ref": "FEATURES-V1",
            "orb_policy_ref": "ORBS-V1",
            "pairing_rule_ref": "PAIR-RULE-V1",
            "inclusion_rule_ref": "INCLUDE-V1",
            "planned_min_samples": 40,
        },
        "blinding_plan_ref": "BLIND-V1",
        "leakage_audit_plan_ref": "LEAK-V1",
        "independent_replication_plan_refs": ["REPL-V1"],
        "negative_control_refs": ["NEG-V1"],
        "ablation_refs": ["AB-V1"],
        "planned_holdout_refs": ["HOLD-A", "HOLD-B"],
        "endpoints": [
            {"endpoint_id": "SPECIFICITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "NEGATIVE_CONTROL_FALSE_SPECIFICITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "ABLATION_STABILITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "REPLICATION_STABILITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "LEAKAGE_ZERO", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "NO_POSTHOC_CHANGE", "success_criterion": "A", "failure_criterion": "B"},
        ],
    }


def open_request():
    return {
        "runtime_almas_version": "1.16.0",
        "runtime_commit_sha": "abcdef1234567890",
        "candidate_id": "PX3-V5",
        "formula_ref": "FORMULA:PX3-V5:v1",
        "cohort_header": {
            "cohort_id": "HOLDOUT-V5",
            "null_model": "PAIR_SHUFFLE",
            "feature_set_ref": "FEATURES-V1",
            "orb_policy_ref": "ORBS-V1",
            "pairing_rule_ref": "PAIR-RULE-V1",
            "inclusion_rule_ref": "INCLUDE-V1",
            "sample_count": 40,
        },
    }


def holdout_result():
    return {
        "state": "HOLDOUT_EVALUATED_DIAGNOSTIC_ONLY",
        "policy_id": "ALMAS_PX_V3_HOLDOUT_EVALUATION_V1",
        "policy_status": "FROZEN_EXPERIMENTAL_PROTOCOL",
        "epistemic_class": "E_PROJECT_POLICY",
        "candidate_id": "PX3-V5",
        "formula_ref": "FORMULA:PX3-V5:v1",
        "evaluation_engine_ref": "ENGINE-V1",
        "cohort_id": "HOLDOUT-V5",
        "null_model": "PAIR_SHUFFLE",
        "clean_holdout_sample_count": 38,
        "distribution": {
            "count": 38,
            "mean": 0.5,
            "median": 0.5,
            "min": 0.1,
            "max": 0.9,
            "p10_nearest_rank": 0.2,
            "p90_nearest_rank": 0.8,
        },
        "distribution_fingerprint_sha256": "1" * 64,
        "cohort_summary": {},
        "sample_identifiers_exposed": False,
        "sample_values_exposed": False,
        "promotion_decision": "FORBIDDEN",
        "candidate_validated": False,
        "scoring_enabled": False,
        "weighting_enabled": False,
        "ontology_enabled": False,
        "l3_validation": False,
        "metaphysical_probability": False,
        "population_probability_claim": False,
    }


def promotion_evidence(holdout):
    return {
        "candidate": candidate(),
        "holdout_evaluations": [holdout],
        "external_calibration_refs": ["EXT-CAL-1"],
        "independent_replication_refs": ["REPL-1"],
        "leakage_audit_refs": ["LEAK-1"],
        "criterion_results": [
            {
                "criterion_id": "CRIT-1",
                "preregistration_ref": "PREREG-CRIT-1",
                "evaluation_ref": "EVAL-CRIT-1",
                "passed": True,
            }
        ],
        "negative_control_failure_count": 0,
        "ablation_failure_count": 0,
        "case_fitting_count": 0,
        "label_leakage_count": 0,
        "narrative_leakage_count": 0,
        "post_holdout_rule_change_count": 0,
    }


def reveal_request():
    return {
        "documentary_reveal_ref": "REVEAL-V5",
        "documentary_source_refs": ["DOC-1", "DOC-2"],
        "blinding_audit_ref": "BLIND-AUDIT-V5",
        "leakage_audit_ref": "LEAK-AUDIT-V5",
        "pre_reveal_structural_output_sha256": "2" * 64,
        "post_reveal_structural_output_sha256": "2" * 64,
        "identity_blinding_state": "BLINDED",
        "identity_risk_refs": [],
        "forbidden_field_hits": 0,
        "label_leakage_count": 0,
        "narrative_leakage_count": 0,
        "case_fitting_count": 0,
        "post_holdout_rule_change_count": 0,
    }


def closure_request():
    return {
        "closure_ref": "CLOSE-V5",
        "release_audit_ref": "RELEASE-AUDIT-V5",
        "reviewer_refs": [],
    }


def chain():
    pre = build_validation_preregistration_bundle(candidate(), plan())
    opening = evaluate_holdout_open(pre, open_request())
    ledger = initialize_validation_ledger(pre)["ledger"]
    ledger = append_validation_event(
        ledger,
        event_type="HOLDOUT_OPENED",
        artifact_ref="OPEN-V5",
        artifact_sha256=opening["opening_sha256"],
    )["ledger"]
    holdout = holdout_result()
    ledger = append_validation_event(
        ledger,
        event_type="HOLDOUT_EVALUATED",
        artifact_ref="HOLDOUT-EVAL-V5",
        artifact_sha256=_sha(holdout),
    )["ledger"]
    continuity = evaluate_validation_continuity(
        pre, opening, holdout, ledger
    )
    promotion = evaluate_px_v3_promotion_with_continuity(
        promotion_evidence(holdout),
        continuity,
    )
    return continuity, promotion, ledger


class ValidationClosureTests(unittest.TestCase):
    def test_policy_locks_release_activation_firewall(self):
        policy = load_validation_closure_release_audit_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_VALIDATION_CLOSURE_RELEASE_AUDIT_V1",
        )
        principles = policy["principles"]
        self.assertTrue(principles["structural_output_invariance_required"])
        self.assertTrue(principles["manual_release_review_required"])
        self.assertTrue(principles["same_release_activation_forbidden"])
        self.assertFalse(principles["scoring_activation"])
        self.assertFalse(principles["metaphysical_probability"])

    def test_valid_reveal_appends_fourth_ledger_event(self):
        continuity, _, ledger = chain()
        result = record_documentary_reveal(
            continuity, ledger, reveal_request()
        )
        self.assertEqual(result["state"], "DOCUMENTARY_REVEALED")
        self.assertEqual(result["ledger"]["entry_count"], 4)
        self.assertEqual(
            result["ledger"]["current_event"],
            "DOCUMENTARY_REVEALED",
        )
        self.assertTrue(result["record"]["structural_output_invariant"])
        self.assertFalse(result["record"]["private_payloads_exposed"])

    def test_reveal_blocks_structural_mutation(self):
        continuity, _, ledger = chain()
        request = reveal_request()
        request["post_reveal_structural_output_sha256"] = "3" * 64
        result = build_documentary_reveal_record(
            continuity, ledger, request
        )
        self.assertEqual(result["state"], "BLOCKED_VALIDATION_CLOSURE")
        self.assertEqual(result["reason"], "POST_REVEAL_STRUCTURAL_MUTATION")

    def test_reveal_blocks_leakage(self):
        continuity, _, ledger = chain()
        request = reveal_request()
        request["label_leakage_count"] = 1
        result = build_documentary_reveal_record(
            continuity, ledger, request
        )
        self.assertEqual(
            result["reason"],
            "LEAKAGE_OR_CASE_FITTING_DETECTED",
        )

    def test_reveal_rejects_unexpected_payload_field(self):
        continuity, _, ledger = chain()
        request = reveal_request()
        request["raw_narrative"] = {"text": "forbidden"}
        result = build_documentary_reveal_record(
            continuity, ledger, request
        )
        self.assertEqual(result["reason"], "UNEXPECTED_REVEAL_FIELDS")

    def test_public_identity_requires_risk_reference(self):
        continuity, _, ledger = chain()
        request = reveal_request()
        request["identity_blinding_state"] = "UNAVOIDABLE_PUBLIC"
        result = build_documentary_reveal_record(
            continuity, ledger, request
        )
        self.assertEqual(
            result["reason"],
            "PUBLIC_IDENTITY_RISK_REF_REQUIRED",
        )

    def test_eligible_cycle_closes_without_activation(self):
        continuity, promotion, ledger = chain()
        reveal = record_documentary_reveal(
            continuity, ledger, reveal_request()
        )
        result = close_validation_cycle(
            continuity,
            promotion,
            reveal,
            reveal["ledger"],
            closure_request(),
        )
        self.assertEqual(result["state"], "VALIDATION_CLOSED_AUDIT_READY")
        self.assertEqual(result["ledger"]["entry_count"], 5)
        self.assertTrue(result["ledger"]["closed"])
        self.assertEqual(
            result["closure_record"]["validation_outcome"],
            "PROMOTION_ELIGIBLE_AWAITING_VERSIONED_ACTIVATION",
        )
        package = result["release_audit_package"]
        self.assertTrue(package["release_audit_ready"])
        self.assertTrue(package["manual_release_review_required"])
        self.assertTrue(package["same_release_activation_forbidden"])
        self.assertFalse(package["automatic_registry_mutation"])
        self.assertFalse(package["scoring_activation"])
        self.assertFalse(package["l3_validation"])

    def test_noneligible_cycle_can_close_without_promotion(self):
        continuity, promotion, ledger = chain()
        reveal = record_documentary_reveal(
            continuity, ledger, reveal_request()
        )
        not_eligible = deepcopy(promotion)
        not_eligible["state"] = "NOT_ELIGIBLE"
        not_eligible["reasons"] = ["PREREGISTERED_CRITERION_FAILED"]
        result = close_validation_cycle(
            continuity,
            not_eligible,
            reveal,
            reveal["ledger"],
            closure_request(),
        )
        self.assertEqual(result["state"], "VALIDATION_CLOSED_AUDIT_READY")
        self.assertEqual(
            result["closure_record"]["validation_outcome"],
            "CLOSED_NOT_ELIGIBLE",
        )
        self.assertFalse(result["release_audit_package"]["scoring_activation"])

    def test_closure_rejects_wrong_s8_policy(self):
        continuity, promotion, ledger = chain()
        reveal = record_documentary_reveal(
            continuity, ledger, reveal_request()
        )
        bad = deepcopy(promotion)
        bad["policy_id"] = "OTHER_POLICY"
        result = close_validation_cycle(
            continuity,
            bad,
            reveal,
            reveal["ledger"],
            closure_request(),
        )
        self.assertEqual(result["reason"], "S8_POLICY_MISMATCH")

    def test_closure_rejects_s8_without_continuity_certificate(self):
        continuity, promotion, ledger = chain()
        reveal = record_documentary_reveal(
            continuity, ledger, reveal_request()
        )
        bad = deepcopy(promotion)
        bad["validation_continuity_verified"] = False
        result = close_validation_cycle(
            continuity,
            bad,
            reveal,
            reveal["ledger"],
            closure_request(),
        )
        self.assertEqual(result["reason"], "S8_CONTINUITY_NOT_VERIFIED")

    def test_closure_detects_reveal_ledger_tampering(self):
        continuity, promotion, ledger = chain()
        reveal = record_documentary_reveal(
            continuity, ledger, reveal_request()
        )
        tampered = deepcopy(reveal["ledger"])
        tampered["entries"][3]["artifact_sha256"] = "f" * 64
        result = close_validation_cycle(
            continuity,
            promotion,
            reveal,
            tampered,
            closure_request(),
        )
        self.assertEqual(result["reason"], "LEDGER_INTEGRITY_FAILURE")


if __name__ == "__main__":
    unittest.main()
