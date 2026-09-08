"""Real solve parity and serving-only boundaries; no benchmark claims."""
from fractions import Fraction as F

import pytest

from ocm.kso import navigation as N, navigation_matrix_free as MF
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import CannotCheck, WarrantProfile as WP
from ocm.kso.surprise import SurpriseModel
from ocm.runtime import navigation_serving as NS, solve as SV
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.event import EventType


def space():
    return KnowledgeSpace((Atom("q", "query_seed"), Atom("f", "claim", WP.of({"fact"})),
                           Atom("u", "claim", WP.partial(()))),
                          (Hyperedge("qf", ("q",), ("f",), "SUPPORT"),
                           Hyperedge("qu", ("q",), ("u",), "SUPPORT")))


def task(targets=()):
    return SV.Task("t", (SV.QueryPart("use fact", "claim", ("q",)),), targets=targets)


def operators(calls):
    def backend(name, value):
        def run(*args):
            calls.append(name)
            return {"value": value}
        return run
    return (SV.OperatorSpec("z_first", "1", backend("first", 42), ("f",),
                            warrant=WP.of({"first"}), checker=lambda out: SV.Status.PASS),
            SV.OperatorSpec("a_second", "1", backend("second", 99), ("f",),
                            checker=lambda out: SV.Status.PASS))


def semantic(result):
    data = result.as_dict()
    for stage in data["trace"]["stages"]:
        stage["payload"].pop("exact_navigation", None)
    return data


@pytest.mark.parametrize("revoked", ((), ("first",), ("fact",)))
@pytest.mark.parametrize("bound", (0, 12))
def test_complete_solve_matches_dense_ranking_tie_and_resources(monkeypatch, revoked, bound):
    cfg = SV.SolveConfig(exact_extraction_max_atoms=bound, surprise_model=SurpriseModel.PROPAGATED)
    actual_calls = []
    actual = SV.solve(space(), task(("f",)), operators(actual_calls), config=cfg, revoked=revoked)
    expected_calls = []
    def dense(*args, work, **kwargs):
        return N.fixed_point(*args, **kwargs)
    monkeypatch.setattr(NS, "fixed_point", dense)
    expected = SV.solve(space(), task(("f",)), operators(expected_calls), config=cfg, revoked=revoked)
    assert semantic(actual) == semantic(expected)
    assert actual_calls == expected_calls
    if revoked != ("fact",):
        assert actual.answer == {"value": 99 if revoked else 42}
    assert SV.committed(actual) == SV.committed(expected)


def test_actual_runtime_records_path_revocation_and_restart(tmp_path, monkeypatch):
    rt = OCMRuntime(tmp_path, config=SV.SolveConfig(surprise_model=SurpriseModel.PROPAGATED))
    rt.admit_object(Atom("q", "query_seed", quarantined=True), (), "INSTRUCTION")
    rt.admit_object(Atom("f", "claim"), (Hyperedge("qf", ("q",), ("f",), "SUPPORT"),), "INSTRUCTION")
    def forbidden(*args, **kwargs):
        raise AssertionError("dense used on authored exact case")
    monkeypatch.setattr(N, "fixed_point", forbidden)
    for action, expected in ((None, 42), ("revoke", 99), ("reinstate", 42)):
        if action:
            getattr(rt, action)(("first",))
        calls = []
        result = rt.solve(task(), operators(calls))
        assert result.answer == {"value": expected} and SV.committed(result)
        assert calls == (["second"] if action == "revoke" else ["first", "second"])
        event = next(e for e in reversed(rt.events) if e.event_type is EventType.NAVIGATION)
        assert all(c["terminal"] == "MATRIX_FREE_EXACT"
                   for c in event.payload["payload"]["exact_navigation"]["calls"])
    rt.persist()
    restored = OCMRuntime(tmp_path, config=rt.config)
    assert restored.solve(task(), operators([])).answer == {"value": 42}


