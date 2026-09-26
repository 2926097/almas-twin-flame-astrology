from __future__ import annotations

from copy import deepcopy
import unittest
from unittest.mock import patch

from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.null_generation import (
    generate_within_year_null_runs,
    load_null_generation_policy,
)
from almas_tfa.null_model_handlers import make_m24_null_models


def raw_input():
    return {
        "mode": "FULL",
        "subjects": [
            {
                "id": "A",
                "birth_date": "2000-03-20",
                "birth_time": "12:00",
                "timezone": "UTC",
                "latitude": 40.0,
                "longitude": -1.0,
                "time_reliability": "A",
            },
            {
                "id": "B",
                "birth_date": "2001-05-23",
                "birth_time": "08:15",
                "timezone": "UTC",
                "latitude": 18.0,
                "longitude": -70.0,
                "time_reliability": "A",
            },
        ],
    }


def snapshot(core_count, max_iem, px):
    return {
        "state": "EVALUABLE",
        "iem_pre": {
            "AF": max_iem - 4.0,
            "KA": max_iem - 3.0,
            "AG": max_iem,
            "LG": max_iem - 1.0,
        },
        "core_root_keys": [f"R{i}:KEY" for i in range(core_count)],
        "core_root_count": core_count,
        "pillars": {
            "PA": 0.7,
            "PK": 0.6,
            "PE": 0.7,
            "PR": 0.7,
            "PX": px,
            "PT": 0.6,
            "PS": 0.5,
            "PU": None,
        },
        "pillar_attribution": {
            "structural_absence_is_zero": True,
            "root_attributions": [],
        },
    }


