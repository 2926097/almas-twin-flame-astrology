from __future__ import annotations

from importlib import resources
import json
from typing import Any, Mapping

POLICY_RESOURCE = "astronomy-golden-validation-policy.json"
POLICY_PACKAGE = "almas_tfa"


def load_astronomy_golden_validation_policy() -> dict[str, Any]:
    resource = resources.files(POLICY_PACKAGE).joinpath("data", POLICY_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("policy_id") != "ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1":
        raise ValueError("Política de validación astronómica dorada desconocida.")
    return policy


def circular_delta_arcsec(a_deg: float, b_deg: float) -> float:
    delta = (float(a_deg) - float(b_deg) + 180.0) % 360.0 - 180.0
    return abs(delta) * 3600.0


def linear_delta_arcsec(a_deg: float, b_deg: float) -> float:
    return abs(float(a_deg) - float(b_deg)) * 3600.0


def tolerance_arcsec(
    metric: str,
    point_id: str,
    policy: Mapping[str, Any],
) -> float:
    table = policy["tolerances_arcsec"].get(metric)
    if table is None:
        raise ValueError(f"Métrica no registrada: {metric}")
    return float(table.get("overrides", {}).get(point_id, table["default"]))


def _required_keys(policy: Mapping[str, Any]) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for metric, points in policy["required_measurements"].items():
        for point_id in points:
            keys.add((metric, point_id))
    return keys


def evaluate_golden_result(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy = dict(policy or load_astronomy_golden_validation_policy())
    required = _required_keys(policy)
    seen: set[tuple[str, str]] = set()
    evaluations: list[dict[str, Any]] = []
    failures: list[str] = []

    for measurement in result.get("measurements", []):
        metric = str(measurement.get("metric", ""))
        point_id = str(measurement.get("point_id", ""))
        key = (metric, point_id)

        if key not in required:
            failures.append(f"UNREGISTERED:{metric}:{point_id}")
            continue
        if key in seen:
            failures.append(f"DUPLICATE:{metric}:{point_id}")
            continue
        seen.add(key)

        implementation = float(measurement["implementation_deg"])
        reference = float(measurement["reference_deg"])
        if metric in {
            "planetary_longitude",
            "true_node_longitude",
            "angle_longitude",
            "house_cusp_longitude",
        }:
            delta = circular_delta_arcsec(implementation, reference)
        else:
            delta = linear_delta_arcsec(implementation, reference)

        tolerance = tolerance_arcsec(metric, point_id, policy)
        passed = delta <= tolerance
        if not passed:
            failures.append(f"OUT_OF_TOLERANCE:{metric}:{point_id}")

        evaluations.append(
            {
                "metric": metric,
                "point_id": point_id,
                "delta_arcsec": delta,
                "tolerance_arcsec": tolerance,
                "passed": passed,
            }
        )

    missing = sorted(required - seen)
    for metric, point_id in missing:
        failures.append(f"MISSING:{metric}:{point_id}")

    return {
        "policy_id": policy["policy_id"],
        "case_id": result.get("case_id"),
        "status": "PASS" if not failures else "FAIL",
        "required_measurement_count": len(required),
        "evaluated_measurement_count": len(seen),
        "failures": failures,
        "evaluations": evaluations,
    }
