#!/usr/bin/env python3
"""Exact finite checks for Grand GMI strategic multi-agent theorem V1.

Deterministic exhaustive checks only. No RNG or floating-point thresholds.
"""

from __future__ import annotations

import json
from collections import defaultdict
from itertools import product


def pure_nash(loss0, loss1):
    out = []
    for a0, a1 in product(range(2), repeat=2):
        idx = 2 * a0 + a1
        br0 = loss0[idx] <= loss0[2 * (1 - a0) + a1]
        br1 = loss1[idx] <= loss1[2 * a0 + (1 - a1)]
        if br0 and br1:
            out.append((a0, a1))
    return tuple(out)


def check_local_obligation_equilibrium():
    values = (0, 1, 2)
    games = 0
    equilibrium_profiles = 0
    no_pure = 0
    unique_pure = 0
    for loss0 in product(values, repeat=4):
        for loss1 in product(values, repeat=4):
            expected = pure_nash(loss0, loss1)
            local = []
            for a0, a1 in product(range(2), repeat=2):
                idx = 2 * a0 + a1
                ok0 = all(loss0[idx] <= loss0[2 * d + a1] for d in range(2))
                ok1 = all(loss1[idx] <= loss1[2 * a0 + d] for d in range(2))
                if ok0 and ok1:
                    local.append((a0, a1))
            assert tuple(local) == expected
            games += 1
            equilibrium_profiles += len(expected)
            no_pure += int(not expected)
            unique_pure += int(len(expected) == 1)
    return {
        "games": games,
        "equilibrium_profiles": equilibrium_profiles,
        "games_without_pure_equilibrium": no_pure,
        "games_with_unique_pure_equilibrium": unique_pure,
        "all_exact": True,
    }


def partition(rows, columns):
    groups = defaultdict(set)
    for i, row in enumerate(rows):
        groups[tuple(row[:columns])].add(i)
    return list(groups.values())


def check_strategic_semantic_refinement():
    checks = 0
    matrices = 0
    for bits in product((0, 1), repeat=16):
        rows = [bits[4 * i : 4 * (i + 1)] for i in range(4)]
        matrices += 1
        for columns in range(1, 4):
            coarse = partition(rows, columns)
            fine = partition(rows, columns + 1)
            assert all(any(fine_class <= coarse_class for coarse_class in coarse) for fine_class in fine)
            assert len(fine) >= len(coarse)
            checks += 1
    return {"response_matrices": matrices, "refinement_checks": checks, "all_exact": True}


def check_ecology_robust_nonexistence():
    # e0: both players have strictly dominant action 0.
    e0_loss0 = (0, 0, 1, 1)
    e0_loss1 = (0, 1, 0, 1)
    # e1: both players have strictly dominant action 1.
    e1_loss0 = (1, 1, 0, 0)
    e1_loss1 = (1, 0, 1, 0)
    eq0 = pure_nash(e0_loss0, e0_loss1)
    eq1 = pure_nash(e1_loss0, e1_loss1)
    intersection = sorted(set(eq0) & set(eq1))
    assert eq0 == ((0, 0),)
    assert eq1 == ((1, 1),)
    assert intersection == []
    return {
        "ecology_0_equilibria": [list(x) for x in eq0],
        "ecology_1_equilibria": [list(x) for x in eq1],
        "intersection": intersection,
        "all_exact": True,
    }


def count_signaling_protocols(message_symbols):
    successful = 0
    total = 0
    for sender in product(range(message_symbols), repeat=2):
        for receiver in product(range(2), repeat=message_symbols):
            total += 1
            if all(receiver[sender[x]] == x for x in range(2)):
                successful += 1
    return successful, total


def check_semantic_signaling_cut():
    one_success, one_total = count_signaling_protocols(1)
    two_success, two_total = count_signaling_protocols(2)
    assert one_success == 0
    assert two_success > 0
    return {
        "one_symbol": {"successful": one_success, "total": one_total},
        "two_symbols": {"successful": two_success, "total": two_total},
        "minimum_message_symbols": 2,
        "minimum_bits": 1,
        "all_exact": True,
    }


def run_all():
    result = {
        "schema": "GRAND_GMI_STRATEGIC_CHECKS_V1",
        "local_obligation_equilibrium": check_local_obligation_equilibrium(),
        "strategic_semantic_refinement": check_strategic_semantic_refinement(),
        "ecology_robust_nonexistence": check_ecology_robust_nonexistence(),
        "semantic_signaling_cut": check_semantic_signaling_cut(),
    }
    result["terminal"] = "GRAND_GMI_STRATEGIC_MULTIAGENT_TRANCHE_ALL_GREEN"
    return result


if __name__ == "__main__":
    print(json.dumps(run_all(), indent=2, sort_keys=True))
