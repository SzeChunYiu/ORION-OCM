"""Closed-fragment public sealer and actual OS-isolation probe.

Anthropic textual signatures are evaluator-only until their elaborated type and
safe definition closure are checked. Static filtering is not OS isolation.
"""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
from kernel import ENVIRONMENT, digest
from native import EqualityTask, identity


def seal(task: EqualityTask, destination: Path, private: Path, budget=64):
    destination = Path(destination).absolute(); private = Path(private).absolute()
    for p in (destination, private):
        if any(x.is_symlink() for x in (p, *p.parents)): raise ValueError('SYMLINK_PACKAGE_PATH')
    if destination == private or destination in private.parents or private in destination.parents:
        raise ValueError('PUBLIC_PRIVATE_OVERLAP')
    if type(budget) is not int or not 0 <= budget <= 64: raise ValueError('BUDGET_CONTRACT')
    private_digest = digest(private)
    destination.mkdir(parents=True, exist_ok=False)
    public = {'schema': 'ocm.flt.public.equality.v1', 'task': task.as_dict(),
              'environment': ENVIRONMENT, 'edge_examination_budget': budget,
              'allowed_operators': ['hyp', 'refl', 'symm', 'trans'], 'imports': []}
    (destination / 'challenge.json').write_text(json.dumps(public, sort_keys=True) + '\n')
    return {'public_sha256': digest(destination / 'challenge.json'),
            'private_manifest_sha256': private_digest, 'physical_isolation': 'NOT_YET_CHECKED'}


def export_anthropic_signature(signature_record):
    # Intentionally no fallback that copies wrappers or silently turns statements into axioms.
    raise ValueError('CANNOT_CHECK_ELABORATED_TYPE_AND_DEFINITION_CLOSURE')


def isolation_probe(public: Path, private_file: Path):
    public = Path(public).resolve(); private_file = Path(private_file).resolve()
    if not private_file.is_file(): raise ValueError('PRIVATE_POSITIVE_CONTROL_REQUIRED')
    if public == private_file or public in private_file.parents:
        raise ValueError('PUBLIC_PRIVATE_OVERLAP')
    if any(Path(x) in private_file.parents for x in ('/usr', '/lib', '/lib64')):
        raise ValueError('PRIVATE_OVERLAPS_RUNTIME_MOUNTS')
    bwrap = shutil.which('bwrap')
    if not bwrap: return {'terminal': 'CANNOT_CHECK_ISOLATION_TOOL_UNAVAILABLE'}
    argv = [bwrap, '--unshare-all', '--die-with-parent', '--new-session', '--clearenv']
    for p in ('/usr', '/lib', '/lib64'):
        if Path(p).exists(): argv += ['--ro-bind', p, p]
    argv += ['--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
             '--ro-bind', str(public), '/challenge', '--chdir', '/challenge',
             '/usr/bin/python3', '-I', '-c',
             "import pathlib,sys\npathlib.Path('/challenge/challenge.json').read_bytes()\n"
             "try: pathlib.Path(sys.argv[1]).read_bytes()\n"
             "except (FileNotFoundError, PermissionError): sys.exit(0)\n"
             "sys.exit(7)", str(private_file)]
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {'terminal': 'CANNOT_CHECK_ISOLATION', 'reason': str(e)}
    return {'terminal': 'PRIVATE_PATH_NOT_MOUNTED_AT_PROBE_SCOPE' if p.returncode == 0 else
            ('SOLUTION_LEAKAGE_DETECTED' if p.returncode == 7 else 'CANNOT_CHECK_ISOLATION'),
            'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr,
            'limitation': 'Probe only; no R2/R3 solver process is implemented or certified'}
