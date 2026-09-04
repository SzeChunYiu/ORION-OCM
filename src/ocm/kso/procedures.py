"""Procedure algebra with warrant readings (MEG-10; contract §8; M1 E2 observable contract).

The control algebra for 𝓟_t is fixed to the KAT/wiring fragment the contract left open:

    p ; q            sequencing
    p ⊗_w q          typed parallel wiring
    if g then p else q   guarded choice (g a test atom)
    p^{≤n}           bounded iteration

with two warrant readings that must never be conflated:

  TRACE reading   Λ_trace(run) = ⊗ of the warrants of the primitives/tests actually executed on
                  this run (the hyperedges fired along the trace);
  STATIC reading  Λ_static(p) = ⊗ over every primitive and test reachable in any branch — the
                  worst case: the procedure is warranted for *all* inputs only if every branch is.

Theorems (checked exhaustively on small programs and all revocations):
  (a) Λ_trace(run) = ⊗_{e ∈ fired} Λ(e)           (definition; matches firing.py KS-T02 gating)
  (b) Λ_static(p) ≤ Λ_trace(run) in the semiring order for every run (static is harder to satisfy)
      — hence LIVE(static) ⇒ LIVE(trace), never the converse.
  (c) iteration: Λ_static(p^{≤n}) = Λ_static(p) for n ≥ 1 (idempotence of ⊗ on antichains);
      Kleene star is well defined in the idempotent antichain semiring.
  (d) guard: in the TRACE reading the guard's warrant composes with the taken branch only; in the
      STATIC reading with both.
Parents: KAT (Kozen 1997, verified); ω-continuous provenance semirings (Green et al. 2007,
verified).  A `LearnedProcedure` must record which reading its warrant carries; using the static
reading for a trace claim (or vice versa) is the planted mutant.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Hashable, Iterable, Union

from .warrant import ONE, Liveness, Profile, WarrantProfile, all_profiles, leq, meet, meet_all, powerset


class Reading(str, Enum):
    TRACE = "TRACE"
    STATIC = "STATIC"


@dataclass(frozen=True)
class Prim:
    name: str
    fn: Callable[[Any], Any]
    warrant: Profile = ONE


@dataclass(frozen=True)
class Test:
    name: str
    pred: Callable[[Any], bool]
    warrant: Profile = ONE


@dataclass(frozen=True)
class Seq:
    left: "Proc"
    right: "Proc"


@dataclass(frozen=True)
class Par:
    left: "Proc"
    right: "Proc"
    merge: Callable[[Any, Any], Any] = lambda a, b: (a, b)


@dataclass(frozen=True)
class If:
    guard: Test
    then: "Proc"
    otherwise: "Proc"


@dataclass(frozen=True)
class Loop:
    body: "Proc"
    guard: Test
    bound: int


Proc = Union[Prim, Seq, Par, If, Loop]


@dataclass(frozen=True)
class Run:
    output: Any
    fired: tuple[str, ...]
    trace_warrant: Profile


def run(p: Proc, x: Any) -> Run:
    """Execute and accumulate the TRACE warrant (⊗ over everything actually fired)."""
    if isinstance(p, Prim):
        return Run(p.fn(x), (p.name,), p.warrant)
    if isinstance(p, Seq):
        a = run(p.left, x)
        b = run(p.right, a.output)
        return Run(b.output, a.fired + b.fired, meet(a.trace_warrant, b.trace_warrant))
    if isinstance(p, Par):
        a = run(p.left, x)
        b = run(p.right, x)
        return Run(p.merge(a.output, b.output), a.fired + b.fired, meet(a.trace_warrant, b.trace_warrant))
    if isinstance(p, If):
        branch = p.then if p.guard.pred(x) else p.otherwise
        r = run(branch, x)
        return Run(r.output, (p.guard.name,) + r.fired, meet(p.guard.warrant, r.trace_warrant))
    if isinstance(p, Loop):
        fired: tuple[str, ...] = ()
        w = ONE
        cur = x
        for _ in range(p.bound):
            fired += (p.guard.name,)
            w = meet(w, p.guard.warrant)
            if not p.guard.pred(cur):
                break
            r = run(p.body, cur)
            cur, fired, w = r.output, fired + r.fired, meet(w, r.trace_warrant)
        return Run(cur, fired, w)
    raise TypeError(type(p))


def static_warrant(p: Proc) -> Profile:
    """STATIC (worst-case) reading: ⊗ over every primitive and test reachable in any branch."""
    if isinstance(p, Prim):
        return p.warrant
    if isinstance(p, (Seq, Par)):
        return meet(static_warrant(p.left), static_warrant(p.right))
    if isinstance(p, If):
        return meet_all([p.guard.warrant, static_warrant(p.then), static_warrant(p.otherwise)])
    if isinstance(p, Loop):
        return meet(p.guard.warrant, static_warrant(p.body)) if p.bound >= 1 else p.guard.warrant
    raise TypeError(type(p))


@dataclass(frozen=True)
class LearnedProcedure:
    """A procedure atom's warrant with its reading recorded (MEG-10 runtime obligation)."""

    name: str
    proc: Proc
    reading: Reading
    warrant: Profile

    @staticmethod
    def static(name: str, proc: Proc) -> "LearnedProcedure":
        return LearnedProcedure(name, proc, Reading.STATIC, static_warrant(proc))

    def liveness_for_input(self, x: Any, revoked: Iterable[Hashable]) -> Liveness:
        w = static_warrant(self.proc) if self.reading is Reading.STATIC else run(self.proc, x).trace_warrant
        return WarrantProfile.certified(w).liveness(revoked)


