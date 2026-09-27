from __future__ import annotations

from typing import Any, Mapping

from .astrology_backend import NatalRequest
from .astronomy_golden_validation import load_astronomy_golden_validation_policy


def extract_backend_measurements(
    chart: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    policy = dict(policy or load_astronomy_golden_validation_policy())
    required = policy["required_measurements"]
    positions = chart.get("positions", {})
    angles = chart.get("angles", {})
    houses = chart.get("houses", {})
    measurements: list[dict[str, Any]] = []

    field_for_metric = {
        "planetary_longitude": "longitude",
        "ecliptic_latitude": "latitude",
        "declination": "declination",
        "true_node_longitude": "longitude",
    }

    for metric in (
        "planetary_longitude",
        "ecliptic_latitude",
        "declination",
        "true_node_longitude",
    ):
        field = field_for_metric[metric]
        for point_id in required[metric]:
            data = positions.get(point_id)
            if not isinstance(data, Mapping) or field not in data:
                raise ValueError(
                    f"Falta observación requerida: {metric}:{point_id}"
                )
            measurements.append(
                {
                    "metric": metric,
                    "point_id": point_id,
                    "value_deg": float(data[field]),
                }
            )

    for point_id in required["angle_longitude"]:
        if point_id not in angles:
            raise ValueError(
                f"Falta observación requerida: angle_longitude:{point_id}"
            )
        measurements.append(
            {
                "metric": "angle_longitude",
                "point_id": point_id,
                "value_deg": float(angles[point_id]),
            }
        )

    for point_id in required["house_cusp_longitude"]:
        number = point_id.removeprefix("H")
        if number not in houses:
            raise ValueError(
                f"Falta observación requerida: house_cusp_longitude:{point_id}"
            )
        measurements.append(
            {
                "metric": "house_cusp_longitude",
                "point_id": point_id,
                "value_deg": float(houses[number]),
            }
        )

    return measurements


def generate_backend_observations(
    case_set: Mapping[str, Any],
    backend: Any,
) -> dict[str, Any]:
    if case_set.get("case_set_id") != "ALMAS_ASTRONOMY_GOLDEN_CASES_V1":
        raise ValueError("Conjunto de casos dorados desconocido.")
    if case_set.get("status") != "PREREGISTERED_INPUTS_ONLY":
        raise ValueError("El conjunto de casos no está en estado preregistrado.")

    cases = case_set.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("El conjunto de casos dorados está vacío.")

    output_cases: list[dict[str, Any]] = []
    shared_provenance: Mapping[str, Any] | None = None

    for case in cases:
        case_id = str(case["case_id"])
        request = NatalRequest(
            subject_id=case_id,
            birth_date=str(case["birth_date"]),
            birth_time=str(case["birth_time"]),
            timezone=str(case["timezone"]),
            place=None,
            latitude=float(case["latitude"]),
            longitude=float(case["longitude"]),
            time_reliability="SYNTHETIC_EXACT",
        )
        chart = backend.calculate_natal(request)
        provenance = chart.get("backend_provenance")
        if not isinstance(provenance, Mapping):
            raise ValueError(f"{case_id}: backend_provenance ausente.")

        if shared_provenance is None:
            shared_provenance = dict(provenance)
        elif dict(provenance) != dict(shared_provenance):
            raise ValueError(
                f"{case_id}: procedencia del backend cambió dentro de la corrida."
            )

        output_cases.append(
            {
                "case_id": case_id,
                "input": {
                    "birth_date": case["birth_date"],
                    "birth_time": case["birth_time"],
                    "timezone": case["timezone"],
                    "latitude": float(case["latitude"]),
                    "longitude": float(case["longitude"]),
                    "house_system": case_set["house_system"],
                },
                "runtime_metadata": dict(chart.get("metadata", {})),
                "measurements": extract_backend_measurements(chart),
            }
        )

    return {
        "schema_version": "1.0.0",
        "artifact_type": "ALMAS_ASTRONOMY_BACKEND_OBSERVATIONS_V1",
        "policy_id": case_set["policy_id"],
        "case_set_id": case_set["case_set_id"],
        "backend_provenance": dict(shared_provenance or {}),
        "case_count": len(output_cases),
        "cases": output_cases,
    }
