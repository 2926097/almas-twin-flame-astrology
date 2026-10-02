"""Controles RRA condicionales sobre una búsqueda astronómica íntegra y fija."""
from __future__ import annotations
from copy import deepcopy
from datetime import timedelta
from random import Random


def _measure(result,events,policy):
    from .return_activation import calculate_event_delta,_fact_key
    units=set()
    for record in result['returns']:
        for event in events:
            relation=calculate_event_delta(record,event,policy)
            if relation['status']=='SUPPORTED':
                for contact in record['contacts']:
                    if not contact['automatic_identity_contact']:
                        units.add((contact['dependency_group'],_fact_key(event)))
    return len(units)


def run_return_null(result,configuration,policy):
    from .return_solver import instant
    from .return_activation import digest
    method=configuration['method'];seed=configuration['seed'];budget=configuration['simulations']
    if method not in policy['null-model']['methods'] or type(seed) is not int or type(budget) is not int or not 1<=budget<=policy['null-model']['maximum_simulations']:
        raise ValueError('Modelo nulo, semilla o presupuesto RRA no registrados.')
    request=result['evaluation_input'];events=deepcopy(request.get('events',[]))
    base=dict(method=method,seed=seed,requested_simulations=budget,measure=policy['null-model']['measure'],
        universe_hash=digest(dict(clocks=request.get('clocks',[]),charts=request.get('charts',[]),policy=policy)),
        multiplicity_rule=policy['null-model']['multiple_search'],exchangeability_status='NOT_ESTABLISHED_FOR_REAL_POPULATION',
        confirmatory_inference_allowed=False,external_validation_status='NOT_PERFORMED',metaphysical_probability=False,
        stopping_rule='FIXED_BUDGET_NO_RESAMPLING_NO_EARLY_STOP')
    if result['execution_status']!='executed' or not events or any(not e.get('event_datetime') or not e['occurred'] or not e['source_refs'] or e['certainty']=='UNKNOWN' for e in events):
        return dict(base,execution_status='NOT_EVALUABLE',reason='INCOMPLETE_COVERAGE_OR_EVENT_INPUT',p_mc=None,completed_simulations=0)
    if any(chart['layer']=='EVENT' for chart in request.get('charts',[])):
        return dict(base,execution_status='NOT_EVALUABLE',reason='EVENT_REFERENCE_CHART_RECOMPUTATION_REQUIRED',p_mc=None,completed_simulations=0)
    dates=[instant(e['event_datetime'],e.get('timezone')) for e in events]
    starts=[instant(c['start']) for c in request.get('clocks',[])];ends=[instant(c['end']) for c in request.get('clocks',[])]
    lower=(max(starts)-min(dates)).total_seconds();upper=(min(ends)-max(dates)).total_seconds()
    if method=='EVENT_DATE_SHIFT' and lower>=upper:
        return dict(base,execution_status='NOT_EVALUABLE',reason='NO_COMMON_SHIFT_SUPPORT',p_mc=None,completed_simulations=0)
    controls=[instant(x) for x in configuration.get('control_datetimes',[])]
    if method=='CONTROL_DATES' and len(controls)!=len(events)*budget:
        raise ValueError('CONTROL_DATES exige una fecha por evento y réplica, fijada antes de calcular.')
    if any(not max(starts)<=x<=min(ends) for x in controls):
        raise ValueError('Fecha control fuera de la cobertura común.')
    rng=Random(seed);observed=_measure(result,events,policy);values=[];replicas=[]
    for index in range(budget):
        if method=='EVENT_DATE_SHIFT':
            delta=rng.uniform(lower,upper);shifted=[d+timedelta(seconds=delta) for d in dates]
        elif method=='EVENT_DATE_PERMUTATION':
            shifted=list(dates);rng.shuffle(shifted)
        else:shifted=controls[index*len(events):(index+1)*len(events)]
        sample=deepcopy(events)
        for event,dt in zip(sample,shifted):
            event['event_datetime']=dt.isoformat();event.pop('timezone',None)
        value=_measure(result,sample,policy);values.append(value)
        replicas.append(dict(index=index,value=value,event_input_hash=digest(sample)))
    k=sum(value>=observed for value in values)
    return dict(base,execution_status='COMPLETED_EXPLORATORY_CONTROL',completed_simulations=budget,observed=observed,k=k,
        p_mc=(k+1)/(budget+1),resolution=1/(budget+1),replicas=replicas,failures=[],null_variation=len(set(values))>1,
        null_scope='CONDITIONAL_EVENT_TIMING_WITH_FIXED_REFERENCE_ARCHITECTURE',
        distribution='UNIFORM_COMMON_SEQUENCE_SHIFT' if method=='EVENT_DATE_SHIFT' else 'PREREGISTERED_CONTROL_DATES' if method=='CONTROL_DATES' else 'UNIFORM_DATE_PERMUTATION',
        common_shift_support_seconds=[lower,upper] if method=='EVENT_DATE_SHIFT' else None,
        interpretation='Excedencia bajo este control; no probabilidad de ontología. Una permutación sin variación es no informativa.')


def annual_return_summary(result):
    """Densidad descriptiva por año UTC; no asigna rareza ni relevancia causal."""
    from .return_solver import instant
    years={}
    seen=set()
    for record in result['returns']:
        key=(record['clock_id'],record['return_pass'])
        if key in seen:continue
        seen.add(key);year=instant(record['exact_return_time']).year
        entry=years.setdefault(year,dict(year=year,return_count=0,activated_return_count=0,root_refs=set()))
        entry['return_count']+=1;entry['activated_return_count']+=bool(record['contacts']);entry['root_refs'].update(record['structural_roots'])
    return [dict(e,root_refs=sorted(e['root_refs'])) for _,e in sorted(years.items())]
