import unittest
import json
from pathlib import Path
from jsonschema import Draft202012Validator

from almas_tfa.chiron_process import assess_chiron_process, summarize_temporal_process


def contact(a, b, variant=None):
    return {
        "point_a": a, "point_b": b, "orb": 0.2, "declared_orb": 2.0,
        "aspect": "CONJUNCTION", "aspect_policy_ref": "ASPECTS-SYNTH-1",
        "node_variant": variant,
    }


def signal(identifier, source, target, group, *, pass_number=1, preregistered=True):
    return {
        "signal_id": identifier, "technique": "TTRANSIT",
        "technique_variant": "RETURN_CYCLE", "exact_datetime": "2026-01-01T00:00:00Z",
        "source_point": source, "target_point": target, "relation": "CONJUNCTION",
        "dependency_group": group, "node_variant": "TRUE", "pass_number": pass_number,
        "preregistered": preregistered, "window_status": "RETROSPECTIVE_CONFIRMED",
    }


class ChironProcessTests(unittest.TestCase):
    def test_venus_nodal_without_chiron_is_not_promoted_to_triad(self):
        out = assess_chiron_process(natal_contacts=[contact("VENUS", "AXIS_NODES", "TRUE")])
        self.assertEqual(out["complex_type"], "VENUS_NODAL_CORE")
        self.assertEqual(out["process_state"], "LATENT_ARCHITECTURE")

    def test_venus_chiron_without_nodes_remains_pair_complex(self):
        out = assess_chiron_process(natal_contacts=[contact("VENUS", "CHIRON")])
        self.assertEqual(out["complex_type"], "VENUS_CHIRON_LINK")

    def test_genuine_natal_triad_is_one_complex_even_with_true_mean_duplicates(self):
        out = assess_chiron_process(natal_contacts=[
            contact("VENUS", "CHIRON"), contact("VENUS", "AXIS_NODES", "TRUE"),
            contact("CHIRON", "AXIS_NODES", "MEAN"),
        ])
        self.assertEqual(out["complex_type"], "VENUS_NODAL_CHIRON")
        self.assertEqual(out["natal_architecture"]["status"], "SUPPORTED")
        self.assertEqual(out["nodal_variants"]["independent_axis_count"], 1)
        self.assertFalse(out["structural_scoring_modified"])

    def test_temporal_triad_alone_does_not_create_natal_vulnerability(self):
        out = assess_chiron_process(natal_contacts=[], temporal_signals=[
            signal("S1", "VENUS", "CHIRON", "TRANSIT_EPHEMERIS"),
            signal("S2", "CHIRON", "NORTH_NODE", "SECONDARY_PROGRESSION"),
            signal("S3", "VENUS", "MEAN_NORTH_NODE", "UNIFORM_YEAR_DIRECTION"),
        ])
        self.assertEqual(out["complex_type"], "TRIADIC_TEMPORAL_BRIDGE")
        self.assertEqual(out["process_state"], "INDETERMINATE")
        self.assertEqual(out["natal_architecture"]["status"], "INSUFFICIENT")

    def test_exploratory_signal_remains_exploratory(self):
        out = assess_chiron_process(
            natal_contacts=[contact("CHIRON", "AXIS_NODES")],
            temporal_signals=[signal("ATACIR-C144", "CHIRON", "NORTH_NODE", "ATACIR_FAMILY", preregistered=False)],
        )
        self.assertEqual(out["temporal_signals"][0]["window_status"], "EXPLORATORY")
        audit = out["technique_search_audit"]
        self.assertEqual(audit["multiple_testing_context"], "UNDECLARED_SEARCH_UNIVERSE")
        self.assertFalse(audit["universe_complete"])

    def test_preregistered_search_universe_and_exploratory_set_are_preserved(self):
        out = assess_chiron_process(
            natal_contacts=[contact("VENUS", "CHIRON")],
            technique_search={
                "techniques_tested": ["TRANSIT", "C360", "SOLAR_ARC"],
                "techniques_matched": ["TRANSIT", "C360"],
                "preregistered_techniques": ["TRANSIT"],
                "exploratory_techniques": ["C360", "SOLAR_ARC"],
                "multiple_testing_context": "3 technique families reviewed",
                "selection_after_observation": True,
                "universe_complete": True,
            },
        )
        self.assertEqual(out["technique_search_audit"]["techniques_tested"], ["C360", "SOLAR_ARC", "TRANSIT"])
        self.assertTrue(out["technique_search_audit"]["selection_after_observation"])

    def test_process_vector_uses_sequence_and_never_claims_real_world_prediction(self):
        signals = [
            {**signal("A", "CHIRON", "VENUS", "TRANSIT_EPHEMERIS"), "process_marker": "TENSION", "geometry_class": "HARD", "strength": 0.8, "evidence_refs": ["E1"]},
            {**signal("B", "VENUS", "NORTH_NODE", "SEC_PROGRESSION"), "exact_datetime": "2026-02-01T00:00:00Z", "process_marker": "INTEGRATIVE", "geometry_class": "HARMONIC", "strength": 0.4, "evidence_refs": ["E2"]},
        ]
        result = summarize_temporal_process(signals)
        self.assertEqual(result["process_vector"], "REORGANIZING")
        self.assertEqual(result["integration_signature"], "MIXED")
        self.assertEqual(result["independent_dependency_group_count"], 2)
        self.assertFalse(result["probability_created"])

    def test_output_obeys_public_schema(self):
        out = assess_chiron_process(natal_contacts=[contact("VENUS", "AXIS_NODES")])
        schema = json.loads((Path(__file__).resolve().parents[1] / "schemas/chiron-process-output.schema.json").read_text())
        Draft202012Validator(schema).validate(out)

    def test_public_synthetic_example_matches_expected_state(self):
        example = json.loads((Path(__file__).resolve().parents[1] / "examples/chiron-process.synthetic.json").read_text())
        self.assertEqual(example["expected"]["complex_type"], example["output"]["complex_type"])
        self.assertEqual(example["expected"]["process_state"], example["output"]["process_state"])
        self.assertFalse(example["output"]["structural_scoring_modified"])
        self.assertFalse(example["output"]["ontological_category_created"])

    def test_integration_window_requires_two_groups_and_documented_sequence(self):
        out = assess_chiron_process(
            natal_contacts=[contact("VENUS", "AXIS_NODES")],
            temporal_signals=[
                signal("A", "VENUS", "CHIRON", "TRANSIT_EPHEMERIS"),
                signal("B", "CHIRON", "NORTH_NODE", "SECONDARY_PROGRESSION"),
            ],
            temporal_sequence={"process_vector": "REORGANIZING", "integration_signature": "MIXED", "sequence_evidence_refs": ["SEQ-1"]},
        )
        self.assertEqual(out["process_state"], "INTEGRATION_WINDOW")
        self.assertEqual(out["integration_signature"], "MIXED")

    def test_documented_integration_requires_qualified_m27_evidence(self):
        args = dict(
            natal_contacts=[contact("CHIRON", "AXIS_NODES")],
            temporal_signals=[
                signal("A", "VENUS", "CHIRON", "TRANSIT_EPHEMERIS"),
                signal("B", "CHIRON", "NORTH_NODE", "SECONDARY_PROGRESSION"),
            ],
            temporal_sequence={"process_vector": "REORGANIZING", "sequence_evidence_refs": ["SEQ-1"]},
        )
        invalid = assess_chiron_process(**args, documentary_evidence=[{"event_ref": "E1"}])
        self.assertEqual(invalid["process_state"], "INTEGRATION_WINDOW")
        valid = assess_chiron_process(**args, documentary_evidence=[{
            "module": "M27", "event_ref": "E1", "source_refs": ["SRC-1"],
            "evidence_roles": ["INTEGRATION_OUTCOME"], "documentary_quality": "DQ1_PRIMARY_DOCUMENT",
            "documentary_quality_contract_met": True, "date_precision_contract_met": True,
            "fact_interpretation_separated": True,
        }])
        self.assertEqual(valid["process_state"], "INTEGRATION_DOCUMENTED")


if __name__ == "__main__":
    unittest.main()
