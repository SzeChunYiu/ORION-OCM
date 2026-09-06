"""Generic mechanical term/search controls; no Lean/native execution."""
import pytest
import f0_terms as T
from f0_search import SearchLimits, search
from f0_fixture import f0_fixture, chain_fixture


def test_exposed_composition_is_typed_and_reconstructed_generically():
    task = f0_fixture()
    result = search(**task)
    assert result.status == "FOUND", result.reason
    constants = T.constants_from_data(task["constants"])
    candidate, goal = T.from_data(result.candidate), T.from_data(task["goal"])
    T.check(candidate, goal, constants)
    assert result.used_constants == (0,)  # Eq appears in annotations; no imported proof lemma.
    assert result.counters["applications"] > 0


def test_json_constant_keys_are_canonical_and_no_unknown_names_enter():
    task = f0_fixture()
    task["constants"] = {str(k): v for k, v in task["constants"].items()}
    assert search(**task).status == "FOUND"
    for key in ("01", "-1", "name", True):
        with pytest.raises(T.TermError): T.constants_from_data({key: ["sort", 0]})
    with pytest.raises(T.TermError): T.constants_from_data({0:["sort",0], "0":["sort",0]})


def test_alpha_renaming_and_independent_premise_order_do_not_choose_a_route():
    assert f0_fixture(rename="arbitrary_") == f0_fixture()
    task = f0_fixture(reverse_premises=True)
    result = search(**task)
    assert result.status == "FOUND"
    T.check(T.from_data(result.candidate), T.from_data(task["goal"]), T.constants_from_data(task["constants"]))


@pytest.mark.parametrize("change", ["missing_member", "reversed_subset", "wrong_witness"])
def test_missing_or_wrong_premise_never_yields_proof(change):
    task = f0_fixture(change=change)
    result = search(**task, limits=SearchLimits(max_application_depth=3))
    assert result.status == "EXHAUSTED_REGISTERED_BOUND"
    assert result.candidate is None


def test_independent_chain_requires_sufficient_registered_depth():
    task = chain_fixture(3)
    low = search(**task, limits=SearchLimits(max_application_depth=2))
    high = search(**task, limits=SearchLimits(max_application_depth=3))
    assert low.status == "EXHAUSTED_REGISTERED_BOUND" and low.candidate is None
    assert high.status == "FOUND"
    assert search(**chain_fixture(0)).status == "FOUND"


def test_actual_operational_stop_is_not_exhaustion_or_falsity():
    result = search(**f0_fixture(), limits=SearchLimits(max_terms=1))
    assert result.status == "CANNOT_CHECK" and result.candidate is None
    assert "max_terms" in result.reason


def test_transport_refuses_unknown_code_unbound_variables_and_malformed_nodes():
    for raw in (["raw", "by sorry"], ["const", "MEFoundation.agreement_sound"], ["var", True],
                ["sort", 3], ["lam", ["sort",0]], ["meta",0]):
        with pytest.raises(T.TermError): T.from_data(raw)
    with pytest.raises(T.TermError): T.infer(T.from_data(["var",0]), {})
    with pytest.raises(T.TermError): T.infer(T.from_data(["const",99]), {})
    assert search(["const",99], {}).status == "CANNOT_CHECK"


def test_capture_avoiding_beta_reduction_preserves_outer_variable():
    term = T.from_data(["app", ["lam", ["sort",0], ["lam",["sort",0],["var",1]]], ["var",0]])
    assert T.to_data(T.normalize(term)) == ["lam",["sort",0],["var",1]]


def test_corrupted_candidate_cannot_acquire_the_requested_type():
    task = chain_fixture(1)
    result = search(**task)
    bad = T.from_data(result.candidate)
    # Replace the final proof body with an out-of-scope local; keep the target untouched.
    def corrupt(t): return (t[0],t[1],corrupt(t[2])) if t[0]=="lam" else ("var",100)
    with pytest.raises(T.TermError): T.check(corrupt(bad),T.from_data(task["goal"]),{})


def test_repeat_search_has_stable_result_and_counters():
    first, second = search(**f0_fixture()), search(**f0_fixture())
    assert first == second


def test_constant_target_is_a_boundary_condition_not_a_search_trick():
    # A registered proof premise trivially solves its type. The trusted runner must
    # reject an injected target constant before giving this altered registry to search.
    task = chain_fixture(0)
    constants = {99: task["goal"]}
    T.check(T.from_data(["const",99]), T.from_data(task["goal"]), T.constants_from_data(constants))
    with pytest.raises(T.TermError): T.check(T.from_data(["const",99]),T.from_data(task["goal"]),{})


def test_oversized_numeric_registry_key_refuses_without_interpreter_exception():
    with pytest.raises(T.TermError):
        T.constants_from_data({"9" * 5000: ["sort", 0]})
    assert search(["sort",0], {"9" * 5000: ["sort",0]}).status == "CANNOT_CHECK"


def test_generic_constant_application_and_id_permutation():
    def task(a, b, fn, value):
        return {"goal":["const",b], "constants":{
            a:["sort",0], b:["sort",0],
            fn:["pi",["const",a],["const",b]], value:["const",a]}}
    for ids in ((42,43,51,52), (113,109,127,101)):
        result = search(**task(*ids))
        assert result.status == "FOUND"
        assert result.candidate == ["app",["const",ids[2]],["const",ids[3]]]
        assert result.used_constants == tuple(sorted(ids[2:]))


def test_exposed_composition_does_not_need_imported_proof_lemmas():
    task = f0_fixture()
    task["constants"] = {0:task["constants"][0]}
    result = search(**task)
    assert result.status == "FOUND"
    assert result.used_constants == (0,)
