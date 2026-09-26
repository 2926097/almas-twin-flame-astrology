from __future__ import annotations

import unittest
from datetime import datetime

from almas_tfa.astrology_backend import NatalRequest
from almas_tfa.handlers import configured_handlers
from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.relationship_chart_handlers import DavisonRequest
from almas_tfa.time_perturbation import (
    generate_birth_time_sensitivity,
    load_birth_time_perturbation_policy,
)


def minutes_from_noon(value: str) -> int:
    fmt = "%H:%M:%S" if value.count(":") >= 2 else "%H:%M"
    parsed = datetime.strptime(value, fmt)
    return (parsed.hour - 12) * 60 + parsed.minute


class TimeSensitiveNatalBackend:
    backend_id = "Q4_SYNTH_NATAL"
    backend_version = "1"

    def calculate_natal(self, request: NatalRequest):
        offset = minutes_from_noon(request.birth_time or "12:00")
        if request.subject_id == "A":
            positions = {
                "SUN": {"longitude": 0.0, "declination": 1.0, "point_type": "LUMINARY"},
                "MOON": {"longitude": 190.0, "declination": 4.0, "point_type": "LUMINARY"},
                "SATURN": {"longitude": 200.0, "declination": 8.0, "point_type": "PLANET"},
                "PLUTO": {"longitude": 250.0, "declination": -8.0, "point_type": "PLANET"},
                "NORTH_NODE": {"longitude": 30.0, "declination": 2.0, "point_type": "NODE"},
                "SOUTH_NODE": {"longitude": 210.0, "declination": -2.0, "point_type": "NODE"}
            }
            asc = 10.0 + offset * 0.10
        else:
            positions = {
                "SUN": {"longitude": 10.0, "declination": 1.2, "point_type": "LUMINARY"},
                "MOON": {"longitude": 120.0, "declination": 4.2, "point_type": "LUMINARY"},
                "VENUS": {"longitude": 200.0, "declination": 7.8, "point_type": "PLANET"},
                "MARS": {"longitude": 250.0, "declination": -7.8, "point_type": "PLANET"},
                "NORTH_NODE": {"longitude": 150.0, "declination": -2.0, "point_type": "NODE"},
                "SOUTH_NODE": {"longitude": 330.0, "declination": 2.0, "point_type": "NODE"}
            }
            asc = 40.0 + offset * 0.05

        return {
            "subject_id": request.subject_id,
            "timed": request.timed,
            "positions": positions,
            "angles": {
                "ASC": asc % 360.0,
                "MC": (asc + 90.0) % 360.0
            },
            "houses": {
                str(i): (asc + (i - 1) * 30.0) % 360.0
                for i in range(1, 13)
            }
        }


class TimeSensitiveDavisonBackend:
    backend_id = "Q4_SYNTH_DAVISON"
    backend_version = "1"

    def calculate_davison(self, request: DavisonRequest):
        a = minutes_from_noon(request.subject_a.birth_time or "12:00")
        b = minutes_from_noon(request.subject_b.birth_time or "12:00")
        shift = (a + b) * 0.01
        return {
            "positions": {
                "SUN": {"longitude": 5.0 + shift, "point_type": "LUMINARY"},
                "MOON": {"longitude": 155.0 + shift, "point_type": "LUMINARY"}
            },
            "angles": {
                "ASC": 25.0 + shift,
                "MC": 115.0 + shift
            }
        }


