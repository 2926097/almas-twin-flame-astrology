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

    def test_current_bundle(self):
        validator.validate_bundle(self.data, ROOT)

    def test_silent_conflict_resolution(self):
        self.data['coverage']['event_conflicts'][0]['resolved_event_date'] = '1895-07-26'
        self.reject()

    def test_conflict_deleted(self):
        self.data['coverage']['event_conflicts'] = []
        self.reject()

    def test_alternative_erased_from_pilot(self):
        self.data['archival']['pilot_candidates'][0]['events'][0]['alternative_date_assertions'] = []
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
