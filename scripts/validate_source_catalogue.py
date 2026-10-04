#!/usr/bin/env python3
"""Check catalogue integrity without redistributing local copyrighted sources."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    data=json.loads((ROOT/'reference/attached-source-catalogue.json').read_text())
    entries=data['entries']
    assert len(entries)==data['files']==19
    assert len({e['dependency_family'] for e in entries})==data['work_dependency_families']==18
    assert len({e['id'] for e in entries})==19
    assert entries[1]['dependency_family']==entries[5]['dependency_family']
    assert entries[0]['author']!=entries[4]['author']
    assert entries[2]['author']=='Noel Langley'
    assert entries[11]['author']=='Harry B. Joseph'
    assert entries[14]['author']=='Liz Greene'
    for e in entries:
        assert len(e['sha256'])==len(e['passage']['extracted_text_sha256'])==64
        assert 1<=e['passage']['pdf_page']<=e['pdf_page_count']
        assert all(1<=p<=e['pdf_page_count'] for p in e['identity_pdf_pages'])
        assert not e['full_text_doctrinal_review'] and not e['canonical_effect']
        assert e['external_validation']=='NOT_PERFORMED'
        assert e['ontological_discrimination']=='INSUFFICIENT'
    registry=json.loads((ROOT/'reference/source-registry.json').read_text())['entries']
    gaps={e['id'] for e in registry if not(e.get('passage') or e.get('pages') or e.get('verification_anchor'))}
    assert {e['source_id'] for e in data['existing_registry_locator_gaps']}==gaps
    print(f'CATALOGUE: PASS; {len(entries)} files, 18 dependency families, {len(gaps)} registry locator gaps')


if __name__=='__main__':main()
