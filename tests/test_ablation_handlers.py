import unittest

from almas_tfa.ablation_handlers import ABLATION_RUNS, m22_ablation
from almas_tfa.module_contract import ExecutionStatus, ModuleContext


class TestStructuralAblation(unittest.TestCase):
    def test_canonical_ablation_filters(self):
        evidence = [
            {
                "evidence_id": "E1",
                "root_key": "A:SUN|B:MOON|CONJUNCTION",
                "technique_family": "SYN",
                "dependency_family": "SYN",
                "canonical_source": "synastry",
                "contact": {
                    "subject_a": "A",
                    "subject_b": "B",
                    "point_a": "SUN",
                    "point_b": "MOON",
                    "point_a_type": "LUMINARY",
                    "point_b_type": "LUMINARY",
                },
            },
            {
                "evidence_id": "E2",
                "root_key": "A:JUNO|B:SUN|CONJUNCTION",
                "technique_family": "SECONDARY",
                "dependency_family": "SECONDARY",
                "canonical_source": "secondary_symbolic",
                "contact": {
                    "subject_a": "A",
                    "subject_b": "B",
                    "point_a": "JUNO",
                    "point_b": "SUN",
                },
            },
            {
                "evidence_id": "E3",
                "root_key": "A:SUN|B:MOON|CONJUNCTION|NATAL>DRACONIC",
                "technique_family": "NATAL_DRACONIC",
                "dependency_family": "NATAL_DRACONIC",
                "canonical_source": "natal_draconic_cross",
                "contact": {
                    "subject_a": "A",
                    "subject_b": "B",
                    "point_a": "SUN",
                    "point_b": "MOON",
                },
            },
            {
                "evidence_id": "E4",
                "root_key": "A:AXIS_HORIZON|B:SUN|AXIS_ANGLE:0.000000",
                "technique_family": "SYN",
                "dependency_family": "SYN",
                "canonical_source": "synastry",
                "contact": {
                    "subject_a": "A",
                    "subject_b": "B",
                    "point_a": "ASC",
                    "point_b": "SUN",
                    "point_a_type": "ANGLE",
                    "point_b_type": "LUMINARY",
                },
            },
            {
                "evidence_id": "E5",
                "root_key": "A:AXIS_NODES|B:MOON|CONJUNCTION",
                "technique_family": "SYN",
                "dependency_family": "SYN",
                "canonical_source": "synastry",
                "contact": {
                    "subject_a": "A",
                    "subject_b": "B",
                    "point_a": "NORTH_NODE",
                    "point_b": "MOON",
                    "point_a_type": "NODE",
                    "point_b_type": "LUMINARY",
                },
            },
        ]

        roots = [
            {"root_id": f"R{i}", "evidence_ids": [f"E{i}"]}
            for i in range(1, 6)
        ]
        canonical = {
            "deduplicated_evidence": {"retained": evidence},
            "independent_roots": {"roots": roots},
        }
        context = ModuleContext(
            module_id="M22",
            module_name="ablation",
            mode="FULL",
            raw_input={},
            canonical_snapshot=canonical,
            prior_results={},
        )

        result = m22_ablation(context)
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["ablation"]
        self.assertEqual(
            [run["run"] for run in output["runs"]],
            list(ABLATION_RUNS),
        )

        runs = {run["run"]: run for run in output["runs"]}
        self.assertIn("R2", runs["AB1_NO_ASTEROIDS"]["lost_root_ids"])
        self.assertIn("R3", runs["AB3_NO_DRACONIC"]["lost_root_ids"])
        self.assertIn("R4", runs["AB5_NO_HOUSES_ANGLES"]["lost_root_ids"])
        self.assertIn("R5", runs["AB6_NO_NODES"]["lost_root_ids"])
        self.assertEqual(
            runs["AB7_TROPICAL_PLANETARY_CORE"]["surviving_root_ids"],
            ["R1"],
        )
        self.assertEqual(
            runs["AB8_INDIVIDUAL_ONLY"]["surviving_root_ids"],
            [],
        )
        self.assertTrue(output["structural_only"])
        self.assertFalse(output["dependency_classes_assigned"])


if __name__ == "__main__":
    unittest.main()
