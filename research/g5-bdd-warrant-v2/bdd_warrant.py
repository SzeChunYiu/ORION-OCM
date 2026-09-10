"""G5.3 research ROBDD parent for warrant intervals.

Independent of the hash-consed support DAG. Production ``ocm.kso.warrant`` stays
the antichain oracle. No BDD package: Bryant unique-table + apply, stdlib only.

Boolean reading of a profile P: f_P(x) = OR_{w in P} AND_{e in w} x_e, with
x_e = 1 iff evidence e is present (not revoked). Interval liveness is Kleene
eval of (f_lower, f_upper) on that assignment.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Hashable, Iterable

from ocm.kso.warrant import (
    ONE,
    ZERO,
    CannotCheck,
    Liveness,
    Profile,
    WarrantProfile,
    canon,
)


@dataclass(frozen=True, slots=True)
class BDDNode:
    ident: int
    var: Hashable | None  # None for terminals
    lo: int
    hi: int
    terminal: bool
    value: bool


class ROBDD:
    """Reduced ordered BDD. Variable rank is the index in ``order``."""

    def __init__(self, order: tuple[Hashable, ...] = ()) -> None:
        self._order: list[Hashable] = list(order)
        self._rank: dict[Hashable, int] = {v: i for i, v in enumerate(self._order)}
        self._unique: dict[tuple, int] = {}
        false = BDDNode(0, None, 0, 0, True, False)
        true = BDDNode(1, None, 1, 1, True, True)
        self._by_id: list[BDDNode] = [false, true]
        self.FALSE = false
        self.TRUE = true
        self._computed: dict[tuple, int] = {}

    @property
    def node_count(self) -> int:
        return len(self._by_id)

    def ensure_var(self, evidence: Hashable) -> None:
        if evidence not in self._rank:
            self._rank[evidence] = len(self._order)
            self._order.append(evidence)

    def node(self, ident: int) -> BDDNode:
        return self._by_id[ident]

    def mk(self, var: Hashable, lo: int, hi: int) -> int:
        self.ensure_var(var)
        if lo == hi:
            return lo
        key = (var, lo, hi)
        hit = self._unique.get(key)
        if hit is not None:
            return hit
        ident = len(self._by_id)
        self._by_id.append(BDDNode(ident, var, lo, hi, False, False))
        self._unique[key] = ident
        return ident

    def var(self, evidence: Hashable) -> int:
        return self.mk(evidence, self.FALSE.ident, self.TRUE.ident)

    def _rank_of(self, ident: int) -> int:
        node = self._by_id[ident]
        if node.terminal:
            return 10**9
        return self._rank[node.var]

    def apply(self, op: Callable[[bool, bool], bool], left: int, right: int) -> int:
        key = (op.__name__, left, right)
        hit = self._computed.get(key)
        if hit is not None:
            return hit
        a = self._by_id[left]
        b = self._by_id[right]
        if a.terminal and b.terminal:
            out = self.TRUE.ident if op(a.value, b.value) else self.FALSE.ident
        else:
            ra, rb = self._rank_of(left), self._rank_of(right)
            if ra == rb:
                lo = self.apply(op, a.lo, b.lo)
                hi = self.apply(op, a.hi, b.hi)
                out = self.mk(a.var, lo, hi)
            elif ra < rb:
                lo = self.apply(op, a.lo, right)
                hi = self.apply(op, a.hi, right)
                out = self.mk(a.var, lo, hi)
            else:
                lo = self.apply(op, left, b.lo)
                hi = self.apply(op, left, b.hi)
                out = self.mk(b.var, lo, hi)
        self._computed[key] = out
        return out

    def bdd_or(self, left: int, right: int) -> int:
        a, b = self._by_id[left], self._by_id[right]
        if a.terminal:
            return right if not a.value else self.TRUE.ident
        if b.terminal:
            return left if not b.value else self.TRUE.ident
        return self.apply(_op_or, left, right)

    def bdd_and(self, left: int, right: int) -> int:
        a, b = self._by_id[left], self._by_id[right]
        if a.terminal:
            return self.FALSE.ident if not a.value else right
        if b.terminal:
            return self.FALSE.ident if not b.value else left
        return self.apply(_op_and, left, right)

    def from_profile(self, profile: Profile) -> int:
        if profile == ZERO:
            return self.FALSE.ident
        if profile == ONE:
            return self.TRUE.ident
        acc = self.FALSE.ident
        for warrant in profile:
            for evidence in warrant:
                self.ensure_var(evidence)
            term = self.TRUE.ident
            for evidence in sorted(warrant, key=lambda e: (self._rank.get(e, 10**9), type(e).__name__, repr(e))):
                term = self.bdd_and(term, self.var(evidence))
            acc = self.bdd_or(acc, term)
        return acc

    def eval(self, ident: int, present: frozenset) -> bool:
        node = self._by_id[ident]
        while not node.terminal:
            node = self._by_id[node.hi if node.var in present else node.lo]
        return node.value

    def liveness_bool(self, ident: int, revoked: Iterable[Hashable]) -> bool:
        rv = frozenset(revoked)
        present = frozenset(v for v in self._order if v not in rv)
        return self.eval(ident, present)

    def support(self, ident: int) -> frozenset:
        seen: set[Hashable] = set()
        stack = [ident]
        visited: set[int] = set()
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            node = self._by_id[cur]
            if node.terminal:
                continue
            seen.add(node.var)
            stack.append(node.lo)
            stack.append(node.hi)
        return frozenset(seen)

    def expand(self, ident: int, *, cap: int) -> Profile:
        """Minimal satisfying sets. Fail-closed if 2^|order| exceeds ``cap`` assignments."""
        n = len(self._order)
        if (1 << n) > cap:
            raise CannotCheck("CANNOT_CHECK_OUTPUT_SIZE")
        satisfying: list[frozenset] = []
        for mask in range(1 << n):
            present = frozenset(self._order[i] for i in range(n) if mask & (1 << i))
            if self.eval(ident, present):
                satisfying.append(present)
                if len(satisfying) > cap:
                    raise CannotCheck("CANNOT_CHECK_OUTPUT_SIZE")
        return canon(satisfying)


def _op_or(a: bool, b: bool) -> bool:
    return a or b


def _op_and(a: bool, b: bool) -> bool:
    return a and b


_op_or.__name__ = "or"
_op_and.__name__ = "and"


@dataclass(frozen=True)
class BDDWarrant:
    manager: ROBDD
    lower: int
    upper: int

    @staticmethod
    def from_profile(wp: WarrantProfile, manager: ROBDD | None = None) -> "BDDWarrant":
        evidence = sorted(
            {e for w in (*wp.lower, *wp.upper) for e in w},
            key=lambda e: (type(e).__name__, repr(e)),
        )
        mgr = manager or ROBDD(tuple(evidence))
        for e in evidence:
            mgr.ensure_var(e)
        return BDDWarrant(mgr, mgr.from_profile(wp.lower), mgr.from_profile(wp.upper))

    def join(self, other: "BDDWarrant") -> "BDDWarrant":
        if other.manager is not self.manager:
            raise ValueError("ROBDD manager mismatch")
        return BDDWarrant(
            self.manager,
            self.manager.bdd_or(self.lower, other.lower),
            self.manager.bdd_or(self.upper, other.upper),
        )

    def meet(self, other: "BDDWarrant") -> "BDDWarrant":
        if other.manager is not self.manager:
            raise ValueError("ROBDD manager mismatch")
        return BDDWarrant(
            self.manager,
            self.manager.bdd_and(self.lower, other.lower),
            self.manager.bdd_and(self.upper, other.upper),
        )

    def expand(self, *, cap: int = 256) -> WarrantProfile:
        return WarrantProfile(
            self.manager.expand(self.lower, cap=cap),
            self.manager.expand(self.upper, cap=cap),
        )

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        rv = frozenset(revoked)
        if self.manager.liveness_bool(self.lower, rv):
            return Liveness.LIVE
        if not self.manager.liveness_bool(self.upper, rv):
            return Liveness.DEAD
        return Liveness.UNKNOWN

    def upper_only_evidence(self) -> frozenset:
        return self.manager.support(self.upper) - self.manager.support(self.lower)

    def as_dict(self) -> dict[str, Any]:
        return {
            "lower_id": self.lower,
            "upper_id": self.upper,
            "nodes": self.manager.node_count,
            "upper_only": sorted(map(repr, self.upper_only_evidence())),
        }


def mutant_collapse_bounds(wp: WarrantProfile) -> WarrantProfile:
    return WarrantProfile(wp.upper, wp.upper)


def mutant_eval_lower_only(bw: BDDWarrant, revoked: Iterable[Hashable]) -> Liveness:
    """Planted: ignore upper; absence of exhibited support is DEAD."""
    return Liveness.LIVE if bw.manager.liveness_bool(bw.lower, revoked) else Liveness.DEAD
