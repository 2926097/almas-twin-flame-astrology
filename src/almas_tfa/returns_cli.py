"""Entrada RRA explícita mediante archivos y backend de producción fijado."""
import argparse
import json
from pathlib import Path
from .production_astronomy import MoiraBackendConfig,MoiraProductionBackend
from .return_activation import attach_return_activation,render_ssar_with_returns,validate_return_activation

def main(argv=None):
    parser=argparse.ArgumentParser(description='ALMAS RRA: nueva ejecución sobre raíces y SSAR canónicos existentes')
    parser.add_argument('--request',required=True,type=Path)
    parser.add_argument('--snapshot',required=True,type=Path,help='Snapshot M17 con independent_roots y ssar activo')
    parser.add_argument('--backend-config',required=True,type=Path,help='MoiraBackendConfig JSON con kernel local y SHA-256')
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args(argv)
    read=lambda path:json.loads(path.read_text(encoding='utf-8'))
    backend=MoiraProductionBackend(MoiraBackendConfig(**read(args.backend_config)))
    out=attach_return_activation(read(args.snapshot),read(args.request),backend=backend)
    validate_return_activation(out['ssar']['temporal_activation'],backend=backend)
    text=json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    args.output.write_text(text,encoding='utf-8')
    if args.report:args.report.write_text(render_ssar_with_returns(out)+'\n',encoding='utf-8')
    return 0
if __name__=='__main__':raise SystemExit(main())
