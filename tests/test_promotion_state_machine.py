import copy
import unittest

from almas_tfa.promotion_state_machine import (
    apply_promotion_transition,
    load_promotion_state_machine_policy,
    validate_promotion_transition,
)


EVIDENCE_KEYS = (
    "implementation_refs",
    "reproducibility_refs",
    "synthetic_test_refs",
    "preregistration_refs",
    "counterevidence_refs",
    "negative_control_plan_refs",
    "leakage_plan_refs",
    "independent_replication_refs",
    "negative_control_result_refs",
    "doctrine_gate_refs",
    "discriminator_evaluation_refs",
    "holdout_protocol_refs",
    "support_only_exclusion_refs",
)


def evidence(*, complete=False):
    result = {key: [] for key in EVIDENCE_KEYS}
    if complete:
        for key in EVIDENCE_KEYS:
            result[key] = [f"REF:{key}"]
    return result


def base_record(status="EXPLORATORY"):
    return {
        "discriminator_id": "TEST_DISC",
        "current_status": status,
        "l3_authorized": False,
        "promotion_ref": None,
        "promoted_at": None,
        "validated_pairs": [],
        "root_key_prefix": "TEST:",
        "frozen": None,
        "validation_evidence": None,
        "block_reason": None,
        "uses_astrology": False,
        "astrology_validation": None,
        "discriminant_validation": None,
        "blinding_audit": None,
        "promotion_evidence": evidence(),
        "last_active_status": None,
        "state_history": [
            {
                "transition_id": "IMPORT:TEST",
                "from_status": None,
                "to_status": status,
                "mode": "IMPORT",
                "occurred_at": "2026-09-26T00:00:00Z",
                "actor_ref": "TEST",
                "reason": "fixture",
                "evidence_refs": ["FIXTURE"],
                "record_fingerprint_before": None,
                "record_fingerprint_after": None,
            }
        ],
    }


def transition(
    source,
    target,
    mode,
    *,
    transition_id="T1",
    updates=None,
    block_resolution_refs=None,
):
    value = {
        "transition_id": transition_id,
        "from_status": source,
        "to_status": target,
        "mode": mode,
        "occurred_at": "2026-09-26T12:00:00Z",
        "actor_ref": "TEST-ACTOR",
        "reason": "test transition",
        "evidence_refs": ["EVIDENCE-1"],
        "record_updates": updates or {},
    }
    if block_resolution_refs is not None:
        value["block_resolution_refs"] = block_resolution_refs
    return value


def reproducible_evidence():
    value = evidence()
    for key in (
        "implementation_refs",
        "reproducibility_refs",
        "synthetic_test_refs",
    ):
        value[key] = [f"REF:{key}"]
    return value


def complete_blinding_audit():
    return {
        "policy_id": "ALMAS_BLINDING_LEAKAGE_V1",
        "audit_refs": ["BLIND-1"],
        "structural_input_refs": ["INPUT-1"],
        "structural_input_sha256": "a" * 64,
        "pre_reveal_output_sha256": "b" * 64,
        "post_reveal_structural_output_sha256": "b" * 64,
        "development_evaluation_disjoint": True,
        "labels_hidden": True,
        "narrative_hidden": True,
        "expected_result_hidden": True,
        "holdout_outcome_hidden": True,
        "late_reveal_performed": True,
        "structural_output_invariant_after_reveal": True,
        "forbidden_field_hits": 0,
        "label_leakage_count": 0,
        "narrative_leakage_count": 0,
        "case_fitting_count": 0,
        "post_holdout_rule_change_count": 0,
        "identity_visibility": "HIDDEN",
        "identity_risk_refs": [],
    }


