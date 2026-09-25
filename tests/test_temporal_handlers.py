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

    def signal(
        self,
        signal_id,
        *,
        root_id="R0001",
        family="TTRANSIT",
        activation_class="DIRECT_REPETITION",
        strength=1.0,
        window_status="CURRENT_ACTIVE",
        preregistered=True,
        structural_family="SYN",
        exactitude_orb=0.5,
        preregistered_window_rule="WINDOW-RULE-V1",
    ):
        return {
            "signal_id": signal_id,
            "root_id": root_id,
            "temporal_family": family,
            "activation_class": activation_class,
            "strength": strength,
            "window_status": window_status,
            "preregistered": preregistered,
            "structural_family": structural_family,
            "exactitude_orb": exactitude_orb,
            "preregistered_window_rule": preregistered_window_rule,
        }

    def test_unanchored_signal_has_zero_k_and_never_enters_iat(self):
        raw_signal = self.signal("T1", root_id="UNKNOWN")
        result = m26_temporal_activation(
            context("M26", {"temporal_signals": [raw_signal]}, self.canonical)
        )
        output = result.canonical_updates["temporal_activation"]
        signal = output["signals"][0]

        self.assertFalse(signal["anchored"])
        self.assertEqual(signal["k"], 0.0)
        self.assertEqual(signal["window_status"], "UNANCHORED")
        self.assertFalse(signal["iat_eligible"])
        self.assertIsNone(output["iat"])
        self.assertFalse(output["structural_roots_created"])

    def test_same_root_family_keeps_strongest(self):
        signals = [
            self.signal(
                "T1",
                activation_class="RELATIONAL_ROOT_ACTIVATION",
                strength=0.5,
            ),
            self.signal(
                "T2",
                activation_class="DIRECT_REPETITION",
                strength=0.8,
            ),
        ]
        result = m26_temporal_activation(
            context("M26", {"temporal_signals": signals}, self.canonical)
        )
        output = result.canonical_updates["temporal_activation"]

        self.assertEqual(len(output["selected_independent_signals"]), 1)
        self.assertEqual(
            output["selected_independent_signals"][0]["signal_id"],
            "T2",
        )
        self.assertEqual(len(output["suppressed"]), 1)
        self.assertIsNone(output["iat"])
        self.assertEqual(output["iat_state"], "NOT_CALCULATED")
        self.assertFalse(output["aggregation_weights_applied"])

    def test_unregistered_atacir_is_exploratory_and_not_iat_eligible(self):
        signal = self.signal(
            "A1",
            root_id="R0002",
            family="TATACIR",
            activation_class="ENDPOINT_ACTIVATION",
            strength=0.8,
            window_status="PROSPECTIVE_ACTIVATION",
            preregistered=False,
        )
        result = m26_temporal_activation(
            context("M26", {"temporal_signals": [signal]}, self.canonical)
        )
        item = result.canonical_updates["temporal_activation"]["signals"][0]

        self.assertEqual(item["window_status"], "EXPLORATORY")
        self.assertFalse(item["iat_eligible"])

    def test_incomplete_traceability_excludes_signal_from_iat(self):
        signal = self.signal(
            "T1",
            preregistered_window_rule=None,
        )
        result = m26_temporal_activation(
            context("M26", {"temporal_signals": [signal]}, self.canonical)
        )
        item = result.canonical_updates["temporal_activation"]["signals"][0]

        self.assertFalse(item["traceability_complete"])
        self.assertFalse(item["iat_eligible"])
        self.assertIn(
            "preregistered_window_rule",
            item["missing_traceability"],
        )

    def test_iat_requires_explicit_preregistered_weights(self):
        signals = [
            self.signal(
                "T1",
                root_id="R0001",
                family="TTRANSIT",
                activation_class="DIRECT_REPETITION",
                strength=0.8,
            ),
            self.signal(
                "T2",
                root_id="R0002",
                family="TPROG",
                activation_class="RELATIONAL_ROOT_ACTIVATION",
                strength=1.0,
            ),
        ]
        raw = {
            "temporal_signals": signals,
            "iat_aggregation_policy": {
                "preregistration_ref": "IAT-PREREG-001",
                "window_scope_ref": "WINDOW-2030",
                "formula": "WEIGHTED_MEAN_EFFECTIVE_STRENGTH",
                "family_weights": {
                    "TTRANSIT": 1.0,
                    "TPROG": 2.0,
                },
                "root_weights": {
                    "R0001": 1.0,
                    "R0002": 0.5,
                },
            },
        }
        result = m26_temporal_activation(
            context("M26", raw, self.canonical)
        )
        output = result.canonical_updates["temporal_activation"]

        # T1 = 0.8*1.0, weight 1*1 = 1
        # T2 = 1.0*0.9, weight 2*0.5 = 1
        self.assertAlmostEqual(output["iat"], 85.0)
        self.assertEqual(output["iat_state"], "CALCULATED")
        self.assertTrue(output["aggregation_weights_applied"])
        self.assertEqual(
            output["iat_policy"]["preregistration_ref"],
            "IAT-PREREG-001",
        )

    def test_missing_weight_for_eligible_signal_is_rejected(self):
        signal = self.signal("T1", family="TECLIPSE")
        raw = {
            "temporal_signals": [signal],
            "iat_aggregation_policy": {
                "preregistration_ref": "IAT-PREREG-002",
                "window_scope_ref": "WINDOW-X",
                "formula": "WEIGHTED_MEAN_EFFECTIVE_STRENGTH",
                "family_weights": {"TTRANSIT": 1.0},
                "root_weights": {"R0001": 1.0},
            },
        }
        with self.assertRaises(ValueError):
            m26_temporal_activation(
                context("M26", raw, self.canonical)
            )

    def test_recurrence_requires_independent_temporal_families(self):
        signals = [
            self.signal("T1", family="TTRANSIT", strength=0.7),
            self.signal("T2", family="TPROG", strength=0.8),
            self.signal("T3", family="TTRANSIT", strength=0.9),
        ]
        result = m26_temporal_activation(
            context("M26", {"temporal_signals": signals}, self.canonical)
        )
        summary = result.canonical_updates["temporal_activation"][
            "root_activation_summary"
        ][0]

        self.assertEqual(summary["independent_family_count"], 2)
        self.assertTrue(
            summary["recurring_across_independent_families"]
        )

    def test_future_window_never_predicts_real_world_event(self):
        signal = self.signal(
            "F1",
            window_status="PROSPECTIVE_ACTIVATION",
        )
        result = m26_temporal_activation(
            context("M26", {"temporal_signals": [signal]}, self.canonical)
        )
        output = result.canonical_updates["temporal_activation"]

        self.assertFalse(output["real_world_event_prediction_made"])
        self.assertFalse(
            output["signals"][0]["predicts_real_world_event"]
        )
        self.assertFalse(output["structural_score_modified"])




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
