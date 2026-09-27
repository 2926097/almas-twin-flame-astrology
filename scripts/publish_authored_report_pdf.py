#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from almas_tfa.pdf_publication import publish_authored_report_pdf


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publica un authored_report ALMAS como PDF B5 con preflight."
    )
    parser.add_argument("authored_report", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--docx-out", type=Path, default=None)
    parser.add_argument("--receipt", type=Path, default=None)
    parser.add_argument("--soffice", default=None)
    parser.add_argument("--title", default="ALMAS · Informe interpretativo")
    parser.add_argument(
        "--subtitle",
        default="Astrología relacional y hermenéutica metafísica basada en fuentes",
    )
    args = parser.parse_args()

    with args.authored_report.open("r", encoding="utf-8") as handle:
        authored = json.load(handle)

    receipt = publish_authored_report_pdf(
        authored,
        args.output_pdf,
        output_docx=args.docx_out,
        title=args.title,
        subtitle=args.subtitle,
        soffice_path=args.soffice,
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
