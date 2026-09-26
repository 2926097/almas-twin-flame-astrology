from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .personal_reporting import build_personal_report_model
from .publication import build_publication_plan


def _load(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _dump(value, path: str | None):
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path:
        Path(path).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Construye un plan de publicación ALMAS sin mutar el análisis canónico."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    relational = sub.add_parser("relational")
    relational.add_argument("--canonical", required=True)
    relational.add_argument("--report-model", required=True)
    relational.add_argument("--profile", default="B5_BOOK")
    relational.add_argument("--format", default="PDF", choices=["PLAN", "DOCX", "PDF"])
    relational.add_argument("--available", default="")
    relational.add_argument("--output")

    personal = sub.add_parser("personal")
    personal.add_argument("--canonical", required=True)
    personal.add_argument("--mode", default="FULL_CRITICAL_REPORT")
    personal.add_argument("--profile", default="B5_BOOK")
    personal.add_argument("--format", default="PDF", choices=["PLAN", "DOCX", "PDF"])
    personal.add_argument("--available", default="")
    personal.add_argument("--output")

    args = parser.parse_args()
    canonical = _load(args.canonical)
    available = tuple(x.strip() for x in args.available.split(",") if x.strip())

    if args.command == "relational":
        report_model = _load(args.report_model)
    else:
        report_model = build_personal_report_model(canonical, mode=args.mode)

    plan = build_publication_plan(
        canonical,
        report_model,
        profile_id=args.profile,
        output_format=args.format,
        available_capabilities=available,
    )
    _dump(plan, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
