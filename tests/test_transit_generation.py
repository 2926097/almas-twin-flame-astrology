from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import unittest

from almas_tfa.module_contract import ModuleContext
from almas_tfa.temporal_handlers import make_m26_temporal_activation_auto
from almas_tfa.transit_generation import generate_ttransit_signals


ROOT = Path(__file__).resolve().parents[1]


ASPECT_POLICY = {
    "CONJUNCTION": {"angle": 0.0, "orb": 2.0},
    "SEXTILE": {"angle": 60.0, "orb": 2.0},
    "SQUARE": {"angle": 90.0, "orb": 2.0},
    "TRINE": {"angle": 120.0, "orb": 2.0},
    "OPPOSITION": {"angle": 180.0, "orb": 2.0},
}


class FakeTransitBackend:
    backend_id = "FAKE_TRANSIT"
    backend_version = "1"

    def __init__(self, positions=None):
        self.positions = positions or {
            "SATURN": {"longitude": 10.0},
        }
        self.calls = []

    def calculate_transit_positions(self, instant_utc: datetime):
        self.calls.append(instant_utc)
        return {
            "instant_utc": instant_utc.isoformat(),
            "positions": self.positions,
            "backend_id": self.backend_id,
            "backend_version": self.backend_version,
            "backend_provenance": {
                "synthetic": True,
            },
        }


def canonical():
    return {
        "independent_roots": {
            "roots": [
                {
                    "root_id": "R0001",
                    "dependency_families": ["SYN"],
                    "concrete_contacts": [
                        {
                            "subject_a": "A",
                            "point_a": "VENUS",
                            "layer_a": "",
                            "subject_b": "B",
                            "point_b": "MARS",
                            "layer_b": "",
                        }
                    ],
                },
                {
                    "root_id": "R0002",
                    "dependency_families": ["DRACO_CROSS"],
                    "concrete_contacts": [
                        {
                            "subject_a": "A",
                            "point_a": "VENUS",
                            "layer_a": "DRACONIC",
                            "subject_b": "B",
                            "point_b": "MARS",
                            "layer_b": "DRACONIC",
                        }
                    ],
                },
            ]
        },
        "natal_context": {
            "subjects": {
                "A": {
                    "point_signs": {
                        "VENUS": {"longitude": 100.0},
                        "JUPITER": {"longitude": 10.0},
                    },
                    "angles": {
                        "ASC": {"longitude": 40.0},
                        "MC": {"longitude": 200.0},
                    },
                },
                "B": {
                    "point_signs": {
                        "MARS": {"longitude": 190.0},
                    },
                    "angles": {
                        "ASC": {"longitude": 20.0},
                        "MC": {"longitude": 300.0},
                    },
                },
            }
        },
    }


def request(**overrides):
    data = {
        "request_id": "TR-2030-01",
        "instant_utc": "2030-01-01T12:00:00Z",
        "window_status": "PROSPECTIVE_ACTIVATION",
        "preregistered": True,
        "preregistered_window_rule": "TRANSIT-INSTANT-DECLARED",
    }
    data.update(overrides)
    return data


