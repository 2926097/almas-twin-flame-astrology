import copy
import unittest
from almas_tfa.ssar_pipeline import run_ssar_pipeline, validate_canonical_ssar, render_ssar_summary, GENERAL
from almas_tfa.ssar_integration import freeze_architecture
from almas_tfa.ssar_controls import run_ablations, run_synthetic_null, ABLATIONS
from test_ssar_liminal_moirai import fixture as liminal
from test_ssar_s1 import fixture as s1
from test_ssar_lots import fixture as lots

COMPLEX='LIMINAL_TRANSITION_COMPLEX'

def fixture():
    r=dict(enabled=True,profiles={'liminal':liminal()},complex_search=[dict(complex_ref=COMPLEX,search_complete=True)])
    return r

def integrated():
    r=fixture();w=dict(id='W',complex_ref=COMPLEX,start='2020-01-01',end='2020-01-31',observed_through='2020-02-01',
        observation_complete=True,monitoring_ref='synthetic:complete-monitoring',clocks=[])
    for i,f in enumerate(('TPROG','TTRANSIT')):
        w['clocks'].append(dict(id='T'+str(i),complex_ref=COMPLEX,family=f,date='2020-01-15',longitude=10,target_longitude=11,
            input_precision_sufficient=True,robust=True,source_refs=['synthetic:clock'],core_root_refs=['R1']))
    r['integration']=dict(windows=[w],claims=[],freeze=None)
    out=run_ssar_pipeline(r)
    r['integration']['freeze']=freeze_architecture(out['structure'],r['integration'],policy_hash=out['evaluation_policy_hash'],registered_at='2019-12-01')
    return r

def ledger():
    return dict(events=[dict(event_id='E',fact_key='FACT',subjects=['A','B'],date='2020-01-15',date_precision='EXACT_DATE',
        fact_statement='SYNTHETIC documented transition',record_status='ACTIVE',documentary_quality_contract_met=True,
        fact_interpretation_separated=True,date_precision_contract_met=True,source_refs=['synthetic:event'],resolved_root_refs=['R1'])])

def claim(scope='STRUCTURAL',id='D'):
    return dict(id=id,complex_ref=COMPLEX,scope=scope,window_ref='W' if scope=='TEMPORAL' else None,
        coding_rule_ref=COMPLEX+'_DOCUMENTARY_V1',support_event_refs=['E'],excluding_event_refs=[],coverage_complete=True)

def rebind(r):
    old=r['integration']['freeze'];r['integration']['freeze']=None;out=run_ssar_pipeline(r)
    r['integration']['freeze']=freeze_architecture(out['structure'],r['integration'],policy_hash=out['evaluation_policy_hash'],registered_at=old['registered_at'] if old else '2019-12-01')

