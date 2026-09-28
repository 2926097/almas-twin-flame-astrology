from __future__ import annotations

from collections import defaultdict
from math import isfinite
from numbers import Real
from typing import Any, Mapping, Sequence

from .quantitative_contracts import MODELS, validate_ice_by_model


ALLOWED_KINDS = {"EXPLICIT_CONTRADICTION", "STRUCTURAL_INCOMPATIBILITY"}
ICE_FORMULA_ID = "ALMAS_ICE_AUTONOMOUS_V1"
ICE_WEIGHTS = (1.0, 0.5, 1.0 / 3.0)


def _validate_severity(value: Any, *, item_id: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{item_id}: severity debe ser numérica.")
    severity = float(value)
    if not isfinite(severity) or not 0.0 <= severity <= 1.0:
        raise ValueError(f"{item_id}: severity debe estar en [0,1].")
    return severity


def normalize_counterevidence(
    raw_items: Any,
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    """Normaliza y deduplica contraevidencia explícita.

    La unidad de deduplicación es modelo + familia de dependencia + clave de
    contradicción. La ausencia de datos no se acepta como contraevidencia.
    """

    if raw_items is None:
        raw_items = []
    if not isinstance(raw_items, list):
        raise ValueError("counterevidence_items debe ser una lista.")

    exploded: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, Mapping):
            raise ValueError("Cada elemento de contraevidencia debe ser un objeto.")

        item_id = str(raw.get("id") or f"CE{index:04d}")
        kind = raw.get("kind")
        if kind not in ALLOWED_KINDS:
            raise ValueError(
                f"{item_id}: kind debe ser EXPLICIT_CONTRADICTION o "
                "STRUCTURAL_INCOMPATIBILITY; los datos ausentes no son "
                "contraevidencia."
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

        severity = _validate_severity(raw.get("severity"), item_id=item_id)
        evidence_refs_raw = raw.get("evidence_refs", [])
        if not isinstance(evidence_refs_raw, list):
            raise ValueError(f"{item_id}: evidence_refs debe ser una lista.")
        evidence_refs = [str(value) for value in evidence_refs_raw]

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
                    "evidence_refs": evidence_refs,
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

    retained: dict[str, list[dict[str, Any]]] = {model: [] for model in MODELS}
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
        retained[winner["model"]].append(winner)
        for duplicate in members[1:]:
            item = dict(duplicate)
            item["suppressed_by"] = winner["id"]
            item["suppression_reason"] = (
                "SAME_CONTRADICTION_AND_DEPENDENCY_FAMILY"
            )
            suppressed.append(item)

    for model in MODELS:
        retained[model].sort(
            key=lambda item: (
                item["dependency_family"],
                item["contradiction_key"],
                item["id"],
            )
        )
    return retained, suppressed


def derive_ice_by_model(
    retained_by_model: Mapping[str, Sequence[Mapping[str, Any]]],
) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    """Deriva ICE autónomo después de deduplicar dependencia.

    Dentro de cada familia se conserva la severidad máxima. Entre familias se
    agregan como máximo las tres severidades más altas con pesos 1, 1/2, 1/3,
    normalizados por los pesos efectivamente presentes. ICE es un índice
    acotado de contraevidencia, no una probabilidad metafísica.
    """

    ice: dict[str, float] = {}
    family_scores_by_model: dict[str, dict[str, float]] = {}

    for model in MODELS:
        family_scores: dict[str, float] = {}
        for item in retained_by_model.get(model, []):
            severity = item.get("severity")
            if severity is None:
                raise ValueError(
                    f"{item.get('id', 'counterevidence')}: severity es "
                    "obligatoria cuando counterevidence_review_complete=true."
                )
            severity = _validate_severity(
                severity,
                item_id=str(item.get("id") or "counterevidence"),
            )
            family = str(item.get("dependency_family") or "")
            if not family:
                raise ValueError("Contraevidencia sin dependency_family.")
            family_scores[family] = max(
                family_scores.get(family, 0.0),
                float(severity),
            )

        ordered = sorted(family_scores.values(), reverse=True)[:3]
        if not ordered:
            ice[model] = 0.0
        else:
            weights = ICE_WEIGHTS[: len(ordered)]
            ice[model] = 100.0 * sum(
                value * weight
                for value, weight in zip(ordered, weights)
            ) / sum(weights)
        family_scores_by_model[model] = {
            key: family_scores[key] for key in sorted(family_scores)
        }

    return ice, family_scores_by_model


def resolve_counterevidence(raw_input: Mapping[str, Any]) -> dict[str, Any]:
    """Resuelve M19/M20 desde una única implementación fail-closed."""

    retained, suppressed = normalize_counterevidence(
        raw_input.get("counterevidence_items")
    )
    precomputed = validate_ice_by_model(raw_input.get("ice_by_model"))

    review_raw = raw_input.get("counterevidence_review_complete")
    if review_raw is not None and not isinstance(review_raw, bool):
        raise ValueError("counterevidence_review_complete debe ser booleano.")
    review_complete = review_raw is True

    family_scores = {model: {} for model in MODELS}
    consistency_checked = False

    if review_complete:
        derived, family_scores = derive_ice_by_model(retained)
        if precomputed is not None:
            consistency_checked = True
            conflicts = [
                model for model in MODELS
                if abs(precomputed[model] - derived[model]) > 1e-9
            ]
            if conflicts:
                raise ValueError(
                    "ICE precomputado contradice ALMAS_ICE_AUTONOMOUS_V1 "
                    "para: " + ", ".join(conflicts) + "."
                )
        ice_by_model = derived
        ice_state = "DERIVED_AUTONOMOUS_V1"
        formula_id: str | None = ICE_FORMULA_ID
    elif precomputed is not None:
        ice_by_model = precomputed
        ice_state = "PRECOMPUTED"
        formula_id = None
    else:
        ice_by_model = None
        ice_state = "NOT_CALCULATED"
        formula_id = None

    models: dict[str, Any] = {}
    for model in MODELS:
        items = retained[model]
        models[model] = {
            "items": items,
            "contradiction_count": len(items),
            "essential_contradiction": any(
                bool(item["essential"]) for item in items
            ),
            "dependency_family_scores": family_scores[model],
        }

    return {
        "models": models,
        "suppressed": suppressed,
        "ice_state": ice_state,
        "ice_by_model": ice_by_model,
        "ice_formula_id": formula_id,
        "counterevidence_review_complete": review_complete,
        "precomputed_consistency_checked": consistency_checked,
        "missing_data_penalized": False,
    }
