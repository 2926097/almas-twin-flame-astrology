"""Auditoría del vocabulario preregistrado del Paso 3."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "reference" / "dynamic-phase-vocabulary.json"
SCHEMA_PATH = ROOT / "schemas" / "dynamic-phase-vocabulary.schema.json"
EXPECTED_PHASES = {
    "recognition", "activation", "polarization", "crisis_mirror",
    "pursuit_withdrawal", "boundary_assertion", "separation_or_suspension",
    "surrender_candidate", "surrender_stabilized", "individual_restructuring",
    "awakening_candidate", "integration_candidate", "bilateral_reengagement",
    "reunion", "service", "closure", "indeterminate",
}


class DynamicPhaseVocabularyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocabulary = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_vocabulary_conforms_to_closed_schema(self):
        Draft202012Validator(self.schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(self.vocabulary)

    def test_all_plan_states_are_present_once(self):
        ids = [phase["id"] for phase in self.vocabulary["phases"]]
        self.assertEqual(set(ids), EXPECTED_PHASES)
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_phase_has_scope_entry_exclusion_evidence_and_counterevidence(self):
        for phase in self.vocabulary["phases"]:
            with self.subTest(phase=phase["id"]):
                self.assertTrue(phase["scope"])
                self.assertTrue(phase["entry_criteria"])
                self.assertTrue(phase["exclusions"])
                self.assertTrue(phase["required_evidence"])
                self.assertTrue(phase["counterevidence"])
                self.assertIn("non_implications", phase["possible_relations"])

    def test_phase_links_do_not_introduce_undefined_states(self):
        allowed = EXPECTED_PHASES | {"any_phase", "any_phase_after_new_evidence"}
        for phase in self.vocabulary["phases"]:
            links = phase["possible_relations"]
            for key in ("may_precede", "may_follow"):
                self.assertTrue(set(links[key]).issubset(allowed),
                                f"{phase['id']}:{key}")

    def test_sequence_and_astrology_cannot_assign_states(self):
        policy = self.vocabulary["sequence_policy"]
        self.assertFalse(policy["mandatory_order"])
        self.assertFalse(policy["missing_phases_may_be_inferred"])
        self.assertFalse(policy["state_transition_is_automatic"])
        self.assertFalse(policy["temporal_astrology_assigns_phase"])
        self.assertEqual(policy["causal_interpretation_from_order"], "UNESTABLISHED")

    def test_provenance_class_is_project_hypothesis_not_historical_doctrine(self):
        self.assertEqual(self.vocabulary["epistemic_class"], "E_PROJECT_HYPOTHESIS")
        self.assertEqual(self.vocabulary["contemporary_usage"]["status"],
                         "HETEROGENEOUS_EMIC_USAGE")
        self.assertTrue(all(source["limit"] for source in
                            self.vocabulary["contemporary_usage"]["sources"]))


if __name__ == "__main__":
    unittest.main()
