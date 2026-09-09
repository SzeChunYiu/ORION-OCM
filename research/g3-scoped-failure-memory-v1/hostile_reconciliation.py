"""Altered-evidence controls for the archived C-to-D continuation."""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment as E
import continue_lineage as C
import audit_representation as A


def run(root, predecessor):
    tests = E.read(root / 'TESTS.json'); request = E.read(root / 'REQUEST.json')
    reports = [E.read(root / (m + '.json')) for m in C.MODES]
    launches = [E.read(root / ('LAUNCH-' + m + '.json')) for m in C.MODES]
    outcomes = []
    mutations = ('missing-arm', 'empty-task-population', 'truncated-task-arm', 'duplicate-process',
                 'foreign-task', 'unsuccessful-process', 'missing-request-binding', 'missing-consumption',
                 'wrong-support-phase')
    for mutation in mutations:
        t, q, rs, ls = deepcopy((tests, request, reports, launches))
        if mutation == 'missing-arm': rs.pop()
        elif mutation == 'empty-task-population': t.clear()
        elif mutation == 'truncated-task-arm': rs[2]['rows'].pop()
        elif mutation == 'duplicate-process': rs[2]['pid'] = rs[1]['pid']
        elif mutation == 'foreign-task': rs[2]['rows'][0]['result']['task_fingerprint'] = 'foreign'
        elif mutation == 'unsuccessful-process': ls[2]['returncode'] = 1
        elif mutation == 'missing-request-binding': rs[2]['request_digest'] = 'foreign'
        elif mutation == 'missing-consumption': rs[2]['rows'][0]['used'] = {}
        elif mutation == 'wrong-support-phase': rs[5]['state']['representation_live'] = True
        try:
            C.reconcile(t, rs, q, ls)
        except ValueError as exc:
            outcomes.append({'mutation': mutation, 'rejected': True, 'reason': str(exc)})
        else:
            raise RuntimeError('mutant survived: ' + mutation)
    # Coordinated forged counts evade pairwise equality but must not evade replay.
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / 'retained'; shutil.copytree(root, copy)
        altered = deepcopy(reports)
        for report in altered:
            report['rows'][0]['counts']['interpreter_steps'] += 1
            (copy / (report['mode'] + '.json')).write_bytes(E.encoded(report) + b'\n')
        forged = E.read(copy / 'RESULT.json')
        forged.update(C.reconcile(tests, altered, request, launches))
        (copy / 'RESULT.json').write_bytes(E.encoded(forged) + b'\n')
        try:
            A.audit(copy, predecessor)
        except ValueError as exc:
            E.require(str(exc) == 'test accounting oracle mismatch', 'mutant rejected for incidental reason: ' + str(exc))
            outcomes.append({'mutation': 'coordinated-counts-and-derived-summary', 'rejected': True, 'reason': str(exc)})
        else:
            raise RuntimeError('coordinated count forgery survived')
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / 'retained'; shutil.copytree(root, copy)
        shutil.rmtree(copy / 'snapshots/representation-revoked')
        shutil.copytree(copy / 'snapshots/restored', copy / 'snapshots/representation-revoked')
        try:
            A.audit(copy, predecessor)
        except ValueError as exc:
            E.require(str(exc) == 'actual persisted phase mismatch', 'mutant rejected for incidental reason: ' + str(exc))
            outcomes.append({'mutation': 'false-withdrawal-snapshot', 'rejected': True, 'reason': str(exc)})
        else:
            raise RuntimeError('false withdrawal snapshot survived')
    return {'terminal': 'ALL_ALTERED_EVIDENCE_CONTROLS_REJECTED', 'cases': outcomes,
            'count': len(outcomes), 'scope': 'authored corruption controls, not independent hostile review'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--predecessor', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    result = run(args.root.resolve(), args.predecessor.resolve())
    E.write(args.report, result)
    print(json.dumps(result, indent=2))
