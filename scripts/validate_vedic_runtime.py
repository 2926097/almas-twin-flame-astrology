"""Reproduce la envolvente sintética, schema y firewall VED."""
from pathlib import Path
import json
from jsonschema import Draft202012Validator
from almas_tfa.vedic.pipeline import run_vedic_pipeline, attach_vedic, render_vedic_report
from almas_tfa.analysis import analyze_precomputed

ROOT = Path(__file__).resolve().parents[1]


def main():
    request=json.loads((ROOT/'examples/vedic-request.synthetic.json').read_text(encoding='utf-8'))
    result=run_vedic_pipeline(request)
    schema=json.loads((ROOT/'schemas/vedic.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result)
    core=analyze_precomputed(dict(pillars=dict(PA=90,PK=80,PE=70,PR=80,PX=60,PT=75,PS=60,PU=40)))
    extended=attach_vedic(core,result)
    assert {k:v for k,v in extended.items() if k!='vedic'}==core
    assert result['shapley']['interpretive_importance'] is False
    assert result['synastry']['ived']['value'] is None
    assert len(result['sensitivity'])==2
    assert result['events'][0]['temporal_independent_root_count']==0
    assert 'INSUFFICIENT' in render_vedic_report(result)
    assert result['synastry']['methodological_readiness']['independence']['status'] == 'NOT_ESTABLISHED'
    assert result['synastry']['methodological_readiness']['ashtakuta']['status'] == 'NOT_EVALUABLE'
    assert result['synastry']['methodological_readiness']['ived']['status'] == 'UNVALIDATED'
    assert result['temporal_readiness']['status'] == 'DESCRIPTIVE_ONLY'
    print('VED: PASS; cartas, cuatro capas D1/D9, eventos, sensibilidad, schema y delta canónico cero. Validación externa NOT_PERFORMED.')


if __name__=='__main__':
    main()
