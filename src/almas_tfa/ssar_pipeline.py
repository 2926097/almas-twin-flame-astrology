"""Frozen experimental SSAR envelope, independent of numerical core outputs."""
from __future__ import annotations
from copy import deepcopy
from importlib import resources
from hashlib import sha256
import json
from .ssar import _index, load_ssar_policy, ssar_dependency_groups, validate_ssar_schema, assess_ssar_claim
from .ssar_calculated_points import _hash, build_calculated_points_request, run_calculated_points
from .ssar_s1 import build_s1_request, run_s1
from .ssar_families import build_families_request, run_families
from .ssar_liminal_moirai import build_liminal_request, run_liminal_moirai, _complex
from .ssar_lots import build_lots_request, run_lots
from .ssar_integration import run_integration

PROFILES=dict(s1=(build_s1_request,run_s1),families=(build_families_request,run_families),
 liminal=(build_liminal_request,run_liminal_moirai),calculated_points=(build_calculated_points_request,run_calculated_points),lots=(build_lots_request,run_lots))

GENERAL=dict(COVENANT_COMPLEX=['JUNO'],CONSECRATION_COMPLEX=['VESTA'],PATTERN_RECOGNITION_COMPLEX=['PALLAS'],
 NURTURE_LOSS_RETURN_COMPLEX=['CERES'],WOUND_INITIATION_COMPLEX=['CHIRON'])
THEMES=(('JUNO','VESTA'),('CERES','VESTA'),('CERES','CHIRON'),('JUNO','CHIRON'),('PALLAS','CHIRON'),('PALLAS','VESTA'),('JUNO','CERES'))

