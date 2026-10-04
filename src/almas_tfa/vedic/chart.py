"""Carta védica autónoma; backend opcional Swiss/Moshier identificado."""
from datetime import datetime, timedelta, timezone
from math import isfinite
from threading import RLock
from zoneinfo import ZoneInfo
from .geometry import (PLANETS, LORDS, longitude, sign_of, compute_nakshatra,
    compute_navamsha, compute_chara_karakas, compute_arudhas, compute_bhrigu_bindu,
    compute_solar_upagrahas)
from .timing import instant

_LOCK = RLock()
DEFAULTS = dict(ayanamsha='LAHIRI', chara_karaka_system=8, node='MEAN',
                arudha_profile='SEVEN_LORDS_RAW_1_7_TO_TENTH',
                bindu_arc='RAHU_TO_MOON_FORWARD', year_days=365.2425,
                time_upagraha_profile='RAO_2000_MIDDLE_GULIKA_BEGIN_MANDI',
                abhijit_overlay=False)


def settings(values=None):
    values = values or {}
    unknown = set(values) - set(DEFAULTS) - {'custom_reference_jd', 'custom_ayanamsha_deg'}
    if unknown:
        raise ValueError(f'Configuración védica desconocida: {sorted(unknown)}')
    out = {**DEFAULTS, **values}
    if out['ayanamsha'] not in ('LAHIRI', 'RAMAN', 'KP', 'FAGAN_BRADLEY', 'CUSTOM'):
        raise ValueError('Ayanāṃśa no soportado.')
    if out['node'] not in ('MEAN', 'TRUE'):
        raise ValueError('La convención nodal debe ser MEAN o TRUE.')
    if out['chara_karaka_system'] not in (7, 8) or isinstance(out['chara_karaka_system'], bool):
        raise ValueError('Sistema kāraka inválido.')
    if out['year_days'] not in (360, 365.2425, 365.25636):
        raise ValueError('Convención anual no soportada.')
    if out['time_upagraha_profile'] not in ('RAO_2000_MIDDLE_GULIKA_BEGIN_MANDI',
                                           'BEGIN_GULIKA_MIDDLE_MANDI'):
        raise ValueError('Perfil de upagrahas no soportado.')
    if not isinstance(out['abhijit_overlay'], bool):
        raise ValueError('Abhijit overlay debe ser booleano.')
    if out['ayanamsha'] == 'CUSTOM':
        for k in ('custom_reference_jd', 'custom_ayanamsha_deg'):
            if k not in out or isinstance(out[k], bool) or not isfinite(out[k]):
                raise ValueError('CUSTOM requiere época JD y ayanāṃśa finitos.')
    return out


def chart_from_sidereal(positions, *, configuration=None, provenance=None, birth=None):
    cfg = settings(configuration)
    required = set(PLANETS) | {'Rahu', 'Lagna'}
    if required - set(positions):
        raise ValueError(f'Faltan posiciones siderales: {sorted(required - set(positions))}')
    pos = {k: longitude(v) for k, v in positions.items()}
    ketu = longitude(pos['Rahu'] + 180)
    if 'Ketu' in pos and abs((pos['Ketu'] - ketu + 180) % 360 - 180) > 1e-8:
        raise ValueError('Ketu debe ser el antípoda exacto de Rahu.')
    pos['Ketu'] = ketu
    kr = compute_chara_karakas(pos, cfg['chara_karaka_system'])
    d9 = {p: compute_navamsha(v) for p, v in pos.items()}
    ak = kr['roles'].get('AK')
    ka = (dict(sign=d9[ak]['sign'], representation='SIGN_ONLY', longitude=None,
               source_body=ak, reference_varga='D9', status='IMPLEMENTED') if ak
          else dict(status='NOT_EVALUABLE', sign=None, longitude=None))
    ar = compute_arudhas(pos['Lagna'], pos, cfg['arudha_profile'])
    out = dict(schema_version='ALMAS_VED_1', configuration=cfg,
        provenance=provenance or dict(engine='PRECOMPUTED', verification='USER_SUPPLIED'),
        birth=instant(birth).isoformat() if birth else None,
        d1={k: dict(longitude=v, sign=sign_of(v), nakshatra=compute_nakshatra(v),
                     dispositor=LORDS[sign_of(v)]) for k, v in pos.items()},
        d9=d9, karakas=kr, karakamsha=ka, arudhas=ar,
        bhrigu_bindu=compute_bhrigu_bindu(pos['Moon'], pos['Rahu'], cfg['bindu_arc']),
        upagrahas=compute_solar_upagrahas(pos['Sun']),
        confidence=dict(astronomical='PRECOMPUTED_UNVERIFIED', birth_time='UNDECLARED',
                        computational='IMPLEMENTED', doctrinal='PROFILE_DECLARED', empirical='NOT_PERFORMED'),
        canonical_effect=False, metaphysical_assessment='INSUFFICIENT')
    if cfg['abhijit_overlay']:
        # Intervalo tradicional 6°40′–10°53′20″ Capricornio, no 28 sectores iguales.
        lower, upper = 276 + 2 / 3, 280 + 8 / 9
        out['abhijit_overlay'] = {k: dict(active=lower <= v < upper,
            interval_deg=[lower, upper], default_weight=0, modifies_dasha=False) for k, v in pos.items()}
    return out


