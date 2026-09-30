from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]


class PhaseCompletionGateTests(unittest.TestCase):
    def test_prospective_evaluation_waits_for_observation_date(self):
        record = json.loads((ROOT / "reference/prospective-evaluation-protocol-2027-03-29.json").read_text())
        schema = json.loads((ROOT / "schemas/prospective-evaluation-protocol.schema.json").read_text())
        validate(record, schema)
        self.assertEqual(record["status"], "WAITING_FOR_OBSERVATION")
        self.assertEqual(record["evaluation_not_before"], "2027-03-30")
        self.assertFalse(record["comparison_rules"]["retrospective_domain_addition_allowed"])
        self.assertFalse(record["comparison_rules"]["relationship_outcome_inferred"])

    def test_quantitative_review_defers_all_index_changes(self):
        record = json.loads((ROOT / "reference/quantitative-phase-review-decision.json").read_text())
        self.assertEqual(record["scores_added"], [])
        self.assertFalse(record["weights_changed"])
        self.assertFalse(record["thresholds_changed"])
        self.assertFalse(record["existing_indices_modified"])

    def test_ipt_has_no_formula_or_score_before_validation(self):
        record = json.loads((ROOT / "reference/ipt-validation-gate.json").read_text())
        self.assertFalse(record["components_defined"])
        self.assertFalse(record["formula_defined"])
        self.assertFalse(record["score_created"])
        self.assertEqual(record["status"], "NOT_IMPLEMENTED_VALIDATION_NOT_DEMONSTRATED")

    def test_release_audit_records_gates_without_claiming_prospective_validation(self):
        root = ROOT
        matrix = json.loads((root / "reference/dynamic-phase-regression-matrix-1.22.0.json").read_text())
        audit = json.loads((root / "reference/phase-final-audit-1.22.0.json").read_text())
        readiness = json.loads((root / "reference/release-readiness-1.22.0.json").read_text())
        self.assertEqual(matrix["suite_result"]["status"], "PASS")
        self.assertEqual(matrix["suite_result"]["tests_run"], 700)
        for area in matrix["coverage"]:
            for test_file in area["test_files"]:
                self.assertTrue((root / test_file).is_file(), test_file)
        self.assertEqual(audit["prospective_validation"]["status"], "PENDING_FUTURE_OBSERVATION")
        self.assertEqual(readiness["status"], "CANDIDATE_BLOCKED_PENDING_PROSPECTIVE_EVALUATION")
        self.assertFalse(readiness["release_published"])


if __name__ == "__main__":
    unittest.main()
