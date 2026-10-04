"""Regression tests for audit findings and lossless canonical reporting."""
import copy
import json
from importlib import resources
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from almas_tfa.phase_preregistration import verify_phase_preregistration
from almas_tfa.vedic.chart import chart_from_sidereal
from almas_tfa.vedic.pipeline import attach_vedic, run_vedic_pipeline, render_vedic_report
from almas_tfa.vedic.synastry import compute_vedic_synastry, compute_vedic_event_activation
from almas_tfa.vedic.validation import descriptive_shapley, group_ablation
from almas_tfa.vedic.reporting import build_vedic_report_model
from almas_tfa.vedic.cli import main

ROOT = Path(__file__).resolve().parents[1]
POS = dict(Sun=72.8, Moon=20.4, Mars=73.9, Mercury=85.3, Jupiter=35.7,
           Venus=77.4, Saturn=32.5, Rahu=91.7, Lagna=154.)


def envelope():
    a = chart_from_sidereal(POS, birth='2000-01-01T12:00:00Z')
    b = chart_from_sidereal({k:(v+17)%360 for k,v in POS.items()}, birth='2001-01-01T12:00:00Z')
    syn = compute_vedic_synastry(a,b)
    out = run_vedic_pipeline({'enabled':False})
    out.update(enabled=True,charts=[a,b],synastry=syn,ablation=group_ablation(syn),shapley=descriptive_shapley(syn))
    return out


