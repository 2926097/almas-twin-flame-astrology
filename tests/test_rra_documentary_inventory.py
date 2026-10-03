"""Mutaciones de riesgo documental: no son pruebas de eficacia de RRA."""
from copy import deepcopy
import importlib.util
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rra_documentary', ROOT / 'scripts/validate_rra_documentary_inventory.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class DocumentaryInventoryTests(unittest.TestCase):
    def setUp(self):
        self.data = deepcopy(validator.load_bundle(ROOT))

    def reject(self):
        with self.assertRaises(ValueError):
            validator.validate_bundle(self.data)

    def synthetic_conflict(self):
        case = self.data['archival']['pilot_candidates'][0]
        key = 'SYNTHETIC_DATE_DISAGREEMENT'
        ids = ['SYNTHETIC_UNIT_A', 'SYNTHETIC_UNIT_B']
        dates = ['2000-01-01', '2000-01-02']
        coverage = self.data['coverage']
        for uid, date in zip(ids, dates):
            unit = deepcopy(coverage['units'][0])
            unit.update(unit_id=uid, candidate_id=case['id'], unit_type='SYNTHETIC_TEST_ONLY',
                        fact_claims=[dict(fact_key=key, date_assertion=date)])
            coverage['units'].append(unit)
        coverage['unit_count'] += 2
        coverage['event_conflicts'] = [dict(fact_key=key, candidate_id=case['id'], unit_refs=ids,
            asserted_dates=dates, resolved_event_date=None, status='EVENT_DATE_CONFLICT_PENDING_ADJUDICATION')]
        case['events'].append(dict(fact_key=key, date_assertion=dates[0], source_refs=case['source_refs'],
            local_time=None, utc_instant=None, resolved_event_date=None,
            adjudication_status='EVENT_DATE_CONFLICT_PENDING_ADJUDICATION',
            alternative_date_assertions=[dict(date=dates[1])]))
        self.data['readiness']['documentary_event_conflicts_pending'] = 1

    def test_retired_candidate_reintroduced(self):
        case = self.data['archival']['pilot_candidates'][-1]
        case['id'] = 'P05'
        self.reject()

    def test_replacement_target_missing(self):
        self.data['archival']['replacement_history'][0]['replacement_candidate_id'] = 'ABSENT'
        self.reject()

    def test_current_bundle(self):
        validator.validate_bundle(self.data, ROOT)

    def test_synthetic_conflict_is_valid_baseline(self):
        self.synthetic_conflict()
        validator.validate_bundle(self.data)

    def test_silent_conflict_resolution(self):
        self.synthetic_conflict()
        self.data['coverage']['event_conflicts'][0]['resolved_event_date'] = '2000-01-02'
        self.reject()

    def test_conflict_deleted(self):
        self.synthetic_conflict()
        self.data['coverage']['event_conflicts'] = []
        self.reject()

    def test_alternative_erased_from_pilot(self):
        self.synthetic_conflict()
        self.data['archival']['pilot_candidates'][0]['events'][-1]['alternative_date_assertions'] = []
        self.reject()

    def test_unsupported_negative(self):
        self.data['coverage']['units'][0]['control_eligible'] = True
        self.reject()

    def test_holdout_leak(self):
        self.data['archival']['pilot_candidates'][0]['holdout_eligible'] = True
        self.reject()

    def test_shared_person_split(self):
        self.data['initial']['pilot_candidates'][2]['person_component'] = 'WRONG_SPLIT'
        self.reject()

    def test_unknown_source(self):
        self.data['archival']['pilot_candidates'][0]['source_refs'].append('UNKNOWN')
        self.reject()

    def test_false_original_read_count(self):
        self.data['coverage']['original_manuscripts_read'] = 1
        self.reject()

    def test_confirmatory_promotion(self):
        self.data['readiness']['confirmatory_execution_allowed'] = True
        self.reject()

    def test_corrupt_payload_cli_fails(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            path = Path(directory) / validator.FILES['initial']
            path.parent.mkdir(parents=True)
            path.write_text('{bad json')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_rra_documentary_inventory.py'),
                                     '--root', directory], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('FAIL', result.stdout)
            self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
