import unittest

from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.null_model_handlers import m24_null_models, wilson_interval


def context(raw):
    return ModuleContext(
        module_id="M24",
        module_name="null_models",
        mode="FULL",
        raw_input=raw,
        canonical_snapshot={},
        prior_results={},
    )


def base_run(run_id="NM1"):
    return {
        "id": run_id,
        "preregistration_ref": "PREREG-001",
        "null_model": "PAIR_SHUFFLE",
        "feature_set_ref": "FEATURES-V1",
        "orb_policy_ref": "ORBS-V1",
        "event_set_ref": "EVENTS-V1",
        "generator_ref": "GENERATOR-V1",
        "statistic_id": "ROOT_COUNT",
        "observed_value": 4.0,
        "tail": "GREATER_OR_EQUAL",
        "confidence_level": 0.95,
    }


class TestNullModels(unittest.TestCase):
    def test_samples_produce_structural_frequency(self):
        run = base_run()
        run["null_samples"] = [1, 2, 3, 4, 5, 0, 4, 2, 1, 3]

        result = m24_null_models(
            context({"null_model_runs": [run]})
        )

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["null_models"]
        self.assertEqual(output["run_count"], 1)
        evaluated = output["runs"][0]

        self.assertEqual(evaluated["n"], 10)
        self.assertEqual(evaluated["extreme_count"], 3)
        self.assertAlmostEqual(evaluated["structural_frequency"], 0.3)
        self.assertFalse(evaluated["sampling_generated_by_m24"])
        self.assertFalse(output["metaphysical_probability"])

    def test_multiple_null_families_remain_separate(self):
        a = base_run("PAIR")
        a["n"] = 1000
        a["extreme_count"] = 25

        b = base_run("WITHIN")
        b["null_model"] = "WITHIN_YEAR"
        b["n"] = 500
        b["extreme_count"] = 50

        result = m24_null_models(
            context({"null_model_runs": [b, a]})
        )
        output = result.canonical_updates["null_models"]

        self.assertEqual(output["run_count"], 2)
        self.assertEqual(
            [item["id"] for item in output["runs"]],
            ["PAIR", "WITHIN"],
        )
        self.assertAlmostEqual(
            output["runs"][0]["structural_frequency"],
            0.025,
        )
        self.assertAlmostEqual(
            output["runs"][1]["structural_frequency"],
            0.1,
        )

    def test_precomputed_counts_have_wilson_interval(self):
        run = base_run()
        run["n"] = 100
        run["extreme_count"] = 5

        result = m24_null_models(
            context({"null_model_runs": [run]})
        )
        evaluated = result.canonical_updates["null_models"]["runs"][0]

        self.assertLessEqual(
            evaluated["wilson_interval"]["lower"],
            evaluated["structural_frequency"],
        )
        self.assertGreaterEqual(
            evaluated["wilson_interval"]["upper"],
            evaluated["structural_frequency"],
        )

    def test_wilson_interval_is_bounded(self):
        lower, upper = wilson_interval(0, 100, 0.95)
        self.assertGreaterEqual(lower, 0.0)
        self.assertLessEqual(upper, 1.0)
        self.assertLess(lower, upper)

    def test_unfrozen_orb_policy_is_rejected(self):
        run = base_run()
        del run["orb_policy_ref"]
        run["n"] = 100
        run["extreme_count"] = 10

        with self.assertRaises(ValueError):
            m24_null_models(
                context({"null_model_runs": [run]})
            )

    def test_counts_must_match_samples_and_tail(self):
        run = base_run()
        run["null_samples"] = [4, 5, 1]
        run["extreme_count"] = 1

        with self.assertRaises(ValueError):
            m24_null_models(
                context({"null_model_runs": [run]})
            )

    def test_duplicate_run_ids_are_rejected(self):
        a = base_run("DUP")
        a["n"] = 100
        a["extreme_count"] = 10
        b = dict(a)

        with self.assertRaises(ValueError):
            m24_null_models(
                context({"null_model_runs": [a, b]})
            )

    def test_missing_runs_is_not_evaluable(self):
        result = m24_null_models(context({}))
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)


if __name__ == "__main__":
    unittest.main()
