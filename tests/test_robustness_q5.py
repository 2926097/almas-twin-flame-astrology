from __future__ import annotations

import unittest
from unittest.mock import patch

from almas_tfa.core import pillar_score, score_model
from almas_tfa.module_contract import ExecutionStatus, ModuleContext
from almas_tfa.robustness_index_handlers import make_m25_robustness
from almas_tfa.robustness_quantification import (
    derive_ablation_component,
    derive_parameter_and_idd_components,
    load_q5_robustness_policy,
)


def root_attributions():
    return [
        {"root_id": "R1", "eligible": True, "contributions": {"PA": 0.90}},
        {"root_id": "R2", "eligible": True, "contributions": {"PR": 0.85}},
        {"root_id": "R3", "eligible": True, "contributions": {"PE": 0.80}},
        {"root_id": "R4", "eligible": True, "contributions": {"PX": 0.75}},
        {"root_id": "R5", "eligible": True, "contributions": {"PK": 0.70}},
        {"root_id": "R6", "eligible": True, "contributions": {"PT": 0.72}},
        {"root_id": "R7", "eligible": True, "contributions": {"PS": 0.60}},
    ]


def pillars_from(items):
    strengths = {
        "PA": [], "PK": [], "PE": [], "PR": [],
        "PX": [], "PT": [], "PS": []
    }
    for item in items:
        for pillar, value in item["contributions"].items():
            strengths[pillar].append(value)
    output = {
        pillar: pillar_score(values) if values else 0.0
        for pillar, values in strengths.items()
    }
    output["PU"] = None
    return output


def canonical_for_ablation():
    attrs = root_attributions()
    pillars = pillars_from(attrs)
    indices = {
        model: {
            "iem_pre": score_model(model, pillars, ice=0).iem_pre
        }
        for model in ("AF", "KA", "AG", "LG")
    }
    roots = [
        {
            "root_id": item["root_id"],
            "root_key": item["root_id"] + ":KEY",
            "core_eligible": True,
            "strength_state": "CALCULATED_CORE",
        }
        for item in attrs
    ]
    selected = {
        "AB3_NO_DRACONIC": {"R1", "R2", "R3", "R5", "R6", "R7"},
        "AB4_NO_RELCHART": {"R1", "R2", "R3", "R4", "R5", "R6", "R7"},
        "AB5_NO_HOUSES_ANGLES": {"R1", "R3", "R4", "R5", "R6", "R7"},
        "AB6_NO_NODES": {"R1", "R2", "R3", "R4", "R6", "R7"},
        "AB7_TROPICAL_PLANETARY_CORE": {"R1", "R2", "R3", "R6"},
    }
    runs = [
        {
            "run": run,
            "surviving_root_ids": sorted(ids),
            "lost_root_ids": sorted(
                {item["root_id"] for item in attrs} - ids
            ),
        }
        for run, ids in selected.items()
    ]
    return {
        "independent_roots": {"roots": roots},
        "pillar_attribution": {
            "structural_absence_is_zero": True,
            "root_attributions": attrs,
        },
        "structural_model_indices": indices,
        "ablation": {
            "runs": runs,
            "root_survival": [],
            "structural_only": True,
            "dependency_classes_assigned": False,
        },
    }


def snapshot(iem):
    attrs = root_attributions()
    return {
        "state": "EVALUABLE",
        "iem_pre": dict(iem),
        "core_root_keys": [item["root_id"] + ":KEY" for item in attrs],
        "core_root_count": len(attrs),
        "pillars": pillars_from(attrs),
        "pillar_attribution": {
            "structural_absence_is_zero": True,
            "root_attributions": attrs,
        },
    }


