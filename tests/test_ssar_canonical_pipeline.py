import copy
import unittest
from unittest.mock import patch
from almas_tfa.orchestrator import Orchestrator
from almas_tfa.ssar_controls import ABLATIONS,ablate_request
from almas_tfa.ssar_pipeline import validate_canonical_ssar
from test_ssar_finish import fixture

CORE=('independent_roots','pillars','structural_model_indices','model_attributions','pairwise_idd','robustness_index','temporal_activation','counterevidence')
CANONICAL=('models','indices','pairwise_idd','ontology','evidence','robustness','counterevidence','counterevidence_state','temporal')

def full_run(request=None):
    from test_full_pipeline import TestFullPipelineSynthetic
    class Captured(Exception):pass
    original=Orchestrator.run;captured=[]
    def run(self,raw,manifest,**kwargs):
        raw=copy.deepcopy(raw)
        if request is not None:raw['ssar_request']=copy.deepcopy(request)
        result=original(self,raw,manifest,**kwargs);captured.append(result);raise Captured
    case=TestFullPipelineSynthetic('test_m00_m31_complete_with_explicit_inputs')
    with patch.object(Orchestrator,'run',run):
        try:case.test_m00_m31_complete_with_explicit_inputs()
        except Captured:pass
    if len(captured)!=1:raise AssertionError('Expected one complete pipeline')
    return captured[0]

class CanonicalSSARTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.baseline=full_run()
    def check_core(self,result):
        self.assertEqual({k:result.canonical[k] for k in CORE},{k:self.baseline.canonical[k] for k in CORE})
        self.assertEqual({k:result.canonical['canonical_analysis'][k] for k in CANONICAL},
                         {k:self.baseline.canonical['canonical_analysis'][k] for k in CANONICAL})
        self.assertEqual({k:v.status for k,v in result.results.items()},{k:v.status for k,v in self.baseline.results.items()})
    def bound_request(self):
        r=fixture();root=next(r for r in self.baseline.canonical['independent_roots']['roots'] if r['core_eligible'] and 'SUN' in r['point_ids'])
        reduced={k:root[k] for k in ('root_id','core_eligible','core_evidence_ids','point_ids')}
        r['profiles']['liminal']['core_roots']=[reduced]
        for o in r['profiles']['liminal']['observations']:o['core_root_refs']=[root['root_id']]
        return r
    def test_absent_has_no_optional_block_and_disabled_preserves_core(self):
        self.assertNotIn('ssar',self.baseline.canonical['canonical_analysis'])
        result=full_run(dict(enabled=False));self.check_core(result)
        ssar=result.canonical['canonical_analysis']['ssar'];self.assertFalse(ssar['enabled']);self.assertEqual(ssar['completion'],'NONE')
    def test_enabled_is_m14_registered_m27_consumed_before_gate_and_m31_paths(self):
        result=full_run(self.bound_request());self.check_core(result)
        canonical=result.canonical['canonical_analysis'];ssar=canonical['ssar'];validate_canonical_ssar(ssar)
        self.assertEqual(result.canonical['report_gate']['canonical_values_mutated'],False)
        self.assertTrue(any('ssar' in section['optional_paths'] for section in result.canonical['report_document_model']['sections']))
        self.assertEqual(ssar['documentary_input']['events'][0]['fact_interpretation_separated'],True)
    def test_nine_ablations_through_actual_m00_m31_preserve_numeric_outputs(self):
        for ablation in ABLATIONS:
            with self.subTest(ablation=ablation):
                result=full_run(ablate_request(self.bound_request(),ablation));self.check_core(result)
                self.assertEqual(result.canonical['canonical_analysis']['ssar']['ablation'],ablation)
