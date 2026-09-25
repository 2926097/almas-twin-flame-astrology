from __future__ import annotations

from typing import Any, Mapping

from .astrology_geometry import match_declared_aspect
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result


def m09_relationship_chart_consonance(context: ModuleContext) -> ModuleResult:
    """M09: compara puntos homólogos entre compuesta y Davison.

    No existe un umbral implícito de consonancia. Sólo se registran contactos
    geométricos bajo una policy declarada y todos pertenecen a RELCHART.
    """

    composite = context.canonical_snapshot.get("composite")
    davison = context.canonical_snapshot.get("davison")

    if not isinstance(composite, Mapping) or not isinstance(davison, Mapping):
        return not_evaluable_result(
            "M09",
            "M09 requiere salidas canónicas de M07 y M08.",
        )

    policy = context.raw_input.get("relationship_chart_consonance_policy")
    if not isinstance(policy, Mapping):
        return not_evaluable_result(
            "M09",
            "Falta relationship_chart_consonance_policy.",
        )

    aspect_policy = policy.get("aspect_policy")
    if not isinstance(aspect_policy, Mapping) or not aspect_policy:
        return not_evaluable_result(
            "M09",
            "La policy debe declarar aspect_policy.",
        )

    composite_positions = composite.get("positions")
    davison_chart = davison.get("chart")
    davison_positions = (
        davison_chart.get("positions")
        if isinstance(davison_chart, Mapping)
        else None
    )

    if not isinstance(composite_positions, Mapping) or not isinstance(davison_positions, Mapping):
        return not_evaluable_result(
            "M09",
            "Compuesta o Davison no contienen posiciones comparables.",
        )

    declared_points = policy.get("point_ids")
    if declared_points is None:
        point_ids = sorted(set(composite_positions) & set(davison_positions))
    elif isinstance(declared_points, list):
        point_ids = [
            str(point_id)
            for point_id in declared_points
            if point_id in composite_positions and point_id in davison_positions
        ]
    else:
        raise ValueError("point_ids debe ser lista cuando se declara.")

    contacts: list[dict[str, Any]] = []
    unavailable: list[str] = []

    for point_id in point_ids:
        c_data = composite_positions.get(point_id)
        d_data = davison_positions.get(point_id)

        if not isinstance(c_data, Mapping) or not isinstance(d_data, Mapping):
            unavailable.append(point_id)
            continue

        c_lon = c_data.get("longitude")
        d_lon = d_data.get("longitude")
        if c_lon is None or d_lon is None:
            unavailable.append(point_id)
            continue

        match = match_declared_aspect(
            float(c_lon),
            float(d_lon),
            aspect_policy,
        )
        if match is None:
            continue

        contacts.append(
            {
                "subject_a": "RELCHART_COMPOSITE",
                "point_a": point_id,
                "longitude_a": float(c_lon),
                "subject_b": "RELCHART_DAVISON",
                "point_b": point_id,
                "longitude_b": float(d_lon),
                "dependency_family": "RELCHART",
                **match,
            }
        )

    contacts.sort(key=lambda x: (x["orb"], x["point_a"], x["aspect"]))
    output = {
        "dependency_family": "RELCHART",
        "policy": dict(policy),
        "contacts": contacts,
        "contact_count": len(contacts),
        "unavailable_points": sorted(set(unavailable)),
        "consonance_score": None,
        "score_state": "NOT_DEFINED",
    }

    return ModuleResult(
        module_id="M09",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"relationship_chart_consonance": output},
        limitations=(
            "M09 registra geometría compuesta↔Davison dentro de una única familia RELCHART; no existe puntuación de consonancia preregistrada.",
        ),
    )
