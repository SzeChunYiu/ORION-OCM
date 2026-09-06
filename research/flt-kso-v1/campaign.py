"""Prospectively bind and execute the R0 -> R1 DEVELOPMENT prerequisite gate.

The pure-Init R1 task is not an Anthropic hole, a learned-method study, or N4
acceptance. Both arms run the identical symbolic search. No positive terminal
can be produced from an absent toolchain, stored JSON, or source drift.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
from kernel import ARCHIVE, ENVIRONMENT, KernelSession
from native import atom, imp, conj, synthesize, emit_source, render_formula
from ocm_adapter import TheoremView
from ocm.runtime.ocm_runtime import OCMRuntime
from substrate import PINS, Refusal, encoded, digest_json, sha256

ROOT = Path(__file__).resolve().parents[2]
TASK_ID = 'R1-development-composition-20260906-v1'
P,Q,R,S = map(atom, ('P','Q','R','S'))
FORMULA = imp(imp(P,Q), imp(imp(Q,R), imp(imp(P,S), imp(P,conj(R,S)))))
BUDGET = {'max_expansions':256, 'max_depth':24}
REGISTRATION = 'SzeChunYiu/ORION-OCM#62:5562227033'


def inventory():
    paths = set(ROOT.joinpath('src').rglob('*.py'))
    paths.update(ROOT.joinpath('research/flt-kso-v1').glob('*.py'))
    paths.update(ROOT.joinpath('research/flt-kso-v1').glob('*.json'))
    paths.update(p for p in ROOT.joinpath('research/proof-replay-v1').iterdir() if p.is_file())
    paths.update(ROOT.joinpath('.github/workflows').glob('*.yml'))
    paths.update((ROOT/'requirements-dev.lock', ROOT/'pyproject.toml'))
    values = {}
    for path in sorted(paths):
        if path.is_symlink(): raise Refusal('CANNOT_CHECK_SOURCE_IDENTITY', str(path))
        values[path.relative_to(ROOT).as_posix()] = sha256(path.read_bytes())
    return values


def public_task():
    return {'id':TASK_ID, 'regime':'R1_DEVELOPMENT_EXPOSED', 'formula':FORMULA,
            'statement':'∀ P Q R S : Prop, '+render_formula(FORMULA),
            'environment':ENVIRONMENT, 'budget':BUDGET, 'library':['Init'],
            'operators':['local_exact@1','implication_intro@1','implication_apply@1','conjunction_intro@1'],
            'proof_body_supplied':False, 'private_evaluator_package':None,
            'hole_selection':'NOT_APPLICABLE_NOT_AN_ANTHROPIC_HOLE'}


def source_context():
    try:
        p=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,timeout=5)
        if p.returncode==0: return {'kind':'GIT_CHECKOUT','head':p.stdout.strip()}
    except (OSError,subprocess.TimeoutExpired): pass
    return {'kind':'CONTENT_INVENTORY_ONLY',
            'historical_main':'d53d0082bfdada811a565253f3e18680f91e878a',
            'local_git_head':'UNAVAILABLE_NOT_FABRICATED'}


def prepare(path):
    path=Path(path); files=inventory()
    value={'schema':'ocm.flt.r1-launch.v1','registration':REGISTRATION,
           'task':public_task(),'public_package_sha256':digest_json(public_task()),
           'source':source_context(),'source_inventory':files,'source_inventory_sha256':digest_json(files),
           'checker_archive':ARCHIVE,'future_flt_environment':PINS,
           'parent':{'mechanism':'native.synthesize','source_sha256':files['research/flt-kso-v1/native.py'],
                     'same_task_grammar_policy_budget':True,'theorem_cache':'EMPTY_IN_BOTH_ARMS',
                     'scope':'STRONG_EQUAL_MECHANISM_PARENT_FOR_THIS_PROPOSITIONAL_FRAGMENT_ONLY'},
           'success':'kernel construction only: fresh R0 AND runtime construction AND fresh pinned R1 kernel AND restart support replay; scientific promotion additionally requires unearned closed-executor qualification',
           'mechanism_boundary':'CANNOT_CHECK_CLOSED_EXECUTOR_NOT_YET_QUALIFIED',
           'programme_gate':'F0_EXPOSED_APPARATUS_PREREQUISITE_NOT_COMPLETE',
           'metrics':['state expansions','operator candidates','full canonical solve ResourceVector',
                      'N and conservative k','exact index construction','checker controls/calls',
                      'source/runtime bytes hashed','wall/child CPU','persistent bytes'],
           'negative_terminals':['CANNOT_CHECK_R0_GATE','CANNOT_CHECK_TOOLCHAIN','CHECKER_OR_ENVIRONMENT_MISMATCH',
                                 'FAILED_UNDER_BUDGET','CHECKER_REJECTED','CANNOT_CHECK_SOURCE_DRIFT','CANNOT_CHECK_MECHANISM_BOUNDARY'],
           'not_registered':['learned-method acquisition','fresh causal method reuse','R2-R8 solving','sparse scaling'],
           'environment_observed':{'python':sys.version,'platform':platform.platform()}}
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as out: out.write(encoded(value))
    return {'launch_sha256':sha256(path.read_bytes()),'source_inventory_sha256':value['source_inventory_sha256']}


def run(launch_path, destination, archive, r0_archive):
    launch_bytes=Path(launch_path).read_bytes(); launch=json.loads(launch_bytes)
    destination=Path(destination); destination.mkdir(exist_ok=False)
    started=time.perf_counter(); cpu=time.process_time()
    result={'schema':'ocm.flt.r1-result.v1','launch_sha256':sha256(launch_bytes),'task_id':TASK_ID,
            'terminal':'CANNOT_CHECK_SOURCE_DRIFT','science_scope':'EXPOSED_DEVELOPMENT_PREREQUISITE',
            'LLM_CALLS':0,'LLM_TOKENS':0,'learned_method_reuse':'NOT_RUN','R2_R8':'NOT_RUN'}
    try:
        if (launch.get('schema')!='ocm.flt.r1-launch.v1' or launch.get('registration')!=REGISTRATION
            or launch['source_inventory']!=inventory() or launch['source_inventory_sha256']!=digest_json(inventory())
            or digest_json(launch['task'])!=digest_json(public_task())
            or launch['public_package_sha256']!=digest_json(public_task())
            or launch['checker_archive']!=ARCHIVE):
            raise Refusal('CANNOT_CHECK_SOURCE_DRIFT')
        # Original source and runner are unchanged. This session produces a NEW R0 receipt.
        r0_path=destination/'R0.json'
        command=[sys.executable,str(ROOT/'research/proof-replay-v1/replay.py'),
                 '--archive',str(r0_archive or destination/'UNAVAILABLE-4.19.0'), '--out',str(r0_path)]
        before=time.perf_counter(); env=dict(os.environ); env['PYTHONPATH']=str(ROOT/'src')
        with (destination/'R0.log').open('xb') as log:
            try:
                process=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
                r0_exit=process.returncode
            except subprocess.TimeoutExpired: r0_exit=124
        r0=json.loads(r0_path.read_bytes()) if r0_path.exists() else {}
        r0_ok=(r0_exit==0 and r0.get('terminal')=='FIXED_PROOF_REPLAY_PASS' and r0.get('fresh_kernel_replay') is True)
        result['r0']={'exit_code':r0_exit,'wall_seconds':time.perf_counter()-before,
                      'log_sha256':sha256((destination/'R0.log').read_bytes()),'passed':r0_ok,
                      'receipt_sha256':sha256(r0_path.read_bytes()) if r0_path.exists() else None}
        # When R0 is unavailable, construct a diagnostic proposal but never launch a
        # scientific R1 kernel attempt or silently skip the prerequisite.
        with KernelSession(archive if r0_ok else None) as checker:
            runtime_path=destination/'knowledge-space'
            view=TheoremView(OCMRuntime(str(runtime_path)))
            goal=view.open(TASK_ID,FORMULA); view.runtime.persist()
            view=TheoremView(OCMRuntime(str(runtime_path)))
            before=time.perf_counter(); native=view.attempt(goal,checker,**BUDGET)
            native['complete_arm_wall_seconds']=time.perf_counter()-before
            before=time.perf_counter(); parent=synthesize(FORMULA,**BUDGET)
            parent_wall=time.perf_counter()-before
            parent_check=(checker.check(FORMULA,parent['term']) if parent['term'] is not None
                          else {'terminal':'FAILED_UNDER_BUDGET','kernel_verified':False})
            replay=TheoremView(OCMRuntime(str(runtime_path)))
            lifecycle={'restart_status':replay.status(goal),'revocation':'NOT_APPLICABLE_NO_CHECKED_CLAIM'}
            if native['kernel_evidence'] is not None:
                eid=native['kernel_evidence']; replay.runtime.revoke((eid,))
                lifecycle['after_revoke']=TheoremView(OCMRuntime(str(runtime_path))).status(goal)
                replay.runtime.reinstate((eid,))
                lifecycle['after_reinstate']=TheoremView(OCMRuntime(str(runtime_path))).status(goal)
                lifecycle['revocation']='LIVE_SUPPORT_WITHDRAWAL_NOT_THEOREM_FALSITY'
            root_ok=(r0_ok and native['checker']['kernel_verified'] and native['goal_status']=='PROVED'
                     and lifecycle.get('restart_status')=='PROVED' and lifecycle.get('after_revoke')=='OPEN'
                     and lifecycle.get('after_reinstate')=='PROVED')
            terminal=('CANNOT_CHECK_MECHANISM_BOUNDARY' if root_ok else
                      'CANNOT_CHECK_R0_GATE' if not r0_ok else native['checker']['terminal'])
            parent_equal=(root_ok and parent_check['kernel_verified'] and native['proposal']['term']==parent['term']
                          and native['proposal']['metrics']==parent['metrics'])
            result.update(terminal=terminal, kernel_construction_supported=root_ok,
                          mechanism_boundary='CANNOT_CHECK_CLOSED_EXECUTOR_NOT_YET_QUALIFIED',
                          programme_gate='F0_EXPOSED_APPARATUS_PREREQUISITE_NOT_COMPLETE',
                          native=native,parent={'proposal':parent,'checker':parent_check,
                          'construction_wall_seconds':parent_wall,'comparison_terminal':'PARENT_SUFFICIENT_FOR_KERNEL_CONSTRUCTION_ONLY'
                          if parent_equal else 'CANNOT_CHECK_PARENT_COMPARISON'},lifecycle=lifecycle,
                          checker_preparation=checker.report,checker_metrics=dict(checker.metrics),
                          mechanism_models='ABSENT_CLOSED_SYMBOLIC_GRAMMAR',
                          proof_generation_scope='native.py AND registered runtime callback; AI-assisted software development excluded')
            if native['proposal'] and native['proposal']['term'] is not None:
                (destination/'Candidate.lean').write_text(emit_source(FORMULA,native['proposal']['term']),encoding='utf-8')
        if inventory()!=launch['source_inventory']: raise Refusal('CANNOT_CHECK_SOURCE_DRIFT')
    except Exception as exc:  # An execution exception is a negative terminal, never a pass.
        result.update(terminal=getattr(exc,'terminal','CANNOT_CHECK_CAMPAIGN_EXECUTION'),reason=str(exc))
    result['resources']={'wall_seconds':time.perf_counter()-started,'host_cpu_seconds':time.process_time()-cpu,
                         'peak_rss_bytes':None,'energy':None,
                         'persisted_bytes_before_result_finalization':sum(p.stat().st_size for p in destination.rglob('*') if p.is_file()),
                         'unmeasured':['host filesystem read bytes','process-tree peak RSS','energy','development and installation cost'],
                         'global_work':'canonical full-field navigation and full runtime hashing explicitly retained'}
    (destination/'RESULT.json').write_bytes(encoded(result))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='action',required=True)
    prepare_parser=sub.add_parser('prepare');prepare_parser.add_argument('--out',type=Path,required=True)
    run_parser=sub.add_parser('run');run_parser.add_argument('--launch',type=Path,required=True)
    run_parser.add_argument('--out',type=Path,required=True);run_parser.add_argument('--archive',type=Path)
    run_parser.add_argument('--r0-archive',type=Path)
    args=parser.parse_args()
    result=prepare(args.out) if args.action=='prepare' else run(args.launch,args.out,args.archive,args.r0_archive)
    print(json.dumps({k:result[k] for k in ('launch_sha256','terminal','source_inventory_sha256') if k in result}))
    raise SystemExit(0 if args.action=='prepare' or result['terminal'].startswith('UNSEEN_COMPOSITION_SUPPORTED') else 2)
