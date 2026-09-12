#!/usr/bin/env python3
"""Exact finite checks for EMPIRICAL_RESOURCE_IDENTIFICATION_THEOREM_V1."""

import json


def robust_dominates(a, b):
    """Box a robustly dominates box b iff every a upper <= b lower and one strict."""
    weak = all(a_hi <= b_lo for (_, a_hi), (b_lo, _) in zip(a, b))
    strict = any(a_hi < b_lo for (_, a_hi), (b_lo, _) in zip(a, b))
    return weak and strict


def certified_feasible(interval, budget):
    return interval[1] <= budget


def certified_infeasible(interval, budget):
    return interval[0] > budget


def main():
    # A. clear neural robust domination.
    n_clear = [(2.0, 2.2), (3.0, 3.1)]
    p_clear = [(4.6, 5.1), (3.8, 4.2)]
    assert robust_dominates(n_clear, p_clear)
    assert not robust_dominates(p_clear, n_clear)

    # B. overlap requires abstention; two compatible point worlds reverse winner.
    n_amb = [(2.0, 4.0)]
    p_amb = [(3.0, 5.0)]
    assert not robust_dominates(n_amb, p_amb)
    assert not robust_dominates(p_amb, n_amb)
    world_neural = {"N": 2.0, "P": 5.0}
    world_program = {"N": 4.0, "P": 3.0}
    assert world_neural["N"] < world_neural["P"]
    assert world_program["P"] < world_program["N"]

    # C. same semantics, alternate substrate robustly selects program/non-neural.
    n_alt = [(5.0, 5.4), (4.0, 4.2)]
    p_alt = [(2.0, 2.2), (2.5, 2.8)]
    assert robust_dominates(p_alt, n_alt)
    assert not robust_dominates(n_alt, p_alt)

    # D. budget feasibility can remove a competing family before Pareto comparison.
    memory_budget = 5.0
    n_memory = (3.0, 3.2)
    table_memory = (9.0, 11.0)
    assert certified_feasible(n_memory, memory_budget)
    assert certified_infeasible(table_memory, memory_budget)

    # E. universal domination is monotone under interval refinement.
    n_refined = [(2.05, 2.15), (3.02, 3.08)]
    p_refined = [(4.7, 5.0), (3.9, 4.1)]
    assert robust_dominates(n_refined, p_refined)

    receipt = {
        "terminal": "GRAND_GMI_EMPIRICAL_RESOURCE_IDENTIFICATION_ALL_GREEN",
        "robust_neural_selection": True,
        "overlap_verdict": "UNDECIDED_FROM_CURRENT_RESOURCE_EVIDENCE",
        "opposite_compatible_worlds_checked": 2,
        "robust_non_neural_selection_on_alternate_substrate": True,
        "constraint_certified_neural_feasible": True,
        "constraint_certified_table_infeasible": True,
        "refinement_preserves_prior_robust_domination": True,
        "scope_boundary": "Exact interval logic only; intervals are evidence inputs, not real-hardware measurements."
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
