#!/usr/bin/env python3
"""Exact Section-D witness: NFL symmetry control + structure-conditioned morphology law.

This script is downstream of FREEZE_V1.md commit 3fc4ddb2af98f738e5898a63488341c0d11f4364.
All headline predictions were frozen before this file existed.

Stdlib only. Exact integer/Fraction arithmetic. No randomness.
"""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_PATH = HERE / "RESULT_V1.json"


def frac(x):
    return str(Fraction(x))


# ---------------------------------------------------------------------------
# 1. NFL control and structured free lunch
# ---------------------------------------------------------------------------

X8 = tuple(range(8))
LOW = tuple(range(8))
HIGH = tuple(reversed(range(8)))


def best_seen(values, order, q):
    return max(values[i] for i in order[:q])


def nfl_control():
    rows = []
    all_functions = list(itertools.product((0, 1), repeat=8))
    for q in range(1, 9):
        dist_low = {"0": 0, "1": 0}
        dist_high = {"0": 0, "1": 0}
        for f in all_functions:
            dist_low[str(best_seen(f, LOW, q))] += 1
            dist_high[str(best_seen(f, HIGH, q))] += 1
        mean_low = Fraction(dist_low["1"], len(all_functions))
        mean_high = Fraction(dist_high["1"], len(all_functions))
        assert dist_low == dist_high
        assert mean_low == mean_high
        rows.append({
            "q": q,
            "low_distribution": dist_low,
            "high_distribution": dist_high,
            "mean": frac(mean_low),
        })
    return rows


def up_world(t):
    return tuple(int(x >= t) for x in X8)


def down_world(t):
    return tuple(int(x <= t) for x in X8)


def structured_free_lunch():
    ups = [up_world(t) for t in range(0, 9)]
    downs = [down_world(t) for t in range(-1, 8)]

    def mean_first(order, family):
        return Fraction(sum(f[order[0]] for f in family), len(family))

    up_low = mean_first(LOW, ups)
    up_high = mean_first(HIGH, ups)
    down_low = mean_first(LOW, downs)
    down_high = mean_first(HIGH, downs)

    constant_low = (up_low + down_low) / 2
    constant_high = (up_high + down_high) / 2
    conditioned = (up_high + down_low) / 2
    gap = conditioned - min(constant_low, constant_high)

    assert up_low == Fraction(1, 9)
    assert up_high == Fraction(8, 9)
    assert down_low == Fraction(8, 9)
    assert down_high == Fraction(1, 9)
    assert constant_low == constant_high == Fraction(1, 2)
    assert conditioned == Fraction(8, 9)
    assert gap == Fraction(7, 18)

    # Explicit permutation-closure hostile. The union of UP/DOWN worlds is not
    # closed under arbitrary permutation of the input domain. Swap 3 and 4 in
    # UP_4: 00111000, which is neither a suffix nor a prefix threshold.
    structured = set(ups + downs)
    f = list(up_world(4))
    p = list(range(8))
    p[3], p[4] = p[4], p[3]
    permuted = tuple(f[p[i]] for i in range(8))
    assert permuted not in structured

    return {
        "up_low": frac(up_low),
        "up_high": frac(up_high),
        "down_low": frac(down_low),
        "down_high": frac(down_high),
        "best_constant": frac(constant_low),
        "conditioned": frac(conditioned),
        "free_lunch_gap": frac(gap),
        "structured_class_closed_under_all_input_permutations": False,
        "closure_counterexample": {
            "source": list(up_world(4)),
            "swap": [3, 4],
            "permuted": list(permuted),
        },
    }


# ---------------------------------------------------------------------------
# 2. Finite decision theorem exhaustive checker
# ---------------------------------------------------------------------------


