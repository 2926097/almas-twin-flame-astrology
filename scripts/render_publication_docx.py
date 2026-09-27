#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from almas_tfa.publication_docx import render_publication_docx


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Renderiza un manuscrito ALMAS en DOCX."
    )
    parser.add_argument("manuscript", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--profile",
        choices=("B5_BOOK", "A4_REPORT"),
        default="B5_BOOK",
    )
    args = parser.parse_args()

    with args.manuscript.open("r", encoding="utf-8") as handle:
        manuscript = json.load(handle)

    render_publication_docx(
        manuscript,
        args.output,
        profile=args.profile,
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
