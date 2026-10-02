import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from jsonschema import ValidationError
from almas_tfa.calculated_points import mean_apogee
from almas_tfa.ssar import load_ssar_policy,run_ssar
from almas_tfa.ssar_calculated_points import (
    POINTS, build_calculated_points_request,calculate_point_context,load_calculated_points_catalog,
    load_calculated_points_policy,run_calculated_points,validate_calculated_points_result,
)
from test_calculated_points import lunar_state

ROOT=Path(__file__).resolve().parents[1]


def context():
    epochs=[2451545.+offset/1440 for offset in (-30,-15,0,15,30)]
    apogee=mean_apogee(2451545.,0)
    return dict(id='CTX1',subject_id='A',technique='SYNASTRY',time_uncertainty_minutes=1,
        location_precision_sufficient=True,input_provenance=dict(provider='SYNTHETIC_INPUTS',software_version='fixture-1',
        epoch_scale='TT',armc_scale='GAST_UT1',coordinate_origin='GEOCENTRIC',state_frame='ICRF_INERTIAL',
        reference_frame='TRUE_ECLIPTIC_EQUINOX_OF_DATE',ephemeris_id='DE440',ephemeris_sha256='0'*64,
        source_refs=['synthetic:geometry'],network_io_used=False,time_conversion='SYNTHETIC_TT_AND_ARMC',frame_model='SYNTHETIC_ROTATION'),
        samples=[dict(offset_minutes=o,jd_tt=e,armc_deg=270+o*.250684,latitude_deg=41.,true_obliquity_deg=23.4392911,
            nutation_longitude_deg=0.,moon_state=lunar_state(apogee,e)) for o,e in zip((-30,-15,0,15,30),epochs)])


def fixture(point='VERTEX'):
    c=context();p=next(p for p in calculate_point_context(c)['points'] if p['point_id']==point)
    target=p['central_longitude']+1
    return dict(enabled=True,contexts=[c],core_roots=[dict(root_id='R1',core_eligible=True,core_evidence_ids=['CORE1'],point_ids=['SUN'])],
        contacts=[dict(id='C1',context_ref='CTX1',target_id='SUN',target_longitude=target,
            target_samples=[dict(offset_minutes=s['offset_minutes'],target_longitude=s['longitude']+1) for s in p['samples']],
            core_root_refs=['R1'],core_anchor_search_complete=True)],edges=[])


def appearance(result,point='VERTEX'):
    return next(a for a in result['ssar']['appearances'] if a['point_id']==point)


