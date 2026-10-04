"""Transformaciones geométricas; signos 0–11, intervalos [inicio, fin)."""
from math import floor, isfinite

PLANETS = ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')
LORDS = ('Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury',
         'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter')
DASHA_LORDS = ('Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury')
NAKSHATRAS = ('Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
             'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
             'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula',
             'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha', 'Shatabhisha',
             'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati')


def longitude(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError('La longitud debe ser numérica y finita.')
    return value % 360.0


def sign_of(value):
    return int(longitude(value) // 30)


def compute_nakshatra(value):
    value = longitude(value)
    # Multiplicación antes de división evita errores en límites representables.
    units = value * 3 / 40
    index = floor(units)
    return dict(index=index + 1, name=NAKSHATRAS[index], pada=floor(value * 3 / 10) % 4 + 1,
                lord=DASHA_LORDS[index % 9], start_deg=index * 40 / 3,
                end_deg=(index + 1) * 40 / 3, fraction_elapsed=units - index,
                source_ref='RAO_2000_1_3_6_TABLE_2', epistemic_class='A_CALCULATED')


def compute_navamsha(value):
    value = longitude(value)
    # Signo armónico coincide con la asignación parāśarī fuego/tierra/aire/agua.
    transformed = (value * 9) % 360
    return dict(sign=sign_of(transformed), longitude_in_sign=transformed % 30,
                symbolic_longitude=transformed, source_longitude=value,
                representation='DIVISIONAL_COORDINATE', physical_longitude=False,
                source_ref='RAO_2000_6_2_9_EXAMPLE_16')


def compute_chara_karakas(positions, system=8, tie_tolerance_deg=1e-9):
    if system not in (7, 8) or isinstance(system, bool):
        raise ValueError('El sistema de kārakas debe ser 7 u 8.')
    if not isfinite(tie_tolerance_deg) or tie_tolerance_deg < 0:
        raise ValueError('Tolerancia de empate inválida.')
    names = PLANETS + (('Rahu',) if system == 8 else ())
    advancements = {p: (30 - longitude(positions[p]) % 30 if p == 'Rahu'
                         else longitude(positions[p]) % 30) for p in names}
    ranked = sorted(names, key=lambda p: (-advancements[p], p))
    roles = ('AK', 'AmK', 'BK', 'MK') + (('PiK',) if system == 8 else ()) + ('PK', 'GK', 'DK')
    ties = [(a, b) for a, b in zip(ranked, ranked[1:])
            if abs(advancements[a] - advancements[b]) <= tie_tolerance_deg]
    # No resolución arbitraria por orden alfabético ni falsa precisión en empates.
    return dict(system=system, status='NOT_EVALUABLE' if ties else 'IMPLEMENTED',
                roles={} if ties else dict(zip(roles, ranked)), ranking=ranked,
                advancements=advancements, ties=ties, tie_policy='FAIL_CLOSED',
                source_ref='RAO_2000_8_2_EXAMPLE_28')


def compute_arudhas(lagna, positions, profile='SEVEN_LORDS_RAW_1_7_TO_TENTH'):
    if profile != 'SEVEN_LORDS_RAW_1_7_TO_TENTH':
        raise ValueError('Perfil Arudha no implementado; no se sustituye silenciosamente.')
    asc = sign_of(lagna)
    out = {}
    for house in range(1, 13):
        source = (asc + house - 1) % 12
        lord = LORDS[source]
        lord_sign = sign_of(positions[lord])
        distance = (lord_sign - source) % 12
        raw = (lord_sign + distance) % 12
        correction = (raw - source) % 12 in (0, 6)
        final = (raw + 9) % 12 if correction else raw
        key = 'AL' if house == 1 else 'UL' if house == 12 else f'A{house}'
        out[key] = dict(source_house=house, source_sign=source, lord=lord,
                        lord_sign=lord_sign, inclusive_distance=distance + 1,
                        raw_sign=raw, correction_applied=correction, sign=final,
                        representation='SIGN_ONLY', longitude=None, profile=profile,
                        source_ref='RAO_2000_9_2_SEVEN_LORDS_VARIANT')
    out['UL']['second_sign'] = (out['UL']['sign'] + 1) % 12
    out['UL']['second_lord'] = LORDS[out['UL']['second_sign']]
    return out


def compute_bhrigu_bindu(moon, rahu, arc='RAHU_TO_MOON_FORWARD'):
    moon, rahu = longitude(moon), longitude(rahu)
    if arc == 'RAHU_TO_MOON_FORWARD':
        delta = (moon - rahu) % 360
    elif arc == 'SHORTEST_ARC':
        delta = (moon - rahu + 180) % 360 - 180
        if abs(delta) == 180:
            return dict(status='NOT_EVALUABLE', reason='ANTIPODAL_AMBIGUITY', longitude=None)
    else:
        raise ValueError('Arco Bhrigu Bindu desconocido.')
    result = longitude(rahu + delta / 2)
    return dict(status='IMPLEMENTED', longitude=result, antipode=(result + 180) % 360,
                moon=moon, rahu=rahu, directed_arc_deg=delta, arc_profile=arc,
                doctrinal_class='MODERN_JYOTISHA', empirical='NOT_PERFORMED',
                epistemic_class='A_CALCULATED', relational_use='E_PROJECT_HYPOTHESIS', default_weight=0)


def compute_solar_upagrahas(sun):
    dhuma = longitude(longitude(sun) + 133 + 1 / 3)
    vyati = longitude(-dhuma)
    parivesha = longitude(vyati + 180)
    indra = longitude(-parivesha)
    values = dict(DHUMA=dhuma, VYATIPATA=vyati, PARIVESHA=parivesha,
                  INDRACHAPA=indra, UPAKETU=longitude(indra + 16 + 2 / 3))
    return {k: dict(longitude=v, source_ref='RAO_2000_4_2', default_weight=0,
                    doctrinal_class='TRADITIONAL_JYOTISHA') for k, v in values.items()}


def compute_vivaha_saham(venus, saturn, lagna, *, is_day, annual_context):
    if annual_context is not True or not isinstance(is_day, bool):
        raise ValueError('Vivāha requiere contexto anual explícito y día/noche booleano.')
    a, b = (longitude(venus), longitude(saturn)) if is_day else (longitude(saturn), longitude(venus))
    c = longitude(lagna)
    correction = not (0 < (c - b) % 360 < (a - b) % 360)
    result = longitude(a - b + c + (30 if correction else 0))
    return dict(longitude=result, day_or_night='DAY' if is_day else 'NIGHT',
                formula_profile='RAO_2000_TABLE_74_ARC_CORRECTION',
                correction_deg=30 if correction else 0, input_points=dict(A=a, B=b, C=c),
                context='ANNUAL', source_ref='RAO_2000_28_8', default_weight=0,
                endpoint_policy='STRICT_INTERIOR')
