from __future__ import annotations

from math import sqrt
from typing import Any, Mapping

from .core import robustness_component
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result


ALLOWED_NULL_MODELS = {
    "MATCHED_AGE",
    "WITHIN_YEAR",
    "MATCHED_AGE_CLOCK",
    "EPHEMERIS_DATE",
    "PAIR_SHUFFLE",
    "EVENT_DATE_SHIFT",
    "TECHNIQUE_SPECIFIC_CYCLE",
}


def m23_time_sensitivity(context: ModuleContext) -> ModuleResult:
    """M23: evalúa un resumen preregistrado de perturbación horaria.

    M23 no genera por sí mismo horas perturbadas. Consume delta90 y G ya
    derivados por una corrida reproducible y aplica la fórmula normativa R_X.
    """

    summary = context.raw_input.get("time_sensitivity_summary")
    if not isinstance(summary, Mapping):
        return not_evaluable_result(
            "M23",
            "Falta time_sensitivity_summary preregistrado.",
        )

    preregistration_ref = summary.get("preregistration_ref")
    if not isinstance(preregistration_ref, str) or not preregistration_ref:
        raise ValueError("M23 requiere preregistration_ref.")

    delta90 = summary.get("delta90")
    preserved_fraction = summary.get("preserved_fraction")
    if delta90 is None or preserved_fraction is None:
        return not_evaluable_result(
            "M23",
            "Faltan delta90 o preserved_fraction.",
        )

    delta90 = float(delta90)
    preserved_fraction = float(preserved_fraction)
    component = robustness_component(delta90, preserved_fraction)

    perturbation_count = summary.get("perturbation_count")
    if perturbation_count is not None:
        perturbation_count = int(perturbation_count)
        if perturbation_count < 1:
            raise ValueError("perturbation_count debe ser positivo.")

    output = {
        "preregistration_ref": preregistration_ref,
        "subject_scope": summary.get("subject_scope"),
        "perturbation_rule": summary.get("perturbation_rule"),
        "metric": summary.get("metric"),
        "delta90": delta90,
        "preserved_fraction": preserved_fraction,
        "perturbation_count": perturbation_count,
        "robustness_component": component,
        "perturbations_generated_by_m23": False,
    }

    return ModuleResult(
        module_id="M23",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"time_sensitivity": output},
        limitations=(
            "M23 evalúa un resumen de perturbaciones preregistradas; no genera por sí mismo horas alternativas.",
        ),
    )


def wilson_interval(successes: int, trials: int, z: float) -> tuple[float, float]:
    """Intervalo Wilson para una proporción binomial."""

    successes = int(successes)
    trials = int(trials)
    z = float(z)

    if trials <= 0:
        raise ValueError("trials debe ser positivo.")
    if not 0 <= successes <= trials:
        raise ValueError("successes debe estar entre 0 y trials.")
    if z <= 0:
        raise ValueError("z debe ser positivo.")

    p = successes / trials
    z2 = z * z
    denominator = 1.0 + z2 / trials
    center = (p + z2 / (2.0 * trials)) / denominator
    margin = (
        z
        * sqrt(
            (p * (1.0 - p) / trials)
            + (z2 / (4.0 * trials * trials))
        )
        / denominator
    )
    return max(0.0, center - margin), min(1.0, center + margin)


def m24_null_models(context: ModuleContext) -> ModuleResult:
    """M24: resume corridas nulas preregistradas sin generar simulaciones."""

    runs = context.raw_input.get("null_model_runs")
    if not isinstance(runs, list) or not runs:
        return not_evaluable_result(
            "M24",
            "Faltan null_model_runs preregistrados.",
        )

    output_runs: list[dict[str, Any]] = []
    for index, run in enumerate(runs, start=1):
        if not isinstance(run, Mapping):
            raise ValueError("Cada null_model_run debe ser un objeto.")

        run_id = str(run.get("run_id") or f"NULL_{index:03d}")
        model_type = run.get("null_model")
        if model_type not in ALLOWED_NULL_MODELS:
            raise ValueError(
                f"{run_id}: null_model debe ser uno de {sorted(ALLOWED_NULL_MODELS)}."
            )

        preregistration_ref = run.get("preregistration_ref")
        if not isinstance(preregistration_ref, str) or not preregistration_ref:
            raise ValueError(f"{run_id}: preregistration_ref es obligatorio.")

        if run.get("frozen_before_inspection") is not True:
            raise ValueError(
                f"{run_id}: una corrida confirmatoria requiere frozen_before_inspection=true."
            )

        trials = int(run.get("trials", 0))
        hits = int(run.get("hits", -1))
        z = run.get("wilson_z")

        if trials <= 0 or hits < 0 or hits > trials:
            raise ValueError(f"{run_id}: hits/trials inválidos.")

        frequency = hits / trials
        wilson = None
        if z is not None:
            low, high = wilson_interval(hits, trials, float(z))
            wilson = {
                "z": float(z),
                "low": low,
                "high": high,
            }

        output_runs.append(
            {
                "run_id": run_id,
                "null_model": model_type,
                "preregistration_ref": preregistration_ref,
                "feature_set_ref": run.get("feature_set_ref"),
                "orb_policy_ref": run.get("orb_policy_ref"),
                "event_set_ref": run.get("event_set_ref"),
                "trials": trials,
                "hits": hits,
                "frequency": frequency,
                "wilson_interval": wilson,
                "observed_statistic": run.get("observed_statistic"),
                "sampling_generated_by_m24": False,
                "interpretation": "STRUCTURAL_FREQUENCY_UNDER_DECLARED_NULL",
            }
        )

    output = {
        "runs": output_runs,
        "run_count": len(output_runs),
        "metaphysical_probability": False,
        "sampling_generated_by_m24": False,
    }

    return ModuleResult(
        module_id="M24",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"null_models": output},
        limitations=(
            "La frecuencia nula describe rareza estructural bajo el modelo declarado; no es probabilidad metafísica.",
        ),
    )
