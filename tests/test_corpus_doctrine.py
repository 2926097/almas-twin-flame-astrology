"""Pruebas de alcance doctrinal y resistencia a promociones por acumulación de citas."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from almas_tfa.corpus_doctrine import assess_corpus_claim, corpus_source_trace, load_corpus_doctrine_policy
from almas_tfa.surrender_vestal import assess_surrender_vestal, validate_surrender_vestal_result
from test_surrender_vestal import request, active_request, add_activation

ROOT = Path(__file__).resolve().parents[1]


class CorpusDoctrineTests(unittest.TestCase):
    def test_vesta_never_creates_celibacy(self):
        data = request(); add_activation(data)
        data['doctrinal_source_refs'] = ['homeric_hymn_hestia_24', 'gellius_attic_nights_1_12']
        result = assess_surrender_vestal(data)
        self.assertEqual(result['sexual_observations']['celibacy']['status'], 'NOT_EVALUABLE')
        self.assertEqual(result['vestal_withdrawal']['state'], 'NOT_EVALUABLE')

    def test_surrender_preserves_action_in_ramanuja(self):
        refs = ['ramanuja_gita_18_66']
        for concept in ['RELINQUISH_FRUIT_ATTACHMENT', 'CONTINUE_RIGHT_ACTION']:
            claim = assess_corpus_claim(concept, refs)
            self.assertEqual(claim['status'], 'SUPPORTED')
            self.assertEqual(claim['scope'], 'DOCTRINAL_ATTRIBUTION')
        result = assess_surrender_vestal(active_request())
        self.assertEqual(result['vestal_withdrawal']['status'], 'SUPPORTED')

    def test_kardec_contradicts_half_soul_only_in_its_doctrine(self):
        refs = ['kardec_spirits_affinity_298_303']
        self.assertEqual(assess_corpus_claim('SPLIT_SOUL', refs)['status'], 'CONTRADICTED')
        actual = assess_corpus_claim('SPLIT_SOUL', refs, scope='CASE_ONTOLOGY')
        self.assertEqual(actual['status'], 'INSUFFICIENT')
        self.assertEqual(actual['ontology_effect'], 'NONE')

    def test_petach_and_luria_do_not_duplicate_root(self):
        trace = corpus_source_trace(['petach_einayim_sotah_2a_2', 'vital_shaar_hagilgulim_20_zivug'])
        self.assertEqual(len(trace['dependency_groups']), 1)
        self.assertEqual(trace['dependency_groups'][0]['dependency_root'], 'LURIANIC_ZIVUG_GILGUL')
        self.assertFalse(trace['independence_validated'])

    def test_classical_chiron_not_modern_wounded_healer(self):
        refs = ['pindar_pythian_3_chiron', 'apollodorus_library_chiron_wound']
        self.assertEqual(assess_corpus_claim('CHIRON_MYTH_HEALER', refs)['status'], 'SUPPORTED')
        self.assertEqual(assess_corpus_claim('CHIRON_ASTROLOGICAL_WOUNDED_HEALER', refs)['status'], 'INSUFFICIENT')
        trace = corpus_source_trace(refs + ['reinhart_chiron_healing_journey_2010', 'stein_essence_application_chiron'])
        self.assertEqual({g['dependency_root'] for g in trace['dependency_groups']}, {'CHIRON_CLASSICAL_MYTH', 'CHIRON_MODERN_ASTROLOGY'})

    def test_spiritual_marriage_never_creates_dyadic_union(self):
        refs = ['teresa_interior_castle_seventh']
        self.assertEqual(assess_corpus_claim('INTERNAL_OR_TRANSPERSONAL_UNION', refs, scope='PROJECT_CORRESPONDENCE')['status'], 'COMPATIBLE')
        self.assertEqual(assess_corpus_claim('EXTERNAL_DYADIC_UNION', refs)['status'], 'NOT_EVALUABLE')

    def test_preincarnational_choice_not_bilateral_contract(self):
        refs = ['plato_republic_er_choice', 'kardec_spirits_book_choice_trials']
        self.assertEqual(assess_corpus_claim('PREINCARNATIONAL_CHOICE', refs)['status'], 'SUPPORTED')
        self.assertEqual(assess_corpus_claim('DYADIC_SOUL_CONTRACT', refs)['status'], 'INSUFFICIENT')

    def test_every_forbidden_upgrade_blocked(self):
        for upgrade in load_corpus_doctrine_policy()['forbidden_upgrades']:
            with self.subTest(upgrade=upgrade):
                result = assess_corpus_claim('PREINCARNATIONAL_CHOICE', ['plato_republic_er_choice'], proposed_upgrade=upgrade)
                self.assertEqual(result['status'], 'INSUFFICIENT')
                self.assertEqual(result['blocked_upgrades'], [upgrade])
                self.assertFalse(result['l3_substituted'])
                self.assertFalse(result['pu_created'])

    def test_metadata_cannot_support_direct_doctrine(self):
        self.assertEqual(assess_corpus_claim('CONIUNCTIO', ['jung_mysterium_coniunctionis'])['status'], 'INSUFFICIENT')
        self.assertEqual(assess_corpus_claim('MODERN_NODAL_REINCARNATION', ['schulman_nodes_reincarnation_1975'])['status'], 'INSUFFICIENT')

    def test_modern_author_method_is_not_primary_doctrine(self):
        claim = assess_corpus_claim('CHIRON_INTEGRATION_PROCESS', ['stein_essence_application_chiron'])
        self.assertEqual(claim['status'], 'INSUFFICIENT')
        self.assertEqual(claim['assertions'][0]['epistemic_class'], 'B_TECHNIQUE')

    def test_empty_unknown_and_invalid_scope(self):
        self.assertEqual(assess_corpus_claim('SPLIT_SOUL', [])['status'], 'NOT_EVALUABLE')
        for kwargs in [{'scope':'ROMANTIC_PROOF'}, {'proposed_upgrade':'UNKNOWN'}]:
            with self.assertRaises(ValueError): assess_corpus_claim('SPLIT_SOUL', [], **kwargs)
        with self.assertRaises(ValueError): corpus_source_trace(['invented-source'])
        with self.assertRaises(ValueError): assess_corpus_claim('invented-concept', [])

    def test_duplicate_citations_have_no_effect(self):
        refs = ['plato_republic_er_choice']
        self.assertEqual(assess_corpus_claim('PREINCARNATIONAL_CHOICE', refs), assess_corpus_claim('PREINCARNATIONAL_CHOICE', refs * 30))

    def test_doctrine_does_not_change_personal_state_or_scores(self):
        data = active_request(); add_activation(data)
        baseline = assess_surrender_vestal(data)
        data['doctrinal_source_refs'] = [s['id'] for s in load_corpus_doctrine_policy()['source_snapshots']]
        result = assess_surrender_vestal(data)
        for key in baseline:
            if key != 'traceability': self.assertEqual(baseline[key], result[key], key)
        validate_surrender_vestal_result(result)
        result['traceability']['doctrinal_correspondence']['source_count_adds_weight'] = True
        with self.assertRaises(ValueError): validate_surrender_vestal_result(result)

    def test_registry_and_snapshot_consistency(self):
        registry = json.loads((ROOT/'reference/source-registry.json').read_text())
        sources = {s['id']:s for s in registry['entries']}
        policy = load_corpus_doctrine_policy()
        for snapshot in policy['source_snapshots']:
            self.assertEqual(snapshot, sources[snapshot['id']])
        for assertion in policy['assertions']:
            self.assertIn(assertion['source_id'], sources)
            self.assertIn(assertion['concept_id'], policy['concept_ceilings'])

    def test_policy_schema_and_quantitative_preservation(self):
        from referencing import Registry, Resource
        schema=json.loads((ROOT/'schemas/corpus-doctrine-policy.schema.json').read_text())
        source_schema=json.loads((ROOT/'schemas/source-registry.schema.json').read_text())
        registry=Registry().with_resource('https://example.invalid/almas/source-registry.schema.json', Resource.from_contents(source_schema))
        Draft202012Validator(schema, registry=registry).validate(load_corpus_doctrine_policy())
        audit=json.loads((ROOT/'reference/corpus-expansion-audit-1.24.1.json').read_text())
        for path, expected in audit['preserved_code_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), expected, path)

    def test_all_source_and_concept_limits_present(self):
        for file, collection, schema in [('source-registry','entries','source-registry'), ('concept-registry','concepts','concept-registry')]:
            data=json.loads((ROOT/f'reference/{file}.json').read_text())
            Draft202012Validator(json.loads((ROOT/f'schemas/{schema}.schema.json').read_text())).validate(data)
            for item in data[collection]:
                self.assertTrue(item['inferential_ceiling'])
                self.assertTrue(item['forbidden_upgrades'])
        registry=json.loads((ROOT/'src/almas_tfa/data/discriminator-source-genealogy.json').read_text())
        Draft202012Validator(json.loads((ROOT/'schemas/discriminator-source-genealogy.schema.json').read_text())).validate(registry)

    def test_trace_schema_and_separate_layers(self):
        data=active_request();data['doctrinal_source_refs']=['ramanuja_gita_18_66']
        result=assess_surrender_vestal(data)
        Draft202012Validator(json.loads((ROOT/'schemas/surrender-vestal-output.schema.json').read_text())).validate(result)
        self.assertEqual(set(result['traceability']), {'documentary_behavior','doctrinal_correspondence','symbolic_astrological_activation'})
        self.assertEqual(result['traceability']['symbolic_astrological_activation']['signal_refs'], [])


if __name__ == '__main__':
    unittest.main()
