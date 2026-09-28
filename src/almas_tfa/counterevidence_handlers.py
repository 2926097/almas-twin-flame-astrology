from __future__ import annotations

from collections import defaultdict
from math import isfinite
from numbers import Real
from typing import Any, Mapping

from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .quantitative_contracts import MODELS, validate_ice_by_model


ALLOWED_KINDS = {"EXPLICIT_CONTRADICTION", "STRUCTURAL_INCOMPATIBILITY"}
AUTONOMOUS_ICE_FORMULA = (
    "100 * (1 - product(1 - severity_k for distinct contradiction_key k))"
)


def _derive_autonomous_ice(
    retained_by_model: Mapping[str, list[dict[str, Any]]],
) -> tuple[dict[str, float], dict[str, Any]]:
    """Deriva ICE desde contradicciones explícitas con deduplicación semántica.

    La fórmula es un operador de saturación acotado, no una probabilidad. Una
    misma contradiction_key observada en varias familias conserva únicamente
    su severidad máxima, evitando que la corroboración técnica multiplique una
    contradicción idéntica.
    """

    ice: dict[str, float] = {}
    details: dict[str, Any] = {}

    for model in MODELS:
        by_key: dict[str, float] = {}
        for item in retained_by_model.get(model, []):
            severity = item.get("severity")
            if (
                isinstance(severity, bool)
                or not isinstance(severity, Real)
            ):
                raise ValueError(
                    f"{item.get('id')}: severity numérica es obligatoria "
                    "cuando counterevidence_complete=true."
                )
            severity = float(severity)
            if not isfinite(severity) or not 0.0 <= severity <= 1.0:
                raise ValueError(
                    f"{item.get('id')}: severity debe ser finita y estar en [0,1]."
                )
            key = str(item["contradiction_key"])
            by_key[key] = max(by_key.get(key, 0.0), severity)

        residual = 1.0
        for severity in by_key.values():
            residual *= 1.0 - severity
        value = 100.0 * (1.0 - residual)
        ice[model] = value
        details[model] = {
            "semantic_contradiction_count": len(by_key),
            "contradiction_severities": {
                key: by_key[key] for key in sorted(by_key)
            },
            "ice": value,
        }

    return ice, details


def m20_counterevidence(context: ModuleContext) -> ModuleResult:
    """M20: normaliza contraevidencia explícita y elimina duplicación dependiente."""

    raw_items = context.raw_input.get("counterevidence_items")
    precomputed_ice = validate_ice_by_model(
        context.raw_input.get("ice_by_model")
    )
    completeness_raw = context.raw_input.get("counterevidence_complete")
    if completeness_raw is not None and not isinstance(completeness_raw, bool):
        raise ValueError("counterevidence_complete debe ser booleano.")
    counterevidence_complete = completeness_raw is True

    if raw_items is None:
        raw_items = []
    if not isinstance(raw_items, list):
        raise ValueError("counterevidence_items debe ser una lista.")

    if (
        not raw_items
        and precomputed_ice is None
        and not counterevidence_complete
    ):
        return not_evaluable_result(
            "M20",
            "No se declararon contradicciones explícitas, ICE precomputado "
            "ni cierre explícito de la evaluación de contraevidencia.",
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
            if isinstance(severity, bool) or not isinstance(severity, Real):
                raise ValueError(f"{item_id}: severity debe ser numérica.")
            severity = float(severity)
            if not isfinite(severity) or not 0.0 <= severity <= 1.0:
                raise ValueError(
                    f"{item_id}: severity debe ser finita y estar en [0,1]."
                )

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
                    "essential": bool(raw.get("essential", False)),
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

    if precomputed_ice is not None:
        ice_state = "PRECOMPUTED"
        ice_by_model = precomputed_ice
        ice_derivation = {
            "method": "PRECOMPUTED",
            "formula": None,
            "dependency_control": "EXTERNAL_PRECOMPUTED_CONTRACT",
            "by_model": {},
        }
    elif counterevidence_complete:
        ice_by_model, derivation_details = _derive_autonomous_ice(
            retained_by_model
        )
        ice_state = "AUTONOMOUS"
        ice_derivation = {
            "method": "AUTONOMOUS_SEMANTIC_SATURATION_V1",
            "formula": AUTONOMOUS_ICE_FORMULA,
            "dependency_control": (
                "MAX_SEVERITY_PER_MODEL_AND_CONTRADICTION_KEY_AFTER_"
                "FAMILY_LEVEL_DEDUPLICATION"
            ),
            "by_model": derivation_details,
        }
    else:
        ice_state = "NOT_CALCULATED"
        ice_by_model = None
        ice_derivation = {
            "method": "NOT_CALCULATED",
            "formula": None,
            "dependency_control": None,
            "by_model": {},
        }

    output = {
        "models": models_output,
        "suppressed": suppressed,
        "ice_state": ice_state,
        "ice_by_model": ice_by_model,
        "counterevidence_complete": counterevidence_complete,
        "ice_derivation": ice_derivation,
        "missing_data_penalized": False,
    }

    return ModuleResult(
        module_id="M20",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"counterevidence": output},
        limitations=(
            "ICE autónomo sólo se deriva cuando counterevidence_complete=true; "
            "una lista parcial de contradicciones nunca se interpreta como evaluación exhaustiva.",
            "La agregación autónoma es una política cuantitativa E del proyecto, "
            "no una probabilidad metafísica ni una doctrina de fuente.",
            "Las contradicciones esenciales conservan un gate categórico separado "
            "y no reciben una penalización numérica adicional por ser esenciales.",
        ),
    )
