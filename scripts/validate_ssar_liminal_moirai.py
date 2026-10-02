#!/usr/bin/env python3
"""Reproduce el fixture sintético de liminalidad, Moiras y futuros eventos."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from almas_tfa.ssar_liminal_moirai import validate_liminal_result
from almas_tfa.ssar_process_study import validate_process_study_result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, default=ROOT / 'examples/ssar-liminal-moirai.synthetic.json')
    args = parser.parse_args()
    artifact = json.loads(args.fixture.read_text(encoding='utf-8'))
    if artifact.get('synthetic') is not True or artifact.get('scope') != 'DEVELOPMENT_FIXTURE_ONLY':
        raise ValueError('Este verificador exige un fixture sintético de desarrollo.')
    validate_liminal_result(artifact['result'], request=artifact['request'])
    validate_process_study_result(artifact['study_result'], request=artifact['study_request'])
    print('SSAR fase 5: PASS; dos complejos y estudio documental reproducidos sin promoción M27.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
