from __future__ import annotations

from typing import Any, Mapping

from .astrology_geometry import match_declared_aspect, normalize_longitude
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .relational_handlers import _chart_points


def m10_individual_draconics(context: ModuleContext) -> ModuleResult:
    """M10: transforma cada carta llevando el nodo norte declarado a 0° Aries."""

    natal = context.canonical_snapshot.get("natal")
    if not isinstance(natal, Mapping):
        return not_evaluable_result("M10", "No existe salida natal canónica.")

    charts = natal.get("charts")
    if not isinstance(charts, Mapping) or len(charts) != 2:
        return not_evaluable_result("M10", "M10 requiere exactamente dos cartas.")

    policy = context.raw_input.get("draconic_policy")
    if not isinstance(policy, Mapping):
        return not_evaluable_result(
            "M10",
            "Falta draconic_policy con node_id y transform declarados.",
        )

    node_id = policy.get("node_id")
    if not isinstance(node_id, str) or not node_id:
        return not_evaluable_result("M10", "draconic_policy.node_id es obligatorio.")

    if policy.get("transform") != "NORTH_NODE_TO_ZERO":
        return not_evaluable_result(
            "M10",
            "La implementación actual requiere transform=NORTH_NODE_TO_ZERO.",
        )

    include_angles = bool(policy.get("include_angles", False))
    include_houses = bool(policy.get("include_houses", False))
    output: dict[str, Any] = {"policy": dict(policy), "charts": {}}
    limitations: list[str] = []

    for subject_id, chart in charts.items():
        if not isinstance(chart, Mapping):
            raise ValueError(f"{subject_id}: carta natal inválida.")

        positions = chart.get("positions")
        if not isinstance(positions, Mapping):
            return not_evaluable_result(
                "M10",
                f"{subject_id}: no existen posiciones natales.",
            )

        node = positions.get(node_id)
        if not isinstance(node, Mapping) or "longitude" not in node:
            return not_evaluable_result(
                "M10",
                f"{subject_id}: no existe el nodo declarado {node_id}.",
            )

        node_longitude = float(node["longitude"])
        d_positions: dict[str, Any] = {}
        for point_id, data in sorted(positions.items()):
            if not isinstance(data, Mapping) or "longitude" not in data:
                continue
            natal_longitude = float(data["longitude"])
            d_positions[str(point_id)] = {
                "longitude": normalize_longitude(natal_longitude - node_longitude),
                "source_longitude": natal_longitude,
                "point_type": data.get("point_type"),
            }

        d_angles: dict[str, float] = {}
        if include_angles:
            angles = chart.get("angles")
            if isinstance(angles, Mapping):
                d_angles = {
                    str(point_id): normalize_longitude(
                        float(longitude) - node_longitude
                    )
                    for point_id, longitude in angles.items()
                }
            else:
                limitations.append(
                    f"{subject_id}: include_angles=true pero no existen ángulos natales."
                )

        d_houses: dict[str, float] = {}
        if include_houses:
            houses = chart.get("houses")
            if isinstance(houses, Mapping) and all(str(i) in houses for i in range(1, 13)):
                d_houses = {
                    str(i): normalize_longitude(
                        float(houses[str(i)]) - node_longitude
                    )
                    for i in range(1, 13)
                }
            else:
                limitations.append(
                    f"{subject_id}: include_houses=true pero no existen doce cúspides natales."
                )

        output["charts"][str(subject_id)] = {
            "node_id": node_id,
            "node_source_longitude": node_longitude,
            "positions": d_positions,
            "angles": d_angles,
            "houses": d_houses,
        }

    return ModuleResult(
        module_id="M10",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"draconic": output},
        limitations=tuple(limitations),
    )


