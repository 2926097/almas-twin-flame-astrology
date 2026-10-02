"""Retornos longitudinales; reutiliza el solver de perfecciones de ALMAS."""
from __future__ import annotations
from datetime import datetime, timezone
from math import isfinite
from zoneinfo import ZoneInfo
from .astrology_backend import AstronomyBackendNotEvaluableError
from .temporal_perfection_solver import solve_aspect_perfections


def finite(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(label + ': número finito obligatorio.')
    return float(value)


def instant(value, zone=None):
    """UTC explícito; rechaza horas IANA inexistentes o ambiguas sin offset."""
    dt = datetime.fromisoformat(value.replace('Z', '+00:00')) if isinstance(value, str) else value
    if not isinstance(dt, datetime):
        raise ValueError('Instante ISO-8601 obligatorio.')
    if dt.tzinfo is not None:
        if zone and dt.utcoffset() != dt.astimezone(ZoneInfo(zone)).utcoffset():
            raise ValueError('Offset incompatible con timezone IANA.')
        return dt.astimezone(timezone.utc)
    if not zone:
        raise ValueError('El instante necesita offset o timezone IANA.')
    tz = ZoneInfo(zone)
    valid = set()
    for fold in (0, 1):
        utc = dt.replace(tzinfo=tz, fold=fold).astimezone(timezone.utc)
        if utc.astimezone(tz).replace(tzinfo=None) == dt:
            valid.add(utc)
    if len(valid) != 1:
        raise ValueError('Hora local inexistente o ambigua: aportar offset explícito.')
    return valid.pop()


class ReturnPositionProvider:
    """Cache compartida, sin fallback de cuerpo, motor ni coordenadas."""
    def __init__(self, backend):
        self.backend = backend
        self.cache = {}

    def snapshot(self, when):
        when = instant(when)
        if when not in self.cache:
            calculate = getattr(self.backend, 'calculate_transit_positions', None)
            if not callable(calculate):
                raise AstronomyBackendNotEvaluableError('Backend sin posiciones de tránsito.')
            data = calculate(when)
            if not isinstance(data, dict) or not isinstance(data.get('positions'), dict):
                raise AstronomyBackendNotEvaluableError('Snapshot astronómico incompleto.')
            for key in ('backend_id', 'backend_version', 'backend_provenance'):
                if not data.get(key):
                    raise AstronomyBackendNotEvaluableError('Procedencia del backend incompleta: ' + key)
            self.cache[when] = data
        return self.cache[when]

    def body(self, when, body):
        data = self.snapshot(when)['positions'].get(body)
        if not isinstance(data, dict):
            raise AstronomyBackendNotEvaluableError('Cuerpo no disponible en el backend: ' + body)
        return finite(data.get('longitude'), body + '/longitude') % 360, finite(data.get('speed'), body + '/speed')


def find_all_return_passes(provider, *, body, reference_longitude, start, end, policy):
    target = finite(reference_longitude, 'reference_longitude') % 360
    start, end = instant(start), instant(end)
    if body not in policy['step_hours']:
        step = policy['secondary_step_hours']
    else:
        step = policy['step_hours'][body]
    def evaluate(when):
        return provider.body(when, body)[0], target
    def context(when):
        speed = provider.body(when, body)[1]
        return dict(motion_state='STATIONARY' if abs(speed) <= policy['station_speed_limit'] else 'DIRECT' if speed > 0 else 'RETROGRADE',
                    station_context='NUMERICAL_SPEED', applying_or_separating='EXACT_PERFECTION')
    result = solve_aspect_perfections(evaluate, start=start, end=end, aspect_angle=0,
        technique='RRA', technique_variant='LONGITUDE_RETURN', source_point=body, target_point=body,
        relation='CONJUNCTION', dependency_group='TRANSIT_EPHEMERIS', context_evaluator=context,
        step_seconds=step * 3600, time_tolerance_seconds=policy['time_tolerance_seconds'],
        angular_tolerance_degrees=policy['angular_tolerance_degrees'], max_samples=policy['max_samples'])
    # El solver genérico encuentra candidatos; RRA exige el residual declarado en todos ellos.
    for hit in result['exact_hits']:
        if hit['orb'] > policy['angular_tolerance_degrees']:
            raise AstronomyBackendNotEvaluableError('Un candidato no satisface la tolerancia astronómica RRA.')
    return result


def find_exact_return(provider, **kwargs):
    """Primer retorno en la ventana; el motor conserva siempre la búsqueda completa."""
    hits = find_all_return_passes(provider, **kwargs)['exact_hits']
    return hits[0] if hits else None


def resolve_return_location(location):
    allowed = {'birth_location', 'residence_location', 'actual_return_location', 'event_location', 'unknown'}
    if not isinstance(location, dict) or location.get('basis') not in allowed:
        raise ValueError('Base geográfica RRA explícita obligatoria.')
    if location['basis'] == 'unknown':
        return None
    if not location.get('source_ref'):
        raise ValueError('Ubicación de retorno sin fuente.')
    latitude = finite(location.get('latitude'), 'latitude')
    longitude = finite(location.get('longitude'), 'longitude')
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError('Coordenadas fuera de rango.')
    return latitude, longitude


def build_return_chart(provider, when, location, *, angular_reliability):
    snapshot = provider.snapshot(when)
    result = dict(positions=snapshot['positions'], angles={}, angular_status='BLOCKED',
        location_basis=location['basis'], backend_id=snapshot['backend_id'], backend_version=snapshot['backend_version'],
        backend_provenance=snapshot['backend_provenance'])
    coords = resolve_return_location(location)
    if coords is not None and angular_reliability is True:
        calculate = getattr(provider.backend, 'calculate_return_chart', None)
        if not callable(calculate):
            result['angular_reason'] = 'BACKEND_RETURN_CHART_CAPABILITY_MISSING'
        else:
            chart = calculate(instant(when), latitude=coords[0], longitude=coords[1])
            for key in ('positions', 'angles', 'backend_provenance'):
                if not isinstance(chart.get(key), dict):
                    raise AstronomyBackendNotEvaluableError('Carta de retorno incompleta: ' + key)
            for point, value in chart['angles'].items():
                finite(value.get('longitude') if isinstance(value, dict) else value, 'angle/' + point)
            # Retorno y carta usan idéntico backend y reducción astronómica.
            if chart.get('backend_id') != snapshot['backend_id'] or chart.get('backend_version') != snapshot['backend_version'] or chart['backend_provenance'] != snapshot['backend_provenance']:
                raise AstronomyBackendNotEvaluableError('Carta y retorno tienen procedencias diferentes.')
            result.update(positions=chart['positions'], angles=chart['angles'], angular_status='CALCULATED',
                          houses=chart.get('houses', {}))
    return result
