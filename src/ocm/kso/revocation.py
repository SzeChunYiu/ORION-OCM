"""Revocation, pruning equivalence, the impact cone and the reopening report (contract §5, §13).

* ``prune`` removes every non-LIVE atom/edge but keeps the original structural denominators;
  KS-T04 (matrix level) and KS-T04c (fixed-point and reacting-subgraph level) say the gated space
  and the pruned space navigate identically.
* ``impact_cone`` is the least dependency-closed superset of a changed set (KS-T09).
* ``reopening_report`` (KS-T22) splits the cone after a revocation delta into atoms whose liveness
  changed (REOPEN), cone members that stay LIVE through an alternative warrant (RECHECK, no forced
  reopening) and everything outside the cone (UNAFFECTED — the no-alarm control).  Activation
  outside ``Reach(dead)`` is exactly unchanged (KS-T04b (ii)).
Parents: dependency-directed backtracking / JTMS (Doyle 1979), ATMS label update (de Kleer 1986),
incremental / self-adjusting computation (Acar 2005).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Hashable, Iterable, Sequence

from .navigation import NavigationMatrix, NavigationMode, fixed_point, navigation_matrix, structural_denominators
from .space import Hyperedge, KnowledgeSpace
from .warrant import Liveness


@dataclass(frozen=True)
class PrunedSpace:
    """A knowledge space with the non-live structure removed and the original structural
    denominators **and** original head shares γ_h retained.

    An edge survives iff the edge and every tail are LIVE; a dead head is dropped from the edge
    but its share of γ_h is *not* redistributed to the surviving heads (it dissipates, exactly as
    the gated matrix dissipates it).  Renormalising the surviving heads would be the KS-T04 defect
    at the head level."""

    space: KnowledgeSpace
    denominators: dict[str, Fraction]
    head_shares: dict[str, dict[str, Fraction]]
    removed_atoms: frozenset[str]
    removed_edges: frozenset[str]


def prune(ks: KnowledgeSpace, revoked: Iterable[Hashable] = (), *, relevance=None) -> PrunedSpace:
    rv = frozenset(revoked)
    amap = ks.atom_map()
    non_live = frozenset(a.atom_id for a in ks.atoms if not a.is_live(rv))
    denominators = structural_denominators(ks, relevance)
    kept_atoms = tuple(a for a in ks.atoms if a.atom_id not in non_live)
    kept_edges = []
    head_shares: dict[str, dict[str, Fraction]] = {}
    removed_edges: set[str] = set()
    for e in ks.hyperedges:
        if not e.warrant.is_live(rv) or any(t in non_live for t in e.tails):
            removed_edges.add(e.edge_id)
            continue
        shares = {h: hw for h, hw in zip(e.heads, e.normalized_head_weights(), strict=True) if h not in non_live}
        if not shares:
            removed_edges.add(e.edge_id)
            continue
        kept_edges.append(replace(e, heads=tuple(shares), head_weights=()))
        head_shares[e.edge_id] = shares
    pruned = replace(ks, atoms=kept_atoms, hyperedges=tuple(kept_edges))
    return PrunedSpace(pruned, denominators, head_shares, non_live, frozenset(removed_edges))


def navigation_matrix_on_pruned(p: PrunedSpace, *, relevance=None) -> NavigationMatrix:
    """Navigate the pruned space with the **original** denominators and head shares (KS-T04 RHS)."""
    ks = p.space
    ids = ks.ids
    idx = {x: i for i, x in enumerate(ids)}
    from .navigation import _beta

    out = [[Fraction(0, 1) for _ in ids] for _ in ids]
    for e in ks.hyperedges:
        m = e.weight * _beta(relevance, e.relation_type)
        shares = p.head_shares[e.edge_id]
        for tail in e.tails:
            d = p.denominators[tail]
            if d == 0:
                continue
            for head, hw in shares.items():
                out[idx[tail]][idx[head]] += (m / d) * hw
    return NavigationMatrix(ids, tuple(tuple(r) for r in out), tuple(p.denominators[x] for x in ids), NavigationMode.WARRANTED, frozenset())


def mutant_prune_renormalize_heads(p: PrunedSpace) -> NavigationMatrix:
    """Planted head-level defect: surviving heads absorb the dead head's share."""
    ks = p.space
    ids = ks.ids
    idx = {x: i for i, x in enumerate(ids)}
    out = [[Fraction(0, 1) for _ in ids] for _ in ids]
    for e in ks.hyperedges:
        for tail in e.tails:
            d = p.denominators[tail]
            if d == 0:
                continue
            for head, hw in zip(e.heads, e.normalized_head_weights(), strict=True):  # renormalised!
                out[idx[tail]][idx[head]] += (e.weight / d) * hw
    return NavigationMatrix(ids, tuple(tuple(r) for r in out), tuple(p.denominators[x] for x in ids), NavigationMode.WARRANTED, frozenset())


