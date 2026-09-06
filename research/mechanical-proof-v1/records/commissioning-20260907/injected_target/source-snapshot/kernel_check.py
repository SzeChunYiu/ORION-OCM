"""Fresh isolated kernel checking against one independently fixed F0 challenge."""
from hashlib import sha256
import json
from pathlib import Path
import re

from isolation import run_isolated
from lean_transport import audit_axioms
from proof_check import FOUNDATION_SHA256, TARGET_SHA256, source_bytes

LEAN_SHA256 = 'e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550'
VERSION = ('Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit '
           '819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)')
SOURCES = {'Foundation.lean', 'Target.lean', 'Candidate.lean', 'candidate.json'}


def _source_check(stage, initial=False):
    if (stage.get('formal_target') != 'F0Target.statement' or
            stage.get('target_sha256') != TARGET_SHA256 or stage.get('terminal') != 'STAGED_UNCHECKED'):
        raise ValueError('unregistered target metadata')
    work = Path(stage['directory'])
    if work.is_symlink() or not work.is_dir():
        raise ValueError('regular checker work directory required')
    if set(stage['files']) != SOURCES:
        raise ValueError('unregistered checker source set')
    if initial and {p.name for p in work.iterdir()} != SOURCES:
        raise ValueError('fresh checker stage contains undeclared files or caches')
    data = {}
    for name, expected in stage['files'].items():
        path = work / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('checker source missing or linked')
        data[name] = path.read_bytes()
        if sha256(data[name]).hexdigest() != expected:
            raise ValueError('checker source identity changed')
    if sha256(data['Target.lean']).hexdigest() != TARGET_SHA256:
        raise ValueError('independent target changed')
    if sha256(data['Foundation.lean']).hexdigest() != FOUNDATION_SHA256:
        raise ValueError('trusted Foundation changed')
    if data['Candidate.lean'] != source_bytes(json.loads(data['candidate.json'])):
        raise ValueError('candidate source differs from trusted data translation')
    return work


def check_staged(stage, runtime, shared_mounts, *, timeout_s=30, max_output_bytes=1048576):
    """Return KERNEL_PASS only for the exact target; process completion is insufficient.

    The caller must qualify full copied runtime/library mount custody separately.
    This function checks executable identity, fixed sources, actual compilation and
    transitive axiom output. It does not grant whole-machine no-neural qualification.
    """
    result = {'terminal': 'CANNOT_CHECK', 'reason': '', 'phases': [], 'stage': stage,
              'fresh_kernel_replay': False, 'axioms': None,
              'formal_target': 'F0Target.statement', 'target_sha256': TARGET_SHA256}
    try:
        work = _source_check(stage, initial=True)
        mounts = [(Path(runtime).resolve(), '/lean'), *shared_mounts]
        commands = [('version', ['--version']),
                    ('foundation', ['-o', 'Foundation.olean', 'Foundation.lean']),
                    ('target', ['-o', 'Target.olean', 'Target.lean']),
                    ('candidate', ['-o', 'Candidate.olean', 'Candidate.lean'])]
        for phase, args in commands:
            _source_check(stage)
            record = run_isolated(['/lean/bin/lean', *args], read_only=mounts,
                                  executable_sha256=LEAN_SHA256, work_dir=work,
                                  env={'LEAN_PATH': '/work', 'LANG': 'C.UTF-8'},
                                  timeout_s=timeout_s, max_output_bytes=max_output_bytes)
            result['phases'].append({'phase': phase, 'process': record})
            _source_check(stage)
            if record['terminal'] != 'COMPLETED':
                result['reason'] = phase + ': incomplete process envelope'
                return result
            if record['returncode'] != 0:
                error = record.get('stdout', '') + record.get('stderr', '')
                if phase == 'candidate' and re.search(
                        r'(?:^|\n)Candidate\.lean:\d+:\d+: error: (?:type mismatch|application type mismatch)\b',
                        error, flags=re.IGNORECASE):
                    result['terminal'] = 'REJECTED'
                result['reason'] = phase + ': nonzero tool exit'
                return result
            if phase == 'version' and record['stdout'].strip() != VERSION:
                result['reason'] = 'unregistered toolchain version'
                return result
        axioms = audit_axioms(record['stdout'], 'OCMMechanicalProof.constructed')
        if record.get('stderr', '').strip():
            raise ValueError('unexpected checker diagnostics')
        artifact = work / 'Candidate.olean'
        if artifact.is_symlink() or not artifact.is_file():
            raise ValueError('fresh compiled proof artifact missing')
        result.update(terminal='KERNEL_PASS', fresh_kernel_replay=True, axioms=axioms,
                      compiled_proof_sha256=sha256(artifact.read_bytes()).hexdigest())
    except (ValueError, KeyError, TypeError, OSError, RecursionError) as exc:
        result['reason'] = type(exc).__name__ + ': ' + str(exc)
    return result
