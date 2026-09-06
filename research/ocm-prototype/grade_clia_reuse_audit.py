"""External lifecycle checks over frozen data; no runtime, solver or donor imports."""
import hashlib
import json
from grade_clia_reuse import support_state

PHASES = ('acquire', 'warm', 'restart', 'history', 'withdraw', 'restore')
ORDERS = (('native', 'ocm'), ('native', 'ocm'), ('ocm', 'native'),
          ('native', 'ocm'), ('ocm', 'native'), ('native', 'ocm'))
TASKS = {'max3': 'jmbl_fg_max3', 'guard2': 'jmbl_fg_mpg_guard2'}
COUNTS = {'acquire': 2, 'warm': 13, 'restart': 13, 'history': 5, 'withdraw': 5, 'restore': 5}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def need(value, reason):
    if not value: raise ValueError(reason)


def validate_f1(f1):
    need(set(f1['arms']) == {'native', 'ocm'}, 'F1_ARMS')
    for arm, bindings in f1['arms'].items():
        need(set(bindings['programs']) == set(TASKS), 'F1_PROGRAMS')
        for alias, b in bindings['programs'].items():
            d = b['descriptor']; support = b['support']
            need(b['task_id'] == TASKS[alias] == d['task']['task_id'], 'F1_TASK')
            need(b['task_sha256'] == d['task']['task_sha256'], 'F1_TASK_HASH')
            need(b['descriptor_id'] == d['id'] == digest({k: v for k, v in d.items() if k != 'id'}), 'F1_DESCRIPTOR')
            need(b['program_sha256'] == d['program_sha256'] == digest({'task_sha256': b['task_sha256'], 'candidate': d['candidate']}), 'F1_PROGRAM_HASH')
            need(b['checker_identity'] == digest(d['checker_prior']), 'F1_CHECKER')
            need(support == d['support'] and support_state(support, []) == 'LIVE', 'F1_SUPPORT')
            certificate = d['universal_certificate']
            need(all(certificate[k] == 'PASS' for k in ('status', 'grammar', 'semantic'))
                 and certificate['task_sha256'] == b['task_sha256'], 'F1_UNIVERSAL_CHECK')
            ids = {e for terms in support.values() for term in terms for e in term}
            need(b['registration'] and set(b['registration']) <= ids, 'F1_REGISTRATION')
            need(b['history_ids'] and set(b['history_ids']).isdisjoint(ids), 'F1_HISTORY_SUPPORT_OVERLAP')
            need(set(b['history_ids']) == set(d['history_only']) == {h['id'] for h in b['history_records']}, 'F1_HISTORY')
        need(bindings['model_sha256'] == f1['arms']['native']['model_sha256'], 'F1_MODEL_PARITY')
        maximum, guard = [bindings['programs'][a] for a in TASKS]
        need(support_state(maximum['support'], maximum['registration']) == 'DEAD'
             and support_state(guard['support'], maximum['registration']) == 'LIVE', 'REGISTRATION_GRANULARITY')
    for alias in TASKS:
        a, b = [f1['arms'][arm]['programs'][alias] for arm in ('native', 'ocm')]
        need(all(a[k] == b[k] for k in ('program_sha256', 'task_sha256', 'checker_identity')), 'CANNOT_CHECK_IDENTICAL_DONOR_BINDING')


def revoked_for(bindings, phase, *, after=False):
    b = bindings['programs']['max3']; history = set(b['history_ids']); registration = set(b['registration'])
    state = {'acquire': set(), 'warm': set(), 'restart': set(), 'history': history,
             'withdraw': history | registration, 'restore': history}[phase]
    if after and phase == 'restart': state = history
    elif after and phase == 'history': state = history | registration
    elif after and phase == 'withdraw': state = history
    return state


def check_audit(audit, bindings, revoked, previous=None):
    need(set(audit['revoked']) == revoked, 'AUDIT_REVOKED')
    need(audit['model_liveness'] == 'LIVE', 'MODEL_RETENTION')
    expected = {b['descriptor_id']: b for b in bindings['programs'].values()}
    need(set(audit['programs']) == set(expected), 'AUDIT_PROGRAM_DENOMINATOR')
    for key, b in expected.items():
        p = audit['programs'][key]
        need(p['support'] == b['support'] and p['program_sha256'] == b['program_sha256'], 'AUDIT_PROGRAM_BINDING')
        need(p['history_only'] == b['history_ids'], 'AUDIT_HISTORY_BINDING')
        need(p['liveness'] == support_state(b['support'], sorted(revoked)), 'PROGRAM_AUTHORITY')
        for h in b['history_records']:
            need(audit['history_records'][h['id']] == {'sha256': h['file_sha256'], 'payload_sha256': h['payload_sha256']}, 'HISTORY_CHANGED')
        proof = audit['records'][b['proof_id']]
        need(proof['support'] == b['support'], 'ACQUISITION_SUPPORT')
    records = audit['records']
    for key, record in records.items():
        need(record['payload_sha256'] == digest(record['payload']), 'PAYLOAD_HASH')
        need(record['liveness'] == support_state(record['support'], sorted(revoked)), 'PRIOR_OUTPUT_AUTHORITY')
    for key, old in (previous or {}).items():
        need(key in records and all(records[key][k] == old[k] for k in ('payload_sha256', 'payload', 'support')), 'IMMUTABLE_PRIOR_CHANGED')
    return records


