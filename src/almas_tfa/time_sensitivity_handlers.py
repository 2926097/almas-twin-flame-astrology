from __future__ import annotations

from typing import Any, Mapping

from .core import robustness_component
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .time_perturbation import generate_birth_time_sensitivity, load_birth_time_perturbation_policy


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



def make_m23_time_sensitivity(astrology_backend, davison_backend):
    """Construye M23 automático con backends explícitos.

    Si Q4 no puede evaluarse, conserva el adaptador legacy basado en
    time_sensitivity_summary cuando exista. El fallback no se usa si la
    generación automática sí es evaluable.
    """

    def m23_auto(context: ModuleContext) -> ModuleResult:
        auto = generate_birth_time_sensitivity(
            context.raw_input,
            astrology_backend=astrology_backend,
            davison_backend=davison_backend,
            policy=load_birth_time_perturbation_policy(),
        )

        if auto.get("state") == "EVALUABLE":
            delta90 = float(auto["delta90"])
            preserved_fraction = float(auto["preserved_fraction"])
            component = robustness_component(delta90, preserved_fraction)

            output = {
                "preregistration_ref": auto["preregistration_ref"],
                "subject_scope": auto["subject_scope"],
                "perturbation_rule": auto["perturbation_rule"],
                "metric": auto["metric"],
                "preservation_metric": auto["preservation_metric"],
                "percentile": auto["percentile"],
                "percentile_method": auto["percentile_method"],
                "delta90": delta90,
                "preserved_fraction": preserved_fraction,
                "perturbation_count": int(auto["perturbation_count"]),
                "robustness_component": component,
                "perturbations_generated_by_m23": True,
                "generator_policy_id": auto["policy_id"],
                "generator_policy_status": auto["policy_status"],
                "epistemic_class": auto["epistemic_class"],
                "baseline": auto["baseline"],
                "samples": auto["samples"],
                "root_preservation_min": auto["root_preservation_min"],
                "root_preservation_mean": auto["root_preservation_mean"],
                "root_preservation_max": auto["root_preservation_max"],
                "iem_delta_max": auto["iem_delta_max"],
                "idd_recomputed": auto["idd_recomputed"],
                "ice_used": auto["ice_used"],
                "iem_final_used": auto["iem_final_used"],
                "temporal_activation_used": auto["temporal_activation_used"],
                "null_rarity_used": auto["null_rarity_used"],
            }

            return ModuleResult(
                module_id="M23",
                status=ExecutionStatus.COMPLETED,
                payload=output,
                canonical_updates={"time_sensitivity": output},
                limitations=(
                    "La parrilla horaria es una política de proyecto congelada, no una validación empírica de las categorías A/B/C/D.",
                    "delta90 mide movimiento máximo de IEM_pre; G mide preservación media de raíces core.",
                    "IDD stability queda separado para Q5 y no se duplica dentro de BIRTH_TIME.",
                    "El componente BIRTH_TIME se integra en IRC únicamente en M25.",
                ),
                diagnostics=(
                    "M23 source=AUTO_BIRTH_TIME_PERTURBATION",
                ),
            )

        legacy = context.raw_input.get("time_sensitivity_summary")
        if isinstance(legacy, Mapping):
            result = m23_time_sensitivity(context)
            if result.status is ExecutionStatus.COMPLETED:
                return ModuleResult(
                    module_id="M23",
                    status=result.status,
                    payload=result.payload,
                    canonical_updates=result.canonical_updates,
                    evidence_refs=result.evidence_refs,
                    limitations=result.limitations
                    + (
                        "Fallback legacy utilizado porque Q4 automático no fue evaluable: "
                        + str(auto.get("reason")),
                    ),
                    diagnostics=result.diagnostics
                    + ("M23 source=LEGACY_PRECOMPUTED_SUMMARY",),
                )
            return result

        return not_evaluable_result(
            "M23",
            "Q4 automático no evaluable: " + str(auto.get("reason")),
        )

    return m23_auto
