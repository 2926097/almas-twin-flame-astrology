#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from almas_tfa.astrology_backend import NatalRequest
from almas_tfa.astronomy_golden_validation import (
    evaluate_golden_result,
    load_astronomy_golden_validation_policy,
)
from almas_tfa.production_astronomy import (
    MoiraBackendConfig,
    MoiraProductionBackend,
)
from almas_tfa.skyfield_planetary_reference import (
    REFERENCE_METHOD_ID as PLANETARY_REFERENCE_ID,
    SkyfieldPlanetaryReference,
    SkyfieldReferenceConfig,
)
from almas_tfa.skyfield_true_node_reference import (
    REFERENCE_METHOD_ID as TRUE_NODE_REFERENCE_ID,
    SkyfieldTrueNodeReference,
    SkyfieldTrueNodeReferenceConfig,
)
from almas_tfa.skyfield_placidus_reference import (
    REFERENCE_METHOD_ID as HOUSE_REFERENCE_ID,
    SkyfieldPlacidusReference,
)


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "validation" / "astronomy" / "golden-cases.v1.json"
PLANETARY_FIELDS = {
    "planetary_longitude": "longitude",
    "ecliptic_latitude": "latitude",
    "declination": "declination",
}


def load_cases() -> dict:
    with CASES_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_complete_measurements(
    chart: dict,
    planetary_reference: dict,
    true_node_reference: float,
    house_reference: dict,
    policy: dict,
) -> list[dict]:
    measurements: list[dict] = []

    for metric, field in PLANETARY_FIELDS.items():
        for point_id in policy["required_measurements"][metric]:
            measurements.append(
                {
                    "metric": metric,
                    "point_id": point_id,
                    "implementation_deg": float(
                        chart["positions"][point_id][field]
                    ),
                    "reference_deg": float(
                        planetary_reference[point_id][field]
                    ),
                    "reference_method_id": PLANETARY_REFERENCE_ID,
                }
            )

    measurements.append(
        {
            "metric": "true_node_longitude",
            "point_id": "NORTH_NODE",
            "implementation_deg": float(
                chart["positions"]["NORTH_NODE"]["longitude"]
            ),
            "reference_deg": float(true_node_reference),
            "reference_method_id": TRUE_NODE_REFERENCE_ID,
        }
    )

    for point_id in policy["required_measurements"]["angle_longitude"]:
        measurements.append(
            {
                "metric": "angle_longitude",
                "point_id": point_id,
                "implementation_deg": float(chart["angles"][point_id]),
                "reference_deg": float(house_reference["angles"][point_id]),
                "reference_method_id": HOUSE_REFERENCE_ID,
            }
        )

    for point_id in policy["required_measurements"]["house_cusp_longitude"]:
        measurements.append(
            {
                "metric": "house_cusp_longitude",
                "point_id": point_id,
                "implementation_deg": float(
                    chart["houses"][point_id[1:]]
                ),
                "reference_deg": float(
                    house_reference["houses"][point_id]
                ),
                "reference_method_id": HOUSE_REFERENCE_ID,
            }
        )

    return measurements


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Ejecuta COMPLETE_GATE del backend astronómico ALMAS con las "
            "tres referencias independientes preregistradas."
        )
    )
    parser.add_argument("--kernel", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    policy = load_astronomy_golden_validation_policy()
    artifact = policy["kernel_artifact"]
    if args.sha256 != artifact["sha256"]:
        raise ValueError(
            "El SHA-256 suministrado no coincide con el artefacto preregistrado."
        )

    cases_doc = load_cases()
    if cases_doc["policy_id"] != policy["policy_id"]:
        raise ValueError("Case set y política dorada divergen.")

    backend = MoiraProductionBackend(
        MoiraBackendConfig(
            kernel_path=str(args.kernel),
            kernel_sha256=args.sha256,
            kernel_family="DE440",
            house_system=cases_doc["house_system"],
        )
    )
    planetary_reference_engine = SkyfieldPlanetaryReference(
        SkyfieldReferenceConfig(
            kernel_path=str(args.kernel),
            kernel_sha256=args.sha256,
        )
    )
    true_node_reference_engine = SkyfieldTrueNodeReference(
        SkyfieldTrueNodeReferenceConfig(
            kernel_path=str(args.kernel),
            kernel_sha256=args.sha256,
        )
    )
    house_reference_engine = SkyfieldPlacidusReference()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_cases: list[dict] = []
    any_failure = False

    for case in cases_doc["cases"]:
        request = NatalRequest(
            subject_id=case["case_id"],
            birth_date=case["birth_date"],
            birth_time=case["birth_time"],
            timezone=case["timezone"],
            place=None,
            latitude=float(case["latitude"]),
            longitude=float(case["longitude"]),
            time_reliability="A",
        )
        chart = dict(backend.calculate_natal(request))
        metadata = chart.get("metadata", {})
        jd_ut = metadata.get("jd_ut")
        jd_tt = metadata.get("jd_tt")
        delta_t = metadata.get("delta_t_seconds")
        for name, value in (
            ("jd_ut", jd_ut),
            ("jd_tt", jd_tt),
            ("delta_t_seconds", delta_t),
        ):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise RuntimeError(
                    f"{case['case_id']}: backend sin {name} utilizable."
                )

        planetary_reference = (
            planetary_reference_engine.calculate_at_tt_jd(float(jd_tt))
        )
        true_node_reference = (
            true_node_reference_engine.calculate_at_tt_jd(float(jd_tt))
        )
        house_reference = house_reference_engine.calculate(
            jd_ut=float(jd_ut),
            delta_t_seconds=float(delta_t),
            latitude=float(case["latitude"]),
            longitude=float(case["longitude"]),
        )

        result = {
            "schema_version": "1.0.0",
            "policy_id": policy["policy_id"],
            "case_set_id": cases_doc["case_set_id"],
            "case_id": case["case_id"],
            "validation_stage": "COMPLETE_GATE",
            "backend_provenance": chart["backend_provenance"],
            "reference_provenance": [
                planetary_reference_engine.provenance,
                true_node_reference_engine.provenance,
                house_reference_engine.provenance,
            ],
            "measurements": build_complete_measurements(
                chart,
                planetary_reference,
                true_node_reference,
                house_reference,
                policy,
            ),
        }
        evaluation = evaluate_golden_result(result, policy)
        any_failure = any_failure or evaluation["status"] != "PASS"

        (args.output_dir / f"{case['case_id']}.complete-result.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (args.output_dir / f"{case['case_id']}.complete-evaluation.json").write_text(
            json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        max_by_metric: dict[str, dict] = {}
        for item in evaluation["evaluations"]:
            metric = str(item["metric"])
            delta = float(item["delta_arcsec"])
            current = max_by_metric.get(metric)
            if current is None or delta > float(current["delta_arcsec"]):
                max_by_metric[metric] = {
                    "point_id": item["point_id"],
                    "delta_arcsec": delta,
                    "tolerance_arcsec": float(item["tolerance_arcsec"]),
                    "reference_method_id": item["reference_method_id"],
                    "passed": bool(item["passed"]),
                }

        deltas = [
            float(item["delta_arcsec"])
            for item in evaluation["evaluations"]
        ]
        summary_cases.append(
            {
                "case_id": case["case_id"],
                "status": evaluation["status"],
                "measurement_count": len(evaluation["evaluations"]),
                "max_delta_arcsec": max(deltas) if deltas else None,
                "max_by_metric": max_by_metric,
                "failure_count": len(evaluation["failures"]),
                "failures": list(evaluation["failures"]),
            }
        )

    summary = {
        "policy_id": policy["policy_id"],
        "case_set_id": cases_doc["case_set_id"],
        "validation_stage": "COMPLETE_GATE",
        "kernel_sha256": args.sha256,
        "backend": "moira-astro==6.8.2",
        "references": [
            PLANETARY_REFERENCE_ID,
            TRUE_NODE_REFERENCE_ID,
            HOUSE_REFERENCE_ID,
        ],
        "reference_software": "skyfield==1.55",
        "required_measurements_per_case": 47,
        "status": "FAIL" if any_failure else "PASS",
        "cases": summary_cases,
    }
    (args.output_dir / "complete-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if any_failure else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ALMAS golden complete execution: ERROR: {exc}", file=sys.stderr)
        raise
