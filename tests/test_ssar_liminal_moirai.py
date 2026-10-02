import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from jsonschema import ValidationError
from almas_tfa.ssar import load_ssar_policy, run_ssar
from almas_tfa.ssar_families import load_families_catalog, load_families_policy
from almas_tfa.ssar_liminal_moirai import (
    build_liminal_request, load_liminal_catalog, load_liminal_policy,
    run_liminal_moirai, validate_liminal_result,
)

ROOT = Path(__file__).resolve().parents[1]
POINTS = ['HEKATE', 'PERSEPHONE', 'ERIS', 'KLOTHO', 'LACHESIS', 'ATROPOS', 'MOIRA']


def observation(point='HEKATE', id='A1', technique='SYNASTRY', longitude=10):
    return dict(id=id, point_id=point, subject_id='A' if technique == 'SYNASTRY' else 'RELATIONSHIP',
                technique=technique, evidence_key='CONTACT:' + id,
                geometry=dict(longitude=longitude, target_longitude=longitude + 1, target_id='SUN', frame='TROPICAL_ECLIPTIC'),
                core_root_refs=['R1'], core_anchor_search_complete=True,
                robustness=dict(input_precision_sufficient=True, samples=[dict(id='P' + str(i), offset_minutes=o,
                    longitude=longitude, target_longitude=longitude + 1) for i, o in enumerate([-30, -15, 0, 15, 30])]))


def fixture(fate=False):
    points = POINTS[3:] if fate else POINTS[:2]
    return dict(enabled=True, core_roots=[dict(root_id='R1', core_eligible=True, core_evidence_ids=['CORE1'], point_ids=['SUN'])],
                observations=[observation(p, 'A' + str(i + 1), 'SYNASTRY' if i == 0 else 'COMPOSITE', 10 + i * 40) for i, p in enumerate(points)],
                edges=[], complexes=[dict(id='FATE_PROCESS_COMPLEX' if fate else 'LIMINAL_TRANSITION_COMPLEX',
                    appearance_refs=['A' + str(i + 1) for i in range(len(points))], search_complete=True)])