class AuditDepurationTests(unittest.TestCase):
    def test_packaged_frozen_bytes_equal_repository_and_verify_default(self):
        data=resources.files('almas_tfa').joinpath('data')
        record=json.loads(data.joinpath('phase-preregistration-1.22.0.json').read_text())
        self.assertEqual(verify_phase_preregistration(record)['status'],'VERIFIED')
        for item in record['frozen_artifacts']:
            self.assertEqual(data.joinpath(Path(item['path']).name).read_bytes(),(ROOT/item['path']).read_bytes())
        self.assertEqual(data.joinpath('vedic-envelope-schema.json').read_bytes(),(ROOT/'schemas/vedic.schema.json').read_bytes())

    def test_incomplete_active_envelope_rejected_and_input_preserved(self):
        bad=dict(schema_version='ALMAS_VED_ENVELOPE_1',canonical_effect=False,external_validation='NOT_PERFORMED',
                 metaphysical_assessment='INSUFFICIENT',enabled=True,charts=[],synastry=None)
        before=copy.deepcopy(bad)
        with self.assertRaises(ValueError):attach_vedic({},bad)
        self.assertEqual(bad,before)

    def test_schema_type_duplicate_unknown_ref_hash_and_count_rejected(self):
        e=envelope()
        mutations=[lambda r:r['synastry']['features'].append(copy.deepcopy(r['synastry']['features'][0])),
                   lambda r:r['synastry']['features'][0].update(object_a='UNKNOWN'),
                   lambda r:r['synastry']['chart_hashes'].__setitem__(0,'0'*64),
                   lambda r:r['temporal_readiness'].update(events_requested=1),
                   lambda r:r['synastry']['methodological_readiness']['descriptive'].update(feature_count=-1),
                   lambda r:r['charts'][0].update(canonical_effect=True),
                   lambda r:r.update(sensitivity=[{}]),
                   lambda r:r['charts'][0].update(confidence={}),
                   lambda r:r['charts'][0]['d1']['Sun'].update(longitude=True)]
        for change in mutations:
            bad=copy.deepcopy(e);change(bad)
            with self.assertRaises(ValueError):attach_vedic({},bad)

    def test_boolean_nonfinite_string_orbs_rejected_in_both_functions(self):
        a,b=envelope()['charts']
        for value in (True,False,float('nan'),float('inf'),'1',None,-1,6):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):compute_vedic_synastry(a,b,orb_deg=value)
                with self.assertRaises(ValueError):compute_vedic_event_activation(a,b,{'timestamp':'2026-01-01T12:00:00Z'},orb_deg=value)

    def test_lossless_report_no_recalculation_and_core_identity(self):
        e=envelope();before=copy.deepcopy(e)
        core={'models':{'AF':17},'indices':{'IRC':10}}
        augmented=attach_vedic(core,e)
        with patch('almas_tfa.vedic.chart.compute_vedic_chart',side_effect=AssertionError('recalculation')):
            model=build_vedic_report_model(e);text=render_vedic_report(e)
        self.assertEqual(model['coverage']['projected_features'],len(e['synastry']['features']))
        self.assertEqual(model['coverage']['excluded_feature_ids'],[])
        for f in e['synastry']['features']:
            self.assertIn('Ficha '+f['feature_id'],text)
        self.assertEqual({k:v for k,v in augmented.items() if k!='vedic'},core)
        self.assertEqual(e,before)
        self.assertFalse(model['canonical_effect'])

    def test_divisional_and_sign_only_endpoints_never_get_physical_longitude(self):
        m=build_vedic_report_model(envelope())
        for p in m['positions']:
            if p['layer']=='D9' or p['object'] in ('AL','UL','A7','KARAKAMSHA'):
                self.assertIsNone(p['longitude_deg'])
            self.assertIsNone(p['house'])
        aliases=[p for p in m['positions'] if p['object']=='AK']
        self.assertTrue(all(p['source_object'] in POS for p in aliases))

    def test_subject_swap_preserves_geometry_and_feature_order_keeps_identity(self):
        a,b=envelope()['charts'];forward=compute_vedic_synastry(a,b);reverse=compute_vedic_synastry(b,a)
        rev={(f['varga_b'],f['object_b'],f['varga_a'],f['object_a']):f for f in reverse['features']}
        for f in forward['features']:
            r=rev[(f['varga_a'],f['object_a'],f['varga_b'],f['object_b'])]
            self.assertEqual(f['angular_contacts_deg'],r['angular_contacts_deg'])
            self.assertEqual(f['same_sign'],r['same_sign'])
            self.assertEqual(f['sign_relation'],list(reversed(r['sign_relation'])))
        e=envelope();original=build_vedic_report_model(e)
        e['synastry']['features'].reverse();reordered=build_vedic_report_model(e)
        self.assertEqual({r['feature_id'] for r in original['contacts']},{r['feature_id'] for r in reordered['contacts']})

    def test_cli_report_canonical_and_model_without_astronomical_backend(self):
        e=envelope()
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'input.json';out=Path(d)/'out.json'
            source.write_text(json.dumps({'vedic':e}),encoding='utf-8')
            with patch('almas_tfa.vedic.cli.compute_vedic_chart',side_effect=AssertionError('recalculation')):
                self.assertEqual(main(['report-model',str(source),'-o',str(out)]),0)
                self.assertEqual(json.loads(out.read_text())['coverage']['status'],'COMPLETE')
                self.assertEqual(main(['report-canonical',str(source),'-o',str(out)]),0)
                self.assertIn('Ficha VED.',out.read_text())

    def test_temporal_nested_promotion_and_unknown_roots_rejected(self):
        e=envelope();a,b=e['charts']
        event=dict(event_id='E1',**compute_vedic_event_activation(a,b,{'timestamp':'2026-01-01T12:00:00Z'},synastry=e['synastry']))
        e['events']=[event];e['temporal_readiness'].update(status='DESCRIPTIVE_ONLY',events_requested=1,vimshottari_subject_results=2)
        attach_vedic({},e)
        promoted=copy.deepcopy(e);promoted['events'][0]['predicts_event']=True
        with self.assertRaises(ValueError):attach_vedic({},promoted)
        broken=copy.deepcopy(e);broken['events'][0]['persons'][0]['periods']['antara']['end']='2000-01-01T00:00:00Z'
        with self.assertRaises(ValueError):attach_vedic({},broken)
        self.assertIn(event['persons'][0]['periods']['maha']['start'],render_vedic_report(e))
