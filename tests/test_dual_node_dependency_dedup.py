import unittest
import json
from pathlib import Path
from jsonschema import Draft202012Validator

from almas_tfa.temporal_dependency import summarize_temporal_dependencies


class DualNodeDependencyDedupTests(unittest.TestCase):
    def test_true_mean_and_north_south_are_one_axis_dependency_unit(self):
        result = summarize_temporal_dependencies([
            {"signal_id": "TRUE-N", "root_id": "R1", "temporal_family": "TTRANSIT", "node_variant": "TRUE", "nodal_axis_id": "AXIS-1", "dependency_group": "TRANSIT_EPHEMERIS"},
            {"signal_id": "MEAN-N", "root_id": "R1", "temporal_family": "TTRANSIT", "node_variant": "MEAN", "nodal_axis_id": "AXIS-1", "dependency_group": "TRANSIT_EPHEMERIS"},
            {"signal_id": "TRUE-S", "root_id": "R1", "temporal_family": "TTRANSIT", "node_variant": "TRUE", "nodal_axis_id": "AXIS-1", "dependency_group": "TRANSIT_EPHEMERIS"},
        ])
        self.assertEqual(len(result["dependency_units"]), 1)
        unit = result["dependency_units"][0]
        self.assertEqual(unit["independent_unit_count"], 1)
        self.assertEqual(unit["node_variants"], ["MEAN", "TRUE"])
        self.assertFalse(result["score_created"])
        self.assertFalse(result["legacy_iat_modified"])
        self.assertEqual(result["policy_id"], "ALMAS_TEMPORAL_DEPENDENCY_POLICY_V2")
        schema = json.loads((Path(__file__).resolve().parents[1] / "schemas/temporal-dependency-result.schema.json").read_text())
        Draft202012Validator(schema).validate(result)

    def test_node_variant_requires_axis_identity(self):
        with self.assertRaises(ValueError):
            summarize_temporal_dependencies([
                {"signal_id": "TRUE-N", "root_id": "R1", "temporal_family": "TTRANSIT", "node_variant": "TRUE"}
            ])


if __name__ == "__main__":
    unittest.main()
