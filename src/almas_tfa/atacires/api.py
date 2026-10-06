"""API interna temporal: ciclos uniformes sin efemérides, red ni puntuación."""
from datetime import datetime,timezone
from .engine import calculate, InputError, utc_datetime, iso
from .models import UniformCycleRequest
from .provenance import fingerprint_payload

ENGINE_REVISION='ALMAS_UNIFORM_CYCLE_1'
UPSTREAM_SHA='d0d3a4bcf315708a4bf6f7e40cf2873732819b61'
MAX_COMBINATIONS=40000

def calculate_uniform_cycle(request: UniformCycleRequest, *, executed_at=None):
    if not isinstance(request,UniformCycleRequest):raise ValueError('Usar solicitud del adaptador canónico.')
    data=request.engine_payload();source=request.source()
    try:
        # Límite de trabajo independiente del límite de eventos del algoritmo.
        if isinstance(data.get('promissors'),list) and isinstance(data.get('significators'),list) and isinstance(data.get('aspects_deg'),list):
            if len(data['promissors'])*len(data['significators'])*len(data['aspects_deg'])*2 > MAX_COMBINATIONS:
                raise InputError('WORK_LIMIT_EXCEEDED','Reducir selectores o aspectos.')
        out=calculate(data)
    except OverflowError as exc:
        raise InputError('DATETIME_RANGE_EXCEEDED','La ventana excede el intervalo datetime.') from exc
    events=[{'source_point':h['promissor'],'target_point':h['significator'],
             'aspect_deg':h['aspect_deg'],'oriented_aspect_deg':h['oriented_aspect_deg'],
             'exact_datetime':h['date_exact_utc'],'exact_datetime_local':h['date_exact_local'],
             'angular_residual_deg':h['angular_residual_deg'],
             'window_start_utc':h['window_start_utc'],'window_end_utc':h['window_end_utc'],
             'window_half_days':h['window_half_days']} for h in out['hits']]
    result={'technique_family':'TATACIR','technique':'UNIFORM_CYCLE','events':events,
            'calculation':out['calculation'],'directed_positions_start':out['directed_positions_start'],
            'directed_positions_end':out['directed_positions_end'],'warnings':out['warnings']}
    effective={**data,**out['input'],**out['calculation'],
               'promissors':sorted(set(data['promissors'])),
               'significators':sorted(set(data['significators']))}
    provenance={**source,'technique_id':'UNIFORM_CYCLE','technique_version':out['engine_version'],
                'engine_revision':ENGINE_REVISION,'upstream_commit':UPSTREAM_SHA,
                'parameters':out['calculation'],'timescale':out['calculation']['timescale'],
                'ephemeris_used':False,'input_fingerprint':fingerprint_payload({'request':effective,'source':source}),
                'output_fingerprint':fingerprint_payload(result),
                'executed_at':iso(utc_datetime(executed_at,'executed_at')) if executed_at is not None else iso(datetime.now(timezone.utc))}
    return {**result,'provenance':provenance}
