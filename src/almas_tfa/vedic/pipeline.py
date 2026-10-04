"""Envolvente optativa VED; entrada explícita y salida aislada."""
from copy import deepcopy
from .chart import compute_vedic_chart
from .synastry import compute_vedic_synastry, compute_vedic_event_activation
from .validation import group_ablation, descriptive_shapley, compute_sensitivity
from .geometry import compute_vivaha_saham


def run_vedic_pipeline(request):
    if not isinstance(request.get('enabled'), bool):
        raise ValueError('enabled debe declararse booleano.')
    out = dict(schema_version='ALMAS_VED_ENVELOPE_1', enabled=request['enabled'],
               canonical_effect=False, external_validation='NOT_PERFORMED',
               metaphysical_assessment='INSUFFICIENT', charts=[], synastry=None,
               events=[], sensitivity=[], ablation=None, shapley=None, annual=[])
    if not request['enabled']:
        return out
    subjects = request.get('subjects', [])
    if len(subjects) != 2 or subjects[0]['id'] == subjects[1]['id']:
        raise ValueError('Se requieren exactamente dos sujetos diferentes.')
    cfg = request.get('configuration')
    charts = [compute_vedic_chart(s['birth'], cfg) for s in subjects]
    syn = compute_vedic_synastry(*charts, orb_deg=request.get('orb_deg', 3.0))
    out.update(charts=charts, synastry=syn, ablation=group_ablation(syn), shapley=descriptive_shapley(syn))
    seen = set()
    for event in request.get('events', []):
        if event['id'] in seen:
            raise ValueError('IDs de eventos duplicados.')
        seen.add(event['id'])
        # Coordenadas sólo necesarias para ángulos/solar-context de carta de evento.
        transit = compute_vedic_chart(event, cfg) if {'latitude','longitude'} <= set(event) else None
        out['events'].append(dict(event_id=event['id'], **compute_vedic_event_activation(*charts, event,
            synastry=syn, transit_chart=transit)))
    if request.get('sensitivity', False):
        out['sensitivity'] = [compute_sensitivity(s['birth'], cfg) for s in subjects]
    for annual in request.get('annual_charts', []):
        # No confundir una fecha arbitraria con el retorno solar: recibo requerido.
        if annual.get('return_verified') is not True or not annual.get('return_source_ref'):
            raise ValueError('La carta anual requiere recibo verificable del retorno solar.')
        chart = compute_vedic_chart(annual['chart'], cfg)
        if 'solar_context' not in chart:
            raise ValueError('No se puede determinar día/noche de la carta anual.')
        p = chart['d1']
        saham = compute_vivaha_saham(p['Venus']['longitude'], p['Saturn']['longitude'], p['Lagna']['longitude'],
                                     is_day=chart['solar_context']['is_day'], annual_context=True)
        out['annual'].append(dict(return_source_ref=annual['return_source_ref'], chart=chart, vivaha_saham=saham))
    return out


def attach_vedic(canonical, envelope):
    if 'vedic' in canonical:
        raise ValueError('El bloque VED existente no puede sobrescribirse silenciosamente.')
    if envelope.get('canonical_effect') is not False or envelope.get('schema_version') != 'ALMAS_VED_ENVELOPE_1':
        raise ValueError('Envolvente VED incompatible.')
    if envelope.get('external_validation') != 'NOT_PERFORMED' or envelope.get('metaphysical_assessment') != 'INSUFFICIENT':
        raise ValueError('Esta release no admite promoción empírica ni ontológica de VED.')
    if any(c.get('canonical_effect') is not False for c in envelope.get('charts', [])):
        raise ValueError('Carta VED con efecto canónico no permitido.')
    syn = envelope.get('synastry')
    if syn and (syn.get('canonical_effect') is not False or any(f.get('default_weight') != 0 for f in syn['features'])):
        raise ValueError('Los pesos VED deben permanecer en cero.')
    out = deepcopy(canonical)
    out['vedic'] = deepcopy(envelope)
    return out


def render_vedic_report(envelope):
    if not envelope['enabled']:
        return 'Jyotiṣa Relacional permanece desactivado.\n'
    cfg = envelope['charts'][0]['configuration']
    parts = [f"Jyotiṣa Relacional. Configuración: {cfg['ayanamsha']}, nodos {cfg['node']}, "
             f"{cfg['chara_karaka_system']} kārakas y año daśā de {cfg['year_days']} días."]
    for label, chart in zip(('A', 'B'), envelope['charts']):
        roles = chart['karakas']['roles']
        ar = chart['arudhas']
        parts.append(f"Sujeto {label}: AK={roles.get('AK', 'no evaluable')}; DK={roles.get('DK', 'no evaluable')}. "
            f"AL, UL y A7 ocupan los signos {ar['AL']['sign']+1}, {ar['UL']['sign']+1} y {ar['A7']['sign']+1} "
            "(numeración Aries=1). Son posiciones por signo; no poseen longitud angular propia. "
            f"Calidad horaria declarada: {chart['confidence']['birth_time']}.")
    syn = envelope['synastry']
    parts.append(f"La matriz contiene {len(syn['features'])} comparaciones descriptivas en D1/D9, "
        f"con {syn['recurrence']['raw_matches']} coincidencias y "
        f"{syn['recurrence']['dependency_bundles']} bundles de dependencia. Los bundles no acreditan raíces independientes. "
        "Las coordenadas D9 son divisionales y sus cruces entre sujetos constituyen hipótesis ALMAS.")
    parts.append(f"Se procesaron {len(envelope['events'])} eventos mediante Vimśottarī y, cuando se suministraron "
        "coordenadas, contactos de tránsito anclados a la estructura. Estas activaciones no predicen decisiones ni hechos.")
    parts.append("La contraevidencia recoge relaciones por signo potencialmente conflictivas para revisión, "
        "sin equipararlas a incompatibilidad factual. Aṣṭakūṭa completo permanece no evaluable sin tablas y excepciones verificadas. "
        "IVED carece de valor escalar calibrado; los pesos canónicos permanecen en cero. La validación externa no se ha realizado "
        "y la discriminación metafísica permanece INSUFFICIENT.")
    parts.append("Procedencia técnica: P. V. R. Narasimha Rao, Vedic Astrology: An Integrated Approach (2000), "
        "capítulos 4, 6, 8, 9, 16 y 28; efemérides Swiss Ephemeris/Moshier identificadas en cada carta. "
        "Se separan datos calculados, técnicas tradicionales y usos relacionales experimentales.")
    return '\n\n'.join(parts) + '\n'
