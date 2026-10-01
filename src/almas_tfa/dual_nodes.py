"""Capa dual True/Mean Node con eje compartido y procedencia explícita.

El cálculo del Mean Node usa el polinomio secular de Meeus para el nodo
ascendente medio. True y Mean son variantes de un eje nodal común; Norte y Sur
son extremos del mismo eje y nunca se suman como raíces independientes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite
from typing import Any, Mapping

NODE_VARIANTS = ("TRUE", "MEAN")
CONCORDANCE_STATES = (
    "DUAL_CONVERGENCE",
    "TRUE_DOMINANT",
    "MEAN_DOMINANT",
    "DIVERGENT_TIMING",
    "NOT_EVALUABLE",
)
MEAN_NODE_METHOD = "MEEUS_MEAN_ASCENDING_NODE_1998_47_7"


def julian_day(instant: datetime) -> float:
    """Return Julian Day in UT for an aware datetime."""
    if not isinstance(instant, datetime) or instant.tzinfo is None:
        raise ValueError("instant debe ser datetime con zona horaria.")
    utc = instant.astimezone(timezone.utc)
    year, month = utc.year, utc.month
    day = utc.day + (
        utc.hour + (utc.minute + (utc.second + utc.microsecond / 1e6) / 60) / 60
    ) / 24
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    return (
        int(365.25 * (year + 4716))
        + int(30.6001 * (month + 1))
        + day + b - 1524.5
    )


def mean_ascending_node_longitude(instant: datetime) -> float:
    """Mean lunar ascending-node longitude, degrees in [0, 360).

    Meeus, *Astronomical Algorithms*, 2nd ed. (1998), §47, equation 47.7.
    This is an explicit project calculation, not a claim that Mean Node and
    True Node are interchangeable or that either has ontological force.
    """
    t = (julian_day(instant) - 2451545.0) / 36525.0
    longitude = (
        125.0445479
        - 1934.1362891 * t
        + 0.0020754 * t * t
        + (t**3) / 467441.0
        - (t**4) / 60616000.0
    )
    return longitude % 360.0


def mean_ascending_node_longitude_from_jd_tt(jd_tt: float) -> float:
    if isinstance(jd_tt, bool) or not isinstance(jd_tt, (int, float)) or not isfinite(float(jd_tt)):
        raise ValueError("jd_tt debe ser un Julian Day TT finito.")
    t = (float(jd_tt) - 2451545.0) / 36525.0
    return (
        125.0445479 - 1934.1362891 * t + 0.0020754 * t * t
        + t**3 / 467441.0 - t**4 / 60616000.0
    ) % 360.0


def mean_node_speed_degrees_per_day(instant: datetime) -> float:
    """Derivative of the declared Meeus polynomial in degrees per day."""
    t = (julian_day(instant) - 2451545.0) / 36525.0
    derivative_per_century = (
        -1934.1362891
        + 2.0 * 0.0020754 * t
        + 3.0 * t * t / 467441.0
        - 4.0 * t**3 / 60616000.0
    )
    return derivative_per_century / 36525.0


def mean_node_positions(
    instant: datetime | None = None,
    *,
    jd_tt: float | None = None,
) -> dict[str, dict[str, Any]]:
    """Return Mean North/South Node entries with calculation provenance."""
    if (instant is None) == (jd_tt is None):
        raise ValueError("Proporcione exactamente uno entre instant y jd_tt.")
    if jd_tt is None:
        north = mean_ascending_node_longitude(instant)
        speed = mean_node_speed_degrees_per_day(instant)
        epoch = "UTC_INPUT_CONVERTED_TO_JD_UT"
    else:
        north = mean_ascending_node_longitude_from_jd_tt(jd_tt)
        t = (float(jd_tt) - 2451545.0) / 36525.0
        speed = (
            -1934.1362891 + 2.0 * 0.0020754 * t
            + 3.0 * t * t / 467441.0 - 4.0 * t**3 / 60616000.0
        ) / 36525.0
        epoch = "JD_TT"
    shared = {
        "latitude": 0.0,
        "speed": speed,
        "retrograde": speed < 0.0,
        "point_type": "NODE",
        "node_variant": "MEAN",
        "nodal_axis_id": "LUNAR_NODE_AXIS",
        "calculation_method": MEAN_NODE_METHOD,
        "time_scale": epoch,
        "epistemic_class": "A_CALCULATED",
    }
    return {
        "MEAN_NORTH_NODE": {**shared, "longitude": north},
        "MEAN_SOUTH_NODE": {**shared, "longitude": (north + 180.0) % 360.0},
    }


def _longitude(point: Mapping[str, Any], label: str) -> float:
    value = point.get("longitude")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label}.longitude debe ser numérica.")
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{label}.longitude debe ser finita.")
    return value % 360.0


def angular_distance(a: float, b: float) -> float:
    return abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)


def build_dual_node_layer(
    true_north: Mapping[str, Any],
    mean_north: Mapping[str, Any],
    *,
    nodal_axis_id: str = "LUNAR_NODE_AXIS",
) -> dict[str, Any]:
    """Normalize both variants and derive each South Node as its antipode."""
    if not isinstance(nodal_axis_id, str) or not nodal_axis_id.strip():
        raise ValueError("nodal_axis_id debe ser texto no vacío.")
    if not isinstance(true_north, Mapping) or not isinstance(mean_north, Mapping):
        raise ValueError("True y Mean Node deben proporcionarse como objetos.")
    variants: dict[str, Any] = {}
    for variant, source in (("TRUE", true_north), ("MEAN", mean_north)):
        north = _longitude(source, f"{variant}_NORTH_NODE")
        south = (north + 180.0) % 360.0
        variants[variant] = {
            "node_variant": variant,
            "nodal_axis_id": nodal_axis_id,
            "north_node": {"longitude": north, "point_id": "NORTH_NODE"},
            "south_node": {"longitude": south, "point_id": "SOUTH_NODE"},
            "source_point": source.get("source_point", f"{variant}_NORTH_NODE"),
            "calculation_method": source.get("calculation_method"),
        }
    separation = angular_distance(
        variants["TRUE"]["north_node"]["longitude"],
        variants["MEAN"]["north_node"]["longitude"],
    )
    return {
        "nodal_axis_id": nodal_axis_id,
        "variants": variants,
        "variant_separation_degrees": separation,
        "independent_axis_count": 1,
        "north_south_double_counting": False,
        "true_mean_double_counting": False,
        "epistemic_class": "A_CALCULATED",
    }


def classify_nodal_variant_concordance(
    dual_nodes: Mapping[str, Any],
    *,
    target_longitude: float | None = None,
    aspect_angle: float | None = None,
    orb_limit: float | None = None,
) -> dict[str, Any]:
    """Compare timing support only under a caller-declared aspect/orb rule."""
    variants = dual_nodes.get("variants") if isinstance(dual_nodes, Mapping) else None
    if not isinstance(variants, Mapping) or not all(v in variants for v in NODE_VARIANTS):
        return {"status": "NOT_EVALUABLE", "epistemic_class": "B_TECHNIQUE"}
    inputs = (target_longitude, aspect_angle, orb_limit)
    if any(value is None for value in inputs):
        return {
            "status": "NOT_EVALUABLE",
            "reason": "No se declaró un objetivo, aspecto y orbe comparables.",
            "epistemic_class": "B_TECHNIQUE",
        }
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in inputs):
        raise ValueError("objetivo, aspecto y orbe deben ser numéricos.")
    if not isfinite(float(target_longitude)) or not 0.0 <= float(aspect_angle) <= 180.0:
        raise ValueError("target_longitude debe ser finito y aspect_angle estar en [0, 180].")
    if float(orb_limit) < 0:
        raise ValueError("orb_limit no puede ser negativo.")
    residuals: dict[str, float] = {}
    for variant in NODE_VARIANTS:
        longitude = _longitude(variants[variant]["north_node"], variant)
        residuals[variant] = abs(angular_distance(longitude, float(target_longitude)) - float(aspect_angle))
    matches = {key: value <= float(orb_limit) for key, value in residuals.items()}
    if all(matches.values()):
        status = "DUAL_CONVERGENCE"
    elif matches["TRUE"]:
        status = "TRUE_DOMINANT"
    elif matches["MEAN"]:
        status = "MEAN_DOMINANT"
    else:
        status = "DIVERGENT_TIMING"
    return {
        "status": status,
        "residual_orbs": residuals,
        "orb_limit": float(orb_limit),
        "independent_axis_count": 1,
        "epistemic_class": "B_TECHNIQUE",
    }
