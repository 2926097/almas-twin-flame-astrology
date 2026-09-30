from __future__ import annotations

import unittest
import json
from pathlib import Path
from jsonschema import validate

from almas_tfa.angular_robustness import TIME_OFFSETS, evaluate_angular_robustness


class AngularRobustnessTests(unittest.TestCase):
    def samples(self, roots_by_offset):
        return [
            {"subject": subject, "offset_minutes": offset, "surviving_angular_root_ids": roots_by_offset.get((subject, offset), ["R1"])}
            for subject in ("A", "B")
            for offset in TIME_OFFSETS
        ]

    def test_all_requested_time_perturbations_high_without_new_score(self):
        result = evaluate_angular_robustness(["R1"], self.samples({}))
        schema = json.loads((Path(__file__).resolve().parents[1] / "schemas/angular-robustness-output.schema.json").read_text())
        validate(result, schema)
        self.assertEqual(result["angular_robustness"], "HIGH")
        self.assertEqual(result["sample_count"], 16)
        self.assertFalse(result["score_created"])

    def test_missing_time_samples_fail_closed(self):
        result = evaluate_angular_robustness(["R1"], [])
        schema = json.loads((Path(__file__).resolve().parents[1] / "schemas/angular-robustness-output.schema.json").read_text())
        validate(result, schema)
        self.assertEqual(result["status"], "NOT_EVALUABLE")
        self.assertEqual(result["angular_robustness"], "NOT_EVALUABLE")

    def test_weak_retention_is_low_and_duplicate_offsets_rejected(self):
        values = {(subject, offset): [] for subject in ("A", "B") for offset in TIME_OFFSETS}
        result = evaluate_angular_robustness(["R1", "R2"], self.samples(values))
        self.assertEqual(result["angular_robustness"], "LOW")
        duplicate = self.samples({}) + [self.samples({})[0]]
        with self.assertRaises(ValueError):
            evaluate_angular_robustness(["R1"], duplicate)


if __name__ == "__main__":
    unittest.main()
