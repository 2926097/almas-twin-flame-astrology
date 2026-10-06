#!/usr/bin/env python3
"""Exhaustive disjoint test shards, timings and terminal receipts for CI."""
import argparse
import faulthandler
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
INTEGRATIONS={
    'test_full_pipeline.TestFullPipelineSynthetic.test_m00_m31_complete_with_explicit_inputs',
    'test_return_activation.ReturnsTests.test_complete_pipeline_preserves_core_and_report_gate',
}


def worktree_digest():
    paths=subprocess.run(['git','ls-files','-co','--exclude-standard'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
    digest=hashlib.sha256()
    for name in sorted(set(paths)):
        path=ROOT/name
        digest.update(name.encode()+b'\0')
        digest.update(path.read_bytes() if path.is_file() else b'<deleted>')
        digest.update(b'\0')
    return digest.hexdigest()


def flatten(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from flatten(item)
        else:yield item


class TimedResult(unittest.TextTestResult):
    def startTest(self,test):
        self.started=time.monotonic();super().startTest(test)
    def stopTest(self,test):
        duration=time.monotonic()-self.started
        self.timings.append({'test_id':test.id(),'seconds':round(duration,6)})
        super().stopTest(test)
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.timings=[]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shard',choices=['core','atacires-core','full-pipeline','returns','all'],default='all')
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--diagnostic-interval',type=int,default=0)
    args=parser.parse_args()
    revision=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
    initial_digest=worktree_digest()
    faulthandler.enable()
    # A periodic stack is diagnostic only; it never converts a slow test to PASS.
    if args.diagnostic_interval:
        faulthandler.dump_traceback_later(args.diagnostic_interval,repeat=True)
    tests=list(flatten(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')))
    ids={t.id() for t in tests}
    if not INTEGRATIONS<=ids:raise RuntimeError('Integration shard registry no longer matches discovery')
    target={'full-pipeline':sorted(INTEGRATIONS)[0],'returns':sorted(INTEGRATIONS)[1]}
    selected=[t for t in tests if args.shard=='all' or
              (args.shard=='core' and t.id() not in INTEGRATIONS and not t.id().startswith('test_atacires_')) or
              (args.shard=='atacires-core' and t.id().startswith('test_atacires_')) or
              (args.shard in target and t.id()==target[args.shard])]
    started=time.monotonic()
    result=unittest.TextTestRunner(verbosity=2,resultclass=TimedResult).run(unittest.TestSuite(selected))
    faulthandler.cancel_dump_traceback_later()
    final_digest=worktree_digest()
    receipt=dict(schema_version='ALMAS_TEST_RECEIPT_V1',commit=revision,python=platform.python_version(),
                 worktree_digest=initial_digest,worktree_unchanged=initial_digest==final_digest,
                 shard=args.shard,discovered=len(tests),selected=len(selected),executed=result.testsRun,
                 deselected_test_ids=[t.id() for t in tests if t not in selected],
                 failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],
                 skipped=[{'test_id':t.id(),'reason':reason} for t,reason in result.skipped],
                 seconds=round(time.monotonic()-started,6),timings=result.timings,
                 status='PASS' if result.wasSuccessful() and initial_digest==final_digest else 'FAIL',
                 metaphysical_validation=False)
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0 if receipt['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
