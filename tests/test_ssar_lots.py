import copy
import unittest
from almas_tfa.ssar_lots import POINTS, calculate_lots, calculate_lot_context, run_lots, validate_lots_result

POSITIONS=dict(ASC=350,SUN=10,MOON=40,MERCURY=70,VENUS=120,JUPITER=200,SATURN=290)

def fixture(point='LOT_EROS_PAULUS',sect='DAY'):
    lon=calculate_lots(POSITIONS,sect)[point]['longitude']
    return dict(enabled=True,contexts=[dict(id='CTX',subject_id='A',technique='SYNASTRY',sect=sect,
        sect_source_refs=['synthetic:sect'],input_source_refs=['synthetic:positions'],time_uncertainty_minutes=1,
        location_precision_sufficient=True,samples=[dict(offset_minutes=o,positions=POSITIONS.copy(),sect=sect) for o in (-30,-15,0,15,30)])],
        contacts=[dict(id='C',context_ref='CTX',target_id='SUN',target_longitude=lon+1,
        target_samples=[dict(offset_minutes=o,target_longitude=lon+1) for o in (-30,-15,0,15,30)],
        core_root_refs=['R'],core_anchor_search_complete=True)],
        core_roots=[dict(root_id='R',core_eligible=True,core_evidence_ids=['CORE'],point_ids=['SUN'])],edges=[])

def appearance(out,point):
    return next(a for a in out['ssar']['appearances'] if a['point_id']==point)

class LotsTests(unittest.TestCase):
    def test_historical_arithmetic_both_sects_and_all_variants(self):
        for sect,expected in [('DAY',[20,320,150,300,80,230,290,50]),('NIGHT',[320,20,250,100,320,170,290,50])]:
            self.assertEqual([calculate_lots(POSITIONS,sect)[p]['longitude'] for p in POINTS],expected)
    def test_periodicity_and_missing_dependencies(self):
        self.assertEqual(calculate_lots(POSITIONS,'DAY'),calculate_lots({k:v+360*(i-4) for i,(k,v) in enumerate(POSITIONS.items())},'DAY'))
        p=POSITIONS.copy();p['SATURN']=None
        r=calculate_lots(p,'DAY');self.assertEqual(r['LOT_NEMESIS']['missing_inputs'],['SATURN'])
        self.assertEqual(r['LOT_EROS_PAULUS']['status'],'CALCULATED')
    def test_nonfinite_and_unknown_sect_rejected_by_pure_calculator(self):
        for sect in (None,'UNKNOWN'):
            with self.assertRaises(ValueError):calculate_lots(POSITIONS,sect)
        p=POSITIONS.copy();p['ASC']=float('nan')
        with self.assertRaises(ValueError):calculate_lots(p,'DAY')
    def test_positive_and_negative_each_variant_both_sects(self):
        for sect in ('DAY','NIGHT'):
            for point in POINTS:
                request=fixture(point,sect);out=run_lots(request)
                self.assertEqual(appearance(out,point)['qualification'],'QUALIFIED_SIGNIFICATOR')
                validate_lots_result(out,request=request)
                request['contacts'][0]['target_longitude']+=50
                for s in request['contacts'][0]['target_samples']:s['target_longitude']+=50
                self.assertEqual(appearance(run_lots(request),point)['qualification'],'NO_CONTACT')
    def test_unknown_sect_retains_day_night_and_blocks_even_invariant_valens(self):
        r=fixture();r['contexts'][0]['sect']=None
        out=run_lots(r)
        self.assertTrue(all(a['qualification']=='BLOCKED' for a in out['ssar']['appearances']))
        self.assertEqual(len(out['calculations'][0]['points'][0]['samples'][0]['variants']),2)
        self.assertEqual(len(out['variant_sensitivity']),2)
    def test_time_location_sources_horizon_flip_and_missing_sample(self):
        for field,value in [('time_uncertainty_minutes',None),('time_uncertainty_minutes',31),('location_precision_sufficient',False),('input_source_refs',[]),('sect_source_refs',[])]:
            r=fixture();r['contexts'][0][field]=value
            self.assertEqual(appearance(run_lots(r),'LOT_EROS_PAULUS')['qualification'],'BLOCKED')
        r=fixture();r['contexts'][0]['samples'][0]['sect']='NIGHT'
        self.assertFalse(calculate_lot_context(r['contexts'][0])['sect_stable'])
        self.assertEqual(appearance(run_lots(r),'LOT_EROS_PAULUS')['qualification'],'BLOCKED')
        r=fixture();r['contexts'][0]['samples'].pop()
        self.assertEqual(appearance(run_lots(r),'LOT_EROS_PAULUS')['qualification'],'BLOCKED')
    def test_variants_not_selected_and_shared_group_not_equivalence(self):
        out=run_lots(fixture())
        self.assertEqual(out['variant_sensitivity'][0]['separation_deg'],140)
        self.assertTrue(all(v['selected_variant'] is None for v in out['variant_sensitivity']))
        graph=out['ssar']['dependency_graph']
        self.assertEqual(len(graph['effective_groups']),1)
        self.assertEqual(len(graph['equivalence_classes']),8)
        self.assertFalse(graph['statistical_independence_established'])
    def test_absence_of_core_and_disabled_empty_distinctions(self):
        r=fixture();r['contacts'][0]['core_root_refs']=[]
        self.assertEqual(appearance(run_lots(r),'LOT_EROS_PAULUS')['qualification'],'SECONDARY_SUPPORT')
        disabled=run_lots(dict(enabled=False));empty=run_lots(dict(enabled=True))
        self.assertIsNone(disabled['catalog_hash']);self.assertIsNotNone(empty['catalog_hash'])
        self.assertEqual(disabled['execution_status'],'not_run')
    def test_duplicate_and_broken_context_and_forged_result(self):
        for action in ('duplicate','broken','central'):
            r=fixture()
            if action=='duplicate':r['contexts'][0]['samples'].append(copy.deepcopy(r['contexts'][0]['samples'][0]))
            elif action=='broken':r['contacts'][0]['context_ref']='BAD'
            else:r['contacts'][0]['target_samples'][2]['target_longitude']+=1
            with self.assertRaises(ValueError):run_lots(r)
        r=fixture();out=run_lots(r);out['calculations'][0]['points'][0]['central_longitude']=123
        with self.assertRaises(ValueError):validate_lots_result(out,request=r)
