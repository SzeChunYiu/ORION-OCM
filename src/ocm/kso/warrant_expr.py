"""Experimental factored warrant expressions for issue #115 FK-5.

The production warrant authority remains :mod:`ocm.kso.warrant`.  This module is
an additive reference/prototype that represents the same monotone support
functions as shared Boolean-expression DAGs so joins/meets need not immediately
enumerate every minimal sufficient support set.

The structural normal form implemented here is deterministic under
associativity/commutativity/idempotence and Boolean constants.  It is *not* a
canonical representation of arbitrary Boolean functions (no BDD/ZDD/d-DNNF
claim).  Scientific or production adoption requires the exact finite oracle and
resource studies registered in #115/#70.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Hashable, Iterable

from .warrant import Liveness, Profile, WarrantProfile

FALSE_KIND = "FALSE"
TRUE_KIND = "TRUE"
EVIDENCE_KIND = "EVIDENCE"
OR_KIND = "OR"
AND_KIND = "AND"


def _evidence_key(value: Hashable) -> tuple[str, str]:
    return type(value).__name__, repr(value)


@dataclass(frozen=True, slots=True)
class SupportExpr:
    """One immutable node in a monotone support-expression DAG."""

    kind: str
    evidence: Hashable | None = None
    children: tuple["SupportExpr", ...] = ()

    def __post_init__(self) -> None:
        if self.kind in (FALSE_KIND, TRUE_KIND):
            if self.evidence is not None or self.children:
                raise ValueError(f"{self.kind} cannot carry evidence or children")
        elif self.kind == EVIDENCE_KIND:
            if self.evidence is None or self.children:
                raise ValueError("EVIDENCE requires one evidence identity and no children")
            hash(self.evidence)
        elif self.kind in (OR_KIND, AND_KIND):
            if self.evidence is not None or len(self.children) < 2:
                raise ValueError(f"{self.kind} requires at least two children")
        else:
            raise ValueError(f"unknown support-expression kind: {self.kind}")

    def evaluate(self, revoked: Iterable[Hashable] = ()) -> bool:
        rv = revoked if isinstance(revoked, frozenset) else frozenset(revoked)
        return _evaluate(self, rv)

    @property
    def evidence_ids(self) -> frozenset[Hashable]:
        return frozenset(node.evidence for node in iter_nodes(self) if node.kind == EVIDENCE_KIND)

    @property
    def node_count(self) -> int:
        return sum(1 for _ in iter_nodes(self))


FALSE = SupportExpr(FALSE_KIND)
TRUE = SupportExpr(TRUE_KIND)


@lru_cache(maxsize=None)
def evidence_leaf(evidence: Hashable) -> SupportExpr:
    """Intern one evidence-survival leaf."""

    hash(evidence)
    return SupportExpr(EVIDENCE_KIND, evidence=evidence)


def _expr_key(expr: SupportExpr):
    order = {FALSE_KIND: 0, TRUE_KIND: 1, EVIDENCE_KIND: 2, AND_KIND: 3, OR_KIND: 4}
    if expr.kind == EVIDENCE_KIND:
        return order[expr.kind], _evidence_key(expr.evidence)
    return order[expr.kind], tuple(_expr_key(child) for child in expr.children)


@lru_cache(maxsize=None)
def _compound(kind: str, children: tuple[SupportExpr, ...]) -> SupportExpr:
    return SupportExpr(kind, children=children)


def _normalize(kind: str, expressions: Iterable[SupportExpr]) -> SupportExpr:
    if kind not in (OR_KIND, AND_KIND):
        raise ValueError("compound kind must be OR or AND")

    identity = FALSE if kind == OR_KIND else TRUE
    absorber = TRUE if kind == OR_KIND else FALSE
    flattened: list[SupportExpr] = []
    for expr in expressions:
        if expr == absorber:
            return absorber
        if expr == identity:
            continue
        if expr.kind == kind:
            flattened.extend(expr.children)
        else:
            flattened.append(expr)

    if not flattened:
        return identity
    unique = tuple(sorted(set(flattened), key=_expr_key))
    if len(unique) == 1:
        return unique[0]
    return _compound(kind, unique)


def any_of(*expressions: SupportExpr) -> SupportExpr:
    """Alternative support (Boolean OR / warrant semiring join)."""

    return _normalize(OR_KIND, expressions)


def all_of(*expressions: SupportExpr) -> SupportExpr:
    """Conjunctive support (Boolean AND / warrant semiring meet)."""

    return _normalize(AND_KIND, expressions)


def _evaluate(expr: SupportExpr, revoked: frozenset[Hashable]) -> bool:
    if expr.kind == FALSE_KIND:
        return False
    if expr.kind == TRUE_KIND:
        return True
    if expr.kind == EVIDENCE_KIND:
        return expr.evidence not in revoked
    if expr.kind == OR_KIND:
        return any(_evaluate(child, revoked) for child in expr.children)
    return all(_evaluate(child, revoked) for child in expr.children)


def iter_nodes(root: SupportExpr):
    """Yield each structurally shared node once."""

    seen: set[SupportExpr] = set()
    stack = [root]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        yield node
        stack.extend(node.children)


def from_profile(profile: Profile) -> SupportExpr:
    """Compile an explicit antichain profile into a monotone support DAG."""

    alternatives = []
    for warrant in profile:
        alternatives.append(all_of(*(evidence_leaf(evidence) for evidence in warrant)))
    return any_of(*alternatives)


@dataclass(frozen=True, slots=True)
class CompiledWarrantInterval:
    """Factored lower/upper support functions with production-equivalent liveness."""

    lower: SupportExpr
    upper: SupportExpr

    @staticmethod
    def from_warrant_profile(profile: WarrantProfile) -> "CompiledWarrantInterval":
        return CompiledWarrantInterval(from_profile(profile.lower), from_profile(profile.upper))

    @property
    def lower_evidence(self) -> frozenset[Hashable]:
        return self.lower.evidence_ids

    @property
    def upper_evidence(self) -> frozenset[Hashable]:
        return self.upper.evidence_ids

    @property
    def all_evidence(self) -> frozenset[Hashable]:
        """Every evidence identity that can affect interval liveness.

        Reverse dependency indexes for an interval must include the upper bound as
        well as the exhibited lower bound; otherwise an UNKNOWN -> DEAD transition
        can be missed when upper-only support is revoked.
        """

        return self.lower_evidence | self.upper_evidence

    def liveness(self, revoked: Iterable[Hashable] = ()) -> Liveness:
        rv = revoked if isinstance(revoked, frozenset) else frozenset(revoked)
        if _evaluate(self.lower, rv):
            return Liveness.LIVE
        if not _evaluate(self.upper, rv):
            return Liveness.DEAD
        return Liveness.UNKNOWN

    def join(self, other: "CompiledWarrantInterval") -> "CompiledWarrantInterval":
        return CompiledWarrantInterval(any_of(self.lower, other.lower), any_of(self.upper, other.upper))

    def meet(self, other: "CompiledWarrantInterval") -> "CompiledWarrantInterval":
        return CompiledWarrantInterval(all_of(self.lower, other.lower), all_of(self.upper, other.upper))

    @property
    def node_count(self) -> int:
        """Unique nodes across both bounds, counting structurally shared nodes once."""

        return len(set(iter_nodes(self.lower)) | set(iter_nodes(self.upper)))
