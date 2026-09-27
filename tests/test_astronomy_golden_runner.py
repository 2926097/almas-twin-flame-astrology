from __future__ import annotations

import unittest

from almas_tfa.astronomy_golden_runner import (
    extract_backend_measurements,
    generate_backend_observations,
)
from almas_tfa.astronomy_golden_validation import (
    load_astronomy_golden_validation_policy,
)


class FakeBackend:
    def __init__(self):
        self.calls = []

    def calculate_natal(self, request):
        self.calls.append(request)
        points = [
            "SUN", "MOON", "MERCURY", "VENUS", "MARS",
            "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO",
        ]
        positions = {
            point: {
                "longitude": float(index * 20 + 1),
                "latitude": float(index) / 10.0,
                "declination": float(index) / 5.0,
            }
            for index, point in enumerate(points)
        }
        positions["NORTH_NODE"] = {
            "longitude": 123.0,
            "latitude": 0.0,
            "declination": 0.0,
        }
        return {
            "positions": positions,
            "angles": {
                "ASC": 10.0,
                "DSC": 190.0,
                "MC": 100.0,
                "IC": 280.0,
            },
            "houses": {str(i): float(i * 25 % 360) for i in range(1, 13)},
            "backend_provenance": {
                "adapter_id": "ALMAS_MOIRA_JPL_SPK_V1",
                "provider_version": "6.8.2",
                "kernel_family": "DE440",
                "kernel_sha256": "a" * 64,
            },
            "metadata": {
                "utc_instant": "2000-01-01T12:00:00+00:00",
                "jd_ut": 2451545.0,
                "delta_t_seconds": 63.8,
                "jd_tt": 2451545.000738,
            },
        }


def case_set():
    return {
        "schema_version": "1.0.0",
        "case_set_id": "ALMAS_ASTRONOMY_GOLDEN_CASES_V1",
        "policy_id": "ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1",
        "status": "PREREGISTERED_INPUTS_ONLY",
        "house_system": "PLACIDUS",
        "cases": [
            {
                "case_id": "G01",
                "birth_date": "2000-01-01",
                "birth_time": "12:00:00",
                "timezone": "UTC",
                "latitude": 0.0,
                "longitude": 0.0,
            },
            {
                "case_id": "G02",
                "birth_date": "2001-01-01",
                "birth_time": "12:00:00",
                "timezone": "UTC",
                "latitude": 10.0,
                "longitude": 20.0,
            },
        ],
    }


class AstronomyGoldenRunnerTests(unittest.TestCase):
    def test_extracts_exact_required_measurement_surface(self):
        backend = FakeBackend()
        chart = backend.calculate_natal(
            type("R", (), {"subject_id": "X"})()
        )
        measurements = extract_backend_measurements(chart)
        policy = load_astronomy_golden_validation_policy()
        expected = sum(
            len(points)
            for points in policy["required_measurements"].values()
        )
        self.assertEqual(len(measurements), expected)
        keys = {(m["metric"], m["point_id"]) for m in measurements}
        self.assertIn(("planetary_longitude", "SUN"), keys)
        self.assertIn(("true_node_longitude", "NORTH_NODE"), keys)
        self.assertIn(("angle_longitude", "ASC"), keys)
        self.assertIn(("house_cusp_longitude", "H12"), keys)

    def test_generate_preserves_frozen_case_order_and_inputs(self):
        backend = FakeBackend()
        artifact = generate_backend_observations(case_set(), backend)
        self.assertEqual(
            [item["case_id"] for item in artifact["cases"]],
            ["G01", "G02"],
        )
        self.assertEqual(artifact["case_count"], 2)
        self.assertEqual(len(backend.calls), 2)
        self.assertEqual(backend.calls[1].latitude, 10.0)
        self.assertEqual(
            artifact["artifact_type"],
            "ALMAS_ASTRONOMY_BACKEND_OBSERVATIONS_V1",
        )

    def test_backend_provenance_must_be_constant_for_run(self):
        class ChangingBackend(FakeBackend):
            def calculate_natal(self, request):
                chart = super().calculate_natal(request)
                if len(self.calls) == 2:
                    chart["backend_provenance"] = dict(
                        chart["backend_provenance"]
                    )
                    chart["backend_provenance"]["kernel_sha256"] = "b" * 64
                return chart

        with self.assertRaisesRegex(ValueError, "procedencia"):
            generate_backend_observations(case_set(), ChangingBackend())

    def test_missing_required_observation_fails_closed(self):
        backend = FakeBackend()
        chart = backend.calculate_natal(
            type("R", (), {"subject_id": "X"})()
        )
        del chart["positions"]["PLUTO"]
        with self.assertRaisesRegex(ValueError, "PLUTO"):
            extract_backend_measurements(chart)

    def test_unknown_case_set_is_rejected(self):
        payload = case_set()
        payload["case_set_id"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "desconocido"):
            generate_backend_observations(payload, FakeBackend())


if __name__ == "__main__":
    unittest.main()
