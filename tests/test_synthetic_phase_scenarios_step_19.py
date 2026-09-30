"""Paso 19: escenarios sintéticos A–D del plan 1.22.0."""
import unittest
from almas_tfa.awakening_assessment import CRITERIA, assess_awakening
from almas_tfa.doctrinal_sequence_engine import evaluate_doctrinal_sequence
from almas_tfa.phase_transition_matrix import LAYER_NAMES, build_phase_transition_matrix
from almas_tfa.surrender_assessment import assess_surrender


class SyntheticPhaseScenariosStep19Tests(unittest.TestCase):
    def test_a_pursuit_resumes_after_24_hours_candidate_does_not_stabilize(self):
        result=assess_surrender("A",{
          "assessment_start":"2026-01-01","assessment_end":"2026-01-02","preregistration_ref":"SYNTH-PREREG",
          "pursuit_ledger":{"prior_pursuit_attempt_refs":["P1","P2"],"post_window_pursuit_refs":["P3-24H"],"contact_opportunity_refs":["O1"],"contact_log_complete":True},
          "boundary_assertion_refs":["B1"],"decentering_activities":[],"counterevidence":[{"kind":"CONTINUED_PURSUIT","evidence_refs":["P3-24H"]}]})
        self.assertEqual(result["candidate"]["phase_id"],"surrender_candidate")
        self.assertNotEqual(result["stabilized"]["status"],"SUPPORTED")
        self.assertIn(result["stabilized"]["status"],{"INSUFFICIENT","CONTRADICTED"})

    def test_b_astrology_only_means_awakening_not_evaluable(self):
        assessment={"criteria":{key:{"state":"NOT_EVALUABLE","evidence_refs":[]} for key in CRITERIA}}
        result=assess_awakening("B",assessment)
        self.assertEqual(result["status"],"NOT_EVALUABLE")
        self.assertTrue(all(item["state"]=="NOT_EVALUABLE" for item in result["criteria"].values()))
        self.assertFalse(result["astrology_established_awakening"])

    def test_c_clear_behavioral_change_can_support_transition_without_astrology(self):
        layers={key:{"status":"NOT_EVALUABLE","evidence_refs":[],"rationale":"No evidence in this layer."} for key in LAYER_NAMES}
        layers["documentary"]={"status":"SUPPORTED","evidence_refs":["DOC-1"],"rationale":"Cambio declarado y fechado por el actor."}
        layers["behavioral"]={"status":"SUPPORTED","evidence_refs":["ACT-1"],"rationale":"Cambio conductual posterior verificable."}
        result=build_phase_transition_matrix("T-C","crisis_mirror","individual_restructuring","Cambio longitudinal documentado.",layers)
        self.assertEqual(result["final_status"],"SUPPORTED")
        self.assertEqual(result["astrological_structural"]["status"],"NOT_EVALUABLE")
        self.assertEqual(result["astrological_temporal"]["status"],"NOT_EVALUABLE")

    def test_d_surrender_then_awakening_sequence_never_proves_causality(self):
        phases=["boundary_assertion","surrender_candidate","surrender_stabilized","awakening_candidate","bilateral_reengagement"]
        observations=[{"phase_id":phase,"occurred_at":f"2026-01-{day:02d}T12:00:00Z","evidence_refs":[f"F{day}"]} for day,phase in enumerate(phases,1)]
        result=evaluate_doctrinal_sequence("TF_DF_DM_SURRENDER",observations)
        self.assertEqual(result["sequence_match"],"MATCH")
        self.assertEqual(result["doctrinal_compatibility"],"COMPATIBLE")
        self.assertEqual(result["causal_status"],"UNESTABLISHED")
        self.assertEqual(result["ontology_status"],"INSUFFICIENT")
        self.assertFalse(result["twin_flame_demonstrated"])

if __name__=="__main__": unittest.main()
