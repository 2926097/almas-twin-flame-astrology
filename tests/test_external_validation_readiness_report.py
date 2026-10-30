"""Pruebas sintéticas del preflight de cohorte; ningún caso real se publica."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from report_external_validation_readiness import (  # noqa: E402
    audit_external_readiness,
    load_manifests,
)


class ExternalReadinessCrossManifestTests(unittest.TestCase):
    def setUp(self):
        self.data = load_manifests(ROOT)

    def test_current_public_baseline_is_consistent_but_not_ready(self):
        out = audit_external_readiness(self.data)
        self.assertEqual(out["status"], "NOT_READY")
        self.assertEqual(out["rra_unresolved_requirements"], 7)
        self.assertEqual(set(out["declared_counts"].values()), {0})
        self.assertEqual(out["violations"], [])
        self.assertFalse(out["confirmatory_execution_authorized"])
        self.assertFalse(out["metaphysical_hypotheses_evaluable"])

    def test_report_is_deterministic_and_inputs_are_untouched(self):
        before = deepcopy(self.data)
        first = audit_external_readiness(self.data)
        self.assertEqual(first, audit_external_readiness(self.data))
        self.assertEqual(before, self.data)

    def test_declared_holdout_is_not_auto_admitted(self):
        data = deepcopy(self.data)
        data["public_holdouts"]["artifacts"] = [{"opaque_test_id": "SYNTHETIC"}]
        out = audit_external_readiness(data)
        self.assertEqual(out["status"], "REVIEW_REQUIRED")
        self.assertEqual(out["declared_counts"]["public_holdout_artifacts"], 1)
        self.assertFalse(out["independent_provenance_verified"])
        self.assertFalse(out["confirmatory_execution_authorized"])

    def test_declared_dyad_is_not_metaphysical_truth(self):
        data = deepcopy(self.data)
        data["pair_identity"]["real_cohorts"] = [{"synthetic": True}]
        out = audit_external_readiness(data)
        self.assertEqual(out["status"], "REVIEW_REQUIRED")
        self.assertFalse(out["metaphysical_hypotheses_evaluable"])
        self.assertFalse(out["empirical_utility_validated"])

    def test_forced_confirmatory_rra_execution_fails_closed(self):
        data = deepcopy(self.data)
        data["rra"]["confirmatory_execution_allowed"] = True
        out = audit_external_readiness(data)
        self.assertEqual(out["status"], "CONTRACT_VIOLATION")
        self.assertIn("RRA_CONFIRMATORY_EXECUTION_NOT_BLOCKED", out["violations"])
        self.assertFalse(out["confirmatory_execution_authorized"])

    def test_forged_l3_and_metaphysical_ground_truth_fail_closed(self):
        data = deepcopy(self.data)
        data["pair_identity"]["l3_validated_discriminator_present"] = True
        data["pair_identity"]["metaphysical_ground_truth"] = True
        out = audit_external_readiness(data)
        self.assertIn("UNVERIFIED_L3_PROMOTION", out["violations"])
        self.assertIn("METAPHYSICAL_GROUND_TRUTH_CLAIM", out["violations"])

    def test_forged_registration_and_reduced_blockers_fail_closed(self):
        data = deepcopy(self.data)
        data["rra"]["external_registration"] = "PREREG-NOT-VERIFIED"
        data["rra"]["blockers"].pop()
        out = audit_external_readiness(data)
        self.assertIn("RRA_REGISTRATION_REQUIRES_INDEPENDENT_AUDIT", out["violations"])
        self.assertIn("RRA_SEVEN_BLOCKERS_MISMATCH", out["violations"])

    def test_wrong_types_and_missing_files_are_not_pass(self):
        data = deepcopy(self.data)
        data["cohorts"]["real_cases"] = "none"
        with self.assertRaisesRegex(ValueError, "expected list"):
            audit_external_readiness(data)
        data = deepcopy(self.data)
        data["rra"]["closure_assessment"] = None
        with self.assertRaisesRegex(ValueError, "expected JSON object"):
            audit_external_readiness(data)

    def test_unexpected_status_does_not_grant_ready(self):
        data = deepcopy(self.data)
        data["cohorts"]["status"] = "FROZEN_CONFIRMATORY"
        result = audit_external_readiness(data)
        self.assertEqual(result["status"], "CONTRACT_VIOLATION")
        self.assertFalse(result["confirmatory_execution_authorized"])

    def test_report_never_contains_raw_cases(self):
        data = deepcopy(self.data)
        data["cohorts"]["real_cases"] = [{"private_label": "DO_NOT_EMIT"}]
        report = audit_external_readiness(data)
        self.assertNotIn("DO_NOT_EMIT", str(report))
        self.assertEqual(report["declared_counts"]["general_real_cases"], 1)


if __name__ == "__main__":
    unittest.main()
