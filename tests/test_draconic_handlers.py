import unittest

from almas_tfa.draconic_handlers import (
    m10_individual_draconics,
    m11_natal_draconic_cross,
    m12_draconic_draconic,
)
from almas_tfa.module_contract import ExecutionStatus, ModuleContext


def context(module_id, raw, canonical):
    return ModuleContext(
        module_id=module_id,
        module_name=module_id,
        mode="FULL",
        raw_input=raw,
        canonical_snapshot=canonical,
        prior_results={},
    )


class TestDraconicHandlers(unittest.TestCase):
    def setUp(self):
        self.natal = {
            "charts": {
                "A": {
                    "positions": {
                        "NORTH_NODE": {
                            "longitude": 100.0,
                            "point_type": "NODE",
                        },
                        "SUN": {
                            "longitude": 130.0,
                            "point_type": "LUMINARY",
                        },
                    },
                    "angles": {"ASC": 160.0},
                    "houses": {
                        str(i): float((100 + (i - 1) * 30) % 360)
                        for i in range(1, 13)
                    },
                },
                "B": {
                    "positions": {
                        "NORTH_NODE": {
                            "longitude": 200.0,
                            "point_type": "NODE",
                        },
                        "SUN": {
                            "longitude": 330.0,
                            "point_type": "LUMINARY",
                        },
                        "MOON": {
                            "longitude": 232.0,
                            "point_type": "LUMINARY",
                        },
                    },
                    "angles": {"ASC": 260.0},
                    "houses": {
                        str(i): float((200 + (i - 1) * 30) % 360)
                        for i in range(1, 13)
                    },
                },
            }
        }
        self.raw = {
            "draconic_policy": {
                "node_id": "NORTH_NODE",
                "transform": "NORTH_NODE_TO_ZERO",
                "include_angles": True,
                "include_houses": True,
            },
            "draconic_aspect_policy": {
                "CONJUNCTION": {"angle": 0, "orb": 3},
                "OPPOSITION": {"angle": 180, "orb": 3},
            },
        }

    def test_m10_places_declared_node_at_zero(self):
        result = m10_individual_draconics(
            context("M10", self.raw, {"natal": self.natal})
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        charts = result.canonical_updates["draconic"]["charts"]

        self.assertAlmostEqual(charts["A"]["positions"]["NORTH_NODE"]["longitude"], 0)
        self.assertAlmostEqual(charts["A"]["positions"]["SUN"]["longitude"], 30)
        self.assertAlmostEqual(charts["A"]["angles"]["ASC"], 60)
        self.assertAlmostEqual(charts["A"]["houses"]["1"], 0)

    def test_m10_requires_declared_node(self):
        raw = {
            "draconic_policy": {
                "node_id": "MISSING_NODE",
                "transform": "NORTH_NODE_TO_ZERO",
            }
        }
        result = m10_individual_draconics(
            context("M10", raw, {"natal": self.natal})
        )
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)

    def test_m11_and_m12_use_draconic_output(self):
        m10 = m10_individual_draconics(
            context("M10", self.raw, {"natal": self.natal})
        )
        canonical = {
            "natal": self.natal,
            "draconic": m10.canonical_updates["draconic"],
        }

        m11 = m11_natal_draconic_cross(
            context("M11", self.raw, canonical)
        )
        m12 = m12_draconic_draconic(
            context("M12", self.raw, canonical)
        )

        self.assertEqual(m11.status, ExecutionStatus.COMPLETED)
        self.assertEqual(m12.status, ExecutionStatus.COMPLETED)
        self.assertGreaterEqual(
            m11.canonical_updates["natal_draconic_cross"]["contact_count"],
            1,
        )
        self.assertGreaterEqual(
            m12.canonical_updates["draconic_draconic"]["contact_count"],
            1,
        )
        self.assertTrue(
            m12.canonical_updates["draconic_draconic"]["corroborative_only"]
        )


if __name__ == "__main__":
    unittest.main()
