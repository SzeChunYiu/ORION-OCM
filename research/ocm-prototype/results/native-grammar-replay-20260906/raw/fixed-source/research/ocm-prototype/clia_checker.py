"""Independent host admission: exact CLIA grammar first, separate native Z3 second."""
import hashlib
import time
import clia_process
from clia_grammar import dump, forms, validate
from clia_tasks import signatures, validate_task

# Minimal neutral proposal schema; additional resource metadata is not authority.
PROPOSAL_SCHEMA = {
    'type': 'object',
    'required': ['status', 'candidate', 'task_sha256', 'grammar_id'],
    'properties': {'status': {'enum': ['SOLUTION', 'CANNOT_CHECK']}, 'candidate': {'type': 'string'},
                   'task_sha256': {'type': 'string'}, 'grammar_id': {'type': 'string'}},
}


def check(task, proposal, *, timeout_ms=5000, deadline_s=10):
    start = time.perf_counter(); cpu = time.process_time()
    base = {'grammar': 'FAIL', 'semantic': 'NOT_RUN', 'status': 'FAIL',
            'native_checker_invoked': False, 'metrics': {}}
    try:
        validate_task(task)
        if isinstance(proposal, dict) and proposal.get('status') == 'CANNOT_CHECK':
            base.update(status='CANNOT_CHECK', grammar='NOT_RUN', reason='proposer returned no checkable candidate')
            base['metrics']['check_total_wall_s'] = time.perf_counter() - start
            return base
        if not isinstance(proposal, dict) or proposal.get('status') != 'SOLUTION':
            raise ValueError('no proposed solution')
        if proposal.get('task_sha256') != task['task_sha256'] or proposal.get('grammar_id') != task['grammar']['id']:
            raise ValueError('proposal task/grammar binding mismatch')
        definitions = validate(proposal.get('candidate'), signatures(task))
        names = {str(x[1]): x for x in definitions}; commands = []; constraints = []
        for node in forms(task['original_sygus']):
            tag = str(node[0])
            if tag == 'synth-fun':
                commands.append(dump(names[str(node[1])]))
            elif tag == 'declare-var':
                commands.append(f'(declare-const {dump(node[1])} {dump(node[2])})')
            elif tag == 'define-fun':
                commands.append(dump(node))  # checked-in, source-bound helpers only
            elif tag == 'constraint':
                constraints.append(dump(node[1]))
            elif tag not in ('set-logic', 'check-synth'):
                raise ValueError('unsupported fixed task command')
        if not constraints:
            raise ValueError('no specification constraints')
        smt2 = '\n'.join(commands) + '\n(assert (not (and ' + ' '.join(constraints) + ')))\n'
        base['grammar'] = 'PASS'; base['metrics']['grammar_wall_s'] = time.perf_counter() - start
        native = clia_process.invoke('verify', {'smt2': smt2}, timeout_ms=timeout_ms, deadline_s=deadline_s)
        base.update({'semantic': native['status'], 'status': native['status'],
                     'native_checker_invoked': native['native_invoked'],
                     'verification_sha256': hashlib.sha256(smt2.encode()).hexdigest(),
                     'task_sha256': task['task_sha256'], 'grammar_id': task['grammar']['id']})
        base['metrics'].update(native['metrics'])
        for key in ('solver_result', 'solver', 'counterexample', 'reason', 'worker_exit', 'worker_error'):
            if key in native:
                base[key] = native[key]
    except OSError as exc:
        base.update(status='CANNOT_CHECK', grammar='CANNOT_CHECK', reason='fixed task custody unavailable: ' + str(exc))
    except (ValueError, TypeError, KeyError, IndexError, RecursionError) as exc:
        base['reason'] = f'{type(exc).__name__}: {exc}'
    base['metrics']['check_total_wall_s'] = time.perf_counter() - start
    base['metrics']['host_check_cpu_s'] = time.process_time() - cpu
    return base
