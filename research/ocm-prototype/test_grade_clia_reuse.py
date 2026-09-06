"""External grading against real emitted unit records; never the prospective panel."""
import copy
import json
import os
from pathlib import Path

import pytest

import grade_clia_reuse as G


@pytest.fixture(scope='module')
def emitted(tmp_path_factory):
    from clia_reuse_native import NativeLibrary
    import clia_reuse_vessel as V
    from test_clia_reuse_vessel import fixture_state
    from test_clia_reuse_program import UNIT_PROGRAMS, PROFILE
    from clia_tasks import load_task
    base = tmp_path_factory.mktemp('actual-reuse-grade-unit')
    task = load_task('jmbl_fg_max3')
    native = NativeLibrary(base / 'native')
    candidate = dict(status='SOLUTION', candidate=UNIT_PROGRAMS[task['task_id']],
                     task_sha256=task['task_sha256'], grammar_id=task['grammar']['id'])
    key = native.acquire(task, candidate, PROFILE, history=['search-unit'])
    native.bind(key); nd = native.load(key)
    runtime, proofs, history, _ = fixture_state(base / 'ocm')
    od = V.adopt(runtime, proofs[task['task_id']][0], history=[history]); V.bind(runtime, od['id'])
    records = {}
    for arm, desc, registration in [('native', nd, ['query-unit']),
                                    ('ocm', od, [proofs[task['task_id']][1]])]:
        request = dict(kind='clia_apply', program_id=desc['id'], arguments=[41, -7, 12])
        result = native.apply(request) if arm == 'native' else V.query(runtime, request)
        binding = dict(descriptor_id=desc['id'], program_sha256=desc['program_sha256'],
                       task_id=task['task_id'], registration=registration, support=desc['support'])
        row = dict(id='UNIT_FIXTURE.' + arm, arm=arm, request=request, result=result,
                   authority=dict(liveness='LIVE', revoked=[]), invocation_delta=dict(synthesize=0, application=1))
        if arm == 'native':
            before = native.stats['applications']; native.revoke(registration)
            refused = native.apply(request); live = native.audit()['programs'][desc['id']]['liveness']
            delta = dict(synthesize=0, application=native.stats['applications'] - before)
        else:
            runtime.revoke(registration); runtime.persist(); refused = V.query(runtime, request)
            live = V.audit(runtime)['programs'][desc['id']]['liveness']
            delta = dict(synthesize=refused['counters']['synthesis_dispatches'], application=refused['counters']['application_calls'])
        policy = dict(id='UNIT_FIXTURE.' + arm + '.withdraw', arm=arm, request=request, result=refused,
                      authority=dict(liveness=live, revoked=registration), invocation_delta=delta)
        records[arm] = dict(row=row, binding=binding, policy_row=policy)
    directory = os.environ.get('OCM_REUSE_GRADE_FIXTURE_DIR')
    if directory:
        out = Path(directory); out.mkdir(parents=True, exist_ok=False)
        for arm, record in records.items():
            (out / (arm + '.json')).write_text(json.dumps(record, sort_keys=True, indent=2) + '\n')
    return records


def test_actual_native_and_ocm_selected_outputs_no_alarm(emitted):
    for record in emitted.values():
        assert G.grade_math(record['row'], record['binding'], authorized=True)['status'] == 'CORRECT_VALUE'
        assert G.grade_math(record['policy_row'], record['binding'], authorized=False)['status'] == 'EXPECTED_POLICY_REFUSAL'


@pytest.mark.parametrize('mutation,expected', [('value', 'WRONG_VALUE'), ('tuple', 'WRONG_BINDING'),
    ('program', 'WRONG_BINDING'), ('not_selected', 'NO_SELECTED_VALUE'), ('check', 'CHECK_NOT_PASSED')])
def test_altered_actual_records_are_not_accepted(emitted, mutation, expected):
    for arm, record in emitted.items():
        row = copy.deepcopy(record['row']); result = row['result']
        if mutation == 'value': result['answer']['value'] = 40
        elif mutation == 'tuple': result['answer']['arguments'] = [41, -7, 11]
        elif mutation == 'program': result['answer']['program_sha256'] = '0' * 64
        elif mutation == 'not_selected': result['proposal_diagnostic'] = result.pop('answer')
        elif arm == 'native': result['check']['status'] = 'CANNOT_CHECK'
        else:
            for check in result['checks']:
                if check.get('phase') == 'admission': check['status'] = 'CANNOT_CHECK'
        assert G.grade_math(row, record['binding'], authorized=True)['status'] == expected


