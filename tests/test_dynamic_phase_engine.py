"""Pruebas sintéticas del motor documental/conductual (Paso 5)."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError

from almas_tfa.dynamic_phase_engine import evaluate_dynamic_phase_event

ROOT = Path(__file__).resolve().parents[1]
INPUT_SCHEMA = json.loads((ROOT / "schemas" / "dynamic-phase-event.schema.json").read_text(encoding="utf-8"))
OUTPUT_SCHEMA = json.loads((ROOT / "schemas" / "dynamic-phase-event-result.schema.json").read_text(encoding="utf-8"))
IN_VALIDATOR = Draft202012Validator(INPUT_SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER)
OUT_VALIDATOR = Draft202012Validator(OUTPUT_SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER)


def fact(fact_id, actor, *, kind="DOCUMENTARY", source_ref="SYNTHETIC-RECORD"):
    return {
        "fact_id": fact_id, "kind": kind, "actor": actor,
        "description": "Hecho sintético directamente documentado.",
        "source_ref": source_ref, "occurred_at": "2026-01-12T10:00:00Z",
    }


def event(code, actor, evidence, **kwargs):
    value = {
        "schema_version": "1.0.0", "event_id": "SYNTH-EVENT-1",
        "occurred_at": "2026-01-12T10:00:00Z", "actor": actor,
        "behavior_code": code, "context": "Contexto relacional sintético.",
        "evidence": evidence, "counterevidence": [],
    }
    value.update(kwargs)
    return value


class DynamicPhaseEngineTests(unittest.TestCase):
    def test_explicit_actor_boundary_yields_supported_candidate_and_state(self):
        value = event("EXPLICIT_BOUNDARY", "A", [fact("F1", "A")])
        IN_VALIDATOR.validate(value)
        result = evaluate_dynamic_phase_event(value)
        OUT_VALIDATOR.validate(result)
        self.assertEqual(result["status"], "SUPPORTED")
        self.assertEqual(result["phase_candidate"]["phase_id"], "boundary_assertion")
        self.assertEqual(result["phase_after"]["evidence_refs"], ["F1"])
        self.assertFalse(result["automatic_text_interpretation"])

    def test_mutual_pause_requires_direct_records_from_both_actors(self):
        insufficient = event("MUTUAL_PAUSE", "BOTH", [fact("F1", "A")])
        result = evaluate_dynamic_phase_event(insufficient)
        self.assertEqual(result["status"], "INSUFFICIENT")
        self.assertIsNone(result["phase_after"])
        complete = event("MUTUAL_PAUSE", "BOTH", [fact("F1", "A"), fact("F2", "B")])
        result = evaluate_dynamic_phase_event(complete)
        self.assertEqual(result["phase_candidate"]["phase_id"], "separation_or_suspension")
        self.assertEqual(result["evidence_strength"], "DIRECT_MULTI_ACTOR")

    def test_mutual_resumption_requires_bilateral_evidence(self):
        result = evaluate_dynamic_phase_event(event(
            "MUTUAL_RESUMPTION", "BOTH", [fact("F1", "A"), fact("F2", "B")]
        ))
        self.assertEqual(result["status"], "SUPPORTED")
        self.assertEqual(result["phase_after"]["phase_id"], "bilateral_reengagement")

    def test_counterevidence_blocks_phase_after(self):
        value = event("EXPLICIT_BOUNDARY", "A", [fact("F1", "A")],
                      counterevidence=[fact("F2", "A", kind="BEHAVIORAL")])
        result = evaluate_dynamic_phase_event(value)
        self.assertEqual(result["status"], "CONTRADICTED")
        self.assertEqual(result["phase_candidate"]["status"], "CONTRADICTED")
        self.assertIsNone(result["phase_after"])

    def test_unknown_behavior_fails_closed_and_preserves_previous_state(self):
        before = {"phase_id": "recognition", "status": "COMPATIBLE", "evidence_refs": ["OLD"]}
        value = event("UNCLASSIFIED", "A", [fact("F1", "A")], phase_before=before)
        result = evaluate_dynamic_phase_event(value)
        self.assertEqual(result["status"], "NOT_EVALUABLE")
        self.assertIsNone(result["phase_candidate"])
        self.assertEqual(result["phase_after"], before)

    def test_secondary_only_evidence_cannot_support_candidate(self):
        value = event("EXPLICIT_BOUNDARY", "A", [fact("F1", "A", kind="SECONDARY_REPORT")])
        result = evaluate_dynamic_phase_event(value)
        self.assertEqual(result["status"], "INSUFFICIENT")
        self.assertEqual(result["evidence_strength"], "NO_DIRECT_EVIDENCE")

    def test_actor_rule_rejects_relationship_actor_code(self):
        value = event("EXPLICIT_BOUNDARY", "BOTH", [fact("F1", "A"), fact("F2", "B")])
        self.assertEqual(evaluate_dynamic_phase_event(value)["status"], "INSUFFICIENT")

    def test_astrology_and_doctrine_cannot_be_smuggled_into_event_schema(self):
        value = event("EXPLICIT_BOUNDARY", "A", [fact("F1", "A")])
        value["transit"] = {"meaning": "awakening"}
        with self.assertRaises(ValidationError):
            IN_VALIDATOR.validate(value)

    def test_evaluator_does_not_mutate_event(self):
        value = event("EXPLICIT_BOUNDARY", "A", [fact("F1", "A")])
        before = deepcopy(value)
        evaluate_dynamic_phase_event(value)
        self.assertEqual(value, before)


if __name__ == "__main__":
    unittest.main()