def prune_equivalence(ks: KnowledgeSpace, revoked: Iterable[Hashable], seed: Sequence[Fraction], alpha: Fraction, *, relevance=None) -> dict[str, bool]:
    """KS-T04 + KS-T04c: gated navigation on K equals ungated navigation on Prune_R(K) with the
    original denominators — at the matrix level and at the fixed point (restricted to survivors)."""
    rv = frozenset(revoked)
    gated = navigation_matrix(ks, revoked=rv, relevance=relevance)
    p = prune(ks, rv, relevance=relevance)
    pruned = navigation_matrix_on_pruned(p, relevance=relevance)
    live_ids = p.space.ids
    gi = {x: gated.index(x) for x in live_ids}
    matrix_equal = all(
        gated.rows[gi[u]][gi[v]] == pruned.rows[pruned.index(u)][pruned.index(v)] for u in live_ids for v in live_ids
    ) and all(gated.rows[gated.index(u)][j] == 0 for u in p.removed_atoms for j in range(len(ks.ids)))
    a_gated = fixed_point(ks, seed, alpha, revoked=rv, relevance=relevance)
    seed_pruned = [seed[ks.ids.index(x)] for x in live_ids]
    from .navigation import restart_fixed_point_exact

    a_pruned = dict(zip(live_ids, restart_fixed_point_exact(pruned.as_lists(), seed_pruned, alpha), strict=True))
    fixed_equal = all(a_gated[x] == a_pruned[x] for x in live_ids) and all(a_gated[x] == 0 for x in p.removed_atoms)
    return {"matrix_equal": matrix_equal, "fixed_point_equal": fixed_equal}


# --------------------------------------------------------------------------------------------
# impact cone and reopening
# --------------------------------------------------------------------------------------------


def impact_cone(ks: KnowledgeSpace, changed: Iterable[str], dependency_types: Iterable[str] | None = None) -> frozenset[str]:
    """Impact_D(X) = μY. X ∪ {u : ∃h, r_h ∈ D, T_h ∩ Y ≠ ∅, u ∈ O_h} (KS-T09: least closed superset).

    Cycles are handled by the fixed point itself (monotone operator on a finite lattice).
    Worklist over a tail-indexed adjacency of dependency edges: O(|incidences|)."""
    dep = frozenset(dependency_types) if dependency_types is not None else ks.registry.dependency_types
    by_tail: dict[str, list[Hyperedge]] = {}
    for e in ks.hyperedges:
        if e.relation_type in dep:
            for t in e.tails:
                by_tail.setdefault(t, []).append(e)
    impacted = set(changed)
    work = list(impacted)
    while work:
        v = work.pop()
        for e in by_tail.get(v, ()):
            for h in e.heads:
                if h not in impacted:
                    impacted.add(h)
                    work.append(h)
    return frozenset(impacted)


def is_dependency_closed(ks: KnowledgeSpace, s: Iterable[str], dependency_types: Iterable[str] | None = None) -> bool:
    dep = frozenset(dependency_types) if dependency_types is not None else ks.registry.dependency_types
    ss = set(s)
    for e in ks.hyperedges:
        if e.relation_type in dep and any(t in ss for t in e.tails) and not set(e.heads) <= ss:
            return False
    return True


def mutant_impact_cone_direct_only(ks: KnowledgeSpace, changed: Iterable[str], dependency_types: Iterable[str] | None = None) -> frozenset[str]:
    """Planted: one-hop dependents only (stale deep dependent remains live)."""
    dep = frozenset(dependency_types) if dependency_types is not None else ks.registry.dependency_types
    out = set(changed)
    for e in ks.hyperedges:
        if e.relation_type in dep and any(t in changed for t in e.tails):
            out.update(e.heads)
    return frozenset(out)


@dataclass(frozen=True)
class ReopeningReport:
    revoked_before: frozenset
    revoked_after: frozenset
    liveness_changed: frozenset[str]     # atoms whose three-valued liveness differs
    cone: frozenset[str]                 # Impact_D(liveness_changed)
    reopen: frozenset[str]               # cone ∩ liveness_changed  (forced)
    recheck: frozenset[str]              # cone \ liveness_changed  (alternative live path survives)
    unaffected: frozenset[str]           # V \ cone                 (no-alarm control)
    activation_changed: frozenset[str]   # atoms whose fixed-point activation differs (⊆ Reach(dead))

    def as_dict(self) -> dict:
        return {
            "liveness_changed": sorted(self.liveness_changed),
            "cone": sorted(self.cone),
            "reopen": sorted(self.reopen),
            "recheck": sorted(self.recheck),
            "unaffected": sorted(self.unaffected),
            "activation_changed": sorted(self.activation_changed),
        }


