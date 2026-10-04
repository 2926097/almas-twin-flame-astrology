#!/usr/bin/env python3
"""Build and test the wheel outside the checkout, without editable import paths."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='almas-wheel-') as directory:
        destination=Path(directory)
        subprocess.run([sys.executable,'-m','pip','wheel',str(ROOT),'--no-deps','--no-build-isolation',
                        '-w',str(destination)],check=True)
        wheel=next(destination.glob('*.whl'))
        installed=destination/'installed'
        with zipfile.ZipFile(wheel) as archive:
            archive.extractall(installed)
        code='''
import json,sys
from importlib import resources
sys.path.insert(0,sys.argv[1])
sys.path.extend(json.loads(sys.argv[2]))
from almas_tfa.doctrinal_sequence_engine import evaluate_doctrinal_sequence
from almas_tfa.phase_preregistration import verify_phase_preregistration
from almas_tfa.vedic.pipeline import run_vedic_pipeline, attach_vedic
from almas_tfa.vedic.reporting import build_vedic_report_model
from almas_tfa.metaphysical_singularity import assess_metaphysical_singularity
record=json.loads(resources.files('almas_tfa').joinpath('data','phase-preregistration-1.22.0.json').read_text())
assert verify_phase_preregistration(record)['status']=='VERIFIED'
assert evaluate_doctrinal_sequence('TF_PROPHET',[])['ontology_status']=='INSUFFICIENT'
envelope=run_vedic_pipeline({'enabled':False})
assert attach_vedic({'core':1},envelope)['core']==1
assert build_vedic_report_model(envelope)['coverage']['status']=='COMPLETE'
pu=assess_metaphysical_singularity({})
assert pu['PU_O']['state']=='NOT_EVALUABLE' and pu['pu_score'] is None
assert pu['ontology_effect']=='NONE' and pu['production_scores_affected'] is False
print('WHEEL_ISOLATED: PASS; doctrinal registry, frozen bytes, VED schema/reporting and PU-M')
'''
        # The managed runtime exposes installed extras through explicit paths.
        # Retain those dependencies, but exclude every checkout/import path.
        dependencies=[p for p in sys.path if p and not Path(p).resolve().is_relative_to(ROOT)]
        subprocess.run([sys.executable,'-I','-c',code,str(installed),json.dumps(dependencies)],cwd=destination,check=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
