"""Measured exact-index extraction serving paths (conventional parent mechanics).

Warm sparse-support reaction avoids global liveness/pending preparation. Dense
seed adapters still inspect N entries. Greedy preserves the incumbent search
policy; bounded exact PCST remains the separate, globally bounded reference.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Hashable, Iterable, Mapping

from .extraction import Approximation, ExtractionResult, ReactingSubgraph
from .extraction_index import ExtractionIndex, ExtractionRun, IndexedExtractionWork
from .navigation import NavigationMode
from .space import KnowledgeSpace


def _reaction(ks, rho, support, mode, run):
    warranted = mode is NavigationMode.WARRANTED
    # Lazy pending counts preserve conjunctive firing. Exploratory closure uses
    # any reached tail. Do not substitute positive-activation support here.
    reached = {x for x in support if run.live_atom(x)} if warranted else set(support)
    pending, work = {}, list(reached)
    while work:
        atom_id = work.pop()
        run.counts["closure_expansions"] += 1
        for edge in run.adjacent(atom_id, outgoing=True):
            if warranted:
                pending[edge.edge_id] = pending.get(edge.edge_id, len(edge.tails)) - 1
                if pending[edge.edge_id] or not run.live_edge(edge):
                    continue
            for head in edge.heads:
                run.counts["incidence_memberships_examined"] += 1
                if head not in reached and (not warranted or run.live_atom(head)):
                    reached.add(head)
                    work.append(head)
    atoms = frozenset(x for x in reached if rho[x] > 0) | support
    run.atoms.update(reached)
    if warranted:
        atoms = frozenset(x for x in atoms if run.live_atom(x))
    edges = frozenset(edge.edge_id for edge in run.touching(atoms)
                      if run.incidences(edge) <= atoms and (not warranted or run.live_edge(edge)))
    return ReactingSubgraph(atoms, edges, mode, support)


def reacting_subgraph_from_support_indexed(
    ks: KnowledgeSpace, rho: Mapping[str, float], seed_support: Iterable[str], *,
    revoked: Iterable[Hashable] = (), mode: NavigationMode = NavigationMode.WARRANTED,
    index: ExtractionIndex | None = None, with_work: bool = False,
) -> ReactingSubgraph | tuple[ReactingSubgraph, IndexedExtractionWork]:
    """Equivalent reaction given exactly the positive seed IDs, without a dense scan.

    ``rho`` is queried only on reached IDs; a missing reached value raises
    KeyError as in the reference. Unknown seed IDs are rejected in both modes.
    The caller establishes the support/seed correspondence; this API does not
    certify that a truncated activation or surprise map is sufficient.
    """
    run = ExtractionRun(ks, index, revoked)
    support = set()
    for atom_id in seed_support:
        run.counts["seed_entries_examined"] += 1
        if atom_id not in run.index.atoms:
            raise KeyError(atom_id)
        support.add(atom_id)
    result = _reaction(ks, rho, frozenset(support), mode, run)
    return (result, run.finish()) if with_work else result


def reacting_subgraph_from_surprise_indexed(
    ks: KnowledgeSpace, rho: Mapping[str, float], seed, *,
    revoked: Iterable[Hashable] = (), mode: NavigationMode = NavigationMode.WARRANTED,
    index: ExtractionIndex | None = None, with_work: bool = False,
) -> ReactingSubgraph | tuple[ReactingSubgraph, IndexedExtractionWork]:
    """Reference-compatible dense adapter; its full seed scan is explicitly counted."""
    run = ExtractionRun(ks, index, revoked)
    support = set()
    for atom_id, value in zip(ks.ids, seed, strict=True):
        run.counts["dense_seed_entries_examined"] += 1
        if value > 0:
            support.add(atom_id)
    run.counts["seed_entries_examined"] = run.counts["dense_seed_entries_examined"]
    result = _reaction(ks, rho, frozenset(support), mode, run)
    return (result, run.finish()) if with_work else result


def pcst_greedy_indexed(
    ks: KnowledgeSpace, prizes: Mapping[str, Fraction], seeds: Iterable[str], *,
    edge_prizes: Mapping[str, Fraction] | None = None,
    lam: Fraction = Fraction(1), mu: Fraction = Fraction(1), cost=None,
    revoked: Iterable[Hashable] = (), mode: NavigationMode = NavigationMode.WARRANTED,
    index: ExtractionIndex | None = None, with_work: bool = False,
) -> ExtractionResult | tuple[ExtractionResult, IndexedExtractionWork]:
    """Incident-index implementation of the incumbent greedy policy and tie order.

    This is the same approximation, not exact PCST. Custom cost functions must
    be pure. Disconnected fields are skipped, but a global reachable frontier
    may demand global work. Liveness caches are discarded after every call.
    """
    run = ExtractionRun(ks, index, revoked)
    seed_items = tuple(seeds)
    run.counts["seed_entries_examined"] = len(seed_items)
    seeds = frozenset(seed_items)
    edge_prizes = edge_prizes or {}
    cost = cost or (lambda atoms, edges: Fraction(len(atoms) + len(edges)))
    warranted = mode is NavigationMode.WARRANTED

    def edges_ok(edge):
        return not warranted or (run.live_edge(edge) and all(run.live_atom(x) for x in run.incidences(edge)))

    def objective(atoms):
        run.counts["objective_evaluations"] += 1
        run.atoms.update(atoms)
        edges = frozenset(edge.edge_id for edge in run.touching(atoms)
                          if run.incidences(edge) <= atoms and edges_ok(edge))
        value = sum((Fraction(prizes.get(x, 0)) for x in atoms), Fraction(0))
        value += lam * sum((Fraction(edge_prizes.get(edge_id, 0)) for edge_id in edges), Fraction(0))
        return value - mu * cost(atoms, edges), edges

    current = seeds
    value, edges = objective(current)
    considered = 0
    while True:
        frontier = set()
        for edge in run.touching(current):
            if edges_ok(edge):
                frontier |= run.incidences(edge) - current
        if warranted:
            frontier = {x for x in frontier if run.live_atom(x)}
        best_gain, best_atom = Fraction(0), None
        for atom_id in sorted(frontier):
            considered += 1
            run.counts["candidate_evaluations"] += 1
            candidate_value, _ = objective(current | {atom_id})
            if candidate_value - value > best_gain:
                best_gain, best_atom = candidate_value - value, atom_id
        if best_atom is None:
            break
        current = current | {best_atom}
        value, edges = objective(current)
    result = ExtractionResult(current, edges, value, Approximation.GREEDY_PRIZE_DENSITY, (), 0, considered)
    return (result, run.finish()) if with_work else result
