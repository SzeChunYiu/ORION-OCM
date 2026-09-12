#!/usr/bin/env python3
"""Exact finite witnesses for ACTIVE_CLOSED_LOOP_INTELLIGENCE_THEOREM_V1."""

from itertools import product
import json


def passive_success(guess):
    return sum(int(guess == h) for h in (0, 1)) / 2.0


def delayed_memory_success(e0, e1, d0, d1):
    encode = {0: e0, 1: e1}
    decode = {0: d0, 1: d1}
    return sum(int(decode[encode[h]] == h) for h in (0, 1)) / 2.0


def main():
    # A. Without sensing, both deterministic open-loop guesses achieve only 1/2.
    passive_scores = [passive_success(g) for g in (0, 1)]
    assert passive_scores == [0.5, 0.5]

    # B. With no persistent distinction after sensing, terminal output is still constant.
    one_state_scores = [passive_success(g) for g in (0, 1)]
    assert max(one_state_scores) == 0.5

    # C. Enumerate every binary encoder/decoder pair for one persistent bit.
    pairs_checked = 0
    perfect_pairs = []
    scores = []
    for e0, e1, d0, d1 in product([0, 1], repeat=4):
        score = delayed_memory_success(e0, e1, d0, d1)
        scores.append(score)
        pairs_checked += 1
        if score == 1.0:
            perfect_pairs.append((e0, e1, d0, d1))
    assert pairs_checked == 16
    assert len(perfect_pairs) == 2
    assert set(perfect_pairs) == {(0, 1, 0, 1), (1, 0, 1, 0)}

    # D. Budget phase: the zero-error obligation is feasible iff sensing cost 1 is admitted.
    sense_cost = 1
    zero_error_feasible_budget_0 = 0 >= sense_cost
    zero_error_feasible_budget_1 = 1 >= sense_cost and len(perfect_pairs) > 0
    assert not zero_error_feasible_budget_0
    assert zero_error_feasible_budget_1

    receipt = {
        "terminal": "GRAND_GMI_ACTIVE_CLOSED_LOOP_INTELLIGENCE_ALL_GREEN",
        "passive_deterministic_policies_checked": 2,
        "passive_success_scores": passive_scores,
        "one_state_delayed_best_success": max(one_state_scores),
        "binary_memory_encoder_decoder_pairs_checked": pairs_checked,
        "perfect_delayed_memory_pairs": [list(x) for x in perfect_pairs],
        "perfect_pair_count": len(perfect_pairs),
        "required_distinguishable_persistent_states": 2,
        "required_binary_memory_bits": 1,
        "zero_error_feasible_with_sensing_budget_0": zero_error_feasible_budget_0,
        "zero_error_feasible_with_sensing_budget_1": zero_error_feasible_budget_1,
        "derived_operational_property": "SENSE_STORE_ACT",
        "neurality_implied_by_closed_loop_structure": False
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
