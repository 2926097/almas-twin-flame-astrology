from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FixedStarParanPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(
            (
                ROOT
                / "src/almas_tfa/data/fixed-star-paran-policy.json"
            ).read_text(encoding="utf-8")
        )

    def test_provider_and_canon_are_frozen(self):
        self.assertEqual(
            self.policy["policy_id"],
            "ALMAS_FIXED_STAR_PARAN_POLICY_V1",
        )
        self.assertEqual(self.policy["structural_role"], "SUPPORT_ONLY")
        self.assertEqual(
            self.policy["provider"]["pinned_version"],
            "6.8.2",
        )
        self.assertTrue(
            self.policy["provider"]["reuse_existing_backend"]
        )
        self.assertEqual(
            self.policy["star_canon"]["selection"],
            "ALL_AVAILABLE_ENGINE_CANON",
        )
        self.assertEqual(
            set(self.policy["star_canon"]["documented_memberships"]),
            {"ROYAL", "BEHENIAN", "PTOLEMAIC"},
        )
        self.assertTrue(
            self.policy["star_canon"][
                "runtime_canon_fingerprint_required"
            ]
        )

    def test_orbs_are_explicit_not_implicit_defaults(self):
        self.assertEqual(self.policy["parans"]["orb_minutes"], 4.0)
        self.assertEqual(
            self.policy["natal_angular_contacts"]["orb_minutes"],
            2.0,
        )
        self.assertIn(
            "PREREGISTERED_EXPLICITLY",
            self.policy["parans"]["orb_origin"],
        )
        self.assertEqual(
            self.policy["failure_policy"]["implicit_orb_fallback"],
            "FORBIDDEN",
        )

    def test_inferential_firewall_is_support_only(self):
        firewall = self.policy["inferential_firewall"]
        for field in (
            "creates_structural_root",
            "changes_iem",
            "changes_idd",
            "changes_irc",
            "changes_ontology",
        ):
            self.assertFalse(firewall[field])
        self.assertEqual(
            firewall["discriminating_power"],
            "SUPPORT_ONLY",
        )


if __name__ == "__main__":
    unittest.main()