class TestNullGeneration(unittest.TestCase):
    def test_policy_is_frozen_and_forbids_metaphysical_probability(self):
        policy = load_null_generation_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_NULL_WITHIN_YEAR_V1",
        )
        self.assertEqual(policy["null_model"], "WITHIN_YEAR")
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertFalse(
            policy["principles"]["metaphysical_probability"]
        )
        self.assertFalse(
            policy["principles"]["null_rarity_used_as_irc"]
        )
        self.assertTrue(
            policy["principles"]["combined_p_value_forbidden"]
        )

    def test_generator_is_deterministic_and_preserves_birth_year(self):
        policy = deepcopy(load_null_generation_policy())
        policy["generator"]["samples_per_subject"] = 2

        side_effect = [
            snapshot(7, 82.0, 0.80),
            snapshot(5, 70.0, 0.55),
            snapshot(6, 76.0, 0.65),
            snapshot(4, 68.0, 0.45),
            snapshot(7, 80.0, 0.75),
        ]

        with patch(
            "almas_tfa.null_generation.structural_recalculation_snapshot",
            side_effect=side_effect,
        ):
            result = generate_within_year_null_runs(
                raw_input(),
                astrology_backend=object(),
                davison_backend=object(),
                policy=policy,
            )

        self.assertEqual(result["state"], "EVALUABLE")
        self.assertEqual(result["sample_count"], 4)
        self.assertEqual(len(result["run_specs"]), 3)
        self.assertEqual(
            {run["statistic_id"] for run in result["run_specs"]},
            {"CORE_ROOT_COUNT", "MAX_IEM_PRE", "PX_PILLAR_SCORE"},
        )
        self.assertIsNone(result["combined_p_value"])
        self.assertEqual(
            result["combined_p_value_state"],
            "FORBIDDEN",
        )
        self.assertFalse(result["external_population_claim"])

        manifest = result["sample_manifest"]
        years_by_subject = {"A": "2000", "B": "2001"}
        for sample in manifest:
            subject_id = sample["perturbed_subject_id"]
            self.assertTrue(
                sample["replacement_birth_date"].startswith(
                    years_by_subject[subject_id]
                )
            )

    def test_generator_does_not_use_pair_shuffle_without_external_pool(self):
        policy = load_null_generation_policy()
        self.assertTrue(
            policy["principles"]["pair_shuffle_requires_external_pool"]
        )
        self.assertTrue(
            policy["principles"]["matched_age_requires_external_pool"]
        )
        self.assertTrue(
            policy["principles"]["matched_age_clock_requires_external_pool"]
        )

    def test_m24_auto_marks_sampling_as_generated(self):
        generated = {
            "state": "EVALUABLE",
            "policy_id": "ALMAS_NULL_WITHIN_YEAR_V1",
            "policy_status": "FROZEN_EXPERIMENTAL_BASELINE",
            "epistemic_class": "E_PROJECT_POLICY",
            "sample_count": 4,
            "samples_per_subject": 2,
            "sample_manifest": [
                {
                    "perturbed_subject_id": "A",
                    "replacement_birth_date": "2000-01-10",
                    "core_root_count": 5,
                    "max_iem_pre": 72.0,
                    "px_pillar_score": 50.0,
                }
            ],
            "run_specs": [
                {
                    "id": "AUTO_WITHIN_YEAR_CORE_ROOT_COUNT",
                    "preregistration_ref": "ALMAS_NULL_WITHIN_YEAR_V1",
                    "null_model": "WITHIN_YEAR",
                    "feature_set_ref": "ALMAS_Q1_Q2_STRUCTURAL_FEATURES_V1",
                    "orb_policy_ref": "RAW_INPUT_DECLARED_ORBS_UNCHANGED",
                    "event_set_ref": "NOT_APPLICABLE_STRUCTURAL_NULL",
                    "generator_ref": "ALMAS_NULL_WITHIN_YEAR_V1:GEN",
                    "statistic_id": "CORE_ROOT_COUNT",
                    "observed_value": 7.0,
                    "tail": "GREATER_OR_EQUAL",
                    "confidence_level": 0.95,
                    "null_samples": [4.0, 5.0, 8.0, 6.0],
                }
            ],
        }

        handler = make_m24_null_models(object(), object())
        with patch(
            "almas_tfa.null_model_handlers.generate_within_year_null_runs",
            return_value=generated,
        ):
            result = handler(
                ModuleContext(
                    module_id="M24",
                    module_name="null_models",
                    mode="FULL",
                    raw_input=raw_input(),
                    canonical_snapshot={},
                    prior_results={},
                )
            )

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["null_models"]
        self.assertTrue(output["sampling_generated_by_m24"])
        self.assertFalse(output["metaphysical_probability"])
        self.assertEqual(
            output["generator_policy_id"],
            "ALMAS_NULL_WITHIN_YEAR_V1",
        )
        self.assertEqual(output["combined_p_value_state"], "FORBIDDEN")
        self.assertTrue(
            output["runs"][0]["sampling_generated_by_m24"]
        )
        self.assertEqual(
            output["runs"][0]["evaluation_source"],
            "NULL_SAMPLES",
        )

    def test_explicit_legacy_runs_have_priority(self):
        raw = raw_input()
        raw["null_model_runs"] = [
            {
                "id": "EXTERNAL_PAIR",
                "preregistration_ref": "EXT-1",
                "null_model": "PAIR_SHUFFLE",
                "feature_set_ref": "F",
                "orb_policy_ref": "O",
                "event_set_ref": "E",
                "generator_ref": "EXTERNAL_POOL",
                "statistic_id": "CORE_ROOT_COUNT",
                "observed_value": 7.0,
                "tail": "GREATER_OR_EQUAL",
                "n": 100,
                "extreme_count": 5,
            }
        ]

        handler = make_m24_null_models(object(), object())
        with patch(
            "almas_tfa.null_model_handlers.generate_within_year_null_runs"
        ) as generator:
            result = handler(
                ModuleContext(
                    module_id="M24",
                    module_name="null_models",
                    mode="FULL",
                    raw_input=raw,
                    canonical_snapshot={},
                    prior_results={},
                )
            )

        generator.assert_not_called()
        output = result.canonical_updates["null_models"]
        self.assertFalse(output["sampling_generated_by_m24"])
        self.assertEqual(
            output["runs"][0]["null_model"],
            "PAIR_SHUFFLE",
        )


if __name__ == "__main__":
    unittest.main()
