#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from almas_tfa.astronomy_golden_runner import generate_backend_observations
from almas_tfa.production_astronomy import (
    MoiraBackendConfig,
    MoiraProductionBackend,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "validation" / "astronomy" / "golden-cases.v1.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera observaciones Moira para los casos dorados preregistrados."
    )
    parser.add_argument("--kernel", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.cases.open("r", encoding="utf-8") as handle:
        case_set = json.load(handle)

    backend = MoiraProductionBackend(
        MoiraBackendConfig(
            kernel_path=str(args.kernel),
            kernel_sha256=args.sha256,
            kernel_family="DE440",
            house_system=str(case_set["house_system"]),
        )
    )

    artifact = generate_backend_observations(case_set, backend)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"ALMAS astronomy backend observations: {artifact['case_count']} cases")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
