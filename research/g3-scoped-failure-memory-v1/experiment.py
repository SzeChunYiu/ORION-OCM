"""Checked failure-point reuse through the existing solver and OCM runtime.

Research adapter only. No production changes or untrusted code execution.
See PROTOCOL.md for the frozen allocation and deliberately narrow claim.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
from dataclasses import dataclass
from types import MappingProxyType
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

REPO = Path(os.environ.get('OCM_REPO', Path(__file__).resolve().parents[2])).resolve()
sys.path.insert(0, str(REPO / 'src'))
from ocm.learning import methods as M
from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import WarrantProfile, Liveness
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

METHOD_BLOB = '50323a33418b8ef8bb6500ddeba4b9d1f795e9e3'
REAL_EXECUTE = M.execute
SCHEMA = 'g3.failure-point.v1'
BUDGET = M.SearchBudget(2000, 5)
CAP = 64
MODES = ('primitive', 'ordinary', 'ocm-live', 'ocm-revoked', 'ocm-restored')
SCOPE = Scope.of(SCHEMA)


def require(value, reason):
    if not value:
        raise ValueError(reason)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def read(path):
    def unique(pairs):
        d = {}
        for k, v in pairs:
            require(k not in d, 'duplicate JSON key')
            d[k] = v
        return d
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(encoded(obj) + b'\n'); f.flush(); os.fsync(f.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def source_pin():
    raw = Path(M.__file__).read_bytes()
    blob = hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
    require(blob == METHOD_BLOB, 'polynomial engine source drift')
    return blob


def context(budget=BUDGET, environment='rational-total.v1'):
    return {'domain': M.CHECKER, 'source_blob': source_pin(), 'environment': environment,
            'representation': 'exact-rational-coefficients.v1',
            'budget': {'slots': budget.slots, 'max_length': budget.max_length}}


def task_data(task):
    return {'task_id': task.task_id, 'coefficients': [str(c) for c in task.coefficients],
            'fingerprint': task.fingerprint}


def task_from(data):
    require(set(data) == {'task_id', 'coefficients', 'fingerprint'}, 'task fields')
    task = M.PolynomialTask(data['task_id'], tuple(Fraction(c) for c in data['coefficients']))
    require(task.fingerprint == data['fingerprint'], 'task identity')
    return task


def validate_record(record):
    fields = {'schema', 'program', 'x', 'value', 'target_value', 'task', 'context', 'outcome'}
    require(type(record) is dict and set(record) == fields, 'failure record fields')
    require(record['schema'] == SCHEMA and record['outcome'] == 'CHECKED_POINT_MISMATCH', 'not an exact failure')
    p = M.checked_program(record['program']); x = record['x']
    require(type(x) is int and 0 <= x <= 256, 'point range')
    c = record['context']
    require(type(c) is dict and set(c) == set(context()), 'context fields')
    require(c['source_blob'] == source_pin() and c['domain'] == M.CHECKER and
            c['environment'] == 'rational-total.v1' and c['representation'] == 'exact-rational-coefficients.v1', 'source/scope identity')
    budget = M.SearchBudget(**c['budget'])
    require(len(p) <= budget.max_length, 'record outside attempted grammar')
    task = task_from(record['task'])
    # Independent symbolic evaluator, not the interpreter whose call is replaced.
    value = M.evaluate_polynomial(M.normal_form(p), x)
    target = M.evaluate_polynomial(task.coefficients, x)
    require(str(value) == record['value'] and str(target) == record['target_value'] and value != target, 'counterexample refutation failed')
    return (p, x), (value, digest(record))


@dataclass(frozen=True)
class PointIndex:
    context_bytes: bytes
    entries: object

    def __len__(self):
        return len(self.entries)

    def get(self, key):
        return self.entries.get(key)


def index_records(records, requested_context):
    index = {}; meters = Counter()
    for record in records:
        key, value = validate_record(record)
        meters['certificate_checks'] += 1
        meters['certificate_program_steps'] += len(key[0])
        if record['context'] != requested_context:
            meters['out_of_scope'] += 1
            continue
        require(key not in index, 'duplicate failure-point certificate')
        index[key] = value
        meters['index_inserts'] += 1
    return PointIndex(encoded(requested_context), MappingProxyType(index)), dict(meters)


def solve(task, budget=BUDGET, index=None, acquire=False, environment='rational-total.v1'):
    """Scoped process-local substitution; every other solver operation is original."""
    index = {} if index is None else index
    counts = Counter(); used = Counter(); failures = []
    ctx = context(budget, environment)
    if index:
        require(isinstance(index, PointIndex), 'unqualified point index')
        if index.context_bytes != encoded(ctx):
            counts['context_reopens'] += 1
            index = {}
    original = M.execute
    require(original is REAL_EXECUTE, 'nested/concurrent interpreter substitution')
    def point(program, x):
        counts['point_calls'] += 1
        key = (tuple(program), x)
        if index:
            counts['lookups'] += 1
            found = index.get(key)
            if found is not None:
                value, certificate = found
                counts['hits'] += 1
                counts['avoided_interpreter_steps'] += len(program)
                used[certificate] += 1
                return value
        counts['interpreter_calls'] += 1
        counts['interpreter_steps'] += len(program)
        value = REAL_EXECUTE(program, x)
        if acquire:
            target = M.evaluate_polynomial(task.coefficients, x)
            if value != target:
                failures.append({'schema': SCHEMA, 'program': list(program), 'x': x,
                                 'value': str(value), 'target_value': str(target),
                                 'task': task_data(task), 'context': ctx,
                                 'outcome': 'CHECKED_POINT_MISMATCH'})
        return value
    wall, cpu = time.perf_counter(), time.process_time()
    M.execute = point
    try:
        result = M.solve(task, budget)
    finally:
        M.execute = original
    return {'result': result.as_dict(), 'counts': dict(counts), 'used': dict(used),
            'wall_seconds': time.perf_counter() - wall, 'cpu_seconds': time.process_time() - cpu,
            'failures': failures}


def allocate():
    best = {}
    for length in range(6):
        for program in product(M.PRIMITIVES, repeat=length):
            task = M.PolynomialTask('mathematical-task', M.normal_form(program))
            best.setdefault(task.fingerprint, (length, task))
    def take(length, n, salt):
        pool = [t for k, t in best.values() if k == length]
        ordered = sorted(pool, key=lambda t: (hashlib.sha256((salt + '\0' + t.fingerprint).encode()).hexdigest(), t.fingerprint))
        require(len(ordered) >= n, 'insufficient population')
        return [task_data(t) for t in ordered[:n]]
    training = take(4, 8, 'ocm-g3-failure-training-v1-20260909')
    tests = take(5, 16, 'ocm-g3-failure-test-v1-20260909')
    ids = [t['fingerprint'] for t in training + tests]
    require(len(set(ids)) == 24, 'mathematical population overlap')
    return {'training': training, 'test': tests, 'all_identities': len(best)}


def admit(root, records):
    index_records(records, context())
    rt = OCMRuntime(root)
    payload = {'kind': SCHEMA, 'records': records}
    _, evidence = rt.admit_evidence(payload, Channel.PROOF, SCHEMA, scope=SCOPE)
    warrant = WarrantProfile.of({evidence})
    source_id = 'failure-source:' + content_hash(payload)
    rt.admit_object(Atom(source_id, 'proof', warrant, scope=SCOPE, quarantined=True,
                         content_ref=content_hash(payload), meta=tuple(payload.items())), (), 'OBSERVATION')
    object_id = 'failure-memory:' + content_hash(payload)
    edge = Hyperedge('support:' + object_id, (source_id,), (object_id,), 'SUPPORT', warrant=warrant)
    rt.admit_object(Atom(object_id, 'procedure', warrant, scope=SCOPE,
                         content_ref=content_hash(payload), meta=tuple(payload.items())), (edge,), 'OBSERVATION')
    rt.persist()
    return {'object_id': object_id, 'evidence': evidence, 'records_digest': digest(records)}


def load_ocm(root, identity):
    rt = OCMRuntime(root)
    atom = rt.state.ks.atom_map().get(identity['object_id'])
    require(atom is not None and atom.atom_type == 'procedure', 'missing memory object')
    payload = dict(atom.meta)
    require(content_hash(payload) == atom.content_ref and payload.get('kind') == SCHEMA, 'stored object identity')
    records = payload['records']
    require(digest(records) == identity['records_digest'], 'record identity')
    live = atom.liveness(rt.state.revoked) is Liveness.LIVE
    return (records if live else []), {'live': live, 'field_hash': rt.state.kso_state_hash,
                                        'evidence_epoch': rt.state.evidence_epoch,
                                        'event_count': len(rt.trace())}


def bytes_under(path):
    return sum(p.stat().st_size for p in Path(path).rglob('*') if p.is_file())


def worker(root, mode, output):
    started, cpu = time.perf_counter(), time.process_time()
    require(mode in MODES, 'unknown arm')
    request = read(root / 'REQUEST.json')
    require(request['engine'] == source_pin() and request['source_sha256'] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'worker source binding')
    tests = read(root / 'TESTS.json')
    require(digest(tests) == request['tests_digest'], 'issued population mismatch')
    phase = time.perf_counter()
    state = None
    if mode.startswith('ocm-'):
        records, state = load_ocm(root / 'lineage', request['memory'])
        require(state['live'] == (mode != 'ocm-revoked'), 'wrong persisted support state')
    elif mode == 'ordinary':
        records = read(root / 'ORDINARY.json')
        require(digest(records) == request['memory']['records_digest'], 'ordinary memory identity')
    else:
        records = []
    load_wall = time.perf_counter() - phase
    phase = time.perf_counter()
    index, build = index_records(records, context())
    build_wall = time.perf_counter() - phase
    rows = []
    for data in tests:
        row = solve(task_from(data), index=index)
        rows.append(row)
    report = {'mode': mode, 'pid': os.getpid(), 'ppid': os.getppid(), 'request_digest': digest(request),
              'tests_digest': digest(tests), 'memory_digest': digest(records), 'state': state,
              'load_wall_seconds': load_wall, 'index_wall_seconds': build_wall, 'index_counts': build,
              'rows': rows, 'worker_body_wall_seconds': time.perf_counter() - started,
              'worker_body_cpu_seconds': time.process_time() - cpu,
              'worker_body_scope': 'Excludes interpreter startup and imports; whole-process costs are parent-observed in launches',
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'peak_rss_scope': 'Linux process high-water RSS; not additive',
              'working_input_bytes': (root / 'TESTS.json').stat().st_size +
                 (bytes_under(root / 'lineage') if mode.startswith('ocm-') else
                  ((root / 'ORDINARY.json').stat().st_size if mode == 'ordinary' else 0))}
    write(output, report)


def reconcile(tests, reports, request_digest, launches):
    require(type(tests) is list and len(tests) > 0, 'empty population')
    expected = [task_from(t).fingerprint for t in tests]
    require(len(set(expected)) == len(expected), 'duplicate population')
    require([r['mode'] for r in reports] == list(MODES), 'missing/duplicate/ordered arms')
    require([a['mode'] for a in launches] == list(MODES), 'missing issued process observations')
    require(all(a['returncode'] == 0 and a['pid'] == r['pid'] and r['ppid'] == os.getpid()
                for a, r in zip(launches, reports)), 'actual process/exit binding')
    require(len({r['pid'] for r in reports}) == len(MODES), 'not distinct worker processes')
    for report in reports:
        require(report['request_digest'] == request_digest and report['tests_digest'] == digest(tests), 'request binding')
        require([r['result']['task_fingerprint'] for r in report['rows']] == expected, 'truncated/foreign population')
        for task, row in zip(tests, report['rows']):
            result = row['result']
            if result['status'] == 'VERIFIED_POLYNOMIAL_IDENTITY':
                require(M.normal_form(tuple(result['program'])) == task_from(task).coefficients, 'invalid answer')
    base = [r['result'] for r in reports[0]['rows']]
    for report in reports[1:]:
        require([r['result'] for r in report['rows']] == base, 'solver refinement mismatch')
    ordinary, live, revoked, restored = reports[1:]
    for a, b in ((ordinary, live), (live, restored), (reports[0], revoked)):
        require([(x['counts'], x['used']) for x in a['rows']] == [(x['counts'], x['used']) for x in b['rows']], 'causal work/usage mismatch')
    require(ordinary['memory_digest'] == live['memory_digest'] == restored['memory_digest'], 'parent memory mismatch')
    require(live['state']['live'] and not revoked['state']['live'] and restored['state']['live'], 'liveness mismatch')
    totals = {}
    for report in reports:
        sums = Counter()
        for row in report['rows']:
            sums.update(row['counts'])
        totals[report['mode']] = dict(sums)
    saving = totals['primitive'].get('interpreter_steps', 0) - totals['ocm-live'].get('interpreter_steps', 0)
    hits = totals['ocm-live'].get('hits', 0)
    return {'terminal': 'FAILURE_POINT_MEMORY_USEFUL_AT_SCOPE' if saving > 0 and hits > 0 else 'FAILURE_MEMORY_NOT_USEFUL_AT_SCOPE',
            'parent_terminal': 'PARENT_SUFFICIENT_FOR_FAILURE_POINT_MECHANISM', 'totals': totals,
            'avoided_interpreter_steps': saving, 'all_results_equal': True,
            'lifetime_payback_established': False, 'full_G3_2_closed': False}


def study(out):
    require(not out.exists(), 'new output directory required')
    out.mkdir(parents=True)
    wall, cpu = time.perf_counter(), time.process_time()
    source_pin()
    started = time.perf_counter(); population = allocate()
    allocation_wall = time.perf_counter() - started
    write(out / 'ALLOCATION.json', population)
    write(out / 'TESTS.json', population['test'])
    rows = []; records = []; seen = set()
    started = time.perf_counter()
    for task in population['training']:
        row = solve(task_from(task), acquire=True)
        rows.append(row)
        for record in row['failures']:
            key = (tuple(record['program']), record['x'])
            if key not in seen and len(records) < CAP:
                validate_record(record); records.append(record); seen.add(key)
    acquisition_wall = time.perf_counter() - started
    write(out / 'TRAINING.json', rows)
    write(out / 'ORDINARY.json', records)
    started = time.perf_counter(); identity = admit(out / 'lineage', records)
    admission_wall = time.perf_counter() - started
    request = {'schema': SCHEMA + '.request', 'engine': source_pin(), 'memory': identity,
               'tests_digest': digest(population['test']),
               'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    write(out / 'REQUEST.json', request)
    reports = []; launches = []; lifecycle = []
    for mode in MODES:
        if mode in ('ocm-revoked', 'ocm-restored'):
            started = time.perf_counter()
            rt = OCMRuntime(out / 'lineage')
            if mode == 'ocm-revoked': rt.revoke([identity['evidence']])
            else: rt.reinstate([identity['evidence']])
            rt.persist()
            lifecycle.append({'mode': mode, 'wall_seconds': time.perf_counter() - started,
                              'field_hash': rt.state.kso_state_hash, 'evidence_epoch': rt.state.evidence_epoch})
        destination = out / (mode + '.json')
        cache = out / 'empty-pycache' / mode
        cache.mkdir(parents=True, exist_ok=False)
        command = [sys.executable, '-I', '-S', '-B', '-X', 'pycache_prefix=' + str(cache), str(Path(__file__).resolve()), '--worker', str(out), mode, str(destination)]
        started = time.perf_counter()
        usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
        with (out / (mode + '.log')).open('xb') as log:
            proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                    env={**os.environ, 'OCM_REPO': str(REPO)})
            try:
                proc.wait(timeout=120)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait()
                write(out / ('TIMEOUT-' + mode + '.json'), {'pid': proc.pid, 'returncode': proc.returncode, 'terminal': 'UNKNOWN'})
                raise
        usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        launches.append({'mode': mode, 'pid': proc.pid, 'returncode': proc.returncode, 'wall_seconds': time.perf_counter() - started,
                         'user_cpu_seconds': usage_after.ru_utime - usage_before.ru_utime,
                         'system_cpu_seconds': usage_after.ru_stime - usage_before.ru_stime})
        write(out / ('LAUNCH-' + mode + '.json'), launches[-1])
        require(proc.returncode == 0, 'worker failed: ' + mode)
        report = read(destination); reports.append(report)
    result = reconcile(population['test'], reports, digest(request), launches)
    result.update({'source': request['source_sha256'], 'engine': source_pin(),
                   'train_tasks': len(rows), 'test_tasks': len(population['test']),
                   'failed_point_attempts_retained': sum(len(r['failures']) for r in rows),
                   'certificates': len(records), 'allocation_wall_seconds': allocation_wall,
                   'acquisition_wall_seconds': acquisition_wall, 'admission_wall_seconds': admission_wall,
                   'lifecycle': lifecycle, 'launches': launches, 'controller_wall_seconds': time.perf_counter() - wall,
                   'controller_cpu_seconds': time.process_time() - cpu,
                   'retained_bytes_before_summary': bytes_under(out), 'python': sys.version,
                   'scope': 'Authored development, exact point memoization parent; not protected replication, complete G3.2, or whole-lifetime economics.'})
    write(out / 'RESULT.json', result)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    if len(sys.argv) == 5 and sys.argv[1] == '--worker':
        worker(Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4]))
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--out', type=Path, required=True)
        study(parser.parse_args().out.resolve())
