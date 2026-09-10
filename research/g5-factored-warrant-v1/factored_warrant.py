"""G5.3 factored warrant parent — hash-consed support DAGs with exact antichain parity.

Research-only. Production ``ocm.kso.warrant`` remains the antichain oracle.
Lower and upper bounds are distinct DAG roots. Enumeration is capped; overflow
is ``CANNOT_CHECK_OUTPUT_SIZE``, not an approximation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Hashable, Iterable

from ocm.kso.warrant import (
    ONE,
    ZERO,
    CannotCheck,
    Liveness,
    Profile,
    WarrantProfile,
    canon,
    join as antichain_join,
    live,
    meet as antichain_meet,
)


class Kind(str, Enum):
    ZERO = "ZERO"
    ONE = "ONE"
    LEAF = "LEAF"
    JOIN = "JOIN"
    MEET = "MEET"


@dataclass(frozen=True, slots=True)
class Node:
    kind: Kind
    payload: tuple
    ident: int

    def as_key(self) -> tuple:
        return (self.kind.value, self.payload)


class SupportDAG:
    """Hash-consed ⊕/⊗ DAG over evidence leaves."""

    def __init__(self) -> None:
        self._nodes: dict[tuple, Node] = {}
        self._by_id: list[Node] = []
        self.zero = self._cons(Kind.ZERO, ())
        self.one = self._cons(Kind.ONE, ())

    def _cons(self, kind: Kind, payload: tuple) -> Node:
        key = (kind.value, payload)
        hit = self._nodes.get(key)
        if hit is not None:
            return hit
        node = Node(kind, payload, len(self._by_id))
        self._nodes[key] = node
        self._by_id.append(node)
        return node

    @property
    def node_count(self) -> int:
        return len(self._by_id)

    def leaf(self, evidence: Hashable) -> Node:
        return self._cons(Kind.LEAF, (evidence,))

    def join(self, left: Node, right: Node) -> Node:
        if left.kind is Kind.ZERO:
            return right
        if right.kind is Kind.ZERO:
            return left
        if left.kind is Kind.ONE or right.kind is Kind.ONE:
            return self.one
        if left.ident == right.ident:
            return left
        a, b = (left, right) if left.ident <= right.ident else (right, left)
        return self._cons(Kind.JOIN, (a.ident, b.ident))

    def meet(self, left: Node, right: Node) -> Node:
        if left.kind is Kind.ONE:
            return right
        if right.kind is Kind.ONE:
            return left
        if left.kind is Kind.ZERO or right.kind is Kind.ZERO:
            return self.zero
        if left.ident == right.ident:
            return left
        a, b = (left, right) if left.ident <= right.ident else (right, left)
        return self._cons(Kind.MEET, (a.ident, b.ident))

    def from_profile(self, profile: Profile) -> Node:
        if profile == ZERO:
            return self.zero
        if profile == ONE:
            return self.one
        acc = self.zero
        for warrant in profile:
            term = self.one
            for evidence in sorted(warrant, key=lambda e: (type(e).__name__, repr(e))):
                term = self.meet(term, self.leaf(evidence))
            acc = self.join(acc, term)
        return acc

    def expand(self, node: Node, *, cap: int) -> Profile:
        """Expand to an antichain. Exceeding ``cap`` warrants is fail-closed."""
        table: dict[int, Profile] = {}

        def rec(cur: Node) -> Profile:
            if cur.ident in table:
                return table[cur.ident]
            if cur.kind is Kind.ZERO:
                out = ZERO
            elif cur.kind is Kind.ONE:
                out = ONE
            elif cur.kind is Kind.LEAF:
                out = (frozenset({cur.payload[0]}),)
            elif cur.kind is Kind.JOIN:
                left = rec(self._by_id[cur.payload[0]])
                right = rec(self._by_id[cur.payload[1]])
                out = antichain_join(left, right)
            else:
                left = rec(self._by_id[cur.payload[0]])
                right = rec(self._by_id[cur.payload[1]])
                out = antichain_meet(left, right)
            if len(out) > cap:
                raise CannotCheck("CANNOT_CHECK_OUTPUT_SIZE")
            table[cur.ident] = out
            return out

        return rec(node)

    def liveness(self, node: Node, revoked: Iterable[Hashable]) -> Liveness:
        rv = frozenset(revoked)
        memo: dict[int, Liveness] = {}

        def rec(cur: Node) -> Liveness:
            if cur.ident in memo:
                return memo[cur.ident]
            if cur.kind is Kind.ZERO:
                out = Liveness.DEAD
            elif cur.kind is Kind.ONE:
                out = Liveness.LIVE
            elif cur.kind is Kind.LEAF:
                out = Liveness.DEAD if cur.payload[0] in rv else Liveness.LIVE
            elif cur.kind is Kind.JOIN:
                a = rec(self._by_id[cur.payload[0]])
                b = rec(self._by_id[cur.payload[1]])
                if a is Liveness.LIVE or b is Liveness.LIVE:
                    out = Liveness.LIVE
                elif a is Liveness.DEAD and b is Liveness.DEAD:
                    out = Liveness.DEAD
                else:
                    out = Liveness.UNKNOWN
            else:
                a = rec(self._by_id[cur.payload[0]])
                b = rec(self._by_id[cur.payload[1]])
                if a is Liveness.DEAD or b is Liveness.DEAD:
                    out = Liveness.DEAD
                elif a is Liveness.LIVE and b is Liveness.LIVE:
                    out = Liveness.LIVE
                else:
                    out = Liveness.UNKNOWN
            memo[cur.ident] = out
            return out

        return rec(node)

    def evidence(self, node: Node) -> frozenset:
        seen: set[Hashable] = set()
        stack = [node]
        visited: set[int] = set()
        while stack:
            cur = stack.pop()
            if cur.ident in visited:
                continue
            visited.add(cur.ident)
            if cur.kind is Kind.LEAF:
                seen.add(cur.payload[0])
            elif cur.kind in (Kind.JOIN, Kind.MEET):
                stack.append(self._by_id[cur.payload[0]])
                stack.append(self._by_id[cur.payload[1]])
        return frozenset(seen)


@dataclass(frozen=True)
class FactoredWarrant:
    dag: SupportDAG
    lower: Node
    upper: Node

    @staticmethod
    def from_profile(wp: WarrantProfile, dag: SupportDAG | None = None) -> "FactoredWarrant":
        dag = dag or SupportDAG()
        return FactoredWarrant(dag, dag.from_profile(wp.lower), dag.from_profile(wp.upper))

    def join(self, other: "FactoredWarrant") -> "FactoredWarrant":
        if other.dag is not self.dag:
            raise ValueError("DAG mismatch")
        return FactoredWarrant(
            self.dag,
            self.dag.join(self.lower, other.lower),
            self.dag.join(self.upper, other.upper),
        )

    def meet(self, other: "FactoredWarrant") -> "FactoredWarrant":
        if other.dag is not self.dag:
            raise ValueError("DAG mismatch")
        return FactoredWarrant(
            self.dag,
            self.dag.meet(self.lower, other.lower),
            self.dag.meet(self.upper, other.upper),
        )

    def expand(self, *, cap: int = 256) -> WarrantProfile:
        return WarrantProfile(self.dag.expand(self.lower, cap=cap), self.dag.expand(self.upper, cap=cap))

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        lo = self.dag.liveness(self.lower, revoked)
        if lo is Liveness.LIVE:
            return Liveness.LIVE
        up = self.dag.liveness(self.upper, revoked)
        if up is Liveness.DEAD:
            return Liveness.DEAD
        return Liveness.UNKNOWN

    def upper_only_evidence(self) -> frozenset:
        return self.dag.evidence(self.upper) - self.dag.evidence(self.lower)

    def as_dict(self) -> dict[str, Any]:
        return {
            "lower_id": self.lower.ident,
            "upper_id": self.upper.ident,
            "nodes": self.dag.node_count,
            "upper_only": sorted(map(repr, self.upper_only_evidence())),
        }


def mutant_collapse_bounds(wp: WarrantProfile) -> WarrantProfile:
    """Planted: feed upper into both bounds — treats possible support as exhibited."""
    return WarrantProfile(wp.upper, wp.upper)


def mutant_upper_only_as_live(wp: WarrantProfile, revoked: Iterable[Hashable]) -> bool:
    """Planted: any surviving upper-only evidence counts as LIVE exhibited support."""
    rv = frozenset(revoked)
    upper_only = frozenset(e for w in wp.upper for e in w) - frozenset(e for w in wp.lower for e in w)
    return any(e not in rv for e in upper_only)


def antichain_size(profile: Profile) -> int:
    return len(profile)
