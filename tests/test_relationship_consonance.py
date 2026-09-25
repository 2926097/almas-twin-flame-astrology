import unittest

from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.relationship_consonance import m09_relationship_chart_consonance


class TestRelationshipChartConsonance(unittest.TestCase):
    def test_requires_both_relationship_charts(self):
        context = ModuleContext(
            module_id="M09",
            module_name="relchart",
            mode="FULL",
            raw_input={},
            canonical_snapshot={"composite": {}},
            prior_results={},
        )
        result = m09_relationship_chart_consonance(context)
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)

    def test_compares_shared_points_under_declared_orb(self):
        canonical = {
            "composite": {
                "positions": {
                    "SUN": {"longitude": 10.0},
                    "MOON": {"longitude": 90.0},
                }
            },
            "davison": {
                "chart": {
                    "positions": {
                        "SUN": {"longitude": 12.0},
                        "MOON": {"longitude": 270.0},
                    }
                }
            },
        }
        raw = {
            "relationship_chart_consonance_policy": {
                "point_ids": ["SUN", "MOON"],
                "aspect_policy": {
                    "CONJUNCTION": {"angle": 0, "orb": 3},
                    "OPPOSITION": {"angle": 180, "orb": 3},
                },
            }
        }
        context = ModuleContext(
            module_id="M09",
            module_name="relchart",
            mode="FULL",
            raw_input=raw,
            canonical_snapshot=canonical,
            prior_results={},
        )
        result = m09_relationship_chart_consonance(context)
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["relationship_chart_consonance"]
        self.assertEqual(output["dependency_family"], "RELCHART")
        self.assertEqual(output["contact_count"], 2)
        self.assertIsNone(output["consonance_score"])
        self.assertEqual(output["score_state"], "NOT_DEFINED")


if __name__ == "__main__":
    unittest.main()
