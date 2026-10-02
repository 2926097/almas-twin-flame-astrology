#!/usr/bin/env python3
"""Reproduce frozen synthetic fixtures, controls, and release policy integrity."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from almas_tfa.ssar_lots import validate_lots_result
from almas_tfa.ssar_pipeline import validate_canonical_ssar,load_frozen_policy
from almas_tfa.ssar_controls import run_ablations,run_synthetic_null
from almas_tfa.ssar_calculated_points import _hash


def main():
    a=json.loads((ROOT/'examples/ssar-lots.synthetic.json').read_text());validate_lots_result(a['result'],request=a['request'])
    a=json.loads((ROOT/'examples/ssar-integrated.synthetic.json').read_text());validate_canonical_ssar(a['result'],request=a['request'],m27_ledger=a['m27_ledger'])
    receipt=json.loads((ROOT/'validation/ssar/controls.synthetic.receipt.json').read_text())
    if _hash(receipt['ablations'])!=_hash(run_ablations(a['request'],core_snapshot=receipt['core_snapshot'],m27_ledger=a['m27_ledger'])):raise ValueError('Ablaciones no reproducidas.')
    for expected in receipt['null_controls']:
        if _hash(expected)!=_hash(run_synthetic_null(a['request'],seed=expected['seed'],simulations=expected['requested_simulations'],core_snapshot=receipt['core_snapshot'],m27_ledger=a['m27_ledger'],method=expected['method'])):raise ValueError('Control no reproducido.')
    manifest=json.loads((ROOT/'manifests/ssar-release-manifest.json').read_text())
    if manifest['evaluation_policy_hash']!=_hash(load_frozen_policy()):raise ValueError('Manifiesto SSAR divergente.')
    print('SSAR 1.25.0: PASS; lotes, canonical, M27, nueve ablaciones y cuatro controles reproducidos. Validación externa NOT_PERFORMED.')
    return 0
if __name__=='__main__':raise SystemExit(main())
