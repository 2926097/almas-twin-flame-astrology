"""Paso 20: regresión por casos negativos sin forzar el modelo twin-flame."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from almas_tfa.dynamic_phase_engine import evaluate_dynamic_phase_event
from almas_tfa.doctrinal_sequence_engine import evaluate_doctrinal_sequence

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=json.loads((ROOT/"examples/negative-phase-cases.synthetic.json").read_text())
INPUT_SCHEMA=json.loads((ROOT/"schemas/dynamic-phase-event.schema.json").read_text())
OUTPUT_SCHEMA=json.loads((ROOT/"schemas/dynamic-phase-event-result.schema.json").read_text())
INPUT_VALIDATOR=Draft202012Validator(INPUT_SCHEMA,format_checker=Draft202012Validator.FORMAT_CHECKER)
OUTPUT_VALIDATOR=Draft202012Validator(OUTPUT_SCHEMA)


def fact(ref,actor):
    return {"fact_id":ref,"kind":"DOCUMENTARY","actor":actor,"description":"Hecho directo sintético.","source_ref":"SYNTHETIC-SOURCE","occurred_at":"2026-01-01T10:00:00Z"}

def event(code,actor,evidence,**extra):
    value={"schema_version":"1.0.0","event_id":"NEGATIVE-CONTROL","occurred_at":"2026-01-01T10:00:00Z","actor":actor,"behavior_code":code,"context":"Escenario negativo sintético.","evidence":evidence,"counterevidence":[]}
    value.update(extra)
    return value

class NegativeCasePhaseFirewallStep20Tests(unittest.TestCase):
    def test_complete_negative_case_set_stays_outside_supported_twin_flame_sequence(self):
        self.assertEqual(len(FIXTURE["cases"]),6)
        for case in FIXTURE["cases"]:
            result=evaluate_doctrinal_sequence("TF_RUNNER_CHASER",case["observations"])
            with self.subTest(case=case["case_id"]):
                self.assertNotEqual(result["sequence_status"],"SEQUENCE_SUPPORTED")
                self.assertEqual(result["ontology_status"],"INSUFFICIENT")
                self.assertFalse(result["twin_flame_demonstrated"])

    def test_ghosting_does_not_auto_assign_closure_surrender_or_reunion(self):
        value=event("UNCLASSIFIED","B",[],phase_before={"phase_id":"pursuit_withdrawal","status":"COMPATIBLE","evidence_refs":["OLD"]})
        INPUT_VALIDATOR.validate(value)
        result=evaluate_dynamic_phase_event(value)
        OUTPUT_VALIDATOR.validate(result)
        self.assertEqual(result["status"],"NOT_EVALUABLE")
        self.assertEqual(result["phase_after"]["phase_id"],"pursuit_withdrawal")

    def test_definitive_separation_supports_only_documented_closure(self):
        result=evaluate_dynamic_phase_event(event("EXPLICIT_TERMINATION","A",[fact("END-A","A")]))
        self.assertEqual(result["phase_after"]["phase_id"],"closure")
        self.assertNotIn("reunion",[result["phase_after"]["phase_id"]])

    def test_ordinary_reconciliation_and_return_without_change_support_only_reengagement(self):
        for scenario in ("ordinary_reconciliation","return_without_transformation"):
            result=evaluate_dynamic_phase_event(event("MUTUAL_RESUMPTION","BOTH",[fact("R-A","A"),fact("R-B","B")]))
            with self.subTest(scenario=scenario):
                self.assertEqual(result["phase_after"]["phase_id"],"bilateral_reengagement")
                self.assertNotIn("awakening_candidate",[result["phase_after"]["phase_id"]])
                self.assertNotIn("reunion",[result["phase_after"]["phase_id"]])

    def test_crisis_without_following_evidence_creates_no_automatic_transition(self):
        before={"phase_id":"crisis_mirror","status":"COMPATIBLE","evidence_refs":["CRISIS"]}
        result=evaluate_dynamic_phase_event(event("UNCLASSIFIED","B",[],phase_before=before))
        self.assertEqual(result["status"],"NOT_EVALUABLE")
        self.assertEqual(result["phase_after"],before)

if __name__=="__main__": unittest.main()
