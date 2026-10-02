#!/usr/bin/env python3
"""Validación numérica RRA sobre épocas ficticias, sin calibración personal."""
import argparse,json
from pathlib import Path
from almas_tfa.production_astronomy import MoiraBackendConfig,MoiraProductionBackend
from almas_tfa.skyfield_planetary_reference import SkyfieldReferenceConfig,SkyfieldPlanetaryReference
from almas_tfa.return_solver import ReturnPositionProvider,find_all_return_passes,instant
from almas_tfa.return_activation import load_return_policy,digest
SHA='c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2'
CASES=[('SUN','2020-01-01T00:00:00Z','2020-12-20T00:00:00Z','2021-01-10T00:00:00Z',1),
       ('MOON','2020-01-01T00:00:00Z','2020-01-20T00:00:00Z','2020-02-15T00:00:00Z',1),
       ('VENUS','2020-05-01T00:00:00Z','2020-04-01T00:00:00Z','2020-08-01T00:00:00Z',3)]
def main():
    p=argparse.ArgumentParser();p.add_argument('--kernel',required=True);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    backend=MoiraProductionBackend(MoiraBackendConfig(a.kernel,SHA,'DE440','PLACIDUS'))
    provider=ReturnPositionProvider(backend);reference=SkyfieldPlanetaryReference(SkyfieldReferenceConfig(a.kernel,SHA))
    policy=load_return_policy();rows=[]
    for body,epoch,start,end,expected in CASES:
        target=provider.body(instant(epoch),body)[0]
        solved=find_all_return_passes(provider,body=body,reference_longitude=target,start=start,end=end,policy=policy['activation']['solver'])
        if len(solved['exact_hits'])!=expected:raise AssertionError((body,len(solved['exact_hits']),expected))
        hits=[]
        for hit in solved['exact_hits']:
            chart=backend.calculate_return_chart(instant(hit['exact_datetime']),latitude=0,longitude=0)
            jd_tt=chart['metadata']['jd_tt'];independent=reference.calculate_at_tt_jd(jd_tt)[body]['longitude']
            difference=abs((independent-target+180)%360-180)
            if difference>2/3600:raise AssertionError((body,difference,'Skyfield residual > 2 arcsec'))
            if hit['orb']>policy['activation']['solver']['angular_tolerance_degrees']:raise AssertionError('RRA residual')
            moved=backend.calculate_return_chart(instant(hit['exact_datetime']),latitude=40,longitude=30)
            if chart['positions']!=moved['positions'] or chart['angles']==moved['angles']:raise AssertionError('Relocation invariant')
            hits.append(dict(exact_time=hit['exact_datetime'],motion_state=hit['motion_state'],residual_degrees=hit['orb'],independent_skyfield_residual_degrees=difference))
        rows.append(dict(body=body,reference_epoch=epoch,reference_longitude=target,window=[start,end],expected_passes=expected,hits=hits))
    out=dict(status='PASSED_NUMERICAL_RUNTIME',policy_hash=digest(policy),kernel_sha256=SHA,backend_provenance=provider.snapshot(instant(CASES[0][1]))['backend_provenance'],
        independent_method='Skyfield 1.55 apparent geocentric ecliptic of date at common TT',independent_tolerance_arcseconds=2,cases=rows,personal_cases_used=False,external_relational_validation='NOT_PERFORMED')
    a.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps({'status':out['status'],'cases':len(rows),'passes':sum(len(c['hits']) for c in rows)}))
    return 0
if __name__=='__main__':raise SystemExit(main())
