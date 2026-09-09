"""Read-only source/receipt reconciliation and deterministic G3 accounting replay.

This checks retained evidence, not new scientific outcomes or independent hosts.
The public workflow/artifact is the execution-custody parent, not a signature
issued by this script. No frozen study file is modified.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def require(value, message):
    if not value:
        raise ValueError(message)


def read(p):
    return json.loads(Path(p).read_bytes())


def raw_id(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(v):
    return hashlib.sha256(canonical(v)).hexdigest()


def audit_b(root):
    r = root / 'pr203-repeat'; run = r / 'run'
    tasks_bytes = (r / 'allocation/TASKS.json').read_bytes()
    require(hashlib.sha256(tasks_bytes).hexdigest() == '11aa5ae4f887dda9606b4f2def3aa3432811977027fd4a52bc709e7ed8d5a92d', 'frozen task drift')
    tasks = json.loads(tasks_bytes)
    summary = read(run / 'RESULT.json')
    modes = ['enabled', 'resident-disabled', 'restored']; pids = set(); rows = 0; reasons = Counter(); workers = []
    checked_files = 0
    for i, mode in enumerate(modes):
        arm = run / f'arm-{i}'
        process = read(arm / 'PROCESS.json'); worker = read(arm / 'output/WORKER.json')
        receipt = read(arm / 'RECONCILIATION.json'); request = read(arm / 'REQUEST.json')
        require(process == summary['observations'][i], 'process observation mismatch')
        require(process['mode'] == worker['mode'] == mode and process['returncode'] == 0 and not process['timed_out'], 'process outcome')
        require(process['pid'] == worker['pid'] and process['parent_pid'] == worker['parent_pid'], 'recorded process identity')
        require(process['occurrence'] == worker['occurrence'] == request['occurrence'], 'invocation identity')
        require(worker['source'] == summary['source'], 'source identity')
        require(raw_id((arm / 'REQUEST.json').read_bytes()) == process['request'] == worker['request'] == receipt['request'], 'request bytes')
        require(raw_id((arm / 'output/WORKER.json').read_bytes()) == receipt['worker'], 'worker bytes')
        for name in ('stdout', 'stderr'):
            require(raw_id((arm / (name + '.txt')).read_bytes()) == process[name], 'log bytes')
        for name, identity in receipt['files'].items():
            require(raw_id((arm / 'output' / name).read_bytes()) == identity, 'retained file identity')
            checked_files += 1
        require(worker['population'] == summary['population'] and len(worker['rows']) == 10, 'complete population')
        for j, row in enumerate(worker['rows']):
            require(row['index'] == j and row['task'] == summary['population'][j], 'row identity')
            solve = row['solve']
            require(solve['terminal'] == 'UNKNOWN' and row['native'] is None and not solve['native_acceptance'], 'v1 terminal changed')
            require(solve['generated_proof'] is None and not solve['parent_scope_complete'], 'incomplete preparation boundary')
            reasons[solve['error']['reason']] += 1; rows += 1
        pids.add(worker['pid'])
        workers.append({'mode': mode, 'pid': worker['pid'], 'resources': worker['resources'], 'parent_observed_wall_seconds': process['wall_seconds']})
    require(len(pids) == 3 and rows == 30, 'cold-process or population count')
    require(summary['comparison']['causal_decision_witnesses'] == summary['comparison']['checked_cohort_use_tasks'] == 0, 'causal witness summary')
    return {'terminal': 'FROZEN_PR203_RETAINED_BYTES_AND_SCOPE_RECONCILED', 'rows': rows, 'file_identities_checked': checked_files,
            'reasons': dict(reasons), 'workers': workers, 'native_verified_target_proofs': 0,
            'scientific_disposition': 'RESOURCE_BOUND during grounding; not unprovability, failed representation, or useless method proof',
            'source_commit': '29c0ec40bb377152e24b5e9cd5ad133daae6fa36', 'experiment_wall_seconds': summary['wall_seconds']}


def audit_c(root, source):
    pins = {}; checked = 0
    for line in (root / 'GIT-TREE.txt').read_text().splitlines():
        meta, name = line.split('\t', 1); mode, kind, blob = meta.split()
        require(kind == 'blob', 'non-blob source')
        raw = (source / name).read_bytes()
        require(hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == blob, 'source blob mismatch')
        pins[name] = blob; checked += 1
    sys.path.insert(0, str(source / 'src'))
    from ocm.learning import methods as M
    study = root / 'study'; tests = read(study / 'TESTS.json'); records = read(study / 'ORDINARY.json')
    request = read(study / 'REQUEST.json'); result = read(study / 'RESULT.json')
    require(len(tests) == 16 and len(records) == 64 and sha(records) == request['memory']['records_digest'], 'population or memory binding')
    require(hashlib.sha256((source / 'research/g3-scoped-failure-memory-v1/experiment.py').read_bytes()).hexdigest() == request['source_sha256'] == result['source'], 'study source binding')
    allocation = read(study / 'ALLOCATION.json'); training = read(study / 'TRAINING.json')
    require(len(training) == len(allocation['training']) == 8, 'training population')
    require(not ({d['fingerprint'] for d in allocation['training']} & {d['fingerprint'] for d in tests}), 'training/test overlap')
    real = M.execute; selected = []; seen = set(); acquired_attempts = 0
    for data, retained in zip(allocation['training'], training):
        task = M.PolynomialTask(data['task_id'], tuple(Fraction(c) for c in data['coefficients']))
        failures = []; counts = Counter()
        def acquiring(program, x):
            counts['point_calls'] += 1; counts['interpreter_calls'] += 1; counts['interpreter_steps'] += len(program)
            value = real(program, x); target = M.evaluate_polynomial(task.coefficients, x)
            if value != target:
                failures.append({'schema': 'g3.failure-point.v1', 'program': list(program), 'x': x,
                                 'value': str(value), 'target_value': str(target), 'task': data,
                                 'context': records[0]['context'], 'outcome': 'CHECKED_POINT_MISMATCH'})
            return value
        M.execute = acquiring
        try:
            replay = M.solve(task, M.SearchBudget(2000, 5))
        finally:
            M.execute = real
        require(json.loads(canonical(replay.as_dict())) == retained['result'], 'training solution replay')
        require(failures == retained['failures'] and dict(counts) == retained['counts'], 'actual failed-attempt replay')
        acquired_attempts += len(failures)
        for record in failures:
            key = (tuple(record['program']), record['x'])
            if key not in seen and len(selected) < 64:
                seen.add(key); selected.append(record)
    require(selected == records and acquired_attempts == result['failed_point_attempts_retained'], 'frozen acquisition selection')
    certified = {}
    for record in records:
        p = tuple(record['program']); x = record['x']; value = M.evaluate_polynomial(M.normal_form(p), x)
        require(record['outcome'] == 'CHECKED_POINT_MISMATCH' and str(value) == record['value'], 'independent value certificate')
        target = tuple(Fraction(c) for c in record['task']['coefficients'])
        require(str(M.evaluate_polynomial(target, x)) == record['target_value'] != record['value'], 'independent mismatch witness')
        require((p, x) not in certified, 'duplicate certificate')
        certified[p, x] = sha(record)
    baseline = []; cached = []; uncached = []; uses = []
    real = M.execute
    for data in tests:
        task = M.PolynomialTask(data['task_id'], tuple(Fraction(c) for c in data['coefficients']))
        trajectory = []
        def observing(program, x):
            trajectory.append((tuple(program), x))
            return real(program, x)
        M.execute = observing
        try:
            exact = M.solve(task, M.SearchBudget(2000, 5))
        finally:
            M.execute = real
        require(exact.status == 'VERIFIED_POLYNOMIAL_IDENTITY', 'task capability unresolved')
        baseline.append(json.loads(canonical(exact.as_dict())))
        a = Counter(); b = Counter(); used = Counter()
        for program, x in trajectory:
            a['point_calls'] += 1; a['interpreter_calls'] += 1; a['interpreter_steps'] += len(program)
            b['point_calls'] += 1; b['lookups'] += 1
            if (program, x) in certified:
                b['hits'] += 1; b['avoided_interpreter_steps'] += len(program); used[certified[program, x]] += 1
            else:
                b['interpreter_calls'] += 1; b['interpreter_steps'] += len(program)
        uncached.append(dict(a)); cached.append(dict(b)); uses.append(dict(used))
    modes = ['primitive', 'ordinary', 'ocm-live', 'ocm-revoked', 'ocm-restored']
    require([x['mode'] for x in result['launches']] == modes, 'launch completeness')
    observations = []; pids = set(); total = {}
    for mode, launch in zip(modes, result['launches']):
        report = read(study / (mode + '.json')); pids.add(report['pid'])
        require(launch == read(study / ('LAUNCH-' + mode + '.json')), 'issued observation mismatch')
        require(launch['returncode'] == 0 and launch['pid'] == report['pid'], 'recorded process outcome')
        require(report['request_digest'] == sha(request) and report['tests_digest'] == sha(tests), 'issued data binding')
        require([row['result'] for row in report['rows']] == baseline, 'exact unmodified solver replay disagreement')
        on = mode in ('ordinary', 'ocm-live', 'ocm-restored')
        require([row['counts'] for row in report['rows']] == (cached if on else uncached), 'independent point-work accounting')
        require([row['used'] for row in report['rows']] == (uses if on else [{} for _ in tests]), 'certificate actual-use reconciliation')
        sums = Counter()
        for row in report['rows']: sums.update(row['counts'])
        total[mode] = dict(sums)
        observations.append({'mode': mode, 'launch': launch, 'body_wall_seconds': report['worker_body_wall_seconds'],
                             'solve_wall_seconds': sum(x['wall_seconds'] for x in report['rows']),
                             'peak_rss_kib': report['peak_rss_kib'], 'working_input_bytes': report['working_input_bytes'], 'state': report['state']})
    require(len(pids) == 5 and total == result['totals'], 'process cardinality or totals mismatch')
    require(total['primitive']['interpreter_steps'] - total['ocm-live']['interpreter_steps'] == result['avoided_interpreter_steps'], 'saving arithmetic')
    return {'terminal': 'G3_RETAINED_SOURCE_AND_INDEPENDENT_POINT_ACCOUNTING_RECONCILED', 'source_blobs_checked': checked,
            'training_tasks_replayed': len(training), 'failed_attempts_replayed': acquired_attempts,
            'tasks_replayed_through_original_solver': len(tests), 'reports_reconciled': len(modes), 'totals': total,
            'observations': observations, 'scope': 'Read-only self-authored accounting replay, not another research replicate or independent review.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pr203', type=Path, required=True); p.add_argument('--g3', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    require(not a.out.exists(), 'new audit output required')
    r = {'B': audit_b(a.pr203), 'C': audit_c(a.g3, a.source)}
    a.out.write_bytes(canonical(r) + b'\n')
    print(json.dumps({'B': r['B']['terminal'], 'C': r['C']['terminal']}, sort_keys=True))
