import unittest

from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.secondary_handlers import m14_secondary_symbolic


class TestSecondarySymbolic(unittest.TestCase):
    def setUp(self):
        self.canonical = {
            "natal": {
                "charts": {
                    "A": {
                        "positions": {
                            "SUN": {"longitude": 10.0, "point_type": "LUMINARY"},
                            "JUNO": {"longitude": 40.0, "point_type": "ASTEROID"},
                        }
                    },
                    "B": {
                        "positions": {
                            "MOON": {"longitude": 42.0, "point_type": "LUMINARY"},
                            "EROS": {"longitude": 190.0, "point_type": "ASTEROID"},
                        }
                    },
                }
            }
        }

    def context(self, policy):
        return ModuleContext(
            module_id="M14",
            module_name="secondary_symbolic",
            mode="FULL",
            raw_input={"secondary_symbolic_policy": policy},
            canonical_snapshot=self.canonical,
            prior_results={},
        )

    def test_only_declared_secondary_points_enter_layer(self):
        result = m14_secondary_symbolic(
            self.context(
                {
                    "point_ids": ["JUNO", "EROS"],
                    "support_only": True,
                    "aspect_policy": {
                        "CONJUNCTION": {"angle": 0, "orb": 3},
                        "OPPOSITION": {"angle": 180, "orb": 3},
                    },
                }
            )
        )

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["secondary_symbolic"]
        self.assertTrue(output["support_only"])
        self.assertGreaterEqual(output["contact_count"], 1)
        for contact in output["contacts"]:
            self.assertTrue(
                contact["point_a_secondary"] or contact["point_b_secondary"]
            )
            self.assertTrue(contact["support_only"])

    def test_support_only_cannot_be_disabled(self):
        with self.assertRaises(ValueError):
            m14_secondary_symbolic(
                self.context(
                    {
                        "point_ids": ["JUNO"],
                        "support_only": False,
                        "aspect_policy": {
                            "CONJUNCTION": {"angle": 0, "orb": 3}
                        },
                    }
                )
            )


if __name__ == "__main__":
    unittest.main()
