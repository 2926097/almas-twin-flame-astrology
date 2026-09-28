from __future__ import annotations

from typing import Any, Mapping

from .astrology_geometry import match_declared_aspect
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .relational_handlers import _chart_points


def m14_secondary_symbolic(context: ModuleContext) -> ModuleResult:
    """M14: contactos de puntos secundarios declarados, siempre support-only."""

    natal = context.canonical_snapshot.get("natal")
    if not isinstance(natal, Mapping):
        return not_evaluable_result("M14", "No existe salida natal canónica.")

    charts = natal.get("charts")
    if not isinstance(charts, Mapping) or len(charts) != 2:
        return not_evaluable_result("M14", "M14 requiere exactamente dos cartas.")

    policy = context.raw_input.get("secondary_symbolic_policy")
    if not isinstance(policy, Mapping):
        return not_evaluable_result(
            "M14",
            "Falta secondary_symbolic_policy.",
        )

    if policy.get("support_only") is not True:
        raise ValueError(
            "M14 exige support_only=true; la capa secundaria no puede ser core por sí sola."
        )

    point_ids = policy.get("point_ids")
    if not isinstance(point_ids, list) or not point_ids:
        return not_evaluable_result(
            "M14",
            "secondary_symbolic_policy.point_ids debe declarar al menos un punto.",
        )
    selected = {str(x) for x in point_ids if isinstance(x, str) and x}
    if not selected:
        return not_evaluable_result("M14", "No hay point_ids válidos.")

    aspect_policy = policy.get("aspect_policy")
    if not isinstance(aspect_policy, Mapping) or not aspect_policy:
        return not_evaluable_result(
            "M14",
            "Falta aspect_policy específico de la capa secundaria.",
        )

    subject_ids = list(charts)
    a_id, b_id = subject_ids
    a_points = _chart_points(charts[a_id])
    b_points = _chart_points(charts[b_id])

    missing = {
        a_id: sorted(selected - set(a_points)),
        b_id: sorted(selected - set(b_points)),
    }

    if not (selected & set(a_points) or selected & set(b_points)):
        return not_evaluable_result(
            "M14",
            "Ninguno de los puntos secundarios declarados está disponible.",
        )

    contacts: list[dict[str, Any]] = []
    for a_point, a_data in sorted(a_points.items()):
        for b_point, b_data in sorted(b_points.items()):
            if a_point not in selected and b_point not in selected:
                continue

            matched = match_declared_aspect(
                float(a_data["longitude"]),
                float(b_data["longitude"]),
                aspect_policy,
            )
            if matched is None:
                continue

            contacts.append(
                {
                    "subject_a": a_id,
                    "point_a": a_point,
                    "point_a_secondary": a_point in selected,
                    "longitude_a": float(a_data["longitude"]),
                    "subject_b": b_id,
                    "point_b": b_point,
                    "point_b_secondary": b_point in selected,
                    "longitude_b": float(b_data["longitude"]),
                    **matched,
                    "support_only": True,
                }
            )

    contacts.sort(
        key=lambda x: (
            x["orb"],
            x["aspect"],
            x["point_a"],
            x["point_b"],
        )
    )

    output = {
        "subjects": [a_id, b_id],
        "point_ids": sorted(selected),
        "support_only": True,
        "aspect_policy": {
            str(name): dict(spec)
            for name, spec in aspect_policy.items()
            if isinstance(spec, Mapping)
        },
        "missing_points_by_subject": missing,
        "contacts": contacts,
        "contact_count": len(contacts),
    }

    return ModuleResult(
        module_id="M14",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"secondary_symbolic": output},
        limitations=(
            "M14 es support-only y no puede crear por sí sola una raíz ontológica.",
        ),
    )
