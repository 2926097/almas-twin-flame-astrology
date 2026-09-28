from __future__ import annotations

from copy import deepcopy
import unittest

from almas_tfa.null_calibration import (
    derive_recurrence_null_calibration,
    load_recurrence_null_calibration_policy,
)


def motif_record(
    motif_id,
    *,
    motif_type="PRIMARY",
    strength=0.8,
    families=None,
):
    families = list(families or ["SYN", "DECLINATION"])
    return {
        "motif_id": motif_id,
        "motif_type": motif_type,
        "root_ids": [motif_id + ":R1", motif_id + ":R2"],
        "root_count": 2,
        "dependency_families": families,
        "independent_family_count": len(families),
        "family_strengths": {
            family: strength - index * 0.05
            for index, family in enumerate(families)
        },
        "exact_multifamily_root_present": False,
        "recurrence_state": "RECURRENT",
        "motif_strength": strength,
        "includes_relchart": "RELCHART" in families,
        "includes_natal_draconic": "NATAL_DRACONIC" in families,
    }


def quality_record(
    motif_id,
    *,
    motif_type="PRIMARY",
    family_class_count=2,
    entropy=0.9,
    effective=1.9,
    dominance=0.55,
    cross_class=True,
    non_draconic=True,
    loo_family=0.5,
    loo_class=0.5,
    includes_draconic=False,
):
    return {
        "motif_id": motif_id,
        "motif_type": motif_type,
        "baseline_recurrent": True,
        "root_count": 2,
        "dependency_families": ["SYN", "DECLINATION"],
        "family_count": 2,
        "family_classes": ["TROPICAL_RELATIONAL", "SYMMETRY"],
        "family_class_count": family_class_count,
        "cross_class_recurrence": cross_class,
        "family_strength_entropy": entropy,
        "effective_family_count": effective,
        "family_dominance_share": dominance,
        "includes_natal_draconic": includes_draconic,
        "non_draconic_recurrence": non_draconic,
        "non_draconic_family_count": 2 if non_draconic else 1,
        "non_draconic_root_count": 2 if non_draconic else 1,
        "leave_one_family_out": {},
        "leave_one_family_out_survival_fraction": loo_family,
        "leave_one_class_out": {},
        "leave_one_class_out_survival_fraction": loo_class,
    }


def snapshot(
    *,
    primary=None,
    mission=None,
    primary_quality=None,
    mission_quality=None,
    px=80.0,
    ps=0.0,
):
    primary = list(primary or [])
    mission = list(mission or [])
    primary_quality = list(primary_quality or [])
    mission_quality = list(mission_quality or [])
    return {
        "pillar_attribution": {
            "semantic_motifs": {
                "recurrent_primary_motifs": primary,
                "recurrent_mission_motifs": mission,
                "px": {
                    "score": px,
                    "recurrent_motif_count": len(primary),
                },
                "ps": {
                    "score": ps,
                    "recurrent_motif_count": len(mission),
                },
            },
            "recurrence_quality": {
                "primary_motifs": primary_quality,
                "mission_motifs": mission_quality,
            },
        }
    }


