"""Synthetic tests for the biographical awakening policy (Step 7)."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, ValidationError
from almas_tfa.awakening_assessment import CRITERIA, assess_awakening

ROOT = Path(__file__).resolve().parents[1]
IN_SCHEMA = json.loads((ROOT / "schemas/awakening-assessment.schema.json").read_text())
OUT_SCHEMA = json.loads((ROOT / "schemas/awakening-assessment-result.schema.json").read_text())
IN_VALIDATOR = Draft202012Validator(IN_SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER)
OUT_VALIDATOR = Draft202012Validator(OUT_SCHEMA)


def full_assessment():
    value = {"criteria": {name: {"state": "SUPPORTED", "evidence_refs": ["E-" + name]} for name in CRITERIA}, "counterevidence": []}
    value["criteria"]["sustained_behavioral_change"]["observations"] = [
        {"fact_id": "F1", "actor": "A", "occurred_on": "2026-01-01", "behavior_changed": True},
        {"fact_id": "F2", "actor": "A", "occurred_on": "2026-02-01", "behavior_changed": True},
    ]
    return value


class AwakeningAssessmentTests(unittest.TestCase):
    def test_all_biographical_criteria_and_sustained_change_support(self):
        value = full_assessment()
        IN_VALIDATOR.validate(value)
        result = assess_awakening("A", value)
        OUT_VALIDATOR.validate(result)
        self.assertEqual(result["status"], "SUPPORTED")
        self.assertFalse(result["astrology_established_awakening"])

    def test_missing_or_short_duration_keeps_sustained_change_unavailable(self):
        value = full_assessment()
        value["criteria"]["sustained_behavioral_change"]["observations"][1]["occurred_on"] = "2026-01-20"
        result = assess_awakening("A", value)
        self.assertEqual(result["status"], "INSUFFICIENT")
        self.assertEqual(result["criteria"]["sustained_behavioral_change"]["state"], "NOT_EVALUABLE")

    def test_other_actor_observations_do_not_establish_subject_change(self):
        value = full_assessment()
        for observation in value["criteria"]["sustained_behavioral_change"]["observations"]:
            observation["actor"] = "B"
        self.assertEqual(assess_awakening("A", value)["status"], "INSUFFICIENT")

    def test_any_contradiction_or_counterevidence_blocks_supported(self):
        value = full_assessment()
        value["criteria"]["voluntary_reengagement"] = {"state": "CONTRADICTED", "evidence_refs": ["X1"]}
        self.assertEqual(assess_awakening("A", value)["status"], "CONTRADICTED")
        value = full_assessment()
        value["counterevidence"] = [{"kind": "SYNTHETIC-CONTRARY", "evidence_refs": ["X2"]}]
        self.assertEqual(assess_awakening("A", value)["status"], "CONTRADICTED")

    def test_supported_criterion_requires_evidence(self):
        value = full_assessment()
        value["criteria"]["explicit_reframing"]["evidence_refs"] = []
        with self.assertRaises(ValueError):
            assess_awakening("A", value)

    def test_astrology_fields_are_rejected_by_closed_input_schema(self):
        value = full_assessment()
        value["transit"] = {"event": "awakening"}
        with self.assertRaises(ValidationError):
            IN_VALIDATOR.validate(value)

    def test_duplicate_observation_refs_fail_closed(self):
        value = full_assessment()
        value["criteria"]["sustained_behavioral_change"]["observations"][1]["fact_id"] = "F1"
        with self.assertRaises(ValueError):
            assess_awakening("A", value)

if __name__ == "__main__":
    unittest.main()
