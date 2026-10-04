"""Features descriptivas, dependencias y temporalidad anclada a estructura."""
from hashlib import sha256
import json
from .geometry import longitude, sign_of, compute_nakshatra, LORDS
from .timing import compute_vimshottari, instant


def _fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _objects(chart, varga):
    if varga == 'D9':
        # No nakṣatras físicos ni orbes tropicales sobre grados divisionales.
        out = {p: dict(sign=v['sign'], longitude=None, dependency=['NODE_AXIS' if p in ('Rahu','Ketu') else p], family='VARGA')
               for p, v in chart['d9'].items()}
        for role in ('AK', 'DK'):
            p = chart['karakas']['roles'].get(role)
            if p:
                out[role] = {**out[p]}
        return out
    out = {p: dict(sign=v['sign'], longitude=v['longitude'], dependency=['NODE_AXIS' if p in ('Rahu','Ketu') else p], family='NAKSHATRA')
           for p, v in chart['d1'].items()}
    for role in ('AK', 'DK'):
        p = chart['karakas']['roles'].get(role)
        if p:
            out[role] = {**out[p], 'family': 'KARAKA'}
    for p in ('AL', 'UL', 'A7'):
        v = chart['arudhas'][p]
        out[p] = dict(sign=v['sign'], longitude=None, dependency=sorted(['Lagna', v['lord']]), family='ARUDHA')
    ka = chart['karakamsha']
    if ka['status'] == 'IMPLEMENTED':
        out['KARAKAMSHA'] = dict(sign=ka['sign'], longitude=None,
            dependency=['NODE_AXIS' if ka['source_body'] in ('Rahu','Ketu') else ka['source_body']], family='VARGA')
    bb = chart['bhrigu_bindu']
    if bb['status'] == 'IMPLEMENTED':
        out['BHRIGU_BINDU'] = dict(sign=sign_of(bb['longitude']), longitude=bb['longitude'],
            dependency=['Moon', 'NODE_AXIS'], family='BINDU')
    for p, v in chart['upagrahas'].items():
        out[p] = dict(sign=sign_of(v['longitude']), longitude=v['longitude'],
            dependency=['Sun'] if p in ('DHUMA', 'VYATIPATA', 'PARIVESHA', 'INDRACHAPA', 'UPAKETU')
            else ['Lagna', 'Sun', 'BIRTH_TIME'], family='UPAGRAHA')
    return out


def lunar_compatibility(a, b):
    """Datos lunares y Tara; las otras siete tablas requieren fuente/perfil verificado."""
    ma, mb = a['d1']['Moon'], b['d1']['Moon']
    na, nb = ma['nakshatra']['index'], mb['nakshatra']['index']
    tara_ab = ((nb - na) % 27 + 1 - 1) % 9 + 1
    tara_ba = ((na - nb) % 27 + 1 - 1) % 9 + 1
    sign_relation = ((mb['sign'] - ma['sign']) % 12 + 1,
                     (ma['sign'] - mb['sign']) % 12 + 1)
    components = {k: dict(status='NOT_EVALUABLE', score=None,
        reason='PROFILE_TABLE_AND_EXCEPTIONS_NOT_VERIFIED') for k in
        ('VARNA', 'VASHYA', 'TARA', 'YONI', 'GRAHA_MAITRI', 'GANA', 'BHAKUTA', 'NADI')}
    components['TARA'].update(status='OBSERVATIONAL', category_a_to_b=tara_ab, category_b_to_a=tara_ba)
    return dict(components=components, lunar_sign_relation=list(sign_relation),
        moon_lords=[LORDS[ma['sign']], LORDS[mb['sign']]], total_score=None,
        matrimonial_assessment='NOT_EVALUABLE', metaphysical_assessment='INSUFFICIENT',
        source_ref='ALMAS_EXPERIMENTAL_LUNAR_GEOMETRY', gender_roles_inferred=False,
        verification=dict(profile='UNSPECIFIED', source_tables_verified=False,
            exceptions_verified=False, orientation_verified=False, scored_components=0,
            blockers=['SELECT_PROFILE_AND_PRIMARY_SOURCE', 'VERIFY_ALL_COMPONENT_TABLES',
                      'VERIFY_EXCEPTIONS_AND_ORIENTATION', 'ADD_BOUNDARY_AND_GOLDEN_TESTS']))


