"""Lossless editorial projection from an already computed VED envelope."""
from copy import deepcopy
from importlib import resources
import json

from .contracts import validate_vedic_envelope
from .synastry import _fingerprint, _objects

SIGNS = ('Aries', 'Tauro', 'Géminis', 'Cáncer', 'Leo', 'Virgo', 'Libra',
         'Escorpio', 'Sagitario', 'Capricornio', 'Acuario', 'Piscis')
ASPECTS = {0: 'conjunción', 60: 'sextil', 90: 'cuadratura', 120: 'trígono', 180: 'oposición'}


def _endpoint(chart, layer, name, subject):
    obj = _objects(chart, layer)[name]
    underlying = name
    if name in ('AK', 'DK'):
        underlying = chart['karakas']['roles'][name]
    source = chart['d1'].get(underlying, {}) if layer == 'D1' else chart['d9'].get(underlying, {})
    lon = obj['longitude']
    representation = ('DIVISIONAL_SIGN' if layer == 'D9' else
                      'SIGN_ONLY' if lon is None else
                      'DERIVED_LONGITUDE' if name not in chart['d1'] and name not in ('AK', 'DK') else
                      'SIDEREAL_LONGITUDE')
    point = dict(subject=subject, object=name, source_object=underlying, layer=layer,
                 representation=representation, longitude_deg=lon, sign_index=obj['sign'],
                 sign=SIGNS[obj['sign']], degree_in_sign=lon % 30 if lon is not None else None,
                 symbolic_longitude_deg=source.get('symbolic_longitude') if layer == 'D9' else None,
                 house=None, dispositor=source.get('dispositor'),
                 speed_deg_per_day=source.get('speed_deg_per_day') if layer == 'D1' else None,
                 retrograde=source.get('retrograde') if layer == 'D1' else None,
                 nakshatra=deepcopy(source.get('nakshatra')) if layer == 'D1' else None,
                 input_dependencies=list(obj['dependency']), provenance=deepcopy(chart['provenance']),
                 birth_time_quality=chart['confidence']['birth_time'])
    point['missing_dimensions'] = [k for k in ('house', 'dispositor', 'speed_deg_per_day', 'retrograde') if point[k] is None]
    return point


