"""Contract checks for provenance-qualified doctrinal sequence models (Step 8)."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "reference/doctrinal-sequence-models.json").read_text())
SCHEMA = json.loads((ROOT / "schemas/doctrinal-sequence-models.schema.json").read_text())
MODELS = {item["model_id"]: item for item in REGISTRY["models"]}


class DoctrinalSequenceRegistryTests(unittest.TestCase):
    def test_registry_schema_and_model_coverage(self):
        Draft202012Validator(SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(REGISTRY)
        self.assertEqual(set(MODELS), {"TF_PROPHET", "TF_RUNNER_CHASER", "TF_DF_DM_SURRENDER", "KARMIC_CATALYTIC", "JUNGIAN_INDIVIDUATION_ANALOGY", "MYSTICAL_UNION_ANALOGY", "ORDINARY_RELATIONAL_CRISIS"})

    def test_every_model_has_provenance_evidence_alternatives_and_limits(self):
        for model in MODELS.values():
            self.assertTrue(model["provenance"]["source_id"])
            self.assertTrue(model["provenance"]["scope"])
            self.assertTrue(model["required_evidence"])
            self.assertTrue(model["incompatible_evidence"])
            self.assertTrue(model["alternatives"])
            self.assertTrue(model["cannot_prove"])

    def test_models_without_source_defined_sequence_do_not_claim_one(self):
        for key in ("TF_PROPHET", "MYSTICAL_UNION_ANALOGY", "ORDINARY_RELATIONAL_CRISIS"):
            self.assertEqual(MODELS[key]["expected_sequence"], [])
        self.assertFalse(REGISTRY["policy"]["ontology_inference_permitted"])
        self.assertEqual(REGISTRY["policy"]["causality_from_sequence"], "UNESTABLISHED")

    def test_prophet_doctrine_is_not_conflated_with_runner_chaser_stages(self):
        self.assertNotEqual(MODELS["TF_PROPHET"]["sequence_status"], "EMIC_SEQUENCE_HYPOTHESIS")
        self.assertEqual(MODELS["TF_PROPHET"]["provenance"]["source_id"], "prophet_twin_flames_qa_part1")

    def test_jung_and_mystical_union_are_explicit_analogies_not_twin_flame_evidence(self):
        self.assertEqual(MODELS["JUNGIAN_INDIVIDUATION_ANALOGY"]["mapping_status"], "ANALOGICAL_MAPPING")
        self.assertIn("una secuencia de pareja romántica", MODELS["MYSTICAL_UNION_ANALOGY"]["provenance"]["scope"])

if __name__ == "__main__":
    unittest.main()
