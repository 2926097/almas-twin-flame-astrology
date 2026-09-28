from __future__ import annotations

import unittest

from almas_tfa.root_strengths import (
    derive_root_strength,
    evidence_strength,
    load_root_strength_policy,
)


def item(
    evidence_id: str,
    exactness: float,
    *,
    family: str = "SYN",
    core: bool = True,
    support: bool = False,
    point_a: str = "SUN",
    point_b: str = "MOON",
    aspect: str = "CONJUNCTION",
):
    return {
        "evidence_id": evidence_id,
        "exactness": exactness,
        "technique_family": family,
        "dependency_family": family,
        "core_eligible": core,
        "support_only": support,
        "contact": {
            "point_a": point_a,
            "point_b": point_b,
            "aspect": aspect,
        },
    }


class RootStrengthTests(unittest.TestCase):
    def test_policy_is_frozen_neutral_baseline(self):
        policy = load_root_strength_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_ROOT_STRENGTH_BASELINE_V1",
        )
        self.assertEqual(
            policy["status"],
            "FROZEN_NEUTRAL_BASELINE",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])

    def test_neutral_baseline_preserves_exactness(self):
        self.assertAlmostEqual(
            evidence_strength(item("E1", 0.75)),
            0.75,
        )

    def test_timed_point_is_not_double_penalized(self):
        self.assertAlmostEqual(
            evidence_strength(
                item(
                    "E1",
                    0.61,
                    point_a="ASC",
                    point_b="SUN",
                )
            ),
            0.61,
        )

    def test_core_evidence_controls_root_even_if_support_is_stronger(self):
        result = derive_root_strength(
            [
                item("CORE", 0.62),
                item(
                    "SUPPORT",
                    0.99,
                    family="SECONDARY",
                    core=False,
                    support=True,
                ),
            ]
        )
        self.assertEqual(result["strength_state"], "CALCULATED_CORE")
        self.assertAlmostEqual(result["strength"], 0.62)
        self.assertEqual(result["dominant_evidence_id"], "CORE")

    def test_support_only_never_becomes_core(self):
        result = derive_root_strength(
            [
                item(
                    "SUPPORT",
                    0.95,
                    family="DRACONIC_DD",
                    core=False,
                    support=True,
                )
            ]
        )
        self.assertEqual(
            result["strength_state"],
            "CALCULATED_SUPPORT_ONLY",
        )
        self.assertAlmostEqual(result["strength"], 0.95)

    def test_invalid_exactness_fails_closed(self):
        with self.assertRaises(ValueError):
            evidence_strength(item("E1", 1.1))


if __name__ == "__main__":
    unittest.main()
