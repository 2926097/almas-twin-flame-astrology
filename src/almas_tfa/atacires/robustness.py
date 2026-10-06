"""Compara muestras ya recalculadas; no inventa efemérides perturbadas ni probabilidades."""
from math import isfinite
from .engine import utc_datetime

def assess_robustness(samples, *, max_spread_seconds, sampling_ref, exact_time=False):
    if not isinstance(samples,list) or not 1<=len(samples)<=1000:
        raise ValueError('Se requieren entre 1 y 1000 muestras explícitas.')
    if not isinstance(sampling_ref,str) or not sampling_ref.strip():raise ValueError('Falta regla de muestreo registrada.')
    if isinstance(max_spread_seconds,bool) or not isinstance(max_spread_seconds,(int,float)) or not isfinite(max_spread_seconds) or max_spread_seconds<0:
        raise ValueError('Umbral finito no negativo obligatorio.')
    if type(exact_time) is not bool or (exact_time and len(samples)!=1):raise ValueError('Hora exacta requiere una sola muestra.')
    signatures=[];times=[]
    for sample in samples:
        events=sample['events']
        signatures.append([(e['source_point'],e['target_point'],e['aspect_deg'],e['oriented_aspect_deg']) for e in events])
        times.append([utc_datetime(e['exact_datetime'],'exact_datetime') for e in events])
    matching=all(s==signatures[0] for s in signatures)
    spread=max(((max(t[i] for t in times)-min(t[i] for t in times)).total_seconds()
                for i in range(len(signatures[0]))),default=0.) if matching else None
    classification=('NOT_EVALUABLE' if not any(signatures) or (len(samples)==1 and not exact_time) else 'EXACT_INPUT' if exact_time else 'SENSITIVE' if not matching or spread>max_spread_seconds else 'ROBUST')
    return {'classification':classification,'sample_count':len(samples),'contact_presence_stable':matching,
            'maximum_spread_seconds':spread,'threshold_seconds':max_spread_seconds,
            'sampling_ref':sampling_ref,'metaphysical_probability':None,
            'scope':'SUPPLIED_RECALCULATED_SAMPLES_ONLY'}