def _cross_contacts(
    chart_a: Mapping[str, Any],
    chart_b: Mapping[str, Any],
    *,
    subject_a: str,
    subject_b: str,
    layer_a: str,
    layer_b: str,
    policy: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    a_points = _chart_points(chart_a)
    b_points = _chart_points(chart_b)
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
                    "subject_a": subject_a,
                    "layer_a": layer_a,
                    "point_a": a_point,
                    "longitude_a": float(a_data["longitude"]),
                    "subject_b": subject_b,
                    "layer_b": layer_b,
                    "point_b": b_point,
                    "longitude_b": float(b_data["longitude"]),
                    **matched,
                }
            )

    contacts.sort(
        key=lambda x: (
            x["orb"],
            x["aspect"],
            x["subject_a"],
            x["point_a"],
            x["subject_b"],
            x["point_b"],
        )
    )
    return contacts


def m11_natal_draconic_cross(context: ModuleContext) -> ModuleResult:
    """M11: cruces natal A↔dracónica B y natal B↔dracónica A."""

    natal = context.canonical_snapshot.get("natal")
    draconic = context.canonical_snapshot.get("draconic")
    if not isinstance(natal, Mapping) or not isinstance(draconic, Mapping):
        return not_evaluable_result(
            "M11",
            "M11 requiere salidas canónicas de M02 y M10.",
        )

    policy = context.raw_input.get("draconic_aspect_policy")
    if not isinstance(policy, Mapping) or not policy:
        return not_evaluable_result(
            "M11",
            "Falta draconic_aspect_policy con orbes declarados.",
        )

    n_charts = natal.get("charts")
    d_charts = draconic.get("charts")
    if not isinstance(n_charts, Mapping) or not isinstance(d_charts, Mapping):
        return not_evaluable_result("M11", "Cartas natales o dracónicas inválidas.")

    subject_ids = list(n_charts)
    if len(subject_ids) != 2 or any(s not in d_charts for s in subject_ids):
        return not_evaluable_result("M11", "M11 requiere dos sujetos coincidentes.")

    a_id, b_id = subject_ids
    contacts = []
    contacts.extend(
        _cross_contacts(
            n_charts[a_id],
            d_charts[b_id],
            subject_a=a_id,
            subject_b=b_id,
            layer_a="NATAL",
            layer_b="DRACONIC",
            policy=policy,
        )
    )
    contacts.extend(
        _cross_contacts(
            n_charts[b_id],
            d_charts[a_id],
            subject_a=b_id,
            subject_b=a_id,
            layer_a="NATAL",
            layer_b="DRACONIC",
            policy=policy,
        )
    )
    contacts.sort(
        key=lambda x: (
            x["orb"],
            x["aspect"],
            x["subject_a"],
            x["point_a"],
            x["subject_b"],
            x["point_b"],
        )
    )

    output = {
        "subjects": subject_ids,
        "policy": dict(policy),
        "contacts": contacts,
        "contact_count": len(contacts),
    }
    return ModuleResult(
        module_id="M11",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"natal_draconic_cross": output},
    )


def m12_draconic_draconic(context: ModuleContext) -> ModuleResult:
    """M12: cruces dracónica↔dracónica como capa corroborativa."""

    draconic = context.canonical_snapshot.get("draconic")
    if not isinstance(draconic, Mapping):
        return not_evaluable_result("M12", "M12 requiere la salida canónica de M10.")

    policy = context.raw_input.get("draconic_aspect_policy")
    if not isinstance(policy, Mapping) or not policy:
        return not_evaluable_result(
            "M12",
            "Falta draconic_aspect_policy con orbes declarados.",
        )

    charts = draconic.get("charts")
    if not isinstance(charts, Mapping) or len(charts) != 2:
        return not_evaluable_result("M12", "M12 requiere dos cartas dracónicas.")

    a_id, b_id = list(charts)
    contacts = _cross_contacts(
        charts[a_id],
        charts[b_id],
        subject_a=a_id,
        subject_b=b_id,
        layer_a="DRACONIC",
        layer_b="DRACONIC",
        policy=policy,
    )

    output = {
        "subjects": [a_id, b_id],
        "policy": dict(policy),
        "contacts": contacts,
        "contact_count": len(contacts),
        "corroborative_only": True,
    }
    return ModuleResult(
        module_id="M12",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"draconic_draconic": output},
        limitations=(
            "La capa dracónica↔dracónica es corroborativa y no es raíz independiente por defecto.",
        ),
    )
