import copy
import unittest

from jsonschema import ValidationError
from almas_tfa.ssar_process_study import run_process_study, validate_process_study_result


def event(id='E1', role='START_EVENT', start='2030-01-03', end=None):
    return dict(event_id=id, fact_key='FACT:' + id, episode_id='EP1', subject_id='S1', role=role,
                start_date=start, end_date=end, precision_sufficient=True, verification_status='VERIFIED',
                source_refs=['synthetic:record:' + id], fact_interpretation_separated=True,
                continuity_observed=True if role == 'DURATION_INTERVAL' else None,
                from_state='STATE_A' if role == 'TRANSITION_EVENT' else None,
                to_state='STATE_B' if role == 'TRANSITION_EVENT' else None, data_class='DOCUMENT')


def claim(kind='INITIATION_OCCURRED'):
    return dict(id='C1', kind=kind, episode_id='EP1', subject_id='S1', window_start='2030-01-01',
                window_end='2030-01-31', as_of='2030-02-01', preregistered_before_chart_inspection=True,
                observation_coverage_complete=True, event_refs=['E1'],
                minimum_days=5 if kind == 'DURATION_WITHIN_BOUNDS' else None,
                maximum_days=10 if kind == 'DURATION_WITHIN_BOUNDS' else None)


def fixture(kind='INITIATION_OCCURRED'):
    roles = dict(INITIATION_OCCURRED='START_EVENT', DURATION_WITHIN_BOUNDS='DURATION_INTERVAL',
                 CLOSURE_PERSISTED_IN_WINDOW='CLOSURE_EVENT', TRANSITION_OCCURRED='TRANSITION_EVENT',
                 DISCORD_FREE_WINDOW='DISCORD_EVENT')
    e = event(role=roles[kind], end='2030-01-10' if kind == 'DURATION_WITHIN_BOUNDS' else None)
    return dict(events=[e], claims=[claim(kind)])


def result(request):
    return run_process_study(request)['claims'][0]


