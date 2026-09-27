#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from almas_tfa.authored_report import validate_authored_report_trace


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida schema y trazabilidad de un authored_report ALMAS."
    )
    parser.add_argument("authored_report", type=Path)
    parser.add_argument("report_document_model", type=Path)
    parser.add_argument("canonical_analysis", type=Path)
    args = parser.parse_args()

    schema = load(ROOT / "schemas/authored-report.schema.json")
    authored = load(args.authored_report)
    model = load(args.report_document_model)
    canonical = load(args.canonical_analysis)

    Draft202012Validator(schema).validate(authored)
    validate_authored_report_trace(authored, model, canonical)
    print("ALMAS authored report contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
