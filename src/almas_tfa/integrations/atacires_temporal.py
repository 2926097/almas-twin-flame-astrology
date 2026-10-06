"""Decorador de M26. Feature OFF preserva incluso payload, estado y limitaciones."""
from collections.abc import Mapping
from dataclasses import replace
import os
from ..atacires.adapters import build_uniform_cycle_request
from ..atacires.api import calculate_uniform_cycle
from ..atacires.temporal_signal import to_temporal_signals

FLAG='ALMAS_TEMPORAL_ATACIRES_ENABLED'
MAX_REQUESTS=16
MAX_SIGNALS=10000

def enabled_from_environment():
    value=os.environ.get(FLAG,'false').lower()
    if value not in {'true','false'}:raise ValueError('Feature flag debe ser true o false.')
    return value=='true'

def run_atacires_temporal(context):
    try:
        requests=context.raw_input.get('atacires_requests')
        if not isinstance(requests,list) or not 1<=len(requests)<=MAX_REQUESTS:
            raise ValueError('Se requieren de 1 a 16 solicitudes Atacires.')
        subjects=context.raw_input.get('subjects')
        if not isinstance(subjects,list) or any(not isinstance(s,Mapping) or not s.get('id') for s in subjects):
            raise ValueError('Faltan sujetos canónicos.')
        subjects_by_id={s['id']:s for s in subjects}
        if len(subjects_by_id)!=len(subjects):raise ValueError('Identificadores de sujeto duplicados.')
        natal=context.canonical_snapshot.get('natal')
        charts=natal.get('charts') if isinstance(natal,Mapping) else None
        if not isinstance(charts,Mapping):raise ValueError('Faltan cartas natales canónicas.')
        roots_obj=context.canonical_snapshot.get('independent_roots',{})
        roots=roots_obj.get('roots',[]) if isinstance(roots_obj,Mapping) else []
        calculations=[];signals={}
        for item in requests:
            if not isinstance(item,Mapping) or set(item)!={'subject_id','settings'}:
                raise ValueError('Solicitud Atacires: usar subject_id y settings.')
            subject_id=item['subject_id']
            if not isinstance(subject_id,str) or subject_id not in charts or subject_id not in subjects_by_id:
                raise ValueError('Sujeto/carta no disponible.')
            request=build_uniform_cycle_request(charts[subject_id],subjects_by_id[subject_id],item['settings'])
            result=calculate_uniform_cycle(request);calculations.append(result)
            for signal in to_temporal_signals(result,subject_id,roots):
                signals[signal['signal_id']]=signal
                if len(signals)>MAX_SIGNALS:raise ValueError('Límite agregado de señales excedido.')
        return {'status':'COMPLETED','mode':'SHADOW','scoring_enabled':False,
                'signals':list(signals.values()),'calculations':calculations,'diagnostics':[]}
    except ValueError:
        # No emitir los inputs privados ni mensajes que podrían contener datos natales.
        return {'status':'NOT_EVALUABLE','mode':'SHADOW','scoring_enabled':False,'signals':[],
                'calculations':[],'diagnostics':['ATACIRES_INPUT_NOT_EVALUABLE']}

def make_atacires_temporal_handler(base_handler, *, enabled=None):
    if enabled is not None and type(enabled) is not bool:raise ValueError('enabled debe ser booleano.')
    def handler(context):
        active=enabled_from_environment() if enabled is None else enabled
        baseline=base_handler(context)
        if not active:return baseline
        shadow=run_atacires_temporal(context)
        return replace(baseline,canonical_updates={**baseline.canonical_updates,'atacires_shadow':shadow})
    return handler
