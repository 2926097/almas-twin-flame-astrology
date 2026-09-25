import unittest

from almas_tfa.lot_handlers import m13_lots
from almas_tfa.module_contract import ExecutionStatus, ModuleContext


class TestLots(unittest.TestCase):
    def setUp(self):
        self.canonical = {
            "natal": {
                "charts": {
                    "A": {
                        "positions": {
                            "SUN": {"longitude": 10.0},
                            "MOON": {"longitude": 40.0},
                        },
                        "angles": {"ASC": 100.0},
                    },
                    "B": {
                        "positions": {
                            "SUN": {"longitude": 210.0},
                            "MOON": {"longitude": 180.0},
                        },
                        "angles": {"ASC": 20.0},
                    },
                }
            }
        }

    def test_formula_and_source_are_preserved(self):
        raw = {
            "lot_policy": {
                "sect_by_subject": {"A": "DAY", "B": "NIGHT"},
                "lots": [
                    {
                        "id": "FORTUNE",
                        "source_ref": "SRC_TEST",
                        "variants": {
                            "DAY": {
                                "base": "ASC",
                                "add": ["MOON"],
                                "subtract": ["SUN"],
                            },
                            "NIGHT": {
                                "base": "ASC",
                                "add": ["SUN"],
                                "subtract": ["MOON"],
                            },
                        },
                    }
                ],
            }
        }
        context = ModuleContext(
            module_id="M13",
            module_name="lots",
            mode="FULL",
            raw_input=raw,
            canonical_snapshot=self.canonical,
            prior_results={},
        )
        result = m13_lots(context)
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        lots = result.canonical_updates["lots"]["subjects"]
        self.assertAlmostEqual(lots["A"]["FORTUNE"]["longitude"], 130.0)
        self.assertAlmostEqual(lots["B"]["FORTUNE"]["longitude"], 50.0)
        self.assertEqual(lots["A"]["FORTUNE"]["source_ref"], "SRC_TEST")

    def test_missing_sect_does_not_guess_variant(self):
        raw = {
            "lot_policy": {
                "lots": [
                    {
                        "id": "FORTUNE",
                        "source_ref": "SRC_TEST",
                        "variants": {
                            "DAY": {"base": "ASC", "add": ["MOON"], "subtract": ["SUN"]},
                            "NIGHT": {"base": "ASC", "add": ["SUN"], "subtract": ["MOON"]},
                        },
                    }
                ]
            }
        }
        context = ModuleContext(
            module_id="M13",
            module_name="lots",
            mode="FULL",
            raw_input=raw,
            canonical_snapshot=self.canonical,
            prior_results={},
        )
        result = m13_lots(context)
        lot = result.canonical_updates["lots"]["subjects"]["A"]["FORTUNE"]
        self.assertEqual(lot["status"], "NOT_EVALUABLE")
        self.assertIsNone(lot["longitude"])


if __name__ == "__main__":
    unittest.main()
