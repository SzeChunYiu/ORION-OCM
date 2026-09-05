"""MEG-10 procedure algebra readings and MEG-16 nogoods: exhaustive checkers + mutants."""
from __future__ import annotations

from ocm.kso import nogoods as NG
from ocm.kso import procedures as P
from ocm.kso.warrant import ONE, Liveness, WarrantProfile as WP


def test_procedure_algebra_exhaustive():
    out = P.check_procedure_algebra(3)
    assert out["strict_witness"] == 1 and out["static_below_trace"] == out["trace_is_meet_of_fired"] == 800


def test_reading_is_recorded_and_the_static_for_trace_mutant_is_wrong_on_the_live_branch():
    a = P.Prim("a", lambda v: v, (frozenset({0}),))
    b = P.Prim("b", lambda v: v, (frozenset({1}),))
    prog = P.If(P.Test("even", lambda v: v % 2 == 0), a, b)
    static_lp = P.LearnedProcedure.static("c", prog)
    trace_lp = P.LearnedProcedure("c", prog, P.Reading.TRACE, ONE)
    assert static_lp.liveness_for_input(2, (1,)) is Liveness.DEAD          # static: both branches must be live
    assert trace_lp.liveness_for_input(2, (1,)) is Liveness.LIVE           # trace: the even branch ran and is live
    assert P.mutant_static_reading_for_trace_claim(trace_lp, 2, (1,)) is Liveness.DEAD
    assert trace_lp.liveness_for_input(3, (1,)) is Liveness.DEAD


def test_bounded_loop_fires_guard_each_round_and_static_is_idempotent():
    body = P.Prim("inc", lambda v: v + 1, (frozenset({5}),))
    loop = P.Loop(body, P.Test("lt3", lambda v: v < 3, ONE), 10)
    r = P.run(loop, 0)
    assert r.output == 3 and r.fired.count("inc") == 3 and r.trace_warrant == (frozenset({5}),)
    assert P.static_warrant(P.Loop(body, P.Test("lt3", lambda v: v < 3), 1)) == P.static_warrant(loop)


def test_nogood_filter_after_compose_not_before():
    ng = NG.NogoodSet.of({0, 1})
    p, q = WP.of({0}), WP.of({1})
    assert ng.liveness(p.meet(q), ()) is Liveness.DEAD
    assert NG.mutant_filter_before_compose(ng, p.lower, q.lower) == (frozenset({0, 1}),)
    assert ng.liveness(p, ()) is Liveness.LIVE and ng.liveness(q, ()) is Liveness.LIVE
