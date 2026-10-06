"""Frontera única: ALMAS conserva la carta y el instante natal canónicos."""
from collections.abc import Mapping
import re
from .engine import number, local_to_utc, utc_datetime, iso
from .models import UniformCycleRequest
from .provenance import serialize, fingerprint_payload

SETTINGS = {'start_utc','end_utc','cycle_years','year_days','direction','aspects_deg',
            'orb_deg','promissors','significators','include_self','output_timezone'}
DEFAULTS = {'year_days':365.2422,'direction':'direct','aspects_deg':[0,60,90,120,180],
            'orb_deg':1.,'include_self':False}

def extract_canonical_longitudes(chart):
    positions=chart.get('positions')
    if not isinstance(positions,Mapping) or not positions:
        raise ValueError('Se requieren posiciones canónicas.')
    points={}
    for point, data in positions.items():
        if not isinstance(point,str) or not re.fullmatch(r'[A-Z][A-Z0-9_]*',point):
            raise ValueError('Identificador de punto no canónico.')
        if not isinstance(data,Mapping) or 'longitude' not in data or 'longitude_deg' in data:
            raise ValueError('Usar únicamente longitude canónico.')
        if data.get("node_variant") is not None and data["node_variant"] not in {"TRUE","MEAN"}:
            raise ValueError("node_variant no canónico.")
        points[point]=number(data['longitude'],point,0.,359.99999999999994)
    angles=chart.get('angles',{})
    if not isinstance(angles,Mapping):raise ValueError('angles debe ser un objeto.')
    for point,value in angles.items():
        if point not in {'ASC','MC','DSC','IC'} or point in points:
            raise ValueError('Ángulo desconocido o duplicado.')
        if isinstance(value,Mapping):
            if 'longitude_deg' in value:raise ValueError('Ángulo no canónico.')
            value=value.get('longitude')
        points[point]=number(value,point,0.,359.99999999999994)
    return points

def build_uniform_cycle_request(chart,subject,settings):
    if not all(isinstance(v,Mapping) for v in (chart,subject,settings)):
        raise ValueError('Carta, sujeto y settings deben ser objetos.')
    if set(settings)-SETTINGS:raise ValueError('Campos settings no admitidos.')
    if chart.get('timed') is not True or not subject.get('birth_time'):
        raise ValueError('Se requiere hora natal documentada.')
    reliability=subject.get('time_reliability')
    if not isinstance(reliability,str) or reliability.upper() not in {'EXACT','A','AA','RECORDED','DOCUMENTED'}:
        raise ValueError('Hora incierta: se requieren cartas perturbadas y robustez explícita.')
    if subject.get('time_uncertainty_minutes',0) != 0 or subject.get('birth_time_range'):
        raise ValueError('Rango natal: evaluar muestras recalculadas, sin falsa precisión.')
    if not subject.get('id') or chart.get('subject_id') != subject['id']:
        raise ValueError('La carta no corresponde al sujeto.')
    for field in ('backend_id','backend_version','zodiac'):
        if not isinstance(chart.get(field),str) or not chart[field].strip():
            raise ValueError('Falta provenance de la carta.')
    if not isinstance(chart.get('backend_provenance'),Mapping) or not chart['backend_provenance']:
        raise ValueError('Falta backend_provenance.')
    metadata=chart.get('metadata')
    if not isinstance(metadata,Mapping):raise ValueError('Falta metadata natal.')
    local=f"{subject.get('birth_date')}T{subject['birth_time']}"
    tz=subject.get('timezone')
    birth=local_to_utc(local,tz,subject.get('fold'))
    if birth != utc_datetime(metadata.get('utc_instant'),'utc_instant'):
        raise ValueError('El instante de la carta difiere del sujeto canónico.')
    coordinates={}
    for field,lo,hi in (('latitude',-90,90),('longitude',-180,180)):
        coordinates[field]=number(metadata.get(field),field,lo,hi)
        if coordinates[field] != number(subject.get(field),field,lo,hi):
            raise ValueError('Coordenadas incompatibles con la carta.')
    points=extract_canonical_longitudes(chart)
    effective={**DEFAULTS,'output_timezone':tz,**settings}
    for field in ('start_utc','end_utc','cycle_years'):
        if field not in effective:raise ValueError('Falta parámetro temporal obligatorio.')
    effective.setdefault('promissors',sorted(points))
    effective.setdefault('significators',sorted(points))
    # La fuente completa y el esquema natal quedan comprometidos por la huella.
    source={'chart_fingerprint':fingerprint_payload(chart),'subject_fingerprint':fingerprint_payload(subject),
            'backend_id':chart['backend_id'],'backend_version':chart['backend_version'],
            'backend_provenance':dict(chart['backend_provenance']),'zodiac':chart['zodiac'],
            'house_system':metadata.get('house_system_requested'),'coordinates':coordinates,
            'coordinate_source':'CANONICAL_NATAL_METADATA','timezone_id':tz,
            'birth_utc':iso(birth),'time_reliability':reliability,'natal_uncertainty':'EXACT_INPUT',
            'node_variants':{p:d.get('node_variant') for p,d in chart['positions'].items() if 'NODE' in p}}
    payload={'schema_version':'1.0','technique':'UNIFORM_CYCLE','datetime_local':local,
             'timezone_id':tz,'natal_points':points,'positions_source':source['chart_fingerprint'],**effective}
    if 'fold' in subject:payload['fold']=subject['fold']
    return UniformCycleRequest(serialize(payload),serialize(source))
