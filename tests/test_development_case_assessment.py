"""Paso 13: una aplicación de desarrollo no puede reescribir criterios."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = json.loads((ROOT / "reference/development-case-assessment-2026-09-29.json").read_text())
SCHEMA = json.loads((ROOT / "schemas/development-case-assessment.schema.json").read_text())


class DevelopmentCaseAssessmentTests(unittest.TestCase):
    def test_anonymous_development_record_keeps_all_phases_not_evaluable(self):
        Draft202012Validator(SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(RECORD)
        self.assertEqual(RECORD["assessment_date"], "2026-09-29")
        self.assertEqual({item["phase_id"] for item in RECORD["phase_checks"]}, {"crisis_mirror", "boundary_assertion", "separation_or_suspension", "surrender_candidate"})
        self.assertTrue(all(item["status"] == "NOT_EVALUABLE" for item in RECORD["phase_checks"]))
        self.assertEqual(RECORD["doctrinal_sequence"]["causal_status"], "UNESTABLISHED")

    def test_public_record_contains_no_case_facts_or_case_specific_tuning(self):
        self.assertEqual(RECORD["observed_facts"], [])
        self.assertFalse(RECORD["source_artifacts_in_repository"])
        self.assertFalse(RECORD["case_specific_tuning"])
        self.assertFalse(any("José" in key or "Indira" in key for key in RECORD))

if __name__ == "__main__":
    unittest.main()
