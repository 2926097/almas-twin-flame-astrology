"""Pruebas de especificidad relativa, procedencia y firewall ontológico PU-M."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from jsonschema import Draft202012Validator
from almas_tfa.metaphysical_singularity import (
    _hash, assess_metaphysical_singularity, build_singularity_signature,
    load_metaphysical_singularity_policy, render_metaphysical_singularity_summary,
)
ROOT=Path(__file__).resolve().parents[1]

def case(ids=('A','B'),strength=0.9):
    c={'evidence':[{'root_id':'R1','core_eligible':True,'strength':strength,'dependency_families':['SYN']}],
       'semantic_motifs':{'policy_id':'ALMAS_SEMANTIC_MOTIF_V2','assignments':[{'root_id':'R1','primary_motif':'RELATIONAL_COHERENCE'}]},
       'assembly':{'policy_id':'ALMAS_CANONICAL_ASSEMBLY_V2'},'natal_context':{'subjects':{i:{} for i in ids}},
       'indices':{'IRC':90,'ICC':100},'astronomy_backend':{'backend_id':'SYNTHETIC_TEST_ONLY'}}
    return {'subject_ids':list(ids),'canonical':c,'canonical_fingerprint':_hash(c),
            'protocol':{'analysis_policy_fingerprint':'0'*64,'house_system':'SYNTHETIC','time_quality':'SYNTHETIC_EQUIVALENT',
                        'signature_policy':'CORE_PRIMARY_MOTIF_MAX_V1'}}

def refresh(c):c['canonical_fingerprint']=_hash(c['canonical'])

def request():
    target=case(); comps=[case(('A','C'),0.2),case(('B','D'),0.3)]
    features=load_metaphysical_singularity_policy()['feature_ids']
    template={f:(0.9 if f=='RELATIONAL_COHERENCE' else 0) for f in features}
    p={'template':template,'weights':{f:1 for f in features},'equivalence_margin':0.02,'minimum_irc':0.7,'selection_record_ref':'SYNTHETIC_SELECTION'}
    pairs=sorted([sorted(x['subject_ids']) for x in [target]+comps])
    return {'target':target,'comparators':comps,'comparison_policy':p,
            'source_refs':['pu_summit_soulmates_twin_flames'],
            'preregistration':{'status':'DECLARED_FROZEN','record_ref':'SYNTHETIC_PROTOCOL_NOT_AUTHENTICATED',
                               'comparison_fingerprint':_hash({'policy':p,'pairs':pairs})}}

class MetaphysicalSingularityTests(unittest.TestCase):
    def test_favourable_margin_is_compatible_only(self):
        r=assess_metaphysical_singularity(request())
        self.assertEqual(r['PU_R']['state'],'COMPATIBLE')
        self.assertEqual(r['PU_O']['state'],'NOT_EVALUABLE')
        self.assertIsNone(r['pu_score'])
        self.assertFalse(r['production_scores_affected'])
        self.assertFalse(r['PU_R']['preregistration_authenticated'])
    def test_same_comparator_contradicts_only_proxy(self):
        q=request();q['comparators'][0]=case(('A','C'),0.9)
        r=assess_metaphysical_singularity(q)
        self.assertEqual(r['PU_R']['state'],'CONTRADICTED')
        self.assertEqual(r['ontology_effect'],'NONE')
    def test_no_comparators_is_missing_not_zero(self):
        q=request();q['comparators']=[]
        r=assess_metaphysical_singularity(q)
        self.assertEqual(r['PU_R']['state'],'NOT_EVALUABLE')
        self.assertIsNone(r['PU_R']['score'])
    def test_low_irc_blocks(self):
        q=request();q['target']['canonical']['indices']['IRC']=12.8;refresh(q['target'])
        self.assertEqual(assess_metaphysical_singularity(q)['PU_R']['state'],'NOT_EVALUABLE')
    def test_missing_quality_blocks(self):
        q=request();q['comparators'][0]['canonical']['indices']['IRC']=None;refresh(q['comparators'][0])
        self.assertIn('MISSING_QUALITY',assess_metaphysical_singularity(q)['PU_R']['blockers'])
    def test_one_sided_network_is_insufficient(self):
        q=request();q['comparators']=q['comparators'][:1]
        self.assertIn('ONE_SIDED_NETWORK',assess_metaphysical_singularity(q)['PU_R']['blockers'])
    def test_unfrozen_policy_insufficient(self):
        q=request();q['preregistration']['status']='DRAFT'
        self.assertEqual(assess_metaphysical_singularity(q)['PU_R']['state'],'INSUFFICIENT')
    def test_hash_does_not_allow_post_selection_overrides(self):
        q=request();q['comparison_policy']['equivalence_margin']=0.01
        self.assertIn('NO_MATCHING_PREREGISTRATION',assess_metaphysical_singularity(q)['PU_R']['blockers'])
    def test_protocol_mismatch_rejected(self):
        q=request();q['comparators'][0]['protocol']['house_system']='OTHER'
        with self.assertRaises(ValueError):assess_metaphysical_singularity(q)
    def test_fingerprint_mismatch_rejected(self):
        q=request();q['target']['canonical']['indices']['IRC']=50
        with self.assertRaises(ValueError):assess_metaphysical_singularity(q)
    def test_duplicate_pair_rejected(self):
        q=request();q['comparators'].append(deepcopy(q['comparators'][0]))
        with self.assertRaises(ValueError):assess_metaphysical_singularity(q)
    def test_identity_mismatch_rejected(self):
        q=request();q['target']['subject_ids']=['A','Z']
        with self.assertRaises(ValueError):assess_metaphysical_singularity(q)
    def test_unrelated_comparator_rejected(self):
        q=request();q['comparators'][0]=case(('C','D'))
        with self.assertRaises(ValueError):assess_metaphysical_singularity(q)
    def test_unknown_source_rejected(self):
        with self.assertRaises(ValueError):assess_metaphysical_singularity({'source_refs':['invented']})
    def test_duplicate_sources_have_no_effect(self):
        q=request();a=assess_metaphysical_singularity(q);q['source_refs']*=30;b=assess_metaphysical_singularity(q)
        self.assertEqual(a['PU_D'],b['PU_D']);self.assertEqual(a['PU_R'],b['PU_R'])
    def test_unknown_tradition_is_source_gap(self):
        r=assess_metaphysical_singularity({'model_ids':['ZIVUG'],'source_refs':['pu_summit_soulmates_twin_flames']})
        self.assertTrue(all(x['doctrine_state']=='NOT_EVALUABLE' for x in r['PU_D']['rows']))
    def test_input_not_mutated(self):
        q=request();before=deepcopy(q);assess_metaphysical_singularity(q);self.assertEqual(q,before)
    def test_support_only_cannot_create_signature(self):
        q=case();q['canonical']['evidence'][0]['core_eligible']=False;refresh(q)
        self.assertEqual(build_singularity_signature(q)['features']['RELATIONAL_COHERENCE'],0)
    def test_duplicate_root_rejected(self):
        q=case();q['canonical']['evidence']*=2;refresh(q)
        with self.assertRaises(ValueError):build_singularity_signature(q)
    def test_unresolved_assignment_rejected(self):
        q=case();q['canonical']['semantic_motifs']['assignments'][0]['root_id']='UNKNOWN';refresh(q)
        with self.assertRaises(ValueError):build_singularity_signature(q)
    def test_missing_assignment_cannot_turn_into_zero(self):
        q=case();q['canonical']['semantic_motifs']['assignments']=[];refresh(q)
        with self.assertRaises(ValueError):build_singularity_signature(q)
    def test_nonfinite_rejected(self):
        for v in [float('nan'),float('inf'),True,-1]:
            q=request();q['comparison_policy']['equivalence_margin']=v
            with self.subTest(v=v),self.assertRaises(ValueError):assess_metaphysical_singularity(q)
    def test_weights_required(self):
        q=request();q['comparison_policy']['weights']={}
        with self.assertRaises(ValueError):assess_metaphysical_singularity(q)
    def test_source_count_does_not_create_numeric_pu(self):
        q={'source_refs':['pu_summit_soulmates_twin_flames']*200}
        r=assess_metaphysical_singularity(q);self.assertIsNone(r['pu_score']);self.assertEqual(r['PU_O']['state'],'NOT_EVALUABLE')
    def test_hypothesis_cannot_support_documentary_correspondence(self):
        q={'value_observations':[{'value_id':'SHARED_IDENTITY','model_id':'TWIN_FLAME_MODEL','status':'SUPPORTED','epistemic_class':'E_PROJECT_HYPOTHESIS','evidence_refs':['E1'],'dependency_group':'G1'}]}
        with self.assertRaises(ValueError):assess_metaphysical_singularity(q)
    def test_documentary_correspondence_keeps_origin_blocked(self):
        q={'value_observations':[{'value_id':'SPIRITUAL_PURPOSE','model_id':'TWIN_FLAME_MODEL','status':'SUPPORTED','epistemic_class':'A_DOCUMENTARY','evidence_refs':['DOC1'],'dependency_group':'G1'}]}
        r=assess_metaphysical_singularity(q);self.assertEqual(r['PU_O']['state'],'NOT_EVALUABLE')
    def test_case_label_cannot_influence_result(self):
        q=request();q['target']['canonical']['emic_label']='twin-flame';refresh(q['target']);a=assess_metaphysical_singularity(q)
        q['target']['canonical']['emic_label']='ordinary-friendship';refresh(q['target']);b=assess_metaphysical_singularity(q)
        for k in ['state','target_distance','minimum_margin']:self.assertEqual(a['PU_R'][k],b['PU_R'][k])
    def test_schema_valid_and_rejects_score_promotion(self):
        schema=json.loads((ROOT/'schemas/metaphysical-singularity.schema.json').read_text())
        r=assess_metaphysical_singularity(request());Draft202012Validator(schema).validate(r)
        r['pu_score']=100;self.assertTrue(list(Draft202012Validator(schema).iter_errors(r)))
        with self.assertRaises(ValueError):render_metaphysical_singularity_summary(r)
    def test_resources_match_public_registries(self):
        for name in ['values','source-map']:
            p=f'metaphysical-singularity-{name}.json'
            self.assertEqual(json.loads((ROOT/'reference'/p).read_text()),json.loads((ROOT/'src/almas_tfa/data'/p).read_text()))
    def test_all_verified_contexts_preserve_model_requirements(self):
        sources=json.loads((ROOT/'reference/metaphysical-singularity-source-map.json').read_text())['sources']
        models=['TWIN_FLAME_MODEL','SOULMATE_MODEL','SOUL_FAMILY_GROUP','MONADIC_COMMON_SOURCE','SPLIT_SOUL','ZIVUG']
        baseline=assess_metaphysical_singularity({'model_ids':models,'source_refs':[sources[0]['id']]})
        expanded=assess_metaphysical_singularity({'model_ids':models,'source_refs':[s['id'] for s in sources]})
        for key in ['PU_D','PU_R','PU_O','pu_score','ontology_effect','production_scores_affected']:
            self.assertEqual(baseline[key],expanded[key])
    def test_contemporary_books_do_not_become_ontology_or_case_evidence(self):
        r=assess_metaphysical_singularity({'source_refs':['pu_dispenza_deja_ser','pu_dispenza_sobrenatural','pu_joseph_sabiduria_ii']})
        self.assertTrue(all(x['doctrine_state']=='NOT_EVALUABLE' and x['case_correspondence']['status']=='NOT_EVALUABLE' for x in r['PU_D']['rows']))
        self.assertEqual(r['PU_O']['state'],'NOT_EVALUABLE')
        self.assertIsNone(r['pu_score'])
    def test_cli_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp=Path(tmp)/'input.json';out=Path(tmp)/'output.json';inp.write_text(json.dumps(request()))
            p=subprocess.run([sys.executable,'-m','almas_tfa.metaphysical_singularity_cli',str(inp),'-o',str(out)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(out.read_text()),assess_metaphysical_singularity(request()))
    def test_cli_rejects_invalid_without_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp=Path(tmp)/'input.json';out=Path(tmp)/'output.json';inp.write_text('{"pu_score":100}')
            p=subprocess.run([sys.executable,'-m','almas_tfa.metaphysical_singularity_cli',str(inp),'-o',str(out)],capture_output=True,text=True)
            self.assertEqual(p.returncode,2);self.assertFalse(out.exists())
if __name__=='__main__':unittest.main()
