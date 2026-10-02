"""RRA: arquitectura previa → retorno calculado → activación temporal experimental."""
from __future__ import annotations
from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
from importlib import resources
import json
from .astrology_backend import AstronomyBackendNotEvaluableError
from .return_solver import ReturnPositionProvider, build_return_chart, find_all_return_passes, finite, instant, resolve_return_location

POLICY_NAMES = ('activation','eligibility','orb','location','event-window','dependency','null-model')
ANGULAR_POINTS = {'ASC','DSC','MC','IC','VERTEX','ANTI_VERTEX'}


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def load_return_policy():
    root = resources.files('almas_tfa').joinpath('data')
    manifest=json.loads(root.joinpath('return-frozen-manifest.json').read_text(encoding='utf-8'))
    for filename,expected in manifest['resources'].items():
        if sha256(root.joinpath(filename).read_bytes()).hexdigest()!=expected:
            raise ValueError('Recurso RRA divergente de la política congelada: '+filename)
    return {name:json.loads(root.joinpath('return-'+name+'-policy.json').read_text(encoding='utf-8')) for name in POLICY_NAMES}


def validate_contract(value, definition):
    from jsonschema import Draft202012Validator
    from .ssar import _finite_tree
    _finite_tree(value)
    schema=json.loads(resources.files('almas_tfa').joinpath('data','return-contract-definitions.json').read_text(encoding='utf-8'))
    schema['$ref']='#/$defs/'+definition
    Draft202012Validator(schema).validate(value)


def _index(items, key):
    result={item[key]:item for item in items}
    if len(result)!=len(items):raise ValueError('Identificadores RRA duplicados: '+key)
    return result


def _groups(roots, edges):
    parent={key:key for key in roots}
    def find(key):
        while parent[key]!=key:
            parent[key]=parent[parent[key]];key=parent[key]
        return key
    def join(a,b):
        if a not in roots or b not in roots:raise ValueError('Dependencia apunta a raíz inexistente.')
        ra,rb=find(a),find(b)
        parent[max(ra,rb)]=min(ra,rb)
    # Raíces con un grupo heredado común no se proclaman independientes.
    inherited={}
    for key,root in roots.items():
        group=root.get('dependency_cluster')
        if group:
            if group in inherited:join(key,inherited[group])
            inherited[group]=key
    unknown=[key for key,root in roots.items() if not root.get('dependency_cluster')]
    for key in unknown[1:]:join(unknown[0],key)
    for edge in edges:join(edge['a'],edge['b'])
    return {key:find(key) for key in roots}


def _validate_inputs(request, roots, ssar):
    validate_contract(request,'Request')
    root_index=_index(roots,'root_id');charts=_index(request.get('charts',[]),'id');_index(request.get('clocks',[]),'id')
    _index(request.get('events',[]),'event_id')
    for event in request.get('events',[]):
        if event.get('event_datetime'):instant(event['event_datetime'],event.get('timezone'))
    groups=_groups(root_index,request.get('dependencies',[]))
    appearances=_index((ssar or {}).get('appearances',[]),'id')
    for chart in charts.values():
        _index(chart['points'],'point_id')
        for point in chart['points']:
            finite(point['longitude'],'overlay longitude')
            for ref in point['core_root_refs']:
                if ref not in root_index or not root_index[ref].get('core_eligible',False):
                    raise ValueError('RRA requiere una raíz core preexistente y elegible.')
                ids=set(root_index[ref].get('point_ids',[]))
                parents=set(point.get('parent_point_ids',[]))
                if chart['layer'] in {'NATAL','SYNASTRY'}:
                    if point['point_id'] not in ids:raise ValueError('Punto natal ajeno a la raíz referenciada.')
                elif chart['layer']=='SSAR':
                    a=appearances.get(point.get('significator_ref'))
                    if not a or a['qualification']!='QUALIFIED_SIGNIFICATOR' or a['point_id']!=point['point_id'] or ref not in a['core_root_refs']:
                        raise ValueError('Overlay SSAR no está previamente cualificado.')
                elif not parents or not parents<=ids or not point.get('derivation_method'):
                    raise ValueError('Overlay derivado requiere método y padres de la raíz.')
    for clock in request.get('clocks',[]):
        if clock['reference_chart'] not in charts:raise ValueError('Carta de referencia desconocida.')
        points=_index(charts[clock['reference_chart']]['points'],'point_id')
        if clock['reference_point'] not in points:raise ValueError('Punto de referencia desconocido.')
        if clock['reference_point']!=clock['returning_body']:
            raise ValueError('Un retorno longitudinal requiere cuerpo homólogo; una recurrencia de otro punto es otra técnica.')
        start,end=instant(clock['start']),instant(clock['end'])
        if end<=start:raise ValueError('Ventana de búsqueda invertida.')
        if not clock['locations']:raise ValueError('Declarar ubicación o variante unknown.')
        _index(clock['locations'],'id')
        for location in clock['locations']:resolve_return_location(location)
        if clock['angular_reliability'] and (clock['birth_time_quality'] in {'UNKNOWN','APPROXIMATE'} or clock.get('reference_uncertainty_degrees') is None):
            raise ValueError('Ángulos fiables requieren precisión natal explícita y incertidumbre acotada.')
    return root_index,charts,appearances,groups


