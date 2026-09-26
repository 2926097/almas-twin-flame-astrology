from __future__ import annotations

from math import sqrt
from statistics import NormalDist
from typing import Any, Mapping, Sequence

from .module_contract import (
    ExecutionStatus,
    ModuleContext,
    ModuleResult,
    not_evaluable_result,
)
from .null_generation import (
    generate_within_year_null_runs,
    load_null_generation_policy,
)


ALLOWED_NULL_MODELS = {
    "MATCHED_AGE",
    "WITHIN_YEAR",
    "MATCHED_AGE_CLOCK",
    "EPHEMERIS_DATE",
    "PAIR_SHUFFLE",
    "EVENT_DATE_SHIFT",
    "TECHNIQUE_SPECIFIC_CYCLE",
}

ALLOWED_TAILS = {
    "GREATER_OR_EQUAL",
    "LESS_OR_EQUAL",
    "ABS_GREATER_OR_EQUAL",
}


def wilson_interval(
    successes: int,
    trials: int,
    confidence_level: float = 0.95,
) -> tuple[float, float]:
    """Intervalo de Wilson para una frecuencia binomial."""

    if isinstance(successes, bool) or isinstance(trials, bool):
        raise ValueError("successes y trials deben ser enteros.")

    successes = int(successes)
    trials = int(trials)

    if trials <= 0:
        raise ValueError("trials debe ser positivo.")
    if successes < 0 or successes > trials:
        raise ValueError("successes debe estar entre 0 y trials.")

    confidence_level = float(confidence_level)
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level debe estar en (0,1).")

    alpha = 1.0 - confidence_level
    z = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    phat = successes / trials
    z2 = z * z

    denominator = 1.0 + z2 / trials
    center = (phat + z2 / (2.0 * trials)) / denominator
    half = (
        z
        * sqrt(
            phat * (1.0 - phat) / trials
            + z2 / (4.0 * trials * trials)
        )
        / denominator
    )
    return max(0.0, center - half), min(1.0, center + half)


def _is_extreme(value: float, observed: float, tail: str) -> bool:
    if tail == "GREATER_OR_EQUAL":
        return value >= observed
    if tail == "LESS_OR_EQUAL":
        return value <= observed
    if tail == "ABS_GREATER_OR_EQUAL":
        return abs(value) >= abs(observed)
    raise ValueError(f"tail desconocido: {tail}")


def _numeric_samples(values: Any) -> list[float]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ValueError("null_samples debe ser una lista numérica.")

    samples: list[float] = []
    for index, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"null_samples[{index}] no es numérico.")
        samples.append(float(value))

    if not samples:
        raise ValueError("null_samples no puede estar vacío.")

    return samples


def _evaluate_run(spec: Mapping[str, Any], index: int) -> dict[str, Any]:
    run_id = spec.get("id")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError(f"Corrida nula {index}: id es obligatorio.")

    preregistration_ref = spec.get("preregistration_ref")
    if not isinstance(preregistration_ref, str) or not preregistration_ref:
        raise ValueError(f"{run_id}: preregistration_ref es obligatorio.")

    null_model = spec.get("null_model")
    if null_model not in ALLOWED_NULL_MODELS:
        raise ValueError(
            f"{run_id}: null_model debe ser uno de los modelos admitidos por ALMAS."
        )

    frozen_refs = {}
    for field_name in ("feature_set_ref", "orb_policy_ref", "event_set_ref"):
        value = spec.get(field_name)
        if not isinstance(value, str) or not value:
            raise ValueError(
                f"{run_id}: {field_name} es obligatorio para demostrar "
                "congelación preregistrada."
            )
        frozen_refs[field_name] = value

    generator_ref = spec.get("generator_ref")
    if not isinstance(generator_ref, str) or not generator_ref:
        raise ValueError(f"{run_id}: generator_ref es obligatorio.")

    statistic_id = spec.get("statistic_id")
    if not isinstance(statistic_id, str) or not statistic_id:
        raise ValueError(f"{run_id}: statistic_id es obligatorio.")

    observed = spec.get("observed_value")
    if isinstance(observed, bool) or not isinstance(observed, (int, float)):
        raise ValueError(f"{run_id}: observed_value debe ser numérico.")
    observed = float(observed)

    tail = spec.get("tail")
    if tail not in ALLOWED_TAILS:
        raise ValueError(
            f"{run_id}: tail debe ser GREATER_OR_EQUAL, LESS_OR_EQUAL "
            "o ABS_GREATER_OR_EQUAL."
        )

    confidence_level = float(spec.get("confidence_level", 0.95))

    samples_raw = spec.get("null_samples")
    n_raw = spec.get("n")
    extreme_count_raw = spec.get("extreme_count")

    if samples_raw is not None:
        samples = _numeric_samples(samples_raw)
        n = len(samples)
        extreme_count = sum(
            1 for value in samples if _is_extreme(value, observed, tail)
        )

        if n_raw is not None and int(n_raw) != n:
            raise ValueError(
                f"{run_id}: n no coincide con la longitud de null_samples."
            )
        if (
            extreme_count_raw is not None
            and int(extreme_count_raw) != extreme_count
        ):
            raise ValueError(
                f"{run_id}: extreme_count no coincide con null_samples "
                "y la regla tail."
            )
        evaluation_source = "NULL_SAMPLES"
    else:
        if n_raw is None or extreme_count_raw is None:
            raise ValueError(
                f"{run_id}: sin null_samples deben declararse n y extreme_count."
            )
        if isinstance(n_raw, bool) or int(n_raw) != n_raw or int(n_raw) <= 0:
            raise ValueError(f"{run_id}: n debe ser entero positivo.")
        if (
            isinstance(extreme_count_raw, bool)
            or int(extreme_count_raw) != extreme_count_raw
        ):
            raise ValueError(f"{run_id}: extreme_count debe ser entero.")

        n = int(n_raw)
        extreme_count = int(extreme_count_raw)
        if extreme_count < 0 or extreme_count > n:
            raise ValueError(
                f"{run_id}: extreme_count debe estar entre 0 y n."
            )
        evaluation_source = "PRECOMPUTED_COUNTS"

    frequency = extreme_count / n
    lower, upper = wilson_interval(
        extreme_count,
        n,
        confidence_level=confidence_level,
    )

    return {
        "id": run_id,
        "preregistration_ref": preregistration_ref,
        "null_model": null_model,
        **frozen_refs,
        "generator_ref": generator_ref,
        "statistic_id": statistic_id,
        "observed_value": observed,
        "tail": tail,
        "n": n,
        "extreme_count": extreme_count,
        "structural_frequency": frequency,
        "wilson_interval": {
            "confidence_level": confidence_level,
            "lower": lower,
            "upper": upper,
        },
        "evaluation_source": evaluation_source,
        "sampling_generated_by_m24": False,
        "interpretation_scope": "STRUCTURAL_FREQUENCY_UNDER_DECLARED_NULL",
    }


