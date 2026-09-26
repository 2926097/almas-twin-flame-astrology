import copy
import unittest

from almas_tfa.promotion_reporting import build_promotion_reporting


def registry_fixture():
    return {
        "registry_version": "TEST-1",
        "authority": "ALMAS_CANONICAL_DISCRIMINATOR_PROMOTION_REGISTRY",
        "validated_discriminator_ids": [],
        "records": [
            {
                "discriminator_id": "OD_A",
                "current_status": "EXPLORATORY",
                "last_active_status": None,
                "block_reason": None,
                "uses_astrology": True,
                "l3_authorized": False,
                "promotion_ref": None,
                "promoted_at": None,
                "validated_pairs": [],
                "root_key_prefix": "OD_A:",
                "frozen": None,
                "validation_evidence": None,
                "discriminant_validation": None,
                "blinding_audit": None,
                "astrology_validation": None,
                "promotion_evidence": {
                    "implementation_refs": ["IMPL-1"],
                    "reproducibility_refs": [],
                    "synthetic_test_refs": [],
                    "preregistration_refs": [],
                    "counterevidence_refs": [],
                    "negative_control_plan_refs": [],
                    "leakage_plan_refs": [],
                    "independent_replication_refs": [],
                    "negative_control_result_refs": [],
                    "doctrine_gate_refs": [],
                    "discriminator_evaluation_refs": [],
                    "holdout_protocol_refs": [],
                    "support_only_exclusion_refs": [],
                },
                "state_history": [
                    {
                        "transition_id": "IMPORT:OD_A",
                        "from_status": None,
                        "to_status": "EXPLORATORY",
                        "mode": "IMPORT",
                        "occurred_at": "2026-09-26T00:00:00Z",
                        "actor_ref": "TEST",
                        "reason": "fixture",
                        "evidence_refs": ["FIXTURE"],
                        "record_fingerprint_before": None,
                        "record_fingerprint_after": None,
                    }
                ],
            },
            {
                "discriminator_id": "OD_B",
                "current_status": "BLOCKED",
                "last_active_status": "EXPLORATORY",
                "block_reason": "No existe observable independiente.",
                "uses_astrology": False,
                "l3_authorized": False,
                "promotion_ref": None,
                "promoted_at": None,
                "validated_pairs": [],
                "root_key_prefix": "OD_B:",
                "frozen": None,
                "validation_evidence": None,
                "discriminant_validation": None,
                "blinding_audit": None,
                "astrology_validation": None,
                "promotion_evidence": {
                    "implementation_refs": [],
                    "reproducibility_refs": [],
                    "synthetic_test_refs": [],
                    "preregistration_refs": [],
                    "counterevidence_refs": [],
                    "negative_control_plan_refs": [],
                    "leakage_plan_refs": [],
                    "independent_replication_refs": [],
                    "negative_control_result_refs": [],
                    "doctrine_gate_refs": [],
                    "discriminator_evaluation_refs": [],
                    "holdout_protocol_refs": [],
                    "support_only_exclusion_refs": [],
                },
                "state_history": [
                    {
                        "transition_id": "IMPORT:OD_B",
                        "from_status": None,
                        "to_status": "BLOCKED",
                        "mode": "IMPORT",
                        "occurred_at": "2026-09-26T00:00:00Z",
                        "actor_ref": "TEST",
                        "reason": "fixture",
                        "evidence_refs": ["FIXTURE"],
                        "record_fingerprint_before": None,
                        "record_fingerprint_after": None,
                    }
                ],
            },
            {
                "discriminator_id": "OD_C",
                "current_status": "RETIRED",
                "last_active_status": None,
                "block_reason": "No discrimina modelos.",
                "uses_astrology": False,
                "l3_authorized": False,
                "promotion_ref": None,
                "promoted_at": None,
                "validated_pairs": [],
                "root_key_prefix": "OD_C:",
                "frozen": None,
                "validation_evidence": None,
                "discriminant_validation": None,
                "blinding_audit": None,
                "astrology_validation": None,
                "promotion_evidence": {
                    "implementation_refs": [],
                    "reproducibility_refs": [],
                    "synthetic_test_refs": [],
                    "preregistration_refs": [],
                    "counterevidence_refs": [],
                    "negative_control_plan_refs": [],
                    "leakage_plan_refs": [],
                    "independent_replication_refs": [],
                    "negative_control_result_refs": [],
                    "doctrine_gate_refs": [],
                    "discriminator_evaluation_refs": [],
                    "holdout_protocol_refs": [],
                    "support_only_exclusion_refs": [],
                },
                "state_history": [
                    {
                        "transition_id": "IMPORT:OD_C",
                        "from_status": None,
                        "to_status": "RETIRED",
                        "mode": "IMPORT",
                        "occurred_at": "2026-09-26T00:00:00Z",
                        "actor_ref": "TEST",
                        "reason": "fixture",
                        "evidence_refs": ["FIXTURE"],
                        "record_fingerprint_before": None,
                        "record_fingerprint_after": None,
                    }
                ],
            },
        ],
    }


