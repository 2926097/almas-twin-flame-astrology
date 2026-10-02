"""RRA synthetic fixtures: numerical contracts, not empirical relationship evidence."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import unittest
from almas_tfa.return_activation import (run_return_activation,validate_return_activation,load_return_policy,
    attach_return_activation,validate_ssar_with_returns,render_ssar_with_returns)
from almas_tfa.return_solver import ReturnPositionProvider,find_all_return_passes,instant
from almas_tfa.return_controls import annual_return_summary
EPOCH=datetime(2020,1,1,tzinfo=timezone.utc)
ROOTS=[dict(root_id='R1',core_eligible=True,core_evidence_ids=['CORE'],point_ids=['SUN','MOON','VENUS'])]
class SyntheticBackend:
    def __init__(self,fn=None):self.fn=fn or (lambda d:(d-10,1))
    def calculate_transit_positions(self,when):
        lon,speed=self.fn((when-EPOCH).total_seconds()/86400)
        return dict(positions={'SUN':dict(longitude=lon%360,speed=speed),'VENUS':dict(longitude=60,speed=0),'MOON':dict(longitude=(lon*13)%360,speed=speed*13)},
            backend_id='SYNTHETIC_TEST_ONLY',backend_version='1',backend_provenance={'fixture':'not-an-ephemeris'})
    def calculate_return_chart(self,when,*,latitude,longitude):
        return dict(self.calculate_transit_positions(when),angles={'ASC':longitude%360,'MC':latitude%360},houses={})
def request():
    return dict(enabled=True,clocks=[dict(id='SOLAR',owner='SYNTHETIC_A',returning_body='SUN',reference_chart='N',reference_point='SUN',
        start='2020-01-01T00:00:00Z',end='2020-02-01T00:00:00Z',locations=[dict(id='UNKNOWN',basis='unknown')],
        angular_reliability=False,birth_time_quality='UNKNOWN')],charts=[dict(id='N',layer='NATAL',source_ref='synthetic:natal',points=[
            dict(point_id='SUN',longitude=0,core_root_refs=['R1']),dict(point_id='MOON',longitude=61,core_root_refs=['R1'])])],
        events=[dict(event_id='E',event_type='SYNTHETIC',fact_statement='Synthetic event',fact_key='FACT',source_refs=['synthetic:event'],
            occurred=True,certainty='DOCUMENTED',uncertainty_hours=0,event_datetime='2020-01-11T00:00:00Z')],robustness=True,
        null_model=dict(method='EVENT_DATE_SHIFT',seed=42,simulations=20))
def run(req=None,backend=None,roots=None,ssar=None):
    return run_return_activation(req or request(),backend=backend or SyntheticBackend(),canonical_roots=roots or ROOTS,ssar_structure=ssar)
class ReturnsTests(unittest.TestCase):
    def test_report_exposes_contacts_controls_and_negative_evidence(self):
        from almas_tfa.return_activation import render_return_summary
        req=request();req['events'][0]['event_datetime']='2020-01-30T00:00:00Z'
        report=render_return_summary(run(req))
        for text in ['Activación en NATAL','Contacto obligatorio','Ablación HALF_ORB','semilla 42',
                     'activation_without_event','event_without_activation','Interpretación:']:
            self.assertIn(text,report)
    def test_exact_wrap_and_replay(self):
        out=run();r=out['returns'][0]
        self.assertEqual(r['exact_return_time'],'2020-01-11T00:00:00Z');self.assertLessEqual(r['angular_error'],1e-5)
        self.assertEqual(r['return_chart']['angular_status'],'BLOCKED');validate_return_activation(out,backend=SyntheticBackend())
        self.assertFalse(out['iat_modified']);self.assertEqual(out['ontology_effect'],'NONE')
    def test_three_passes_preserved(self):
        b=SyntheticBackend(lambda d:((d-5)*(d-10)*(d-15)/100,(3*d*d-60*d+275)/100))
        out=run(backend=b);self.assertEqual(len(out['returns']),3)
        self.assertEqual([r['motion_state'] for r in out['returns']],['DIRECT','RETROGRADE','DIRECT'])
    def test_stationary_tangent_and_no_opposition(self):
        out=run(backend=SyntheticBackend(lambda d:((d-10)**2/100,2*(d-10)/100)))
        self.assertEqual(len(out['returns']),1);self.assertAlmostEqual(out['returns'][0]['angular_error'],0,places=5)
        self.assertEqual(run(backend=SyntheticBackend(lambda d:(180+d/100,.01)))['returns'],[])
    def test_lunar_and_disabled(self):
        req=request();req['clocks'][0].update(returning_body='MOON',reference_point='MOON');req['charts'][0]['points'][1]['longitude']=0
        self.assertGreaterEqual(len(run(req)['returns']),1)
        req['enabled']=False;out=run(req);self.assertEqual(out['execution_status'],'not_run');self.assertEqual(out['returns'],[])
    def test_future_uncertain_and_cycle_events(self):
        for change,status in [({'occurred':False},'NOT_EVALUABLE'),({'uncertainty_hours':169},'NOT_EVALUABLE'),
                              ({'event_datetime':'2020-01-25T00:00:00Z'},'COMPATIBLE'),({'source_refs':[]},'NOT_EVALUABLE')]:
            req=request();req['events'][0].update(change);out=run(req)
            self.assertEqual(out['returns'][0]['event_correspondences'][0]['status'],status)
    def test_identity_return_is_not_new_evidence(self):
        req=request();req['charts'][0]['points']=req['charts'][0]['points'][:1]
        b=SyntheticBackend();original=b.calculate_transit_positions
        b.calculate_transit_positions=lambda when:dict(original(when),positions={'SUN':original(when)['positions']['SUN']})
        out=run(req,b);self.assertEqual(out['dependency_graph']['effective_units'],[])
        self.assertNotEqual(out['returns'][0]['event_correspondences'][0]['status'],'SUPPORTED')
    def test_locations_and_documentary_alias_deduplicate(self):
        req=request();req['clocks'][0].update(angular_reliability=True,birth_time_quality='DOCUMENTED',reference_uncertainty_degrees=0,
          locations=[dict(id='B',basis='birth_location',latitude=0,longitude=0,source_ref='synthetic:location'),dict(id='R',basis='residence_location',latitude=1,longitude=2,source_ref='synthetic:location')])
        alias=deepcopy(req['events'][0]);alias.update(event_id='ALIAS',fact_statement='Alternate wording of same fact');req['events'].append(alias)
        out=run(req);self.assertEqual(len(out['returns']),2);self.assertEqual(len(out['dependency_graph']['effective_units']),1)
        self.assertEqual(out['recurrence'][0]['recurrence_count'],1);self.assertEqual(annual_return_summary(out)[0]['return_count'],1)
        self.assertNotEqual(out['returns'][0]['return_chart']['angles'],out['returns'][1]['return_chart']['angles'])
    def test_secondary_is_blocked_and_missing_backend_body(self):
        req=request();req['clocks'][0].update(returning_body='CERES',reference_point='CERES');req['charts'][0]['points'].append(dict(point_id='CERES',longitude=0,core_root_refs=[]))
        self.assertEqual(run(req)['execution_status'],'blocked')
        req=request();req['clocks'][0].update(returning_body='SATURN',reference_point='SATURN');req['charts'][0]['points'].append(dict(point_id='SATURN',longitude=0,core_root_refs=[]))
        self.assertEqual(run(req)['execution_status'],'blocked')
    def test_invalid_roots_coordinates_and_nonfinite(self):
        for mutation in [lambda r:r['charts'][0]['points'][0].update(core_root_refs=['FAKE']),
                         lambda r:r['charts'][0]['points'][0].update(longitude=float('nan')),
                         lambda r:r['clocks'][0].update(locations=[dict(id='B',basis='birth_location',latitude=95,longitude=0,source_ref='s')])]:
            req=request();mutation(req)
            with self.assertRaises(Exception):run(req)
    def test_null_fixed_seed_formula_and_controls(self):
        a=run();b=run();self.assertEqual(a,b);n=a['null_model_result'];self.assertEqual(n['p_mc'],(n['k']+1)/21)
        self.assertEqual(n['completed_simulations'],20);self.assertFalse(n['confirmatory_inference_allowed'])
        req=request();req['null_model'].update(method='CONTROL_DATES',simulations=2,control_datetimes=['2020-01-11T00:00:00Z','2020-01-30T00:00:00Z'])
        n=run(req)['null_model_result'];self.assertEqual([x['value'] for x in n['replicas']],[1,0])
        req['null_model'].update(method='EVENT_DATE_PERMUTATION');n=run(req)['null_model_result'];self.assertFalse(n['null_variation'])
    def test_derivations_and_event_null_block(self):
        for layer in ['COMPOSITE','DAVISON','DRACONIC','EVENT']:
            req=request();req['charts'].append(dict(id=layer,layer=layer,source_ref='synthetic:derived',points=[dict(point_id='MID',longitude=60,
                core_root_refs=['R1'],parent_point_ids=['SUN','MOON'],derivation_method='SYNTHETIC_TEST')]))
            out=run(req);self.assertIn(layer,[c['layer'] for c in out['returns'][0]['contacts']])
            if layer=='EVENT':self.assertEqual(out['null_model_result']['reason'],'EVENT_REFERENCE_CHART_RECOMPUTATION_REQUIRED')
    def test_orb_boundary_and_uncertainty(self):
        req=request();out=run(req);self.assertTrue(any(c['orb']==1 for c in out['returns'][0]['contacts']))
        req['charts'][0]['points'][1]['uncertainty_degrees']=.001
        out=run(req);self.assertTrue(out['returns'][0]['excluded_contacts'])
    def test_tamper_fails_and_no_input_mutation(self):
        req=request();before=deepcopy(req);out=run(req);self.assertEqual(req,before)
        for key,value in [('iat_modified',True),('calculation_hash','0'*64)]:
            forged=deepcopy(out);forged[key]=value
            with self.assertRaises(Exception):validate_return_activation(forged)
        forged=deepcopy(out);forged['returns'][0]['contacts']=[]
        with self.assertRaises(ValueError):validate_return_activation(forged)
    def test_attach_preserves_ssar_and_indices(self):
        from almas_tfa.ssar_pipeline import run_ssar_pipeline
        canonical=dict(ssar=run_ssar_pipeline(dict(enabled=True)),independent_roots=dict(roots=ROOTS),indices={'IAT':0,'IEM':3})
        before=deepcopy(canonical);out=attach_return_activation(canonical,request(),backend=SyntheticBackend())
        self.assertEqual(canonical,before);self.assertEqual(out['indices'],before['indices']);validate_ssar_with_returns(out['ssar'])
        self.assertIn('RRA',render_ssar_with_returns(out));self.assertEqual({k:v for k,v in out['ssar'].items() if k!='temporal_activation'},before['ssar'])
    def test_timezone_ambiguity_nonexistent_and_explicit_offset(self):
        for date in ['2020-10-25T02:30:00','2020-03-29T02:30:00']:
            with self.assertRaises(ValueError):instant(date,'Europe/Madrid')
        self.assertEqual(instant('2020-10-25T02:30:00+02:00','Europe/Madrid').hour,0)
        with self.assertRaises(ValueError):instant('2020-10-25T02:30:00+04:00','Europe/Madrid')
    def test_complete_pipeline_preserves_core_and_report_gate(self):
        from unittest.mock import patch
        from test_ssar_canonical_pipeline import full_run,CORE,CANONICAL
        from almas_tfa.orchestrator import Orchestrator
        baseline=full_run(dict(enabled=True));root=next(r for r in baseline.canonical['independent_roots']['roots'] if r['core_eligible'] and 'SUN' in r['point_ids'])
        req=request();req['charts'][0]['points']=[dict(point_id='SUN',longitude=0,core_root_refs=[root['root_id']])]
        original=Orchestrator.run
        def inject(self,raw,manifest,**kwargs):
            raw=deepcopy(raw);raw['return_activation_request']=req
            return original(self,raw,manifest,**kwargs)
        with patch.object(Orchestrator,'run',inject):out=full_run(dict(enabled=True))
        self.assertEqual({k:out.canonical[k] for k in CORE},{k:baseline.canonical[k] for k in CORE})
        self.assertEqual({k:out.canonical['canonical_analysis'][k] for k in CANONICAL},{k:baseline.canonical['canonical_analysis'][k] for k in CANONICAL})
        self.assertIn('temporal_activation',out.canonical['canonical_analysis']['ssar'])
        self.assertEqual(out.canonical['report_gate']['canonical_values_mutated'],False)
    def test_qualified_ssar_overlay_and_secondary_return(self):
        from almas_tfa.ssar_pipeline import run_ssar_pipeline
        from test_ssar_s1 import fixture
        ssar=run_ssar_pipeline(dict(enabled=True,profiles={'s1':fixture()}))['structure']
        appearance=next(a for a in ssar['appearances'] if a['qualification']=='QUALIFIED_SIGNIFICATOR')
        req=request();req['charts'].append(dict(id='S',layer='SSAR',source_ref='synthetic:ssar',points=[dict(point_id='CERES',longitude=10,
             core_root_refs=['R1'],significator_ref=appearance['id'])]))
        req['clocks'][0].update(returning_body='CERES',reference_point='CERES',reference_chart='S',significator_ref=appearance['id'])
        b=SyntheticBackend();original=b.calculate_transit_positions
        def calculate(when):
            value=original(when);value['positions']['CERES']=dict(longitude=((when-EPOCH).total_seconds()/86400)%360,speed=1);return value
        b.calculate_transit_positions=calculate
        out=run(req,b,ssar=ssar);self.assertEqual(out['execution_status'],'executed')
        self.assertIn('SSAR',[c['layer'] for c in out['returns'][0]['contacts']])
        req['clocks'][0].pop('significator_ref');self.assertEqual(run(req,b,ssar=ssar)['execution_status'],'blocked')
    def test_documentary_recurrence_and_negative_controls(self):
        req=request();second=deepcopy(req['events'][0]);second.update(event_id='SECOND',fact_key='SECOND_FACT',event_datetime='2020-01-12T00:00:00Z');req['events'].append(second)
        out=run(req);self.assertEqual(out['recurrence'][0]['recurrence_count'],2);self.assertEqual(out['returns'][0]['activation_depth'],'R6')
        req=request()
        for point in req['charts'][0]['points']:point['core_root_refs']=[]
        out=run(req);self.assertTrue(any(n['kind']=='event_without_activation' for n in out['negative_results']))
        req=request();req['charts'][0]['points'][1].update(time_sensitive=True,angular_reliability=False)
        out=run(req);self.assertTrue(any(n['reason']=='TARGET_ANGULAR_PRECISION_BLOCKED' for n in out['returns'][0]['excluded_contacts']))
    def test_synastry_and_event_return_are_experimental(self):
        req=request();req['charts'].append(dict(id='B',layer='SYNASTRY',source_ref='synthetic:synastry',points=[dict(point_id='MOON',longitude=60,core_root_refs=['R1'])]))
        self.assertIn('SYNASTRY',[c['layer'] for c in run(req)['returns'][0]['contacts']])
        req=request();req['charts'][0]['layer']='EVENT'
        for point in req['charts'][0]['points']:point.update(parent_point_ids=['SUN','MOON'],derivation_method='DOCUMENTED_EVENT_REFERENCE')
        out=run(req);self.assertEqual(out['returns'][0]['return_type'],'EVENT_RETURN_EXPERIMENTAL')
        self.assertEqual(out['returns'][0]['doctrine_class'],'E_PROJECT_HYPOTHESIS')
