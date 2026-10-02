"""Calendar and documentary assessments over an already qualified structure."""
from __future__ import annotations
from datetime import date
from .ssar import _index, assess_ssar_claim, validate_ssar_schema
from .ssar_calculated_points import _hash

CLOCK_GROUPS = dict(TPROG='DIRECTIONS_PROGRESSIONS',TDIR='DIRECTIONS_PROGRESSIONS',
                    TTRANSIT='TRANSITS_ECLIPSES',TECLIPSE='TRANSITS_ECLIPSES',TREL='RELATIONAL',TATACIR='CIRCUMAMBULATION')

def architecture_hash(structure, request):
    # Includes window boundaries, monitoring and coding commitments, not their observed outcomes.
    windows=[{k:w[k] for k in ('id','complex_ref','start','end','monitoring_ref')} for w in request['windows']]
    claims=[{k:c[k] for k in ('id','complex_ref','scope','window_ref','coding_rule_ref')} for c in request['claims']]
    return _hash(dict(structure=structure,windows=windows,claims=claims))

def freeze_architecture(structure, request, *, policy_hash, registered_at, mode='RETROSPECTIVE'):
    date.fromisoformat(registered_at)
    out=dict(policy_hash=policy_hash,architecture_hash=architecture_hash(structure,request),registered_at=registered_at,
             mode=mode,timestamp_externally_verified=False)
    validate_ssar_schema(out,'F8Receipt')
    return out

