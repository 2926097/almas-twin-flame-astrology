from __future__ import annotations

import unittest

from almas_tfa.canonical_assembly import (
    assemble_canonical_analysis,
    derive_canonical_coverage,
    load_canonical_assembly_policy,
)
from almas_tfa.module_contract import ExecutionStatus, ModuleContext, ModuleResult
from almas_tfa.report_gate_handlers import make_m30_report_gate_auto


def completed(module_id: str) -> ModuleResult:
    return ModuleResult(
        module_id=module_id,
        status=ExecutionStatus.COMPLETED,
    )


def prior_all():
    return {
        f"M{i:02d}": completed(f"M{i:02d}")
        for i in range(30)
    }


def natal_context():
    houses = {str(i): {"longitude": float(i * 30)} for i in range(1, 13)}
    return {
        "subjects": {
            "A": {
                "angles": {"ASC": {"longitude": 10.0}, "MC": {"longitude": 100.0}},
                "house_cusps": houses,
            },
            "B": {
                "angles": {"ASC": {"longitude": 20.0}, "MC": {"longitude": 110.0}},
                "house_cusps": houses,
            },
        }
    }


def canonical_base(*, with_ice=True):
    roots = {
        "roots": [
            {
                "root_id": "R0001",
                "root_key": "A:SUN|B:MOON|TRINE",
                "strength": 0.9,
                "strength_state": "CALCULATED_CORE",
                "core_eligible": True,
                "dependency_families": ["SYN"],
            }
        ],
        "root_count": 1,
        "strength_policy_applied": True,
        "strength_policy_id": "ALMAS_ROOT_STRENGTH_BASELINE_V1",
    }
    counter = {
        "models": {
            model: {
                "items": [],
                "contradiction_count": 0,
                "essential_contradiction": False,
            }
            for model in ("AF", "KA", "AG", "LG")
        },
        "suppressed": [],
        "ice_state": "PRECOMPUTED" if with_ice else "NOT_CALCULATED",
        "ice_by_model": (
            {model: 0.0 for model in ("AF", "KA", "AG", "LG")}
            if with_ice
            else None
        ),
        "missing_data_penalized": False,
    }
    return {
        "natal_context": natal_context(),
        "independent_roots": roots,
        "pillars": {
            "PA": 90.0,
            "PK": 90.0,
            "PE": 90.0,
            "PR": 90.0,
            "PX": 90.0,
            "PT": 90.0,
            "PS": 90.0,
            "PU": None,
        },
        "structural_model_indices": {
            model: {
                "core": 0.9,
                "support": 0.9,
                "iem_pre": 89.1,
                "ice": 0.0,
                "iem_final": 89.1,
                "essential_evaluable": True,
                "supported_gate": None,
            }
            for model in ("AF", "KA", "AG", "LG")
        },
        "counterevidence": counter,
        "pairwise_idd": {
            "AF_vs_KA": {"idd": 35.0, "band": "MATERIAL"},
            "AF_vs_AG": {"idd": 20.0, "band": "TRANSITION"},
            "AG_vs_LG": {"idd": 12.0, "band": "OVERLAP"},
        },
        "robustness_index": {
            "irc": 90.0,
            "r_min": 0.8,
            "components": [],
            "component_count": 4,
        },
    }


class TestCanonicalAssemblyQ7(unittest.TestCase):
    def test_policy_is_frozen_and_case_fit_forbidden(self):
        policy = load_canonical_assembly_policy()
        self.assertEqual(
            policy["policy_id"],
            "ALMAS_CANONICAL_ASSEMBLY_V1",
        )
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertFalse(
            policy["principles"]["assembler_recalculates_astrology"]
        )
        self.assertEqual(
            policy["global_idd"]["method"],
            "MIN_EVALUABLE_PAIRWISE_IDD",
        )

    def test_full_structural_coverage_is_100(self):
        result = derive_canonical_coverage(
            canonical_base(),
            prior_all(),
        )
        self.assertAlmostEqual(result["ICC"], 100.0)
        self.assertTrue(
            all(
                domain["q"] == 1.0
                for domain in result["domains"].values()
            )
        )

    def test_global_idd_uses_weakest_pair(self):
        result = assemble_canonical_analysis(
            canonical_base(),
            prior_all(),
        )
        self.assertEqual(result["state"], "EVALUABLE")
        canonical = result["canonical_analysis"]
        self.assertAlmostEqual(canonical["indices"]["IDD"], 12.0)
        self.assertEqual(
            canonical["assembly"]["policy_id"],
            "ALMAS_CANONICAL_ASSEMBLY_V1",
        )

    def test_supported_requires_evaluable_ice(self):
        result = assemble_canonical_analysis(
            canonical_base(with_ice=False),
            prior_all(),
        )
        self.assertEqual(result["state"], "EVALUABLE")
        canonical = result["canonical_analysis"]
        self.assertIsNone(canonical["indices"]["ICE"])
        for model in ("AF", "KA", "AG", "LG"):
            self.assertNotEqual(
                canonical["models"][model]["state"],
                "SUPPORTED",
            )
            self.assertEqual(
                canonical["models"][model]["state"],
                "COMPATIBLE",
            )
            self.assertEqual(
                canonical["models"][model]["ice_state"],
                "NOT_EVALUABLE",
            )

    def test_supported_gate_can_close_after_m25(self):
        result = assemble_canonical_analysis(
            canonical_base(with_ice=True),
            prior_all(),
        )
        canonical = result["canonical_analysis"]
        self.assertEqual(canonical["coverage"]["ICC"], 100.0)
        self.assertEqual(canonical["robustness"]["IRC"], 90.0)
        self.assertEqual(canonical["robustness"]["R_min"], 0.8)
        for model in ("AF", "KA", "AG", "LG"):
            self.assertEqual(
                canonical["models"][model]["state"],
                "SUPPORTED",
            )

    def test_auto_m30_builds_canonical_and_reaches_ready(self):
        handler = make_m30_report_gate_auto()
        result = handler(
            ModuleContext(
                module_id="M30",
                module_name="report_gate",
                mode="FULL",
                raw_input={},
                canonical_snapshot=canonical_base(with_ice=True),
                prior_results=prior_all(),
            )
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertIn("canonical_analysis", result.canonical_updates)
        self.assertIn("report_gate", result.canonical_updates)
        gate = result.canonical_updates["report_gate"]
        self.assertEqual(gate["state"], "READY")
        self.assertTrue(gate["reportable"])
        self.assertEqual(gate["source"], "CANONICAL_SNAPSHOT")
        self.assertIn(
            "M30 source=AUTO_CANONICAL_ASSEMBLY_Q7",
            result.diagnostics,
        )


if __name__ == "__main__":
    unittest.main()
