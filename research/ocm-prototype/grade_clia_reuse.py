"""External exact-integer grading; row diagnostics never establish study completeness."""

TASKS = {'jmbl_fg_max3', 'jmbl_fg_mpg_guard2'}


def arguments(value):
    if not isinstance(value, list) or len(value) != 3 or any(type(x) is not int or x.bit_length() > 4096 for x in value):
        raise ValueError('three bounded exact integers required')
    return value


def oracle(task_id, values):
    """Public specifications only; no import of acquired code, cvc5, Z3 or actor."""
    x, y, z = arguments(values)
    if task_id == 'jmbl_fg_max3': return max(x, y, z)
    if task_id == 'jmbl_fg_mpg_guard2': return x + y if x + y + z >= 1 else x - y
    raise ValueError('unknown public task')


def support_state(profile, revoked):
    """Independent two-bound monotone-support oracle; UNKNOWN is not a refusal."""
    if not isinstance(profile, dict) or set(profile) != {'lower', 'upper'}: raise ValueError('missing support bounds')
    for terms in profile.values():
        if not isinstance(terms, list) or any(not isinstance(t, list) or any(not isinstance(e, str) or not e for e in t) for t in terms):
            raise ValueError('invalid support terms')
    if any(not any(set(u) <= set(l) for u in profile['upper']) for l in profile['lower']):
        raise ValueError('lower does not imply upper')
    if not isinstance(revoked, list) or any(not isinstance(e, str) or not e for e in revoked): raise ValueError('invalid revoked IDs')
    if any(not set(t).intersection(revoked) for t in profile['lower']): return 'LIVE'
    if not any(not set(t).intersection(revoked) for t in profile['upper']): return 'DEAD'
    return 'UNKNOWN'


def _binding(row, binding):
    request = row['request']
    if row.get('arm') not in {'native', 'ocm'}: raise ValueError('explicit arm required')
    if set(request) != {'kind', 'program_id', 'arguments'} or request['kind'] != 'clia_apply': raise ValueError('request contract')
    if request['program_id'] != binding['descriptor_id'] or binding['task_id'] not in TASKS: raise ValueError('request/F1 binding')
    arguments(request['arguments'])
    return request


def _ocm_support_refusal(result, binding):
    aid = 'clia:executable:' + binding['descriptor_id']; op = 'apply:' + binding['descriptor_id']
    entries = result.get('trace', {}).get('stages', [])
    stages = {s['stage']: s for s in entries}
    if len(stages) != len(entries): return False
    ground = stages.get('GROUNDING', {}); extract = stages.get('EXTRACTION', {})
    composition = stages.get('COMPOSITION', {}); commit = stages.get('COMMITMENT', {})
    counters = result.get('counters', {})
    return (ground.get('status') == 'PASS' and aid in ground.get('object_ids', [])
        and extract.get('reason') == 'REACTING_SUBGRAPH' and extract.get('status') == 'PASS'
        and aid in extract.get('payload', {}).get('exploratory_only_atoms', [])
        and aid not in extract.get('payload', {}).get('warranted_atoms', [])
        and op in result.get('catalogue', []) and op not in composition.get('object_ids', [])
        and op not in counters.get('catalogue_visits', []) and composition.get('status') == 'PASS'
        and all(type(counters.get(k)) is int and counters[k] == 0 for k in ('application_calls', 'synthesis_dispatches'))
        and commit.get('status') == 'FAIL' and commit.get('reason', '').startswith('REFUSED:'))


