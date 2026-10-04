"""CLI JSON: carta, sinastría, temporalidad, pipeline y auditoría."""
import argparse
import json
from pathlib import Path
from .chart import compute_vedic_chart
from .synastry import compute_vedic_synastry
from .timing import compute_vimshottari
from .pipeline import run_vedic_pipeline, render_vedic_report
from .validation import compute_sensitivity, validate_corpus


def main(argv=None):
    parser = argparse.ArgumentParser(prog='almas-vedic', description='Motor Jyotiṣa Relacional observacional')
    parser.add_argument('command', choices=('chart','synastry','timing','events','pipeline','sensitivity','validate','report'))
    parser.add_argument('input', type=Path, help='Entrada JSON; consultar docs/vedic/README.md')
    parser.add_argument('--at', help='Instante ISO con offset para timing')
    parser.add_argument('-o','--output', type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding='utf-8'))
        cfg = data.get('configuration')
        if args.command == 'chart':
            result = compute_vedic_chart(data.get('birth',data), cfg)
        elif args.command == 'synastry':
            result = compute_vedic_synastry(*[compute_vedic_chart(s['birth'],cfg) for s in data['subjects']])
        elif args.command == 'timing':
            if not args.at:
                parser.error('timing requiere --at')
            chart = compute_vedic_chart(data.get('birth',data),cfg)
            result = compute_vimshottari(chart['d1']['Moon']['longitude'],chart['birth'],args.at,chart['configuration']['year_days'])
        elif args.command == 'sensitivity':
            result = compute_sensitivity(data.get('birth',data),cfg)
        elif args.command == 'validate':
            result = validate_corpus(data)
        else:
            result = run_vedic_pipeline(data)
            if args.command == 'report':
                result = render_vedic_report(result)
    except (ValueError, KeyError, TypeError, RuntimeError) as exc:
        parser.error(str(exc))
    rendered = result if isinstance(result,str) else json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    if args.output:
        args.output.write_text(rendered,encoding='utf-8')
    else:
        print(rendered,end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