def _julian(dt, swe):
    dt = instant(dt)
    return swe.julday(dt.year, dt.month, dt.day,
        dt.hour + dt.minute / 60 + (dt.second + dt.microsecond / 1e6) / 3600)


def _from_jd(jd):
    return datetime(2000, 1, 1, 12, tzinfo=timezone.utc) + timedelta(days=jd - 2451545)


def _solar_context(jd, latitude, lon, swe):
    """Última salida y puesta; sin tiempos ficticios en latitudes polares."""
    def next_event(start, mode):
        code, times = swe.rise_trans(start, swe.SUN, mode | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION,
            (lon, latitude, 0.0), 0.0, 0.0, swe.FLG_MOSEPH)
        if code != 0:
            raise ValueError('Sin salida/puesta solar evaluable en esta latitud y fecha.')
        return times[0]
    rises, sets = [], []
    for delta in (-2, -1, 0):
        rises.append(next_event(jd + delta, swe.CALC_RISE))
        sets.append(next_event(jd + delta, swe.CALC_SET))
    last_rise = max(t for t in rises if t <= jd)
    last_set = max(t for t in sets if t <= jd)
    is_day = last_rise > last_set
    start = last_rise if is_day else last_set
    end = next_event(jd, swe.CALC_SET if is_day else swe.CALC_RISE)
    # Día planetario comienza al amanecer, incluso después de medianoche civil.
    solar_date = _from_jd(last_rise + lon / 360).date()
    weekday = (solar_date.weekday() + 1) % 7
    return dict(start_jd=start, end_jd=end, last_sunrise_jd=last_rise,
                weekday=weekday, is_day=is_day, rise_definition='CENTER_NO_REFRACTION_SEA_LEVEL')


def compute_time_upagrahas(context, ascendant_at, profile):
    if profile not in ('RAO_2000_MIDDLE_GULIKA_BEGIN_MANDI', 'BEGIN_GULIKA_MIDDLE_MANDI'):
        raise ValueError('Perfil temporal desconocido.')
    ring = ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', None)
    start_index = context['weekday'] if context['is_day'] else (context['weekday'] + 4) % 7
    sequence = [ring[(start_index + i) % 8] for i in range(8)]
    width = (context['end_jd'] - context['start_jd']) / 8
    midpoint_gulika = profile == 'RAO_2000_MIDDLE_GULIKA_BEGIN_MANDI'
    endpoints = {'KALA': ('Sun', .5), 'MRTYU': ('Mars', .5),
        'ARDHA_PRAHARA': ('Mercury', .5), 'YAMA_GHANTAKA': ('Jupiter', .5),
        'GULIKA': ('Saturn', .5 if midpoint_gulika else 0),
        'MANDI': ('Saturn', 0 if midpoint_gulika else .5)}
    out = {}
    for key, (lord, fraction) in endpoints.items():
        time = context['start_jd'] + (sequence.index(lord) + fraction) * width
        out[key] = dict(longitude=longitude(ascendant_at(time)), instant=_from_jd(time).isoformat(),
            method=profile, day_or_night='DAY' if context['is_day'] else 'NIGHT',
            solar_context=context, source_ref='RAO_2000_4_3' if midpoint_gulika else None,
            doctrinal_class='TRADITIONAL_JYOTISHA' if midpoint_gulika else 'EXPERIMENTAL_CROSS_SYSTEM',
            interpretation_validated=False, default_weight=0)
    return out


