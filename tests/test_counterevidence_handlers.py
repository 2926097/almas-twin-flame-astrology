import unittest

from almas_tfa.counterevidence_handlers import m20_counterevidence
from almas_tfa.module_contract import ExecutionStatus, ModuleContext


def context(raw):
    return ModuleContext(
        module_id="M20",
        module_name="counterevidence",
        mode="FULL",
        raw_input=raw,
        canonical_snapshot={},
        prior_results={},
    )


class TestCounterevidence(unittest.TestCase):
    def test_deduplicates_same_contradiction_family(self):
        raw = {
            "counterevidence_items": [
                {
                    "id": "CE1",
                    "kind": "EXPLICIT_CONTRADICTION",
                    "models": ["LG"],
                    "contradiction_key": "NO_RECIPROCITY_STRUCTURAL",
                    "dependency_family": "FACTS",
                    "essential": False,
                    "severity": 0.4,
                },
                {
                    "id": "CE2",
                    "kind": "EXPLICIT_CONTRADICTION",
                    "models": ["LG"],
                    "contradiction_key": "NO_RECIPROCITY_STRUCTURAL",
                    "dependency_family": "FACTS",
                    "essential": True,
                    "severity": 0.8,
                },
            ]
        }
        result = m20_counterevidence(context(raw))
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["counterevidence"]
        self.assertEqual(output["models"]["LG"]["contradiction_count"], 1)
        self.assertTrue(output["models"]["LG"]["essential_contradiction"])
        self.assertEqual(len(output["suppressed"]), 1)

    def test_missing_data_cannot_be_counterevidence(self):
        raw = {
            "counterevidence_items": [
                {
                    "id": "CE1",
                    "kind": "MISSING_DATA",
                    "models": ["AG"],
                    "contradiction_key": "MISSING_BIRTH_TIME",
                    "dependency_family": "DATA",
                }
            ]
        }
        with self.assertRaises(ValueError):
            m20_counterevidence(context(raw))

    def test_precomputed_ice_is_preserved_not_rederived(self):
        result = m20_counterevidence(
            context({"ice_by_model": {"AF": 0, "KA": 5, "AG": 10, "LG": 20}})
        )
        output = result.canonical_updates["counterevidence"]
        self.assertEqual(output["ice_state"], "PRECOMPUTED")
        self.assertEqual(output["ice_by_model"]["LG"], 20.0)
        self.assertFalse(output["missing_data_penalized"])

    def test_autonomous_ice_is_derived_only_from_complete_assessment(self):
        raw = {
            "counterevidence_assessment_complete": True,
            "counterevidence_items": [
                {
                    "id": "CE1",
                    "kind": "EXPLICIT_CONTRADICTION",
                    "models": ["LG"],
                    "contradiction_key": "FACT_A",
                    "dependency_family": "FACTS",
                    "essential": False,
                    "severity": 0.6,
                },
                {
                    "id": "CE2",
                    "kind": "STRUCTURAL_INCOMPATIBILITY",
                    "models": ["LG"],
                    "contradiction_key": "STRUCT_A",
                    "dependency_family": "STRUCTURE",
                    "essential": False,
                    "severity": 0.5,
                },
            ],
        }
        result = m20_counterevidence(context(raw))
        output = result.canonical_updates["counterevidence"]
        self.assertEqual(output["ice_state"], "AUTONOMOUS")
        self.assertEqual(output["ice_formula_id"], "ALMAS_ICE_AUTONOMOUS_V1")
        self.assertAlmostEqual(output["ice_by_model"]["LG"], 80.0)
        self.assertEqual(output["ice_by_model"]["AF"], 0.0)
        self.assertTrue(output["assessment_complete"])

    def test_complete_empty_assessment_yields_zero_ice(self):
        result = m20_counterevidence(
            context(
                {
                    "counterevidence_assessment_complete": True,
                    "counterevidence_items": [],
                }
            )
        )
        output = result.canonical_updates["counterevidence"]
        self.assertEqual(
            output["ice_by_model"],
            {"AF": 0.0, "KA": 0.0, "AG": 0.0, "LG": 0.0},
        )

    def test_autonomous_and_precomputed_ice_are_mutually_exclusive(self):
        with self.assertRaises(ValueError):
            m20_counterevidence(
                context(
                    {
                        "counterevidence_assessment_complete": True,
                        "ice_by_model": {
                            "AF": 0, "KA": 0, "AG": 0, "LG": 0
                        },
                    }
                )
            )

    def test_autonomous_ice_requires_strict_severity_on_retained_items(self):
        invalid_items = [
            {
                "id": "CE1",
                "kind": "EXPLICIT_CONTRADICTION",
                "models": ["AF"],
                "contradiction_key": "NO_SEVERITY",
                "dependency_family": "FACTS",
                "essential": False,
            },
            {
                "id": "CE2",
                "kind": "EXPLICIT_CONTRADICTION",
                "models": ["AF"],
                "contradiction_key": "BOOL_SEVERITY",
                "dependency_family": "FACTS",
                "essential": False,
                "severity": True,
            },
            {
                "id": "CE3",
                "kind": "EXPLICIT_CONTRADICTION",
                "models": ["AF"],
                "contradiction_key": "STRING_SEVERITY",
                "dependency_family": "FACTS",
                "essential": False,
                "severity": "0.5",
            },
        ]
        for item in invalid_items:
            with self.subTest(item=item["id"]):
                with self.assertRaises(ValueError):
                    m20_counterevidence(
                        context(
                            {
                                "counterevidence_assessment_complete": True,
                                "counterevidence_items": [item],
                            }
                        )
                    )

    def test_partial_precomputed_ice_is_rejected(self):
        with self.assertRaises(ValueError):
            m20_counterevidence(
                context({"ice_by_model": {"AF": 0, "KA": 5, "AG": 10}})
            )

    def test_empty_precomputed_ice_map_is_rejected(self):
        with self.assertRaises(ValueError):
            m20_counterevidence(context({"ice_by_model": {}}))

    def test_precomputed_ice_accepts_closed_interval_boundaries(self):
        result = m20_counterevidence(
            context({"ice_by_model": {"AF": 0, "KA": 100, "AG": 0, "LG": 100}})
        )
        ice = result.canonical_updates["counterevidence"]["ice_by_model"]
        self.assertEqual(ice, {"AF": 0.0, "KA": 100.0, "AG": 0.0, "LG": 100.0})

    def test_non_numeric_and_boolean_ice_are_rejected(self):
        for invalid in ("0", True):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    m20_counterevidence(
                        context(
                            {
                                "ice_by_model": {
                                    "AF": invalid,
                                    "KA": 0,
                                    "AG": 0,
                                    "LG": 0,
                                }
                            }
                        )
                    )


if __name__ == "__main__":
    unittest.main()
