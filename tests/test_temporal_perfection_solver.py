import unittest
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from jsonschema import Draft202012Validator

from almas_tfa.temporal_perfection_solver import solve_aspect_perfections


class TemporalPerfectionSolverTests(unittest.TestCase):
    def solve(self, fn, *, days=2, angle=0, step=21600):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        return solve_aspect_perfections(
            lambda when: (0.0, fn((when - start).total_seconds() / 86400)),
            start=start,
            end=start + timedelta(days=days),
            aspect_angle=angle,
            technique="TTRANSIT",
            technique_variant="RETURN_CYCLE",
            source_point="CHIRON_TRANSIT",
            target_point="CHIRON_NATAL",
            step_seconds=step,
            time_tolerance_seconds=1,
            angular_tolerance_degrees=1e-4,
        )

    def test_finds_multiple_perfections_in_one_window(self):
        result = self.solve(lambda day: (day * 100.0) % 360.0, days=4, angle=80, step=21600)
        self.assertGreaterEqual(len(result["exact_hits"]), 2)
        self.assertEqual([hit["pass_number"] for hit in result["exact_hits"]], list(range(1, len(result["exact_hits"]) + 1)))
        self.assertFalse(result["creates_structural_root"])

    def test_finds_wraparound_conjunction(self):
        result = self.solve(lambda day: (359.0 + day * 2.0) % 360.0, days=1, angle=0, step=21600)
        self.assertTrue(any(abs(hit["orb"]) < 1e-4 for hit in result["exact_hits"]))

    def test_signed_angle_branch_cut_is_not_a_false_conjunction(self):
        result = self.solve(lambda day: (179.0 + day * 2.0) % 360.0, days=2, angle=0, step=21600)
        self.assertEqual(result["exact_hits"], [])

    def test_detects_stationary_tangent_perfection(self):
        result = self.solve(lambda day: 10.0 + (day - 1.0) ** 2, days=2, angle=10, step=21600)
        self.assertTrue(any(abs(hit["orb"]) <= 1e-4 for hit in result["exact_hits"]))

    def test_invalid_window_and_naive_times_fail_closed(self):
        with self.assertRaises(ValueError):
            self.solve(lambda day: day, days=0)
        with self.assertRaises(ValueError):
            solve_aspect_perfections(
                lambda when: (0, 0), start=datetime(2026, 1, 1),
                end=datetime(2026, 1, 2, tzinfo=timezone.utc), aspect_angle=0,
                technique="TTRANSIT", technique_variant="RETURN_CYCLE",
                source_point="A", target_point="B",
            )

    def test_solver_hit_obeys_public_kinematic_schema(self):
        result = self.solve(lambda day: (day * 20.0) % 360, days=1, angle=10, step=3600)
        schema = json.loads((Path(__file__).resolve().parents[1] / "schemas/temporal-perfection-hit.schema.json").read_text())
        validator = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
        for hit in result["exact_hits"]:
            validator.validate(hit)


if __name__ == "__main__":
    unittest.main()
