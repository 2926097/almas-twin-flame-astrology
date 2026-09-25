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
    def test_requires_documentary_roles(self):
        canonical = {
            "documentary_events": {
                "events": [
                    {
                        "event_id": "E1",
                        "evidence_roles": ["VIABILITY_FACT"],
                    },
                    {
                        "event_id": "E2",
                        "evidence_roles": ["RECIPROCITY_FACT"],
                    },
                ]
            }
        }
        result = m29_viability_reciprocity(
            ctx(
                "M29",
                {
                    "viability_reciprocity_assessment": {
                        "real_viability": "STABLE",
                        "reciprocity": "BILATERAL",
                        "viability_event_refs": ["E1"],
                        "reciprocity_event_refs": ["E2"],
                    }
                },
                canonical,
            )
        )
        output = result.canonical_updates["viability_reciprocity"]
        self.assertFalse(output["astrology_used_as_real_world_fact"])
        self.assertFalse(output["future_decisions_inferred"])


class TestReportingFirewall(unittest.TestCase):
    def setUp(self):
        self.canonical_analysis = {
            "schema_version": "1.0.0",
            "analysis_mode": "FULL",
            "evidence": [],
            "models": {},
            "coverage": {},
            "robustness": {},
            "counterevidence": [],
        }

    def test_m30_copies_without_mutating_canonical_input(self):
        result = m30_report_gate(
            ctx("M30", {"canonical_analysis": self.canonical_analysis})
        )
        self.assertTrue(result.canonical_updates["report_gate"]["reportable"])
        self.assertFalse(
            result.canonical_updates["report_gate"]["canonical_values_mutated"]
        )
        self.assertEqual(
            result.canonical_updates["canonical_analysis"],
            self.canonical_analysis,
        )

    def test_failed_prior_module_blocks_report(self):
        prior = {
            "M10": ModuleResult(
                module_id="M10",
                status=ExecutionStatus.FAILED,
            )
        }
        result = m30_report_gate(
            ctx(
                "M30",
                {"canonical_analysis": self.canonical_analysis},
                prior=prior,
            )
        )
        self.assertFalse(result.canonical_updates["report_gate"]["reportable"])

    def test_m31_builds_reference_model_only(self):
        gate = {
            "reportable": True,
            "state": "READY",
        }
        result = m31_report(
            ctx(
                "M31",
                canonical={
                    "canonical_analysis": self.canonical_analysis,
                    "report_gate": gate,
                },
            )
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        model = result.canonical_updates["report_document_model"]
        self.assertEqual(len(model["sections"]), 11)
        self.assertFalse(model["canonical_values_mutated"])
        self.assertFalse(model["rendered_document_created"])


if __name__ == "__main__":
    unittest.main()
