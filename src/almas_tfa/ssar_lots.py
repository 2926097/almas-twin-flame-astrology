"""Six historical lot families; all declared formula variants remain visible."""
from __future__ import annotations
from copy import deepcopy
from math import fsum
from typing import Mapping
from .ssar import _index, run_ssar, validate_ssar_schema
from .ssar_calculated_points import _hash, _load

POINTS = ('LOT_FORTUNE','LOT_SPIRIT','LOT_EROS_PAULUS','LOT_NECESSITY_PAULUS',
          'LOT_NEMESIS','LOT_VICTORY','LOT_EROS_VALENS','LOT_NECESSITY_VALENS')

def load_lots_catalog():
    return _load('ssar-lots-catalog.json')

def load_lots_policy():
    return _load('ssar-lots-development-policy.json')

def calculate_lots(positions: Mapping, sect: str) -> dict:
    validate_ssar_schema(positions, 'F7Positions')
    if sect not in ('DAY','NIGHT'):
        raise ValueError('El cálculo de una variante exige secta explícita.')
    entries = _index(load_lots_catalog()['entries'], 'point_id')
    calculated = {}
    def value(key):
        if key in entries:
            return compute(key)
        v = positions.get(key)
        return dict(longitude=None if v is None else v % 360, missing_inputs=[key] if v is None else [])
    def compute(point):
        if point in calculated:
            return calculated[point]
        formula = entries[point]['formulas'][sect]
        parts = [value(formula[k]) for k in ('base','add','subtract')]
        missing = sorted({k for v in parts for k in v['missing_inputs']})
        longitude = None if missing else fsum((parts[0]['longitude'],parts[1]['longitude'],-parts[2]['longitude'])) % 360
        calculated[point] = dict(status='BLOCKED' if missing else 'CALCULATED',longitude=longitude,missing_inputs=missing)
        return calculated[point]
    return {p:deepcopy(compute(p)) for p in POINTS}

def calculate_lot_context(context: Mapping) -> dict:
    validate_ssar_schema(context, 'F7Context')
    if (context['technique']=='SYNASTRY') != (context['subject_id'] in ('A','B')):
        raise ValueError('Contexto de carta incompatible con técnica.')
    samples = _index(context['samples'],'offset_minutes')
    sect = context['sect']
    stable = sect in ('DAY','NIGHT') and bool(samples) and all(s['sect']==sect for s in samples.values())
    precision = (context['time_uncertainty_minutes'] is not None and context['time_uncertainty_minutes'] <= 30
                 and context['location_precision_sufficient'] is True and bool(context['input_source_refs'])
                 and bool(context['sect_source_refs']) and stable)
    computed = {o:{s:calculate_lots(sample['positions'],s) for s in ('DAY','NIGHT')} for o,sample in samples.items()}
    points=[]
    for entry in load_lots_catalog()['entries']:
        records=[]
        for offset in sorted(samples):
            variants=[dict(sect=s,**computed[offset][s][entry['point_id']]) for s in ('DAY','NIGHT')]
            selected = next((v for v in variants if v['sect']==sect),None)
            records.append(dict(offset_minutes=offset,variants=variants,longitude=selected['longitude'] if selected else None))
        central=next((r['longitude'] for r in records if r['offset_minutes']==0),None)
        points.append(dict(point_id=entry['point_id'],function_id=entry['function_id'],formula_variant=entry['variant'],
                           central_longitude=central,status='CALCULATED' if central is not None else 'BLOCKED',samples=records))
    output=dict(context_id=context['id'],subject_id=context['subject_id'],technique=context['technique'],input_hash=_hash(context),
                sect=sect,sect_stable=stable,precision_sufficient=bool(precision),
                source_refs=sorted(set(context['input_source_refs']+context['sect_source_refs'])),points=points)
    validate_ssar_schema(output,'F7Calculation')
    return output