class TestQ5Robustness(unittest.TestCase):
    def test_policy_is_frozen_and_case_fit_forbidden(self):
        policy = load_q5_robustness_policy()
        self.assertEqual(policy["policy_id"], "ALMAS_ROBUSTNESS_Q5_V1")
        self.assertTrue(policy["principles"]["case_fitting_forbidden"])
        self.assertFalse(policy["principles"]["null_rarity_used"])
        self.assertEqual(
            policy["idd_stability"]["source_samples"],
            "PARAMETER_PERTURBATION",
        )

    def test_ablation_component_is_derived_from_selected_runs(self):
        result = derive_ablation_component(
            canonical_for_ablation(),
            policy=load_q5_robustness_policy(),
        )
        self.assertEqual(result["state"], "EVALUABLE")
        component = result["component"]
        self.assertEqual(component["kind"], "ABLATION")
        self.assertTrue(component["auto_derived"])
        self.assertGreaterEqual(component["value"], 0.0)
        self.assertLessEqual(component["value"], 1.0)
        runs = [sample["run"] for sample in result["details"]["samples"]]
        self.assertEqual(
            runs,
            load_q5_robustness_policy()["ablation"]["selected_runs"],
        )
        self.assertNotIn("AB8_INDIVIDUAL_ONLY", runs)

    def test_parameter_and_idd_components_use_frozen_samples(self):
        baseline = {
            "AF": 70.0, "KA": 65.0, "AG": 68.0, "LG": 66.0
        }
        samples = [
            {"AF": 68.0, "KA": 64.0, "AG": 66.0, "LG": 65.0},
            {"AF": 69.0, "KA": 64.5, "AG": 67.0, "LG": 65.5},
            {"AF": 71.0, "KA": 65.5, "AG": 69.0, "LG": 66.5},
            {"AF": 72.0, "KA": 66.0, "AG": 70.0, "LG": 67.0},
        ]
        side_effect = [snapshot(baseline)] + [snapshot(x) for x in samples]

        with patch(
            "almas_tfa.robustness_quantification."
            "structural_recalculation_snapshot",
            side_effect=side_effect,
        ):
            result = derive_parameter_and_idd_components(
                {"aspect_policy": {}},
                astrology_backend=object(),
                davison_backend=object(),
                policy=load_q5_robustness_policy(),
            )

        self.assertEqual(result["parameter_state"], "EVALUABLE")
        self.assertEqual(result["idd_state"], "EVALUABLE")
        self.assertEqual(
            result["parameter_component"]["kind"],
            "PARAMETER_PERTURBATION",
        )
        self.assertEqual(
            result["idd_component"]["kind"],
            "IDD_STABILITY",
        )
        self.assertTrue(result["parameter_component"]["auto_derived"])
        self.assertTrue(result["idd_component"]["auto_derived"])
        self.assertEqual(
            len(result["parameter_details"]["samples"]),
            4,
        )
        self.assertAlmostEqual(
            result["parameter_details"]["preserved_fraction"],
            1.0,
        )
        self.assertAlmostEqual(
            result["idd_details"]["preserved_fraction"],
            1.0,
        )

    def test_auto_q5_components_replace_legacy_same_kinds(self):
        bundle = {
            "policy_id": "ALMAS_ROBUSTNESS_Q5_V1",
            "components": [
                {
                    "id": "ABLATION_AUTO",
                    "kind": "ABLATION",
                    "value": 0.8,
                    "source_module": "M22",
                    "preregistration_ref": "ALMAS_ROBUSTNESS_Q5_V1",
                    "derivation_ref": "Q5:A",
                    "note": None,
                    "auto_derived": True,
                },
                {
                    "id": "PARAMETER_PERTURBATION_AUTO",
                    "kind": "PARAMETER_PERTURBATION",
                    "value": 0.9,
                    "source_module": "M25",
                    "preregistration_ref": "ALMAS_ROBUSTNESS_Q5_V1",
                    "derivation_ref": "Q5:P",
                    "note": None,
                    "auto_derived": True,
                },
                {
                    "id": "IDD_STABILITY_AUTO",
                    "kind": "IDD_STABILITY",
                    "value": 0.7,
                    "source_module": "M21",
                    "preregistration_ref": "ALMAS_ROBUSTNESS_Q5_V1",
                    "derivation_ref": "Q5:I",
                    "note": None,
                    "auto_derived": True,
                },
            ],
        }
        canonical = {
            "time_sensitivity": {
                "preregistration_ref": "ALMAS_BIRTH_TIME_PERTURBATION_V1",
                "robustness_component": 0.95,
            },
            "ablation": {"runs": []},
        }
        raw = {
            "robustness_component_summaries": [
                {
                    "id": "LEGACY_ABLATION",
                    "kind": "ABLATION",
                    "value": 0.1,
                    "source_module": "M22",
                    "preregistration_ref": "LEGACY",
                    "derivation_ref": "LEGACY",
                },
                {
                    "id": "LEGACY_PARAMETER",
                    "kind": "PARAMETER_PERTURBATION",
                    "value": 0.1,
                    "source_module": "EXTERNAL",
                    "preregistration_ref": "LEGACY",
                    "derivation_ref": "LEGACY",
                },
                {
                    "id": "LEGACY_IDD",
                    "kind": "IDD_STABILITY",
                    "value": 0.1,
                    "source_module": "EXTERNAL",
                    "preregistration_ref": "LEGACY",
                    "derivation_ref": "LEGACY",
                },
            ]
        }

        handler = make_m25_robustness(object(), object())
        with patch(
            "almas_tfa.robustness_index_handlers."
            "derive_q5_robustness_components",
            return_value=bundle,
        ):
            result = handler(
                ModuleContext(
                    module_id="M25",
                    module_name="robustness",
                    mode="FULL",
                    raw_input=raw,
                    canonical_snapshot=canonical,
                    prior_results={},
                )
            )

        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        output = result.canonical_updates["robustness_index"]
        ids = {component["id"] for component in output["components"]}
        self.assertIn("BIRTH_TIME", ids)
        self.assertIn("ABLATION_AUTO", ids)
        self.assertIn("PARAMETER_PERTURBATION_AUTO", ids)
        self.assertIn("IDD_STABILITY_AUTO", ids)
        self.assertNotIn("LEGACY_ABLATION", ids)
        self.assertNotIn("LEGACY_PARAMETER", ids)
        self.assertNotIn("LEGACY_IDD", ids)
        self.assertEqual(output["ablation_state"], "INCLUDED_AUTO_Q5")


if __name__ == "__main__":
    unittest.main()