class SSARProcessStudyTests(unittest.TestCase):
    def test_four_event_roles_positive_are_standalone_without_astrological_promotion(self):
        for kind in ('INITIATION_OCCURRED', 'DURATION_WITHIN_BOUNDS', 'CLOSURE_PERSISTED_IN_WINDOW', 'TRANSITION_OCCURRED'):
            request = fixture(kind); output = run_process_study(request)
            self.assertEqual(output['claims'][0]['assessment']['status'], 'SUPPORTED')
            self.assertEqual(output['integration_status'], 'STANDALONE_STUDY_CONTRACT_NOT_M27')
            for key in ('astrological_effect', 'documentary_correspondence_effect', 'ontology_effect'):
                self.assertEqual(output[key], 'NONE')
            validate_process_study_result(output, request=request)

    def test_known_fact_occurrence_supported_even_with_incomplete_window_coverage(self):
        for kind in ('INITIATION_OCCURRED', 'TRANSITION_OCCURRED', 'DURATION_WITHIN_BOUNDS'):
            request = fixture(kind); request['claims'][0]['observation_coverage_complete'] = False
            self.assertEqual(result(request)['assessment']['status'], 'SUPPORTED')

    def test_all_five_claims_unknown_precision_sources_verification_and_mixed_fact_block(self):
        for kind in ('INITIATION_OCCURRED', 'DURATION_WITHIN_BOUNDS', 'CLOSURE_PERSISTED_IN_WINDOW', 'TRANSITION_OCCURRED', 'DISCORD_FREE_WINDOW'):
            for field, value in (('precision_sufficient', None), ('verification_status', 'PENDING'),
                                 ('source_refs', []), ('fact_interpretation_separated', False), ('start_date', None)):
                request = fixture(kind); request['events'][0][field] = value
                if field == 'start_date': request['events'][0]['end_date'] = None
                self.assertEqual(result(request)['assessment']['status'], 'NOT_EVALUABLE')

    def test_self_reports_and_interpretations_do_not_verify_external_occurrence(self):
        for cls in ('SELF_REPORT', 'INTERPRETATION'):
            request = fixture(); request['events'][0]['data_class'] = cls
            self.assertEqual(result(request)['assessment']['status'], 'NOT_EVALUABLE')

    def test_duration_requires_observed_continuity_not_just_endpoints(self):
        request = fixture('DURATION_WITHIN_BOUNDS')
        request['events'][0]['continuity_observed'] = False
        self.assertEqual(result(request)['assessment']['status'], 'NOT_EVALUABLE')

    def test_duration_elapsed_days_and_inclusive_bounds(self):
        for minimum, maximum in ((7, 7), (0, 7), (7, 20)):
            request = fixture('DURATION_WITHIN_BOUNDS')
            request['claims'][0].update(minimum_days=minimum, maximum_days=maximum)
            output = result(request)
            self.assertEqual(output['duration_days'], 7)
            self.assertEqual(output['assessment']['status'], 'SUPPORTED')

    def test_duration_outside_bounds_contradicts_specific_measurement(self):
        request = fixture('DURATION_WITHIN_BOUNDS'); request['claims'][0].update(minimum_days=8, maximum_days=10)
        self.assertEqual(result(request)['assessment']['status'], 'CONTRADICTED')
        self.assertEqual(result(request)['contradicting_event_refs'], ['E1'])

    def test_duration_missing_bounds_is_not_evaluable_even_with_complete_absence(self):
        request = fixture('DURATION_WITHIN_BOUNDS'); request['claims'][0]['minimum_days'] = None
        self.assertEqual(result(request)['assessment']['status'], 'NOT_EVALUABLE')
        request['events'] = []; request['claims'][0]['event_refs'] = []
        self.assertEqual(result(request)['assessment']['status'], 'NOT_EVALUABLE')

    def test_conflicting_duration_measurements_are_insufficient_not_best_fit(self):
        request = fixture('DURATION_WITHIN_BOUNDS')
        request['events'].append(event('E2', 'DURATION_INTERVAL', '2030-01-03', '2030-01-12'))
        request['claims'][0]['event_refs'].append('E2')
        output = result(request)
        self.assertEqual(output['assessment']['status'], 'INSUFFICIENT')
        self.assertIsNone(output['duration_days'])

    def test_transition_requires_two_distinct_documented_states(self):
        for change in ('missing', 'same'):
            request = fixture('TRANSITION_OCCURRED')
            request['events'][0]['to_state'] = None if change == 'missing' else 'STATE_A'
            self.assertEqual(result(request)['assessment']['status'], 'NOT_EVALUABLE')

    def test_complete_observed_absence_contradicts_occurrence_only_after_window(self):
        for kind in ('INITIATION_OCCURRED', 'CLOSURE_PERSISTED_IN_WINDOW', 'TRANSITION_OCCURRED', 'DURATION_WITHIN_BOUNDS'):
            request = fixture(kind); request['events'] = []; c = request['claims'][0]; c['event_refs'] = []
            self.assertEqual(result(request)['assessment']['status'], 'CONTRADICTED')
            c['as_of'] = '2030-01-15'
            self.assertEqual(result(request)['assessment']['status'], 'NOT_EVALUABLE')
            c['as_of'] = '2030-02-01'; c['observation_coverage_complete'] = False
            self.assertEqual(result(request)['assessment']['status'], 'NOT_EVALUABLE')

    def test_no_discord_only_supported_in_closed_completely_observed_window(self):
        request = fixture('DISCORD_FREE_WINDOW'); request['events'] = []; c = request['claims'][0]; c['event_refs'] = []
        self.assertEqual(result(request)['assessment']['status'], 'SUPPORTED')
        c['as_of'] = '2030-01-15'
        self.assertEqual(result(request)['assessment']['status'], 'NOT_EVALUABLE')

    def test_known_discord_excludes_even_while_window_is_open_and_other_data_missing(self):
        request = fixture('DISCORD_FREE_WINDOW')
        request['claims'][0].update(as_of='2030-01-15', observation_coverage_complete=False)
        output = result(request)
        self.assertEqual(output['assessment']['status'], 'CONTRADICTED')
        self.assertFalse(output['window_closed'])
        self.assertEqual(output['contradicting_event_refs'], ['E1'])

    def test_closure_never_irreversible_beyond_observed_window(self):
        request = fixture('CLOSURE_PERSISTED_IN_WINDOW')
        c = request['claims'][0]; c['as_of'] = '2030-01-15'
        self.assertEqual(result(request)['assessment']['status'], 'NOT_EVALUABLE')
        c['as_of'] = '2030-02-01'
        output = result(request)
        self.assertEqual(output['assessment']['status'], 'SUPPORTED')
        self.assertEqual(output['assessment']['scope'], 'DOCUMENTARY_PROCESS_STUDY:CLOSURE_PERSISTED_IN_WINDOW')
        self.assertNotIn('irreversible', output)

    def test_reopening_after_closure_contradicts_without_complete_observation(self):
        request = fixture('CLOSURE_PERSISTED_IN_WINDOW')
        request['events'].append(event('E2', 'REOPENING_EVENT', '2030-01-07'))
        request['claims'][0].update(event_refs=['E1', 'E2'], observation_coverage_complete=False, as_of='2030-01-15')
        self.assertEqual(result(request)['assessment']['status'], 'CONTRADICTED')
        self.assertEqual(result(request)['contradicting_event_refs'], ['E2'])

    def test_omitting_known_counter_ref_does_not_hide_it(self):
        for kind, role in (('CLOSURE_PERSISTED_IN_WINDOW', 'REOPENING_EVENT'), ('DISCORD_FREE_WINDOW', 'DISCORD_EVENT')):
            request = fixture(kind)
            if kind == 'CLOSURE_PERSISTED_IN_WINDOW': request['events'].append(event('E2', role, '2030-01-07'))
            request['claims'][0]['event_refs'] = []
            self.assertEqual(result(request)['assessment']['status'], 'CONTRADICTED')

    def test_reopening_before_closure_or_other_episode_is_not_excluding(self):
        request = fixture('CLOSURE_PERSISTED_IN_WINDOW')
        request['events'].append(event('E2', 'REOPENING_EVENT', '2030-01-02'))
        self.assertEqual(result(request)['assessment']['status'], 'SUPPORTED')
        request['events'][-1].update(start_date='2030-01-07', episode_id='EP2')
        self.assertEqual(result(request)['assessment']['status'], 'SUPPORTED')

    def test_events_outside_window_and_future_as_of_do_not_create_positive(self):
        request = fixture(); request['events'][0]['start_date'] = '2030-02-03'
        self.assertEqual(result(request)['assessment']['status'], 'CONTRADICTED')
        request['events'][0]['start_date'] = '2030-01-20'; request['claims'][0]['as_of'] = '2030-01-15'
        self.assertEqual(result(request)['assessment']['status'], 'NOT_EVALUABLE')

    def test_window_boundaries_included(self):
        for day in ('2030-01-01', '2030-01-31'):
            request = fixture(); request['events'][0]['start_date'] = day
            self.assertEqual(result(request)['assessment']['status'], 'SUPPORTED')

    def test_same_fact_two_sources_deduplicate_not_two_events(self):
        request = fixture(); other = copy.deepcopy(request['events'][0]); other.update(event_id='E2', source_refs=['synthetic:second'])
        request['events'].append(other); request['claims'][0]['event_refs'].append('E2')
        output = run_process_study(request)
        self.assertEqual(len(output['facts']), 1)
        self.assertEqual(output['facts'][0]['event_refs'], ['E1', 'E2'])
        self.assertEqual(output['claims'][0]['supporting_event_refs'], ['E1'])

    def test_conflicting_alias_dates_or_roles_are_blocked_not_silently_chosen(self):
        for change in ('date', 'role'):
            request = fixture(); other = copy.deepcopy(request['events'][0]); other['event_id'] = 'E2'
            if change == 'date': other['start_date'] = '2030-01-05'
            else: other['role'] = 'CLOSURE_EVENT'
            request['events'].append(other)
            output = run_process_study(request)
            self.assertTrue(output['facts'][0]['conflict'])
            self.assertIsNone(output['facts'][0]['admissible_event_ref'])
            self.assertEqual(output['claims'][0]['assessment']['status'], 'NOT_EVALUABLE')

    def test_pending_alias_cannot_destroy_verified_identical_fact(self):
        request = fixture(); other = copy.deepcopy(request['events'][0]); other.update(event_id='E2', verification_status='PENDING')
        request['events'].append(other)
        self.assertEqual(result(request)['assessment']['status'], 'SUPPORTED')

    def test_event_order_and_claim_order_deterministic_and_input_not_mutated(self):
        request = fixture(); request['events'].append(event('E2', 'DISCORD_EVENT', '2030-01-06'))
        c = claim('DISCORD_FREE_WINDOW'); c['id'] = 'C2'; request['claims'].append(c)
        before = copy.deepcopy(request); output = run_process_study(request)
        self.assertEqual(request, before)
        request['events'].reverse(); request['claims'].reverse()
        self.assertEqual(run_process_study(request), output)

    def test_no_preregistration_never_promotes_claim_or_negation(self):
        for kind in ('INITIATION_OCCURRED', 'DISCORD_FREE_WINDOW'):
            request = fixture(kind); request['claims'][0]['preregistered_before_chart_inspection'] = False
            output = result(request)
            self.assertEqual(output['assessment']['status'], 'NOT_EVALUABLE')
            self.assertEqual(output['contradicting_event_refs'], [])

    def test_bad_dates_intervals_bounds_refs_duplicate_ids_and_subjects_rejected(self):
        for change in ('date', 'format', 'interval', 'window', 'bounds', 'ref', 'id', 'subject', 'episode'):
            request = fixture()
            if change == 'date': request['events'][0]['start_date'] = '2030-02-30'
            if change == 'format': request['events'][0]['start_date'] = '20300103'
            if change == 'interval': request['events'][0]['end_date'] = '2030-01-06'
            if change == 'window': request['claims'][0]['window_end'] = '2029-01-01'
            if change == 'bounds': request['claims'][0]['minimum_days'] = 4
            if change == 'ref': request['claims'][0]['event_refs'] = ['MISSING']
            if change == 'id': request['events'].append(copy.deepcopy(request['events'][0]))
            if change == 'subject': request['events'][0]['subject_id'] = 'S2'
            if change == 'episode': request['events'][0]['episode_id'] = 'EP2'
            with self.assertRaises(ValueError): run_process_study(request)

    def test_unknown_role_astrological_or_ontological_fields_rejected(self):
        for key, value in (('role', 'DESTINY_VERIFIED'), ('ontology', 'SPLIT_SOUL'), ('longitude', 10)):
            request = fixture(); request['events'][0][key] = value
            with self.assertRaises(ValidationError): run_process_study(request)

    def test_result_status_fact_partition_duration_hash_and_effect_tampering_rejected(self):
        request = fixture('DURATION_WITHIN_BOUNDS')
        for change in ('status', 'fact', 'duration', 'hash', 'effect'):
            output = run_process_study(request)
            if change == 'status': output['claims'][0]['assessment']['status'] = 'CONTRADICTED'
            if change == 'fact': output['facts'][0]['event_refs'] = []
            if change == 'duration': output['claims'][0]['duration_days'] = 8
            if change == 'hash': output['policy_hash'] = '0' * 64
            if change == 'effect': output['documentary_correspondence_effect'] = 'SUPPORTED'
            with self.assertRaises((ValueError, ValidationError)): validate_process_study_result(output, request=request)


if __name__ == '__main__':
    unittest.main()
