import unittest
import json
from pathlib import Path
from datetime import datetime, timezone

from almas_tfa.dual_nodes import (
    build_dual_node_layer,
    classify_nodal_variant_concordance,
    mean_node_positions,
)
from jsonschema import Draft202012Validator


class DualNodeTests(unittest.TestCase):
    def test_south_is_antipode_and_both_variants_share_one_axis(self):
        result = build_dual_node_layer(
            {"longitude": 10.0}, {"longitude": 10.2}, nodal_axis_id="AXIS-7"
        )
        self.assertAlmostEqual(result["variants"]["TRUE"]["south_node"]["longitude"], 190.0)
        self.assertAlmostEqual(result["variants"]["MEAN"]["south_node"]["longitude"], 190.2)
        self.assertEqual(result["independent_axis_count"], 1)
        self.assertFalse(result["north_south_double_counting"])
        self.assertFalse(result["true_mean_double_counting"])

    def test_concordance_requires_declared_target_aspect_and_orb(self):
        dual = build_dual_node_layer({"longitude": 30}, {"longitude": 33})
        self.assertEqual(classify_nodal_variant_concordance(dual)["status"], "NOT_EVALUABLE")
        result = classify_nodal_variant_concordance(
            dual, target_longitude=90, aspect_angle=60, orb_limit=2
        )
        self.assertEqual(result["status"], "TRUE_DOMINANT")

    def test_mean_node_output_is_provenanced_and_mean_is_retrograde(self):
        points = mean_node_positions(datetime(2000, 1, 1, 12, tzinfo=timezone.utc))
        self.assertEqual(points["MEAN_NORTH_NODE"]["node_variant"], "MEAN")
        self.assertEqual(points["MEAN_NORTH_NODE"]["calculation_method"], "MEEUS_MEAN_ASCENDING_NODE_1998_47_7")
        self.assertLess(points["MEAN_NORTH_NODE"]["speed"], 0)
        self.assertAlmostEqual(points["MEAN_NORTH_NODE"]["longitude"], 125.0445479, places=5)

    def test_mean_node_rejects_naive_datetimes(self):
        with self.assertRaises(ValueError):
            mean_node_positions(datetime(2000, 1, 1))

    def test_nodal_layer_obeys_schema(self):
        layer = build_dual_node_layer({"longitude": 10.0}, {"longitude": 10.2})
        layer["nodal_variant_concordance"] = classify_nodal_variant_concordance(layer)
        layer["interpretive_hypothesis"] = {
            "statement": "Mean Node = vector estructural; True Node = modulación fenoménica/oscilatoria",
            "epistemic_class": "E_PROJECT_HYPOTHESIS", "validation_status": "UNVALIDATED",
        }
        schema = json.loads((Path(__file__).resolve().parents[1] / "schemas/dual-node-layer.schema.json").read_text())
        Draft202012Validator(schema).validate(layer)


if __name__ == "__main__":
    unittest.main()
