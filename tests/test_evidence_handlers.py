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
