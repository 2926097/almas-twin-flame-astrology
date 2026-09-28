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


def root(root_id, points, relation, strength, family):
    return {
        "root_id": root_id,
        "root_key": root_id + ":KEY",
        "point_ids": list(points),
        "relation_ids": [relation],
        "strength": strength,
        "strength_state": "CALCULATED_CORE",
        "core_eligible": True,
        "independent_family_count": 1,
        "dependency_families": [family],
        "evidence_strengths": [
            {
                "evidence_id": root_id + ":" + family,
                "strength": strength,
                "core_eligible": True,
                "support_only": False,
                "dependency_family": family,
                "technique_family": family,
            }
        ],
    }


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

    def test_m18_derives_semantic_px_from_cross_family_motifs(self):
        roots = [
            root("R1", ["SUN", "MOON"], "TRINE", 0.90, "SYN"),
            root("R2", ["VENUS", "MOON"], "SEXTILE", 0.80, "DECLINATION"),
            root("R3", ["SUN", "MOON"], "OPPOSITION", 0.85, "ANTISCIA"),
            root("R4", ["AXIS_NODES", "VENUS"], "SQUARE", 0.70, "SYN"),
            root("R5", ["PLUTO", "VENUS"], "CONJUNCTION", 0.75, "SYN"),
        ]
        result = default_handlers()["M18"](self.context(roots))
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertEqual(
            result.payload["source"],
            "CANONICAL_INDEPENDENT_ROOTS",
        )
        pillars = result.canonical_updates["pillars"]
        self.assertGreater(pillars["PA"], 0)
        self.assertGreater(pillars["PE"], 0)
        self.assertGreater(pillars["PK"], 0)
        self.assertGreater(pillars["PT"], 0)
        self.assertGreater(pillars["PX"], 0)
        self.assertIsNone(pillars["PU"])
        attribution = result.canonical_updates["pillar_attribution"]
        self.assertEqual(
            attribution["semantic_motif_policy_id"],
            "ALMAS_SEMANTIC_MOTIF_V2",
        )

    def test_incomplete_structural_coverage_keeps_absence_not_evaluable(self):
        roots = [
            root("R1", ["SUN", "MOON"], "TRINE", 0.90, "SYN")
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
        self.assertIsNone(pillars["PX"])
        self.assertIsNone(pillars["PU"])

    def test_complete_structural_coverage_allows_true_structural_zero(self):
        roots = [
            root("R1", ["SUN", "MOON"], "TRINE", 0.90, "SYN")
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
