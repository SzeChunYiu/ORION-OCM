"""Data-only isolated learner entry. The external runner binds files and runtime.

The audit guard protects this registered, trusted source closure; it is not a
sandbox for arbitrary Python programs. Only the independent kernel may accept proof.
"""
import json
import os
import sys

MAX_INPUT_BYTES = 262144
MAX_JSON_NODES = 32768
MAX_JSON_DEPTH = 128
# -I excludes the script directory; add only this trusted, externally bound app root.
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from worker_guard import PolicyError, install_guard


def parse_task(raw):
    if type(raw) is not bytes or len(raw) > MAX_INPUT_BYTES:
        raise ValueError('input byte bound or representation')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError('nonfinite JSON number')
    try:
        task = json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)
    except (UnicodeError, RecursionError) as exc:
        raise ValueError('invalid JSON encoding or depth') from exc
    pending, count = [(task, 0)], 0
    while pending:
        value, depth = pending.pop(); count += 1
        if count > MAX_JSON_NODES or depth > MAX_JSON_DEPTH:
            raise ValueError('JSON node/depth bound')
        if type(value) is float:
            raise ValueError('floating JSON numbers are outside the term transport')
        if isinstance(value, dict):
            pending.extend((child, depth + 1) for child in value.values())
        elif isinstance(value, list):
            pending.extend((child, depth + 1) for child in value)
    if (type(task) is not dict or not {'goal', 'constants'} <= task.keys() or
            task.keys() - {'goal', 'constants', 'limits'}):
        raise ValueError('task fields must be goal, constants, optional limits')
    if 'limits' in task and type(task['limits']) is not dict:
        raise ValueError('limits must be a data mapping')
    return task


def occurrences(candidate):
    result = {'proof_term': {}, 'type_annotations': {}}
    def visit(node, annotation=False):
        tag = node[0]
        if tag == 'const':
            dest = result['type_annotations' if annotation else 'proof_term']
            key = str(node[1]); dest[key] = dest.get(key, 0) + 1
        elif tag in ('app', 'pi', 'lam'):
            visit(node[1], annotation or tag in ('pi', 'lam'))
            visit(node[2], annotation or tag == 'pi')
    if candidate is not None:
        visit(candidate)
    return result


def empty_audit():
    return {'schema': 'mechanical-worker-audit-v1', 'guard_sealed': False,
            'imported_modules': [], 'prohibited_events': [],
            'constant_occurrences': {'proof_term': {}, 'type_annotations': {}}}


def refusal(reason):
    return {'status': 'CANNOT_CHECK', 'candidate': None, 'reason': reason,
            'counters': {}, 'limits': {}, 'used_constants': [], 'worker_audit': empty_audit()}


def execute(raw):
    guard = None
    try:
        guard = install_guard()
        task = parse_task(raw)
        from f0_search import SearchLimits, search
        guard.seal()  # Dataclass setup/import execution has completed.
        limits = SearchLimits(**task.get('limits', {}))
        found = search(task['goal'], task['constants'], limits)
        result = {key: getattr(found, key) for key in
                  ('status', 'candidate', 'reason', 'counters', 'limits', 'used_constants')}
        result['used_constants'] = list(result['used_constants'])
    except (ValueError, TypeError, OSError, ImportError, RecursionError) as exc:
        result = refusal(type(exc).__name__ + ': ' + str(exc))
    try:
        audit = guard.report() if guard is not None else empty_audit()
    except PolicyError as exc:
        result = refusal(str(exc))
        audit = {'schema': 'mechanical-worker-audit-v1', 'guard_sealed': guard.sealed,
                 'imported_modules': [], 'prohibited_events': list(guard.denied)}
    if audit['prohibited_events']:
        result = refusal('prohibited dispatch recorded during worker execution')
    audit['constant_occurrences'] = occurrences(result['candidate'])
    result['worker_audit'] = audit
    return result


def main():
    if sys.argv[1:] != ['/input/task.json'] or os.path.realpath(__file__) != '/app/worker.py':
        result = refusal('production entry requires /app/worker.py /input/task.json')
    else:
        try:
            with open('/input/task.json', 'rb') as stream:
                raw = stream.read(MAX_INPUT_BYTES + 1)
            result = execute(raw)
        except OSError as exc:
            result = refusal(type(exc).__name__ + ': ' + str(exc))
    print(json.dumps(result, sort_keys=True, separators=(',', ':'), allow_nan=False))


if __name__ == '__main__':
    main()
