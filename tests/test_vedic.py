"""Fixtures documentales, límites y firewall de la capa VED."""
import copy
import importlib.util
import json
from datetime import timedelta
from math import nextafter, inf
from pathlib import Path
import unittest
from almas_tfa.vedic import *
from almas_tfa.vedic.chart import DEFAULTS, settings, compute_time_upagrahas
from almas_tfa.vedic.geometry import longitude
from almas_tfa.vedic.pipeline import run_vedic_pipeline, attach_vedic, render_vedic_report
from almas_tfa.vedic.synastry import _fingerprint
from almas_tfa.vedic.timing import instant
from almas_tfa.vedic.validation import (benjamini_hochberg, compute_sensitivity,
    descriptive_shapley, group_ablation, validate_corpus)
from almas_tfa.analysis import analyze_precomputed

ROOT = Path(__file__).resolve().parents[1]
POS = dict(Sun=72+47/60, Moon=20+28/60, Mars=73+51/60, Mercury=85+18/60,
           Jupiter=35+40/60, Venus=77+21/60, Saturn=32+28/60, Rahu=91+43/60, Lagna=154.)
BIRTH = '2000-01-01T12:00:00+00:00'
RAW = dict(timestamp=BIRTH,latitude=0.,longitude=0.,birth_time_quality='SYNTHETIC_EXACT')
SWE = importlib.util.find_spec('swisseph') is not None


def chart(positions=None):
    return chart_from_sidereal(positions or POS, birth=BIRTH)


