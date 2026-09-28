from __future__ import annotations

import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


class FixedStarParanPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(
            (
                ROOT
                / "src/almas_tfa/data/fixed-star-paran-policy.json"
            ).read_text(encoding="utf-8")
        )
        self.policy_schema = json.loads(
            (ROOT / "schemas/fixed-star-paran-policy.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.result_schema = json.loads(
            (ROOT / "schemas/fixed-star-paran-result.schema.json").read_text(
                encoding="utf-8"
            )
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
            "changes_scoring",
            "creates_structural_root",
            "creates_discriminator",
            "changes_iem",
            "changes_idd",
            "changes_irc",
            "changes_iat",
            "changes_icc",
            "changes_ice",
            "changes_ontology",
        ):
            self.assertFalse(firewall[field])
        self.assertEqual(
            firewall["discriminating_power"],
            "SUPPORT_ONLY",
        )

    def test_frozen_policy_validates_against_closed_schema(self):
        errors = list(
            Draft202012Validator(self.policy_schema).iter_errors(self.policy)
        )
        self.assertEqual(errors, [])
        self.assertEqual(
            self.policy["parans"]["day_basis"],
            "UT_CALENDAR_DAY",
        )
        self.assertEqual(
            self.policy["result_contract"]["partial_success"],
            "FORBIDDEN",
        )

    def test_synthetic_result_fixture_validates_and_firewall_is_closed(self):
        fixture = json.loads(
            (
                ROOT
                / "tests/fixtures/fixed_star_paran/synthetic-result.json"
            ).read_text(encoding="utf-8")
        )
        errors = list(
            Draft202012Validator(self.result_schema).iter_errors(fixture)
        )
        self.assertEqual(errors, [])
        self.assertEqual(
            fixture["structural_role"],
            "SUPPORT_ONLY",
        )
        self.assertEqual(
            fixture["canon"]["returned_count"],
            len(fixture["canon"]["entries"]),
        )

        invalid = dict(fixture)
        invalid["structural_role"] = "STRUCTURAL"
        self.assertTrue(
            list(Draft202012Validator(self.result_schema).iter_errors(invalid))
        )

    def test_manifest_keeps_router_gap_and_names_registered_sources(self):
        manifest = json.loads(
            (ROOT / "reference/fixed-star-paran-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["router_domain_status"], "SOURCE_GAP")
        self.assertEqual(manifest["structural_role"], "SUPPORT_ONLY")
        self.assertEqual(
            set(manifest["source_ids"]),
            {
                "brady_book_fixed_stars_1998",
                "ptolemy_tetrabiblos_1_9_fixed_stars",
            },
        )


if __name__ == "__main__":
    unittest.main()