def _eligible(clock, points, appearances, policy):
    body=clock['returning_body']
    if body in policy['eligibility']['ordinary_bodies']:return True
    a=appearances.get(clock.get('significator_ref'))
    return bool(a and a['qualification']=='QUALIFIED_SIGNIFICATOR' and a['point_id']==body and a['source_refs']
                and a['core_root_refs'] and set(a['core_root_refs'])<=set(points['core_root_refs']))


def calculate_return_overlays(record, charts, groups, policy, *, orb_multiplier=1.0, exclude_layers=(), exclude_angles=False):
    sources=dict(record['return_chart']['positions'])
    sources.update({key:value if isinstance(value,dict) else dict(longitude=value) for key,value in record['return_chart']['angles'].items()})
    contacts=[];excluded=[];limit=policy['orb']['maximum_degrees']*orb_multiplier
    for chart in charts.values():
        if chart['layer'] in exclude_layers:continue
        for target in chart['points']:
            if not target['core_root_refs']:continue
            sensitive=target.get('time_sensitive',False) or target['point_id'] in ANGULAR_POINTS
            uncertainty=target.get('uncertainty_degrees',0)
            if sensitive and (exclude_angles or target.get('angular_reliability') is not True or 'uncertainty_degrees' not in target):
                excluded.append(dict(chart_id=chart['id'],point_id=target['point_id'],reason='TARGET_ANGULAR_PRECISION_BLOCKED'));continue
            for name,point in sorted(sources.items()):
                if name in ANGULAR_POINTS and (exclude_angles or record['return_chart']['angular_status']!='CALCULATED'):continue
                longitude=finite(point.get('longitude'),name+'/longitude')%360
                separation=abs((longitude-target['longitude']+180)%360-180)
                aspect,angle=min(policy['orb']['aspects'].items(),key=lambda x:abs(separation-x[1]))
                orb=abs(separation-angle)
                if orb>limit:continue
                if orb+uncertainty>limit:
                    excluded.append(dict(chart_id=chart['id'],point_id=target['point_id'],source_point=name,reason='ORB_UNCERTAINTY_CROSSES_BOUNDARY'));continue
                # Por raíz dependiente y contacto, preserva la descripción sin crear votos.
                for group in sorted({groups[r] for r in target['core_root_refs']}):
                    refs=sorted(r for r in target['core_root_refs'] if groups[r]==group)
                    automatic=(name==record['returning_body'] and chart['id']==record['reference_chart'] and target['point_id']==name)
                    cid=record['return_id']+':'+chart['id']+':'+name+':'+target['point_id']+':'+aspect+':'+group
                    contacts.append(dict(id=cid,return_id=record['return_id'],chart_id=chart['id'],layer=chart['layer'],source_point=name,
                        target_point=target['point_id'],aspect=aspect,orb=orb,orb_limit=limit,root_refs=refs,dependency_group=group,
                        automatic_identity_contact=automatic,epistemic_class='E_PROJECT_HYPOTHESIS',status='SUPPORTED',scope='CALCULATED_ROOT_ACTIVATION'))
    return contacts,excluded


