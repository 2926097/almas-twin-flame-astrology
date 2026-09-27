import unittest

from almas_tfa.evidence_handlers import (
    m15_evidence_extraction,
    m16_dependency_deduplication,
    m17_independent_roots,
)
from almas_tfa.module_contract import ExecutionStatus, ModuleContext


def ctx(module_id, canonical):
    return ModuleContext(
        module_id=module_id,
        module_name=module_id,
        mode="FULL",
        raw_input={},
        canonical_snapshot=canonical,
        prior_results={},
    )


class TestEvidenceGraph(unittest.TestCase):
    def setUp(self):
        self.canonical = {
            "synastry": {
                "contacts": [
                    {
                        "subject_a": "A",
                        "point_a": "ASC",
                        "subject_b": "B",
                        "point_b": "SUN",
                        "aspect": "CONJUNCTION",
                        "angle": 0.0,
                        "orb": 0.5,
                        "orb_limit": 3.0,
                        "exactness": 0.97,
                    },
                    {
                        "subject_a": "A",
                        "point_a": "DSC",
                        "subject_b": "B",
                        "point_b": "SUN",
                        "aspect": "OPPOSITION",
                        "angle": 180.0,
                        "orb": 0.5,
                        "orb_limit": 3.0,
                        "exactness": 0.97,
                    },
                ]
            },
            "draconic_draconic": {
                "contacts": [
                    {
                        "subject_a": "A",
                        "point_a": "ASC",
                        "subject_b": "B",
                        "point_b": "SUN",
                        "aspect": "CONJUNCTION",
                        "angle": 0.0,
                        "orb": 0.2,
                        "orb_limit": 2.0,
                        "exactness": 0.99,
                    }
                ],
                "corroborative_only": True,
            },
        }

    def test_axis_pair_deduplicates_inside_same_family(self):
        m15 = m15_evidence_extraction(ctx("M15", self.canonical))
        self.assertEqual(m15.status, ExecutionStatus.COMPLETED)

        canonical = {
            **self.canonical,
            "evidence_graph": m15.canonical_updates["evidence_graph"],
        }
        m16 = m16_dependency_deduplication(ctx("M16", canonical))

        self.assertEqual(m16.status, ExecutionStatus.COMPLETED)
        output = m16.canonical_updates["deduplicated_evidence"]

        self.assertEqual(output["retained_count"], 2)
        self.assertEqual(output["suppressed_count"], 1)

    def test_m17_keeps_core_and_corroboration_separate(self):
        m15 = m15_evidence_extraction(ctx("M15", self.canonical))
        c16 = {
            **self.canonical,
            "evidence_graph": m15.canonical_updates["evidence_graph"],
        }
        m16 = m16_dependency_deduplication(ctx("M16", c16))
        c17 = {
            **c16,
            "deduplicated_evidence": m16.canonical_updates["deduplicated_evidence"],
        }
        m17 = m17_independent_roots(ctx("M17", c17))

        self.assertEqual(m17.status, ExecutionStatus.COMPLETED)
        roots = m17.canonical_updates["independent_roots"]["roots"]
        self.assertEqual(len(roots), 1)

        root = roots[0]
        self.assertTrue(root["core_eligible"])
        self.assertEqual(len(root["core_evidence_ids"]), 1)
        self.assertEqual(len(root["support_evidence_ids"]), 1)
        self.assertAlmostEqual(root["strength"], 0.97)
        self.assertEqual(root["strength_state"], "CALCULATED_CORE")
        self.assertEqual(root["policy_id"], "ALMAS_ROOT_STRENGTH_BASELINE_V1")
        self.assertIn("AXIS_HORIZON", root["point_ids"])
        self.assertIn("SUN", root["point_ids"])
        self.assertEqual(len(root["concrete_contacts"]), 2)

        by_family = {
            item["dependency_family"]: item
            for item in root["concrete_contacts"]
        }
        self.assertEqual(by_family["SYN"]["point_a"], "ASC")
        self.assertEqual(by_family["SYN"]["point_b"], "SUN")
        self.assertEqual(by_family["SYN"]["relation_id"], "CONJUNCTION")
        self.assertEqual(
            by_family["DRACONIC_DD"]["point_a"],
            "ASC",
        )
        self.assertEqual(
            root["root_key"],
            "A:AXIS_HORIZON|B:SUN|AXIS_ANGLE:0.000000",
        )

    def test_m15_ignores_relationship_field_internal_contacts(self):
        canonical = {
            "relationship_chart_consonance": {
                "contacts": [
                    {
                        "subject_a": "RELCHART_COMPOSITE",
                        "point_a": "SUN",
                        "subject_b": "RELCHART_DAVISON",
                        "point_b": "SUN",
                        "aspect": "CONJUNCTION",
                        "angle": 0.0,
                        "orb": 1.0,
                        "orb_limit": 3.0,
                        "exactness": 0.9,
                    }
                ],
                "field_context": {
                    "authoring_only": True,
                    "structural_evidence_used": False,
                    "creates_independent_roots": False,
                    "composite": {
                        "internal_contacts": [
                            {
                                "subject_a": "RELCHART_COMPOSITE",
                                "point_a": "SUN",
                                "subject_b": "RELCHART_COMPOSITE",
                                "point_b": "VENUS",
                                "aspect": "TRINE",
                                "angle": 120.0,
                                "orb": 0.5,
                                "orb_limit": 3.0,
                                "exactness": 0.97,
                            }
                        ]
                    },
                },
            }
        }

        result = m15_evidence_extraction(ctx("M15", canonical))
        evidence = result.canonical_updates["evidence_graph"]["evidence"]

        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["source_module"], "M09")
        self.assertEqual(evidence[0]["contact"]["point_a"], "SUN")
        self.assertEqual(evidence[0]["contact"]["point_b"], "SUN")

    def test_secondary_only_root_never_becomes_core(self):
        canonical = {
            "secondary_symbolic": {
                "contacts": [
                    {
                        "subject_a": "A",
                        "point_a": "JUNO",
                        "subject_b": "B",
                        "point_b": "SUN",
                        "aspect": "CONJUNCTION",
                        "angle": 0.0,
                        "exactness": 1.0,
                        "support_only": True,
                    }
                ]
            }
        }
        m15 = m15_evidence_extraction(ctx("M15", canonical))
        m16 = m16_dependency_deduplication(
            ctx(
                "M16",
                {
                    **canonical,
                    "evidence_graph": m15.canonical_updates["evidence_graph"],
                },
            )
        )
        m17 = m17_independent_roots(
            ctx(
                "M17",
                {
                    **canonical,
                    "deduplicated_evidence": m16.canonical_updates[
                        "deduplicated_evidence"
                    ],
                },
            )
        )
        root = m17.canonical_updates["independent_roots"]["roots"][0]
        self.assertFalse(root["core_eligible"])
        self.assertEqual(root["core_evidence_ids"], [])
        self.assertEqual(len(root["support_evidence_ids"]), 1)
        self.assertAlmostEqual(root["strength"], 1.0)
        self.assertEqual(root["strength_state"], "CALCULATED_SUPPORT_ONLY")


if __name__ == "__main__":
    unittest.main()
