"""Theory batch 8 (FDX-01 H1) obligation: the commitment gate may not read an epoch-bounded scope as
current on context alone — without a declared evaluation time it refuses; with one it checks the epoch."""
from __future__ import annotations

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import WarrantProfile as WP
from ocm.runtime import solve as S


def _outcome(op: S.OperatorSpec) -> S.SolveOutcome:
    tr = S.SolveTrace("t")
    tr.add(S.StageResult(S.Stage.COMPOSITION, S.Status.PASS, "ok"))
    return S.SolveOutcome(S.Decision.ANSWER, tr, answer={"v": 1}, candidate=(op, {"v": 1}, WP.of({"e1"})))


def test_epoch_bounded_scope_needs_a_declared_evaluation_time():
    bounded = S.OperatorSpec("op", "1", lambda s: s, ("a",), scope=Scope.of("ctx", epoch=(10.0, 20.0)))
    unbounded = S.OperatorSpec("op2", "1", lambda s: s, ("a",), scope=Scope.of("ctx"))
    auth = Authority.of(commit=1)
    # no time declared: refused (the certificate would be CONDITIONAL_ON_ASSUMPTIONS, not MONITORED_CURRENT)
    r = S.commitment_gate(_outcome(bounded), S.Task("t", (), context="ctx"), (), commit_authority=auth)
    assert r.status is S.Status.FAIL and r.reason == "REFUSED:SCOPE_EPOCH_UNDECLARED"
    # time inside the epoch: committed; outside: out of scope
    assert S.commitment_gate(_outcome(bounded), S.Task("t", (), context="ctx", at=15.0), (), commit_authority=auth).status is S.Status.PASS
    assert S.commitment_gate(_outcome(bounded), S.Task("t", (), context="ctx", at=25.0), (), commit_authority=auth).reason == "REFUSED:OUT_OF_SCOPE"
    # an unbounded scope commits on context alone, as before
    assert S.commitment_gate(_outcome(unbounded), S.Task("t", (), context="ctx"), (), commit_authority=auth).status is S.Status.PASS
    # the hostile (the previous gate): covers() without `at` skips the epoch and would have committed
    assert bounded.scope.covers("ctx") is True and bounded.scope.covers("ctx", 25.0) is False
