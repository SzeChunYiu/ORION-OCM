#!/usr/bin/env python3
"""Independent finite policy oracles for proof search and static reuse."""
from __future__ import annotations

import argparse
from functools import lru_cache
from fractions import Fraction
from itertools import product
import json
from pathlib import Path


def natural(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def query_tree_value(n, promise):
    natural(n, "candidate count", 1)
    if type(promise) is not bool:
        raise ValueError("promise must be Boolean")
    worlds = tuple(range(n)) if promise else tuple(range(-1, n))
    labels = {w: w if promise else w >= 0 for w in worlds}

    @lru_cache(None)
    def solve(possible):
        if len({labels[w] for w in possible}) == 1:
            return 0
        costs = []
        for query in range(n):
            cells = tuple(tuple(w for w in possible if (w == query) == bit)
                          for bit in (False, True))
            if all(cells):
                costs.append(1 + max(solve(cell) for cell in cells))
        if not costs:
            raise ValueError("target not identifiable by registered queries")
        return min(costs)

    return solve(worlds)


def request_schedule_cost(c, s, u, r):
    """Enumerate request actions; unlike the formula, admission may be delayed."""
    for name, value in (("derive", c), ("store", s), ("reuse", u)):
        natural(value, name)
    natural(r, "requests", 1)
    states = {(False, 0)}
    for _ in range(r):
        next_states = set()
        for retained, cost in states:
            next_states.add((retained, cost + c))
            if retained:
                next_states.add((True, cost + u))
            else:
                next_states.add((True, cost + c + s))
        states = next_states
    return min(cost for _, cost in states)


def capacity_solution(items, capacity):
    """Rows (C,S,U,r,size); return exact cost and selected indices via parent DP."""
    natural(capacity, "capacity")
    for row in items:
        if len(row) != 5:
            raise ValueError("expected C,S,U,r,size")
        for i, value in enumerate(row):
            natural(value, "item coordinate", 1 if i >= 3 else 0)
    table = [(0, ()) for _ in range(capacity + 1)]
    baseline = sum(c * r for c, s, u, r, size in items)
    for j, (c, s, u, r, size) in enumerate(items):
        gain = (r - 1) * (c - u) - s
        old = table
        table = old.copy()
        for b in range(size, capacity + 1):
            candidate = (old[b - size][0] + gain, old[b - size][1] + (j,))
            if candidate[0] > old[b][0]:
                table[b] = candidate
    gain, selected = table[capacity]
    return baseline - gain, selected


def subset_execution_cost(items, capacity):
    """Independent oracle: run each feasible static admission subset."""
    costs = []
    for chosen in product((False, True), repeat=len(items)):
        if sum(row[4] for row, keep in zip(items, chosen) if keep) > capacity:
            continue
        cost = 0
        for (c, s, u, r, size), keep in zip(items, chosen):
            for request in range(r):
                cost += c if not keep or request == 0 else u
                if keep and request == 0:
                    cost += s
        costs.append(cost)
    return min(costs)


def greedy_execution(items, capacity, density):
    gains = [(r - 1) * (c - u) - s for c, s, u, r, size in items]
    key = lambda j: Fraction(gains[j], items[j][4]) if density else gains[j]
    remaining, selected = capacity, []
    for j in sorted(range(len(items)), key=key, reverse=True):
        if gains[j] > 0 and items[j][4] <= remaining:
            selected.append(j)
            remaining -= items[j][4]
    cost = 0
    for j, (c, s, u, r, size) in enumerate(items):
        for request in range(r):
            cost += c if j not in selected or request == 0 else u
            if j in selected and request == 0:
                cost += s
    return cost, tuple(sorted(selected))


def run():
    search = [{"n": n, "existence": query_tree_value(n, False),
               "identification": query_tree_value(n, True)} for n in range(1, 9)]
    schedule_cases = schedule_matches = 0
    for c, s, u, r in product(range(5), range(4), range(5), range(1, 6)):
        schedule_cases += 1
        schedule_matches += request_schedule_cost(c, s, u, r) == min(
            r * c, c + s + (r - 1) * u)
    catalog = ((0, 0, 1, 3, 1), (2, 1, 0, 3, 2), (1, 3, 2, 2, 1),
               (3, 0, 1, 3, 3), (2, 0, 2, 2, 2))
    capacity_cases = capacity_matches = 0
    for items in product(catalog, repeat=3):
        for capacity in range(8):
            capacity_cases += 1
            cost, selected = capacity_solution(items, capacity)
            capacity_matches += cost == subset_execution_cost(items, capacity)
            if sum(items[j][4] for j in selected) > capacity:
                raise RuntimeError("constructed admission exceeds capacity")
    greedy_items = ((7, 0, 0, 2, 4), (5, 0, 0, 2, 3), (5, 0, 0, 2, 3))
    cost, selected = capacity_solution(greedy_items, 6)
    greedy_gain = greedy_execution(greedy_items, 6, False)
    greedy_density = greedy_execution(greedy_items, 6, True)
    verifier = lambda context, proof: context == proof
    solve = lambda context: context
    transported = lambda source, target, proof: target
    transport = {
        "solve_profiles_equal": verifier(0, solve(0)) == verifier(1, solve(1)),
        "raw_reuse_accepted": verifier(1, solve(0)),
        "transported_reuse_accepted": verifier(1, transported(0, 1, solve(0)))}
    ok = (all(row["existence"] == row["n"] and
              row["identification"] == row["n"] - 1 for row in search)
          and schedule_cases == schedule_matches and capacity_cases == capacity_matches
          and (cost, selected) == (24, (1, 2))
          and greedy_gain == greedy_density == (27, (0,))
          and transport == {"solve_profiles_equal": True,
                            "raw_reuse_accepted": False,
                            "transported_reuse_accepted": True})
    return {"terminal": "PROOF_SEARCH_REUSE_SCOPED_CHECKS_GREEN" if ok else "RED",
            "all_checks_green": ok, "search": search,
            "request_schedules": {"cases": schedule_cases, "matches": schedule_matches},
            "capacity": {"cases": capacity_cases, "matches": capacity_matches},
            "greedy_counterexample": {"optimal_cost": cost, "selected": list(selected),
                                      "greedy_gain_cost": greedy_gain[0],
                                      "greedy_density_cost": greedy_density[0]},
            "certificate_transport": transport}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    result = run()
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args = parser.parse_args()
    if args.out:
        args.out.write_text(output)
    print(output, end="")
    raise SystemExit(0 if result["all_checks_green"] else 1)