class SSARCalculatedPointTests(unittest.TestCase):
    def test_all_four_points_positive_with_technical_not_nominal_provenance(self):
        for point in POINTS:
            request=fixture(point);output=run_calculated_points(request)
            self.assertEqual(appearance(output,point)['qualification'],'QUALIFIED_SIGNIFICATOR')
            effective,_=build_calculated_points_request(request)
            record=next(a for a in effective['appearances'] if a['point_id']==point)
            self.assertEqual(record['provenance']['basis'],'TECHNICAL');self.assertIsNone(record['provenance']['name_class'])
            validate_calculated_points_result(output,request=request)

    def test_all_four_no_contact_suppresses_interpretation(self):
        for point in POINTS:
            request=fixture(point);request['contacts'][0]['target_longitude']+=50
            for s in request['contacts'][0]['target_samples']:s['target_longitude']+=50
            output=run_calculated_points(request)
            self.assertEqual(appearance(output,point)['qualification'],'NO_CONTACT')
            self.assertIsNone(next(n for n in output['functional_notes'] if n['appearance_ref']=='C1:'+point)['interpretation'])

    def test_all_four_unknown_or_excess_time_uncertainty_blocks_qualification(self):
        for point in POINTS:
            for precision in (None,31):
                request=fixture(point);request['contexts'][0]['time_uncertainty_minutes']=precision
                output=run_calculated_points(request)
                self.assertEqual(appearance(output,point)['qualification'],'BLOCKED')
                self.assertIsNotNone(output['calculations'][0]['points'][POINTS.index(point)]['central_longitude'])

    def test_vertex_requires_location_precision_lunar_points_do_not(self):
        for point in POINTS:
            request=fixture(point);request['contexts'][0]['location_precision_sufficient']=None
            expected='BLOCKED' if point in POINTS[:2] else 'QUALIFIED_SIGNIFICATOR'
            self.assertEqual(appearance(run_calculated_points(request),point)['qualification'],expected)

    def test_missing_tt_blocks_all_calculations_without_inventing_zero(self):
        request=fixture()
        for sample in request['contexts'][0]['samples']:sample['jd_tt']=None
        output=run_calculated_points(request)
        self.assertTrue(all(a['qualification']=='BLOCKED' for a in output['ssar']['appearances']))
        self.assertTrue(all(p['central_longitude'] is None for p in output['calculations'][0]['points']))

    def test_missing_vertex_inputs_do_not_block_available_mean_lunar_calculation(self):
        for field in ('armc_deg','latitude_deg','true_obliquity_deg'):
            request=fixture('BLACK_MOON_MEAN');request['contexts'][0]['samples'][2][field]=None
            output=run_calculated_points(request)
            self.assertEqual(appearance(output)['qualification'],'BLOCKED')
            self.assertEqual(appearance(output,'BLACK_MOON_MEAN')['qualification'],'QUALIFIED_SIGNIFICATOR')

    def test_missing_nutation_blocks_mean_but_not_osculating_rotation(self):
        request=fixture('BLACK_MOON_OSCULATING');request['contexts'][0]['samples'][2]['nutation_longitude_deg']=None
        output=run_calculated_points(request)
        self.assertEqual(appearance(output,'BLACK_MOON_MEAN')['qualification'],'BLOCKED')
        self.assertEqual(appearance(output,'BLACK_MOON_OSCULATING')['qualification'],'QUALIFIED_SIGNIFICATOR')

    def test_missing_state_or_ephemeris_metadata_blocks_osculating_only(self):
        for change in ('state','ephemeris','checksum'):
            request=fixture('BLACK_MOON_MEAN');c=request['contexts'][0]
            if change=='state':c['samples'][2]['moon_state']=None
            else:c['input_provenance']['ephemeris_id' if change=='ephemeris' else 'ephemeris_sha256']=None
            output=run_calculated_points(request)
            self.assertEqual(appearance(output,'BLACK_MOON_OSCULATING')['qualification'],'BLOCKED')
            self.assertEqual(appearance(output,'BLACK_MOON_MEAN')['qualification'],'QUALIFIED_SIGNIFICATOR')
            self.assertEqual(output['variant_sensitivity'][0]['geometry_concordance'],'NOT_EVALUABLE')

    def test_bad_lunar_epoch_matrix_and_degenerate_state_are_explicit_blockers(self):
        for change in ('epoch','rotation','state'):
            request=fixture('BLACK_MOON_MEAN');s=request['contexts'][0]['samples'][2]['moon_state']
            if change=='epoch':s['epoch_jd_tt']+=1
            elif change=='rotation':s['rotation_icrf_to_true_ecliptic'][0][0]=2
            else:s['position_icrf_km']=[0,0,0]
            output=run_calculated_points(request)
            self.assertEqual(appearance(output,'BLACK_MOON_OSCULATING')['qualification'],'BLOCKED')
            self.assertTrue(output['calculations'][0]['points'][3]['samples'][2]['reasons'])

    def test_vertex_coincident_planes_and_unoriented_cases_remain_blocked(self):
        request=fixture();c=request['contexts'][0]
        for s in c['samples']:s.update(latitude_deg=23.4392911,armc_deg=90)
        self.assertEqual(appearance(run_calculated_points(request))['qualification'],'BLOCKED')
        for s in c['samples']:s.update(latitude_deg=0,armc_deg=0)
        self.assertEqual(appearance(run_calculated_points(request))['qualification'],'BLOCKED')

    def test_complete_axis_collapses_equivalence_retains_directed_aspects(self):
        request=fixture();output=run_calculated_points(request)
        classes=output['ssar']['dependency_graph']['equivalence_classes']
        self.assertEqual(len(classes),3)
        axis=next(c for c in classes if 'U:C1:VERTEX' in c['unit_refs'])
        self.assertEqual(axis['unit_refs'],['U:C1:ANTI_VERTEX','U:C1:VERTEX'])
        original=output['axis_normalization'][0]['original_longitudes']
        self.assertEqual({r['directed_aspect']['aspect'] for r in original},{'CONJUNCTION','OPPOSITION'})
        self.assertFalse(output['axis_normalization'][0]['contributes_new_evidence'])

    def test_axis_pole_flip_keeps_robust_equivalent_geometry(self):
        request=fixture();c=request['contexts'][0]
        for s in c['samples']:s.update(latitude_deg=0,armc_deg=.1+s['offset_minutes']*.250684)
        contact=request['contacts'][0];contact['target_longitude']=.5
        for s in contact['target_samples']:s['target_longitude']=.5
        output=run_calculated_points(request)
        self.assertEqual(appearance(output)['qualification'],'QUALIFIED_SIGNIFICATOR')
        self.assertEqual(appearance(output)['robustness']['preserved_fraction'],1)
        poles={s['longitude'] for s in output['calculations'][0]['points'][0]['samples']}
        self.assertEqual(poles,{0,180})

    def test_axis_square_is_not_collapsed_into_conjunction(self):
        request=fixture();effective,_=build_calculated_points_request(request)
        lon=effective['appearances'][0]['geometry']['longitude']
        request['contacts'][0]['target_longitude']=lon+90
        for s in request['contacts'][0]['target_samples']:s['target_longitude']=lon+90
        output=run_calculated_points(request)
        self.assertEqual(appearance(output)['qualification'],'NO_CONTACT')
        self.assertEqual(appearance(output,'ANTI_VERTEX')['qualification'],'NO_CONTACT')

    def test_lunar_variants_share_group_without_becoming_equivalent(self):
        output=run_calculated_points(fixture('BLACK_MOON_MEAN'))
        graph=output['ssar']['dependency_graph']
        group=next(g for g in graph['effective_groups'] if 'U:C1:BLACK_MOON_MEAN' in g['unit_refs'])
        self.assertIn('U:C1:BLACK_MOON_OSCULATING',group['unit_refs'])
        self.assertFalse(any({'U:C1:BLACK_MOON_MEAN','U:C1:BLACK_MOON_OSCULATING'}<=set(c['unit_refs']) for c in graph['equivalence_classes']))
        self.assertFalse(graph['statistical_independence_established'])

    def test_lunar_variant_disagreement_visible_no_favorable_selection(self):
        request=fixture('BLACK_MOON_MEAN')
        lon=mean_apogee(2451545.,0)
        for s in request['contexts'][0]['samples']:s['moon_state']=lunar_state(lon+40,s['jd_tt'])
        output=run_calculated_points(request);sensitivity=output['variant_sensitivity'][0]
        self.assertEqual(sensitivity['geometry_concordance'],'DISAGREE')
        self.assertEqual(sensitivity['qualification_concordance'],'DISAGREE')
        self.assertAlmostEqual(sensitivity['separation_deg'],40,places=10)
        self.assertIsNone(sensitivity['selected_variant'])
        self.assertEqual(len(output['ssar']['appearances']),4)

    def test_all_four_missing_sources_or_technical_definition_block(self):
        for point in POINTS:
            for change in ('sources','algorithm','conventions','inputs','variant','name'):
                effective,_=build_calculated_points_request(fixture(point));a=next(a for a in effective['appearances'] if a['point_id']==point)
                field={'sources':'source_refs','name':'basis'}.get(change,change)
                a['provenance'][field]='NAME' if change=='name' else [] if change in ('sources','inputs') else None
                self.assertEqual(next(a for a in run_ssar(effective,policy=load_calculated_points_policy())['appearances'] if a['point_id']==point)['qualification'],'BLOCKED')

    def test_input_source_absence_blocks_computation_not_interpretation_only(self):
        request=fixture();request['contexts'][0]['input_provenance']['source_refs']=[]
        output=run_calculated_points(request)
        self.assertTrue(all(a['qualification']=='BLOCKED' for a in output['ssar']['appearances']))

    def test_supplying_name_body_or_selecting_one_variant_is_rejected(self):
        for field,value in (('point_id','LILITH_ASTEROID'),('selected_variant','BLACK_MOON_MEAN')):
            request=fixture();request['contacts'][0][field]=value
            with self.assertRaises(ValidationError):run_calculated_points(request)

    def test_all_four_missing_core_or_weak_robustness_only_secondary(self):
        for point in POINTS:
            for change in ('root','robustness'):
                request=fixture(point)
                if change=='root':request['contacts'][0]['core_root_refs']=[]
                else:
                    for s in request['contacts'][0]['target_samples'][:2]:s['target_longitude']+=20
                self.assertEqual(appearance(run_calculated_points(request),point)['qualification'],'SECONDARY_SUPPORT')

    def test_incomplete_calculation_or_target_grid_and_search_block_all_dependent_points(self):
        for point in POINTS:
            for change in ('context','target','search'):
                request=fixture(point)
                if change=='context':request['contexts'][0]['samples'].pop()
                elif change=='target':request['contacts'][0]['target_samples'].pop()
                else:request['contacts'][0]['core_anchor_search_complete']=False
                self.assertEqual(appearance(run_calculated_points(request),point)['qualification'],'BLOCKED')

    def test_missing_target_or_central_sample_does_not_invent_contact(self):
        request=fixture();request['contacts'][0]['target_longitude']=None
        request['contacts'][0]['target_samples'][2]['target_longitude']=None
        self.assertTrue(all(a['qualification']=='BLOCKED' for a in run_calculated_points(request)['ssar']['appearances']))
        request=fixture();request['contexts'][0]['samples'].pop(2)
        self.assertEqual(appearance(run_calculated_points(request))['qualification'],'BLOCKED')

    def test_grid_epoch_wrong_latitude_duplicates_and_target_origin_rejected(self):
        for change in ('epoch','latitude','context_offset','target_offset','target_central'):
            request=fixture()
            if change=='epoch':request['contexts'][0]['samples'][0]['jd_tt']+=1
            elif change=='latitude':request['contexts'][0]['samples'][0]['latitude_deg']+=1
            elif change=='context_offset':request['contexts'][0]['samples'].append(copy.deepcopy(request['contexts'][0]['samples'][0]))
            elif change=='target_offset':request['contacts'][0]['target_samples'].append(copy.deepcopy(request['contacts'][0]['target_samples'][0]))
            else:request['contacts'][0]['target_samples'][2]['target_longitude']+=1
            with self.assertRaises(ValueError):run_calculated_points(request)

    def test_duplicate_context_contact_and_target_broken_refs_rejected(self):
        for change in ('context','contact','target','reference'):
            request=fixture()
            if change=='context':request['contexts'].append(copy.deepcopy(request['contexts'][0]))
            elif change in ('contact','target'):
                item=copy.deepcopy(request['contacts'][0])
                if change=='target':item['id']='C2'
                request['contacts'].append(item)
            else:request['contacts'][0]['context_ref']='MISSING'
            with self.assertRaises(ValueError):run_calculated_points(request)

    def test_noninertial_topocentric_units_frame_and_nonfinite_rejected(self):
        for field,value in (('state_frame','ROTATING'),('coordinate_origin','TOPOCENTRIC'),('epoch_scale','UTC'),('reference_frame','SIDEREAL')):
            request=fixture();request['contexts'][0]['input_provenance'][field]=value
            with self.assertRaises(ValidationError):run_calculated_points(request)
        request=fixture();request['contexts'][0]['samples'][2]['moon_state']['velocity_units']='KM_PER_DAY'
        with self.assertRaises(ValidationError):run_calculated_points(request)
        request=fixture();request['contexts'][0]['samples'][2]['armc_deg']=float('nan')
        with self.assertRaises(ValueError):run_calculated_points(request)

    def test_composite_davison_contexts_and_technical_dependence_cannot_add_variant_group(self):
        request=fixture('BLACK_MOON_MEAN');c=copy.deepcopy(request['contexts'][0]);c.update(id='CTX2',subject_id='RELATIONSHIP',technique='DAVISON')
        request['contexts'][0].update(subject_id='RELATIONSHIP',technique='COMPOSITE');request['contexts'].append(c)
        contact=copy.deepcopy(request['contacts'][0]);contact.update(id='C2',context_ref='CTX2');request['contacts'].append(contact)
        output=run_calculated_points(request)
        self.assertEqual(len(output['ssar']['dependency_graph']['effective_groups']),1)
        request['edges']=[dict(a='U:C1:VERTEX',b='U:C1:BLACK_MOON_MEAN',relation='UNKNOWN',rule_id=load_calculated_points_policy()['dependency_rules']['UNKNOWN'])]
        self.assertEqual(len(run_calculated_points(request)['ssar']['dependency_graph']['effective_groups']),1)

    def test_subject_context_mismatch_and_unknown_technique_rejected(self):
        request=fixture();request['contexts'][0]['subject_id']='RELATIONSHIP'
        with self.assertRaises(ValueError):run_calculated_points(request)
        request=fixture();request['contexts'][0]['technique']='VERTEX'
        with self.assertRaises(ValidationError):run_calculated_points(request)

    def test_calculation_without_contacts_has_coverage_but_no_qualification(self):
        request=fixture();request['contacts']=[]
        output=run_calculated_points(request)
        self.assertEqual(output['execution_status'],'executed');self.assertEqual(output['ssar']['qualified_significators'],[])
        self.assertEqual(output['completion'],'PARTIAL')

    def test_four_functions_and_effects_remain_exploratory_without_temporal_documentary_promotion(self):
        output=run_calculated_points(fixture())
        self.assertFalse(output['structural_scoring_modified'])
        self.assertEqual(output['ontology_effect'],'NONE');self.assertEqual(output['discriminator_effect'],'NONE')
        self.assertEqual(output['ssar']['temporal_activation'],[]);self.assertEqual(output['ssar']['documentary_correspondence'],[])
        self.assertTrue(all(n['documentary_status']=='NOT_EVALUABLE' for n in output['functional_notes']))
        self.assertEqual(output['external_validation_status'],'NOT_PERFORMED')

    def test_calculation_axis_variant_hash_and_effect_tampering_cannot_validate(self):
        request=fixture('BLACK_MOON_MEAN')
        for change in ('calculation','axis','variant','hash','effect'):
            output=run_calculated_points(request)
            if change=='calculation':output['calculations'][0]['points'][0]['central_longitude']+=1
            elif change=='axis':output['axis_normalization'][0]['canonical_axis_longitude']+=1
            elif change=='variant':output['variant_sensitivity'][0]['selected_variant']='BLACK_MOON_MEAN'
            elif change=='hash':output['calculations'][0]['input_hash']='0'*64
            else:output['ontology_effect']='SUPPORTED'
            with self.assertRaises((ValueError,ValidationError)):validate_calculated_points_result(output,request=request)

    def test_order_determinism_input_and_catalog_not_mutated(self):
        request=fixture();before=copy.deepcopy(request);catalog=load_calculated_points_catalog()
        output=run_calculated_points(request)
        request['contexts'][0]['samples'].reverse();request['contacts'][0]['target_samples'].reverse()
        other=run_calculated_points(request)
        # El hash identifica exactamente el artefacto de entrada, incluido su orden.
        self.assertEqual(output['ssar'],other['ssar'])
        self.assertEqual(output['calculations'][0]['points'],other['calculations'][0]['points'])
        self.assertEqual(before,fixture());self.assertEqual(catalog,load_calculated_points_catalog())

    def test_default_generic_policy_and_prior_profiles_not_modified(self):
        self.assertEqual(load_ssar_policy()['point_rules'],{})
        self.assertIn('CALCULATED_POINTS',load_ssar_policy()['unimplemented_layers'])
        self.assertNotIn('CALCULATED_POINTS',load_calculated_points_policy()['unimplemented_layers'])

    def test_disabled_ignores_history_without_extras_empty_enabled_is_not_absence(self):
        disabled=run_calculated_points(dict(enabled=False,history='ignored'))
        self.assertEqual(disabled['execution_status'],'not_run');self.assertEqual(disabled['calculations'],[])
        output=run_calculated_points({'enabled':True})
        self.assertEqual(output['completion'],'NONE');self.assertEqual(output['execution_status'],'not_run')
        code="import sys;sys.path.insert(0,'src');from almas_tfa.ssar_calculated_points import run_calculated_points;assert run_calculated_points({'enabled':False})['completion']=='NONE'"
        subprocess.run([sys.executable,'-S','-c',code],cwd=ROOT,check=True)
