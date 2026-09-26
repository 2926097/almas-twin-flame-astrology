from __future__ import annotations

from copy import deepcopy
import unittest

from almas_tfa.external_control_cohorts import (
    extract_validated_external_snapshots,
    load_external_recurrence_cohort_policy,
    validate_external_recurrence_cohort,
)


def recurrence_snapshot():
    return {
        "pillar_attribution": {
            "semantic_motifs": {
                "recurrent_primary_motifs": [],
                "recurrent_mission_motifs": [],
                "px": {"score": 0.0, "recurrent_motif_count": 0},
                "ps": {"score": 0.0, "recurrent_motif_count": 0},
            },
            "recurrence_quality": {
                "primary_motifs": [],
                "mission_motifs": [],
            },
        }
    }


def sample(
    sample_ref: str,
    *,
    validation_status="EXTERNAL_HOLDOUT",
    selection_status="PREREGISTERED",
    label_blinding="BLINDED",
    contamination=False,
    forbidden_field_hits=0,
    label_leakage_count=0,
    narrative_leakage_count=0,
    case_fitting_count=0,
    snapshot=None,
):
    return {
        "sample_ref": sample_ref,
        "validation_status": validation_status,
        "selection_status": selection_status,
        "label_blinding": label_blinding,
        "contamination": contamination,
        "forbidden_field_hits": forbidden_field_hits,
        "label_leakage_count": label_leakage_count,
        "narrative_leakage_count": narrative_leakage_count,
        "case_fitting_count": case_fitting_count,
        "recurrence_snapshot": (
            recurrence_snapshot() if snapshot is None else snapshot
        ),
    }


def cohort(samples=None):
    return {
        "cohort_id": "EXT-REC-001",
        "preregistration_ref": "PREREG-EXT-001",
        "null_model": "PAIR_SHUFFLE",
        "frozen_almas_version": "1.15.0-dev",
        "frozen_commit_sha": "abcdef1234567890",
        "feature_set_ref": "FEATURES-1",
        "orb_policy_ref": "ORBS-1",
        "pairing_rule_ref": "PAIRING-1",
        "inclusion_rule_ref": "INCLUSION-1",
        "leakage_audit_ref": "LEAK-1",
        "samples": list(samples or [sample("S1"), sample("S2")]),
    }


class ExternalRecurrenceCohortTests(unittest.TestCase):
    def test_policy_is_protocol_only(self):
        policy = load_external_recurrence_cohort_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_EXTERNAL_RECURRENCE_COHORT_V1",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertTrue(
            policy["principles"]["public_output_must_be_aggregate_only"]
        )
        self.assertFalse(policy["principles"]["weighting_enabled"])
        self.assertFalse(policy["principles"]["l3_validation_enabled"])

    def test_clean_external_holdout_is_protocol_ready(self):
        result = validate_external_recurrence_cohort(cohort())
        self.assertEqual(result["state"], "PROTOCOL_READY")
        self.assertEqual(result["sample_count"], 2)
        self.assertEqual(result["external_candidate_count"], 2)
        self.assertEqual(result["external_candidate_clean_count"], 2)
        self.assertTrue(result["all_external_candidates_clean"])
        self.assertFalse(result["private_sample_refs_exposed"])
        self.assertFalse(result["sample_snapshots_exposed"])
        self.assertFalse(result["candidate_weighting_enabled"])
        self.assertFalse(result["l3_validation"])

    def test_contamination_and_leakage_are_counted_and_not_promoted(self):
        data = cohort(
            [
                sample(
                    "S1",
                    contamination=True,
                    label_leakage_count=1,
                ),
                sample("S2"),
            ]
        )
        result = validate_external_recurrence_cohort(data)
        self.assertEqual(result["state"], "PROTOCOL_READY")
        self.assertEqual(result["contamination_count"], 1)
        self.assertEqual(result["leakage_sample_count"], 1)
        self.assertEqual(result["external_candidate_count"], 2)
        self.assertEqual(result["external_candidate_clean_count"], 1)
        self.assertFalse(result["all_external_candidates_clean"])
        self.assertFalse(result["used_for_weighting"])

    def test_post_hoc_external_case_is_not_clean_candidate(self):
        data = cohort(
            [
                sample(
                    "S1",
                    selection_status="POST_HOC",
                )
            ]
        )
        result = validate_external_recurrence_cohort(data)
        self.assertEqual(result["external_candidate_count"], 1)
        self.assertEqual(result["external_candidate_clean_count"], 0)
        self.assertFalse(result["all_external_candidates_clean"])

    def test_development_only_never_becomes_external_candidate(self):
        data = cohort(
            [
                sample(
                    "DEV-1",
                    validation_status="DEVELOPMENT_ONLY",
                    selection_status="POST_HOC",
                    label_blinding="UNBLINDED",
                )
            ]
        )
        result = validate_external_recurrence_cohort(data)
        self.assertEqual(result["state"], "PROTOCOL_READY")
        self.assertEqual(result["external_candidate_count"], 0)
        self.assertEqual(result["external_candidate_clean_count"], 0)
        self.assertFalse(result["all_external_candidates_clean"])
        self.assertFalse(result["candidate_weighting_enabled"])

    def test_invalid_snapshot_fails_closed(self):
        data = cohort(
            [
                sample(
                    "S1",
                    snapshot={"pillar_attribution": {}},
                )
            ]
        )
        result = validate_external_recurrence_cohort(data)
        self.assertEqual(result["state"], "NOT_EVALUABLE")
        self.assertEqual(result["invalid_snapshot_count"], 1)
        self.assertFalse(result["sample_snapshots_exposed"])

    def test_duplicate_sample_ref_raises(self):
        data = cohort([sample("S1"), sample("S1")])
        with self.assertRaises(ValueError):
            validate_external_recurrence_cohort(data)

    def test_runtime_extraction_returns_snapshots_only_after_validation(self):
        data = cohort([sample("S1"), sample("S2")])
        snapshots = extract_validated_external_snapshots(data)
        self.assertEqual(len(snapshots), 2)

        bad = deepcopy(data)
        bad["samples"][0]["recurrence_snapshot"] = {}
        self.assertEqual(extract_validated_external_snapshots(bad), [])


if __name__ == "__main__":
    unittest.main()