def calculate_event_delta(return_record,event,policy):
    if not event.get('event_datetime') or not event['source_refs'] or event['certainty']=='UNKNOWN':
        return dict(event_id=event['event_id'],status='NOT_EVALUABLE',reason='EVENT_TIME_OR_SOURCE_MISSING',event_delta_hours=None,
                    within_exact_window=None,within_active_cycle=None,occurred=event['occurred'])
    when=instant(event['event_datetime'],event.get('timezone'))
    exact=instant(return_record['exact_return_time']);delta=(when-exact).total_seconds()/3600
    limit=policy['event-window']['exact_window_hours'].get(return_record['returning_body'],policy['event-window']['secondary_window_hours'])
    uncertainty=event['uncertainty_hours']
    crosses=abs(delta)-uncertainty<=limit<abs(delta)+uncertainty
    in_window=abs(delta)+uncertainty<=limit
    end=instant(return_record['solver']['cycle_end']);active=(exact<=when-timedelta(hours=uncertainty) and when+timedelta(hours=uncertainty)<end)
    outside=when-timedelta(hours=uncertainty)<instant(return_record['solver']['window']['start']) or when+timedelta(hours=uncertainty)>instant(return_record['solver']['window']['end'])
    status='NOT_EVALUABLE' if crosses or outside else 'SUPPORTED' if event['occurred'] and in_window and any(not c['automatic_identity_contact'] for c in return_record['contacts']) else 'COMPATIBLE' if active and return_record['contacts'] else 'INSUFFICIENT'
    if not event['occurred']:status='NOT_EVALUABLE'
    return dict(event_id=event['event_id'],event_delta_hours=delta,delta_interval_hours=[delta-uncertainty,delta+uncertainty],
                within_exact_window=in_window if not crosses and not outside else None,within_active_cycle=active,
                cycle_right_censored=return_record['solver']['cycle_right_censored'],status=status,occurred=event['occurred'],
                reason='EVENT_FUTURE_NOT_OBSERVED' if not event['occurred'] else 'EVENT_OUTSIDE_SEARCH_COVERAGE' if outside else 'EVENT_UNCERTAINTY_CROSSES_WINDOW' if crosses else 'TECHNICAL_TEMPORAL_CORRESPONDENCE',
                correspondence_kind='EXACT_RETURN_WINDOW' if in_window else 'ACTIVE_CYCLE' if active else 'OUTSIDE_WINDOW')


def _fact_key(event):
    # Alias de un mismo hecho documentado no producen recurrencia independiente.
    return digest(dict(documentary_fact_key=event['fact_key']))


