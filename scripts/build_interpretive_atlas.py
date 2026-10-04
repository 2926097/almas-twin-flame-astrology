#!/usr/bin/env python3
"""Extraer atlas canónico para cualquier formato de autoría, sin backend astronómico."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from almas_tfa.interpretive_atlas import build_interpretive_atlas, audit_interpretive_coverage


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('-o','--output',type=Path,required=True)
    parser.add_argument('--dispositions',type=Path,help='JSON con disposiciones editoriales para auditar cobertura')
    args=parser.parse_args()
    canonical=json.loads(args.input.read_text(encoding='utf-8'))
    # Admitir archivo canónico directo o envolvente explícita.
    canonical=canonical.get('canonical_analysis',canonical.get('personal_canonical_analysis',canonical))
    if 'document_kind' in canonical or not any(k in canonical for k in ('evidence','natal','natal_context','vedic','relationship_field','draconic_context')):
        parser.error('Se exige un análisis canónico, no un modelo documental o una solicitud bruta.')
    result=build_interpretive_atlas(canonical)
    if args.dispositions:
        result={'atlas':result,'coverage':audit_interpretive_coverage(canonical,result,json.loads(args.dispositions.read_text(encoding='utf-8')))}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return 0

if __name__=='__main__': raise SystemExit(main())
