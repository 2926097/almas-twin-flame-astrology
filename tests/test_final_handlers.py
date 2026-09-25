import unittest

from almas_tfa.final_handlers import (
    m28_doctrine_hermeneutics,
    m29_viability_reciprocity,
    m30_report_gate,
    m31_report,
)
from almas_tfa.module_contract import ExecutionStatus, ModuleContext, ModuleResult


def ctx(module_id, raw=None, canonical=None, prior=None):
    return ModuleContext(
        module_id=module_id,
        module_name=module_id,
        mode="FULL",
        raw_input=raw or {},
        canonical_snapshot=canonical or {},
        prior_results=prior or {},
    )


class TestDoctrineFirewall(unittest.TestCase):
    def source_registry(self):
        return {
            "registry_version": "TEST-1",
            "entries": [
                {
                    "id": "P1",
                    "priority": "P1_PRIMARY",
                    "source_role": "DOCTRINAL_PRIMARY",
                    "tradition": "Tradition A",
                    "author": "Author A",
                    "work": "Primary Work",
                    "concepts": ["CONCEPT_A"],
                    "supports": ["Explicit doctrine A."],
                    "does_not_support": ["Identity with CONCEPT_B."],
                    "verification_status": "VERIFIED_PRIMARY",
                    "verification_anchor": "Exact passage A.",
                    "verification_anchor_type": "EXACT_PASSAGE",
                    "evidence_scope": "DOCTRINAL_CLAIM",
                },
                {
                    "id": "P2",
                    "priority": "P2_ACADEMIC",
                    "source_role": "ACADEMIC_ANALYSIS",
                    "tradition": "Academic study",
                    "author": "Scholar",
                    "work": "Academic Work",
                    "concepts": ["CONCEPT_A"],
                    "supports": ["Academic description of a doctrine."],
                    "does_not_support": ["Ontological verification."],
                    "verification_status": "VERIFIED_METADATA",
                    "verification_anchor": "Abstract.",
                    "verification_anchor_type": "ABSTRACT",
                    "evidence_scope": "ACADEMIC_DESCRIPTION",
                },
                {
                    "id": "P5",
                    "priority": "P5_EMIC",
                    "source_role": "EMIC_USAGE",
                    "tradition": "Contemporary community",
                    "author": "Community Source",
                    "work": "Usage Source",
                    "concepts": ["CURRENT_TERM"],
                    "supports": ["Contemporary use of a term."],
                    "does_not_support": ["Ontological proof."],
                    "verification_status": "PARTIAL",
                    "verification_anchor": "Usage sample.",
                    "verification_anchor_type": "SECTION",
                    "evidence_scope": "PHENOMENOLOGY",
                },
                {
                    "id": "P4",
                    "priority": "P4_IDENTIFIED_METHOD",
                    "source_role": "IDENTIFIED_METHOD",
                    "tradition": "Modern method",
                    "author": "Method Author",
                    "work": "Technique Manual",
                    "concepts": ["TECHNIQUE_X"],
                    "supports": ["Technique X calculation."],
                    "does_not_support": ["Metaphysical ontology."],
                    "verification_status": "VERIFIED_PRIMARY",
                    "verification_anchor": "Method section.",
                    "verification_anchor_type": "SECTION",
                    "evidence_scope": "METHOD_DESCRIPTION",
                },
            ],
        }

    def base_claim(self, **overrides):
        claim = {
            "schema_version": "2.0.0",
            "claim_id": "C1",
            "statement": "Explicit doctrine A.",
            "epistemic_class": "C_DOCTRINE",
            "claim_scope": "DOCTRINAL_ATTRIBUTION",
            "concept_id": "CONCEPT_A",
            "source_relation": "DIRECT_DOCTRINE",
            "source_ids": ["P1"],
            "source_anchor_refs": ["P1"],
            "source_support_refs": [
                {"source_id": "P1", "support_index": 0}
            ],
            "does_not_support_checked": True,
            "asserts_doctrinal_identity": False,
            "astrological_refs": [],
            "status": "SUPPORTED",
            "requested_conclusion": "DOCTRINE_A",
            "allowed_conclusion": "DOCTRINE_A",
            "inferential_ceiling": "DIRECT_DOCTRINE_ONLY",
            "discriminator_id": None,
            "discriminator_state": "DOCTRINAL_ONLY",
            "ceiling_enforced": True,
            "alternatives": [],
            "limitations": ["Does not establish a case-specific ontology."],
        }
        claim.update(overrides)
        return claim

    def test_direct_doctrine_requires_p1_verified_support_and_anchor(self):
        result = m28_doctrine_hermeneutics(
            ctx(
                "M28",
                {
                    "doctrinal_claims": [self.base_claim()],
                    "source_registry": self.source_registry(),
                },
            )
        )
        output = result.canonical_updates["doctrine_hermeneutics"]
        claim = output["claims"][0]

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertTrue(claim["doctrine_gate"]["passed"])
        self.assertEqual(
            claim["doctrine_gate"]["qualifying_source_ids"],
            ["P1"],
        )
        self.assertFalse(output["doctrine_adds_structural_score"])
        self.assertFalse(output["source_count_used_as_structural_weight"])
        self.assertTrue(output["epistemic_separation_enforced"])

    def test_direct_doctrine_cannot_use_academic_source_as_p1(self):
        claim = self.base_claim(
            source_ids=["P2"],
            source_anchor_refs=["P2"],
            source_support_refs=[{"source_id": "P2", "support_index": 0}],
        )
        with self.assertRaises(ValueError):
            m28_doctrine_hermeneutics(
                ctx(
                    "M28",
                    {
                        "doctrinal_claims": [claim],
                        "source_registry": self.source_registry(),
                    },
                )
            )

    def test_academic_description_stays_academic(self):
        claim = self.base_claim(
            source_relation="ACADEMIC_DESCRIPTION",
            source_ids=["P2"],
            source_anchor_refs=["P2"],
            source_support_refs=[],
            does_not_support_checked=False,
            status="SUPPORTED",
            requested_conclusion="ACADEMIC_DESCRIPTION_ONLY",
            allowed_conclusion="ACADEMIC_DESCRIPTION_ONLY",
            inferential_ceiling="ACADEMIC_DESCRIPTION_ONLY",
        )
        result = m28_doctrine_hermeneutics(
            ctx(
                "M28",
                {
                    "doctrinal_claims": [claim],
                    "source_registry": self.source_registry(),
                },
            )
        )
        normalized = result.canonical_updates["doctrine_hermeneutics"][
            "claims"
        ][0]

        self.assertTrue(normalized["academic_description_gate"]["passed"])
        self.assertFalse(normalized["doctrinal_identity_allowed"])
        self.assertFalse(
            normalized["cross_tradition_identity_inferred"]
        )

    def test_contemporary_usage_is_never_promoted_to_ontology(self):
        claim = self.base_claim(
            epistemic_class="D_CONTEMPORARY_USAGE",
            claim_scope="CONTEMPORARY_USAGE",
            concept_id="CURRENT_TERM",
            source_relation="CONTEMPORARY_USAGE",
            source_ids=["P5"],
            source_anchor_refs=["P5"],
            source_support_refs=[],
            does_not_support_checked=False,
            statement="A contemporary community uses the term.",
            requested_conclusion="USAGE_DOCUMENTED",
            allowed_conclusion="USAGE_DOCUMENTED",
            inferential_ceiling="CONTEMPORARY_USAGE_ONLY",
            discriminator_state="NOT_APPLICABLE",
        )
        result = m28_doctrine_hermeneutics(
            ctx(
                "M28",
                {
                    "doctrinal_claims": [claim],
                    "source_registry": self.source_registry(),
                },
            )
        )
        output = result.canonical_updates["doctrine_hermeneutics"]
        normalized = output["claims"][0]

        self.assertTrue(normalized["contemporary_usage_gate"]["passed"])
        self.assertFalse(
            normalized["contemporary_usage_promoted_to_ontology"]
        )
        self.assertFalse(output["contemporary_usage_promoted_to_ontology"])

    def test_project_hypothesis_cannot_be_direct_doctrine(self):
        claim = self.base_claim(
            epistemic_class="E_PROJECT_HYPOTHESIS",
            claim_scope="PROJECT_SYNTHESIS",
            source_relation="DIRECT_DOCTRINE",
            source_ids=[],
            source_anchor_refs=[],
            source_support_refs=[],
            does_not_support_checked=False,
            status="COMPATIBLE",
            requested_conclusion="PROJECT_MODEL",
            allowed_conclusion="PROJECT_MODEL",
            inferential_ceiling="PROJECT_ONLY",
            discriminator_state="NOT_VALIDATED",
            alternatives=["ALTERNATIVE_MODEL"],
        )
        with self.assertRaises(ValueError):
            m28_doctrine_hermeneutics(
                ctx(
                    "M28",
                    {
                        "doctrinal_claims": [claim],
                        "source_registry": self.source_registry(),
                    },
                )
            )

    def test_project_hypothesis_remains_project_construction(self):
        claim = self.base_claim(
            epistemic_class="E_PROJECT_HYPOTHESIS",
            claim_scope="PROJECT_SYNTHESIS",
            source_relation="PROJECT_SYNTHESIS",
            source_ids=["P2"],
            source_anchor_refs=["P2"],
            source_support_refs=[],
            does_not_support_checked=False,
            statement="ALMAS combines documented motifs into a project model.",
            status="COMPATIBLE",
            requested_conclusion="PROJECT_MODEL",
            allowed_conclusion="PROJECT_MODEL",
            inferential_ceiling="PROJECT_ONLY",
            discriminator_state="NOT_VALIDATED",
            alternatives=["GENERIC_CONTINUITY"],
        )
        result = m28_doctrine_hermeneutics(
            ctx(
                "M28",
                {
                    "doctrinal_claims": [claim],
                    "source_registry": self.source_registry(),
                },
            )
        )
        output = result.canonical_updates["doctrine_hermeneutics"]
        normalized = output["claims"][0]

        self.assertTrue(normalized["project_construction"])
        self.assertFalse(
            normalized["project_hypothesis_promoted_to_doctrine"]
        )
        self.assertFalse(output["project_hypothesis_promoted_to_doctrine"])

    def test_comparative_analogue_cannot_assert_identity(self):
        claim = self.base_claim(
            epistemic_class="E_PROJECT_HYPOTHESIS",
            claim_scope="PROJECT_SYNTHESIS",
            source_relation="COMPARATIVE_ANALOGUE",
            source_ids=["P1"],
            source_anchor_refs=["P1"],
            source_support_refs=[],
            does_not_support_checked=False,
            status="COMPATIBLE",
            requested_conclusion="CONCEPT_A_EQUALS_CONCEPT_B",
            allowed_conclusion="COMPARABLE_NOT_IDENTICAL",
            inferential_ceiling="COMPARATIVE_ONLY",
            discriminator_state="NOT_VALIDATED",
            alternatives=["NON_EQUIVALENT"],
            asserts_doctrinal_identity=True,
            identity_target_concept_id="CONCEPT_B",
        )
        with self.assertRaises(ValueError):
            m28_doctrine_hermeneutics(
                ctx(
                    "M28",
                    {
                        "doctrinal_claims": [claim],
                        "source_registry": self.source_registry(),
                    },
                )
            )

    def test_genealogy_non_equivalent_blocks_identity_pair(self):
        claim = self.base_claim(
            asserts_doctrinal_identity=True,
            identity_target_concept_id="CONCEPT_B",
        )
        genealogy = {
            "genealogy_version": "TEST",
            "almas_version": "TEST",
            "edges": [
                {
                    "from": "CONCEPT_A",
                    "to": "CONCEPT_B",
                    "relation": "NON_EQUIVALENT",
                    "status": "SUPPORTED",
                    "note": "Different doctrinal systems.",
                }
            ],
        }
        with self.assertRaises(ValueError):
            m28_doctrine_hermeneutics(
                ctx(
                    "M28",
                    {
                        "doctrinal_claims": [claim],
                        "source_registry": self.source_registry(),
                        "doctrinal_genealogy": genealogy,
                    },
                )
            )

    def test_technique_is_independent_from_metaphysical_validation(self):
        claim = self.base_claim(
            epistemic_class="B_TECHNIQUE",
            claim_scope="TECHNIQUE_DESCRIPTION",
            concept_id="TECHNIQUE_X",
            source_relation="PROJECT_OPERATIONALIZATION",
            source_ids=["P4"],
            source_anchor_refs=["P4"],
            source_support_refs=[],
            does_not_support_checked=False,
            statement="Technique X has a defined calculation procedure.",
            astrological_refs=["TECHNIQUE_X_FORMULA"],
            requested_conclusion="TECHNIQUE_DEFINED",
            allowed_conclusion="TECHNIQUE_DEFINED",
            inferential_ceiling="TECHNIQUE_ONLY",
            discriminator_state="NOT_APPLICABLE",
        )
        result = m28_doctrine_hermeneutics(
            ctx(
                "M28",
                {
                    "doctrinal_claims": [claim],
                    "source_registry": self.source_registry(),
                },
            )
        )
        normalized = result.canonical_updates["doctrine_hermeneutics"][
            "claims"
        ][0]

        self.assertEqual(normalized["epistemic_class"], "B_TECHNIQUE")
        self.assertFalse(normalized["doctrine_adds_structural_score"])




