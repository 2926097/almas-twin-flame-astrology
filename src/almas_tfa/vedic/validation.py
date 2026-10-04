"""Auditoría descriptiva; no promoción automática de variables ni etiquetas L3."""
from copy import deepcopy
from datetime import timedelta
from itertools import permutations
from math import isfinite
from random import Random
from zoneinfo import ZoneInfo
from .chart import compute_vedic_chart
from .synastry import compute_vedic_synastry
from .timing import instant


def chart_signature(chart):
    return dict(nakshatras={p: [v['nakshatra']['index'], v['nakshatra']['pada']] for p,v in chart['d1'].items()},
        d9={p:v['sign'] for p,v in chart['d9'].items()}, karakas=chart['karakas']['roles'],
        arudhas={p:v['sign'] for p,v in chart['arudhas'].items()}, karakamsha=chart['karakamsha']['sign'])


def compute_sensitivity(request, configuration=None, minutes=(1, 5, 15, 30), ayanamshas=('LAHIRI', 'RAMAN', 'KP')):
    baseline = compute_vedic_chart(request, configuration)
    base = chart_signature(baseline)
    runs = []
    for mode in ayanamshas:
        cfg = {**baseline['configuration'], 'ayanamsha': mode}
        chart = compute_vedic_chart(request, cfg)
        sig = chart_signature(chart)
        changed = [k for k in base if sig[k] != base[k]]
        runs.append(dict(axis='AYANAMSHA', value=mode, changed_families=changed, stable=not changed))
    for margin in minutes:
        if isinstance(margin, bool) or not isinstance(margin, (int,float)) or not isfinite(margin) or not 0 < margin <= 120:
            raise ValueError('Ventana horaria fuera de (0, 120] minutos.')
        for direction in (-1, 1):
            moved = deepcopy(request)
            dt = instant(request['timestamp']) + timedelta(minutes=direction * margin)
            moved['timestamp'] = dt.astimezone(ZoneInfo(request['timezone'])).isoformat() if request.get('timezone') else dt.isoformat()
            sig = chart_signature(compute_vedic_chart(moved, baseline['configuration']))
            changed = [k for k in base if sig[k] != base[k]]
            runs.append(dict(axis='BIRTH_TIME', value_minutes=direction*margin, changed_families=changed, stable=not changed))
    return dict(status='IMPLEMENTED', baseline=base, runs=runs,
        ayanamsha_state='AYANAMSHA_SENSITIVE' if any(not r['stable'] for r in runs if r['axis']=='AYANAMSHA') else 'AYANAMSHA_STABLE',
        time_state='SENSITIVE' if any(not r['stable'] for r in runs if r['axis']=='BIRTH_TIME') else 'SAMPLED_STABLE',
        continuous_stability_proven=False, empirical='NOT_PERFORMED')


def benjamini_hochberg(pvalues):
    """q-values monótonos; se requiere independencia/PRDS o método alternativo."""
    if any(isinstance(p,bool) or not isinstance(p,(int,float)) or not isfinite(p) or not 0 <= p <= 1 for p in pvalues):
        raise ValueError('p-values inválidos.')
    order = sorted(range(len(pvalues)), key=pvalues.__getitem__)
    result = [0.] * len(order)
    bound = 1.
    for rank in range(len(order), 0, -1):
        i = order[rank-1]
        bound = min(bound, pvalues[i] * len(order) / rank)
        result[i] = bound
    return result


def descriptive_groups(synastry):
    groups = {}
    for f in synastry['features']:
        item = groups.setdefault(f['redundancy_group'], dict(features=0, matches=0, dependencies=set()))
        item['features'] += 1
        if f['same_sign'] or f['angular_contacts_deg'] or f['same_nakshatra']:
            item['matches'] += 1
            item['dependencies'].add(f['root_dependency_id'])
    return {k: dict(features=v['features'], matches=v['matches'], dependency_bundles=len(v['dependencies']))
            for k,v in groups.items()}


def group_ablation(synastry):
    groups = descriptive_groups(synastry)
    return dict(baseline_features=len(synastry['features']),
        runs=[dict(removed_group=g, remaining_features=len(synastry['features'])-v['features'], canonical_delta=0)
              for g,v in sorted(groups.items())],
        scientific_increment='NOT_EVALUABLE', metric='DESCRIPTIVE_FEATURE_COUNT')


def descriptive_shapley(synastry):
    """Juego unión de bundles: cada bundle compartido se reparte entre sus grupos."""
    ownership = {}
    for f in synastry['features']:
        if f['same_sign'] or f['angular_contacts_deg'] or f['same_nakshatra']:
            ownership.setdefault(f['root_dependency_id'], set()).add(f['redundancy_group'])
    phi = {g:0. for g in descriptive_groups(synastry)}
    for groups in ownership.values():
        for g in groups:
            phi[g] += 1 / len(groups)
    return dict(game='COVERAGE_OF_DEPENDENCY_BUNDLES', values=phi, total=len(ownership),
                interpretive_importance=False, canonical_effect=False)


def validate_corpus(corpus, *, seed=1260):
    """Corpus declarado y controles estratificados; no infiere ground truth espiritual."""
    subjects = corpus['subjects']
    by_id = {s['id']: s for s in subjects}
    if len(by_id) != len(subjects):
        raise ValueError('Sujetos duplicados en el corpus.')
    pairs = corpus['pairs']
    if not pairs or any(len(p) != 2 or p[0] == p[1] or set(p)-set(by_id) for p in pairs):
        raise ValueError('Pares ausentes, autorrelaciones o referencias desconocidas.')
    pair_keys = [tuple(sorted(p)) for p in pairs]
    if len(set(pair_keys)) != len(pairs):
        raise ValueError('Un par repetido no es una observación independiente.')
    cfg = corpus.get('configuration')
    charts = {s['id']: compute_vedic_chart(s['birth'], cfg) for s in subjects}
    observed = []
    for a,b in pairs:
        syn = compute_vedic_synastry(charts[a], charts[b])
        observed.append(dict(pair=[a,b], groups=descriptive_groups(syn), ablation=group_ablation(syn)))
    rng = Random(seed)
    ids = sorted(by_id)
    candidates = [(a,b) for a,b in permutations(ids,2) if a < b and tuple(sorted((a,b))) not in set(pair_keys)
                  and by_id[a].get('stratum') is not None and by_id[a]['stratum'] == by_id[b].get('stratum')]
    rng.shuffle(candidates)
    controls = [dict(pair=[a,b], groups=descriptive_groups(compute_vedic_synastry(charts[a], charts[b])))
                for a,b in candidates[:len(pairs)]]
    return dict(status='CORPUS_DESCRIBED', seed=seed, observed=observed, controls=controls,
        control_state='COMPLETE' if len(controls)==len(pairs) else 'INSUFFICIENT',
        subjects_reused_between_controls=True, observations_independent=False,
        cohort_type=corpus.get('cohort_type','UNDECLARED'), external_validation='NOT_PERFORMED',
        discriminant_capacity='NOT_EVALUABLE', canonical_effect=False)
