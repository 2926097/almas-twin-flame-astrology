from __future__ import annotations

from copy import deepcopy
import unittest

from almas_tfa.validation_preregistration import (
    build_validation_preregistration_bundle,
    load_validation_preregistration_bundle_policy,
)


def candidate(**overrides):
    data = {
        "candidate_id": "PX3-C1",
        "status": "FROZEN_FOR_VALIDATION",
        "target": "PX",
        "descriptor_ids": [
            "NON_DRACONIC_RECURRENCE",
            "LEAVE_ONE_CLASS_OUT_SURVIVAL",
        ],
        "formula_ref": "PX3-FORMULA-1",
        "expected_direction": "HIGHER_IS_MORE_SPECIFIC",
        "development_case_refs": ["DEV-A", "DEV-B"],
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
    data.update(overrides)
    return data


def plan(**overrides):
    data = {
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
        "independent_replication_plan_refs": ["REPL-2", "REPL-1"],
        "negative_control_refs": ["NEG-B", "NEG-A"],
        "ablation_refs": ["AB-B", "AB-A"],
        "planned_holdout_refs": ["HOLD-2", "HOLD-1"],
        "endpoints": [
            {
                "endpoint_id": "SPECIFICITY",
                "success_criterion": "SPEC-PASS",
                "failure_criterion": "SPEC-FAIL",
            },
            {
                "endpoint_id": "NEGATIVE_CONTROL_FALSE_SPECIFICITY",
                "success_criterion": "NEG-PASS",
                "failure_criterion": "NEG-FAIL",
            },
            {
                "endpoint_id": "ABLATION_STABILITY",
                "success_criterion": "ABL-PASS",
                "failure_criterion": "ABL-FAIL",
            },
            {
                "endpoint_id": "REPLICATION_STABILITY",
                "success_criterion": "REP-PASS",
                "failure_criterion": "REP-FAIL",
            },
            {
                "endpoint_id": "LEAKAGE_ZERO",
                "success_criterion": "LEAK-PASS",
                "failure_criterion": "LEAK-FAIL",
            },
            {
                "endpoint_id": "NO_POSTHOC_CHANGE",
                "success_criterion": "POST-PASS",
                "failure_criterion": "POST-FAIL",
            },
        ],
    }
    data.update(overrides)
    return data


class ValidationPreregistrationTests(unittest.TestCase):
    def test_policy_preserves_firewalls(self):
        policy = load_validation_preregistration_bundle_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_VALIDATION_PREREGISTRATION_BUNDLE_V1",
        )
        self.assertTrue(
            policy["principles"]["candidate_must_be_frozen_for_validation"]
        )
        self.assertTrue(policy["principles"]["raw_holdout_samples_forbidden"])
        self.assertTrue(
            policy["principles"]["observed_holdout_results_forbidden"]
        )
        self.assertFalse(policy["principles"]["scoring_enabled"])
        self.assertFalse(policy["principles"]["metaphysical_probability"])

    def test_valid_bundle_is_deterministic_and_locked(self):
        a = build_validation_preregistration_bundle(candidate(), plan())
        b_plan = plan()
        b_plan["independent_replication_plan_refs"] = ["REPL-1", "REPL-2"]
        b_plan["negative_control_refs"] = ["NEG-A", "NEG-B"]
        b_plan["ablation_refs"] = ["AB-A", "AB-B"]
        b_plan["planned_holdout_refs"] = ["HOLD-1", "HOLD-2"]
        b_plan["endpoints"] = list(reversed(b_plan["endpoints"]))
        b = build_validation_preregistration_bundle(candidate(), b_plan)

        self.assertEqual(a["state"], "PREREGISTERED_READY")
        self.assertEqual(a["bundle_sha256"], b["bundle_sha256"])
        self.assertEqual(len(a["bundle_sha256"]), 64)
        self.assertFalse(a["bundle"]["holdout_opened"])
        self.assertFalse(a["bundle"]["observed_results_present"])
        self.assertFalse(a["bundle"]["raw_samples_present"])
        self.assertFalse(a["scoring_enabled"])
        self.assertFalse(a["metaphysical_probability"])

    def test_observed_or_raw_holdout_material_is_rejected(self):
        bad = plan()
        bad["cohort_plan"]["samples"] = [{"sample_ref": "SECRET"}]
        result = build_validation_preregistration_bundle(
            candidate(), bad
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertEqual(
            result["reason"],
            "FORBIDDEN_PREREGISTRATION_KEYS",
        )
        self.assertIn("samples", result["forbidden_keys"])

    def test_development_holdout_overlap_is_rejected(self):
        bad = plan(planned_holdout_refs=["DEV-A", "HOLD-9"])
        result = build_validation_preregistration_bundle(
            candidate(), bad
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertEqual(
            result["reason"],
            "DEVELOPMENT_HOLDOUT_OVERLAP",
        )
        self.assertEqual(result["overlap_refs"], ["DEV-A"])

    def test_candidate_must_be_frozen(self):
        result = build_validation_preregistration_bundle(
            candidate(status="DRAFT"),
            plan(),
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertEqual(
            result["reason"],
            "CANDIDATE_NOT_FROZEN_FOR_VALIDATION",
        )

    def test_missing_required_endpoint_fails_closed(self):
        bad = plan()
        bad["endpoints"] = [
            item
            for item in bad["endpoints"]
            if item["endpoint_id"] != "LEAKAGE_ZERO"
        ]
        result = build_validation_preregistration_bundle(
            candidate(), bad
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertIn("Faltan endpoints requeridos", result["reason"])

    def test_changing_frozen_criterion_changes_fingerprint(self):
        a = build_validation_preregistration_bundle(candidate(), plan())
        changed = deepcopy(plan())
        changed["endpoints"][0]["success_criterion"] = "SPEC-PASS-V2"
        b = build_validation_preregistration_bundle(candidate(), changed)
        self.assertNotEqual(a["bundle_sha256"], b["bundle_sha256"])


if __name__ == "__main__":
    unittest.main()
