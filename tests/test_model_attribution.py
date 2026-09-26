from __future__ import annotations

import unittest

from almas_tfa.model_attribution import (
    derive_model_attributions,
    load_model_attribution_policy,
)


def pillar_attribution(root_attributions, *, complete=True):
    return {
        "structural_absence_is_zero": complete,
        "root_attributions": root_attributions,
    }


def attributed(root_id, pillar, value, *, px=None):
    contributions = {pillar: value}
    if px is not None:
        contributions["PX"] = px
    return {
        "root_id": root_id,
        "eligible": True,
        "contributions": contributions,
    }


class ModelAttributionTests(unittest.TestCase):
    def test_policy_is_frozen_and_case_fit_forbidden(self):
        policy = load_model_attribution_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V1",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertEqual(policy["value_function"], "IEM_PRE")

    def test_incomplete_coverage_is_not_evaluable(self):
        result = derive_model_attributions(
            pillar_attribution(
                [attributed("R1", "PA", 0.8)],
                complete=False,
            )
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertEqual(
            result["reason"],
            "INCOMPLETE_STRUCTURAL_COVERAGE",
        )

    def test_exact_shapley_is_used_for_small_root_sets(self):
        roots = [
            attributed("R1", "PA", 0.9),
            attributed("R2", "PR", 0.8),
            attributed("R3", "PE", 0.7),
            attributed("R4", "PX", 0.75),
            attributed("R5", "PK", 0.65),
            attributed("R6", "PT", 0.70),
        ]
        result = derive_model_attributions(pillar_attribution(roots))
        self.assertEqual(result["state"], "EVALUABLE")
        self.assertEqual(
            result["method"]["convergence_state"],
            "EXACT",
        )
        self.assertEqual(
            result["method"]["method"],
            "EXACT_SHAPLEY",
        )

    def test_shapley_efficiency_matches_iem_pre(self):
        roots = [
            attributed("R1", "PA", 0.9),
            attributed("R2", "PR", 0.8),
            attributed("R3", "PE", 0.7),
            attributed("R4", "PX", 0.75),
            attributed("R5", "PK", 0.65),
            attributed("R6", "PT", 0.70),
        ]
        result = derive_model_attributions(pillar_attribution(roots))
        for model, error in result["shapley_efficiency_error"].items():
            self.assertLess(error, 1e-8, model)

    def test_model_architectures_produce_different_root_maps(self):
        roots = [
            attributed("R1", "PA", 0.9),
            attributed("R2", "PR", 0.8),
            attributed("R3", "PE", 0.7),
            attributed("R4", "PX", 0.75),
            attributed("R5", "PK", 0.65),
            attributed("R6", "PT", 0.70),
            attributed("R7", "PS", 0.55),
        ]
        result = derive_model_attributions(pillar_attribution(roots))
        self.assertNotEqual(
            result["attributions"]["AF"],
            result["attributions"]["KA"],
        )
        self.assertNotEqual(
            result["attributions"]["AG"],
            result["attributions"]["LG"],
        )

    def test_temporal_or_null_inputs_are_not_part_of_contract(self):
        policy = load_model_attribution_policy()
        self.assertTrue(
            policy["principles"]["temporal_activation_not_used"]
        )
        self.assertTrue(policy["principles"]["null_rarity_not_used"])
        self.assertTrue(policy["principles"]["ice_not_used_for_attribution"])


if __name__ == "__main__":
    unittest.main()