def check_events(worker, rows, phase):
    events = worker['invocations']; cursor = 0
    for index, e in enumerate(events):
        need(e['action'] in ('synthesize', 'verify', 'application', 'syntax'), 'UNKNOWN_INVOCATION')
        need(e['index'] == index and 'finished_monotonic' in e and 'error' not in e and 'result' in e, 'INCOMPLETE_INVOCATION')
        need(e['finished_monotonic'] >= e['started_monotonic'], 'INVOCATION_CLOCK')
        if e['action'] in ('synthesize', 'verify') and e['result'].get('native_invoked'):
            need(type(e['result']['metrics']['worker_pid']) is int and e['result']['metrics']['worker_pid'] > 0, 'NATIVE_PID')
            need(e['result'].get('solver', '').startswith('cvc5' if e['action'] == 'synthesize' else 'Z3'), 'NATIVE_SOLVER_ID')
    for row in rows:
        start, end = row['event_range']
        need(type(start) is int and type(end) is int and start == cursor and start <= end <= len(events), 'EVENT_RANGE')
        current = events[start:end]; cursor = end
        if phase == 'acquire':
            synth = [e for e in current if e['action'] == 'synthesize']
            need(len(synth) == 1 and synth[0]['result'].get('native_invoked') is True, 'EXACT_ONE_ACQUISITION')
            need(any(e['action'] == 'verify' and e['result'].get('native_invoked') is True
                     and e['result'].get('status') == 'PASS' for e in current), 'UNIVERSAL_CHECK_NOT_OBSERVED')
            continue
        need(row['invocation_events'] == current, 'EVENT_SLICE')
        delta = {k: sum(e['action'] == k for e in current) for k in ('application', 'syntax', 'verify')}
        delta.update(synthesize=sum(e['action'] == 'synthesize' and e['result'].get('native_invoked') is True for e in current),
                     synthesis_requests=sum(e['action'] == 'synthesize' for e in current))
        need(row['invocation_delta'] == delta and all(type(v) is int for v in row['invocation_delta'].values()), 'INVOCATION_DELTA')
        need(delta['synthesis_requests'] == 0, 'SYNTHESIS_STILL_EXECUTED')
        for e in current:
            if e['action'] == 'application': need(e['payload_sha256'] == digest(row['request']), 'APPLICATION_EVENT_BINDING')
            elif e['action'] == 'syntax':
                expected = {'tokens': row['request']['tokens'], 'model_sha256': worker['bindings']['model_sha256']}
                need(e['payload_sha256'] == digest(expected), 'SYNTAX_EVENT_BINDING')
    need(cursor == len(events), 'UNASSIGNED_INVOCATIONS')


def stage_audits(worker, bindings, phase, previous):
    entry, before, after = worker['entry_audit'], worker['exit_query_audit'], worker['final_audit']
    revoked = revoked_for(bindings, phase)
    if phase != 'acquire':
        check_audit(entry, bindings, revoked, previous)
        need(all(p['host_bound'] is False for p in entry['programs'].values()), 'FRESH_HOST_REBIND_REQUIRED')
        need(len(worker['binds']) == 2 and {b['alias'] for b in worker['binds']} == set(TASKS), 'BIND_DENOMINATOR')
        for bind in worker['binds']:
            b = bindings['programs'][bind['alias']]
            if support_state(b['support'], sorted(revoked)) == 'LIVE':
                need(bind.get('program_id') == b['descriptor_id'] and bind.get('status') != 'BIND_REFUSED', 'LIVE_BIND_FAILED')
            else: need(bind.get('status') == 'BIND_REFUSED', 'DEAD_BIND_ACCEPTED')
    else: need(not entry['programs'] and not entry['records'] and not entry['revoked'], 'FRESH_ACQUISITION')
    records = check_audit(before, bindings, revoked, previous)
    change = worker['end_revision']; target = bindings['programs']['max3']
    action, ids = {'restart': ('revoke', target['history_ids']), 'history': ('revoke', target['registration']),
                   'withdraw': ('reinstate', target['registration'])}.get(phase, ('none', []))
    need(change['action'] == action and change['ids'] == ids and change['before'] == before and change['after'] == after, 'REVISION_BINDING')
    return check_audit(after, bindings, revoked_for(bindings, phase, after=True), records)