class TestPromotionReporting(unittest.TestCase):

    def test_reporting_is_methodological_only(self):
        report = build_promotion_reporting(registry=registry_fixture())

        self.assertEqual(
            report["epistemic_role"],
            "METHODOLOGICAL_STATUS_ONLY",
        )
        self.assertTrue(report["methodological_status_only"])
        self.assertFalse(report["ontological_inference_allowed"])
        self.assertFalse(report["case_classification_mutated"])
        self.assertFalse(report["irc_mutated"])

        for record in report["records"]:
            self.assertEqual(record["ontological_weight"], 0)
            self.assertFalse(record["can_change_case_classification"])
            self.assertFalse(record["can_raise_irc"])

    def test_exploratory_reports_next_gate_without_promoting(self):
        report = build_promotion_reporting(registry=registry_fixture())
        record = next(
            item for item in report["records"]
            if item["discriminator_id"] == "OD_A"
        )

        self.assertEqual(record["current_status"], "EXPLORATORY")
        self.assertEqual(record["next_mainline_status"], "REPRODUCIBLE")
        self.assertFalse(record["l3_authorized"])
        self.assertFalse(record["l3_gate_complete"])
        self.assertEqual(
            set(record["next_stage_missing_requirements"]),
            {"reproducibility_refs", "synthetic_test_refs"},
        )
        self.assertIn(
            "implementation_refs",
            {
                item["requirement_id"]
                for item in record["next_stage_requirements"]
                if item["satisfied"]
            },
        )

    def test_blocked_and_retired_are_explicit(self):
        report = build_promotion_reporting(registry=registry_fixture())
        by_id = {item["discriminator_id"]: item for item in report["records"]}

        blocked = by_id["OD_B"]
        self.assertTrue(blocked["blocked"])
        self.assertFalse(blocked["terminal"])
        self.assertEqual(blocked["last_active_status"], "EXPLORATORY")
        self.assertIsNone(blocked["next_mainline_status"])
        self.assertEqual(
            blocked["block_reason"],
            "No existe observable independiente.",
        )

        retired = by_id["OD_C"]
        self.assertTrue(retired["terminal"])
        self.assertFalse(retired["blocked"])
        self.assertIsNone(retired["next_mainline_status"])

    def test_history_is_preserved_as_reporting_trace(self):
        report = build_promotion_reporting(registry=registry_fixture())
        record = report["records"][0]

        self.assertEqual(record["history_count"], 1)
        self.assertEqual(record["history"][0]["mode"], "IMPORT")
        self.assertEqual(
            record["history"][0]["evidence_refs"],
            ["FIXTURE"],
        )

    def test_reporting_does_not_mutate_registry(self):
        registry = registry_fixture()
        before = copy.deepcopy(registry)

        build_promotion_reporting(registry=registry)

        self.assertEqual(registry, before)

    def test_packaged_reporting_includes_source_genealogy(self):
        report = build_promotion_reporting()
        genealogy = report["source_genealogy"]

        self.assertIsInstance(genealogy, dict)
        self.assertTrue(genealogy["methodological_provenance_only"])
        self.assertFalse(genealogy["ontological_inference_allowed"])
        self.assertFalse(genealogy["source_count_adds_weight"])
        self.assertFalse(
            genealogy["source_priority_adds_ontological_weight"]
        )
        self.assertEqual(len(genealogy["records"]), 7)
        self.assertTrue(
            all(
                record["can_change_case_classification"] is False
                for record in genealogy["records"]
            )
        )

    def test_custom_registry_does_not_mix_canonical_genealogy(self):
        report = build_promotion_reporting(registry=registry_fixture())
        self.assertIsNone(report["source_genealogy"])

    def test_packaged_registry_reports_no_l3(self):
        report = build_promotion_reporting()

        self.assertEqual(report["validated_discriminator_ids"], [])
        self.assertEqual(
            report["summary_counts"]["VALIDATED_DISCRIMINATOR"],
            0,
        )
        self.assertTrue(
            all(
                record["l3_authorized"] is False
                for record in report["records"]
            )
        )


if __name__ == "__main__":
    unittest.main()
