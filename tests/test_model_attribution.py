from __future__ import annotations

import unittest

from almas_tfa.model_attribution import (
    derive_model_attributions,
    load_model_attribution_policy,
)


def pillar_attribution(units, *, complete=True):
    return {
        "structural_absence_is_zero": complete,
        "attribution_units": units,
    }


def attributed(unit_id, pillar, value, *, unit_type="ROOT", source_root_ids=None):
    item = {
        "unit_id": unit_id,
        "root_id": unit_id,
        "unit_type": unit_type,
        "eligible": True,
        "contributions": {pillar: value},
    }
    if unit_type == "SEMANTIC_MOTIF":
        item["source_root_ids"] = list(source_root_ids or [unit_id + ":SOURCE"])
    return item


class ModelAttributionV3Tests(unittest.TestCase):
    def test_policy_is_frozen_and_case_fit_forbidden(self):
        policy = load_model_attribution_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V3",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertEqual(
            policy["value_function"],
            "IEM_PRE_DEPENDENCY_AWARE",
        )
        self.assertFalse(
            policy["derived_motif_units_are_independent_evidence"]
        )
        self.assertTrue(
            policy["principles"]["root_motif_source_overlap_corrected"]
        )

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

    def test_exact_shapley_uses_small_evidence_unit_sets(self):
        units = [
            attributed("R1", "PA", 0.9),
            attributed("R2", "PR", 0.8),
            attributed("R3", "PE", 0.7),
            attributed("MOTIF:REL", "PX", 0.75, unit_type="SEMANTIC_MOTIF"),
            attributed("R5", "PK", 0.65),
            attributed("R6", "PT", 0.70),
        ]
        result = derive_model_attributions(pillar_attribution(units))
        self.assertEqual(result["state"], "EVALUABLE")
        self.assertEqual(
            result["method"]["convergence_state"],
            "EXACT",
        )
        self.assertEqual(result["method"]["method"], "EXACT_SHAPLEY")
        self.assertEqual(result["motif_unit_count"], 1)

    def test_shapley_efficiency_matches_iem_pre(self):
        units = [
            attributed("R1", "PA", 0.9),
            attributed("R2", "PR", 0.8),
            attributed("R3", "PE", 0.7),
            attributed("MOTIF:REL", "PX", 0.75, unit_type="SEMANTIC_MOTIF"),
            attributed("R5", "PK", 0.65),
            attributed("R6", "PT", 0.70),
        ]
        result = derive_model_attributions(pillar_attribution(units))
        for model, error in result["shapley_efficiency_error"].items():
            self.assertLess(error, 1e-8, model)

    def test_motif_units_make_ag_lg_attribution_possible(self):
        units = [
            attributed("R1", "PA", 0.9),
            attributed("R2", "PR", 0.8),
            attributed("R3", "PE", 0.7),
            attributed("MOTIF:REL", "PX", 0.75, unit_type="SEMANTIC_MOTIF"),
            attributed("R5", "PK", 0.65),
            attributed("R6", "PT", 0.70),
            attributed("MOTIF:MISSION", "PS", 0.55, unit_type="SEMANTIC_MOTIF"),
        ]
        result = derive_model_attributions(pillar_attribution(units))
        self.assertTrue(result["attributions"]["AG"])
        self.assertTrue(result["attributions"]["LG"])
        self.assertIn(
            "MOTIF:REL",
            result["attributions"]["AG"],
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
