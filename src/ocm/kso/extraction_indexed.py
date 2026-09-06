"""Indexed local extraction prototypes for issue #115 FK-3.

The incumbent extraction module remains authoritative.  This additive path uses
KnowledgeSpace's incident-edge index to avoid scanning every registered
hyperedge during greedy frontier/objective work.  Cold construction of that
index is explicitly reported; a warm local result is not evidence that hidden
global preprocessing was free.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Hashable, Iterable, Mapping

from .extraction import Approximation, ExtractionResult, ReactingSubgraph
from .navigation import NavigationMode, gated_closure, ungated_closure
from .space import KnowledgeSpace


@dataclass(frozen=True, slots=True)
class IndexedExtractionWork:
    incident_postings_examined: int
    distinct_edges_examined: int
    objective_evaluations: int
    cold_incident_index_build: bool


def _edges_touching(ks: KnowledgeSpace, atoms: frozenset[str], tracker) -> tuple:
    by_id = {}
    for atom_id in atoms:
        incident = ks.incident_edges(atom_id)
        tracker["postings"] += len(incident)
        for edge in incident:
            by_id[edge.edge_id] = edge
            tracker["edges"].add(edge.edge_id)
    return tuple(by_id[key] for key in sorted(by_id))


def reacting_subgraph_from_surprise_indexed(
    ks: KnowledgeSpace,
    rho: Mapping[str, float],
    seed,
    *,
    revoked: Iterable[Hashable] = (),
    mode: NavigationMode = NavigationMode.WARRANTED,
) -> ReactingSubgraph:
    """Reference-equivalent reacting subgraph with indexed internal-edge recovery.

    ``gated_closure`` itself already uses the outgoing adjacency index.  This
    helper removes the subsequent whole-hyperedge scan when materialising the
    edges internal to the reacting atom set.
    """

    rv = frozenset(revoked)
    support = frozenset(x for x, value in zip(ks.ids, seed, strict=True) if value > 0)
    closure = gated_closure(ks, support, rv) if mode is NavigationMode.WARRANTED else ungated_closure(ks, support)
    atoms = frozenset(x for x in closure if rho[x] > 0) | support
    amap = ks.atom_view
    if mode is NavigationMode.WARRANTED:
        atoms = frozenset(x for x in atoms if amap[x].is_live(rv))

    candidate_edges = {}
    for atom_id in atoms:
        for edge in ks.incident_edges(atom_id):
            candidate_edges[edge.edge_id] = edge
    if mode is NavigationMode.WARRANTED:
        edges = frozenset(
            edge.edge_id
            for edge in candidate_edges.values()
            if edge.incident <= atoms and edge.warrant.is_live(rv)
        )
    else:
        edges = frozenset(edge.edge_id for edge in candidate_edges.values() if edge.incident <= atoms)
    return ReactingSubgraph(atoms, edges, mode, support)


def pcst_greedy_indexed(
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
    with_work: bool = False,
) -> ExtractionResult | tuple[ExtractionResult, IndexedExtractionWork]:
    """Greedy prize-density extraction using incident-index frontier/objectives.

    Candidate ordering, objective, warrant gating and output type match
    :func:`ocm.kso.extraction.pcst_greedy`.  This function changes only how
    candidate edges are located.
    """

    rv = frozenset(revoked)
    amap = ks.atom_view
    seeds = frozenset(seeds)
    edge_prizes = edge_prizes or {}
    cost = cost or (lambda atoms, edges: Fraction(len(atoms) + len(edges), 1))
    if mode is NavigationMode.WARRANTED:
        edges_ok = lambda edge: edge.warrant.is_live(rv) and all(amap[x].is_live(rv) for x in edge.incident)
    else:
        edges_ok = lambda edge: True

    tracker = {
        "postings": 0,
        "edges": set(),
        "objective_evaluations": 0,
        "cold": "_incident_index" not in ks.__dict__,
    }

    def objective(atoms: frozenset[str]):
        tracker["objective_evaluations"] += 1
        edges = frozenset(
            edge.edge_id
            for edge in _edges_touching(ks, atoms, tracker)
            if edge.incident <= atoms and edges_ok(edge)
        )
        value = sum((Fraction(prizes.get(x, 0)) for x in atoms), Fraction(0, 1))
        value += lam * sum((Fraction(edge_prizes.get(edge_id, 0)) for edge_id in edges), Fraction(0, 1))
        value -= mu * cost(atoms, edges)
        return value, edges

    current = seeds
    value, edges = objective(current)
    considered = 0
    while True:
        frontier = set()
        for edge in _edges_touching(ks, current, tracker):
            if edges_ok(edge) and edge.incident & current:
                frontier |= edge.incident - current
        if mode is NavigationMode.WARRANTED:
            frontier = {x for x in frontier if amap[x].is_live(rv)}

        best_gain, best_atom = Fraction(0, 1), None
        for atom_id in sorted(frontier):
            considered += 1
            candidate_value, _ = objective(current | {atom_id})
            if candidate_value - value > best_gain:
                best_gain, best_atom = candidate_value - value, atom_id
        if best_atom is None:
            break
        current = current | {best_atom}
        value, edges = objective(current)

    result = ExtractionResult(current, edges, value, Approximation.GREEDY_PRIZE_DENSITY, (), 0, considered)
    if with_work:
        return result, IndexedExtractionWork(
            tracker["postings"],
            len(tracker["edges"]),
            tracker["objective_evaluations"],
            bool(tracker["cold"]),
        )
    return result
