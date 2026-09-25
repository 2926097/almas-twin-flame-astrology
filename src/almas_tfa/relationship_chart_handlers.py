from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from .astrology_backend import NatalRequest, natal_request_from_subject
from .astrology_geometry import angular_distance, normalize_longitude
from .module_contract import ExecutionStatus, ModuleContext, ModuleResult, not_evaluable_result


def circular_midpoint(
    a: float,
    b: float,
    *,
    opposition_tie_break: str = "NOT_EVALUABLE",
    tolerance: float = 1e-10,
) -> float | None:
    """Punto medio sobre el arco menor; oposición exacta exige política."""

    a_n = normalize_longitude(a)
    b_n = normalize_longitude(b)
    distance = angular_distance(a_n, b_n)

    if abs(distance - 180.0) <= tolerance:
        if opposition_tie_break == "FORWARD_FROM_A":
            return normalize_longitude(a_n + 90.0)
        if opposition_tie_break == "FORWARD_FROM_B":
            return normalize_longitude(b_n + 90.0)
        if opposition_tie_break == "NOT_EVALUABLE":
            return None
        raise ValueError(
            "opposition_tie_break debe ser NOT_EVALUABLE, FORWARD_FROM_A o FORWARD_FROM_B."
        )

    delta = ((b_n - a_n + 180.0) % 360.0) - 180.0
    return normalize_longitude(a_n + delta / 2.0)


def m07_composite(context: ModuleContext) -> ModuleResult:
    """M07: compuesta de puntos medios sobre posiciones compartidas."""

    natal = context.canonical_snapshot.get("natal")
    if not isinstance(natal, Mapping):
        return not_evaluable_result("M07", "No existe salida natal canónica.")

    charts = natal.get("charts")
    if not isinstance(charts, Mapping) or len(charts) != 2:
        return not_evaluable_result("M07", "M07 requiere exactamente dos cartas.")

    policy = context.raw_input.get("composite_policy")
    if not isinstance(policy, Mapping):
        return not_evaluable_result(
            "M07",
            "Falta composite_policy; el método de punto medio debe declararse.",
        )

    if policy.get("midpoint_mode") != "SHORTEST_ARC":
        return not_evaluable_result(
            "M07",
            "La implementación actual requiere midpoint_mode=SHORTEST_ARC.",
        )

    tie_break = str(policy.get("opposition_tie_break", "NOT_EVALUABLE"))
    subject_ids = list(charts)
    a_id, b_id = subject_ids
    a_chart = charts[a_id]
    b_chart = charts[b_id]

    a_positions = a_chart.get("positions") or {}
    b_positions = b_chart.get("positions") or {}
    shared = sorted(set(a_positions) & set(b_positions))

    positions: dict[str, Any] = {}
    ambiguities: list[str] = []
    for point_id in shared:
        a_data = a_positions[point_id]
        b_data = b_positions[point_id]
        if not isinstance(a_data, Mapping) or not isinstance(b_data, Mapping):
            continue
        if "longitude" not in a_data or "longitude" not in b_data:
            continue

        midpoint = circular_midpoint(
            float(a_data["longitude"]),
            float(b_data["longitude"]),
            opposition_tie_break=tie_break,
        )
        if midpoint is None:
            positions[str(point_id)] = {
                "longitude": None,
                "ambiguous": True,
                "reason": "EXACT_OPPOSITION_WITHOUT_TIE_BREAK",
            }
            ambiguities.append(str(point_id))
        else:
            positions[str(point_id)] = {
                "longitude": midpoint,
                "ambiguous": False,
            }

    angles: dict[str, Any] = {}
    a_angles = a_chart.get("angles")
    b_angles = b_chart.get("angles")
    if isinstance(a_angles, Mapping) and isinstance(b_angles, Mapping):
        for angle_id in sorted(set(a_angles) & set(b_angles)):
            midpoint = circular_midpoint(
                float(a_angles[angle_id]),
                float(b_angles[angle_id]),
                opposition_tie_break=tie_break,
            )
            angles[str(angle_id)] = {
                "longitude": midpoint,
                "ambiguous": midpoint is None,
            }
            if midpoint is None:
                ambiguities.append(f"ANGLE:{angle_id}")

    output = {
        "subjects": [a_id, b_id],
        "policy": dict(policy),
        "positions": positions,
        "angles": angles,
        "ambiguous_points": ambiguities,
        "houses_calculated": False,
    }

    limitations = [
        "M07 calcula puntos medios geométricos; no asigna por sí sola significado ontológico.",
        "Las casas de la compuesta no se calculan en esta fase.",
    ]
    if ambiguities:
        limitations.append(
            "Existen posiciones exactamente opuestas sin una solución de punto medio autorizada."
        )

    return ModuleResult(
        module_id="M07",
        status=ExecutionStatus.COMPLETED,
        payload=output,
        canonical_updates={"composite": output},
        limitations=tuple(limitations),
    )


@dataclass(frozen=True)
class DavisonRequest:
    subject_a: NatalRequest
    subject_b: NatalRequest
    policy: Mapping[str, Any]


class DavisonBackend(Protocol):
    backend_id: str
    backend_version: str

    def calculate_davison(self, request: DavisonRequest) -> Mapping[str, Any]:
        ...


def make_m08_davison(backend: DavisonBackend):
    """Construye M08 para un backend que implemente cálculo Davison."""

    def m08_davison(context: ModuleContext) -> ModuleResult:
        subjects = context.raw_input.get("subjects")
        if not isinstance(subjects, list) or len(subjects) != 2:
            return not_evaluable_result(
                "M08",
                "M08 requiere exactamente dos subjects.",
            )

        policy = context.raw_input.get("davison_policy")
        if not isinstance(policy, Mapping):
            return not_evaluable_result(
                "M08",
                "Falta davison_policy; el método debe quedar registrado.",
            )

        a = natal_request_from_subject(subjects[0])
        b = natal_request_from_subject(subjects[1])

        for subject in (a, b):
            if not subject.timed:
                return not_evaluable_result(
                    "M08",
                    f"{subject.subject_id}: Davison requiere hora, zona y localización.",
                )
            if subject.latitude is None or subject.longitude is None:
                return not_evaluable_result(
                    "M08",
                    f"{subject.subject_id}: se requieren coordenadas numéricas para evitar geocodificación implícita.",
                )

        request = DavisonRequest(subject_a=a, subject_b=b, policy=dict(policy))
        chart = dict(backend.calculate_davison(request))
        chart.setdefault("backend_id", backend.backend_id)
        chart.setdefault("backend_version", backend.backend_version)

        output = {
            "subjects": [a.subject_id, b.subject_id],
            "policy": dict(policy),
            "chart": chart,
        }

        return ModuleResult(
            module_id="M08",
            status=ExecutionStatus.COMPLETED,
            payload=output,
            canonical_updates={"davison": output},
        )

    return m08_davison