def compute_vedic_synastry(a, b, *, orb_deg=3.0):
    longitude(orb_deg)
    if not 0 <= orb_deg <= 5:
        raise ValueError('Orbe exploratorio fuera de [0, 5] grados.')
    if a['configuration'] != b['configuration']:
        raise ValueError('Perfiles védicos incompatibles: comparar sólo con configuración idéntica.')
    features = []
    for va, vb in (('D1', 'D1'), ('D9', 'D9'), ('D1', 'D9'), ('D9', 'D1')):
        for oa, pa in _objects(a, va).items():
            for ob, pb in _objects(b, vb).items():
                relation = (pb['sign'] - pa['sign']) % 12 + 1
                reverse = (pa['sign'] - pb['sign']) % 12 + 1
                group = 'VED_' + (pa['family'] if pa['family'] == pb['family'] else 'CROSS_FAMILY')
                # Alias AK/DK no crean raíces independientes de su planeta natal.
                root = _fingerprint(dict(a=pa['dependency'], b=pb['dependency']))[:16]
                angular = pa['longitude'] is not None and pb['longitude'] is not None
                separation = abs((pa['longitude'] - pb['longitude'] + 180) % 360 - 180) if angular else None
                contacts = ([angle for angle in (0, 60, 90, 120, 180) if abs(separation - angle) <= orb_deg]
                            if angular else [])
                nka = compute_nakshatra(pa['longitude']) if angular else None
                nkb = compute_nakshatra(pb['longitude']) if angular else None
                same_nk = nka['index'] == nkb['index'] if angular else None
                features.append(dict(feature_id=f'VED.{va}.{oa}__{vb}.{ob}', object_a=oa, object_b=ob,
                    varga_a=va, varga_b=vb, sign_relation=[relation, reverse],
                    separation_deg=separation, angular_contacts_deg=contacts, same_nakshatra=same_nk,
                    same_pada=(same_nk and nka['pada']==nkb['pada']) if angular else None,
                    same_nakshatra_lord=nka['lord']==nkb['lord'] if angular else None,
                    same_sign=relation == 1, orb_deg=orb_deg if angular else None,
                    root_dependency_id=root, redundancy_group=group, input_dependencies=dict(a=pa['dependency'], b=pb['dependency']),
                    computational='IMPLEMENTED', empirical='NOT_PERFORMED',
                    confidence=dict(astronomical=[a['confidence']['astronomical'], b['confidence']['astronomical']],
                        birth_time=[a['confidence']['birth_time'],b['confidence']['birth_time']],
                        doctrinal='RELATIONAL_USE_EXPERIMENTAL', computational='IMPLEMENTED', empirical='NOT_PERFORMED'),
                    epistemic_class='E_PROJECT_HYPOTHESIS', doctrinal_class='EXPERIMENTAL_CROSS_SYSTEM', default_weight=0))
    matched = [f for f in features if f['same_sign'] or f['angular_contacts_deg'] or f['same_nakshatra']]
    risk = [f['feature_id'] for f in features if set(f['sign_relation']) in ({6, 8}, {2, 12})]
    bundle_count = len({f['root_dependency_id'] for f in matched})
    compatibility = lunar_compatibility(a, b)
    return dict(schema_version='ALMAS_VED_SYNASTRY_1', configuration=a['configuration'],
        chart_hashes=[_fingerprint(a), _fingerprint(b)], features=features,
        compatibility=compatibility, recurrence=dict(raw_matches=len(matched),
            dependency_bundles=bundle_count,
            independent_root_count=None, caution='COMMON_DERIVED_INPUTS_ARE_NOT_INDEPENDENT_EVIDENCE'),
        methodological_readiness=dict(
            descriptive=dict(feature_count=len(features), match_count=len(matched),
                dependency_bundle_count=bundle_count,
                match_rule=['same_sign', 'angular_contact_within_declared_orb', 'same_nakshatra'],
                bundle_rule='unique_root_dependency_id; deduplicates declared shared inputs only'),
            independence=dict(status='NOT_ESTABLISHED', independent_root_count=None,
                statistical_independence_demonstrated=False,
                interpretation='Dependency bundles are bookkeeping units, not independent observations.'),
            ashtakuta=dict(status='NOT_EVALUABLE', total_score=None,
                component_states={k:v['status'] for k,v in compatibility['components'].items()},
                verification=compatibility['verification']),
            ived=dict(status='UNVALIDATED', value=None, family_weights=None,
                gates=dict(preregistered=False, calibrated=False, external_validation=False),
                blockers=['DEFINE_OBSERVABLE_CONSTRUCT', 'PREREGISTER_FEATURES_AND_WEIGHTS',
                    'CALIBRATE_ON_INDEPENDENT_COHORT', 'TEST_INCREMENT_OUT_OF_SAMPLE'])),
        counterevidence=dict(traditional_risk_relations=risk,
            assessment='NOT_EVALUABLE', absence_is_counterevidence_only_with_preregistered_rule=True),
        ived=dict(status='UNVALIDATED', value=None, family_weights=None,
                  reason='NO_PREREGISTERED_CALIBRATION', descriptive_features=len(features),
                  gates=dict(preregistered=False, calibrated=False, external_validation=False)),
        canonical_effect=False, metaphysical_assessment='INSUFFICIENT')


