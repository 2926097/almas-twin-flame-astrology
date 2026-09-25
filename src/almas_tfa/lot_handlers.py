from __future__ import annotations

from typing import Any, Mapping

from .astrology_geometry import normalize_longitude
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .relational_handlers import _chart_points


def _resolve_formula(
    lot_spec: Mapping[str, Any],
    *,
    subject_id: str,
    sect_by_subject: Mapping[str, Any],
) -> Mapping[str, Any] | None:
    formula = lot_spec.get("formula")
    if isinstance(formula, Mapping):
        return formula

    variants = lot_spec.get("variants")
    if not isinstance(variants, Mapping):
        return None

    sect = sect_by_subject.get(subject_id)
    if sect not in {"DAY", "NIGHT"}:
        return None

    selected = variants.get(sect)
    return selected if isinstance(selected, Mapping) else None


def _formula_longitude(
    formula: Mapping[str, Any],
    points: Mapping[str, Mapping[str, Any]],
) -> float | None:
    base = formula.get("base")
    if not isinstance(base, str) or base not in points:
        return None

    value = float(points[base]["longitude"])

    add = formula.get("add", [])
    subtract = formula.get("subtract", [])
    if not isinstance(add, list) or not isinstance(subtract, list):
        raise ValueError("Los campos add y subtract de un lote deben ser listas.")

    for point_id in add:
        if not isinstance(point_id, str) or point_id not in points:
            return None
        value += float(points[point_id]["longitude"])

    for point_id in subtract:
        if not isinstance(point_id, str) or point_id not in points:
            return None
        value -= float(points[point_id]["longitude"])

    return normalize_longitude(value)


def m13_lots(context: ModuleContext) -> ModuleResult:
    """M13: evalúa lotes mediante fórmulas y fuentes expresamente declaradas."""

    natal = context.canonical_snapshot.get("natal")
    if not isinstance(natal, Mapping):
        return not_evaluable_result("M13", "No existe salida natal canónica.")

    charts = natal.get("charts")
    if not isinstance(charts, Mapping) or len(charts) != 2:
        return not_evaluable_result("M13", "M13 requiere exactamente dos cartas.")

    policy = context.raw_input.get("lot_policy")
    if not isinstance(policy, Mapping):
        return not_evaluable_result(
            "M13",
            "Falta lot_policy con fórmulas y source_ref declarados.",
        )

    lot_specs = policy.get("lots")
    if not isinstance(lot_specs, list) or not lot_specs:
        return not_evaluable_result("M13", "lot_policy.lots está vacío.")

    sect_by_subject = policy.get("sect_by_subject") or {}
    if not isinstance(sect_by_subject, Mapping):
        raise ValueError("lot_policy.sect_by_subject debe ser un objeto.")

    for spec in lot_specs:
        if not isinstance(spec, Mapping):
            raise ValueError("Cada lote debe ser un objeto.")
        if not isinstance(spec.get("id"), str) or not spec.get("id"):
            raise ValueError("Cada lote debe declarar id.")
        if not isinstance(spec.get("source_ref"), str) or not spec.get("source_ref"):
            raise ValueError(
                f"{spec.get('id')}: cada lote debe declarar source_ref."
            )

    output: dict[str, Any] = {
        "policy": dict(policy),
        "subjects": {},
    }
    limitations: list[str] = []

    for subject_id, chart in charts.items():
        if not isinstance(chart, Mapping):
            raise ValueError(f"{subject_id}: carta natal inválida.")

        points = _chart_points(chart)
        subject_lots: dict[str, Any] = {}

        for spec in lot_specs:
            lot_id = str(spec["id"])
            formula = _resolve_formula(
                spec,
                subject_id=str(subject_id),
                sect_by_subject=sect_by_subject,
            )

            if formula is None:
                subject_lots[lot_id] = {
                    "status": "NOT_EVALUABLE",
                    "longitude": None,
                    "source_ref": spec["source_ref"],
                    "reason": "FORMULA_OR_SECT_NOT_RESOLVED",
                }
                limitations.append(
                    f"{subject_id}/{lot_id}: fórmula o sect no resuelto."
                )
                continue

            longitude = _formula_longitude(formula, points)
            if longitude is None:
                subject_lots[lot_id] = {
                    "status": "NOT_EVALUABLE",
                    "longitude": None,
                    "source_ref": spec["source_ref"],
                    "formula": dict(formula),
                    "reason": "MISSING_FORMULA_POINT",
                }
                limitations.append(
                    f"{subject_id}/{lot_id}: falta un punto requerido por la fórmula."
                )
                continue

            subject_lots[lot_id] = {
                "status": "CALCULATED",
                "longitude": longitude,
                "source_ref": spec["source_ref"],
                "formula": dict(formula),
                "sect": sect_by_subject.get(subject_id),
            }

        output["subjects"][str(subject_id)] = subject_lots

    return ModuleResult(
        module_id="M13",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"lots": output},
        limitations=tuple(limitations),
    )