class TestViabilityReciprocity(unittest.TestCase):
    def event(
        self,
        event_id,
        role,
        *,
        event_type="RELATIONSHIP_CHANGE",
        subjects=None,
        quality="DQ1_PRIMARY_DOCUMENT",
        record_status="ACTIVE",
        quality_ok=True,
        date_ok=True,
        fact_split=True,
        date_value="2030-04-01",
    ):
        return {
            "event_id": event_id,
            "subjects": subjects or ["A", "B"],
            "event_type": event_type,
            "date": date_value,
            "date_precision": "EXACT_DATE",
            "documentary_quality": quality,
            "evidence_roles": [role],
            "record_status": record_status,
            "documentary_quality_contract_met": quality_ok,
            "date_precision_contract_met": date_ok,
            "fact_interpretation_separated": fact_split,
        }

    def canonical(self, events):
        return {"documentary_events": {"events": events}}

    def assessment(self, **overrides):
        data = {
            "assessment_ref": "VR-001",
            "as_of_date": "2030-05-01",
            "subjects": ["A", "B"],
            "real_viability": "STABLE",
            "reciprocity": "BILATERAL",
            "viability_basis": [
                {
                    "event_id": "E1",
                    "basis_kind": "OBSERVED_STABLE_RELATIONSHIP",
                    "observation_type": "DOCUMENTED_STATUS",
                    "subject_ids": ["A", "B"],
                }
            ],
            "reciprocity_basis": [
                {
                    "event_id": "E2",
                    "basis_kind": "DOCUMENTED_BILATERALITY",
                    "observation_type": "MUTUAL_AGREEMENT",
                    "subject_ids": ["A", "B"],
                }
            ],
        }
        data.update(overrides)
        return data

    def test_requires_active_documentary_facts_for_both_axes(self):
        canonical = self.canonical(
            [
                self.event("E1", "VIABILITY_FACT"),
                self.event("E2", "RECIPROCITY_FACT"),
            ]
        )
        result = m29_viability_reciprocity(
            ctx(
                "M29",
                {"viability_reciprocity_assessment": self.assessment()},
                canonical,
            )
        )
        output = result.canonical_updates["viability_reciprocity"]

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertTrue(output["factual_basis_only"])
        self.assertEqual(output["viability_event_refs"], ["E1"])
        self.assertEqual(output["reciprocity_event_refs"], ["E2"])
        self.assertEqual(output["viability_subject_coverage"], ["A", "B"])
        self.assertEqual(output["reciprocity_subject_coverage"], ["A", "B"])
        self.assertFalse(output["astrology_used_as_real_world_fact"])
        self.assertFalse(output["metaphysical_claim_used_as_real_world_fact"])
        self.assertFalse(output["future_decisions_inferred"])

    def test_superseded_event_cannot_support_current_assessment(self):
        canonical = self.canonical(
            [
                self.event(
                    "E1",
                    "VIABILITY_FACT",
                    record_status="SUPERSEDED",
                ),
                self.event("E2", "RECIPROCITY_FACT"),
            ]
        )
        with self.assertRaises(ValueError):
            m29_viability_reciprocity(
                ctx(
                    "M29",
                    {"viability_reciprocity_assessment": self.assessment()},
                    canonical,
                )
            )

    def test_failed_documentary_contract_is_rejected(self):
        canonical = self.canonical(
            [
                self.event(
                    "E1",
                    "VIABILITY_FACT",
                    quality_ok=False,
                ),
                self.event("E2", "RECIPROCITY_FACT"),
            ]
        )
        with self.assertRaises(ValueError):
            m29_viability_reciprocity(
                ctx(
                    "M29",
                    {"viability_reciprocity_assessment": self.assessment()},
                    canonical,
                )
            )

    def test_weak_unverified_fact_is_not_decisive(self):
        canonical = self.canonical(
            [
                self.event(
                    "E1",
                    "VIABILITY_FACT",
                    quality="DQ5_UNVERIFIED",
                ),
                self.event("E2", "RECIPROCITY_FACT"),
            ]
        )
        with self.assertRaises(ValueError):
            m29_viability_reciprocity(
                ctx(
                    "M29",
                    {"viability_reciprocity_assessment": self.assessment()},
                    canonical,
                )
            )

    def test_future_event_cannot_describe_state_as_of_earlier_date(self):
        canonical = self.canonical(
            [
                self.event(
                    "E1",
                    "VIABILITY_FACT",
                    date_value="2031-01-01",
                ),
                self.event("E2", "RECIPROCITY_FACT"),
            ]
        )
        with self.assertRaises(ValueError):
            m29_viability_reciprocity(
                ctx(
                    "M29",
                    {"viability_reciprocity_assessment": self.assessment()},
                    canonical,
                )
            )

    def test_absence_of_second_subject_does_not_prove_asymmetry(self):
        canonical = self.canonical(
            [
                self.event("E1", "VIABILITY_FACT"),
                self.event(
                    "E2",
                    "RECIPROCITY_FACT",
                    subjects=["A"],
                ),
            ]
        )
        assessment = self.assessment(
            reciprocity="ASYMMETRIC",
            reciprocity_basis=[
                {
                    "event_id": "E2",
                    "basis_kind": "DOCUMENTED_ASYMMETRY",
                    "observation_type": "EXPLICIT_STATEMENT",
                    "subject_ids": ["A"],
                }
            ],
        )
        with self.assertRaises(ValueError):
            m29_viability_reciprocity(
                ctx(
                    "M29",
                    {"viability_reciprocity_assessment": assessment},
                    canonical,
                )
            )

    def test_separated_requires_documented_separation_event(self):
        canonical = self.canonical(
            [
                self.event(
                    "E1",
                    "VIABILITY_FACT",
                    event_type="RELATIONSHIP_CHANGE",
                ),
                self.event("E2", "RECIPROCITY_FACT"),
            ]
        )
        assessment = self.assessment(
            real_viability="SEPARATED",
            viability_basis=[
                {
                    "event_id": "E1",
                    "basis_kind": "DOCUMENTED_SEPARATION",
                    "observation_type": "DOCUMENTED_STATUS",
                    "subject_ids": ["A", "B"],
                }
            ],
        )
        with self.assertRaises(ValueError):
            m29_viability_reciprocity(
                ctx(
                    "M29",
                    {"viability_reciprocity_assessment": assessment},
                    canonical,
                )
            )

    def test_no_contact_requires_no_contact_event(self):
        canonical = self.canonical(
            [
                self.event(
                    "E1",
                    "VIABILITY_FACT",
                    event_type="NO_CONTACT",
                ),
                self.event("E2", "RECIPROCITY_FACT"),
            ]
        )
        assessment = self.assessment(
            real_viability="NO_CONTACT",
            viability_basis=[
                {
                    "event_id": "E1",
                    "basis_kind": "DOCUMENTED_NO_CONTACT",
                    "observation_type": "DOCUMENTED_STATUS",
                    "subject_ids": ["A", "B"],
                }
            ],
        )
        result = m29_viability_reciprocity(
            ctx(
                "M29",
                {"viability_reciprocity_assessment": assessment},
                canonical,
            )
        )
        self.assertEqual(
            result.canonical_updates["viability_reciprocity"][
                "real_viability"
            ],
            "NO_CONTACT",
        )

    def test_unknown_and_not_evaluable_need_no_confirmatory_basis(self):
        result = m29_viability_reciprocity(
            ctx(
                "M29",
                {
                    "viability_reciprocity_assessment": {
                        "assessment_ref": "VR-UNKNOWN",
                        "as_of_date": "2030-05-01",
                        "subjects": ["A", "B"],
                        "real_viability": "UNKNOWN",
                        "reciprocity": "NOT_EVALUABLE",
                        "viability_basis": [],
                        "reciprocity_basis": [],
                    }
                },
                self.canonical([]),
            )
        )
        output = result.canonical_updates["viability_reciprocity"]
        self.assertEqual(output["real_viability"], "UNKNOWN")
        self.assertEqual(output["reciprocity"], "NOT_EVALUABLE")
        self.assertFalse(output["absence_used_as_asymmetry"])
        self.assertFalse(output["mental_states_inferred"])
        self.assertFalse(output["consent_inferred"])
        self.assertFalse(output["fidelity_inferred"])

    def test_phase_and_phenomenology_are_not_factual_substitutes(self):
        canonical = {
            **self.canonical(
                [
                    self.event("E1", "VIABILITY_FACT"),
                    self.event("E2", "RECIPROCITY_FACT"),
                ]
            ),
            "temporal_activation": {
                "phase": "REUNION",
            },
            "doctrine_hermeneutics": {
                "claims": [{"statement": "Metaphysical interpretation"}],
            },
        }
        result = m29_viability_reciprocity(
            ctx(
                "M29",
                {"viability_reciprocity_assessment": self.assessment()},
                canonical,
            )
        )
        output = result.canonical_updates["viability_reciprocity"]

        self.assertFalse(output["phase_used_as_viability"])
        self.assertFalse(
            output["phenomenology_used_as_reciprocity_fact"]
        )
        self.assertFalse(output["mental_states_inferred"])




