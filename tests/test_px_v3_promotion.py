from __future__ import annotations

import unittest

from almas_tfa.px_v3_promotion import (
    evaluate_px_v3_promotion,
    load_px_v3_promotion_gate_policy,
)


def candidate():
    return {
        "candidate_id": "PX3-P1",
        "status": "FROZEN_FOR_VALIDATION",
        "target": "PX",
        "descriptor_ids": ["NON_DRACONIC_RECURRENCE"],
        "formula_ref": "FORMULA:PX3-P1:v1",
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


def holdout():
    return {
        "state": "HOLDOUT_EVALUATED_DIAGNOSTIC_ONLY",
        "candidate_id": "PX3-P1",
        "formula_ref": "FORMULA:PX3-P1:v1",
        "distribution_fingerprint_sha256": "abc123",
        "promotion_decision": "FORBIDDEN",
        "candidate_validated": False,
    }


def evidence(**overrides):
    base = {
        "candidate": candidate(),
        "holdout_evaluations": [holdout()],
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
    base.update(overrides)
    return base


class PxV3PromotionGateTests(unittest.TestCase):
    def test_policy_requires_manual_activation(self):
        policy = load_px_v3_promotion_gate_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_PX_V3_PROMOTION_GATE_V1",
        )
        self.assertTrue(
            policy["principles"]["manual_new_version_required_for_activation"]
        )
        self.assertTrue(
            policy["principles"]["automatic_registry_mutation_forbidden"]
        )
        self.assertFalse(policy["principles"]["scoring_enabled"])

    def test_complete_evidence_is_promotion_eligible_but_inactive(self):
        result = evaluate_px_v3_promotion(evidence())
        self.assertEqual(result["state"], "PROMOTION_ELIGIBLE")
        self.assertEqual(result["reasons"], [])
        self.assertFalse(result["automatic_registry_mutation"])
        self.assertTrue(result["manual_new_version_required_for_activation"])
        self.assertFalse(result["active_in_scoring"])
        self.assertFalse(result["scoring_enabled"])
        self.assertFalse(result["ontology_enabled"])

    def test_failed_preregistered_criterion_blocks_eligibility(self):
        result = evaluate_px_v3_promotion(
            evidence(
                criterion_results=[
                    {
                        "criterion_id": "CRIT-1",
                        "preregistration_ref": "PREREG-1",
                        "evaluation_ref": "EVAL-1",
                        "passed": False,
                    }
                ]
            )
        )
        self.assertEqual(result["state"], "NOT_ELIGIBLE")
        self.assertIn("PREREGISTERED_CRITERION_FAILED", result["reasons"])

    def test_case_fitting_blocks_eligibility(self):
        result = evaluate_px_v3_promotion(
            evidence(case_fitting_count=1)
        )
        self.assertEqual(result["state"], "NOT_ELIGIBLE")
        self.assertIn("CASE_FITTING_COUNT", result["reasons"])

    def test_post_holdout_rule_change_blocks_eligibility(self):
        result = evaluate_px_v3_promotion(
            evidence(post_holdout_rule_change_count=1)
        )
        self.assertEqual(result["state"], "NOT_ELIGIBLE")
        self.assertIn(
            "POST_HOLDOUT_RULE_CHANGE_COUNT",
            result["reasons"],
        )

    def test_missing_independent_replication_blocks(self):
        result = evaluate_px_v3_promotion(
            evidence(independent_replication_refs=[])
        )
        self.assertEqual(result["state"], "NOT_ELIGIBLE")
        self.assertIn(
            "INSUFFICIENT_INDEPENDENT_REPLICATION_REFS",
            result["reasons"],
        )

    def test_formula_mismatch_holdout_blocks(self):
        bad = holdout()
        bad["formula_ref"] = "OTHER"
        result = evaluate_px_v3_promotion(
            evidence(holdout_evaluations=[bad])
        )
        self.assertEqual(result["state"], "NOT_ELIGIBLE")
        self.assertIn("HOLDOUT_FORMULA_REF_MISMATCH", result["reasons"])

    def test_unfrozen_candidate_blocks(self):
        c = candidate()
        c["status"] = "DRAFT"
        result = evaluate_px_v3_promotion(evidence(candidate=c))
        self.assertEqual(result["state"], "NOT_ELIGIBLE")
        self.assertIn(
            "CANDIDATE_NOT_FROZEN_FOR_VALIDATION",
            result["reasons"],
        )

    def test_leakage_blocks(self):
        result = evaluate_px_v3_promotion(
            evidence(label_leakage_count=1)
        )
        self.assertEqual(result["state"], "NOT_ELIGIBLE")
        self.assertIn("LABEL_LEAKAGE_COUNT", result["reasons"])


if __name__ == "__main__":
    unittest.main()
