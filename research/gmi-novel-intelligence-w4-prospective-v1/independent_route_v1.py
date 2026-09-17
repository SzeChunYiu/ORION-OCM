#!/usr/bin/env python3
"""Independent verification route for the W4 prospective replication.

Imports NEITHER the upstream V6 witness NOR the parent W4 executor: every
quantity is recomputed from the ecology pair (q_p, q_o) by direct
combinatorics (fiber-multiplicity counting, first-occurrence canonical
labeling, pigeonhole bounds) with code paths deliberately distinct from the
V6 implementation (per-fiber partition refinement instead of a global
decoder dict). Exact agreement between the two routes is freeze requirement
D4 of FREEZE_V2_PROSPECTIVE.json.

Py3.8-safe, stdlib-only.
"""
from __future__ import annotations

import itertools
from typing import Dict, List, Sequence, Tuple

Partition = Tuple[int, ...]

# Registered brute-force witness budget: enumerate all residual assignments
# over alphabet m-1 only where the tuple count is at most this (freeze rule:
# (m-1)^(2k) <= 2^20).
WITNESS_TUPLE_BUDGET = 1 << 20


def fibers(q_p, q_o):
    # type: (Partition, Partition) -> List[Tuple[int, List[int]]]
    if len(q_p) != len(q_o):
        raise ValueError("partition length mismatch")
    by_p = {}  # type: Dict[int, List[int]]
    for idx, p in enumerate(q_p):
        by_p.setdefault(p, []).append(idx)
    return [(p, hs) for p, hs in sorted(by_p.items())]


def max_multiplicity_direct(q_p, q_o):
    # type: (Partition, Partition) -> int
    """max_m = largest number of distinct target labels inside one fiber."""
    best = 0
    for _, hs in fibers(q_p, q_o):
        best = max(best, len({q_o[h] for h in hs}))
    return best


def canonical_cost_direct(q_p, q_o):
    # type: (Partition, Partition) -> Dict[str, int]
    """First-occurrence canonical labeling: per fiber, rank targets 0,1,2,...;
    the global residual alphabet is the largest per-fiber rank set, so
    |range(R)| = max_m and C* = |distinct p| + max_m."""
    p_size = len(set(q_p))
    r_span = 0
    for _, hs in fibers(q_p, q_o):
        rank = {}  # type: Dict[int, int]
        for h in hs:
            target = q_o[h]
            if target not in rank:
                rank[target] = len(rank)
        r_span = max(r_span, len(rank))
    return {"p_size": p_size, "r_size": r_span, "cost": p_size + r_span}


def flat_table_cost_direct(q_o):
    # type: (Partition) -> int
    return 1 + len(set(q_o))


def assignment_consistent(q_p, q_o, r_assign):
    # type: (Partition, Partition, Sequence[int]) -> bool
    """Decoder consistency, per-fiber form: within each fiber, the residual
    symbol must be injective across distinct targets (equal targets may share
    a symbol; distinct targets within a fiber may not)."""
    for _, hs in fibers(q_p, q_o):
        seen = {}  # type: Dict[int, int]
        for h in hs:
            sym = r_assign[h]
            if sym in seen:
                if seen[sym] != q_o[h]:
                    return False
            else:
                seen[sym] = q_o[h]
    return True


def residual_exact_exists_pigeonhole(q_p, q_o, r_cap):
    # type: (Partition, Partition, int) -> bool
    """Pigeonhole both directions: some exact residual decoder over an
    alphabet of size <= r_cap exists iff r_cap >= max_m (a fiber with m
    distinct targets needs m distinct symbols; the canonical labeling never
    needs more than max_m)."""
    return r_cap >= max_multiplicity_direct(q_p, q_o)


def brute_force_no_decoder_below_m(q_p, q_o):
    # type: (Partition, Partition) -> Dict[str, object]
    """Witness: exhaustively enumerate every residual assignment over the
    alphabet {0..m-2} (m > 1) and confirm none is decoder-consistent --
    a direct empirical check of the PRQ-1 lower bound that the V6 route only
    short-circuits by theorem. Runs solely under the registered tuple budget.
    """
    m = max_multiplicity_direct(q_p, q_o)
    n = len(q_o)
    if m <= 1:
        return {
            "m": m,
            "witness_run": False,
            "reason": "m<=1: no below-m alphabet exists",
            "tuples_enumerated": 0,
            "consistent_found": 0,
        }
    tuples = (m - 1) ** n
    if tuples > WITNESS_TUPLE_BUDGET:
        return {
            "m": m,
            "witness_run": False,
            "reason": "budget: (m-1)^n = %d > %d" % (tuples, WITNESS_TUPLE_BUDGET),
            "tuples_enumerated": 0,
            "consistent_found": 0,
        }
    found = 0
    seen_tuples = 0
    for r_assign in itertools.product(range(m - 1), repeat=n):
        seen_tuples += 1
        if assignment_consistent(q_p, q_o, r_assign):
            found += 1
    return {
        "m": m,
        "witness_run": True,
        "reason": "exhaustive over alphabet m-1",
        "tuples_enumerated": seen_tuples,
        "consistent_found": found,
        "no_decoder_below_m": found == 0,
    }


def ecology_properties(q_p, q_o, fixed_budget_B):
    # type: (Partition, Partition, int) -> Dict[str, object]
    """All registered shared quantities, this route only."""
    m = max_multiplicity_direct(q_p, q_o)
    canon = canonical_cost_direct(q_p, q_o)
    if canon["r_size"] != m:
        raise AssertionError("canonical r_size %s != max_m %s" % (canon["r_size"], m))
    return {
        "max_m": m,
        "C_star": canon["cost"],
        "flat": flat_table_cost_direct(q_o),
        "needs_residual": m > 1,
        "pure_predictor_succeeds": m <= 1,
        "fixed_budget_recovers": residual_exact_exists_pigeonhole(q_p, q_o, fixed_budget_B),
        "canonical_r_size": canon["r_size"],
    }