def compute_vedic_event_activation(a, b, event, *, synastry=None, transit_chart=None, orb_deg=1.0):
    at = instant(event['timestamp'])
    structure = synastry or compute_vedic_synastry(a, b)
    if structure['chart_hashes'] != [_fingerprint(a), _fingerprint(b)]:
        raise ValueError('La estructura temporal no corresponde a las cartas recibidas.')
    if not 0 <= orb_deg <= 5:
        raise ValueError('Orbe de activación inválido.')
    if transit_chart is not None:
        if transit_chart['configuration'] != a['configuration']:
            raise ValueError('Tránsitos con configuración incompatible.')
        if not transit_chart.get('birth') or instant(transit_chart['birth']) != at:
            raise ValueError('La carta de tránsitos debe corresponder al instante del evento.')
    anchor_features = [f for f in structure['features'] if f['angular_contacts_deg'] or f['same_sign']]
    persons = []
    for label, chart in (('A', a), ('B', b)):
        if not chart.get('birth'):
            persons.append(dict(person=label, status='NOT_EVALUABLE', reason='BIRTH_INSTANT_MISSING'))
            continue
        periods = compute_vimshottari(chart['d1']['Moon']['longitude'], chart['birth'], at,
                                     chart['configuration']['year_days'])
        roles = chart['karakas']['roles']
        targets = {'AK': roles.get('AK'), 'DK': roles.get('DK'), 'Venus': 'Venus', 'Moon': 'Moon',
                   'Rahu': 'Rahu', 'Ketu': 'Ketu', 'UL_lord': LORDS[chart['arudhas']['UL']['sign']],
                   'A7_lord': LORDS[chart['arudhas']['A7']['sign']]}
        active = {level: [role for role, lord in targets.items() if lord == periods[level]['lord']]
                  for level in ('maha', 'antara', 'pratyantara')}
        persons.append(dict(person=label, status='IMPLEMENTED', periods=periods, active_significators=active))
    contacts = {}
    if transit_chart:
        for f in anchor_features:
            for label, chart, name in (('A', a, f['object_a']), ('B', b, f['object_b'])):
                objects = _objects(chart, f['varga_a'] if label == 'A' else f['varga_b'])
                natal = objects[name]['longitude']
                if natal is None:
                    continue
                for body in ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu'):
                    delta = abs((transit_chart['d1'][body]['longitude'] - natal + 180) % 360 - 180)
                    for angle in (0, 180):
                        if abs(delta - angle) <= orb_deg:
                            key = (label, natal, body, angle)
                            contact = contacts.setdefault(key, dict(person=label, target_longitude=natal, transit=body,
                                angle=angle, residual_deg=abs(delta-angle), structural_feature_refs=[], root_dependency_refs=[]))
                            if f['feature_id'] not in contact['structural_feature_refs']:
                                contact['structural_feature_refs'].append(f['feature_id'])
                            if f['root_dependency_id'] not in contact['root_dependency_refs']:
                                contact['root_dependency_refs'].append(f['root_dependency_id'])
    return dict(event_timestamp=at.isoformat(), persons=persons, structural_anchor_count=len(anchor_features),
                transit_contacts=list(contacts.values()), transit_status='IMPLEMENTED' if transit_chart else 'NOT_PERFORMED',
                temporal_independent_root_count=0, canonical_effect=False,
                epistemic_class='E_PROJECT_HYPOTHESIS', predicts_event=False,
                assessment='INSUFFICIENT', confirmatory_temporal_rule='NOT_PREREGISTERED')
