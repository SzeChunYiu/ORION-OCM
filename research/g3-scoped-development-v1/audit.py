"""Read-only reconciliation using global independent catalogs, not saved success flags."""
from __future__ import annotations
from collections import deque
from pathlib import Path
from fractions import Fraction
import argparse
import json
import sys
import tarfile
import mechanisms as X
import runtime_bridge as R
from run import PHASES,reconcile,selected_coordinates


def catalog(key=None,bound=5):
    """One complete traversal vs the producer's separate goal-terminated traversals.

    Uses whole-program normal_form, not the producer's incremental transition
    algebra. Captures the exact queue frontier before each candidate expansion.
    """
    q=deque([()]);seen=set();checked=edges=dropped=0;first={}
    while q:
        p=q.popleft();poly=X.M.normal_form(p)
        if key:
            k=X.representation_key(p,poly,key)
            if k in seen:dropped+=1;continue
            seen.add(k)
        checked+=1
        first.setdefault(poly,{'terminal':'VERIFIED_POLYNOMIAL_IDENTITY','program':list(p),
            'checked_programs':checked,'generated_edges':edges,'duplicate_states_dropped':dropped})
        if len(p)<bound:q.extend(p+(t,) for t in X.M.PRIMITIVES);edges+=4
    return first


def expected_failure(t,s,guard,raw):
    target=X.coefficients(t['coefficients']);skip=bool(guard and X.guard_applies(guard,target,s))
    attempt=None if skip else X.prefix_search(target,s,'audit-occurrence-is-not-a-scientific-coordinate')
    if attempt and attempt['program']:
        result={'terminal':'VERIFIED_POLYNOMIAL_IDENTITY','program':attempt['program'],
            'checked_programs':0,'generated_edges':0,'duplicate_states_dropped':0}
    else:result=raw[target]
    row={'target':t['identity'],'result':result,'prefix_checks':0 if skip else attempt['checked_programs'],
        'fallback_checks':result['checked_programs'],'method_used':bool(attempt and attempt['program']),
        'guard_consumed':X.digest(guard) if skip else None}
    return selected_coordinates(row),attempt


