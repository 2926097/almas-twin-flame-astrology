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
    def test_project_hypothesis_cannot_be_direct_doctrine(self):
        claim = {
            "claim_id": "C1",
            "statement": "Hipótesis sintética.",
            "epistemic_class": "E_PROJECT_HYPOTHESIS",
            "status": "COMPATIBLE",
            "source_relation": "DIRECT_DOCTRINE",
            "source_ids": [],
            "source_anchor_refs": [],
            "discriminator_state": "NOT_VALIDATED",
            "ceiling_enforced": True,
        }
        with self.assertRaises(ValueError):
            m28_doctrine_hermeneutics(ctx("M28", {"doctrinal_claims": [claim]}))

    def test_doctrine_never_adds_score(self):
        claim = {
            "claim_id": "C1",
            "statement": "Doctrina sintética con fuente.",
            "epistemic_class": "C_DOCTRINE",
            "status": "SUPPORTED",
            "source_relation": "DIRECT_DOCTRINE",
            "source_ids": ["SRC1"],
            "source_anchor_refs": ["SRC1:PASSAGE"],
            "discriminator_state": "DOCTRINAL_ONLY",
            "ceiling_enforced": True,
        }
        result = m28_doctrine_hermeneutics(
            ctx(
                "M28",
                {
                    "doctrinal_claims": [claim],
                    "source_registry": ["SRC1"],
                },
            )
        )
        output = result.canonical_updates["doctrine_hermeneutics"]
        self.assertFalse(output["doctrine_adds_structural_score"])
        self.assertEqual(output["unresolved_sources"], [])


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
