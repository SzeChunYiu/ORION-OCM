"""Apply the unchanged host checker once per sealed public diagnostic output."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--capture', required=True)
    ap.add_argument('--worktree', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    assert not Path(args.output).exists(), 'create-only checker output already exists'
    root, wt = Path(args.capture), Path(args.worktree)
    sys.path.insert(0, str(wt/'research/ocm-prototype'))
    from clia_checker import check
    seal = json.loads((root/'seal.json').read_text())
    for name, binding in seal.items():
        path = root/name
        assert path.stat().st_size == binding['bytes'] and digest(path) == binding['sha256'], name
    proposal = json.loads((root/'proposal.json').read_text())
    task = json.loads((wt/'research/ocm-prototype/results/generation-feasibility-20260906/prospective/public-task.json').read_text())
    assert task['task_sha256'] == proposal['task_sha256']
    rows = []
    for item in proposal['proposed_cases']:
        case = item['case']; directory = root/case
        assert digest(directory/'stdin.json') == item['input_sha256']
        process = json.loads((directory/'result.json').read_text())
        row = {'case': case, 'process_exit': process['exit_code'], 'check': None}
        try:
            assert process['exit_code'] == 0 and process['error'] is None
            native = json.loads((directory/'stdout').read_text())
            if not isinstance(native, dict):
                raise ValueError('native response must be a JSON object')
            row['native_status'] = native.get('status')
            bound = {'status': native.get('status'), 'candidate': native.get('candidate', ''),
                     'task_sha256': task['task_sha256'], 'grammar_id': task['grammar']['id']}
            row['check'] = check(task, bound, timeout_ms=5000, deadline_s=10)
        except (AssertionError, ValueError, TypeError, KeyError) as exc:
            row['check'] = {'status': 'CANNOT_CHECK', 'reason': type(exc).__name__+': '+str(exc),
                            'native_checker_invoked': False}
        rows.append(row)
    for name, binding in seal.items():
        assert digest(root/name) == binding['sha256'], name
    result = {'scope': 'Existing fixed checker on unchanged native output; no candidate rewriting or synthesis retry.',
              'capture_seal_sha256': digest(root/'seal.json'), 'cases': rows,
              'membership': 'SEPARATE_NATIVE_RAW_REVIEW_REQUIRED', 'learning': 'NOT_TESTED'}
    with Path(args.output).open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'cases': len(rows), 'statuses': [r['check']['status'] for r in rows]}))


if __name__ == '__main__':
    main()
