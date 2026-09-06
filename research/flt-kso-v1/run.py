"""Execute the one registered engineering micro-gate; never overwrite a row."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from native import EqualityTask, construct, identity
from kernel import ENVIRONMENT, check, digest
from bridge import run_ocm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def run(out: Path, archive: Path | None, control_archive: Path | None):
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    registry = json.loads((HERE / 'REGISTRY.json').read_text())
    receipt = {'schema': 'ocm.flt.micro.receipt.v1', 'challenge_id': registry['challenge_id'],
        'registration': registry, 'environment': ENVIRONMENT,
        'source_commit': git('rev-parse', 'HEAD'), 'source_tree': git('rev-parse', 'HEAD^{tree}'),
        'source_files': {p.name: digest(p) for p in sorted(HERE.iterdir()) if p.is_file()},
        'terminal': 'CANNOT_CHECK_R0_REQUIRED', 'LLM_CALLS': 0, 'LLM_TOKENS': 0,
        'scope': 'engineering prerequisite; not N4 qualification',
        'unmeasured': ['energy', 'complete OS bytes read', 'per-process CPU and RSS', 'end-to-end active k'],
        'unearned': registry['unearned']}
    def finish():
        receipt['wall_seconds'] = time.monotonic() - started
        (out / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
        print(json.dumps({'terminal': receipt['terminal'], 'receipt': str(out / 'receipt.json')}))
        return 0 if receipt['terminal'] == 'UNSEEN_COMPOSITION_SUPPORTED_AT_REGISTERED_R1_SCOPE' else 2
    if git('status', '--porcelain', '--untracked-files=no'):
        receipt['terminal'] = 'CANNOT_CHECK_DIRTY_SOURCE'; return finish()
    if control_archive is None:
        return finish()
    command = [sys.executable, str(ROOT / 'research/proof-replay-v1/replay.py'),
               '--archive', str(control_archive), '--out', str(out / 'r0.json')]
    control = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    receipt['r0_process'] = {'argv': command, 'exit_code': control.returncode,
                             'stdout': control.stdout, 'stderr': control.stderr}
    if control.returncode != 0:
        receipt['terminal'] = 'CANNOT_CHECK_R0_CONTROL'; return finish()
    receipt['r0_receipt_sha256'] = digest(out / 'r0.json')
    task = EqualityTask(**registry['task'])
    native = run_ocm(task, ENVIRONMENT, str(out / 'ocm-ledger'),
                     lambda t, p: check(t, p, archive), registry['edge_examination_budget'])
    receipt['native'] = native
    parent_start = time.monotonic()
    parent = construct(task, registry['edge_examination_budget'])
    (out / 'parent-cache.json').write_text(json.dumps(parent, sort_keys=True))
    parent['checker'] = check(task, parent['proof'], archive) if parent['proof'] else None
    parent['wall_seconds'] = time.monotonic() - parent_start
    receipt['parent'] = parent
    receipt['comparison'] = 'CANNOT_CHECK_PARENT_KERNEL'
    if native['terminal'] == 'KERNEL_ACCEPTED' and parent['checker'] and parent['checker']['terminal'] == 'KERNEL_ACCEPTED':
        receipt['terminal'] = 'UNSEEN_COMPOSITION_SUPPORTED_AT_REGISTERED_R1_SCOPE'
        receipt['comparison'] = 'PARENT_SUFFICIENT_AT_EQUALITY_CONSTRUCTION_SCOPE'
    else:
        receipt['terminal'] = native['terminal']
    after = {p.name: digest(p) for p in sorted(HERE.iterdir()) if p.is_file()}
    if receipt['source_files'] != after or git('status', '--porcelain', '--untracked-files=no'):
        receipt['terminal'] = 'CANNOT_CHECK_SOURCE_DRIFT'
    return finish()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--archive', type=Path)
    p.add_argument('--control-archive', type=Path)
    a = p.parse_args()
    raise SystemExit(run(a.out.resolve(), a.archive, a.control_archive))
