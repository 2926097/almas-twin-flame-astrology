from __future__ import annotations

from itertools import combinations
from typing import Any, Mapping

from .core import (
    diagnostic_discrimination,
    idd_band,
    score_model,
    supported_gate,
)

MODELS = ("AF", "KA", "AG", "LG")


def analyze_precomputed(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Analyze precomputed ALMAS pillar values.

    This function does not calculate astronomical positions or evidence roots.
    It consumes already-derived pillar percentages and optional root attributions.
    """
    pillars = payload.get("pillars")
    if not isinstance(pillars, Mapping):
        raise ValueError("payload.pillars must be an object")

    ice_by_model = payload.get("ice_by_model", {})
    if ice_by_model is None:
        ice_by_model = {}
    if not isinstance(ice_by_model, Mapping):
        raise ValueError("payload.ice_by_model must be an object")

    contradictions = payload.get("essential_contradictions", {})
    if contradictions is None:
        contradictions = {}
    if not isinstance(contradictions, Mapping):
        raise ValueError("payload.essential_contradictions must be an object")

    icc = payload.get("icc")
    irc = payload.get("irc")
    r_min = payload.get("r_min")

    results: dict[str, Any] = {
        "public_version": "1.9.3",
        "input_mode": "PRECOMPUTED_PILLARS",
        "models": {},
        "pairwise_idd": {},
        "limitations": [
            "This output does not calculate astronomy, aspects, roots, null models or timing.",
            "Model scores are structural compatibility indices, not metaphysical probabilities.",
        ],
    }

    for model in MODELS:
        score = score_model(
            model,
            pillars,
            ice=float(ice_by_model.get(model, 0.0)),
        )
        model_result: dict[str, Any] = {
            "core": score.core,
            "support": score.support,
            "iem_pre": score.iem_pre,
            "ice": score.ice,
            "iem_final": score.iem_final,
            "essential_evaluable": score.essential_evaluable,
            "supported_gate": None,
        }

        if icc is not None and irc is not None and r_min is not None:
            model_result["supported_gate"] = supported_gate(
                score,
                icc=float(icc),
                irc=float(irc),
                r_min=float(r_min),
                essential_contradiction=bool(
                    contradictions.get(model, False)
                ),
            )

        results["models"][model] = model_result

    attributions = payload.get("attributions", {})
    if attributions is None:
        attributions = {}
    if not isinstance(attributions, Mapping):
        raise ValueError("payload.attributions must be an object")

    for a, b in combinations(MODELS, 2):
        av = attributions.get(a)
        bv = attributions.get(b)
        if isinstance(av, Mapping) and isinstance(bv, Mapping):
            idd = diagnostic_discrimination(av, bv)
            results["pairwise_idd"][f"{a}_vs_{b}"] = {
                "idd": idd,
                "band": idd_band(idd),
            }

    return results
