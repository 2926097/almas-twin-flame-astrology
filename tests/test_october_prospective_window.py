"""Paso 14: ventana futura sin resultado relacional predeterminado."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = json.loads((ROOT / "reference/october-2026-prospective-window.json").read_text())
SCHEMA = json.loads((ROOT / "schemas/october-prospective-window.schema.json").read_text())


class OctoberProspectiveWindowTests(unittest.TestCase):
    def test_window_layers_are_explicitly_not_run_without_source_artifacts(self):
        Draft202012Validator(SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(RECORD)
        self.assertEqual(RECORD["evaluation_status"], "NOT_EVALUABLE")
        self.assertTrue(all(layer["execution_status"] == "NOT_RUN" for layer in RECORD["requested_layers"]))
        self.assertEqual(len(RECORD["requested_layers"]), 6)

    def test_no_meeting_or_reunion_is_predicted_or_used_to_assign_phase(self):
        self.assertIsNone(RECORD["predicted_outcome"])
        self.assertFalse(RECORD["meeting_or_reunion_predeclared"])
        self.assertFalse(RECORD["phase_assignment_from_astrology"])
        self.assertEqual(RECORD["causal_status"], "UNESTABLISHED")
        self.assertEqual(RECORD["ontology_status"], "INSUFFICIENT")

if __name__ == "__main__":
    unittest.main()
