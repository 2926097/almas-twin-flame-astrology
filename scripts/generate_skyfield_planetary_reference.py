#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from almas_tfa.skyfield_reference import (
    generate_skyfield_planetary_reference,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Genera referencias planetarias independientes Skyfield/DE440 "
            "para los casos dorados preregistrados."
        )
    )
    parser.add_argument("--kernel", required=True, type=Path)
    parser.add_argument("--kernel-sha256", required=True)
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path("validation/astronomy/golden-cases.v1.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("validation/astronomy/generated/skyfield"),
    )
    args = parser.parse_args()

    with args.cases.open("r", encoding="utf-8") as handle:
        case_set = json.load(handle)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for case in case_set["cases"]:
        result = generate_skyfield_planetary_reference(
            kernel_path=str(args.kernel),
            expected_kernel_sha256=args.kernel_sha256,
            case=case,
        )
        output = args.output_dir / f'{case["case_id"]}.planetary-reference.json'
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