def run_integration(structure, request, *, policy_hash, m27_ledger=None):
    validate_ssar_schema(request,'F8Request')
    complexes=_index(structure['complexes']+structure['dyads'],'id');windows=_index(request['windows'],'id')
    _index(request['claims'],'id')
    receipt=request['freeze']
    if receipt and (receipt['policy_hash']!=policy_hash or receipt['architecture_hash']!=architecture_hash(structure,request)):
        raise ValueError('El recibo no reproduce la política y arquitectura comprometidas.')
    temporal=[];global_clock_ids=set()
    for w in request['windows']:
        if w['complex_ref'] not in complexes:raise ValueError('Complejo temporal desconocido.')
        start,end=date.fromisoformat(w['start']),date.fromisoformat(w['end'])
        if end<start:raise ValueError('Ventana temporal invertida.')
        c=complexes[w['complex_ref']];clocks=_index(w['clocks'],'id');admitted=[];groups=set();blocked=[]
        for clock in clocks.values():
            if clock['id'] in global_clock_ids:raise ValueError('El mismo reloj requiere una referencia compartida.')
            global_clock_ids.add(clock['id'])
            if clock['complex_ref']!=c['id']:
                raise ValueError('Reloj fuera de su complejo o anclaje.')
            day=date.fromisoformat(clock['date'])
            precise=(clock['longitude'] is not None and clock['target_longitude'] is not None
                     and clock['input_precision_sufficient'] is True and clock['robust'] is True
                     and clock['source_refs'] and clock['core_root_refs'] and set(clock['core_root_refs'])<=set(c['core_root_refs']))
            if not precise:blocked.append(clock['id']);continue
            delta=abs((clock['longitude']-clock['target_longitude']+180)%360-180)
            if start<=day<=end and min(delta,abs(180-delta))<=1.0:
                admitted.append(clock['id']);groups.add(CLOCK_GROUPS[clock['family']])
        closed=bool(w['observed_through'] and date.fromisoformat(w['observed_through'])>=end and w['observation_complete'] and w['monitoring_ref'])
        frozen=bool(receipt and date.fromisoformat(receipt['registered_at'])<start)
        complete=bool(c['qualified_complex'] and frozen and closed and not blocked and len(groups)>=2)
        reasons=[label for ok,label in [(c['qualified_complex'],'STRUCTURE_NOT_QUALIFIED'),(frozen,'ARCHITECTURE_NOT_FROZEN_BEFORE_WINDOW'),
                 (closed,'WINDOW_OPEN_OR_OBSERVATION_INCOMPLETE'),(not blocked,'CLOCK_PRECISION_OR_PROVENANCE_MISSING'),(len(groups)>=2,'TWO_CLOCK_GROUPS_NOT_MET')] if not ok]
        assessment=assess_ssar_claim(scope='TEMPORAL_ACTIVATION',policy_ref='ALMAS_SSAR_1_25_FROZEN_EXPERIMENTAL_V1',rule_ref='SSAR_TEMPORAL_TWO_GROUPS_V1',
            coverage_sufficient=bool(frozen and closed and not blocked and c['qualified_complex']),positive_complete=complete,
            compatible=bool(c['qualified_complex'] and admitted),evidence_refs=admitted)
        temporal.append(dict(window_ref=w['id'],complex_ref=c['id'],clock_refs=sorted(admitted),effective_clock_groups=sorted(groups),
            assessment=assessment,qualified_temporal_complex=complete,window_closed=closed,architecture_frozen_before_window=frozen,
            prediction_class='UNREGISTERED' if not receipt else 'RETROSPECTIVE' if receipt['mode']=='RETROSPECTIVE' else 'PROSPECTIVELY_DECLARED_UNVERIFIED',blockers=reasons))
    events=_index((m27_ledger or {}).get('events',[]),'event_id');facts={};event_facts={}
    for e in events.values():
        # Equal facts do not become independent merely by acquiring another event ID.
        key=e.get('fact_key') or _hash({k:e.get(k) for k in ('subjects','date','date_range','fact_statement')})
        facts.setdefault(key,[]).append(e['event_id']);event_facts[e['event_id']]=key
    docs=[];consumers={};tindex=_index(temporal,'window_ref')
    for claim in request['claims']:
        if claim['complex_ref'] not in complexes:raise ValueError('Complejo documental desconocido.')
        c=complexes[claim['complex_ref']]
        if claim['coding_rule_ref']!=c['id']+'_DOCUMENTARY_V1':raise ValueError('Regla de codificación documental no congelada.')
        support=set(claim['support_event_refs']);exclude=set(claim['excluding_event_refs']);refs=support|exclude
        if m27_ledger is not None and refs-set(events):raise ValueError('Referencia de evento M27 rota.')
        if support&exclude:raise ValueError('Un evento no puede apoyar y excluir la misma hipótesis.')
        if {event_facts[e] for e in support if e in events}&{event_facts[e] for e in exclude if e in events}:
            raise ValueError('Alias documentales asignan roles contradictorios al mismo hecho.')
        wr=claim['window_ref'];temporal_claim=claim['scope']=='TEMPORAL'
        if temporal_claim and (wr not in windows or windows[wr]['complex_ref']!=c['id']):
            raise ValueError('Correspondencia temporal sin ventana del complejo.')
        if not temporal_claim and wr is not None:raise ValueError('La correspondencia estructural no impone ventana.')
        good=[]
        for ref in sorted(refs):
            if ref not in events:continue
            e=events[ref];valid=bool(e.get('record_status')=='ACTIVE' and e.get('documentary_quality_contract_met') is True
                and e.get('fact_interpretation_separated') is True and e.get('source_refs')
                and set(e.get('resolved_root_refs',[]))&set(c['core_root_refs']))
            if temporal_claim:
                valid=bool(valid and e.get('date_precision_contract_met') is True and e.get('date_precision') in ('EXACT_DATE','EXACT_DATETIME') and e.get('date')
                    and windows[wr]['start']<=e['date'][:10]<=windows[wr]['end'])
            if valid:good.append(ref)
            consumers.setdefault(event_facts[ref],[]).append(claim['id'])
        neg=sorted(exclude&set(good));pos=sorted(support&set(good))
        covered=bool(claim['coverage_complete'] and set(good)==refs and m27_ledger and c['qualified_complex'])
        if temporal_claim:covered=bool(covered and tindex[wr]['qualified_temporal_complex'])
        assessment=assess_ssar_claim(scope='DOCUMENTARY_TEMPORAL_CORRESPONDENCE' if temporal_claim else 'DOCUMENTARY_STRUCTURAL_CORRESPONDENCE',
            policy_ref='ALMAS_SSAR_1_25_FROZEN_EXPERIMENTAL_V1',rule_ref=claim['coding_rule_ref'],coverage_sufficient=covered,
            positive_complete=bool(pos and not neg),compatible=bool(pos),evidence_refs=pos,
            excluding_counterevidence_refs=neg,counterevidence_evaluable=bool(neg))
        docs.append(dict(claim_ref=claim['id'],complex_ref=c['id'],scope=claim['scope'],assessment=assessment,event_refs=sorted(refs),
            fact_group_refs=sorted({event_facts[e] for e in refs if e in events}),window_ref=wr,coding_rule_ref=claim['coding_rule_ref'],
            independent_fact_count=len({event_facts[e] for e in good}),causal_status='UNESTABLISHED'))
    out=dict(temporal=temporal,documentary=docs,shared_events=[dict(fact_group_ref=k,event_refs=sorted(facts[k]),consumer_refs=sorted(set(ids)),
        contributes_new_evidence=False) for k,ids in sorted(consumers.items()) if len(set(ids))>1 or len(facts[k])>1],
        documentary_event_source='M27_NORMALIZED_LEDGER',external_validation_status='NOT_PERFORMED')
    validate_ssar_schema(out,'F8Result');return out
