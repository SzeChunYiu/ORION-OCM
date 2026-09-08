"""Exact serving selection, reference parity, fallback, and whole-field work."""
from dataclasses import replace
from fractions import Fraction as F
from importlib import import_module

import pytest

from ocm.kso import navigation as N
from ocm.kso import navigation_matrix_free as MF
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import CannotCheck, WarrantProfile as WP
from ocm.runtime import solve as SV


def space(kind="pair"):
    atoms = (Atom("a", "query_seed"), Atom("b", "claim", WP.of({"b"})),
             Atom("c", "claim", WP.partial(())), Atom("d", "claim"))
    edges = (Hyperedge("ab", ("a",), ("b",), "SUPPORT"),
             Hyperedge("ac", ("a",), ("c",), "SUPPORT"))
    if kind == "joint":
        edges = (Hyperedge("joint", ("a", "b"), ("c", "d"), "DEPENDENCE",
                           weight=F(3, 2), head_weights=(F(1), F(3)), warrant=WP.of({"edge"})),)
    if kind == "cycle":
        edges = (Hyperedge("ab", ("a",), ("b",), "SUPPORT"),
                 Hyperedge("ba", ("b",), ("a",), "SUPPORT"),
                 Hyperedge("bd", ("b",), ("d",), "SUPPORT"))
    if kind == "empty":
        edges = ()
    return KnowledgeSpace(atoms, edges)


def task():
    return SV.Task("t", (SV.QueryPart("a", "query_seed", ("a",)),))


def reference(ks, seed, cfg, rv):
    return {name: N.fixed_point(ks, value, cfg.alpha, revoked=rv, relevance=cfg.relevance, mode=mode)
            for name, value, mode in (
                ("act_w", seed, N.NavigationMode.WARRANTED),
                ("act_x", seed, N.NavigationMode.EXPLORATORY),
                ("background", N.uniform_seed(ks), N.NavigationMode.WARRANTED),
                ("background_x", N.uniform_seed(ks), N.NavigationMode.EXPLORATORY))}


@pytest.mark.parametrize("kind", ("pair", "joint", "empty"))
@pytest.mark.parametrize("rv", ((), ("b",), ("edge",)))
def test_four_exact_vectors_and_gates_bypass_dense(kind, rv, monkeypatch):
    ks = space(kind); seed = [F(1), F(0), F(0), F(0)]; cfg = SV.SolveConfig()
    expected = reference(ks, seed, cfg, rv)
    def forbidden(*args, **kwargs):
        raise AssertionError("dense fallback on exact zero residual")
    monkeypatch.setattr(N, "fixed_point", forbidden)
    stage, nav = SV.navigate_stage(ks, seed, task(), cfg, iter(rv))
    assert {name: nav[name] for name in expected} == expected
    report = stage.payload["exact_navigation"]
    assert report["scope"] == "WHOLE_FIELD"
    assert [c["output"] for c in report["calls"]] == list(expected)
    for call in report["calls"]:
        assert call["terminal"] == "MATRIX_FREE_EXACT" and call["residual_l1"] == "0"
        assert call["matvec_attempts"] == call["matvec_completed"] == 3
        assert call["index_entries"] == 3 * len(ks.ids)
        assert call["denominator_edge_visits"] == 3 * len(ks.hyperedges)
        assert call["dense_calls"] == 0
    assert stage.resources.navigation_work == 4 * len(ks.ids) ** 2


def test_cycle_falls_back_and_retains_all_attempted_work(monkeypatch):
    ks = space("cycle"); seed = [F(1), F(0), F(0), F(0)]; cfg = SV.SolveConfig()
    expected = reference(ks, seed, cfg, ())
    original = N.fixed_point; dense = []
    def counted(*args, **kwargs):
        dense.append(kwargs["mode"])
        return original(*args, **kwargs)
    monkeypatch.setattr(N, "fixed_point", counted)
    stage, nav = SV.navigate_stage(ks, seed, task(), cfg, ())
    assert {name: nav[name] for name in expected} == expected and len(dense) == 4
    for call in stage.payload["exact_navigation"]["calls"]:
        assert call["terminal"] == "DENSE_REFERENCE" and F(call["residual_l1"]) > 0
        assert call["matvec_attempts"] == call["matvec_completed"] == 3
        assert call["dense_calls"] == 1 and call["dense_matrix_entries"] == 16
        assert call["reason"] == "NONZERO_RESIDUAL"


