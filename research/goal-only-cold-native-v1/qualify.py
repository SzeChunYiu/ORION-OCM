"""Observe an authored cold-process lifecycle; never opens a scientific task corpus."""
from __future__ import annotations
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from custody import (HERE, encoded, parse, raw_id, checked_read, checked_sources,
                     adapter_sources, require, store)

MODES = ('enabled', 'resident-disabled', 'restored')
PLAN = ('producer', 'ordinary-enabled', 'ocm-enabled', 'revoke',
        'ordinary-resident-disabled', 'ocm-resident-disabled', 'reinstate',
        'ordinary-restored', 'ocm-restored')


def request(producer: dict, mode: str, route: str, lease=None) -> dict:
    return {'schema': 'ordinary.cold-native.request.v1', 'task': producer['task'],
            'mode': mode, 'bundle': producer['bundle'], 'label': 'cold-issued-goal',
            'holes': ['cold-input-0'], 'nonce': uuid.uuid4().hex, 'route': route,
            'state': None if route == 'ordinary' else
            {'binding': producer['state_binding'], 'lease': lease}}


def launch(root: Path, name: str, operation: str, issued=None, timeout=60.0) -> dict:
    """Hard parent wait bound; native subprocesses are synchronous in this worker."""
    cmd = [sys.executable, '-I', '-B', str(HERE / 'worker.py'), operation,
           '--output', str(root / name)]
    if issued is not None:
        raw = encoded(issued)
        path = root / (name + '.request.json')
        store(path, raw)
        cmd += ['--request', str(path), '--request-sha256', raw_id(raw)['sha256'],
                '--bundle', str(root / 'producer/bundle')]
        if issued['route'] == 'ocm':
            cmd += ['--state', str(root / 'producer/state'), '--state-binding',
                    str(root / 'producer/state-binding.json')]
    environment = {'PATH': os.defpath, 'LANG': 'C.UTF-8', 'PYTHONHASHSEED': '0'}
    start = time.perf_counter()
    timed_out = False
    # No inherited file descriptors or Python objects convey a proof/search cache.
    child = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=environment, close_fds=True)
    try:
        stdout, stderr = child.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        child.kill()
        stdout, stderr = child.communicate()
    wall = time.perf_counter() - start
    store(root / (name + '.stdout'), stdout)
    store(root / (name + '.stderr'), stderr)
    observation_path = root / name / 'observation.json'
    observation = observation_path.read_bytes() if observation_path.is_file() else None
    receipt = {'schema': 'ordinary.cold-native.launch.v1', 'name': name, 'operation': operation,
               'command': cmd, 'environment': environment, 'pid': child.pid, 'parent_pid': os.getpid(),
               'returncode': child.returncode, 'timed_out': timed_out, 'hard_wait_s': timeout,
               'outer_wall_s': wall, 'stdout': raw_id(stdout), 'stderr': raw_id(stderr),
               'request': None if issued is None else raw_id(encoded(issued)),
               'observation': None if observation is None else raw_id(observation)}
    store(root / (name + '.launch.json'), encoded(receipt) + b'\n')
    return receipt


def read_observation(root: Path, name: str) -> dict:
    receipt = parse((root / (name + '.launch.json')).read_bytes())
    require(not receipt['timed_out'] and receipt['returncode'] == 0, 'CHILD_NOT_SUCCESSFUL: ' + name)
    result = parse(checked_read(root / name / 'observation.json', receipt['observation']))
    require(result['pid'] == receipt['pid'] and result['parent_pid'] == receipt['parent_pid']
            and result['pid'] != result['parent_pid'], 'PROCESS_BINDING')
    checked_read(root / (name + '.stdout'), receipt['stdout'])
    checked_read(root / (name + '.stderr'), receipt['stderr'])
    if receipt['request'] is not None:
        raw = checked_read(root / (name + '.request.json'), receipt['request'])
        require(result['request'] == raw_id(raw), 'OBSERVED_REQUEST_BINDING')
    return result


