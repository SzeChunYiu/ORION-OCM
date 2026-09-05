"""Cross-scale navigation (M8 §3, §5; theory batch 4 D7 / MEG-09).

    query → coarse region activation (the region quotient's gated closure from the seed's regions)
          → choose regions (those the coarse walk reaches)
          → descend only where a registered sufficiency certificate does not cover the query
            (otherwise answer from the macro: no false-no-descent allowed without a certificate)
          → local navigation inside the chosen regions (gated closure restricted to the region)
          → cross-region transport where a live, applicable TransportMap exists
          → ascend with the checked result

Outcomes: FOUND / REFINE_REQUIRED / GAP; a coarse GAP maps to REFINE_REQUIRED, never to an
obstruction, unless every level fails.  Measurements: atoms visited, regions descended, transports
used, unnecessary descents (descended but the macro would have sufficed), missed regions (target's
region not reached coarsely), against the flat baseline (gated closure over the whole space).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Hashable, Iterable, Sequence

from ocm.kso import navigation as N
from ocm.kso.space import KnowledgeSpace
from ocm.kso.warrant import Liveness

from .interface import Organisation, Region, TransportMap, macro_liveness, transport_applicable


@dataclass(frozen=True)
class CrossScaleResult:
    outcome: str                              # FOUND | REFINE_REQUIRED | GAP
    target: str
    coarse_regions: tuple[str, ...]
    descended: tuple[str, ...]
    visited: int
    transports: int
    unnecessary_descents: int
    missed_region: bool
    answered_from_macro: bool


def _region_graph(org: Organisation, ks: KnowledgeSpace) -> dict[str, set[str]]:
    """Regions are adjacent when a hyperedge crosses them (or a transport links them)."""
    regs = {r.region_id: r for r in org.regions()}
    adj: dict[str, set[str]] = {rid: set() for rid in regs}
    for e in ks.hyperedges:
        inc = list(e.incident)
        rs = {rid for a in inc for rid in org.regions_of(a)}
        for a in rs:
            for b in rs:
                if a != b:
                    adj[a].add(b)
    for t in org.transports():
        adj.setdefault(t.source, set()).add(t.target)
    return adj


def cross_scale(org: Organisation, ks: KnowledgeSpace, seed: str, target: str, *, revoked: Iterable[Hashable] = (), certified_queries: Iterable[str] = (), contexts: Iterable[str] = (), max_regions: int = 3) -> CrossScaleResult:
    rv = frozenset(revoked)
    certified = set(certified_queries)
    regs = {r.region_id: r for r in org.regions()}
    adj = _region_graph(org, ks)
    start = set(org.regions_of(seed))
    # coarse activation: breadth-first over the region graph, bounded
    coarse: list[str] = []
    frontier = list(sorted(start))
    seen = set(frontier)
    while frontier and len(coarse) < max_regions:
        rid = frontier.pop(0)
        coarse.append(rid)
        for nb in sorted(adj.get(rid, ())):
            if nb not in seen:
                seen.add(nb)
                frontier.append(nb)
    target_regions = set(org.regions_of(target))
    missed = not (target_regions & set(coarse))
    visited = 0
    descended: list[str] = []
    transports = 0
    unnecessary = 0
    answered_macro = False
    for rid in coarse:
        macro = org.macro(rid)
        q = f"{rid}:{target}"
        if q in certified and macro_liveness(ks, macro, rv) is Liveness.LIVE and target in macro.exported_claims:
            answered_macro = True
            return CrossScaleResult("FOUND", target, tuple(coarse), tuple(descended), visited + 1, transports, unnecessary, missed, True)
        # descend: local gated closure restricted to the region
        local = N.gated_closure(ks, [a for a in regs[rid].atoms if a == seed or a in _entry_points(ks, regs[rid], coarse, org)], rv) & regs[rid].atoms
        visited += len(local)
        descended.append(rid)
        if q in certified and target in macro.exported_claims:
            unnecessary += 1
        if target in local and ks.atom(target).liveness(rv) is Liveness.LIVE:
            return CrossScaleResult("FOUND", target, tuple(coarse), tuple(descended), visited, transports, unnecessary, missed, False)
        # transport out of this region if a live applicable map exists
        for t in org.transports():
            if t.source == rid and transport_applicable(t, contexts) and t.warrant.liveness(rv) is Liveness.LIVE:
                transports += 1
                if target in t.mapping.values():
                    return CrossScaleResult("FOUND", target, tuple(coarse), tuple(descended), visited + 1, transports, unnecessary, missed, False)
    if missed:
        return CrossScaleResult("REFINE_REQUIRED", target, tuple(coarse), tuple(descended), visited, transports, unnecessary, missed, False)
    return CrossScaleResult("GAP", target, tuple(coarse), tuple(descended), visited, transports, unnecessary, missed, False)


def _entry_points(ks: KnowledgeSpace, region: Region, coarse: Sequence[str], org: Organisation) -> set[str]:
    """Atoms of the region that receive an edge from an already-activated region (or the seed)."""
    entries: set[str] = set()
    for e in ks.hyperedges:
        heads = set(e.heads) & region.atoms
        if not heads:
            continue
        if any(rid in coarse for a in e.tails for rid in org.regions_of(a)):
            entries |= heads
    return entries


def flat(ks: KnowledgeSpace, seed: str, target: str, *, revoked: Iterable[Hashable] = ()) -> dict[str, Any]:
    rv = frozenset(revoked)
    reach = N.gated_closure(ks, [seed], rv)
    found = target in reach and ks.atom(target).liveness(rv) is Liveness.LIVE
    return {"outcome": "FOUND" if found else "GAP", "visited": len(reach)}


def mutant_summary_answers_outside_scope(org: Organisation, ks: KnowledgeSpace, rid: str, target: str, revoked: Iterable[Hashable]) -> str:
    """Planted (M8 §15 'summary answers a query outside registered sufficiency scope')."""
    macro = org.macro(rid)
    return "FOUND" if target in macro.exported_claims else "GAP"