@pytest.mark.parametrize("alpha,seed", ((F(1), [F(1), F(0), F(0), F(0)]),
                                       (F(1, 3), [F(0)] * 4)))
def test_cyclic_stationary_or_zero_seed_is_exact(alpha, seed):
    ks = space("cycle"); work = {}
    serve = import_module("ocm.runtime.navigation_serving").fixed_point
    assert serve(ks, seed, alpha, work=work) == N.fixed_point(ks, seed, alpha)
    assert work["terminal"] == "MATRIX_FREE_EXACT" and work["residual_l1"] == "0"


def test_tiny_nonzero_residual_never_gets_tolerance_acceptance():
    ks = space("cycle"); seed = [F(1), F(0), F(0), F(0)]; work = {}
    alpha = F(10**12 - 1, 10**12)
    serve = import_module("ocm.runtime.navigation_serving").fixed_point
    assert serve(ks, seed, alpha, work=work) == N.fixed_point(ks, seed, alpha)
    assert 0 < F(work["residual_l1"]) < F(1, 10**12)
    assert work["terminal"] == "DENSE_REFERENCE" and work["dense_calls"] == 1


@pytest.mark.parametrize("seed", ([F(-1), F(0), F(0), F(0)],
                                  [F(2), F(0), F(0), F(0)]))
def test_gated_seed_validation_matches_reference(seed):
    ks = replace(space(), atoms=(Atom("a", "query_seed", WP.of({"dead"})), *space().atoms[1:]))
    serve = import_module("ocm.runtime.navigation_serving").fixed_point
    assert serve(ks, seed, F(1, 3), revoked=("dead",), work={}) == N.fixed_point(ks, seed, F(1, 3), revoked=("dead",))
    for mode in N.NavigationMode:
        with pytest.raises(ValueError, match="sub-probability"):
            serve(ks, seed, F(1, 3), mode=mode, work={})


def test_unsupported_callable_preserves_calls_and_has_no_attempt():
    ks = space(); seed = [F(1), F(0), F(0), F(0)]; beta_calls = []
    def beta(relation):
        beta_calls.append(relation); return F(1)
    cfg = SV.SolveConfig(relevance=beta)
    expected = reference(ks, seed, cfg, ()); expected_calls = beta_calls[:]; beta_calls.clear()
    stage, nav = SV.navigate_stage(ks, seed, task(), cfg, ())
    assert {name: nav[name] for name in expected} == expected and beta_calls == expected_calls
    for call in stage.payload["exact_navigation"]["calls"]:
        assert call["reason"] == "UNSUPPORTED_INPUT" and call["matvec_attempts"] == 0
        assert call["dense_calls"] == 1


def test_partial_attempt_and_dense_refusal_keep_reached_work(monkeypatch):
    def refused(*args, **kwargs):
        raise CannotCheck("authored serving refusal")
    monkeypatch.setattr(MF, "transpose_matvec", refused)
    monkeypatch.setattr(N, "fixed_point", refused)
    stage, nav = SV.navigate_stage(space(), [F(1), F(0), F(0), F(0)], task(), SV.SolveConfig(), ())
    assert stage.status is SV.Status.CANNOT_CHECK and nav == {}
    calls = stage.payload["exact_navigation"]["calls"]
    assert len(calls) == 1
    assert calls[0]["matvec_attempts"] == 1 and calls[0]["matvec_completed"] == 0
    assert calls[0]["partial_matvec_work"] == "UNAVAILABLE"
    assert calls[0]["dense_calls"] == 1 and calls[0]["terminal"] == "REFUSED"


def test_whole_field_and_global_cyclic_fallback():
    n = 12
    ks = KnowledgeSpace(tuple(Atom(str(i), "claim") for i in range(n)),
        tuple(Hyperedge(str(i), (str(i),), (str((i+1) % n),), "SUPPORT") for i in range(n)))
    seed = [F(1)] + [F(0)] * (n-1); work = {}
    serve = import_module("ocm.runtime.navigation_serving").fixed_point
    assert serve(ks, seed, F(1, 3), work=work) == N.fixed_point(ks, seed, F(1, 3))
    assert work["terminal"] == "DENSE_REFERENCE" and work["matvec_completed"] == 3
    assert work["index_entries"] == 3*n and work["denominator_edge_visits"] == 3*n
    assert work["dense_matrix_entries"] == n*n
