"""Pure proposal donor; full legitimate specification, never an expected program."""
import clia_process
from clia_tasks import signatures, validate_task
from clia_grammar import validate


def propose(task, *, timeout_ms=5000, deadline_s=15):
    try:
        validate_task(task)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        return {'status': 'CANNOT_CHECK', 'reason': str(exc), 'native_invoked': False}
    result = clia_process.invoke('synthesize', {'sygus': task['original_sygus']},
                                 timeout_ms=timeout_ms, deadline_s=deadline_s)
    result['native_search_contract'] = task['native_search_contract']
    if result['status'] == 'SOLUTION':
        try:
            validate(result['candidate'], signatures(task))
            result['grammar_preflight'] = 'PASS'
        except (ValueError, TypeError, IndexError, RecursionError) as exc:
            result.update(status='CANNOT_CHECK', grammar_preflight='FAIL', reason='native candidate outside accepted grammar: ' + str(exc))
    return {**result, 'task_sha256': task['task_sha256'], 'grammar_id': task['grammar']['id']}
