#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from almas_tfa.astrology_backend import NatalRequest
from almas_tfa.astronomy_golden_validation import (
    evaluate_golden_stage,
    load_astronomy_golden_validation_policy,
)
from almas_tfa.production_astronomy import (
    MoiraBackendConfig,
    MoiraProductionBackend,
)
from almas_tfa.skyfield_planetary_reference import (
    REFERENCE_METHOD_ID,
    SkyfieldPlanetaryReference,
    SkyfieldReferenceConfig,
)


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "validation" / "astronomy" / "golden-cases.v1.json"
METRIC_FIELDS = {
    "planetary_longitude": "longitude",
    "ecliptic_latitude": "latitude",
    "declination": "declination",
}


def load_cases() -> dict:
    with CASES_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_measurements(
    implementation: dict,
    reference: dict,
    policy: dict,
) -> list[dict]:
    measurements: list[dict] = []
    for metric in policy["validation_stages"]["PLANETARY_REFERENCE"]:
        field = METRIC_FIELDS[metric]
        for point_id in policy["required_measurements"][metric]:
            measurements.append(
                {
                    "metric": metric,
                    "point_id": point_id,
                    "implementation_deg": float(
                        implementation[point_id][field]
                    ),
                    "reference_deg": float(reference[point_id][field]),
                    "reference_method_id": REFERENCE_METHOD_ID,
                }
            )
    return measurements


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Ejecuta la etapa planetaria real del gate astronómico dorado "
            "con Moira y una referencia independiente Skyfield."
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
    if cases_doc["case_set_id"] != "ALMAS_ASTRONOMY_GOLDEN_CASES_V1":
        raise ValueError("Case set dorado desconocido.")

    backend = MoiraProductionBackend(
        MoiraBackendConfig(
            kernel_path=str(args.kernel),
            kernel_sha256=args.sha256,
            kernel_family="DE440",
            house_system=cases_doc["house_system"],
        )
    )
    reference = SkyfieldPlanetaryReference(
        SkyfieldReferenceConfig(
            kernel_path=str(args.kernel),
            kernel_sha256=args.sha256,
        )
    )

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
        jd_tt = metadata.get("jd_tt")
        if not isinstance(jd_tt, (int, float)) or isinstance(jd_tt, bool):
            raise RuntimeError(
                f"{case['case_id']}: backend sin recibo jd_tt utilizable."
            )

        reference_positions = reference.calculate_at_tt_jd(float(jd_tt))
        result = {
            "schema_version": "1.0.0",
            "policy_id": policy["policy_id"],
            "case_set_id": cases_doc["case_set_id"],
            "case_id": case["case_id"],
            "validation_stage": "PLANETARY_REFERENCE",
            "backend_provenance": chart["backend_provenance"],
            "reference_provenance": [reference.provenance],
            "measurements": build_measurements(
                chart["positions"],
                reference_positions,
                policy,
            ),
        }
        evaluation = evaluate_golden_stage(result, policy)
        any_failure = any_failure or evaluation["status"] != "PASS"

        result_path = (
            args.output_dir / f"{case['case_id']}.planetary-result.json"
        )
        eval_path = (
            args.output_dir / f"{case['case_id']}.planetary-evaluation.json"
        )
        result_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        eval_path.write_text(
            json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        deltas = [
            float(item["delta_arcsec"])
            for item in evaluation["evaluations"]
        ]
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
                    "passed": bool(item["passed"]),
                }
        summary_cases.append(
            {
                "case_id": case["case_id"],
                "status": evaluation["status"],
                "max_delta_arcsec": max(deltas) if deltas else None,
                "max_by_metric": max_by_metric,
                "failure_count": len(evaluation["failures"]),
                "failures": list(evaluation["failures"]),
            }
        )

    summary = {
        "policy_id": policy["policy_id"],
        "case_set_id": cases_doc["case_set_id"],
        "validation_stage": "PLANETARY_REFERENCE",
        "kernel_sha256": args.sha256,
        "backend": "moira-astro==6.8.2",
        "reference": "skyfield==1.55",
        "status": "FAIL" if any_failure else "PASS",
        "cases": summary_cases,
    }
    summary_path = args.output_dir / "planetary-summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if any_failure else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ALMAS golden planetary execution: ERROR: {exc}", file=sys.stderr)
        raise
