from __future__ import annotations

import unittest

from almas_tfa.robustness_aggregation import (
    grouped_robustness_index,
    load_irc_aggregation_policy,
)


class GroupedRobustnessTests(unittest.TestCase):
    def test_policy_groups_parameter_and_idd_stability_together(self):
        policy = load_irc_aggregation_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_IRC_DEPENDENCY_AGGREGATION_V2",
        )
        self.assertEqual(
            policy["kind_dependency_groups"]["PARAMETER_PERTURBATION"],
            policy["kind_dependency_groups"]["IDD_STABILITY"],
        )

    def test_correlated_components_count_once_using_minimum(self):
        components = [
            {"id": "TIME", "kind": "BIRTH_TIME", "value": 1.0},
            {"id": "PARAM", "kind": "PARAMETER_PERTURBATION", "value": 0.81},
            {"id": "IDD", "kind": "IDD_STABILITY", "value": 0.64},
        ]
        irc, r_min, groups = grouped_robustness_index(components)
        self.assertAlmostEqual(irc, 80.0)
        self.assertAlmostEqual(r_min, 0.64)
        self.assertEqual(len(groups), 2)
        parameter = next(
            item for item in groups
            if item["dependency_group"] == "PARAMETER_PERTURBATION"
        )
        self.assertEqual(parameter["aggregate_value"], 0.64)
        self.assertEqual(set(parameter["component_ids"]), {"PARAM", "IDD"})

    def test_extra_correlated_measure_does_not_create_extra_group_weight(self):
        base = [
            {"id": "TIME", "kind": "BIRTH_TIME", "value": 0.9},
            {"id": "PARAM", "kind": "PARAMETER_PERTURBATION", "value": 0.8},
        ]
        expanded = base + [
            {"id": "IDD", "kind": "IDD_STABILITY", "value": 0.8},
        ]
        irc_base, _, groups_base = grouped_robustness_index(base)
        irc_expanded, _, groups_expanded = grouped_robustness_index(expanded)
        self.assertAlmostEqual(irc_base, irc_expanded)
        self.assertEqual(len(groups_base), len(groups_expanded))

    def test_independent_groups_still_use_geometric_mean(self):
        components = [
            {"id": "TIME", "kind": "BIRTH_TIME", "value": 0.81},
            {"id": "ABL", "kind": "ABLATION", "value": 1.0},
        ]
        irc, r_min, groups = grouped_robustness_index(components)
        self.assertAlmostEqual(irc, 90.0)
        self.assertEqual(r_min, 0.81)
        self.assertEqual(len(groups), 2)


if __name__ == "__main__":
    unittest.main()
