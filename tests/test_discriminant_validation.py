import copy
import unittest

from almas_tfa.discriminant_validation import (
    evaluate_discriminant_validation,
    load_discriminant_validation_policy,
    wilson_interval,
)


PAIR = ["SOULMATE_MODEL", "TWIN_FLAME_MODEL"]


def valid_block():
    return {
        "policy_id": "ALMAS_DISCRIMINANT_VALIDATION_V1",
        "evaluation_refs": ["EVAL-1"],
        "development_evaluation_disjoint": True,
        "pairwise_results": [
            {
                "pair": PAIR,
                "positive_model": "TWIN_FLAME_MODEL",
                "tp": 240,
                "tn": 480,
                "fp": 10,
                "fn": 20,
            }
        ],
        "false_specificity": {
            "evaluable_count": 100,
            "error_count": 0,
        },
        "synthetic_adversarial": {
            "evaluable_count": 100,
            "false_specificity_count": 0,
        },
        "calibration": {
            "mode": "NOT_APPLICABLE_CATEGORICAL",
            "passed": None,
            "criterion_ref": None,
            "refs": [],
        },
    }


class TestDiscriminantValidation(unittest.TestCase):

    def test_policy_is_explicit_project_policy(self):
        policy = load_discriminant_validation_policy()
        self.assertEqual(policy["policy_id"], "ALMAS_DISCRIMINANT_VALIDATION_V1")
        self.assertEqual(policy["epistemic_class"], "E_PROJECT_POLICY")
        self.assertEqual(policy["false_specificity"]["max_ci_upper"], 0.05)

    def test_valid_block_passes_and_returns_derived_metrics(self):
        result = evaluate_discriminant_validation(
            valid_block(),
            validated_pairs=[PAIR],
        )
        self.assertLessEqual(result["false_specificity_ci_upper"], 0.05)
        self.assertEqual(result["synthetic_adversarial_false_specificity_rate"], 0.0)
        self.assertGreater(result["pairwise"][0]["specificity_ci_lower"], 0.90)

    def test_small_zero_error_control_sample_fails_by_uncertainty(self):
        block = valid_block()
        block["false_specificity"] = {
            "evaluable_count": 20,
            "error_count": 0,
        }
        with self.assertRaises(ValueError):
            evaluate_discriminant_validation(block, validated_pairs=[PAIR])

    def test_wilson_gate_makes_73_zero_error_controls_pass_but_72_fail(self):
        _, upper_73 = wilson_interval(0, 73)
        _, upper_72 = wilson_interval(0, 72)
        self.assertLessEqual(upper_73, 0.05)
        self.assertGreater(upper_72, 0.05)

    def test_poor_specificity_blocks_promotion(self):
        block = valid_block()
        block["pairwise_results"][0]["tn"] = 90
        block["pairwise_results"][0]["fp"] = 10
        with self.assertRaises(ValueError):
            evaluate_discriminant_validation(block, validated_pairs=[PAIR])

    def test_poor_sensitivity_blocks_promotion(self):
        block = valid_block()
        block["pairwise_results"][0]["tp"] = 60
        block["pairwise_results"][0]["fn"] = 40
        with self.assertRaises(ValueError):
            evaluate_discriminant_validation(block, validated_pairs=[PAIR])

    def test_false_specificity_error_blocks_when_ci_ceiling_exceeded(self):
        block = valid_block()
        block["false_specificity"] = {
            "evaluable_count": 100,
            "error_count": 1,
        }
        with self.assertRaises(ValueError):
            evaluate_discriminant_validation(block, validated_pairs=[PAIR])

    def test_synthetic_false_specificity_has_zero_tolerance(self):
        block = valid_block()
        block["synthetic_adversarial"]["false_specificity_count"] = 1
        with self.assertRaises(ValueError):
            evaluate_discriminant_validation(block, validated_pairs=[PAIR])

    def test_missing_validated_pair_blocks_promotion(self):
        block = valid_block()
        with self.assertRaises(ValueError):
            evaluate_discriminant_validation(
                block,
                validated_pairs=[
                    PAIR,
                    ["MONADIC_ORIGIN", "SPLIT_SOUL"],
                ],
            )

    def test_probabilistic_output_requires_calibration_pass(self):
        block = valid_block()
        block["calibration"] = {
            "mode": "PROBABILISTIC",
            "passed": False,
            "criterion_ref": "CAL-CRITERION-1",
            "refs": ["CAL-1"],
        }
        with self.assertRaises(ValueError):
            evaluate_discriminant_validation(block, validated_pairs=[PAIR])

        block["calibration"]["passed"] = True
        result = evaluate_discriminant_validation(block, validated_pairs=[PAIR])
        self.assertEqual(result["calibration_mode"], "PROBABILISTIC")

    def test_development_evaluation_overlap_blocks(self):
        block = valid_block()
        block["development_evaluation_disjoint"] = False
        with self.assertRaises(ValueError):
            evaluate_discriminant_validation(block, validated_pairs=[PAIR])


if __name__ == "__main__":
    unittest.main()
