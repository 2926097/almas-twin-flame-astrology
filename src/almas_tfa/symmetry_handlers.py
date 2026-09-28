from __future__ import annotations

from typing import Any, Mapping

from .astrology_geometry import angular_distance, normalize_longitude
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result
from .relational_handlers import _chart_points


def _exactness(orb: float, orb_limit: float) -> float:
    if orb_limit < 0:
        raise ValueError("El orbe no puede ser negativo.")
    if orb_limit == 0:
        return 1.0 if orb == 0 else 0.0
    return max(0.0, 1.0 - (orb / orb_limit) ** 2)


def m05_declinations(context: ModuleContext) -> ModuleResult:
    """M05: paralelos y contra-paralelos entre dos cartas.

    Paralelo: |dec_A - dec_B|.
    Contra-paralelo: |dec_A + dec_B|.
    Los orbes deben declararse en declination_policy.
    """

    natal = context.canonical_snapshot.get("natal")
    if not isinstance(natal, Mapping):
        return not_evaluable_result("M05", "No existe salida natal canónica.")

    charts = natal.get("charts")
    if not isinstance(charts, Mapping) or len(charts) != 2:
        return not_evaluable_result("M05", "M05 requiere exactamente dos cartas.")

    policy = context.raw_input.get("declination_policy")
    if not isinstance(policy, Mapping):
        return not_evaluable_result(
            "M05",
            "Falta declination_policy con orbes declarados.",
        )

    parallel_orb = policy.get("parallel_orb")
    contra_orb = policy.get("contra_parallel_orb")
    if parallel_orb is None and contra_orb is None:
        return not_evaluable_result(
            "M05",
            "declination_policy no declara parallel_orb ni contra_parallel_orb.",
        )

    if parallel_orb is not None:
        parallel_orb = float(parallel_orb)
        if parallel_orb < 0:
            raise ValueError("parallel_orb no puede ser negativo.")
    if contra_orb is not None:
        contra_orb = float(contra_orb)
        if contra_orb < 0:
            raise ValueError("contra_parallel_orb no puede ser negativo.")

    subject_ids = list(charts)
    a_id, b_id = subject_ids
    a_positions = charts[a_id].get("positions") or {}
    b_positions = charts[b_id].get("positions") or {}

    contacts: list[dict[str, Any]] = []
    for a_point, a_data in sorted(a_positions.items()):
        if not isinstance(a_data, Mapping) or a_data.get("declination") is None:
            continue
        dec_a = float(a_data["declination"])

        for b_point, b_data in sorted(b_positions.items()):
            if not isinstance(b_data, Mapping) or b_data.get("declination") is None:
                continue
            dec_b = float(b_data["declination"])

            if parallel_orb is not None:
                orb = abs(dec_a - dec_b)
                if orb <= parallel_orb:
                    contacts.append(
                        {
                            "subject_a": a_id,
                            "point_a": str(a_point),
                            "declination_a": dec_a,
                            "subject_b": b_id,
                            "point_b": str(b_point),
                            "declination_b": dec_b,
                            "relation": "PARALLEL",
                            "orb": orb,
                            "orb_limit": parallel_orb,
                            "exactness": _exactness(orb, parallel_orb),
                        }
                    )

            if contra_orb is not None:
                orb = abs(dec_a + dec_b)
                if orb <= contra_orb:
                    contacts.append(
                        {
                            "subject_a": a_id,
                            "point_a": str(a_point),
                            "declination_a": dec_a,
                            "subject_b": b_id,
                            "point_b": str(b_point),
                            "declination_b": dec_b,
                            "relation": "CONTRA_PARALLEL",
                            "orb": orb,
                            "orb_limit": contra_orb,
                            "exactness": _exactness(orb, contra_orb),
                        }
                    )

    contacts.sort(
        key=lambda x: (x["orb"], x["relation"], x["point_a"], x["point_b"])
    )
    output = {
        "subjects": [a_id, b_id],
        "policy": dict(policy),
        "contacts": contacts,
        "contact_count": len(contacts),
    }

    return ModuleResult(
        module_id="M05",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"declinations": output},
        limitations=(
            "M05 describe relaciones de declinación; no crea por sí sola una raíz ontológica.",
        ),
    )


