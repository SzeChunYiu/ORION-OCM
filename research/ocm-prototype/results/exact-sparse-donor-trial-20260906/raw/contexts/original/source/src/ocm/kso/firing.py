"""Execution is not navigation (contract §4): Petri-style conjunctive enabling.

An executable hyperedge may fire only when the edge and every required tail are LIVE, in scope,
and sufficiently activated.  KS-T02: revoking any required tail (or the edge) disables firing for
every activation vector.  With three-valued liveness the enabling verdict is itself three-valued:
ENABLED / DISABLED / UNKNOWN (some tail UNKNOWN, none DEAD).  Parent: Petri nets (Reisig).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Hashable, Iterable, Mapping

from .space import Hyperedge, KnowledgeSpace
from .warrant import Liveness, kleene_and


class Enabling(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class EnablingVerdict:
    edge_id: str
    enabling: Enabling
    reason: str


def enabling_verdict(
    ks: KnowledgeSpace,
    edge: Hyperedge,
    activation: Mapping[str, Fraction],
    threshold: Fraction,
    revoked: Iterable[Hashable] = (),
    *,
    context: str | None = None,
) -> EnablingVerdict:
    rv = frozenset(revoked)
    amap = ks.atom_map()
    liveness = edge.liveness(rv)
    for t in edge.tails:
        liveness = kleene_and(liveness, amap[t].liveness(rv))
    if liveness is Liveness.DEAD:
        return EnablingVerdict(edge.edge_id, Enabling.DISABLED, "REQUIRED_TAIL_OR_EDGE_DEAD")
    if context is not None:
        if not edge.scope.covers(context) or any(not amap[t].scope.covers(context) for t in edge.tails):
            return EnablingVerdict(edge.edge_id, Enabling.DISABLED, "OUT_OF_SCOPE")
    if any(activation.get(t, Fraction(0, 1)) < threshold for t in edge.tails):
        return EnablingVerdict(edge.edge_id, Enabling.DISABLED, "TAIL_BELOW_ACTIVATION_THRESHOLD")
    if liveness is Liveness.UNKNOWN:
        return EnablingVerdict(edge.edge_id, Enabling.UNKNOWN, "REQUIRED_TAIL_OR_EDGE_WARRANT_UNKNOWN")
    return EnablingVerdict(edge.edge_id, Enabling.ENABLED, "ALL_TAILS_LIVE_AND_ACTIVE")


def enabled_hyperedges(
    ks: KnowledgeSpace,
    activation: Mapping[str, Fraction],
    threshold: Fraction,
    revoked: Iterable[Hashable] = (),
    *,
    context: str | None = None,
) -> tuple[str, ...]:
    """Edge ids that are ENABLED (two-valued view; UNKNOWN is *not* enabled)."""
    out = [
        e.edge_id
        for e in ks.hyperedges
        if enabling_verdict(ks, e, activation, threshold, revoked, context=context).enabling is Enabling.ENABLED
    ]
    return tuple(sorted(out))


def mutant_enable_ignores_tail_warrant(
    ks: KnowledgeSpace, activation: Mapping[str, Fraction], threshold: Fraction, revoked: Iterable[Hashable] = ()
) -> tuple[str, ...]:
    """Planted: enabling that checks activation but not the tails' warrant (navigation-as-truth)."""
    rv = frozenset(revoked)
    return tuple(sorted(e.edge_id for e in ks.hyperedges if e.warrant.is_live(rv) and all(activation.get(t, Fraction(0, 1)) >= threshold for t in e.tails)))
