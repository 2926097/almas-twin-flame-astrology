"""Pruebas del endpoint candidato, sin usar una cohorte real."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from almas_tfa.return_activation import digest
from almas_tfa.return_external_evaluation import evaluate_study, exact_date_indicator

ROOT = Path(__file__).resolve().parents[1]


class ExternalEndpointTests(unittest.TestCase):
    def setUp(self):
        self.result = json.loads((ROOT / 'examples/return-activation.synthetic.json').read_text())['expected_output']
        event = deepcopy(self.result['evaluation_input']['events'][0])
        control = deepcopy(event); control.update(event_id='C', fact_key='CONTROL', event_datetime='2020-01-25T00:00:00Z')
        self.case = dict(case_id='A', person_refs=['P1', 'P2'], component_id='G1',
                         execution_sha256=digest(self.result), observations=[
            dict(observation_id='E', kind='EVENT', date_input=event, coverage_refs=['SYNTHETIC'], selection_stratum='SYNTHETIC'),
            dict(observation_id='C', kind='CONTROL', date_input=control, coverage_refs=['SYNTHETIC'], selection_stratum='SYNTHETIC')])
        self.study = dict(mode='SYNTHETIC_TEST_ONLY', return_policy_hash=self.result['return_policy_hash'], cases=[self.case])

    def run_study(self):
        return evaluate_study(self.study, {c['case_id']: self.result for c in self.study['cases']})

    def test_exact_indicator_not_active_cycle(self):
        output = self.run_study()
        self.assertEqual(output['primary_difference'], 1)
        self.assertEqual(output['cases'][0]['counts']['CONTROL']['positive'], 0)
        self.assertIsNone(output['p_value'])
        self.assertFalse(output['confirmatory_inference_allowed'])

    def test_no_missing_to_zero_even_without_returns(self):
        result = deepcopy(self.result); result['returns'] = []
        event = deepcopy(self.case['observations'][0]['date_input']); event['event_datetime'] = '2030-01-01T00:00:00Z'
        self.assertIsNone(exact_date_indicator(result, event)['indicator'])

    def test_uncertainty_boundary_is_missing(self):
        event = deepcopy(self.case['observations'][0]['date_input'])
        event.update(event_datetime='2020-01-18T00:00:00Z', uncertainty_hours=1)
        self.assertIsNone(exact_date_indicator(self.result, event)['indicator'])

    def test_search_edges_require_full_exact_window_even_without_returns(self):
        result = deepcopy(self.result); result['returns'] = []
        event = deepcopy(self.case['observations'][0]['date_input'])
        event['event_datetime'] = '2020-01-02T00:00:00Z'
        self.assertIsNone(exact_date_indicator(result, event)['indicator'])
        event['event_datetime'] = '2020-01-10T00:00:00Z'
        self.assertEqual(exact_date_indicator(result, event)['indicator'], 0)

    def test_contact_duplication_does_not_add_votes(self):
        event = self.case['observations'][0]['date_input']
        self.result['returns'] *= 3
        self.assertEqual(exact_date_indicator(self.result, event)['indicator'], 1)

    def test_identity_only_is_not_positive(self):
        for row in self.result['returns']:
            row['contacts'] = [c for c in row['contacts'] if c['automatic_identity_contact']]
        self.assertEqual(exact_date_indicator(self.result, self.case['observations'][0]['date_input'])['indicator'], 0)

    def test_shared_person_split_rejected(self):
        second = deepcopy(self.case); second.update(case_id='B', component_id='G2')
        self.study['cases'].append(second)
        with self.assertRaises(ValueError): self.run_study()

    def test_duplicate_fact_and_same_date_rejected(self):
        self.case['observations'][1]['date_input']['fact_key'] = self.case['observations'][0]['date_input']['fact_key']
        with self.assertRaises(ValueError): self.run_study()

    def test_empty_event_denominator_is_none(self):
        self.case['observations'] = self.case['observations'][1:]
        self.assertIsNone(self.run_study()['primary_difference'])

    def test_equal_component_weight_not_equal_event_weight(self):
        second = deepcopy(self.case); second.update(case_id='B', person_refs=['P3', 'P4'], component_id='G2')
        second['observations'][0]['date_input'].update(fact_key='OTHER', event_datetime='2020-01-24T00:00:00Z')
        second['observations'][1]['date_input']['fact_key'] = 'OTHER_CONTROL'
        self.study['cases'].append(second)
        self.assertEqual(self.run_study()['primary_difference'], .5)

    def test_tamper_and_confirmatory_mode_rejected(self):
        self.case['execution_sha256'] = '0' * 64
        with self.assertRaises(ValueError): self.run_study()
        self.study['mode'] = 'FROZEN_CONFIRMATORY'
        with self.assertRaises(ValueError): self.run_study()

    def test_blocked_execution_is_missing(self):
        self.result['execution_status'] = 'partial'
        self.assertIsNone(exact_date_indicator(self.result, self.case['observations'][0]['date_input'])['indicator'])


if __name__ == '__main__': unittest.main()
