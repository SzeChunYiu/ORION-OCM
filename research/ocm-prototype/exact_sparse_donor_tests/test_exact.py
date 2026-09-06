"""Exact kernel semantics, unchanged fallback and independent checker controls."""
from fractions import Fraction as F
import importlib
import importlib.util
import pytest
from ocm.kso import navigation as N
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import CannotCheck, WarrantProfile as WP


def donor():
    assert importlib.util.find_spec("exact_sparse_donor"), "missing exact sparse donor"
    return importlib.import_module("exact_sparse_donor")


def field():
    atoms = (Atom("s", "claim"), Atom("a", "claim", WP.of({"a"})),
             Atom("b", "claim"), Atom("u", "claim", WP.partial([frozenset({"u"})])),
             Atom("isolated", "claim"))
    edges = (
        Hyperedge("multi", ("s", "a"), ("b", "u"), "SUPPORT", F(3), (F(2), F(1))),
        Hyperedge("parallel", ("s",), ("b",), "SUPPORT", F(2)),
        Hyperedge("dead", ("s",), ("a",), "DEPENDENCE", F(5), warrant=WP.of({"edge"})),
        Hyperedge("loop", ("b",), ("s",), "DEPENDENCE", F(1)),
        Hyperedge("zero", ("b",), ("a",), "SUPPORT", F(0)))
    return KnowledgeSpace(atoms, edges)


@pytest.mark.parametrize("mode", list(N.NavigationMode))
@pytest.mark.parametrize("revoked", [(), ("a",), ("edge",), ("u",), ("a", "edge")])
@pytest.mark.parametrize("relevance", [None, {"SUPPORT": F(2), "DEPENDENCE": F(0)}])
def test_sparse_coefficients_and_full_values_match_original(mode, revoked, relevance):
    D = donor()
    ks, seed, alpha = field(), [F(1), F(0), F(0), F(0), F(0)], F(1, 3)
    kwargs = dict(mode=mode, revoked=revoked, relevance=relevance)
    A, B = D.assemble(ks, seed, alpha, **kwargs)
    P = N.navigation_matrix(ks, **kwargs)
    expected = {(i, j): F(i == j) - (1-alpha)*P.rows[j][i]
                for i in range(5) for j in range(5)}
    assert A.rep.fmt == B.rep.fmt == "sparse"
    assert {(i, j): F(str(A[i, j].element)) for i, j in expected} == expected
    expected_values = N.fixed_point(ks, seed, alpha, **kwargs)
    actual, receipt = D.solve_checked(ks, seed, alpha, **kwargs)
    assert actual == expected_values and tuple(actual) == ks.ids
    assert all(type(x) is F for x in actual.values())
    assert receipt["independent_residual"] == "EXACT_ZERO"
    assert receipt["donor_solve_calls"] == 1


def test_exact_builder_does_not_materialize_original_dense_kernel(monkeypatch):
    D = donor()
    def forbidden(*args, **kwargs):
        pytest.fail("dense assembly was used by candidate builder")
    monkeypatch.setattr(N, "navigation_matrix", forbidden)
    A, B = D.assemble(field(), [F(1), F(0), F(0), F(0), F(0)], F(1, 3))
    assert A.shape == (5, 5) and B.shape == (5, 1)


def test_original_elimination_is_not_used_for_supported_donor(monkeypatch):
    D = donor()
    expected = N.fixed_point(field(), [F(1), F(0), F(0), F(0), F(0)], F(1, 3))
    monkeypatch.setattr(N, "_solve_exact", lambda *a: pytest.fail("parent elimination called"))
    assert D.fixed_point(field(), [F(1), F(0), F(0), F(0), F(0)], F(1, 3)) == expected


def test_callable_relevance_falls_back_without_extra_evaluation():
    D = donor()
    calls = []
    def relevance(relation):
        calls.append(relation)
        return F(1 + len(calls) % 2)
    args = (field(), [F(1), F(0), F(0), F(0), F(0)], F(1, 3))
    expected = N.fixed_point(*args, relevance=relevance)
    expected_calls = calls[:]
    calls.clear()
    actual, receipt = D.solve_checked(*args, relevance=relevance)
    assert actual == expected and calls == expected_calls
    assert receipt["route"] == "ORIGINAL_CALLABLE_RELEVANCE"
    assert receipt["donor_solve_calls"] == 0


def test_supplied_matrix_keeps_original_contract():
    D = donor()
    ks = field()
    matrix = N.navigation_matrix(ks, mode=N.NavigationMode.EXPLORATORY)
    args = (ks, [F(1), F(0), F(0), F(0), F(0)], F(1, 3))
    actual, receipt = D.solve_checked(*args, matrix=matrix, revoked=("a",))
    assert actual == N.fixed_point(*args, matrix=matrix, revoked=("a",))
    assert receipt["route"] == "ORIGINAL_SUPPLIED_MATRIX"


@pytest.mark.parametrize("seed,alpha", [([F(-1), F(0), F(0), F(0), F(0)], F(1,3)),
    ([F(2), F(0), F(0), F(0), F(0)], F(1,3)), ([F(1)]*5, F(0)), ([F(0)]*4, F(1,3))])
def test_invalid_inputs_retain_original_exception_type(seed, alpha):
    D = donor()
    with pytest.raises(Exception) as original:
        N.fixed_point(field(), seed, alpha)
    with pytest.raises(type(original.value)):
        D.fixed_point(field(), seed, alpha)


@pytest.mark.parametrize("seed,alpha", [([F(0)]*5, F(1,3)), ([F(1),F(0),F(0),F(0),F(0)], F(1))])
def test_zero_seed_and_alpha_one(seed, alpha):
    D = donor()
    assert D.fixed_point(field(), seed, alpha) == N.fixed_point(field(), seed, alpha)


def test_empty_field_retains_empty_result():
    D = donor()
    ks = KnowledgeSpace((), ())
    assert D.fixed_point(ks, [], F(1,3)) == N.fixed_point(ks, [], F(1,3)) == {}


def test_checker_accepts_real_result_and_rejects_changed_missing_or_float_output():
    D = donor()
    C = importlib.import_module("exact_sparse_donor_check")
    ks, seed, alpha = field(), [F(1),F(0),F(0),F(0),F(0)], F(1,3)
    values = D.fixed_point(ks, seed, alpha)
    C.verify(ks, seed, alpha, values)
    bad = [{**values, "b": values["b"]+F(1,100)},
           {k:v for k,v in values.items() if k != "isolated"},
           {**values, "b": float(values["b"])}]
    for changed in bad:
        with pytest.raises(CannotCheck):
            C.verify(ks, seed, alpha, changed)
