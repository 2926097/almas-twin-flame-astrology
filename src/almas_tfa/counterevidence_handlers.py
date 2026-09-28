from __future__ import annotations

from collections import defaultdict
from math import isfinite
from numbers import Real
from typing import Any, Mapping

from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .quantitative_contracts import MODELS, validate_ice_by_model
from .quantitative_v122 import derive_autonomous_ice


ALLOWED_KINDS = {"EXPLICIT_CONTRADICTION", "STRUCTURAL_INCOMPATIBILITY"}


def m20_counterevidence(context: ModuleContext) -> ModuleResult:
    """M20: normaliza contraevidencia explícita y elimina duplicación dependiente."""

    raw_items = context.raw_input.get("counterevidence_items")
    precomputed_ice = validate_ice_by_model(
        context.raw_input.get("ice_by_model")
    )
    assessment_complete = context.raw_input.get(
        "counterevidence_assessment_complete",
        False,
    )
    if not isinstance(assessment_complete, bool):
        raise ValueError(
            "counterevidence_assessment_complete debe ser booleano."
        )
    if assessment_complete and precomputed_ice is not None:
        raise ValueError(
            "No se puede mezclar ICE autónomo con ice_by_model precomputado."
        )

    if raw_items is None:
        raw_items = []
    if not isinstance(raw_items, list):
        raise ValueError("counterevidence_items debe ser una lista.")

    if not raw_items and precomputed_ice is None and not assessment_complete:
        return not_evaluable_result(
            "M20",
            "No se declararon contradicciones explícitas ni ICE precomputado.",
        )

    exploded: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, Mapping):
            raise ValueError("Cada elemento de contraevidencia debe ser un objeto.")

        item_id = str(raw.get("id") or f"CE{index:04d}")
        kind = raw.get("kind")
        if kind not in ALLOWED_KINDS:
            raise ValueError(
                f"{item_id}: kind debe ser EXPLICIT_CONTRADICTION o STRUCTURAL_INCOMPATIBILITY; "
                "los datos ausentes no son contraevidencia."
            )

        contradiction_key = raw.get("contradiction_key")
        dependency_family = raw.get("dependency_family")
        models = raw.get("models")

        if not isinstance(contradiction_key, str) or not contradiction_key:
            raise ValueError(f"{item_id}: contradiction_key es obligatorio.")
        if not isinstance(dependency_family, str) or not dependency_family:
            raise ValueError(f"{item_id}: dependency_family es obligatoria.")
        if not isinstance(models, list) or not models:
            raise ValueError(f"{item_id}: models debe contener al menos un modelo.")

        severity = raw.get("severity")
        if severity is not None:
            if (
                isinstance(severity, bool)
                or not isinstance(severity, Real)
            ):
                raise ValueError(
                    f"{item_id}: severity debe ser numérico real."
                )
            severity = float(severity)
            if not isfinite(severity) or not 0.0 <= severity <= 1.0:
                raise ValueError(
                    f"{item_id}: severity debe ser finito y estar en [0,1]."
                )

        essential = raw.get("essential", False)
        if not isinstance(essential, bool):
            raise ValueError(f"{item_id}: essential debe ser booleano.")

        for model in models:
            if model not in MODELS:
                raise ValueError(f"{item_id}: modelo desconocido {model}.")
            exploded.append(
                {
                    "id": item_id,
                    "model": model,
                    "kind": kind,
                    "contradiction_key": contradiction_key,
                    "dependency_family": dependency_family,
                    "essential": essential,
                    "severity": severity,
                    "evidence_refs": list(raw.get("evidence_refs", [])),
                    "note": raw.get("note"),
                }
            )

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in exploded:
        key = (
            f"{item['model']}|{item['dependency_family']}|"
            f"{item['contradiction_key']}"
        )
        groups[key].append(item)

    retained_by_model: dict[str, list[dict[str, Any]]] = {
        model: [] for model in MODELS
    }
    suppressed: list[dict[str, Any]] = []

    for key in sorted(groups):
        members = groups[key]
        members.sort(
            key=lambda item: (
                -int(bool(item["essential"])),
                -(item["severity"] if item["severity"] is not None else -1.0),
                item["id"],
            )
        )
        winner = dict(members[0])
        retained_by_model[winner["model"]].append(winner)

        for duplicate in members[1:]:
            dup = dict(duplicate)
            dup["suppressed_by"] = winner["id"]
            dup["suppression_reason"] = "SAME_CONTRADICTION_AND_DEPENDENCY_FAMILY"
            suppressed.append(dup)

    models_output: dict[str, Any] = {}
    for model in MODELS:
        items = retained_by_model[model]
        models_output[model] = {
            "items": items,
            "contradiction_count": len(items),
            "essential_contradiction": any(
                bool(item["essential"]) for item in items
            ),
        }

    if assessment_complete:
        autonomous_ice, ice_family_diagnostics = derive_autonomous_ice(
            retained_by_model
        )
        ice_state = "AUTONOMOUS"
        ice_by_model = autonomous_ice
        ice_formula_id = "ALMAS_ICE_AUTONOMOUS_V1"
    elif precomputed_ice is not None:
        ice_state = "PRECOMPUTED"
        ice_by_model = precomputed_ice
        ice_family_diagnostics = {model: [] for model in MODELS}
        ice_formula_id = None
    else:
        ice_state = "NOT_CALCULATED"
        ice_by_model = None
        ice_family_diagnostics = {model: [] for model in MODELS}
        ice_formula_id = None

    output = {
        "models": models_output,
        "suppressed": suppressed,
        "assessment_complete": assessment_complete,
        "ice_state": ice_state,
        "ice_formula_id": ice_formula_id,
        "ice_by_model": ice_by_model,
        "ice_family_diagnostics": ice_family_diagnostics,
        "missing_data_penalized": False,
    }

    return ModuleResult(
        module_id="M20",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"counterevidence": output},
        limitations=(
            "ICE autónomo sólo se deriva cuando counterevidence_assessment_complete=true.",
            "La agregación de severidad no representa una probabilidad metafísica.",
            "La ausencia de datos no se penaliza como contraevidencia.",
        ),
    )