def _policy(row, binding):
    result = row['result']; authority = row.get('authority', {}); delta = row.get('invocation_delta', {})
    registration = binding.get('registration'); revoked = authority.get('revoked', [])
    if not isinstance(registration, list) or not registration or any(not isinstance(e, str) or not e for e in registration): return False
    if not isinstance(revoked, list) or any(not isinstance(e, str) for e in revoked): return False
    if authority.get('liveness') != 'DEAD' or not set(registration) <= set(revoked): return False
    try:
        if support_state(binding['support'], revoked) != 'DEAD': return False
    except (KeyError, ValueError, TypeError): return False
    support_ids = {e for terms in binding['support'].values() for term in terms for e in term}
    if not set(registration) <= support_ids: return False
    if any(type(delta.get(k)) is not int or delta[k] != 0 for k in ('synthesize', 'application')): return False
    expected = 'REFUSED_DEAD_SUPPORT' if row['arm'] == 'native' else 'NOT_ADMITTED'
    if result.get('status') != expected: return False
    if row['arm'] == 'ocm' and not _ocm_support_refusal(result, binding): return False
    if 'answer' not in result or result['answer'] is not None: return False
    if any(result.get(k) is not None for k in ('admitted_id', 'record_id', 'proposal_diagnostic', 'error')): return False
    if result.get('reason') not in (None, 'DEAD_SUPPORT', 'AUTHORITY_WITHDRAWN'): return False
    if result.get('solve_status') == 'CANNOT_CHECK': return False
    return not any(c.get('status') == 'CANNOT_CHECK' for c in result.get('checks', []))


def _checked(result, answer, binding):
    if result['status'] == 'ACCEPTED_PARENT': checks = [result.get('check', {})]
    else:
        checks = [c for c in result.get('checks', []) if c.get('phase') == 'admission'
                  and c.get('operator') == 'apply:' + binding['descriptor_id']]
    if len(checks) != 1 or checks[0].get('status') != 'PASS': return False
    check = checks[0]
    for key in ('program_id', 'arguments', 'value'):
        if key in check and (check[key] != answer[key] or (key == 'value' and type(check[key]) is not int)): return False
    if 'arguments' in check: arguments(check['arguments'])
    return True


def grade_math(row, binding, *, authorized):
    """Per-row quality/policy diagnosis. Caller must independently verify custody/meter/audits."""
    try:
        if type(authorized) is not bool: raise ValueError('explicit phase authorization required')
        request = _binding(row, binding); result = row['result']
        if not authorized:
            status = 'EXPECTED_POLICY_REFUSAL' if _policy(row, binding) else 'REFUSAL_NOT_ESTABLISHED'
            return {'status': status, 'support_independently_checked': status == 'EXPECTED_POLICY_REFUSAL'}
        status = result.get('status')
        selected = ((row['arm'] == 'ocm' and status == 'ADMITTED' and isinstance(result.get('admitted_id'), str) and bool(result['admitted_id']))
                    or (row['arm'] == 'native' and status == 'ACCEPTED_PARENT' and isinstance(result.get('record_id'), str) and bool(result['record_id'])))
        answer = result.get('answer')
        if not selected or not isinstance(answer, dict): return {'status': 'NO_SELECTED_VALUE'}
        if (answer.get('status') != 'APPLIED' or answer.get('program_id') != binding['descriptor_id']
                or answer.get('program_sha256') != binding['program_sha256']): return {'status': 'WRONG_BINDING'}
        arguments(answer.get('arguments'))
        if answer['arguments'] != request['arguments']: return {'status': 'WRONG_BINDING'}
        if type(answer.get('value')) is not int: return {'status': 'WRONG_VALUE'}
        expected = oracle(binding['task_id'], request['arguments'])
        if answer['value'] != expected: return {'status': 'WRONG_VALUE', 'expected': expected}
        if not _checked(result, answer, binding): return {'status': 'CHECK_NOT_PASSED'}
        return {'status': 'CORRECT_VALUE', 'expected': expected}
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        return {'status': 'WRONG_BINDING', 'reason': str(exc)}


