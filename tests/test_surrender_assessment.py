"""Synthetic tests for operational surrender (implementation plan Step 6)."""
from __future__ import annotations
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, ValidationError
from almas_tfa.surrender_assessment import assess_surrender

ROOT = Path(__file__).resolve().parents[1]
IN_SCHEMA = json.loads((ROOT / "schemas/surrender-assessment.schema.json").read_text())
OUT_SCHEMA = json.loads((ROOT / "schemas/surrender-assessment-result.schema.json").read_text())
IN_VALIDATOR = Draft202012Validator(IN_SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER)
OUT_VALIDATOR = Draft202012Validator(OUT_SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER)


def assessment(**overrides):
    value = {
        "assessment_start": "2026-01-01", "assessment_end": "2026-02-01",
        "preregistration_ref": "SYNTH-PREREG-1",
        "pursuit_ledger": {"prior_pursuit_attempt_refs": ["P1", "P2"],
          "post_window_pursuit_refs": [], "contact_opportunity_refs": ["O1"], "contact_log_complete": True},
        "boundary_assertion_refs": ["B1"],
        "decentering_activities": [
          {"fact_id": "D1", "actor": "A", "domain": "WORK", "occurred_on": "2026-01-01", "independent_of_other_actor_response": True},
          {"fact_id": "D2", "actor": "A", "domain": "HEALTH", "occurred_on": "2026-02-01", "independent_of_other_actor_response": True}],
        "counterevidence": []}
    value.update(overrides)
    return value


class SurrenderAssessmentTests(unittest.TestCase):
    def test_all_three_components_and_preregistration_support_stabilized(self):
        value = assessment()
        IN_VALIDATOR.validate(value)
        result = assess_surrender("A", value)
        OUT_VALIDATOR.validate(result)
        self.assertEqual(result["candidate"]["status"], "COMPATIBLE")
        self.assertEqual(result["stabilized"]["status"], "SUPPORTED")
        self.assertFalse(result["metaphysical_claim"])

    def test_candidate_requires_two_components_including_boundary_or_decentering(self):
        value = assessment(decentering_activities=[])
        result = assess_surrender("A", value)
        self.assertEqual(result["candidate"]["status"], "COMPATIBLE")
        value["boundary_assertion_refs"] = []
        self.assertEqual(assess_surrender("A", value)["candidate"]["status"], "INSUFFICIENT")

    def test_silence_alone_and_incomplete_contact_log_do_not_support_cessation(self):
        value = assessment(boundary_assertion_refs=[], decentering_activities=[],
          pursuit_ledger={"contact_log_complete": False})
        result = assess_surrender("A", value)
        self.assertEqual(result["components"]["cessation_of_pursuit"]["state"], "NOT_EVALUABLE")
        self.assertEqual(result["candidate"]["status"], "NOT_EVALUABLE")

    def test_post_window_pursuit_is_counterevidence_to_cessation(self):
        value = assessment(pursuit_ledger={"prior_pursuit_attempt_refs": ["P1", "P2"],
          "post_window_pursuit_refs": ["P3"], "contact_opportunity_refs": ["O1"], "contact_log_complete": True})
        result = assess_surrender("A", value)
        self.assertEqual(result["components"]["cessation_of_pursuit"]["state"], "ABSENT")
        self.assertEqual(result["stabilized"]["status"], "INSUFFICIENT")

    def test_window_below_30_days_and_missing_preregistration_prevent_stability(self):
        value = assessment(assessment_end="2026-01-20")
        self.assertEqual(assess_surrender("A", value)["stabilized"]["status"], "INSUFFICIENT")
        value = assessment(preregistration_ref="")
        self.assertEqual(assess_surrender("A", value)["stabilized"]["status"], "INSUFFICIENT")

    def test_activity_from_other_actor_or_response_dependent_does_not_count(self):
        value = assessment(decentering_activities=[
          {"fact_id": "D1", "actor": "A", "domain": "WORK", "occurred_on": "2026-01-01", "independent_of_other_actor_response": True},
          {"fact_id": "D2", "actor": "B", "domain": "HEALTH", "occurred_on": "2026-02-01", "independent_of_other_actor_response": True}])
        self.assertEqual(assess_surrender("A", value)["components"]["behavioral_decentering"]["state"], "NOT_EVALUABLE")

    def test_control_counterevidence_blocks_candidate_and_stability(self):
        value = assessment(counterevidence=[{"kind": "CONTROL_ATTEMPT", "evidence_refs": ["C1"]}])
        result = assess_surrender("A", value)
        self.assertEqual(result["candidate"]["status"], "CONTRADICTED")
        self.assertEqual(result["stabilized"]["status"], "CONTRADICTED")

    def test_strategic_silence_requires_explicit_actor_self_report(self):
        value = assessment(counterevidence=[{"kind": "EXPLICIT_STRATEGIC_SILENCE_TO_PROVOKE_RESPONSE", "evidence_refs": ["C1"]}])
        with self.assertRaises(ValueError):
            assess_surrender("A", value)
        with self.assertRaises(ValidationError):
            IN_VALIDATOR.validate(value)
        value["counterevidence"][0]["actor_self_reported_intent"] = True
        self.assertEqual(assess_surrender("A", value)["candidate"]["status"], "CONTRADICTED")

    def test_unregistered_fields_and_duplicate_fact_ids_fail_closed(self):
        value = assessment(astrology_interpretation="awakening")
        with self.assertRaises(ValidationError):
            IN_VALIDATOR.validate(value)
        value = assessment()
        value["decentering_activities"][1]["fact_id"] = "D1"
        with self.assertRaises(ValueError):
            assess_surrender("A", value)

    def test_invalid_actor_and_reversed_window_rejected(self):
        with self.assertRaises(ValueError):
            assess_surrender("RELATIONSHIP", assessment())
        with self.assertRaises(ValueError):
            assess_surrender("A", assessment(assessment_start="2026-02-01", assessment_end="2026-01-01"))

if __name__ == "__main__":
    unittest.main()
