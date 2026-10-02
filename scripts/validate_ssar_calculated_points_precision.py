#!/usr/bin/env python3
"""Compara algoritmos de fase 6 con referencias sobre entradas idénticas."""
from __future__ import annotations

import argparse
from importlib import metadata
import json
from math import atan2, cos, degrees, pi, sin
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from almas_tfa.calculated_points import mean_apogee, osculating_apogee, vertex_axis
from almas_tfa.skyfield_calculated_points import CalculatedPointInputConfig, SkyfieldCalculatedPointInputs


def validate_precision(kernel: Path) -> dict:
    policy = json.loads((ROOT / 'src/almas_tfa/data/ssar-calculated-points-precision-policy.json').read_text())
    for name in ('pyswisseph', 'pyerfa', 'spiceypy', 'skyfield'):
        if metadata.version(name) != policy['references'][name]:
            raise RuntimeError('Versión de referencia no admitida: ' + name)
    import erfa
    import spiceypy
    import swisseph
    if swisseph.version != policy['references']['swisseph']:
        raise RuntimeError('Versión de Swiss Ephemeris no admitida.')
    provider = SkyfieldCalculatedPointInputs(CalculatedPointInputConfig(str(kernel), policy['kernel_sha256']))
    records = []

    def compare(kind, id, actual, expected, inputs):
        delta = abs((actual - expected + 180) % 360 - 180)
        records.append(dict(id=id, point_id=kind, input=inputs, actual_deg=actual, reference_deg=expected,
            delta_deg=delta, tolerance_deg=policy['tolerances_deg'][kind], passed=delta <= policy['tolerances_deg'][kind]))

    eps = policy['vertex_obliquity_deg']
    for latitude in policy['vertex_latitudes_deg']:
        for armc in policy['vertex_armc_deg']:
            reference = swisseph.houses_armc(armc, latitude, eps, b'E')[1][3]
            actual = vertex_axis(armc, latitude, eps)['vertex']
            compare('VERTEX', 'V:' + str(latitude) + ':' + str(armc), actual, reference,
                    dict(armc_deg=armc,latitude_deg=latitude,obliquity_deg=eps))
    for epoch in policy['jd_tt_epochs']:
        t = (epoch - 2451545.0)/36525
        raw_reference = degrees(erfa.faf03(t) + erfa.faom03(t) - erfa.fal03(t)) + 180
        for dpsi in policy['nutation_offsets_deg']:
            compare('BLACK_MOON_MEAN', 'M:' + str(epoch) + ':' + str(dpsi), mean_apogee(epoch,dpsi),
                    (raw_reference+dpsi)%360, dict(jd_tt=epoch,nutation_longitude_deg=dpsi))
        for sample in provider.samples(epoch,41.,0.):
            state = sample['moon_state']
            actual = osculating_apogee(state['position_icrf_km'],state['velocity_icrf_km_s'],
                state['rotation_icrf_to_true_ecliptic'],state['mu_km3_s2'])['longitude']
            elements = spiceypy.oscelt(state['position_icrf_km'] + state['velocity_icrf_km_s'],
                                     0.,state['mu_km3_s2'])
            inc, node, apogee_argument = elements[2], elements[3], elements[4]+pi
            x = cos(node)*cos(apogee_argument)-sin(node)*sin(apogee_argument)*cos(inc)
            y = sin(node)*cos(apogee_argument)+cos(node)*sin(apogee_argument)*cos(inc)
            z = sin(apogee_argument)*sin(inc)
            rotation = state['rotation_icrf_to_true_ecliptic']
            direction = [sum(row[i]*v for i,v in enumerate((x,y,z))) for row in rotation]
            expected = degrees(atan2(direction[1],direction[0]))%360
            compare('BLACK_MOON_OSCULATING','O:'+str(epoch)+':'+str(sample['offset_minutes']),actual,expected,state)
    return dict(policy_id=policy['policy_id'],policy_status='DEVELOPMENT',status='PASS' if all(r['passed'] for r in records) else 'FAIL',
        comparison_scope=policy['scope'],records=records,comparison_count=len(records),input_provenance=provider.provenance,
        references=dict(policy['references'],cspice=spiceypy.tkvrsn('TOOLKIT')),
        maximum_delta_deg={point:max(r['delta_deg'] for r in records if r['point_id']==point) for point in policy['tolerances_deg']},
        kernel_sha256=policy['kernel_sha256'],external_validation_status='NOT_PERFORMED',
        interpretation_validated=False,independent_ephemeris_accuracy_validated=False)


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('No se sobrescribe un recibo de precisión anterior.')
    report=validate_precision(args.kernel)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('SSAR fase 6 precisión: '+report['status']+'; '+str(report['comparison_count'])+' comparaciones sobre entradas idénticas.')
    print(json.dumps(report['maximum_delta_deg'],sort_keys=True))
    return 0 if report['status']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
