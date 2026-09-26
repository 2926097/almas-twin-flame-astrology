from __future__ import annotations

from typing import Any, Mapping

from .core import robustness_index
from .module_contract import (
    ExecutionStatus,
    ModuleContext,
    ModuleResult,
    not_evaluable_result,
)


ALLOWED_COMPONENT_KINDS = {
    "BIRTH_TIME",
    "ABLATION",
    "PARAMETER_PERTURBATION",
    "IDD_STABILITY",
    "VALIDATED_DISCRIMINATOR",
}

FORBIDDEN_COMPONENT_KINDS = {
    "NULL_RARITY",
    "NULL_MODEL_FREQUENCY",
    "METAPHYSICAL_PROBABILITY",
}


def _validated_ontology_roots(canonical_snapshot: Mapping[str, Any]) -> set[str]:
    """Devuelve únicamente raíces L3 confirmatorias presentes en M21."""

    ontology = canonical_snapshot.get("ontological_discrimination")
    if not isinstance(ontology, Mapping):
        return set()

    matrix = ontology.get("pairwise_matrix")
    if not isinstance(matrix, Mapping):
        return set()

    roots: set[str] = set()
    for assessment in matrix.values():
        if not isinstance(assessment, Mapping):
            continue
        if assessment.get("confirmatory_status") != "SEPARABLE_VALIDATED":
            continue
        validated_roots = assessment.get("validated_roots")
        if not isinstance(validated_roots, list):
            continue
        for root in validated_roots:
            if isinstance(root, str) and root:
                roots.add(root)

    return roots


def _validate_discriminator_component(
    raw: Mapping[str, Any],
    component: Mapping[str, Any],
    canonical_snapshot: Mapping[str, Any],
) -> None:
    """Impide que L1/L2 o señales no trazables entren en IRC como L3."""

    component_id = str(component["id"])

    validation_level = raw.get("validation_level")
    if validation_level != "L3_VALIDATED":
        raise ValueError(
            f"{component_id}: VALIDATED_DISCRIMINATOR requiere "
            "validation_level=L3_VALIDATED."
        )

    if component.get("source_module") != "M21":
        raise ValueError(
            f"{component_id}: VALIDATED_DISCRIMINATOR debe declarar "
            "source_module=M21."
        )

    root_key = raw.get("root_key")
    if not isinstance(root_key, str) or not root_key:
        raise ValueError(
            f"{component_id}: VALIDATED_DISCRIMINATOR requiere root_key trazable."
        )

    validated_roots = _validated_ontology_roots(canonical_snapshot)
    if root_key not in validated_roots:
        raise ValueError(
            f"{component_id}: root_key={root_key!r} no consta como raíz "
            "L3 confirmatoria en ontological_discrimination."
        )


def _validated_component(raw: Mapping[str, Any], index: int) -> dict[str, Any]:
    component_id = raw.get("id")
    if not isinstance(component_id, str) or not component_id:
        raise ValueError(f"Componente {index}: id es obligatorio.")

    kind = raw.get("kind")
    if kind in FORBIDDEN_COMPONENT_KINDS:
        raise ValueError(
            f"{component_id}: la rareza de modelos nulos no es un componente IRC."
        )
    if kind not in ALLOWED_COMPONENT_KINDS:
        raise ValueError(
            f"{component_id}: kind debe ser uno de {sorted(ALLOWED_COMPONENT_KINDS)}."
        )

    value = raw.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{component_id}: value debe ser numérico.")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{component_id}: value debe estar en [0,1].")

    source_module = raw.get("source_module")
    if not isinstance(source_module, str) or not source_module:
        raise ValueError(f"{component_id}: source_module es obligatorio.")

    preregistration_ref = raw.get("preregistration_ref")
    if not isinstance(preregistration_ref, str) or not preregistration_ref:
        raise ValueError(f"{component_id}: preregistration_ref es obligatorio.")

    derivation_ref = raw.get("derivation_ref")
    if not isinstance(derivation_ref, str) or not derivation_ref:
        raise ValueError(f"{component_id}: derivation_ref es obligatorio.")

    return {
        "id": component_id,
        "kind": kind,
        "value": value,
        "source_module": source_module,
        "preregistration_ref": preregistration_ref,
        "derivation_ref": derivation_ref,
        "note": raw.get("note"),
        "auto_derived": False,
    }


