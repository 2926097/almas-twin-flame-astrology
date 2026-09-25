import unittest

from almas_tfa.handlers import default_handlers
from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.orchestrator import Orchestrator


def full_manifest():
    return {
        "mode": "FULL",
        "manifest_version": "1.0.0",
        "modules": [
            {"id": f"M{i:02d}", "name": f"module_{i:02d}"}
            for i in range(32)
        ],
    }


class TestDeterministicHandlers(unittest.TestCase):
    def test_precomputed_pipeline_adapters(self):
        payload = {
            "mode": "FULL",
            "pillars": {
                "PA": 90,
                "PK": 80,
                "PE": 85,
                "PR": 92,
                "PX": 88,
                "PT": 82,
                "PS": 70,
                "PU": 50,
            },
            "ice_by_model": {"AF": 0, "KA": 5, "AG": 0, "LG": 10},
            "icc": 90,
            "irc": 85,
            "r_min": 0.8,
            "attributions": {
                "AG": {"root_affinity": 1, "root_mirror": 1},
                "LG": {"root_affinity": 1, "root_transform": 1},
            },
            "robustness_components": [1.0, 0.81, 0.64],
        }

        run = Orchestrator(default_handlers()).run(payload, full_manifest())

        self.assertEqual(run.results["M00"].status, ExecutionStatus.COMPLETED)
        self.assertEqual(run.results["M18"].status, ExecutionStatus.COMPLETED)
        self.assertEqual(run.results["M19"].status, ExecutionStatus.COMPLETED)
        self.assertEqual(run.results["M21"].status, ExecutionStatus.COMPLETED)
        self.assertEqual(run.results["M25"].status, ExecutionStatus.COMPLETED)

        self.assertEqual(run.canonical["pillars"]["PA"], 90)
        self.assertAlmostEqual(
            run.canonical["structural_model_indices"]["AF"]["iem_final"],
            89.76607950668227,
        )
        self.assertAlmostEqual(
            run.canonical["pairwise_idd"]["AG_vs_LG"]["idd"],
            70.71067811865476,
        )
        self.assertEqual(
            run.canonical["robustness_index"]["r_min"],
            0.64,
        )

    def test_pillars_can_be_derived_from_independent_roots(self):
        context = ModuleContext(
            module_id="M18",
            module_name="pillars",
            mode="FULL",
            raw_input={
                "root_strengths": {
                    "PA": [1.0, 1.0, 1.0],
                    "PK": [0.5],
                }
            },
            canonical_snapshot={},
            prior_results={},
        )
        result = default_handlers()["M18"](context)
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertAlmostEqual(result.canonical_updates["pillars"]["PA"], 100.0)
        self.assertIsNone(result.canonical_updates["pillars"]["PE"])


if __name__ == "__main__":
    unittest.main()
