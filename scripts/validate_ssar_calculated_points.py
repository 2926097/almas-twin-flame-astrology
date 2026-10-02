#!/usr/bin/env python3
"""Reproduce el fixture sintético de puntos calculados sin selección de variante."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from almas_tfa.ssar_calculated_points import validate_calculated_points_result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, default=ROOT / 'examples/ssar-calculated-points.synthetic.json')
    args = parser.parse_args()
    artifact = json.loads(args.fixture.read_text(encoding='utf-8'))
    if artifact.get('synthetic') is not True or artifact.get('scope') != 'DEVELOPMENT_FIXTURE_ONLY':
        raise ValueError('Este verificador exige un fixture sintético de desarrollo.')
    validate_calculated_points_result(artifact['result'], request=artifact['request'])
    print('SSAR fase 6: PASS; eje y dos variantes reproducidos sin selección ni promoción M27.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
