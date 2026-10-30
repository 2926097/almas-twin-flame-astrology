#!/usr/bin/env python3
"""Auditar un snapshot canónico de ALMAS sin alterar cálculos ni guardar datos privados."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from almas_tfa.methodological_evidence_audit import audit_methodological_evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="JSON canónico local, no se publica")
    args = parser.parse_args()
    try:
        source = json.loads(args.snapshot.read_text(encoding="utf-8"))
        report = audit_methodological_evidence(source)
    except (ValueError, OSError, TypeError) as exc:
        print(f"NOT_EVALUABLE: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
