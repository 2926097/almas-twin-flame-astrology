import math
import unittest

from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.time_sensitivity_handlers import m23_time_sensitivity


def context(raw):
    return ModuleContext(
        module_id="M23",
        module_name="time_sensitivity",
        mode="FULL",
        raw_input=raw,
        canonical_snapshot={},
        prior_results={},
    )


class TestTimeSensitivity(unittest.TestCase):
    def test_computes_normative_component_from_preregistered_summary(self):
        result = m23_time_sensitivity(
            context(
                {
                    "time_sensitivity_summary": {
                        "preregistration_ref": "TS-001",
                        "subject_scope": "BOTH",
                        "perturbation_rule": {
                            "window_minutes": 30,
                            "step_minutes": 5
                        },
                        "metric": "IEM_FINAL",
                        "delta90": 10.0,
                        "preserved_fraction": 0.81,
                        "perturbation_count": 25
                    }
                }
            )
        )

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["time_sensitivity"]
        expected = math.exp(-10.0 / 20.0) * math.sqrt(0.81)

        self.assertAlmostEqual(output["robustness_component"], expected)
        self.assertEqual(output["preregistration_ref"], "TS-001")
        self.assertFalse(output["perturbations_generated_by_m23"])

    def test_missing_summary_is_not_evaluable(self):
        result = m23_time_sensitivity(context({}))
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)

    def test_missing_delta90_is_rejected(self):
        with self.assertRaises(ValueError):
            m23_time_sensitivity(
                context(
                    {
                        "time_sensitivity_summary": {
                            "preregistration_ref": "TS-002",
                            "preserved_fraction": 1.0
                        }
                    }
                )
            )

    def test_invalid_preserved_fraction_is_rejected(self):
        with self.assertRaises(ValueError):
            m23_time_sensitivity(
                context(
                    {
                        "time_sensitivity_summary": {
                            "preregistration_ref": "TS-003",
                            "delta90": 5.0,
                            "preserved_fraction": 1.2
                        }
                    }
                )
            )

    def test_samples_do_not_replace_preregistered_delta90(self):
        with self.assertRaises(ValueError):
            m23_time_sensitivity(
                context(
                    {
                        "time_sensitivity_summary": {
                            "preregistration_ref": "TS-004",
                            "preserved_fraction": 1.0,
                            "samples": [1, 2, 3]
                        }
                    }
                )
            )


if __name__ == "__main__":
    unittest.main()
