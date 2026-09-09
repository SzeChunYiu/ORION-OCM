"""Execute the frozen representation continuation on the actual #205 field root.

No new domain core, no modifications to frozen studies, no learning on test rows.
Use --out NEW_DIRECTORY --predecessor COMPLETED_LOCAL_205_STUDY.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment as E
import representation as R

MODES = ('primitive', 'ordinary-point', 'ordinary-prefix', 'ocm-point', 'ocm-selected',
         'representation-revoked', 'memory-revoked', 'restored', 'reset-ocm')
HERE = Path(__file__).resolve().parent


def hashfile(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_manifest():
    files = sorted(p for p in (E.REPO / 'src').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    files += [HERE / n for n in ('experiment.py', 'representation.py', 'continue_lineage.py',
                                 'REPRESENTATION_PROTOCOL.md')]
    return {str(p.relative_to(E.REPO)): hashfile(p) for p in files}


def allocate(old):
    excluded = {t['fingerprint'] for t in old['training'] + old['test']}
    E.require(len(excluded) == 24, 'incomplete predecessor population')
    best = {}
    for length in range(6):
        for p in product(E.M.PRIMITIVES, repeat=length):
            t = E.M.PolynomialTask('mathematical-task', E.M.normal_form(p))
            best.setdefault(t.fingerprint, (length, t))
    def select(length, count, salt):
        candidates = [t for n, t in best.values() if n == length and t.fingerprint not in excluded]
        candidates.sort(key=lambda t: (hashlib.sha256((salt + '\0' + t.fingerprint).encode()).hexdigest(), t.fingerprint))
        E.require(len(candidates) >= count, 'insufficient unexposed identities')
        return [E.task_data(t) for t in candidates[:count]]
    validation = select(4, 8, 'ocm-g3-representation-validation-v1-20260909')
    test = select(5, 64, 'ocm-g3-representation-test-v1-20260909')
    new = [t['fingerprint'] for t in validation + test]
    E.require(len(set(new)) == 72 and not (set(new) & excluded), 'new sample overlap')
    return {'validation': validation, 'test': test, 'excluded_predecessor': sorted(excluded),
            'all_grammar_identities': len(best), 'scope': 'locally frozen authored development, not protected replication'}


def worker(root, mode, destination):
    start, cpu = time.perf_counter(), time.process_time()
    E.require(mode in MODES, 'foreign mode')
    request = E.read(root / 'REQUEST.json')
    E.require(source_manifest() == request['source_manifest'], 'worker source drift')
    tests = E.read(root / 'TESTS.json')
    E.require(E.digest(tests) == request['tests_digest'], 'foreign task population')
    records = []; state = None
    phase = time.perf_counter()
    lineage = (root / request['lineage_relpath']).resolve()
    if mode in ('ordinary-point', 'ordinary-prefix'):
        records = E.read(root / 'ORDINARY.json')
        E.require(E.digest(records) == request['memory']['records_digest'], 'foreign ordinary records')
        kind = 'P1' if mode == 'ordinary-point' else 'P2'
    elif mode == 'primitive':
        kind = 'P0'
    elif mode == 'reset-ocm':
        reset = root / 'reset-lineage'
        E.require(not reset.exists(), 'reset must be fresh')
        rt = E.OCMRuntime(reset); rt.persist()
        E.require(request['memory']['object_id'] not in rt.state.ks.atom_map(), 'reset retained learned state')
        kind = 'P0'
        state = {'memory_live': False, 'representation_live': False,
                 'field_hash': rt.state.kso_state_hash, 'event_count': len(rt.trace()),
                 'evidence_epoch': rt.state.evidence_epoch}
    elif mode == 'ocm-point':
        records, old = E.load_ocm(lineage, request['memory'])
        E.require(old['live'], 'point memory withdrawn unexpectedly')
        kind = 'P1'; state = old
    else:
        records, kind, state = R.load(lineage, request['memory'], request['representation'])
        expected = {'ocm-selected': (True, True), 'representation-revoked': (True, False),
                    'memory-revoked': (False, False), 'restored': (True, True)}[mode]
        E.require((state['memory_live'], state['representation_live']) == expected, 'wrong persisted phase')
    loading = time.perf_counter() - phase
    phase = time.perf_counter(); index, build_counts = R.build(records, kind)
    building = time.perf_counter() - phase
    rows = [R.solve(E.task_from(t), index=index) for t in tests]
    report = {'mode': mode, 'kind': kind, 'pid': os.getpid(), 'ppid': os.getppid(),
              'request_digest': E.digest(request), 'tests_digest': E.digest(tests),
              'records_digest': E.digest(records), 'state': state, 'rows': rows,
              'load_wall_seconds': loading, 'build_wall_seconds': building, 'build_counts': build_counts,
              'worker_body_wall_seconds': time.perf_counter() - start,
              'worker_body_cpu_seconds': time.process_time() - cpu,
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'physical_scope': 'body excludes imports/startup; Linux RSS high-water is not additive',
              'input_storage_bytes': (root / 'TESTS.json').stat().st_size +
                  (E.bytes_under(lineage) if mode not in ('primitive', 'ordinary-point', 'ordinary-prefix', 'reset-ocm')
                   else ((root / 'ORDINARY.json').stat().st_size if mode.startswith('ordinary-') else 0))}
    E.write(destination, report)


def reconcile(tests, reports, request, launches):
    E.require(type(tests) is list and len(tests) == 64, 'complete registered test population required')
    expected = [E.task_from(t).fingerprint for t in tests]
    E.require(len(set(expected)) == len(expected), 'duplicate population')
    E.require([r['mode'] for r in reports] == list(MODES), 'complete ordered arm population required')
    E.require([a['mode'] for a in launches] == list(MODES), 'complete launches required')
    E.require(len({r['pid'] for r in reports}) == len(MODES), 'distinct processes required')
    for report, launch in zip(reports, launches):
        E.require(report['pid'] == launch['pid'] and report['ppid'] == request['controller_pid'] and
                  launch['returncode'] == 0, 'process/exit binding')
        E.require(report['request_digest'] == E.digest(request) and report['tests_digest'] == E.digest(tests), 'request binding')
        E.require([row['result']['task_fingerprint'] for row in report['rows']] == expected, 'truncated/foreign task population')
        for task, row in zip(tests, report['rows']):
            result = row['result']
            if result['status'] == 'VERIFIED_POLYNOMIAL_IDENTITY':
                E.require(E.M.normal_form(tuple(result['program'])) == E.task_from(task).coefficients, 'false solution')
    baseline = [row['result'] for row in reports[0]['rows']]
    for report in reports:
        E.require([row['result'] for row in report['rows']] == baseline, 'changed first solution/search')
    by = {r['mode']: r for r in reports}
    def signatures(mode):
        return [(r['counts'], r['used']) for r in by[mode]['rows']]
    for a, b in (('ordinary-point', 'ocm-point'), ('ordinary-point', 'representation-revoked'),
                 ('primitive', 'memory-revoked'), ('primitive', 'reset-ocm'), ('ocm-selected', 'restored')):
        E.require(signatures(a) == signatures(b), 'counterfactual mismatch: ' + a + '/' + b)
    selected = request['selected']
    parent = {'P0': 'primitive', 'P1': 'ordinary-point', 'P2': 'ordinary-prefix'}[selected]
    E.require(signatures('ocm-selected') == signatures(parent), 'selected strongest available representation parent mismatch')
    E.require(by['representation-revoked']['state']['memory_live'] and
              not by['representation-revoked']['state']['representation_live'] and
              not by['memory-revoked']['state']['memory_live'] and
              by['restored']['state']['representation_live'], 'invalid support interventions')
    totals = {mode: R.totals(by[mode]['rows']) for mode in MODES}
    baseline_steps = totals['primitive'].get('interpreter_steps', 0)
    point_steps = totals['ordinary-point'].get('interpreter_steps', 0)
    selected_steps = totals['ocm-selected'].get('interpreter_steps', 0)
    positive = selected == 'P2' and selected_steps < point_steps and totals['ocm-selected'].get('positive_proper_prefix_hits', 0) > 0
    return {'terminal': ('PREFIX_REPRESENTATION_CAUSALLY_USEFUL_AT_INTERPRETER_STEP_SCOPE' if positive
                         else 'PREFIX_REPRESENTATION_NOT_SUPPORTED_AT_REGISTERED_SCOPE'),
            'parent_terminal': 'PARENT_SUFFICIENT_FOR_PREFIX_REPRESENTATION',
            'selected': selected, 'totals': totals, 'all_first_results_equal': True,
            'saving_vs_primitive_steps': baseline_steps - selected_steps,
            'saving_vs_point_steps': point_steps - selected_steps,
            'architectural_advantage_established': False,
            'full_G3_3_or_G3_4_closed': False, 'full_lifetime_payback_established': False}


def study(predecessor, out):
    E.require(not out.exists(), 'fresh output directory required')
    out.mkdir(parents=True)
    start, cpu = time.perf_counter(), time.process_time()
    source = source_manifest()
    E.write(out / 'SOURCE-FREEZE.json', {'files': source, 'sha256': E.digest(source),
             'timing': 'before first new allocation, validation or test solve', 'independent_registration': False})
    old_request = E.read(predecessor / 'REQUEST.json')
    old_result = E.read(predecessor / 'RESULT.json')
    old_population = E.read(predecessor / 'ALLOCATION.json')
    records = E.read(predecessor / 'ORDINARY.json')
    E.require(old_request['source_sha256'] == hashfile(HERE / 'experiment.py') and
              old_request['engine'] == E.source_pin() and
              old_result['all_results_equal'] and len(records) == 64, 'invalid predecessor')
    memory = old_request['memory']; lineage = predecessor / 'lineage'
    E.require(E.load_ocm(lineage, memory)[1]['live'], 'predecessor must end restored')
    ledger_before = (lineage / 'ledger.jsonl').read_bytes()
    (out / 'PREDECESSOR-LEDGER.jsonl').write_bytes(ledger_before)
    E.write(out / 'PREDECESSOR.json', {'relative_path': os.path.relpath(predecessor, out),
            'files': {n: hashfile(predecessor / n) for n in ('REQUEST.json', 'RESULT.json', 'ALLOCATION.json', 'ORDINARY.json', 'TRAINING.json')},
            'ledger_bytes': len(ledger_before), 'ledger_sha256': hashlib.sha256(ledger_before).hexdigest(),
            'origin': 'same local exposed #205 reproduction, not remote historical lineage',
            'memory': memory})
    phase = time.perf_counter(); population = allocate(old_population)
    allocation_wall = time.perf_counter() - phase
    E.write(out / 'ALLOCATION.json', population); E.write(out / 'TESTS.json', population['test'])
    E.write(out / 'ORDINARY.json', records)
    training = E.read(predecessor / 'TRAINING.json')
    programs = sorted({tuple(r['program']) for row in training for r in row['failures']})
    phase = time.perf_counter()
    old_obs = R.observer_certificate(programs, (0,))
    new_obs = R.observer_certificate(programs, (0, 1))
    diagnosis = {'before': old_obs, 'after': new_obs, 'old_receipt_still_valid_in_old_scope': R.certificate_applicable(old_obs, programs, (0,)),
                 'old_receipt_valid_in_expanded_scope': R.certificate_applicable(old_obs, programs, (0, 1)),
                 'diagnosis': R.diagnose(observation_witness=new_obs) if new_obs['witness'] else 'CANNOT_CHECK',
                 'timeout_diagnosis': R.diagnose(solver_status='TIMEOUT'),
                 'construction_wall_seconds': time.perf_counter() - phase,
                 'population': 'all actual predecessor failed-attempt program identities',
                 'program_count': len(programs), 'not_full_diagnostic_taxonomy': True}
    E.write(out / 'REPRESENTATION-WITNESS.json', diagnosis)
    validation = {}; build_records = {}
    phase = time.perf_counter()
    for kind in R.KINDS:
        build_start = time.perf_counter(); index, meters = R.build(records, kind)
        build_records[kind] = {'counts': meters, 'wall_seconds': time.perf_counter() - build_start}
        validation[kind] = [R.solve(E.task_from(t), index=index) for t in population['validation']]
    selected = R.choose(validation)
    selection = {'selected': selected, 'rule': 'interpreter_steps, then lookup counts, then P0/P1/P2',
                 'validation': validation, 'build': build_records,
                 'keys': {k: list(R.selection_key(k, validation[k])) for k in R.KINDS},
                 'wall_seconds': time.perf_counter() - phase,
                 'not_a_physical_cost_objective': True}
    E.write(out / 'SELECTION.json', selection)
    phase = time.perf_counter()
    rep = R.admit(lineage, memory, selected, E.digest(selection), E.digest(diagnosis))
    admission_wall = time.perf_counter() - phase
    E.require((lineage / 'ledger.jsonl').read_bytes().startswith(ledger_before), 'predecessor ledger replaced')
    request = {'schema': R.SCHEMA + '.request', 'source_manifest': source, 'engine': E.source_pin(),
               'memory': memory, 'representation': rep, 'selected': selected,
               'tests_digest': E.digest(population['test']), 'selection_digest': E.digest(selection),
               'lineage_relpath': os.path.relpath(lineage, out), 'controller_pid': os.getpid()}
    E.write(out / 'REQUEST.json', request)
    reports = []; launches = []; revisions = []
    for mode in MODES:
        if mode in ('representation-revoked', 'memory-revoked', 'restored'):
            phase = time.perf_counter(); rt = E.OCMRuntime(lineage)
            if mode == 'representation-revoked': rt.revoke([rep['assurance']])
            elif mode == 'memory-revoked': rt.revoke([memory['evidence']])
            else: rt.reinstate([rep['assurance'], memory['evidence']])
            rt.persist()
            revisions.append({'mode': mode, 'wall_seconds': time.perf_counter() - phase,
                              'field_hash': rt.state.kso_state_hash, 'evidence_epoch': rt.state.evidence_epoch})
        snapshot = out / 'snapshots' / mode
        shutil.copytree(lineage, snapshot)
        cache = out / 'empty-pycache' / mode; cache.mkdir(parents=True)
        command = [sys.executable, '-I', '-S', '-B', '-X', 'pycache_prefix=' + str(cache),
                   str(Path(__file__).resolve()), '--worker', str(out), mode, str(out / (mode + '.json'))]
        phase = time.perf_counter(); before = resource.getrusage(resource.RUSAGE_CHILDREN)
        with (out / (mode + '.log')).open('xb') as log:
            proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                    env={**os.environ, 'OCM_REPO': str(E.REPO)})
            try:
                proc.wait(timeout=120)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait()
                E.write(out / ('TIMEOUT-' + mode + '.json'), {'pid': proc.pid, 'returncode': proc.returncode, 'terminal': 'UNKNOWN'})
                raise
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        launch = {'mode': mode, 'pid': proc.pid, 'returncode': proc.returncode,
                  'wall_seconds': time.perf_counter() - phase,
                  'user_cpu_seconds': after.ru_utime - before.ru_utime,
                  'system_cpu_seconds': after.ru_stime - before.ru_stime}
        E.write(out / ('LAUNCH-' + mode + '.json'), launch); launches.append(launch)
        E.require(proc.returncode == 0, 'worker failed: ' + mode)
        reports.append(E.read(out / (mode + '.json')))
    result = reconcile(population['test'], reports, request, launches)
    E.require(source_manifest() == source, 'execution source changed')
    final_ledger = (lineage / 'ledger.jsonl').read_bytes()
    E.require(final_ledger.startswith(ledger_before), 'lineage ancestor lost')
    result.update({'source_manifest_digest': E.digest(source), 'predecessor_ledger_preserved': True,
                   'predecessor_ledger_bytes': len(ledger_before), 'final_ledger_bytes': len(final_ledger),
                   'validation_tasks': 8, 'test_tasks': 64, 'test_arms': 9, 'launches': launches,
                   'allocation_wall_seconds': allocation_wall, 'selection_wall_seconds': selection['wall_seconds'],
                   'representation_admission_wall_seconds': admission_wall, 'revisions': revisions,
                   'controller_wall_seconds': time.perf_counter() - start,
                   'controller_cpu_seconds': time.process_time() - cpu,
                   'predecessor_acquisition_wall_seconds': old_result['acquisition_wall_seconds'],
                   'predecessor_admission_wall_seconds': old_result['admission_wall_seconds'],
                   'diagnostic_terminal': diagnosis['diagnosis'], 'snapshot_bytes': E.bytes_under(out / 'snapshots'),
                   'live_lineage_bytes': E.bytes_under(lineage), 'retained_bytes_before_result': E.bytes_under(out),
                   'python': sys.version,
                   'scope': 'authored same-field C-to-D continuation; not three earned generations or cross-domain/protected completion'})
    E.write(out / 'RESULT.json', result)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    if len(sys.argv) == 5 and sys.argv[1] == '--worker':
        worker(Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4]))
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--predecessor', required=True, type=Path)
        parser.add_argument('--out', required=True, type=Path)
        args = parser.parse_args()
        study(args.predecessor.resolve(), args.out.resolve())
