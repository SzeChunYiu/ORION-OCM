"""Manual engineering fixtures only; no discovery or cvc5 synthesis is executed."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from sexpdata import Symbol as S
import generation_clia as G
import generation_stitch as D
from clia_tasks import load_task, signatures

SIG = {'f': {'parameters': [[S('x'), S('Int')], [S('y'), S('Int')]], 'sort': 'Int'}}


def fun(body):
    return '(define-fun f ((x Int) (y Int)) Int '+body+')'


@pytest.mark.parametrize('body', [
    '(+ x y)', '-2', '(- -2)', '(* (+ 2 3) x)',
    '(let ((a (+ x 1)) (b (- y 2))) (let ((c (+ a b))) (- c)))',
    '(ite (and (< x y) (not (= x 0))) x y)',
])
def test_roundtrip(body):
    before = fun(body)
    encoded = G.encode(before, SIG)[0]['program']
    after = G.decode(encoded, 'f', SIG)['candidate']
    assert G.one(after)[4] == G.one(G.dump(G.unlet(G.one(before)[4])))


@pytest.mark.parametrize('body', [
    '(let ((x 2)) x)', '(let ((a 1) (a 2)) a)',
    '(let ((a 1)) (let ((a 2)) a))', '(let ((a 1) (b a)) b)',
    '(+ x z)', '(+ x true)', '(* x y)', '(lambda x x)', '(+ x)',
])
def test_host_refusals(body):
    with pytest.raises(ValueError):
        G.encode(fun(body), SIG)


def test_manual_typed_macros_expand_without_capture():
    library = G.admit_macros([
        {'name': 'fn_0', 'body': '(+ #0 #1)', 'arity': 2},
        {'name': 'fn_1', 'body': '(ite #0 (fn_0 #1 2) (- #1))', 'arity': 2},
    ])
    assert library['fn_1'].sorts == ('Bool', 'Int')
    assert library['fn_0'].sorts == ('Int', 'Int')
    got = G.decode('(lam (lam (fn_1 (< $1 $0) $1)))', 'f', SIG, library)
    assert got['candidate'] == fun('(ite (< x y) (+ x 2) (- x))')
    assert got['macro_calls_in_input'] == ['fn_1']
    assert library['fn_1'].body == '(ite #0 (+ #1 2) (- #1))'


@pytest.mark.parametrize('body,arity', [
    ('(* #0 #1)', 2), ('(+ #0 (ite #0 1 0))', 1),
    ('(+ #0 #2)', 2), ('(+ #0 1)', 2), ('(fn_0 #0)', 1),
    ('(fn_1 #0)', 1), ('(lam (+ $0 #0))', 1), ('(+ $0 #0)', 1),
    ('(mod #0 2)', 1), ('#0', 1), ('(+ #0)', 1), ('(+ #0 2.0)', 1),
])
def test_macro_refusals(body, arity):
    with pytest.raises(ValueError):
        G.admit_macros([{'name': 'fn_0', 'body': body, 'arity': arity}])


@pytest.mark.parametrize('program', [
    '(lam (fn_0 $0 1))', '(lam (lam (lam $0)))',
    '(lam (lam (fn_0 $2 1)))', '(lam (lam (fn_0 $0)))',
    '(lam (lam (fn_0 true 1)))', '(lam (lam (#0 $0)))',
])
def test_decode_refusals(program):
    library = G.admit_macros([{'name': 'fn_0', 'body': '(+ #0 #1)', 'arity': 2}])
    with pytest.raises(ValueError):
        G.decode(program, 'f', SIG, library)


def test_quoted_outer_binder_is_not_a_symbol():
    assert G.decode('(lam (lam $0))', 'f', SIG)['candidate'] == fun('y')
    with pytest.raises(ValueError, match='outer binders'):
        G.decode('("lam" (lam $0))', 'f', SIG)


def test_fixed_z3_equivalence_and_wrong_value(tmp_path):
    import json
    original = fun('(let ((a (+ x -2))) (+ a y))')
    restored = G.decode(G.encode(original, SIG)[0]['program'], 'f', SIG)['candidate']
    good = G.equivalent(original, restored, SIG)
    bad = G.equivalent(original, fun('(+ x y)'), SIG)
    (tmp_path/'actual-checks.json').write_text(json.dumps({'manual_fixture': True, 'pass': good, 'wrong_value': bad}, indent=2))
    assert good['status'] == 'PASS' and good['solver_result'] == 'unsat'
    assert bad['status'] == 'FAIL' and bad['solver_result'] == 'sat'
    assert good['native_invoked'] and bad['native_invoked']


@pytest.mark.parametrize('task_id', ['jmbl_fg_max3','jmbl_fg_max10','jmbl_fg_array_search_4','jmbl_fg_array_search_10','jmbl_fg_mpg_guard2'])
def test_requests_keep_primitive_grammar_and_exact_task(task_id):
    task = load_task(task_id)
    library = G.admit_macros([{'name':'fn_0','body':'(+ #0 #1)','arity':2}])
    original = G.forms(task['sygus'])
    primitive = D.search_request(task, library, 'explicit_primitive')
    adapted = D.search_request(task, library, 'explicit_macro')
    assert G.forms(primitive['sygus']) == original
    nodes = G.forms(adapted['sygus'])
    assert [n for n in nodes if str(n[0]) == 'constraint'] == [n for n in original if str(n[0]) == 'constraint']
    before = next(n for n in original if str(n[0]) == 'synth-fun')
    after = next(n for n in nodes if str(n[0]) == 'synth-fun')
    assert before[:4] == after[:4]
    assert before[4] == after[4][:-1]
    assert after[4][-1] == G.one('(GEN_fn_0 Int)')
    assert after[5][0][2][:-1] == before[5][0][2]
    assert after[5][1:-1] == before[5][1:]
    assert after[5][0][2][-1] == S('GEN_fn_0')
    assert after[5][-1] == G.one('(GEN_fn_0 Int ((fn_0 OCM_I OCM_I)))')
    assert adapted['consumption'] == 'CANNOT_CHECK_CONSUMPTION'
    assert D.search_request(task, {}, 'implicit_primitive')['sygus'] == task['original_sygus']


def test_malformed_input_never_calls_discovery(monkeypatch):
    def forbidden(*a, **k):
        pytest.fail('discovery not authorized in engineering qualification')
    monkeypatch.setattr(D, 'donor', forbidden)
    with pytest.raises(ValueError, match='two distinct'):
        D.induce([])


@pytest.mark.parametrize('check_status,terminal', [('FAIL','REFUSED_REWRITE'), ('CANNOT_CHECK','CANNOT_CHECK_REWRITE')])
def test_nonpass_manual_rewrite_never_ready(monkeypatch, check_status, terminal):
    from types import SimpleNamespace
    task = load_task('jmbl_fg_max3')
    rewritten = '(lam (lam (lam $0)))'
    prepared = [{'task': task, 'candidate': 'MANUAL_UNUSED', 'program': rewritten}]
    # An explicit fabricated donor record tests gating; no donor backend runs.
    fake = SimpleNamespace(json={'manual_fixture': True}, abstractions=[], rewritten=[rewritten])
    monkeypatch.setattr(D, 'prepare', lambda _: prepared)
    monkeypatch.setattr(D, 'donor', lambda: SimpleNamespace(compress=lambda *a, **k: fake))
    monkeypatch.setattr(D, 'equivalent', lambda *a: {'status': check_status})
    assert D.induce([])['status'] == terminal


def test_malformed_manual_donor_retains_raw_without_retry():
    from types import SimpleNamespace
    raw = {'manual_fixture': True, 'abstractions': [{'name':'fn_0','body':'(lam #0)','arity':1}], 'rewritten':[]}
    fake = SimpleNamespace(json=raw, abstractions=[SimpleNamespace(**raw['abstractions'][0])], rewritten=[])
    got = D.assess(fake, [])
    assert got['status'] == 'REFUSED_DONOR_RESULT' and got['raw'] == raw
    assert got['reason'].startswith('ValueError:') and got['library'] == {}
    assert got['later_generation_consumption'] == 'NOT_RUN'


def test_manual_donor_receipt_is_json_data(monkeypatch):
    import json
    from types import SimpleNamespace
    task = load_task('jmbl_fg_max3')
    raw = {'manual_fixture': True, 'abstractions': [{'name':'fn_0','body':'(+ #0 #1)','arity':2}]}
    fake = SimpleNamespace(json=raw, abstractions=[SimpleNamespace(**raw['abstractions'][0])], rewritten=['(lam (lam (lam (fn_0 $0 $1))))'])
    monkeypatch.setattr(D, 'equivalent', lambda *a: {'status':'PASS', 'manual_fixture':True})
    got = D.assess(fake, [{'task':task, 'candidate':'MANUAL_UNUSED'}])
    assert got['status'] == 'PROPOSED_ABSTRACTIONS'
    assert json.loads(json.dumps(got))['library']['fn_0']['sorts'] == ['Int','Int']
