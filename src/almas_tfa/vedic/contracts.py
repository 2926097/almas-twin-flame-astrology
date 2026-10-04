"""Packaged VED boundary validation; no optional silent weakening."""
from importlib import resources
import json
from math import isfinite
from collections.abc import Mapping

from .chart import settings
from .synastry import _fingerprint, _objects
from .timing import instant
from .geometry import sign_of


def _finite(value):
    if isinstance(value, float) and not isfinite(value):
        raise ValueError('VED no admite números no finitos.')
    if isinstance(value, Mapping):
        for item in value.values():
            _finite(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _finite(item)


def validate_vedic_envelope(envelope):
    """Validate schema, references, totals and the observational firewall."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise RuntimeError('VED requiere el extra schema-validation para validar envolventes.') from exc
    schema = json.loads(resources.files('almas_tfa').joinpath('data', 'vedic-envelope-schema.json').read_text(encoding='utf-8'))
    _finite(envelope)
    errors = sorted(Draft202012Validator(schema).iter_errors(envelope), key=lambda e: str(e.path))
    if errors:
        error = errors[0]
        path = '.'.join(map(str, error.absolute_path)) or '<root>'
        raise ValueError(f'Envolvente VED inválida en {path}: {error.message}')
    try:
        _validate_consistency(envelope)
    except (KeyError, TypeError, IndexError) as exc:
        raise ValueError(f'Contenido VED incompleto o mal tipado: {exc}') from exc
    return envelope


def _validate_consistency(e):
    ready = e['temporal_readiness']
    events = e['events']
    if ready['events_requested'] != len(events) or ready['status'] != ('DESCRIPTIVE_ONLY' if events else 'NOT_RUN'):
        raise ValueError('Estado temporal VED no coincide con los eventos.')
    if not e['enabled']:
        if events or e['annual'] or e['sensitivity'] or e['ablation'] is not None or e['shapley'] is not None:
            raise ValueError('Una envolvente desactivada no puede contener resultados activos.')
        if ready['vimshottari_subject_results'] or ready['transit_events']:
            raise ValueError('Una envolvente desactivada no puede declarar resultados temporales.')
        return
    a, b = e['charts']
    for chart in (a, b):
        if settings(chart['configuration']) != chart['configuration']:
            raise ValueError('Configuración VED incompleta.')
        for layer in ('D1', 'D9'):
            for point in _objects(chart, layer).values():
                sign = point['sign']
                if isinstance(sign, bool) or not isinstance(sign, int) or not 0 <= sign < 12:
                    raise ValueError('Signo VED mal tipado o fuera de rango.')
                lon = point['longitude']
                if lon is not None and (isinstance(lon, bool) or not isinstance(lon, (int, float)) or not 0 <= lon < 360 or sign_of(lon) != sign):
                    raise ValueError('Longitud VED inválida o incoherente con su signo.')
    syn = e['synastry']
    if a['configuration'] != b['configuration'] or syn['configuration'] != a['configuration']:
        raise ValueError('Configuraciones VED incoherentes.')
    if syn['chart_hashes'] != [_fingerprint(a), _fingerprint(b)]:
        raise ValueError('La sinastría VED no corresponde a las cartas.')
    features = syn['features']
    refs = {f['feature_id'] for f in features}
    bundles = {f['root_dependency_id'] for f in features}
    if len(refs) != len(features):
        raise ValueError('IDs de features VED duplicados.')
    for f in features:
        for chart, suffix in ((a, 'a'), (b, 'b')):
            if f['object_' + suffix] not in _objects(chart, f['varga_' + suffix]):
                raise ValueError('Endpoint VED desconocido.')
    matched = [f for f in features if f['same_sign'] or f['angular_contacts_deg'] or f['same_nakshatra']]
    counts = syn['methodological_readiness']['descriptive']
    expected = (len(features), len(matched), len({f['root_dependency_id'] for f in matched}))
    actual = tuple(counts[k] for k in ('feature_count', 'match_count', 'dependency_bundle_count'))
    if expected != actual or syn['recurrence']['raw_matches'] != expected[1] or syn['recurrence']['dependency_bundles'] != expected[2]:
        raise ValueError('Recuentos descriptivos VED incoherentes.')
    ids = [event['event_id'] for event in events]
    if len(set(ids)) != len(ids):
        raise ValueError('IDs de eventos VED duplicados.')
    dasha_count = transit_count = 0
    for event in events:
        at = instant(event['event_timestamp'])
        labels = [p['person'] for p in event['persons']]
        if set(labels) != {'A', 'B'} or len(labels) != 2:
            raise ValueError('El evento debe contener exactamente los dos sujetos VED.')
        for person in event['persons']:
            if person['status'] == 'IMPLEMENTED':
                dasha_count += 1
                intervals = []
                for level in ('maha', 'antara', 'pratyantara'):
                    period = person['periods'][level]
                    start, end = instant(period['start']), instant(period['end'])
                    if not start <= at < end:
                        raise ValueError('Período VED no contiene el instante de evento.')
                    intervals.append((start, end))
                if not all(x[0] <= y[0] < y[1] <= x[1] for x, y in zip(intervals, intervals[1:])):
                    raise ValueError('Los períodos VED deben estar anidados.')
        transit_count += event['transit_status'] == 'IMPLEMENTED'
        if event['transit_status'] == 'NOT_PERFORMED' and event['transit_contacts']:
            raise ValueError('Contactos de tránsito sin evaluación temporal.')
        for contact in event['transit_contacts']:
            if not contact['structural_feature_refs'] or set(contact['structural_feature_refs']) - refs:
                raise ValueError('Referencias estructurales VED no resolubles.')
            if not contact['root_dependency_refs'] or set(contact['root_dependency_refs']) - bundles:
                raise ValueError('Referencias de dependencia VED no resolubles.')
    if ready['vimshottari_subject_results'] != dasha_count or ready['transit_events'] != transit_count:
        raise ValueError('Recuentos temporales VED incoherentes.')
