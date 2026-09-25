import math
import unittest

from almas_tfa.handlers import m25_robustness
from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.robustness_handlers import (
    m23_time_sensitivity,
    m24_null_models,
    wilson_interval,
)


def ctx(module_id, raw):
    return ModuleContext(
        module_id=module_id,
        module_name=module_id,
        mode="FULL",
        raw_input=raw,
        canonical_snapshot={},
        prior_results={},
    )


class TestTimeSensitivity(unittest.TestCase):
    def test_m23_applies_normative_component_formula(self):
        result = m23_time_sensitivity(
            ctx(
                "M23",
                {
                    "time_sensitivity_summary": {
                        "preregistration_ref": "TS-001",
                        "subject_scope": "BOTH",
                        "perturbation_rule": "synthetic ±30m",
                        "metric": "IEM_BAND",
                        "delta90": 10.0,
                        "preserved_fraction": 0.81,
                        "perturbation_count": 100,
                    }
                },
            )
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        component = result.canonical_updates["time_sensitivity"][
            "robustness_component"
        ]
        self.assertAlmostEqual(component, math.exp(-0.5) * 0.9)

    def test_m23_does_not_generate_perturbations(self):
        result = m23_time_sensitivity(
            ctx(
                "M23",
                {
                    "time_sensitivity_summary": {
                        "preregistration_ref": "TS-001",
                        "delta90": 0,
                        "preserved_fraction": 1,
                    }
                },
            )
        )
        self.assertFalse(
            result.canonical_updates["time_sensitivity"][
                "perturbations_generated_by_m23"
            ]
        )


class TestRobustnessAggregation(unittest.TestCase):
    def test_m25_can_consume_m23_component_without_null_rarity(self):
        time_result = m23_time_sensitivity(
            ctx(
                "M23",
                {
                    "time_sensitivity_summary": {
                        "preregistration_ref": "TS-002",
                        "delta90": 5.0,
                        "preserved_fraction": 1.0,
                    }
                },
            )
        )
        context = ModuleContext(
            module_id="M25",
            module_name="robustness",
            mode="FULL",
            raw_input={},
            canonical_snapshot={
                "time_sensitivity": time_result.canonical_updates[
                    "time_sensitivity"
                ],
                "null_models": {
                    "runs": [
                        {"frequency": 0.001}
                    ]
                },
            },
            prior_results={},
        )
        result = m25_robustness(context)
        output = result.canonical_updates["robustness_index"]
        self.assertIn("BIRTH_TIME", output["component_map"])
        self.assertFalse(output["null_model_rarity_used_as_robustness"])


class TestNullModels(unittest.TestCase):
    def test_wilson_interval(self):
        low, high = wilson_interval(50, 100, 1.96)
        self.assertLess(low, 0.5)
        self.assertGreater(high, 0.5)

    def test_m24_reports_frequency_not_metaphysical_probability(self):
        result = m24_null_models(
            ctx(
                "M24",
                {
                    "null_model_runs": [
                        {
                            "run_id": "N1",
                            "null_model": "PAIR_SHUFFLE",
                            "preregistration_ref": "NULL-001",
                            "frozen_before_inspection": True,
                            "trials": 1000,
                            "hits": 25,
                            "wilson_z": 1.96,
                            "observed_statistic": 87.2,
                        }
                    ]
                },
            )
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["null_models"]
        self.assertFalse(output["metaphysical_probability"])
        self.assertFalse(output["sampling_generated_by_m24"])
        self.assertAlmostEqual(output["runs"][0]["frequency"], 0.025)
        self.assertIsNotNone(output["runs"][0]["wilson_interval"])

    def test_confirmatory_null_must_be_frozen(self):
        with self.assertRaises(ValueError):
            m24_null_models(
                ctx(
                    "M24",
                    {
                        "null_model_runs": [
                            {
                                "null_model": "PAIR_SHUFFLE",
                                "preregistration_ref": "NULL-001",
                                "frozen_before_inspection": False,
                                "trials": 100,
                                "hits": 10,
                            }
                        ]
                    },
                )
            )


if __name__ == "__main__":
    unittest.main()