def compute_vedic_chart(request, configuration=None):
    """Entrada: timestamp ISO con offset, latitude, longitude, timezone opcional."""
    cfg = settings(configuration)
    dt = instant(request['timestamp'])
    for k, limit in (('latitude', 90), ('longitude', 180)):
        v = request[k]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v) or abs(v) > limit:
            raise ValueError(f'Coordenada {k} inválida.')
    zone = request.get('timezone')
    if zone:
        original = datetime.fromisoformat(request['timestamp'].replace('Z', '+00:00'))
        local = dt.astimezone(ZoneInfo(zone))
        if original.replace(tzinfo=None) != local.replace(tzinfo=None) or original.utcoffset() != local.utcoffset():
            raise ValueError('La hora/offset no coincide con la zona IANA; revisar DST.')
    try:
        import swisseph as swe
    except ImportError as exc:
        raise RuntimeError('Instale el extra astronomy-vedic para calcular cartas brutas.') from exc
    with _LOCK:
        modes = dict(LAHIRI=swe.SIDM_LAHIRI, RAMAN=swe.SIDM_RAMAN, KP=swe.SIDM_KRISHNAMURTI,
                     FAGAN_BRADLEY=swe.SIDM_FAGAN_BRADLEY, CUSTOM=swe.SIDM_USER)
        swe.set_sid_mode(modes[cfg['ayanamsha']], cfg.get('custom_reference_jd', 0),
                         cfg.get('custom_ayanamsha_deg', 0))
        jd = _julian(dt, swe)
        flags = swe.FLG_MOSEPH | swe.FLG_SPEED
        aya = swe.get_ayanamsa_ex_ut(jd, swe.FLG_MOSEPH)[1]
        def ascendant_at(t):
            ay = swe.get_ayanamsa_ex_ut(t, swe.FLG_MOSEPH)[1]
            return longitude(swe.houses(t, request['latitude'], request['longitude'], b'E')[1][0] - ay)
        bodies = dict(zip(PLANETS, (swe.SUN, swe.MOON, swe.MARS, swe.MERCURY,
                                  swe.JUPITER, swe.VENUS, swe.SATURN)))
        bodies['Rahu'] = swe.MEAN_NODE if cfg['node'] == 'MEAN' else swe.TRUE_NODE
        pos, returned_flags = {}, {}
        for name, body in bodies.items():
            values, actual_flags = swe.calc_ut(jd, body, flags)
            pos[name] = longitude(values[0] - aya)
            returned_flags[name] = actual_flags
        pos['Lagna'] = ascendant_at(jd)
        pos['MC'] = longitude(swe.houses(jd, request['latitude'], request['longitude'], b'E')[1][1] - aya)
        out = chart_from_sidereal(pos, configuration=cfg, birth=dt,
            provenance=dict(engine='SWISS_EPHEMERIS_MOSHIER', version=swe.version,
                ayanamsha_value_deg=aya, julian_day_ut=jd, returned_flags=returned_flags,
                requested_flags=flags, coordinates=dict(latitude=request['latitude'], longitude=request['longitude']),
                timezone_id=zone, original_timestamp=request['timestamp'], zodiac='sidereal',
                calendar='PROLEPTIC_GREGORIAN', time_scale='UTC_AS_UT_APPROXIMATION',
                backend_role='VED_ONLY_COMPARATIVE', independent_cross_verification='NOT_PERFORMED'))
        out['confidence']['astronomical'] = 'COMPUTED_BACKEND_DECLARED'
        out['confidence']['birth_time'] = request.get('birth_time_quality', 'UNDECLARED')
        try:
            context = _solar_context(jd, request['latitude'], request['longitude'], swe)
            out['solar_context'] = context
            out['upagrahas'].update(compute_time_upagrahas(context, ascendant_at, cfg['time_upagraha_profile']))
        except (ValueError, swe.Error) as exc:
            out['time_upagrahas'] = dict(status='NOT_EVALUABLE', reason=str(exc))
        return out
