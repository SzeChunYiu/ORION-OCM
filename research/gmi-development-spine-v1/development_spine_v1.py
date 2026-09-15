from __future__ import annotations

import heapq
import math
from fractions import Fraction
from typing import Dict, Iterable, Mapping, Sequence, Set, Tuple

Graph = Mapping[str, Sequence[Tuple[str, int]]]


def _validate_graph(graph: Graph) -> None:
    if not graph:
        raise ValueError("development graph must be nonempty")
    states = set(graph)
    for src, edges in graph.items():
        if not isinstance(src, str) or not src:
            raise ValueError("state identifiers must be nonempty strings")
        for dst, cost in edges:
            if dst not in states:
                raise ValueError("every destination must be a registered state")
            if isinstance(cost, bool) or not isinstance(cost, int) or cost < 0:
                raise ValueError("development edge costs must be nonnegative integers")


def shortest_costs(graph: Graph, start: str) -> Dict[str, int]:
    _validate_graph(graph)
    if start not in graph:
        raise ValueError("unknown start state")
    dist: Dict[str, int] = {start: 0}
    queue = [(0, start)]
    while queue:
        cost, state = heapq.heappop(queue)
        if cost != dist[state]:
            continue
        for nxt, edge_cost in graph[state]:
            new_cost = cost + edge_cost
            if new_cost < dist.get(nxt, math.inf):
                dist[nxt] = new_cost
                heapq.heappush(queue, (new_cost, nxt))
    return dist


def adaptation_burden(graph: Graph, start: str, satisfying_states: Iterable[str]) -> float | int:
    targets = set(satisfying_states)
    if not targets:
        raise ValueError("at least one satisfying state is required")
    if not targets.issubset(graph):
        raise ValueError("unknown satisfying state")
    dist = shortest_costs(graph, start)
    reachable = [dist[state] for state in targets if state in dist]
    return min(reachable) if reachable else math.inf


def morphology_search_burden(graph: Graph, start: str, target_morphologies: Iterable[str]) -> float | int:
    """Minimum fully charged developmental search cost to a target morphology set."""
    return adaptation_burden(graph, start, target_morphologies)


def current_capability(current_success: Mapping[str, bool]) -> Fraction:
    if not current_success:
        raise ValueError("current obligation set must be nonempty")
    if any(not isinstance(value, bool) for value in current_success.values()):
        raise ValueError("current-success values must be boolean")
    return Fraction(sum(current_success.values()), len(current_success))


def learning_potential(
    graph: Graph,
    start: str,
    future_obligations: Mapping[str, Iterable[str]],
    *,
    budget: int,
) -> Fraction:
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 0:
        raise ValueError("budget must be a nonnegative integer")
    if not future_obligations:
        raise ValueError("future obligation set must be nonempty")
    reachable = 0
    for targets in future_obligations.values():
        if adaptation_burden(graph, start, targets) <= budget:
            reachable += 1
    return Fraction(reachable, len(future_obligations))


def useful_descendant_mass(
    graph: Graph,
    start: str,
    useful_weights: Mapping[str, int],
    *,
    budget: int,
) -> int:
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 0:
        raise ValueError("budget must be a nonnegative integer")
    if not useful_weights:
        raise ValueError("at least one useful descendant weight is required")
    if not set(useful_weights).issubset(graph):
        raise ValueError("unknown useful descendant")
    if any(isinstance(w, bool) or not isinstance(w, int) or w < 0 for w in useful_weights.values()):
        raise ValueError("useful weights must be nonnegative integers")
    dist = shortest_costs(graph, start)
    return sum(weight for state, weight in useful_weights.items() if dist.get(state, math.inf) <= budget)


def transfer_benefit(
    graph: Graph,
    *,
    reset_state: str,
    continued_state: str,
    satisfying_states: Iterable[str],
) -> float | int:
    """Positive means continued development reduces next-task adaptation burden."""
    reset = adaptation_burden(graph, reset_state, satisfying_states)
    continued = adaptation_burden(graph, continued_state, satisfying_states)
    if math.isinf(reset) and math.isinf(continued):
        return 0
    if math.isinf(reset):
        return math.inf
    if math.isinf(continued):
        return -math.inf
    return reset - continued


def harmful_transfer(*args, **kwargs) -> bool:
    return transfer_benefit(*args, **kwargs) < 0


def developmental_path_dependence(
    graph: Graph,
    state_a: str,
    state_b: str,
    current_outputs_a: Mapping[str, object],
    current_outputs_b: Mapping[str, object],
    future_target_sets: Sequence[Iterable[str]],
) -> bool:
    """True iff present outputs match but some future adaptation burden differs."""
    if current_outputs_a != current_outputs_b:
        return False
    for targets in future_target_sets:
        if adaptation_burden(graph, state_a, targets) != adaptation_burden(graph, state_b, targets):
            return True
    return False


def graph_extends_without_repricing(base: Graph, extended: Graph) -> bool:
    """Check the load-bearing premise for free optional inheritance.

    Every base edge/cost must remain available unchanged; extra inherited options
    may be added but old feasible developmental paths may not be removed/repriced.
    """
    _validate_graph(base)
    _validate_graph(extended)
    if set(base) != set(extended):
        return False
    for src in base:
        if not set(base[src]).issubset(set(extended[src])):
            return False
    return True


def optional_inheritance_monotonicity(
    base: Graph,
    inherited: Graph,
    *,
    start: str,
    target_sets: Sequence[Iterable[str]],
    useful_weights: Mapping[str, int],
    budget: int,
) -> Dict[str, object]:
    if not graph_extends_without_repricing(base, inherited):
        raise ValueError("inheritance is not a free optional extension of the base path set")
    base_burdens = tuple(adaptation_burden(base, start, targets) for targets in target_sets)
    inherited_burdens = tuple(adaptation_burden(inherited, start, targets) for targets in target_sets)
    burden_monotone = all(new <= old for old, new in zip(base_burdens, inherited_burdens))
    base_mass = useful_descendant_mass(base, start, useful_weights, budget=budget)
    inherited_mass = useful_descendant_mass(inherited, start, useful_weights, budget=budget)
    return {
        "base_burdens": base_burdens,
        "inherited_burdens": inherited_burdens,
        "burden_nonincreasing": burden_monotone,
        "base_useful_mass": base_mass,
        "inherited_useful_mass": inherited_mass,
        "useful_mass_nondecreasing": inherited_mass >= base_mass,
    }
