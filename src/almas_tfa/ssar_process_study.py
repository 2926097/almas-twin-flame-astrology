"""Contratos documentales para futuros estudios, sin integración M27/SSAR."""
from __future__ import annotations

from datetime import date
from hashlib import sha256
from importlib import resources
import json
from typing import Mapping

from .ssar import _index, assess_ssar_claim, validate_ssar_schema


def load_process_study_policy() -> dict:
    return json.loads(resources.files('almas_tfa').joinpath('data', 'ssar-process-study-development-policy.json').read_text(encoding='utf-8'))


def _date(value: str) -> date:
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError('La fecha de estudio exige ISO YYYY-MM-DD.')
    return parsed


def _admissible(event: Mapping) -> bool:
    return (event['verification_status'] == 'VERIFIED' and event['precision_sufficient'] is True
            and event['data_class'] in {'DOCUMENT', 'OBSERVATION'}
            and bool(event['source_refs']) and event['fact_interpretation_separated'] is True
            and event['start_date'] is not None
            and (event['role'] != 'DURATION_INTERVAL' or event['end_date'] is not None and event['continuity_observed'] is True)
            and (event['role'] != 'TRANSITION_EVENT' or bool(event['from_state']) and bool(event['to_state'])
                 and event['from_state'] != event['to_state']))


def _facts(events: list[dict]) -> list[dict]:
    _index(events, 'event_id')
    groups = {}
    for event in events:
        start = _date(event['start_date']) if event['start_date'] else None
        end = _date(event['end_date']) if event['end_date'] else None
        if end is not None and (start is None or end < start):
            raise ValueError('Intervalo de evento inválido.')
        if event['role'] != 'DURATION_INTERVAL' and end is not None and end != start:
            raise ValueError('Un hito requiere fecha puntual; la duración utiliza intervalo.')
        groups.setdefault(event['fact_key'], []).append(event)
    fields = ('episode_id', 'subject_id', 'role', 'start_date', 'end_date', 'continuity_observed', 'from_state', 'to_state')
    output = []
    for key, records in sorted(groups.items()):
        signatures = {tuple(record[field] for field in fields) for record in records}
        conflict = len(signatures) != 1
        admitted = sorted(record['event_id'] for record in records if _admissible(record))
        output.append(dict(fact_key=key, event_refs=sorted(r['event_id'] for r in records), conflict=conflict,
                           admissible_event_ref=admitted[0] if admitted and not conflict else None))
    return output


