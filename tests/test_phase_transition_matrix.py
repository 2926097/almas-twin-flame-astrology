"""Paso 17: trazabilidad de cada transición y límites de cada evidencia."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from almas_tfa.phase_transition_matrix import LAYER_NAMES, build_phase_transition_matrix

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/"schemas/phase-transition-evidence-matrix.schema.json").read_text())

def layers(**overrides):
    result={name:{"status":"NOT_EVALUABLE","evidence_refs":[],"rationale":"Sin evidencia en esta fuente."} for name in LAYER_NAMES}
    for name,item in overrides.items(): result[name]=item
    return result

class PhaseTransitionMatrixTests(unittest.TestCase):
    def build(self, data, unresolved=None):
        result=build_phase_transition_matrix("T1","crisis_mirror","boundary_assertion","Se propone revisar el posible paso a un límite observable.",data,unresolved)
        Draft202012Validator(SCHEMA).validate(result)
        return result

    def test_each_category_is_present_and_documentary_support_is_traceable(self):
        result=self.build(layers(documentary={"status":"SUPPORTED","evidence_refs":["D1"],"rationale":"Declaración fechada atribuible al actor."}))
        self.assertEqual(set(LAYER_NAMES),{k for k in result if k in LAYER_NAMES})
        self.assertEqual(result["final_status"],"SUPPORTED")
        self.assertEqual(result["documentary"]["evidence_refs"],["D1"])

    def test_astrology_or_doctrine_alone_cannot_support_transition(self):
        result=self.build(layers(astrological_temporal={"status":"SUPPORTED","evidence_refs":["A1"],"rationale":"Señal temporal disponible."},doctrinal={"status":"COMPATIBLE","evidence_refs":["C1"],"rationale":"Modelo doctrinal registrado."}))
        self.assertEqual(result["final_status"],"INSUFFICIENT")
        self.assertFalse(result["astrology_or_doctrine_promoted_factual_transition"])

    def test_supported_counterevidence_contradicts_transition(self):
        result=self.build(layers(documentary={"status":"SUPPORTED","evidence_refs":["D1"],"rationale":"Hecho inicial."},counterevidence={"status":"SUPPORTED","evidence_refs":["C1"],"rationale":"Hecho contrario posterior."}))
        self.assertEqual(result["final_status"],"CONTRADICTED")

    def test_no_evidence_is_not_evaluable_and_unresolved_is_insufficient(self):
        self.assertEqual(self.build(layers())["final_status"],"NOT_EVALUABLE")
        self.assertEqual(self.build(layers(),["Cronología documental incompleta."])["final_status"],"INSUFFICIENT")

    def test_supported_without_reference_and_missing_layer_are_rejected(self):
        invalid=layers(documentary={"status":"SUPPORTED","evidence_refs":[],"rationale":"Falta fuente."})
        with self.assertRaises(ValueError): self.build(invalid)
        invalid=layers(); del invalid["doctrinal"]
        with self.assertRaises(ValueError): self.build(invalid)

if __name__=="__main__": unittest.main()
