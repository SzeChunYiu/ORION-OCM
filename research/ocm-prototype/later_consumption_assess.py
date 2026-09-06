"""Assess already sealed candidates, retaining each assigned route and checker call."""
import argparse
import json
from pathlib import Path
import time

import clia_checker
import clia_process
from clia_tasks import load_task
from later_consumption_contract import ROOT, ROUTES, CHECKS, TASK_ID, prepare_return, sha
from later_consumption_capture import capture_one, decode_result, seal, verify, verify_seal, write


def native_verify(manifest, output, slot, payload):
    if slot not in CHECKS:
        raise ValueError('unregistered native obligation')
    verify(manifest)
    directory = Path(output)/slot
    request = json.dumps({'action':'verify','payload':payload,'timeout_ms':5000}).encode()
    raw = capture_one(manifest['checker_commands'][slot],request,directory,ROOT,manifest['checker_watchdog_s'])
    result = decode_result(directory,raw)
    if result['status'] not in ('PASS','FAIL','CANNOT_CHECK'):
        result.update(status='CANNOT_CHECK',reason='unexpected native checker response')
    verify(manifest)
    return result


def _spec_check(task, candidate, call):
    """Reuse unchanged grammar/specification construction; capture its one native boundary."""
    original = clia_process.invoke
    def intercepted(action, payload, *, timeout_ms=5000, deadline_s=10):
        if action != 'verify' or timeout_ms != 5000 or deadline_s != 10:
            raise ValueError('checker launch contract drift')
        return call(payload)
    clia_process.invoke = intercepted
    try:
        return clia_checker.check(task,{'status':'SOLUTION','candidate':candidate,
            'task_sha256':task['task_sha256'],'grammar_id':task['grammar']['id']},timeout_ms=5000,deadline_s=10)
    finally:
        clia_process.invoke = original


def run(manifest_path):
    start, cpu = time.perf_counter(), time.process_time()
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    verify(manifest)
    root = Path(manifest['output']); candidates = root/'candidates'
    verify_seal(candidates)
    receipt = json.loads((candidates/'receipt.json').read_text())
    if receipt['manifest_sha256'] != sha(manifest_path):
        raise ValueError('capture manifest binding drift')
    output = root/'assessment'; output.mkdir()
    write(output/'input.json',{'raw_seal_sha256':sha(candidates/'seal.json'), 'manifest_sha256':sha(manifest_path)})
    task = load_task(TASK_ID)
    reached, native_results, rows = [], {}, []
    def call(slot,payload):
        if slot in reached or slot not in CHECKS or len(reached) >= 4:
            raise ValueError('checker ceiling or slot violated')
        reached.append(slot)
        result = native_verify(manifest,output,slot,payload)
        native_results[slot] = result
        return result
    for assigned in receipt['rows']:
        route = assigned['route']
        row = {'route':route,'status':'CANNOT_CHECK','check':{'status':'NOT_RUN'},
               'expansion':{'status':'NOT_RUN'},'observed_calls':[]}
        try:
            verify(manifest); verify_seal(candidates)
            if 'capture' not in assigned:
                raise ValueError('candidate route never completed capture')
            native = decode_result(candidates/route,assigned['capture'])
            row['candidate_return'] = native
            if native['status'] != 'SOLUTION' or not native.get('candidate'):
                raise ValueError(native.get('reason','no returned solution'))
            prepared = prepare_return(native['candidate'],route)
            row.update(prepared)
            if route == 'B':
                row['expansion'] = call('B-expansion',{'smt2':prepared['equivalence_smt2']})
            row['check'] = _spec_check(task,prepared['expanded_candidate'],lambda p:call(route+'-spec',p))
            row['status'] = row['check']['status']
            if route == 'B' and row['expansion']['status'] != 'PASS':
                row['status'] = 'CANNOT_CHECK'
        except (OSError, ValueError, TypeError, KeyError, IndexError, RecursionError) as exc:
            row.update(status='CANNOT_CHECK',reason=type(exc).__name__+': '+str(exc))
        rows.append(row)
        write(output/(route+'-assessment.json'),row)
    b = next(row for row in rows if row['route'] == 'B')
    consumption = 'CANNOT_CHECK_CONSUMPTION'
    if b['status'] == 'PASS':
        consumption = 'LEARNED_DEFINITION_CONSUMPTION_QUALIFIED' if b['observed_calls'] else 'NO_OBSERVED_USE'
    summary = {
        'status':'ASSESSMENT_SEALED','rows':rows,'consumption':consumption,
        'raw_seal_sha256':sha(candidates/'seal.json'),'manifest_sha256':sha(manifest_path),
        'reached_obligations':reached,
        'completed_native_worker_boundaries':sum(x.get('native_invoked') is True for x in native_results.values()),
        'unresolved_native_boundaries':[s for s in reached if s not in native_results or native_results[s].get('native_invoked') == 'UNKNOWN'],
        'maximum_obligations':4,'assigned_candidate_denominator':3,
        'whole_lifetime_economics':'NOT_ESTABLISHED','causal_search_benefit':'NOT_ESTABLISHED',
        'parent_capability':'SUPPORTED_ON_EXPOSED_TASK' if rows[0]['status'] == 'PASS' else 'CANNOT_CHECK',
        'utility_verdict':'NOT_ESTABLISHED; compare declared C total work with B plus retained acquisition/repair costs before PARENT_SUFFICIENT.',
        'assessment_wall_s':time.perf_counter()-start,'assessor_self_cpu_s':time.process_time()-cpu,
        'process_tree_cpu':'UNKNOWN','process_tree_peak_rss':'UNKNOWN',
    }
    verify_seal(candidates)
    write(output/'receipt.json',summary)
    seal(output)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest',required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.manifest)))
