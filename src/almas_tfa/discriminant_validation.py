from __future__ import annotations

import json
import math
from functools import lru_cache
from importlib.resources import files
from typing import Any, Mapping, Sequence


POLICY_RESOURCE = "data/discriminant-validation-policy.json"
POLICY_ID = "ALMAS_DISCRIMINANT_VALIDATION_V1"


@lru_cache(maxsize=1)
def load_discriminant_validation_policy() -> dict[str, Any]:
    resource = files("almas_tfa").joinpath(POLICY_RESOURCE)
    return json.loads(resource.read_text(encoding="utf-8"))


def _canonical_pair(pair: Sequence[str]) -> tuple[str, str]:
    if len(pair) != 2:
        raise ValueError("El par de modelos debe contener exactamente dos elementos.")
    a, b = str(pair[0]), str(pair[1])
    if not a or not b or a == b:
        raise ValueError("Par de modelos inválido.")
    return tuple(sorted((a, b)))


def _require_nonnegative_int(value: Any, *, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name}: se requiere entero no negativo.")
    return value


def wilson_interval(successes: int, total: int, *, z: float = 1.959963984540054) -> tuple[float, float]:
    successes = _require_nonnegative_int(successes, name="successes")
    total = _require_nonnegative_int(total, name="total")
    if total <= 0:
        raise ValueError("Wilson requiere total > 0.")
    if successes > total:
        raise ValueError("successes no puede superar total.")

    p = successes / total
    z2 = z * z
    denom = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denom
    margin = (
        z
        * math.sqrt((p * (1.0 - p) / total) + (z2 / (4.0 * total * total)))
        / denom
    )
    return max(0.0, center - margin), min(1.0, center + margin)


def _nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item) for item in value)
    )


