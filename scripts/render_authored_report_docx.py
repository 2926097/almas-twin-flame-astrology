#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from almas_tfa.docx_publication import build_authored_report_docx


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materializa un authored_report ALMAS como DOCX B5."
    )
    parser.add_argument("authored_report", type=Path)
    parser.add_argument("output_docx", type=Path)
    parser.add_argument("--title", default="ALMAS · Informe interpretativo")
    parser.add_argument(
        "--subtitle",
        default="Astrología relacional y hermenéutica metafísica basada en fuentes",
    )
    parser.add_argument("--receipt", type=Path, default=None)
    args = parser.parse_args()

    with args.authored_report.open("r", encoding="utf-8") as handle:
        authored = json.load(handle)

    receipt = build_authored_report_docx(
        authored,
        args.output_docx,
        title=args.title,
        subtitle=args.subtitle,
    )
    payload = receipt.as_dict()
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.receipt is not None:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
