import unittest

from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.symmetry_handlers import (
    antiscion_longitude,
    contra_antiscion_longitude,
    m05_declinations,
    m06_antiscia,
)


def ctx(module_id, natal, raw):
    return ModuleContext(
        module_id=module_id,
        module_name=module_id,
        mode="FULL",
        raw_input=raw,
        canonical_snapshot={"natal": natal},
        prior_results={},
    )


class TestDeclinationsAndAntiscia(unittest.TestCase):
    def setUp(self):
        self.natal = {
            "charts": {
                "A": {
                    "subject_id": "A",
                    "timed": True,
                    "positions": {
                        "SUN": {
                            "longitude": 10.0,
                            "declination": 5.0,
                            "point_type": "LUMINARY",
                        },
                        "MARS": {
                            "longitude": 20.0,
                            "declination": 12.0,
                            "point_type": "PLANET",
                        },
                    },
                },
                "B": {
                    "subject_id": "B",
                    "timed": True,
                    "positions": {
                        "MOON": {
                            "longitude": 169.0,
                            "declination": 5.5,
                            "point_type": "LUMINARY",
                        },
                        "VENUS": {
                            "longitude": 350.5,
                            "declination": -5.2,
                            "point_type": "PLANET",
                        },
                    },
                },
            }
        }

    def test_antiscion_formula(self):
        self.assertAlmostEqual(antiscion_longitude(10.0), 170.0)
        self.assertAlmostEqual(contra_antiscion_longitude(10.0), 350.0)

    def test_m05_parallel_and_contra_parallel(self):
        result = m05_declinations(
            ctx(
                "M05",
                self.natal,
                {
                    "declination_policy": {
                        "parallel_orb": 1.0,
                        "contra_parallel_orb": 1.0,
                    }
                },
            )
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        contacts = result.canonical_updates["declinations"]["contacts"]
        relations = {(x["point_a"], x["point_b"], x["relation"]) for x in contacts}
        self.assertIn(("SUN", "MOON", "PARALLEL"), relations)
        self.assertIn(("SUN", "VENUS", "CONTRA_PARALLEL"), relations)

    def test_m05_requires_declared_policy(self):
        result = m05_declinations(ctx("M05", self.natal, {}))
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)

    def test_m06_antiscia_and_contra_antiscia(self):
        result = m06_antiscia(
            ctx(
                "M06",
                self.natal,
                {
                    "antiscia_policy": {
                        "antiscia_orb": 1.5,
                        "contra_antiscia_orb": 1.0,
                    }
                },
            )
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        contacts = result.canonical_updates["antiscia"]["contacts"]
        relations = {(x["point_a"], x["point_b"], x["relation"]) for x in contacts}
        self.assertIn(("SUN", "MOON", "ANTISCION"), relations)
        self.assertIn(("SUN", "VENUS", "CONTRA_ANTISCION"), relations)

    def test_m06_requires_declared_policy(self):
        result = m06_antiscia(ctx("M06", self.natal, {}))
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)


if __name__ == "__main__":
    unittest.main()
