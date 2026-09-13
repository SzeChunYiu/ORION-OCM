#!/usr/bin/env python3
"""Exact finite witnesses for FOC reachability and comparison corrections."""
from __future__ import annotations

import argparse
from collections import deque
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path


def pareto(profiles):
    """All coordinates are minimized; retain profiles rather than source IDs."""
    profiles = set(profiles)
    return {p for p in profiles if not any(
        all(x <= y for x, y in zip(other, p)) and other != p
        for other in profiles
    )}


def reachable_labels(states, edges, starts, budget):
    """Exact finite state/cost-label closure; zero-cost cycles are deduplicated.

    Return (state, accumulated-label) -> minimum step count. The state is
    assumed to contain all path information relevant to future moves/output.
    """
    states = tuple(states)
    budget = tuple(F(value) for value in budget)
    if not budget or any(value < 0 for value in budget):
        raise ValueError("Require a nonempty nonnegative rational budget")
    outgoing = {state: [] for state in states}
    for source, target, raw_cost in edges:
        cost = tuple(F(value) for value in raw_cost)
        if (source not in outgoing or target not in outgoing
                or len(cost) != len(budget) or any(value < 0 for value in cost)):
            raise ValueError("Edges require registered states and matching nonnegative costs")
        outgoing[source].append((target, cost))
    zero = (F(0),) * len(budget)
    distance = {}
    queue = deque()
    for state in starts:
        if state not in outgoing:
            raise ValueError("Initial state is not registered")
        key = (state, zero)
        if key not in distance:
            distance[key] = 0
            queue.append(key)
    while queue:
        key = queue.popleft()
        state, label = key
        for target, cost in outgoing[state]:
            new_label = tuple(x + y for x, y in zip(label, cost))
            next_key = (target, new_label)
            if all(x <= y for x, y in zip(new_label, budget)) and next_key not in distance:
                distance[next_key] = distance[key] + 1
                queue.append(next_key)
    return distance


def simple_path_labels(states, edges, start, budget):
    """Independent oracle: enumerate only original-state-simple paths.

    Nonnegative costs allow cycle deletion, so these paths suffice for
    reachability and Pareto cost labels, though not all dominated labels.
    """
    outgoing = {state: [] for state in states}
    for source, target, cost in edges:
        outgoing[source].append((target, tuple(F(x) for x in cost)))
    found = {state: set() for state in states}
    stack = [(start, (F(0),) * len(budget), frozenset((start,)))]
    while stack:
        state, label, visited = stack.pop()
        found[state].add(label)
        for target, cost in outgoing[state]:
            candidate = tuple(x + y for x, y in zip(label, cost))
            if target not in visited and all(x <= y for x, y in zip(candidate, budget)):
                stack.append((target, candidate, visited | {target}))
    return found


def frontier_restriction_checks():
    grid = tuple(product(range(3), repeat=2))
    checks = strict = 0
    for profiles in product(grid, repeat=3):
        global_frontier = pareto(profiles)
        for mask in range(1, 8):
            reachable = {profiles[i] for i in range(3) if mask & (1 << i)}
            constrained = pareto(reachable)
            accessible = global_frontier & reachable
            assert accessible <= constrained
            assert constrained
            checks += 1
            strict += accessible != constrained
    reachable = {(F(2),)}
    global_frontier = pareto(((F(2),), (F(1),)))
    assert global_frontier & reachable == set()
    assert pareto(reachable) == reachable
    return {"finite_profile_scope_cases": checks,
            "filter_global_frontier_loses_reachable_optima": strict,
            "hidden_unreachable_dominator_witness": {
                "global_cost_frontier": [1], "reachable_cost_frontier": [2],
                "accessible_global_profiles": []}}


def graph_closure_checks():
    states = (0, 1, 2)
    arcs = tuple((source, target) for source in states for target in states if source != target)
    checked = zero_cycle_cases = 0
    for configuration in product((None, 0, 1), repeat=len(arcs)):
        edges = tuple((source, target, (F(cost),))
                      for (source, target), cost in zip(arcs, configuration) if cost is not None)
        has_zero_two_cycle = any((target, source, (F(0),)) in edges
                                for source, target, cost in edges if cost == (0,))
        for scalar_budget in range(3):
            budget = (F(scalar_budget),)
            closure = reachable_labels(states, edges, (0,), budget)
            oracle = simple_path_labels(states, edges, 0, budget)
            assert len(closure) <= len(states) * (scalar_budget + 1)
            for state in states:
                actual = {label for (target, label) in closure if target == state}
                assert bool(actual) == bool(oracle[state])
                assert pareto(actual) == pareto(oracle[state])
            checked += 1
            zero_cycle_cases += has_zero_two_cycle
    return {"graph_budget_cases": checked,
            "cases_containing_zero_cost_two_cycle": zero_cycle_cases,
            "oracle": "independent_original_state_simple_path_enumeration"}


