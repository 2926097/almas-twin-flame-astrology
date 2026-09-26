from __future__ import annotations

import unittest

from almas_tfa.handlers import default_handlers
from almas_tfa.module_contract import ExecutionStatus, ModuleContext


def root_attr(root_id, pillar, value):
    return {
        "root_id": root_id,
        "eligible": True,
        "contributions": {pillar: value},
    }


class M21AutomaticIDDTests(unittest.TestCase):
    def context(self, *, complete=True, legacy=None):
        pillar_attribution = {
            "structural_absence_is_zero": complete,
            "root_attributions": [
                root_attr("R1", "PA", 0.90),
                root_attr("R2", "PR", 0.85),
                root_attr("R3", "PE", 0.80),
                root_attr("R4", "PX", 0.75),
                root_attr("R5", "PK", 0.70),
                root_attr("R6", "PT", 0.72),
                root_attr("R7", "PS", 0.60),
            ],
        }
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
            "AUTO_SHAPLEY_CANONICAL_ROOTS",
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
            "AUTO_SHAPLEY_CANONICAL_ROOTS",
        )
        auto = result.canonical_updates["model_attributions"]["attributions"]
        self.assertNotIn("legacy_a", auto["AF"])

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
