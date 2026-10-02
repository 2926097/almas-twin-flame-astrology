"""Fixed-budget synthetic pipeline controls; no empirical validation claim."""
from __future__ import annotations
from copy import deepcopy
from random import Random
from .ssar_calculated_points import _hash
from .ssar_pipeline import run_ssar_pipeline
from .ssar_integration import freeze_architecture

ABLATIONS=('AB_NO_SSAR','AB_NO_S1','AB_NO_EROS_PSYCHE','AB_NO_MYTHIC_DYADS','AB_NO_MOIRAI',
           'AB_NO_VERTEX','AB_NO_BML','AB_NO_LOTS','AB_ONLY_PLANETS_NODES_ANGLES')
REMOVED=dict(AB_NO_EROS_PSYCHE={'EROS','PSYCHE'},AB_NO_MOIRAI={'KLOTHO','LACHESIS','ATROPOS','MOIRA'},
             AB_NO_VERTEX={'VERTEX','ANTI_VERTEX'},AB_NO_BML={'BLACK_MOON_MEAN','BLACK_MOON_OSCULATING'})

def experimental_metrics(result):
    return dict(qualified_significators=sum(a['qualification']=='QUALIFIED_SIGNIFICATOR' for a in result['structure']['appearances']),
                effective_groups=len(result['structure']['dependency_graph']['effective_groups']),
                qualified_complexes=sum(c['qualified_complex'] for c in result['structure']['complexes']+result['structure']['dyads']),
                qualified_windows=sum(w['qualified_temporal_complex'] for w in result['integration']['temporal']),
                supported_documentary_claims=sum(c['assessment']['status']=='SUPPORTED' for c in result['integration']['documentary']))

def ablate_request(request, ablation):
    if ablation not in ABLATIONS:raise ValueError('Ablación no registrada.')
    if ablation in ('AB_NO_SSAR','AB_ONLY_PLANETS_NODES_ANGLES'):return dict(enabled=False,ablation=ablation)
    out=deepcopy(request);out['ablation']=ablation
    if 'integration' in out:out['integration']['freeze']=None
    return out

def _counterfactual_freeze(request, original, m27_ledger):
    receipt=original.get('integration',{}).get('freeze')
    if not receipt or not request['enabled'] or 'integration' not in request:return request
    initial=run_ssar_pipeline(request,m27_ledger=m27_ledger)
    request['integration']['freeze']=freeze_architecture(initial['structure'],request['integration'],
        policy_hash=initial['evaluation_policy_hash'],registered_at=receipt['registered_at'],mode='RETROSPECTIVE')
    return request

def run_ablations(request, *, core_snapshot, m27_ledger=None):
    baseline=run_ssar_pipeline(request,m27_ledger=m27_ledger);core_hash=_hash(core_snapshot);runs=[]
    for name in ABLATIONS:
        req=_counterfactual_freeze(ablate_request(request,name),request,m27_ledger);result=run_ssar_pipeline(req,m27_ledger=m27_ledger)
        runs.append(dict(id=name,input_hash=_hash(req),experimental_metrics=experimental_metrics(result),
            core_before_hash=core_hash,core_after_hash=_hash(core_snapshot),core_invariant=core_hash==_hash(core_snapshot),
            prediction_class='RETROSPECTIVE_COUNTERFACTUAL',discrimination_improvement_measured=False))
    return dict(policy_id=baseline['policy_id'],policy_hash=baseline['evaluation_policy_hash'],baseline_metrics=experimental_metrics(baseline),
                runs=runs,external_validation_status='NOT_PERFORMED',synthetic_scope_only=True)

def _rotate_targets(request, rotation):
    out=deepcopy(request)
    def visit(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key=='target_longitude' and item is not None:value[key]=(item+rotation)%360
                else:visit(item)
        elif isinstance(value,list):
            for item in value:visit(item)
    visit(out)
    if 'integration' in out:out['integration']['freeze']=None
    return out

def run_synthetic_null(request, *, seed, simulations, core_snapshot, m27_ledger=None, method='TARGET_ROTATION'):
    if type(seed) is not int or type(simulations) is not int or not 1<=simulations<=10000:
        raise ValueError('El control exige semilla entera y presupuesto fijo de 1 a 10000 réplicas.')
    if method not in ('TARGET_ROTATION','CLOCK_DATE_SHIFT','EVENT_DATE_PERMUTATION','PRECISION_LOSS'):raise ValueError('Método de control no registrado.')
    rng=Random(seed);observed=run_ssar_pipeline(request,m27_ledger=m27_ledger);replicas=[];failures=[]
    core_hash=_hash(core_snapshot)
    for i in range(simulations):
        rotation=rng.randrange(1,360000)/1000
        control=_rotate_targets(request,rotation) if method=='TARGET_ROTATION' else deepcopy(request)
        control_ledger=deepcopy(m27_ledger)
        if 'integration' in control:control['integration']['freeze']=None
        if method=='CLOCK_DATE_SHIFT':
            from datetime import date,timedelta
            shift=rng.randrange(-365,366)
            for w in control.get('integration',{}).get('windows',[]):
                for clock in w['clocks']:clock['date']=(date.fromisoformat(clock['date'])+timedelta(days=shift)).isoformat()
        elif method=='EVENT_DATE_PERMUTATION' and control_ledger:
            events=[e for e in control_ledger['events'] if e.get('date_precision')=='EXACT_DATE' and e.get('date')]
            dates=[e['date'] for e in events];rng.shuffle(dates)
            for e,day in zip(events,dates):e['date']=day
        elif method=='PRECISION_LOSS':
            for profile in control.get('profiles',{}).values():
                for observation in profile.get('observations',[]):
                    if observation.get('robustness'):observation['robustness']['input_precision_sufficient']=None
                for context in profile.get('contexts',[]):context['time_uncertainty_minutes']=None
        try:
            control=_counterfactual_freeze(control,request,control_ledger)
            result=run_ssar_pipeline(control,m27_ledger=control_ledger)
            replicas.append(dict(index=i,rotation_deg=rotation,input_hash=_hash(control),ledger_hash=_hash(control_ledger) if control_ledger is not None else None,metrics=experimental_metrics(result)))
        except ValueError as exc:failures.append(dict(index=i,reason=str(exc)))
    return dict(policy_id=observed['policy_id'],policy_hash=observed['evaluation_policy_hash'],method=method,seed=seed,requested_simulations=simulations,
        completed_simulations=len(replicas),failures=failures,replicas=replicas,observed_metrics=experimental_metrics(observed),
        execution_status='NOT_EVALUABLE' if failures else 'COMPLETED_SYNTHETIC_STRESS_TEST',
        stopping_rule='FIXED_BUDGET_NO_RESAMPLING_NO_EARLY_STOP',multiplicity_rule='REPLAY_ALL_DECLARED_OBJECTS_VARIANTS_ASPECTS_FILTERS_GROUPS_COMPLEXES_WINDOWS',
        exchangeability_status='NOT_ESTABLISHED_FOR_REAL_POPULATION',matched_factors=['ALL_UNROTATED_INPUTS_FIXED'],
        epoch_age_place_precision_density_control='HELD_FIXED_WITHIN_SYNTHETIC_INPUT; NO_POPULATION_MATCHING',
        p_values=None,cluster_strength=None,primary_metric_status='NOT_OPERATIONALIZED',confirmatory_inference_allowed=False,
        core_invariant=core_hash==_hash(core_snapshot),external_validation_status='NOT_PERFORMED')
