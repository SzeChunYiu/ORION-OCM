"""Prepare exact commands and byte bindings; no solver or induction calls."""
import argparse
from functools import lru_cache
import importlib.metadata as metadata
import json
from pathlib import Path
import subprocess
import sys

from later_consumption_contract import ROOT, PRIOR, ADAPTER, ADAPTER_SHA, SEAL_SHA, ROUTES, CHECKS, TASK_ID, requests
from later_consumption_capture import binding, write, SUPERVISOR
from clia_tasks import load_task

PYTHON = Path('/home/billy/orion-director-work/20260906/generation-env/bin/python')
TOOLS = ['/usr/bin/env','/usr/bin/timeout','/usr/bin/taskset','/usr/bin/prlimit']


@lru_cache(maxsize=1)
def environment():
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise ValueError('prepare with the pinned generation environment')
    paths = {PYTHON, *map(Path, TOOLS)}
    for name, version in [('cvc5','1.3.4'),('z3-solver','5.1.0.0'),('sexpdata','1.0.2')]:
        distribution = metadata.distribution(name)
        if distribution.version != version:
            raise ValueError('pinned dependency drift: '+name)
        paths.update(Path(distribution.locate_file(f)) for f in distribution.files or []
                     if '__pycache__' not in str(f) and str(f).endswith(('.py','.so','.so.4.16','METADATA','RECORD','WHEEL')))
        # Include every native shared library, including versioned wheel members.
        paths.update(Path(distribution.locate_file(f)) for f in distribution.files or [] if '.so' in str(f))
    paths.update(PYTHON.resolve().parents[1].glob('lib/libpython*.so*'))
    return {str(p):binding(p) for p in sorted(paths) if p.is_file()}


def command(seconds):
    return ['/usr/bin/env','-i','PATH=/usr/bin:/bin','LANG=C.UTF-8',
            '/usr/bin/timeout','--kill-after=2s',str(seconds)+'s','/usr/bin/taskset','-c','0',
            '/usr/bin/prlimit','--as=4294967296',str(PYTHON),'-B','-E','-s',str(ROOT/'clia_worker.py')]


def prepare(packet):
    packet = Path(packet).resolve(); packet.mkdir()
    sources = [ROOT/p for p in ('clia_tasks.py','clia_grammar.py','clia_checker.py','clia_process.py',
        'clia_worker.py','generation_clia.py','later_consumption_contract.py','later_consumption_prepare.py',
        'later_consumption_capture.py','later_consumption_assess.py')]
    sources += [SUPERVISOR, ADAPTER, PRIOR/'seal.json']
    sources += sorted((ROOT/'clia_fixtures').glob('*.json')) + sorted((ROOT/'clia_fixtures').glob('*.sl'))
    request_paths = {}
    for route, text in requests().items():
        path = packet/(route+'-request.json')
        write(path, {'action':'synthesize','payload':{'sygus':text},'timeout_ms':5000})
        request_paths[route] = str(path)
    task = load_task(TASK_ID)
    manifest = {
        'schema':'ocm.later-consumption.public.v1','status':'PREPARED_NOT_FROZEN_NOT_EXECUTED',
        'source_base_commit':'02e32dfa6755ec737ef472c054c9b3117af79e5b',
        'source_head':subprocess.check_output(['/usr/bin/git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
        'source_authority':'Exact source_bindings; source_head is lineage and may precede uncommitted preparation.',
        'task_id':TASK_ID,'task_sha256':task['task_sha256'],'task_source':task['source'],
        'library_adapter_sha256':ADAPTER_SHA,'library_predecessor_seal_sha256':SEAL_SHA,
        'source_bindings':{str(p):binding(p) for p in sources},'environment_bindings':environment(),
        'requests':request_paths,'request_bindings':{p:binding(p) for p in request_paths.values()},
        'route_order':list(ROUTES),'candidate_commands':{r:command(20) for r in ROUTES},
        'checker_commands':{s:command(10) for s in CHECKS},'native_timeout_ms':5000,
        'candidate_watchdog_s':24,'checker_watchdog_s':14,'maximum_checker_obligations':4,
        'output':str(packet.parent/'run-v1'),
        'launch_commands':{
            'capture':[str(PYTHON),'-B','-E','-s',str(ROOT/'later_consumption_capture.py'),'--manifest',str(packet/'manifest.json')],
            'assess':[str(PYTHON),'-B','-E','-s',str(ROOT/'later_consumption_assess.py'),'--manifest',str(packet/'manifest.json')]},
        'assignment':'One C, E0, B in order. No induction, option change, retry, restricted grammar or follow-up.',
        'checker_input_rule':'After raw seal: existing specification checker plus B fixed-helper/expanded equality; source-bound construction, no prospective target solution.',
        'prior_history':{'adapter':str(ADAPTER),'seal':str(PRIOR/'seal.json'),
            'costs':'Imported acquisition/induction/repair history stays separate and is not zeroed.'},
        'cost_scope':'Per-native-worker completed CPU/RSS plus envelope wall; timed-out CPU/RSS, complete process tree, prior full history and lifetime economics UNKNOWN.',
        'use_observation':'Returned fn_0 body dependency only. Unchanged worker has no GEN derivation output; no option added.',
        'claims_excluded':['general useful learning','causal search benefit','OCM residual','whole-lifetime efficiency'],
    }
    path = packet/'manifest.json'; write(path,manifest)
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--packet',required=True)
    args = parser.parse_args()
    print(prepare(args.packet))
