from __future__ import annotations

import unittest

from almas_tfa.astronomy_golden_validation import (
    circular_delta_arcsec,
    evaluate_golden_result,
    evaluate_golden_stage,
    load_astronomy_golden_validation_policy,
    tolerance_arcsec,
)


REFERENCE_ID = "TEST_REFERENCE"


class AstronomyGoldenValidationTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_astronomy_golden_validation_policy()

    def measurements_for_stage(self, stage):
        metrics = set(self.policy["validation_stages"][stage])
        measurements = []
        for metric, points in self.policy["required_measurements"].items():
            if metric not in metrics:
                continue
            for point_id in points:
                measurements.append(
                    {
                        "metric": metric,
                        "point_id": point_id,
                        "implementation_deg": 10.0,
                        "reference_deg": 10.0,
                        "reference_method_id": REFERENCE_ID,
                    }
                )
        return measurements

    def result_for_stage(self, stage):
        return {
            "case_id": "SYNTHETIC_TEST",
            "validation_stage": stage,
            "reference_provenance": [
                {
                    "method_id": REFERENCE_ID,
                    "software": "synthetic",
                    "software_version": "1",
                    "ephemeris_family": "DE440",
                }
            ],
            "measurements": self.measurements_for_stage(stage),
        }

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
        self.assertEqual(
            self.policy["kernel_artifact"]["sha256"],
            "c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2",
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

    def test_planetary_stage_does_not_require_node_or_houses(self):
        evaluation = evaluate_golden_stage(
            self.result_for_stage("PLANETARY_REFERENCE"),
            self.policy,
        )
        self.assertEqual(evaluation["status"], "PASS")
        self.assertEqual(evaluation["required_measurement_count"], 30)

    def test_complete_identical_fixture_passes(self):
        result = self.result_for_stage("COMPLETE_GATE")
        evaluation = evaluate_golden_result(result, self.policy)
        self.assertEqual(evaluation["status"], "PASS")
        self.assertEqual(
            evaluation["evaluated_measurement_count"],
            evaluation["required_measurement_count"],
        )

    def test_missing_measurement_fails(self):
        result = self.result_for_stage("PLANETARY_REFERENCE")
        result["measurements"].pop()
        evaluation = evaluate_golden_stage(result, self.policy)
        self.assertEqual(evaluation["status"], "FAIL")
        self.assertTrue(
            any(x.startswith("MISSING:") for x in evaluation["failures"])
        )

    def test_duplicate_measurement_fails(self):
        result = self.result_for_stage("PLANETARY_REFERENCE")
        result["measurements"].append(dict(result["measurements"][0]))
        evaluation = evaluate_golden_stage(result, self.policy)
        self.assertEqual(evaluation["status"], "FAIL")
        self.assertTrue(
            any(x.startswith("DUPLICATE:") for x in evaluation["failures"])
        )

    def test_unknown_reference_method_fails(self):
        result = self.result_for_stage("PLANETARY_REFERENCE")
        result["measurements"][0]["reference_method_id"] = "UNKNOWN"
        evaluation = evaluate_golden_stage(result, self.policy)
        self.assertEqual(evaluation["status"], "FAIL")
        self.assertTrue(
            any(
                x.startswith("UNKNOWN_REFERENCE_METHOD:")
                for x in evaluation["failures"]
            )
        )

    def test_out_of_tolerance_fails_without_averaging(self):
        result = self.result_for_stage("PLANETARY_REFERENCE")
        for item in result["measurements"]:
            if (
                item["metric"] == "planetary_longitude"
                and item["point_id"] == "SUN"
            ):
                item["implementation_deg"] = 10.01
                break
        evaluation = evaluate_golden_stage(result, self.policy)
        self.assertEqual(evaluation["status"], "FAIL")
        self.assertIn(
            "OUT_OF_TOLERANCE:planetary_longitude:SUN",
            evaluation["failures"],
        )


if __name__ == "__main__":
    unittest.main()
