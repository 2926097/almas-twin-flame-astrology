from __future__ import annotations

import unittest

from almas_tfa.px_v3_holdout import (
    evaluate_px_v3_holdout,
    load_px_v3_holdout_evaluation_policy,
)


def snapshot():
    return {
        "pillar_attribution": {
            "semantic_motifs": {},
            "recurrence_quality": {},
        }
    }


def sample(ref, *, contamination=False, status="EXTERNAL_HOLDOUT"):
    return {
        "sample_ref": ref,
        "validation_status": status,
        "selection_status": "PREREGISTERED",
        "label_blinding": "BLINDED",
        "contamination": contamination,
        "forbidden_field_hits": 0,
        "label_leakage_count": 0,
        "narrative_leakage_count": 0,
        "case_fitting_count": 0,
        "recurrence_snapshot": snapshot(),
    }


def cohort(samples):
    return {
        "cohort_id": "HOLDOUT-C1",
        "preregistration_ref": "PREREG-H1",
        "null_model": "PAIR_SHUFFLE",
        "frozen_almas_version": "1.15.0-dev",
        "frozen_commit_sha": "abcdef1234567890",
        "feature_set_ref": "FEATURES-1",
        "orb_policy_ref": "ORBS-1",
        "pairing_rule_ref": "PAIR-1",
        "inclusion_rule_ref": "INCLUDE-1",
        "samples": samples,
    }


def candidate(**overrides):
    base = {
        "candidate_id": "PX3-H1",
        "status": "FROZEN_FOR_VALIDATION",
        "target": "PX",
        "descriptor_ids": ["NON_DRACONIC_RECURRENCE"],
        "formula_ref": "FORMULA:PX3-H1:v1",
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
    base.update(overrides)
    return base


def scores(values, formula_ref="FORMULA:PX3-H1:v1"):
    return {
        "formula_ref": formula_ref,
        "evaluation_engine_ref": "ENGINE:PX3-EVAL:v1",
        "scores": [
            {"sample_ref": ref, "candidate_value": value}
            for ref, value in values
        ],
    }


class PxV3HoldoutTests(unittest.TestCase):
    def test_policy_forbids_promotion_and_scoring(self):
        policy = load_px_v3_holdout_evaluation_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_PX_V3_HOLDOUT_EVALUATION_V1",
        )
        self.assertTrue(
            policy["principles"]["candidate_must_be_frozen_for_validation"]
        )
        self.assertTrue(
            policy["principles"]["development_overlap_forbidden"]
        )
        self.assertFalse(policy["principles"]["scoring_enabled"])
        self.assertFalse(policy["principles"]["weighting_enabled"])

    def test_clean_holdout_returns_aggregate_distribution_only(self):
        data = cohort([sample("H1"), sample("H2"), sample("H3")])
        result = evaluate_px_v3_holdout(
            candidate(),
            data,
            scores([("H1", 0.2), ("H2", 0.5), ("H3", 0.8)]),
        )
        self.assertEqual(
            result["state"],
            "HOLDOUT_EVALUATED_DIAGNOSTIC_ONLY",
        )
        self.assertEqual(result["clean_holdout_sample_count"], 3)
        self.assertAlmostEqual(result["distribution"]["mean"], 0.5)
        self.assertAlmostEqual(result["distribution"]["median"], 0.5)
        self.assertFalse(result["sample_identifiers_exposed"])
        self.assertFalse(result["sample_values_exposed"])
        self.assertEqual(result["promotion_decision"], "FORBIDDEN")
        self.assertFalse(result["candidate_validated"])

    def test_contaminated_sample_is_excluded(self):
        data = cohort([
            sample("H1"),
            sample("H2", contamination=True),
        ])
        result = evaluate_px_v3_holdout(
            candidate(),
            data,
            scores([("H1", 0.4)]),
        )
        self.assertEqual(result["clean_holdout_sample_count"], 1)
        self.assertEqual(result["distribution"]["count"], 1)

    def test_development_holdout_overlap_fails_closed(self):
        data = cohort([sample("DEV-A")])
        result = evaluate_px_v3_holdout(
            candidate(),
            data,
            scores([("DEV-A", 0.4)]),
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertEqual(result["reason"], "DEVELOPMENT_HOLDOUT_OVERLAP")

    def test_formula_ref_mismatch_raises(self):
        data = cohort([sample("H1")])
        with self.assertRaises(ValueError):
            evaluate_px_v3_holdout(
                candidate(),
                data,
                scores([("H1", 0.4)], formula_ref="OTHER"),
            )

    def test_missing_score_fails_closed(self):
        data = cohort([sample("H1"), sample("H2")])
        result = evaluate_px_v3_holdout(
            candidate(),
            data,
            scores([("H1", 0.4)]),
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertEqual(
            result["reason"],
            "INCOMPLETE_HOLDOUT_SCORE_COVERAGE",
        )

    def test_unfrozen_candidate_cannot_run(self):
        data = cohort([sample("H1")])
        result = evaluate_px_v3_holdout(
            candidate(status="DRAFT"),
            data,
            scores([("H1", 0.4)]),
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertFalse(result["scoring_enabled"])

    def test_distribution_fingerprint_is_deterministic(self):
        data = cohort([sample("H1"), sample("H2")])
        bundle = scores([("H1", 0.3), ("H2", 0.7)])
        a = evaluate_px_v3_holdout(candidate(), data, bundle)
        b = evaluate_px_v3_holdout(candidate(), data, bundle)
        self.assertEqual(
            a["distribution_fingerprint_sha256"],
            b["distribution_fingerprint_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
