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


if __name__ == "__main__":
    unittest.main()
