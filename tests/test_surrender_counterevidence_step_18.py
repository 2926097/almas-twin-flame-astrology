"""Paso 18: contraevidencia suficiente impide surrender estabilizado."""
import unittest
from almas_tfa.surrender_assessment import assess_surrender


def complete_assessment(counter):
    return {
      "assessment_start":"2026-01-01","assessment_end":"2026-02-01","preregistration_ref":"FROZEN-PROTOCOL-1",
      "pursuit_ledger":{"prior_pursuit_attempt_refs":["P1","P2"],"post_window_pursuit_refs":[],"contact_opportunity_refs":["O1"],"contact_log_complete":True},
      "boundary_assertion_refs":["B1"],
      "decentering_activities":[
        {"fact_id":"D1","actor":"A","domain":"WORK","occurred_on":"2026-01-01","independent_of_other_actor_response":True},
        {"fact_id":"D2","actor":"A","domain":"HEALTH","occurred_on":"2026-02-01","independent_of_other_actor_response":True}],
      "counterevidence":[counter]
    }


class SurrenderCounterevidenceStep18Tests(unittest.TestCase):
    def test_each_registered_falsifier_blocks_stabilized_status(self):
        kinds=["CONTINUED_PURSUIT","EXPLICIT_STRATEGIC_SILENCE_TO_PROVOKE_RESPONSE","REPEATED_CONFLICT_REOPENING","OUTCOME_BARGAINING","CONTROL_ATTEMPT"]
        for index,kind in enumerate(kinds,1):
            contrary={"kind":kind,"evidence_refs":[f"C{index}"]}
            if kind=="EXPLICIT_STRATEGIC_SILENCE_TO_PROVOKE_RESPONSE":
                contrary["actor_self_reported_intent"]=True
            result=assess_surrender("A",complete_assessment(contrary))
            with self.subTest(kind=kind):
                self.assertEqual(result["stabilized"]["status"],"CONTRADICTED")
                self.assertNotEqual(result["stabilized"]["status"],"SUPPORTED")

    def test_strategic_silence_is_not_inferred_without_self_report(self):
        contrary={"kind":"EXPLICIT_STRATEGIC_SILENCE_TO_PROVOKE_RESPONSE","evidence_refs":["C1"]}
        with self.assertRaises(ValueError):
            assess_surrender("A",complete_assessment(contrary))

    def test_no_references_means_unregistered_counterevidence_is_rejected(self):
        with self.assertRaises(ValueError):
            assess_surrender("A",complete_assessment({"kind":"CONTROL_ATTEMPT","evidence_refs":[]}))

if __name__=="__main__": unittest.main()
