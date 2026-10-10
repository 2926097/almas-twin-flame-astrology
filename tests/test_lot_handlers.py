import unittest
import json
from pathlib import Path

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
                        "houses": {
                            str(i): float((100 + (i - 1) * 30) % 360)
                            for i in range(1, 13)
                        },
                    },
                    "B": {
                        "positions": {
                            "SUN": {"longitude": 210.0},
                            "MOON": {"longitude": 180.0},
                        },
                        "angles": {"ASC": 20.0},
                        "houses": {
                            str(i): float((20 + (i - 1) * 30) % 360)
                            for i in range(1, 13)
                        },
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
        self.assertEqual(lots["A"]["FORTUNE"]["sign"], "LEO")
        self.assertAlmostEqual(
            lots["A"]["FORTUNE"]["degree_in_sign"],
            10.0,
        )
        self.assertEqual(lots["A"]["FORTUNE"]["house"], 2)
        self.assertIsNone(
            lots["A"]["FORTUNE"]["corroborating_source_ref"]
        )

    def test_calculated_virtual_point_gets_position_profile_when_enabled(self):
        context = ModuleContext(
            module_id="M13", module_name="lots", mode="FULL",
            raw_input={
                "maximum_definition_context": True,
                "lot_policy": {
                    "sect_by_subject": {"A": "DAY", "B": "DAY"},
                    "lots": [{
                        "id": "FORTUNE", "source_ref": "SRC_TEST",
                        "formula": {"base": "ASC", "add": ["MOON"], "subtract": ["SUN"]},
                    }],
                },
                "rulership_policy": {"LEO": ["SUN"]},
            },
            canonical_snapshot=self.canonical, prior_results={},
        )
        lots = m13_lots(context).canonical_updates["lots"]["subjects"]["A"]
        profile = lots["FORTUNE"]["position_profile"]
        self.assertEqual(profile["point_type"], "LOT")
        self.assertEqual(profile["sign"], "LEO")
        self.assertEqual(profile["sign_rulers"]["rulers"], ["SUN"])
        self.assertEqual(profile["motion"]["state"], "NOT_EVALUABLE")
        self.assertEqual(profile["motion"]["interpretation_state"], "NOT_AUTHORED")
        from jsonschema import Draft202012Validator
        schema = json.loads((Path(__file__).resolve().parents[1] / "schemas/positional-hermeneutics.schema.json").read_text())
        Draft202012Validator(schema).validate(profile)

    def test_positional_schema_accepts_legacy_profiles_without_provenance_fields(self):
        context = ModuleContext(
            module_id="M13", module_name="lots", mode="FULL",
            raw_input={
                "maximum_definition_context": True,
                "lot_policy": {"sect_by_subject": {"A": "DAY", "B": "DAY"}, "lots": [{
                    "id": "FORTUNE", "source_ref": "SRC_TEST",
                    "formula": {"base": "ASC", "add": ["MOON"], "subtract": ["SUN"]},
                }]},
                "rulership_policy": {"LEO": ["SUN"]},
            },
            canonical_snapshot=self.canonical, prior_results={},
        )
        profile = m13_lots(context).canonical_updates["lots"]["subjects"]["A"]["FORTUNE"]["position_profile"]
        profile["decan"].pop("ruler_source_refs")
        profile["sign_rulers"].pop("source_refs")
        from jsonschema import Draft202012Validator
        schema = json.loads((Path(__file__).resolve().parents[1] / "schemas/positional-hermeneutics.schema.json").read_text())
        Draft202012Validator(schema).validate(profile)

    def test_default_policy_resolves_fortune_and_spirit_from_house_sect(self):
        canonical = {
            **self.canonical,
            "natal_context": {
                "subjects": {
                    "A": {
                        "house_placements": {
                            "SUN": {"house": 10}
                        }
                    },
                    "B": {
                        "house_placements": {
                            "SUN": {"house": 4}
                        }
                    },
                }
            },
        }
        context = ModuleContext(
            module_id="M13",
            module_name="lots",
            mode="FULL",
            raw_input={},
            canonical_snapshot=canonical,
            prior_results={},
        )
        result = m13_lots(context)
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["lots"]
        self.assertEqual(
            output["policy_source"],
            "ALMAS_HELLENISTIC_LOTS_V1",
        )
        self.assertEqual(output["sect_by_subject"]["A"], "DAY")
        self.assertEqual(output["sect_by_subject"]["B"], "NIGHT")
        self.assertAlmostEqual(
            output["subjects"]["A"]["FORTUNE"]["longitude"],
            130.0,
        )
        self.assertAlmostEqual(
            output["subjects"]["A"]["SPIRIT"]["longitude"],
            70.0,
        )
        self.assertEqual(
            output["subjects"]["A"]["SPIRIT"]["sign"],
            "GEMINI",
        )
        self.assertEqual(output["subjects"]["A"]["SPIRIT"]["house"], 12)
        self.assertEqual(
            output["subjects"]["A"]["SPIRIT"][
                "corroborating_source_ref"
            ],
            "vettius_valens_anthology_lots",
        )
        self.assertAlmostEqual(
            output["subjects"]["B"]["FORTUNE"]["longitude"],
            50.0,
        )
        self.assertAlmostEqual(
            output["subjects"]["B"]["SPIRIT"]["longitude"],
            350.0,
        )

    def test_calculated_lot_without_houses_keeps_house_unknown(self):
        canonical = {
            "natal": {
                "charts": {
                    subject_id: {
                        key: value
                        for key, value in chart.items()
                        if key != "houses"
                    }
                    for subject_id, chart in self.canonical["natal"]["charts"].items()
                }
            }
        }
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
        result = m13_lots(
            ModuleContext(
                module_id="M13",
                module_name="lots",
                mode="FULL",
                raw_input=raw,
                canonical_snapshot=canonical,
                prior_results={},
            )
        )
        lot = result.canonical_updates["lots"]["subjects"]["A"]["FORTUNE"]

        self.assertEqual(lot["status"], "CALCULATED")
        self.assertEqual(lot["sign"], "LEO")
        self.assertIsNone(lot["house"])

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
        self.assertIsNone(lot["sign"])
        self.assertIsNone(lot["house"])


if __name__ == "__main__":
    unittest.main()