def audit(root: Path) -> dict:
    # Fixed nonempty ordered population: truncation cannot create vacuous parity.
    index = parse((root / 'RUN.json').read_bytes())
    require(index['plan'] == list(PLAN), 'COMPLETE_ORDERED_PROCESS_POPULATION')
    require({p.name for p in root.glob('*.launch.json')} == {name + '.launch.json' for name in PLAN}, 'LAUNCH_FILE_POPULATION')
    rows = {name: read_observation(root, name) for name in PLAN}
    p = rows['producer']
    require(p['terminal'] == 'AUTHORED_BUNDLE_PERSISTED' and p['native_calls'] == 0, 'PRODUCER')
    source = p['source_manifest']
    require(all(r['source_manifest'] == source for r in rows.values()), 'MIXED_SOURCE_GENERATIONS')
    require(index['adapter_before'] == index['adapter_after'] == p['adapter_sources'], 'ADAPTER_DRIFT')
    require(rows['revoke']['ocm']['method_liveness'] == 'DEAD'
            and rows['reinstate']['ocm']['method_liveness'] == 'LIVE', 'REVISION_PARITY')
    manifest = parse(checked_read(root / 'producer/bundle/manifest.json', p['bundle']['manifest.json']))
    cohort = {x['label'] for x in manifest['cohort']}
    prefix_labels = [x['label'] for x in manifest['joined_proofs']]
    binding = parse(checked_read(root / 'producer/state-binding.json', p['state_binding']))
    expected_lease = p['lease']
    nonces = set()
    task_pin = raw_id(encoded(p['task']))
    for name in PLAN[1:]:
        r = rows[name]
        issued = parse((root / (name + '.request.json')).read_bytes())
        expected_route, expected_mode = (('ocm', 'resident-disabled' if name == 'revoke' else 'restored')
                                          if name in ('revoke', 'reinstate') else name.split('-', 1))
        require(issued['route'] == expected_route and issued['mode'] == expected_mode, 'PLAN_REQUEST_MISMATCH')
        require(r['mode'] == expected_mode and r['operation'] == (name if name in ('revoke', 'reinstate') else 'solve'), 'PLAN_OPERATION_MISMATCH')
        require('authored_fixture' not in r['file_imports'], 'CONSUMER_IMPORTED_FIXTURE')
        require(issued['nonce'] not in nonces, 'REPLAYED_INVOCATION_NONCE')
        nonces.add(issued['nonce'])
        require(raw_id(encoded(issued['task'])) == task_pin and issued['bundle'] == p['bundle'], 'TASK_OR_BUNDLE_DRIFT')
        if issued['route'] == 'ocm':
            require(issued['state']['lease'] == expected_lease, 'BROKEN_REVISION_CHAIN')
            expected_lease = r['ocm']['lease']
        if name in ('revoke', 'reinstate'):
            require(r['native_calls'] == 0, 'REVISION_REPLAYED_PROOF')
            continue
        s, n = r['solver'], r['native']
        require(s['parent_scope_complete'] and not s['unsupported_actions'], 'UNSUPPORTED_PARENT_SCOPE')
        require(r['terminal'] == ('OCM_GOAL_NATIVE_COMMITTED' if issued['route'] == 'ocm'
                                  else 'GENERATED_PROOF_NATIVE_VERIFIED'), 'SOLVE_TERMINAL')
        require(s['task'] == task_pin and n['generated_result'] == raw_id(encoded(s)), 'RESULT_BINDING')
        require(n['terminal'] == 'GENERATED_PROOF_NATIVE_VERIFIED' and r['native_calls'] == 1, 'FRESH_NATIVE_CHECK')
        require(n['native_result']['verified_labels'] == prefix_labels + [issued['label']], 'COMPLETE_NATIVE_PREFIX')
        expected_trust = [x['label'] for x in manifest['axioms']]
        require(n['native_result']['trusted_assertions'] == expected_trust, 'TRUST_INVENTORY')
        for filename, key in [('native.log','log'), ('database.mm','database')]:
            pin = {k:n['native_result'][key][k] for k in ('bytes','sha256')}
            checked_read(root / name / 'native' / filename, pin)
        claim = n['issued_claim']
        require(claim['query'] == issued['task']['query'] and claim['premises'] == issued['task']['premises'], 'ISSUED_CLAIM')
        used = set(n['used_contracts']) & cohort
        expected_used = cohort if issued['mode'] != 'resident-disabled' else set()
        require(used == expected_used == set(n['selected_cohort_labels']), 'NATIVE_CAUSAL_USE')
        if issued['route'] == 'ocm':
            route = r['ocm']
            require(route['committed'] and route['dispatches'] == route['checks'] == 1, 'OCM_DISPATCH')
            last = route['trace']['stages'][-1]
            require(last['stage'] == 'COMMITMENT' and last['status'] == 'PASS', 'OCM_COMMITMENT')
            require((binding['method'] in route['answer_support']) == bool(expected_used), 'ANSWER_SUPPORT')
            require((repr(binding['method']) in last['evidence_ids']) == bool(expected_used), 'COMMITMENT_SUPPORT')
    comparable = ('task', 'library', 'bank_identity', 'grounded_actions_identity',
                  'emission_syntax_identity', 'generated_target', 'generated_premises',
                  'generated_proof', 'decision_count', 'selected_cohort_labels')
    for mode in MODES:
        ordinary, ocm = [rows[route + '-' + mode]['solver'] for route in ('ordinary','ocm')]
        require(all(ordinary[k] == ocm[k] for k in comparable), 'ORDINARY_OCM_PARITY')
    for key in ('bank_identity', 'grounded_actions_identity', 'emission_syntax_identity'):
        require(len({str(rows['ordinary-' + mode]['solver'][key]) for mode in MODES}) == 1, 'CHANGED_TERM_HINTS')
    counts = [rows['ordinary-' + mode]['solver']['decision_count'] for mode in MODES]
    require(counts == [1, 2, 1], 'AUTHORED_DECISION_COUNTS')
    require(rows['ordinary-enabled']['solver']['generated_proof'] ==
            rows['ordinary-restored']['solver']['generated_proof'], 'RESTORATION')
    launches = [parse((root / (name + '.launch.json')).read_bytes()) for name in PLAN]
    return {'schema': 'ordinary.cold-native.qualification.v1',
            'terminal': 'AUTHORED_COLD_OCM_NATIVE_LIFECYCLE_QUALIFIED', 'processes': len(PLAN),
            'native_calls': sum(r['native_calls'] for r in rows.values()),
            'decision_counts': counts, 'ordinary_ocm_parity': True,
            'source_manifest': source, 'outer_wall_sum_s': sum(r['outer_wall_s'] for r in launches),
            'worker_cpu_sum_s': sum(r['process_cost']['user_s'] + r['process_cost']['system_s'] for r in rows.values()),
            'max_worker_peak_rss_kib_linux': max(r['process_cost']['peak_rss_kib_linux'] for r in rows.values()),
            'scope': 'Authored integration, not acquired learning, protected evaluation, speedup, lifetime payback or full OCM completion.'}


def run(root: Path, timeout=60.0) -> dict:
    root.mkdir(parents=True, exist_ok=False)
    before = adapter_sources()
    checked_sources()
    run_record = {'schema': 'ordinary.cold-native.run.v1', 'plan': list(PLAN), 'adapter_before': before}
    launch(root, 'producer', 'produce-authored', timeout=timeout)
    p = read_observation(root, 'producer')
    current_lease = p['lease']
    for name in PLAN[1:]:
        if name in ('revoke', 'reinstate'):
            r = request(p, 'resident-disabled' if name == 'revoke' else 'restored', 'ocm', current_lease)
            launch(root, name, name, r, timeout)
        else:
            route, mode = name.split('-', 1)
            r = request(p, mode, route, current_lease)
            launch(root, name, 'solve', r, timeout)
        observed = read_observation(root, name)
        if r['route'] == 'ocm':
            current_lease = observed['ocm']['lease']
    run_record['adapter_after'] = adapter_sources()
    store(root / 'RUN.json', encoded(run_record) + b'\n')
    result = audit(root)
    store(root / 'RESULT.json', encoded(result) + b'\n')
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--audit-only', action='store_true')
    args = parser.parse_args()
    print(encoded(audit(args.out) if args.audit_only else run(args.out)).decode())
