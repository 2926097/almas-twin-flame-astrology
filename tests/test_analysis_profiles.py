from __future__ import annotations

import unittest

from almas_tfa.analysis_profiles import (
    load_analysis_profile_policy,
    profile_trace_assessment,
    resolve_analysis_profile,
)


class AnalysisProfileTests(unittest.TestCase):
    def test_default_preserves_multidisciplinary_strictness(self):
        profile = resolve_analysis_profile(None)
        self.assertEqual(
            profile["profile_id"],
            "FULL_MULTIDISCIPLINARY",
        )
        self.assertIn("M28", profile["required_modules"])
        self.assertIn("M29", profile["required_modules"])

    def test_full_astrology_excludes_doctrine_temporal_and_reality_layers(self):
        profile = resolve_analysis_profile("FULL_ASTROLOGY")
        self.assertEqual(profile["analysis_mode"], "FULL")
        self.assertIn("M23", profile["required_modules"])
        self.assertIn("M25", profile["required_modules"])
        self.assertIn("M20", profile["optional_modules"])
        self.assertIn("M28", profile["excluded_modules"])
        self.assertIn("M29", profile["excluded_modules"])

    def test_profile_assessment_ignores_excluded_not_evaluable(self):
        profile = resolve_analysis_profile("FULL_ASTROLOGY")
        trace = {
            "completed_modules": profile["required_modules"],
            "failed_modules": [],
            "not_evaluable_modules": ["M20", "M28", "M29"],
            "skipped_modules": [],
            "not_applicable_modules": [],
        }
        result = profile_trace_assessment(trace, profile)
        self.assertEqual(result["required_not_evaluable"], [])
        self.assertEqual(
            set(result["ignored_not_evaluable"]),
            {"M20", "M28", "M29"},
        )

    def test_required_not_evaluable_still_degrades(self):
        profile = resolve_analysis_profile("FULL_ASTROLOGY")
        trace = {
            "completed_modules": [],
            "failed_modules": [],
            "not_evaluable_modules": ["M23"],
            "skipped_modules": [],
            "not_applicable_modules": [],
        }
        result = profile_trace_assessment(trace, profile)
        self.assertIn("M23", result["required_not_evaluable"])

    def test_policy_states_ready_is_not_metaphysical_truth(self):
        policy = load_analysis_profile_policy()
        self.assertTrue(
            policy["principles"][
                "ready_means_profile_complete_not_metaphysically_proven"
            ]
        )


if __name__ == "__main__":
    unittest.main()
