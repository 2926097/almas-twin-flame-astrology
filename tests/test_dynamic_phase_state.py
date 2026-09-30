"""Contrato sin inferencia del Paso 2."""

from __future__ import annotations

from copy import deepcopy
import unittest

from jsonschema import ValidationError

from almas_tfa.canonical_assembly import assemble_canonical_analysis
from almas_tfa.dynamic_phase_state import empty_dynamic_phase_state
from test_canonical_assembly import canonical_base, prior_all
from test_canonical_schema_validation import canonical_validator


class DynamicPhaseStateTests(unittest.TestCase):
    def setUp(self):
        self.validator = canonical_validator()

    def test_new_canonical_has_three_independent_unassessed_scopes(self):
        result = assemble_canonical_analysis(canonical_base(), prior_all())
        self.assertEqual(result["state"], "EVALUABLE")
        canonical = result["canonical_analysis"]
        state = canonical["dynamic_phases"]
        self.assertEqual(state, empty_dynamic_phase_state())
        self.assertIsNot(state["actor_a_phase"], state["actor_b_phase"])
        self.assertIsNot(state["relational_phase"], state["actor_a_phase"])
        self.validator.validate(canonical)

    def test_no_automatic_phase_from_temporal_or_existing_labels(self):
        source = canonical_base()
        source["temporal_activation"] = {"iat": 100.0}
        source["reality"] = {"phase": "REUNION"}
        source["dynamic_phases"] = {
            "relational_phase": {"phase": "reunion", "status": "SUPPORTED"}
        }
        result = assemble_canonical_analysis(source, prior_all())
        self.assertEqual(result["canonical_analysis"]["dynamic_phases"],
                         empty_dynamic_phase_state())

    def test_legacy_canonical_without_field_remains_valid(self):
        canonical = assemble_canonical_analysis(
            canonical_base(), prior_all()
        )["canonical_analysis"]
        del canonical["dynamic_phases"]
        self.validator.validate(canonical)

    def test_unassessed_contract_rejects_premature_assignments(self):
        canonical = assemble_canonical_analysis(
            canonical_base(), prior_all()
        )["canonical_analysis"]
        for scope in ("relational_phase", "actor_a_phase", "actor_b_phase"):
            assigned = deepcopy(canonical)
            assigned["dynamic_phases"][scope] = {
                "phase": "surrender_candidate", "status": "SUPPORTED"
            }
            with self.subTest(scope=scope), self.assertRaises(ValidationError):
                self.validator.validate(assigned)

    def test_unknown_scope_and_status_are_rejected(self):
        canonical = assemble_canonical_analysis(
            canonical_base(), prior_all()
        )["canonical_analysis"]
        extra = deepcopy(canonical)
        extra["dynamic_phases"]["actor_c_phase"] = {
            "phase": None, "status": "NOT_EVALUABLE"
        }
        with self.assertRaises(ValidationError):
            self.validator.validate(extra)
        wrong_status = deepcopy(canonical)
        wrong_status["dynamic_phases"]["actor_b_phase"]["status"] = "SUPPORTED"
        with self.assertRaises(ValidationError):
            self.validator.validate(wrong_status)


if __name__ == "__main__":
    unittest.main()