def grade_capture(root):
    """Fixed development denominators; incomplete cost custody never becomes zero."""
    from grade_clia_reuse_capture import collect
    observed = dict(schema='ocm.reuse.external-grade.v1', scope='PUBLIC_DEVELOPMENT_ONLY',
        stages_checked=0, arms={a: {'math': [], 'syntax': []} for a in ('native', 'ocm')},
        audits=[], invocations=[], resources=[], cost={'status': 'CANNOT_CHECK_COST',
        'total_process_tree_cpu_s': None, 'reason': 'No verified complete descendant CPU custody; raw scopes retained. Capture excludes F0 construction and original donor training; no whole-lifetime efficiency inference.'})
    try:
        collect(root, observed)
        supported = True
        for data in observed['arms'].values():
            counts = {s: sum(r['status'] == s for r in data['math']) for s in sorted({r['status'] for r in data['math']})}
            data['counts'] = counts
            complete = len(data['math']) == 36 and sum(r['authorized'] for r in data['math']) == 34 and len(data['syntax']) == 5
            good = complete and counts.get('CORRECT_VALUE', 0) == 34 and counts.get('EXPECTED_POLICY_REFUSAL', 0) == 2
            trees = [r['words'] for r in data['syntax'] if r['status'] == 'VALID_STRUCTURE']
            data['syntax_retained'] = len(trees) == 5 and all(t == trees[0] for t in trees)
            supported &= good and data['syntax_retained']
        native, ocm = [observed['arms'][a] for a in ('native', 'ocm')]
        observed['syntax_parent_equality'] = len(native['syntax']) == len(ocm['syntax']) == 5 and all(a['words'] == b['words'] for a, b in zip(native['syntax'], ocm['syntax']))
        supported &= observed['syntax_parent_equality']
        all_math = [r for data in observed['arms'].values() for r in data['math']]
        failure = 'NO_EXECUTABLE_REUSE'
        if any(r['cannot_check'] for r in all_math) or any(r['status'] != 'VALID_STRUCTURE' for data in observed['arms'].values() for r in data['syntax']): failure = 'CANNOT_CHECK_FUNCTION'
        if any(r['status'] in ('WRONG_VALUE', 'WRONG_BINDING', 'CHECK_NOT_PASSED') for r in all_math): failure = 'WRONG_APPLICATION'
        if any(r['unauthorized_selected'] for r in all_math): failure = 'DEPENDENCY_UNSOUND'
        observed['function'] = 'EXECUTABLE_REUSE_DEVELOPMENT_SUPPORTED' if supported else failure
        observed['parent'] = 'PARENT_SUFFICIENT_FUNCTION_ONLY' if supported else 'NOT_ESTABLISHED'
    except (KeyError, ValueError, TypeError, AttributeError, OSError, StopIteration) as exc:
        observed['function'] = 'CANNOT_CHECK_STUDY'
        observed['reason'] = type(exc).__name__ + ':' + str(exc)
        observed['parent'] = 'NOT_ESTABLISHED'
    observed['actual_backend_calls'] = {arm: {phase: {
        action: sum(e['arm'] == arm and e['phase'] == phase and e['action'] == action
                    and (action not in ('synthesize', 'verify') or e.get('result', {}).get('native_invoked') is True)
                    for e in observed['invocations']) if any(r['arm'] == arm and r['phase'] == phase for r in observed['resources']) else None for action in ('synthesize', 'verify', 'application', 'syntax')}
        for phase in ('acquire', 'warm', 'restart', 'history', 'withdraw', 'restore')} for arm in ('native', 'ocm')}
    for data in observed['arms'].values():
        data['assigned'] = {'acquisitions': 2, 'math': 36, 'authorized_values': 34, 'policy_refusals': 2, 'syntax': 5}
        data['math_unchecked'] = 36 - len(data['math']); data['syntax_unchecked'] = 5 - len(data['syntax'])
    return observed


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(); parser.add_argument('root'); parser.add_argument('--output', required=True)
    args = parser.parse_args(); result = grade_capture(args.root)
    with Path(args.output).open('x') as out: json.dump(result, out, indent=2, sort_keys=True); out.write('\n')
    raise SystemExit(0 if result['function'] == 'EXECUTABLE_REUSE_DEVELOPMENT_SUPPORTED' else 2)
