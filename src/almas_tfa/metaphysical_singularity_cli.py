"""Ejecución local: python -m almas_tfa.metaphysical_singularity_cli entrada.json -o salida.json."""
import argparse
import json
from pathlib import Path
from .metaphysical_singularity import assess_metaphysical_singularity

def main(argv=None):
    parser=argparse.ArgumentParser(description='PU-M: evaluación experimental de singularidad metafísica')
    parser.add_argument('input',type=Path)
    parser.add_argument('-o','--output',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        result=assess_metaphysical_singularity(json.loads(args.input.read_text(encoding='utf-8')))
    except (ValueError,TypeError,KeyError) as exc:
        parser.exit(2, f'Entrada rechazada: {exc}\n')
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
