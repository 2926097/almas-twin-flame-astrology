import unittest

from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.temporal_handlers import m26_temporal_activation, m27_dated_events


def context(module_id, raw, canonical):
    return ModuleContext(
        module_id=module_id,
        module_name=module_id,
        mode="FULL",
        raw_input=raw,
        canonical_snapshot=canonical,
        prior_results={},
    )


class TestTemporalActivation(unittest.TestCase):
    def setUp(self):
        self.canonical = {
            "independent_roots": {
                "roots": [
                    {"root_id": "R0001"},
                    {"root_id": "R0002"},
                ]
            }
        }

    def test_unanchored_signal_has_zero_k(self):
        result = m26_temporal_activation(
            context(
                "M26",
                {
                    "temporal_signals": [
                        {
                            "signal_id": "T1",
                            "root_id": "UNKNOWN",
                            "temporal_family": "TTRANSIT",
                            "activation_class": "DIRECT_REPETITION",
                            "strength": 1.0,
                            "window_status": "CURRENT_ACTIVE",
                            "preregistered": True,
                        }
                    ]
                },
                self.canonical,
            )
        )
        signal = result.canonical_updates["temporal_activation"]["signals"][0]
        self.assertFalse(signal["anchored"])
        self.assertEqual(signal["k"], 0.0)
        self.assertEqual(signal["window_status"], "UNANCHORED")

    def test_same_root_family_keeps_strongest(self):
        result = m26_temporal_activation(
            context(
                "M26",
                {
                    "temporal_signals": [
                        {
                            "signal_id": "T1",
                            "root_id": "R0001",
                            "temporal_family": "TTRANSIT",
                            "activation_class": "RELATIONAL_ROOT_ACTIVATION",
                            "strength": 0.5,
                            "window_status": "CURRENT_ACTIVE",
                            "preregistered": True,
                        },
                        {
                            "signal_id": "T2",
                            "root_id": "R0001",
                            "temporal_family": "TTRANSIT",
                            "activation_class": "DIRECT_REPETITION",
                            "strength": 0.8,
                            "window_status": "CURRENT_ACTIVE",
                            "preregistered": True,
                        },
                    ]
                },
                self.canonical,
            )
        )
        output = result.canonical_updates["temporal_activation"]
        self.assertEqual(len(output["selected_independent_signals"]), 1)
        self.assertEqual(output["selected_independent_signals"][0]["signal_id"], "T2")
        self.assertEqual(len(output["suppressed"]), 1)
        self.assertIsNone(output["iat"])
        self.assertFalse(output["structural_score_modified"])

    def test_unregistered_atacir_is_exploratory(self):
        result = m26_temporal_activation(
            context(
                "M26",
                {
                    "temporal_signals": [
                        {
                            "signal_id": "A1",
                            "root_id": "R0002",
                            "temporal_family": "TATACIR",
                            "activation_class": "ENDPOINT_ACTIVATION",
                            "strength": 0.8,
                            "window_status": "PROSPECTIVE_ACTIVATION",
                            "preregistered": False,
                        }
                    ]
                },
                self.canonical,
            )
        )
        signal = result.canonical_updates["temporal_activation"]["signals"][0]
        self.assertEqual(signal["window_status"], "EXPLORATORY")


class TestDocumentaryEvents(unittest.TestCase):
    def setUp(self):
        self.canonical = {
            "independent_roots": {
                "roots": [{"root_id": "R0001"}]
            }
        }

    def test_append_only_and_no_structural_creation(self):
        raw = {
            "documentary_event_ledger": {
                "schema_version": "1.0.0",
                "analysis_freeze_ref": "FREEZE-001",
                "events": [
                    {
                        "event_id": "E1",
                        "subjects": ["A", "B"],
                        "event_type": "FIRST_MEETING",
                        "date": "2030-04-12",
                        "date_precision": "EXACT_DATE",
                        "fact_statement": "A y B se encontraron presencialmente.",
                        "documentary_quality": "DQ3_CORROBORATED_REPORT",
                        "source_refs": ["S1", "S2"],
                        "privacy_class": "SYNTHETIC",
                        "evidence_roles": ["ACTIVATION_CORROBORATION"],
                        "linked_root_refs": ["R0001"],
                    },
                    {
                        "event_id": "E2",
                        "subjects": ["A", "B"],
                        "event_type": "FIRST_MEETING",
                        "date": "2030-04-13",
                        "date_precision": "EXACT_DATE",
                        "fact_statement": "Corrección de la fecha del encuentro.",
                        "documentary_quality": "DQ1_PRIMARY_DOCUMENT",
                        "source_refs": ["S3"],
                        "privacy_class": "SYNTHETIC",
                        "evidence_roles": ["ACTIVATION_CORROBORATION"],
                        "linked_root_refs": ["R0001"],
                        "supersedes_event_id": "E1",
                        "correction_reason": "Documento primario posterior.",
                    },
                ],
            }
        }
        result = m27_dated_events(context("M27", raw, self.canonical))
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["documentary_events"]
        self.assertTrue(output["append_only_validated"])
        self.assertFalse(output["structural_mutation_allowed"])
        self.assertFalse(output["events"][0]["creates_structural_root"])

    def test_correction_must_reference_prior_event(self):
        raw = {
            "documentary_event_ledger": {
                "schema_version": "1.0.0",
                "analysis_freeze_ref": "FREEZE-001",
                "events": [
                    {
                        "event_id": "E2",
                        "subjects": ["A"],
                        "event_type": "OTHER",
                        "date_precision": "UNKNOWN",
                        "fact_statement": "Corrección sintética.",
                        "documentary_quality": "DQ5_UNVERIFIED",
                        "source_refs": [],
                        "privacy_class": "SYNTHETIC",
                        "evidence_roles": ["CONTEXT_ONLY"],
                        "supersedes_event_id": "E1",
                        "correction_reason": "test",
                    }
                ],
            }
        }
        with self.assertRaises(ValueError):
            m27_dated_events(context("M27", raw, self.canonical))


if __name__ == "__main__":
    unittest.main()
