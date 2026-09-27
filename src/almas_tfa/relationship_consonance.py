from __future__ import annotations

from itertools import combinations
from typing import Any, Mapping

from .astrology_geometry import match_declared_aspect, zodiac_sign
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result




def _longitude_value(value: Any) -> float | None:
    if isinstance(value, Mapping):
        value = value.get("longitude")
    if value is None:
        return None
    return float(value)


def _zodiac_context(values: Mapping[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for point_id, raw in sorted(values.items()):
        longitude = _longitude_value(raw)
        if longitude is None:
            continue
        item = {
            "longitude": longitude,
            **zodiac_sign(longitude),
        }
        if isinstance(raw, Mapping) and raw.get("point_type") is not None:
            item["point_type"] = raw.get("point_type")
        output[str(point_id)] = item
    return output


def _internal_contacts(
    values: Mapping[str, Any],
    point_ids: list[str],
    aspect_policy: Mapping[str, Mapping[str, Any]],
    *,
    subject_id: str,
) -> list[dict[str, Any]]:
    contacts: list[dict[str, Any]] = []
    available = [
        point_id
        for point_id in point_ids
        if point_id in values and _longitude_value(values.get(point_id)) is not None
    ]
    for point_a, point_b in combinations(available, 2):
        longitude_a = _longitude_value(values[point_a])
        longitude_b = _longitude_value(values[point_b])
        if longitude_a is None or longitude_b is None:
            continue
        match = match_declared_aspect(
            longitude_a,
            longitude_b,
            aspect_policy,
        )
        if match is None:
            continue
        contacts.append(
            {
                "subject_a": subject_id,
                "point_a": point_a,
                "longitude_a": longitude_a,
                "subject_b": subject_id,
                "point_b": point_b,
                "longitude_b": longitude_b,
                **match,
            }
        )

    contacts.sort(
        key=lambda item: (
            item["orb"],
            item["point_a"],
            item["point_b"],
            item["aspect"],
        )
    )
    return contacts


def _field_context(
    composite: Mapping[str, Any],
    davison_chart: Mapping[str, Any],
    point_ids: list[str],
    aspect_policy: Mapping[str, Mapping[str, Any]],
    cross_contact_count: int,
) -> dict[str, Any]:
    composite_positions = composite.get("positions")
    if not isinstance(composite_positions, Mapping):
        composite_positions = {}
    davison_positions = davison_chart.get("positions")
    if not isinstance(davison_positions, Mapping):
        davison_positions = {}

    composite_angles = composite.get("angles")
    if not isinstance(composite_angles, Mapping):
        composite_angles = {}
    davison_angles = davison_chart.get("angles")
    if not isinstance(davison_angles, Mapping):
        davison_angles = {}

    davison_houses = davison_chart.get("houses")
    if not isinstance(davison_houses, Mapping):
        davison_houses = {}

    return {
        "authoring_only": True,
        "structural_evidence_used": False,
        "creates_independent_roots": False,
        "aspect_policy_source": (
            "relationship_chart_consonance_policy.aspect_policy"
        ),
        "point_ids": list(point_ids),
        "composite": {
            "positions": _zodiac_context(composite_positions),
            "angles": _zodiac_context(composite_angles),
            "internal_contacts": _internal_contacts(
                composite_positions,
                point_ids,
                aspect_policy,
                subject_id="RELCHART_COMPOSITE",
            ),
            "houses_calculated": bool(
                composite.get("houses_calculated", False)
            ),
        },
        "davison": {
            "positions": _zodiac_context(davison_positions),
            "angles": _zodiac_context(davison_angles),
            "house_cusps": _zodiac_context(davison_houses),
            "internal_contacts": _internal_contacts(
                davison_positions,
                point_ids,
                aspect_policy,
                subject_id="RELCHART_DAVISON",
            ),
        },
        "cross_consonance_contact_count": int(cross_contact_count),
    }


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
        "field_context": _field_context(
            composite,
            davison_chart,
            point_ids,
            aspect_policy,
            len(contacts),
        ),
    }

    return ModuleResult(
        module_id="M09",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"relationship_chart_consonance": output},
        limitations=(
            "M09 registra geometría compuesta↔Davison dentro de una única familia RELCHART; no existe puntuación de consonancia preregistrada.",
            "field_context es contexto de autoría: sus posiciones, signos y aspectos internos no crean evidencia estructural ni raíces independientes.",
        ),
    )
