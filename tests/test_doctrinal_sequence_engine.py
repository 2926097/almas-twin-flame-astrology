"""Synthetic tests for sequence and causal firewall (Step 9)."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, ValidationError
from almas_tfa.doctrinal_sequence_engine import evaluate_doctrinal_sequence

ROOT = Path(__file__).resolve().parents[1]
IN_SCHEMA = json.loads((ROOT / "schemas/doctrinal-sequence-assessment.schema.json").read_text())
OUT_SCHEMA = json.loads((ROOT / "schemas/doctrinal-sequence-result.schema.json").read_text())
IN_VALIDATOR = Draft202012Validator(IN_SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER)
OUT_VALIDATOR = Draft202012Validator(OUT_SCHEMA)


def obs(phase, day, ref):
    return {"phase_id": phase, "occurred_at": f"2026-01-{day:02d}T10:00:00Z", "evidence_refs": [ref]}


class DoctrinalSequenceEngineTests(unittest.TestCase):
    def test_temporal_precedence_and_sequence_match_never_establish_causality(self):
        events = [obs("recognition", 1, "F1"), obs("crisis_mirror", 2, "F2"), obs("pursuit_withdrawal", 3, "F3"), obs("surrender_stabilized", 4, "F4"), obs("awakening_candidate", 5, "F5"), obs("reunion", 6, "F6")]
        value = {"model_id": "TF_RUNNER_CHASER", "observations": events}
        IN_VALIDATOR.validate(value)
        result = evaluate_doctrinal_sequence(**value)
        OUT_VALIDATOR.validate(result)
        self.assertEqual(result["temporal_precedence"]["status"], "BEFORE")
        self.assertEqual(result["sequence_match"], "MATCH")
        self.assertEqual(result["doctrinal_compatibility"], "COMPATIBLE")
        self.assertEqual(result["causal_status"], "UNESTABLISHED")
        self.assertNotIn("caused_by", result)

    def test_reverse_order_is_temporal_fact_not_causal_explanation(self):
        result = evaluate_doctrinal_sequence("TF_DF_DM_SURRENDER", [obs("awakening_candidate", 3, "A1"), obs("surrender_stabilized", 4, "S1")])
        self.assertEqual(result["temporal_precedence"]["status"], "AFTER")
        self.assertEqual(result["causal_status"], "UNESTABLISHED")

    def test_unordered_sequence_mismatch_and_missing_phase_insufficient(self):
        wrong = [obs("crisis_mirror", 1, "F1"), obs("recognition", 2, "F2"), obs("pursuit_withdrawal", 3, "F3"), obs("surrender_stabilized", 4, "F4"), obs("reunion", 5, "F5")]
        result = evaluate_doctrinal_sequence("TF_RUNNER_CHASER", wrong)
        self.assertEqual(result["sequence_match"], "MISMATCH")
        self.assertEqual(result["doctrinal_compatibility"], "INCOMPATIBLE")
        result = evaluate_doctrinal_sequence("TF_RUNNER_CHASER", [obs("recognition", 1, "F1")])
        self.assertEqual(result["sequence_match"], "INCOMPLETE")
        self.assertEqual(result["doctrinal_compatibility"], "INSUFFICIENT")

    def test_no_source_defined_sequence_is_not_evaluable(self):
        result = evaluate_doctrinal_sequence("TF_PROPHET", [obs("recognition", 1, "F1")])
        self.assertEqual(result["sequence_match"], "NOT_EVALUABLE")
        self.assertEqual(result["doctrinal_compatibility"], "NOT_EVALUABLE")
        self.assertEqual(result["causal_status"], "UNESTABLISHED")

    def test_missing_refs_unknown_model_and_unregistered_astrology_field_rejected(self):
        with self.assertRaises(ValidationError):
            IN_VALIDATOR.validate({"model_id": "TF_RUNNER_CHASER", "observations": [{"phase_id": "recognition", "occurred_at": "2026-01-01T00:00:00Z", "evidence_refs": []}]})
        with self.assertRaises(ValueError):
            evaluate_doctrinal_sequence("UNKNOWN", [])
        with self.assertRaises(ValidationError):
            IN_VALIDATOR.validate({"model_id": "TF_RUNNER_CHASER", "observations": [], "transits": []})

    def test_timezone_offsets_are_compared_as_instants(self):
        events = [
          {"phase_id": "surrender_stabilized", "occurred_at": "2026-01-01T10:00:00+02:00", "evidence_refs": ["S1"]},
          {"phase_id": "awakening_candidate", "occurred_at": "2026-01-01T09:00:00Z", "evidence_refs": ["A1"]}]
        result = evaluate_doctrinal_sequence("TF_DF_DM_SURRENDER", events)
        self.assertEqual(result["temporal_precedence"]["status"], "BEFORE")

if __name__ == "__main__":
    unittest.main()