def m24_null_models(context: ModuleContext) -> ModuleResult:
    """M24: evalúa uno o más modelos nulos preregistrados.

    M24 no genera universos nulos. Consume muestras o conteos producidos por
    generadores declarados y reporta frecuencias estructurales con intervalos
    de Wilson. Ningún resultado se interpreta como probabilidad metafísica.
    """

    raw_runs = context.raw_input.get("null_model_runs")
    if not isinstance(raw_runs, list) or not raw_runs:
        return not_evaluable_result(
            "M24",
            "Falta null_model_runs con al menos una corrida preregistrada.",
        )

    runs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for index, raw in enumerate(raw_runs, start=1):
        if not isinstance(raw, Mapping):
            raise ValueError(
                f"null_model_runs[{index - 1}] debe ser un objeto."
            )
        evaluated = _evaluate_run(raw, index)
        if evaluated["id"] in seen_ids:
            raise ValueError(
                f"ID de corrida nula duplicado: {evaluated['id']}."
            )
        seen_ids.add(evaluated["id"])
        runs.append(evaluated)

    runs.sort(key=lambda item: item["id"])

    output = {
        "runs": runs,
        "run_count": len(runs),
        "metaphysical_probability": False,
        "sampling_generated_by_m24": False,
    }

    return ModuleResult(
        module_id="M24",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"null_models": output},
        limitations=(
            "La frecuencia bajo un modelo nulo es rareza estructural, no probabilidad metafísica.",
            "La ruta legacy consume muestras o conteos preregistrados externos.",
        ),
    )


def make_m24_null_models(astrology_backend, davison_backend):
    """Construye M24 con generación nula Q6 y fallback legacy.

    Los null_model_runs explícitos conservan prioridad por compatibilidad y
    para permitir cohortes externas. Si no existen, Q6 genera WITHIN_YEAR de
    forma determinista con la política congelada del proyecto.
    """

    def m24_auto(context: ModuleContext) -> ModuleResult:
        explicit = context.raw_input.get("null_model_runs")
        if isinstance(explicit, list) and explicit:
            return m24_null_models(context)

        generated = generate_within_year_null_runs(
            context.raw_input,
            astrology_backend=astrology_backend,
            davison_backend=davison_backend,
            policy=load_null_generation_policy(),
        )
        if generated.get("state") != "EVALUABLE":
            return not_evaluable_result(
                "M24",
                "Q6 automático no evaluable: " + str(generated.get("reason")),
            )

        derived_raw = dict(context.raw_input)
        derived_raw["null_model_runs"] = generated["run_specs"]
        derived_context = ModuleContext(
            module_id=context.module_id,
            module_name=context.module_name,
            mode=context.mode,
            raw_input=derived_raw,
            canonical_snapshot=context.canonical_snapshot,
            prior_results=context.prior_results,
        )
        evaluated = m24_null_models(derived_context)
        if evaluated.status is not ExecutionStatus.COMPLETED:
            return evaluated

        legacy_output = evaluated.canonical_updates["null_models"]
        runs = []
        for run in legacy_output["runs"]:
            item = dict(run)
            item["sampling_generated_by_m24"] = True
            item["generator_policy_id"] = generated["policy_id"]
            runs.append(item)

        output = {
            "runs": runs,
            "run_count": len(runs),
            "metaphysical_probability": False,
            "sampling_generated_by_m24": True,
            "generator_policy_id": generated["policy_id"],
            "generator_policy_status": generated["policy_status"],
            "epistemic_class": generated["epistemic_class"],
            "generated_sample_count": generated["sample_count"],
            "samples_per_subject": generated["samples_per_subject"],
            "sample_manifest": generated["sample_manifest"],
            "external_population_claim": False,
            "combined_p_value": None,
            "combined_p_value_state": "FORBIDDEN",
        }

        return ModuleResult(
            module_id="M24",
            status=ExecutionStatus.COMPLETED,
            payload=output,
            canonical_updates={"null_models": output},
            limitations=(
                "WITHIN_YEAR es un universo nulo autocontenido; no representa una población externa.",
                "PAIR_SHUFFLE, MATCHED_AGE y MATCHED_AGE_CLOCK requieren un pool externo y no se fabrican desde una sola pareja.",
                "Las frecuencias se reportan por estadístico y no se combinan en un p-value único.",
                "La rareza estructural nunca se interpreta como probabilidad metafísica ni entra en IRC.",
            ),
            diagnostics=(
                "M24 source=AUTO_WITHIN_YEAR_Q6",
            ),
        )

    return m24_auto
