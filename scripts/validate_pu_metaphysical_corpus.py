#!/usr/bin/env python3
"""Verifica el corpus público PU-M; opcionalmente coteja los PDF aportados."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate(source_dir=None):
    name = 'metaphysical-singularity-source-map.json'
    registry = json.loads((ROOT/'reference'/name).read_text(encoding='utf-8'))
    packaged = json.loads((ROOT/'src/almas_tfa/data'/name).read_text(encoding='utf-8'))
    if registry != packaged:
        raise ValueError('El registro público y el incluido en el paquete difieren.')
    inventory = json.loads((ROOT/'reference/metaphysical-singularity-corpus-inventory.json').read_text(encoding='utf-8'))
    if inventory['corpus_revision'] != registry['corpus_revision']:
        raise ValueError('Revisiones del corpus incompatibles.')
    if not registry['context_passages_do_not_set_model_requirements']:
        raise ValueError('Los contextos no pueden fijar requisitos de modelos.')
    values = {v['id'] for v in json.loads((ROOT/'reference/metaphysical-singularity-values.json').read_text())['values']}
    documents = {d['file']: d for d in inventory['documents']}
    if len(documents) != len(inventory['documents']) or inventory['pdf_distribution']:
        raise ValueError('Inventario duplicado o distribución de PDF habilitada.')
    if inventory['independent_evidence_count_from_document_count']:
        raise ValueError('El recuento documental no es evidencia independiente.')
    source_ids, passages, groups = set(), {}, set()
    for s in registry['sources']:
        if s['id'] in source_ids:
            raise ValueError('Fuente duplicada.')
        source_ids.add(s['id'])
        if 'passages' not in s:
            continue  # La fuente web Summit anterior conserva su contrato.
        if s['claims'] or s['model_requirements_inferred']:
            raise ValueError('Un contexto nuevo se ha promovido a requisito doctrinal.')
        if s['verification'] != 'PASSAGE_VERIFIED':
            raise ValueError('Fuente no verificada en el registro de pasajes.')
        d = s['document']
        item = documents[d['filename']]
        if d['sha256'] != item['sha256'] or d['page_count'] != item['pages']:
            raise ValueError('Identidad documental incompatible.')
        if d['availability'] != 'USER_PROVIDED_NOT_DISTRIBUTED':
            raise ValueError('Disponibilidad documental no autorizada.')
        if s['dependency_group'] != item['dependency_group']:
            raise ValueError('Dependencia documental incompatible.')
        groups.add(s['dependency_group'])
        if sum(len(p['excerpt'].split()) for p in s['passages']) > 25:
            raise ValueError('La extensión agregada de extractos excede la política breve.')
        for p in s['passages']:
            if p['id'] in passages:
                raise ValueError('Pasaje duplicado.')
            passages[p['id']] = p
            if not isinstance(p['pdf_page'], int) or isinstance(p['pdf_page'], bool) or not 1 <= p['pdf_page'] <= d['page_count']:
                raise ValueError('Página PDF fuera del testigo.')
            if p['verification'] != 'PASSAGE_VERIFIED' or p['origin_effect'] != 'NONE':
                raise ValueError('Estado de verificación o efecto ontológico inválido.')
            if hashlib.sha256(p['excerpt'].encode()).hexdigest() != p['excerpt_sha256']:
                raise ValueError('Huella de extracto incompatible.')
            if not p['excerpt'] or not p['summary_es'] or not p['interpretive_limit']:
                raise ValueError('Pasaje sin texto, resumen o límite.')
            if not p['value_links'] or not set(p['value_links']) <= values:
                raise ValueError('Enlace a valor inexistente.')
        if set(item['passage_refs']) != {p['id'] for p in s['passages']}:
            raise ValueError('Referencias del inventario incompatibles.')
    for d in documents.values():
        if not re.fullmatch('[0-9a-f]{64}', d['sha256']):
            raise ValueError('Huella documental inválida.')
        if not set(d['passage_refs']) <= passages.keys():
            raise ValueError('Referencia documental sin resolver.')
        if source_dir is not None:
            local = Path(source_dir)/d['file']
            if hashlib.sha256(local.read_bytes()).hexdigest() != d['sha256']:
                raise ValueError(f'El testigo local difiere: {d["file"]}')
    for gap in registry['source_gaps']:
        if gap['state'] != 'SOURCE_GAP' or not set(gap['related_passage_refs']) <= passages.keys():
            raise ValueError('Hueco doctrinal promovido o referencia sin resolver.')
        if any(gap['value_id'] not in passages[r]['value_links'] for r in gap['related_passage_refs']):
            raise ValueError('Referencia contextual ajena al valor del hueco.')
    return {'documents':len(documents), 'new_sources':sum('passages' in s for s in registry['sources']),
            'passages':len(passages),'dependency_groups':len(groups),
            'local_pdf_hashes_checked':source_dir is not None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.source_dir)
    except (ValueError, KeyError, OSError) as exc:
        print(f'PU-M corpus: FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
    print('PU-M corpus: PASS')
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
