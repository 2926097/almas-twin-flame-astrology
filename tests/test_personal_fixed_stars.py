"""Integración personal y bloqueos reales de precisión/procedencia."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from test_personal_request_pipeline import FakePersonalBackend, request, provenance
from almas_tfa.astrology_backend import AstronomyBackendNotEvaluableError
from almas_tfa.personal_request_pipeline import build_personal_report_context_from_request
from almas_tfa.personal_reporting import validate_personal_canonical
from almas_tfa.personal_fixed_stars import render_personal_fixed_stars
from almas_tfa.production_astronomy import (_canon_fingerprint, _canonical_json_fingerprint,
                                           load_fixed_star_paran_policy)

ROOT = Path(__file__).resolve().parents[1]


class Backend(FakePersonalBackend):
    def calculate_fixed_star_parans(self, natal):
        result = json.loads((ROOT / 'tests/fixtures/fixed_star_paran/synthetic-result.json').read_text())
        result.update(subject_id=natal.subject_id, backend_provenance=provenance(),
                      policy_fingerprint_sha256=_canonical_json_fingerprint(load_fixed_star_paran_policy()))
        result['canon']['fingerprint_sha256'] = _canon_fingerprint(result['canon']['entries'])
        return result


class PersonalStarsTests(unittest.TestCase):
    def context(self, quality='A', backend=None):
        data = request(quality); data['fixed_stars'] = {'enabled': True}
        return build_personal_report_context_from_request(data, backend or Backend())

    def test_layer_is_minimized_and_enters_document_model(self):
        context = self.context(); canonical = context['personal_canonical_analysis']
        layer = canonical['secondary_layers']['fixed_stars']
        self.assertTrue(validate_personal_canonical(canonical)['reportable'])
        self.assertNotIn('metadata', layer)
        self.assertNotIn('jd1', layer['parans'][0])
        self.assertNotIn('natal_jd', layer['natal_angular_contacts'][0])
        serialized = json.dumps(layer)
        for field in ('birth_date', 'birth_time', 'utc_instant', 'crossing_jd'):
            self.assertNotIn(field, serialized)
        self.assertEqual(layer['structural_role'], 'SUPPORT_ONLY')
        self.assertIn('Brady', render_personal_fixed_stars(layer))

    def test_invalid_quality_is_blocked(self):
        with self.assertRaises(AstronomyBackendNotEvaluableError): self.context('C')

    def test_missing_capability_is_blocked(self):
        with self.assertRaises(AstronomyBackendNotEvaluableError): self.context(backend=FakePersonalBackend())

    def test_foreign_subject_and_scoring_mutation_are_blocked(self):
        canonical = self.context()['personal_canonical_analysis']
        for key, value in [('subject_id', 'OTHER'), ('structural_role', 'CORE')]:
            modified = deepcopy(canonical); modified['secondary_layers']['fixed_stars'][key] = value
            self.assertFalse(validate_personal_canonical(modified)['reportable'])

    def test_personal_schema_rejects_absolute_birth_metadata(self):
        from jsonschema import Draft202012Validator
        layer = self.context()['personal_canonical_analysis']['secondary_layers']['fixed_stars']
        schema = json.loads((ROOT / 'schemas/personal-fixed-star-paran.schema.json').read_text())
        validator = Draft202012Validator(schema); validator.validate(layer)
        layer['metadata'] = {'birth_time': '12:30'}
        self.assertTrue(list(validator.iter_errors(layer)))

    def test_empty_contacts_are_reported_as_negative(self):
        layer = self.context()['personal_canonical_analysis']['secondary_layers']['fixed_stars']
        layer['parans'] = []; layer['natal_angular_contacts'] = []
        self.assertIn('No se encontraron', render_personal_fixed_stars(layer))


if __name__ == '__main__': unittest.main()