class SSARLiminalMoiraiTests(unittest.TestCase):
    def test_two_complexes_positive_four_scopes_without_temporal_documentary_promotion(self):
        for fate in (False, True):
            request = fixture(fate); output = run_liminal_moirai(request); c = output['complexes'][0]
            self.assertTrue(c['qualified_complex'])
            self.assertEqual(len(c['effective_group_refs']), 2)
            for scope in ('structural_geometry', 'functional_interpretation'):
                self.assertEqual(c['assessments'][scope]['status'], 'SUPPORTED')
            for scope in ('temporal_activation', 'documentary_correspondence'):
                self.assertEqual(c['assessments'][scope]['status'], 'NOT_EVALUABLE')
            self.assertIsNone(c['cluster_strength'])
            self.assertFalse(output['structural_scoring_modified'])
            self.assertEqual(output['ontology_effect'], 'NONE')
            validate_liminal_result(output, request=request)

    def test_all_seven_functions_have_positive_geometry_and_explicit_limits(self):
        for point in POINTS:
            request = fixture(); request['complexes'] = []; request['observations'] = [observation(point)]
            output = run_liminal_moirai(request)
            self.assertEqual(output['ssar']['qualified_significators'], ['A1'])
            self.assertIsNotNone(output['functional_notes'][0]['interpretation'])
            self.assertEqual(output['functional_notes'][0]['documentary_status'], 'NOT_EVALUABLE')
            self.assertTrue(output['functional_notes'][0]['inferential_limit'])

    def test_all_seven_negative_geometry_suppresses_functional_notes(self):
        for point in POINTS:
            request = fixture(); request['complexes'] = []; request['observations'] = [observation(point)]
            request['observations'][0]['geometry']['longitude'] += 20
            output = run_liminal_moirai(request)
            self.assertEqual(output['ssar']['appearances'][0]['qualification'], 'NO_CONTACT')
            self.assertIsNone(output['functional_notes'][0]['interpretation'])

    def test_all_seven_missing_inputs_and_incomplete_anchor_search_block(self):
        for point in POINTS:
            for field, value in (('geometry', None), ('robustness', None), ('core_anchor_search_complete', False)):
                request = fixture(); request['complexes'] = []; request['observations'] = [observation(point)]
                request['observations'][0][field] = value
                self.assertEqual(run_liminal_moirai(request)['ssar']['appearances'][0]['qualification'], 'BLOCKED')

    def test_all_seven_source_roles_identity_and_name_cannot_be_removed(self):
        for point in POINTS:
            for field in ('provenance', 'semantic_basis', 'method'):
                request = fixture(); request['complexes'] = []; request['observations'] = [observation(point)]
                effective = build_liminal_request(request)
                effective['appearances'][0][field]['source_refs'] = []
                self.assertEqual(run_ssar(effective, policy=load_liminal_policy())['appearances'][0]['qualification'], 'BLOCKED')
            for field in ('identity_status', 'verification_status'):
                effective = build_liminal_request(request); effective['appearances'][0]['provenance'][field] = 'PENDING'
                self.assertEqual(run_ssar(effective, policy=load_liminal_policy())['qualified_significators'], [])

    def test_all_seven_no_anchor_or_weak_robustness_are_only_secondary(self):
        for point in POINTS:
            for change in ('anchor', 'robustness'):
                request = fixture(); request['complexes'] = []; request['observations'] = [observation(point)]
                obs = request['observations'][0]
                if change == 'anchor': obs['core_root_refs'] = []
                else:
                    for sample in obs['robustness']['samples'][:2]: sample['longitude'] += 20
                self.assertEqual(run_liminal_moirai(request)['ssar']['secondary_support'], ['A1'])

    def test_all_seven_precision_or_grid_missing_are_not_support(self):
        for point in POINTS:
            for change in ('precision', 'grid'):
                request = fixture(); request['complexes'] = []; request['observations'] = [observation(point)]
                robust = request['observations'][0]['robustness']
                if change == 'precision': robust['input_precision_sufficient'] = None
                else: robust['samples'].pop()
                self.assertEqual(run_liminal_moirai(request)['ssar']['appearances'][0]['qualification'], 'BLOCKED')

    def test_missing_component_or_incomplete_search_not_absence(self):
        for fate in (False, True):
            for change in ('component', 'search'):
                request = fixture(fate)
                if change == 'component': request['complexes'][0]['appearance_refs'].pop()
                else: request['complexes'][0]['search_complete'] = False
                c = run_liminal_moirai(request)['complexes'][0]
                self.assertFalse(c['qualified_complex'])
                self.assertEqual(c['assessments']['functional_interpretation']['status'], 'NOT_EVALUABLE')
                self.assertEqual(c['assessments']['structural_geometry']['counterevidence_refs'], [])

    def test_evaluable_geometry_contradictor_precedes_other_missing_components(self):
        request = fixture(True)
        request['complexes'][0]['appearance_refs'] = ['A1']
        request['observations'][0]['geometry']['longitude'] += 30
        c = run_liminal_moirai(request)['complexes'][0]
        self.assertEqual(c['assessments']['structural_geometry']['status'], 'CONTRADICTED')
        self.assertEqual(c['assessments']['functional_interpretation']['status'], 'NOT_EVALUABLE')
        self.assertEqual(c['assessments']['structural_geometry']['counterevidence_refs'], ['A1'])

    def test_one_group_is_compatible_and_core_exception_is_forbidden(self):
        request = fixture()
        request['observations'][1].update(technique='SYNASTRY', subject_id='B')
        c = run_liminal_moirai(request)['complexes'][0]
        self.assertFalse(c['qualified_complex'])
        self.assertEqual(c['assessments']['functional_interpretation']['status'], 'COMPATIBLE')
        for obs in request['observations']: obs['core_root_refs'] = []
        c = run_liminal_moirai(request)['complexes'][0]
        self.assertIn('CORE_ANCHOR_MISSING', c['blockers'])
        self.assertIn('QUALIFIED_SIGNIFICATOR_MISSING', c['blockers'])

    def test_dependency_unknown_technical_statistical_and_equivalence_collapse(self):
        for relation in ('UNKNOWN', 'TECHNICAL_DEPENDENCY', 'STATISTICAL_DEPENDENCY', 'EQUIVALENT'):
            request = fixture()
            if relation == 'EQUIVALENT': request['observations'][1]['evidence_key'] = request['observations'][0]['evidence_key']
            request['edges'] = [dict(a='U:A1', b='U:A2', relation=relation, rule_id=load_liminal_policy()['dependency_rules'][relation])]
            c = run_liminal_moirai(request)['complexes'][0]
            self.assertEqual(len(c['effective_group_refs']), 1)
            self.assertFalse(c['qualified_complex'])

    def test_semantic_overlap_kept_distinct_and_composite_davison_share_group(self):
        request = fixture(True)
        request['observations'][2]['technique'] = 'DAVISON'
        request['edges'] = [dict(a='U:A1', b='U:A2', relation='SEMANTIC_OVERLAP',
                                rule_id=load_liminal_policy()['dependency_rules']['SEMANTIC_OVERLAP'])]
        output = run_liminal_moirai(request)
        self.assertTrue(output['complexes'][0]['qualified_complex'])
        self.assertEqual(len(output['complexes'][0]['effective_group_refs']), 2)
        self.assertFalse(output['ssar']['dependency_graph']['statistical_independence_established'])

    def test_eris_context_neither_supplies_missing_member_nor_second_group(self):
        request = fixture()
        request['observations'][1].update(technique='SYNASTRY', subject_id='B')
        request['observations'].append(observation('ERIS', 'E1', 'COMPOSITE', 210))
        request['complexes'][0]['appearance_refs'].append('E1')
        output = run_liminal_moirai(request); c = output['complexes'][0]
        self.assertEqual(c['context_refs'], ['E1'])
        self.assertEqual(len(c['effective_group_refs']), 1)
        self.assertFalse(c['qualified_complex'])
        self.assertEqual(c['assessments']['structural_geometry']['counterevidence_refs'], [])
        request['complexes'][0]['appearance_refs'] = ['A1', 'E1']
        self.assertEqual(run_liminal_moirai(request)['complexes'][0]['component_coverage'][1]['coverage'], 'MISSING')

    def test_moirai_shared_family_complex_no_added_units_strength_or_event(self):
        output = run_liminal_moirai(fixture(True))
        self.assertEqual(len(output['ssar']['dependency_graph']['units']), 4)
        self.assertEqual(len(output['shared_contacts']), 4)
        self.assertTrue(all(not c['contributes_new_evidence'] for c in output['shared_contacts']))
        self.assertIsNone(output['families'][0]['cluster_strength'])
        self.assertEqual(output['ssar']['temporal_activation'], [])
        self.assertEqual(output['ssar']['documentary_correspondence'], [])

    def test_family_missing_component_is_partial_and_never_zero(self):
        request = fixture(True); request['complexes'] = []; request['observations'].pop()
        family = run_liminal_moirai(request)['families'][0]
        self.assertEqual(family['coverage'], 'PARTIAL')
        self.assertEqual(family['components'][-1]['coverage'], 'MISSING')
        self.assertIsNone(family['cluster_strength'])
        self.assertNotIn('winner', family)

    def test_weak_robustness_of_required_member_prevents_complex_qualification(self):
        request = fixture()
        for sample in request['observations'][1]['robustness']['samples'][:2]:
            sample['longitude'] += 20
        c = run_liminal_moirai(request)['complexes'][0]
        self.assertFalse(c['qualified_complex'])
        self.assertIn('ROBUST_COMPONENT_CONTACTS_NOT_MET', c['blockers'])
        self.assertEqual(c['assessments']['functional_interpretation']['status'], 'INSUFFICIENT')

    def test_negative_eris_context_does_not_contradict_positive_liminal_complex(self):
        request = fixture()
        obs = observation('ERIS', 'E1', 'SYNASTRY', 210)
        obs['geometry']['longitude'] += 20
        request['observations'].append(obs)
        request['complexes'][0]['appearance_refs'].append('E1')
        c = run_liminal_moirai(request)['complexes'][0]
        self.assertTrue(c['qualified_complex'])
        self.assertEqual(c['assessments']['functional_interpretation']['counterevidence_refs'], [])

    def test_inherited_persephone_data_link_does_not_add_evidence(self):
        request = fixture(); obs = request['observations'][1]
        record = {k: copy.deepcopy(v) for k, v in obs.items() if k != 'id'}
        record.update(appearance_ref=obs['id'], artifact_ref='synthetic:phase4', upstream_layer='DEMETER_PERSEPHONE_SEPARATION_RETURN_COMPLEX')
        before = run_liminal_moirai(request)
        request['existing_contacts'] = [record]; after = run_liminal_moirai(request)
        self.assertEqual(before['ssar'], after['ssar'])
        self.assertFalse(after['reused_contacts'][0]['contributes_new_evidence'])
        validate_liminal_result(after, request=request)

    def test_reuse_context_geometry_roots_perturbations_and_duplicates_checked(self):
        for change in ('context', 'geometry', 'roots', 'samples', 'duplicate', 'ref'):
            request = fixture(); obs = request['observations'][1]
            record = {k: copy.deepcopy(v) for k, v in obs.items() if k != 'id'}
            record.update(appearance_ref=obs['id'], artifact_ref='synthetic:phase4', upstream_layer='DEMETER_PERSEPHONE_SEPARATION_RETURN_COMPLEX')
            if change == 'context': record['subject_id'] = 'A'
            if change == 'geometry': record['geometry']['longitude'] += 1
            if change == 'roots': record['core_root_refs'] = []
            if change == 'samples': record['robustness']['samples'][0]['longitude'] += 1
            if change == 'ref': record['appearance_ref'] = 'MISSING'
            request['existing_contacts'] = [record, copy.deepcopy(record)] if change == 'duplicate' else [record]
            with self.assertRaises(ValueError): run_liminal_moirai(request)

    def test_duplicate_contact_reference_unknown_object_and_nonfinite_rejected(self):
        for change in ('duplicate', 'broken', 'object', 'finite', 'context'):
            request = fixture()
            if change == 'duplicate':
                obs = copy.deepcopy(request['observations'][0]); obs['id'] = 'OTHER'; request['observations'].append(obs)
            if change == 'broken': request['complexes'][0]['appearance_refs'] = ['MISSING']
            if change == 'object': request['observations'][0]['point_id'] = 'KARMA'
            if change == 'finite': request['observations'][0]['geometry']['longitude'] = float('inf')
            if change == 'context': request['observations'][0]['subject_id'] = 'RELATIONSHIP'
            with self.assertRaises((ValueError, ValidationError)): run_liminal_moirai(request)

    def test_source_class_cannot_be_promoted_to_doctrine(self):
        request = build_liminal_request(fixture())
        request['appearances'][0]['semantic_basis']['epistemic_class'] = 'C_DOCTRINE'
        self.assertEqual(run_ssar(request, policy=load_liminal_policy())['appearances'][0]['qualification'], 'BLOCKED')

    def test_result_four_scopes_hash_and_group_tampering_rejected(self):
        request = fixture()
        for scope in ('structural_geometry', 'functional_interpretation', 'temporal_activation', 'documentary_correspondence'):
            output = run_liminal_moirai(request); output['complexes'][0]['assessments'][scope]['status'] = 'CONTRADICTED'
            with self.assertRaises(ValueError): validate_liminal_result(output, request=request)
        for field, value in (('qualified_complex', False), ('effective_group_refs', []), ('cluster_strength', 99)):
            output = run_liminal_moirai(request); output['complexes'][0][field] = value
            with self.assertRaises((ValueError, ValidationError)): validate_liminal_result(output, request=request)
        output = run_liminal_moirai(request); output['catalog_hash'] = '0' * 64
        with self.assertRaises(ValueError): validate_liminal_result(output, request=request)

    def test_defaults_previous_catalogs_and_inputs_unchanged(self):
        request = fixture(True); before = copy.deepcopy(request)
        catalog, policy = load_families_catalog(), load_families_policy()
        run_liminal_moirai(request)
        self.assertEqual(request, before)
        self.assertEqual(load_families_catalog(), catalog)
        self.assertEqual(load_families_policy(), policy)
        self.assertEqual(load_ssar_policy()['point_rules'], {})
        self.assertEqual(len(load_liminal_catalog()['entries']), 7)

    def test_disabled_ignores_history_without_extras_and_empty_is_not_absence(self):
        self.assertEqual(run_liminal_moirai({'enabled': False, 'history': 'ignored'})['completion'], 'NONE')
        code = "import sys;sys.path.insert(0,'src');from almas_tfa.ssar_liminal_moirai import run_liminal_moirai;assert run_liminal_moirai({'enabled':False})['ssar']['execution_status']=='not_run'"
        subprocess.run([sys.executable, '-S', '-c', code], cwd=ROOT, check=True)
        result = run_liminal_moirai({'enabled': True})
        self.assertEqual(result['completion'], 'NONE')
        self.assertEqual(result['families'][0]['coverage'], 'PARTIAL')


if __name__ == '__main__':
    unittest.main()
