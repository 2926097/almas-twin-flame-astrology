"""Controles sintéticos congelados; ningún caso privado se usa para calibrar."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from almas_tfa.surrender_vestal import (
    assess_surrender_vestal, evaluate_surrender_requests,
    surrender_vestal_report_paragraphs, validate_surrender_vestal_result,
)

ROOT = Path(__file__).resolve().parents[1]


def observation(code, value=True, *, ident=None, subject='SYNTHETIC-A', dated='2030-01-10'):
    return dict(observation_id=ident or code, subject_id=subject, code=code, value=value,
                date=dated, source_refs=['SYNTHETIC-SELF-REPORT'],
                documentary_quality='DQ2_DIRECT_SELF_REPORT', fact_interpretation_separated=True)


def request(*codes):
    return dict(subject_id='SYNTHETIC-A', window_start='2030-01-01', window_end='2030-01-31',
                observations=[observation(code) for code in codes], structural_roots=[], temporal_activations=[])


def active_request():
    return request('PURSUIT_CEASED', 'OWN_ACTIVITIES_RECOVERED', 'AUTONOMY_RECOVERED')


def add_activation(data, ident='T1', root='R1', family='VESTA', technique='TRANSIT', dep=None):
    if root not in {item['root_id'] for item in data['structural_roots']}:
        data['structural_roots'].append(dict(root_id=root, subject_id=data['subject_id'], source_refs=['SYNTHETIC-GEOMETRY'], verified=True))
    data['temporal_activations'].append(dict(signal_id=ident, root_id=root, subject_id=data['subject_id'],
        technique=technique, symbolic_family=family, date='2030-01-10', source_refs=['SYNTHETIC-GEOMETRY'],
        dependency_keys=[dep or root], orb=0.2, declared_orb=1.0, aspect_policy_ref='SYNTHETIC-ORB-V1',
        verified=True, temporal_correspondence_documented=True))


class SurrenderVestalTests(unittest.TestCase):
    def test_empty_unknown_not_absent(self):
        result=assess_surrender_vestal(request())
        self.assertEqual(result['vestal_withdrawal']['state'],'NOT_EVALUABLE')
        self.assertIsNone(result['sexual_observations']['celibacy']['value'])

    def test_isolated_vesta_compatible_never_supported(self):
        data=request(); add_activation(data)
        result=assess_surrender_vestal(data)
        self.assertEqual(result['astrological_correspondence']['status'],'COMPATIBLE')
        self.assertEqual(result['vestal_withdrawal']['state'],'NOT_EVALUABLE')

    def test_convergent_vesta_saturn_documented_recentring(self):
        data=active_request();add_activation(data);add_activation(data,'T2','R2','SATURN','DIRECTION')
        result=assess_surrender_vestal(data)
        self.assertEqual(result['vestal_withdrawal']['state'],'ACTIVE')
        self.assertEqual(result['astrological_correspondence']['status'],'SUPPORTED')

    def test_celibacy_with_pursuit_not_integration(self):
        result=assess_surrender_vestal(request('CELIBACY_CHOSEN','PURSUIT_PERSISTENT','WAITING_FOR_UNION'))
        self.assertTrue(result['sexual_observations']['celibacy']['value'])
        self.assertNotEqual(result['vestal_withdrawal']['state'],'INTEGRATED')
        self.assertIn('WAITING_CELIBACY',result['phenotypes'])

    def test_noncelibate_recentring_supported_without_astrology(self):
        data=active_request();data['observations'].append(observation('CELIBACY_CHOSEN',False))
        result=assess_surrender_vestal(data)
        self.assertEqual(result['vestal_withdrawal']['status'],'SUPPORTED')
        self.assertFalse(result['sexual_observations']['celibacy']['value'])
        self.assertEqual(result['astrological_correspondence']['status'],'NOT_EVALUABLE')

    def test_other_subject_never_inferred(self):
        data=request();data['observations'].append(observation('CELIBACY_CHOSEN',subject='SYNTHETIC-B'))
        result=assess_surrender_vestal(data)
        self.assertIsNone(result['sexual_observations']['celibacy']['value'])
        self.assertEqual(result['rejected_observations'][0]['reasons'],['OTHER_SUBJECT'])

    def test_activation_never_predicts_outcome(self):
        data=active_request();add_activation(data);add_activation(data,'T2','R2','SATURN','DIRECTION')
        result=assess_surrender_vestal(data)
        self.assertEqual(result['outcome'],{'status':'NOT_EVALUABLE','value':None})
        self.assertEqual(result['ontology_effect'],'NONE')
        self.assertFalse(result['iat_modified'])
        self.assertFalse(result['structural_scoring_modified'])

    def test_three_chiron_passes_collapse_one_root(self):
        data=active_request()
        for i in range(3):add_activation(data,f'T{i}','CHIRON-ROOT','CHIRON','TRANSIT')
        result=assess_surrender_vestal(data)
        self.assertEqual(result['dependencies'],[['T0','T1','T2']])
        self.assertNotEqual(result['astrological_correspondence']['status'],'SUPPORTED')

    def test_transitive_dependencies(self):
        data=active_request()
        add_activation(data,'T1','R1',dep='D1');add_activation(data,'T2','R2','SATURN','DIRECTION',dep='D2')
        add_activation(data,'T3','R3','CHIRON','SOLAR_ARC',dep='D1')
        data['temporal_activations'][-1]['dependency_keys'].append('D2')
        self.assertEqual(len(assess_surrender_vestal(data)['dependencies']),1)

    def test_symbolic_families_not_technique_independence(self):
        data=active_request();add_activation(data);add_activation(data,'T2','R2','SATURN','TRANSIT')
        self.assertEqual(assess_surrender_vestal(data)['astrological_correspondence']['status'],'COMPATIBLE')

    def test_same_root_different_techniques_no_promotion(self):
        data=active_request();add_activation(data);add_activation(data,'T2','R1','SATURN','DIRECTION')
        self.assertEqual(assess_surrender_vestal(data)['astrological_correspondence']['status'],'COMPATIBLE')

    def test_solar_arc_and_progression_share_clock(self):
        data=active_request();add_activation(data,technique='SOLAR_ARC');add_activation(data,'T2','R2','SATURN','SECONDARY_PROGRESSION')
        self.assertEqual(assess_surrender_vestal(data)['astrological_correspondence']['status'],'COMPATIBLE')

    def test_draconic_only_corroborative(self):
        data=active_request();add_activation(data);add_activation(data,'T2','R2','SATURN','DRACONIC')
        self.assertEqual(assess_surrender_vestal(data)['astrological_correspondence']['status'],'COMPATIBLE')

    def test_strong_counterevidence_blocks_supported(self):
        data=active_request();data['observations'].append(observation('INTERNAL_COMPULSION'))
        result=assess_surrender_vestal(data)
        self.assertEqual(result['vestal_withdrawal']['status'],'INSUFFICIENT')

    def test_reactive_abstinence_not_surrender(self):
        result=assess_surrender_vestal(request('ABSTINENCE_DECLARED','REACTIVE_ABSTINENCE'))
        self.assertIn('REACTIVE_ABSTINENCE',result['phenotypes'])
        self.assertEqual(result['vestal_withdrawal']['status'],'CONTRADICTED')

    def test_explicit_absence_supported_as_negative(self):
        result=assess_surrender_vestal(request('WITHDRAWAL_ABSENT'))
        self.assertEqual(result['vestal_withdrawal']['state'],'ABSENT')
        self.assertEqual(result['vestal_withdrawal']['status'],'CONTRADICTED')

    def test_conflicting_observations_not_silently_chosen(self):
        data=active_request();data['observations'].append(observation('PURSUIT_CEASED',False,ident='CONFLICT'))
        self.assertEqual(assess_surrender_vestal(data)['vestal_withdrawal']['status'],'INSUFFICIENT')

    def test_domains_independent(self):
        result=assess_surrender_vestal(request('PURSUIT_CEASED','CHECKING_REDUCED'))
        self.assertEqual(result['surrender']['behavioral']['state'],'ACTIVE')
        self.assertEqual(result['surrender']['emotional']['state'],'NOT_EVALUABLE')

    def test_integration_requires_four_domains_and_dates(self):
        data=active_request()
        for code in ('CHECKING_REDUCED','OUTCOMES_ACCEPTED','EROTIC_DECENTERING','SUBSTITUTION_REDUCED','LABEL_NEED_REDUCED','UNCERTAINTY_ACCEPTED'):
            data['observations'].append(observation(code,dated='2030-01-20'))
        self.assertEqual(assess_surrender_vestal(data)['vestal_withdrawal']['state'],'INTEGRATED')
        for item in data['observations']:item['date']='2030-01-10'
        self.assertEqual(assess_surrender_vestal(data)['vestal_withdrawal']['state'],'ACTIVE')

    def test_out_of_window_rejected(self):
        data=request();data['observations'].append(observation('CELIBACY_CHOSEN',dated='2030-02-01'))
        self.assertIsNone(assess_surrender_vestal(data)['sexual_observations']['celibacy']['value'])

    def test_low_quality_rejected(self):
        data=active_request();data['observations'][0]['documentary_quality']='DQ4_INTERPRETATION'
        self.assertNotEqual(assess_surrender_vestal(data)['vestal_withdrawal']['status'],'SUPPORTED')

    def test_unverified_root_excludes_activation(self):
        data=request();add_activation(data);data['structural_roots'][0]['verified']=False
        result=assess_surrender_vestal(data)
        self.assertFalse(result['temporal_activations'])

    def test_outside_orb_rejected(self):
        data=request();add_activation(data);data['temporal_activations'][0]['orb']=1.01
        self.assertFalse(assess_surrender_vestal(data)['temporal_activations'])

    def test_invalid_numeric_and_dates_rejected(self):
        for bad in (float('nan'),float('inf'),True,-1):
            data=request();add_activation(data);data['temporal_activations'][0]['orb']=bad
            with self.assertRaises(ValueError):assess_surrender_vestal(data)
        data=request();data['window_start']='2030-02-30'
        with self.assertRaises(ValueError):assess_surrender_vestal(data)

    def test_duplicate_ids_rejected(self):
        data=request('CELIBACY_CHOSEN');data['observations']*=2
        with self.assertRaises(ValueError):assess_surrender_vestal(data)

    def test_input_immutable_and_order_invariant(self):
        data=active_request();add_activation(data);add_activation(data,'T2','R2','SATURN','DIRECTION')
        before=deepcopy(data);result=assess_surrender_vestal(data)
        self.assertEqual(data,before)
        data['temporal_activations'].reverse();data['observations'].reverse()
        self.assertEqual(result,assess_surrender_vestal(data))

    def test_semantic_validation_blocks_tampered_ontology_and_state(self):
        result=assess_surrender_vestal(active_request());validate_surrender_vestal_result(result)
        for key,value in (('ontology_effect','TWIN_FLAME'),('iat_modified',True)):
            changed=deepcopy(result);changed[key]=value
            with self.assertRaises(ValueError):validate_surrender_vestal_result(changed)
        result['vestal_withdrawal']['state']='INTEGRATED'
        with self.assertRaises(ValueError):validate_surrender_vestal_result(result)

    def test_schema_and_report(self):
        from jsonschema import Draft202012Validator
        data=active_request();add_activation(data)
        result=assess_surrender_vestal(data)
        for filename,value in (('surrender-vestal-request.schema.json',data),('surrender-vestal-output.schema.json',result)):
            schema=json.loads((ROOT/'schemas'/filename).read_text())
            Draft202012Validator.check_schema(schema);Draft202012Validator(schema).validate(value)
        self.assertEqual(len(surrender_vestal_report_paragraphs(result)),4)

    def test_personal_report_and_semantic_gate(self):
        from test_personal_reporting import canonical
        from almas_tfa.personal_reporting import build_personal_report_document_model,validate_personal_canonical
        data=canonical();data['surrender_vestal']=evaluate_surrender_requests([active_request()])
        report=build_personal_report_document_model(data)
        self.assertEqual(report['sections'][-1]['section_id'],'P13_SURRENDER_VESTAL')
        data['surrender_vestal']['SYNTHETIC-A']['ontology_effect']='LG'
        self.assertFalse(validate_personal_canonical(data)['reportable'])

    def test_personal_request_pipeline_and_subject_mismatch(self):
        from test_personal_request_pipeline import request as personal_request, FakePersonalBackend
        from almas_tfa.personal_request_pipeline import build_personal_canonical_from_request,PersonalRequestError
        data=personal_request();sv=active_request();sv['subject_id']='SYNTHETIC-REQUEST'
        for item in sv['observations']:item['subject_id']=sv['subject_id']
        data['surrender_vestal']=sv
        result=build_personal_canonical_from_request(data,backend=FakePersonalBackend())
        self.assertIn('SYNTHETIC-REQUEST',result['surrender_vestal'])
        data['surrender_vestal']['subject_id']='OTHER'
        with self.assertRaises(PersonalRequestError):build_personal_canonical_from_request(data,backend=FakePersonalBackend())

    def test_m27_adapter_requires_actual_event(self):
        data=active_request()
        result=evaluate_surrender_requests([data],documentary_events={'events':[]})['SYNTHETIC-A']
        self.assertEqual(result['vestal_withdrawal']['status'],'NOT_EVALUABLE')
        events=[]
        for obs in data['observations']:
            obs['event_ref']=obs['observation_id']
            events.append(dict(event_id=obs['event_ref'],date=obs['date'],date_precision='EXACT_DATE',subjects=['SYNTHETIC-A'],record_status='ACTIVE',documentary_quality_contract_met=True,date_precision_contract_met=True,fact_interpretation_separated=True,source_refs=obs['source_refs'],documentary_quality=obs['documentary_quality']))
        result=evaluate_surrender_requests([data],documentary_events={'events':events})['SYNTHETIC-A']
        self.assertEqual(result['vestal_withdrawal']['status'],'SUPPORTED')
        events[0]['record_status']='SUPERSEDED'
        result=evaluate_surrender_requests([data],documentary_events={'events':events})['SYNTHETIC-A']
        self.assertNotEqual(result['vestal_withdrawal']['status'],'SUPPORTED')

    def test_explicit_absence_blocks_astrological_support(self):
        data=active_request();data['observations'].append(observation('WITHDRAWAL_ABSENT'))
        add_activation(data);add_activation(data,'T2','R2','SATURN','DIRECTION')
        result=assess_surrender_vestal(data)
        self.assertEqual(result['astrological_correspondence']['status'],'INSUFFICIENT')
        self.assertTrue(result['counterevidence'])

    def test_sexual_conflict_does_not_change_recentring(self):
        for code in ('CELIBACY_CHOSEN','ABSTINENCE_DECLARED'):
            data=active_request();data['observations'] += [observation(code),observation(code,False,ident='CONFLICT')]
            result=assess_surrender_vestal(data)
            self.assertEqual(result['vestal_withdrawal']['status'],'SUPPORTED')
            key='celibacy' if code=='CELIBACY_CHOSEN' else 'abstinence'
            self.assertEqual(result['sexual_observations'][key]['status'],'INSUFFICIENT')

    def test_noncanonical_dates_cannot_fabricate_integration(self):
        data=active_request();data['observations'][0]['date']='20300110'
        with self.assertRaises(ValueError):assess_surrender_vestal(data)

    def test_semantic_validator_enforces_output_shape(self):
        result=assess_surrender_vestal(active_request())
        changed=deepcopy(result);changed['iem_modified']=True
        with self.assertRaises(ValueError):validate_surrender_vestal_result(changed)
        changed=deepcopy(result);changed.pop('rejected_observations')
        with self.assertRaises(ValueError):validate_surrender_vestal_result(changed)
        changed=deepcopy(result);changed['iat_modified']=0
        with self.assertRaises(ValueError):validate_surrender_vestal_result(changed)
        changed=deepcopy(result);changed['rejected_activations']='INVALID'
        with self.assertRaises(ValueError):validate_surrender_vestal_result(changed)

    def test_m27_handler_links_documentary_extension(self):
        from test_temporal_handlers import TestDocumentaryEvents,context
        from almas_tfa.temporal_handlers import m27_dated_events
        helper=TestDocumentaryEvents();helper.setUp();data=active_request();events=[]
        for obs in data['observations']:
            obs['event_ref']=obs['observation_id']
            events.append(helper.event(obs['event_ref'],subjects=['SYNTHETIC-A'],date=obs['date'],documentary_quality='DQ2_DIRECT_SELF_REPORT',source_refs=obs['source_refs'],fact_statement='Observación sintética de recentrado.'))
        raw={'documentary_event_ledger':{'schema_version':'1.0.0','analysis_freeze_ref':'SYNTHETIC-FREEZE','events':events},'surrender_vestal_requests':[data]}
        result=m27_dated_events(context('M27',raw,helper.canonical))
        self.assertEqual(result.canonical_updates['surrender_vestal']['SYNTHETIC-A']['vestal_withdrawal']['status'],'SUPPORTED')
        self.assertFalse(result.payload['structural_mutation_allowed'])

    def test_canonical_assembly_retains_extension_and_indices(self):
        from test_canonical_assembly import canonical_base,prior_all
        from test_canonical_schema_validation import canonical_validator
        from almas_tfa.canonical_assembly import assemble_canonical_analysis
        base=canonical_base();before=assemble_canonical_analysis(base,prior_all())['canonical_analysis']
        base['surrender_vestal']=evaluate_surrender_requests([active_request()])
        after=assemble_canonical_analysis(base,prior_all())['canonical_analysis']
        canonical_validator().validate(after)
        self.assertEqual(before['indices'],after['indices'])
        self.assertEqual(before['models'],after['models'])
        self.assertEqual(base['surrender_vestal'],after['surrender_vestal'])

    def test_relational_report_gate_blocks_invalid_extension(self):
        from test_canonical_schema_validation import valid_canonical_analysis
        from test_temporal_handlers import context
        from almas_tfa.report_gate_handlers import m30_report_gate
        from almas_tfa.report_model_handlers import m31_report
        data=valid_canonical_analysis();data['surrender_vestal']=evaluate_surrender_requests([active_request()])
        result=m30_report_gate(context('M30',{'canonical_analysis':data},{}))
        self.assertTrue(result.payload['reportable'])
        report=m31_report(context('M31',{},dict(canonical_analysis=data,report_gate=result.payload)))
        self.assertIn('surrender_vestal',report.payload['sections'][-1]['available_paths'])
        data['surrender_vestal']['SYNTHETIC-A']['score_created']=True
        result=m30_report_gate(context('M30',{'canonical_analysis':data},{}))
        self.assertFalse(result.payload['reportable'])

    def test_source_registry_matches_schema(self):
        from jsonschema import Draft202012Validator
        schema=json.loads((ROOT/'schemas/source-registry.schema.json').read_text())
        registry=json.loads((ROOT/'reference/source-registry.json').read_text())
        Draft202012Validator(schema).validate(registry)

    def test_m27_unknown_date_degrades_without_crash(self):
        data=active_request();events=[]
        for obs in data['observations']:
            obs['event_ref']=obs['observation_id']
            events.append(dict(event_id=obs['event_ref'],date=None,date_precision='UNKNOWN',subjects=['SYNTHETIC-A'],record_status='ACTIVE',documentary_quality_contract_met=True,date_precision_contract_met=True,fact_interpretation_separated=True,source_refs=obs['source_refs'],documentary_quality=obs['documentary_quality']))
        result=evaluate_surrender_requests([data],documentary_events={'events':events})['SYNTHETIC-A']
        self.assertEqual(result['vestal_withdrawal']['status'],'NOT_EVALUABLE')

    def test_same_subject_request_duplicate_rejected(self):
        with self.assertRaises(ValueError):evaluate_surrender_requests([request(),request()])


if __name__=='__main__':unittest.main()
