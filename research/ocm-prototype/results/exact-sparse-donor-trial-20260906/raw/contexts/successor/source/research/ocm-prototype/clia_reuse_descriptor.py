"""Data-only checked CLIA descriptor shared by the vessel and ordinary native library."""
import hashlib
from pathlib import Path
import z3
import clia_checker
from clia_grammar import dump, validate as grammar_validate
from clia_tasks import digest, signatures, validate_task

HERE = Path(__file__).parent
TASKS = frozenset({'jmbl_fg_max3', 'jmbl_fg_mpg_guard2'})


def checker_prior():
    names = ('clia_checker.py', 'clia_grammar.py', 'clia_tasks.py', 'clia_process.py',
             'clia_worker.py', 'clia_reuse_descriptor.py', 'clia_reuse_apply.py')
    return {'z3': z3.get_full_version(), 'files': {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names}}


def profile(value):
    if not isinstance(value, dict) or set(value) != {'lower', 'upper'}:
        raise ValueError('support must include both warrant bounds')
    result = {}
    for bound in ('lower', 'upper'):
        terms = value[bound]
        if not isinstance(terms, list) or any(not isinstance(t, list) or any(not isinstance(e, str) or not e for e in t) for t in terms):
            raise ValueError('support must be data-only evidence identifier families')
        sets = {frozenset(t) for t in terms}
        result[bound] = sorted(sorted(t) for t in sets if not any(s < t for s in sets))
    if any(not any(set(u) <= set(l) for u in result['upper']) for l in result['lower']):
        raise ValueError('lower support must imply upper support')
    return result


def liveness(support, revoked):
    p = profile(support); revoked = set(revoked)
    if any(not revoked.intersection(t) for t in p['lower']): return 'LIVE'
    if not any(not revoked.intersection(t) for t in p['upper']): return 'DEAD'
    return 'UNKNOWN'


def proposal(desc):
    return dict(status='SOLUTION', candidate=desc['candidate'], task_sha256=desc['task']['task_sha256'],
                grammar_id=desc['task']['grammar']['id'])


def certificate(receipt):
    if not isinstance(receipt, dict): raise ValueError('missing universal certificate')
    if any(receipt.get(k) != 'PASS' for k in ('status', 'grammar', 'semantic')):
        raise ValueError('universal verification did not PASS: ' + str(receipt.get('reason', receipt.get('status'))))
    return {k: receipt[k] for k in ('status', 'grammar', 'semantic', 'verification_sha256', 'task_sha256', 'grammar_id', 'solver')}


def create(task, candidate, support, *, history=()):
    validate_task(task)
    if task['task_id'] not in TASKS: raise ValueError('outside the two-function adapter contract')
    if not isinstance(candidate, dict) or candidate.get('task_sha256') != task['task_sha256'] or candidate.get('grammar_id') != task['grammar']['id'] or candidate.get('status') != 'SOLUTION':
        raise ValueError('proposal identity or status mismatch')
    definitions = grammar_validate(candidate.get('candidate'), signatures(task))
    if len(definitions) != 1: raise ValueError('exactly one function required')
    if not isinstance(history, (list, tuple)) or any(not isinstance(e, str) or not e for e in history):
        raise ValueError('history identifiers must be strings')
    data = {'schema': 'ocm.clia-executable.v1', 'task': task, 'candidate': '\n'.join(dump(x) for x in definitions),
            'support': profile(support), 'history_only': sorted(set(history)), 'checker_prior': checker_prior()}
    if set(data['history_only']).intersection(e for terms in data['support'].values() for term in terms for e in term):
        raise ValueError('history-only provenance cannot be a truth support premise')
    data['program_sha256'] = digest({'task_sha256': task['task_sha256'], 'candidate': data['candidate']})
    checked = clia_checker.check(task, proposal(data))
    data['universal_certificate'] = certificate(checked)
    data['universal_check'] = checked
    data['id'] = digest(data)
    return data


def validate(desc):
    keys = {'schema', 'task', 'candidate', 'support', 'history_only', 'checker_prior', 'program_sha256', 'universal_certificate', 'universal_check', 'id'}
    if not isinstance(desc, dict) or set(desc) != keys or desc['schema'] != 'ocm.clia-executable.v1':
        raise ValueError('invalid executable descriptor schema')
    if desc['id'] != digest({k: v for k, v in desc.items() if k != 'id'}): raise ValueError('descriptor identity changed')
    validate_task(desc['task'])
    if desc['task']['task_id'] not in TASKS: raise ValueError('unsupported function')
    if desc['checker_prior'] != checker_prior(): raise ValueError('checker/evaluator prior changed; reacquire explicitly')
    if profile(desc['support']) != desc['support']: raise ValueError('noncanonical support')
    if not isinstance(desc['history_only'], list) or any(not isinstance(x, str) for x in desc['history_only']): raise ValueError('invalid history metadata')
    definitions = grammar_validate(desc['candidate'], signatures(desc['task']))
    if len(definitions) != 1 or '\n'.join(dump(x) for x in definitions) != desc['candidate']: raise ValueError('noncanonical program')
    if desc['program_sha256'] != digest({'task_sha256': desc['task']['task_sha256'], 'candidate': desc['candidate']}): raise ValueError('program identity changed')
    c = desc['universal_certificate']; certificate(c)
    if certificate(desc['universal_check']) != c: raise ValueError('universal check receipt binding mismatch')
    if set(desc['history_only']).intersection(e for terms in desc['support'].values() for term in terms for e in term): raise ValueError('history overlaps authority')
    if c['task_sha256'] != desc['task']['task_sha256'] or c['grammar_id'] != desc['task']['grammar']['id']: raise ValueError('certificate task mismatch')
    return desc


def verify_import(desc, receipts=None):
    """An untrusted imported descriptor receives a real universal check once, not on application."""
    validate(desc)
    checked = clia_checker.check(desc['task'], proposal(desc))
    if receipts is not None: receipts.append(checked)
    if certificate(checked) != desc['universal_certificate']:
        raise ValueError('imported universal certificate mismatch')
    return desc
