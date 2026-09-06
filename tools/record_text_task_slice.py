#!/usr/bin/env python3
"""Record the fixed donor suite additively; never update an engineering selector."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile
import text_task_qualification as Q

ROOT=Path(__file__).resolve().parents[1]
_collected=[]
_reports=[]


# Loaded only by the registered pytest child; records collection plus actual call phases.
def pytest_collection_finish(session):
    _collected.extend(item.nodeid for item in session.items)


def pytest_runtest_logreport(report):
    _reports.append({'nodeid':report.nodeid,'when':report.when,'outcome':report.outcome})


def pytest_sessionfinish(session,exitstatus):
    path=Path(os.environ['OCM_TEXT_TASK_TRACE'])
    write(path,{'collected':_collected,'reports':_reports,'exit_status':int(exitstatus)})


def write(path,value):
    with Path(path).open('xb') as out:out.write(Q.encoded(value)+b'\n')


def execute(argv,root,env,stdout,stderr):
    return subprocess.run(argv,cwd=root,env=env,stdout=stdout,stderr=stderr,check=False).returncode


def record(root,output,expected_source_id):
    root=Path(root).resolve();output=Path(output).resolve();before=Q.snapshot(root)
    if Q.identity(before)!=expected_source_id:raise ValueError('frozen qualification source identity changed')
    if any(output.is_relative_to(root/p) for p in ('src','tests','tools',Q.PROTO)):
        raise ValueError('qualification output must be outside bound source directories')
    output.mkdir(parents=True,exist_ok=False)
    write(output/'SOURCE.json',before)
    argv=[sys.executable,'-m','pytest','-p','record_text_task_slice','-o','addopts=',
          *Q.TESTS,'-q','--junitxml='+str(output/'junit.xml'),'--basetemp='+str(output/'temporary-state')]
    env=dict(os.environ)
    for key in ('PYTEST_ADDOPTS','PYTHONPATH','PYTHONHOME'):env.pop(key,None)
    env.update(PYTHONPATH=os.pathsep.join((str(root/'src'),str(root/'tools'))),
               PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',PYTHONDONTWRITEBYTECODE='1',
               OCM_TEXT_TASK_TRACE=str(output/'pytest-trace.json'))
    write(output/'LAUNCH.json',{'argv':argv,'cwd':str(root),'source_id':expected_source_id,
          'environment_overrides':{k:env[k] for k in ('PYTHONPATH','PYTEST_DISABLE_PLUGIN_AUTOLOAD','PYTHONDONTWRITEBYTECODE','OCM_TEXT_TASK_TRACE')}})
    receipt={'schema':'ocm.text-task-donor-qualification.v1','status':'TEXT_TASK_DONOR_FAILED',
             'qualification_source_id':expected_source_id,'root_source_id':before['root_source_id'],
             'git':before['git'],'test_files':Q.TESTS,'minimum_tests':Q.MINIMUM_TESTS,
             'started_at':datetime.now(timezone.utc).isoformat(),'scientific_promotion':'NOT_ESTABLISHED',
             'scope':'Additive donor execution attestation; historical engineering receipt scope and selection unchanged.'}
    start=time.perf_counter()
    try:
        Q.archive(root,output/'source.zip',before)
        with (output/'stdout.log').open('xb') as stdout,(output/'stderr.log').open('xb') as stderr:
            receipt['exit_code']=execute(argv,root,env,stdout,stderr)
        after=Q.snapshot(root);write(output/'SOURCE_AFTER.json',after)
        if after!=before:raise ValueError('source or dependency environment changed during qualification')
        if receipt['exit_code']!=0:raise ValueError('donor test process did not exit successfully')
        receipt['junit']=Q.validate_execution(output)
        Q.verify_archive(output/'source.zip',before)
        receipt['status']='TEXT_TASK_DONOR_QUALIFIED'
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,Q.ET.ParseError) as exc:
        receipt['reason']=type(exc).__name__+': '+str(exc)
    receipt['wall_seconds']=time.perf_counter()-start
    receipt['completed_at']=datetime.now(timezone.utc).isoformat()
    receipt['artifacts']={p.name:Q.sha(p) for p in output.iterdir() if p.is_file()}
    passed=receipt['status']=='TEXT_TASK_DONOR_QUALIFIED'
    write(output/('RECEIPT.json' if passed else 'FAILED.json'),receipt)
    return 0 if passed else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--describe',action='store_true',help='print the current identity without executing tests')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--expected-source-id')
    args=parser.parse_args()
    if args.describe:
        state=Q.snapshot(ROOT)
        print(json.dumps({'qualification_source_id':Q.identity(state),'root_source_id':state['root_source_id'],
              'git':state['git'],'donor_inventory':state['donor_inventory'],'required_versions':Q.PINS},indent=2))
    else:
        if args.output is None or not args.expected_source_id:parser.error('execution requires --output and --expected-source-id')
        raise SystemExit(record(ROOT,args.output,args.expected_source_id))
