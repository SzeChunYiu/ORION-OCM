"""Read evaluator Git objects at the pinned commit; never execute imported Lean.

A full audit is required before staging. Unsupported signatures are counted, not
silently omitted. The syntactic import DAG is not a kernel-certified dependency
DAG. The staged package has no executable boundary library or OS sandbox yet.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from substrate import (PINS, Refusal, build_graph, digest_json, encoded,
                       extract_wrapper, select_holes, sha256, stage_challenge)

EXPECTED_COUNT = 29511
SELECTION = {'seed': 'flt-kso-v1-layout-20260906', 'maximum_holes': 1,
             'rule': 'minimum sha256(seed NUL node); bounded ancestor expansion'}


def read_objects(checkout: Path):
    """Use Git object identity, not potentially modified working-tree files."""
    start = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='flt-git-home-') as home:
        env = {'PATH': '/usr/bin:/bin', 'HOME': home, 'LC_ALL': 'C.UTF-8',
               'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null',
               'GIT_NO_REPLACE_OBJECTS': '1', 'GIT_TERMINAL_PROMPT': '0'}
        base = ['git', '--no-replace-objects', '-C', str(checkout)]
        def run(args, data=None):
            try:
                result = subprocess.run(base + args, input=data, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, env=env, timeout=180)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise Refusal('CANNOT_CHECK_SOURCE_ACQUISITION', str(exc)) from exc
            if result.returncode:
                raise Refusal('CANNOT_CHECK_SOURCE_ACQUISITION', result.stderr.decode(errors='replace')[:1000])
            return result.stdout
        commit = run(['rev-parse', '--verify', PINS['anthropic_commit']+'^{commit}']).decode().strip()
        if commit != PINS['anthropic_commit']:
            raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH', 'evaluator commit')
        tree = run(['rev-parse', commit+'^{tree}']).decode().strip()
        listing = run(['ls-tree', '-rz', '--full-tree', commit, '--',
                       'Theorems', 'P2M/Sol', 'lean-toolchain', 'lake-manifest.json'])
        entries = []
        for entry in listing.split(b'\0'):
            if not entry: continue
            identity, path = entry.split(b'\t', 1)
            mode, kind, oid = identity.decode().split()
            path = path.decode('utf-8')
            if not (path.startswith(('Theorems/Thm_', 'P2M/Sol/S_')) and path.endswith('.lean')
                    or path in ('lean-toolchain', 'lake-manifest.json')): continue
            if mode != '100644' or kind != 'blob':
                raise Refusal('CANNOT_CHECK_SOURCE_ACQUISITION', 'non-regular source: '+path)
            entries.append((path, oid))
        # One batch read; count the global read/materialization explicitly.
        data = run(['cat-file', '--batch'], ''.join(oid+'\n' for _,oid in entries).encode())
        offset = 0; files = {}; identities = {}
        import hashlib
        for path, expected in entries:
            end = data.index(b'\n', offset)
            oid, kind, raw_size = data[offset:end].decode().split()
            size = int(raw_size); offset = end+1
            body = data[offset:offset+size]; offset += size
            if (oid != expected or kind != 'blob' or data[offset:offset+1] != b'\n'
                or hashlib.sha1(b'blob '+str(size).encode()+b'\0'+body).hexdigest() != oid):
                raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH', 'Git blob')
            offset += 1
            files[path] = body.decode('utf-8')
            identities[path] = {'git_blob': oid, 'sha256': sha256(body), 'bytes': size}
        if offset != len(data): raise Refusal('CANNOT_CHECK_SOURCE_ACQUISITION', 'batch framing')
    if files.pop('lean-toolchain', '').strip() != 'leanprover/lean4:v4.33.1':
        raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH', 'Lean pin')
    lake = json.loads(files.pop('lake-manifest.json', '{}'))
    mathlib = [p for p in lake.get('packages', []) if p.get('name') == 'mathlib']
    if len(mathlib) != 1 or mathlib[0].get('rev') != PINS['mathlib_commit']:
        raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH', 'Mathlib pin')
    return files, {'commit': commit, 'tree': tree, 'files': identities,
                   'global_source_files': len(identities), 'bytes_materialized': len(data)+len(listing),
                   'wall_seconds': time.perf_counter()-start,
                   'cost_scope': 'FULL_EVALUATOR_GIT_SCAN_NOT_SOLVER_QUERY'}


def audit(checkout, destination):
    destination = Path(destination)
    destination.mkdir(exist_ok=False)
    try:
        files, acquisition = read_objects(Path(checkout))
        rows = sorted((p,s) for p,s in files.items() if p.startswith('Theorems/Thm_'))
        failures = []; codes = Counter()
        for path, text in rows:
            try: extract_wrapper(text, path[len('Theorems/Thm_'):-5])
            except Refusal as exc:
                failures.append({'path':path,'terminal':exc.terminal,'reason':str(exc)})
                codes[exc.terminal] += 1
        report = {'environment':PINS,'source':acquisition,'selection':SELECTION,
                  'wrappers_examined':len(rows),'supported_wrappers':len(rows)-len(failures),
                  'unsupported_counts':dict(codes),'failures':failures,
                  'solver_launched':False,'kernel_elaboration':'NOT_RUN',
                  'terminal':'CANNOT_CHECK_SOURCE_COVERAGE'}
        if not failures:
            graph = build_graph(files, expected_count=EXPECTED_COUNT)
            graph['source_acquisition'] = {'commit':acquisition['commit'],'tree':acquisition['tree'],
                                         'inventory_sha256':digest_json(acquisition['files'])}
            root, holes = select_holes(graph, SELECTION['maximum_holes'], SELECTION['seed'])
            public, private = stage_challenge(graph, holes, root, 'R2',
                                              destination/'public', destination/'private')
            report.update(terminal='SYNTACTIC_GRAPH_AND_STAGING_SUPPORTED',
                          graph_sha256=digest_json(graph), public_sha256=digest_json(public),
                          private_sha256=digest_json(private), graph_nodes=graph['count'],
                          hole_count=len(holes), execution_terminal='CANNOT_CHECK_ISOLATION_AND_BOUNDARY')
        (destination/'AUDIT.json').write_bytes(encoded(report))
        return report
    except (Refusal, ValueError, OSError) as exc:
        report = {'terminal':getattr(exc,'terminal','CANNOT_CHECK_SOURCE_AUDIT'),
                  'reason':str(exc),'solver_launched':False,'environment':PINS}
        (destination/'AUDIT.json').write_bytes(encoded(report))
        return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkout',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    result=audit(args.checkout,args.out)
    print(json.dumps({k:result[k] for k in ('terminal','wrappers_examined','supported_wrappers','graph_nodes') if k in result}))
    raise SystemExit(0 if result['terminal']=='SYNTACTIC_GRAPH_AND_STAGING_SUPPORTED' else 2)