@pytest.mark.parametrize('value', [True, 41.0, '41', None])
def test_real_record_noninteger_values_are_rejected(emitted, value):
    for record in emitted.values():
        row = copy.deepcopy(record['row']); row['result']['answer']['value'] = value
        assert G.grade_math(row, record['binding'], authorized=True)['status'] != 'CORRECT_VALUE'


def test_policy_refusal_needs_support_and_cannot_be_an_error(emitted):
    for arm, record in emitted.items():
        row = copy.deepcopy(record['policy_row']); binding = record['binding']
        assert G.grade_math(row, binding, authorized=False)['status'] == 'EXPECTED_POLICY_REFUSAL'
        for bad in [dict(status='CANNOT_CHECK_APPLICATION', answer=None),
                    dict(status='NOT_ADMITTED', answer=None, reason='HOST_CALLABLE_UNBOUND'),
                    dict(status='NOT_ADMITTED', answer=None, admitted_id='stale')]:
            row['result'] = bad
            assert G.grade_math(row, binding, authorized=False)['status'] == 'REFUSAL_NOT_ESTABLISHED'
        row['result'] = copy.deepcopy(record['policy_row']['result'])
        for key in ['synthesize', 'application']:
            row['invocation_delta'][key] = 1
            assert G.grade_math(row, binding, authorized=False)['status'] == 'REFUSAL_NOT_ESTABLISHED'
            row['invocation_delta'][key] = 0
        row['authority']['revoked'] = []
        assert G.grade_math(row, binding, authorized=False)['status'] == 'REFUSAL_NOT_ESTABLISHED'


def test_oracle_is_exact_and_policy_does_not_collapse_unknown():
    assert G.oracle('jmbl_fg_max3', [41, -7, 12]) == 41
    assert G.oracle('jmbl_fg_mpg_guard2', [17, -9, -7]) == 8
    assert G.oracle('jmbl_fg_mpg_guard2', [17, -9, -8]) == 26
    for args in [[True, 2, 3], [1, 2], [1.0, 2, 3]]:
        with pytest.raises(ValueError): G.oracle('jmbl_fg_max3', args)
    profile = dict(lower=[['a']], upper=[[]])
    assert G.support_state(profile, ['a']) == 'UNKNOWN'
    assert G.support_state(dict(lower=[['a'], ['b']], upper=[['a'], ['b']]), ['a']) == 'LIVE'


def test_policy_needs_real_both_bound_support_and_ocm_trace(emitted):
    for arm, record in emitted.items():
        row = copy.deepcopy(record['policy_row']); binding = copy.deepcopy(record['binding'])
        binding.pop('support')
        assert G.grade_math(row, binding, authorized=False)['status'] == 'REFUSAL_NOT_ESTABLISHED'
        binding['support'] = dict(lower=[binding['registration']], upper=[[]])
        assert G.grade_math(row, binding, authorized=False)['status'] == 'REFUSAL_NOT_ESTABLISHED'
        binding['support'] = dict(lower=[], upper='malformed')
        assert G.grade_math(row, binding, authorized=False)['status'] == 'REFUSAL_NOT_ESTABLISHED'
    record = emitted['ocm']; row = copy.deepcopy(record['policy_row'])
    row['result'].pop('trace')
    assert G.grade_math(row, record['binding'], authorized=False)['status'] == 'REFUSAL_NOT_ESTABLISHED'
    row = copy.deepcopy(record['policy_row'])
    for stage in row['result']['trace']['stages']:
        if stage['stage'] == 'EXTRACTION': stage['payload']['warranted_atoms'].append('clia:executable:' + record['binding']['descriptor_id'])
    assert G.grade_math(row, record['binding'], authorized=False)['status'] == 'REFUSAL_NOT_ESTABLISHED'


def test_arm_status_cannot_be_swapped(emitted):
    for arm, record in emitted.items():
        row = copy.deepcopy(record['row']); row['arm'] = 'native' if arm == 'ocm' else 'ocm'
        assert G.grade_math(row, record['binding'], authorized=True)['status'] != 'CORRECT_VALUE'
        row = copy.deepcopy(record['policy_row']); row['arm'] = 'native' if arm == 'ocm' else 'ocm'
        assert G.grade_math(row, record['binding'], authorized=False)['status'] != 'EXPECTED_POLICY_REFUSAL'
