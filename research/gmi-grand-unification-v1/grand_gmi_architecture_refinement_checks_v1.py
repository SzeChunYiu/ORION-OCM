#!/usr/bin/env python3
"""Exact finite checks for INTRAFAMILY_ARCHITECTURE_REFINEMENT_THEOREM_V1."""

from itertools import product
import json


def ring_target(x):
    n = len(x)
    return tuple(x[i] ^ x[(i + 1) % n] for i in range(n))


def shift(x, k):
    n = len(x)
    return tuple(x[(i - k) % n] for i in range(n))


def main():
    # A. local translation-equivariant protected map on a 4-site ring.
    xs = list(product([0, 1], repeat=4))
    equivariance_checks = 0
    for x in xs:
        for k in range(4):
            assert ring_target(shift(x, k)) == shift(ring_target(x), k)
            equivariance_checks += 1
    assert equivariance_checks == 64

    locality_checks = 0
    for i in range(4):
        j = (i + 1) % 4
        for a in xs:
            for b in xs:
                if a[i] == b[i] and a[j] == b[j]:
                    assert ring_target(a)[i] == ring_target(b)[i]
                    locality_checks += 1
    assert locality_checks == 256

    # B. delayed bit reproduction: one persistent state is insufficient.
    one_state_best = max(sum(out == x for x in (0, 1)) for out in (0, 1))
    assert one_state_best == 1

    # With two states, exactly the two bijective encode/decode pairings succeed.
    two_state_exact = 0
    for e0, e1, d0, d1 in product([0, 1], repeat=4):
        enc = {0: e0, 1: e1}
        dec = {0: d0, 1: d1}
        if all(dec[enc[x]] == x for x in (0, 1)):
            two_state_exact += 1
    assert two_state_exact == 2

    # C. delayed selector: fixed routing fails; context-dependent routing is exact.
    cases = list(product([0, 1], repeat=3))  # x0, x1, q
    fixed_scores = []
    for src in (0, 1):
        score = 0
        for x0, x1, q in cases:
            routed = x0 if src == 0 else x1
            target = x0 if q == 0 else x1
            score += int(routed == target)
        fixed_scores.append(score)
    assert fixed_scores == [6, 6]

    dynamic_score = 0
    for x0, x1, q in cases:
        routed = x0 if q == 0 else x1
        target = x0 if q == 0 else x1
        dynamic_score += int(routed == target)
    assert dynamic_score == 8

    receipt = {
        "terminal": "GRAND_GMI_ARCHITECTURE_REFINEMENT_ALL_GREEN",
        "ring_equivariance_checks": equivariance_checks,
        "ring_locality_checks": locality_checks,
        "delayed_bit_one_state_best": one_state_best,
        "delayed_bit_two_state_exact_encodings": two_state_exact,
        "selector_fixed_route_scores": fixed_scores,
        "selector_dynamic_route_score": dynamic_score,
        "derived_properties": [
            "LOCAL_TRANSLATION_EQUIVARIANT",
            "PERSISTENT_STATE_REQUIRED",
            "DYNAMIC_ROUTING_REQUIRED"
        ],
        "named_architecture_uniqueness_claimed": False
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
