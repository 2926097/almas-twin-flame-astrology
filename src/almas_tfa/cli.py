from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .analysis import analyze_precomputed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="almas-score",
        description=(
            "Calcula AF/KA/AG/LG a partir de valores de pilares ALMAS precomputados. "
            "Este comando no calcula posiciones astronómicas."
        ),
    )
    parser.add_argument("input", type=Path, help="Archivo JSON de entrada")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Escribe la salida JSON en este archivo en lugar de stdout",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    with args.input.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    result = analyze_precomputed(payload)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"

    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