def build_vedic_report_model(envelope):
    """Retain every comparison, position, period and source without ephemerides."""
    validate_vedic_envelope(envelope)
    model = dict(model_revision='ALMAS_VED_REPORT_V1', canonical_fingerprint=_fingerprint(envelope),
                 enabled=envelope['enabled'], positions=[], contacts=[], dependency_groups=[],
                 events=deepcopy(envelope['events']), sensitivity=deepcopy(envelope['sensitivity']),
                 annual=deepcopy(envelope['annual']), coverage=dict(input_features=0, projected_features=0,
                     excluded_feature_ids=[], status='COMPLETE'),
                 classification=dict(origin='INSUFFICIENT', history='NOT_EVALUABLE', function='INSUFFICIENT',
                     polarity='INSUFFICIENT', modality='NOT_EVALUABLE', phase='NOT_EVALUABLE',
                     viability='NOT_EVALUABLE', reciprocity='NOT_EVALUABLE'),
                 canonical_effect=False)
    if not envelope['enabled']:
        return model
    a, b = envelope['charts']
    for subject, chart in (('A', a), ('B', b)):
        for layer in ('D1', 'D9'):
            for name in sorted(_objects(chart, layer)):
                model['positions'].append(_endpoint(chart, layer, name, subject))
    groups = {}
    for index, f in enumerate(envelope['synastry']['features']):
        matched = bool(f['same_sign'] or f['angular_contacts_deg'] or f['same_nakshatra'])
        row = dict(feature_id=f['feature_id'], data_ref=f'/synastry/features/{index}',
                   endpoints=[_endpoint(a, f['varga_a'], f['object_a'], 'A'),
                              _endpoint(b, f['varga_b'], f['object_b'], 'B')],
                   separation_deg=f['separation_deg'], sign_relation=list(f['sign_relation']),
                   orb_limit_deg=f['orb_deg'], aspects=[dict(angle_deg=angle, name=ASPECTS[angle],
                       residual_deg=abs(f['separation_deg']-angle)) for angle in f['angular_contacts_deg']],
                   same_sign=f['same_sign'], same_nakshatra=f['same_nakshatra'],
                   same_pada=f.get('same_pada'), same_nakshatra_lord=f.get('same_nakshatra_lord'),
                   matched=matched, dependency_bundle=f['root_dependency_id'],
                   dependency_family=f['redundancy_group'], confidence=deepcopy(f['confidence']),
                   counterevidence=dict(sign_relation_flag=set(f['sign_relation']) in ({6,8},{2,12}),
                       factual_incompatibility=False, assessment='NOT_EVALUABLE'),
                   epistemic_layers=dict(A='CALCULATED_GEOMETRY', B='DECLARED_SIGN_VARGA_AND_ORB_RULE',
                       C='SOURCE_GAP_FOR_DYADIC_INTERPRETATION', D='NOT_DOCUMENTED',
                       E='DESCRIPTIVE_RELATIONAL_CORRESPONDENCE'),
                   alternative_models=['shared_symbolic_theme', 'ordinary_similarity', 'projection_or_context'],
                   source_refs=['RAO_2000_6_2_9_EXAMPLE_16'] if 'D9' in (f['varga_a'],f['varga_b']) else [],
                   source_scope='METHOD_ONLY', metaphysical_assessment='INSUFFICIENT')
        model['contacts'].append(row)
        group = groups.setdefault(f['root_dependency_id'], dict(bundle_id=f['root_dependency_id'],
            feature_ids=[], matched_feature_ids=[], statistical_independence=False))
        group['feature_ids'].append(f['feature_id'])
        if matched:
            group['matched_feature_ids'].append(f['feature_id'])
    model['dependency_groups'] = [groups[key] for key in sorted(groups)]
    model['coverage'].update(input_features=len(envelope['synastry']['features']), projected_features=len(model['contacts']))
    anchors = json.loads(resources.files('almas_tfa').joinpath('data','vedic-source-anchors.json').read_text(encoding='utf-8'))
    model['sources'] = anchors
    return model