def reopening_report(
    ks: KnowledgeSpace,
    revoked_before: Iterable[Hashable],
    revoked_after: Iterable[Hashable],
    *,
    seed: Sequence[Fraction] | None = None,
    alpha: Fraction = Fraction(1, 3),
    dependency_types: Iterable[str] | None = None,
) -> ReopeningReport:
    rb, ra = frozenset(revoked_before), frozenset(revoked_after)
    changed = frozenset(a.atom_id for a in ks.atoms if a.liveness(rb) is not a.liveness(ra))
    edge_changed_heads: set[str] = set()
    for e in ks.hyperedges:
        if e.liveness(rb) is not e.liveness(ra):
            edge_changed_heads.update(e.heads)
    cone = impact_cone(ks, changed | edge_changed_heads, dependency_types)
    act_changed: frozenset[str] = frozenset()
    if seed is not None:
        a0 = fixed_point(ks, seed, alpha, revoked=rb)
        a1 = fixed_point(ks, seed, alpha, revoked=ra)
        act_changed = frozenset(x for x in ks.ids if a0[x] != a1[x])
    return ReopeningReport(
        rb, ra, changed, cone, cone & changed, cone - changed, frozenset(ks.ids) - cone, act_changed
    )


def reach_of_dead(ks: KnowledgeSpace, revoked: Iterable[Hashable]) -> frozenset[str]:
    """Reach(D_R): ungated forward closure of the non-live set (KS-T04b (ii) boundary)."""
    from .navigation import ungated_closure

    rv = frozenset(revoked)
    dead = [a.atom_id for a in ks.atoms if a.liveness(rv) is not Liveness.LIVE]
    dead_edge_heads = [h for e in ks.hyperedges if not e.warrant.is_live(rv) for h in e.heads]
    return ungated_closure(ks, dead + dead_edge_heads)


@dataclass(frozen=True)
class RetractionReport:
    revoked_atom: str
    mutation_applied: bool
    revoked_activation_pre: Fraction
    revoked_activation_post: Fraction
    downstream_pre: dict[str, Fraction]
    downstream_post: dict[str, Fraction]
    unrelated_pre: Fraction
    unrelated_post: Fraction
    unrelated_under_renormalising_parent: Fraction
    reinstated_equals_pre: bool
    independent_implementation_agrees: bool


def retraction_checker(
    ks: KnowledgeSpace,
    *,
    seed: Sequence[Fraction],
    alpha: Fraction,
    revoke: frozenset,
    revoked_atom: str,
    downstream: tuple[str, ...],
    unrelated: str,
) -> RetractionReport:
    """F2 (KS-T04b): mutation asserted applied; exact zero on the revoked atom; downstream drops;
    unrelated unchanged; renormalising parent must differ; reinstatement restores exactly."""
    from .navigation import CannotCheck, mutant_navigation_matrix_renormalize, navigation_matrix_by_pruning, restart_fixed_point_exact, gated_seed

    amap = ks.atom_map()
    for x in (revoked_atom, unrelated, *downstream):
        if x not in amap:
            raise CannotCheck(f"atom {x!r} not in the space")
    if not (amap[revoked_atom].is_live(()) and not amap[revoked_atom].is_live(revoke)):
        raise CannotCheck(f"planted retraction {sorted(map(repr, revoke))} does not flip {revoked_atom!r}; nothing to check")
    pre = fixed_point(ks, seed, alpha)
    post = fixed_point(ks, seed, alpha, revoked=revoke)
    post_ind = fixed_point(ks, seed, alpha, revoked=revoke, matrix=navigation_matrix_by_pruning(ks, revoked=revoke))
    bad_p = mutant_navigation_matrix_renormalize(ks, revoked=revoke)
    bad = dict(zip(ks.ids, restart_fixed_point_exact(bad_p.as_lists(), gated_seed(ks, seed, revoke), alpha), strict=True))
    back = fixed_point(ks, seed, alpha, revoked=frozenset())
    return RetractionReport(
        revoked_atom=revoked_atom,
        mutation_applied=True,
        revoked_activation_pre=pre[revoked_atom],
        revoked_activation_post=post[revoked_atom],
        downstream_pre={x: pre[x] for x in downstream},
        downstream_post={x: post[x] for x in downstream},
        unrelated_pre=pre[unrelated],
        unrelated_post=post[unrelated],
        unrelated_under_renormalising_parent=bad[unrelated],
        reinstated_equals_pre=(back == pre),
        independent_implementation_agrees=(post == post_ind),
    )


def strip_all_warrants(ks: KnowledgeSpace) -> KnowledgeSpace:
    """D4 hostile helper: same weights, every warrant certified-zero — navigation without truth."""
    from .warrant import WarrantProfile

    return replace(
        ks,
        atoms=tuple(replace(a, warrant=WarrantProfile.zero()) for a in ks.atoms),
        hyperedges=tuple(replace(e, warrant=WarrantProfile.zero()) for e in ks.hyperedges),
    )
