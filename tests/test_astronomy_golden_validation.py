from __future__ import annotations

import unittest

from almas_tfa.astronomy_golden_validation import (
    circular_delta_arcsec,
    evaluate_golden_result,
    load_astronomy_golden_validation_policy,
    tolerance_arcsec,
)


class AstronomyGoldenValidationTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_astronomy_golden_validation_policy()

    def complete_measurements(self):
        measurements = []
        for metric, points in self.policy["required_measurements"].items():
            for point_id in points:
                measurements.append(
                    {
                        "metric": metric,
                        "point_id": point_id,
                        "implementation_deg": 10.0,
                        "reference_deg": 10.0,
                    }
                )
        return measurements

    def test_policy_is_preregistered_and_frozen_before_observation(self):
        self.assertEqual(
            self.policy["policy_id"],
            "ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1",
        )
        self.assertEqual(
            self.policy["status"],
            "PREREGISTERED_NOT_EXECUTED",
        )
        self.assertTrue(
            self.policy["decision_rule"][
                "threshold_change_after_observation_forbidden"
            ]
        )

    def test_circular_delta_handles_zero_degree_wrap(self):
        self.assertAlmostEqual(
            circular_delta_arcsec(359.999, 0.001),
            7.2,
            places=6,
        )

    def test_moon_has_explicit_longitude_override(self):
        self.assertEqual(
            tolerance_arcsec("planetary_longitude", "SUN", self.policy),
            5.0,
        )
        self.assertEqual(
            tolerance_arcsec("planetary_longitude", "MOON", self.policy),
            15.0,
        )

    def test_complete_identical_fixture_passes(self):
        result = {
            "case_id": "SYNTHETIC_TEST",
            "measurements": self.complete_measurements(),
        }
        evaluation = evaluate_golden_result(result, self.policy)
        self.assertEqual(evaluation["status"], "PASS")
        self.assertEqual(
            evaluation["evaluated_measurement_count"],
            evaluation["required_measurement_count"],
        )

    def test_missing_measurement_fails(self):
        measurements = self.complete_measurements()
        measurements.pop()
        evaluation = evaluate_golden_result(
            {"case_id": "SYNTHETIC_TEST", "measurements": measurements},
            self.policy,
        )
        self.assertEqual(evaluation["status"], "FAIL")
        self.assertTrue(any(x.startswith("MISSING:") for x in evaluation["failures"]))

    def test_duplicate_measurement_fails(self):
        measurements = self.complete_measurements()
        measurements.append(dict(measurements[0]))
        evaluation = evaluate_golden_result(
            {"case_id": "SYNTHETIC_TEST", "measurements": measurements},
            self.policy,
        )
        self.assertEqual(evaluation["status"], "FAIL")
        self.assertTrue(any(x.startswith("DUPLICATE:") for x in evaluation["failures"]))

    def test_out_of_tolerance_fails_without_averaging(self):
        measurements = self.complete_measurements()
        for item in measurements:
            if item["metric"] == "planetary_longitude" and item["point_id"] == "SUN":
                item["implementation_deg"] = 10.01
                break
        evaluation = evaluate_golden_result(
            {"case_id": "SYNTHETIC_TEST", "measurements": measurements},
            self.policy,
        )
        self.assertEqual(evaluation["status"], "FAIL")
        self.assertIn(
            "OUT_OF_TOLERANCE:planetary_longitude:SUN",
            evaluation["failures"],
        )


if __name__ == "__main__":
    unittest.main()
