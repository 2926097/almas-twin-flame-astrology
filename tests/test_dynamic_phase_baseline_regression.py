"""Baseline cuantitativo previo al motor de fases dinámicas.

Los resultados esperados se conservan en un archivo revisable e independiente
de las funciones que se prueban. Los casos son sintéticos y no personales.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from almas_tfa.core import (
    MODEL_PILLARS,
    SUPPORTED_THRESHOLDS,
    diagnostic_discrimination,
    grouped_robustness_index,
    idd_band,
    score_model,
    supported_gate,
)
from almas_tfa.canonical_assembly import derive_canonical_coverage
from almas_tfa.counterevidence_handlers import m20_counterevidence
from almas_tfa.model_attribution import derive_model_attributions
from almas_tfa.module_contract import ExecutionStatus, ModuleContext, ModuleResult
from almas_tfa.pillar_attribution import derive_pillars_from_roots
from almas_tfa.temporal_handlers import m26_temporal_activation


BASELINE = Path(__file__).parent / "fixtures" / "dynamic_phase_quantitative_baseline_1.22.0.json"


def _root(root_id, points, relation, family, strength):
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
        "evidence_strengths": [{
            "evidence_id": root_id + ":" + family,
            "strength": strength,
            "core_eligible": True,
            "support_only": False,
            "dependency_family": family,
            "technique_family": family,
        }],
    }


def current_snapshot():
    """Recorre el código productivo; no deriva expectativas desde sus fórmulas."""
    roots = [
        _root("R1", ["SUN", "MOON"], "TRINE", "SYN", .90),
        _root("R2", ["SUN", "MOON"], "PARALLEL", "DECLINATION", .82),
        _root("R3", ["MERCURY", "MOON"], "TRINE", "ANTISCIA", .84),
        _root("R4", ["SUN", "MOON"], "SQUARE", "RELCHART", .78),
        _root("R5", ["SATURN", "MOON"], "CONJUNCTION", "SYN", .76),
        _root("R6", ["PLUTO", "SUN"], "SQUARE", "NATAL_DRACONIC", .74),
    ]
    attribution = derive_pillars_from_roots(
        roots, structural_absence_is_zero=True
    )
    shapley = derive_model_attributions(attribution)
    pillars = attribution["pillars"]
    ice = {"AF": 0, "KA": 5, "AG": 10, "LG": 20}
    scores = {model: score_model(model, pillars, ice=ice[model])
              for model in ("AF", "KA", "AG", "LG")}
    partial = score_model("AF", {"PA": 90, "PR": None})
    irc, r_min, groups = grouped_robustness_index([
        ("TIME_INPUT", .8),
        ("STRUCTURAL_PERTURBATION", .9),
        ("STRUCTURAL_PERTURBATION", .72),
    ])
    counterevidence = m20_counterevidence(ModuleContext(
        module_id="M20", module_name="counterevidence", mode="FULL",
        raw_input={
            "counterevidence_complete": True,
            "counterevidence_items": [
                {"id": "C1", "kind": "EXPLICIT_CONTRADICTION",
                 "models": ["LG"], "contradiction_key": "K1",
                 "dependency_family": "FACTS", "severity": .4},
                {"id": "C2", "kind": "EXPLICIT_CONTRADICTION",
                 "models": ["LG"], "contradiction_key": "K1",
                 "dependency_family": "OTHER", "severity": .8},
                {"id": "C3", "kind": "EXPLICIT_CONTRADICTION",
                 "models": ["LG"], "contradiction_key": "K2",
                 "dependency_family": "FACTS", "severity": .5},
            ],
        },
        canonical_snapshot={}, prior_results={},
    )).canonical_updates["counterevidence"]
    idd = diagnostic_discrimination(
        shapley["attributions"]["AG"],
        shapley["attributions"]["LG"],
    )
    temporal = m26_temporal_activation(ModuleContext(
        module_id="M26", module_name="temporal", mode="FULL",
        raw_input={
            "temporal_signals": [
                {"signal_id": "T1", "root_id": "R1",
                 "temporal_family": "TTRANSIT", "activation_class": "DIRECT_REPETITION",
                 "strength": .8, "window_status": "CURRENT_ACTIVE",
                 "preregistered": True, "structural_family": "SYN",
                 "exactitude_orb": .5,
                 "preregistered_window_rule": "SYNTHETIC-WINDOW-V1"},
                {"signal_id": "T2", "root_id": "R2",
                 "temporal_family": "TPROG",
                 "activation_class": "RELATIONAL_ROOT_ACTIVATION",
                 "strength": 1., "window_status": "CURRENT_ACTIVE",
                 "preregistered": True, "structural_family": "DECLINATION",
                 "exactitude_orb": .5,
                 "preregistered_window_rule": "SYNTHETIC-WINDOW-V1"},
            ],
            "iat_aggregation_policy": {
                "preregistration_ref": "SYNTHETIC-IAT-V1",
                "window_scope_ref": "SYNTHETIC-WINDOW-V1",
                "formula": "WEIGHTED_MEAN_EFFECTIVE_STRENGTH",
                "family_weights": {"TTRANSIT": 1., "TPROG": 2.},
                "root_weights": {"R1": 1., "R2": .5},
            },
        },
        canonical_snapshot={"independent_roots": {"roots": roots}},
        prior_results={},
    )).canonical_updates["temporal_activation"]
    coverage = derive_canonical_coverage({}, {
        module: ModuleResult(module_id=module, status=ExecutionStatus.COMPLETED)
        for module in ("M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11", "M13", "M14")
    })
    return {
        "policy": {
            "model_pillars": MODEL_PILLARS,
            "supported_thresholds": SUPPORTED_THRESHOLDS,
            "pillar_policy_id": attribution["policy_id"],
            "shapley_policy_id": shapley["policy_id"],
        },
        "synthetic_roots": {
            "pillars": pillars,
            "pillar_root_ids": attribution["pillar_root_ids"],
            "motif_count": len(attribution["motif_attributions"]),
            "recurrence_source": attribution["recurrence_source"],
            "shapley_players": shapley["unit_ids"],
            "shapley_motif_players": shapley["motif_player_count"],
            "shapley_method": shapley["method"]["method"],
            "shapley_iem_pre": shapley["model_iem_pre_from_roots"],
            "shapley_attributions": shapley["attributions"],
            "idd_ag_lg": idd,
            "idd_band_ag_lg": idd_band(idd),
        },
        "model_scores": {
            model: {
                "core": score.core,
                "support": score.support,
                "iem_pre": score.iem_pre,
                "ice": score.ice,
                "iem_final": score.iem_final,
                "essential_evaluable": score.essential_evaluable,
                "supported_gate": supported_gate(
                    score, icc=90, irc=irc, r_min=r_min
                ),
            }
            for model, score in scores.items()
        },
        "missing_essential": {
            "essential_evaluable": partial.essential_evaluable,
            "iem_final": partial.iem_final,
            "supported_gate": supported_gate(
                partial, icc=90, irc=irc, r_min=r_min
            ),
        },
        "robustness": {"irc": irc, "r_min": r_min, "groups": groups},
        "temporal": {"iat": temporal["iat"], "state": temporal["iat_state"],
                     "selected_count": len(temporal["selected_independent_signals"]),
                     "structural_roots_created": temporal["structural_roots_created"]},
        "coverage": coverage,
        "counterevidence": {
            "state": counterevidence["ice_state"],
            "ice_by_model": counterevidence["ice_by_model"],
            "lg_contradictions": counterevidence["ice_derivation"]["by_model"]["LG"]["semantic_contradiction_count"],
        },
    }


class DynamicPhaseBaselineRegression(unittest.TestCase):
    def test_quantitative_baseline_is_unchanged(self):
        expected = json.loads(BASELINE.read_text(encoding="utf-8"))
        actual = json.loads(json.dumps(current_snapshot()))
        self._compare(expected["expected_output"], actual)

    def _compare(self, expected, actual, path="baseline"):
        if isinstance(expected, dict):
            self.assertIsInstance(actual, dict, path)
            self.assertEqual(set(expected), set(actual), path)
            for key in expected:
                self._compare(expected[key], actual[key], f"{path}.{key}")
        elif isinstance(expected, list):
            self.assertIsInstance(actual, list, path)
            self.assertEqual(len(expected), len(actual), path)
            for index, (left, right) in enumerate(zip(expected, actual)):
                self._compare(left, right, f"{path}[{index}]")
        elif isinstance(expected, float):
            self.assertIsInstance(actual, (int, float), path)
            self.assertAlmostEqual(expected, actual, places=10, msg=path)
        else:
            self.assertEqual(expected, actual, path)

    def test_provenance_is_explicit(self):
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        self.assertEqual(baseline["baseline_commit"],
                         "3899add29d20e09574e9eb7c2336d2d923063d7b")
        self.assertEqual(baseline["case_type"], "SYNTHETIC")


if __name__ == "__main__":
    unittest.main()