def test_reused_work_does_not_replay_prior_failure(monkeypatch):
    work = {}; original = MF.transpose_matvec
    def refused(*args, **kwargs):
        raise CannotCheck("one authored attempt")
    monkeypatch.setattr(MF, "transpose_matvec", refused)
    NS.fixed_point(space(), [F(1), F(0), F(0)], F(1, 3), work=work)
    assert work["attempt_error"] and work["dense_calls"] == 1
    monkeypatch.setattr(MF, "transpose_matvec", original)
    NS.fixed_point(space(), [F(1), F(0), F(0)], F(1, 3), work=work)
    assert work["terminal"] == "MATRIX_FREE_EXACT" and work["dense_calls"] == 0
    assert work["attempt_error"] is None and work["dense_internal_work"] is None
    assert work["partial_matvec_work"] is None


def test_unsupported_mode_does_not_run_formatter_before_reference():
    class Mode:
        def __str__(self):
            raise AssertionError("unsupported formatter executed")
    mode = Mode(); ks = space(); seed = [F(1), F(0), F(0)]; work = {}
    expected = N.fixed_point(ks, seed, F(1, 3), mode=mode)
    assert NS.fixed_point(ks, seed, F(1, 3), mode=mode, work=work) == expected
    assert work["matvec_attempts"] == 0


def test_target_scope_and_frozen_denominator_tail_work():
    ks = KnowledgeSpace(space().atoms,
        (Hyperedge("j", ("q", "f"), ("u",), "DEPENDENCE", warrant=WP.of({"dead"})),))
    stage, _ = SV.navigate_stage(ks, [F(1), F(0), F(0)], task(("u",)), SV.SolveConfig(), ("dead",))
    report = stage.payload["exact_navigation"]
    assert report["coverage"] == "FOUR_FIXED_POINTS_ONLY"
    assert report["target_navigation_calls_outside_detail"] == 1
    assert all(c["denominator_tail_visits"] == 6 for c in report["calls"])


def test_stateful_relevance_exact_sequence_matches_reference():
    ks = space(); seed = [F(1), F(0), F(0)]
    calls = []
    def beta(relation):
        calls.append(relation)
        return F(len(calls) % 3 + 1)
    cfg = SV.SolveConfig(relevance=beta)
    stage, nav = SV.navigate_stage(ks, seed, task(), cfg, ())
    observed = list(calls); calls.clear()
    expected = {}
    for name, value, mode in (("act_w", seed, N.NavigationMode.WARRANTED),
            ("act_x", seed, N.NavigationMode.EXPLORATORY),
            ("background", N.uniform_seed(ks), N.NavigationMode.WARRANTED),
            ("background_x", N.uniform_seed(ks), N.NavigationMode.EXPLORATORY)):
        expected[name] = N.fixed_point(ks, value, cfg.alpha, relevance=beta, mode=mode)
    assert calls == observed and {k: nav[k] for k in expected} == expected
    assert all(c["matvec_attempts"] == 0 for c in stage.payload["exact_navigation"]["calls"])


@pytest.mark.parametrize("seed,alpha", (([F(1), F(0)], F(1, 3)), ([F(1)] * 3, F(0)),
                                      ([F(1)] * 3, F(2))))
def test_invalid_reference_inputs_keep_exception(seed, alpha):
    with pytest.raises(ValueError) as expected:
        N.fixed_point(space(), seed, alpha)
    work = {}
    with pytest.raises(ValueError) as actual:
        NS.fixed_point(space(), seed, alpha, work=work)
    assert str(actual.value) == str(expected.value) and work["terminal"] == "REFUSED"


def test_explicit_matrix_reference_api_and_unsupported_float_unchanged(monkeypatch):
    ks = space(); seed = [F(1), F(0), F(0)]; matrix = N.navigation_matrix(ks)
    expected = N.fixed_point(ks, seed, F(1, 3), matrix=matrix)
    monkeypatch.setattr(MF, "transpose_matvec", lambda *a, **k: pytest.fail("not the reference API"))
    assert N.fixed_point(ks, seed, F(1, 3), matrix=matrix) == expected
    work = {}
    assert NS.fixed_point(ks, seed, .25, work=work) == N.fixed_point(ks, seed, .25)
    assert work["reason"] == "UNSUPPORTED_INPUT" and work["matvec_attempts"] == 0
