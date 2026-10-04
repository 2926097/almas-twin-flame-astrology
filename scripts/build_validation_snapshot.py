#!/usr/bin/env python3
"""Current counts and explicit verification layers; historic releases stay separate."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def flatten(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from flatten(item)
        else:yield item


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt',action='append',type=Path,default=[])
    parser.add_argument('-o','--output',required=True,type=Path)
    args=parser.parse_args()
    registry=json.loads((ROOT/'reference/source-registry.json').read_text())['entries']
    tests=list(flatten(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')))
    known={t.id() for t in tests};receipts=[json.loads(p.read_text()) for p in args.receipt]
    executed={row['test_id'] for r in receipts for row in r.get('timings',[])}
    dirty=bool(subprocess.run(['git','status','--porcelain'],cwd=ROOT,capture_output=True,text=True,check=True).stdout)
    result=dict(schema_version='ALMAS_VALIDATION_SNAPSHOT_V1',generated_at=datetime.now(timezone.utc).isoformat(),
                version=(ROOT/'VERSION').read_text().strip(),python=platform.python_version(),
                commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
                tracked_worktree_modified=dirty,sources=len(registry),source_verification=dict(Counter(x['verification_status'] for x in registry)),
                sources_without_passage_locator=[x['id'] for x in registry if not(x.get('passage') or x.get('pages') or x.get('verification_anchor'))],
                tests_discovered=len(tests),test_receipts=receipts,
                missing_test_ids=sorted(known-executed),unknown_test_ids=sorted(executed-known),
                local_suite_state='PASS' if receipts and known==executed and all(r['status']=='PASS' for r in receipts) else 'NOT_FULLY_VERIFIED',
                verification_layers=dict(distribution='SEE_DISTRIBUTION_GATE',contract='SEE_PUBLIC_CONTRACT_GATE',
                    astronomy='SEE_BACKEND_WORKFLOW',publication='SEE_DOCX_PDF_WORKFLOWS',empirical='NOT_PERFORMED',
                    metaphysical_probabilities=False))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Snapshot: {len(tests)} tests, {len(registry)} sources, suite {result['local_suite_state']}")
    return 0


if __name__=='__main__':raise SystemExit(main())
