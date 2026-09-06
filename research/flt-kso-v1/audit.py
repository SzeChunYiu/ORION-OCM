"""Inventory the frozen evaluator checkout; never run a solver in that checkout."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import time
from graph import inventory
from kernel import ENVIRONMENT, digest
from native import EqualityTask
from seal import isolation_probe, seal
from ocm.kso.resources import ResourceVector


def audit(root, out):
    out.mkdir(parents=True, exist_ok=False)
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()
    if git('rev-parse', 'HEAD') != ENVIRONMENT['anthropic_commit'] or git('status', '--porcelain', '--untracked-files=no'):
        raise ValueError('CHECKER_OR_ENVIRONMENT_MISMATCH')
    start = time.monotonic()
    row = inventory(root)
    row['anthropic_commit'] = git('rev-parse', 'HEAD')
    row['source_tree'] = git('rev-parse', 'HEAD^{tree}')
    row['wall_seconds'] = time.monotonic() - start
    row['resource_vector'] = ResourceVector(object_count=row['wrapper_count'],
        io_calls=2 * row['wrapper_count'], update_work=row['wrapper_count']).as_dict()
    for name in ('lean-toolchain', 'lakefile.lean', 'lake-manifest.json'):
        row.setdefault('environment_source_hashes', {})[name] = digest(root / name)
    if git('status', '--porcelain', '--untracked-files=no'):
        row['terminal'] = 'CANNOT_CHECK_SOURCE_DRIFT'
    private = out / 'private-inventory.json'
    private.write_text(json.dumps(row, sort_keys=True) + '\n')
    # Synthetic development package, not a selected Anthropic hole or an R2 run.
    task = EqualityTask(('x', 'y'), (('x', 'y'),), ('y', 'x'))
    package = seal(task, out / 'public-development', private)
    guard = isolation_probe(out / 'public-development', private)
    summary = {k: v for k, v in row.items() if k not in ('nodes', 'errors')}
    summary['error_count'] = len(row['errors'])
    summary['signature_count'] = sum('signature' in n['signature'] for n in row['nodes'].values())
    summary['package'] = package; summary['isolation_probe'] = guard
    summary['r2_terminal'] = 'CANNOT_CHECK_ELABORATED_TYPE_AND_DEFINITION_CLOSURE'
    (out / 'summary.json').write_text(json.dumps(summary, sort_keys=True, indent=2) + '\n')
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args(); audit(a.source.resolve(), a.out.resolve())
