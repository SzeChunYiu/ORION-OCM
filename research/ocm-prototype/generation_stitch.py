"""Pinned donor call boundary. Import/fixture qualification does not invoke discovery."""
import importlib.metadata as metadata
import hashlib
from dataclasses import asdict
from generation_clia import encode, admit_macros, decode, equivalent, request
from clia_tasks import signatures, validate_task

VERSION = '0.1.29'
SETTINGS = {'iterations': 1, 'max_arity': 2, 'threads': 1, 'silent': True}


def donor():
    if metadata.version('stitch-core') != VERSION:
        raise ValueError('pinned Stitch version mismatch')
    import stitch_core
    return stitch_core


def prepare(experiences):
    """Require supplied exact public tasks and PASS checks before learning input exists."""
    if len(experiences) < 2:
        raise ValueError('at least two distinct public functions required')
    out = []
    for task, candidate in experiences:
        validate_task(task)
        from clia_checker import check
        receipt = check(task, {'status': 'SOLUTION', 'candidate': candidate,
                              'task_sha256': task['task_sha256'], 'grammar_id': task['grammar']['id']})
        if receipt['status'] != 'PASS':
            raise ValueError('TRAIN candidate lacks fixed checker PASS: '+receipt['status'])
        programs = encode(candidate, signatures(task))
        if len(programs) != 1:
            raise ValueError('one function per public experience')
        out.append({'task': task, 'candidate': candidate, 'program': programs[0]['program'], 'check': receipt})
    if len({x['task']['task_id'] for x in out}) != len(out):
        raise ValueError('distinct public tasks required; semantic equivalence grouping remains external')
    return out


def induce(experiences):
    """UNEXECUTED until preregistration: one fixed donor call, no tuning/retry loop."""
    prepared = prepare(experiences)
    result = donor().compress([x['program'] for x in prepared],
                              tasks=[x['task']['task_id'] for x in prepared], **SETTINGS)
    return assess(result, prepared)


def assess(result, prepared):
    """Keep the actual returned JSON even if typed admission/decoding refuses it."""
    receipt = {'status': 'REFUSED_DONOR_RESULT', 'settings': dict(SETTINGS),
               'raw': result.json, 'library': {}, 'training': prepared,
               'rewrite_checks': [], 'later_generation_consumption': 'NOT_RUN'}
    try:
        library = admit_macros([{'name': a.name, 'body': a.body, 'arity': a.arity} for a in result.abstractions])
        if len(result.rewritten) != len(prepared):
            raise ValueError('donor changed experience inventory')
        for x, rewritten in zip(prepared, result.rewritten):
            sigs = signatures(x['task']); name = next(iter(sigs))
            decoded = decode(rewritten, name, sigs, library)
            check = equivalent(x['candidate'], decoded['candidate'], sigs)
            receipt['rewrite_checks'].append({'decoded': decoded, 'equivalence': check})
        status = 'NO_NEW_ABSTRACTION' if not library else 'PROPOSED_ABSTRACTIONS'
        checks = receipt['rewrite_checks']
        if any(x['equivalence']['status'] != 'PASS' for x in checks):
            status = 'CANNOT_CHECK_REWRITE' if any(x['equivalence']['status'] == 'CANNOT_CHECK' for x in checks) else 'REFUSED_REWRITE'
        receipt.update(status=status, library={name: asdict(m) for name, m in library.items()})
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError) as exc:
        receipt['reason'] = type(exc).__name__+': '+str(exc)
    return receipt


def search_request(task, library, route):
    if route not in ('implicit_primitive', 'explicit_primitive', 'explicit_macro'):
        raise ValueError('unknown public feasibility route')
    validate_task(task)
    text = task['original_sygus'] if route == 'implicit_primitive' else request(task, library if route == 'explicit_macro' else {})
    return {'route': route, 'task_sha256': task['task_sha256'], 'sygus': text,
            'sygus_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'consumption': 'CANNOT_CHECK_CONSUMPTION',
            'reason': 'Existing cvc5 worker returns a builtin solution term, not a learned-production derivation; submitted grammar is not use evidence.'}
