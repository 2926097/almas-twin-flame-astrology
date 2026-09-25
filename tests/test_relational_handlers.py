import unittest

from almas_tfa.astrology_geometry import (
    angular_distance,
    house_for_longitude,
    match_declared_aspect,
    zodiac_sign,
)
from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.relational_handlers import (
    m03_synastry,
    m04_nodes_angles_houses_regencies,
)


def context_for(module_id, canonical, raw):
    return ModuleContext(
        module_id=module_id,
        module_name=module_id,
        mode="FULL",
        raw_input=raw,
        canonical_snapshot=canonical,
        prior_results={},
    )


class TestAstrologyGeometry(unittest.TestCase):
    def test_angular_distance_wraps(self):
        self.assertAlmostEqual(angular_distance(359, 1), 2.0)

    def test_zodiac_sign(self):
        result = zodiac_sign(44.5)
        self.assertEqual(result["sign"], "TAURUS")
        self.assertAlmostEqual(result["degree_in_sign"], 14.5)

    def test_declared_aspect_has_no_implicit_orb(self):
        policy = {
            "CONJUNCTION": {"angle": 0, "orb": 3},
            "OPPOSITION": {"angle": 180, "orb": 5},
        }
        match = match_declared_aspect(10, 12, policy)
        self.assertEqual(match["aspect"], "CONJUNCTION")
        self.assertAlmostEqual(match["orb"], 2.0)
        self.assertIsNone(match_declared_aspect(10, 15, policy))

    def test_house_placement_wraps_house_twelve(self):
        cusps = {str(i): (350 + (i - 1) * 30) % 360 for i in range(1, 13)}
        self.assertEqual(house_for_longitude(355, cusps), 1)
        self.assertEqual(house_for_longitude(345, cusps), 12)


class TestRelationalHandlers(unittest.TestCase):
    def setUp(self):
        self.natal = {
            "natal": {
                "charts": {
                    "A": {
                        "subject_id": "A",
                        "timed": True,
                        "backend_id": "TEST",
                        "backend_version": "1",
                        "positions": {
                            "SUN": {
                                "longitude": 10.0,
                                "point_type": "LUMINARY",
                            },
                            "NORTH_NODE": {
                                "longitude": 190.0,
                                "point_type": "NODE",
                            },
                        },
                        "angles": {"ASC": 35.0, "MC": 280.0},
                        "houses": {
                            str(i): float((i - 1) * 30)
                            for i in range(1, 13)
                        },
                    },
                    "B": {
                        "subject_id": "B",
                        "timed": False,
                        "backend_id": "TEST",
                        "backend_version": "1",
                        "positions": {
                            "MOON": {
                                "longitude": 12.0,
                                "point_type": "LUMINARY",
                            },
                            "SOUTH_NODE": {
                                "longitude": 8.0,
                                "point_type": "NODE",
                            },
                        },
                    },
                }
            }
        }

    def test_m03_synastry_uses_declared_policy(self):
        raw = {
            "aspect_policy": {
                "CONJUNCTION": {"angle": 0, "orb": 3},
                "OPPOSITION": {"angle": 180, "orb": 4},
            }
        }
        result = m03_synastry(context_for("M03", self.natal, raw))

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        contacts = result.canonical_updates["synastry"]["contacts"]
        pairs = {(c["point_a"], c["point_b"], c["aspect"]) for c in contacts}
        self.assertIn(("SUN", "MOON", "CONJUNCTION"), pairs)
        self.assertIn(("NORTH_NODE", "MOON", "OPPOSITION"), pairs)

    def test_m03_without_policy_is_not_evaluable(self):
        result = m03_synastry(context_for("M03", self.natal, {}))
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)

    def test_m04_context_and_declared_rulership(self):
        raw = {
            "rulership_policy": {
                "ARIES": ["MARS"],
                "TAURUS": ["VENUS"],
                "LIBRA": ["VENUS"],
            }
        }
        result = m04_nodes_angles_houses_regencies(
            context_for("M04", self.natal, raw)
        )

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        subjects = result.canonical_updates["natal_context"]["subjects"]

        self.assertEqual(subjects["A"]["point_signs"]["SUN"]["sign"], "ARIES")
        self.assertEqual(subjects["A"]["house_placements"]["SUN"]["house"], 1)
        self.assertIn("NORTH_NODE", subjects["A"]["nodes"])
        self.assertEqual(subjects["A"]["rulerships"]["1"]["rulers"], ["MARS"])

        self.assertEqual(subjects["B"]["house_cusps"], {})
        self.assertTrue(result.limitations)


if __name__ == "__main__":
    unittest.main()
