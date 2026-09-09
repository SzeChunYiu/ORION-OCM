"""G5.3 research ZDD parent for warrant intervals.

Independent Minato zero-suppressed decision diagram (unique table + apply).
Suppresses nodes whose hi-edge is the 0-terminal. Stdlib only — no ``dd`` /
CUDD / pyeda. Production ``ocm.kso.warrant`` stays the antichain oracle.

A profile is stored as the combinatorial family of its warrants (not the
Boolean onset of all supersets). Interval liveness is: some family member is
disjoint from the revocation set. Join is family union (ZDD OR); meet is the
family product {a ∪ b} (Minato join). Expand returns the antichain of members.
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
class ZDDNode:
    ident: int
    var: Hashable | None  # None for terminals
    lo: int
    hi: int
    terminal: bool
    value: bool


class ZDD:
    """Zero-suppressed BDD. Variable rank is the index in ``order``."""

    def __init__(self, order: tuple[Hashable, ...] = ()) -> None:
        self._order: list[Hashable] = list(order)
        self._rank: dict[Hashable, int] = {v: i for i, v in enumerate(self._order)}
        self._unique: dict[tuple, int] = {}
        false = ZDDNode(0, None, 0, 0, True, False)
        true = ZDDNode(1, None, 1, 1, True, True)
        self._by_id: list[ZDDNode] = [false, true]
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

    def node(self, ident: int) -> ZDDNode:
        return self._by_id[ident]

    def mk(self, var: Hashable, lo: int, hi: int) -> int:
        """Zero-suppression: a node whose hi-edge is 0-terminal is dropped."""
        self.ensure_var(var)
        if hi == self.FALSE.ident:
            return lo
        key = (var, lo, hi)
        hit = self._unique.get(key)
        if hit is not None:
            return hit
        ident = len(self._by_id)
        self._by_id.append(ZDDNode(ident, var, lo, hi, False, False))
        self._unique[key] = ident
        return ident

    def var(self, evidence: Hashable) -> int:
        """Family {{evidence}}."""
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
                # ``right`` has no node for a.var ⇒ that variable is 0 in
                # every combination of ``right``. Hi-cofactor is the empty family.
                lo = self.apply(op, a.lo, right)
                hi = self.apply(op, a.hi, self.FALSE.ident)
                out = self.mk(a.var, lo, hi)
            else:
                lo = self.apply(op, left, b.lo)
                hi = self.apply(op, self.FALSE.ident, b.hi)
                out = self.mk(b.var, lo, hi)
        self._computed[key] = out
        return out

    def zdd_or(self, left: int, right: int) -> int:
        a, b = self._by_id[left], self._by_id[right]
        if left == right:
            return left
        if a.terminal and not a.value:
            return right
        if b.terminal and not b.value:
            return left
        return self.apply(_op_or, left, right)

    def zdd_and(self, left: int, right: int) -> int:
        a, b = self._by_id[left], self._by_id[right]
        if left == right:
            return left
        if (a.terminal and not a.value) or (b.terminal and not b.value):
            return self.FALSE.ident
        return self.apply(_op_and, left, right)

    def zdd_xor(self, left: int, right: int) -> int:
        a, b = self._by_id[left], self._by_id[right]
        if left == right:
            return self.FALSE.ident
        if a.terminal and not a.value:
            return right
        if b.terminal and not b.value:
            return left
        return self.apply(_op_xor, left, right)

    def product(self, left: int, right: int) -> int:
        """Minato join: {α ∪ β | α ∈ left, β ∈ right}. Warrant meet."""
        key = ("product", left, right)
        hit = self._computed.get(key)
        if hit is not None:
            return hit
        a = self._by_id[left]
        b = self._by_id[right]
        if (a.terminal and not a.value) or (b.terminal and not b.value):
            out = self.FALSE.ident
        elif a.terminal and a.value:
            out = right
        elif b.terminal and b.value:
            out = left
        else:
            ra, rb = self._rank_of(left), self._rank_of(right)
            if ra == rb:
                lo = self.product(a.lo, b.lo)
                hi = self.zdd_or(
                    self.product(a.lo, b.hi),
                    self.zdd_or(self.product(a.hi, b.lo), self.product(a.hi, b.hi)),
                )
                out = self.mk(a.var, lo, hi)
            elif ra < rb:
                out = self.mk(a.var, self.product(a.lo, right), self.product(a.hi, right))
            else:
                out = self.mk(b.var, self.product(left, b.lo), self.product(left, b.hi))
        self._computed[key] = out
        return out

    def change(self, ident: int, evidence: Hashable) -> int:
        """Add ``evidence`` to every combination in the family."""
        self.ensure_var(evidence)
        key = ("change", ident, evidence)
        hit = self._computed.get(key)
        if hit is not None:
            return hit
        node = self._by_id[ident]
        rv = self._rank[evidence]
        if node.terminal:
            out = self.mk(evidence, self.FALSE.ident, ident) if node.value else self.FALSE.ident
        else:
            rf = self._rank[node.var]
            if rf == rv:
                out = self.mk(evidence, self.FALSE.ident, self.zdd_or(node.lo, node.hi))
            elif rv < rf:
                out = self.mk(evidence, self.FALSE.ident, ident)
            else:
                out = self.mk(
                    node.var,
                    self.change(node.lo, evidence),
                    self.change(node.hi, evidence),
                )
        self._computed[key] = out
        return out

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
            for evidence in sorted(
                warrant,
                key=lambda e: (self._rank.get(e, 10**9), type(e).__name__, repr(e)),
            ):
                term = self.change(term, evidence)
            acc = self.zdd_or(acc, term)
        return acc

    def contains(self, ident: int, combination: frozenset) -> bool:
        """True iff ``combination`` is an exact member of the family.

        Skipped variables are 0 under ZDD semantics, so extra members of
        ``combination`` that jump a suppressed node are rejected.
        """
        node = self._by_id[ident]
        last_rank = -1
        while not node.terminal:
            r = self._rank[node.var]
            for i in range(last_rank + 1, r):
                if self._order[i] in combination:
                    return False
            last_rank = r
            node = self._by_id[node.hi if node.var in combination else node.lo]
        for i in range(last_rank + 1, len(self._order)):
            if self._order[i] in combination:
                return False
        return node.value

    def some_subset_of(self, ident: int, present: frozenset) -> bool:
        """True iff some combination in the family is ⊆ ``present``."""
        memo: dict[int, bool] = {}

        def rec(cur: int) -> bool:
            hit = memo.get(cur)
            if hit is not None:
                return hit
            node = self._by_id[cur]
            if node.terminal:
                out = node.value
            elif node.var not in present:
                out = rec(node.lo)
            else:
                out = rec(node.lo) or rec(node.hi)
            memo[cur] = out
            return out

        return rec(ident)

    def liveness_bool(self, ident: int, revoked: Iterable[Hashable]) -> bool:
        rv = frozenset(revoked)
        present = frozenset(v for v in self._order if v not in rv)
        return self.some_subset_of(ident, present)

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
        """Enumerate family members. Fail-closed if output exceeds ``cap``."""
        satisfying: list[frozenset] = []

        def rec(cur: int, chosen: list[Hashable]) -> None:
            if len(satisfying) > cap:
                raise CannotCheck("CANNOT_CHECK_OUTPUT_SIZE")
            node = self._by_id[cur]
            if node.terminal:
                if node.value:
                    satisfying.append(frozenset(chosen))
                return
            rec(node.lo, chosen)
            chosen.append(node.var)
            rec(node.hi, chosen)
            chosen.pop()

        rec(ident, [])
        if len(satisfying) > cap:
            raise CannotCheck("CANNOT_CHECK_OUTPUT_SIZE")
        return canon(satisfying)


def _op_or(a: bool, b: bool) -> bool:
    return a or b


def _op_and(a: bool, b: bool) -> bool:
    return a and b


def _op_xor(a: bool, b: bool) -> bool:
    return a != b


_op_or.__name__ = "or"
_op_and.__name__ = "and"
_op_xor.__name__ = "xor"


@dataclass(frozen=True)
class ZDDWarrant:
    manager: ZDD
    lower: int
    upper: int

    @staticmethod
    def from_profile(wp: WarrantProfile, manager: ZDD | None = None) -> "ZDDWarrant":
        evidence = sorted(
            {e for w in (*wp.lower, *wp.upper) for e in w},
            key=lambda e: (type(e).__name__, repr(e)),
        )
        mgr = manager or ZDD(tuple(evidence))
        for e in evidence:
            mgr.ensure_var(e)
        return ZDDWarrant(mgr, mgr.from_profile(wp.lower), mgr.from_profile(wp.upper))

    def join(self, other: "ZDDWarrant") -> "ZDDWarrant":
        if other.manager is not self.manager:
            raise ValueError("ZDD manager mismatch")
        return ZDDWarrant(
            self.manager,
            self.manager.zdd_or(self.lower, other.lower),
            self.manager.zdd_or(self.upper, other.upper),
        )

    def meet(self, other: "ZDDWarrant") -> "ZDDWarrant":
        if other.manager is not self.manager:
            raise ValueError("ZDD manager mismatch")
        return ZDDWarrant(
            self.manager,
            self.manager.product(self.lower, other.lower),
            self.manager.product(self.upper, other.upper),
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


def mutant_eval_lower_only(zw: ZDDWarrant, revoked: Iterable[Hashable]) -> Liveness:
    """Planted: ignore upper; absence of exhibited support is DEAD."""
    return Liveness.LIVE if zw.manager.liveness_bool(zw.lower, revoked) else Liveness.DEAD


def mutant_join_as_xor(left: ZDDWarrant, right: ZDDWarrant) -> ZDDWarrant:
    """Planted: family symmetric difference is not warrant ⊕."""
    if right.manager is not left.manager:
        raise ValueError("ZDD manager mismatch")
    return ZDDWarrant(
        left.manager,
        left.manager.zdd_xor(left.lower, right.lower),
        left.manager.zdd_xor(left.upper, right.upper),
    )
