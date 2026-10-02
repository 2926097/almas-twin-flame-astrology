#!/usr/bin/env python3
"""Comprueba el fixture público sintético de contratos SSAR."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from almas_tfa.ssar import validate_ssar_result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=ROOT / "examples/ssar-contracts.synthetic.json")
    args = parser.parse_args()
    artifact = json.loads(args.fixture.read_text(encoding="utf-8"))
    if artifact.get("synthetic") is not True or artifact.get("scope") != "DEVELOPMENT_FIXTURE_ONLY":
        raise ValueError("Este verificador exige un fixture sintético de desarrollo.")
    validate_ssar_result(artifact["result"], policy=artifact["policy"], request=artifact["request"])
    print("Contrato SSAR: PASS; fixture reproducido, alcance exploratorio y núcleo conservado por diseño.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
