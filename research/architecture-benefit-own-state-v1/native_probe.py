"""Source-bound native OCM method-lane attribution pilot; exposed, not protected.

Three isolated arms use the same native solver. The ordinary parent is deliberately
allowed the same endogenous fragment miner, validation data and search/checker.
Its JSON persistence is single-writer only; this is not a full OCM-contract parent.
No protected corpus is read. Timings are descriptive, not IID admission evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time

ARMS = ('primitive', 'ordinary_fragments', 'ocm_fragments')
METHOD_BLOB = '50323a33418b8ef8bb6500ddeba4b9d1f795e9e3'


def dump_new(path, value):
    with Path(path).open('x', encoding='utf-8') as file:
        json.dump(value, file, sort_keys=True, indent=2)
        file.write('\n')


def save_plain(path, value):
    # Strong single-writer snapshot parent: atomic replace + file/directory fsync.
    tmp = path.with_suffix('.tmp')
    with tmp.open('x', encoding='utf-8') as file:
        json.dump(value, file, sort_keys=True, separators=(',', ':'))
        file.flush()
        os.fsync(file.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def worker(arm, root):
    from itertools import product
    from ocm.learning import methods as M
    from ocm.runtime.ocm_runtime import OCMRuntime
    source = Path(M.__file__).read_bytes()
    if hashlib.sha1(f'blob {len(source)}\0'.encode() + source).hexdigest() != METHOD_BLOB:
        raise RuntimeError('native method source drift')
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    training_tasks = (M.PolynomialTask('train-a', (2, 2, 1)), M.PolynomialTask('train-b', (2, 4, 2)))
    validation = (M.PolynomialTask('validation-a', (0, 2, 1)), M.PolynomialTask('validation-b', (1, 4, 6, 4, 1)))
    excluded = {t.fingerprint for t in training_tasks + validation}
    universe = {}
    for length in range(5):
        for program in product(M.PRIMITIVES, repeat=length):
            task = M.PolynomialTask('pilot', M.normal_form(program))
            if task.fingerprint not in excluded:
                universe[task.fingerprint] = task
    # Selection uses mathematical task identity, never measured solve outcomes.
    tasks = tuple(universe[key] for key in sorted(universe)[:24])
    if len(tasks) != 24:
        raise RuntimeError('pilot population changed')
    training = tuple((task, M.solve(task)) for task in training_tasks)
    slots = sum(result.slots for _, result in training)
    plain = {'source_blob': METHOD_BLOB, 'revoked': False, 'results': {}, 'generator': None}
    snapshot = root / 'ordinary.json'
    rt, receipt = None, None
    if arm == 'ocm_fragments':
        rt = OCMRuntime(root / 'runtime')
        receipt = M.admit_generator(rt, training, validation)
        method = M.load_generator(rt, receipt['generator_id'])
        validation_report = receipt['validation']
    elif arm == 'ordinary_fragments':
        method = M.learn_generator(training)
        validation_report = M.validate_generator(method, validation)
        if not validation_report['accepted']:
            raise RuntimeError('frozen native generator no longer validates')
        plain['generator'] = {'fragments': method.fragments, 'training_tasks': method.training_tasks,
                              'fingerprint': method.fingerprint, 'validation': validation_report,
                              'training_proofs': [result.as_dict() for _, result in training]}
    else:
        method = M.GeneratorMethod()
        validation_report = None
    if validation_report:
        slots += sum(row[which]['slots'] for row in validation_report['held_out']
                     for which in ('baseline', 'candidate'))
    if rt is None:
        save_plain(snapshot, plain)
    trace, usage = [], []
    for i, task in enumerate(tasks):
        if i in (8, 16):
            if rt is not None:
                if i == 16:
                    rt.revoke((receipt['training'][0]['evidence_id'],))
                rt.persist()
                rt = OCMRuntime(root / 'runtime')
                try:
                    method = M.load_generator(rt, receipt['generator_id'])
                    available = True
                except ValueError:
                    method, available = M.GeneratorMethod(), False
                if available != (i == 8):
                    raise RuntimeError('native generator lifecycle failure')
            else:
                if i == 16:
                    plain['revoked'] = True
                save_plain(snapshot, plain)
                plain = json.loads(snapshot.read_text())
                if plain['source_blob'] != METHOD_BLOB:
                    raise RuntimeError('plain source custody failure')
                payload = plain['generator']
                if payload is not None and not plain['revoked']:
                    method = M.GeneratorMethod(tuple(tuple(p) for p in payload['fragments']),
                                               tuple(payload['training_tasks']))
                    if method.fingerprint != payload['fingerprint']:
                        raise RuntimeError('ordinary generator identity failure')
                else:
                    method = M.GeneratorMethod()
            trace.append(('RESTART' if i == 8 else 'WITHDRAW_AND_RESTART',))
        result = M.solve(task, M.SearchBudget(), method)
        if not M.verify_solution(task, result):
            raise RuntimeError('native exact answer failure')
        slots += result.slots
        usage.append({'task': task.fingerprint, 'slots': result.slots,
                      'program': result.program, 'method': method.fingerprint,
                      'fragment_available': bool(method.fragments)})
        trace.append((task.fingerprint, tuple(str(c) for c in M.normal_form(result.program))))
        if rt is not None:
            M.admit_solution(rt, task, result)
        else:
            plain['results'][task.fingerprint] = result.as_dict()
            save_plain(snapshot, plain)
    if rt is not None:
        rt.persist()
        replay = OCMRuntime(root / 'runtime')
        if len(replay.state.ks.atoms) != len(rt.state.ks.atoms):
            raise RuntimeError('final native replay mismatch')
    else:
        save_plain(snapshot, plain)
        if len(json.loads(snapshot.read_text())['results']) != len(tasks):
            raise RuntimeError('ordinary final replay mismatch')
    disk = sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
    return {'arm': arm, 'method_blob': METHOD_BLOB, 'queries': len(tasks),
            'total_search_slots_including_training_and_validation': slots,
            'query_slots': sum(row['slots'] for row in usage), 'usage': usage,
            'projected_trace': trace, 'final_serialized_bytes': disk,
            'peak_rss_platform_units': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'scope': 'exposed method-lane pilot; not full architecture evaluation'}


def run(repetitions):
    reports = []
    with tempfile.TemporaryDirectory(prefix='ocm-net-benefit-') as temp:
        for rep in range(repetitions):
            # Rotate fixed execution order to expose, not eliminate, order effects.
            order = ARMS[rep % len(ARMS):] + ARMS[:rep % len(ARMS)]
            current = {}
            for arm in order:
                cpu0 = resource.getrusage(resource.RUSAGE_CHILDREN)
                wall0 = time.perf_counter_ns()
                proc = subprocess.run([sys.executable, '-B', __file__, '--arm', arm,
                                       '--root', str(Path(temp) / f'{rep}-{arm}')],
                                      capture_output=True, text=True, timeout=180, check=True)
                wall = time.perf_counter_ns() - wall0
                cpu1 = resource.getrusage(resource.RUSAGE_CHILDREN)
                row = json.loads(proc.stdout)
                row.update(repetition=rep, whole_child_wall_ns=wall,
                           whole_child_cpu_seconds=(cpu1.ru_utime + cpu1.ru_stime
                                                    - cpu0.ru_utime - cpu0.ru_stime))
                current[arm] = row
                reports.append(row)
            if any(current[a]['projected_trace'] != current['primitive']['projected_trace'] for a in ARMS):
                raise RuntimeError('protected projection differs across arms')
            # Same conventional discovery algorithm -> same learned search traces.
            if current['ordinary_fragments']['usage'] != current['ocm_fragments']['usage']:
                raise RuntimeError('component transplant parity changed')
    return {'schema': 'ocm.architecture-net-benefit.native-pilot.v1', 'rows': reports,
            'terminal': 'NATIVE_COMPONENT_ATTRIBUTION_CONTROL_COMPLETE',
            'whole_architecture_net_benefit_established': False,
            'ordinary_parent_qualified_for_full_ocm_contract': False,
            'claim_boundary': 'Same learned-search mechanism transferred to conventional persistence; '
                              'timings descriptive; full provenance/durability equivalence and fresh ecology open',
            'protected_evaluation_run': False, 'ml_router_trained': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arm', choices=ARMS)
    parser.add_argument('--root', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--repetitions', type=int, default=3)
    args = parser.parse_args()
    if args.arm:
        if args.root is None:
            parser.error('--root required for worker')
        print(json.dumps(worker(args.arm, args.root), sort_keys=True))
    else:
        if args.out is None or not 1 <= args.repetitions <= 10:
            parser.error('--out required and repetitions must be in 1..10')
        result = run(args.repetitions)
        dump_new(args.out, result)
        print(json.dumps({'terminal': result['terminal'], 'processes': len(result['rows'])}))


if __name__ == '__main__':
    main()
