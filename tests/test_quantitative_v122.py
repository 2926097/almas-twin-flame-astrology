from __future__ import annotations

import unittest

from almas_tfa.quantitative_v122 import (
    derive_autonomous_ice,
    grouped_robustness_index,
    score_model_dependency_aware,
)


class QuantitativeV122Tests(unittest.TestCase):
    def test_root_motif_overlap_reduces_duplicate_dimension_weight(self):
        pillars = {
            "PA": 100.0,
            "PE": 80.0,
            "PR": 80.0,
            "PX": 20.0,
            "PK": 60.0,
            "PT": 60.0,
            "PS": 50.0,
            "PU": None,
        }
        independent = {
            "PA": ["R1"],
            "PE": ["R2"],
            "PR": ["R3"],
            "PX": ["R4"],
            "PK": ["R5"],
            "PT": ["R6"],
            "PS": ["R7"],
            "PU": [],
        }
        dependent = dict(independent)
        dependent["PX"] = ["R1"]

        a = score_model_dependency_aware("AG", pillars, independent)
        b = score_model_dependency_aware("AG", pillars, dependent)

        self.assertGreater(b.core_weights["PA"], 0.0)
        self.assertLess(b.core_weights["PA"], a.core_weights["PA"])
        self.assertLess(b.core_weights["PX"], a.core_weights["PX"])
        self.assertGreater(b.core, a.core)

    def test_support_fully_redundant_with_core_is_not_counted_again(self):
        pillars = {
            "PA": 90.0, "PR": 90.0, "PE": 10.0, "PX": None,
            "PK": None, "PT": None, "PS": None, "PU": None,
        }
        sources = {
            "PA": ["R1"], "PR": ["R2"], "PE": ["R1"],
            "PX": [], "PK": [], "PT": [], "PS": [], "PU": [],
        }
        score = score_model_dependency_aware("AF", pillars, sources)
        self.assertIsNone(score.support)
        self.assertAlmostEqual(score.iem_pre, 90.0)

    def test_positive_pillar_without_lineage_fails_closed(self):
        pillars = {
            "PA": 80.0, "PR": 80.0, "PE": None, "PX": None,
            "PK": None, "PT": None, "PS": None, "PU": None,
        }
        sources = {key: [] for key in pillars}
        with self.assertRaises(ValueError):
            score_model_dependency_aware("AF", pillars, sources)

    def test_grouped_irc_does_not_count_same_parameter_ensemble_twice(self):
        base = [
            {"id": "P", "kind": "PARAMETER_PERTURBATION", "value": 0.9},
            {"id": "B", "kind": "BIRTH_TIME", "value": 0.8},
        ]
        duplicated_family = base + [
            {"id": "I", "kind": "IDD_STABILITY", "value": 0.9},
        ]
        irc_a, rmin_a, groups_a = grouped_robustness_index(base)
        irc_b, rmin_b, groups_b = grouped_robustness_index(duplicated_family)
        self.assertAlmostEqual(irc_a, irc_b)
        self.assertAlmostEqual(rmin_a, rmin_b)
        self.assertEqual(len(groups_a), 2)
        self.assertEqual(len(groups_b), 2)

    def test_autonomous_ice_uses_max_within_family_and_saturates_across_families(self):
        retained = {
            "AF": [],
            "KA": [],
            "AG": [],
            "LG": [
                {"dependency_family": "FACTS", "severity": 0.4},
                {"dependency_family": "FACTS", "severity": 0.6},
                {"dependency_family": "STRUCTURE", "severity": 0.5},
            ],
        }
        ice, diagnostics = derive_autonomous_ice(retained)
        self.assertAlmostEqual(ice["LG"], 80.0)
        self.assertEqual(len(diagnostics["LG"]), 2)
        self.assertEqual(ice["AF"], 0.0)

    def test_autonomous_ice_missing_severity_is_not_evaluable(self):
        retained = {
            "AF": [{"dependency_family": "FACTS", "severity": None}],
            "KA": [], "AG": [], "LG": [],
        }
        with self.assertRaises(ValueError):
            derive_autonomous_ice(retained)


if __name__ == "__main__":
    unittest.main()
