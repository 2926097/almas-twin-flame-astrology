"""Liminalidad y Moiras: hipótesis E optativas sobre raíces suministradas."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from importlib import resources
import json
from typing import Mapping

from .ssar import _index, assess_ssar_claim, run_ssar, validate_ssar_schema
from .ssar_families import _family, _group_refs


def _load(name: str) -> dict:
    return json.loads(resources.files('almas_tfa').joinpath('data', name).read_text(encoding='utf-8'))


def load_liminal_catalog() -> dict:
    return _load('ssar-liminal-moirai-catalog.json')


def load_liminal_policy() -> dict:
    policy = _load('ssar-liminal-moirai-development-policy.json')
    validate_ssar_schema(policy, 'Policy')
    return policy


def liminal_catalog_hash() -> str:
    value = json.dumps(load_liminal_catalog(), sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    return sha256(value.encode('utf-8')).hexdigest()


def build_liminal_request(request: Mapping) -> dict:
    validate_ssar_schema(request, 'F5Request')
    if not request['enabled']:
        return {'enabled': False}
    catalog = load_liminal_catalog()
    entries = _index(catalog['entries'], 'point_id')
    _index(request.get('observations', []), 'id')
    appearances, units, seen = [], [], set()
    for observation in request.get('observations', []):
        technique, subject = observation['technique'], observation['subject_id']
        if (technique == 'SYNASTRY') != (subject in {'A', 'B'}):
            raise ValueError('Contexto de carta incompatible con la técnica.')
        geometry = observation['geometry']
        if geometry:
            key = (observation['point_id'], subject, technique, geometry['frame'], geometry['target_id'],
                   geometry['longitude'] % 360, geometry['target_longitude'] % 360,
                   tuple(sorted(observation['core_root_refs'])))
            if key in seen:
                raise ValueError('El mismo contacto requiere una aparición compartida.')
            seen.add(key)
        entry = entries[observation['point_id']]
        appearance = {key: deepcopy(observation[key]) for key in
                      ('id', 'point_id', 'geometry', 'robustness', 'core_root_refs', 'core_anchor_search_complete')}
        appearance.update(kind='NAMED_SMALL_BODY')
        appearance.update({key: deepcopy(entry[key]) for key in ('provenance', 'semantic_basis', 'method')})
        appearances.append(appearance)
        units.append(dict(id='U:' + observation['id'], appearance_ref=observation['id'], technique=technique,
                          equivalence_key=observation['evidence_key']))
    return dict(enabled=True, sources=deepcopy(catalog['sources']), appearances=appearances,
                core_roots=deepcopy(request.get('core_roots', [])), units=units, edges=deepcopy(request.get('edges', [])))


def _reused_contacts(request: Mapping) -> list[dict]:
    observations = _index(request.get('observations', []), 'id')
    seen, output = set(), []
    for record in request.get('existing_contacts', []):
        ref = record['appearance_ref']
        key = (record['artifact_ref'], record['evidence_key'])
        if key in seen or ref not in observations:
            raise ValueError('Enlace heredado duplicado o referencia rota.')
        seen.add(key)
        observation = observations[ref]
        for field in ('point_id', 'subject_id', 'technique', 'evidence_key', 'core_anchor_search_complete', 'robustness'):
            if record[field] != observation[field]:
                raise ValueError('El enlace heredado no reproduce el contexto y perturbaciones.')
        if set(record['core_root_refs']) != set(observation['core_root_refs']):
            raise ValueError('El enlace heredado no reproduce los anclajes.')
        a, b = record['geometry'], observation['geometry']
        if a is None or b is None or a['frame'] != b['frame'] or a['target_id'] != b['target_id'] or any(
            a[field] % 360 != b[field] % 360 for field in ('longitude', 'target_longitude')):
            raise ValueError('El enlace heredado no reproduce el contacto geométrico.')
        output.append(dict(appearance_ref=ref, artifact_ref=record['artifact_ref'], upstream_layer=record['upstream_layer'],
                           contributes_new_evidence=False))
    return sorted(output, key=lambda item: (item['artifact_ref'], item['appearance_ref']))


def _complex(selection: Mapping, spec: Mapping, appearances: Mapping, ssar: Mapping,
             catalog: Mapping, policy: Mapping) -> dict:
    refs = selection['appearance_refs']
    if set(refs) - set(appearances):
        raise ValueError('Referencias de complejo rotas.')
    if any(appearances[ref]['point_id'] not in spec['members'] + spec['context_points'] for ref in refs):
        raise ValueError('El complejo incluye un cuerpo ajeno a su regla.')
    context = sorted(ref for ref in refs if appearances[ref]['point_id'] in spec['context_points'])
    members = sorted(set(refs) - set(context))
    components = []
    for point in spec['members']:
        point_refs = sorted(ref for ref in members if appearances[ref]['point_id'] == point)
        good = sorted(ref for ref in point_refs if appearances[ref]['qualification'] in {'QUALIFIED_SIGNIFICATOR', 'SECONDARY_SUPPORT'})
        components.append(dict(point_id=point, appearance_refs=point_refs, admissible_refs=good,
                               coverage='MISSING' if not point_refs else 'BLOCKED' if not good else 'SUPPLIED'))
    admitted = sorted(ref for c in components for ref in c['admissible_refs'])
    groups = _group_refs(admitted, ssar)
    roots = sorted({root for ref in admitted for root in appearances[ref]['core_root_refs']})
    qualified = any(appearances[ref]['qualification'] == 'QUALIFIED_SIGNIFICATOR' for ref in admitted)
    # No se confunde una búsqueda incompleta con ausencia geométrica.
    coverage = selection['search_complete'] and all(c['appearance_refs'] for c in components) and all(
        appearances[ref]['qualification'] != 'BLOCKED' for ref in members)
    robust_refs = {ref for ref in admitted if appearances[ref]['robustness'] and
                   appearances[ref]['robustness']['preserved_fraction'] >= appearances[ref]['robustness']['required_fraction']}
    geometric = all(set(c['admissible_refs']) & robust_refs for c in components)
    negative = [ref for c in components if c['appearance_refs'] and all(
        appearances[ref]['qualification'] == 'NO_CONTACT' for ref in c['appearance_refs']) for ref in c['appearance_refs']]
    rule = spec['rule_id']
    geometry = assess_ssar_claim(scope='STRUCTURAL_GEOMETRY', policy_ref=policy['policy_id'], rule_ref=rule,
                                coverage_sufficient=bool(coverage), positive_complete=bool(geometric),
                                compatible=bool(robust_refs), evidence_refs=members,
                                excluding_counterevidence_refs=negative,
                                counterevidence_evaluable=bool(negative) and selection['search_complete'])
    complete = bool(coverage and geometric and qualified and roots and
                    len(groups) >= catalog['complex_rule']['minimum_effective_groups'])
    functional = assess_ssar_claim(scope='FUNCTIONAL_INTERPRETATION', policy_ref=policy['policy_id'], rule_ref=rule,
                                  coverage_sufficient=bool(coverage), positive_complete=complete,
                                  compatible=bool(geometric and admitted), evidence_refs=admitted)
    blockers = []
    for condition, reason in ((coverage, 'ESSENTIAL_COMPONENT_OR_SEARCH_COVERAGE_MISSING'),
                              (geometric, 'ROBUST_COMPONENT_CONTACTS_NOT_MET'), (qualified, 'QUALIFIED_SIGNIFICATOR_MISSING'),
                              (roots, 'CORE_ANCHOR_MISSING'), (len(groups) >= 2, 'TWO_EFFECTIVE_GROUPS_NOT_MET')):
        if not condition:
            blockers.append(reason)
    sources = sorted({source for ref in members for source in appearances[ref]['source_refs']})
    return dict(id=spec['id'], members=list(spec['members']), appearance_refs=members, context_refs=context,
                component_coverage=components, admissible_refs=admitted, effective_group_refs=groups, core_root_refs=roots,
                qualified_complex=complete, assessments=dict(structural_geometry=geometry, functional_interpretation=functional,
                    temporal_activation=assess_ssar_claim(scope='TEMPORAL_ACTIVATION', policy_ref=policy['policy_id'], rule_ref=rule, coverage_sufficient=False),
                    documentary_correspondence=assess_ssar_claim(scope='DOCUMENTARY_STRUCTURAL_CORRESPONDENCE', policy_ref=policy['policy_id'], rule_ref=rule, coverage_sufficient=False)),
                blockers=sorted(blockers), epistemic_class='E_PROJECT_HYPOTHESIS', documentary_scope='STRUCTURAL',
                cluster_strength=None, source_refs=sources,
                inferential_limit='Patrón funcional E; no demuestra fase vivida, destino, reunión ni cierre irreversible. Eris es contexto, no contradicto automático.')


def run_liminal_moirai(request: Mapping) -> dict:
    if type(request.get('enabled')) is not bool:
        raise ValueError('Liminalidad y Moiras exige enabled explícito.')
    output = dict(schema_version='ssar-liminal-moirai-1.0-development', enabled=request['enabled'], catalog_id=None,
                  catalog_hash=None, policy_id=None, policy_status='DEVELOPMENT', ssar=run_ssar({'enabled': False}),
                  families=[], complexes=[], functional_notes=[], shared_contacts=[], reused_contacts=[], completion='NONE',
                  execution_status='not_run', coverage=[dict(layer='LIMINAL_MOIRAI', status='not_run', completion='NONE', reason='DISABLED', assessed_refs=[])],
                  external_validation_status='NOT_PERFORMED', structural_scoring_modified=False, ontology_effect='NONE', discriminator_effect='NONE')
    if not request['enabled']:
        return output
    effective = build_liminal_request(request)
    catalog, policy = load_liminal_catalog(), load_liminal_policy()
    ssar = run_ssar(effective, policy=policy)
    appearances = _index(ssar['appearances'], 'id')
    specs = _index(catalog['complexes'], 'id')
    _index(request.get('complexes', []), 'id')
    complexes = [_complex(s, specs[s['id']], appearances, ssar, catalog, policy) for s in request.get('complexes', [])]
    families = [_family(spec, appearances, ssar) for spec in catalog['families']]
    entries = _index(catalog['entries'], 'point_id')
    notes = []
    for appearance in ssar['appearances']:
        entry = entries[appearance['point_id']]
        notes.append(dict(appearance_ref=appearance['id'], function_id=entry['function_id'], epistemic_class='E_PROJECT_HYPOTHESIS',
                          interpretation=entry['interpretation'] if appearance['qualification'] in {'QUALIFIED_SIGNIFICATOR', 'SECONDARY_SUPPORT'} else None,
                          inferential_limit=entry['inferential_limit'], source_refs=appearance['source_refs'], documentary_status='NOT_EVALUABLE'))
    consumers = {}
    for item in families + complexes:
        for ref in item.get('appearance_refs', item.get('contact_refs', [])):
            consumers.setdefault(ref, []).append(item['id'])
    output.update(catalog_id=catalog['catalog_id'], catalog_hash=liminal_catalog_hash(), policy_id=policy['policy_id'], ssar=ssar,
                  families=families, complexes=sorted(complexes, key=lambda c: c['id']), functional_notes=notes,
                  shared_contacts=[dict(appearance_ref=ref, consumer_refs=sorted(set(ids)), contributes_new_evidence=False)
                                   for ref, ids in sorted(consumers.items()) if len(set(ids)) > 1],
                  reused_contacts=_reused_contacts(request), completion='PARTIAL' if appearances or complexes else 'NONE')
    supplied_moirai = bool(families[0]['contact_refs']) or any(c['appearance_refs'] for c in families[0]['components'])
    output.update(execution_status='executed' if appearances or complexes else 'not_run', coverage=deepcopy(ssar['coverage']) + [
        dict(layer='MOIRAI_CLUSTER', status='executed' if supplied_moirai else 'not_run',
             completion=('COMPLETE' if families[0]['coverage'] == 'SUPPLIED' else 'PARTIAL') if supplied_moirai else 'NONE',
             reason='SUPPLIED_COMPONENTS_ONLY' if supplied_moirai else 'NO_COMPONENTS_SUPPLIED', assessed_refs=families[0]['contact_refs']),
        dict(layer='STRUCTURAL_COMPLEXES', status='executed' if complexes else 'not_run', completion='COMPLETE' if complexes else 'NONE',
             reason='DECLARED_SELECTIONS_ONLY' if complexes else 'NO_SELECTIONS_SUPPLIED', assessed_refs=[c['id'] for c in complexes])])
    validate_ssar_schema(output, 'F5Result')
    return output


def validate_liminal_result(result: Mapping, *, request: Mapping) -> None:
    validate_ssar_schema(result, 'F5Result')
    if result != run_liminal_moirai(request):
        raise ValueError('La salida de liminalidad/Moiras no reproduce sus entradas y política.')
