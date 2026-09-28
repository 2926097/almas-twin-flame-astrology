from __future__ import annotations

from copy import deepcopy
import unittest

from almas_tfa.validation_ledger import (
    append_validation_event,
    audit_validation_ledger,
    initialize_validation_ledger,
)
from almas_tfa.validation_preregistration import (
    build_validation_preregistration_bundle,
)


def candidate():
    return {
        "candidate_id": "PX3-C1",
        "status": "FROZEN_FOR_VALIDATION",
        "target": "PX",
        "descriptor_ids": ["NON_DRACONIC_RECURRENCE"],
        "formula_ref": "PX3-FORMULA-1",
        "expected_direction": "HIGHER_IS_MORE_SPECIFIC",
        "development_case_refs": ["DEV-A"],
        "s2_refs": ["S2-1"],
        "s3_refs": ["S3-1"],
        "ablation_refs": ["AB-1"],
        "negative_control_refs": ["NEG-1"],
        "falsification_criteria": ["FALSIFY-1"],
        "holdout_refs": [],
        "formula_frozen_before_holdout": True,
        "holdout_fitted_thresholds": False,
        "scoring_enabled": False,
        "ontology_enabled": False,
    }


def plan():
    return {
        "validation_id": "VAL-1",
        "preregistration_ref": "PREREG-VAL-1",
        "frozen_almas_version": "1.16.0-dev",
        "frozen_commit_sha": "abcdef1234567890",
        "cohort_plan": {
            "cohort_id": "HOLDOUT-C1",
            "null_model": "PAIR_SHUFFLE",
            "feature_set_ref": "FEATURES-V1",
            "orb_policy_ref": "ORBS-V1",
            "pairing_rule_ref": "PAIR-RULE-1",
            "inclusion_rule_ref": "INCLUSION-1",
            "planned_min_samples": 40,
        },
        "blinding_plan_ref": "BLIND-1",
        "leakage_audit_plan_ref": "LEAK-1",
        "independent_replication_plan_refs": ["REPL-1"],
        "negative_control_refs": ["NEG-1"],
        "ablation_refs": ["AB-1"],
        "planned_holdout_refs": ["HOLD-1"],
        "endpoints": [
            {"endpoint_id": "SPECIFICITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "NEGATIVE_CONTROL_FALSE_SPECIFICITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "ABLATION_STABILITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "REPLICATION_STABILITY", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "LEAKAGE_ZERO", "success_criterion": "A", "failure_criterion": "B"},
            {"endpoint_id": "NO_POSTHOC_CHANGE", "success_criterion": "A", "failure_criterion": "B"},
        ],
    }


def prereg():
    return build_validation_preregistration_bundle(candidate(), plan())


class ValidationLedgerTests(unittest.TestCase):
    def test_initializes_from_valid_preregistration(self):
        result = initialize_validation_ledger(prereg())
        self.assertEqual(result["state"], "LEDGER_ACTIVE")
        ledger = result["ledger"]
        self.assertEqual(ledger["entry_count"], 1)
        self.assertEqual(ledger["current_event"], "PREREGISTERED")
        self.assertFalse(ledger["closed"])
        self.assertEqual(
            audit_validation_ledger(ledger)["state"],
            "LEDGER_VALID",
        )

    def test_full_event_chain_closes_in_strict_order(self):
        ledger = initialize_validation_ledger(prereg())["ledger"]
        for event, ref, digit in [
            ("HOLDOUT_OPENED", "OPEN-1", "1"),
            ("HOLDOUT_EVALUATED", "EVAL-1", "2"),
            ("DOCUMENTARY_REVEALED", "REVEAL-1", "3"),
            ("VALIDATION_CLOSED", "CLOSE-1", "4"),
        ]:
            result = append_validation_event(
                ledger,
                event_type=event,
                artifact_ref=ref,
                artifact_sha256=digit * 64,
            )
            ledger = result["ledger"]

        self.assertEqual(result["state"], "LEDGER_CLOSED")
        self.assertEqual(ledger["entry_count"], 5)
        self.assertTrue(ledger["closed"])
        audit = audit_validation_ledger(ledger)
        self.assertEqual(audit["state"], "LEDGER_VALID")
        self.assertEqual(audit["current_event"], "VALIDATION_CLOSED")

    def test_event_order_cannot_be_skipped(self):
        ledger = initialize_validation_ledger(prereg())["ledger"]
        result = append_validation_event(
            ledger,
            event_type="HOLDOUT_EVALUATED",
            artifact_ref="EVAL-1",
            artifact_sha256="2" * 64,
        )
        self.assertEqual(result["state"], "BLOCKED_LEDGER_OPERATION")
        self.assertEqual(result["reason"], "INVALID_EVENT_TRANSITION")
        self.assertEqual(result["expected_event"], "HOLDOUT_OPENED")

    def test_prior_entry_tampering_is_detected(self):
        ledger = initialize_validation_ledger(prereg())["ledger"]
        ledger = append_validation_event(
            ledger,
            event_type="HOLDOUT_OPENED",
            artifact_ref="OPEN-1",
            artifact_sha256="1" * 64,
        )["ledger"]
        tampered = deepcopy(ledger)
        tampered["entries"][0]["artifact_ref"] = "CHANGED"
        audit = audit_validation_ledger(tampered)
        self.assertEqual(audit["state"], "LEDGER_INVALID")
        self.assertEqual(audit["reason"], "ENTRY_HASH_MISMATCH")

    def test_chain_link_tampering_is_detected(self):
        ledger = initialize_validation_ledger(prereg())["ledger"]
        ledger = append_validation_event(
            ledger,
            event_type="HOLDOUT_OPENED",
            artifact_ref="OPEN-1",
            artifact_sha256="1" * 64,
        )["ledger"]
        tampered = deepcopy(ledger)
        tampered["entries"][1]["previous_entry_sha256"] = "0" * 64
        audit = audit_validation_ledger(tampered)
        self.assertEqual(audit["state"], "LEDGER_INVALID")
        self.assertEqual(audit["reason"], "CHAIN_LINK_MISMATCH")

    def test_closed_ledger_cannot_be_appended(self):
        ledger = initialize_validation_ledger(prereg())["ledger"]
        for event, digit in [
            ("HOLDOUT_OPENED", "1"),
            ("HOLDOUT_EVALUATED", "2"),
            ("DOCUMENTARY_REVEALED", "3"),
            ("VALIDATION_CLOSED", "4"),
        ]:
            ledger = append_validation_event(
                ledger,
                event_type=event,
                artifact_ref=event,
                artifact_sha256=digit * 64,
            )["ledger"]

        result = append_validation_event(
            ledger,
            event_type="VALIDATION_CLOSED",
            artifact_ref="SECOND-CLOSE",
            artifact_sha256="5" * 64,
        )
        self.assertEqual(result["state"], "BLOCKED_LEDGER_OPERATION")
        self.assertEqual(result["reason"], "LEDGER_ALREADY_CLOSED")

    def test_invalid_artifact_hash_is_rejected(self):
        ledger = initialize_validation_ledger(prereg())["ledger"]
        result = append_validation_event(
            ledger,
            event_type="HOLDOUT_OPENED",
            artifact_ref="OPEN-1",
            artifact_sha256="not-a-sha",
        )
        self.assertEqual(result["state"], "BLOCKED_LEDGER_OPERATION")
        self.assertEqual(result["reason"], "INVALID_ARTIFACT_SHA256")


if __name__ == "__main__":
    unittest.main()