def complete_discriminant_validation():
    return {
        "policy_id": "ALMAS_DISCRIMINANT_VALIDATION_V1",
        "evaluation_refs": ["EVAL-1"],
        "development_evaluation_disjoint": True,
        "pairwise_results": [
            {
                "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
                "positive_model": "MONADIC_ORIGIN",
                "tp": 240,
                "tn": 480,
                "fp": 10,
                "fn": 20,
            }
        ],
        "false_specificity": {
            "evaluable_count": 100,
            "error_count": 0,
        },
        "synthetic_adversarial": {
            "evaluable_count": 100,
            "false_specificity_count": 0,
        },
        "calibration": {
            "mode": "NOT_APPLICABLE_CATEGORICAL",
            "passed": None,
            "criterion_ref": None,
            "refs": [],
        },
    }


class TestPromotionStateMachine(unittest.TestCase):

    def test_policy_has_expected_mainline(self):
        policy = load_promotion_state_machine_policy()
        self.assertEqual(policy["policy_id"], "ALMAS_PROMOTION_STATE_MACHINE_V1")
        self.assertEqual(
            policy["mainline_states"],
            [
                "EXPLORATORY",
                "REPRODUCIBLE",
                "REPLICATION_READY",
                "CONFIRMATORY_ELIGIBLE",
                "VALIDATED_DISCRIMINATOR",
            ],
        )
        self.assertTrue(policy["retired_is_terminal"])
        self.assertFalse(policy["forward_skips_allowed"])

    def test_forward_requires_cumulative_target_evidence(self):
        record = base_record()
        step = transition("EXPLORATORY", "REPRODUCIBLE", "FORWARD")

        with self.assertRaises(ValueError):
            validate_promotion_transition(record, step)

        step["record_updates"] = {
            "promotion_evidence": reproducible_evidence()
        }
        candidate = validate_promotion_transition(record, step)
        self.assertEqual(candidate["current_status"], "REPRODUCIBLE")

    def test_forward_skip_is_rejected_even_with_complete_evidence(self):
        record = base_record()
        step = transition(
            "EXPLORATORY",
            "REPLICATION_READY",
            "FORWARD",
            updates={"promotion_evidence": evidence(complete=True)},
        )
        with self.assertRaises(ValueError):
            validate_promotion_transition(record, step)

    def test_rollback_only_one_mainline_level(self):
        record = base_record("REPRODUCIBLE")
        record["promotion_evidence"] = reproducible_evidence()

        allowed = transition(
            "REPRODUCIBLE",
            "EXPLORATORY",
            "ROLLBACK",
        )
        result = apply_promotion_transition(record, allowed)
        self.assertEqual(result["current_status"], "EXPLORATORY")
        self.assertEqual(result["state_history"][-1]["mode"], "ROLLBACK")

        skipped = transition(
            "REPRODUCIBLE",
            "REPLICATION_READY",
            "ROLLBACK",
            transition_id="T2",
        )
        with self.assertRaises(ValueError):
            validate_promotion_transition(record, skipped)

    def test_block_and_unblock_return_to_last_active_state(self):
        record = base_record()
        blocked = apply_promotion_transition(
            record,
            transition("EXPLORATORY", "BLOCKED", "BLOCK"),
        )
        self.assertEqual(blocked["current_status"], "BLOCKED")
        self.assertEqual(blocked["last_active_status"], "EXPLORATORY")

        with self.assertRaises(ValueError):
            validate_promotion_transition(
                blocked,
                transition(
                    "BLOCKED",
                    "EXPLORATORY",
                    "UNBLOCK",
                    transition_id="T2",
                ),
            )

        unblocked = apply_promotion_transition(
            blocked,
            transition(
                "BLOCKED",
                "EXPLORATORY",
                "UNBLOCK",
                transition_id="T2",
                block_resolution_refs=["RESOLUTION-1"],
            ),
        )
        self.assertEqual(unblocked["current_status"], "EXPLORATORY")
        self.assertIsNone(unblocked["last_active_status"])

    def test_retired_is_terminal(self):
        record = base_record("RETIRED")
        with self.assertRaises(ValueError):
            validate_promotion_transition(
                record,
                transition(
                    "RETIRED",
                    "EXPLORATORY",
                    "ROLLBACK",
                ),
            )

    def test_validated_cannot_rollback_and_must_retire_if_invalidated(self):
        record = base_record("VALIDATED_DISCRIMINATOR")
        record["l3_authorized"] = True

        with self.assertRaises(ValueError):
            validate_promotion_transition(
                record,
                transition(
                    "VALIDATED_DISCRIMINATOR",
                    "CONFIRMATORY_ELIGIBLE",
                    "ROLLBACK",
                ),
            )

        retired = apply_promotion_transition(
            record,
            transition(
                "VALIDATED_DISCRIMINATOR",
                "RETIRED",
                "RETIRE",
                transition_id="T2",
            ),
        )
        self.assertEqual(retired["current_status"], "RETIRED")
        self.assertFalse(retired["l3_authorized"])

    def test_transition_id_cannot_be_reused(self):
        record = base_record()
        step = transition(
            "EXPLORATORY",
            "REPRODUCIBLE",
            "FORWARD",
            transition_id="IMPORT:TEST",
            updates={"promotion_evidence": reproducible_evidence()},
        )
        with self.assertRaises(ValueError):
            validate_promotion_transition(record, step)

    def test_identity_fields_are_immutable_through_transition(self):
        record = base_record()
        step = transition(
            "EXPLORATORY",
            "REPRODUCIBLE",
            "FORWARD",
            updates={
                "promotion_evidence": reproducible_evidence(),
                "discriminator_id": "MUTATED",
            },
        )
        with self.assertRaises(ValueError):
            validate_promotion_transition(record, step)

    def test_non_validated_state_cannot_authorize_l3(self):
        record = base_record()
        step = transition(
            "EXPLORATORY",
            "REPRODUCIBLE",
            "FORWARD",
            updates={
                "promotion_evidence": reproducible_evidence(),
                "l3_authorized": True,
            },
        )
        with self.assertRaises(ValueError):
            validate_promotion_transition(record, step)

    def test_confirmatory_to_validated_requires_all_existing_l3_gates(self):
        record = base_record("CONFIRMATORY_ELIGIBLE")
        record["promotion_evidence"] = evidence(complete=True)

        incomplete = transition(
            "CONFIRMATORY_ELIGIBLE",
            "VALIDATED_DISCRIMINATOR",
            "FORWARD",
        )
        with self.assertRaises(ValueError):
            validate_promotion_transition(record, incomplete)

        updates = {
            "l3_authorized": True,
            "promotion_ref": "PROMO:TEST:1",
            "promoted_at": "2026-09-26T12:30:00Z",
            "validated_pairs": [
                ["SOULMATE_MODEL", "MONADIC_ORIGIN"]
            ],
            "frozen": {
                "almas_version": "TEST",
                "commit_sha": "test-sha",
                "rule_ref": "TEST-RULE",
                "schema_refs": ["TEST-SCHEMA"],
            },
            "validation_evidence": {
                "preregistration_refs": ["PREREG-1"],
                "independent_replication_refs": ["REPL-1"],
                "external_holdout_refs": ["HOLDOUT-1"],
                "negative_control_refs": ["NEG-1"],
                "leakage_audit_refs": ["LEAK-1"],
            },
            "discriminant_validation": complete_discriminant_validation(),
            "blinding_audit": complete_blinding_audit(),
        }
        valid = transition(
            "CONFIRMATORY_ELIGIBLE",
            "VALIDATED_DISCRIMINATOR",
            "FORWARD",
            transition_id="T2",
            updates=updates,
        )
        candidate = apply_promotion_transition(record, valid)
        self.assertEqual(
            candidate["current_status"],
            "VALIDATED_DISCRIMINATOR",
        )
        self.assertTrue(candidate["l3_authorized"])
        self.assertEqual(candidate["promotion_ref"], "PROMO:TEST:1")
        self.assertRegex(
            candidate["state_history"][-1]["record_fingerprint_after"],
            r"^[0-9a-f]{64}$",
        )


if __name__ == "__main__":
    unittest.main()
