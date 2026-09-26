from __future__ import annotations

import unittest

from almas_tfa.handlers import default_handlers
from almas_tfa.module_contract import ExecutionStatus, ModuleContext, ModuleResult


REQUIRED = ("M03", "M05", "M06", "M09", "M11")


def completed(module_id: str) -> ModuleResult:
    return ModuleResult(
        module_id=module_id,
        status=ExecutionStatus.COMPLETED,
    )


class M18AutomaticPillarsTests(unittest.TestCase):
    def context(self, roots, *, complete=True):
        prior = {
            module_id: completed(module_id)
            for module_id in REQUIRED
        }
        if not complete:
            prior["M09"] = ModuleResult(
                module_id="M09",
                status=ExecutionStatus.NOT_EVALUABLE,
            )

        return ModuleContext(
            module_id="M18",
            module_name="pillars",
            mode="FULL",
            raw_input={},
            canonical_snapshot={
                "independent_roots": {
                    "roots": roots,
                    "root_count": len(roots),
                }
            },
            prior_results=prior,
        )

    def test_m18_prefers_canonical_roots_and_derives_pillars(self):
        roots = [
            {
                "root_id": "R1",
                "point_ids": ["SUN", "MOON"],
                "relation_ids": ["TRINE"],
                "strength": 0.90,
                "strength_state": "CALCULATED_CORE",
                "core_eligible": True,
                "independent_family_count": 2,
            },
            {
                "root_id": "R2",
                "point_ids": ["MERCURY", "MOON"],
                "relation_ids": ["SEXTILE"],
                "strength": 0.80,
                "strength_state": "CALCULATED_CORE",
                "core_eligible": True,
                "independent_family_count": 1,
            },
            {
                "root_id": "R3",
                "point_ids": ["SUN", "MOON"],
                "relation_ids": ["OPPOSITION"],
                "strength": 0.85,
                "strength_state": "CALCULATED_CORE",
                "core_eligible": True,
                "independent_family_count": 1,
            },
            {
                "root_id": "R4",
                "point_ids": ["AXIS_NODES", "VENUS"],
                "relation_ids": ["SQUARE"],
                "strength": 0.70,
                "strength_state": "CALCULATED_CORE",
                "core_eligible": True,
                "independent_family_count": 1,
            },
            {
                "root_id": "R5",
                "point_ids": ["PLUTO", "VENUS"],
                "relation_ids": ["CONJUNCTION"],
                "strength": 0.75,
                "strength_state": "CALCULATED_CORE",
                "core_eligible": True,
                "independent_family_count": 1,
            },
        ]
        result = default_handlers()["M18"](self.context(roots))
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertEqual(
            result.payload["source"],
            "CANONICAL_INDEPENDENT_ROOTS",
        )
        pillars = result.canonical_updates["pillars"]
        self.assertGreater(pillars["PA"], 0)
        self.assertGreater(pillars["PR"], 0)
        self.assertGreater(pillars["PE"], 0)
        self.assertGreater(pillars["PK"], 0)
        self.assertGreater(pillars["PT"], 0)
        self.assertGreater(pillars["PX"], 0)
        self.assertIsNone(pillars["PU"])
        self.assertIn("pillar_attribution", result.canonical_updates)

    def test_incomplete_structural_coverage_keeps_absence_not_evaluable(self):
        roots = [
            {
                "root_id": "R1",
                "point_ids": ["SUN", "MOON"],
                "relation_ids": ["TRINE"],
                "strength": 0.90,
                "strength_state": "CALCULATED_CORE",
                "core_eligible": True,
                "independent_family_count": 1,
            }
        ]
        result = default_handlers()["M18"](
            self.context(roots, complete=False)
        )
        pillars = result.canonical_updates["pillars"]
        self.assertGreater(pillars["PA"], 0)
        self.assertIsNone(pillars["PK"])
        self.assertIsNone(pillars["PE"])
        self.assertIsNone(pillars["PR"])
        self.assertIsNone(pillars["PT"])
        self.assertIsNone(pillars["PS"])
        self.assertIsNone(pillars["PU"])

    def test_complete_structural_coverage_allows_true_structural_zero(self):
        roots = [
            {
                "root_id": "R1",
                "point_ids": ["SUN", "MOON"],
                "relation_ids": ["TRINE"],
                "strength": 0.90,
                "strength_state": "CALCULATED_CORE",
                "core_eligible": True,
                "independent_family_count": 1,
            }
        ]
        result = default_handlers()["M18"](self.context(roots, complete=True))
        pillars = result.canonical_updates["pillars"]
        self.assertEqual(pillars["PK"], 0.0)
        self.assertEqual(pillars["PE"], 0.0)
        self.assertEqual(pillars["PR"], 0.0)
        self.assertEqual(pillars["PT"], 0.0)
        self.assertEqual(pillars["PS"], 0.0)
        self.assertEqual(pillars["PX"], 0.0)
        self.assertIsNone(pillars["PU"])


if __name__ == "__main__":
    unittest.main()