def m25_robustness(context: ModuleContext) -> ModuleResult:
    """M25: consolida componentes aplicables en IRC y R_min.

    Reglas:
    - M23 aporta BIRTH_TIME automáticamente porque su fórmula está definida.
    - M22 sólo puede aportar ABLATION mediante un componente preregistrado.
    - M24 no aporta rareza/frecuencia a IRC.
    - VALIDATED_DISCRIMINATOR exige L3_VALIDATED y respaldo canónico M21.
    - los demás componentes deben declarar procedencia y derivación.
    """

    components: list[dict[str, Any]] = []
    ids: set[str] = set()

    time_sensitivity = context.canonical_snapshot.get("time_sensitivity")
    time_state = "ABSENT"
    if isinstance(time_sensitivity, Mapping):
        value = time_sensitivity.get("robustness_component")
        preregistration_ref = time_sensitivity.get("preregistration_ref")
        if value is not None:
            if not isinstance(preregistration_ref, str) or not preregistration_ref:
                raise ValueError(
                    "M23 aporta robustez sin preregistration_ref trazable."
                )
            value = float(value)
            if not 0.0 <= value <= 1.0:
                raise ValueError("El componente BIRTH_TIME de M23 debe estar en [0,1].")
            components.append(
                {
                    "id": "BIRTH_TIME",
                    "kind": "BIRTH_TIME",
                    "value": value,
                    "source_module": "M23",
                    "preregistration_ref": preregistration_ref,
                    "derivation_ref": "ALMAS:R_X=exp(-delta90/20)*sqrt(G)",
                    "note": None,
                    "auto_derived": True,
                }
            )
            ids.add("BIRTH_TIME")
            time_state = "INCLUDED"

    raw_components = context.raw_input.get("robustness_component_summaries")
    if raw_components is None:
        raw_components = []
    if not isinstance(raw_components, list):
        raise ValueError("robustness_component_summaries debe ser una lista.")

    ablation = context.canonical_snapshot.get("ablation")
    ablation_present = isinstance(ablation, Mapping)
    ablation_included = False

    for index, raw in enumerate(raw_components, start=1):
        if not isinstance(raw, Mapping):
            raise ValueError(
                f"robustness_component_summaries[{index - 1}] debe ser un objeto."
            )

        component = _validated_component(raw, index)
        component_id = component["id"]

        if component_id in ids:
            raise ValueError(
                f"Componente de robustez duplicado: {component_id}."
            )

        if component["kind"] == "BIRTH_TIME":
            if time_state == "INCLUDED":
                raise ValueError(
                    "BIRTH_TIME ya procede de M23 y no puede sobrescribirse."
                )

        if component["kind"] == "ABLATION":
            if component["source_module"] != "M22":
                raise ValueError(
                    f"{component_id}: ABLATION debe declarar source_module=M22."
                )
            if not ablation_present:
                raise ValueError(
                    f"{component_id}: no existe salida canónica M22 para respaldar ABLATION."
                )
            ablation_included = True

        if component["kind"] == "VALIDATED_DISCRIMINATOR":
            _validate_discriminator_component(
                raw,
                component,
                context.canonical_snapshot,
            )

        if component["source_module"] == "M24":
            raise ValueError(
                f"{component_id}: M24 no puede convertirse en componente IRC."
            )

        components.append(component)
        ids.add(component_id)

    if not components:
        return not_evaluable_result(
            "M25",
            "No existen componentes de robustez aplicables y preregistrados.",
        )

    values = [component["value"] for component in components]
    irc, r_min = robustness_index(values)

    if ablation_included:
        ablation_state = "INCLUDED_PREREGISTERED"
    elif ablation_present:
        ablation_state = "AVAILABLE_NOT_QUANTIFIED"
    else:
        ablation_state = "ABSENT"

    null_models = context.canonical_snapshot.get("null_models")
    null_model_state = (
        "AVAILABLE_EXCLUDED_FROM_IRC"
        if isinstance(null_models, Mapping)
        else "ABSENT"
    )

    output = {
        "irc": irc,
        "r_min": r_min,
        "components": components,
        "component_count": len(components),
        "time_sensitivity_state": time_state,
        "ablation_state": ablation_state,
        "null_model_state": null_model_state,
        "null_model_rarity_used_as_robustness": False,
        "formula": "100 * geometric_mean(applicable_R_i)",
        "r_min_formula": "min(applicable_R_i)",
    }

    return ModuleResult(
        module_id="M25",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"robustness_index": output},
        limitations=(
            "M22 no se transforma automáticamente en un componente IRC sin regla preregistrada.",
            "La rareza/frecuencia de M24 queda excluida de IRC.",
            "Sólo discriminadores L3 validados y trazables desde M21 pueden entrar en IRC.",
        ),
    )