def zero_cycle_and_cost_tradeoff_checks():
    edges = (("s", "s", (F(0),)), ("s", "t", (F(1),)))
    closure = reachable_labels(("s", "t"), edges, ("s",), (F(1),))
    assert closure == {("s", (F(0),)): 0, ("t", (F(1),)): 1}
    # Each distinct path loop^n;exit costs one. This finite prefix accompanies
    # the analytic infinite family, and does not enumerate all histories.
    paths = {("loop",) * count + ("exit",) for count in range(65)}
    assert len(paths) == 65
    assert all(sum(1 for edge in path if edge == "exit") == 1 for path in paths)

    tradeoff_edges = (("s", "t", (F(1), F(3))),
                      ("s", "t", (F(3), F(1))))
    tradeoff = reachable_labels(("s", "t"), tradeoff_edges, ("s",), (F(3), F(3)))
    terminal_labels = {label for (state, label) in tradeoff if state == "t"}
    assert pareto(terminal_labels) == {(F(1), F(3)), (F(3), F(1))}
    impossible_budget = reachable_labels(("s", "t"), tradeoff_edges, ("s",), (F(2), F(2)))
    assert all(state != "t" for (state, _) in impossible_budget)
    assert (F(1), F(1)) not in terminal_labels

    fractional = reachable_labels(("s",), (("s", "s", (F(1, 2),)),),
                                  ("s",), (F(1),))
    assert fractional == {("s", (F(0),)): 0, ("s", (F(1, 2),)): 1,
                          ("s", (F(1),)): 2}
    return {"zero_loop_distinct_history_prefix": len(paths),
            "zero_loop_state_labels": len(closure),
            "nondominated_terminal_cost_labels": [[1, 3], [3, 1]],
            "coordinatewise_minimum_is_attainable": False,
            "fractional_state_label_count": len(fractional)}


def delayed_halting_interval(halt_step, precision_steps):
    """Finite delayed-halt model for x=2^-t; None denotes no halt.

    This is not a halting decider. Only the first precision_steps are inspected.
    """
    if halt_step is not None and halt_step <= precision_steps:
        value = F(1, 2 ** halt_step)
        return value, value
    return F(0), F(1, 2 ** precision_steps)


def computable_real_boundary_checks():
    checks = indistinguishable = 0
    for precision in range(1, 33):
        for halt_step in (None,) + tuple(range(1, 34)):
            interval = delayed_halting_interval(halt_step, precision)
            actual = F(0) if halt_step is None else F(1, 2 ** halt_step)
            assert interval[0] <= actual <= interval[1]
            assert interval[1] - interval[0] <= F(1, 2 ** precision)
            checks += 1
        never = delayed_halting_interval(None, precision)
        delayed = delayed_halting_interval(precision + 1, precision)
        assert never == delayed and never[0] == 0 < never[1]
        indistinguishable += 1
    return {"certified_interval_cases": checks,
            "finite_precision_zero_versus_later_halt_pairs": indistinguishable,
            "scope": "finite_delayed_halt_witnesses; undecidability_requires_analytic_reduction"}


def realization_universe_boundary_checks():
    # M_n all emit the singleton protected trace (0,), but carry resource n.
    # Prefixes witness injective resource profiles; infinitude is analytical.
    response = (0,)
    cardinality_checks = 0
    for maximum_cost in range(65):
        profiles = {(response, F(cost)) for cost in range(maximum_cost + 1)}
        assert len({trace for trace, _ in profiles}) == 1
        assert len(profiles) == maximum_cost + 1
        assert pareto({(cost,) for _, cost in profiles}) == {(F(0),)}
        cardinality_checks += 1
    bounded = {(response, F(cost)) for cost in range(65) if cost <= 6}
    assert len(bounded) == 7
    # A finite register explicitly makes fiber enumeration finite; the
    # response/profile equivalence does not choose one candidate identity.
    register = {f"candidate_{index}": (response, F(1)) for index in range(65)}
    fiber = [name for name, profile in register.items() if profile == (response, F(1))]
    assert len(set(register.values())) == 1 and len(fiber) == 65
    return {"same_response_growing_profile_prefixes": cardinality_checks,
            "largest_prefix_response_classes": 1,
            "largest_prefix_resource_profiles": 65,
            "finite_grid_budget_six_profiles": len(bounded),
            "same_profile_registered_fiber_size": len(fiber),
            "scope": "finite_prefixes_and_finite_register; infinite_universe_counterexample_is_analytic"}


def run():
    return {"terminal": "GMI_OPERATIONAL_REACHABILITY_CORRECTION_GREEN_AT_FINITE_SCOPE",
            "determinism": "exact_rational_no_rng",
            "frontier_restriction": frontier_restriction_checks(),
            "graph_closure": graph_closure_checks(),
            "cycle_and_cost_labels": zero_cycle_and_cost_tradeoff_checks(),
            "computable_real_boundary": computable_real_boundary_checks(),
            "realization_universe_boundary": realization_universe_boundary_checks(),
            "boundary": "finite registered machines and decidable exact comparisons; no all-history or unrestricted-computability closure"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
