import unittest

from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.orchestrator import Orchestrator
from almas_tfa.relationship_chart_handlers import (
    DavisonRequest,
    circular_midpoint,
    m07_composite,
    make_m08_davison,
)


def full_manifest():
    return {
        "mode": "FULL",
        "manifest_version": "1.0.0",
        "modules": [
            {"id": f"M{i:02d}", "name": f"module_{i:02d}"}
            for i in range(32)
        ],
    }


class FakeDavisonBackend:
    backend_id = "FAKE_DAVISON"
    backend_version = "0"

    def calculate_davison(self, request: DavisonRequest):
        return {
            "subject_ids": [
                request.subject_a.subject_id,
                request.subject_b.subject_id,
            ],
            "positions": {
                "SUN": {"longitude": 42.0, "point_type": "LUMINARY"}
            },
            "metadata": {"policy": dict(request.policy)},
        }


class TestRelationshipCharts(unittest.TestCase):
    def test_circular_midpoint_wrap(self):
        self.assertAlmostEqual(circular_midpoint(350, 10), 0.0)

    def test_exact_opposition_requires_explicit_resolution(self):
        self.assertIsNone(circular_midpoint(10, 190))
        self.assertAlmostEqual(
            circular_midpoint(10, 190, opposition_tie_break="FORWARD_FROM_A"),
            100.0,
        )
        self.assertAlmostEqual(
            circular_midpoint(10, 190, opposition_tie_break="FORWARD_FROM_B"),
            280.0,
        )

    def test_m07_composite(self):
        natal = {
            "charts": {
                "A": {
                    "positions": {
                        "SUN": {"longitude": 350.0},
                        "MOON": {"longitude": 10.0},
                    },
                    "angles": {"ASC": 20.0},
                },
                "B": {
                    "positions": {
                        "SUN": {"longitude": 10.0},
                        "MOON": {"longitude": 190.0},
                    },
                    "angles": {"ASC": 40.0},
                },
            }
        }
        context = ModuleContext(
            module_id="M07",
            module_name="composite",
            mode="FULL",
            raw_input={
                "composite_policy": {
                    "midpoint_mode": "SHORTEST_ARC",
                    "opposition_tie_break": "NOT_EVALUABLE",
                }
            },
            canonical_snapshot={"natal": natal},
            prior_results={},
        )
        result = m07_composite(context)

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        composite = result.canonical_updates["composite"]
        self.assertAlmostEqual(composite["positions"]["SUN"]["longitude"], 0.0)
        self.assertTrue(composite["positions"]["MOON"]["ambiguous"])
        self.assertAlmostEqual(composite["angles"]["ASC"]["longitude"], 30.0)

    def test_m08_davison_uses_injected_backend(self):
        subjects = [
            {
                "id": "A",
                "birth_date": "2001-02-03",
                "birth_time": "09:17",
                "timezone": "Europe/Paris",
                "latitude": 40.0,
                "longitude": -3.0,
            },
            {
                "id": "B",
                "birth_date": "2002-04-05",
                "birth_time": "12:00",
                "timezone": "America/New_York",
                "latitude": 10.0,
                "longitude": 20.0,
            },
        ]

        run = Orchestrator(
            {"M08": make_m08_davison(FakeDavisonBackend())}
        ).run(
            {
                "mode": "FULL",
                "subjects": subjects,
                "davison_policy": {
                    "time_midpoint": "UTC_INSTANT",
                    "geographic_midpoint": "BACKEND_DECLARED",
                },
            },
            full_manifest(),
        )

        self.assertEqual(run.results["M08"].status, ExecutionStatus.COMPLETED)
        self.assertEqual(
            run.canonical["davison"]["chart"]["backend_id"],
            "FAKE_DAVISON",
        )

    def test_m08_rejects_hidden_geocoding(self):
        subjects = [
            {
                "id": "A",
                "birth_date": "2001-02-03",
                "birth_time": "09:17",
                "timezone": "Europe/Paris",
                "place": "Ciudad Sintética A",
            },
            {
                "id": "B",
                "birth_date": "2002-04-05",
                "birth_time": "12:00",
                "timezone": "Europe/Paris",
                "place": "Ciudad Sintética B",
            },
        ]

        run = Orchestrator(
            {"M08": make_m08_davison(FakeDavisonBackend())}
        ).run(
            {
                "mode": "FULL",
                "subjects": subjects,
                "davison_policy": {"time_midpoint": "UTC_INSTANT"},
            },
            full_manifest(),
        )
        self.assertEqual(run.results["M08"].status, ExecutionStatus.NOT_EVALUABLE)


if __name__ == "__main__":
    unittest.main()