def decision_value_of_information_examples():
    """Exhaust small integer loss tables and verify the frozen theorem.

    W has four equiprobable worlds partitioned into Z={0,1}, two worlds each.
    Three morphologies, losses in {0,1,2}. Exhausting all 3^(3*4)=531,441
    tables is still small and validates both inequality and strictness iff the
    positive-mass conditional argmin sets have empty intersection.
    """
    checked = 0
    strict = 0
    equality = 0
    for flat in itertools.product(range(3), repeat=12):
        loss = [flat[4*m:4*(m+1)] for m in range(3)]
        global_sums = [sum(row) for row in loss]
        r0_num = min(global_sums)  # denominator 4

        cond_sets = []
        rz_num = 0
        for worlds in ((0, 1), (2, 3)):
            sums = [sum(loss[m][w] for w in worlds) for m in range(3)]
            best = min(sums)
            rz_num += best  # denominator 4 overall
            cond_sets.append({m for m, s in enumerate(sums) if s == best})

        assert rz_num <= r0_num
        common = set.intersection(*cond_sets)
        is_strict = rz_num < r0_num
        assert is_strict == (not common)
        checked += 1
        strict += int(is_strict)
        equality += int(not is_strict)

    assert checked == 3 ** 12
    return {"tables_checked": checked, "strict": strict, "equality": equality}


# ---------------------------------------------------------------------------
# 3. Morphology grammar and architecture-neutral structural signature
# ---------------------------------------------------------------------------

N = 5
X5 = tuple(itertools.product((0, 1), repeat=N))
SIZE = 2 ** N
BIT_PERM = (2, 4, 1, 0, 3)


def world_A(x):
    return x[0] ^ x[2] ^ x[4]


def world_B(x):
    return int(tuple(x) == (1, 0, 1, 0, 1))


def world_C(x):
    return int(sum(x) >= 3)


def world_D(x):
    y = int(sum(x) >= 3)
    if tuple(x) == (0, 0, 0, 0, 0):
        y ^= 1
    return y


WORLD_FNS = {
    "W-A": world_A,
    "W-B": world_B,
    "W-C": world_C,
    "W-D": world_D,
}

FROZEN_Q = 16
FROZEN_BUDGET = 8


def truth(fn):
    return tuple(fn(x) for x in X5)


def anf_coefficients(values):
    a = list(values)
    for bit_index in range(N):
        bit = 1 << (N - 1 - bit_index)
        for mask in range(SIZE):
            if mask & bit:
                a[mask] ^= a[mask ^ bit]
    return tuple(a)


def algebraic_signature(values):
    coeffs = anf_coefficients(values)
    degree = 0
    singleton_support = 0
    for mask, c in enumerate(coeffs):
        if not c:
            continue
        d = mask.bit_count()
        degree = max(degree, d)
        if d == 1:
            singleton_support += 1
    return degree, singleton_support


def count_step_residual(values):
    best = None
    for polarity in ("down", "up"):
        for cut in range(-1, N + 2):
            pred = []
            for x in X5:
                w = sum(x)
                pred.append(int(w <= cut) if polarity == "down" else int(w >= cut))
            errors = sum(a != b for a, b in zip(values, pred))
            key = (errors, polarity, cut)
            if best is None or key < best:
                best = key
    return best


def structural_signature(values):
    degree, support = algebraic_signature(values)
    ones = sum(values)
    minority = min(ones, SIZE - ones)
    step_errors, polarity, cut = count_step_residual(values)
    return {
        "algebraic_degree": degree,
        "algebraic_support_size_if_degree_le_1": support if degree <= 1 else None,
        "minority_count": minority,
        "best_hamming_weight_step_residual": step_errors,
        "best_step_polarity": polarity,
        "best_step_cut": cut,
    }


