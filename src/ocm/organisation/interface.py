"""Common organisation interface (M8 §1–§2, §7): every representation arm exposes the same contract
over one KnowledgeSpace so identical task/evidence streams can be run against each arm.

* `Region` — a named set of atoms (regions may overlap: multiple membership is legitimate, M8 §6);
  never a copy of authority-bearing objects.
* `MacroInterface` — what a summarised region exports: identity/version, scope, exported claims,
  the query families it is sufficient for (registered certificates), a warrant/provenance summary
  (⊗ over the exported claims' warrants — never stronger than the children), a cost model, known
  obstructions, a descent pointer and a reopen summary.  Invariant (M8 §2): LIVE(macro) ⇒ a live
  child support exists (`macro_liveness` is computed from the children, never cached).
* `TransportMap` — a correspondence between regions with applicability conditions, preserved /
  lost structure and its own warrant; a transported object's warrant is ⊗(source, correspondence)
  (M8 §7), so revoking the source or the correspondence kills the transported object.
* `Organisation` — the arm protocol: regions, membership, macro for a region, transports, and
  `describe()` for the parent-subtraction report.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Hashable, Iterable, Mapping, Protocol, Sequence

from ocm.kso.space import KnowledgeSpace
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile, meet_all_profiles


@dataclass(frozen=True)
class Region:
    region_id: str
    atoms: frozenset[str]
    parents: tuple[str, ...] = ()            # containment (may have several parents: R2)
    label: str = ""


@dataclass(frozen=True)
class MacroInterface:
    region_id: str
    version: int
    scope: Scope
    exported_claims: tuple[str, ...]         # atom ids the parent level may cite
    sufficient_for: tuple[str, ...]          # registered query-family ids with certificates
    warrant_summary: WarrantProfile           # ⊗ over exported claims' warrants (never stronger)
    cost_model: Mapping[str, int]
    known_obstructions: tuple[str, ...]
    descent: str                              # pointer: how to refine (region id)
    reopen_summary: tuple[str, ...]           # evidence the exports depend on


@dataclass(frozen=True)
class TransportMap:
    transport_id: str
    source: str
    target: str
    mapping: Mapping[str, str]                # source atom → target atom (or image id)
    applicability: tuple[str, ...]            # registered conditions (scope contexts) that must hold
    preserved: tuple[str, ...]
    lost: tuple[str, ...]
    warrant: WarrantProfile                   # warrant of the correspondence itself
    cost: int = 1
    known_failures: tuple[str, ...] = ()


def macro_for(ks: KnowledgeSpace, region: Region, *, version: int = 1, sufficient_for: Iterable[str] = (), cost: Mapping[str, int] | None = None, obstructions: Iterable[str] = ()) -> MacroInterface:
    """The macro is *derived* from the children: exports = the region's atoms of claim/procedure type
    (registry data), warrant = ⊗ of their warrants, scope = intersection of their scopes."""
    amap = ks.atom_map()
    exports = tuple(sorted(a for a in region.atoms if a in amap and amap[a].atom_type in ("claim", "procedure", "summary")))
    warrant = meet_all_profiles([amap[a].warrant for a in exports]) if exports else WarrantProfile.zero()
    scope = Scope.universal()
    for a in exports:
        scope = scope.intersect(amap[a].scope) if hasattr(scope, "intersect") else scope
    reopen = tuple(sorted({str(e) for a in exports for w in amap[a].warrant.lower for e in w}))
    return MacroInterface(region.region_id, version, scope, exports, tuple(sufficient_for), warrant, dict(cost or {"atoms": len(region.atoms)}), tuple(obstructions), region.region_id, reopen)


def macro_liveness(ks: KnowledgeSpace, macro: MacroInterface, revoked: Iterable[Hashable]) -> Liveness:
    """Computed from the children every time (M8 §2 invariant; no cache can outlive its support)."""
    rv = frozenset(revoked)
    amap = ks.atom_map()
    live_exports = [a for a in macro.exported_claims if a in amap and amap[a].liveness(rv) is Liveness.LIVE]
    if not macro.exported_claims:
        return Liveness.DEAD
    if live_exports:
        return Liveness.LIVE if len(live_exports) == len(macro.exported_claims) else Liveness.UNKNOWN
    return Liveness.DEAD if all(amap[a].liveness(rv) is Liveness.DEAD for a in macro.exported_claims if a in amap) else Liveness.UNKNOWN


def transported_warrant(ks: KnowledgeSpace, tm: TransportMap, source_atom: str) -> WarrantProfile:
    """Λ(transported) = Λ(source) ⊗ Λ(correspondence): never stronger than either (M8 §7)."""
    return ks.atom(source_atom).warrant.meet(tm.warrant)


def transport_applicable(tm: TransportMap, contexts: Iterable[str]) -> bool:
    ctx = set(contexts)
    return all(c in ctx for c in tm.applicability)


class Organisation(Protocol):
    name: str

    def regions(self) -> Sequence[Region]: ...
    def regions_of(self, atom_id: str) -> Sequence[str]: ...
    def macro(self, region_id: str) -> MacroInterface: ...
    def transports(self) -> Sequence[TransportMap]: ...
    def describe(self) -> dict[str, Any]: ...


def containment_consistent(regions: Sequence[Region]) -> tuple[bool, str]:
    """No cycles in the parent relation; a child's atoms are contained in each parent's (M8 §15
    hostile: cyclic / inconsistent containment accepted silently)."""
    by_id = {r.region_id: r for r in regions}
    for r in regions:
        for p in r.parents:
            if p not in by_id:
                return False, f"dangling parent {p} of {r.region_id}"
            if not r.atoms <= by_id[p].atoms:
                return False, f"{r.region_id} not contained in parent {p}"
    # cycle check
    seen: set[str] = set()

    def visit(rid: str, stack: tuple[str, ...]) -> str | None:
        if rid in stack:
            return f"cycle through {rid}"
        if rid in seen:
            return None
        seen.add(rid)
        for p in by_id[rid].parents:
            err = visit(p, stack + (rid,))
            if err:
                return err
        return None

    for r in regions:
        err = visit(r.region_id, ())
        if err:
            return False, err
    return True, "ok"


def mutant_macro_cache(ks: KnowledgeSpace, macro: MacroInterface, cached: Liveness) -> Liveness:
    """Planted (M8 §4/§15 'macro claims remain live after child revocation'): return the cached value."""
    return cached


def mutant_transport_similarity_as_proof(tm: TransportMap, similarity: float) -> WarrantProfile:
    """Planted (M8 §7 'similarity-only transport treated as proof')."""
    return WarrantProfile.one() if similarity > 0.8 else tm.warrant
