#!/usr/bin/env python3
"""Comprueba coherencia del piloto RRA 0.1; no autentica fuentes ni admite una cohorte."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'initial': 'validation/returns/documentary-feasibility-screen.json',
    'archival': 'validation/returns/archival-feasibility-screen.json',
    'coverage': 'validation/returns/documentary-coverage-inventory.json',
    'readiness': 'validation/returns/external-validation-readiness.json',
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_bundle(bundle: dict, root: Path | None = None) -> None:
    """Contrato del piloto documental actual, independiente de la política del motor."""
    first, archive, coverage, ready = (bundle[k] for k in FILES)
    cases = first['pilot_candidates'] + archive['pilot_candidates']
    ids = [c['id'] for c in cases]
    require(len(set(ids)) == len(ids), 'Identificador de vínculo duplicado')
    known = set(ids)
    history = archive.get('replacement_history', [])
    require(history == coverage.get('replacement_history', []) == ready.get('replacement_history', []),
            'Historial de sustituciones divergente')
    for replacement in history:
        require(replacement['retired_candidate_id'] not in known, 'Candidato retirado reintroducido')
        require(replacement['replacement_candidate_id'] in known, 'Sustituto ausente del piloto')
        require(replacement['retired_holdout_eligible'] is False and replacement['astrological_results_seen'] is False,
                'Sustitución incompatible con exclusión del holdout o selección documental')
    require(set(ready.get('retired_pilot_candidate_ids', [])) ==
            {h['retired_candidate_id'] for h in history}, 'Registro de retirados incoherente')
    for panel in (first, archive):
        require(panel['status'] == 'DOCUMENTARY_PILOT_ONLY', 'Estado del piloto alterado')
        require(panel['candidate_count'] == len(panel['pilot_candidates']), 'Recuento de vínculos incorrecto')
        sources = {s['id'] for s in panel['source_registry']}
        require(len(sources) == len(panel['source_registry']), 'Identificador de fuente duplicado')
        for case in panel['pilot_candidates']:
            require(case['holdout_eligible'] is False and case['confirmatory_admission'] is False,
                    'El piloto no puede admitir vínculos al holdout')
            require(case['status'] == 'SCREENED_PILOT_ONLY', 'Estado del vínculo alterado')
            require(set(case['source_refs']) <= sources, 'Referencia documental inexistente')
            for event in case.get('events', []):
                require(set(event['source_refs']) <= sources, 'Fuente del acontecimiento inexistente')
                require(event.get('utc_instant') is None and event.get('local_time') is None,
                        'Instante exacto no acreditado en este piloto')
        require(panel['charts_computed'] is False and panel['returns_computed'] is False,
                'El cribado no puede declarar cálculos astrológicos')
    # Reconstruir componentes desde personas compartidas; no confiar sólo en etiquetas.
    groups: list[set[str]] = []
    for case in cases:
        members = set(case['person_refs'])
        require(len(members) == 2, 'Un vínculo necesita dos personas distintas')
        joined = [g for g in groups if g & members]
        for group in joined:
            members |= group
            groups.remove(group)
        groups.append(members)
    labels = {}
    for case in cases:
        component = next(i for i, g in enumerate(groups) if set(case['person_refs']) <= g)
        labels.setdefault(component, set()).add(case['person_component'])
    require(all(len(v) == 1 for v in labels.values()), 'Una persona compartida cruza componentes')
    require(len({next(iter(v)) for v in labels.values()}) == len(groups), 'Componentes distintos fusionados por etiqueta')
    require(ready['pilot_candidate_count'] == len(cases), 'Acumulado de vínculos incorrecto')
    require(ready['pilot_distinct_person_count'] == len(set().union(*groups)), 'Acumulado de personas incorrecto')
    require(ready['pilot_person_graph_components'] == len(groups), 'Acumulado de componentes incorrecto')
    units = coverage['units']
    unit_ids = [u['unit_id'] for u in units]
    require(len(unit_ids) == len(set(unit_ids)) == coverage['unit_count'], 'Recuento o duplicado de unidades')
    require(set(coverage['candidate_ids']) == {u['candidate_id'] for u in units}, 'Cobertura por vínculo incoherente')
    require(set(coverage['candidate_ids']) <= known, 'Vínculo del inventario inexistente')
    require(coverage['status'] == 'PARTIAL_INVENTORY_NOT_CONTROL_READY', 'Estado de cobertura alterado')
    require(coverage['exhaustive_inventory'] is False, 'No se ha acreditado inventario exhaustivo')
    for unit in units:
        url = urlparse(unit['source_url'])
        require(url.scheme in ('http', 'https') and bool(url.netloc), 'Localizador documental inválido')
        require(unit['control_eligible'] is False and unit['negative_observation_supported'] is False,
                'Control negativo sin cobertura acreditada')
    require(coverage['original_manuscripts_read'] == sum(u['original_manuscript_read'] is True for u in units),
            'Recuento de originales leídos incoherente')
    require(coverage['published_primary_transcription_passages_read'] == sum(
        u['unit_type'] == 'PRIMARY_PUBLISHED_TESTIMONY_TRANSCRIPTION' and
        u['access_status'].startswith('PAGINATED_TRANSCRIPTION_READ') for u in units),
        'Recuento de pasajes leídos incoherente')
    # Toda divergencia de fechas debe figurar con sus afirmaciones y no resolverse implícitamente.
    claims = {}
    for unit in units:
        for claim in unit['fact_claims']:
            claims.setdefault(claim['fact_key'], []).append((unit['unit_id'], claim['date_assertion']))
    conflicts = {c['fact_key']: c for c in coverage['event_conflicts']}
    require(len(conflicts) == len(coverage['event_conflicts']), 'Conflicto duplicado')
    for key, entries in claims.items():
        dates = {d for _, d in entries}
        if len(dates) > 1:
            require(key in conflicts, 'Discrepancia de fechas no registrada')
    for case in archive['pilot_candidates']:
        for event in case['events']:
            if event.get('alternative_date_assertions'):
                require(event['fact_key'] in conflicts, 'Alternativas del piloto sin registro de conflicto')
    for key, conflict in conflicts.items():
        require(key in claims, 'Conflicto sin afirmaciones documentales')
        entries = claims[key]
        require(set(conflict['asserted_dates']) == {d for _, d in entries}, 'Se ha perdido una fecha en conflicto')
        require(set(conflict['unit_refs']) == {u for u, _ in entries}, 'Referencia del conflicto incoherente')
        require(conflict['resolved_event_date'] is None and conflict['status'] == 'EVENT_DATE_CONFLICT_PENDING_ADJUDICATION',
                'Resolución de fecha sin adjudicación documental')
        events = [e for c in archive['pilot_candidates'] for e in c['events'] if e['fact_key'] == key]
        require(len(events) == 1, 'El mismo hecho conflictivo se ha duplicado o eliminado')
        require(events[0].get('resolved_event_date') is None and
                events[0].get('adjudication_status') == conflict['status'], 'Piloto y conflicto divergen')
        event_dates = {events[0]['date_assertion']} | {a['date'] for a in events[0]['alternative_date_assertions']}
        require(event_dates == set(conflict['asserted_dates']), 'El piloto ha perdido una afirmación alternativa')
    require(ready['documentary_event_conflicts_pending'] == len(conflicts), 'Recuento de conflictos incoherente')
    for state in (coverage, ready):
        require(state['confirmatory_execution_allowed'] is False and state['holdout_opened'] is False,
                'La coherencia documental no autoriza ejecución confirmatoria')
        require(state['negative_observation_periods_verified'] == 0, 'Observación negativa no acreditada')
        require(state['external_validation_status'] == 'NOT_PERFORMED', 'Validación externa no ejecutada')
    require(coverage['controls_admitted'] == [] and ready['real_cases'] == [], 'Admisión no autorizada por este contrato')
    require(ready['engine_policy_modified'] is False and ready['runner_status'] == 'NOT_IMPLEMENTED',
            'El validador documental no sustituye al runner externo')
    if root is not None:
        for path in [coverage['report_path'], ready['protocol_path'], ready['documentary_coverage_inventory']]:
            resolved = (root / path).resolve()
            require(resolved.is_relative_to(root.resolve()) and resolved.is_file(), 'Archivo de procedencia inexistente o fuera del repositorio')


def load_bundle(root: Path) -> dict:
    return {key: json.loads((root / path).read_text(encoding='utf-8')) for key, path in FILES.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        validate_bundle(load_bundle(args.root), args.root)
    except (ValueError, KeyError, TypeError, OSError, StopIteration) as error:
        print(f'Validación documental RRA: FAIL — {error}')
        return 1
    print('Validación documental RRA: PASS — coherencia del piloto; eficacia y fuentes no autenticadas')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