def raw_input():
    aspect_policy = {
        "CONJUNCTION": {"angle": 0, "orb": 6},
        "OPPOSITION": {"angle": 180, "orb": 6},
        "TRINE": {"angle": 120, "orb": 5},
        "SQUARE": {"angle": 90, "orb": 5},
        "SEXTILE": {"angle": 60, "orb": 4}
    }
    return {
        "mode": "FULL",
        "subjects": [
            {
                "id": "A",
                "birth_date": "2000-01-01",
                "birth_time": "12:00",
                "timezone": "UTC",
                "latitude": 40.0,
                "longitude": -1.0,
                "time_reliability": "A"
            },
            {
                "id": "B",
                "birth_date": "2001-01-01",
                "birth_time": "12:00",
                "timezone": "UTC",
                "latitude": 18.0,
                "longitude": -70.0,
                "time_reliability": "A"
            }
        ],
        "aspect_policy": aspect_policy,
        "declination_policy": {
            "parallel_orb": 1.0,
            "contra_parallel_orb": 1.0
        },
        "antiscia_policy": {
            "antiscia_orb": 3.0,
            "contra_antiscia_orb": 3.0
        },
        "composite_policy": {
            "midpoint_mode": "SHORTEST_ARC",
            "opposition_tie_break": "NOT_EVALUABLE"
        },
        "davison_policy": {
            "time_midpoint": "UTC_INSTANT",
            "geographic_midpoint": "BACKEND_DECLARED"
        },
        "relationship_chart_consonance_policy": {
            "point_ids": ["SUN", "MOON"],
            "aspect_policy": {
                "CONJUNCTION": {"angle": 0, "orb": 4},
                "OPPOSITION": {"angle": 180, "orb": 4}
            }
        },
        "draconic_policy": {
            "node_id": "NORTH_NODE",
            "transform": "NORTH_NODE_TO_ZERO",
            "include_angles": True,
            "include_houses": True
        },
        "draconic_aspect_policy": aspect_policy
    }


class TestAutomaticTimeSensitivity(unittest.TestCase):
    def test_policy_is_frozen_and_case_fit_forbidden(self):
        policy = load_birth_time_perturbation_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_BIRTH_TIME_PERTURBATION_V1",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertEqual(
            policy["metric"]["percentile_method"],
            "NEAREST_RANK",
        )

    def test_generator_builds_cartesian_grid_and_metrics(self):
        result = generate_birth_time_sensitivity(
            raw_input(),
            astrology_backend=TimeSensitiveNatalBackend(),
            davison_backend=TimeSensitiveDavisonBackend(),
        )
        self.assertEqual(result["state"], "EVALUABLE")
        self.assertEqual(result["perturbation_count"], 48)
        self.assertGreaterEqual(result["delta90"], 0.0)
        self.assertGreaterEqual(result["preserved_fraction"], 0.0)
        self.assertLessEqual(result["preserved_fraction"], 1.0)
        self.assertEqual(
            result["preservation_metric"],
            "MEAN_BASELINE_CORE_ROOT_RETENTION",
        )
        self.assertFalse(result["idd_recomputed"])
        self.assertFalse(result["ice_used"])

    def test_configured_m23_prefers_automatic_generator(self):
        handler = configured_handlers(
            astrology_backend=TimeSensitiveNatalBackend(),
            davison_backend=TimeSensitiveDavisonBackend(),
        )["M23"]
        result = handler(
            ModuleContext(
                module_id="M23",
                module_name="time_sensitivity",
                mode="FULL",
                raw_input=raw_input(),
                canonical_snapshot={},
                prior_results={},
            )
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["time_sensitivity"]
        self.assertTrue(output["perturbations_generated_by_m23"])
        self.assertEqual(
            output["generator_policy_id"],
            "ALMAS_BIRTH_TIME_PERTURBATION_V1",
        )

    def test_missing_reliability_is_not_evaluable_without_legacy(self):
        raw = raw_input()
        raw["subjects"][0]["time_reliability"] = None
        handler = configured_handlers(
            astrology_backend=TimeSensitiveNatalBackend(),
            davison_backend=TimeSensitiveDavisonBackend(),
        )["M23"]
        result = handler(
            ModuleContext(
                module_id="M23",
                module_name="time_sensitivity",
                mode="FULL",
                raw_input=raw,
                canonical_snapshot={},
                prior_results={},
            )
        )
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)

    def test_missing_reliability_can_use_explicit_legacy_summary(self):
        raw = raw_input()
        raw["subjects"][0]["time_reliability"] = None
        raw["time_sensitivity_summary"] = {
            "preregistration_ref": "LEGACY-Q4",
            "delta90": 5.0,
            "preserved_fraction": 0.9,
            "perturbation_count": 10
        }
        handler = configured_handlers(
            astrology_backend=TimeSensitiveNatalBackend(),
            davison_backend=TimeSensitiveDavisonBackend(),
        )["M23"]
        result = handler(
            ModuleContext(
                module_id="M23",
                module_name="time_sensitivity",
                mode="FULL",
                raw_input=raw,
                canonical_snapshot={},
                prior_results={},
            )
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertFalse(
            result.canonical_updates["time_sensitivity"][
                "perturbations_generated_by_m23"
            ]
        )


if __name__ == "__main__":
    unittest.main()
