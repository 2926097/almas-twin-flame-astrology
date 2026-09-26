import copy
import json
import unittest
from pathlib import Path

from almas_tfa.module_contract import ModuleContext
from almas_tfa.ontological_discriminator import discriminate_ontology
from almas_tfa.report_gate_handlers import m30_report_gate
from almas_tfa.report_model_handlers import m31_report


ROOT = Path(__file__).resolve().parents[1]


def ctx(module_id, raw=None, canonical=None, prior=None):
    return ModuleContext(
        module_id=module_id,
        module_name=module_id,
        mode="FULL",
        raw_input=raw or {},
        canonical_snapshot=canonical or {},
        prior_results=prior or {},
    )


def ontology_output():
    return discriminate_ontology(
        [
            {
                "discriminator_id": "TEST_L3",
                "promotion_ref": "PROMO:TEST_L3:1",
                "pair": ["SOULMATE_MODEL", "MONADIC_ORIGIN"],
                "validation_level": "L3_VALIDATED",
                "result": "SEPARATES",
                "excluded_model": "SOULMATE_MODEL",
                "root_key": "TEST_L3:ROOT_1",
            }
        ]
    )


def canonical_analysis():
    return {
        "schema_version": "1.0.0",
        "analysis_mode": "FULL",
        "evidence": [{"evidence_id": "E1"}],
        "models": {
            "AF": {"iem": 80, "state": "COMPATIBLE"},
            "KA": {"iem": 70, "state": "COMPATIBLE"},
            "AG": {"iem": 82, "state": "COMPATIBLE"},
            "LG": {"iem": 79, "state": "INSUFFICIENT"},
        },
        "indices": {
            "IDD": 35,
            "IAT": None,
            "ICC": 90,
            "IRC": 80,
            "ICE": 5,
        },
        "coverage": {"ICC": 90},
        "robustness": {"IRC": 80},
        "counterevidence": [],
        "ontology": {},
        "ontological_discrimination": ontology_output(),
        "doctrine": [],
        "temporal": {},
        "limitations": [],
    }


class TestCanonicalOntologicalReporting(unittest.TestCase):

    def test_canonical_schema_references_ontological_output(self):
        schema = json.loads(
            (ROOT / "schemas/canonical-analysis.schema.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(
            schema["properties"]["ontological_discrimination"]["$ref"],
            "ontological-discriminator-output.schema.json",
        )

    def test_m30_accepts_consistent_ontological_discrimination(self):
        canonical = canonical_analysis()
        result = m30_report_gate(
            ctx("M30", {"canonical_analysis": canonical})
        )
        gate = result.canonical_updates["report_gate"]

        self.assertTrue(gate["reportable"])
        self.assertNotEqual(gate["state"], "BLOCKED")
        self.assertNotIn(
            "ONTOLOGY_CLASSIFICATION_INCONSISTENT",
            gate["blocking_issues"],
        )

    def test_m30_blocks_false_specificity(self):
        canonical = canonical_analysis()
        malformed = copy.deepcopy(canonical["ontological_discrimination"])
        malformed["classification"] = "TWIN_FLAME_MODEL"
        canonical["ontological_discrimination"] = malformed

        result = m30_report_gate(
            ctx("M30", {"canonical_analysis": canonical})
        )
        gate = result.canonical_updates["report_gate"]

        self.assertEqual(gate["state"], "BLOCKED")
        self.assertIn(
            "ONTOLOGY_CLASSIFICATION_INCONSISTENT",
            gate["blocking_issues"],
        )

    def test_m31_exposes_ontology_and_promotion_trace_paths(self):
        canonical = canonical_analysis()
        gate_result = m30_report_gate(
            ctx("M30", {"canonical_analysis": canonical})
        )
        snapshot = dict(gate_result.canonical_updates)

        report_result = m31_report(
            ctx("M31", canonical=snapshot)
        )
        model = report_result.canonical_updates["report_document_model"]
        sections = {
            section["section_id"]: section for section in model["sections"]
        }

        for section_id in (
            "S01_SYNTHESIS",
            "S03_NUMERIC_ONTOLOGY",
            "S06_DIFFERENTIAL",
            "S10_FINAL_SYNTHESIS",
        ):
            self.assertIn(
                "ontological_discrimination",
                sections[section_id]["available_paths"],
            )

        for section_id in ("S08_ROBUSTNESS", "S11_SOURCES_APPENDICES"):
            self.assertIn(
                "ontological_discrimination.promotion_trace",
                sections[section_id]["available_paths"],
            )

        self.assertFalse(model["canonical_values_embedded"])
        self.assertFalse(model["canonical_values_mutated"])


if __name__ == "__main__":
    unittest.main()
