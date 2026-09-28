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
from almas_tfa.skyfield_true_node_reference import (
    REFERENCE_METHOD_ID,
    SkyfieldTrueNodeReference,
    SkyfieldTrueNodeReferenceConfig,
)


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "validation" / "astronomy" / "golden-cases.v1.json"


def load_cases() -> dict:
    with CASES_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Ejecuta TRUE_NODE_REFERENCE con Moira y una referencia "
            "Skyfield DE440 de geometría osculadora de primeros principios."
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
    reference = SkyfieldTrueNodeReference(
        SkyfieldTrueNodeReferenceConfig(
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
        jd_tt = chart.get("metadata", {}).get("jd_tt")
        if not isinstance(jd_tt, (int, float)) or isinstance(jd_tt, bool):
            raise RuntimeError(
                f"{case['case_id']}: backend sin recibo jd_tt utilizable."
            )

        reference_longitude = reference.calculate_at_tt_jd(float(jd_tt))
        implementation_longitude = float(
            chart["positions"]["NORTH_NODE"]["longitude"]
        )

        result = {
            "schema_version": "1.0.0",
            "policy_id": policy["policy_id"],
            "case_set_id": cases_doc["case_set_id"],
            "case_id": case["case_id"],
            "validation_stage": "TRUE_NODE_REFERENCE",
            "backend_provenance": chart["backend_provenance"],
            "reference_provenance": [reference.provenance],
            "measurements": [
                {
                    "metric": "true_node_longitude",
                    "point_id": "NORTH_NODE",
                    "implementation_deg": implementation_longitude,
                    "reference_deg": float(reference_longitude),
                    "reference_method_id": REFERENCE_METHOD_ID,
                }
            ],
        }
        evaluation = evaluate_golden_stage(result, policy)
        any_failure = any_failure or evaluation["status"] != "PASS"
        item = evaluation["evaluations"][0] if evaluation["evaluations"] else {}

        (args.output_dir / f"{case['case_id']}.true-node-result.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (args.output_dir / f"{case['case_id']}.true-node-evaluation.json").write_text(
            json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        summary_cases.append(
            {
                "case_id": case["case_id"],
                "status": evaluation["status"],
                "delta_arcsec": item.get("delta_arcsec"),
                "tolerance_arcsec": item.get("tolerance_arcsec"),
                "failure_count": len(evaluation["failures"]),
                "failures": list(evaluation["failures"]),
            }
        )

    summary = {
        "policy_id": policy["policy_id"],
        "case_set_id": cases_doc["case_set_id"],
        "validation_stage": "TRUE_NODE_REFERENCE",
        "kernel_sha256": args.sha256,
        "backend": "moira-astro==6.8.2",
        "reference": REFERENCE_METHOD_ID,
        "reference_software": "skyfield==1.55",
        "status": "FAIL" if any_failure else "PASS",
        "cases": summary_cases,
    }
    (args.output_dir / "true-node-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if any_failure else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ALMAS golden true-node execution: ERROR: {exc}", file=sys.stderr)
        raise
