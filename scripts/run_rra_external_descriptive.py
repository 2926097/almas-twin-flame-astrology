#!/usr/bin/env python3
"""Evalúa un manifiesto RRA descriptivo; no registra ni valida una cohorte real."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from almas_tfa.return_external_evaluation import evaluate_study


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        study = json.loads(args.study.read_text(encoding='utf-8'))
        root = args.study.resolve().parent
        results = {}
        for case in study['cases']:
            path = (root / case['execution_path']).resolve()
            if not path.is_relative_to(root):
                raise ValueError('La ejecución debe pertenecer al directorio del estudio.')
            results[case['case_id']] = json.loads(path.read_text(encoding='utf-8'))
        result = evaluate_study(study, results)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    except (ValueError, KeyError, TypeError, OSError, OverflowError) as error:
        print(f'Evaluación descriptiva RRA: FAIL — {error}', file=sys.stderr)
        return 1
    print('Evaluación descriptiva RRA: PASS — inferencia confirmatoria bloqueada')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
