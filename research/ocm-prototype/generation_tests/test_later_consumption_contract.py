"""Protocol controls only: all native donors are replaced before assessment."""
import copy
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import clia_tasks as T
from clia_grammar import forms, dump

OLD = {
    'jmbl_fg_max3': 'c781247fce36a1f3c9548e53cb916e4e02b06380b3d9b7403da12f964d58e6dc',
    'jmbl_fg_max10': '51a1a23475149970f505573212990e0f5ec8e57c3bbd2fe287aff021601b0a00',
    'jmbl_fg_array_search_4': 'a749d493821bdb783128333026ce4962707472a2d8c8b357cdcffecaf4ad5b14',
    'jmbl_fg_array_search_10': '5d470549229879f6b90e941f165e8a7cfa7bcff7058eccac584bf830baee2476',
    'jmbl_fg_mpg_guard2': '1d6172d3cb9e848cc31a11eab9f18e1e3c59eaafd1bd2b93d893a78119a69a97',
}
PRIMITIVE = '(define-fun absdiff2 ((x Int) (y Int)) Int (ite (>= x y) (- x y) (- y x)))'
USED = '(define-fun absdiff2 ((x Int) (y Int)) Int (ite (fn_0 (- x y)) (- y x) (- x y)))'
HELPER = '(define-fun fn_0 ((h0 Int)) Bool (not (>= h0 1)))'


def api():
    assert importlib.util.find_spec('later_consumption_contract') is not None, 'prepared consumption contract is missing'
    import later_consumption_contract
    return later_consumption_contract


def test_exact_new_fixture_and_unchanged_historical_identities():
    try:
        task = T.load_task('public_absdiff2_v1')
    except ValueError:
        pytest.fail('registered source-bound task successor is missing')
    assert T.validate_task(task) == task
    assert {name: T.load_task(name)['task_sha256'] for name in OLD} == OLD
    assert task['source']['split'] == 'PUBLIC_DEVELOPMENT_ONLY'
    assert task['source']['origin'] == 'RESEARCHER_DESIGNED_EXPOSED_SPECIFICATION'
    assert list(T.signatures(task)) == ['absdiff2']
    damaged = copy.deepcopy(task)
    damaged['original_sygus'] = damaged['original_sygus'].replace('(>=', '(>')
    damaged['task_sha256'] = T.digest({k:v for k,v in damaged.items() if k != 'task_sha256'})
    with pytest.raises(ValueError, match='binding'):
        T.validate_task(damaged)
    with pytest.raises(ValueError):
        T.load_task('public_absdiff2_v2')


def test_exact_sealed_library_and_matched_full_grammar():
    a = api()
    library = a.load_library()
    assert library['fn_0'].body == '(not (>= #0 1))'
    requests = a.requests()
    assert list(requests) == ['C', 'E0', 'B']
    task = T.load_task('public_absdiff2_v1')
    assert requests['C'] == task['original_sygus']
    primitive, learned = forms(requests['E0']), forms(requests['B'])
    before = next(x for x in primitive if str(x[0]) == 'synth-fun')
    after = next(x for x in learned if str(x[0]) == 'synth-fun')
    assert before[:4] == after[:4]
    assert after[4][:-1] == before[4]
    assert after[5][0] == before[5][0]
    assert after[5][1][2][:-1] == before[5][1][2]
    assert after[5][2] == before[5][2]
    assert dump(after[5][-1]) == '(GEN_fn_0 Bool ((fn_0 OCM_I)))'
    assert [x for x in learned if str(x[0]) == 'constraint'] == [x for x in primitive if str(x[0]) == 'constraint']
    assert [dump(x) for x in learned if str(x[0]) == 'define-fun'] == [HELPER]


def test_returned_body_calls_are_distinct_from_declaration_and_similarity():
    a = api()
    assert a.prepare_return(PRIMITIVE, 'B')['observed_calls'] == []
    assert a.prepare_return(HELPER + PRIMITIVE, 'B')['observed_calls'] == []
    got = a.prepare_return(HELPER + USED, 'B')
    assert got['observed_calls'] == ['fn_0']
    assert 'fn_0' not in got['expanded_candidate']
    assert '(define-fun fn_0' in got['equivalence_smt2']
    assert '(assert (not (= (left x y) (right x y))))' in got['equivalence_smt2']
    # A declared unused let is not a dependency of the returned body.
    unused = PRIMITIVE.replace('(ite', '(let ((a (fn_0 x))) (ite') + ')'
    assert a.prepare_return(unused, 'B')['observed_calls'] == []


@pytest.mark.parametrize('candidate', [
    HELPER.replace('1)', '2)') + USED,
    HELPER + HELPER + USED,
    HELPER,
    USED.replace('fn_0', 'fn_1'),
    USED.replace('(fn_0 (- x y))', '(fn_0 true)'),
    USED.replace('(fn_0 (- x y))', '(fn_0 x y)'),
    USED.replace('(fn_0 (- x y))', '(GEN_fn_0 (- x y))'),
    USED + '(assert false)',
    PRIMITIVE.replace('(ite', '(! (ite') + ' :gterm GEN_fn_0)',
    PRIMITIVE.replace('(ite', '(let ((x 1)) (ite') + ')',
])
def test_unsupported_or_unbound_return_never_establishes_consumption(candidate):
    with pytest.raises((ValueError, TypeError)):
        api().prepare_return(candidate, 'B')


def test_primitive_routes_cannot_import_helper_power():
    for route in ('C', 'E0'):
        with pytest.raises(ValueError):
            api().prepare_return(USED, route)
        with pytest.raises(ValueError):
            api().prepare_return(HELPER + PRIMITIVE, route)


def test_library_hash_drift_is_refused(tmp_path, monkeypatch):
    a = api()
    bad = tmp_path/'adapter-return.json'
    bad.write_bytes(a.ADAPTER.read_bytes().replace(b'(not (>= #0 1))', b'(not (>= #0 2))'))
    monkeypatch.setattr(a, 'ADAPTER', bad)
    with pytest.raises(ValueError, match='binding'):
        a.load_library()


def test_exponential_let_dependency_is_bounded_before_native(monkeypatch):
    a = api()
    original = a.G.expand
    count = 0
    def counted(*args, **kwargs):
        nonlocal count
        count += 1
        assert count <= 20000, "expanded DAG traversal exceeded host work bound"
        return original(*args, **kwargs)
    monkeypatch.setattr(a.G, "expand", counted)
    body = '(ite (fn_0 x) 0 a15)'
    for index in reversed(range(16)):
        prior = 'x' if index == 0 else 'a'+str(index-1)
        body = '(let ((a'+str(index)+' (+ '+prior+' '+prior+'))) '+body+')'
    candidate = '(define-fun absdiff2 ((x Int) (y Int)) Int '+body+')'
    with pytest.raises(ValueError, match='bound'):
        api().prepare_return(candidate,'B')


def test_let_cannot_shadow_the_acquired_global_helper():
    candidate = USED.replace('(ite', '(let ((fn_0 1)) (ite') + ')'
    with pytest.raises(ValueError, match='shadow'):
        api().prepare_return(candidate, 'B')
