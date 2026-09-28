from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from .astrology_backend import AstronomyBackendNotEvaluableError
from .astrology_geometry import match_declared_aspect
from .structural_policies import validate_declared_aspect_policy


TRANSIT_PLANETS = (
    "SUN",
    "MOON",
    "MERCURY",
    "VENUS",
    "MARS",
    "JUPITER",
    "SATURN",
    "URANUS",
    "NEPTUNE",
    "PLUTO",
)

TRANSIT_TARGET_PLANETS = set(TRANSIT_PLANETS)
TRANSIT_TARGET_ANGLES = {"ASC", "MC"}
ALLOWED_TRANSIT_ASPECTS = {
    "CONJUNCTION",
    "SEXTILE",
    "SQUARE",
    "TRINE",
    "OPPOSITION",
}


def _instant_utc(value: Any, request_id: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{request_id}: instant_utc es obligatorio.")
    try:
        instant = datetime.fromisoformat(
            value.strip().replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise ValueError(
            f"{request_id}: instant_utc debe ser ISO-8601."
        ) from exc
    if instant.tzinfo is None:
        raise ValueError(
            f"{request_id}: instant_utc debe incluir offset o Z."
        )
    return instant.astimezone(timezone.utc)


def _target_longitude(
    natal_context: Mapping[str, Any],
    subject_id: str,
    point_id: str,
) -> tuple[float, str] | None:
    subjects = natal_context.get("subjects")
    if not isinstance(subjects, Mapping):
        return None
    subject = subjects.get(subject_id)
    if not isinstance(subject, Mapping):
        return None

    point_id = str(point_id).upper()
    if point_id in TRANSIT_TARGET_PLANETS:
        point_signs = subject.get("point_signs")
        if not isinstance(point_signs, Mapping):
            return None
        data = point_signs.get(point_id)
        if not isinstance(data, Mapping):
            return None
        longitude = data.get("longitude")
        if isinstance(longitude, bool) or not isinstance(
            longitude, (int, float)
        ):
            return None
        return float(longitude) % 360.0, "NATAL"

    if point_id in TRANSIT_TARGET_ANGLES:
        angles = subject.get("angles")
        if not isinstance(angles, Mapping):
            return None
        data = angles.get(point_id)
        if not isinstance(data, Mapping):
            return None
        longitude = data.get("longitude")
        if isinstance(longitude, bool) or not isinstance(
            longitude, (int, float)
        ):
            return None
        return float(longitude) % 360.0, "NATAL_ANGLE"

    return None


def _root_endpoints(
    root: Mapping[str, Any],
    natal_context: Mapping[str, Any],
    target_subjects: set[str] | None,
) -> list[dict[str, Any]]:
    endpoints: dict[tuple[str, str], dict[str, Any]] = {}

    contacts = root.get("concrete_contacts")
    if not isinstance(contacts, list):
        return []

    for contact in contacts:
        if not isinstance(contact, Mapping):
            continue
        for side in ("a", "b"):
            subject_id = str(contact.get(f"subject_{side}") or "").strip()
            point_id = str(contact.get(f"point_{side}") or "").strip().upper()
            layer = str(contact.get(f"layer_{side}") or "").strip().upper()

            if not subject_id or not point_id:
                continue
            if target_subjects is not None and subject_id not in target_subjects:
                continue
            if layer and layer not in {"NATAL", "TROPICAL"}:
                continue

            resolved = _target_longitude(
                natal_context,
                subject_id,
                point_id,
            )
            if resolved is None:
                continue
            longitude, target_layer = resolved
            endpoints[(subject_id, point_id)] = {
                "subject_id": subject_id,
                "point_id": point_id,
                "longitude": longitude,
                "target_layer": target_layer,
            }

    return [
        endpoints[key]
        for key in sorted(endpoints)
    ]


def _structural_family(root: Mapping[str, Any]) -> str:
    families = root.get("dependency_families")
    if isinstance(families, list):
        values = sorted(
            {
                str(value).strip()
                for value in families
                if str(value).strip()
            }
        )
        if values:
            return "+".join(values)
    return "ROOT_ENDPOINT"


def generate_ttransit_signals(
    *,
    requests: Sequence[Mapping[str, Any]],
    canonical: Mapping[str, Any],
    aspect_policy: Mapping[str, Mapping[str, Any]],
    backend: Any,
) -> list[dict[str, Any]]:
    """Genera TTRANSIT sólo sobre endpoints natales de raíces existentes."""

    if not isinstance(requests, Sequence) or isinstance(
        requests, (str, bytes)
    ) or not requests:
        raise ValueError("transit_requests debe ser una lista no vacía.")

    validate_declared_aspect_policy(aspect_policy)
    unknown_aspects = {
        str(name).upper()
        for name in aspect_policy
    } - ALLOWED_TRANSIT_ASPECTS
    if unknown_aspects:
        raise ValueError(
            "TTRANSIT sólo admite aspectos mayores documentados: "
            + ", ".join(sorted(unknown_aspects))
        )

    roots_obj = canonical.get("independent_roots")
    roots = roots_obj.get("roots") if isinstance(roots_obj, Mapping) else None
    if not isinstance(roots, list) or not roots:
        return []

    natal_context = canonical.get("natal_context")
    if not isinstance(natal_context, Mapping):
        return []

    calculate = getattr(backend, "calculate_transit_positions", None)
    if not callable(calculate):
        raise AstronomyBackendNotEvaluableError(
            "El backend configurado no implementa calculate_transit_positions."
        )

    generated: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for index, request in enumerate(requests, start=1):
        if not isinstance(request, Mapping):
            raise ValueError("Cada transit_request debe ser un objeto.")

        request_id = str(
            request.get("request_id") or f"TREQ_{index:04d}"
        ).strip()
        if not request_id:
            raise ValueError("transit_request.request_id no puede estar vacío.")

        instant = _instant_utc(request.get("instant_utc"), request_id)

        preregistered = request.get("preregistered")
        if not isinstance(preregistered, bool):
            raise ValueError(
                f"{request_id}: preregistered debe ser boolean."
            )

        window_rule = request.get("preregistered_window_rule")
        if not isinstance(window_rule, str) or not window_rule.strip():
            raise ValueError(
                f"{request_id}: preregistered_window_rule es obligatorio."
            )

        window_status = request.get("window_status")
        if not isinstance(window_status, str) or not window_status.strip():
            raise ValueError(
                f"{request_id}: window_status es obligatorio."
            )

        target_subjects_raw = request.get("target_subjects")
        target_subjects = None
        if target_subjects_raw is not None:
            if not isinstance(target_subjects_raw, list):
                raise ValueError(
                    f"{request_id}: target_subjects debe ser una lista."
                )
            target_subjects = {
                str(value).strip()
                for value in target_subjects_raw
                if str(value).strip()
            }
            if not target_subjects:
                raise ValueError(
                    f"{request_id}: target_subjects no puede quedar vacío."
                )

        result = calculate(instant)
        positions = result.get("positions") if isinstance(result, Mapping) else None
        if not isinstance(positions, Mapping):
            raise AstronomyBackendNotEvaluableError(
                f"{request_id}: backend TTRANSIT sin positions."
            )

        backend_id = result.get("backend_id")
        backend_version = result.get("backend_version")
        provenance = result.get("backend_provenance")

        for root in roots:
            if not isinstance(root, Mapping):
                continue
            root_id = str(root.get("root_id") or "").strip()
            if not root_id:
                continue

            endpoints = _root_endpoints(
                root,
                natal_context,
                target_subjects,
            )
            if not endpoints:
                continue

            for trigger_point in TRANSIT_PLANETS:
                trigger_data = positions.get(trigger_point)
                if not isinstance(trigger_data, Mapping):
                    continue
                trigger_longitude = trigger_data.get("longitude")
                if isinstance(trigger_longitude, bool) or not isinstance(
                    trigger_longitude, (int, float)
                ):
                    continue

                for endpoint in endpoints:
                    aspect = match_declared_aspect(
                        float(trigger_longitude),
                        float(endpoint["longitude"]),
                        aspect_policy,
                    )
                    if aspect is None:
                        continue

                    aspect_id = str(aspect["aspect"]).upper()
                    signal_id = (
                        "TTRANSIT:"
                        f"{request_id}:{root_id}:{trigger_point}:"
                        f"{endpoint['subject_id']}:{endpoint['point_id']}:"
                        f"{aspect_id}"
                    )
                    if signal_id in seen_ids:
                        continue
                    seen_ids.add(signal_id)

                    generated.append(
                        {
                            "signal_id": signal_id,
                            "root_id": root_id,
                            "clause_id": request.get("clause_id"),
                            "structural_family": _structural_family(root),
                            "temporal_family": "TTRANSIT",
                            "activation_class": "ENDPOINT_ACTIVATION",
                            "strength": float(aspect["exactness"]),
                            "exactitude_orb": float(aspect["orb"]),
                            "preregistered_window_rule": window_rule.strip(),
                            "preregistered": preregistered,
                            "window_status": window_status.strip(),
                            "date_or_period": request.get(
                                "date_or_period",
                                instant.isoformat(),
                            ),
                            "event_refs": list(request.get("event_refs", [])),
                            "trigger_context": {
                                "trigger_point": trigger_point,
                                "target_point": endpoint["point_id"],
                                "relation": aspect_id,
                                "source_layer": "TRANSIT",
                                "target_layer": endpoint["target_layer"],
                                "source_subject": None,
                                "target_subject": endpoint["subject_id"],
                                "orb": float(aspect["orb"]),
                                "orb_limit": float(aspect["orb_limit"]),
                                "aspect_angle": float(aspect["angle"]),
                                "transit_longitude": (
                                    float(trigger_longitude) % 360.0
                                ),
                                "target_longitude": float(
                                    endpoint["longitude"]
                                ),
                                "request_id": request_id,
                                "instant_utc": instant.isoformat(),
                                "backend_id": backend_id,
                                "backend_version": backend_version,
                                "backend_provenance": (
                                    dict(provenance)
                                    if isinstance(provenance, Mapping)
                                    else None
                                ),
                                "method_sources": [
                                    "astrodienst_transit",
                                    "hand_planets_in_transit_2002",
                                ],
                            },
                        }
                    )

    generated.sort(key=lambda item: item["signal_id"])
    return generated
