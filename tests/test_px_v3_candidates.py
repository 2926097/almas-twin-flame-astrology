from __future__ import annotations

from copy import deepcopy
import unittest

from almas_tfa.px_v3_candidates import (
    evaluate_px_v3_candidate,
    evaluate_px_v3_candidate_registry,
    load_px_v3_candidate_freeze_policy,
    load_px_v3_candidate_registry,
)


def candidate(candidate_id="PX3-C1", **overrides):
    base = {
        "candidate_id": candidate_id,
        "status": "FROZEN_FOR_VALIDATION",
        "target": "PX",
        "descriptor_ids": [
            "NON_DRACONIC_RECURRENCE",
            "LEAVE_ONE_CLASS_OUT_SURVIVAL",
        ],
        "formula_ref": "FORMULA:PX3-C1:v1",
        "expected_direction": "HIGHER_IS_MORE_SPECIFIC",
        "development_case_refs": ["DEV-CASE-A"],
        "s2_refs": ["S2-REF-A"],
        "s3_refs": ["S3-REF-A"],
        "ablation_refs": ["AB-REF-A"],
        "negative_control_refs": ["NEG-REF-A"],
        "falsification_criteria": [
            "Retirar si no supera controles externos preregistrados."
        ],
        "holdout_refs": [],
        "formula_frozen_before_holdout": True,
        "holdout_fitted_thresholds": False,
        "scoring_enabled": False,
        "ontology_enabled": False,
        "notes": [],
    }
    base.update(overrides)
    return base


class PxV3CandidateTests(unittest.TestCase):
    def test_canonical_registry_is_empty_and_non_scoring(self):
        registry = load_px_v3_candidate_registry()
        self.assertEqual(registry["records"], [])
        self.assertFalse(registry["scoring_enabled"])
        self.assertFalse(registry["weighting_enabled"])
        self.assertFalse(registry["ontology_enabled"])
        self.assertEqual(registry["validated_candidate_ids"], [])

        result = evaluate_px_v3_candidate_registry(registry)
        self.assertEqual(result["record_count"], 0)
        self.assertEqual(result["scoring_candidate_count"], 0)
        self.assertEqual(result["validated_candidate_count"], 0)

    def test_policy_freezes_before_holdout(self):
        policy = load_px_v3_candidate_freeze_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_PX_V3_CANDIDATE_FREEZE_V1",
        )
        self.assertTrue(policy["principles"]["freeze_before_holdout"])
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertFalse(policy["principles"]["scoring_enabled"])
        self.assertFalse(policy["principles"]["weighting_enabled"])

    def test_clean_candidate_can_be_frozen_for_validation_only(self):
        result = evaluate_px_v3_candidate(candidate())
        self.assertTrue(result["frozen_for_validation"])
        self.assertEqual(result["freeze_violations"], [])
        self.assertFalse(result["scoring_enabled"])
        self.assertFalse(result["weighting_enabled"])
        self.assertFalse(result["ontology_enabled"])
        self.assertFalse(result["l3_validation"])

    def test_holdout_already_seen_blocks_freeze(self):
        result = evaluate_px_v3_candidate(
            candidate(holdout_refs=["HOLDOUT-1"])
        )
        self.assertFalse(result["frozen_for_validation"])
        self.assertIn(
            "HOLDOUT_ALREADY_OBSERVED_AT_FREEZE",
            result["freeze_violations"],
        )

    def test_holdout_fitted_threshold_blocks_freeze(self):
        result = evaluate_px_v3_candidate(
            candidate(holdout_fitted_thresholds=True)
        )
        self.assertFalse(result["frozen_for_validation"])
        self.assertIn(
            "HOLDOUT_FITTED_THRESHOLDS",
            result["freeze_violations"],
        )

    def test_formula_not_frozen_blocks_freeze(self):
        result = evaluate_px_v3_candidate(
            candidate(formula_frozen_before_holdout=False)
        )
        self.assertFalse(result["frozen_for_validation"])
        self.assertIn(
            "FORMULA_NOT_FROZEN_BEFORE_HOLDOUT",
            result["freeze_violations"],
        )

    def test_unknown_descriptor_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_px_v3_candidate(
                candidate(descriptor_ids=["CASE_SPECIFIC_MAGIC"])
            )

    def test_scoring_enable_attempt_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_px_v3_candidate(
                candidate(scoring_enabled=True)
            )

    def test_duplicate_candidate_ids_are_rejected(self):
        registry = deepcopy(load_px_v3_candidate_registry())
        registry["status"] = "CANDIDATES_PRESENT"
        registry["records"] = [candidate("C1"), candidate("C1")]
        with self.assertRaises(ValueError):
            evaluate_px_v3_candidate_registry(registry)

    def test_validated_ids_are_forbidden_in_s6(self):
        registry = deepcopy(load_px_v3_candidate_registry())
        registry["validated_candidate_ids"] = ["C1"]
        with self.assertRaises(ValueError):
            evaluate_px_v3_candidate_registry(registry)


if __name__ == "__main__":
    unittest.main()