def _finish(result,policy):
    request=result['evaluation_input'];roots,charts,_,groups=_validate_inputs(request,result['root_input'],result['ssar_input'])
    events=_index(request.get('events',[]),'event_id');effective={};recurrence={};negative=[x for x in result['negative_results'] if x.get('stage')=='CALCULATION']
    edges=[];units=[]
    for record in result['returns']:
        record['contacts'],record['excluded_contacts']=calculate_return_overlays(record,charts,groups,policy)
        record['structural_roots']=sorted({r for c in record['contacts'] for r in c['root_refs']})
        record['event_correspondences']=[calculate_event_delta(record,e,policy) for e in events.values()]
        layers={c['layer'] for c in record['contacts']}
        record['activation_depth']='R5' if 'SSAR' in layers else 'R4' if layers&{'COMPOSITE','DAVISON','DRACONIC','EVENT'} else 'R3' if 'SYNASTRY' in layers else 'R2' if record['contacts'] else 'R1'
        record['status']='COMPATIBLE' if record['contacts'] else 'INSUFFICIENT'
        if any(c['status']=='SUPPORTED' for c in record['event_correspondences']):record['status']='SUPPORTED'
        if record['contacts'] and all(c['automatic_identity_contact'] for c in record['contacts']):
            negative.append(dict(stage='ACTIVATION',kind='weak_activation',return_id=record['return_id'],reason='MANDATORY_RETURN_IDENTITY_ONLY'))
        if not record['contacts']:negative.append(dict(stage='ACTIVATION',kind='no_activation',return_id=record['return_id']))
        if record['contacts'] and not any(e['occurred'] and e['within_exact_window'] is True for e in record['event_correspondences']):
            negative.append(dict(stage='CORRESPONDENCE',kind='activation_without_event',return_id=record['return_id']))
        for c in record['contacts']:
            units.append(dict(id=c['id'],return_id=record['return_id'],root_refs=c['root_refs'],dependency_group=c['dependency_group'],contributes_new_geometry=not c['automatic_identity_contact']))
            edges.append(dict(a=c['id'],b=c['dependency_group'],relation='RETURN_DERIVED_FROM_ROOT'))
            for correspondence in record['event_correspondences']:
                e=events[correspondence['event_id']]
                if correspondence['status']=='SUPPORTED' and not c['automatic_identity_contact']:
                    fact=_fact_key(e);effective.setdefault((c['dependency_group'],fact),set()).add(c['id'])
                    for root in c['root_refs']:recurrence.setdefault(root,{}).setdefault(fact,set()).add(e['event_id'])
    for event in events.values():
        if not any(e['event_id']==event['event_id'] and e['status']=='SUPPORTED' for r in result['returns'] for e in r['event_correspondences']):
            negative.append(dict(stage='CORRESPONDENCE',kind='event_without_activation',event_id=event['event_id']))
    result['negative_results']=negative
    result['dependency_graph']=dict(units=units,edges=edges,effective_units=[dict(dependency_group=key[0],fact_group_ref=key[1],contact_refs=sorted(value)) for key,value in sorted(effective.items())],
        statistical_independence_established=False,structural_roots_created=False)
    result['recurrence']=[dict(root_id=r,recurrence_count=len(facts),documentary_fact_group_refs=sorted(facts),event_refs=sorted({e for ids in facts.values() for e in ids}),
                               independent_event_count=None,independence_reason='DOCUMENTARY_FACT_DEDUPLICATION_IS_NOT_SOURCE_INDEPENDENCE') for r,facts in sorted(recurrence.items())]
    # R6 exige recurrencia documental; no declara independencia estadística de eventos.
    recurring={r for r,facts in recurrence.items() if len(facts)>=2}
    for record in result['returns']:
        if recurring&set(record['structural_roots']):record['activation_depth']='R6'
    result['robustness']=_robustness(result,charts,groups,policy) if request.get('robustness') and result['returns'] else dict(execution_status='not_run')
    from .return_controls import run_return_null
    result['null_model_result']=run_return_null(result,request['null_model'],policy) if request.get('null_model') and result['returns'] else dict(execution_status='not_run')
    result['calculation_hash']=digest([_calculation(r) for r in result['returns']])
    return result


def _calculation(record):
    return {key:value for key,value in record.items() if key not in {'contacts','excluded_contacts','event_correspondences','structural_roots','activation_depth','status'}}


