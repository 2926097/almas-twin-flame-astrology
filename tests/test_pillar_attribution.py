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
    families=None,
    core=True,
    state="CALCULATED_CORE",
):
    family_list = list(families or [family])
    return {
        "root_id": root_id,
        "root_key": root_id + ":KEY",
        "point_ids": list(points),
        "relation_ids": list(relations),
        "strength": strength,
        "strength_state": state,
        "core_eligible": core,
        "independent_family_count": len(family_list),
        "dependency_families": family_list,
        "evidence_strengths": [
            {
                "evidence_id": root_id + ":" + fam,
                "strength": strength,
                "core_eligible": core,
                "support_only": not core,
                "dependency_family": fam,
                "technique_family": fam,
            }
            for fam in family_list
        ],
    }


class PillarAttributionV2Tests(unittest.TestCase):
    def test_policy_is_v2_and_case_fit_forbidden(self):
        policy = load_root_pillar_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_ROOT_PILLAR_ATTRIBUTION_V2",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertTrue(
            policy["principles"]["px_derived_from_semantic_motifs"]
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

    def test_node_or_saturn_maps_to_pk(self):
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

    def test_single_root_no_longer_creates_px_from_family_count_alone(self):
        derived = derive_pillars_from_roots(
            [
                root(
                    "R1",
                    ["SUN", "MOON"],
                    ["TRINE"],
                    families=["SYN", "DECLINATION"],
                )
            ],
            structural_absence_is_zero=True,
        )
        # El motivo exacto multifamilia puede ser recurrente aunque exista una
        # sola root_key; éste es el único caso permitido por la política.
        self.assertGreater(derived["pillars"]["PX"], 0.0)
        self.assertEqual(
            derived["recurrence_source"],
            "SEMANTIC_MOTIF_GRAPH_V2",
        )

    def test_semantically_same_motif_across_different_root_keys_creates_px(self):
        derived = derive_pillars_from_roots(
            [
                root(
                    "R1",
                    ["SUN", "MOON"],
                    ["TRINE"],
                    family="SYN",
                    strength=0.9,
                ),
                root(
                    "R2",
                    ["VENUS", "MOON"],
                    ["SEXTILE"],
                    family="DECLINATION",
                    strength=0.8,
                ),
            ],
            structural_absence_is_zero=True,
        )
        self.assertGreater(derived["pillars"]["PX"], 0.0)
        recurrent = derived["semantic_motifs"][
            "recurrent_primary_motifs"
        ]
        self.assertTrue(
            any(
                item["motif_id"] == "RELATIONAL_COHERENCE"
                for item in recurrent
            )
        )

    def test_same_dependency_family_does_not_create_semantic_px(self):
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
                    ["VENUS", "MOON"],
                    ["SEXTILE"],
                    family="RELCHART",
                ),
            ],
            structural_absence_is_zero=True,
        )
        self.assertEqual(derived["pillars"]["PX"], 0.0)

    def test_mission_is_emergent_across_roots_and_families(self):
        derived = derive_pillars_from_roots(
            [
                root(
                    "R1",
                    ["AXIS_MERIDIAN", "SUN"],
                    ["TRINE"],
                    family="SYN",
                    strength=0.9,
                ),
                root(
                    "R2",
                    ["AXIS_MERIDIAN", "SUN"],
                    ["CONJUNCTION"],
                    family="NATAL_DRACONIC",
                    strength=0.8,
                ),
            ],
            structural_absence_is_zero=True,
        )
        self.assertGreater(derived["pillars"]["PS"], 0.0)
        mission = derived["semantic_motifs"][
            "recurrent_mission_motifs"
        ]
        self.assertEqual(mission[0]["motif_id"], "MISSION_SOLAR")

    def test_support_only_never_creates_core_px(self):
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
                    ["SUN", "MOON"],
                    ["TRINE"],
                    family="SECONDARY",
                    core=False,
                    state="CALCULATED_SUPPORT_ONLY",
                ),
            ],
            structural_absence_is_zero=True,
        )
        self.assertEqual(derived["pillars"]["PX"], 0.0)

    def test_motif_units_are_exposed_for_shapley_but_not_new_roots(self):
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
                    ["VENUS", "MOON"],
                    ["SEXTILE"],
                    family="DECLINATION",
                ),
            ],
            structural_absence_is_zero=True,
        )
        motif_units = [
            item
            for item in derived["attribution_units"]
            if item["unit_type"] == "SEMANTIC_MOTIF"
        ]
        self.assertTrue(motif_units)
        self.assertTrue(
            all(item["derived_unit_not_independent_root"] for item in motif_units)
        )

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
        self.assertIsNone(derived["pillars"]["PS"])

    def test_absence_can_be_zero_when_required_structure_completed(self):
        derived = derive_pillars_from_roots(
            [root("R1", ["SUN", "MOON"], ["TRINE"])],
            structural_absence_is_zero=True,
        )
        self.assertEqual(derived["pillars"]["PK"], 0.0)
        self.assertEqual(derived["pillars"]["PX"], 0.0)
        self.assertEqual(derived["pillars"]["PS"], 0.0)


if __name__ == "__main__":
    unittest.main()
