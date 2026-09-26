from __future__ import annotations

import unittest

from almas_tfa.analysis_profiles import (
    classify_trace_for_profile,
    load_analysis_profile_policy,
    resolve_analysis_profile,
)


class AnalysisProfileTests(unittest.TestCase):
    def test_policy_contains_three_frozen_profiles(self):
        policy = load_analysis_profile_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_ANALYSIS_PROFILES_V1",
        )
        self.assertEqual(
            set(policy["profiles"]),
            {
                "FULL_MULTIDISCIPLINARY",
                "FULL_ASTROLOGY",
                "STRUCTURAL_ASTROLOGY",
            },
        )

    def test_default_is_multidisciplinary(self):
        self.assertEqual(
            resolve_analysis_profile(None),
            "FULL_MULTIDISCIPLINARY",
        )

    def test_unknown_profile_fails_closed(self):
        with self.assertRaises(ValueError):
            resolve_analysis_profile("PRIVATE_CASE_TUNED")

    def test_full_astrology_separates_optional_not_evaluable(self):
        trace = {
            "not_evaluable_modules": ["M13", "M23", "M28", "M03"],
            "skipped_modules": ["M29"],
        }
        result = classify_trace_for_profile(trace, "FULL_ASTROLOGY")
        self.assertEqual(
            result["optional_not_evaluable_modules"],
            ["M13", "M23", "M28"],
        )
        self.assertEqual(
            result["required_not_evaluable_modules"],
            ["M03"],
        )
        self.assertEqual(
            result["optional_skipped_modules"],
            ["M29"],
        )

    def test_multidisciplinary_keeps_not_evaluable_required(self):
        trace = {
            "not_evaluable_modules": ["M28"],
            "skipped_modules": [],
        }
        result = classify_trace_for_profile(
            trace,
            "FULL_MULTIDISCIPLINARY",
        )
        self.assertEqual(
            result["required_not_evaluable_modules"],
            ["M28"],
        )
        self.assertEqual(result["optional_not_evaluable_modules"], [])


if __name__ == "__main__":
    unittest.main()
