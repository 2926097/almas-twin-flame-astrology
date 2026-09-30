"""Paso 11: casos negativos que no deben forzar una lectura twin-flame."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from almas_tfa.doctrinal_sequence_engine import evaluate_doctrinal_sequence

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "examples/negative-phase-cases.synthetic.json").read_text())
SCHEMA = json.loads((ROOT / "schemas/negative-phase-cases.schema.json").read_text())


class NegativePhaseCasesTests(unittest.TestCase):
    def test_fixture_validates_and_covers_six_required_negative_scenarios(self):
        Draft202012Validator(SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(FIXTURE)
        self.assertEqual(len(FIXTURE["cases"]), 6)
        self.assertEqual({case["case_id"] for case in FIXTURE["cases"]}, {
            "NEG_ORDINARY_BREAKUP", "NEG_GHOSTING", "NEG_DEFINITIVE_SEPARATION",
            "NEG_ORDINARY_RECONCILIATION", "NEG_CRISIS_WITHOUT_CHANGE",
            "NEG_RETURN_WITHOUT_TRANSFORMATION"})

    def test_no_negative_case_demonstrates_twin_flame_or_supports_full_runner_sequence(self):
        for case in FIXTURE["cases"]:
            result = evaluate_doctrinal_sequence("TF_RUNNER_CHASER", case["observations"])
            self.assertNotEqual(result["sequence_status"], "SEQUENCE_SUPPORTED", case["case_id"])
            self.assertEqual(result["ontology_status"], "INSUFFICIENT")
            self.assertFalse(result["twin_flame_demonstrated"])

    def test_reconciliation_and_return_do_not_imply_transformation(self):
        for case_id in ("NEG_ORDINARY_RECONCILIATION", "NEG_RETURN_WITHOUT_TRANSFORMATION"):
            case = next(item for item in FIXTURE["cases"] if item["case_id"] == case_id)
            self.assertEqual([item["phase_id"] for item in case["observations"]], ["bilateral_reengagement"])
            self.assertNotIn("awakening_candidate", [item["phase_id"] for item in case["observations"]])
            self.assertNotIn("individual_restructuring", [item["phase_id"] for item in case["observations"]])

if __name__ == "__main__":
    unittest.main()