def _claim(claim: Mapping, registry: Mapping, facts: list[dict], policy: Mapping) -> dict:
    start, end, as_of = (_date(claim[key]) for key in ('window_start', 'window_end', 'as_of'))
    if end < start:
        raise ValueError('Ventana documental invertida.')
    if set(claim['event_refs']) - set(registry):
        raise ValueError('Referencia documental rota.')
    for ref in claim['event_refs']:
        event = registry[ref]
        if event['episode_id'] != claim['episode_id'] or event['subject_id'] != claim['subject_id']:
            raise ValueError('Un estudio no mezcla episodios o sujetos.')
    kind, bounds = claim['kind'], (claim['minimum_days'], claim['maximum_days'])
    if kind != 'DURATION_WITHIN_BOUNDS' and bounds != (None, None):
        raise ValueError('Los límites de duración sólo se aplican a su afirmación.')
    if None not in bounds and bounds[1] < bounds[0]:
        raise ValueError('Límites de duración invertidos.')
    rule = policy['claims'][kind]
    # El registro es el universo observado: omitir un ref no oculta un contradicto conocido.
    keys = {registry[ref]['fact_key'] for ref in claim['event_refs']} | {
        event['fact_key'] for event in registry.values()
        if event['episode_id'] == claim['episode_id'] and event['subject_id'] == claim['subject_id']
        and event['role'] in {rule['event_role'], rule['counter_role']}}
    selected = [fact for fact in facts if fact['fact_key'] in keys]
    unresolved, known = [], []
    for fact in selected:
        event = registry[fact['admissible_event_ref']] if fact['admissible_event_ref'] else None
        if event is None:
            # Un registro sin fecha/precisión no prueba ausencia en la ventana.
            records = [registry[ref] for ref in fact['event_refs']]
            relevant = [r for r in records if r['role'] in {rule['event_role'], rule['counter_role']}]
            if any(r['start_date'] is None or start <= _date(r['start_date']) <= end for r in relevant):
                unresolved.append(fact['fact_key'])
            continue
        a = _date(event['start_date']); b = _date(event['end_date']) if event['end_date'] else a
        if start <= a <= b <= end and b <= as_of:
            known.append(event)
    target = [event for event in known if event['role'] == rule['event_role']]
    counter = [event for event in known if event['role'] == rule['counter_role']]
    positives, negatives, duration, mixed = [], [], None, False
    closed = as_of >= end
    complete = claim['observation_coverage_complete'] and closed and not unresolved
    sufficient = False
    if kind == 'DURATION_WITHIN_BOUNDS':
        lengths = {(_date(e['end_date']) - _date(e['start_date'])).days for e in target}
        if len(lengths) > 1:
            sufficient, mixed = True, True
        elif lengths and None not in bounds:
            duration = next(iter(lengths)); sufficient = True
            refs = [e['event_id'] for e in target]
            if bounds[0] <= duration <= bounds[1]: positives = refs
            else: negatives = refs
    elif kind == 'CLOSURE_PERSISTED_IN_WINDOW':
        for reopened in counter:
            if any(_date(e['start_date']) < _date(reopened['start_date']) for e in target):
                negatives.append(reopened['event_id'])
        positives = [e['event_id'] for e in target] if complete and not negatives else []
        sufficient = bool(negatives or complete)
    elif kind == 'DISCORD_FREE_WINDOW':
        negatives = [e['event_id'] for e in counter]
        sufficient = bool(negatives or complete)
        if complete and not negatives: positives = [claim['id'] + ':observation_coverage']
    else:
        positives = [e['event_id'] for e in target]
        sufficient = bool(positives or complete)
    # Ausencia sólo después de una ventana terminada y observada completamente.
    if complete and not target and kind != 'DISCORD_FREE_WINDOW':
        negatives.append(claim['id'] + ':observation_coverage')
    if unresolved and not negatives:
        sufficient = False
    if kind == 'DURATION_WITHIN_BOUNDS' and None in bounds:
        sufficient, positives, negatives, mixed = False, [], [], False
    if not claim['preregistered_before_chart_inspection']:
        sufficient, positives, negatives, mixed = False, [], [], False
    assessment = assess_ssar_claim(scope='DOCUMENTARY_PROCESS_STUDY:' + kind, policy_ref=policy['policy_id'],
                                  rule_ref=rule['rule_id'], coverage_sufficient=sufficient,
                                  positive_complete=bool(positives) and not mixed,
                                  mixed_or_underdetermined=mixed,
                                  evidence_refs=[e['event_id'] for e in target] + positives,
                                  excluding_counterevidence_refs=negatives,
                                  counterevidence_evaluable=bool(negatives))
    return dict(id=claim['id'], assessment=assessment, supporting_event_refs=sorted(set(positives)),
                contradicting_event_refs=sorted(set(negatives)), unresolved_fact_keys=sorted(unresolved),
                duration_days=duration, window_closed=closed)


def run_process_study(request: Mapping) -> dict:
    """Comprueba datos declarados; no verifica documentos ni recibe cartas o complejos."""
    validate_ssar_schema(request, 'ProcessStudyRequest')
    policy = load_process_study_policy()
    encoded = json.dumps(policy, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    registry = _index(request['events'], 'event_id')
    _index(request['claims'], 'id')
    facts = _facts(request['events'])
    output = dict(schema_version='ssar-process-study-1.0-development', policy_id=policy['policy_id'],
                  policy_status='DEVELOPMENT', epistemic_class='E_PROJECT_HYPOTHESIS', external_validation_status='NOT_PERFORMED',
                  policy_hash=sha256(encoded.encode('utf-8')).hexdigest(), integration_status=policy['integration_status'],
                  facts=facts, claims=[_claim(claim, registry, facts, policy) for claim in sorted(request['claims'], key=lambda c: c['id'])],
                  astrological_effect='NONE', documentary_correspondence_effect='NONE', ontology_effect='NONE')
    validate_ssar_schema(output, 'ProcessStudyResult')
    return output


def validate_process_study_result(result: Mapping, *, request: Mapping) -> None:
    validate_ssar_schema(result, 'ProcessStudyResult')
    if result != run_process_study(request):
        raise ValueError('El estudio documental no reproduce sus registros y política.')
