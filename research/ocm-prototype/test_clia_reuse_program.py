"""Separate unit examples; these tuples are exposed controls, not the future reuse panel."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
from clia_tasks import load_task
import clia_reuse_descriptor as D
from clia_reuse_apply import CompiledProgram, check_value
from clia_reuse_native import NativeLibrary

UNIT_PROGRAMS = {
    'jmbl_fg_max3': '(define-fun mux_3 ((x Int) (y Int) (z Int)) Int (ite (>= x y) (ite (>= x z) x z) (ite (>= y z) y z)))',
    'jmbl_fg_mpg_guard2': '(define-fun eq_1 ((x Int) (y Int) (z Int)) Int (ite (>= (+ x y z) 1) (+ x y) (- x y)))',
}
PROFILE = {'lower': [['query-unit', 'checker-unit']], 'upper': [['query-unit', 'checker-unit']]}


def descriptor(task_id='jmbl_fg_max3'):
    task = load_task(task_id)
    proposal = dict(status='SOLUTION', candidate=UNIT_PROGRAMS[task_id],
                    task_sha256=task['task_sha256'], grammar_id=task['grammar']['id'])
    return D.create(task, proposal, PROFILE, history=['search-unit'])


def request(desc, arguments):
    return {'kind': 'clia_apply', 'program_id': desc['id'], 'arguments': arguments}


def test_actual_z3_application_and_wrong_value_control():
    desc = descriptor(); program = CompiledProgram(desc)
    query = request(desc, [41, -7, 12])
    value = program.apply(query)
    assert value['value'] == 41
    assert check_value(desc, query, value)['status'] == 'PASS'
    wrong = {**value, 'value': 12}
    assert check_value(desc, query, wrong)['status'] == 'FAIL'
    assert check_value(desc, request(desc, [0, 0, 0]), value)['status'] == 'FAIL'


@pytest.mark.parametrize('args', [[1, 2], [True, 2, 3], [1.0, 2, 3], ['1', 2, 3], [1 << 4097, 2, 3]])
def test_bad_tuple_is_refused(args):
    desc = descriptor()
    with pytest.raises(ValueError): CompiledProgram(desc).apply(request(desc, args))


def test_descriptor_hash_grammar_and_proof_custody_refuse():
    desc = descriptor()
    for key, value in [('candidate', UNIT_PROGRAMS['jmbl_fg_max3'] + ' '), ('id', '0' * 64), ('checker_prior', {})]:
        changed = copy.deepcopy(desc); changed[key] = value
        with pytest.raises(ValueError): D.validate(changed)
    task = load_task('jmbl_fg_max3')
    for candidate in ['(define-fun mux_3 ((x Int) (y Int) (z Int)) Int (* x y))',
                      '(define-fun mux_3 ((x Int) (y Int) (z Int)) Int x)']:
        with pytest.raises(ValueError):
            D.create(task, dict(status='SOLUTION', candidate=candidate, task_sha256=task['task_sha256'], grammar_id=task['grammar']['id']), PROFILE)


def test_native_restart_support_and_history_are_separate(tmp_path):
    library = NativeLibrary(tmp_path)
    desc = descriptor(); library.install(desc); library.bind(desc['id'])
    assert library.apply(request(desc, [41, -7, 12]))['status'] == 'ACCEPTED_PARENT'
    restarted = NativeLibrary(tmp_path)
    assert restarted.apply(request(desc, [41, -7, 12]))['status'] == 'CANNOT_CHECK_UNBOUND'
    restarted.bind(desc['id']); restarted.revoke(['search-unit'])
    assert restarted.apply(request(desc, [41, -7, 12]))['status'] == 'ACCEPTED_PARENT'
    restarted.revoke(['query-unit'])
    assert restarted.apply(request(desc, [41, -7, 12]))['status'] == 'REFUSED_DEAD_SUPPORT'
    restarted.reinstate(['query-unit'])
    assert restarted.apply(request(desc, [41, -7, 12]))['status'] == 'ACCEPTED_PARENT'
    assert restarted.stats['synthesis_calls_in_library'] == 0


def test_native_real_new_process_rebind_and_guard_unit(tmp_path):
    library = NativeLibrary(tmp_path); desc = descriptor('jmbl_fg_mpg_guard2'); library.install(desc)
    script = '''import json,sys
from clia_reuse_native import NativeLibrary
lib=NativeLibrary(sys.argv[1]); key=sys.argv[2]; lib.bind(key)
print(json.dumps(lib.apply({'kind':'clia_apply','program_id':key,'arguments':[17,-9,0]})))'''
    cp = subprocess.run([sys.executable, '-c', script, str(tmp_path), desc['id']], cwd=Path(__file__).parent,
                        text=True, capture_output=True, check=True)
    assert json.loads(cp.stdout)['answer']['value'] == 8


def test_native_tampered_disk_and_alternate_unknown_support(tmp_path):
    library = NativeLibrary(tmp_path); desc = descriptor(); library.install(desc)
    path = library.path(desc['id']); data = json.loads(path.read_text()); data['candidate'] += ' '
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError): library.bind(desc['id'])
    assert D.liveness({'lower': [['a'], ['b']], 'upper': [['a'], ['b']]}, {'a'}) == 'LIVE'
    assert D.liveness({'lower': [['a'], ['b']], 'upper': [['a'], ['b']]}, {'a', 'b'}) == 'DEAD'
    assert D.liveness({'lower': [], 'upper': [['a']]}, set()) == 'UNKNOWN'


def test_bool_alias_in_returned_tuple_and_history_overlap_refuse():
    desc = descriptor(); q = request(desc, [0, 0, 0]); output = CompiledProgram(desc).apply(q)
    assert check_value(desc, q, {**output, 'arguments': [False, 0, 0]})['status'] == 'FAIL'
    task = load_task('jmbl_fg_max3')
    with pytest.raises(ValueError):
        D.create(task, D.proposal(desc), PROFILE, history=['query-unit'])


def test_forged_import_and_native_audit_do_not_restore_authority(tmp_path):
    desc = descriptor(); library = NativeLibrary(tmp_path); library.install(desc); library.bind(desc['id'])
    result = library.apply(request(desc, [41, -7, 12]))
    library.revoke(['query-unit'])
    audit = library.audit()
    assert audit['programs'][desc['id']]['liveness'] == 'DEAD'
    assert audit['answers'][result['record_id']]['liveness'] == 'DEAD'
    assert library.revoked == {'query-unit'}
    forged = copy.deepcopy(desc); forged['candidate'] = '(define-fun mux_3 ((x Int) (y Int) (z Int)) Int x)'
    forged['program_sha256'] = D.digest({'task_sha256': forged['task']['task_sha256'], 'candidate': forged['candidate']})
    forged['id'] = D.digest({k: v for k, v in forged.items() if k != 'id'})
    with pytest.raises(ValueError): library.install(forged)


def test_actual_archived_donor_programs_compile_without_application():
    root = Path(__file__).parent / 'results/g1-admission-support-20260906/revised'
    found = set()
    for path in sorted(root.glob('*-ocm.rows.jsonl')):
        for line in path.read_text().splitlines():
            row = json.loads(line); name = row['id'].removeprefix('clia:')
            if name not in UNIT_PROGRAMS: continue
            assert row['result']['status'] == 'ADMITTED'
            desc = D.create(load_task(name), row['result']['answer'], PROFILE)
            assert CompiledProgram(desc).descriptor['task']['task_id'] == name
            found.add(name)
    assert found == set(UNIT_PROGRAMS)


def test_guard_negative_unit_branch():
    desc = descriptor('jmbl_fg_mpg_guard2'); q = request(desc, [-17, 9, 0])
    result = CompiledProgram(desc).apply(q)
    assert result['value'] == -26 and check_value(desc, q, result)['status'] == 'PASS'


def test_lower_only_history_overlap_is_refused():
    d = descriptor(); task = d['task']
    support = {'lower': [['history']], 'upper': [[]]}
    assert D.liveness(support, set()) == 'LIVE'
    assert D.liveness(support, {'history'}) == 'UNKNOWN'
    with pytest.raises(ValueError): D.create(task, D.proposal(d), support, history=['history'])
    clean = D.create(task, D.proposal(d), support, history=['separate-history'])
    assert D.liveness(clean['support'], {'separate-history'}) == 'LIVE'
    changed = copy.deepcopy(clean); changed['history_only'] = ['history']
    changed['id'] = D.digest({k: v for k, v in changed.items() if k != 'id'})
    with pytest.raises(ValueError): D.validate(changed)
