"""Pruebas sintéticas sin personas reales ni adaptación del scoring."""
from __future__ import annotations
from copy import deepcopy
import unittest

from almas_tfa.methodological_evidence_audit import audit_methodological_evidence
from almas_tfa.ablation_handlers import m22_ablation
from almas_tfa.null_model_handlers import m24_null_models
from almas_tfa.time_sensitivity_handlers import m23_time_sensitivity
from almas_tfa.module_contract import ModuleContext


def context(module, raw, canonical=None):
    return ModuleContext(module_id=module, module_name=module, mode="FULL",
                         raw_input=raw, canonical_snapshot=canonical or {}, prior_results={})


def synthetic_canonical():
    # Test real M22, M23 y M24; no se introducen puntuaciones inventadas.
    evidence = [{"evidence_id": "E1", "root_key": "A:SUN|B:MOON",
                 "technique_family": "SYN", "dependency_family": "SYN",
                 "contact": {"subject_a": "A", "subject_b": "B", "point_a_type": "PLANET", "point_b_type": "PLANET"}},
                {"evidence_id": "E2", "root_key": "A:JUNO|B:SUN",
                 "technique_family": "SECONDARY", "dependency_family": "SECONDARY",
                 "canonical_source": "secondary_symbolic",
                 "contact": {"subject_a": "A", "subject_b": "B"}}]
    canon = {"deduplicated_evidence": {"retained": evidence},
             "independent_roots": {"roots": [{"root_id": "R1", "evidence_ids": ["E1"]},
                                            {"root_id": "R2", "evidence_ids": ["E2"]}]}}
    ab = m22_ablation(context("M22", {}, canon)).canonical_updates["ablation"]
    null = m24_null_models(context("M24", {"null_model_runs": [{
        "id": "N1", "preregistration_ref": "SYNTHETIC-PRE",
        "null_model": "PAIR_SHUFFLE", "feature_set_ref": "F", "orb_policy_ref": "O",
        "event_set_ref": "E", "generator_ref": "G", "statistic_id": "ROOT_COUNT",
        "observed_value": 4, "tail": "GREATER_OR_EQUAL", "null_samples": [0, 4, 2, 5]}]})).canonical_updates["null_models"]
    time = m23_time_sensitivity(context("M23", {"time_sensitivity_summary": {
        "preregistration_ref": "SYNTHETIC-TS", "delta90": 10,
        "preserved_fraction": 0.81}})).canonical_updates["time_sensitivity"]
    shapley = {"state": "EVALUABLE", "player_unit": "INDEPENDENT_ROOT",
               "motif_player_count": 0, "motifs_recomputed_inside_coalitions": True,
               "unit_ids": ["R1", "R2"], "attributions": {"AF": {"R1": 1.0}},
               "shapley_efficiency_error": {"AF": 0.0}}
    return {"null_models": null, "ablation": ab, "time_sensitivity": time,
            "model_attributions": shapley}


class EvidenceAuditTests(unittest.TestCase):
    def test_missing_is_not_negative_or_empirically_validated(self):
        out = audit_methodological_evidence({})
        self.assertEqual(out["null_models"]["status"], "NOT_EVALUABLE")
        self.assertEqual(out["metaphysical_hypotheses"]["status"], "NOT_EVALUABLE")
        self.assertFalse(out["promotes_ontology"])

    def test_real_m22_m23_m24_outputs_remain_descriptive_and_unchanged(self):
        source = synthetic_canonical()
        old = deepcopy(source)
        a = audit_methodological_evidence(source)
        self.assertEqual(a, audit_methodological_evidence(source))
        self.assertEqual(source, old)
        self.assertEqual(a["null_models"]["status"], "DESCRIPTIVE_CHECKED")
        self.assertIsNone(a["null_models"]["p_value"])
        self.assertEqual(a["ablations"]["status"], "STRUCTURAL_CHECKED")
        self.assertEqual(len(a["ablations"]["runs"]), 9)
        self.assertEqual(a["shapley"]["independent_players"], 2)
        self.assertEqual(a["empirical_validation"]["status"], "NOT_VERIFIED_BY_THIS_AUDIT")
        self.assertFalse(a["production_indices_modified"])

    def test_forged_null_frequency_rejected(self):
        canon = synthetic_canonical()
        canon["null_models"]["runs"][0]["structural_frequency"] = 0.99
        with self.assertRaisesRegex(ValueError, "frecuencia inconsistente"):
            audit_methodological_evidence(canon)

    def test_incomplete_ablations_rejected(self):
        canon = synthetic_canonical()
        canon["ablation"]["runs"].pop()
        with self.assertRaisesRegex(ValueError, "incompleta"):
            audit_methodological_evidence(canon)

    def test_duplicated_roots_and_inconsistent_survival_rejected(self):
        canon = synthetic_canonical()
        canon["ablation"]["runs"][0]["surviving_root_ids"].append("R1")
        with self.assertRaisesRegex(ValueError, "duplicados"):
            audit_methodological_evidence(canon)
        canon = synthetic_canonical()
        canon["ablation"]["runs"][1]["survival_fraction"] = 1.0
        with self.assertRaisesRegex(ValueError, "supervivencia inconsistente"):
            audit_methodological_evidence(canon)

    def test_time_without_proven_reliability_is_diagnostic_only(self):
        canon = synthetic_canonical()
        canon["time_sensitivity"]["robustness_component_eligible"] = False
        canon["time_sensitivity"]["robustness_component"] = None
        self.assertEqual(audit_methodological_evidence(canon)["birth_time"]["status"],
                         "DIAGNOSTIC_ONLY")
        canon["time_sensitivity"]["robustness_component"] = 0.8
        with self.assertRaises(ValueError):
            audit_methodological_evidence(canon)

    def test_derived_shapley_player_rejected(self):
        canon = synthetic_canonical()
        canon["model_attributions"]["attributions"]["AF"]["MOTIF:PX"] = 2.0
        with self.assertRaisesRegex(ValueError, "derivado"):
            audit_methodological_evidence(canon)

    def test_declared_external_validity_cannot_promote(self):
        canon = synthetic_canonical()
        canon["external_validation"] = {"validated": True, "ontology": "TWIN_FLAME"}
        report = audit_methodological_evidence(canon)
        self.assertEqual(report["empirical_validation"]["status"], "NOT_VERIFIED_BY_THIS_AUDIT")
        self.assertEqual(report["metaphysical_hypotheses"]["status"], "NOT_EVALUABLE")


if __name__ == "__main__":
    unittest.main()
