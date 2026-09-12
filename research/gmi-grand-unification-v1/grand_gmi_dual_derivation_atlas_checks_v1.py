#!/usr/bin/env python3
"""Exact finite checks for NN_NONNN_DUAL_DERIVATION_ATLAS_V1.

These checks validate the operational derivation examples. Synthetic resource
numbers are theorem witnesses only, not measurements of real hardware.
"""

from itertools import product, permutations
import json


def parity3(x):
    return x[0] ^ x[1] ^ x[2]


def parity_threshold_dnf(x):
    positives = [p for p in product([0, 1], repeat=3) if parity3(p) == 1]
    hidden = []
    for p in positives:
        matches = sum(1 for a, b in zip(x, p) if a == b)
        hidden.append(int(matches >= 3))
    return int(sum(hidden) >= 1)


def cyclic_local_xor(x):
    n = len(x)
    return tuple(x[i] ^ x[(i + 1) % n] for i in range(n))


def cyclic_shift(x, s):
    n = len(x)
    return tuple(x[(i - s) % n] for i in range(n))


def selector_output(c, x0, x1):
    return x0 if c == 0 else x1


def main():
    # Atlas A: exact neural-threshold DNF and direct Boolean parity coincide.
    parity_checks = 0
    for x in product([0, 1], repeat=3):
        assert parity_threshold_dnf(x) == parity3(x)
        parity_checks += 1
    assert parity_checks == 8

    # Atlas C: repeated local XOR rule is exactly equivariant to cyclic shifts.
    translation_checks = 0
    for x in product([0, 1], repeat=4):
        for s in range(4):
            assert cyclic_local_xor(cyclic_shift(x, s)) == cyclic_shift(cyclic_local_xor(x), s)
            translation_checks += 1
    assert translation_checks == 64

    # Atlas D: fixed source routes are insufficient; context-aware routing is exact.
    routing_rows = list(product([0, 1], repeat=3))
    fixed_x0 = sum(x0 == selector_output(c, x0, x1) for c, x0, x1 in routing_rows)
    fixed_x1 = sum(x1 == selector_output(c, x0, x1) for c, x0, x1 in routing_rows)
    dynamic = sum((x0 if c == 0 else x1) == selector_output(c, x0, x1) for c, x0, x1 in routing_rows)
    assert (fixed_x0, fixed_x1, dynamic) == (6, 6, 8)

    # Atlas E: OR aggregation is invariant under every permutation of three inputs.
    permutation_checks = 0
    perms = list(permutations(range(3)))
    assert len(perms) == 6
    for x in product([0, 1], repeat=3):
        base = int(any(x))
        for p in perms:
            xp = tuple(x[i] for i in p)
            assert int(any(xp)) == base
            permutation_checks += 1
    assert permutation_checks == 48

    # Atlas B: exact delayed reproduction of four messages needs at least four states.
    memory_encoding_checks = 0
    injective_counts = []
    for k in range(1, 5):
        injective = 0
        for enc in product(range(k), repeat=4):
            memory_encoding_checks += 1
            if len(set(enc)) == 4:
                injective += 1
        injective_counts.append(injective)
    assert memory_encoding_checks == 354
    assert injective_counts == [0, 0, 0, 24]

    # Same protected response can select opposite families under opposite legal
    # resource orderings: semantics alone cannot choose neurality.
    world_neural = {"NEURAL": 1, "NON_NEURAL": 2}
    world_nonneural = {"NEURAL": 2, "NON_NEURAL": 1}
    assert min(world_neural, key=world_neural.get) == "NEURAL"
    assert min(world_nonneural, key=world_nonneural.get) == "NON_NEURAL"

    # Atlas I: synthetic hybrid decomposition witness from the family-phase theorem.
    hybrid_upper = 4 + 3 + 1
    pure_neural_lower = 4 + 8
    pure_nonneural_lower = 9 + 3
    assert hybrid_upper == 8
    assert pure_neural_lower == 12
    assert pure_nonneural_lower == 12
    assert hybrid_upper < min(pure_neural_lower, pure_nonneural_lower)

    receipt = {
        "terminal": "GRAND_GMI_NN_NONNN_DUAL_DERIVATION_ATLAS_ALL_GREEN",
        "parity3_exact_checks": parity_checks,
        "translation_equivariance_checks": translation_checks,
        "routing_fixed_x0_correct_of_8": fixed_x0,
        "routing_fixed_x1_correct_of_8": fixed_x1,
        "routing_dynamic_correct_of_8": dynamic,
        "permutation_invariance_checks": permutation_checks,
        "memory_encoding_checks": memory_encoding_checks,
        "memory_injective_counts_state_sizes_1_to_4": injective_counts,
        "response_equivalent_family_selection_can_reverse": True,
        "hybrid_upper_bound": hybrid_upper,
        "pure_neural_lower_bound": pure_neural_lower,
        "pure_non_neural_lower_bound": pure_nonneural_lower,
        "empirical_hardware_cost_claimed": False,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
