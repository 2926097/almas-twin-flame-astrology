from __future__ import annotations

from copy import deepcopy
import unittest

from almas_tfa.model_attribution import (
    derive_model_attributions,
    load_model_attribution_policy,
)
from almas_tfa.pillar_attribution import derive_pillars_from_roots


def root(root_id, points, relation, family, strength=0.8):
    return {
        "root_id": root_id,
        "root_key": root_id + ":KEY",
        "point_ids": list(points),
        "relation_ids": [relation],
        "strength": strength,
        "strength_state": "CALCULATED_CORE",
        "core_eligible": True,
        "independent_family_count": 1,
        "dependency_families": [family],
        "evidence_strengths": [
            {
                "evidence_id": root_id + ":" + family,
                "strength": strength,
                "core_eligible": True,
                "support_only": False,
                "dependency_family": family,
                "technique_family": family,
            }
        ],
    }


def source_roots():
    return [
        root("R1", ["SUN", "MOON"], "TRINE", "SYN", 0.90),
        root("R2", ["SUN", "MOON"], "PARALLEL", "DECLINATION", 0.82),
        root("R3", ["MERCURY", "MOON"], "TRINE", "ANTISCIA", 0.84),
        root("R4", ["SUN", "MOON"], "SQUARE", "RELCHART", 0.78),
        root("R5", ["SATURN", "MOON"], "CONJUNCTION", "SYN", 0.76),
        root("R6", ["PLUTO", "SUN"], "SQUARE", "NATAL_DRACONIC", 0.74),
    ]


def attribution():
    return derive_pillars_from_roots(
        source_roots(),
        structural_absence_is_zero=True,
    )


class ModelAttributionV3Tests(unittest.TestCase):
    def test_policy_forbids_motifs_as_shapley_players(self):
        policy = load_model_attribution_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V3",
        )
        self.assertEqual(policy["player_unit"], "INDEPENDENT_ROOT")
        self.assertFalse(policy["derived_motif_units_are_shapley_players"])
        self.assertTrue(policy["motifs_recomputed_inside_each_coalition"])
        self.assertTrue(
            policy["principles"]["root_motif_double_counting_as_players_forbidden"]
        )

    def test_incomplete_coverage_is_not_evaluable(self):
        data = attribution()
        data["structural_absence_is_zero"] = False
        result = derive_model_attributions(data)
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertEqual(
            result["reason"],
            "INCOMPLETE_STRUCTURAL_COVERAGE",
        )

    def test_missing_source_roots_fails_closed(self):
        data = attribution()
        del data["source_roots"]
        result = derive_model_attributions(data)
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertEqual(
            result["reason"],
            "SOURCE_ROOTS_REQUIRED_FOR_DEPENDENCY_SAFE_SHAPLEY",
        )

    def test_exact_shapley_uses_roots_only(self):
        data = attribution()
        self.assertGreater(len(data["motif_attributions"]), 0)

        result = derive_model_attributions(data)

        self.assertEqual(result["state"], "EVALUABLE")
        self.assertEqual(result["player_unit"], "INDEPENDENT_ROOT")
        self.assertEqual(result["motif_player_count"], 0)
        self.assertTrue(result["motifs_recomputed_inside_coalitions"])
        self.assertEqual(
            result["method"]["method"],
            "EXACT_ROOT_INTERACTION_SHAPLEY",
        )
        self.assertEqual(set(result["unit_ids"]), {f"R{i}" for i in range(1, 7)})
        for values in result["attributions"].values():
            self.assertTrue(set(values).issubset(set(result["unit_ids"])))
            self.assertFalse(any(key.startswith("MOTIF:") for key in values))

    def test_shapley_efficiency_matches_full_interaction_value(self):
        result = derive_model_attributions(attribution())
        for model, error in result["shapley_efficiency_error"].items():
            self.assertLess(error, 1e-8, model)

    def test_forged_motif_player_cannot_change_attribution(self):
        data = attribution()
        baseline = derive_model_attributions(data)

        forged = deepcopy(data)
        forged["attribution_units"].append(
            {
                "unit_id": "MOTIF:FORGED",
                "unit_type": "SEMANTIC_MOTIF",
                "eligible": True,
                "contributions": {"PX": 1.0, "PS": 1.0},
            }
        )
        mutated = derive_model_attributions(forged)

        self.assertEqual(baseline["attributions"], mutated["attributions"])
        self.assertEqual(
            baseline["model_iem_pre_from_roots"],
            mutated["model_iem_pre_from_roots"],
        )

    def test_temporal_null_and_ice_are_not_part_of_value_function(self):
        policy = load_model_attribution_policy()
        self.assertTrue(policy["principles"]["temporal_activation_not_used"])
        self.assertTrue(policy["principles"]["null_rarity_not_used"])
        self.assertTrue(policy["principles"]["ice_not_used_for_attribution"])


if __name__ == "__main__":
    unittest.main()