class FinishTests(unittest.TestCase):
    def test_general_complexes_two_groups_positive_one_group_candidate(self):
        for cid,points in GENERAL.items():
            req=s1(points[0]);o=copy.deepcopy(req['observations'][0]);o['id']='A2';o['geometry']['longitude']=50;o['geometry']['target_longitude']=51
            for sample in o['robustness']['samples']:sample['longitude']=50;sample['target_longitude']=51
            req['observations'].append(o);req['units'].append(dict(id='U2',appearance_ref='A2',technique='COMPOSITE',equivalence_key='CONTACT2'))
            r=dict(enabled=True,profiles={'s1':req},complex_search=[dict(complex_ref=cid,search_complete=True)])
            out=run_ssar_pipeline(r);c=next(c for c in out['structure']['complexes'] if c['id']==cid)
            self.assertTrue(c['qualified_complex']);self.assertEqual(c['cluster_strength'],None)
            req['units'][1]['technique']='SYNASTRY';out=run_ssar_pipeline(r);c=next(c for c in out['structure']['complexes'] if c['id']==cid)
            self.assertFalse(c['qualified_complex']);self.assertEqual(c['assessments']['functional_interpretation']['status'],'COMPATIBLE')
    def test_pipeline_preserves_legacy_profile_results_and_reproduces(self):
        r=fixture();out=run_ssar_pipeline(r);validate_canonical_ssar(out,request=r)
        self.assertEqual(out['policy_status'],'FROZEN_EXPERIMENTAL');self.assertEqual(out['profiles']['liminal']['policy_status'],'DEVELOPMENT')
        self.assertIn('validación externa',render_ssar_summary({'ssar':out}))
        self.assertTrue(all(a['policy_ref']==out['policy_id'] for c in out['structure']['complexes']+out['structure']['dyads'] for a in c['assessments'].values()))
    def test_disabled_enabled_empty_and_complete_negative_search(self):
        disabled=run_ssar_pipeline(dict(enabled=False));empty=run_ssar_pipeline(dict(enabled=True))
        self.assertEqual(disabled['completion'],'NONE');self.assertEqual(empty['completion'],'NONE')
        r=fixture()
        for o in r['profiles']['liminal']['observations']:
            o['geometry']['longitude']+=20
            for s in o['robustness']['samples']:s['longitude']+=20
        out=run_ssar_pipeline(r);self.assertEqual(out['completion'],'COMPLETE')
        self.assertFalse(next(c for c in out['structure']['complexes'] if c['id']==COMPLEX)['qualified_complex'])
    def test_two_clocks_positive_without_any_documentary_promotion(self):
        out=run_ssar_pipeline(integrated());w=out['integration']['temporal'][0]
        self.assertTrue(w['qualified_temporal_complex']);self.assertEqual(w['prediction_class'],'RETROSPECTIVE')
        self.assertEqual(out['integration']['documentary'],[])
    def test_temporal_clocks_cannot_create_structure(self):
        r=integrated()
        for o in r['profiles']['liminal']['observations']:o['core_root_refs']=[]
        rebind(r);out=run_ssar_pipeline(r)
        self.assertFalse(out['integration']['temporal'][0]['qualified_temporal_complex'])
        self.assertIn('STRUCTURE_NOT_QUALIFIED',out['integration']['temporal'][0]['blockers'])
    def test_same_group_unknown_precision_open_window_missing_monitoring_no_freeze(self):
        for change in ('group','precision','open','monitoring','freeze','late'):
            r=integrated();w=r['integration']['windows'][0]
            if change=='group':w['clocks'][1]['family']='TDIR'
            elif change=='precision':w['clocks'][0]['input_precision_sufficient']=None
            elif change=='open':w['observed_through']='2020-01-20'
            elif change=='monitoring':w['observation_complete']=False
            elif change=='freeze':r['integration']['freeze']=None
            else:r['integration']['freeze']['registered_at']='2020-02-01'
            out=run_ssar_pipeline(r)
            self.assertFalse(out['integration']['temporal'][0]['qualified_temporal_complex'])
    def test_freeze_change_to_architecture_policy_or_windows_rejected(self):
        for change in ('policy','window','geometry'):
            r=integrated()
            if change=='policy':r['integration']['freeze']['policy_hash']='0'*64
            elif change=='window':r['integration']['windows'][0]['end']='2020-02-28'
            else:r['profiles']['liminal']['observations'][0]['geometry']['longitude']+=1
            with self.assertRaises(ValueError):run_ssar_pipeline(r)
    def test_structural_documentary_positive_without_clocks_temporal_requires_window(self):
        r=fixture();r['integration']=dict(windows=[],claims=[claim()],freeze=None)
        d=run_ssar_pipeline(r,m27_ledger=ledger())['integration']['documentary'][0]
        self.assertEqual(d['assessment']['status'],'SUPPORTED')
        r=integrated();r['integration']['claims']=[claim('TEMPORAL')];rebind(r)
        self.assertEqual(run_ssar_pipeline(r,m27_ledger=ledger())['integration']['documentary'][0]['assessment']['status'],'SUPPORTED')
    def test_documentary_missing_m27_quality_coverage_superseded_or_wrong_date_not_absence(self):
        for change in ('ledger','quality','coverage','superseded','date'):
            r=integrated();r['integration']['claims']=[claim('TEMPORAL')];rebind(r);l=ledger()
            if change=='ledger':l=None;r['integration']['claims'][0]['support_event_refs']=[]
            elif change=='quality':l['events'][0]['documentary_quality_contract_met']=False
            elif change=='coverage':r['integration']['claims'][0]['coverage_complete']=False
            elif change=='superseded':l['events'][0]['record_status']='SUPERSEDED'
            else:l['events'][0]['date_precision']='UNKNOWN'
            self.assertEqual(run_ssar_pipeline(r,m27_ledger=l)['integration']['documentary'][0]['assessment']['status'],'NOT_EVALUABLE')
    def test_exclusion_precedes_missing_clocks_and_shared_event_one_fact(self):
        r=fixture();r['integration']=dict(windows=[],claims=[claim(id='D1'),claim(id='D2')],freeze=None)
        out=run_ssar_pipeline(r,m27_ledger=ledger());self.assertEqual(len(out['integration']['shared_events']),1)
        self.assertFalse(out['integration']['shared_events'][0]['contributes_new_evidence'])
        r['integration']['claims'][0]['support_event_refs']=[];r['integration']['claims'][0]['excluding_event_refs']=['E']
        r['integration']['claims'][0]['coverage_complete']=False
        self.assertEqual(run_ssar_pipeline(r,m27_ledger=ledger())['integration']['documentary'][0]['assessment']['status'],'CONTRADICTED')
    def test_duplicate_event_alias_opposite_roles_rejected(self):
        r=fixture();r['integration']=dict(windows=[],claims=[claim()],freeze=None);l=ledger()
        e=copy.deepcopy(l['events'][0]);e['event_id']='E2';l['events'].append(e)
        r['integration']['claims'][0]['excluding_event_refs']=['E2']
        with self.assertRaises(ValueError):run_ssar_pipeline(r,m27_ledger=l)
    def test_root_forgery_and_duplicate_profile_contact_rejected(self):
        r=fixture()
        with self.assertRaises(ValueError):run_ssar_pipeline(r,canonical_roots=[])
        r['profiles']['s1']=s1('CERES')
        known=copy.deepcopy(r['profiles']['liminal']['core_roots']);known[0]['point_ids']=['SUN','MOON']
        with self.assertRaises(ValueError):run_ssar_pipeline(r,canonical_roots=known)
    def test_nine_ablations_and_fixed_budget_controls_deterministic_no_pvalues(self):
        r=fixture();r['profiles']['lots']=lots();r['profiles']['lots']['core_roots'][0]['root_id']='R1'
        r['profiles']['lots']['contacts'][0]['core_root_refs']=['R1'];r['profiles']['lots']['core_roots'][0]['core_evidence_ids']=['CORE1']
        core={'unchanged':123};before=copy.deepcopy(core)
        a=run_ablations(r,core_snapshot=core);self.assertEqual([x['id'] for x in a['runs']],list(ABLATIONS))
        self.assertTrue(all(x['core_invariant'] for x in a['runs']));self.assertEqual(core,before)
        kwargs=dict(seed=20261002,simulations=3,core_snapshot=core)
        a=run_synthetic_null(r,**kwargs);self.assertEqual(a,run_synthetic_null(r,**kwargs))
        self.assertEqual(a['completed_simulations'],3);self.assertIsNone(a['p_values']);self.assertFalse(a['confirmatory_inference_allowed'])
    def test_forged_canonical_claim_rejected_and_summary_absent_is_empty(self):
        out=run_ssar_pipeline(fixture());out['structure']['complexes'][0]['qualified_complex']=True
        with self.assertRaises(ValueError):validate_canonical_ssar(out)
        self.assertEqual(render_ssar_summary({}),'')

