import math
import unittest

from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.robustness_index_handlers import m25_robustness


def context(raw=None, canonical=None):
    return ModuleContext(
        module_id="M25",
        module_name="robustness",
        mode="FULL",
        raw_input=raw or {},
        canonical_snapshot=canonical or {},
        prior_results={},
    )


class TestRobustnessIndex(unittest.TestCase):
    def test_m23_enters_automatically(self):
        canonical = {
            "time_sensitivity": {
                "preregistration_ref": "TS-001",
                "robustness_component": 0.8,
            }
        }
        result = m25_robustness(context(canonical=canonical))
        output = result.canonical_updates["robustness_index"]

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertEqual(output["component_count"], 1)
        self.assertAlmostEqual(output["irc"], 80.0)
        self.assertAlmostEqual(output["r_min"], 0.8)
        self.assertEqual(output["time_sensitivity_state"], "INCLUDED")

    def test_ablation_requires_preregistered_conversion_and_m22(self):
        canonical = {
            "ablation": {
                "runs": [],
                "root_survival": [],
                "structural_only": True,
                "dependency_classes_assigned": False,
            }
        }
        raw = {
            "robustness_component_summaries": [
                {
                    "id": "ABLATION_CORE",
                    "kind": "ABLATION",
                    "value": 0.85,
                    "source_module": "M22",
                    "preregistration_ref": "ROB-AB-001",
                    "derivation_ref": "ABLATION-RULE-V1",
                }
            ]
        }
        result = m25_robustness(context(raw, canonical))
        output = result.canonical_updates["robustness_index"]

        self.assertEqual(
            output["ablation_state"],
            "INCLUDED_PREREGISTERED",
        )
        self.assertAlmostEqual(output["irc"], 85.0)

    def test_m22_available_without_mapping_is_not_silently_scored(self):
        canonical = {
            "ablation": {"runs": []},
            "time_sensitivity": {
                "preregistration_ref": "TS-002",
                "robustness_component": 0.9,
            },
        }
        result = m25_robustness(context(canonical=canonical))
        output = result.canonical_updates["robustness_index"]

        self.assertEqual(
            output["ablation_state"],
            "AVAILABLE_NOT_QUANTIFIED",
        )
        self.assertEqual(output["component_count"], 1)

    def test_multiple_components_use_geometric_mean_and_rmin(self):
        canonical = {
            "time_sensitivity": {
                "preregistration_ref": "TS-003",
                "robustness_component": 0.8,
            },
            "ablation": {"runs": []},
        }
        raw = {
            "robustness_component_summaries": [
                {
                    "id": "ABLATION_CORE",
                    "kind": "ABLATION",
                    "value": 0.9,
                    "source_module": "M22",
                    "preregistration_ref": "ROB-AB-002",
                    "derivation_ref": "ABLATION-RULE-V1",
                },
                {
                    "id": "PARAMETERS",
                    "kind": "PARAMETER_PERTURBATION",
                    "value": 0.72,
                    "source_module": "EXTERNAL",
                    "preregistration_ref": "ROB-P-001",
                    "derivation_ref": "PARAM-RULE-V1",
                },
            ]
        }
        result = m25_robustness(context(raw, canonical))
        output = result.canonical_updates["robustness_index"]

        expected = 100.0 * (0.8 * 0.9 * 0.72) ** (1 / 3)
        self.assertAlmostEqual(output["irc"], expected)
        self.assertAlmostEqual(output["r_min"], 0.72)

    def test_null_model_rarity_is_always_excluded(self):
        canonical = {
            "null_models": {
                "runs": [
                    {"structural_frequency": 0.001}
                ]
            },
            "time_sensitivity": {
                "preregistration_ref": "TS-004",
                "robustness_component": 1.0,
            },
        }
        result = m25_robustness(context(canonical=canonical))
        output = result.canonical_updates["robustness_index"]

        self.assertEqual(
            output["null_model_state"],
            "AVAILABLE_EXCLUDED_FROM_IRC",
        )
        self.assertFalse(output["null_model_rarity_used_as_robustness"])
        self.assertAlmostEqual(output["irc"], 100.0)

    def test_m24_cannot_be_smuggled_in_as_component(self):
        raw = {
            "robustness_component_summaries": [
                {
                    "id": "BAD_NULL",
                    "kind": "PARAMETER_PERTURBATION",
                    "value": 0.99,
                    "source_module": "M24",
                    "preregistration_ref": "BAD",
                    "derivation_ref": "BAD",
                }
            ]
        }
        with self.assertRaises(ValueError):
            m25_robustness(context(raw=raw))

    def test_birth_time_cannot_override_m23(self):
        canonical = {
            "time_sensitivity": {
                "preregistration_ref": "TS-005",
                "robustness_component": 0.8,
            }
        }
        raw = {
            "robustness_component_summaries": [
                {
                    "id": "BIRTH_TIME_2",
                    "kind": "BIRTH_TIME",
                    "value": 1.0,
                    "source_module": "EXTERNAL",
                    "preregistration_ref": "TS-ALT",
                    "derivation_ref": "ALT",
                }
            ]
        }
        with self.assertRaises(ValueError):
            m25_robustness(context(raw, canonical))

    def test_no_components_is_not_evaluable(self):
        result = m25_robustness(context())
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)


if __name__ == "__main__":
    unittest.main()