def audit(root:Path,check_archives=True):
    X.require(not (root/'INCOMPLETE.json').exists() and not (root/'INTERRUPTED.json').exists(),'INCOMPLETE_RUN')
    files=X.read_json(root/'FILES.json');X.require(type(files) is dict and bool(files),'EMPTY_FILE_CUSTODY')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    X.require(actual==set(files)|{'FILES.json'},'UNLISTED_OR_MISSING_RETAINED_FILES')
    for name,ident in files.items():
        p=root/name;X.require(p.is_file() and p.stat().st_size==ident['bytes'] and
                             X.raw_digest(p.read_bytes())==ident['sha256'],'RETAINED_FILE_IDENTITY:'+name)
    source=X.read_json(root/'SOURCE.json');source_id=X.digest(source)
    if check_archives:
        with tarfile.open(root/'SOURCE.tar.gz','r:gz') as archive:
            members=archive.getmembers()
            X.require(len(members)==len(source['files']) and {m.name for m in members}==set(source['files']),
                      'SOURCE_ARCHIVE_POPULATION')
            for m in members:
                X.require(m.isfile(),'SOURCE_ARCHIVE_NOT_REGULAR');raw=archive.extractfile(m).read()
                ident=source['files'][m.name]
                X.require(len(raw)==ident['bytes'] and X.raw_digest(raw)==ident['sha256'],'SOURCE_ARCHIVE_IDENTITY')
    current_m=X.REPO/'src/ocm/learning/methods.py'
    X.require(X.raw_digest(current_m.read_bytes())==source['files']['src/ocm/learning/methods.py']['sha256'],
              'AUDIT_CHECKER_SOURCE_DRIFT')
    targets=X.read_json(root/'TARGETS.json');raw=catalog();quotient=catalog('coefficients');refined=catalog('coefficients-last')
    expected={X.digest(X.wire(p)):len(v['program']) for p,v in raw.items() if 3<=len(v['program'])<=5}
    X.require(len(targets)==len(expected) and {t['identity']:t['minimum_length'] for t in targets}==expected,
              'INDEPENDENT_CENSUS_MISMATCH')
    X.require(all(t['identity']==X.digest(X.wire(t['coefficients'])) for t in targets),'TARGET_IDENTITY')
    X.require(all(t['identity']==X.digest(X.wire(t['coefficients'])) for t in targets),'TARGET_IDENTITY')
    reports=[];processes=[]
    for i,phase in enumerate(PHASES):
        directory=root/f'{i:02d}-{phase}';p=X.read_json(directory/'PROCESS.json')
        r=X.read_json(directory/'output/PHASE.json');request=X.read_json(directory/'REQUEST.json')
        X.require(p['returncode']==0 and p['timed_out'] is False and p['phase']==phase,'PROCESS_NOT_SUCCESSFUL')
        X.require(r['pid']==p['pid'] and r['parent_pid']==p['parent_pid'] and
                  r['request']==p['request']==X.raw_digest((directory/'REQUEST.json').read_bytes()),'PROCESS_IDENTITY')
        X.require(r['phase']==phase and r['source']==request['source']==source_id and
                  request['occurrence']==r['occurrence'] and request['targets']==targets,'REQUEST_BINDING')
        X.require(r['before']==request['lease'],'REQUEST_LEASE')
        reports.append(r);processes.append(p)
    X.require(X.read_json(root/'PROCESS-INDEX.json')==processes,'PROCESS_INDEX')
    guard=reports[1]['result']['guard'];attempt=reports[1]['result']['attempt'];X.validate_guard(guard,attempt)
    scope=X.MethodScope(source=source_id);proof_checks=0;count_checks=0
    for report in reports:
        phase=report['phase'];result=report['result']
        if phase.startswith('failure-') or phase.startswith('representation-'):
            rows=result['packet']['rows'];X.require(len(rows)==len(targets),'ROW_POPULATION')
            support=[e for e in result['trace']['stages'] if e['stage']=='COMMITMENT']
            X.require(len(support)==1 and support[0]['status']=='PASS' and support[0]['reason']=='COMMITTED',
                      'NO_ACTUAL_COMMITMENT_TRACE')
            X.require(set(support[0]['evidence_ids'])=={repr(x) for x in result['answer_support']},'COMMITMENT_SUPPORT_MISMATCH')
            b=report['binding'];dependencies=set(result['answer_support'])
            if phase.startswith('failure-'):
                X.require(b['method_permission'] in dependencies,'MISSING_METHOD_DEPENDENCY')
                X.require((b['guard_permission'] in dependencies)==(phase!='failure-revoked'),'GUARD_DEPENDENCY_MISMATCH')
                X.require((b['failure_evidence'] in dependencies)==(phase!='failure-revoked'),'FAILURE_DEPENDENCY_MISMATCH')
            elif phase!='representation-raw':X.require(b['representation_permission'] in dependencies,'MISSING_REPRESENTATION_DEPENDENCY')
            for t,row in zip(targets,rows):
                p=tuple(row['result']['program']);X.require(X.M.normal_form(p)==X.coefficients(t['coefficients']),'NATIVE_POLYNOMIAL_REFUSAL')
                proof_checks+=1
                if phase.startswith('failure-'):
                    g=None if phase=='failure-revoked' else guard
                    expected_row,expected_attempt=expected_failure(t,scope,g,raw)
                    if expected_attempt is not None:
                        actual_attempt=row['prefix_attempt'];X.require(actual_attempt is not None,'MISSING_ATTEMPT')
                        X.require(actual_attempt['occurrence']==report['occurrence']+':'+str(count_checks%len(targets)),
                                  'ATTEMPT_OCCURRENCE')
                        actual_attempt=dict(actual_attempt,occurrence=expected_attempt['occurrence'])
                        X.require(actual_attempt==expected_attempt,'FORGED_ATTEMPT')
                    else:X.require(row['prefix_attempt'] is None,'SKIPPED_ATTEMPT_WAS_EXECUTED')
                else:
                    chosen=raw if phase=='representation-raw' else quotient if phase=='representation-quotient' else refined
                    expected_row=selected_coordinates({'target':t['identity'],'result':chosen[X.coefficients(t['coefficients'])]})
                X.require(selected_coordinates(row)==expected_row,'INDEPENDENT_SEARCH_WORK_MISMATCH');count_checks+=1
    replay=R.OCMRuntime(root/'lineage')
    X.require(R.lease(replay)==reports[-1]['after'],'FINAL_REAL_RUNTIME_REPLAY')
    summary=reconcile(reports,targets);recorded=X.read_json(root/'SUMMARY.json')
    for k,v in summary.items():X.require(recorded[k]==v,'SUMMARY_RECONCILIATION:'+k)
    X.require(recorded['source_archive_bytes']==(root/'SOURCE.tar.gz').stat().st_size,'ARCHIVE_SIZE')
    return {'terminal':'EXACT_G3_LINEAGE_RECONCILED','retained_files_checked':len(files),
            'source_files_checked':len(source['files']),'fresh_processes_checked':len(reports),
            'exact_polynomial_proofs_rechecked':proof_checks,'independent_work_rows':count_checks,
            'final_ledger_events':len(replay.events),'source':source_id,'population':X.digest(targets),
            'scope':'Read-only arithmetic/custody/replay audit, not independent authorship, signed remote execution or protected evaluation.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);a=p.parse_args()
    print(json.dumps(audit(a.run.resolve()),indent=2))
