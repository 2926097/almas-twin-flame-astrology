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
    contacts=[]
    for sample in samples:
        grouped={}
        for event in sample['events']:
            signature=(event['source_point'],event['target_point'],event['aspect_deg'],event['oriented_aspect_deg'])
            grouped.setdefault(signature,[]).append(utc_datetime(event['exact_datetime'],'exact_datetime'))
        contacts.append({(signature,index):instant for signature,instants in grouped.items()
                         for index,instant in enumerate(sorted(instants))})
    keys=set(contacts[0])
    matching=all(set(sample_contacts)==keys for sample_contacts in contacts)
    spread=max(((max(sample_contacts[key] for sample_contacts in contacts)-
                 min(sample_contacts[key] for sample_contacts in contacts)).total_seconds()
                for key in keys),default=0.) if matching else None
    all_empty=all(not sample_contacts for sample_contacts in contacts)
    classification=('NOT_EVALUABLE' if all_empty or (len(samples)==1 and not exact_time) else 'EXACT_INPUT' if exact_time else 'SENSITIVE' if not matching or spread>max_spread_seconds else 'ROBUST')
    return {'classification':classification,'sample_count':len(samples),'contact_presence_stable':matching,
            'maximum_spread_seconds':spread,'threshold_seconds':max_spread_seconds,
            'sampling_ref':sampling_ref,'metaphysical_probability':None,
            'scope':'SUPPLIED_RECALCULATED_SAMPLES_ONLY'}