def evaluate_discriminant_validation(
    validation: Mapping[str, Any],
    *,
    validated_pairs: Sequence[Sequence[str]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or load_discriminant_validation_policy()

    if validation.get("policy_id") != policy.get("policy_id"):
        raise ValueError("discriminant_validation: policy_id no coincide con la política canónica.")
    if validation.get("development_evaluation_disjoint") is not True:
        raise ValueError("discriminant_validation: desarrollo y evaluación deben ser disjuntos.")
    if not _nonempty_string_list(validation.get("evaluation_refs")):
        raise ValueError("discriminant_validation: evaluation_refs no vacío es obligatorio.")

    target_pairs = {_canonical_pair(pair) for pair in validated_pairs}
    if not target_pairs:
        raise ValueError("discriminant_validation: validated_pairs no puede estar vacío.")

    pairwise_results = validation.get("pairwise_results")
    if not isinstance(pairwise_results, list) or not pairwise_results:
        raise ValueError("discriminant_validation: pairwise_results no puede estar vacío.")

    minimums = policy.get("minimums", {})
    min_sens = float(minimums.get("pairwise_sensitivity_ci_lower"))
    min_spec = float(minimums.get("pairwise_specificity_ci_lower"))
    min_ba = float(minimums.get("pairwise_balanced_accuracy"))

    seen_pairs: set[tuple[str, str]] = set()
    pairwise_summary: list[dict[str, Any]] = []

    for item in pairwise_results:
        if not isinstance(item, Mapping):
            raise ValueError("discriminant_validation: resultado pairwise inválido.")

        pair = item.get("pair")
        if not isinstance(pair, (list, tuple)):
            raise ValueError("discriminant_validation: pair ausente.")
        canonical = _canonical_pair(pair)
        if canonical not in target_pairs:
            raise ValueError(f"discriminant_validation: par fuera del alcance validado {canonical}.")
        if canonical in seen_pairs:
            raise ValueError(f"discriminant_validation: par duplicado {canonical}.")
        seen_pairs.add(canonical)

        positive_model = item.get("positive_model")
        if positive_model not in canonical:
            raise ValueError("discriminant_validation: positive_model debe pertenecer al par.")

        tp = _require_nonnegative_int(item.get("tp"), name="tp")
        tn = _require_nonnegative_int(item.get("tn"), name="tn")
        fp = _require_nonnegative_int(item.get("fp"), name="fp")
        fn = _require_nonnegative_int(item.get("fn"), name="fn")

        positive_total = tp + fn
        negative_total = tn + fp
        if positive_total <= 0 or negative_total <= 0:
            raise ValueError("discriminant_validation: ambas clases deben estar representadas.")

        sensitivity = tp / positive_total
        specificity = tn / negative_total
        sensitivity_ci_lower, _ = wilson_interval(tp, positive_total)
        specificity_ci_lower, _ = wilson_interval(tn, negative_total)
        balanced_accuracy = (sensitivity + specificity) / 2.0

        if sensitivity_ci_lower < min_sens:
            raise ValueError(
                f"discriminant_validation: sensibilidad insuficiente para {canonical}: "
                f"CI95 inferior {sensitivity_ci_lower:.4f} < {min_sens:.4f}."
            )
        if specificity_ci_lower < min_spec:
            raise ValueError(
                f"discriminant_validation: especificidad insuficiente para {canonical}: "
                f"CI95 inferior {specificity_ci_lower:.4f} < {min_spec:.4f}."
            )
        if balanced_accuracy < min_ba:
            raise ValueError(
                f"discriminant_validation: balanced_accuracy insuficiente para {canonical}: "
                f"{balanced_accuracy:.4f} < {min_ba:.4f}."
            )

        pairwise_summary.append(
            {
                "pair": list(canonical),
                "positive_model": positive_model,
                "sensitivity": sensitivity,
                "specificity": specificity,
                "sensitivity_ci_lower": sensitivity_ci_lower,
                "specificity_ci_lower": specificity_ci_lower,
                "balanced_accuracy": balanced_accuracy,
            }
        )

    if seen_pairs != target_pairs:
        missing = sorted(target_pairs - seen_pairs)
        raise ValueError(f"discriminant_validation: faltan métricas para pares validados: {missing}.")

    fs = validation.get("false_specificity")
    if not isinstance(fs, Mapping):
        raise ValueError("discriminant_validation: false_specificity ausente.")
    fs_total = _require_nonnegative_int(fs.get("evaluable_count"), name="false_specificity.evaluable_count")
    fs_errors = _require_nonnegative_int(fs.get("error_count"), name="false_specificity.error_count")
    if fs_total <= 0 or fs_errors > fs_total:
        raise ValueError("discriminant_validation: false_specificity counts inválidos.")
    fs_rate = fs_errors / fs_total
    _, fs_ci_upper = wilson_interval(fs_errors, fs_total)
    max_fs_upper = float(policy.get("false_specificity", {}).get("max_ci_upper"))
    if fs_ci_upper > max_fs_upper:
        raise ValueError(
            "discriminant_validation: FALSE_SPECIFICITY_RATE no supera el gate de incertidumbre: "
            f"CI95 superior {fs_ci_upper:.4f} > {max_fs_upper:.4f}."
        )

    synthetic = validation.get("synthetic_adversarial")
    if not isinstance(synthetic, Mapping):
        raise ValueError("discriminant_validation: synthetic_adversarial ausente.")
    syn_total = _require_nonnegative_int(
        synthetic.get("evaluable_count"), name="synthetic_adversarial.evaluable_count"
    )
    syn_errors = _require_nonnegative_int(
        synthetic.get("false_specificity_count"),
        name="synthetic_adversarial.false_specificity_count",
    )
    if syn_total <= 0 or syn_errors > syn_total:
        raise ValueError("discriminant_validation: synthetic_adversarial counts inválidos.")
    syn_rate = syn_errors / syn_total
    max_syn_rate = float(
        policy.get("false_specificity", {}).get("synthetic_adversarial_max_rate")
    )
    if syn_rate > max_syn_rate:
        raise ValueError(
            "discriminant_validation: existe falsa especificidad en controles sintéticos/adversariales."
        )

    calibration = validation.get("calibration")
    if not isinstance(calibration, Mapping):
        raise ValueError("discriminant_validation: calibration ausente.")
    mode = calibration.get("mode")
    categorical_mode = policy.get("calibration", {}).get("categorical_mode")
    if mode == categorical_mode:
        if calibration.get("passed") is not None:
            raise ValueError("calibration: passed debe ser null en salida categórica.")
        if calibration.get("criterion_ref") is not None:
            raise ValueError("calibration: criterion_ref debe ser null en salida categórica.")
        if calibration.get("refs") not in ([], tuple()):
            raise ValueError("calibration: refs debe estar vacío en salida categórica.")
    elif mode == "PROBABILISTIC":
        if policy.get("calibration", {}).get("probabilistic_outputs_require_pass") is not True:
            raise ValueError("Política de calibración probabilística inválida.")
        if calibration.get("passed") is not True:
            raise ValueError("calibration: salida probabilística sin calibración aprobada.")
        if not isinstance(calibration.get("criterion_ref"), str) or not calibration["criterion_ref"]:
            raise ValueError("calibration: criterion_ref obligatorio.")
        if not _nonempty_string_list(calibration.get("refs")):
            raise ValueError("calibration: refs no vacío obligatorio.")
    else:
        raise ValueError("calibration: mode no reconocido.")

    return {
        "policy_id": policy.get("policy_id"),
        "pairwise": pairwise_summary,
        "false_specificity_rate": fs_rate,
        "false_specificity_ci_upper": fs_ci_upper,
        "synthetic_adversarial_false_specificity_rate": syn_rate,
        "calibration_mode": mode,
    }


def has_complete_discriminant_validation(
    validation: Any,
    *,
    validated_pairs: Sequence[Sequence[str]],
    policy: Mapping[str, Any] | None = None,
) -> bool:
    if not isinstance(validation, Mapping):
        return False
    try:
        evaluate_discriminant_validation(
            validation,
            validated_pairs=validated_pairs,
            policy=policy,
        )
    except (TypeError, ValueError):
        return False
    return True
