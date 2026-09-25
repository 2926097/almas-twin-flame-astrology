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
                "roots": [
                    {"root_id": "R0001"},
                    {"root_id": "R0002"},
                ]
            },
            "clause_assembly": {
                "clauses": [
                    {"id": "CL_COMUNICACION_VERDAD"},
                    {"id": "CL_LIBERTAD_AUTONOMIA"},
                ]
            },
            "temporal_activation": {
                "signals": [
                    {
                        "signal_id": "T1",
                        "event_refs": ["E1", "MISSING_EVENT"],
                    }
                ]
            },
        }

    def event(self, event_id="E1", **overrides):
        base = {
            "event_id": event_id,
            "subjects": ["A", "B"],
            "event_type": "FIRST_MEETING",
            "date": "2030-04-12",
            "date_precision": "EXACT_DATE",
            "fact_statement": "A y B se encontraron presencialmente.",
            "documentary_quality": "DQ3_CORROBORATED_REPORT",
            "source_refs": ["S1", "S2"],
            "source_independence_declared": True,
            "privacy_class": "SYNTHETIC",
            "evidence_roles": ["ACTIVATION_CORROBORATION"],
            "linked_root_refs": ["R0001"],
            "linked_clause_refs": [],
            "interpretations": [],
        }
        base.update(overrides)
        return base

    def run_ledger(self, events, canonical=None):
        raw = {
            "documentary_event_ledger": {
                "schema_version": "1.0.0",
                "analysis_freeze_ref": "FREEZE-001",
                "events": events,
            }
        }
        return m27_dated_events(
            context("M27", raw, canonical or self.canonical)
        )

    def test_append_only_correction_preserves_superseded_record(self):
        first = self.event("E1")
        correction = self.event(
            "E2",
            date="2030-04-13",
            documentary_quality="DQ1_PRIMARY_DOCUMENT",
            source_refs=["S3"],
            source_independence_declared=False,
            supersedes_event_id="E1",
            correction_reason="Documento primario posterior.",
        )

        result = self.run_ledger([first, correction])
        output = result.canonical_updates["documentary_events"]

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertTrue(output["append_only_validated"])
        self.assertEqual(output["event_count"], 2)
        self.assertEqual(output["active_event_count"], 1)
        self.assertEqual(output["superseded_event_count"], 1)

        by_id = {event["event_id"]: event for event in output["events"]}
        self.assertEqual(by_id["E1"]["record_status"], "SUPERSEDED")
        self.assertEqual(by_id["E1"]["superseded_by_event_id"], "E2")
        self.assertEqual(by_id["E2"]["record_status"], "ACTIVE")

    def test_no_event_can_create_structure_clause_or_origin(self):
        result = self.run_ledger([self.event("E1")])
        output = result.canonical_updates["documentary_events"]
        event = output["events"][0]

        self.assertFalse(output["structural_mutation_allowed"])
        self.assertFalse(output["clause_creation_allowed"])
        self.assertFalse(output["origin_elevation_allowed"])
        self.assertFalse(output["astrology_backfill_allowed"])
        self.assertFalse(event["creates_structural_root"])
        self.assertFalse(event["creates_clause"])
        self.assertFalse(event["elevates_origin"])
        self.assertFalse(event["astrology_backfill_allowed"])

    def test_date_precision_mismatch_is_reported_not_rewritten(self):
        event = self.event(
            "E1",
            date=None,
            date_precision="EXACT_DATE",
        )
        result = self.run_ledger([event])
        output = result.canonical_updates["documentary_events"]

        self.assertFalse(
            output["events"][0]["date_precision_contract_met"]
        )
        self.assertEqual(len(output["date_contract_issues"]), 1)

    def test_documentary_quality_claim_can_be_flagged_without_silent_downgrade(self):
        event = self.event(
            "E1",
            documentary_quality="DQ3_CORROBORATED_REPORT",
            source_refs=["ONLY_ONE"],
            source_independence_declared=False,
        )
        result = self.run_ledger([event])
        output = result.canonical_updates["documentary_events"]
        normalized = output["events"][0]

        self.assertEqual(
            normalized["documentary_quality"],
            "DQ3_CORROBORATED_REPORT",
        )
        self.assertFalse(normalized["documentary_quality_contract_met"])
        self.assertEqual(
            normalized["source_independence_state"],
            "NOT_VERIFIED",
        )
        self.assertEqual(len(output["documentary_quality_issues"]), 1)

    def test_activation_role_requires_resolved_root_or_clause(self):
        event = self.event(
            "E1",
            linked_root_refs=["UNKNOWN_ROOT"],
        )
        result = self.run_ledger([event])
        output = result.canonical_updates["documentary_events"]
        trace = output["events"][0]["role_traceability"][
            "ACTIVATION_CORROBORATION"
        ]

        self.assertFalse(trace["target_traceability_complete"])
        self.assertEqual(trace["state"], "UNRESOLVED_TARGET")
        self.assertEqual(len(output["unresolved_root_refs"]), 1)
        self.assertEqual(len(output["role_traceability_issues"]), 1)

    def test_fulfillment_role_requires_resolved_clause(self):
        event = self.event(
            "E1",
            evidence_roles=["FULFILLMENT_EVIDENCE"],
            linked_root_refs=[],
            linked_clause_refs=["CL_COMUNICACION_VERDAD"],
        )
        result = self.run_ledger([event])
        output = result.canonical_updates["documentary_events"]
        trace = output["events"][0]["role_traceability"][
            "FULFILLMENT_EVIDENCE"
        ]

        self.assertTrue(trace["target_traceability_complete"])
        self.assertEqual(trace["state"], "RESOLVED_CLAUSE_TARGET")
        self.assertEqual(
            output["events"][0]["resolved_clause_refs"],
            ["CL_COMUNICACION_VERDAD"],
        )

    def test_missing_clause_registry_is_not_fabricated(self):
        canonical = {
            "independent_roots": self.canonical["independent_roots"]
        }
        event = self.event(
            "E1",
            evidence_roles=["FULFILLMENT_EVIDENCE"],
            linked_root_refs=[],
            linked_clause_refs=["CL_COMUNICACION_VERDAD"],
        )
        result = self.run_ledger([event], canonical=canonical)
        output = result.canonical_updates["documentary_events"]

        self.assertEqual(
            output["clause_reference_registry_state"],
            "NOT_AVAILABLE",
        )
        self.assertEqual(len(output["unresolved_clause_refs"]), 1)
        trace = output["events"][0]["role_traceability"][
            "FULFILLMENT_EVIDENCE"
        ]
        self.assertFalse(trace["target_traceability_complete"])

    def test_private_events_are_not_public_exportable(self):
        private_event = self.event(
            "E1",
            privacy_class="PRIVATE_RESTRICTED",
        )
        result = self.run_ledger([private_event])
        output = result.canonical_updates["documentary_events"]

        self.assertFalse(output["events"][0]["public_exportable"])
        self.assertEqual(output["public_event_ids"], [])
        self.assertEqual(output["restricted_event_ids"], ["E1"])
        self.assertTrue(output["public_export_policy_enforced"])

    def test_temporal_event_backreferences_are_audited(self):
        result = self.run_ledger([self.event("E1")])
        output = result.canonical_updates["documentary_events"]

        self.assertEqual(
            output["temporal_event_links"],
            [{"signal_id": "T1", "event_id": "E1"}],
        )
        self.assertEqual(
            output["unresolved_temporal_event_refs"],
            [{"signal_id": "T1", "event_id": "MISSING_EVENT"}],
        )

    def test_fact_and_interpretations_remain_separate(self):
        event = self.event(
            "E1",
            interpretations=[
                {
                    "claim_class": "PROJECT_SYNTHESIS",
                    "text": "Lectura simbólica sintética.",
                }
            ],
        )
        result = self.run_ledger([event])
        normalized = result.canonical_updates["documentary_events"][
            "events"
        ][0]

        self.assertTrue(normalized["fact_interpretation_separated"])
        self.assertEqual(normalized["interpretation_count"], 1)
        self.assertEqual(
            normalized["fact_statement"],
            "A y B se encontraron presencialmente.",
        )

    def test_correction_must_reference_prior_event(self):
        correction = self.event(
            "E2",
            supersedes_event_id="E1",
            correction_reason="test",
        )
        with self.assertRaises(ValueError):
            self.run_ledger([correction])




if __name__ == "__main__":
    unittest.main()