def selected_record(row, audit):
    """Bind selected output to an actually persisted record, not its mere nonempty ID."""
    result = row['result']; request = row['request']; answer = result.get('answer')
    if row['arm'] == 'ocm':
        record = audit['records'][result['admitted_id']]
        need(record['payload'].get('request', record['payload'].get('query')) == request
             and record['payload']['output'] == answer, 'SELECTED_OCM_RECORD')
    elif request['kind'] == 'clia_apply':
        key = 'library/answer-' + result['record_id'] + '.json'; record = audit['records'][key]
        need(digest(record['payload']) == result['record_id'] and record['payload']['request'] == request
             and record['payload']['answer'] == answer, 'SELECTED_NATIVE_RECORD')
    else:
        matches = [r for k, r in audit['records'].items() if k.startswith('syntax/')
                   and r['payload']['request'] == request and r['payload']['result'].get('answer') == answer]
        need(len(matches) == 1, 'SELECTED_NATIVE_SYNTAX_RECORD'); record = matches[0]
    need(record['liveness'] == 'LIVE', 'SELECTED_DEAD_RECORD')
    return record


def grade_rows(worker, rows, bindings):
    from grade_clia_reuse import grade_math
    from syntax_contract import validate
    results = []; syntax = []; phase = worker['phase']; revoked = revoked_for(bindings, phase)
    catalogue = {'syntax:udpipe1', 'procedure:cvc5'} | {'apply:' + b['descriptor_id'] for b in bindings['programs'].values()}
    for row in rows:
        request = row['request']; result = row['result']
        need(len(result.get('catalogue', [])) == 4 and set(result['catalogue']) == catalogue, 'CATALOGUE_AVAILABILITY')
        if request['kind'] == 'clia_apply':
            b = next(b for b in bindings['programs'].values() if b['descriptor_id'] == request['program_id'])
            live = support_state(b['support'], sorted(revoked))
            need(row['authority'] == {'liveness': live, 'revoked': sorted(revoked)}, 'ROW_AUDIT_AUTHORITY')
            authorized = not (phase == 'withdraw' and b['task_id'] == TASKS['max3'])
            need(live == ('LIVE' if authorized else 'DEAD'), 'PROTOCOL_AUTHORITY')
            grade = grade_math(row, b, authorized=authorized)
            if grade['status'] == 'CORRECT_VALUE':
                need(row['invocation_delta']['application'] >= 1, 'APPLICATION_NOT_OBSERVED')
                record = selected_record(row, worker['exit_query_audit'])
                need(record['support'] == b['support'], 'SELECTED_SUPPORT_BINDING')
            elif grade['status'] == 'EXPECTED_POLICY_REFUSAL':
                need(not row['invocation_events'], 'REFUSAL_EXECUTED_BACKEND')
            results.append({'id': row['id'], 'phase': phase, 'authorized': authorized,
                            'actor_status': result.get('status'),
                            'cannot_check': str(result.get('status', '')).startswith('CANNOT_CHECK') or any(c.get('status') == 'CANNOT_CHECK' for c in result.get('checks', [])),
                            'unauthorized_selected': not authorized and result.get('answer') is not None and bool(result.get('admitted_id') or result.get('record_id')), **grade})
        else:
            need(request['kind'] == 'syntax' and row['authority'] is None, 'SYNTAX_REQUEST')
            accepted = result.get('status') == ('ADMITTED' if row['arm'] == 'ocm' else 'ACCEPTED_PARENT')
            answer = result.get('answer') or {}
            good = accepted and answer.get('status') == 'PREDICTED' and answer.get('model_sha256') == bindings['model_sha256']
            good = good and validate(answer.get('words'), request['tokens']) is None
            if good:
                selected_record(row, worker['exit_query_audit'])
                need(row['invocation_delta']['syntax'] >= 1 and row['invocation_delta']['application'] == 0, 'SYNTAX_NOT_OBSERVED')
                if row['arm'] == 'ocm': need(result.get('claim') == 'MODEL_SUPPORTED_SYNTAX_OBSERVATION', 'SYNTAX_AUTHORITY')
            syntax.append({'id': row['id'], 'status': 'VALID_STRUCTURE' if good else 'CANNOT_CHECK_SYNTAX',
                           'words': answer.get('words') if good else None})
    return results, syntax
