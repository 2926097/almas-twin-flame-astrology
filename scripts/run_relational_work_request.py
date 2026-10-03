#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from almas_tfa.production_astronomy import (
    MoiraBackendConfig,
    MoiraProductionBackend,
)
from almas_tfa.relational_execution import (
    execute_relational_work_request,
)
from almas_tfa.relational_request_pipeline import (
    assess_relational_work_request,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "manifests" / "analysis-pipeline-manifest.json"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: se esperaba un objeto JSON.")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(
            value,
            handle,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        handle.write("\n")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Ejecuta un ALMAS_WORK_REQUEST relacional de forma local "
            "y materializa el canonical únicamente si M30 lo produce."
        )
    )
    parser.add_argument("request", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
    )
    parser.add_argument(
        "--assessment-only",
        action="store_true",
        help="Valida/adapta la solicitud sin inicializar astronomía.",
    )
    parser.add_argument("--kernel-path", type=Path)
    parser.add_argument("--kernel-sha256")
    parser.add_argument(
        "--kernel-family",
        choices=("DE430", "DE440", "DE441"),
    )
    parser.add_argument("--house-system")
    return parser


def main() -> int:
    args = _parser().parse_args()
    request = _load_json(args.request)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    assessment = assess_relational_work_request(request)
    _write_json(
        args.output_dir / "request_assessment.json",
        assessment,
    )

    if args.assessment_only:
        print(
            "ALMAS relational assessment: "
            + (
                "READY_FOR_RAW_INPUT"
                if assessment["ready_for_raw_input"]
                else "INCOMPLETE"
            )
        )
        return 0 if assessment["ready_for_raw_input"] else 2

    missing_backend_args = [
        name
        for name, value in (
            ("--kernel-path", args.kernel_path),
            ("--kernel-sha256", args.kernel_sha256),
            ("--kernel-family", args.kernel_family),
            ("--house-system", args.house_system),
        )
        if value is None
    ]
    if missing_backend_args:
        raise SystemExit(
            "Faltan argumentos del backend de producción: "
            + ", ".join(missing_backend_args)
        )

    manifest = _load_json(args.manifest)
    config = MoiraBackendConfig(
        kernel_path=str(args.kernel_path),
        kernel_sha256=str(args.kernel_sha256),
        kernel_family=str(args.kernel_family),
        house_system=str(args.house_system),
    )
    backend = MoiraProductionBackend(config)

    result = execute_relational_work_request(
        request,
        manifest,
        astrology_backend=backend,
        davison_backend=backend,
        stop_on_failure=False,
    )

    _write_json(args.output_dir / "raw_input.json", result["raw_input"])
    _write_json(
        args.output_dir / "orchestration_run.json",
        result["orchestration_run"],
    )
    _write_json(
        args.output_dir / "execution_receipt.json",
        result["execution_receipt"],
    )

    canonical = result["canonical_analysis"]
    if isinstance(canonical, dict):
        _write_json(
            args.output_dir / "canonical_analysis.json",
            canonical,
        )
        print("ALMAS canonical_analysis.json: CREATED")
    else:
        print("ALMAS canonical_analysis.json: NOT_CREATED")

    receipt = result["execution_receipt"]
    if receipt["failed_modules"]:
        print(
            "FAILED modules: "
            + ", ".join(receipt["failed_modules"]),
            file=sys.stderr,
        )
        return 3
    if canonical is None:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
