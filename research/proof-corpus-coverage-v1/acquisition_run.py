"""Shared exact-source acquisition under the original four-row episode clock."""
from pathlib import Path
from hashlib import sha256
import json
import resource
import sys
import time
import types

HERE = Path(__file__).resolve().parent
path = HERE / 'acquisition_contract.py'
contract = types.ModuleType('acquisition_contract'); contract.__file__ = str(path)
sys.modules['acquisition_contract'] = contract
CONTRACT_BYTES = path.read_bytes()
exec(compile(CONTRACT_BYTES, str(path), 'exec'), contract.__dict__)


def run(registrar, lock_path, destination):
    started = time.monotonic(); utc = time.time()
    out = contract.new_output(destination, [registrar, lock_path, HERE])
    expected = {}
    def persist(name, value):
        raw = contract.canonical(value)
        expected[name] = dict(path=str(out / name), sha256=sha256(raw).hexdigest(), bytes=len(raw))
        contract.write(out / name, value)
    start = dict(schema='ocm.f1.coverage-episode-start.v1', monotonic_seconds=started,
                 unix_seconds=utc, boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                 whole_deadline_monotonic=started + 43200, acquisition_deadline_monotonic=started + 3600,
                 registration_seal_sha256=contract.SEAL, denominator=4, continuation_cursor=4)
    persist('STARTED.json', start)
    before = resource.getrusage(resource.RUSAGE_SELF)
    sources = {}; assigned = None; receipt = {}; result = None; ready = False; error = None
    reached = 'INPUT_VALIDATION'
    try:
        interpreter = contract.record(sys.executable)
        if interpreter['sha256'] != contract.PYTHON:
            raise ValueError('qualified Python required')
        seal, assigned, policy = contract.registration(registrar)
        persist('REGISTRATION-REFERENCE.json', dict(seal=seal, assignments=assigned, policy=policy))
        persist('ROWS-DECLARED.json', dict(denominator=4, continuation_cursor=4, rows=[
            dict(key=row['key'], assignment_rank=row['assignment_rank'], stages=[
                dict(stage=stage, state='NOT_DISPATCHED', cause='EPISODE_PRE_DISPATCH')
                for stage in contract.STAGES]) for row in assigned['rows']]))
        source = out / 'sources'; source.mkdir()
        names = ['resource_boot', 'resource_contract', 'resource_pidfd', 'resource_cgroup',
                 'resource_monitor', 'resource_runner', 'build_profile_policy', 'build_profile',
                 'resource_install', 'acquisition_contract', 'acquisition_run', 'acquisition_worker',
                 'acquisition_git', 'acquisition_git_custody']
        for name in names:
            original = contract.record(HERE / (name + '.py'))
            raw = Path(original['path']).read_bytes()
            if sha256(raw).hexdigest() != original['sha256']:
                raise ValueError('source changed while copying')
            if name == 'acquisition_contract' and raw != CONTRACT_BYTES:
                raise ValueError('executed contract differs from source freeze')
            with (source / (name + '.py')).open('xb') as target:
                target.write(raw)
            sources[name] = dict(original=original, frozen=contract.record(source / (name + '.py')))
        boot = contract.load_source(source / 'resource_boot.py', 'resource_boot')
        modules = boot.load()
        persist('SOURCE-FREEZE.json', dict(sources=sources, interpreter=interpreter,
                       git=contract.record('/usr/bin/git'), loaded=boot.loaded_sources(modules['build_profile'].__dict__)))
        original_lock = contract.record(lock_path)
        with Path(lock_path).open('rb') as stream:
            raw_lock = stream.read(65537)
        if len(raw_lock) > 65536 or sha256(raw_lock).hexdigest() != contract.LOCK:
            raise ValueError('exact corpus lock unavailable')
        with (out / 'lake-manifest.json').open('xb') as stream:
            stream.write(raw_lock)
        lock = contract.record(out / 'lake-manifest.json'); expected['lake-manifest.json'] = lock
        persist('LOCK-INPUT.json', dict(original=original_lock, frozen=lock,
                scope='Already exposed lock metadata; no dependency material acquired before episode.'))
        bounds = contract.limits(policy, min(start['acquisition_deadline_monotonic'],
                                             start['whole_deadline_monotonic']) - time.monotonic())
        persist('LIMITS.json', bounds)
        command = [sys.executable, '-I', '-S', str(source / 'acquisition_worker.py'),
                   str(out / 'lake-manifest.json'), str(out / 'materials')]
        reached = 'RESOURCE_SETUP'
        receipt = modules['resource_runner'].run(command, {}, bounds, out / 'resource', [out])
        if receipt.get('dispatch', {}).get('attempted'):
            reached = 'ACQUISITION'
        if (out / 'materials' / 'RESULT.json').is_file():
            result_path = out / 'materials' / 'RESULT.json'
            raw = result_path.read_bytes()
            expected['materials/RESULT.json'] = dict(path=str(result_path), sha256=sha256(raw).hexdigest(), bytes=len(raw))
            result = json.loads(raw)
        if receipt['terminal'] == 'COMPLETED':
            worker = contract.load_source(source / 'acquisition_git.py', 'acquisition_git')
            validation = contract.validate_worker(result, out / 'materials', worker, receipt)
            persist('MATERIAL-REVALIDATION.json', validation)
            ready = True
        for pair in sources.values():
            if any(contract.record(value['path']) != value for value in pair.values()):
                raise ValueError('source drift after acquisition')
        if contract.record(original_lock['path']) != original_lock or contract.record(seal['path']) != seal:
            raise ValueError('input drift after acquisition')
        for binding in expected.values():
            if contract.record(binding['path']) != binding:
                raise ValueError('phase authority artifact drift: ' + binding['path'])
        if time.monotonic() > start['acquisition_deadline_monotonic']:
            raise ValueError('ACQUISITION_DEADLINE_INCLUDING_CUSTODY')
    except BaseException as exc:
        error = dict(kind=type(exc).__name__, message=str(exc)); ready = False
    after = resource.getrusage(resource.RUSAGE_SELF)
    phase = dict(schema='ocm.f1.acquisition-phase.v1', terminal='MATERIAL_READY' if ready else 'CANNOT_CHECK',
                 error=error, resource=receipt, worker=result, semantic_checks_reached=0,
                 reached_phase=reached, whole_episode_open=ready, wall_before_phase_receipt_s=time.monotonic() - started,
                 supervisor_user_seconds=after.ru_utime-before.ru_utime,
                 supervisor_system_seconds=after.ru_stime-before.ru_stime,
                 cost_scope='Shared acquisition and custody; nested timers overlap; network wire bytes unmeasured.',
                 remaining_whole_seconds=contract.remaining_episode(start, time.monotonic(), start['boot_id']))
    contract.write(out / 'ACQUISITION.json', phase)
    if assigned is not None:
        cause = 'MATERIAL_READY' if ready else ((error or {}).get('message') or receipt.get('reason')
                                               or receipt.get('terminal') or 'INPUT_VALIDATION_FAILED')
        contract.write(out / 'ROWS-AFTER-ACQUISITION.json', dict(denominator=4, continuation_cursor=4,
                       rows=contract.row_states(assigned, ready, receipt, cause, reached),
                       claim='Phase state only; no semantic coverage, search, learning or transfer result.'))
    return phase


def main():
    if len(sys.argv) != 4 or not sys.flags.isolated or not sys.flags.no_site:
        raise SystemExit('use pinned Python -I -S acquisition_run.py REGISTRATION LOCK NEW_EPISODE')
    result = run(*sys.argv[1:])
    print(json.dumps(dict(terminal=result['terminal'], semantic_checks_reached=0, error=result['error'])))
    return 0 if result['terminal'] == 'MATERIAL_READY' else 2


if __name__ == '__main__':
    raise SystemExit(main())
