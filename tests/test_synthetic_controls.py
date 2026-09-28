from __future__ import annotations

import unittest

from almas_tfa.synthetic_controls import (
    derive_recurrence_synthetic_controls,
    load_recurrence_synthetic_controls_policy,
)


def root(
    root_id,
    *,
    family,
    points,
    relations,
    strength=0.8,
):
    return {
        "root_id": root_id,
        "root_key": root_id + ":REAL",
        "point_ids": list(points),
        "relation_ids": list(relations),
        "strength": strength,
        "strength_state": "CALCULATED_CORE",
        "core_eligible": True,
        "independent_family_count": 1,
        "dependency_families": [family],
        "evidence_strengths": [
            {
                "evidence_id": root_id + ":" + family,
                "strength": strength,
                "core_eligible": True,
                "support_only": False,
                "dependency_family": family,
                "technique_family": family,
            }
        ],
    }


def roots_fixture():
    signatures = [
        (["SUN", "PLUTO"], ["SQUARE"]),
        (["SUN", "URANUS"], ["OPPOSITION"]),
        (["SATURN", "MOON"], ["CONJUNCTION"]),
        (["AXIS_NODES", "VENUS"], ["TRINE"]),
        (["VENUS", "MARS"], ["CONJUNCTION"]),
        (["MERCURY", "MOON"], ["SEXTILE"]),
        (["NEPTUNE", "SUN"], ["TRINE"]),
        (["PLUTO", "MOON"], ["SQUARE"]),
        (["SUN", "MOON"], ["OPPOSITION"]),
        (["VENUS", "JUPITER"], ["TRINE"]),
        (["AXIS_MERIDIAN", "SUN"], ["CONJUNCTION"]),
        (["AXIS_MERIDIAN", "AXIS_NODES"], ["CONJUNCTION"]),
    ]
    families = [
        "SYN",
        "NATAL_DRACONIC",
        "DECLINATION",
        "ANTISCIA",
        "SYN",
        "RELCHART",
        "NATAL_DRACONIC",
        "DECLINATION",
        "ANTISCIA",
        "RELCHART",
        "SYN",
        "NATAL_DRACONIC",
    ]
    return [
        root(
            f"R{index:02d}",
            family=families[index],
            points=signatures[index][0],
            relations=signatures[index][1],
            strength=0.70 + index * 0.02,
        )
        for index in range(len(signatures))
    ]


class SyntheticRecurrenceControlsTests(unittest.TestCase):
    def test_policy_is_diagnostic_and_deterministic(self):
        policy = load_recurrence_synthetic_controls_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_RECURRENCE_SYNTHETIC_CONTROLS_V1",
        )
        self.assertTrue(policy["principles"]["diagnostic_only"])
        self.assertTrue(policy["principles"]["deterministic_no_rng"])
        self.assertTrue(
            policy["principles"]["external_nulls_required_before_weighting"]
        )
        self.assertFalse(
            policy["principles"]["metaphysical_probability"]
        )

    def test_controls_are_deterministic(self):
        roots = roots_fixture()
        first = derive_recurrence_synthetic_controls(roots)
        second = derive_recurrence_synthetic_controls(roots)
        self.assertEqual(first, second)
        self.assertEqual(first["state"], "DIAGNOSTIC_ONLY")
        self.assertTrue(first["deterministic"])
        self.assertFalse(first["rng_used"])

    def test_two_control_families_are_generated(self):
        result = derive_recurrence_synthetic_controls(roots_fixture())
        self.assertEqual(
            set(result["by_control_family"]),
            {
                "SEMANTIC_SIGNATURE_ROTATION",
                "DECOUPLED_POINT_RELATION_ROTATION",
            },
        )
        self.assertEqual(
            result["control_count"],
            2 * result["controls_per_family"],
        )
        self.assertGreater(result["control_count"], 0)

    def test_diagnostics_never_enter_scoring(self):
        result = derive_recurrence_synthetic_controls(roots_fixture())
        for field in (
            "used_for_weighting",
            "used_in_px_score",
            "used_in_ps_score",
            "used_in_iem",
            "used_in_idd",
            "used_in_irc",
            "used_in_ontology",
            "metaphysical_probability",
            "population_probability_claim",
            "p_value_claim",
        ):
            self.assertFalse(result[field])

    def test_observed_and_controls_publish_px_ps_and_counts(self):
        result = derive_recurrence_synthetic_controls(roots_fixture())
        observed = result["observed"]
        self.assertIn("px_score", observed)
        self.assertIn("ps_score", observed)
        self.assertIn("primary_recurrent_motif_count", observed)
        self.assertIn("mission_recurrent_motif_count", observed)
        for control in result["control_manifest"]:
            self.assertIn("px_score", control)
            self.assertIn("ps_score", control)

    def test_finite_control_frequency_is_not_population_probability(self):
        result = derive_recurrence_synthetic_controls(roots_fixture())
        px = result["aggregate"]["PX_SCORE"]
        self.assertEqual(
            px["interpretation_scope"],
            "FINITE_DETERMINISTIC_CONTROL_FAMILY_FREQUENCY",
        )
        self.assertGreaterEqual(px["frequency"], 0.0)
        self.assertLessEqual(px["frequency"], 1.0)
        self.assertFalse(result["population_probability_claim"])

    def test_insufficient_roots_fails_closed(self):
        result = derive_recurrence_synthetic_controls(
            roots_fixture()[:4]
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertFalse(result["used_for_weighting"])
        self.assertFalse(result["metaphysical_probability"])


if __name__ == "__main__":
    unittest.main()
