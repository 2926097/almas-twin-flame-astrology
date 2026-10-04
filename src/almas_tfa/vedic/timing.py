"""Vimśottarī: períodos completos, intervalos UTC semiabiertos."""
from datetime import datetime, timedelta, timezone
from math import isfinite
from .geometry import DASHA_LORDS, compute_nakshatra

YEARS = dict(zip(DASHA_LORDS, (7, 20, 6, 10, 7, 18, 16, 19, 17)))


def instant(value):
    dt = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError('Se requiere fecha/hora con offset UTC explícito.')
    return dt.astimezone(timezone.utc)


def _subperiod(parent_lord, start, duration, target):
    offset = DASHA_LORDS.index(parent_lord)
    parent_end = start + duration
    for step in range(9):
        lord = DASHA_LORDS[(offset + step) % 9]
        end = parent_end if step == 8 else start + duration * (YEARS[lord] / 120)
        if start <= target < end:
            return lord, start, end - start
        start = end
    raise ValueError('Instante fuera del período contenedor.')


def compute_vimshottari(moon, birth, at, year_days=365.2425):
    birth, at = instant(birth), instant(at)
    if isinstance(year_days, bool) or not isfinite(year_days) or year_days not in (360, 365.2425, 365.25636):
        raise ValueError('Año daśā permitido: 360, 365.2425 o 365.25636 días.')
    if at < birth:
        raise ValueError('El evento no puede ser anterior al nacimiento.')
    nk = compute_nakshatra(moon)
    first = nk['lord']
    duration = timedelta(days=YEARS[first] * year_days)
    start = birth - duration * nk['fraction_elapsed']
    initial_start = start
    offset = DASHA_LORDS.index(first)
    maha = None
    # Límite explícito: dos ciclos, no un bucle sin límite ni fechas inválidas.
    for step in range(18):
        lord = DASHA_LORDS[(offset + step) % 9]
        duration = timedelta(days=YEARS[lord] * year_days)
        if start <= at < start + duration:
            maha = lord
            break
        start += duration
    if maha is None:
        raise ValueError('Evento fuera de los dos ciclos admitidos de Vimśottarī.')
    antara, a_start, a_duration = _subperiod(maha, start, duration, at)
    pratya, p_start, p_duration = _subperiod(antara, a_start, a_duration, at)
    def record(lord, s, d):
        return dict(lord=lord, start=s.isoformat(), end=(s + d).isoformat())
    return dict(maha=record(maha, start, duration), antara=record(antara, a_start, a_duration),
                pratyantara=record(pratya, p_start, p_duration), year_days=year_days,
                initial_lord=first, initial_start=initial_start.isoformat(),
                balance_at_birth_years=YEARS[first] * (1 - nk['fraction_elapsed']),
                source_ref='RAO_2000_16_2_16_3', status='IMPLEMENTED',
                epistemic_class='A_CALCULATED', event_prediction=False)