def candidates(values, q, memory_budget):
    sig = structural_signature(values)
    degree = sig["algebraic_degree"]
    support = sig["algebraic_support_size_if_degree_le_1"]
    k = sig["minority_count"]
    e = sig["best_hamming_weight_step_residual"]

    raw = [
        {"name": "full_map", "exact": True, "memory": SIZE, "description": SIZE, "serve": 1},
        {
            "name": "xor_fold",
            "exact": degree <= 1,
            "memory": (1 + support) if degree <= 1 else None,
            "description": (1 + support) if degree <= 1 else None,
            "serve": support if degree <= 1 else None,
        },
        {"name": "default_exceptions", "exact": True, "memory": 1 + k, "description": 1 + k, "serve": 2},
        {"name": "count_step", "exact": e == 0, "memory": 2 if e == 0 else None, "description": 2 if e == 0 else None, "serve": N if e == 0 else None},
        {"name": "count_step_plus_exceptions", "exact": True, "memory": 2 + e, "description": 2 + e, "serve": N + 1},
    ]

    out = []
    for row in raw:
        r = dict(row)
        r["within_memory_budget"] = bool(r["exact"] and r["memory"] <= memory_budget)
        r["feasible"] = r["within_memory_budget"]
        if r["feasible"]:
            r["verification"] = SIZE
            r["lifecycle_ops"] = r["description"] + SIZE + q * r["serve"]
            r["resource_vector"] = [r["memory"], r["lifecycle_ops"]]
        else:
            r["verification"] = SIZE if r["exact"] else None
            r["lifecycle_ops"] = None
            r["resource_vector"] = None
        out.append(r)
    return out