def antiscion_longitude(longitude: float) -> float:
    """Reflexión sobre el eje solsticial Cáncer-Capricornio."""

    return normalize_longitude(180.0 - float(longitude))


def contra_antiscion_longitude(longitude: float) -> float:
    """Punto opuesto al antiscion."""

    return normalize_longitude(antiscion_longitude(longitude) + 180.0)


def m06_antiscia(context: ModuleContext) -> ModuleResult:
    """M06: contactos de antiscio y contra-antiscio entre dos cartas."""

    natal = context.canonical_snapshot.get("natal")
    if not isinstance(natal, Mapping):
        return not_evaluable_result("M06", "No existe salida natal canónica.")

    charts = natal.get("charts")
    if not isinstance(charts, Mapping) or len(charts) != 2:
        return not_evaluable_result("M06", "M06 requiere exactamente dos cartas.")

    policy = context.raw_input.get("antiscia_policy")
    if not isinstance(policy, Mapping):
        return not_evaluable_result(
            "M06",
            "Falta antiscia_policy con orbes declarados.",
        )

    antiscia_orb = policy.get("antiscia_orb")
    contra_orb = policy.get("contra_antiscia_orb")
    if antiscia_orb is None and contra_orb is None:
        return not_evaluable_result(
            "M06",
            "antiscia_policy no declara antiscia_orb ni contra_antiscia_orb.",
        )

    if antiscia_orb is not None:
        antiscia_orb = float(antiscia_orb)
        if antiscia_orb < 0:
            raise ValueError("antiscia_orb no puede ser negativo.")
    if contra_orb is not None:
        contra_orb = float(contra_orb)
        if contra_orb < 0:
            raise ValueError("contra_antiscia_orb no puede ser negativo.")

    subject_ids = list(charts)
    a_id, b_id = subject_ids
    a_points = _chart_points(charts[a_id])
    b_points = _chart_points(charts[b_id])

    contacts: list[dict[str, Any]] = []
    for a_point, a_data in sorted(a_points.items()):
        lon_a = float(a_data["longitude"])
        ant_lon = antiscion_longitude(lon_a)
        contra_lon = contra_antiscion_longitude(lon_a)

        for b_point, b_data in sorted(b_points.items()):
            lon_b = float(b_data["longitude"])

            if antiscia_orb is not None:
                orb = angular_distance(ant_lon, lon_b)
                if orb <= antiscia_orb:
                    contacts.append(
                        {
                            "subject_a": a_id,
                            "point_a": a_point,
                            "longitude_a": lon_a,
                            "transformed_longitude": ant_lon,
                            "subject_b": b_id,
                            "point_b": b_point,
                            "longitude_b": lon_b,
                            "relation": "ANTISCION",
                            "orb": orb,
                            "orb_limit": antiscia_orb,
                            "exactness": _exactness(orb, antiscia_orb),
                        }
                    )

            if contra_orb is not None:
                orb = angular_distance(contra_lon, lon_b)
                if orb <= contra_orb:
                    contacts.append(
                        {
                            "subject_a": a_id,
                            "point_a": a_point,
                            "longitude_a": lon_a,
                            "transformed_longitude": contra_lon,
                            "subject_b": b_id,
                            "point_b": b_point,
                            "longitude_b": lon_b,
                            "relation": "CONTRA_ANTISCION",
                            "orb": orb,
                            "orb_limit": contra_orb,
                            "exactness": _exactness(orb, contra_orb),
                        }
                    )

    contacts.sort(
        key=lambda x: (x["orb"], x["relation"], x["point_a"], x["point_b"])
    )
    output = {
        "subjects": [a_id, b_id],
        "policy": dict(policy),
        "contacts": contacts,
        "contact_count": len(contacts),
    }

    return ModuleResult(
        module_id="M06",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"antiscia": output},
        limitations=(
            "M06 registra simetrías zodiacales; su peso evidencial se decide en capas posteriores.",
        ),
    )
