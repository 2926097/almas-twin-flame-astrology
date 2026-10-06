"""Contrato público temporal: datos sintéticos, aislamiento y rechazo explícito."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from almas_tfa.atacires.api import calculate_uniform_cycle
from almas_tfa.atacires.adapters import build_uniform_cycle_request
from almas_tfa.atacires.provenance import fingerprint_payload
from almas_tfa.atacires.robustness import assess_robustness
from almas_tfa.integrations.atacires_temporal import make_atacires_temporal_handler
from almas_tfa.handlers import configured_handlers, default_handlers
from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.orchestrator import Orchestrator
from almas_tfa.temporal_handlers import m26_temporal_activation
from almas_tfa.canonical_assembly import assemble_canonical_analysis
from test_canonical_assembly import canonical_base, prior_all
from test_canonical_schema_validation import canonical_validator

ROOT = Path(__file__).resolve().parents[1]

def subject():
    return dict(id='A', birth_date='2000-01-01', birth_time='00:00:00',
                timezone='Etc/UTC', latitude=0., longitude=0., time_reliability='EXACT')

def chart():
    return dict(subject_id='A', timed=True, backend_id='SYNTHETIC', backend_version='1',
                backend_provenance={'fixture': 'synthetic-only'}, zodiac='TROPICAL',
                positions={'SUN': {'longitude': 0.}, 'MOON': {'longitude': 90.}},
                angles={'ASC': 45.}, metadata={'utc_instant':'2000-01-01T00:00:00Z',
                'latitude':0., 'longitude':0., 'house_system_requested':'P'})

def settings(**changes):
    d=dict(start_utc='2000-01-01T00:00:00Z',end_utc='2002-01-01T00:00:00Z',
           cycle_years=1,year_days=360,aspects_deg=[0],orb_deg=1,
           direction='direct',output_timezone='Etc/UTC',promissors=['SUN'],significators=['MOON'])
    d.update(changes);return d

def request():
    return build_uniform_cycle_request(chart(), subject(), settings())

def ctx(raw=None, canonical=None):
    base=canonical_base() if canonical is None else canonical
    base=deepcopy(base);base['natal']={'charts':{'A':chart()}}
    d={'subjects':[subject()], 'atacires_requests':[{'subject_id':'A','settings':settings()}]}
    if raw: d.update(raw)
    return ModuleContext('M26','Temporal','FULL',d,base,{})

class AdapterTests(unittest.TestCase):
    def test_canonical_positions_are_used_and_not_mutated(self):
        c=chart();original=deepcopy(c)
        result=calculate_uniform_cycle(build_uniform_cycle_request(c,subject(),settings()), executed_at='2026-01-01T00:00:00Z')
        self.assertEqual(c,original)
        self.assertEqual([e['exact_datetime'] for e in result['events']],['2000-03-31T00:00:00.000000Z','2001-03-26T00:00:00.000000Z'])
        self.assertEqual(result['directed_positions_start']['SUN'],0)
        self.assertEqual(result['provenance']['backend_id'],'SYNTHETIC')
        self.assertEqual(result['provenance']['coordinates'],{'latitude':0.,'longitude':0.})
    def test_reject_dialect_and_ambiguous_keys(self):
        for positions in ({'Sun':{'longitude':0}}, {'SUN':{'longitude_deg':0}}, {'SUN':{'longitude':0,'longitude_deg':1}}):
            c=chart();c['positions']=positions
            with self.subTest(positions=positions), self.assertRaises(ValueError):build_uniform_cycle_request(c,subject(),settings())
    def test_reject_missing_provenance(self):
        c=chart();del c['backend_provenance']
        with self.assertRaises(ValueError):build_uniform_cycle_request(c,subject(),settings())
    def test_reject_inconsistent_instant(self):
        c=chart();c['metadata']['utc_instant']='2000-01-02T00:00:00Z'
        with self.assertRaises(ValueError):build_uniform_cycle_request(c,subject(),settings())
    def test_reject_inconsistent_subject_and_coordinates(self):
        for field,value in [('subject_id','B'),('metadata',{'utc_instant':'2000-01-01T00:00:00Z','latitude':1.,'longitude':0.,'house_system_requested':'P'})]:
            c=chart();c[field]=value
            with self.assertRaises(ValueError):build_uniform_cycle_request(c,subject(),settings())
    def test_unknown_or_missing_hour_degrades(self):
        for key,value in [('birth_time',None),('time_reliability','UNKNOWN'),('time_uncertainty_minutes',30),('latitude',None)]:
            s=subject();s[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):build_uniform_cycle_request(chart(),s,settings())
    def test_reject_nonfinite_and_boolean_longitude(self):
        for value in (True,float('nan'),float('inf'),360,-1):
            c=chart();c['positions']['SUN']['longitude']=value
            with self.assertRaises(ValueError):build_uniform_cycle_request(c,subject(),settings())
    def test_reject_settings_override_and_unknown_field(self):
        for key in ('natal_points','positions_source','datetime_local','made_up'):
            with self.assertRaises(ValueError):build_uniform_cycle_request(chart(),subject(),settings(**{key:'bad'}))
    def test_fingerprint_is_order_independent_and_sensitive(self):
        self.assertEqual(fingerprint_payload({'a':1,'b':2}),fingerprint_payload({'b':2,'a':1}))
        self.assertNotEqual(fingerprint_payload({'a':1}),fingerprint_payload({'a':2}))
        with self.assertRaises(ValueError):fingerprint_payload({'a':float('nan')})
    def test_execution_timestamp_excluded_from_result_fingerprint(self):
        a=calculate_uniform_cycle(request(),executed_at='2026-01-01T00:00:00Z')
        b=calculate_uniform_cycle(request(),executed_at='2026-01-02T00:00:00Z')
        self.assertEqual(a['provenance']['output_fingerprint'],b['provenance']['output_fingerprint'])
        self.assertEqual(a['events'],b['events'])
        self.assertNotEqual(a['provenance']['executed_at'],b['provenance']['executed_at'])
    def test_effective_defaults_are_fingerprinted(self):
        a=settings();b=settings();del b['direction']
        r1=calculate_uniform_cycle(build_uniform_cycle_request(chart(),subject(),a))
        r2=calculate_uniform_cycle(build_uniform_cycle_request(chart(),subject(),b))
        self.assertEqual(r1['provenance']['input_fingerprint'],r2['provenance']['input_fingerprint'])
    def test_equivalent_numeric_inputs_share_signal_fingerprint(self):
        integer=calculate_uniform_cycle(build_uniform_cycle_request(chart(),subject(),settings(cycle_years=1)))
        floating=calculate_uniform_cycle(build_uniform_cycle_request(chart(),subject(),settings(cycle_years=1.0)))
        self.assertEqual(integer['events'],floating['events'])
        self.assertEqual(integer['provenance']['input_fingerprint'],floating['provenance']['input_fingerprint'])
    def test_request_is_snapshot(self):
        c=chart();s=settings();r=build_uniform_cycle_request(c,subject(),s)
        c['positions']['SUN']['longitude']=42;s['cycle_years']=60
        self.assertEqual(calculate_uniform_cycle(r)['events'][0]['exact_datetime'],'2000-03-31T00:00:00.000000Z')
    def test_limits_typed_including_datetime_overflow(self):
        for changes in ({'cycle_years':.0001},{'cycle_years':float('inf')},{'end_utc':'9999-12-31T00:00:00Z','cycle_years':10000,'orb_deg':179}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):calculate_uniform_cycle(build_uniform_cycle_request(chart(),subject(),settings(**changes)))
    def test_shadow_schema_strict(self):
        result=make_atacires_temporal_handler(m26_temporal_activation, enabled=True)(ctx())
        shadow=result.canonical_updates['atacires_shadow']
        from jsonschema import Draft202012Validator
        schema=json.loads((ROOT/'schemas/atacires-shadow.schema.json').read_text())
        validator=Draft202012Validator(schema);validator.validate(shadow)
        bad=deepcopy(shadow);bad['scoring_enabled']=True
        self.assertTrue(list(validator.iter_errors(bad)))

class IsolationTests(unittest.TestCase):
    def test_feature_off_exact_baseline_even_with_invalid_request(self):
        context=ctx({'atacires_requests':'invalid'})
        with patch.dict(os.environ,{'ALMAS_TEMPORAL_ATACIRES_ENABLED':'false'}):
            before=m26_temporal_activation(context)
            after=make_atacires_temporal_handler(m26_temporal_activation)(context)
        self.assertEqual(before.to_dict(),after.to_dict())
    def test_registered_in_default_and_backend_handlers(self):
        for handlers in (default_handlers(),configured_handlers()):
            with patch.dict(os.environ,{'ALMAS_TEMPORAL_ATACIRES_ENABLED':'true'}):
                self.assertIn('atacires_shadow',handlers['M26'](ctx()).canonical_updates)
    def test_environment_invalid_fails_closed(self):
        with patch.dict(os.environ,{'ALMAS_TEMPORAL_ATACIRES_ENABLED':'perhaps'}):
            with self.assertRaises(ValueError):make_atacires_temporal_handler(m26_temporal_activation)(ctx())
    def test_explicit_bool_required(self):
        with self.assertRaises(ValueError):make_atacires_temporal_handler(m26_temporal_activation,enabled='false')
    def test_root_matching_cannot_be_asserted_by_caller(self):
        context=ctx({'atacires_requests':[{'subject_id':'A','root_id':'R0001','settings':settings()}]})
        result=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context)
        self.assertEqual(result.canonical_updates['atacires_shadow']['status'],'NOT_EVALUABLE')
    def test_root_link_verified_by_structural_point_endpoint(self):
        context=ctx()
        context.canonical_snapshot['independent_roots']['roots'][0]['root_key']='A:SUN|B:MOON|TRINE'
        result=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context)
        signals=result.canonical_updates['atacires_shadow']['signals']
        self.assertEqual(signals[0]['root_id'],'R0001')
        self.assertEqual(signals[0]['activation_class'],'ENDPOINT_ACTIVATION')
        self.assertFalse(signals[0]['iat_eligible'])
        self.assertFalse(signals[0]['creates_structural_root'])
        self.assertEqual(signals[0]['dependency_group'],'ATACIR_FAMILY')
    def test_orphan_not_scored_and_existing_iat_unchanged(self):
        sig=dict(signal_id='T1',root_id='R0001',temporal_family='TTRANSIT',activation_class='DIRECT_REPETITION',strength=.7,window_status='CURRENT_ACTIVE',preregistergistered=True,preregistered=True,structural_family='SYN',exactitude_orb=.1,preregistered_window_rule='TEST')
        policy=dict(preregistration_ref='TEST',window_scope_ref='TEST',formula='WEIGHTED_MEAN_EFFECTIVE_STRENGTH',family_weights={'TTRANSIT':1.},root_weights={'R0001':1.})
        context=ctx({'temporal_signals':[sig],'iat_aggregation_policy':policy})
        context.canonical_snapshot['independent_roots']['roots'][0]['root_key']='B:SUN|B:MOON|TRINE'
        original=deepcopy(context.canonical_snapshot)
        baseline=m26_temporal_activation(context)
        result=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context)
        self.assertEqual(result.payload,baseline.payload)
        self.assertEqual(result.canonical_updates['temporal_activation'],baseline.canonical_updates['temporal_activation'])
        self.assertEqual(context.canonical_snapshot,original)
        self.assertEqual(result.canonical_updates['atacires_shadow']['signals'][0]['root_id'],None)
        self.assertEqual(result.canonical_updates['temporal_activation']['iat'],70.)
    def test_missing_data_not_evaluable_without_swallowing_existing_errors(self):
        context=ctx();del context.canonical_snapshot['natal']
        result=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context)
        self.assertEqual(result.canonical_updates['atacires_shadow']['status'],'NOT_EVALUABLE')
        self.assertEqual(result.canonical_updates['atacires_shadow']['signals'],[])
    def test_multiple_requests_atomic_no_partial_success(self):
        context=ctx();context.raw_input['atacires_requests'].append({'subject_id':'MISSING','settings':settings()})
        result=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context)
        self.assertEqual(result.canonical_updates['atacires_shadow']['status'],'NOT_EVALUABLE')
        self.assertEqual(result.canonical_updates['atacires_shadow']['signals'],[])
    def test_canonical_assembly_adds_only_shadow_and_validates(self):
        context=ctx();before=deepcopy(context.canonical_snapshot)
        result=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context)
        a=assemble_canonical_analysis(before,prior_all())['canonical_analysis']
        after=deepcopy(before);after.update(result.canonical_updates)
        b=assemble_canonical_analysis(after,prior_all())['canonical_analysis']
        canonical_validator().validate(b)
        self.assertEqual(b['temporal'].pop('atacires_shadow'),result.canonical_updates['atacires_shadow'])
        self.assertEqual(a,b)
    def test_rollback_restores_original(self):
        context=ctx();handler=make_atacires_temporal_handler(m26_temporal_activation)
        with patch.dict(os.environ,{'ALMAS_TEMPORAL_ATACIRES_ENABLED':'true'}): self.assertIn('atacires_shadow',handler(context).canonical_updates)
        with patch.dict(os.environ,{'ALMAS_TEMPORAL_ATACIRES_ENABLED':'false'}): self.assertEqual(handler(context).to_dict(),m26_temporal_activation(context).to_dict())
    def test_no_new_runtime_dependencies(self):
        text=(ROOT/'pyproject.toml').read_text()
        self.assertNotIn('\ndependencies =',text)
        self.assertNotIn('atacires-swiss',text)

class RobustnessTests(unittest.TestCase):
    def test_exact_hour_needs_no_monte_carlo(self):
        result=calculate_uniform_cycle(request())
        r=assess_robustness([result],max_spread_seconds=60,sampling_ref='EXACT',exact_time=True)
        self.assertEqual(r['classification'],'EXACT_INPUT');self.assertIsNone(r['metaphysical_probability'])
    def test_same_samples_stable(self):
        result=calculate_uniform_cycle(request())
        self.assertEqual(assess_robustness([result,result],max_spread_seconds=60,sampling_ref='GRID-V1')['classification'],'ROBUST')
    def test_shifted_samples_sensitive(self):
        a=calculate_uniform_cycle(request());b=deepcopy(a);b['events'][0]['exact_datetime']='2000-04-01T00:00:00Z'
        r=assess_robustness([a,b],max_spread_seconds=60,sampling_ref='GRID-V1')
        self.assertEqual(r['classification'],'SENSITIVE');self.assertEqual(r['maximum_spread_seconds'],86400.)
    def test_missing_contact_is_sensitive(self):
        a=calculate_uniform_cycle(request());b=deepcopy(a);b['events']=[]
        self.assertEqual(assess_robustness([a,b],max_spread_seconds=60,sampling_ref='GRID-V1')['classification'],'SENSITIVE')
    def test_same_contacts_reordered_across_samples_remain_robust(self):
        a=calculate_uniform_cycle(request())
        self.assertGreaterEqual(len(a['events']),2)
        a['events'][0]['aspect_deg']=0.;a['events'][0]['oriented_aspect_deg']=0.
        a['events'][1]['aspect_deg']=60.;a['events'][1]['oriented_aspect_deg']=60.
        b=deepcopy(a);b['events'].reverse()
        result=assess_robustness([a,b],max_spread_seconds=60,sampling_ref='GRID-V1')
        self.assertEqual(result['classification'],'ROBUST')
        self.assertTrue(result['contact_presence_stable'])
        self.assertEqual(result['maximum_spread_seconds'],0.)
    def test_empty_or_unpreregistered_samples_rejected(self):
        for samples,ref in (([],'GRID'),([calculate_uniform_cycle(request())],'')):
            with self.assertRaises(ValueError):assess_robustness(samples,max_spread_seconds=60,sampling_ref=ref)

if __name__=='__main__':unittest.main()

class WorkRequestTests(unittest.TestCase):
    def test_public_request_preserves_temporal_configuration(self):
        from test_relational_request_pipeline import work_request
        from almas_tfa.relational_request_pipeline import prepare_relational_raw_input
        w=work_request();w['request']['atacires_requests']=[{'subject_id':'A','settings':settings()}]
        raw=prepare_relational_raw_input(w)
        self.assertEqual(raw['atacires_requests'],w['request']['atacires_requests'])
        raw['atacires_requests'][0]['settings']['cycle_years']=99
        self.assertEqual(w['request']['atacires_requests'][0]['settings']['cycle_years'],1)
    def test_duplicate_requests_deduplicate_signals(self):
        context=ctx();context.raw_input['atacires_requests']*=2
        shadow=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context).canonical_updates['atacires_shadow']
        self.assertEqual(len(shadow['signals']),2)
    def test_node_metadata_retained_and_axis_grouped(self):
        context=ctx();c=context.canonical_snapshot['natal']['charts']['A']
        c['positions']['MEAN_NORTH_NODE']={'longitude':0.,'node_variant':'MEAN','nodal_axis_id':'LUNAR_NODE_AXIS'}
        context.raw_input['atacires_requests'][0]['settings']['promissors']=['MEAN_NORTH_NODE']
        shadow=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context).canonical_updates['atacires_shadow']
        self.assertEqual(shadow['signals'][0]['node_variant'],'MEAN')
        self.assertEqual(shadow['signals'][0]['nodal_axis_id'],'LUNAR_NODE_AXIS')

class BoundaryTests(unittest.TestCase):
    def test_shadow_sidecar_is_published_without_promoting_base_m26_status(self):
        context=ctx({'temporal_signals':[]})
        manifest={'mode':'FULL','modules':[{'id':f'M{i:02d}','name':f'module_{i:02d}'} for i in range(32)]}
        run=Orchestrator({'M26':make_atacires_temporal_handler(m26_temporal_activation,enabled=True)}).run(
            context.raw_input,manifest,initial_canonical=context.canonical_snapshot)
        self.assertEqual(run.results['M26'].status,ExecutionStatus.NOT_EVALUABLE)
        self.assertIn('atacires_shadow',run.canonical)
        self.assertEqual(run.canonical['atacires_shadow']['status'],'COMPLETED')

    def test_signals_cannot_reenter_m26_scoring_when_client_sets_preregistered(self):
        context=ctx();shadow=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context).canonical_updates['atacires_shadow']
        signal=deepcopy(shadow['signals'][0]);signal.update(preregistered=True,strength=1.,structural_family='SYN',exactitude_orb=0.,preregistered_window_rule='ATTEMPT',window_status='CURRENT_ACTIVE',technique_variant='C360')
        raw=ctx({'temporal_signals':[signal]})
        output=m26_temporal_activation(raw).payload
        self.assertFalse(output['signals'][0]['iat_eligible'])
    def test_root_link_fanout_is_bounded(self):
        context=ctx();context.canonical_snapshot['independent_roots']['roots']=[{'root_id':str(i),'root_key':'A:SUN|B:MOON|TRINE'} for i in range(10001)]
        shadow=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context).canonical_updates['atacires_shadow']
        self.assertEqual(shadow['status'],'NOT_EVALUABLE')
    def test_empty_grid_cannot_claim_robustness(self):
        a=calculate_uniform_cycle(request());a['events']=[]
        result=assess_robustness([a,a],max_spread_seconds=60,sampling_ref='GRID')
        self.assertEqual(result['classification'],'NOT_EVALUABLE')
    def test_mixed_empty_contact_grid_is_sensitive_independent_of_order(self):
        populated=calculate_uniform_cycle(request());empty=deepcopy(populated);empty['events']=[]
        forward=assess_robustness([empty,populated],max_spread_seconds=60,sampling_ref='GRID')
        reverse=assess_robustness([populated,empty],max_spread_seconds=60,sampling_ref='GRID')
        self.assertEqual(forward['classification'],'SENSITIVE')
        self.assertEqual(reverse['classification'],'SENSITIVE')
        self.assertFalse(forward['contact_presence_stable'])

class ReviewRegressionTests(unittest.TestCase):
    def test_axis_contact_links_existing_canonical_root(self):
        from almas_tfa.evidence_handlers import _root_key
        context=ctx()
        root_key=_root_key({'chart_a':'A','chart_b':'B','point_a':'ASC','point_b':'MOON','relation':'CONJUNCTION','angle':0}, directional=False)
        context.canonical_snapshot['independent_roots']['roots']=[{'root_id':'R-AXIS','root_key':root_key}]
        context.raw_input['atacires_requests'][0]['settings']['promissors']=['ASC']
        result=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context).canonical_updates['atacires_shadow']
        self.assertEqual(result['signals'][0]['root_id'],'R-AXIS')

    def test_target_endpoint_can_anchor_existing_root(self):
        context=ctx()
        context.canonical_snapshot['independent_roots']['roots']=[{'root_id':'R-TARGET','root_key':'A:MOON|B:SUN|CONJUNCTION'}]
        result=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context).canonical_updates['atacires_shadow']
        anchored=[signal for signal in result['signals'] if signal['target_point']=='MOON']
        self.assertTrue(anchored)
        self.assertTrue(all(signal['root_id']=='R-TARGET' for signal in anchored))

    def test_mean_node_contact_links_existing_canonical_axis_root(self):
        context=ctx();chart_data=context.canonical_snapshot['natal']['charts']['A']
        chart_data['positions']['MEAN_NORTH_NODE']={'longitude':0.,'node_variant':'MEAN','nodal_axis_id':'LUNAR_NODE_AXIS'}
        context.canonical_snapshot['independent_roots']['roots']=[{'root_id':'R-MEAN-AXIS','root_key':'A:AXIS_NODES|B:MOON|CONJUNCTION'}]
        context.raw_input['atacires_requests'][0]['settings']['promissors']=['MEAN_NORTH_NODE']
        result=make_atacires_temporal_handler(m26_temporal_activation,enabled=True)(context).canonical_updates['atacires_shadow']
        self.assertEqual(result['signals'][0]['root_id'],'R-MEAN-AXIS')
        self.assertTrue(result['signals'][0]['anchored'])

    def test_root_endpoints_are_indexed_once_for_all_events(self):
        from almas_tfa.atacires.temporal_signal import to_temporal_signals
        class CountingRoots(list):
            iterations=0
            def __iter__(self):
                self.iterations+=1
                return super().__iter__()
        calculated=calculate_uniform_cycle(request())
        event=calculated['events'][0]
        calculated['events']=[deepcopy(event) for _ in range(8)]
        roots=CountingRoots([{'root_id':'R-SUN-MOON','root_key':'A:SUN|B:MOON|CONJUNCTION'}])
        to_temporal_signals(calculated,'A',roots)
        self.assertEqual(roots.iterations,1)

    def test_shadow_does_not_suppress_existing_scored_atacir(self):
        context=ctx();s=dict(signal_id='LIVE',root_id='R0001',temporal_family='TATACIR',activation_class='DIRECT_REPETITION',strength=.7,window_status='CURRENT_ACTIVE',preregistered=True,structural_family='SYN',exactitude_orb=0.,preregistered_window_rule='REGISTERED',technique_variant='C360')
        policy=dict(preregistration_ref='REGISTERED',window_scope_ref='REGISTERED',formula='WEIGHTED_MEAN_EFFECTIVE_STRENGTH',family_weights={'TATACIR':1.},root_weights={'R0001':1.})
        baseline=m26_temporal_activation(ctx({'temporal_signals':[s],'iat_aggregation_policy':policy})).payload
        shadow=deepcopy(s);shadow.update(signal_id='SHADOW',execution_mode='SHADOW',strength=1.)
        result=m26_temporal_activation(ctx({'temporal_signals':[s,shadow],'iat_aggregation_policy':policy})).payload
        self.assertEqual(baseline['iat'],70.)
        self.assertEqual(result['iat'],baseline['iat'])
        self.assertEqual(result['iat_eligible_signal_ids'],['LIVE'])
        self.assertEqual(result['iat_components'],baseline['iat_components'])
        self.assertEqual([s['signal_id'] for s in result['selected_independent_signals']],['LIVE'])
    def test_single_nonexact_sample_is_not_evaluable(self):
        result=assess_robustness([calculate_uniform_cycle(request())],max_spread_seconds=60,sampling_ref='GRID-V1')
        self.assertEqual(result['classification'],'NOT_EVALUABLE')
