#!/usr/bin/env python3
"""Finite exact witnesses for Grand GMI measurable/continuous boundary theorems."""

from fractions import Fraction as F
from itertools import combinations, product
import json


def pareto(points):
    pts = list(points)
    out = set()
    for p in pts:
        if not any(
            q != p
            and all(a <= b for a, b in zip(q, p))
            and any(a < b for a, b in zip(q, p))
            for q in pts
        ):
            out.add(p)
    return out


def check_compact_finite_witness():
    cube = list(product([0, 1], repeat=3))
    weights = (1, 2, 4)
    checks = 0
    for mask in range(1, 1 << len(cube)):
        y = [cube[i] for i in range(len(cube)) if (mask >> i) & 1]
        vals = [sum(w * c for w, c in zip(weights, p)) for p in y]
        best = min(vals)
        minimizers = [p for p, v in zip(y, vals) if v == best]
        frontier = pareto(y)
        assert all(p in frontier for p in minimizers)
        checks += 1
    return {
        "nonempty_binary_cube_subsets": checks,
        "positive_weight_minimizers_all_nondominated": True,
    }


def check_noncompact_frontier_boundary(nmax=256):
    successor_checks = 0
    for n in range(1, nmax + 1):
        y = F(1, n)
        z = F(1, n + 1)
        assert z < y
        successor_checks += 1

    prefix_minima = [F(1, n) for n in range(1, nmax + 1)]
    # For prefix {1,1/2,...,1/N}, minimum is 1/N and keeps strictly improving.
    for n in range(1, nmax):
        assert prefix_minima[n] < prefix_minima[n - 1]

    compactified = {(F(0),)} | {(F(1, n),) for n in range(1, nmax + 1)}
    assert pareto(compactified) == {(F(0),)}
    return {
        "successor_dominance_checks": successor_checks,
        "finite_prefix_minima_strictly_improve": True,
        "infinite_sequence_has_attained_infimum": False,
        "compactified_prefix_unique_pareto": "0",
    }


def cover_number_line_grid(n, radius_steps):
    # Grid {0,...,n}; metric is integer step distance. Centers restricted to grid.
    points = list(range(n + 1))
    for k in range(1, len(points) + 1):
        for centers in combinations(points, k):
            if all(any(abs(x - c) <= radius_steps for c in centers) for x in points):
                return k
    raise AssertionError("cover not found")


def check_cover_monotonicity():
    rows = []
    for n in (4, 8, 12):
        counts = [cover_number_line_grid(n, r) for r in (0, 1, 2, 3)]
        assert all(counts[i + 1] <= counts[i] for i in range(len(counts) - 1))
        rows.append({"grid_max": n, "cover_counts_radius_0_1_2_3": counts})
    return {"rows": rows, "larger_tolerance_never_increases_cover_number": True}


def check_infimum_vs_minimum():
    # An abstract lower-bound family R={1/n}. Exact infimum is 0, but 0 is not a member.
    sample = {F(1, n) for n in range(1, 101)}
    assert F(0) not in sample
    assert min(sample) == F(1, 100)
    return {
        "symbolic_family": "{1/n : n>=1}",
        "infimum": "0",
        "infimum_attained": False,
        "first_100_minimum": "1/100",
    }


def run():
    return {
        "terminal": "GRAND_GMI_MEASURABLE_CONTINUOUS_TRANCHE_ALL_GREEN",
        "compact_finite_witness": check_compact_finite_witness(),
        "noncompact_frontier_boundary": check_noncompact_frontier_boundary(),
        "cover_monotonicity": check_cover_monotonicity(),
        "infimum_minimum": check_infimum_vs_minimum(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