class RecurrenceNullCalibrationTests(unittest.TestCase):
    def policy(self, minimum=3):
        policy = deepcopy(load_recurrence_null_calibration_policy())
        policy["null_source"]["minimum_samples"] = minimum
        return policy

    def test_policy_is_diagnostic_and_forbids_weighting(self):
        policy = load_recurrence_null_calibration_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_RECURRENCE_NULL_CALIBRATION_V1",
        )
        self.assertTrue(policy["principles"]["diagnostic_only"])
        self.assertTrue(policy["principles"]["combined_p_value_forbidden"])
        self.assertTrue(
            policy["principles"]["external_nulls_required_before_weighting"]
        )

    def test_calibrates_presence_strength_and_quality(self):
        observed_motif = motif_record(
            "IDENTITY_TRANSFORMATION",
            strength=0.9,
            families=["SYN", "NATAL_DRACONIC"],
        )
        observed_quality = quality_record(
            "IDENTITY_TRANSFORMATION",
            entropy=0.95,
            effective=1.95,
            dominance=0.52,
            non_draconic=False,
            includes_draconic=True,
            loo_family=0.0,
            loo_class=0.0,
        )
        baseline = snapshot(
            primary=[observed_motif],
            primary_quality=[observed_quality],
            px=90.0,
        )

        nulls = [
            snapshot(
                primary=[
                    motif_record(
                        "IDENTITY_TRANSFORMATION",
                        strength=0.92,
                    )
                ],
                primary_quality=[
                    quality_record(
                        "IDENTITY_TRANSFORMATION",
                        entropy=0.96,
                        effective=1.96,
                        dominance=0.50,
                        non_draconic=True,
                    )
                ],
                px=92.0,
            ),
            snapshot(
                primary=[
                    motif_record(
                        "IDENTITY_TRANSFORMATION",
                        strength=0.70,
                    )
                ],
                primary_quality=[
                    quality_record(
                        "IDENTITY_TRANSFORMATION",
                        entropy=0.70,
                        effective=1.60,
                        dominance=0.65,
                        non_draconic=False,
                    )
                ],
                px=75.0,
            ),
            snapshot(px=20.0),
        ]

        result = derive_recurrence_null_calibration(
            baseline,
            nulls,
            policy=self.policy(),
        )

        self.assertEqual(result["state"], "DIAGNOSTIC_ONLY")
        self.assertFalse(result["used_for_weighting"])
        self.assertFalse(result["used_in_px_score"])
        self.assertFalse(result["used_in_ontology"])
        self.assertEqual(len(result["observed_motifs"]), 1)

        item = result["observed_motifs"][0]
        presence = item["metrics"]["RECURRENCE_PRESENCE"][
            "unconditional_true"
        ]
        self.assertEqual(presence["count"], 2)
        self.assertAlmostEqual(presence["frequency"], 2 / 3)

        strength = item["metrics"]["MOTIF_STRENGTH"]
        self.assertEqual(strength["unconditional"]["count"], 1)
        self.assertAlmostEqual(
            strength["unconditional"]["frequency"],
            1 / 3,
        )
        self.assertAlmostEqual(
            strength["conditional_on_motif_present"]["frequency"],
            1 / 2,
        )

        non_draconic = item["metrics"]["NON_DRACONIC_RECURRENCE"]
        self.assertEqual(
            non_draconic["unconditional_true"]["count"],
            1,
        )

    def test_null_catalog_includes_motifs_not_observed_in_baseline(self):
        baseline = snapshot(
            primary=[motif_record("RELATIONAL_COHERENCE")],
            primary_quality=[quality_record("RELATIONAL_COHERENCE")],
        )
        nulls = [
            snapshot(
                primary=[motif_record("TRANSFORMATION_POWER")],
                primary_quality=[quality_record("TRANSFORMATION_POWER")],
            ),
            snapshot(
                primary=[motif_record("TRANSFORMATION_POWER")],
                primary_quality=[quality_record("TRANSFORMATION_POWER")],
            ),
            snapshot(),
        ]
        result = derive_recurrence_null_calibration(
            baseline,
            nulls,
            policy=self.policy(),
        )
        catalog = {
            item["motif_id"]: item
            for item in result["null_catalog"]["primary"]
        }
        self.assertIn("TRANSFORMATION_POWER", catalog)
        self.assertAlmostEqual(
            catalog["TRANSFORMATION_POWER"]["recurrence"]["frequency"],
            2 / 3,
        )

    def test_aggregate_calibrates_px_and_motif_count(self):
        baseline = snapshot(
            primary=[
                motif_record("RELATIONAL_COHERENCE"),
                motif_record("TRANSFORMATION_POWER"),
            ],
            primary_quality=[
                quality_record("RELATIONAL_COHERENCE"),
                quality_record("TRANSFORMATION_POWER"),
            ],
            px=95.0,
        )
        nulls = [
            snapshot(
                primary=[
                    motif_record("RELATIONAL_COHERENCE"),
                    motif_record("TRANSFORMATION_POWER"),
                    motif_record("KARMIC_CONTINUITY"),
                ],
                primary_quality=[
                    quality_record("RELATIONAL_COHERENCE"),
                    quality_record("TRANSFORMATION_POWER"),
                    quality_record("KARMIC_CONTINUITY"),
                ],
                px=97.0,
            ),
            snapshot(
                primary=[motif_record("RELATIONAL_COHERENCE")],
                primary_quality=[quality_record("RELATIONAL_COHERENCE")],
                px=80.0,
            ),
            snapshot(px=30.0),
        ]
        result = derive_recurrence_null_calibration(
            baseline,
            nulls,
            policy=self.policy(),
        )
        self.assertAlmostEqual(
            result["aggregate"]["PX_SCORE"]["structural_frequency"][
                "frequency"
            ],
            1 / 3,
        )
        self.assertAlmostEqual(
            result["aggregate"]["PRIMARY_RECURRENT_MOTIF_COUNT"][
                "structural_frequency"
            ]["frequency"],
            1 / 3,
        )

    def test_insufficient_null_count_is_not_evaluable(self):
        result = derive_recurrence_null_calibration(
            snapshot(),
            [snapshot()],
            policy=self.policy(minimum=2),
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")

    def test_missing_quality_data_fails_closed_without_scoring(self):
        result = derive_recurrence_null_calibration(
            {"pillar_attribution": {}},
            [snapshot(), snapshot(), snapshot()],
            policy=self.policy(),
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertFalse(result["used_for_weighting"])
        self.assertFalse(result["metaphysical_probability"])


if __name__ == "__main__":
    unittest.main()
