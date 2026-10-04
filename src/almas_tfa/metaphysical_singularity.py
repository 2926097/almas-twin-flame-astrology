"""PU-M: atribución doctrinal y especificidad relativa, sin promoción ontológica."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
from importlib.resources import files
import json
import math
from typing import Any, Mapping

STATES = {'SUPPORTED', 'COMPATIBLE', 'INSUFFICIENT', 'CONTRADICTED', 'NOT_EVALUABLE'}

def _load(name):
    return json.loads(files('almas_tfa').joinpath('data', name).read_text(encoding='utf-8'))

def load_metaphysical_singularity_policy():
    return _load('metaphysical-singularity-policy.json')

def _hash(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def _unit(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f'{name}: se requiere número finito en [0,1].')
    return float(value)

def _canonical(case):
    c = case.get('canonical')
    if not isinstance(c, Mapping):
        raise ValueError('Cada díada requiere canonical.')
    if case.get('canonical_fingerprint') != _hash(c):
        raise ValueError('CANONICAL_FINGERPRINT_MISMATCH')
    if not isinstance(c.get('evidence'), list) or not isinstance(c.get('semantic_motifs'), Mapping):
        raise ValueError('Faltan evidencia canónica o motivos.')
    if c['semantic_motifs'].get('policy_id') != 'ALMAS_SEMANTIC_MOTIF_V2':
        raise ValueError('Política de motivos incompatible.')
    protocol = case.get('protocol')
    required = ('analysis_policy_fingerprint', 'house_system', 'time_quality', 'signature_policy')
    if not isinstance(protocol, Mapping) or any(not protocol.get(k) for k in required):
        raise ValueError('Falta declaración de protocolo comparable.')
    if protocol['signature_policy'] != 'CORE_PRIMARY_MOTIF_MAX_V1':
        raise ValueError('Política de firma desconocida.')
    ids = case.get('subject_ids')
    if not isinstance(ids, list) or len(ids) != 2 or len(set(ids)) != 2 or any(not isinstance(i, str) or not i for i in ids):
        raise ValueError('Se requieren dos subject_ids distintos.')
    natal_context = c.get('natal_context', {})
    if not isinstance(natal_context, Mapping):
        raise ValueError('natal_context debe ser objeto.')
    ctx = natal_context.get('subjects', {})
    if not isinstance(ctx, Mapping):
        raise ValueError('natal_context.subjects debe ser objeto.')
    if set(ctx) != set(ids):
        raise ValueError('Identidades incompatibles con natal_context.')
    return c

def build_singularity_signature(case):
    """Extrae máximos por motivo de raíces core ya calculadas, sin nueva astronomía."""
    c = _canonical(case)
    features = load_metaphysical_singularity_policy()['feature_ids']
    evidence = {}
    for row in c['evidence']:
        if not isinstance(row, Mapping):
            raise ValueError('Cada fila de evidence debe ser objeto.')
        rid = row.get('root_id')
        if not isinstance(rid, str) or rid in evidence:
            raise ValueError('Identidad de raíz ausente o duplicada.')
        evidence[rid] = row
    values = {f: 0.0 for f in features}
    refs = {f: [] for f in features}
    seen = set()
    assignments = c['semantic_motifs'].get('assignments', [])
    if not isinstance(assignments, list):
        raise ValueError('semantic_motifs.assignments debe ser una lista.')
    for row in assignments:
        if not isinstance(row, Mapping):
            raise ValueError('Cada asignación de motivos debe ser objeto.')
        rid, motif = row.get('root_id'), row.get('primary_motif')
        if rid in seen or rid not in evidence:
            raise ValueError('Asignación duplicada o raíz sin resolver.')
        seen.add(rid)
        if motif is None:
            continue
        if motif not in values:
            raise ValueError('Motivo primario desconocido.')
        root = evidence[rid]
        if root.get('core_eligible') is not True:
            continue
        strength = _unit(root.get('strength'), 'root.strength')
        if not root.get('dependency_families'):
            raise ValueError('Raíz core sin familia de dependencia.')
        values[motif] = max(values[motif], strength)
        refs[motif].append(rid)
    # Una ausencia vale cero sólo dentro de un inventario core declarado completo.
    assembly = c.get('assembly', {})
    if not isinstance(assembly, Mapping) or assembly.get('policy_id') != 'ALMAS_CANONICAL_ASSEMBLY_V2':
        raise ValueError('Se requiere ensamblaje canónico completo V2.')
    if seen != set(evidence):
        raise ValueError('Inventario de asignaciones incompleto.')
    return {'policy_id': 'CORE_PRIMARY_MOTIF_MAX_V1', 'features': values,
            'root_refs': refs, 'canonical_fingerprint': case['canonical_fingerprint'],
            'feature_group': 'DERIVED_CORE_GRAPH', 'independent_votes': False}

def _doctrine(request):
    registry = _load('metaphysical-singularity-values.json')
    sources = {s['id']: s for s in _load('metaphysical-singularity-source-map.json')['sources']}
    refs = sorted(set(request.get('source_refs', [])))
    if any(s not in sources for s in refs):
        raise ValueError('Fuente PU-M desconocida.')
    models = request.get('model_ids', ['TWIN_FLAME_MODEL', 'SOULMATE_MODEL'])
    allowed = {'TWIN_FLAME_MODEL', 'SOULMATE_MODEL', 'SOUL_FAMILY_GROUP', 'MONADIC_COMMON_SOURCE', 'SPLIT_SOUL', 'ZIVUG'}
    if not models or any(m not in allowed for m in models) or len(set(models)) != len(models):
        raise ValueError('Modelo doctrinal desconocido o repetido.')
    observations = request.get('value_observations', [])
    value_ids = {v['id'] for v in registry['values']}
    index = {}
    for obs in observations:
        key = (obs.get('value_id'), obs.get('model_id'))
        if key[0] not in value_ids or key[1] not in models or key in index:
            raise ValueError('Observación desconocida o duplicada.')
        if obs.get('status') not in STATES or obs.get('epistemic_class') not in {'A_DOCUMENTARY','D_CONTEMPORARY_USAGE','E_PROJECT_HYPOTHESIS'}:
            raise ValueError('Estado o clase de observación inválida.')
        if not obs.get('evidence_refs') or not obs.get('dependency_group'):
            raise ValueError('Observación sin procedencia o dependencia.')
        if obs['status'] == 'SUPPORTED' and obs['epistemic_class'] != 'A_DOCUMENTARY':
            raise ValueError('Un relato o hipótesis no soporta correspondencia documental.')
        index[key] = obs
    rows = []
    for value in registry['values']:
        for model in models:
            matched = [(s, cl) for sid in refs for s in [sources[sid]] for cl in s['claims']
                       if cl['value_id'] == value['id'] and cl['model_id'] == model]
            reqs = {cl['requirement'] for s, cl in matched}
            requirement = next(iter(reqs)) if len(reqs) == 1 else 'UNRESOLVED'
            observation = index.get((value['id'], model))
            # Respaldo doctrinal y correspondencia no son identidad de origen.
            rows.append({'value_id': value['id'], 'model_id': model,
                         'doctrine_state': 'SUPPORTED' if len(reqs) == 1 else ('INSUFFICIENT' if reqs else 'NOT_EVALUABLE'),
                         'requirement': requirement, 'source_refs': sorted({s['id'] for s, cl in matched}),
                         'dependency_groups': sorted({s['dependency_group'] for s, cl in matched}),
                         'case_correspondence': deepcopy(observation) if observation else {'status':'NOT_EVALUABLE'},
                         'scope':'DOCTRINAL_ATTRIBUTION_AND_DECLARED_CORRESPONDENCE', 'origin_effect':'NONE'})
    return {'rows':rows, 'citation_count_adds_weight':False, 'score':None}

def _distance(signature, template, weights):
    return sum(weights[f] * abs(signature[f] - template[f]) for f in template) / sum(weights.values())

def _relative(request):
    target = request.get('target')
    comparators = request.get('comparators', [])
    if not target:
        return {'state':'NOT_EVALUABLE', 'reason':'MISSING_TARGET', 'score':None}
    signature = build_singularity_signature(target)
    if not comparators:
        return {'state':'NOT_EVALUABLE', 'reason':'MISSING_REAL_COMPARATORS', 'target_signature':signature, 'score':None}
    policy = request.get('comparison_policy')
    if not isinstance(policy, Mapping):
        raise ValueError('Falta comparison_policy explícita.')
    features = set(signature['features'])
    template, weights = policy.get('template'), policy.get('weights')
    if not isinstance(template, Mapping) or not isinstance(weights, Mapping) or set(template) != features or set(weights) != features:
        raise ValueError('Firma y pesos deben cubrir exactamente los nueve motivos.')
    template = {f:_unit(v,'template') for f,v in template.items()}
    for w in weights.values():
        if isinstance(w,bool) or not isinstance(w,(int,float)) or not math.isfinite(w) or w <= 0:
            raise ValueError('Pesos finitos positivos requeridos.')
    margin = _unit(policy.get('equivalence_margin'), 'equivalence_margin')
    if margin == 0:
        raise ValueError('El margen debe ser positivo.')
    min_irc = _unit(policy.get('minimum_irc'), 'minimum_irc') * 100
    if not isinstance(policy.get('selection_record_ref'), str) or not policy['selection_record_ref']:
        raise ValueError('Falta registro de selección de comparadores.')
    c = _canonical(target)
    target_distance = _distance(signature['features'],template,weights)
    target_pair = frozenset(target['subject_ids'])
    pairs = {target_pair}; rows=[]; coverage=set(); quality=[]
    cases = [target]
    for comp in comparators:
        cc = _canonical(comp)
        pair = frozenset(comp['subject_ids'])
        if pair in pairs:
            raise ValueError('Díada repetida o idéntica al objetivo.')
        pairs.add(pair)
        shared = target_pair.intersection(pair)
        if len(shared) != 1:
            raise ValueError('Cada comparador debe compartir exactamente un sujeto objetivo.')
        coverage.update(shared)
        if comp['protocol'] != target['protocol'] or cc.get('astronomy_backend') != c.get('astronomy_backend'):
            raise ValueError('Protocolo o backend de comparador incompatible.')
        sig = build_singularity_signature(comp)
        distance = _distance(sig['features'],template,weights)
        rows.append({'canonical_fingerprint':comp['canonical_fingerprint'], 'subject_ids':comp['subject_ids'],
                     'shared_subject':next(iter(shared)), 'distance':distance, 'margin_to_target':distance-target_distance})
        cases.append(comp)
    for case in cases:
        cc=case['canonical']; irc=cc.get('indices',{}).get('IRC'); icc=cc.get('indices',{}).get('ICC')
        for v in (irc,icc):
            if v is None:
                quality.append('MISSING_QUALITY'); continue
            _unit(v/100 if not isinstance(v,bool) else v,'quality')
        if irc is not None and irc < min_irc: quality.append('LOW_ROBUSTNESS')
        if icc is not None and icc != c.get('indices',{}).get('ICC'): quality.append('COVERAGE_MISMATCH')
    pre=request.get('preregistration',{})
    comparison_hash=_hash({'policy':dict(policy),'pairs':sorted([sorted(p) for p in pairs])})
    pre_valid=pre.get('status')=='DECLARED_FROZEN' and pre.get('comparison_fingerprint')==comparison_hash and bool(pre.get('record_ref'))
    blockers=sorted(set(quality + ([] if coverage==set(target_pair) else ['ONE_SIDED_NETWORK']) + ([] if pre_valid else ['NO_MATCHING_PREREGISTRATION'])))
    worst_margin=min(row['margin_to_target'] for row in rows)
    state='NOT_EVALUABLE' if quality else 'INSUFFICIENT' if blockers else ('CONTRADICTED' if worst_margin <= margin else 'COMPATIBLE')
    return {'state':state,'scope':'RELATIVE_SPECIFICITY_IN_DECLARED_NETWORK','target_distance':target_distance,
            'minimum_margin':worst_margin,'equivalence_margin':margin,'comparators':rows,'blockers':blockers,
            'comparison_fingerprint':comparison_hash,'preregistration_authenticated':False,
            'minimum_irc':min_irc,'target_signature':signature,'score':None,
            'external_validation':'NOT_PERFORMED','origin_effect':'NONE'}

def assess_metaphysical_singularity(request):
    """Evalúa PU-M lateral. No muta entrada ni calcula PU heredado o IEM."""
    if not isinstance(request, Mapping): raise ValueError('request debe ser objeto.')
    from jsonschema import Draft202012Validator
    schema = _load('metaphysical-singularity-request.schema.json')
    errors = sorted(Draft202012Validator(schema).iter_errors(request), key=lambda e: str(list(e.path)))
    if errors: raise ValueError('REQUEST_SCHEMA: ' + errors[0].message)
    before=_hash(request)
    result={'schema_version':'1.0.0','extension_id':'ALMAS_PU_METAPHYSICAL_V1',
            'status':'FROZEN_EXPERIMENTAL','PU_D':_doctrine(request),'PU_R':_relative(request),
            'PU_O':{'state':'NOT_EVALUABLE','reason':'NO_INDEPENDENT_ORIGIN_CRITERION','score':None},
            'pu_score':None,'pu_score_state':'NOT_OPERATIONALIZED',
            'ontology_effect':'NONE','production_scores_affected':False,
            'request_fingerprint':before,'validation_status':'NOT_PERFORMED'}
    if _hash(request)!=before: raise RuntimeError('Entrada mutada.')
    from jsonschema import Draft202012Validator
    Draft202012Validator(_load('metaphysical-singularity.schema.json')).validate(result)
    return result

def render_metaphysical_singularity_summary(result):
    if result.get('extension_id')!='ALMAS_PU_METAPHYSICAL_V1' or result.get('pu_score') is not None or result.get('ontology_effect')!='NONE':
        raise ValueError('Resultado fuera del contrato PU-M.')
    return ('PU-M: singularidad relativa '+result['PU_R']['state']+'. '
            'Origen único '+result['PU_O']['state']+'. '
            'Índice numérico no operacionalizado; validación externa no realizada.')
