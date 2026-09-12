#!/usr/bin/env python3
"""Exact finite checks for Grand GMI planning semantic-resolution V1."""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from itertools import product
from pathlib import Path


@lru_cache(maxsize=None)
def min_label_queries(class_sizes):
    """Independent minimax DP for equality-to-item queries identifying only a class."""
    sizes = tuple(sorted((x for x in class_sizes if x > 0), reverse=True))
    if len(sizes) <= 1:
        return 0
    best = None
    for value in set(sizes):
        nxt = list(sizes)
        nxt[nxt.index(value)] -= 1
        nxt = tuple(sorted((x for x in nxt if x > 0), reverse=True))
        candidate = 1 + min_label_queries(nxt)
        best = candidate if best is None else min(best, candidate)
    return best


def class_query_checks():
    cases = 0
    exact = 0
    for k in range(2, 6):
        for sizes in product(range(1, 5), repeat=k):
            cases += 1
            dp = min_label_queries(tuple(sizes))
            formula = sum(sizes) - max(sizes)
            if dp == formula:
                exact += 1
    return {"cases": cases, "formula_exact": exact}


def prefix_tree_checks():
    cases = 0
    exact = 0
    rows = []
    # Independent minimax DP on small cells. The theorem itself is general finite b,d,q.
    for b in (2, 3):
        for d in range(1, 4):
            total = b ** d
            for q in range(0, d + 1):
                classes = b ** q
                per_class = b ** (d - q)
                dp = min_label_queries(tuple([per_class] * classes))
                formula = total - per_class
                cases += 1
                exact += dp == formula
                rows.append(
                    {
                        "branching": b,
                        "depth": d,
                        "prefix_resolution": q,
                        "semantic_classes": classes,
                        "class_size": per_class,
                        "dp_queries": dp,
                        "formula_queries": formula,
                    }
                )
    return {"cases": cases, "formula_exact": exact, "rows": rows}


def quotient_dp(m, horizon):
    actions = (0, 1)

    @lru_cache(maxsize=None)
    def win(state, steps):
        if steps == 0:
            return state == 0
        return any(win((state + a) % m, steps - 1) for a in actions)

    values = {}
    first_actions = {}
    for steps in range(horizon + 1):
        for state in range(m):
            values[(state, steps)] = win(state, steps)
            if steps:
                first_actions[(state, steps)] = tuple(
                    a for a in actions if win((state + a) % m, steps - 1)
                )
    return values, first_actions


def brute_planning(m, state, steps):
    if steps == 0:
        return state == 0, ()
    winning_first = set()
    any_win = False
    for seq in product((0, 1), repeat=steps):
        terminal = state
        for a in seq:
            terminal = (terminal + a) % m
        if terminal == 0:
            any_win = True
            winning_first.add(seq[0])
    return any_win, tuple(sorted(winning_first))


def semantic_state_planning_checks():
    value_checks = 0
    action_checks = 0
    value_exact = 0
    action_exact = 0
    for m in range(2, 7):
        values, first = quotient_dp(m, 8)
        for steps in range(0, 9):
            for state in range(m):
                brute_value, brute_actions = brute_planning(m, state, steps)
                value_checks += 1
                value_exact += values[(state, steps)] == brute_value
                if steps:
                    action_checks += 1
                    action_exact += first[(state, steps)] == brute_actions
    return {
        "value_checks": value_checks,
        "value_exact": value_exact,
        "first_action_checks": action_checks,
        "first_action_exact": action_exact,
        "binary_depth12_raw_histories": 2 ** 12,
        "binary_depth12_raw_tree_nodes": 2 ** 13 - 1,
        "binary_mod2_semantic_states": 2,
    }


def run():
    class_checks = class_query_checks()
    prefix = prefix_tree_checks()
    quotient = semantic_state_planning_checks()
    ok = class_checks == {"cases": 1360, "formula_exact": 1360}
    ok = ok and prefix["cases"] == 18 and prefix["formula_exact"] == 18
    ok = ok and quotient["value_checks"] == 180 and quotient["value_exact"] == 180
    ok = ok and quotient["first_action_checks"] == 160 and quotient["first_action_exact"] == 160
    canonical = {
        "branching": 2,
        "depth": 10,
        "prefix_resolution": 1,
        "output_bits": 1,
        "leaf_verifier_queries": 2 ** 10 - 2 ** 9,
    }
    ok = ok and canonical["leaf_verifier_queries"] == 512
    return {
        "terminal": (
            "GRAND_GMI_PLANNING_RESOLUTION_TRANCHE_ALL_GREEN"
            if ok
            else "GRAND_GMI_PLANNING_RESOLUTION_TRANCHE_RED"
        ),
        "all_checks_green": ok,
        "determinism": "exact-exhaustive-no-rng",
        "class_query_theorem": class_checks,
        "prefix_tree": prefix,
        "semantic_state_planning": quotient,
        "canonical_exponential_first_action_witness": canonical,
    }


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
