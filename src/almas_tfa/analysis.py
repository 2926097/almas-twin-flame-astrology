from __future__ import annotations

from itertools import combinations
from typing import Any, Mapping

from .core import (
    diagnostic_discrimination,
    idd_band,
    score_model,
    supported_gate,
)
from .quantitative_contracts import MODELS, validate_ice_by_model


def analyze_precomputed(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Analiza valores de pilares ALMAS previamente calculados.

    Esta función no calcula posiciones astronómicas ni raíces de evidencia.
    Consume porcentajes de pilares ya derivados y atribuciones opcionales de raíces.
    """
    pillars = payload.get("pillars")
    if not isinstance(pillars, Mapping):
        raise ValueError("payload.pillars debe ser un objeto")

    ice_by_model = validate_ice_by_model(
        payload.get("ice_by_model"),
        field_name="payload.ice_by_model",
    )
    ice_evaluable = ice_by_model is not None

    contradictions = payload.get("essential_contradictions", {})
    if contradictions is None:
        contradictions = {}
    if not isinstance(contradictions, Mapping):
        raise ValueError("payload.essential_contradictions debe ser un objeto")

    icc = payload.get("icc")
    irc = payload.get("irc")
    r_min = payload.get("r_min")

    results: dict[str, Any] = {
        "public_version": "1.22.0",
        "input_mode": "PRECOMPUTED_PILLARS",
        "models": {},
        "pairwise_idd": {},
        "limitations": [
            "Esta salida no calcula astronomía, aspectos, raíces, modelos nulos ni temporalidad.",
            "Las puntuaciones de modelos son índices de compatibilidad estructural, no probabilidades metafísicas.",
        ],
    }

    if not ice_evaluable:
        results["limitations"].append(
            "ICE no fue declarado: IEM_final y el gate SUPPORTED permanecen no evaluables."
        )

    for model in MODELS:
        ice_value = ice_by_model[model] if ice_evaluable else 0.0
        score = score_model(
            model,
            pillars,
            ice=ice_value,
        )
        model_result: dict[str, Any] = {
            "core": score.core,
            "support": score.support,
            "iem_pre": score.iem_pre,
            "ice": score.ice if ice_evaluable else None,
            "iem_final": score.iem_final if ice_evaluable else None,
            "ice_state": "EVALUABLE" if ice_evaluable else "NOT_EVALUABLE",
            "essential_evaluable": score.essential_evaluable,
            "supported_gate": None,
        }

        if (
            ice_evaluable
            and icc is not None
            and irc is not None
            and r_min is not None
        ):
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
        raise ValueError("payload.attributions debe ser un objeto")

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
