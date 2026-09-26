from __future__ import annotations

import unittest

from almas_tfa.semantic_motifs import (
    classify_semantic_motif,
    derive_semantic_motifs,
    load_semantic_motif_policy,
)


def root(
    root_id,
    points,
    relation,
    strength,
    family,
    *,
    core=True,
    state="CALCULATED_CORE",
):
    return {
        "root_id": root_id,
        "point_ids": list(points),
        "relation_ids": [relation],
        "strength": strength,
        "strength_state": state,
        "core_eligible": core,
        "dependency_families": [family],
    }


class SemanticMotifTests(unittest.TestCase):
    def test_policy_is_frozen_and_not_case_fitted(self):
        policy = load_semantic_motif_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_SEMANTIC_MOTIF_RECURRENCE_V1",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertTrue(
            policy["principles"]["private_case_fitting_forbidden"]
        )
        self.assertEqual(
            policy["principles"]["recurrence_strength_rule"],
            "SECOND_STRONGEST_FAMILY",
        )

    def test_different_root_keys_same_motif_can_recur(self):
        roots = [
            root("R1", ["SUN", "MOON"], "TRINE", 0.91, "SYN"),
            root(
                "R2",
                ["VENUS", "MARS"],
                "SEXTILE",
                0.73,
                "NATAL_DRACONIC",
            ),
        ]
        result = derive_semantic_motifs(roots)
        motif = next(
            item
            for item in result["motifs"]
            if item["motif_id"] == "STRUCTURAL_AFFINITY"
        )
        self.assertTrue(motif["recurrent"])
        self.assertEqual(motif["independent_family_count"], 2)
        self.assertAlmostEqual(motif["recurrence_strength"], 0.73)

    def test_same_dependency_family_does_not_fake_recurrence(self):
        roots = [
            root("R1", ["SUN", "MOON"], "TRINE", 0.91, "RELCHART"),
            root("R2", ["VENUS", "MARS"], "SEXTILE", 0.73, "RELCHART"),
        ]
        result = derive_semantic_motifs(roots)
        motif = next(
            item
            for item in result["motifs"]
            if item["motif_id"] == "STRUCTURAL_AFFINITY"
        )
        self.assertFalse(motif["recurrent"])
        self.assertEqual(motif["independent_family_count"], 1)

    def test_support_only_cannot_create_recurrence(self):
        roots = [
            root("R1", ["SUN", "MOON"], "TRINE", 0.91, "SYN"),
            root(
                "R2",
                ["VENUS", "MARS"],
                "SEXTILE",
                0.99,
                "DRACONIC_DD",
                core=False,
                state="CALCULATED_SUPPORT_ONLY",
            ),
        ]
        result = derive_semantic_motifs(roots)
        motif = next(
            item
            for item in result["motifs"]
            if item["motif_id"] == "STRUCTURAL_AFFINITY"
        )
        self.assertFalse(motif["recurrent"])

    def test_mission_recurrence_creates_ps_and_px_attribution(self):
        roots = [
            root(
                "R1",
                ["AXIS_MERIDIAN", "JUPITER"],
                "TRINE",
                0.86,
                "SYN",
            ),
            root(
                "R2",
                ["AXIS_MERIDIAN", "SUN"],
                "PARALLEL",
                0.71,
                "DECLINATION",
            ),
        ]
        result = derive_semantic_motifs(roots)
        attr = next(
            item
            for item in result["motif_attributions"]
            if item["motif_id"] == "MISSION_SERVICE"
        )
        self.assertEqual(set(attr["contributions"]), {"PX", "PS"})
        self.assertAlmostEqual(attr["contributions"]["PX"], 0.71)
        self.assertAlmostEqual(attr["contributions"]["PS"], 0.71)

    def test_neptune_has_transpersonal_motif_without_ontology_claim(self):
        motif = classify_semantic_motif(
            root(
                "R1",
                ["NEPTUNE", "MOON"],
                "TRINE",
                0.8,
                "SYN",
            )
        )
        self.assertEqual(motif, "TRANSPERSONAL_FIELD")


if __name__ == "__main__":
    unittest.main()