class AdversarialFinishTests(unittest.TestCase):
    def test_clock_zero_geometry_unknown_orb_boundary_and_invalid_calendar(self):
        r=integrated();clock=r['integration']['windows'][0]['clocks'][0]
        clock['longitude']=0;clock['target_longitude']=1
        self.assertTrue(run_ssar_pipeline(r)['integration']['temporal'][0]['qualified_temporal_complex'])
        clock['target_longitude']=1.00001
        self.assertFalse(run_ssar_pipeline(r)['integration']['temporal'][0]['qualified_temporal_complex'])
        clock['date']='2020-02-31'
        with self.assertRaises(ValueError):run_ssar_pipeline(r)
    def test_canonical_forged_good_groups_and_profile_metadata_cannot_escape_reproduction(self):
        out=run_ssar_pipeline(fixture());c=next(c for c in out['structure']['complexes'] if c['id']==COMPLEX)
        c['assessments']['functional_interpretation']['status']='CONTRADICTED'
        with self.assertRaises(ValueError):validate_canonical_ssar(out)
        out=run_ssar_pipeline(fixture());out['profiles']['liminal']['catalog_hash']='0'*64
        with self.assertRaises(ValueError):validate_canonical_ssar(out)
    def test_conservative_cross_dependency_defeats_two_profiles_and_broken_refs(self):
        r=fixture();r['cross_edges']=[dict(a='liminal:U:A1',b='liminal:U:A2',relation='UNKNOWN',rule_id='SSAR_DECLARED_UNKNOWN_V1')]
        out=run_ssar_pipeline(r);c=next(c for c in out['structure']['complexes'] if c['id']==COMPLEX)
        self.assertFalse(c['qualified_complex']);self.assertEqual(len(c['effective_group_refs']),1)
        r['cross_edges'][0]['b']='BAD'
        with self.assertRaises(ValueError):run_ssar_pipeline(r)
    def test_all_four_control_methods_replay_windows_and_missing_precision(self):
        r=integrated()
        for method in ('TARGET_ROTATION','CLOCK_DATE_SHIFT','EVENT_DATE_PERMUTATION','PRECISION_LOSS'):
            out=run_synthetic_null(r,seed=42,simulations=2,core_snapshot={'core':1},m27_ledger=ledger(),method=method)
            self.assertEqual(out['completed_simulations'],2);self.assertFalse(out['confirmatory_inference_allowed'])
        with self.assertRaises(ValueError):run_synthetic_null(r,seed=1,simulations=0,core_snapshot={})
    def test_missing_components_and_search_incomplete_remain_not_evaluable(self):
        for change in ('member','search','precision'):
            r=fixture()
            if change=='member':r['profiles']['liminal']['observations'].pop();r['profiles']['liminal']['complexes']=[]
            elif change=='search':r['complex_search'][0]['search_complete']=False
            else:r['profiles']['liminal']['observations'][0]['robustness']['input_precision_sufficient']=False
            out=run_ssar_pipeline(r);c=next(c for c in out['structure']['complexes'] if c['id']==COMPLEX)
            self.assertFalse(c['qualified_complex']);self.assertEqual(c['assessments']['functional_interpretation']['status'],'NOT_EVALUABLE')
    def test_retrospective_labels_and_prospective_declaration_stay_unverified(self):
        r=integrated();r['integration']['freeze']['mode']='PROSPECTIVELY_DECLARED'
        out=run_ssar_pipeline(r)
        self.assertEqual(out['integration']['temporal'][0]['prediction_class'],'PROSPECTIVELY_DECLARED_UNVERIFIED')
        self.assertEqual(out['external_validation_status'],'NOT_PERFORMED')

class FactGroupTests(unittest.TestCase):
    def test_subject_order_and_alias_ids_do_not_create_independent_facts(self):
        r=fixture();r['integration']=dict(windows=[],claims=[claim()],freeze=None);l=ledger();l['events'][0].pop('fact_key')
        alias=copy.deepcopy(l['events'][0]);alias['event_id']='ALIAS';alias['subjects'].reverse();l['events'].append(alias)
        r['integration']['claims'][0]['support_event_refs'].append('ALIAS')
        out=run_ssar_pipeline(r,m27_ledger=l);d=out['integration']['documentary'][0]
        self.assertEqual(d['effective_fact_group_count'],1);self.assertEqual(len(out['integration']['shared_events']),1)
        self.assertNotIn('independent_fact_count',d)
