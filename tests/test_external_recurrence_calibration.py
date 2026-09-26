from __future__ import annotations

from copy import deepcopy
import unittest

from almas_tfa.external_recurrence_calibration import (
    derive_external_recurrence_calibration,
    load_external_recurrence_calibration_policy,
)


def motif(motif_id="IDENTITY_TRANSFORMATION", strength=0.8):
    return {
        "motif_id": motif_id,
        "motif_type": "PRIMARY",
        "motif_strength": strength,
        "recurrence_state": "RECURRENT",
        "root_ids": ["R1", "R2"],
        "dependency_families": ["SYN", "DECLINATION"],
        "independent_family_count": 2,
    }


def quality(motif_id="IDENTITY_TRANSFORMATION", non_draconic=True):
    return {
        "motif_id": motif_id,
        "motif_type": "PRIMARY",
        "family_class_count": 2,
        "cross_class_recurrence": True,
        "family_strength_entropy": 0.9,
        "effective_family_count": 1.9,
        "family_dominance_share": 0.55,
        "includes_natal_draconic": not non_draconic,
        "non_draconic_recurrence": non_draconic,
        "leave_one_family_out_survival_fraction": 0.5,
        "leave_one_class_out_survival_fraction": 0.5,
    }


def snapshot(strength=0.8, include=True):
    motifs = [motif(strength=strength)] if include else []
    qualities = [quality()] if include else []
    return {
        "pillar_attribution": {
            "semantic_motifs": {
                "recurrent_primary_motifs": motifs,
                "recurrent_mission_motifs": [],
                "px": {
                    "score": strength * 100 if include else 0.0,
                    "recurrent_motif_count": 1 if include else 0,
                },
                "ps": {"score": 0.0, "recurrent_motif_count": 0},
            },
            "recurrence_quality": {
                "primary_motifs": qualities,
                "mission_motifs": [],
            },
        }
    }


def sample(
    ref,
    *,
    snap=None,
    status="EXTERNAL_HOLDOUT",
    selection="PREREGISTERED",
    contamination=False,
    leakage=0,
):
    return {
        "sample_ref": ref,
        "validation_status": status,
        "selection_status": selection,
        "label_blinding": "BLINDED",
        "contamination": contamination,
        "forbidden_field_hits": 0,
        "label_leakage_count": leakage,
        "narrative_leakage_count": 0,
        "case_fitting_count": 0,
        "recurrence_snapshot": snap if snap is not None else snapshot(),
    }


def cohort(samples):
    return {
        "cohort_id": "EXT-CAL-1",
        "preregistration_ref": "PREREG-EXT-CAL-1",
        "null_model": "PAIR_SHUFFLE",
        "frozen_almas_version": "1.15.0-dev",
        "frozen_commit_sha": "abcdef1234567890",
        "feature_set_ref": "FEATURES-1",
        "orb_policy_ref": "ORBS-1",
        "pairing_rule_ref": "PAIR-1",
        "inclusion_rule_ref": "INCLUDE-1",
        "samples": samples,
    }


class ExternalRecurrenceCalibrationTests(unittest.TestCase):
    def test_policy_is_diagnostic_only(self):
        policy = load_external_recurrence_calibration_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_EXTERNAL_RECURRENCE_CALIBRATION_V1",
        )
        self.assertTrue(policy["principles"]["diagnostic_only"])
        self.assertTrue(policy["principles"]["clean_external_candidates_only"])
        self.assertFalse(policy["principles"]["weighting_enabled"])
        self.assertFalse(policy["principles"]["candidate_freeze_enabled"])

    def test_clean_external_controls_calibrate_without_weighting(self):
        data = cohort(
            [
                sample("S1", snap=snapshot(0.9)),
                sample("S2", snap=snapshot(0.7)),
                sample("S3", snap=snapshot(include=False)),
            ]
        )
        result = derive_external_recurrence_calibration(
            snapshot(0.8),
            data,
        )
        self.assertEqual(result["state"], "DIAGNOSTIC_ONLY")
        self.assertEqual(result["clean_external_sample_count"], 3)
        self.assertTrue(result["external_control_evidence"])
        self.assertFalse(result["used_for_weighting"])
        self.assertFalse(result["candidate_freeze_enabled"])
        self.assertFalse(result["l3_validation"])
        self.assertFalse(result["sample_identifiers_exposed"])
        self.assertFalse(result["sample_snapshots_exposed"])
        self.assertEqual(
            result["interpretation_scope"],
            "EXTERNAL_CONTROL_COHORT_RECURRENCE_FREQUENCY",
        )

        item = result["observed_motifs"][0]
        frequency = item["metrics"]["MOTIF_STRENGTH"]["unconditional"]
        self.assertEqual(frequency["n"], 3)
        self.assertEqual(frequency["count"], 1)

    def test_development_and_contaminated_samples_are_excluded(self):
        data = cohort(
            [
                sample("GOOD", snap=snapshot(0.9)),
                sample(
                    "DEV",
                    snap=snapshot(0.95),
                    status="DEVELOPMENT_ONLY",
                    selection="POST_HOC",
                ),
                sample(
                    "BAD",
                    snap=snapshot(0.99),
                    contamination=True,
                ),
            ]
        )
        result = derive_external_recurrence_calibration(
            snapshot(0.8),
            data,
        )
        self.assertEqual(result["state"], "DIAGNOSTIC_ONLY")
        self.assertEqual(result["clean_external_sample_count"], 1)
        self.assertEqual(result["sample_count"], 1)
        self.assertEqual(
            result["cohort_summary"]["contamination_count"],
            1,
        )

    def test_leakage_sample_is_excluded(self):
        data = cohort(
            [
                sample("GOOD"),
                sample("LEAK", leakage=1),
            ]
        )
        result = derive_external_recurrence_calibration(
            snapshot(),
            data,
        )
        self.assertEqual(result["clean_external_sample_count"], 1)
        self.assertEqual(result["cohort_summary"]["leakage_sample_count"], 1)

    def test_minimum_clean_external_samples_fails_closed(self):
        policy = deepcopy(load_external_recurrence_calibration_policy())
        policy["minimum_clean_external_samples"] = 2
        data = cohort([sample("ONLY")])
        result = derive_external_recurrence_calibration(
            snapshot(),
            data,
            calibration_policy=policy,
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertFalse(result["used_for_weighting"])
        self.assertFalse(result["metaphysical_probability"])

    def test_invalid_s4_cohort_cannot_calibrate(self):
        bad_snapshot = {"pillar_attribution": {}}
        data = cohort([sample("BAD", snap=bad_snapshot)])
        result = derive_external_recurrence_calibration(
            snapshot(),
            data,
        )
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertFalse(result["candidate_freeze_enabled"])


if __name__ == "__main__":
    unittest.main()
