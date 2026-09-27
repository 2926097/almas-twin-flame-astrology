from __future__ import annotations

from copy import deepcopy
import unittest

from almas_tfa.holdout_open import evaluate_holdout_open
from almas_tfa.validation_preregistration import (
    build_validation_preregistration_bundle,
)


def candidate():
    return {
        "candidate_id": "PX3-C1",
        "status": "FROZEN_FOR_VALIDATION",
        "target": "PX",
        "descriptor_ids": ["NON_DRACONIC_RECURRENCE"],
        "formula_ref": "PX3-FORMULA-1",
        "expected_direction": "HIGHER_IS_MORE_SPECIFIC",
        "development_case_refs": ["DEV-A"],
        "s2_refs": ["S2-1"],
        "s3_refs": ["S3-1"],
        "ablation_refs": ["AB-1"],
        "negative_control_refs": ["NEG-1"],
        "falsification_criteria": ["FALSIFY-1"],
        "holdout_refs": [],
        "formula_frozen_before_holdout": True,
        "holdout_fitted_thresholds": False,
        "scoring_enabled": False,
        "ontology_enabled": False,
    }


def plan():
    return {
        "validation_id": "VAL-1",
        "preregistration_ref": "PREREG-VAL-1",
        "frozen_almas_version": "1.16.0-dev",
        "frozen_commit_sha": "abcdef1234567890",
        "cohort_plan": {
            "cohort_id": "HOLDOUT-C1",
            "null_model": "PAIR_SHUFFLE",
            "feature_set_ref": "FEATURES-V1",
            "orb_policy_ref": "ORBS-V1",
            "pairing_rule_ref": "PAIR-RULE-1",
            "inclusion_rule_ref": "INCLUSION-1",
            "planned_min_samples": 40,
        },
        "blinding_plan_ref": "BLIND-1",
        "leakage_audit_plan_ref": "LEAK-1",
        "independent_replication_plan_refs": ["REPL-1"],
        "negative_control_refs": ["NEG-1"],
        "ablation_refs": ["AB-1"],
        "planned_holdout_refs": ["HOLD-1", "HOLD-2"],
        "endpoints": [
            {"endpoint_id": "SPECIFICITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "NEGATIVE_CONTROL_FALSE_SPECIFICITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "ABLATION_STABILITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "REPLICATION_STABILITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "LEAKAGE_ZERO", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "NO_POSTHOC_CHANGE", "success_criterion": "A", "failure_criterion": "B"},
        ],
    }


def preregistration():
    return build_validation_preregistration_bundle(candidate(), plan())


def request():
    return {
        "runtime_almas_version": "1.16.0-dev",
        "runtime_commit_sha": "abcdef1234567890",
        "candidate_id": "PX3-C1",
        "formula_ref": "PX3-FORMULA-1",
        "cohort_header": {
            "cohort_id": "HOLDOUT-C1",
            "null_model": "PAIR_SHUFFLE",
            "feature_set_ref": "FEATURES-V1",
            "orb_policy_ref": "ORBS-V1",
            "pairing_rule_ref": "PAIR-RULE-1",
            "inclusion_rule_ref": "INCLUSION-1",
            "sample_count": 40,
        },
    }


class HoldoutOpenTests(unittest.TestCase):
    def test_valid_preregistered_holdout_opens_without_evaluation(self):
        result = evaluate_holdout_open(preregistration(), request())
        self.assertEqual(result["state"], "HOLDOUT_OPENED")
        self.assertTrue(result["holdout_evaluation_permitted"])
        self.assertFalse(result["promotion_permitted"])
        self.assertFalse(result["scoring_activation"])
        self.assertFalse(result["l3_validation"])
        self.assertEqual(len(result["opening_sha256"]), 64)
        self.assertFalse(result["opening_record"]["holdout_evaluated"])

    def test_tampered_preregistration_is_blocked(self):
        pre = preregistration()
        pre["bundle"]["cohort_plan"]["planned_min_samples"] = 5
        result = evaluate_holdout_open(pre, request())
        self.assertEqual(result["state"], "BLOCKED_HOLDOUT_OPEN")
        self.assertEqual(
            result["reason"],
            "PREREGISTRATION_FINGERPRINT_MISMATCH",
        )

    def test_runtime_commit_must_match(self):
        bad = request()
        bad["runtime_commit_sha"] = "0000000000000000"
        result = evaluate_holdout_open(preregistration(), bad)
        self.assertEqual(result["state"], "BLOCKED_HOLDOUT_OPEN")
        self.assertEqual(result["reason"], "RUNTIME_COMMIT_MISMATCH")

    def test_formula_must_match(self):
        bad = request()
        bad["formula_ref"] = "PX3-FORMULA-2"
        result = evaluate_holdout_open(preregistration(), bad)
        self.assertEqual(result["state"], "BLOCKED_HOLDOUT_OPEN")
        self.assertEqual(result["reason"], "FORMULA_REF_MISMATCH")

    def test_cohort_metadata_must_match(self):
        bad = request()
        bad["cohort_header"]["pairing_rule_ref"] = "PAIR-RULE-CHANGED"
        result = evaluate_holdout_open(preregistration(), bad)
        self.assertEqual(result["state"], "BLOCKED_HOLDOUT_OPEN")
        self.assertEqual(result["reason"], "COHORT_METADATA_MISMATCH")
        self.assertEqual(result["mismatch_field"], "pairing_rule_ref")

    def test_minimum_sample_count_must_be_met(self):
        bad = request()
        bad["cohort_header"]["sample_count"] = 39
        result = evaluate_holdout_open(preregistration(), bad)
        self.assertEqual(result["state"], "BLOCKED_HOLDOUT_OPEN")
        self.assertEqual(
            result["reason"],
            "PLANNED_MINIMUM_SAMPLE_COUNT_NOT_MET",
        )

    def test_results_are_forbidden_at_open(self):
        bad = request()
        bad["holdout_results"] = {"mean": 0.7}
        result = evaluate_holdout_open(preregistration(), bad)
        self.assertEqual(result["state"], "BLOCKED_HOLDOUT_OPEN")
        self.assertEqual(
            result["reason"],
            "OBSERVED_OR_FORBIDDEN_DATA_PRESENT_AT_OPEN",
        )
        self.assertIn("holdout_results", result["forbidden_keys"])

    def test_open_fingerprint_changes_when_sample_count_changes(self):
        a = evaluate_holdout_open(preregistration(), request())
        b_req = deepcopy(request())
        b_req["cohort_header"]["sample_count"] = 41
        b = evaluate_holdout_open(preregistration(), b_req)
        self.assertNotEqual(a["opening_sha256"], b["opening_sha256"])


if __name__ == "__main__":
    unittest.main()
