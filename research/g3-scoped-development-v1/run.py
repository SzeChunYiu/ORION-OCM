"""Execute a source-bound, cold-process G3 pilot through one real OCM lineage."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
from fractions import Fraction
from itertools import product
import argparse
import hashlib
import json
import os
import platform
import resource
import signal
import subprocess
import sys
import tarfile
import time
import uuid
sys.path.insert(0,str(Path(__file__).resolve().parent))
import mechanisms as X
import runtime_bridge as R

HERE=Path(__file__).resolve().parent
PHASES=('install','acquire-failure','failure-live','revoke-guard','failure-revoked','restore-guard',
        'failure-restored','acquire-representation','representation-raw','representation-quotient',
        'refine-representation','representation-refined','ordinary-parents','boundary-controls')


def source_manifest():
    paths={p for p in X.REPO.joinpath('src').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    paths.update((X.REPO/'LICENSE',X.REPO/'NOTICE'))
    paths.update(X.REPO.joinpath('research/g2-cognitive-objects-v1/g2_cognitive_objects').glob('*.py'))
    paths.update(HERE.glob('*.py'))
    paths.add(X.REPO/'research/g2-macro-source-reconciliation-v1/RAW.zip')
    files={p.relative_to(X.REPO).as_posix():{'bytes':p.stat().st_size,'sha256':X.raw_digest(p.read_bytes())}
           for p in sorted(paths)}
    return {'files':files,'python':sys.version,'executable_sha256':X.raw_digest(Path(sys.executable).read_bytes()),
            'platform':platform.platform()}


def write_new(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:
        f.write(X.encoded(data)+b'\n');f.flush();os.fsync(f.fileno())
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def verified_census():
    targets=X.census();oracle={};evaluations=0
    for n in range(6):
        for p in product(X.M.PRIMITIVES,repeat=n):
            poly=X.M.normal_form(p);oracle.setdefault(tuple(X.wire(poly)),n);evaluations+=1
    expected={k:n for k,n in oracle.items() if 3<=n<=5}
    actual={tuple(t['coefficients']):t['minimum_length'] for t in targets}
    X.require(actual==expected and len(targets)==len(expected),'CENSUS_ORACLE_DISAGREEMENT')
    return targets,{'independent_whole_program_checks':evaluations,'targets':len(targets),
        'minimum_lengths':{str(n):sum(t['minimum_length']==n for t in targets) for n in (3,4,5)},
        'scope':'Complete authored finite census, not independent lifetimes; #192 strata begin at minimum length 6.'}


def selected_coordinates(row):
    result=row['result']
    return {'target':row['target'],'terminal':result['terminal'],'program':result['program'],
        'prefix_checks':row.get('prefix_checks',0),'fallback_checks':row.get('fallback_checks',result['checked_programs']),
        'method_used':row.get('method_used',False),'guard_consumed':row.get('guard_consumed'),
        'checked_programs':result['checked_programs'],'generated_edges':result.get('generated_edges',0),
        'duplicate_states_dropped':result.get('duplicate_states_dropped',0)}


def parent_run(targets,s,guard,arm):
    start=time.perf_counter();cpu=time.process_time();rows=[]
    analytic=dict(guard,reachable_values=sorted(str(2**n) for n in range(2,2+s.max_length-len(s.prefix)+1)))
    for i,t in enumerate(targets):
        poly=X.coefficients(t['coefficients']);identity=t['identity']
        if arm in ('primitive-only','semantic-quotient','semantic-last'):
            key={'primitive-only':None,'semantic-quotient':'coefficients','semantic-last':'coefficients-last'}[arm]
            result=X.primitive_search(poly,5,key)
            row={'result':result,'prefix_checks':0,'fallback_checks':result['checked_programs'],
                 'method_used':False,'guard_consumed':None}
        else:
            # Exact case memory has only the acquisition task x+1, absent from this census.
            applicable=guard if arm=='certified-failure-parent' else analytic if arm=='analytic-degree-parent' else None
            row=X.solve_with_guard(poly,s,applicable,'parent:'+arm+':'+str(i))
        row['target']=identity
        X.require(row['result']['terminal']=='VERIFIED_POLYNOMIAL_IDENTITY' and
                  X.M.normal_form(tuple(row['result']['program']))==poly,'PARENT_EXACT_CHECK_FAILED')
        rows.append(selected_coordinates(row))
    return {'arm':arm,'rows':rows,'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu}


def worker(request_path,expected_hash):
    raw=request_path.read_bytes();X.require(X.raw_digest(raw)==expected_hash,'REQUEST_IDENTITY')
    request=X.read_json(request_path);output=Path(request['output'])
    X.require(not output.exists(),'FRESH_WORKER_OUTPUT');output.mkdir(parents=True)
    started=time.perf_counter();cpu=time.process_time()
    resource.setrlimit(resource.RLIMIT_AS,(2_000_000_000,2_000_000_000))
    resource.setrlimit(resource.RLIMIT_CPU,(150,151))
    resource.setrlimit(resource.RLIMIT_FSIZE,(256_000_000,256_000_000))
    manifest=source_manifest();X.require(X.digest(manifest)==request['source'],'SOURCE_DRIFT')
    phase=request['phase'];X.require(phase in PHASES,'PHASE')
    targets=request['targets'];source=request['source'];binding=request['binding']
    root=Path(request['root']);expected=request['lease'];before=expected
    if phase=='install':
        binding,rt=R.install(root,source);result={'origin':'NEW_LINEAGE_IMPORTING_RECORDED_G2_NOT_HISTORICAL_ROOT_CONTINUATION'}
    else:
        rt=R.load(root,binding,source,expected)
        if phase=='acquire-failure':binding,result=R.acquire_failure(rt,binding)
        elif phase in ('revoke-guard','restore-guard'):
            result=R.change_guard_permission(rt,binding,phase=='restore-guard')
        elif phase.startswith('failure-'):
            tick=time.perf_counter();guard,validation=R.active_guard(rt,binding)
            revalidation=time.perf_counter()-tick;s=X.MethodScope(source=source)
            must_live=phase!='failure-revoked';X.require((guard is not None)==must_live,'GUARD_LIVENESS_MODE')
            def generate():
                rows=[]
                for i,t in enumerate(targets):
                    row=X.solve_with_guard(t['coefficients'],s,guard,request['occurrence']+':'+str(i))
                    row['target']=t['identity'];rows.append(row)
                return {'rows':rows}
            support=[binding['method_permission']]+([binding['guard_permission'],binding['failure_evidence']] if guard else [])
            result=R.commit_batch(rt,binding,request['occurrence'],targets,generate,support)
            result.update(guard_revalidation_checks=validation,guard_revalidation_wall_seconds=revalidation)
        elif phase in ('acquire-representation','refine-representation'):
            binding,result=R.acquire_representation(rt,binding,'coefficients' if phase=='acquire-representation' else 'coefficients-last')
        elif phase.startswith('representation-'):
            cert=R.active_representation(rt,binding) if phase!='representation-raw' else None
            key=cert['name'] if cert else None
            def generate():
                return {'rows':[{'target':t['identity'],'result':X.primitive_search(t['coefficients'],5,key,binding['observer'])}
                                for t in targets]}
            result=R.commit_batch(rt,binding,request['occurrence'],targets,generate,
                                  [binding['representation_permission']] if cert else [])
        elif phase=='ordinary-parents':
            guard,n=R.active_guard(rt,binding);X.require(guard is not None,'PARENT_GUARD_MISSING')
            s=X.MethodScope(source=source)
            arms=('primitive-only','no-failure-memory','exact-case-memory','certified-failure-parent',
                  'analytic-degree-parent','semantic-quotient','semantic-last')
            result={'arms':[parent_run(targets,s,guard,arm) for arm in arms],
                    'cold_certificate_revalidation_checks':n,
                    'scope':'Conventional matched finite parents. Not full ATMS, external CEGAR software, neural or strongest #73 product.'}
        elif phase=='boundary-controls':
            s=X.MethodScope(source=source);target=X.M.normal_form(X.MACRO+('inc',)*3)
            failed=X.prefix_search(target,s,'boundary:budget-failure');g=X.learn_guard(failed)
            X.require(g is not None,'NO_BOUNDARY_CERTIFICATE');X.validate_guard(g,failed)
            expanded=replace(s,max_length=6)
            retry=X.prefix_search(target,expanded,'boundary:budget-success')
            live_guard,_=R.active_guard(rt,binding)
            result={'failed':failed,'guard':g,'larger_budget':retry,
                'blocked_at_old_budget':X.guard_applies(g,target,s),
                'blocked_at_larger_budget':X.guard_applies(g,target,expanded),
                'blocked_in_new_environment':X.guard_applies(live_guard,(1,1),replace(s,environment='polynomial-integers.v2')),
                'scoped_success':X.solve_with_guard(X.M.normal_form(X.MACRO),s,live_guard,'boundary:scope-success'),
                'logical_nogoods':rt.state.nogoods.as_dict()}
        else:raise ValueError('UNIMPLEMENTED_PHASE')
    X.require(X.digest(source_manifest())==source,'POST_SOURCE_DRIFT')
    report={'schema':X.SCHEMA+'.phase','phase':phase,'occurrence':request['occurrence'],
        'request':X.raw_digest(raw),'pid':os.getpid(),'parent_pid':os.getppid(),'source':source,
        'population':X.digest(targets),'before':before,'after':R.lease(rt),'binding':binding,'result':result,
        'resources':{'wall_seconds':time.perf_counter()-started,'cpu_seconds':time.process_time()-cpu,
            'peak_rss_bytes_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
            'persistent_bytes_after':sum(p.stat().st_size for p in root.rglob('*') if p.is_file())}}
    write_new(output/'PHASE.json',report)
    print(json.dumps({'phase':phase,'committed':result.get('committed'),'after':report['after']}))
    return 0


def reconcile(reports,targets):
    X.require([r['phase'] for r in reports]==list(PHASES),'COMPLETE_PHASE_POPULATION')
    X.require(len({r['occurrence'] for r in reports})==len(PHASES),'DUPLICATE_INVOCATION')
    for left,right in zip(reports,reports[1:]):
        X.require(left['after']==right['before'],'BROKEN_LINEAGE')
    for r in reports:
        X.require(r['population']==X.digest(targets),'POPULATION_DRIFT')
    d={r['phase']:r for r in reports};count=len(targets)
    def rows(phase):
        r=d[phase]['result'];X.require(r['committed'] is True and r['verified_goals']==count,'UNCOMMITTED_CENSUS')
        data=r['packet']['rows'];X.require(len(data)==count,'MISSING_GOALS')
        X.require([v['target'] for v in data]==[t['identity'] for t in targets],'GOAL_ORDER_DRIFT')
        return [selected_coordinates(v) for v in data]
    live=rows('failure-live');revoked=rows('failure-revoked');restored=rows('failure-restored')
    X.require(live==restored,'FAILURE_RESTORATION_MISMATCH')
    parent_records=d['ordinary-parents']['result']['arms']
    required_arms=['primitive-only','no-failure-memory','exact-case-memory','certified-failure-parent',
                   'analytic-degree-parent','semantic-quotient','semantic-last']
    X.require([a['arm'] for a in parent_records]==required_arms,'COMPLETE_PARENT_ARMS')
    X.require(all(len(a['rows'])==count and [r['target'] for r in a['rows']]==[t['identity'] for t in targets]
                  for a in parent_records),'COMPLETE_PARENT_POPULATIONS')
    parents={a['arm']:a for a in parent_records}
    X.require(live==parents['certified-failure-parent']['rows'],'CONVENTIONAL_FAILURE_PARENT_MISMATCH')
    X.require(revoked==parents['no-failure-memory']['rows'],'REVOCATION_SEARCH_MISMATCH')
    # Analytic guard origin differs intentionally; compare work and mathematical outputs.
    def without_guard(row):return {k:v for k,v in row.items() if k!='guard_consumed'}
    analytic_parity=all(without_guard(a)==without_guard(b) for a,b in zip(live,parents['analytic-degree-parent']['rows']))
    primitive=parents['primitive-only']['rows']
    raw=rows('representation-raw');quotient=rows('representation-quotient');refined=rows('representation-refined')
    X.require(raw==primitive and quotient==parents['semantic-quotient']['rows'] and
              refined==parents['semantic-last']['rows'],'REPRESENTATION_PARENT_MISMATCH')
    X.require(all(a['program']==b['program']==c['program'] for a,b,c in zip(raw,quotient,refined)),
              'SHORTEST_PROOF_CHANGED')
    invalidation=d['refine-representation']['result']
    X.require(invalidation['old_liveness']=='DEAD' and invalidation['invalidation'] is not None,'OLD_REPRESENTATION_SURVIVED')
    boundary=d['boundary-controls']['result']
    X.require(boundary['blocked_at_old_budget'] and not boundary['blocked_at_larger_budget'] and
              not boundary['blocked_in_new_environment'] and
              boundary['larger_budget']['terminal']=='VERIFIED_POLYNOMIAL_IDENTITY','SCOPE_REOPENING_FAILED')
    def total(rs,field):return sum(r[field] for r in rs)
    return {'schema':X.SCHEMA+'.summary','evidence_class':'E1/E2','targets':count,'cold_processes':len(reports),
        'failure':{'terminal':'FAILURE_MEMORY_USEFUL_AT_SCOPE','compatible_dead_ends_avoided':sum(bool(r['guard_consumed']) for r in live),
            'no_memory_prefix_checks':total(revoked,'prefix_checks'),'live_prefix_checks':total(live,'prefix_checks'),
            'live_fallback_checks':total(live,'fallback_checks'),'revoked_fallback_checks':total(revoked,'fallback_checks'),
            'method_successes_preserved':sum(r['method_used'] for r in live),
            'ordinary_parent_exact_parity':True,'analytic_parent_parity':analytic_parity,
            'parent_disposition':'PARENT_SUFFICIENT','restoration_exact':True,'budget_and_environment_reopen':True,
            'task_impossibility_claimed':False},
        'representation':{'terminal':'REPRESENTATION_CHANGE_CAUSALLY_USEFUL','raw_checks':total(raw,'checked_programs'),
            'quotient_checks':total(quotient,'checked_programs'),'refined_checks':total(refined,'checked_programs'),
            'raw_generated_edges':total(raw,'generated_edges'),'quotient_generated_edges':total(quotient,'generated_edges'),
            'refined_generated_edges':total(refined,'generated_edges'),'shortest_programs_identical':True,
            'old_scope_invalidated_before_refinement':True,'ordinary_parent_exact_parity':True,
            'prior_disposition':'REPRESENTATION_PRIOR_DOMINATES: fixed exact-coefficient language plus conventional congruence'},
        'lineage':{'root_resets_after_install':0,'all_expected_heads_chained':True,'core_and_controller_source_fixed':True,
                   'generations_claimed':0,'scope':'New C-to-D developmental pilot lineage importing #192; not all #151 stages.'},
        'physical':{r['phase']:r['resources'] for r in reports},
        'parent_timings':{name:{k:a[k] for k in ('wall_seconds','cpu_seconds')} for name,a in parents.items()},
        'completion':{'G3_2':'bounded mechanism with actual runtime, fresh-process and conventional-parent controls',
            'G3_3':'finite representation-selection/refinement mechanism; strong authored prior',
            'G3_4':'observed alias and scoped resource/evidence controls; general diagnosis not established',
            'H':'one C-to-D root with fixed source; not whole developmental programme',
            'I':'not three learned self-evolution generations','J':'not language-plus-proof transfer',
            'K':'not strongest integrated neural/classical product','L':'not protected or external replication'},
        'scope':'No OCM architectural residual, whole-lifetime payback, broad G3 closure or programme-completion claim.'}


def run(output:Path):
    controller_start=time.perf_counter()
    X.require(not output.exists(),'FRESH_RUN_DIRECTORY');output.mkdir(parents=True)
    manifest=source_manifest();source=X.digest(manifest);write_new(output/'SOURCE.json',manifest)
    with tarfile.open(output/'SOURCE.tar.gz','w:gz') as archive:
        for name,identity in manifest['files'].items():
            p=X.REPO/name;X.require(X.raw_digest(p.read_bytes())==identity['sha256'],'SOURCE_CHANGED_DURING_ARCHIVE')
            archive.add(p,arcname=name,recursive=False)
    tick=time.perf_counter();targets,allocation=verified_census()
    allocation['wall_seconds']=time.perf_counter()-tick;write_new(output/'ALLOCATION.json',allocation)
    write_new(output/'TARGETS.json',targets)
    binding=None;expected=None;reports=[];processes=[]
    for i,phase in enumerate(PHASES):
        directory=output/f'{i:02d}-{phase}';directory.mkdir()
        request={'schema':X.SCHEMA+'.request','phase':phase,'source':source,'targets':targets,
            'binding':binding,'lease':expected,'occurrence':uuid.uuid4().hex,
            'root':str((output/'lineage').resolve()),'output':str((directory/'output').resolve())}
        path=directory/'REQUEST.json';write_new(path,request)
        pycache=(directory/'empty-pycache').resolve();pycache.mkdir()
        command=[sys.executable,'-I','-S','-B','-X',f'pycache_prefix={pycache}',str(HERE/'run.py'),
                 '--worker',str(path.resolve()),X.raw_digest(path.read_bytes())]
        # -I removes the script directory from sys.path. The fixed bootstrap below
        # adds exactly HERE; the source manifest is then verified inside the worker.
        start=time.perf_counter()
        with (directory/'stdout.txt').open('xb') as out,(directory/'stderr.txt').open('xb') as err:
            child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=out,stderr=err,cwd=directory,
                env={'LANG':'C.UTF-8','LC_ALL':'C.UTF-8'},start_new_session=True)
            timed_out=False
            try:code=child.wait(timeout=170)
            except subprocess.TimeoutExpired:
                timed_out=True;os.killpg(child.pid,signal.SIGKILL);code=child.wait()
        process={'phase':phase,'pid':child.pid,'parent_pid':os.getpid(),'returncode':code,'timed_out':timed_out,
                 'wall_seconds':time.perf_counter()-start,'argv':command,'request':X.raw_digest(path.read_bytes())}
        write_new(directory/'PROCESS.json',process);processes.append(process)
        if code!=0:
            write_new(output/'INCOMPLETE.json',{'processes':processes,'terminal':'CANNOT_CHECK_INCOMPLETE_PHASE_SEQUENCE'})
            raise RuntimeError(f'{phase}: worker {code}; see {directory}/stderr.txt')
        report=X.read_json(directory/'output/PHASE.json')
        X.require(report['pid']==child.pid and report['parent_pid']==os.getpid() and
                  report['request']==process['request'] and report['occurrence']==request['occurrence'],'WORKER_INVOCATION_BINDING')
        reports.append(report);binding=report['binding'];expected=report['after']
    result=reconcile(reports,targets)
    result['controller_wall_seconds']=time.perf_counter()-controller_start
    result['source_archive_bytes']=(output/'SOURCE.tar.gz').stat().st_size
    write_new(output/'SUMMARY.json',result)
    write_new(output/'PROCESS-INDEX.json',processes)
    files={p.relative_to(output).as_posix():{'bytes':p.stat().st_size,'sha256':X.raw_digest(p.read_bytes())}
           for p in sorted(output.rglob('*')) if p.is_file()}
    write_new(output/'FILES.json',files)
    return result


if __name__=='__main__':
    if len(sys.argv)==4 and sys.argv[1]=='--worker':raise SystemExit(worker(Path(sys.argv[2]),sys.argv[3]))
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=run(args.output.resolve());print(json.dumps(result,indent=2))
