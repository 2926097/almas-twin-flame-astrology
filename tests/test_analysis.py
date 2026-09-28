import unittest

from almas_tfa.analysis import analyze_precomputed


class TestAnalyzePrecomputed(unittest.TestCase):
    def test_basic_payload(self):
        result = analyze_precomputed(
            {
                "pillars": {
                    "PA": 90,
                    "PK": 80,
                    "PE": 85,
                    "PR": 92,
                    "PX": 88,
                    "PT": 82,
                    "PS": 70,
                    "PU": 50,
                },
                "ice_by_model": {
                    "AF": 0,
                    "KA": 5,
                    "AG": 0,
                    "LG": 10,
                },
                "icc": 90,
                "irc": 85,
                "r_min": 0.8,
                "attributions": {
                    "AG": {"r1": 1, "r2": 1},
                    "LG": {"r1": 1, "r3": 1},
                },
            }
        )
        self.assertEqual(result["public_version"], "1.21.0")
        self.assertEqual(set(result["models"]), {"AF", "KA", "AG", "LG"})
        self.assertIn("AG_vs_LG", result["pairwise_idd"])
        self.assertIsInstance(result["models"]["AG"]["iem_final"], float)

    def test_gate_without_coverage_is_none(self):
        result = analyze_precomputed(
            {"pillars": {"PA": 90, "PR": 90, "PE": 90, "PX": 90}}
        )
        self.assertIsNone(result["models"]["AF"]["supported_gate"])

    def test_missing_pillars_yield_not_evaluable_models(self):
        result = analyze_precomputed({"pillars": {"PA": 90}})
        self.assertFalse(result["models"]["AF"]["essential_evaluable"])

    def test_missing_ice_never_becomes_zero_or_opens_supported_gate(self):
        result = analyze_precomputed(
            {
                "pillars": {
                    "PA": 90,
                    "PK": 90,
                    "PE": 90,
                    "PR": 90,
                    "PX": 90,
                    "PT": 90,
                    "PS": 90,
                    "PU": 90,
                },
                "icc": 100,
                "irc": 100,
                "r_min": 1.0,
            }
        )
        for model in ("AF", "KA", "AG", "LG"):
            self.assertEqual(result["models"][model]["ice_state"], "NOT_EVALUABLE")
            self.assertIsNone(result["models"][model]["ice"])
            self.assertIsNone(result["models"][model]["iem_final"])
            self.assertIsNone(result["models"][model]["supported_gate"])

    def test_partial_ice_map_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze_precomputed(
                {
                    "pillars": {"PA": 90, "PR": 90},
                    "ice_by_model": {"AF": 0, "KA": 0, "AG": 0},
                }
            )

    def test_ice_boundaries_zero_and_hundred_are_valid(self):
        result = analyze_precomputed(
            {
                "pillars": {
                    "PA": 90,
                    "PK": 90,
                    "PE": 90,
                    "PR": 90,
                    "PX": 90,
                    "PT": 90,
                    "PS": 90,
                    "PU": 90,
                },
                "ice_by_model": {"AF": 0, "KA": 100, "AG": 0, "LG": 100},
            }
        )
        self.assertEqual(result["models"]["AF"]["ice"], 0.0)
        self.assertEqual(result["models"]["KA"]["ice"], 100.0)
        self.assertEqual(result["models"]["LG"]["ice"], 100.0)

    def test_ice_outside_boundaries_is_rejected(self):
        for invalid in (-0.0001, 100.0001):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    analyze_precomputed(
                        {
                            "pillars": {"PA": 90, "PR": 90},
                            "ice_by_model": {
                                "AF": invalid,
                                "KA": 0,
                                "AG": 0,
                                "LG": 0,
                            },
                        }
                    )


if __name__ == "__main__":
    unittest.main()
