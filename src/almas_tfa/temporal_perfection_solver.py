"""Numerical solver for multiple astrological aspect perfections.

The solver is technique-agnostic: each technique supplies an evaluator that
returns geocentric/ecliptic longitudes at an aware UTC datetime. Progressions,
directions and atacires must therefore supply their own declared time map.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import isfinite, remainder
from typing import Any, Callable

LongitudeEvaluator = Callable[[datetime], tuple[float, float]]
ContextEvaluator = Callable[[datetime], dict[str, Any]]


def signed_angle_error(source: float, target: float, aspect_angle: float) -> float:
    """Signed shortest angular residual for an oriented aspect perfection."""
    error = remainder(float(target) - float(source) - float(aspect_angle), 360.0)
    return -180.0 if error == 180.0 else error


def _to_utc(value: datetime, label: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError(f"{label} debe ser datetime timezone-aware.")
    return value.astimezone(timezone.utc)


def _bisect_root(fn: Callable[[datetime], float], left: datetime, right: datetime,
                 tolerance_seconds: float) -> datetime:
    fl, fr = fn(left), fn(right)
    if fl == 0.0:
        return left
    if fr == 0.0:
        return right
    if fl * fr > 0:
        raise ValueError("El intervalo no encierra una raíz.")
    while (right - left).total_seconds() > tolerance_seconds:
        mid = left + (right - left) / 2
        fm = fn(mid)
        if fm == 0.0:
            return mid
        if fl * fm <= 0:
            right, fr = mid, fm
        else:
            left, fl = mid, fm
    return left + (right - left) / 2


def _golden_min_abs(fn: Callable[[datetime], float], left: datetime,
                    right: datetime, tolerance_seconds: float) -> tuple[datetime, float]:
    ratio = (5**0.5 - 1) / 2
    x1 = right - (right - left) * ratio
    x2 = left + (right - left) * ratio
    f1, f2 = abs(fn(x1)), abs(fn(x2))
    while (right - left).total_seconds() > tolerance_seconds:
        if f1 <= f2:
            right, x2, f2 = x2, x1, f1
            x1 = right - (right - left) * ratio
            f1 = abs(fn(x1))
        else:
            left, x1, f1 = x1, x2, f2
            x2 = left + (right - left) * ratio
            f2 = abs(fn(x2))
    point = x1 if f1 <= f2 else x2
    return point, min(f1, f2)


def solve_aspect_perfections(
    evaluator: LongitudeEvaluator,
    *,
    start: datetime,
    end: datetime,
    aspect_angle: float,
    technique: str,
    technique_variant: str,
    source_point: str,
    target_point: str,
    relation: str | None = None,
    dependency_group: str | None = None,
    node_variant: str | None = None,
    nodal_axis_id: str | None = None,
    window_status: str = "EXPLORATORY",
    context_evaluator: ContextEvaluator | None = None,
    step_seconds: float = 21600.0,
    time_tolerance_seconds: float = 1.0,
    angular_tolerance_degrees: float = 1e-5,
    max_samples: int = 2_000_000,
) -> dict[str, Any]:
    """Find all direct and reverse-orientation perfections in a closed window.

    Sign-changing roots are bisected. Stationary/tangent contacts are searched
    by minimizing absolute angular error in sampled local-minimum brackets.
    All tolerances and sampling choices are returned for auditability.
    """
    start, end = _to_utc(start, "start"), _to_utc(end, "end")
    if end <= start:
        raise ValueError("end debe ser posterior a start.")
    if not callable(evaluator):
        raise ValueError("evaluator debe ser callable.")
    for name, value in (("step_seconds", step_seconds),
                        ("time_tolerance_seconds", time_tolerance_seconds),
                        ("angular_tolerance_degrees", angular_tolerance_degrees)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)) or value <= 0:
            raise ValueError(f"{name} debe ser un número finito positivo.")
    if isinstance(aspect_angle, bool) or not isinstance(aspect_angle, (int, float)) or not 0 <= aspect_angle <= 180:
        raise ValueError("aspect_angle debe estar entre 0 y 180 grados.")
    if not technique or not technique_variant or not source_point or not target_point:
        raise ValueError("Técnica, variante y puntos son obligatorios.")
    if technique == "TTRANSIT" and technique_variant == "RETURN_CYCLE":
        body = lambda point: point.upper().replace("_TRANSIT", "").replace("_NATAL", "")
        if body(source_point) != body(target_point):
            raise ValueError("RETURN_CYCLE requiere el mismo cuerpo transitante y natal.")
    if node_variant not in {None, "TRUE", "MEAN"}:
        raise ValueError("node_variant debe ser TRUE, MEAN o null.")
    if node_variant and not nodal_axis_id:
        nodal_axis_id = "LUNAR_NODE_AXIS"
    if window_status not in {"RETROSPECTIVE_CONFIRMED", "RETROSPECTIVE_UNCONFIRMED", "CURRENT_ACTIVE", "PROSPECTIVE_ACTIVATION", "EXPLORATORY", "UNANCHORED"}:
        raise ValueError("window_status no reconocido.")
    if dependency_group is None:
        if technique == "TTRANSIT":
            dependency_group = "TRANSIT_EPHEMERIS"
        elif technique == "TDIR":
            dependency_group = "UNIFORM_YEAR_DIRECTION"
        elif technique == "TATACIR":
            dependency_group = "ATACIR_FAMILY"
        elif technique == "TPROG" and technique_variant.startswith("SECONDARY_"):
            dependency_group = "SEC_PROGRESSION"
        elif technique == "TPROG" and technique_variant.startswith("TERTIARY_"):
            dependency_group = "TERTIARY_LUNAR"
        else:
            dependency_group = f"TEMPORAL_FAMILY:{technique}"
    count = int((end - start).total_seconds() // float(step_seconds)) + 1
    if count + 1 > max_samples:
        raise ValueError("La ventana supera max_samples; aumente step_seconds explícitamente.")
    times = [start + timedelta(seconds=i * float(step_seconds)) for i in range(count + 1)]
    if times[-1] < end:
        times.append(end)
    elif times[-1] > end:
        times[-1] = end

    aspects = [float(aspect_angle)]
    reverse = (360.0 - float(aspect_angle)) % 360.0
    if reverse not in aspects and reverse not in (0.0, 180.0):
        aspects.append(reverse)
    roots: list[tuple[datetime, float]] = []
    for oriented_aspect in aspects:
        cache: dict[datetime, float] = {}
        def residual(when: datetime) -> float:
            if when not in cache:
                pair = evaluator(when)
                if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                    raise ValueError("evaluator debe devolver (source_lon, target_lon).")
                a, b = pair
                if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(float(v)) for v in pair):
                    raise ValueError("evaluator devolvió longitud no finita o no numérica.")
                cache[when] = signed_angle_error(float(a), float(b), oriented_aspect)
            return cache[when]

        values = [residual(when) for when in times]
        candidates: list[datetime] = []
        for i in range(len(times) - 1):
            if values[i] == 0.0:
                candidates.append(times[i])
            elif values[i] * values[i + 1] < 0.0:
                # signed-angle normalization is discontinuous at ±180°; that
                # branch cut is not an aspect perfection.
                if abs(values[i] - values[i + 1]) >= 180.0:
                    continue
                candidates.append(_bisect_root(residual, times[i], times[i + 1], float(time_tolerance_seconds)))
        if values[-1] == 0.0:
            candidates.append(times[-1])
        for i in range(1, len(times) - 1):
            if abs(values[i]) <= abs(values[i - 1]) and abs(values[i]) <= abs(values[i + 1]):
                candidate, error = _golden_min_abs(residual, times[i - 1], times[i + 1], float(time_tolerance_seconds))
                if error <= float(angular_tolerance_degrees):
                    candidates.append(candidate)
        roots.extend((candidate, oriented_aspect) for candidate in candidates)

    roots.sort(key=lambda item: item[0])
    deduplicated: list[tuple[datetime, float]] = []
    for root in roots:
        if deduplicated and abs((root[0] - deduplicated[-1][0]).total_seconds()) <= float(time_tolerance_seconds) * 2:
            if abs(signed_angle_error(*evaluator(root[0]), root[1])) < abs(signed_angle_error(*evaluator(deduplicated[-1][0]), deduplicated[-1][1])):
                deduplicated[-1] = root
        else:
            deduplicated.append(root)

    exact_hits = []
    for index, (when, oriented_aspect) in enumerate(deduplicated, start=1):
        kinematics = dict(context_evaluator(when)) if context_evaluator else {}
        if context_evaluator and not isinstance(kinematics, dict):
            raise ValueError("context_evaluator debe devolver un objeto.")
        exact_hits.append({
            "exact_datetime": when.isoformat().replace("+00:00", "Z"),
            "orb": abs(signed_angle_error(*evaluator(when), oriented_aspect)),
            "applying_or_separating": "EXACT_PERFECTION",
            "pass_number": index,
            "station_context": kinematics.get("station_context", "UNASSESSED"),
            "motion_state": kinematics.get("motion_state", "EVALUATOR_DEFINED"),
            "source_point": source_point,
            "target_point": target_point,
            "relation": relation or f"ASPECT_{float(aspect_angle):g}",
            "oriented_aspect": oriented_aspect,
            "technique": technique,
            "technique_variant": technique_variant,
            "window_status": window_status,
            "date_or_period": when.date().isoformat(),
            "dependency_group": dependency_group,
            **({"node_variant": node_variant, "nodal_axis_id": nodal_axis_id} if node_variant else {}),
            **{key: kinematics[key] for key in ("applying_or_separating", "motion_state", "station_context") if key in kinematics},
        })
    return {
        "status": "READY" if exact_hits else "NO_PERFECTION_FOUND",
        "exact_hits": exact_hits,
        "solver": "BRACKETED_ROOTS_PLUS_STATIONARY_MINIMA",
        "time_scale": "UTC",
        "time_tolerance_seconds": float(time_tolerance_seconds),
        "angular_tolerance_degrees": float(angular_tolerance_degrees),
        "sampling_step_seconds": float(step_seconds),
        "samples_evaluated": len(times),
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "technique": technique,
        "technique_variant": technique_variant,
        "source_point": source_point,
        "target_point": target_point,
        "relation": relation or f"ASPECT_{float(aspect_angle):g}",
        "dependency_group": dependency_group,
        "node_variant": node_variant,
        "epistemic_class": "B_TECHNIQUE",
        "creates_structural_root": False,
        "predicts_real_world_event": False,
    }
