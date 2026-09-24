import unittest

from almas_tfa.core import (
    diagnostic_discrimination,
    idd_band,
    pillar_score,
    robustness_component,
    robustness_index,
    score_model,
    supported_gate,
)


class TestPillars(unittest.TestCase):
    def test_one_root_ceiling(self):
        self.assertAlmostEqual(pillar_score([1.0]), 54.54545454545455)

    def test_top_three_only(self):
        self.assertAlmostEqual(pillar_score([1.0, 1.0, 1.0, 0.2]), 100.0)


class TestIEM(unittest.TestCase):
    def test_models_are_not_probability_simplex(self):
        pillars = {
            "PA": 95,
            "PR": 95,
            "PE": 95,
            "PX": 95,
            "PK": 90,
            "PT": 90,
            "PS": 85,
            "PU": 80,
        }
        af = score_model("AF", pillars)
        ag = score_model("AG", pillars)
        self.assertGreater(af.iem_final + ag.iem_final, 100)

    def test_ice_applied_once(self):
        pillars = {"PA": 100, "PR": 100, "PE": 100, "PX": 100}
        score = score_model("AF", pillars, ice=100)
        self.assertAlmostEqual(score.iem_pre, 100.0)
        self.assertAlmostEqual(score.iem_final, 70.0)

    def test_missing_essential_is_not_zero_evidence(self):
        score = score_model("AF", {"PA": 90, "PR": None})
        self.assertFalse(score.essential_evaluable)
        self.assertEqual(score.iem_final, 0.0)

    def test_supported_gate(self):
        pillars = {
            "PA": 90,
            "PE": 90,
            "PR": 90,
            "PX": 90,
            "PK": 80,
            "PT": 85,
            "PS": 75,
        }
        score = score_model("AG", pillars)
        self.assertTrue(supported_gate(score, icc=90, irc=85, r_min=0.8))
        self.assertFalse(supported_gate(score, icc=79, irc=85, r_min=0.8))


class TestIDD(unittest.TestCase):
    def test_identical_is_zero(self):
        self.assertAlmostEqual(
            diagnostic_discrimination(
                {"r1": 2, "r2": 1},
                {"r1": 2, "r2": 1},
            ),
            0.0,
        )

    def test_disjoint_is_100(self):
        self.assertAlmostEqual(
            diagnostic_discrimination({"r1": 1}, {"r2": 1}),
            100.0,
        )
        self.assertEqual(idd_band(100.0), "VERY_MARKED")

    def test_empty_not_evaluable(self):
        self.assertIsNone(diagnostic_discrimination({}, {"r1": 1}))


class TestRobustness(unittest.TestCase):
    def test_component_range(self):
        self.assertAlmostEqual(robustness_component(0, 1), 1.0)

    def test_index(self):
        irc, rmin = robustness_index([1.0, 0.81, 0.64])
        self.assertGreaterEqual(irc, 0)
        self.assertLessEqual(irc, 100)
        self.assertEqual(rmin, 0.64)


if __name__ == "__main__":
    unittest.main()
