from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import unittest

from almas_tfa.holdout_open import evaluate_holdout_open
from almas_tfa.validation_continuity import (
    evaluate_px_v3_promotion_with_continuity,
    evaluate_validation_continuity,
    load_validation_continuity_gate_policy,
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
        "candidate_id": "PX3-V4",
        "status": "FROZEN_FOR_VALIDATION",
        "target": "PX",
        "descriptor_ids": ["NON_DRACONIC_RECURRENCE"],
        "formula_ref": "FORMULA:PX3-V4:v1",
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
        "validation_id": "VAL-V4",
        "preregistration_ref": "PREREG-V4",
        "frozen_almas_version": "1.16.0-dev",
        "frozen_commit_sha": "abcdef1234567890",
        "cohort_plan": {
            "cohort_id": "HOLDOUT-V4",
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
        "runtime_almas_version": "1.16.0-dev",
        "runtime_commit_sha": "abcdef1234567890",
        "candidate_id": "PX3-V4",
        "formula_ref": "FORMULA:PX3-V4:v1",
        "cohort_header": {
            "cohort_id": "HOLDOUT-V4",
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
        "candidate_id": "PX3-V4",
        "formula_ref": "FORMULA:PX3-V4:v1",
        "evaluation_engine_ref": "ENGINE-V1",
        "cohort_id": "HOLDOUT-V4",
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


def chain():
    pre = build_validation_preregistration_bundle(candidate(), plan())
    opening = evaluate_holdout_open(pre, open_request())
    ledger = initialize_validation_ledger(pre)["ledger"]
    ledger = append_validation_event(
        ledger,
        event_type="HOLDOUT_OPENED",
        artifact_ref="OPEN-V4",
        artifact_sha256=opening["opening_sha256"],
    )["ledger"]
    holdout = holdout_result()
    ledger = append_validation_event(
        ledger,
        event_type="HOLDOUT_EVALUATED",
        artifact_ref="HOLDOUT-EVAL-V4",
        artifact_sha256=_sha(holdout),
    )["ledger"]
    return pre, opening, holdout, ledger


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


class ValidationContinuityTests(unittest.TestCase):
    def test_policy_requires_cryptographic_continuity(self):
        policy = load_validation_continuity_gate_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_VALIDATION_CONTINUITY_GATE_V1",
        )
        self.assertTrue(
            policy["principles"]["ledger_hash_chain_must_be_valid"]
        )
        self.assertTrue(
            policy["principles"]["promotion_bridge_requires_continuity"]
        )
        self.assertFalse(policy["principles"]["scoring_activation"])
        self.assertFalse(policy["principles"]["metaphysical_probability"])

    def test_valid_chain_returns_continuity_certificate(self):
        pre, opening, holdout, ledger = chain()
        result = evaluate_validation_continuity(
            pre, opening, holdout, ledger
        )
        self.assertEqual(result["state"], "CONTINUITY_VERIFIED")
        self.assertEqual(len(result["certificate_sha256"]), 64)
        certificate = result["certificate"]
        self.assertTrue(certificate["continuity_verified"])
        self.assertTrue(certificate["promotion_bridge_permitted"])
        self.assertEqual(certificate["candidate_id"], "PX3-V4")
        self.assertEqual(
            certificate["holdout_distribution_fingerprint_sha256"],
            "1" * 64,
        )
        self.assertFalse(certificate["private_payloads_exposed"])
        self.assertFalse(certificate["scoring_activation"])

    def test_tampered_opening_is_blocked(self):
        pre, opening, holdout, ledger = chain()
        bad = deepcopy(opening)
        bad["opening_record"]["runtime_commit_sha"] = "changed"
        result = evaluate_validation_continuity(
            pre, bad, holdout, ledger
        )
        self.assertEqual(
            result["state"],
            "BLOCKED_VALIDATION_CONTINUITY",
        )
        self.assertEqual(
            result["reason"],
            "OPENING_FINGERPRINT_MISMATCH",
        )

    def test_holdout_formula_mismatch_is_blocked(self):
        pre, opening, holdout, ledger = chain()
        bad = deepcopy(holdout)
        bad["formula_ref"] = "FORMULA:OTHER"
        result = evaluate_validation_continuity(
            pre, opening, bad, ledger
        )
        self.assertEqual(
            result["reason"],
            "HOLDOUT_FORMULA_REF_MISMATCH",
        )

    def test_ledger_must_contain_holdout_evaluation_artifact(self):
        pre = build_validation_preregistration_bundle(candidate(), plan())
        opening = evaluate_holdout_open(pre, open_request())
        ledger = initialize_validation_ledger(pre)["ledger"]
        ledger = append_validation_event(
            ledger,
            event_type="HOLDOUT_OPENED",
            artifact_ref="OPEN-V4",
            artifact_sha256=opening["opening_sha256"],
        )["ledger"]
        result = evaluate_validation_continuity(
            pre, opening, holdout_result(), ledger
        )
        self.assertEqual(
            result["reason"],
            "LEDGER_MISSING_REQUIRED_EVENTS",
        )

    def test_promotion_bridge_rejects_missing_continuity(self):
        result = evaluate_px_v3_promotion_with_continuity(
            promotion_evidence(holdout_result()),
            {"state": "BLOCKED_VALIDATION_CONTINUITY"},
        )
        self.assertEqual(result["state"], "NOT_ELIGIBLE")
        self.assertIn(
            "VALIDATION_CONTINUITY_REQUIRED",
            result["reasons"],
        )
        self.assertFalse(result["validation_continuity_verified"])

    def test_valid_continuity_can_reach_s8_without_activation(self):
        pre, opening, holdout, ledger = chain()
        continuity = evaluate_validation_continuity(
            pre, opening, holdout, ledger
        )
        result = evaluate_px_v3_promotion_with_continuity(
            promotion_evidence(holdout),
            continuity,
        )
        self.assertEqual(result["state"], "PROMOTION_ELIGIBLE")
        self.assertTrue(result["validation_continuity_verified"])
        self.assertFalse(result["automatic_registry_mutation"])
        self.assertFalse(result["active_in_scoring"])
        self.assertFalse(result["scoring_enabled"])
        self.assertFalse(result["ontology_enabled"])


if __name__ == "__main__":
    unittest.main()
