"""Puntos calculados SSAR: datos reproducidos A, interpretación exploratoria E."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from importlib import resources
import json
from typing import Mapping

from .astrology_geometry import match_declared_aspect
from .calculated_points import axis_sample_longitude, mean_apogee, osculating_apogee, vertex_axis
from .ssar import _index, run_ssar, validate_ssar_schema

POINTS = ('VERTEX', 'ANTI_VERTEX', 'BLACK_MOON_MEAN', 'BLACK_MOON_OSCULATING')


def _load(name: str) -> dict:
    return json.loads(resources.files('almas_tfa').joinpath('data', name).read_text(encoding='utf-8'))


def load_calculated_points_catalog() -> dict:
    return _load('ssar-calculated-points-catalog.json')


def load_calculated_points_policy() -> dict:
    policy = _load('ssar-calculated-points-development-policy.json')
    validate_ssar_schema(policy, 'Policy')
    return policy


def _hash(value: Mapping) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    return sha256(encoded.encode('utf-8')).hexdigest()


def _sample(point: str, sample: Mapping, context: Mapping) -> dict:
    out = dict(offset_minutes=sample['offset_minutes'], jd_tt=sample['jd_tt'], status='BLOCKED',
               longitude=None, eccentricity=None, reasons=[])
    if sample['jd_tt'] is None:
        out['reasons'] = ['EPOCH_TT_MISSING']
        return out
    if not context['input_provenance']['source_refs']:
        out['reasons'] = ['INPUT_PROVENANCE_SOURCE_MISSING']
        return out
    try:
        if point in POINTS[:2]:
            if any(sample[key] is None for key in ('armc_deg', 'latitude_deg', 'true_obliquity_deg')):
                out['reasons'] = ['ARMC_LATITUDE_OR_OBLIQUITY_MISSING']
                return out
            axis = vertex_axis(sample['armc_deg'], sample['latitude_deg'], sample['true_obliquity_deg'])
            longitude = axis['vertex' if point == 'VERTEX' else 'anti_vertex']
        elif point == 'BLACK_MOON_MEAN':
            if sample['nutation_longitude_deg'] is None:
                out['reasons'] = ['NUTATION_LONGITUDE_MISSING']
                return out
            longitude = mean_apogee(sample['jd_tt'], sample['nutation_longitude_deg'])
        else:
            state = sample['moon_state']
            provenance = context['input_provenance']
            if state is None or provenance['ephemeris_id'] != 'DE440' or not provenance['ephemeris_sha256']:
                out['reasons'] = ['LUNAR_STATE_OR_DE440_PROVENANCE_MISSING']
                return out
            if abs(state['epoch_jd_tt'] - sample['jd_tt']) > 1e-8:
                raise ValueError('El estado lunar no corresponde a la época TT.')
            result = osculating_apogee(state['position_icrf_km'], state['velocity_icrf_km_s'],
                                       state['rotation_icrf_to_true_ecliptic'], state['mu_km3_s2'])
            longitude = result['longitude']; out['eccentricity'] = result['eccentricity']
        out.update(status='CALCULATED', longitude=longitude)
    except ValueError as exc:
        out['reasons'] = ['GEOMETRY_OR_STATE_UNUSABLE: ' + str(exc)]
    return out


def calculate_point_context(context: Mapping) -> dict:
    validate_ssar_schema(context, 'F6Context')
    if (context['technique'] == 'SYNASTRY') != (context['subject_id'] in {'A', 'B'}):
        raise ValueError('Contexto de carta incompatible con técnica.')
    offsets = [s['offset_minutes'] for s in context['samples']]
    if len(offsets) != len(set(offsets)):
        raise ValueError('Offsets de cálculo duplicados.')
    central = next((s for s in context['samples'] if s['offset_minutes'] == 0), None)
    if len({s['latitude_deg'] for s in context['samples'] if s['latitude_deg'] is not None}) > 1:
        raise ValueError('Una perturbación horaria no cambia la latitud natal.')
    if central and central['jd_tt'] is not None:
        for sample in context['samples']:
            if sample['jd_tt'] is not None and abs(sample['jd_tt'] - central['jd_tt'] - sample['offset_minutes']/1440) > 1e-8:
                raise ValueError('La malla TT no corresponde a sus offsets.')
    catalog = load_calculated_points_catalog()
    entries = _index(catalog['entries'], 'point_id')
    precision = context['time_uncertainty_minutes'] is not None and context['time_uncertainty_minutes'] <= catalog['max_time_uncertainty_minutes']
    points = []
    for point in POINTS:
        samples = [_sample(point, sample, context) for sample in sorted(context['samples'], key=lambda s: s['offset_minutes'])]
        mid = next((s for s in samples if s['offset_minutes'] == 0), None)
        points.append(dict(point_id=point, algorithm_id=entries[point]['algorithm_id'], variant=entries[point]['variant'],
                           status=mid['status'] if mid else 'BLOCKED', central_longitude=mid['longitude'] if mid else None,
                           samples=samples, time_precision_sufficient=bool(precision), location_precision_required=point in POINTS[:2]))
    output = dict(context_id=context['id'], subject_id=context['subject_id'], technique=context['technique'],
                  input_hash=_hash(context), input_provenance=deepcopy(context['input_provenance']), points=points)
    validate_ssar_schema(output, 'F6CalculationResult')
    return output


def build_calculated_points_request(request: Mapping) -> tuple[dict, list[dict]]:
    validate_ssar_schema(request, 'F6Request')
    if not request['enabled']:
        return {'enabled': False}, []
    contexts = _index(request.get('contexts', []), 'id')
    contacts = _index(request.get('contacts', []), 'id')
    calculated = [calculate_point_context(context) for _, context in sorted(contexts.items())]
    results = _index(calculated, 'context_id')
    catalog = load_calculated_points_catalog()
    entries = _index(catalog['entries'], 'point_id')
    seen, appearances, units = set(), [], []
    for contact in sorted(contacts.values(), key=lambda c: c['id']):
        context_id = contact['context_ref']
        if context_id not in contexts:
            raise ValueError('Referencia de contexto rota.')
        key = (context_id, contact['target_id'])
        if key in seen:
            raise ValueError('Un target por contexto requiere un contacto compartido.')
        seen.add(key)
        context = contexts[context_id]
        targets = _index(contact['target_samples'], 'offset_minutes')
        if 0 in targets and targets[0]['target_longitude'] != contact['target_longitude']:
            a, b = targets[0]['target_longitude'], contact['target_longitude']
            if a is None or b is None or (a-b) % 360 != 0:
                raise ValueError('La perturbación central del target no reproduce su posición.')
        for point in results[context_id]['points']:
            id = contact['id'] + ':' + point['point_id']
            entry = entries[point['point_id']]
            central = point['central_longitude']
            axis = point['point_id'] in POINTS[:2]
            # Misma orientación central y continuidad de eje para ambos polos.
            longitude = central % 180 if central is not None and axis else central
            geometry = None if longitude is None or contact['target_longitude'] is None else dict(
                longitude=longitude, target_longitude=contact['target_longitude'], target_id=contact['target_id'], frame='TROPICAL_ECLIPTIC')
            precision = point['time_precision_sufficient'] and (not axis or context['location_precision_sufficient'] is True)
            samples = []
            for sample in point['samples']:
                target = targets.get(sample['offset_minutes'])
                if sample['status'] != 'CALCULATED' or target is None or target['target_longitude'] is None:
                    continue
                value = axis_sample_longitude(sample['longitude'], longitude) if axis and longitude is not None else sample['longitude']
                samples.append(dict(id='P:' + str(sample['offset_minutes']), offset_minutes=sample['offset_minutes'],
                                    longitude=value, target_longitude=target['target_longitude']))
            appearances.append(dict(id=id, point_id=point['point_id'], kind='CALCULATED_POINT',
                geometry=geometry, core_root_refs=deepcopy(contact['core_root_refs']), core_anchor_search_complete=contact['core_anchor_search_complete'],
                robustness=dict(input_precision_sufficient=bool(precision), samples=samples),
                **{key:deepcopy(entry[key]) for key in ('provenance','semantic_basis','method')}))
            units.append(dict(id='U:' + id, appearance_ref=id, technique=point['point_id'],
                equivalence_key='AXIS:' + contact['id'] if axis else 'CONTACT:' + id))
    return dict(enabled=True, sources=deepcopy(catalog['sources']), appearances=appearances,
                core_roots=deepcopy(request.get('core_roots', [])), units=units, edges=deepcopy(request.get('edges', []))), calculated


def run_calculated_points(request: Mapping) -> dict:
    if type(request.get('enabled')) is not bool:
        raise ValueError('Los puntos calculados requieren enabled explícito.')
    output = dict(schema_version='ssar-calculated-points-1.0-development', enabled=request['enabled'],
        catalog_id=None,catalog_hash=None,policy_id=None,policy_status='DEVELOPMENT',ssar=run_ssar({'enabled':False}),
        calculations=[],axis_normalization=[],variant_sensitivity=[],functional_notes=[],completion='NONE',execution_status='not_run',
        coverage=[dict(layer='CALCULATED_POINTS',status='not_run',completion='NONE',reason='DISABLED',assessed_refs=[])],
        external_validation_status='NOT_PERFORMED',structural_scoring_modified=False,ontology_effect='NONE',discriminator_effect='NONE',
        integration_status='AUXILIARY_POST_CORE_NOT_CANONICAL_NOT_M27')
    if not request['enabled']:
        return output
    effective, calculations = build_calculated_points_request(request)
    catalog, policy = load_calculated_points_catalog(), load_calculated_points_policy()
    ssar = run_ssar(effective,policy=policy)
    appearances = _index(ssar['appearances'],'id')
    contexts = _index(calculations,'context_id')
    normalizations, variants, notes = [], [], []
    for contact in sorted(request.get('contacts',[]),key=lambda c:c['id']):
        computed = _index(contexts[contact['context_ref']]['points'],'point_id')
        prefix = contact['id'] + ':'
        vertex = computed['VERTEX']['central_longitude']
        originals = []
        for point in POINTS[:2]:
            lon = computed[point]['central_longitude']
            match = None if lon is None or contact['target_longitude'] is None else match_declared_aspect(
                lon,contact['target_longitude'],policy['type_rules']['CALCULATED_POINT']['aspect_policy'])
            originals.append(dict(appearance_ref=prefix+point,longitude=lon,directed_aspect=match))
        normalizations.append(dict(contact_ref=contact['id'],axis_id=catalog['axis_id'],appearance_refs=[prefix+p for p in POINTS[:2]],
            original_longitudes=originals,canonical_axis_longitude=vertex % 180 if vertex is not None else None,
            contributes_new_evidence=False,equivalence_scope='CONJUNCTION_OPPOSITION_ONLY'))
        pair = [appearances[prefix+p] for p in POINTS[2:]]
        evaluable = all(a['qualification'] != 'BLOCKED' for a in pair)
        contacts = [a['matched_aspect'] is not None for a in pair]
        qualifications = [a['qualification']=='QUALIFIED_SIGNIFICATOR' for a in pair]
        mean, oscu = (computed[p]['central_longitude'] for p in POINTS[2:])
        variants.append(dict(contact_ref=contact['id'],family_id='BLACK_MOON_VARIANTS',mean_appearance_ref=prefix+POINTS[2],osculating_appearance_ref=prefix+POINTS[3],
            separation_deg=abs((mean-oscu+180)%360-180) if mean is not None and oscu is not None else None,
            geometry_concordance=('BOTH_CONTACT' if all(contacts) else 'BOTH_NO_CONTACT' if not any(contacts) else 'DISAGREE') if evaluable else 'NOT_EVALUABLE',
            qualification_concordance=('BOTH_QUALIFIED' if all(qualifications) else 'NEITHER_QUALIFIED' if not any(qualifications) else 'DISAGREE') if evaluable else 'NOT_EVALUABLE',
            selected_variant=None,variant_rule='RETAIN_BOTH_NO_RETROSPECTIVE_SELECTION'))
    entries = _index(catalog['entries'],'point_id')
    for appearance in ssar['appearances']:
        entry = entries[appearance['point_id']]
        notes.append(dict(appearance_ref=appearance['id'],function_id=entry['function_id'],epistemic_class='E_PROJECT_HYPOTHESIS',
            interpretation=entry['interpretation'] if appearance['qualification'] in {'QUALIFIED_SIGNIFICATOR','SECONDARY_SUPPORT'} else None,
            inferential_limit=entry['inferential_limit'],source_refs=appearance['source_refs'],documentary_status='NOT_EVALUABLE'))
    executed = bool(calculations or appearances)
    complete_inputs = bool(calculations) and all({s['offset_minutes'] for s in p['samples']} == {-30,-15,0,15,30}
                                               and all(s['status']=='CALCULATED' for s in p['samples'])
                                               for c in calculations for p in c['points'])
    output.update(catalog_id=catalog['catalog_id'],catalog_hash=_hash(catalog),policy_id=policy['policy_id'],ssar=ssar,
        calculations=calculations,axis_normalization=normalizations,variant_sensitivity=variants,functional_notes=notes,
        completion='PARTIAL' if executed else 'NONE',execution_status='executed' if executed else 'not_run',
        coverage=deepcopy(ssar['coverage'])+[dict(layer='CALCULATED_POINTS',status='executed' if executed else 'not_run',
            completion='COMPLETE' if complete_inputs else 'PARTIAL' if executed else 'NONE',reason='DECLARED_CONTEXTS_ONLY' if executed else 'NO_CONTEXTS_SUPPLIED',
            assessed_refs=[c['context_id'] for c in calculations])])
    validate_ssar_schema(output,'F6Result')
    return output


def validate_calculated_points_result(result: Mapping, *, request: Mapping) -> None:
    validate_ssar_schema(result,'F6Result')
    if result != run_calculated_points(request):
        raise ValueError('La salida no reproduce cálculo, inputs, normalización y política de fase 6.')