class TransitGenerationTests(unittest.TestCase):
    def test_generates_only_aspects_to_existing_root_endpoints(self):
        backend = FakeTransitBackend()
        signals = generate_ttransit_signals(
            requests=[request()],
            canonical=canonical(),
            aspect_policy=ASPECT_POLICY,
            backend=backend,
        )

        self.assertEqual(len(signals), 2)
        by_target = {
            item["trigger_context"]["target_point"]: item
            for item in signals
        }
        self.assertEqual(set(by_target), {"VENUS", "MARS"})
        self.assertEqual(
            by_target["VENUS"]["trigger_context"]["relation"],
            "SQUARE",
        )
        self.assertEqual(
            by_target["MARS"]["trigger_context"]["relation"],
            "OPPOSITION",
        )
        self.assertTrue(
            all(item["root_id"] == "R0001" for item in signals)
        )
        self.assertNotIn(
            "JUPITER",
            {
                item["trigger_context"]["target_point"]
                for item in signals
            },
        )

    def test_draconic_only_endpoint_is_not_reinterpreted_as_natal(self):
        data = canonical()
        data["independent_roots"]["roots"] = [
            data["independent_roots"]["roots"][1]
        ]
        signals = generate_ttransit_signals(
            requests=[request()],
            canonical=data,
            aspect_policy=ASPECT_POLICY,
            backend=FakeTransitBackend(),
        )
        self.assertEqual(signals, [])

    def test_signal_uses_declared_aspect_exactness_as_strength(self):
        backend = FakeTransitBackend(
            {"SATURN": {"longitude": 11.0}}
        )
        signals = generate_ttransit_signals(
            requests=[request(target_subjects=["A"])],
            canonical=canonical(),
            aspect_policy=ASPECT_POLICY,
            backend=backend,
        )

        self.assertEqual(len(signals), 1)
        signal = signals[0]
        self.assertAlmostEqual(signal["exactitude_orb"], 1.0)
        self.assertAlmostEqual(signal["strength"], 0.75)
        self.assertEqual(signal["activation_class"], "ENDPOINT_ACTIVATION")
        self.assertEqual(signal["temporal_family"], "TTRANSIT")
        self.assertEqual(
            signal["trigger_context"]["method_sources"],
            [
                "astrodienst_transit",
                "hand_planets_in_transit_2002",
            ],
        )

    def test_requires_explicit_aspect_policy_and_never_infers_minor_aspects(self):
        with self.assertRaisesRegex(ValueError, "aspectos mayores"):
            generate_ttransit_signals(
                requests=[request()],
                canonical=canonical(),
                aspect_policy={
                    "QUINCUNX": {"angle": 150.0, "orb": 2.0},
                },
                backend=FakeTransitBackend(),
            )

    def test_requires_timezone_aware_utc_instant(self):
        with self.assertRaisesRegex(ValueError, "offset o Z"):
            generate_ttransit_signals(
                requests=[request(instant_utc="2030-01-01T12:00:00")],
                canonical=canonical(),
                aspect_policy=ASPECT_POLICY,
                backend=FakeTransitBackend(),
            )

    def test_configured_m26_wrapper_feeds_generated_signal_to_existing_m26(self):
        handler = make_m26_temporal_activation_auto(
            FakeTransitBackend(
                {"SATURN": {"longitude": 10.0}}
            )
        )
        raw = {
            "transit_requests": [
                request(target_subjects=["A"])
            ],
            "aspect_policy": ASPECT_POLICY,
        }
        ctx = ModuleContext(
            module_id="M26",
            module_name="M26",
            mode="TEMPORAL",
            raw_input=raw,
            canonical_snapshot=canonical(),
            prior_results={},
        )

        result = handler(ctx)
        output = result.canonical_updates["temporal_activation"]

        self.assertEqual(len(output["signals"]), 1)
        self.assertEqual(
            output["signals"][0]["activation_class"],
            "ENDPOINT_ACTIVATION",
        )
        self.assertAlmostEqual(
            output["signals"][0]["effective_strength"],
            0.7,
        )
        self.assertEqual(
            output["signals"][0]["trigger_context"]["trigger_point"],
            "SATURN",
        )
        self.assertIn("TTRANSIT_GENERATED:1", result.diagnostics)

    def test_temporal_reading_fixture_is_root_first_and_source_traced(self):
        fixture = json.loads(
            (ROOT / "examples/temporal-reading.synthetic.json")
            .read_text(encoding="utf-8")
        )
        signal = fixture["temporal_signal"]

        self.assertEqual(signal["temporal_family"], "TTRANSIT")
        self.assertEqual(
            signal["activation_class"],
            "ENDPOINT_ACTIVATION",
        )
        self.assertAlmostEqual(
            signal["effective_strength"],
            signal["strength"] * signal["k"],
        )
        self.assertEqual(
            [stage["stage"] for stage in fixture["interpretive_sequence"]],
            [
                "ROOT",
                "TRIGGER_FUNCTION",
                "TARGET_FUNCTION",
                "GEOMETRY",
                "ROOT_INTEGRATION",
                "EVOLUTIONARY_FUNCTION",
                "BOUNDARY",
            ],
        )
        self.assertIn(
            "astrodienst_transit",
            fixture["source_refs"],
        )
        self.assertIn(
            "hand_planets_in_transit_2002",
            fixture["source_refs"],
        )
        self.assertIn(
            "predice un hecho",
            fixture["authored_paragraph"],
        )

    def test_wrapper_preserves_manual_signals_alongside_generated(self):
        handler = make_m26_temporal_activation_auto(
            FakeTransitBackend(
                {"SATURN": {"longitude": 10.0}}
            )
        )
        manual = {
            "signal_id": "MANUAL-PROG",
            "root_id": "R0001",
            "structural_family": "SYN",
            "temporal_family": "TPROG",
            "activation_class": "ENDPOINT_ACTIVATION",
            "strength": 0.5,
            "exactitude_orb": 0.5,
            "preregistered_window_rule": "MANUAL-RULE",
            "preregistered": True,
            "window_status": "PROSPECTIVE_ACTIVATION",
        }
        ctx = ModuleContext(
            module_id="M26",
            module_name="M26",
            mode="TEMPORAL",
            raw_input={
                "temporal_signals": [manual],
                "transit_requests": [
                    request(target_subjects=["A"])
                ],
                "aspect_policy": ASPECT_POLICY,
            },
            canonical_snapshot=canonical(),
            prior_results={},
        )

        result = handler(ctx)
        output = result.canonical_updates["temporal_activation"]
        self.assertEqual(
            {item["temporal_family"] for item in output["signals"]},
            {"TPROG", "TTRANSIT"},
        )


if __name__ == "__main__":
    unittest.main()
