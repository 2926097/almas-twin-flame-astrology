from __future__ import annotations

import unittest

from almas_tfa.pillar_attribution import derive_pillars_from_roots
from almas_tfa.recurrence_quality import (
    derive_recurrence_quality_diagnostics,
    load_recurrence_quality_policy,
)
from almas_tfa.semantic_motifs import (
    derive_semantic_motif_graph,
    load_semantic_motif_policy,
)


def root(
    root_id,
    points,
    relations,
    *,
    family,
    strength=0.8,
    core=True,
    state="CALCULATED_CORE",
):
    return {
        "root_id": root_id,
        "root_key": root_id + ":KEY",
        "point_ids": list(points),
        "relation_ids": list(relations),
        "strength": strength,
        "strength_state": state,
        "core_eligible": core,
        "independent_family_count": 1,
        "dependency_families": [family],
        "evidence_strengths": [
            {
                "evidence_id": root_id + ":" + family,
                "strength": strength,
                "core_eligible": core,
                "support_only": not core,
                "dependency_family": family,
                "technique_family": family,
            }
        ],
    }


class RecurrenceQualityDiagnosticsTests(unittest.TestCase):
    def test_policy_is_descriptive_and_case_fit_forbidden(self):
        policy = load_recurrence_quality_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_RECURRENCE_QUALITY_DIAGNOSTICS_V1",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertTrue(policy["principles"]["descriptive_only"])
        self.assertTrue(policy["principles"]["px_ps_scores_unchanged"])
        self.assertTrue(
            policy["principles"]["null_calibration_required_before_any_weighting"]
        )

    def test_draconic_dependency_is_exposed_without_rescoring(self):
        roots = [
            root(
                "R1",
                ["SUN", "PLUTO"],
                ["SQUARE"],
                family="SYN",
                strength=0.9,
            ),
            root(
                "R2",
                ["SUN", "URANUS"],
                ["OPPOSITION"],
                family="NATAL_DRACONIC",
                strength=0.85,
            ),
        ]
        semantic_policy = load_semantic_motif_policy()
        graph = derive_semantic_motif_graph(
            roots,
            policy=semantic_policy,
        )
        quality = derive_recurrence_quality_diagnostics(
            roots,
            graph,
            semantic_policy=semantic_policy,
        )

        self.assertEqual(quality["state"], "DESCRIPTIVE_ONLY")
        self.assertFalse(quality["used_in_px_score"])
        self.assertFalse(quality["used_in_iem"])
        self.assertFalse(quality["population_specificity_claim"])

        item = quality["primary_motifs"][0]
        self.assertTrue(item["includes_natal_draconic"])
        self.assertFalse(item["non_draconic_recurrence"])
        self.assertEqual(item["family_class_count"], 2)
        self.assertTrue(item["cross_class_recurrence"])
        self.assertEqual(
            item["leave_one_family_out_survival_fraction"],
            0.0,
        )

    def test_family_class_ablation_distinguishes_two_symmetry_families(self):
        roots = [
            root(
                "R1",
                ["MERCURY", "MOON"],
                ["SEXTILE"],
                family="SYN",
                strength=0.9,
            ),
            root(
                "R2",
                ["MERCURY", "VENUS"],
                ["PARALLEL"],
                family="DECLINATION",
                strength=0.8,
            ),
            root(
                "R3",
                ["MERCURY", "JUPITER"],
                ["ANTISCION"],
                family="ANTISCIA",
                strength=0.7,
            ),
        ]
        semantic_policy = load_semantic_motif_policy()
        graph = derive_semantic_motif_graph(
            roots,
            policy=semantic_policy,
        )
        quality = derive_recurrence_quality_diagnostics(
            roots,
            graph,
            semantic_policy=semantic_policy,
        )

        item = quality["primary_motifs"][0]
        self.assertEqual(item["family_count"], 3)
        self.assertEqual(
            set(item["family_classes"]),
            {"TROPICAL_RELATIONAL", "SYMMETRY"},
        )
        self.assertTrue(item["non_draconic_recurrence"])
        self.assertTrue(
            item["leave_one_class_out"]["TROPICAL_RELATIONAL"]["recurrent"]
        )
        self.assertFalse(
            item["leave_one_class_out"]["SYMMETRY"]["recurrent"]
        )
        self.assertGreater(item["family_strength_entropy"], 0.0)
        self.assertGreater(item["effective_family_count"], 1.0)
        self.assertLess(item["family_dominance_share"], 1.0)

    def test_support_only_root_cannot_enter_quality_recurrence(self):
        roots = [
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
        ]
        semantic_policy = load_semantic_motif_policy()
        graph = derive_semantic_motif_graph(
            roots,
            policy=semantic_policy,
        )
        quality = derive_recurrence_quality_diagnostics(
            roots,
            graph,
            semantic_policy=semantic_policy,
        )
        self.assertEqual(
            quality["px_diagnostics"]["motif_count"],
            0,
        )

    def test_m18_attaches_diagnostics_but_px_equals_semantic_graph_score(self):
        roots = [
            root(
                "R1",
                ["SUN", "PLUTO"],
                ["SQUARE"],
                family="SYN",
                strength=0.9,
            ),
            root(
                "R2",
                ["SUN", "URANUS"],
                ["OPPOSITION"],
                family="NATAL_DRACONIC",
                strength=0.85,
            ),
        ]
        derived = derive_pillars_from_roots(
            roots,
            structural_absence_is_zero=True,
        )
        self.assertEqual(
            derived["pillars"]["PX"],
            derived["semantic_motifs"]["px"]["score"],
        )
        self.assertFalse(derived["recurrence_quality_used_in_scores"])
        self.assertEqual(
            derived["recurrence_quality"]["policy_id"],
            "ALMAS_RECURRENCE_QUALITY_DIAGNOSTICS_V1",
        )

    def test_aggregate_exposes_all_draconic_dependency_exactly(self):
        roots = [
            root(
                "R1",
                ["SUN", "PLUTO"],
                ["SQUARE"],
                family="SYN",
                strength=0.9,
            ),
            root(
                "R2",
                ["SUN", "URANUS"],
                ["OPPOSITION"],
                family="NATAL_DRACONIC",
                strength=0.85,
            ),
        ]
        semantic_policy = load_semantic_motif_policy()
        graph = derive_semantic_motif_graph(
            roots,
            policy=semantic_policy,
        )
        quality = derive_recurrence_quality_diagnostics(
            roots,
            graph,
            semantic_policy=semantic_policy,
        )
        aggregate = quality["px_diagnostics"]
        self.assertTrue(aggregate["all_include_natal_draconic"])
        self.assertTrue(aggregate["all_fail_without_natal_draconic"])
        self.assertEqual(aggregate["non_draconic_recurrent_count"], 0)


if __name__ == "__main__":
    unittest.main()
