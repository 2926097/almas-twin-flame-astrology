from __future__ import annotations

import unittest
import json
from pathlib import Path
from jsonschema import validate

from almas_tfa.temporal_sequence_graph import build_temporal_sequence_graph


class TemporalSequenceGraphTests(unittest.TestCase):
    def test_evidence_backed_graph_preserves_order_without_causal_inference(self):
        nodes = [
            {"node_id": "E1", "kind": "EVENT", "evidence_refs": ["DOC1"]},
            {"node_id": "A1", "kind": "ACTIVATION", "evidence_refs": ["AST1"]},
            {"node_id": "R1", "kind": "ROOT", "evidence_refs": ["ROOT1"]},
            {"node_id": "P1", "kind": "PHASE", "evidence_refs": ["FACT1"]},
        ]
        edges = [
            {"source_id": "E1", "target_id": "A1", "evidence_refs": ["DOC1"]},
            {"source_id": "A1", "target_id": "R1", "evidence_refs": ["AST1"]},
            {"source_id": "R1", "target_id": "P1", "evidence_refs": ["FACT1"]},
        ]
        result = build_temporal_sequence_graph(nodes, edges)
        schema = json.loads((Path(__file__).resolve().parents[1] / "schemas/temporal-sequence-graph.schema.json").read_text())
        validate(result, schema)
        self.assertEqual(result["status"], "READY")
        self.assertEqual(len(result["edges"]), 3)
        self.assertFalse(result["missing_phases_inferred"])
        self.assertEqual(result["causal_status"], "UNESTABLISHED")

    def test_empty_graph_is_not_evaluable_and_does_not_infer_missing_nodes(self):
        result = build_temporal_sequence_graph([], [])
        self.assertEqual(result["status"], "NOT_EVALUABLE")
        self.assertEqual(result["nodes"], [])
        self.assertFalse(result["missing_phases_inferred"])

    def test_invalid_order_or_unreferenced_edge_is_rejected(self):
        nodes = [
            {"node_id": "R1", "kind": "ROOT", "evidence_refs": ["R"]},
            {"node_id": "P1", "kind": "PHASE", "evidence_refs": ["P"]},
        ]
        with self.assertRaises(ValueError):
            build_temporal_sequence_graph(nodes, [{"source_id": "P1", "target_id": "R1", "evidence_refs": ["X"]}])


if __name__ == "__main__":
    unittest.main()