def render_vedic_details(envelope):
    model = build_vedic_report_model(envelope)
    if not model['enabled']:
        return ''
    parts = [f"Trazabilidad documental: fingerprint {model['canonical_fingerprint']}. "
             f"Cobertura completa: {model['coverage']['projected_features']}/{model['coverage']['input_features']} "
             "comparaciones accesibles; ninguna comparación excluida. Las fichas amplían la información, "
             "sin aumentar raíces independientes ni alterar los índices."]
    for point in model['positions']:
        longitude = 'sin longitud física' if point['longitude_deg'] is None else f"{point['longitude_deg']:.9f}° siderales"
        nk = point['nakshatra']
        nktext = f"; nakṣatra {nk['name']}, pāda {nk['pada']}" if nk else ''
        parts.append(f"Ubicación {point['subject']}.{point['layer']}.{point['object']}: {point['sign']}, {longitude}{nktext}. "
            f"Representación {point['representation']}; dependencia {', '.join(point['input_dependencies'])}. "
            f"Regente disponible: {point['dispositor']}; velocidad disponible: {point['speed_deg_per_day']}; "
            f"retrógrado: {point['retrograde']}. Campos no disponibles: {', '.join(point['missing_dimensions']) or 'ninguno'}. "
            "La ausencia de un campo no equivale a cero ni a contraevidencia.")
    for group in model['dependency_groups']:
        if group['matched_feature_ids']:
            parts.append(f"Síntesis de dependencia {group['bundle_id']}: {len(group['matched_feature_ids'])} coincidencias "
                f"en {len(group['feature_ids'])} apariciones. Referencias: {', '.join(group['matched_feature_ids'])}. "
                "Su recurrencia comparte entradas y no acredita independencia ni origen común.")
    for row in model['contacts']:
        a,b = row['endpoints']
        contacts = '; '.join(f"{v['name']} {v['angle_deg']}°, residual {v['residual_deg']:.9f}°" for v in row['aspects']) or 'ningún aspecto angular evaluado coincidente'
        separation = 'no aplicable a coordenadas por signo/divisionales' if row['separation_deg'] is None else f"{row['separation_deg']:.9f}°"
        hypothesis = ('E: correspondencia simbólica compatible con semejanza, complementariedad o espejo; '
                      'esas alternativas no se distinguen por este contacto.' if row['matched'] else
                      'E: esta regla descriptiva no identifica coincidencia; no demuestra incompatibilidad ni ausencia de vínculo.')
        parts.append(f"Ficha {row['feature_id']} ({row['data_ref']}): A.{a['layer']}.{a['object']} en {a['sign']} ↔ "
            f"B.{b['layer']}.{b['object']} en {b['sign']}. A: separación {separation}; relaciones por signo "
            f"{row['sign_relation']}; mismo signo {row['same_sign']}; mismo nakṣatra {row['same_nakshatra']}; "
            f"mismo pāda {row['same_pada']}; mismo regente nakṣatra {row['same_nakshatra_lord']}. "
            f"B: {contacts}; orbe declarado {row['orb_limit_deg']}; paquete {row['dependency_bundle']}. "
            "C: no hay pasaje verificado que convierta esta geometría en diagnóstico de una díada. D: uso no documentado. "
            f"{hypothesis} Contraevidencia: alerta por signo {row['counterevidence']['sign_relation_flag']}, "
            "sin incompatibilidad factual demostrada. Estado INSUFFICIENT; componente estructural, no pronóstico.")
    for event in model['events']:
        parts.append(f"Evento {event['event_id']}: {event['event_timestamp']}. Activación descriptiva de "
                     f"{event['structural_anchor_count']} anclajes; tránsito {event['transit_status']}; "
                     "raíces temporales independientes 0; no acredita fase, reciprocidad ni decisiones.")
        for person in event['persons']:
            if person['status'] != 'IMPLEMENTED':
                parts.append(f"Sujeto {person['person']}: Vimśottarī NOT_EVALUABLE; {person.get('reason')}.")
                continue
            for level in ('maha','antara','pratyantara'):
                period = person['periods'][level]
                roles = person['active_significators'][level]
                parts.append(f"Sujeto {person['person']} · {level}: {period['lord']}, intervalo UTC "
                    f"[{period['start']}, {period['end']}). Significadores activados: {', '.join(roles) or 'ninguno en la lista declarada'}. "
                    f"Convención anual {person['periods']['year_days']} días; técnica Rao 16.2–16.3; "
                    "la identificación de señor/período es A/B y su lectura diádica permanece E.")
        for contact in event['transit_contacts']:
            parts.append(f"Tránsito {contact['transit']} sobre sujeto {contact['person']}, objetivo "
                f"{contact['target_longitude']:.9f}°, ángulo {contact['angle']}°, residual {contact['residual_deg']:.9f}°. "
                f"Arquitectura: {', '.join(contact['structural_feature_refs'])}; dependencias: "
                f"{', '.join(contact['root_dependency_refs'])}. Activación temporal descriptiva E, sin nueva raíz estructural.")
    for index, sensitivity in enumerate(model['sensitivity']):
        parts.append(f"Sensibilidad del sujeto {index+1}: {sensitivity['time_state']}, "
            f"{sensitivity['ayanamsha_state']}; estabilidad continua no demostrada.")
        for run in sensitivity['runs']:
            parts.append(f"Muestra {run['axis']} {run.get('value',run.get('value_minutes'))}: "
                f"estable {run['stable']}; familias alteradas {', '.join(run['changed_families']) or 'ninguna'}.")
    for annual in model['annual']:
        saham = annual['vivaha_saham']
        parts.append(f"Carta anual: recibo declarado {annual['return_source_ref']}; Vivāha Sahama "
            f"{saham['longitude']:.9f}°, {saham['day_or_night']}, corrección {saham['correction_deg']}°. "
            "El recibo no se autentica aquí; no se infiere matrimonio ni fecha de decisión.")
    for entry in model['sources']['entries']:
        parts.append(f"Fuente de método {entry['id']}: {model['sources']['author']}, {model['sources']['work']} "
            f"({model['sources']['date']}), {entry['passage']}; alcance: {entry['supports']}. "
            "No autoriza discriminación ontológica ni equivalencia con la sinastría experimental ALMAS.")
    return '\n\n'.join(parts) + '\n'
