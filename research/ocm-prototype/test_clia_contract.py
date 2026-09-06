"""Public donor qualification and independent grammar-before-semantics gates."""
from importlib import import_module, util
import pytest

IDS = ('jmbl_fg_max3', 'jmbl_fg_max10', 'jmbl_fg_array_search_4',
       'jmbl_fg_array_search_10', 'jmbl_fg_mpg_guard2')
GOOD = '(define-fun mux_3 ((x Int) (y Int) (z Int)) Int (ite (>= x y) (ite (>= x z) x z) (ite (>= y z) y z)))'

def api():
    for name in ('clia_tasks', 'clia_solver', 'clia_checker'):
        assert util.find_spec(name) is not None, f'{name} implementation missing'
    return tuple(import_module(n) for n in ('clia_tasks', 'clia_solver', 'clia_checker'))

def candidate(task, text=GOOD):
    return {'status': 'SOLUTION', 'candidate': text, 'task_sha256': task['task_sha256'],
            'grammar_id': task['grammar']['id']}

@pytest.mark.parametrize('task_id', IDS)
def test_actual_public_solver_outputs_pass_independent_check(task_id):
    tasks, solver, checker = api()
    task = tasks.load_task(task_id)
    assert task['original_sygus'] and task['sygus'] and task['source']['sha256']
    result = solver.propose(task)
    assert result['status'] == 'SOLUTION', result
    checked = checker.check(task, result)
    assert checked['grammar'] == 'PASS' and checked['semantic'] == 'PASS', checked
    assert checked['solver_result'] == 'unsat'
    assert checked.get('reason') in (None, ''), checked
    assert result['metrics']['worker_pid'] != checked['metrics']['worker_pid']

@pytest.mark.parametrize('text', [
    GOOD.replace('mux_3', 'other'),
    GOOD + '\n' + GOOD,
    GOOD.replace('((x Int) (y Int) (z Int))', '((x Int) (y Int))'),
    GOOD.replace('(x Int)', '(x Bool)'),
    GOOD.replace(' Int (ite', ' Bool (ite'),
    GOOD.replace('(>= x y)', '(>= x missing)'),
    GOOD.replace('(>= x y)', '(>= (* x y) z)'),
    GOOD.replace('(>= x y)', '(>= (div x 2) z)'),
    GOOD.replace('(>= x y)', '(>= (sin x) z)'),
    GOOD + '\n(check-sat)',
    GOOD.replace('(>= x y)', '(>= true 0)'),
    GOOD.replace('(>= x y)', '(= (let ((v x) (v y)) v) z)'),
])
def test_invalid_programs_fail_before_native_checker(text):
    tasks, _, checker = api(); task = tasks.load_task(IDS[0])
    result = checker.check(task, candidate(task, text))
    assert result['grammar'] == 'FAIL' and result['semantic'] == 'NOT_RUN', result
    assert result['native_checker_invoked'] is False


def test_wrong_allowed_program_is_counterexample_not_grammar_error():
    tasks, _, checker = api(); task = tasks.load_task(IDS[0])
    result = checker.check(task, candidate(task, '(define-fun mux_3 ((x Int) (y Int) (z Int)) Int 0)'))
    assert result['grammar'] == 'PASS' and result['semantic'] == 'FAIL'
    assert result['solver_result'] == 'sat' and result['counterexample']


def test_total_let_and_linear_constant_multiplication_are_accepted():
    tasks, _, checker = api(); task = tasks.load_task(IDS[0])
    text = GOOD.replace('(>= x y)', '(let ((d (+ x (* (- 1) y)))) (>= d 0))')
    result = checker.check(task, candidate(task, text))
    assert result['grammar'] == 'PASS' and result['semantic'] == 'PASS', result


def test_task_and_proposal_binding_cannot_change_contract():
    tasks, solver, checker = api(); task = tasks.load_task(IDS[0])
    altered = {**task, 'sygus': task['sygus'] + '\n(check-sat)'}
    assert solver.propose(altered)['status'] == 'CANNOT_CHECK'
    assert checker.check(altered, candidate(task))['grammar'] == 'FAIL'
    wrong = {**candidate(task), 'task_sha256': '0' * 64}
    assert checker.check(task, wrong)['grammar'] == 'FAIL'


def test_deadline_and_unavailable_native_checker_are_not_false_proofs(monkeypatch):
    tasks, solver, checker = api(); task = tasks.load_task(IDS[0])
    assert solver.propose(task, deadline_s=0)['status'] == 'CANNOT_CHECK'
    result = checker.check(task, candidate(task), deadline_s=0)
    assert result['grammar'] == 'PASS' and result['semantic'] == 'CANNOT_CHECK'
    process = import_module('clia_process'); monkeypatch.setattr(process, 'PYTHON', '/definitely/missing/python')
    result = checker.check(task, candidate(task))
    assert result['grammar'] == 'PASS' and result['semantic'] == 'CANNOT_CHECK'


def test_non_solution_and_oversized_candidate_are_not_admitted():
    tasks, _, checker = api(); task = tasks.load_task(IDS[0])
    result = checker.check(task, {**candidate(task), 'status': 'CANNOT_CHECK'})
    assert result['semantic'] == 'NOT_RUN' and result['status'] == 'CANNOT_CHECK'
    result = checker.check(task, candidate(task, GOOD + ' ' * 100000))
    assert result['grammar'] == 'FAIL' and not result['native_checker_invoked']

@pytest.mark.parametrize('text', ['(', '"define-fun"', '(define-fun mux_3 ((x Int) (y Int) (z Int)) Int "0")'])
def test_malformed_data_is_a_receipt_not_an_exception(text):
    tasks, _, checker = api(); task = tasks.load_task(IDS[0])
    result = checker.check(task, candidate(task, text))
    assert result['grammar'] == 'FAIL' and result['semantic'] == 'NOT_RUN'


def test_missing_fixture_custody_is_cannot_check(monkeypatch, tmp_path):
    tasks, solver, checker = api(); task = tasks.load_task(IDS[0])
    monkeypatch.setattr(tasks, 'FIXTURES', tmp_path)
    assert solver.propose(task)['status'] == 'CANNOT_CHECK'
    assert checker.check(task, candidate(task))['status'] == 'CANNOT_CHECK'


def test_actual_external_deadline_stops_native_child():
    tasks, solver, checker = api(); task = tasks.load_task(IDS[0])
    result = checker.check(task, candidate(task), deadline_s=0.000001)
    assert result['grammar'] == 'PASS' and result['semantic'] == 'CANNOT_CHECK'
    assert result['reason'] == 'EXTERNAL_TIMEOUT' and result['native_checker_invoked']
