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
    family="SYN",
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
        "dependency_families": [family],
        "independent_family_count": 1,
    }


class PillarAttributionTests(unittest.TestCase):
    def test_policy_is_v2_frozen_and_case_fit_forbidden(self):
        policy = load_root_pillar_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_ROOT_PILLAR_ATTRIBUTION_V2",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertTrue(
            policy["principles"]["single_semantic_primary_pillar"]
        )
        self.assertTrue(
            policy["principles"]["px_derived_by_semantic_motif_graph"]
        )

    def test_affinity_root_maps_to_pa_only(self):
        result = classify_root(
            root("R1", ["SUN", "MOON"], ["TRINE"])
        )
        self.assertEqual(result["primary_pillar"], "PA")
        self.assertEqual(result["contributions"], {"PA": 0.8})
        self.assertNotIn("PX", result["contributions"])

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
        for point in ("PLUTO", "CHIRON", "URANUS"):
            result = classify_root(
                root("R1", [point, "VENUS"], ["CONJUNCTION"])
            )
            self.assertEqual(result["primary_pillar"], "PT", point)

    def test_mercury_coherent_contact_maps_to_pr(self):
        result = classify_root(
            root("R1", ["MERCURY", "MOON"], ["SEXTILE"])
        )
        self.assertEqual(result["primary_pillar"], "PR")

    def test_semantic_recurrence_creates_px_across_distinct_families(self):
        derived = derive_pillars_from_roots(
            [
                root(
                    "R1",
                    ["SUN", "MOON"],
                    ["TRINE"],
                    strength=0.90,
                    family="SYN",
                ),
                root(
                    "R2",
                    ["VENUS", "MARS"],
                    ["SEXTILE"],
                    strength=0.75,
                    family="NATAL_DRACONIC",
                ),
            ],
            structural_absence_is_zero=True,
        )
        self.assertGreater(derived["pillars"]["PX"], 0.0)
        motif = next(
            item
            for item in derived["semantic_motifs"]["motifs"]
            if item["motif_id"] == "STRUCTURAL_AFFINITY"
        )
        self.assertTrue(motif["recurrent"])
        self.assertAlmostEqual(motif["recurrence_strength"], 0.75)

    def test_mission_service_is_motif_recurrence_not_single_root_gate(self):
        derived = derive_pillars_from_roots(
            [
                root(
                    "R1",
                    ["AXIS_MERIDIAN", "JUPITER"],
                    ["TRINE"],
                    strength=0.82,
                    family="SYN",
                ),
                root(
                    "R2",
                    ["AXIS_MERIDIAN", "SUN"],
                    ["PARALLEL"],
                    strength=0.70,
                    family="DECLINATION",
                ),
            ],
            structural_absence_is_zero=True,
        )
        self.assertAlmostEqual(derived["pillars"]["PS"], 0.70)
        self.assertGreater(derived["pillars"]["PX"], 0.0)

    def test_support_only_or_noncore_root_cannot_feed_pillars_or_px(self):
        derived = derive_pillars_from_roots(
            [
                root(
                    "R1",
                    ["SUN", "MOON"],
                    ["TRINE"],
                    family="SYN",
                ),
                root(
                    "R2",
                    ["VENUS", "MARS"],
                    ["SEXTILE"],
                    family="DRACONIC_DD",
                    core=False,
                    state="CALCULATED_SUPPORT_ONLY",
                ),
            ],
            structural_absence_is_zero=True,
        )
        self.assertEqual(derived["pillars"]["PX"], 0.0)

    def test_same_dependency_family_does_not_create_recurrence(self):
        derived = derive_pillars_from_roots(
            [
                root(
                    "R1",
                    ["SUN", "MOON"],
                    ["TRINE"],
                    family="RELCHART",
                ),
                root(
                    "R2",
                    ["VENUS", "MARS"],
                    ["SEXTILE"],
                    family="RELCHART",
                ),
            ],
            structural_absence_is_zero=True,
        )
        self.assertEqual(derived["pillars"]["PX"], 0.0)

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
        self.assertIsNone(derived["pillars"]["PX"])

    def test_absence_can_be_zero_when_required_structure_completed(self):
        derived = derive_pillars_from_roots(
            [root("R1", ["SUN", "MOON"], ["TRINE"])],
            structural_absence_is_zero=True,
        )
        self.assertEqual(derived["pillars"]["PK"], 0.0)
        self.assertEqual(derived["pillars"]["PX"], 0.0)


if __name__ == "__main__":
    unittest.main()
