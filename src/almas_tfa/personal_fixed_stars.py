"""Capa natal secundaria minimizada; no participa en índices ni raíces."""
from copy import deepcopy
from math import isfinite

from .astrology_backend import AstronomyBackendNotEvaluableError
from .production_astronomy import (
    load_fixed_star_paran_policy, _canonical_json_fingerprint, _canon_fingerprint,
)

KEYS = ('subject_id', 'layer_id', 'schema_version', 'status', 'structural_role',
        'policy_id', 'policy_fingerprint_sha256', 'method_source_ids', 'backend_id',
        'backend_version', 'backend_provenance', 'canon', 'fixed_stars', 'parans',
        'natal_angular_contacts')


def validate_personal_fixed_stars(layer, *, subject_id, provenance):
    policy = load_fixed_star_paran_policy()
    if set(layer) != set(KEYS):
        raise ValueError('Campos incompatibles en la capa personal de estrellas.')
    if layer['subject_id'] != subject_id or layer['backend_provenance'] != provenance:
        raise ValueError('Sujeto o procedencia de estrellas incompatibles con natal.')
    expected = dict(layer_id='FIXED_STARS_PARANS', schema_version='1.0.0',
                    status='CALCULATED', structural_role='SUPPORT_ONLY',
                    policy_id=policy['policy_id'],
                    policy_fingerprint_sha256=_canonical_json_fingerprint(policy),
                    method_source_ids=policy['method_source_ids'],
                    backend_id='MOIRA_JPL_SPK', backend_version='6.8.2')
    if any(layer[k] != v for k, v in expected.items()):
        raise ValueError('La capa de estrellas no reproduce la política secundaria.')
    canon = layer['canon']
    names = {e['name'] for e in canon['entries']}
    if (canon['returned_count'] != len(names) or
            canon['fingerprint_sha256'] != _canon_fingerprint(canon['entries']) or
            {e['name'] for e in layer['fixed_stars']} != names or
            len(layer['fixed_stars']) != len(names)):
        raise ValueError('Canon de estrellas incompleto o duplicado.')
    # Evita que NaN eluda comparaciones o se publique como dato astronómico.
    def finite(value):
        if isinstance(value, float) and not isfinite(value):
            raise ValueError('Magnitud no finita en estrellas personales.')
        if isinstance(value, dict):
            for v in value.values(): finite(v)
        elif isinstance(value, list):
            for v in value: finite(v)
    finite(layer)
    planets = {'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter',
               'Saturn', 'Uranus', 'Neptune', 'Pluto'}
    circles = {'Rising', 'Setting', 'Culminating', 'AntiCulminating'}
    for p in layer['parans']:
        bodies = {p['body1'], p['body2']}
        if (len(bodies) != 2 or not bodies & names or not bodies & planets or
                not bodies <= names | planets or p['circle1'] not in circles or
                p['circle2'] not in circles or not 0 <= p['orb_min'] <= policy['parans']['orb_minutes']):
            raise ValueError('Paran personal fuera del contrato.')
    for c in layer['natal_angular_contacts']:
        if (c['body'] not in names or c['body_family'] != 'star' or
                c['circle'] not in circles or
                not 0 <= c['absolute_delta_minutes'] <= policy['natal_angular_contacts']['orb_minutes'] or
                abs(abs(c['delta_minutes']) - c['absolute_delta_minutes']) > 1e-6):
            raise ValueError('Contacto angular personal fuera del contrato.')


def calculate_personal_fixed_stars(backend, request, *, quality, provenance):
    if quality not in {'A', 'B'} or not request.timed:
        raise AstronomyBackendNotEvaluableError('Estrellas/parans requieren hora natal A/B explícita.')
    calculate = getattr(backend, 'calculate_fixed_star_parans', None)
    if not callable(calculate):
        raise AstronomyBackendNotEvaluableError('El backend no dispone de estrellas/parans.')
    raw = calculate(request)
    # No persistir metadata natal, coordenadas ni relojes absolutos de cruces.
    result = {key: deepcopy(raw[key]) for key in KEYS}
    for paran in result['parans']:
        paran.pop('jd1', None); paran.pop('jd2', None)
    for contact in result['natal_angular_contacts']:
        contact.pop('crossing_jd', None); contact.pop('natal_jd', None)
    validate_personal_fixed_stars(result, subject_id=request.subject_id, provenance=provenance)
    return result


def render_personal_fixed_stars(layer):
    """Texto técnico auditable; no inventa significados específicos de estrellas."""
    lines = ['Estrellas fijas y parans: capa secundaria SUPPORT_ONLY calculada con Moira 6.8.2.']
    for p in layer['parans']:
        lines.append(f"{p['body1']} ({p['circle1']}) y {p['body2']} ({p['circle2']}): separación temporal {p['orb_min']:.3f} minutos.")
    for c in layer['natal_angular_contacts']:
        lines.append(f"{c['body']} en {c['circle']}: separación natal {c['absolute_delta_minutes']:.3f} minutos.")
    if not layer['parans'] and not layer['natal_angular_contacts']:
        lines.append('No se encontraron parans ni contactos angulares dentro de los umbrales declarados.')
    lines.append('Brady aporta el método moderno identificado; Ptolomeo I.9 es un antecedente histórico. Esta geometría no crea raíces, puntuación ni categorías de vínculo.')
    return '\n\n'.join(lines)
