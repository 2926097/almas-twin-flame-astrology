from __future__ import annotations

from typing import Any, Mapping

from .core import robustness_component
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result


def m23_time_sensitivity(context: ModuleContext) -> ModuleResult:
    """M23: calcula el componente de robustez horaria preregistrado.

    M23 no genera perturbaciones ni estima delta90. Consume un resumen
    preregistrado y aplica exclusivamente la fórmula normativa de ALMAS:

        R_X = exp(-delta90 / 20) * sqrt(G)
    """

    summary = context.raw_input.get("time_sensitivity_summary")
    if not isinstance(summary, Mapping):
        return not_evaluable_result(
            "M23",
            "Falta time_sensitivity_summary preregistrado.",
        )

    preregistration_ref = summary.get("preregistration_ref")
    if not isinstance(preregistration_ref, str) or not preregistration_ref:
        raise ValueError("preregistration_ref es obligatorio.")

    if summary.get("delta90") is None:
        raise ValueError("delta90 es obligatorio.")
    if summary.get("preserved_fraction") is None:
        raise ValueError("preserved_fraction es obligatorio.")

    delta90 = float(summary["delta90"])
    preserved_fraction = float(summary["preserved_fraction"])
    component = robustness_component(delta90, preserved_fraction)

    perturbation_count = summary.get("perturbation_count")
    if perturbation_count is not None:
        if (
            isinstance(perturbation_count, bool)
            or int(perturbation_count) != perturbation_count
            or int(perturbation_count) <= 0
        ):
            raise ValueError("perturbation_count debe ser entero positivo.")
        perturbation_count = int(perturbation_count)

    perturbation_rule = summary.get("perturbation_rule")
    if perturbation_rule is not None and not isinstance(
        perturbation_rule, (str, Mapping)
    ):
        raise ValueError("perturbation_rule debe ser string, objeto o null.")

    output: dict[str, Any] = {
        "preregistration_ref": preregistration_ref,
        "subject_scope": summary.get("subject_scope"),
        "perturbation_rule": (
            dict(perturbation_rule)
            if isinstance(perturbation_rule, Mapping)
            else perturbation_rule
        ),
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
            "M23 no estima delta90 ni genera perturbaciones; exige un resumen preregistrado.",
            "El componente se integra en IRC únicamente en M25.",
        ),
    )
