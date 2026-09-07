"""Fixed registration and append-only shared material phase; no proof dispatch."""
from hashlib import sha256
from pathlib import Path
import json
import sys
import types

SEAL = '9d02378c93369da33ccd8940509474422d898bee899c42ce28e7bc6958362a2e'
PYTHON = 'edca1fc80dbd58182c849c13707fb6bfb522b0d7049adc408225f7c69b124d3b'
COMMIT = 'aa2d8b34692b16c70f699536de0d8e75b9a3e9ef'
LOCK = '435fe2ab2550e2b82c0a93fd421c96d197d6dd55bc739481e2a4a07e04b979bf'
STAGES = ('RESOURCE_SETUP', 'ACQUISITION', 'BUILD', 'ASSOCIATION', 'EXPORT', 'PREPARE', 'CHECK')


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def write(path, value):
    with Path(path).open('xb') as out:
        out.write(canonical(value))


def record(path):
    path = Path(path).absolute()
    if path.resolve(strict=True) != path or not path.is_file():
        raise ValueError('canonical regular file required: ' + str(path))
    digest = sha256(); size = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block); size += len(block)
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=size)


def load_source(path, name):
    path = Path(path); raw = path.read_bytes()
    module = types.ModuleType(name); module.__file__ = str(path)
    module.__source_record__ = record(path)
    if module.__source_record__['sha256'] != sha256(raw).hexdigest():
        raise ValueError('source changed during loading')
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def registration(path):
    path = Path(path).resolve(strict=True)
    seal_raw = (path / 'SEAL.json').read_bytes()
    binding = dict(path=str(path / 'SEAL.json'), sha256=sha256(seal_raw).hexdigest(), bytes=len(seal_raw))
    if binding['sha256'] != SEAL:
        raise ValueError('fixed registration seal differs')
    seal = json.loads(seal_raw); consumed = {}
    for name, wanted in seal['files'].items():
        if name in ('ASSIGNMENTS.json', 'POLICY.json'):
            raw = (path / name).read_bytes()
            actual = dict(sha256=sha256(raw).hexdigest(), bytes=len(raw))
            consumed[name] = json.loads(raw)
        else:
            actual = record(path / name)
        if {key: actual[key] for key in ('sha256', 'bytes')} != wanted:
            raise ValueError('registration drift: ' + name)
    assigned = consumed['ASSIGNMENTS.json']
    if assigned['denominator'] != 4 or assigned['continuation_cursor'] != 4 or len(assigned['rows']) != 4:
        raise ValueError('fixed four assignments required')
    return binding, assigned, consumed['POLICY.json']


def limits(policy, remaining):
    p = policy['limits']
    if remaining <= 0:
        raise ValueError('ACQUISITION_DEADLINE')
    return dict(memory_bytes=p['memory_bytes'], memsw_bytes=p['memory_and_swap_bytes'],
                cpu_quota_us=p['cpu_equivalents'] * 100000, cpu_period_us=100000,
                pids=p['pids'], max_file_bytes=p['file_size_bytes'],
                min_available_bytes=p['initial_mem_available_bytes'],
                min_free_bytes=p['initial_disk_free_bytes'], stop_free_bytes=p['stop_disk_free_bytes'],
                max_owned_bytes=p['stop_owned_new_bytes'], wall_s=remaining,
                term_grace_s=p['term_grace_seconds'], reap_s=p['forced_reap_seconds'],
                poll_s=p['disk_poll_seconds'])


def row_states(assignments, material_ready, resource_receipt, cause, phase='ACQUISITION'):
    rows = []
    setup = resource_receipt.get('controller_readback') is not None
    attempted = resource_receipt.get('dispatch', {}).get('attempted', False)
    for assigned in assignments['rows']:
        stages = []
        for stage in STAGES:
            state = 'NOT_RUN'; reason = cause
            if stage == 'RESOURCE_SETUP':
                state = 'COMPLETED' if setup else 'NOT_RUN' if phase == 'INPUT_VALIDATION' else 'CANNOT_CHECK'
            elif stage == 'ACQUISITION' and (attempted or material_ready):
                state = 'COMPLETED' if material_ready else 'CANNOT_CHECK'
            elif material_ready:
                reason = 'PENDING_QUALIFIED_EVALUATOR_WITHIN_ORIGINAL_DEADLINE'
            stages.append(dict(stage=stage, state=state, cause=reason,
                               cost_reference='ACQUISITION.json' if stage in STAGES[:2] else None))
        rows.append(dict(key=assigned['key'], assignment_rank=assigned['assignment_rank'], stages=stages))
    return rows


def new_output(destination, inputs):
    out = Path(destination).absolute()
    if out.parent.resolve(strict=True) != out.parent:
        raise ValueError('canonical output parent required')
    for value in inputs:
        source = Path(value).resolve(strict=True)
        if source.is_relative_to(out) or out.is_relative_to(source):
            raise ValueError('output overlaps input: ' + str(source))
    out.mkdir()
    return out


def validate_worker(result, root, worker, receipt):
    dispatch = receipt.get('dispatch', {})
    if (receipt.get('terminal') != 'COMPLETED' or type(receipt.get('returncode')) is not int
            or receipt['returncode'] != 0 or receipt.get('evidence_complete') is not True
            or dispatch.get('state') != 'STARTED' or dispatch.get('attempted') is not True
            or type(dispatch.get('pid')) is not int or dispatch['pid'] <= 0
            or not all(receipt.get('cleanup', {}).get(key) is True
                       for key in ('reaped', 'members_empty', 'controllers_removed'))):
        raise ValueError('acquisition process or cleanup incomplete')
    if type(result) is not dict or result.get('output') != str(root):
        raise ValueError('worker result root differs')
    if result.get('transport') != 'PRODUCTION_SUBPROCESS':
        raise ValueError('qualification transport is not production acquisition')
    value = worker.revalidate(result, root)
    if value.get('terminal') != 'MATERIAL_BYTES_REVALIDATED' or type(value.get('packages')) is not int or value['packages'] != 9:
        raise ValueError('material revalidation incomplete')
    return value


def remaining_episode(start, now, boot_id):
    if boot_id != start['boot_id'] or now < start['monotonic_seconds']:
        raise ValueError('episode clock identity unavailable')
    return max(0, start['whole_deadline_monotonic'] - now)
