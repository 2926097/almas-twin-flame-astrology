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
        self.assertEqual(result["public_version"], "1.3.1")
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


if __name__ == "__main__":
    unittest.main()
