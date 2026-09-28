from __future__ import annotations

import unittest

from almas_tfa.handlers import default_handlers
from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.pillar_attribution import derive_pillars_from_roots


def root(root_id, points, relation, family, strength=0.8):
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


def roots():
    return [
        root("R1", ["SUN", "MOON"], "TRINE", "SYN", 0.90),
        root("R2", ["SUN", "MOON"], "PARALLEL", "DECLINATION", 0.82),
        root("R3", ["MERCURY", "MOON"], "TRINE", "ANTISCIA", 0.84),
        root("R4", ["SUN", "MOON"], "SQUARE", "RELCHART", 0.78),
        root("R5", ["SATURN", "MOON"], "CONJUNCTION", "SYN", 0.76),
        root("R6", ["PLUTO", "SUN"], "SQUARE", "NATAL_DRACONIC", 0.74),
    ]


class M21AutomaticIDDTests(unittest.TestCase):
    def context(self, *, complete=True, legacy=None):
        pillar_attribution = derive_pillars_from_roots(
            roots(),
            structural_absence_is_zero=complete,
        )
        raw = {}
        if legacy is not None:
            raw["attributions"] = legacy
        return ModuleContext(
            module_id="M21",
            module_name="discrimination",
            mode="FULL",
            raw_input=raw,
            canonical_snapshot={
                "pillar_attribution": pillar_attribution,
            },
            prior_results={},
        )

    def test_m21_uses_auto_shapley_without_manual_attributions(self):
        result = default_handlers()["M21"](self.context())
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertEqual(
            result.payload["attribution_source"],
            "AUTO_SHAPLEY_CANONICAL_UNITS",
        )
        self.assertIn("model_attributions", result.canonical_updates)
        self.assertIn("pairwise_idd", result.canonical_updates)
        self.assertIn("AF_vs_KA", result.canonical_updates["pairwise_idd"])
        self.assertIn("AG_vs_LG", result.canonical_updates["pairwise_idd"])

    def test_auto_attributions_take_precedence_over_legacy_maps(self):
        legacy = {
            "AF": {"legacy_a": 1.0},
            "KA": {"legacy_b": 1.0},
            "AG": {"legacy_c": 1.0},
            "LG": {"legacy_d": 1.0},
        }
        result = default_handlers()["M21"](
            self.context(legacy=legacy)
        )
        self.assertEqual(
            result.payload["attribution_source"],
            "AUTO_SHAPLEY_CANONICAL_UNITS",
        )
        auto = result.canonical_updates["model_attributions"]["attributions"]
        self.assertNotIn("legacy_a", auto["AF"])
        self.assertFalse(
            any(
                key.startswith("MOTIF:")
                for values in auto.values()
                for key in values
            )
        )

    def test_incomplete_auto_coverage_can_fall_back_to_legacy(self):
        legacy = {
            "AF": {"legacy_a": 1.0},
            "KA": {"legacy_b": 1.0},
            "AG": {"legacy_c": 1.0},
            "LG": {"legacy_d": 1.0},
        }
        result = default_handlers()["M21"](
            self.context(complete=False, legacy=legacy)
        )
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertEqual(
            result.payload["attribution_source"],
            "LEGACY_PRECOMPUTED",
        )
        self.assertEqual(
            result.canonical_updates["model_attributions"]["state"],
            "NOT_EVALUABLE",
        )

    def test_incomplete_auto_coverage_without_legacy_is_not_evaluable(self):
        result = default_handlers()["M21"](
            self.context(complete=False)
        )
        self.assertEqual(result.status, ExecutionStatus.NOT_EVALUABLE)


if __name__ == "__main__":
    unittest.main()
