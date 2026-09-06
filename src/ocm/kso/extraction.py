"""Reacting-subgraph extraction (contract §7, KS-T11/T11a; M1 E1).

* ``reacting_subgraph`` — the unique object of KS-T11a: atoms with positive reaction surprise in
  the gated closure of the seed support, plus the seed support, with the live hyperedges inside.
* ``pcst_exact_bounded`` — exact prize-collecting connected-subhypergraph optimiser on bounded
  instances (enumerates all optima; ties are reported, never hidden).
* ``pcst_greedy`` — the scalable approximation interface; every result carries
  ``approximation="GREEDY_PRIZE_DENSITY"`` so approximation is reported, not hidden.
Both run in WARRANTED (live only) or EXPLORATORY (ungated) mode; exploratory extractions cannot
authorise a claim.  Parent: prize-collecting Steiner tree (Goemans–Williamson family).
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Hashable, Iterable, Mapping, Sequence

from .navigation import NavigationMode, gated_closure, surprise_vector, ungated_closure
from .space import KnowledgeSpace
from .warrant import CannotCheck


@dataclass(frozen=True)
class ReactingSubgraph:
    atoms: frozenset[str]
    edges: frozenset[str]
    mode: NavigationMode
    seed_support: frozenset[str]

    def as_dict(self) -> dict:
        return {"atoms": sorted(self.atoms), "edges": sorted(self.edges), "mode": self.mode.value, "seed_support": sorted(self.seed_support)}


def reacting_subgraph(
    ks: KnowledgeSpace,
    activation: Mapping[str, Fraction],
    background: Mapping[str, Fraction],
    seed: Sequence[Fraction],
    *,
    revoked: Iterable[Hashable] = (),
    mode: NavigationMode = NavigationMode.WARRANTED,
) -> ReactingSubgraph:
    return reacting_subgraph_from_surprise(ks, surprise_vector(activation, background), seed, revoked=revoked, mode=mode)


def reacting_subgraph_from_surprise(
    ks: KnowledgeSpace,
    rho: Mapping[str, float],
    seed: Sequence[Fraction],
    *,
    revoked: Iterable[Hashable] = (),
    mode: NavigationMode = NavigationMode.WARRANTED,
) -> ReactingSubgraph:
    """KS-T11a object for any registered surprise vector (the surprise model is a parameter)."""
    rv = frozenset(revoked)
    support = frozenset(x for x, v in zip(ks.ids, seed, strict=True) if v > 0)
    closure = gated_closure(ks, support, rv) if mode is NavigationMode.WARRANTED else ungated_closure(ks, support)
    atoms = frozenset(x for x in closure if rho[x] > 0) | support
    if mode is NavigationMode.WARRANTED:
        amap = ks.atom_view
        atoms = frozenset(x for x in atoms if amap[x].is_live(rv))
        edges = frozenset(e.edge_id for e in ks.hyperedges if e.incident <= atoms and e.warrant.is_live(rv))
    else:
        edges = frozenset(e.edge_id for e in ks.hyperedges if e.incident <= atoms)
    return ReactingSubgraph(atoms, edges, mode, support)


# --------------------------------------------------------------------------------------------
# prize-collecting connected sub-hypergraph optimiser (KS-T11 — parent problem)
# --------------------------------------------------------------------------------------------


class Approximation(str, Enum):
    EXACT_BOUNDED = "EXACT_BOUNDED"
    GREEDY_PRIZE_DENSITY = "GREEDY_PRIZE_DENSITY"


@dataclass(frozen=True)
class ExtractionResult:
    atoms: frozenset[str]
    edges: frozenset[str]
    objective: Fraction
    approximation: Approximation
    optima: tuple[frozenset[str], ...] = ()   # every optimal atom set (exact mode only)
    ties: int = 0
    candidates_considered: int = 0

    def as_dict(self) -> dict:
        return {
            "atoms": sorted(self.atoms),
            "edges": sorted(self.edges),
            "objective": str(self.objective),
            "approximation": self.approximation.value,
            "ties": self.ties,
            "candidates_considered": self.candidates_considered,
        }


def _connected(ks: KnowledgeSpace, atoms: frozenset[str], seeds: frozenset[str], edges_ok) -> bool:
    """Every atom is reachable (undirected, through admissible edges inside the set) from a seed."""
    if not seeds <= atoms:
        return False
    inside = [e for e in ks.hyperedges if e.incident <= atoms and edges_ok(e)]
    reached = set(seeds)
    grew = True
    while grew:
        grew = False
        for e in inside:
            if e.incident & reached and not e.incident <= reached:
                reached |= e.incident
                grew = True
    return reached == atoms


def _objective(ks: KnowledgeSpace, atoms: frozenset[str], prizes, edge_prizes, lam, mu, cost, edges_ok) -> tuple[Fraction, frozenset[str]]:
    edges = frozenset(e.edge_id for e in ks.hyperedges if e.incident <= atoms and edges_ok(e))
    value = sum((Fraction(prizes.get(x, 0)) for x in atoms), Fraction(0, 1))
    value += lam * sum((Fraction(edge_prizes.get(e, 0)) for e in edges), Fraction(0, 1))
    value -= mu * cost(atoms, edges)
    return value, edges


def pcst_exact_bounded(
    ks: KnowledgeSpace,
    prizes: Mapping[str, Fraction],
    seeds: Iterable[str],
    *,
    edge_prizes: Mapping[str, Fraction] | None = None,
    lam: Fraction = Fraction(1, 1),
    mu: Fraction = Fraction(1, 1),
    cost=None,
    revoked: Iterable[Hashable] = (),
    mode: NavigationMode = NavigationMode.WARRANTED,
    max_atoms: int = 12,
) -> ExtractionResult:
    """Exact optimiser over every seed-connected atom subset; bounded to ``max_atoms`` free atoms."""
    rv = frozenset(revoked)
    amap = ks.atom_view
    seeds = frozenset(seeds)
    edge_prizes = edge_prizes or {}
    cost = cost or (lambda atoms, edges: Fraction(len(atoms) + len(edges), 1))
    if mode is NavigationMode.WARRANTED:
        edges_ok = lambda e: e.warrant.is_live(rv) and all(amap[x].is_live(rv) for x in e.incident)  # noqa: E731
        universe = [x for x in ks.ids if x not in seeds and amap[x].is_live(rv)]
        if any(not amap[s].is_live(rv) for s in seeds):
            raise CannotCheck("a seed is not live in warranted mode")
    else:
        edges_ok = lambda e: True  # noqa: E731
        universe = [x for x in ks.ids if x not in seeds]
    if len(universe) > max_atoms:
        raise CannotCheck(f"exact extraction bounded to {max_atoms} free atoms; instance has {len(universe)}")
    best: Fraction | None = None
    optima: list[frozenset[str]] = []
    considered = 0
    for r in range(len(universe) + 1):
        for combo in itertools.combinations(universe, r):
            atoms = seeds | frozenset(combo)
            considered += 1
            if not _connected(ks, atoms, seeds, edges_ok):
                continue
            value, _ = _objective(ks, atoms, prizes, edge_prizes, lam, mu, cost, edges_ok)
            if best is None or value > best:
                best, optima = value, [atoms]
            elif value == best:
                optima.append(atoms)
    if best is None:
        raise CannotCheck("no seed-connected candidate exists")
    chosen = min(optima, key=lambda s: (len(s), sorted(s)))
    _, edges = _objective(ks, chosen, prizes, edge_prizes, lam, mu, cost, edges_ok)
    return ExtractionResult(chosen, edges, best, Approximation.EXACT_BOUNDED, tuple(optima), len(optima) - 1, considered)


def pcst_greedy(
    ks: KnowledgeSpace,
    prizes: Mapping[str, Fraction],
    seeds: Iterable[str],
    *,
    edge_prizes: Mapping[str, Fraction] | None = None,
    lam: Fraction = Fraction(1, 1),
    mu: Fraction = Fraction(1, 1),
    cost=None,
    revoked: Iterable[Hashable] = (),
    mode: NavigationMode = NavigationMode.WARRANTED,
) -> ExtractionResult:
    """Greedy growth by marginal objective gain; the reported approximation flag is mandatory."""
    rv = frozenset(revoked)
    amap = ks.atom_view
    seeds = frozenset(seeds)
    edge_prizes = edge_prizes or {}
    cost = cost or (lambda atoms, edges: Fraction(len(atoms) + len(edges), 1))
    if mode is NavigationMode.WARRANTED:
        edges_ok = lambda e: e.warrant.is_live(rv) and all(amap[x].is_live(rv) for x in e.incident)  # noqa: E731
    else:
        edges_ok = lambda e: True  # noqa: E731
    current = seeds
    value, edges = _objective(ks, current, prizes, edge_prizes, lam, mu, cost, edges_ok)
    considered = 0
    while True:
        frontier = set()
        for e in ks.hyperedges:
            if edges_ok(e) and e.incident & current:
                frontier |= e.incident - current
        if mode is NavigationMode.WARRANTED:
            frontier = {x for x in frontier if amap[x].is_live(rv)}
        best_gain, best_atom = Fraction(0, 1), None
        for x in sorted(frontier):
            considered += 1
            v, _ = _objective(ks, current | {x}, prizes, edge_prizes, lam, mu, cost, edges_ok)
            if v - value > best_gain:
                best_gain, best_atom = v - value, x
        if best_atom is None:
            break
        current = current | {best_atom}
        value, edges = _objective(ks, current, prizes, edge_prizes, lam, mu, cost, edges_ok)
    return ExtractionResult(current, edges, value, Approximation.GREEDY_PRIZE_DENSITY, (), 0, considered)