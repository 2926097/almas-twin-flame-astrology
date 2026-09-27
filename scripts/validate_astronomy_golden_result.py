#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from almas_tfa.astronomy_golden_validation import evaluate_golden_result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida un resultado dorado astronómico ALMAS contra la política preregistrada."
    )
    parser.add_argument("result", type=Path)
    args = parser.parse_args()

    with args.result.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    evaluation = evaluate_golden_result(payload)
    print(json.dumps(evaluation, ensure_ascii=False, indent=2))
    return 0 if evaluation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