class TestReportingFirewall(unittest.TestCase):
    def canonical(self, mode="FULL", **overrides):
        data = {
            "schema_version": "1.0.0",
            "analysis_mode": mode,
            "evidence": [],
            "models": {
                "AF": {"iem": None, "state": "NOT_EVALUABLE"},
                "KA": {"iem": None, "state": "NOT_EVALUABLE"},
                "AG": {"iem": None, "state": "NOT_EVALUABLE"},
                "LG": {"iem": None, "state": "NOT_EVALUABLE"},
            },
            "indices": {
                "IDD": None,
                "IAT": None,
                "ICC": 90,
                "IRC": 80,
                "ICE": None,
            },
            "coverage": {"ICC": 90},
            "robustness": {"IRC": 80},
            "counterevidence": [],
            "ontology": {},
            "doctrine": [],
            "temporal": {},
            "limitations": [],
        }
        data.update(overrides)
        return data

    def completed_trace(self):
        return {
            f"M{i:02d}": ModuleResult(
                module_id=f"M{i:02d}",
                status=ExecutionStatus.COMPLETED,
            )
            for i in range(30)
        }

    def test_valid_full_with_complete_trace_is_ready(self):
        result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": self.canonical()},
                prior=self.completed_trace(),
            )
        )
        gate = result.canonical_updates["report_gate"]

        self.assertTrue(gate["reportable"])
        self.assertEqual(gate["state"], "READY")
        self.assertEqual(gate["execution_trace_state"], "AVAILABLE")
        self.assertFalse(gate["canonical_values_mutated"])
        self.assertIsNotNone(gate["canonical_fingerprint"])

    def test_imported_canonical_without_trace_is_partial_not_blocked(self):
        canonical = self.canonical()
        result = m30_report_gate(
            ctx("M30", {"canonical_analysis": canonical})
        )
        gate = result.canonical_updates["report_gate"]

        self.assertTrue(gate["reportable"])
        self.assertEqual(gate["state"], "PARTIAL")
        self.assertIn(
            "EXECUTION_TRACE_UNAVAILABLE",
            gate["degradation_reasons"],
        )
        self.assertEqual(
            result.canonical_updates["canonical_analysis"],
            canonical,
        )

    def test_failed_prior_module_blocks_report(self):
        prior = self.completed_trace()
        prior["M10"] = ModuleResult(
            module_id="M10",
            status=ExecutionStatus.FAILED,
        )
        result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": self.canonical()},
                prior=prior,
            )
        )
        gate = result.canonical_updates["report_gate"]

        self.assertFalse(gate["reportable"])
        self.assertEqual(gate["state"], "BLOCKED")
        self.assertIn("FAILED_PRIOR_MODULES", gate["blocking_issues"])
        self.assertEqual(gate["failed_modules"], ["M10"])

    def test_not_evaluable_prior_module_degrades_to_partial(self):
        prior = self.completed_trace()
        prior["M05"] = ModuleResult(
            module_id="M05",
            status=ExecutionStatus.NOT_EVALUABLE,
        )
        result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": self.canonical()},
                prior=prior,
            )
        )
        gate = result.canonical_updates["report_gate"]

        self.assertTrue(gate["reportable"])
        self.assertEqual(gate["state"], "PARTIAL")
        self.assertIn(
            "PRIOR_MODULES_NOT_EVALUABLE",
            gate["degradation_reasons"],
        )
        self.assertEqual(gate["not_evaluable_modules"], ["M05"])

    def test_targeted_and_temporal_are_partial_by_scope(self):
        for mode in ("TARGETED", "TEMPORAL"):
            result = m30_report_gate(
                ctx(
                    "M30",
                    {"canonical_analysis": self.canonical(mode=mode)},
                    prior=self.completed_trace(),
                )
            )
            gate = result.canonical_updates["report_gate"]

            self.assertTrue(gate["reportable"])
            self.assertEqual(gate["state"], "PARTIAL")
            self.assertIn(
                f"PARTIAL_ANALYSIS_MODE:{mode}",
                gate["degradation_reasons"],
            )

    def test_full_missing_model_is_blocked(self):
        canonical = self.canonical()
        del canonical["models"]["LG"]

        result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": canonical},
                prior=self.completed_trace(),
            )
        )
        gate = result.canonical_updates["report_gate"]

        self.assertFalse(gate["reportable"])
        self.assertEqual(gate["state"], "BLOCKED")
        self.assertIn(
            "FULL_MISSING_MODELS:LG",
            gate["blocking_issues"],
        )

    def test_positive_model_claim_requires_canonical_evidence(self):
        canonical = self.canonical()
        canonical["models"]["AF"] = {
            "iem": 80,
            "state": "COMPATIBLE",
        }

        result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": canonical},
                prior=self.completed_trace(),
            )
        )
        gate = result.canonical_updates["report_gate"]

        self.assertFalse(gate["reportable"])
        self.assertIn(
            "POSITIVE_MODEL_CLAIM_WITHOUT_EVIDENCE",
            gate["blocking_issues"],
        )

    def test_not_evaluable_model_cannot_keep_numeric_iem(self):
        canonical = self.canonical()
        canonical["models"]["AF"] = {
            "iem": 50,
            "state": "NOT_EVALUABLE",
        }

        result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": canonical},
                prior=self.completed_trace(),
            )
        )
        gate = result.canonical_updates["report_gate"]

        self.assertFalse(gate["reportable"])
        self.assertIn(
            "AF:NOT_EVALUABLE_WITH_NUMERIC_IEM",
            gate["blocking_issues"],
        )

    def test_raw_and_snapshot_conflict_blocks_without_overwrite(self):
        raw = self.canonical()
        snapshot = self.canonical()
        snapshot["analysis_mode"] = "REPORT"

        result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": raw},
                canonical={"canonical_analysis": snapshot},
                prior=self.completed_trace(),
            )
        )
        gate = result.canonical_updates["report_gate"]

        self.assertEqual(gate["state"], "BLOCKED")
        self.assertTrue(gate["canonical_source_conflict"])
        self.assertEqual(gate["source"], "CONFLICT")
        self.assertNotIn(
            "canonical_analysis",
            result.canonical_updates,
        )

    def test_absent_canonical_blocks(self):
        result = m30_report_gate(
            ctx("M30", prior=self.completed_trace())
        )
        gate = result.canonical_updates["report_gate"]

        self.assertFalse(gate["reportable"])
        self.assertEqual(gate["state"], "BLOCKED")
        self.assertIn(
            "CANONICAL_ANALYSIS_ABSENT",
            gate["blocking_issues"],
        )

    def test_m31_builds_reference_model_only(self):
        canonical = self.canonical()
        gate_result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": canonical},
                prior=self.completed_trace(),
            )
        )
        gate = gate_result.canonical_updates["report_gate"]

        result = m31_report(
            ctx(
                "M31",
                canonical={
                    "canonical_analysis": canonical,
                    "report_gate": gate,
                },
            )
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        model = result.canonical_updates["report_document_model"]

        self.assertEqual(model["report_state"], "READY")
        self.assertEqual(len(model["sections"]), 11)
        self.assertEqual(
            sum(model["section_counts"].values()),
            11,
        )
        self.assertTrue(model["canonical_fingerprint_verified"])
        self.assertEqual(
            model["canonical_fingerprint"],
            gate["canonical_fingerprint"],
        )
        self.assertFalse(model["canonical_values_embedded"])
        self.assertFalse(model["canonical_values_mutated"])
        self.assertFalse(model["prose_generated"])
        self.assertFalse(model["rendered_document_created"])
        self.assertFalse(model["docx_created"])
        self.assertFalse(model["pdf_created"])
        self.assertFalse(model["pdf_preflight_performed"])

    def test_m31_partial_inherits_degradation_reasons(self):
        canonical = self.canonical(mode="TARGETED")
        gate_result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": canonical},
                prior=self.completed_trace(),
            )
        )
        gate = gate_result.canonical_updates["report_gate"]
        self.assertEqual(gate["state"], "PARTIAL")

        result = m31_report(
            ctx(
                "M31",
                canonical={
                    "canonical_analysis": canonical,
                    "report_gate": gate,
                },
            )
        )
        model = result.canonical_updates["report_document_model"]

        self.assertEqual(model["report_state"], "PARTIAL")
        self.assertTrue(model["partial_disclosure_required"])
        self.assertEqual(
            model["degradation_reasons"],
            gate["degradation_reasons"],
        )

    def test_m31_section_availability_is_explicit(self):
        canonical = self.canonical(mode="TARGETED")
        del canonical["doctrine"]
        del canonical["temporal"]

        gate_result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": canonical},
                prior=self.completed_trace(),
            )
        )
        gate = gate_result.canonical_updates["report_gate"]

        result = m31_report(
            ctx(
                "M31",
                canonical={
                    "canonical_analysis": canonical,
                    "report_gate": gate,
                },
            )
        )
        model = result.canonical_updates["report_document_model"]
        by_id = {
            section["section_id"]: section
            for section in model["sections"]
        }

        self.assertEqual(
            by_id["S07_TEMPORAL"]["section_state"],
            "NOT_AVAILABLE",
        )
        self.assertEqual(
            by_id["S09_DOCTRINE"]["section_state"],
            "NOT_AVAILABLE",
        )
        self.assertIn(
            "temporal",
            by_id["S07_TEMPORAL"]["missing_required_paths"],
        )
        self.assertIn(
            "doctrine",
            by_id["S09_DOCTRINE"]["missing_required_paths"],
        )

    def test_m31_rejects_canonical_changed_after_m30(self):
        canonical = self.canonical()
        gate_result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": canonical},
                prior=self.completed_trace(),
            )
        )
        gate = gate_result.canonical_updates["report_gate"]

        changed = self.canonical()
        changed["limitations"] = ["Changed after gate."]

        with self.assertRaises(ValueError):
            m31_report(
                ctx(
                    "M31",
                    canonical={
                        "canonical_analysis": changed,
                        "report_gate": gate,
                    },
                )
            )

    def test_m31_requires_m30_fingerprint(self):
        canonical = self.canonical()
        gate = {
            "reportable": True,
            "state": "READY",
            "canonical_fingerprint": None,
            "degradation_reasons": [],
        }
        with self.assertRaises(ValueError):
            m31_report(
                ctx(
                    "M31",
                    canonical={
                        "canonical_analysis": canonical,
                        "report_gate": gate,
                    },
                )
            )

    def test_m31_blocked_gate_is_not_evaluable(self):
        canonical = self.canonical()
        gate = {
            "reportable": False,
            "state": "BLOCKED",
            "canonical_fingerprint": None,
            "degradation_reasons": [],
        }
        result = m31_report(
            ctx(
                "M31",
                canonical={
                    "canonical_analysis": canonical,
                    "report_gate": gate,
                },
            )
        )
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)
        self.assertNotIn("report_document_model", result.canonical_updates)




if __name__ == "__main__":
    unittest.main()