def mutant_static_reading_for_trace_claim(lp: LearnedProcedure, x: Any, revoked: Iterable[Hashable]) -> Liveness:
    """Planted: answers a per-run (trace) liveness question with the static reading — claims DEAD
    for a run whose taken branch is fully live (or vice versa when misused the other way)."""
    return WarrantProfile.certified(static_warrant(lp.proc)).liveness(revoked)


def check_procedure_algebra(n_evidence: int = 3) -> dict[str, Any]:
    """Exhaustive on: primitives with every antichain warrant at n, a choice program, a bounded loop,
    all 2^n revocations."""
    ps = all_profiles(n_evidence)
    revs = powerset(tuple(range(n_evidence)))
    inc = Prim("inc", lambda v: v + 1)
    checks = {"trace_is_meet_of_fired": 0, "static_below_trace": 0, "live_static_implies_live_trace": 0, "guard_composes_with_taken_branch_only": 0, "iteration_idempotent": 0, "strict_witness": 0}
    for wa in ps:
        for wb in ps:
            a = Prim("a", lambda v: v * 2, wa)
            b = Prim("b", lambda v: v - 1, wb)
            g = Test("even", lambda v: v % 2 == 0, ONE)
            prog = If(g, a, b)
            for x in (2, 3):
                r = run(prog, x)
                taken = a if x % 2 == 0 else b
                assert r.trace_warrant == meet(g.warrant, taken.warrant)
                checks["trace_is_meet_of_fired"] += 1
                st = static_warrant(prog)
                assert leq(st, r.trace_warrant)
                checks["static_below_trace"] += 1
                for R in revs:
                    if WarrantProfile.certified(st).is_live(R):
                        assert WarrantProfile.certified(r.trace_warrant).is_live(R)
                        checks["live_static_implies_live_trace"] += 1
                assert st == meet_all([g.warrant, a.warrant, b.warrant])   # static: guard with both branches
                checks["guard_composes_with_taken_branch_only"] += 1
            # iteration idempotence (c)
            loop1 = Loop(Seq(a, inc), Test("lt", lambda v: v < 100), 1)
            loop3 = Loop(Seq(a, inc), Test("lt", lambda v: v < 100), 3)
            assert static_warrant(loop1) == static_warrant(loop3)
            checks["iteration_idempotent"] += 1
    # strict witness: static DEAD, trace LIVE on the taken branch
    a = Prim("a", lambda v: v, (frozenset({0}),))
    b = Prim("b", lambda v: v, (frozenset({1}),))
    lp = LearnedProcedure.static("choice", If(Test("even", lambda v: v % 2 == 0), a, b))
    r = run(lp.proc, 2)
    assert WarrantProfile.certified(static_warrant(lp.proc)).liveness((1,)) is Liveness.DEAD
    assert WarrantProfile.certified(r.trace_warrant).liveness((1,)) is Liveness.LIVE
    assert mutant_static_reading_for_trace_claim(lp, 2, (1,)) is Liveness.DEAD  # the mutant's wrong answer for this run
    trace_lp = LearnedProcedure("choice-trace", lp.proc, Reading.TRACE, ONE)
    assert trace_lp.liveness_for_input(2, (1,)) is Liveness.LIVE and trace_lp.liveness_for_input(3, (1,)) is Liveness.DEAD
    checks["strict_witness"] = 1
    return checks