def _robustness(result,charts,groups,policy):
    variants=[]
    for name,mult,layers,angles in [('HALF_ORB',.5,(),False),('NO_ANGLES',1,(),True),('NO_DRACONIC',1,('DRACONIC',),False),
                                   ('NO_RELATIONAL',1,('COMPOSITE','DAVISON'),False),('NO_SSAR',1,('SSAR',),False),('NO_EVENT_CHARTS',1,('EVENT',),False)]:
        contacts=[c for r in result['returns'] for c in calculate_return_overlays(r,charts,groups,policy,orb_multiplier=mult,exclude_layers=layers,exclude_angles=angles)[0]]
        variants.append(dict(id=name,contact_count=len(contacts),root_refs=sorted({root for c in contacts for root in c['root_refs']})))
    for name,bodies in [('NO_RAPID_RETURNS',{'MOON','MERCURY'}),('NO_SECONDARY_BODIES',set(r['returning_body'] for r in result['returns'])-set(policy['eligibility']['ordinary_bodies']))]:
        contacts=[c for r in result['returns'] if r['returning_body'] not in bodies for c in r['contacts']]
        variants.append(dict(id=name,contact_count=len(contacts),root_refs=sorted({root for c in contacts for root in c['root_refs']})))
    byclock={}
    for r in result['returns']:
        byclock.setdefault(r['clock_id'],{}).setdefault(r['location_variant'],set()).update(r['structural_roots'])
    return dict(execution_status='executed',ablations=variants,location_sensitivity=[dict(clock_id=k,variants=[dict(id=v,root_refs=sorted(refs)) for v,refs in sorted(value.items())]) for k,value in sorted(byclock.items())],
                birth_time_sensitivity='RECORDED_PER_RETURN_SOLVER',event_time_sensitivity='INTERVAL_BOUNDARY_TESTED',scores_created=False)