def build_lots_request(request: Mapping) -> tuple[dict,list[dict]]:
    validate_ssar_schema(request,'F7Request')
    if not request['enabled']:
        return {'enabled':False},[]
    contexts=_index(request.get('contexts',[]),'id')
    contacts=_index(request.get('contacts',[]),'id')
    calculations=[calculate_lot_context(c) for _,c in sorted(contexts.items())]
    outputs=_index(calculations,'context_id');entries=_index(load_lots_catalog()['entries'],'point_id')
    appearances=[];units=[];seen=set()
    for contact in sorted(contacts.values(),key=lambda c:c['id']):
        ref=contact['context_ref']
        if ref not in contexts:
            raise ValueError('Referencia de contexto rota.')
        key=(ref,contact['target_id'])
        if key in seen:
            raise ValueError('Un target por contexto requiere un contacto compartido.')
        seen.add(key)
        targets=_index(contact['target_samples'],'offset_minutes')
        if 0 in targets:
            a,b=targets[0]['target_longitude'],contact['target_longitude']
            if a!=b and (a is None or b is None or (a-b)%360!=0):
                raise ValueError('La perturbación central del target no reproduce su posición.')
        for point in outputs[ref]['points']:
            entry=entries[point['point_id']];id=contact['id']+':'+point['point_id'];lon=point['central_longitude']
            geometry=None if lon is None or contact['target_longitude'] is None else dict(longitude=lon,
                target_longitude=contact['target_longitude'],target_id=contact['target_id'],frame='TROPICAL_ECLIPTIC')
            provenance=deepcopy(entry['provenance']);provenance['sect']=contexts[ref]['sect']
            samples=[dict(id='P:'+str(s['offset_minutes']),offset_minutes=s['offset_minutes'],longitude=s['longitude'],
                          target_longitude=targets[s['offset_minutes']]['target_longitude'])
                     for s in point['samples'] if s['longitude'] is not None and s['offset_minutes'] in targets
                     and targets[s['offset_minutes']]['target_longitude'] is not None]
            appearances.append(dict(id=id,point_id=point['point_id'],kind='HELLENISTIC_LOT',geometry=geometry,
                core_root_refs=deepcopy(contact['core_root_refs']),core_anchor_search_complete=contact['core_anchor_search_complete'],
                robustness=dict(input_precision_sufficient=outputs[ref]['precision_sufficient'],samples=samples),provenance=provenance,
                semantic_basis=deepcopy(entry['semantic_basis']),method=deepcopy(entry['method'])))
            units.append(dict(id='U:'+id,appearance_ref=id,technique=point['point_id'],equivalence_key='CONTACT:'+id))
    return dict(enabled=True,sources=deepcopy(load_lots_catalog()['sources']),appearances=appearances,
        core_roots=deepcopy(request.get('core_roots',[])),units=units,edges=deepcopy(request.get('edges',[]))),calculations

def run_lots(request: Mapping) -> dict:
    validate_ssar_schema(request,'F7Request')
    output=dict(schema_version='ssar-lots-1.0-development',enabled=request['enabled'],catalog_id=None,catalog_hash=None,
        ssar=run_ssar({'enabled':False}),calculations=[],variant_sensitivity=[],functional_notes=[],execution_status='not_run',
        completion='NONE',coverage=[dict(layer='HELLENISTIC_LOTS',status='not_run',completion='NONE',reason='DISABLED',assessed_refs=[])],
        external_validation_status='NOT_PERFORMED',structural_scoring_modified=False,ontology_effect='NONE',discriminator_effect='NONE')
    if not request['enabled']:
        return output
    effective,calculations=build_lots_request(request);catalog=load_lots_catalog()
    ssar=run_ssar(effective,policy=load_lots_policy());entries=_index(catalog['entries'],'point_id')
    computed=_index(calculations,'context_id');variants=[]
    for contact in sorted(request.get('contacts',[]),key=lambda c:c['id']):
        points=_index(computed[contact['context_ref']]['points'],'point_id')
        for family in ('EROS','NECESSITY'):
            pair=['LOT_'+family+'_'+v for v in ('PAULUS','VALENS')]
            a,b=[points[p]['central_longitude'] for p in pair]
            variants.append(dict(contact_ref=contact['id'],pair_id=family,appearance_refs=[contact['id']+':'+p for p in pair],
                separation_deg=None if a is None or b is None else abs((a-b+180)%360-180),selected_variant=None,
                rule='RETAIN_BOTH_NO_RETROSPECTIVE_SELECTION'))
    notes=[dict(appearance_ref=a['id'],function_id=entries[a['point_id']]['function_id'],epistemic_class='E_PROJECT_HYPOTHESIS',
        interpretation=entries[a['point_id']]['interpretation'] if a['qualification'] in ('QUALIFIED_SIGNIFICATOR','SECONDARY_SUPPORT') else None,
        inferential_limit=entries[a['point_id']]['inferential_limit'],source_refs=a['source_refs']) for a in ssar['appearances']]
    executed=bool(calculations or ssar['appearances'])
    complete=bool(calculations) and all(c['precision_sufficient'] and all({s['offset_minutes'] for s in p['samples']}=={-30,-15,0,15,30}
        and p['status']=='CALCULATED' and all(s['longitude'] is not None for s in p['samples']) for p in c['points']) for c in calculations)
    output.update(catalog_id=catalog['catalog_id'],catalog_hash=_hash(catalog),ssar=ssar,calculations=calculations,
        variant_sensitivity=variants,functional_notes=notes,execution_status='executed' if executed else 'not_run',
        completion='PARTIAL' if executed else 'NONE',coverage=deepcopy(ssar['coverage'])+[dict(layer='HELLENISTIC_LOTS',
        status='executed' if executed else 'not_run',completion='COMPLETE' if complete else 'PARTIAL' if executed else 'NONE',
        reason='ALL_VARIANTS_RETAINED' if executed else 'NO_CONTEXTS_SUPPLIED',assessed_refs=[c['context_id'] for c in calculations])])
    validate_ssar_schema(output,'F7Result')
    return output

def validate_lots_result(result: Mapping, *, request: Mapping) -> None:
    validate_ssar_schema(result,'F7Result')
    if result != run_lots(request):
        raise ValueError('La salida no reproduce fórmulas, variantes, secta e inputs de fase 7.')
