"""Paso 12: el protocolo congelado precede cualquier aplicación de caso."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, ValidationError
from almas_tfa.phase_preregistration import verify_phase_preregistration

ROOT = Path(__file__).resolve().parents[1]
RECORD = json.loads((ROOT / "reference/phase-preregistration-1.22.0.json").read_text())
SCHEMA = json.loads((ROOT / "schemas/phase-preregistration.schema.json").read_text())


class PhasePreregistrationTests(unittest.TestCase):
    def test_registered_policies_validate_and_fingerprints_match(self):
        Draft202012Validator(SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(RECORD)
        result = verify_phase_preregistration(RECORD, ROOT)
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(len(result["verified_artifacts"]), 4)
        self.assertFalse(result["case_data_included"])

    def test_modified_criterion_artifact_invalidates_preregistration(self):
        value = deepcopy(RECORD)
        value["frozen_artifacts"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            verify_phase_preregistration(value, ROOT)

    def test_case_specific_tuning_and_embedded_case_data_are_forbidden(self):
        for key in ("case_specific_tuning", "case_data_included"):
            value = deepcopy(RECORD)
            value[key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(SCHEMA).validate(value)
            with self.assertRaises(ValueError):
                verify_phase_preregistration(value, ROOT)

    def test_causal_and_sequence_rules_cannot_be_weakened(self):
        value = deepcopy(RECORD)
        value["sequence_rules"]["causal_status"] = "SUPPORTED"
        with self.assertRaises(ValidationError):
            Draft202012Validator(SCHEMA).validate(value)
        with self.assertRaises(ValueError):
            verify_phase_preregistration(value, ROOT)

    def test_missing_required_policy_cannot_be_silently_omitted(self):
        value = deepcopy(RECORD)
        value["frozen_artifacts"].pop()
        with self.assertRaises(ValueError):
            verify_phase_preregistration(value, ROOT)

if __name__ == "__main__":
    unittest.main()