def run_return_activation(request, *, backend, canonical_roots, ssar_structure=None):
    policy=load_return_policy();roots,charts,appearances,groups=_validate_inputs(request,canonical_roots,ssar_structure)
    out=dict(schema_version='rra-1.0',enabled=request['enabled'],return_policy_id=policy['activation']['policy_id'],return_policy_hash=digest(policy),engine_version='RRA_1.0',
        execution_status='not_run',input_hash=digest(request),evaluation_input=deepcopy(request),root_input=deepcopy(canonical_roots),ssar_input=deepcopy(ssar_structure),
        returns=[],coverage=[],negative_results=[],dependency_graph={},recurrence=[],robustness={},null_model_result={},calculation_hash=digest([]),
        external_validation_status='NOT_PERFORMED',structural_scoring_modified=False,ontology_effect='NONE',discriminator_effect='NONE',iat_modified=False,status_scope='TECHNICAL_TEMPORAL_ACTIVATION')
    provider=ReturnPositionProvider(backend)
    if request['enabled']:
        for clock in request.get('clocks',[]):
            ref=charts[clock['reference_chart']];point=next(p for p in ref['points'] if p['point_id']==clock['reference_point'])
            if not _eligible(clock,point,appearances,policy):
                out['coverage'].append(dict(clock_id=clock['id'],execution_status='blocked',reason='RETURN_BODY_NOT_ELIGIBLE'))
                out['negative_results'].append(dict(stage='CALCULATION',clock_id=clock['id'],kind='not_evaluable',reason='RETURN_BODY_NOT_ELIGIBLE'));continue
            try:
                solver=find_all_return_passes(provider,body=clock['returning_body'],reference_longitude=point['longitude'],start=clock['start'],end=clock['end'],policy=policy['activation']['solver'])
                hits=solver['exact_hits'];records=[];time_sensitivity=[]
                uncertainty=clock.get('reference_uncertainty_degrees')
                if request.get('robustness') and uncertainty is not None and uncertainty>0:
                    for offset in (-uncertainty,uncertainty):
                        variant=find_all_return_passes(provider,body=clock['returning_body'],reference_longitude=point['longitude']+offset,start=clock['start'],end=clock['end'],policy=policy['activation']['solver'])
                        time_sensitivity.append(dict(target_offset_degrees=offset,exact_times=[h['exact_datetime'] for h in variant['exact_hits']],pass_count=len(variant['exact_hits'])))
                for n,hit in enumerate(hits):
                    info={key:value for key,value in solver.items() if key!='exact_hits'}
                    info.update(cycle_end=hits[n+1]['exact_datetime'] if n+1<len(hits) else clock['end'],cycle_right_censored=n+1==len(hits),
                                target_uncertainty_degrees=uncertainty,birth_time_sensitivity=time_sensitivity)
                    angular=clock['angular_reliability'] and uncertainty==0
                    for loc in clock['locations']:
                        chart=build_return_chart(provider,hit['exact_datetime'],loc,angular_reliability=angular)
                        rid=clock['id']+':PASS_'+str(n+1)+':'+loc['id']
                        records.append(dict(return_id=rid,clock_id=clock['id'],owner=clock['owner'],return_type='NATAL_RETURN' if ref['layer']=='NATAL' else 'RELATIONAL_RETURN_EXPERIMENTAL' if ref['layer']!='EVENT' else 'EVENT_RETURN_EXPERIMENTAL',
                            returning_body=clock['returning_body'],reference_chart=ref['id'],reference_longitude=point['longitude']%360,exact_return_time=hit['exact_datetime'],return_pass=n+1,motion_state=hit['motion_state'],angular_error=hit['orb'],
                            solver=deepcopy(info),location_variant=loc['id'],location_basis=loc['basis'],return_chart=deepcopy(chart),contacts=[],excluded_contacts=[],event_correspondences=[],structural_roots=[],activation_depth='R1',
                            status='INSUFFICIENT',doctrine_class='B_TECHNIQUE' if ref['layer']=='NATAL' else 'E_PROJECT_HYPOTHESIS',iat_eligible=False))
                out['returns'].extend(records)
                out['coverage'].append(dict(clock_id=clock['id'],execution_status='executed',return_pass_count=len(hits),sampling_step_seconds=solver['sampling_step_seconds'],search_window=solver['window']))
                if not hits:out['negative_results'].append(dict(stage='CALCULATION',kind='no_return_in_window',clock_id=clock['id']))
            except AstronomyBackendNotEvaluableError as exc:
                out['coverage'].append(dict(clock_id=clock['id'],execution_status='blocked',reason=str(exc)))
                out['negative_results'].append(dict(stage='CALCULATION',clock_id=clock['id'],kind='not_evaluable',reason=str(exc)))
        executed=any(c['execution_status']=='executed' for c in out['coverage']);blocked=any(c['execution_status']=='blocked' for c in out['coverage'])
        out['execution_status']='partial' if executed and blocked else 'blocked' if blocked else 'executed' if executed else 'not_run'
    out=_finish(out,policy);validate_contract(out,'Result');return out


def _validate_execution(result,policy):
    request=result['evaluation_input'];clocks=_index(request.get('clocks',[]),'id')
    coverage=_index(result['coverage'],'clock_id');records=result['returns']
    _index(records,'return_id')
    expected=set(clocks) if request['enabled'] else set()
    if set(coverage)!=expected:raise ValueError('Cobertura RRA incompleta o reloj añadido.')
    charts=_index(request.get('charts',[]),'id')
    for cid,clock in clocks.items():
        rows=[r for r in records if r['clock_id']==cid]
        if not request['enabled']:continue
        entry=coverage[cid]
        if entry['execution_status']=='blocked':
            if rows:raise ValueError('Reloj bloqueado contiene retornos.')
            continue
        locations=_index(clock['locations'],'id')
        passes=entry['return_pass_count']
        if {(r['return_pass'],r['location_variant']) for r in rows}!={(n,loc) for n in range(1,passes+1) for loc in locations} or len(rows)!=passes*len(locations):
            raise ValueError('Pasadas o ubicaciones RRA incompletas.')
        target=next(p for p in charts[clock['reference_chart']]['points'] if p['point_id']==clock['reference_point'])['longitude']%360
        for row in rows:
            if row['returning_body']!=clock['returning_body'] or row['reference_chart']!=clock['reference_chart'] or row['reference_longitude']!=target:
                raise ValueError('Retorno RRA distinto del reloj declarado.')
            if not instant(clock['start'])<=instant(row['exact_return_time'])<=instant(clock['end']):
                raise ValueError('Retorno fuera de cobertura.')
            point=row['return_chart']['positions'].get(clock['returning_body'])
            if not point or abs((point['longitude']-target+180)%360-180)>policy['activation']['solver']['angular_tolerance_degrees']:
                raise ValueError('Carta RRA no perfecciona el retorno declarado.')
            if row['return_chart']['angular_status']=='CALCULATED' and (not clock['angular_reliability'] or clock.get('reference_uncertainty_degrees')!=0 or locations[row['location_variant']]['basis']=='unknown'):
                raise ValueError('Ángulos RRA sin precisión o ubicación suficiente.')
    if any(r['clock_id'] not in clocks for r in records):raise ValueError('Retorno de reloj no declarado.')
    executed=any(c['execution_status']=='executed' for c in coverage.values());blocked=any(c['execution_status']=='blocked' for c in coverage.values())
    status='partial' if executed and blocked else 'blocked' if blocked else 'executed' if executed else 'not_run'
    if result['execution_status']!=status:raise ValueError('Estado de ejecución RRA incoherente.')


