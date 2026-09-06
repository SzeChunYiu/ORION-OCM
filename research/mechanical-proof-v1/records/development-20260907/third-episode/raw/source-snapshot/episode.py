"""One source-bound exposed proof episode; no learning, FLT or novelty promotion."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import time

from isolation import run_isolated
from kernel_check import check_staged
from lean_transport import render_term
from proof_check import stage_candidate
from runtime_bundle import file_hash, verify_tree

HERE = Path(__file__).resolve().parent
WORKER_FILES = ('worker.py', 'worker_guard.py', 'f0_terms.py', 'f0_search.py')


def validate_worker(record):
    if type(record) is not dict:
        raise ValueError('worker must return one result object')
    audit = record.get('worker_audit', {})
    if (type(audit) is not dict or audit.get('schema') != 'mechanical-worker-audit-v1' or
            audit.get('guard_sealed') is not True or audit.get('prohibited_events') != []):
        raise ValueError('worker boundary did not remain sealed')
    imports = audit.get('imported_modules')
    if type(imports) is not list:
        raise ValueError('missing module inventory')
    names = set()
    for entry in imports:
        name, origin = entry.get('name'), entry.get('origin')
        if type(name) is not str or type(origin) is not str or name in names:
            raise ValueError('invalid or duplicated module inventory entry')
        names.add(name)
        if name in {'f0_terms', 'f0_search', 'worker_guard'}:
            valid = origin == '/app/' + name + '.py'
        elif name == '__main__':
            valid = origin == 'trusted-entrypoint'
        else:
            valid = (name.split('.')[0] in sys.stdlib_module_names and
                     (origin in {'built-in', 'frozen'} or
                      (origin.startswith('/python/lib/python3.11/') and
                       not {'site-packages', 'dist-packages'} & set(origin.split('/')))))
        if not valid:
            raise ValueError('unregistered worker module origin')
    if not {'f0_terms', 'f0_search', 'worker_guard'} <= names:
        raise ValueError('incomplete learner module inventory')
    status = record.get('status')
    if status not in {'FOUND', 'EXHAUSTED_REGISTERED_BOUND', 'CANNOT_CHECK'}:
        raise ValueError('unregistered worker terminal')
    if (status == 'FOUND') != (record.get('candidate') is not None):
        raise ValueError('worker candidate disagrees with proposal terminal')
    counters = record.get('counters')
    if type(counters) is not dict or any(type(v) is not int or v < 0 for v in counters.values()):
        raise ValueError('invalid work counters')
    occurrences = {'proof_term': {}, 'type_annotations': {}}
    candidate = record.get('candidate')
    if candidate is not None:
        render_term(candidate)  # Independent constructor/scope/constant validation.
    pending = [(candidate, False)] if candidate is not None else []
    while pending:
        node, annotation = pending.pop()
        if node[0] == 'const':
            group = occurrences['type_annotations' if annotation else 'proof_term']
            key = str(node[1]); group[key] = group.get(key, 0) + 1
        elif node[0] in {'app', 'pi', 'lam'}:
            pending += [(node[1], annotation or node[0] in {'pi', 'lam'}),
                        (node[2], annotation or node[0] == 'pi')]
    used = sorted(int(k) for k in set(occurrences['proof_term']) | set(occurrences['type_annotations']))
    if audit.get('constant_occurrences') != occurrences or record.get('used_constants') != used:
        raise ValueError('worker dependency report differs from candidate data')
    return record


def canonical_task(task):
    return (json.dumps(task, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def _source_inventory():
    return {p.name: file_hash(p) for p in sorted(HERE.iterdir())
            if p.is_file() and (p.suffix == '.py' or p.name == 'Target.lean')}


def _runtime_check(runtime):
    verify_tree(runtime['lean_root'], runtime['lean_files'])
    verify_tree(runtime['python']['directory'], runtime['python']['files'])
    for data in runtime['shared_libraries']['files'].values():
        if file_hash(data['source']) != data['sha256']:
            raise ValueError('copied shared-library identity changed')


def run_task(task, registered_sha256, runtime, destination, *, timeout_s=30):
    """The caller freezes the task digest before launching a separate learner.

    The digest establishes the declared information boundary, not mathematical
    correctness of that declaration. The checker always uses its fixed target.
    """
    started = time.monotonic()
    destination = Path(destination)
    destination.mkdir(exist_ok=False)
    result = {'schema': 'mechanical-f0-episode-v1', 'terminal': 'CANNOT_CHECK', 'reason': '',
              'claim_scope': 'Exposed application-closure apparatus; not learned cognition or FLT progress.',
              'registered_task_sha256': registered_sha256, 'source_files': _source_inventory(),
              'worker': None, 'checker': None}
    try:
        snapshot = destination / 'source-snapshot'
        snapshot.mkdir()
        for name, digest in result['source_files'].items():
            shutil.copyfile(HERE / name, snapshot / name)
            if file_hash(snapshot / name) != digest:
                raise ValueError('source snapshot changed during capture')
        raw = canonical_task(task)
        if sha256(raw).hexdigest() != registered_sha256:
            raise ValueError('task differs from separately registered input')
        _runtime_check(runtime)
        app, inputs = destination / 'app', destination / 'input'
        app.mkdir(); inputs.mkdir()
        for name in WORKER_FILES:
            shutil.copyfile(HERE / name, app / name)
            if file_hash(app / name) != result['source_files'][name]:
                raise ValueError('worker source changed during copy')
        (inputs / 'task.json').write_bytes(raw)
        libraries = runtime['shared_libraries']['mounts']
        python = runtime['python']
        process = run_isolated(['/python/bin/python3.11', '-I', '-S', '-B', '/app/worker.py', '/input/task.json'],
                               read_only=[(Path(python['directory']), '/python'), (app.resolve(), '/app'),
                                          (inputs.resolve(), '/input'), *libraries],
                               executable_sha256=python['python_sha256'], env={'LANG': 'C.UTF-8'},
                               timeout_s=timeout_s, max_output_bytes=1048576)
        result['worker_process'] = process
        (destination / 'worker-process.json').write_text(json.dumps(process, indent=2) + '\n')
        if process['terminal'] != 'COMPLETED' or process['returncode'] != 0 or process['stderr'].strip():
            raise ValueError('learner process incomplete or emitted unexpected diagnostics')
        proposal = validate_worker(json.loads(process['stdout']))
        result['worker'] = proposal
        if proposal['status'] != 'FOUND':
            result.update(terminal=proposal['status'], reason=proposal['reason'])
        else:
            stage = stage_candidate(proposal['candidate'], destination / 'checker')
            checked = check_staged(stage, runtime['lean_root'], libraries, timeout_s=timeout_s)
            result['checker'] = checked
            result.update(terminal=checked['terminal'], reason=checked['reason'])
        if result['source_files'] != _source_inventory():
            raise ValueError('host source changed during episode')
        if (inputs / 'task.json').read_bytes() != raw:
            raise ValueError('registered input changed during episode')
        for name in WORKER_FILES:
            if file_hash(app / name) != result['source_files'][name]:
                raise ValueError('worker source changed during episode')
        _runtime_check(runtime)
    except (ValueError, KeyError, TypeError, OSError, RecursionError) as exc:
        result.update(terminal='CANNOT_CHECK', reason=type(exc).__name__ + ': ' + str(exc))
    result['wall_s'] = time.monotonic() - started
    result['cost_scope'] = ('Full episode validation, source/data copying, isolated search, fresh dependency/target/proof '
                            'compilation and final custody checks. Runtime acquisition/preparation recorded separately. '
                            'CPU/RSS/energy and lifetime acquisition benefit are not measured.')
    (destination / 'episode.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return result
