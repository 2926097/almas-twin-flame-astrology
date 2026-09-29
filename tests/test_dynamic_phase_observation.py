"""Pruebas del firewall dato descriptivo / lectura doctrinal (Paso 4)."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError
from almas_tfa.dynamic_phase_observation import validate_phase_observation_record


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "dynamic-phase-observation.schema.json").read_text(encoding="utf-8"))
EXAMPLE = json.loads((ROOT / "examples" / "dynamic-phase-observation.synthetic.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER)


class DynamicPhaseObservationTests(unittest.TestCase):
    def test_synthetic_example_validates(self):
        VALIDATOR.validate(EXAMPLE)
        validate_phase_observation_record(EXAMPLE)

    def test_doctrinal_mapping_does_not_replace_observed_state_or_facts(self):
        self.assertEqual(EXAMPLE["observed_facts"][0]["fact_id"], "FACT-001")
        self.assertEqual(EXAMPLE["observed_state"]["phase_id"], "boundary_assertion")
        self.assertEqual(EXAMPLE["observed_state"]["evidence_refs"], ["FACT-001"])
        self.assertEqual(EXAMPLE["doctrinal_mapping"]["provenance_class"], "D_CONTEMPORARY_USE")
        self.assertEqual(EXAMPLE["doctrinal_status"], "COMPATIBLE")

    def test_state_without_fact_reference_is_rejected(self):
        value = deepcopy(EXAMPLE)
        value["observed_state"]["evidence_refs"] = []
        with self.assertRaises(ValidationError):
            VALIDATOR.validate(value)

    def test_mapping_cannot_be_used_as_observed_evidence(self):
        value = deepcopy(EXAMPLE)
        value["observed_state"]["evidence_refs"] = ["TF_DF_DM_SURRENDER_ANALOGY"]
        VALIDATOR.validate(value)
        with self.assertRaises(ValueError):
            validate_phase_observation_record(value)
        value["observed_state"]["evidence_refs"] = []
        with self.assertRaises(ValidationError):
            VALIDATOR.validate(value)

    def test_no_mapping_requires_doctrinal_status_not_evaluable(self):
        value = deepcopy(EXAMPLE)
        value["doctrinal_mapping"] = None
        value["doctrinal_status"] = "COMPATIBLE"
        with self.assertRaises(ValidationError):
            VALIDATOR.validate(value)
        value["doctrinal_status"] = "NOT_EVALUABLE"
        VALIDATOR.validate(value)

    def test_mapping_requires_provenance_and_sources(self):
        value = deepcopy(EXAMPLE)
        del value["doctrinal_mapping"]["source_refs"]
        with self.assertRaises(ValidationError):
            VALIDATOR.validate(value)

    def test_unknown_fields_are_rejected(self):
        value = deepcopy(EXAMPLE)
        value["doctrinal_mapping"]["caused_by"] = "observed_state"
        with self.assertRaises(ValidationError):
            VALIDATOR.validate(value)


if __name__ == "__main__":
    unittest.main()