def validate_return_activation(result, *, backend=None):
    validate_contract(result,'Result');policy=load_return_policy()
    _validate_execution(result,policy)
    if result['return_policy_hash']!=digest(policy) or result['input_hash']!=digest(result['evaluation_input']):
        raise ValueError('RRA no reproduce política o entradas congeladas.')
    if result['calculation_hash']!=digest([_calculation(r) for r in result['returns']]):raise ValueError('Snapshot astronómico RRA alterado.')
    if not result['enabled'] and (result['returns'] or result['coverage']):raise ValueError('RRA desactivado contiene cálculos.')
    if backend is not None:
        reproduction=run_return_activation(result['evaluation_input'],backend=backend,canonical_roots=result['root_input'],ssar_structure=result['ssar_input'])
    else:
        reproduction=_finish(deepcopy(result),policy)
    if reproduction!=result:raise ValueError('RRA canónico no reproduce geometría, eventos y controles.')


def attach_return_activation(canonical,request,*,backend):
    """Devuelve una copia; no escribe ni modifica una verdad canónica histórica."""
    out=deepcopy(canonical)
    ssar=out.get('ssar')
    if not ssar or not ssar.get('enabled'):raise ValueError('La integración RRA exige SSAR explícitamente activo.')
    validate_ssar_with_returns(ssar)
    roots=out.get('independent_roots',{}).get('roots')
    if not isinstance(roots,list):raise ValueError('La nueva ejecución RRA necesita raíces M17 disponibles.')
    ssar['temporal_activation']=run_return_activation(request,backend=backend,canonical_roots=roots,ssar_structure=ssar['structure'])
    return out


