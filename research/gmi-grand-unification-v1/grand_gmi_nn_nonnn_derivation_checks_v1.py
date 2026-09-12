#!/usr/bin/env python3
"""Exact checks for NN_NONNN_END_TO_END_DERIVATIONS_V1."""

from itertools import product
import json


def H(t):
    return 1 if t > 0 else 0


def dominates(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def hazard_controller():
    rows = []
    for h in (0, 1):
        program = h
        neural = H(h - 0.5)
        assert program == neural == h
        rows.append([h, program, neural])
    p = (1, 1, 1)
    n = (2, 2, 2)
    assert dominates(p, n)
    return {
        "rows": rows,
        "semantic_states": 2,
        "cut_chromatic_number": 2,
        "cut_bits": 1,
        "selected_family": "non-neural",
    }


def ring_and(x):
    n = len(x)
    return tuple(x[i] & x[(i + 1) % n] for i in range(n))


def ring_neural(x):
    n = len(x)
    return tuple(H(x[i] + x[(i + 1) % n] - 1.5) for i in range(n))


def rotate(x):
    n = len(x)
    return tuple(x[(i - 1) % n] for i in range(n))


def translation_local():
    states = 0
    for n in range(2, 9):
        for x in product((0, 1), repeat=n):
            y_gate = ring_and(x)
            y_neural = ring_neural(x)
            assert y_gate == y_neural
            assert ring_and(rotate(x)) == rotate(y_gate)
            states += 1
    neural_profile = (2, 2, 2)
    program_profile = (4, 5, 3)
    assert dominates(neural_profile, program_profile)
    return {
        "ring_sizes": [2, 3, 4, 5, 6, 7, 8],
        "states_checked": states,
        "all_neural_gate_outputs_equal": True,
        "all_rotation_equivariance_checks_green": True,
        "each_local_input_cut_bits": 1,
        "selected_family_in_declared_witness_model": "neural",
    }


def hybrid_product():
    region_a = {"neural": (1, 2), "program": (5, 5)}
    region_b = {"neural": (5, 5), "program": (1, 2)}
    assignments = {}
    for fa, fb in product(region_a, region_b):
        assignments[f"{fa}+{fb}"] = tuple(
            x + y for x, y in zip(region_a[fa], region_b[fb])
        )
    winner = assignments["neural+program"]
    assert all(
        name == "neural+program" or dominates(winner, profile)
        for name, profile in assignments.items()
    )
    return {
        "assignments": {k: list(v) for k, v in assignments.items()},
        "selected_family": "hybrid neural+program",
    }


def xor_underdetermined():
    rows = []
    for x1, x2 in product((0, 1), repeat=2):
        table = x1 ^ x2
        a = H(x1 + x2 - 0.5)
        b = H(x1 + x2 - 1.5)
        neural = H(a - b - 0.5)
        assert table == neural
        rows.append([x1, x2, table, neural])
    neural_profile = (2, 4)
    program_profile = (4, 2)
    assert not dominates(neural_profile, program_profile)
    assert not dominates(program_profile, neural_profile)
    return {
        "rows": rows,
        "profiles": {"neural": list(neural_profile), "program": list(program_profile)},
        "family_derived": False,
    }


def main():
    receipt = {
        "terminal": "GRAND_GMI_NN_NONNN_END_TO_END_FINITE_CHECKS_ALL_GREEN",
        "hazard_non_neural": hazard_controller(),
        "translation_local_neural": translation_local(),
        "hybrid_product": hybrid_product(),
        "xor_underdetermined": xor_underdetermined(),
        "scope_boundary": "Exact finite logic plus synthetic declared resource profiles; no empirical hardware-cost claim."
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
