"""Fresh pinned Lean checker for the closed equality AST only, not arbitrary Lean."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time
import uuid
from native import identity, render

ENVIRONMENT = json.loads((Path(__file__).parent / 'ENVIRONMENT.json').read_text())


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def process(argv, cwd, env, timeout):
    start = time.monotonic()
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        p = subprocess.Popen(argv, cwd=cwd, env=env, stdout=out, stderr=err,
                             start_new_session=True, close_fds=True)
        timed_out = False
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:
            try: os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            p.wait()
        out.seek(0); err.seek(0)
        stdout, stderr = out.read(1048577), err.read(1048577)
    return {'argv': argv, 'exit_code': p.returncode, 'timed_out': timed_out,
            'stdout': stdout.decode('utf-8', errors='replace'),
            'stderr': stderr.decode('utf-8', errors='replace'),
            'output_limit_exceeded': max(len(stdout), len(stderr)) > 1048576,
            'wall_seconds': time.monotonic() - start, 'cpu_seconds': None, 'peak_rss': None}


def check(task, proof, archive=None):
    source = render(task, proof)
    receipt = {'schema': 'ocm.flt.kernel-candidate.v1', 'run_id': uuid.uuid4().hex,
        'statement_id': task.statement_id,
        'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
        'environment_id': identity(ENVIRONMENT), 'environment': ENVIRONMENT,
        'terminal': 'CANNOT_CHECK_LEAN_ARCHIVE_UNAVAILABLE', 'lean_checker_calls': 0,
        'processes': [], 'fresh_kernel': False, 'LLM_CALLS': 0, 'LLM_TOKENS': 0}
    if archive is None or not Path(archive).is_file():
        return receipt
    def verify(path):
        if Path(path).stat().st_size != ENVIRONMENT['lean_archive_size'] or digest(path) != ENVIRONMENT['lean_archive_sha256']:
            raise ValueError('CHECKER_OR_ENVIRONMENT_MISMATCH')
    try:
        verify(archive)
        with tempfile.TemporaryDirectory(prefix='ocm-flt-kernel-') as d:
            root = Path(d)
            pinned = root / 'release.tar.zst'
            shutil.copyfile(archive, pinned); verify(pinned)
            env = {'PATH': '/usr/bin:/bin', 'HOME': d, 'LANG': 'C.UTF-8'}
            extraction = process(['/usr/bin/tar', '--zstd', '-xf', str(pinned), '-C', d], d, env, 180)
            receipt['processes'].append(extraction)
            if extraction['exit_code'] != 0 or extraction['timed_out']:
                receipt['terminal'] = 'CANNOT_CHECK_TOOLCHAIN_EXTRACTION'; return receipt
            lean = root / 'lean-4.33.1-linux/bin/lean'
            receipt['lean_binary_sha256'] = digest(lean)
            proofs = root / 'public'; proofs.mkdir()
            (proofs / 'Candidate.lean').write_text(source)
            env['LEAN_PATH'] = str(proofs)
            version = process([str(lean), '--version'], str(proofs), env, 10)
            receipt['processes'].append(version)
            if version['exit_code'] != 0 or not version['stdout'].startswith('Lean (version 4.33.1,'):
                receipt['terminal'] = 'CHECKER_OR_ENVIRONMENT_MISMATCH'; return receipt
            run = process([str(lean), 'Candidate.lean'], str(proofs), env, 10)
            receipt['processes'].append(run); receipt['lean_checker_calls'] = 1
            receipt['fresh_kernel'] = True
            if run['timed_out']:
                receipt['terminal'] = 'CANNOT_CHECK_KERNEL_TIMEOUT'
            elif run['output_limit_exceeded']:
                receipt['terminal'] = 'CANNOT_CHECK_KERNEL_OUTPUT_LIMIT'
            elif run['exit_code'] != 0:
                receipt['terminal'] = 'CHECKER_REJECTED_CANDIDATE'
            elif re.fullmatch(r"'ocm_candidate' does not depend on any axioms\s*", run['stdout']):
                receipt['terminal'] = 'KERNEL_ACCEPTED'; receipt['axioms'] = []
            else:
                receipt['terminal'] = 'CANNOT_CHECK_AXIOM_AUDIT'
    except ValueError as e:
        receipt['terminal'] = str(e)
    except OSError as e:
        receipt['terminal'] = 'CANNOT_CHECK_TOOLCHAIN_IO'; receipt['reason'] = str(e)
    return receipt
