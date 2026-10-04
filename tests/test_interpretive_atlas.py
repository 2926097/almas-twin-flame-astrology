import copy
import json
from pathlib import Path
import unittest

from almas_tfa.interpretive_atlas import build_interpretive_atlas, audit_interpretive_coverage, resolve_pointer
from almas_tfa.evidence_handlers import m15_evidence_extraction, m16_dependency_deduplication, m17_independent_roots
from almas_tfa.module_contract import ModuleContext
from almas_tfa.relational_handlers import m04_nodes_angles_houses_regencies


def ctx(mid, canonical):
    return ModuleContext(module_id=mid, module_name=mid, mode='FULL', raw_input={"maximum_definition_context": True}, canonical_snapshot=canonical, prior_results={})


class TestInterpretiveAtlas(unittest.TestCase):
    def fixture(self):
        return {'natal_context': {'subjects': {'A/~': {'point_signs': {'VENUS': {'longitude': 42., 'sign': 'TAURUS', 'speed': 0., 'retrograde': False}}, 'house_placements': {'VENUS': {'house': 8}}}}},
                'evidence': [{'root_id': 'R1', 'concrete_contacts': [{'subject_a': 'A/~', 'point_a': 'VENUS', 'subject_b': 'B', 'point_b': 'SOUTH_NODE', 'relation_id': 'SQUARE', 'orb': 0., 'orb_limit': 3., 'layer_a': 'NATAL', 'layer_b': 'DRACONIC'}]}],
                'vedic': {'charts': [{'birth': 'PRIVATE', 'd9': {'Venus': {'sign': 4, 'longitude': None}}}], 'synastry': {'features': [{'object_a': 'DK', 'object_b': 'UL', 'varga_a': 'D1', 'varga_b': 'D9', 'sign_relation': [1, 1], 'root_dependency_id': 'dep'}]}},
                'models': {'LG': {'state': 'INSUFFICIENT', 'iem': 70}}, 'raw_input': {'birth': 'PRIVATE'}}

    def test_no_mutation_no_values_and_all_refs_resolve(self):
        canonical = self.fixture(); before = copy.deepcopy(canonical)
        atlas = build_interpretive_atlas(canonical)
        self.assertEqual(canonical, before)
        self.assertNotIn('PRIVATE', json.dumps(atlas))
        for ref in atlas['leaf_refs']:
            resolve_pointer(canonical, ref)
        contact = next(row for row in atlas['entries'] if '/concrete_contacts/' in row['data_ref'])
        self.assertEqual(len(contact['natal_substrate_refs']), 2)
        self.assertEqual(resolve_pointer(canonical, contact['natal_substrate_refs'][0])['sign'], 'TAURUS')
        self.assertNotIn('orb', contact['missing_dimensions'])
        self.assertNotIn('retrograde', next(row for row in atlas['entries'] if 'point_signs' in row['data_ref'])['missing_dimensions'])
        self.assertEqual(atlas, build_interpretive_atlas(canonical))

    def test_vedic_sign_only_never_invented_longitude(self):
        canonical = self.fixture(); atlas = build_interpretive_atlas(canonical)
        row = next(r for r in atlas['entries'] if '/features/' in r['data_ref'])
        self.assertEqual(row['kind'], 'contact')
        self.assertEqual(row['missing_dimensions'], [])
        pos = next(r for r in atlas['entries'] if '/d9/' in r['data_ref'])
        self.assertIn('longitude', pos['missing_dimensions'])
        self.assertIsNone(canonical['vedic']['charts'][0]['d9']['Venus']['longitude'])

    def test_editorial_omissions_and_stale_atlas_fail_closed(self):
        canonical = self.fixture(); atlas = build_interpretive_atlas(canonical)
        self.assertEqual(audit_interpretive_coverage(canonical, atlas, [])['state'], 'PARTIAL')
        dispositions = [{'data_ref': r['data_ref'], 'state': 'EXCLUDED', 'reason': 'Contexto duplicado o fuera del perfil solicitado.'} for r in atlas['entries']]
        self.assertEqual(audit_interpretive_coverage(canonical, atlas, dispositions)['state'], 'COMPLETE')
        canonical['models']['LG']['iem'] = 71
        with self.assertRaises(ValueError): audit_interpretive_coverage(canonical, atlas, dispositions)

    def test_doctrine_needs_passage_and_dynamics(self):
        canonical = self.fixture(); atlas = build_interpretive_atlas(canonical)
        row = atlas['entries'][0]
        result = audit_interpretive_coverage(canonical, atlas, [{'data_ref': row['data_ref'], 'state': 'INTERPRETED', 'reason': 'Tema relevante', 'epistemic_class': 'C_DOCTRINE'}])
        self.assertTrue(any('fuente/pasaje' in issue for issue in result['issues']))
        self.assertTrue(any('dynamic' in issue for issue in result['issues']))

    def test_adding_details_does_not_inflate_axis_root(self):
        contacts = [{'subject_a': 'A', 'point_a': a, 'subject_b': 'B', 'point_b': 'SUN', 'aspect': aspect, 'angle': angle, 'orb': .5, 'orb_limit': 3., 'exactness': .97} for a, aspect, angle in [('ASC','CONJUNCTION',0.),('DSC','OPPOSITION',180.)]]
        def roots(cs):
            c={'synastry': {'contacts': cs}}
            for mid, handler in [('M15',m15_evidence_extraction),('M16',m16_dependency_deduplication),('M17',m17_independent_roots)]:
                c.update(handler(ctx(mid,c)).canonical_updates)
            return c['independent_roots']['roots']
        baseline=roots(contacts)
        enriched=copy.deepcopy(contacts)
        for contact in enriched: contact.update(longitude_a=10., longitude_b=10., applying=False)
        changed=roots(enriched)
        self.assertEqual(len(baseline),len(changed))
        self.assertEqual([(r['root_key'],r['strength']) for r in baseline],[(r['root_key'],r['strength']) for r in changed])
        self.assertEqual(changed[0]['concrete_contacts'][0]['orb'], .5)
        self.assertIs(changed[0]['concrete_contacts'][0]['applying'],False)

    def test_motion_survives_m04(self):
        charts={sid: {'positions': {'VENUS': {'longitude': 42., 'declination': -12., 'speed': 0., 'retrograde': False}}, 'timed': False} for sid in ('A','B')}
        result=m04_nodes_angles_houses_regencies(ctx('M04',{'natal': {'charts': charts}}))
        data=result.payload['subjects']['A']['point_signs']['VENUS']
        self.assertEqual(data['declination'],-12.)
        self.assertEqual(data['speed'],0.)
        self.assertIs(data['retrograde'],False)

    def test_maximum_definition_flag_rejects_non_booleans_in_direct_handlers(self):
        for value in ("true", 0, 1, None, [], {}):
            raw = {"maximum_definition_context": value}
            for mid, handler in (
                ("M04", m04_nodes_angles_houses_regencies),
                ("M17", m17_independent_roots),
            ):
                context = ModuleContext(
                    module_id=mid, module_name=mid, mode="FULL", raw_input=raw,
                    canonical_snapshot={}, prior_results={},
                )
                with self.subTest(value=value, module=mid):
                    with self.assertRaisesRegex(ValueError, "maximum_definition_context debe ser booleano"):
                        handler(context)

    def test_atlas_schema(self):
        import jsonschema
        root=Path(__file__).resolve().parents[1]
        jsonschema.validate(build_interpretive_atlas(self.fixture()),json.loads((root/'schemas/interpretive-atlas.schema.json').read_text()))

if __name__ == '__main__': unittest.main()