def load_frozen_policy():
    root=resources.files('almas_tfa')
    policy=json.loads(root.joinpath('data','ssar-frozen-policy.json').read_text(encoding='utf-8'))
    for name,digest in policy['resource_sha256'].items():
        if sha256(root.joinpath(name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Recurso divergente de la política SSAR congelada: '+name)
    return policy

def _empty_structure():
    policy=load_ssar_policy()
    return dict(appearances=[],dependency_graph=ssar_dependency_groups([],[],policy),complexes=[],dyads=[],pair_themes=[])

def _root_binding(request, canonical_roots):
    if canonical_roots is None:return
    known=_index(canonical_roots,'root_id')
    for root in request.get('core_roots',[]):
        if root['root_id'] not in known:raise ValueError('SSAR no puede crear una raíz fuera de M17.')
        actual=known[root['root_id']]
        if not actual.get('core_eligible',False) and root['core_eligible']:raise ValueError('SSAR no puede elevar una raíz no core.')
        if set(root['core_evidence_ids'])!=set(actual.get('core_evidence_ids',[])):
            raise ValueError('El anclaje SSAR no reproduce la evidencia core M17.')
        if set(root['point_ids'])!=set(actual.get('point_ids',[])):
            raise ValueError('El anclaje SSAR no reproduce los puntos de M17.')

def _documentary_projection(ledger):
    if ledger is None:return None
    fields=('event_id','fact_key','subjects','date','date_range','fact_statement','record_status',
            'documentary_quality_contract_met','fact_interpretation_separated','date_precision_contract_met',
            'date_precision','source_refs','resolved_root_refs')
    return dict(events=[{k:deepcopy(e.get(k)) for k in fields} for e in ledger.get('events',[])])

def run_ssar_pipeline(request, *, canonical_roots=None, m27_ledger=None):
    validate_ssar_schema(request,'F10Request')
    m27_ledger=_documentary_projection(m27_ledger)
    if m27_ledger is not None:validate_ssar_schema(m27_ledger,'F10DocumentaryInput')
    frozen=load_frozen_policy();policy_hash=_hash(frozen)
    structure=_empty_structure();profiles={};coverage=[];combined_policy=load_ssar_policy();combined_policy['policy_id']=frozen['policy_id'];units=[];edges=[];appearances=[];roots={};seen=set()
    ablation=request.get('ablation')
    removed=dict(AB_NO_EROS_PSYCHE={'EROS','PSYCHE'},AB_NO_MOIRAI={'KLOTHO','LACHESIS','ATROPOS','MOIRA'},AB_NO_VERTEX={'VERTEX','ANTI_VERTEX'},AB_NO_BML={'BLACK_MOON_MEAN','BLACK_MOON_OSCULATING'}).get(ablation,set())
    if request['enabled']:
        for name,req in sorted(request.get('profiles',{}).items()):
            if (ablation=='AB_NO_S1' and name=='s1') or (ablation=='AB_NO_LOTS' and name=='lots'):continue
            _root_binding(req,canonical_roots)
            result=PROFILES[name][1](req);profiles[name]=result
            if not req['enabled']:
                coverage.append(dict(layer=name,status='not_run',completion='NONE',reason='DISABLED',assessed_refs=[]));continue
            raw=PROFILES[name][0](req);raw=raw[0] if isinstance(raw,tuple) else raw
            for root in raw.get('core_roots',[]):
                old=roots.setdefault(root['root_id'],root)
                if old!=root:raise ValueError('Definiciones de raíz incompatibles entre perfiles.')
            prefix=name+':'
            excluded={a['id'] for a in result['ssar']['appearances'] if a['point_id'] in removed}
            technique={u['appearance_ref']:u['technique'] for u in raw['units']}
            for a in result['ssar']['appearances']:
                if a['id'] in excluded:continue
                geometric=next(x for x in raw['appearances'] if x['id']==a['id'])['geometry']
                if geometric:
                    signature=(a['point_id'],technique.get(a['id']),geometric['frame'],geometric['target_id'],
                               geometric['longitude']%360,geometric['target_longitude']%360,tuple(a['core_root_refs']))
                    if signature in seen:raise ValueError('Un contacto compartido entre perfiles no puede duplicarse.')
                    seen.add(signature)
                copy=deepcopy(a);copy['id']=prefix+a['id']
                for field in ('evidence_refs','counterevidence_refs'):
                    copy['assessment'][field]=[prefix+r for r in copy['assessment'][field]]
                appearances.append(copy)
            for unit in raw['units']:
                if unit['appearance_ref'] in excluded:continue
                copy=deepcopy(unit);copy['id']=prefix+unit['id'];copy['appearance_ref']=prefix+unit['appearance_ref']
                # The evidence key is intentionally global: explicitly shared equivalence remains shared.
                units.append(copy)
            allowed_units={u['id'] for u in raw['units'] if u['appearance_ref'] not in excluded}
            edges += [dict(e, a=prefix+e['a'],b=prefix+e['b']) for e in raw['edges'] if {e['a'],e['b']}<=allowed_units]
            for technique,group in frozen['technique_groups'].items():combined_policy['technique_groups'][technique]=group
            evaluated=bool(result['ssar']['appearances'])
            coverage.append(dict(layer=name,status='executed' if evaluated else 'not_run',completion='PARTIAL' if evaluated and any(a['qualification']=='BLOCKED' for a in result['ssar']['appearances']) else 'COMPLETE' if evaluated else 'NONE',
                reason='DECLARED_INPUTS_ONLY' if evaluated else 'NO_INPUTS_SUPPLIED',assessed_refs=[prefix+a['id'] for a in result['ssar']['appearances']]))
        edges+=deepcopy(request.get('cross_edges',[]))
        admitted=[u['id'] for u in units if next(a for a in appearances if a['id']==u['appearance_ref'])['qualification'] in ('QUALIFIED_SIGNIFICATOR','SECONDARY_SUPPORT')]
        graph=ssar_dependency_groups(units,edges,combined_policy,admissible_refs=admitted)
        registry=_index(appearances,'id');merged=dict(appearances=appearances,dependency_graph=graph)
        searches=_index(request.get('complex_search',[]),'complex_ref')
        specs=frozen['complexes'];valid={s['id'] for s in specs}|set(frozen['dyad_ids'])
        if set(searches)-valid:raise ValueError('Búsqueda de complejo no registrado.')
        complexes=[]
        for spec in specs:
            refs=sorted(a['id'] for a in appearances if a['point_id'] in spec['members']+spec['context_points'])
            selection=dict(appearance_refs=refs,search_complete=searches.get(spec['id'],{}).get('search_complete',False))
            complexes.append(_complex(selection,spec,registry,merged,dict(complex_rule=dict(minimum_effective_groups=2)),combined_policy))
        # Retain the stricter historical dyad rules. Recompute group count across profiles, never promote an old rejection.
        dyads=[]
        for dyad in profiles.get('families',{}).get('dyads',[]):
            if ablation=='AB_NO_MYTHIC_DYADS' or any('families:'+r not in registry for r in dyad['appearance_refs']):continue
            c=deepcopy(dyad)
            for field in ('appearance_refs','admissible_refs','cross_contact_refs'):c[field]=['families:'+r for r in c[field]]
            group_refs=sorted(g['id'] for g in graph['effective_groups'] if any(u['appearance_ref'] in c['admissible_refs'] and u['id'] in g['unit_refs'] for u in units))
            c['effective_group_refs']=group_refs
            if len(group_refs)<2 and c['qualified_complex']:
                c['qualified_complex']=False;c['blockers'].append('GLOBAL_TWO_EFFECTIVE_GROUPS_NOT_MET')
                c['assessments']['functional_interpretation']=assess_ssar_claim(scope='FUNCTIONAL_INTERPRETATION',policy_ref=frozen['policy_id'],
                   rule_ref='SSAR_F4_BIDIRECTIONAL_CORE_TWO_GROUPS_V1',coverage_sufficient=True,compatible=True,evidence_refs=c['admissible_refs'])
            for assessment in c['assessments'].values():
                assessment['policy_ref']=frozen['policy_id']
                for field in ('evidence_refs','counterevidence_refs'):assessment[field]=['families:'+r for r in assessment[field] if not r.startswith('families:')]+[r for r in assessment[field] if r.startswith('families:')]
            dyads.append(c)
        themes=[dict(id='_'.join(pair)+'_THEME',members=list(pair),appearance_refs=sorted(a['id'] for a in appearances if a['point_id'] in pair),
            epistemic_class='E_PROJECT_HYPOTHESIS',contributes_new_evidence=False) for pair in THEMES]
        structure=dict(appearances=appearances,dependency_graph=graph,complexes=complexes,dyads=dyads,pair_themes=themes)
    integration_request=request.get('integration',dict(windows=[],claims=[],freeze=None)) if request['enabled'] else dict(windows=[],claims=[],freeze=None)
    integration=run_integration(structure,integration_request,policy_hash=policy_hash,m27_ledger=m27_ledger)
    # Completeness describes execution of declared inputs, including fully evaluated negative/empty searches.
    executed=bool(request['enabled'] and (appearances or request.get('complex_search') or integration_request['windows'] or integration_request['claims']))
    partial=bool(any(a['qualification']=='BLOCKED' for a in appearances) or any(not s['search_complete'] for s in request.get('complex_search',[]))
        or any(any(component['coverage']=='MISSING' for component in c['component_coverage']) for c in structure['complexes'] if c['id'] in {s['complex_ref'] for s in request.get('complex_search',[])})
        or any(t['blockers'] for t in integration['temporal']) or any(d['assessment']['status']=='NOT_EVALUABLE' for d in integration['documentary']))
    coverage.append(dict(layer='SSAR',status='executed' if executed else 'not_run',completion='PARTIAL' if partial and executed else 'COMPLETE' if executed else 'NONE',
        reason='DISABLED' if not request['enabled'] else 'DECLARED_INPUTS_ONLY',assessed_refs=[c['id'] for c in structure['complexes'] if c['id'] in {s['complex_ref'] for s in request.get('complex_search',[])}]))
    out=dict(schema_version='ssar-1.25.0',enabled=request['enabled'],policy_id=frozen['policy_id'],evaluation_policy_hash=policy_hash,
        policy_status='FROZEN_EXPERIMENTAL',execution_status='executed' if executed else 'not_run',completion=coverage[-1]['completion'],input_hash=_hash(request),
        evaluation_input=deepcopy(request),documentary_input=deepcopy(m27_ledger),ablation=ablation,profiles=profiles,structure=structure,integration=integration,coverage=coverage,external_validation_status='NOT_PERFORMED',
        primary_integration_metric_status='NOT_OPERATIONALIZED',structural_scoring_modified=False,ontology_effect='NONE',discriminator_effect='NONE',
        history_policy='ARCHIVE_ONLY_NO_AUTOMATIC_REQUALIFICATION')
    validate_ssar_schema(out,'F10Result');return out

def validate_canonical_ssar(result, *, request=None, canonical_roots=None, m27_ledger=None):
    validate_ssar_schema(result,'F10Result')
    if result['evaluation_policy_hash']!=_hash(load_frozen_policy()):raise ValueError('Política SSAR desconocida o alterada.')
    if not result['enabled'] and (result['structure']!=_empty_structure() or result['profiles'] or any(result['integration'][k] for k in ('temporal','documentary','shared_events')) or result['completion']!='NONE'):
        raise ValueError('SSAR desactivado contiene resultados nuevos.')
    a=_index(result['structure']['appearances'],'id');g=_index(result['structure']['dependency_graph']['effective_groups'],'id')
    units=_index(result['structure']['dependency_graph']['units'],'id')
    for unit in units.values():
        if unit['appearance_ref'] not in a:raise ValueError('Unidad canónica sin aparición.')
    for c in result['structure']['complexes']+result['structure']['dyads']:
        if set(c['appearance_refs'])-set(a) or set(c['effective_group_refs'])-set(g):raise ValueError('Referencia canónica de complejo rota.')
        if c['qualified_complex'] and (len(c['effective_group_refs'])<2 or not c['core_root_refs'] or not any(a[r]['qualification']=='QUALIFIED_SIGNIFICATOR' for r in c['admissible_refs'])):
            raise ValueError('Complejo canónico promovido sin anclaje y grupos.')
    reproduction_request=result['evaluation_input'] if request is None else request
    reproduction_ledger=result['documentary_input'] if m27_ledger is None else m27_ledger
    if result!=run_ssar_pipeline(reproduction_request,canonical_roots=canonical_roots,m27_ledger=reproduction_ledger):
        raise ValueError('SSAR canónico no reproduce entradas y política congelada.')

def render_ssar_summary(canonical):
    if 'ssar' not in canonical:return ''
    result=canonical['ssar'];validate_canonical_ssar(result)
    if not result['enabled']:return 'SSAR está desactivado; no se han generado resultados experimentales.'
    paragraphs=['SSAR ofrece hipótesis funcionales experimentales sobre raíces estructurales existentes. La validación externa está pendiente.']
    catalog_names=dict(s1='ssar-s1-catalog.json',families='ssar-families-catalog.json',liminal='ssar-liminal-moirai-catalog.json',
                       calculated_points='ssar-calculated-points-catalog.json',lots='ssar-lots-catalog.json')
    catalogs={name:json.loads(resources.files('almas_tfa').joinpath('data',path).read_text(encoding='utf-8')) for name,path in catalog_names.items()}
    for appearance in result['structure']['appearances']:
        profile=appearance['id'].split(':',1)[0];catalog=catalogs[profile]
        entry=next(e for e in catalog['entries'] if e['point_id']==appearance['point_id'])
        sources=_index(catalog['sources'],'id')
        attributed='; '.join(sources[r]['work']+' ('+sources[r]['epistemic_class']+')' for r in appearance['source_refs'] if r in sources)
        if appearance['qualification'] in ('QUALIFIED_SIGNIFICATOR','SECONDARY_SUPPORT'):
            paragraphs.append(entry['interpretation']+' '+entry['inferential_limit']+' Fuentes por alcance: '+attributed+'.')
        elif appearance['qualification']=='BLOCKED':
            paragraphs.append(appearance['point_id']+': no evaluable por entradas, procedencia, método o cobertura insuficientes. Fuentes: '+attributed+'.')
    if result['profiles'].get('lots',{}).get('variant_sensitivity') or result['profiles'].get('calculated_points',{}).get('variant_sensitivity'):
        paragraphs.append('Las variantes se conservan juntas, incluidas sus discrepancias; ninguna se selecciona por favorecer la lectura.')
    paragraphs.append('Las alternativas incluyen coincidencia geométrica y funciones generales. La dependencia entre técnicas reduce los grupos efectivos y no establece independencia estadística.')
    for c in result['structure']['complexes']+result['structure']['dyads']:
        if not c['appearance_refs']:continue
        paragraphs.append(c['id']+': '+c['assessments']['functional_interpretation']['status']+'. Anclajes: '+(', '.join(c['core_root_refs']) or 'no disponibles')+
            '. Grupos efectivos: '+str(len(c['effective_group_refs']))+'. '+c['inferential_limit'])
    for w in result['integration']['temporal']:
        paragraphs.append('Activación en la ventana '+w['window_ref']+': '+w['assessment']['status']+'. '+('Observación cerrada y suficiente.' if w['window_closed'] else 'La ventana o su observación está incompleta.')+' Carácter: '+w['prediction_class']+'.')
    for d in result['integration']['documentary']:
        paragraphs.append('Correspondencia documental '+d['scope'].lower()+' de '+d['complex_ref']+': '+d['assessment']['status']+'. Hechos: '+(', '.join(d['event_refs']) or 'no disponibles')+'. Exclusiones evaluadas: '+(', '.join(d['assessment']['counterevidence_refs']) or 'ninguna declarada')+'. No establece causalidad.')
    return '\n\n'.join(paragraphs)
