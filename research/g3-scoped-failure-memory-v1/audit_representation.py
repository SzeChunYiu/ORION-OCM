"""Read-only, independently structured accounting replay for the retained study.

Independent *implementation structure*, not independent authorship/replication.
Runs the original uncached solver, then derives prefix hits by flat linear scans.
Does not execute the trie, trust success fields, or rewrite historical evidence.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment as E
import representation as R
import continue_lineage as C


def capture(task):
    calls = []
    original = E.M.execute
    E.require(original is E.REAL_EXECUTE, 'concurrent solver substitution')
    def tap(p, x):
        calls.append((tuple(p), x))
        return original(p, x)
    E.M.execute = tap
    try:
        answer = E.M.solve(task, E.BUDGET).as_dict()
    finally:
        E.M.execute = original
    return json.loads(E.encoded(answer)), calls


def flat_oracle(calls, records, kind):
    checked = [E.validate_record(r) for r in records]
    entries = [(p, x, v, ident) for (p, x), (v, ident) in checked]
    tree_prefixes = {p[:k] for p, _, _, _ in entries for k in range(len(p) + 1)}
    counts, used = Counter(), Counter()
    for p, x in calls:
        counts['point_calls'] += 1
        found = None
        if kind == 'P1' and entries:
            counts['lookups'] += 1
            full = [e for e in entries if e[0] == p and e[1] == x]
            E.require(len(full) <= 1, 'duplicate oracle full point')
            found = full[0] if full else None
        elif kind == 'P2' and entries:
            compatible = [e for e in entries if e[1] == x and len(e[0]) <= len(p) and p[:len(e[0])] == e[0]]
            found = max(compatible, key=lambda e: len(e[0])) if compatible else None
            # Count the unique path length from SET membership, not trie walking.
            depth = max([k for k in range(len(p) + 1) if p[:k] in tree_prefixes], default=0)
            counts['terminal_lookups'] += depth + 1
            counts['edge_lookups'] += min(depth + 1, len(p))
        if found is not None:
            prefix, _, value, identity = found
            # Independent whole-program coefficient evaluation establishes no semantic drift.
            suffix = p[len(prefix):]
            E.require(E.REAL_EXECUTE(suffix, value) == E.M.evaluate_polynomial(E.M.normal_form(p), x), 'invalid continuation')
            used[identity] += 1
            counts['hits'] += 1
            counts['full_hits' if len(prefix) == len(p) else 'proper_prefix_hits'] += 1
            counts['avoided_interpreter_steps'] += len(prefix)
            if 0 < len(prefix) < len(p): counts['positive_proper_prefix_hits'] += 1
            if kind == 'P1' or not suffix:
                continue
            counts['interpreter_calls'] += 1
            counts['interpreter_steps'] += len(suffix)
        else:
            counts['interpreter_calls'] += 1
            counts['interpreter_steps'] += len(p)
    return counts, used


def snapshot_hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def audit(root, predecessor=None):
    original_files = snapshot_hashes(root)
    request = E.read(root / 'REQUEST.json')
    binding = E.read(root / 'PREDECESSOR.json')
    pred = (root / binding['relative_path']).resolve() if predecessor is None else predecessor.resolve()
    E.require(C.source_manifest() == request['source_manifest'], 'retained execution source drift')
    for name, digest in binding['files'].items():
        E.require(C.hashfile(pred / name) == digest, 'predecessor source/evidence drift: ' + name)
    saved = (root / 'PREDECESSOR-LEDGER.jsonl').read_bytes()
    E.require(len(saved) == binding['ledger_bytes'] and hashlib.sha256(saved).hexdigest() == binding['ledger_sha256'], 'predecessor ledger binding')
    E.require((pred / 'lineage/ledger.jsonl').read_bytes().startswith(saved), 'not the continued ancestor')
    population = E.read(root / 'ALLOCATION.json')
    E.require(population == C.allocate(E.read(pred / 'ALLOCATION.json')), 'allocation drift')
    tests = E.read(root / 'TESTS.json')
    E.require(tests == population['test'], 'test population drift')
    records = E.read(root / 'ORDINARY.json')
    E.require(records == E.read(pred / 'ORDINARY.json') and E.digest(records) == request['memory']['records_digest'], 'memory identity')
    # Reconstruct the original acquired failures and first-64 selection; no test outcomes used.
    selected = []; seen = set(); attempts = 0
    old_population = E.read(pred / 'ALLOCATION.json')
    old_training = E.read(pred / 'TRAINING.json')
    E.require(len(old_training) == len(old_population['training']) == 8, 'incomplete training')
    for data, archived in zip(old_population['training'], old_training):
        row = E.solve(E.task_from(data), acquire=True)
        for field in ('result', 'counts', 'used', 'failures'):
            E.require(E.encoded(row[field]) == E.encoded(archived[field]), 'training reconstruction mismatch: ' + field)
        attempts += len(row['failures'])
        for r in row['failures']:
            key = (tuple(r['program']), r['x'])
            if key not in seen and len(selected) < 64:
                E.validate_record(r); selected.append(r); seen.add(key)
    E.require(selected == records, 'first-64 acquisition selection drift')
    programs = sorted({tuple(r['program']) for row in old_training for r in row['failures']})
    witness = E.read(root / 'REPRESENTATION-WITNESS.json')
    E.require(witness['before'] == R.observer_certificate(programs, (0,)) and
              witness['after'] == R.observer_certificate(programs, (0, 1)), 'false representation witness')
    E.require(witness['diagnosis'] == R.diagnose(observation_witness=witness['after']) and
              witness['timeout_diagnosis'] == 'RESOURCE_BOUND', 'misclassified insufficiency')
    selection = E.read(root / 'SELECTION.json')
    E.require(E.digest(selection) == request['selection_digest'] and R.choose(selection['validation']) == request['selected'], 'selection identity')
    validated_rows = 0
    for i, data in enumerate(population['validation']):
        expected, calls = capture(E.task_from(data))
        for kind in R.KINDS:
            row = selection['validation'][kind][i]
            counts, used = flat_oracle(calls, records, kind)
            E.require(row['result'] == expected and Counter(row['counts']) == counts and Counter(row['used']) == used, 'validation oracle mismatch')
            validated_rows += 1
    reports = [E.read(root / (mode + '.json')) for mode in C.MODES]
    launches = [E.read(root / ('LAUNCH-' + mode + '.json')) for mode in C.MODES]
    reconciled = C.reconcile(tests, reports, request, launches)
    published = E.read(root / 'RESULT.json')
    E.require(all(published.get(k) == v for k, v in reconciled.items()), 'summary not derived from complete evidence')
    count_rows = 0; calls_total = 0
    for i, data in enumerate(tests):
        expected, calls = capture(E.task_from(data)); calls_total += len(calls)
        oracles = {kind: flat_oracle(calls, records, kind) for kind in R.KINDS}
        for report in reports:
            row = report['rows'][i]
            counts, used = oracles[report['kind']]
            E.require(row['result'] == expected and Counter(row['counts']) == counts and Counter(row['used']) == used, 'test accounting oracle mismatch')
            count_rows += 1
    for report in reports:
        mode = report['mode']
        if mode in ('ocm-selected', 'representation-revoked', 'memory-revoked', 'restored'):
            _, kind, state = R.load(root / 'snapshots' / mode, request['memory'], request['representation'])
            E.require(state == report['state'] and kind == report['kind'], 'actual persisted phase mismatch')
    E.require(snapshot_hashes(root) == original_files, 'audit mutated retained evidence')
    return {'terminal': 'RETAINED_REPRESENTATION_ACCOUNTING_RECONCILED',
            'authorship': 'same author; differently structured flat-scan oracle, not protected independent replication',
            'training_attempts_reconstructed': attempts, 'certificates_reconstructed': len(records),
            'validation_rows_reconstructed': validated_rows, 'test_rows_reconstructed': count_rows,
            'uncached_test_point_calls_replayed': calls_total,
            'actual_persisted_support_snapshots_checked': 4,
            'retained_file_count_unchanged': len(original_files), 'all_retained_bytes_unchanged': True,
            'source_manifest_digest': E.digest(request['source_manifest'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--predecessor', type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.root.resolve(), args.predecessor)
    E.write(args.report, result)
    print(E.encoded(result).decode())
