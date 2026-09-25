from __future__ import annotations

from typing import Any, Mapping

from .astrology_geometry import (
    house_for_longitude,
    match_declared_aspect,
    zodiac_sign,
)
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result


def _chart_points(chart: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Une posiciones y ángulos disponibles sin inventar puntos."""

    points: dict[str, dict[str, Any]] = {}

    positions = chart.get("positions")
    if isinstance(positions, Mapping):
        for point_id, data in positions.items():
            if not isinstance(data, Mapping) or "longitude" not in data:
                continue
            points[str(point_id)] = dict(data)

    angles = chart.get("angles")
    if isinstance(angles, Mapping):
        for point_id, longitude in angles.items():
            key = str(point_id)
            if key in points:
                continue
            points[key] = {
                "longitude": float(longitude),
                "point_type": "ANGLE",
            }

    return points


def m03_synastry(context: ModuleContext) -> ModuleResult:
    """M03: calcula contactos cruzados usando exclusivamente orbes declarados."""

    natal = context.canonical_snapshot.get("natal")
    if not isinstance(natal, Mapping):
        return not_evaluable_result(
            "M03",
            "No existe salida natal canónica procedente de M02.",
        )

    charts = natal.get("charts")
    if not isinstance(charts, Mapping) or len(charts) != 2:
        return not_evaluable_result(
            "M03",
            "M03 requiere exactamente dos cartas natales canónicas.",
        )

    policy = context.raw_input.get("aspect_policy")
    if not isinstance(policy, Mapping) or not policy:
        return not_evaluable_result(
            "M03",
            "Falta aspect_policy; ALMAS no aplica orbes implícitos.",
        )

    subject_ids = list(charts)
    a_id, b_id = subject_ids[0], subject_ids[1]
    a_points = _chart_points(charts[a_id])
    b_points = _chart_points(charts[b_id])

    contacts: list[dict[str, Any]] = []
    for a_point, a_data in sorted(a_points.items()):
        for b_point, b_data in sorted(b_points.items()):
            matched = match_declared_aspect(
                float(a_data["longitude"]),
                float(b_data["longitude"]),
                policy,
            )
            if matched is None:
                continue

            contacts.append(
                {
                    "subject_a": a_id,
                    "point_a": a_point,
                    "point_a_type": a_data.get("point_type"),
                    "longitude_a": float(a_data["longitude"]),
                    "subject_b": b_id,
                    "point_b": b_point,
                    "point_b_type": b_data.get("point_type"),
                    "longitude_b": float(b_data["longitude"]),
                    **matched,
                }
            )

    contacts.sort(
        key=lambda item: (
            item["orb"],
            item["aspect"],
            item["point_a"],
            item["point_b"],
        )
    )

    output = {
        "subjects": [a_id, b_id],
        "aspect_policy": {
            str(name): dict(spec)
            for name, spec in policy.items()
            if isinstance(spec, Mapping)
        },
        "contacts": contacts,
        "contact_count": len(contacts),
    }

    return ModuleResult(
        module_id="M03",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"synastry": output},
        limitations=(
            "M03 describe geometría cruzada; no convierte por sí sola un contacto en raíz ontológica.",
        ),
    )


def m04_nodes_angles_houses_regencies(context: ModuleContext) -> ModuleResult:
    """M04: contextualiza puntos, nodos, ángulos, casas y regencias.

    Las regencias sólo se calculan cuando la entrada declara rulership_policy.
    No se impone una escuela de regencias por defecto.
    """

    natal = context.canonical_snapshot.get("natal")
    if not isinstance(natal, Mapping):
        return not_evaluable_result(
            "M04",
            "No existe salida natal canónica procedente de M02.",
        )

    charts = natal.get("charts")
    if not isinstance(charts, Mapping) or len(charts) != 2:
        return not_evaluable_result(
            "M04",
            "M04 requiere exactamente dos cartas natales canónicas.",
        )

    rulership_policy = context.raw_input.get("rulership_policy")
    if rulership_policy is not None and not isinstance(rulership_policy, Mapping):
        raise ValueError("rulership_policy debe ser un objeto cuando se declara.")

    output: dict[str, Any] = {"subjects": {}}
    limitations: list[str] = []

    for subject_id, chart in charts.items():
        if not isinstance(chart, Mapping):
            raise ValueError(f"{subject_id}: carta natal inválida.")

        points = _chart_points(chart)
        point_signs: dict[str, Any] = {}
        nodes: dict[str, Any] = {}

        for point_id, data in sorted(points.items()):
            longitude = float(data["longitude"])
            sign_data = zodiac_sign(longitude)
            point_signs[point_id] = {
                "longitude": longitude,
                **sign_data,
                "point_type": data.get("point_type"),
            }
            if data.get("point_type") == "NODE":
                nodes[point_id] = point_signs[point_id]

        angles = chart.get("angles")
        angle_context: dict[str, Any] = {}
        if isinstance(angles, Mapping):
            for angle_id, longitude in sorted(angles.items()):
                angle_context[str(angle_id)] = {
                    "longitude": float(longitude),
                    **zodiac_sign(float(longitude)),
                }

        houses = chart.get("houses")
        cusp_context: dict[str, Any] = {}
        placements: dict[str, Any] = {}
        regencies: dict[str, Any] = {}

        if isinstance(houses, Mapping) and all(str(i) in houses for i in range(1, 13)):
            for i in range(1, 13):
                key = str(i)
                longitude = float(houses[key])
                sign_data = zodiac_sign(longitude)
                cusp_context[key] = {
                    "longitude": longitude,
                    **sign_data,
                }

                if isinstance(rulership_policy, Mapping):
                    rulers = rulership_policy.get(sign_data["sign"])
                    if rulers is not None:
                        if isinstance(rulers, str):
                            rulers = [rulers]
                        elif isinstance(rulers, (tuple, list)):
                            rulers = list(rulers)
                        else:
                            raise ValueError(
                                f"{sign_data['sign']}: regencia debe ser string o lista."
                            )
                        regencies[key] = {
                            "cusp_sign": sign_data["sign"],
                            "rulers": rulers,
                        }

            for point_id, data in sorted(points.items()):
                house = house_for_longitude(float(data["longitude"]), houses)
                placements[point_id] = {
                    "house": house,
                    "longitude": float(data["longitude"]),
                }
        else:
            limitations.append(
                f"{subject_id}: no hay doce cúspides fiables; casas y regencias quedan no evaluables."
            )

        if not isinstance(rulership_policy, Mapping):
            limitations.append(
                f"{subject_id}: no se declaró rulership_policy; no se asignan regencias."
            )

        output["subjects"][str(subject_id)] = {
            "timed": bool(chart.get("timed")),
            "point_signs": point_signs,
            "nodes": nodes,
            "angles": angle_context,
            "house_cusps": cusp_context,
            "house_placements": placements,
            "rulerships": regencies,
        }

    return ModuleResult(
        module_id="M04",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"natal_context": output},
        limitations=tuple(limitations),
    )