class VedicGeometryTests(unittest.TestCase):
    def test_all_108_pada_boundaries(self):
        for i in range(108):
            x = i * 10 / 3
            nk = compute_nakshatra(x)
            self.assertEqual(nk['index'],i//4+1)
            self.assertEqual(nk['pada'],i%4+1)
            self.assertEqual(compute_nakshatra(x+1e-6)['pada'],i%4+1)
            if i:
                self.assertEqual(compute_nakshatra(x-1e-6)['pada'],(i-1)%4+1)

    def test_longitude_normalization_and_invalids(self):
        self.assertEqual(compute_nakshatra(360)['index'],1)
        self.assertEqual(longitude(-1),359)
        for value in (True, float('nan'), float('inf'),'30', None):
            with self.assertRaises(ValueError): longitude(value)

    def test_navamsha_reference_example_16(self):
        self.assertEqual(compute_navamsha(71)['sign'],9)  # Mercury 11 Gemini -> Capricorn
        self.assertEqual(compute_navamsha(229)['sign'],8) # Jupiter 19 Scorpio -> Sagittarius
        self.assertFalse(compute_navamsha(71)['physical_longitude'])

    def test_all_navamsha_sign_allocations_independent_element_rule(self):
        starts = (0,9,6,3)
        for sign in range(12):
            for part in range(9):
                lon = sign*30 + (part+.5)*10/3
                self.assertEqual(compute_navamsha(lon)['sign'],(starts[sign%4]+part)%12)

    def test_karakas_documentary_example_28(self):
        result=compute_chara_karakas(POS,8)
        self.assertEqual(result['roles'],dict(AK='Rahu',AmK='Mercury',BK='Moon',MK='Venus',
                                             PiK='Mars',PK='Sun',GK='Jupiter',DK='Saturn'))

    def test_seven_karakas_exclude_nodes(self):
        r=compute_chara_karakas(POS,7)
        self.assertEqual(r['roles']['AK'],'Mercury')
        self.assertNotIn('PiK',r['roles'])
        self.assertNotIn('Rahu',r['ranking'])

    def test_karaka_ties_fail_closed(self):
        pos={**POS,'Moon':POS['Sun']}
        r=compute_chara_karakas(pos)
        self.assertEqual(r['status'],'NOT_EVALUABLE')
        self.assertEqual(r['roles'],{})
        self.assertEqual(chart(pos)['karakamsha']['status'],'NOT_EVALUABLE')

    def test_arudha_documentary_example_29_all_twelve(self):
        pos=dict(Sun=330.,Moon=60.,Mars=0.,Mercury=330.,Jupiter=0.,Venus=330.,Saturn=0.)
        result=compute_arudhas(150.,pos)
        names=['AL','A2','A3','A4','A5','A6','A7','A8','A9','A10','A11','UL']
        self.assertEqual([result[k]['sign'] for k in names],[2,4,5,4,0,2,1,9,9,5,1,6])
        self.assertTrue(result['A5']['correction_applied']) # raw 7th, ruler fourth
        self.assertTrue(all(v['longitude'] is None for v in result.values()))

    def test_arudha_variant_is_not_silently_substituted(self):
        with self.assertRaises(ValueError): compute_arudhas(0,POS,'CO_LORDS')

    def test_bindu_wrap_and_antipode(self):
        r=compute_bhrigu_bindu(10,350)
        self.assertEqual(r['longitude'],0)
        self.assertEqual(r['antipode'],180)
        self.assertEqual(compute_bhrigu_bindu(350,10)['longitude'],180)
        self.assertEqual(compute_bhrigu_bindu(180,0,'SHORTEST_ARC')['status'],'NOT_EVALUABLE')

    def test_solar_upagrahas_example_6(self):
        r=compute_solar_upagrahas(249+36/60)
        self.assertAlmostEqual(r['DHUMA']['longitude'],22+56/60)
        self.assertAlmostEqual(r['VYATIPATA']['longitude'],337+4/60)
        self.assertAlmostEqual(r['UPAKETU']['longitude'],219+36/60)

    def test_saham_reverses_at_night_and_correction(self):
        self.assertEqual(compute_vivaha_saham(120,30,60,is_day=True,annual_context=True)['longitude'],150)
        r=compute_vivaha_saham(120,30,60,is_day=False,annual_context=True)
        self.assertEqual(r['longitude'],0)
        self.assertEqual(r['correction_deg'],30)
        with self.assertRaises(ValueError): compute_vivaha_saham(120,30,60,is_day=True,annual_context=False)

    def test_rahu_ketu_single_axis(self):
        c=chart()
        self.assertAlmostEqual((c['d1']['Ketu']['longitude']-c['d1']['Rahu']['longitude'])%360,180)
        with self.assertRaises(ValueError): chart_from_sidereal({**POS,'Ketu':0})

    def test_abhijit_is_overlay_not_dasha_change(self):
        p={**POS,'Moon':278}
        a=chart_from_sidereal(p,configuration={'abhijit_overlay':True},birth=BIRTH)
        b=chart_from_sidereal(p,birth=BIRTH)
        self.assertTrue(a['abhijit_overlay']['Moon']['active'])
        self.assertEqual(a['d1']['Moon'],b['d1']['Moon'])

    def test_time_upagrahas_raos_thursday_night_example(self):
        base=2451545.
        context=dict(start_jd=base,end_jd=base+.5,last_sunrise_jd=base-.5,weekday=4,is_day=False)
        r=compute_time_upagrahas(context,lambda x:(x-base)*360,'RAO_2000_MIDDLE_GULIKA_BEGIN_MANDI')
        # Jupiter fourth slot: 22:30–00:00, midpoint 23:15 (=5.25h after 18:00).
        self.assertAlmostEqual(r['YAMA_GHANTAKA']['longitude'],5.25/24*360)
        self.assertNotEqual(r['GULIKA']['longitude'],r['MANDI']['longitude'])

    def test_default_file_matches_code(self):
        defaults=json.loads((ROOT/'src/almas_tfa/data/vedic-defaults.json').read_text())
        self.assertEqual(defaults,DEFAULTS)
        with self.assertRaises(ValueError): settings({'ayanamsha':'FAKE'})
        with self.assertRaises(ValueError): settings({'ayanamsha':'CUSTOM'})
        with self.assertRaises(ValueError): settings({'unexpected':1})

    def test_documentary_fixture_is_consumed_and_sources_resolve(self):
        f=json.loads((ROOT/'fixtures/vedic/documentary.json').read_text())
        self.assertEqual([compute_navamsha(x)['sign'] for x in f['d9']['input_deg']],f['d9']['expected_sign_zero_based'])
        r=compute_arudhas(f['arudha']['lagna_deg'],f['arudha']['positions_deg'])
        keys=['AL','A2','A3','A4','A5','A6','A7','A8','A9','A10','A11','UL']
        self.assertEqual([r[k]['sign'] for k in keys],f['arudha']['expected_signs_zero_based'])
        anchors=json.loads((ROOT/'src/almas_tfa/data/vedic-source-anchors.json').read_text())
        ids={x['id'] for x in anchors['entries']}
        self.assertIn(compute_nakshatra(0)['source_ref'],ids)
        self.assertIn(compute_navamsha(0)['source_ref'],ids)


class VedicTimingTests(unittest.TestCase):
    def test_vimshottari_example_50_balance_and_savana_end(self):
        r=compute_vimshottari(302+23/60,'2000-04-28T05:50:00-04:00','2001-01-01T00:00:00Z',360)
        self.assertAlmostEqual(r['balance_at_birth_years'],2.24875)
        self.assertEqual(r['maha']['lord'],'Mars')
        expected=instant('2000-04-28T05:50:00-04:00')+timedelta(days=2.24875*360)
        self.assertLess(abs((instant(r['maha']['end'])-expected).total_seconds()),.001)

    def test_birth_balance_does_not_restart_subperiods(self):
        r=compute_vimshottari(302+23/60,BIRTH,BIRTH,360)
        self.assertNotEqual(r['antara']['lord'],'Mars')
        self.assertLess(instant(r['maha']['start']),instant(BIRTH))

    def test_periods_are_nested_and_semiopen(self):
        r=compute_vimshottari(0,BIRTH,BIRTH,360)
        self.assertEqual(r['maha']['lord'],'Ketu')
        self.assertEqual(r['antara']['lord'],'Ketu')
        after=compute_vimshottari(0,BIRTH,r['maha']['end'],360)
        self.assertEqual(after['maha']['lord'],'Venus')
        for key in ('maha','antara','pratyantara'):
            self.assertLessEqual(instant(r[key]['start']),instant(BIRTH))
            self.assertGreater(instant(r[key]['end']),instant(BIRTH))

    def test_no_naive_birth_or_before_birth(self):
        with self.assertRaises(ValueError): compute_vimshottari(0,'2000-01-01T12:00:00',BIRTH)
        with self.assertRaises(ValueError): compute_vimshottari(0,BIRTH,'1999-01-01T00:00:00Z')
        with self.assertRaises(ValueError): compute_vimshottari(0,BIRTH,BIRTH,365)


class VedicSynastryTests(unittest.TestCase):
    def test_matrix_covers_all_four_layers_and_stable_ids(self):
        r=compute_vedic_synastry(chart(),chart())
        self.assertEqual({(f['varga_a'],f['varga_b']) for f in r['features']},{('D1','D1'),('D1','D9'),('D9','D1'),('D9','D9')})
        self.assertEqual(len(r['features']),len({f['feature_id'] for f in r['features']}))
        self.assertTrue(all(f['default_weight']==0 for f in r['features']))

    def test_sign_only_and_d9_never_gain_degrees(self):
        r=compute_vedic_synastry(chart(),chart())
        for f in r['features']:
            if f['varga_a']=='D9' or f['varga_b']=='D9' or f['object_a'] in ('UL','AL','A7','KARAKAMSHA'):
                self.assertIsNone(f['separation_deg'])
                self.assertIsNone(f['orb_deg'])
                self.assertEqual(f['angular_contacts_deg'],[])

    def test_alias_ak_and_planet_share_input_bundle(self):
        r=compute_vedic_synastry(chart(),chart())
        by={f['feature_id']:f for f in r['features']}
        self.assertEqual(by['VED.D1.AK__D1.Moon']['root_dependency_id'],by['VED.D1.Rahu__D1.Moon']['root_dependency_id'])
        self.assertLess(r['recurrence']['dependency_bundles'],r['recurrence']['raw_matches'])

    def test_node_antipodes_share_one_dependency_axis(self):
        by={f['feature_id']:f for f in compute_vedic_synastry(chart(),chart())['features']}
        self.assertEqual(by['VED.D1.Rahu__D1.Moon']['root_dependency_id'],by['VED.D1.Ketu__D1.Moon']['root_dependency_id'])
        self.assertEqual(by['VED.D1.Rahu__D1.Moon']['root_dependency_id'],by['VED.D9.Ketu__D1.Moon']['root_dependency_id'])

    def test_ived_and_ontology_remain_unvalidated(self):
        r=compute_vedic_synastry(chart(),chart())
        self.assertIsNone(r['ived']['value'])
        self.assertEqual(r['metaphysical_assessment'],'INSUFFICIENT')
        self.assertIsNone(r['compatibility']['total_score'])
        self.assertFalse(r['canonical_effect'])
        audit=r['methodological_readiness']
        self.assertEqual(audit['independence']['status'],'NOT_ESTABLISHED')
        self.assertIsNone(audit['independence']['independent_root_count'])
        self.assertEqual(audit['ashtakuta']['status'],'NOT_EVALUABLE')
        self.assertEqual(audit['ashtakuta']['total_score'],None)
        self.assertEqual(audit['ived']['gates'],dict(preregistered=False,calibrated=False,external_validation=False))

    def test_incompatible_profiles_rejected(self):
        b=chart_from_sidereal(POS,configuration={'ayanamsha':'RAMAN'})
        with self.assertRaises(ValueError): compute_vedic_synastry(chart(),b)

    def test_shapley_shared_coverage_efficiency(self):
        r=descriptive_shapley(compute_vedic_synastry(chart(),chart()))
        self.assertAlmostEqual(sum(r['values'].values()),r['total'])
        self.assertFalse(r['interpretive_importance'])

    def test_bh_monotone_and_invalids(self):
        self.assertEqual(benjamini_hochberg([.01,.04,.03]),[.03,.04,.04])
        self.assertEqual(benjamini_hochberg([]),[])
        with self.assertRaises(ValueError): benjamini_hochberg([float('nan')])

    def test_core_identity_and_disabled_envelope(self):
        c=analyze_precomputed({'pillars':{'PA':90,'PR':80,'PE':70,'PX':60}})
        envelope=run_vedic_pipeline({'enabled':False})
        augmented=attach_vedic(c,envelope)
        self.assertEqual({k:v for k,v in augmented.items() if k!='vedic'},c)
        self.assertNotIn('vedic',c)
        with self.assertRaises(ValueError): attach_vedic(augmented,envelope)

    def test_optional_canonical_schema_accepts_vedic_without_changing_core(self):
        from test_canonical_schema_validation import canonical_validator, valid_canonical_analysis
        core=valid_canonical_analysis()
        augmented=attach_vedic(core,run_vedic_pipeline({'enabled':False}))
        canonical_validator().validate(augmented)
        self.assertEqual({k:v for k,v in augmented.items() if k!='vedic'},core)

    def test_promotion_and_wrong_weights_rejected(self):
        r=run_vedic_pipeline({'enabled':False});r['canonical_effect']=True
        with self.assertRaises(ValueError): attach_vedic({},r)
        with self.assertRaises(ValueError): run_vedic_pipeline({'enabled':'false'})

    def test_temporal_activation_no_new_roots(self):
        r=compute_vedic_event_activation(chart(),chart(),dict(timestamp='2026-10-04T12:00:00Z'))
        self.assertEqual(r['temporal_independent_root_count'],0)
        self.assertFalse(r['predicts_event'])

    def test_temporal_structure_hash_mismatch_rejected(self):
        syn=compute_vedic_synastry(chart(),chart())
        b=chart({**POS,'Moon':31.})
        with self.assertRaises(ValueError): compute_vedic_event_activation(chart(),b,dict(timestamp=BIRTH),synastry=syn)


@unittest.skipUnless(SWE,'Extra astronomy-vedic no instalado')
class VedicAstronomyTests(unittest.TestCase):
    def test_real_backend_provenance_and_all_upagrahas(self):
        c=compute_vedic_chart(RAW)
        self.assertEqual(c['provenance']['engine'],'SWISS_EPHEMERIS_MOSHIER')
        self.assertEqual(len(c['upagrahas']),11)
        self.assertEqual(c['confidence']['birth_time'],'SYNTHETIC_EXACT')

    def test_swiss_direct_sidereal_flag_agrees_with_conversion(self):
        import swisseph as swe
        for profile,mode in (('LAHIRI',swe.SIDM_LAHIRI),('RAMAN',swe.SIDM_RAMAN),('KP',swe.SIDM_KRISHNAMURTI)):
            c=compute_vedic_chart(RAW,{'ayanamsha':profile})
            swe.set_sid_mode(mode)
            moon=swe.calc_ut(c['provenance']['julian_day_ut'],swe.MOON,swe.FLG_MOSEPH|swe.FLG_SIDEREAL)[0][0]
            self.assertAlmostEqual(c['d1']['Moon']['longitude'],moon,places=6)

    def test_invalid_coordinates_naive_time_and_dst(self):
        for change in ({'latitude':91.},{'longitude':float('nan')},{'timestamp':'2000-01-01T12:00:00'},
                       {'timezone':'Europe/Madrid'},{'latitude':True}):
            with self.assertRaises(ValueError): compute_vedic_chart({**RAW,**change})

    def test_time_zone_iana_consistent(self):
        c=compute_vedic_chart({**RAW,'timestamp':'2000-01-01T13:00:00+01:00','timezone':'Europe/Madrid'})
        self.assertEqual(c['birth'],BIRTH)

    def test_sensitivity_runs_and_determinism(self):
        r=compute_sensitivity(RAW,minutes=(1,5))
        self.assertEqual(len(r['runs']),7)
        self.assertEqual(compute_vedic_chart(RAW),compute_vedic_chart(RAW))

    def test_pipeline_schema_events_deduplication_and_report(self):
        import jsonschema
        request=json.loads((ROOT/'examples/vedic-request.synthetic.json').read_text())
        request['sensitivity']=False
        r=run_vedic_pipeline(request)
        schema=json.loads((ROOT/'schemas/vedic.schema.json').read_text())
        jsonschema.Draft202012Validator(schema).validate(r)
        self.assertEqual(r['temporal_readiness']['status'],'DESCRIPTIVE_ONLY')
        self.assertGreater(r['temporal_readiness']['vimshottari_subject_results'],0)
        self.assertIn('no está preregistrada',render_vedic_report(r))
        keys=[(x['person'],x['target_longitude'],x['transit'],x['angle']) for x in r['events'][0]['transit_contacts']]
        self.assertEqual(len(keys),len(set(keys)))
        self.assertIn('INSUFFICIENT',render_vedic_report(r))
        bad=copy.deepcopy(r);bad['synastry']['features'][0]['default_weight']=1
        with self.assertRaises(jsonschema.ValidationError): jsonschema.Draft202012Validator(schema).validate(bad)
        with self.assertRaises(ValueError): attach_vedic({},bad)

    def test_report_distinguishes_unrun_temporality_from_zero_events(self):
        import json
        request=json.loads((ROOT/'examples/vedic-request.synthetic.json').read_text())
        request['events']=[]
        request['sensitivity']=False
        result=run_vedic_pipeline(request)
        self.assertEqual(result['temporal_readiness']['status'],'NOT_RUN')
        self.assertEqual(result['temporal_readiness']['events_requested'],0)
        report=render_vedic_report(result)
        self.assertIn('no se suministraron eventos fechados',report)
        self.assertIn('no calculó Vimśottarī de evento ni tránsitos',report)

    def test_event_transits_wrong_instant_rejected(self):
        c=compute_vedic_chart(RAW)
        with self.assertRaises(ValueError): compute_vedic_event_activation(c,c,dict(timestamp='2001-01-01T00:00:00Z'),transit_chart=c)

    def test_annual_without_receipt_rejected(self):
        req=json.loads((ROOT/'examples/vedic-request.synthetic.json').read_text());req['sensitivity']=False
        req['annual_charts']=[dict(chart=RAW,return_verified=False)]
        with self.assertRaises(ValueError): run_vedic_pipeline(req)

    def test_corpus_rejects_duplicate_pairs(self):
        corpus=dict(subjects=[dict(id=str(i),birth={**RAW,'longitude':i},stratum='SYNTHETIC') for i in range(4)],
                    pairs=[['0','1'],['2','3']],cohort_type='SYNTHETIC')
        r=validate_corpus(corpus)
        self.assertEqual(r['external_validation'],'NOT_PERFORMED')
        self.assertEqual(r['control_state'],'COMPLETE')
        self.assertEqual(r,validate_corpus(corpus))
        corpus['pairs'].append(['1','0'])
        with self.assertRaises(ValueError): validate_corpus(corpus)


if __name__=='__main__':
    unittest.main()
