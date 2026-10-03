"""Endpoint externo candidato RRA: descriptivo, con denominadores explícitos."""
from collections import defaultdict
from copy import deepcopy
from datetime import timedelta
from statistics import mean

from .return_activation import (calculate_event_delta, digest,
                                load_return_policy, validate_return_activation)
from .return_solver import instant


def exact_date_indicator(result, event):
    """Un voto por fecha; desconocido no se convierte en resultado negativo."""
    policy = load_return_policy()
    if result['execution_status'] != 'executed' or not result['coverage']:
        return dict(indicator=None, reason='INCOMPLETE_EXECUTION', return_refs=[])
    if any(c['layer'] == 'EVENT' for c in result['evaluation_input']['charts']):
        return dict(indicator=None, reason='EVENT_REFERENCE_EXCLUDED', return_refs=[])
    if not event.get('event_datetime') or not event.get('source_refs') or event.get('certainty') == 'UNKNOWN':
        return dict(indicator=None, reason='DATE_OR_PROVENANCE_MISSING', return_refs=[])
    uncertainty = event['uncertainty_hours']
    if isinstance(uncertainty, bool) or not isinstance(uncertainty, (int, float)) or not 0 <= uncertainty < float('inf'):
        raise ValueError('Incertidumbre de fecha inválida.')
    if not event['occurred']:
        return dict(indicator=None, reason='FUTURE_EVENT', return_refs=[])
    when = instant(event['event_datetime'], event.get('timezone'))
    # Cobertura de todo el universo, incluso cuando no hay retornos encontrados.
    for clock in result['evaluation_input']['clocks']:
        if (when - timedelta(hours=uncertainty) < instant(clock['start']) or
                when + timedelta(hours=uncertainty) > instant(clock['end'])):
            return dict(indicator=None, reason='OUTSIDE_COMMON_COVERAGE', return_refs=[])
    hits = []; ambiguous = False
    for record in result['returns']:
        if not any(not c['automatic_identity_contact'] for c in record['contacts']):
            continue
        relation = calculate_event_delta(record, event, policy)
        if relation['status'] == 'SUPPORTED': hits.append(record['return_id'])
        elif relation['status'] == 'NOT_EVALUABLE': ambiguous = True
    if hits:
        return dict(indicator=1, reason='EXACT_NON_TAUTOLOGICAL_CONTACT', return_refs=sorted(hits))
    return dict(indicator=None if ambiguous else 0,
                reason='WINDOW_BOUNDARY_UNCERTAINTY' if ambiguous else 'NO_EXACT_ACTIVATION', return_refs=[])


def evaluate_study(study, results):
    """Mismos cálculos para fechas evento/control; no ejecuta inferencia confirmatoria."""
    if study.get('mode') not in {'SYNTHETIC_TEST_ONLY', 'DESCRIPTIVE_ONLY'}:
        raise ValueError('El runner candidato no habilita modo confirmatorio.')
    cases = study['cases']
    if not cases or len({c['case_id'] for c in cases}) != len(cases):
        raise ValueError('Casos ausentes o duplicados.')
    people_partition = {}; components = {}; fact_owners = {}; output = []
    for case in cases:
        people = case['person_refs']
        if len(set(people)) != 2 or len(people) != 2:
            raise ValueError('Cada vínculo requiere dos personas distintas.')
        for person in people:
            if person in people_partition and people_partition[person] != case['component_id']:
                raise ValueError('Persona compartida en componentes distintos.')
            people_partition[person] = case['component_id']
        if case['case_id'] not in results:
            raise ValueError('Falta un resultado RRA del caso.')
        result = results[case['case_id']]
        validate_return_activation(result)
        if digest(result) != case['execution_sha256']:
            raise ValueError('Ejecución RRA distinta del snapshot declarado.')
        if result['return_policy_hash'] != study['return_policy_hash']:
            raise ValueError('Políticas distintas dentro del estudio.')
        counts = {kind: dict(total=0, evaluable=0, positive=0, missing=0) for kind in ('EVENT', 'CONTROL')}
        dates = []; seen_dates = set(); seen_facts = set()
        ids = [o['observation_id'] for o in case['observations']]
        if len(ids) != len(set(ids)):
            raise ValueError('Identificador de observación duplicado.')
        for observation in case['observations']:
            kind = observation['kind']
            if kind not in counts:
                raise ValueError('Tipo de observación desconocido.')
            if not observation.get('coverage_refs') or not observation.get('selection_stratum'):
                raise ValueError('La fecha requiere cobertura y estrato documental explícitos.')
            event = deepcopy(observation['date_input'])
            key = event['fact_key']
            if key in seen_facts or (key in fact_owners and fact_owners[key] != case['case_id']):
                raise ValueError('Hecho documental duplicado dentro o entre vínculos.')
            seen_facts.add(key); fact_owners[key] = case['case_id']
            if event.get('event_datetime'):
                timestamp = instant(event['event_datetime'], event.get('timezone')).isoformat()
                if timestamp in seen_dates:
                    raise ValueError('Fecha repetida o compartida entre evento y control.')
                seen_dates.add(timestamp)
            if kind == 'CONTROL':
                # Proxy técnico para consultar una fecha; no afirma acontecimiento real.
                event['occurred'] = True
            measured = exact_date_indicator(result, event)
            counts[kind]['total'] += 1
            if measured['indicator'] is None: counts[kind]['missing'] += 1
            else:
                counts[kind]['evaluable'] += 1
                counts[kind]['positive'] += measured['indicator']
            dates.append(dict(observation_id=observation['observation_id'], kind=kind, **measured))
        for count in counts.values():
            count['rate'] = count['positive'] / count['evaluable'] if count['evaluable'] else None
        difference = (counts['EVENT']['rate'] - counts['CONTROL']['rate']
                      if all(counts[k]['rate'] is not None for k in counts) else None)
        components.setdefault(case['component_id'], []).append(difference)
        output.append(dict(case_id=case['case_id'], component_id=case['component_id'],
                           counts=counts, difference=difference, observations=dates))
    aggregates = []
    for component, values in sorted(components.items()):
        eligible = [v for v in values if v is not None]
        aggregates.append(dict(component_id=component, total_cases=len(values),
                               evaluable_cases=len(eligible),
                               difference=mean(eligible) if eligible else None))
    eligible = [a['difference'] for a in aggregates if a['difference'] is not None]
    return dict(schema_version='rra-external-descriptive-0.1', study_hash=digest(study),
                mode=study['mode'], cases=output, components=aggregates,
                total_components=len(aggregates), evaluable_components=len(eligible),
                primary_difference=mean(eligible) if eligible else None,
                aggregation='EQUAL_CASE_WEIGHT_WITHIN_COMPONENT_THEN_EQUAL_COMPONENT_WEIGHT',
                missingness_rule='EXCLUDE_UNEVALUABLE_KEEP_DENOMINATORS',
                confirmatory_inference_allowed=False, p_value=None,
                external_validation_status='NOT_PERFORMED', ontology_effect='NONE',
                provenance_authenticated=False, exchangeability_established=False,
                runner_scope='CANDIDATE_ENDPOINT_DESCRIPTIVE_ONLY')
