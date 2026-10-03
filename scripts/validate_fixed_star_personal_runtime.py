#!/usr/bin/env python3
"""Reproduce la capa personal de estrellas sobre una época de prueba."""
import argparse
import json
from pathlib import Path

from almas_tfa.personal_request_pipeline import build_personal_report_context_from_request
from almas_tfa.personal_fixed_stars import render_personal_fixed_stars
from almas_tfa.production_astronomy import MoiraBackendConfig, MoiraProductionBackend
from almas_tfa.return_activation import digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kernel', required=True)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    backend = MoiraProductionBackend(MoiraBackendConfig(a.kernel,
        'c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2', 'DE440', 'PLACIDUS'))
    request = dict(schema_version='1.0.0', report_profile='FULL_CRITICAL_REPORT',
        fixed_stars=dict(enabled=True), subject=dict(id='SYNTHETIC_RUNTIME',
        birth_date='2020-01-01', birth_time='12:00', timezone='UTC', place='Synthetic',
        latitude=0, longitude=0, time_reliability='A', birth_time_source_class='DOCUMENTARY'))
    context = build_personal_report_context_from_request(request, backend)
    canonical = context['personal_canonical_analysis']; layer = canonical['secondary_layers']['fixed_stars']
    from jsonschema import Draft202012Validator
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / 'schemas/personal-fixed-star-paran.schema.json').read_text())
    Draft202012Validator(schema).validate(layer)
    narrative = render_personal_fixed_stars(layer)
    receipt = dict(status='PASSED_PERSONAL_RUNTIME', epoch='SYNTHETIC_TEST_ONLY',
                   policy_sha256=layer['policy_fingerprint_sha256'],
                   kernel_sha256=backend.provenance['kernel_sha256'],
                   canon_sha256=layer['canon']['fingerprint_sha256'],
                   stars=len(layer['fixed_stars']), parans=len(layer['parans']),
                   angular_contacts=len(layer['natal_angular_contacts']),
                   canonical_sha256=digest(canonical), narrative_sha256=digest(narrative),
                   personal_data_minimized=True, structural_role='SUPPORT_ONLY',
                   external_astrological_validation='NOT_PERFORMED')
    a.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__': main()