def render_return_summary(result):
    validate_return_activation(result)
    paragraphs=['RRA registra activaciones temporales de raíces preexistentes; su validación externa sigue pendiente. Estado de ejecución: '+result['execution_status']+'.']
    for record in result['returns']:
        paragraphs.append(record['returning_body']+' de '+record['owner']+': retorno '+record['exact_return_time']+', pasada '+str(record['return_pass'])+' ('+record['motion_state']+'). Raíces activadas: '+(', '.join(record['structural_roots']) or 'ninguna')+'. Estado técnico: '+record['status']+'. Ubicación: '+record['location_basis']+'.')
        for contact in record['contacts']:
            identity=' Contacto obligatorio del retorno, sin geometría nueva.' if contact['automatic_identity_contact'] else ''
            paragraphs.append('Activación en '+contact['layer']+': '+contact['source_point']+' '+contact['aspect']+' '+contact['target_point']+
                ', orbe '+f"{contact['orb']:.6f}"+' grados, raíces '+', '.join(contact['root_refs'])+
                ', grupo de dependencia '+contact['dependency_group']+'.'+identity)
        for e in record['event_correspondences']:
            delta=e['event_delta_hours']
            paragraphs.append('Evento '+e['event_id']+': '+e['status']+'. Desfase respecto del retorno: '+('no evaluable' if delta is None else f'{delta:.3f} horas')+'. Una pertenencia al ciclo vigente se distingue de la ventana de exactitud.')
    from .return_controls import annual_return_summary
    paragraphs.append('Recurrencia documental: '+str(len(result['recurrence']))+' raíces; unidades efectivas deduplicadas: '+str(len(result['dependency_graph']['effective_units']))+'. La independencia estadística no está establecida. Densidad anual descriptiva: '+str(annual_return_summary(result))+'.')
    paragraphs.append('Robustez: '+result['robustness']['execution_status']+'. Control nulo: '+result['null_model_result']['execution_status']+'. Su excedencia Monte Carlo es exploratoria y condicional a las referencias fijadas.')
    for variant in result['robustness'].get('ablations',[]):
        paragraphs.append('Ablación '+variant['id']+': '+str(variant['contact_count'])+' contactos; raíces conservadas: '+(', '.join(variant['root_refs']) or 'ninguna')+'.')
    control=result['null_model_result']
    if control.get('execution_status')=='COMPLETED_EXPLORATORY_CONTROL':
        paragraphs.append('Control '+control['method']+', semilla '+str(control['seed'])+': '+str(control['completed_simulations'])+
            ' réplicas, '+str(control['k'])+' excedencias; p_MC='+str(control['p_mc'])+'. No autoriza inferencia confirmatoria.')
    elif control.get('reason'):
        paragraphs.append('Control no evaluable: '+control['reason']+'.')
    for negative in result['negative_results']:
        paragraphs.append('Contraevidencia o cobertura negativa: '+negative['kind']+', ámbito '+negative['stage']+
            ', referencia '+str(negative.get('return_id',negative.get('event_id',negative.get('clock_id','sin referencia'))))+
            (', motivo '+negative['reason'] if negative.get('reason') else '')+'.')
    paragraphs.append('Se conservaron '+str(len(result['negative_results']))+' resultados negativos o no evaluables. Los overlays derivados y la conjunción obligatoria del planeta con su posición de referencia comparten dependencia; no prueban identidad metafísica, reciprocidad ni decisiones futuras.')
    paragraphs.append('Interpretación: la correspondencia describe cuándo se activa una arquitectura previamente cualificada. El ciclo vigente, la proximidad al instante exacto y la coincidencia bajo fechas control permanecen explicaciones distintas. La atribución funcional procede del SSAR estructural y de sus fuentes; RRA no añade una doctrina de origen ni un significado afectivo independiente.')
    return '\n\n'.join(paragraphs)


def validate_ssar_with_returns(ssar):
    """Valida el SSAR histórico byte a byte y después su extensión opcional."""
    from .ssar_pipeline import validate_canonical_ssar
    legacy={k:v for k,v in ssar.items() if k!='temporal_activation'}
    validate_canonical_ssar(legacy)
    if 'temporal_activation' in ssar:
        rra=ssar['temporal_activation']
        if not ssar['enabled']:raise ValueError('RRA requiere SSAR activo.')
        validate_return_activation(rra)
        if rra['ssar_input']!=ssar['structure']:raise ValueError('Anclaje RRA distinto del SSAR canónico.')


def render_ssar_with_returns(canonical):
    from .ssar_pipeline import render_ssar_summary
    ssar=canonical.get('ssar')
    if ssar is None:return ''
    validate_ssar_with_returns(ssar)
    copy=deepcopy(canonical);copy['ssar'].pop('temporal_activation',None)
    text=render_ssar_summary(copy)
    if 'temporal_activation' in ssar:text+='\n\n'+render_return_summary(ssar['temporal_activation'])
    return text