def dominates_vec(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def frontier_all_pairs(rows):
    feasible = [r for r in rows if r["feasible"]]
    return sorted(
        [r["name"] for r in feasible if not any(
            dominates_vec(o["resource_vector"], r["resource_vector"])
            for o in feasible if o["name"] != r["name"]
        )]
    )


def frontier_incremental(rows):
    # Deliberately different implementation and reverse candidate order.
    skyline = []
    for r in reversed([r for r in rows if r["feasible"]]):
        if any(dominates_vec(s["resource_vector"], r["resource_vector"]) for s in skyline):
            continue
        skyline = [s for s in skyline if not dominates_vec(r["resource_vector"], s["resource_vector"])]
        skyline.append(r)
    return sorted(r["name"] for r in skyline)


def remint_values(fn):
    # y'(x) = y(x_pi): coordinate names change while Hamming geometry is kept.
    def renamed(x):
        old_x = tuple(x[i] for i in BIT_PERM)
        return fn(old_x)
    return truth(renamed)


FROZEN_UNIQUE = {
    "W-A": ["xor_fold"],
    "W-B": ["default_exceptions"],
    "W-C": ["count_step"],
    "W-D": ["count_step_plus_exceptions"],
}

FROZEN_PHASES = {
    "W-A": [
        (1, 13, ["xor_fold"]),
        (14, 15, ["default_exceptions", "xor_fold"]),
        (16, 40, ["default_exceptions", "full_map", "xor_fold"]),
    ],
    "W-B": [
        (1, 30, ["default_exceptions"]),
        (31, 40, ["default_exceptions", "full_map"]),
    ],
    "W-C": [
        (1, 5, ["count_step"]),
        (6, 15, ["count_step", "default_exceptions"]),
        (16, 40, ["count_step", "default_exceptions", "full_map"]),
    ],
    "W-D": [
        (1, 3, ["count_step_plus_exceptions"]),
        (4, 16, ["count_step_plus_exceptions", "default_exceptions"]),
        (17, 40, ["count_step_plus_exceptions", "default_exceptions", "full_map"]),
    ],
}


def expected_frontier(world, q):
    for lo, hi, names in FROZEN_PHASES[world]:
        if lo <= q <= hi:
            return sorted(names)
    raise AssertionError((world, q))


def morphology_phase_witness():
    worlds_out = {}
    coarse_frontiers = []

    for name, fn in WORLD_FNS.items():
        values = truth(fn)
        sig = structural_signature(values)
        rows = candidates(values, FROZEN_Q, FROZEN_BUDGET)
        f1 = frontier_all_pairs(rows)
        f2 = frontier_incremental(rows)
        assert f1 == f2
        assert f1 == sorted(FROZEN_UNIQUE[name]), (name, f1)
        coarse_frontiers.append(tuple(f1))

        reminted = remint_values(fn)
        rsig = structural_signature(reminted)
        rrows = candidates(reminted, FROZEN_Q, FROZEN_BUDGET)
        rf1 = frontier_all_pairs(rrows)
        rf2 = frontier_incremental(rrows)
        assert rf1 == rf2 == f1

        # Invariants expected to survive coordinate renaming.
        assert rsig["algebraic_degree"] == sig["algebraic_degree"]
        assert rsig["algebraic_support_size_if_degree_le_1"] == sig["algebraic_support_size_if_degree_le_1"]
        assert rsig["minority_count"] == sig["minority_count"]
        assert rsig["best_hamming_weight_step_residual"] == sig["best_hamming_weight_step_residual"]

        for q in range(1, 41):
            rr = candidates(values, q, 64)
            a = frontier_all_pairs(rr)
            b = frontier_incremental(rr)
            assert a == b
            exp = expected_frontier(name, q)
            assert a == exp, (name, q, a, exp)

        worlds_out[name] = {
            "signature": sig,
            "frontier_Q16_mem8": f1,
            "remint_signature": rsig,
            "remint_frontier_Q16_mem8": rf1,
            "phase_Q1_40_mem64": [
                {"Q_min": lo, "Q_max": hi, "frontier": sorted(names)}
                for lo, hi, names in FROZEN_PHASES[name]
            ],
            "phase_cells_checked": 40,
        }

    # Same coarse n/Q/budget/verifier/history coordinates but different frontiers.
    assert len(set(coarse_frontiers)) == 4
    common = set(FROZEN_UNIQUE["W-A"])
    for n in ("W-B", "W-C", "W-D"):
        common &= set(FROZEN_UNIQUE[n])
    assert not common

    # The registered structural signatures must all differ and therefore can
    # separate the decisions without family labels.
    sig_keys = []
    for name in WORLD_FNS:
        s = worlds_out[name]["signature"]
        sig_keys.append((
            s["algebraic_degree"],
            s["algebraic_support_size_if_degree_le_1"],
            s["minority_count"],
            s["best_hamming_weight_step_residual"],
        ))
    assert len(set(sig_keys)) == 4

    return {
        "coarse_coordinates": {
            "n": N,
            "Q": FROZEN_Q,
            "memory_budget": FROZEN_BUDGET,
            "verifier": "exhaustive_truth_table_32",
            "developmental_history": "none",
        },
        "coarse_map_has_four_distinct_frontiers": True,
        "common_morphology_across_all_four_frontiers": [],
        "structural_signatures_distinct": True,
        "worlds": worlds_out,
    }


def main():
    out = {
        "schema": "GMI_SECTION_D_FREE_LUNCH_V1",
        "freeze_commit": "3fc4ddb2af98f738e5898a63488341c0d11f4364",
        "nfl_control": nfl_control(),
        "structured_free_lunch": structured_free_lunch(),
        "decision_theorem_exhaustion": decision_value_of_information_examples(),
        "morphology_phase": morphology_phase_witness(),
        "terminal": [
            "NFL_SYMMETRY_CONTROL_REPRODUCED",
            "STRICT_FREE_LUNCH_FROM_REGISTERED_STRUCTURE_SUPPORTED",
            "COARSE_D_MAP_FALSIFIED_AND_STRUCTURAL_REPAIR_SUPPORTED_AT_FINITE_SCOPE",
            "PROSPECTIVE_PHASE_BOUNDARIES_CONFIRMED_AS_FROZEN",
        ],
    }
    OUT_PATH.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "nfl_rows": len(out["nfl_control"]),
        "free_lunch_gap": out["structured_free_lunch"]["free_lunch_gap"],
        "decision_tables": out["decision_theorem_exhaustion"]["tables_checked"],
        "worlds": {k: v["frontier_Q16_mem8"] for k, v in out["morphology_phase"]["worlds"].items()},
        "terminal": out["terminal"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
