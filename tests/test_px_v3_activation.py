from __future__ import annotations

from copy import deepcopy
import unittest

from almas_tfa.px_v3_activation import (
    evaluate_px_v3_activation_firewall,
    load_px_v3_activation_firewall_policy,
)
from almas_tfa.px_v3_candidates import load_px_v3_candidate_registry


class PxV3ActivationFirewallTests(unittest.TestCase):
    def test_policy_locks_px_v3_out_of_1_15(self):
        policy = load_px_v3_activation_firewall_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_PX_V3_ACTIVATION_FIREWALL_V1",
        )
        self.assertEqual(policy["release_line"], "1.15")
        self.assertFalse(policy["px_v3_operational_in_release"])
        self.assertTrue(policy["principles"]["same_release_activation_forbidden"])
        self.assertTrue(policy["principles"]["px_v2_remains_operational"])
        self.assertFalse(policy["principles"]["px_v3_scoring_enabled"])

    def test_empty_registry_yields_no_active_candidate(self):
        result = evaluate_px_v3_activation_firewall("1.15.0")
        self.assertEqual(result["state"], "NO_ACTIVE_PX_V3_CANDIDATE")
        self.assertEqual(result["px_v3_candidate_record_count"], 0)
        self.assertEqual(result["validated_px_v3_candidate_count"], 0)
        self.assertFalse(result["px_v3_active"])
        self.assertFalse(result["activation_permitted"])
        self.assertTrue(result["px_v2_remains_operational"])

    def test_promotion_eligible_input_still_does_not_activate(self):
        result = evaluate_px_v3_activation_firewall(
            "1.15.0",
            promotion_result={
                "state": "PROMOTION_ELIGIBLE",
                "candidate_id": "PX3-C1",
            },
        )
        self.assertTrue(result["promotion_eligible_input_present"])
        self.assertFalse(result["promotion_eligible_causes_activation"])
        self.assertFalse(result["px_v3_active"])

    def test_candidate_record_inside_1_15_triggers_firewall(self):
        registry = deepcopy(load_px_v3_candidate_registry())
        registry["records"] = [{"candidate_id": "ILLEGAL"}]
        result = evaluate_px_v3_activation_firewall(
            "1.15.0",
            registry=registry,
        )
        self.assertEqual(result["state"], "BLOCKED_RELEASE_FIREWALL")
        self.assertIn(
            "PX_V3_CANDIDATE_RECORDS_PRESENT_IN_1_15",
            result["violations"],
        )
        self.assertFalse(result["activation_permitted"])

    def test_validated_id_inside_1_15_triggers_firewall(self):
        registry = deepcopy(load_px_v3_candidate_registry())
        registry["validated_candidate_ids"] = ["PX3-C1"]
        result = evaluate_px_v3_activation_firewall(
            "1.15.9",
            registry=registry,
        )
        self.assertEqual(result["state"], "BLOCKED_RELEASE_FIREWALL")
        self.assertIn(
            "VALIDATED_PX_V3_IDS_PRESENT_IN_1_15",
            result["violations"],
        )

    def test_other_release_line_requires_new_policy(self):
        result = evaluate_px_v3_activation_firewall("1.16.0")
        self.assertEqual(result["state"], "OUTSIDE_RELEASE_LINE")
        self.assertTrue(result["requires_new_version_policy"])
        self.assertFalse(result["px_v3_active"])

    def test_runtime_registry_flags_are_blocked(self):
        registry = deepcopy(load_px_v3_candidate_registry())
        registry["scoring_enabled"] = True
        result = evaluate_px_v3_activation_firewall(
            "1.15.0",
            registry=registry,
        )
        self.assertEqual(result["state"], "BLOCKED_RELEASE_FIREWALL")
        self.assertIn("REGISTRY_SCORING_ENABLED", result["violations"])
        self.assertFalse(result["scoring_enabled"])


if __name__ == "__main__":
    unittest.main()
