from __future__ import annotations

import unittest

from almas_tfa.pillar_attribution import (
    classify_root,
    derive_pillars_from_roots,
    load_root_pillar_policy,
)


def root(
    root_id,
    points,
    relations,
    *,
    strength=0.8,
    families=1,
    core=True,
    state="CALCULATED_CORE",
):
    return {
        "root_id": root_id,
        "point_ids": list(points),
        "relation_ids": list(relations),
        "strength": strength,
        "strength_state": state,
        "core_eligible": core,
        "independent_family_count": families,
    }


class PillarAttributionTests(unittest.TestCase):
    def test_policy_is_frozen_and_case_fit_forbidden(self):
        policy = load_root_pillar_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_ROOT_PILLAR_ATTRIBUTION_V1",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertTrue(
            policy["principles"]["single_semantic_primary_pillar"]
        )

    def test_affinity_root_maps_to_pa(self):
        result = classify_root(
            root("R1", ["SUN", "MOON"], ["TRINE"])
        )
        self.assertEqual(result["primary_pillar"], "PA")
        self.assertEqual(result["contributions"], {"PA": 0.8})

    def test_hard_personal_root_maps_to_pe_before_pa(self):
        result = classify_root(
            root("R1", ["SUN", "MOON"], ["OPPOSITION"])
        )
        self.assertEqual(result["primary_pillar"], "PE")

    def test_node_or_saturn_maps_to_pk_before_other_semantics(self):
        result = classify_root(
            root("R1", ["AXIS_NODES", "VENUS"], ["SQUARE"])
        )
        self.assertEqual(result["primary_pillar"], "PK")

    def test_pluto_chiron_uranus_map_to_pt(self):
        result = classify_root(
            root("R1", ["PLUTO", "VENUS"], ["CONJUNCTION"])
        )
        self.assertEqual(result["primary_pillar"], "PT")

    def test_mercury_coherent_contact_maps_to_pr(self):
        result = classify_root(
            root("R1", ["MERCURY", "MOON"], ["SEXTILE"])
        )
        self.assertEqual(result["primary_pillar"], "PR")

    def test_mission_requires_meridian_anchor_and_recurrence(self):
        result = classify_root(
            root(
                "R1",
                ["AXIS_MERIDIAN", "JUPITER"],
                ["TRINE"],
                families=2,
            )
        )
        self.assertEqual(result["primary_pillar"], "PS")
        self.assertTrue(result["recurrent"])
        self.assertEqual(set(result["contributions"]), {"PS", "PX"})

    def test_recurrence_is_orthogonal_not_second_semantic_pillar(self):
        result = classify_root(
            root(
                "R1",
                ["SUN", "MOON"],
                ["TRINE"],
                families=2,
            )
        )
        self.assertEqual(result["primary_pillar"], "PA")
        self.assertEqual(set(result["contributions"]), {"PA", "PX"})
        self.assertAlmostEqual(result["contributions"]["PA"], 0.8)
        self.assertAlmostEqual(result["contributions"]["PX"], 0.8)

    def test_support_only_or_noncore_root_cannot_feed_pillars(self):
        result = classify_root(
            root(
                "R1",
                ["SUN", "MOON"],
                ["TRINE"],
                core=False,
                state="CALCULATED_SUPPORT_ONLY",
            )
        )
        self.assertFalse(result["eligible"])

    def test_pu_remains_not_evaluable(self):
        derived = derive_pillars_from_roots(
            [
                root("R1", ["SUN", "MOON"], ["TRINE"]),
                root("R2", ["PLUTO", "VENUS"], ["CONJUNCTION"]),
            ],
            structural_absence_is_zero=True,
        )
        self.assertIsNone(derived["pillars"]["PU"])
        self.assertEqual(derived["pu_state"], "NOT_EVALUABLE")

    def test_absence_is_not_zero_when_structural_coverage_incomplete(self):
        derived = derive_pillars_from_roots(
            [root("R1", ["SUN", "MOON"], ["TRINE"])],
            structural_absence_is_zero=False,
        )
        self.assertIsNotNone(derived["pillars"]["PA"])
        self.assertIsNone(derived["pillars"]["PK"])

    def test_absence_can_be_zero_when_required_structure_completed(self):
        derived = derive_pillars_from_roots(
            [root("R1", ["SUN", "MOON"], ["TRINE"])],
            structural_absence_is_zero=True,
        )
        self.assertEqual(derived["pillars"]["PK"], 0.0)


if __name__ == "__main__":
    unittest.main()
