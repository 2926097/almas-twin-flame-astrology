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


    def test_complete_review_derives_zero_when_no_contradictions_exist(self):
        result = m20_counterevidence(
            context({"counterevidence_review_complete": True})
        )
        output = result.canonical_updates["counterevidence"]
        self.assertEqual(output["ice_state"], "DERIVED_AUTONOMOUS_V1")
        self.assertEqual(
            output["ice_by_model"],
            {"AF": 0.0, "KA": 0.0, "AG": 0.0, "LG": 0.0},
        )
        self.assertEqual(output["ice_formula_id"], "ALMAS_ICE_AUTONOMOUS_V1")

    def test_autonomous_ice_collapses_same_dependency_family(self):
        result = m20_counterevidence(
            context(
                {
                    "counterevidence_review_complete": True,
                    "counterevidence_items": [
                        {
                            "id": "CE-A",
                            "kind": "EXPLICIT_CONTRADICTION",
                            "models": ["LG"],
                            "contradiction_key": "A",
                            "dependency_family": "FACTS",
                            "severity": 0.2,
                        },
                        {
                            "id": "CE-B",
                            "kind": "EXPLICIT_CONTRADICTION",
                            "models": ["LG"],
                            "contradiction_key": "B",
                            "dependency_family": "FACTS",
                            "severity": 0.8,
                        },
                        {
                            "id": "CE-C",
                            "kind": "STRUCTURAL_INCOMPATIBILITY",
                            "models": ["LG"],
                            "contradiction_key": "C",
                            "dependency_family": "ASTRO_STRUCTURE",
                            "severity": 0.5,
                        },
                    ],
                }
            )
        )
        output = result.canonical_updates["counterevidence"]
        self.assertAlmostEqual(output["ice_by_model"]["LG"], 70.0)
        self.assertEqual(
            output["models"]["LG"]["dependency_family_scores"],
            {"ASTRO_STRUCTURE": 0.5, "FACTS": 0.8},
        )

    def test_complete_review_requires_severity(self):
        with self.assertRaises(ValueError):
            m20_counterevidence(
                context(
                    {
                        "counterevidence_review_complete": True,
                        "counterevidence_items": [
                            {
                                "id": "CE-NO-SEVERITY",
                                "kind": "EXPLICIT_CONTRADICTION",
                                "models": ["AF"],
                                "contradiction_key": "A",
                                "dependency_family": "FACTS",
                            }
                        ],
                    }
                )
            )

    def test_precomputed_ice_must_match_autonomous_when_both_are_declared(self):
        with self.assertRaises(ValueError):
            m20_counterevidence(
                context(
                    {
                        "counterevidence_review_complete": True,
                        "ice_by_model": {"AF": 1, "KA": 0, "AG": 0, "LG": 0},
                    }
                )
            )

    def test_matching_precomputed_ice_is_only_a_consistency_check(self):
        result = m20_counterevidence(
            context(
                {
                    "counterevidence_review_complete": True,
                    "ice_by_model": {"AF": 0, "KA": 0, "AG": 0, "LG": 0},
                }
            )
        )
        output = result.canonical_updates["counterevidence"]
        self.assertEqual(output["ice_state"], "DERIVED_AUTONOMOUS_V1")
        self.assertTrue(output["precomputed_consistency_checked"])


if __name__ == "__main__":
    unittest.main()
