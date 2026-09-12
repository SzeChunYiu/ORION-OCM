#!/usr/bin/env python3
"""Exact microscopes for Grand GMI phenomenology reduction V1.

No RNG, no fitted parameters, no architecture-specific libraries.
"""

from itertools import product
from math import factorial
import json


def check_temporal_memory():
    total_encodings = 0
    rows = []
    for m in range(1, 7):
        minimum = None
        injective_at_m = 0
        by_states = {}
        for s in range(1, m + 1):
            checked = 0
            injective = 0
            for enc in product(range(s), repeat=m):
                checked += 1
                if len(set(enc)) == m:
                    injective += 1
            total_encodings += checked
            by_states[str(s)] = {"encodings": checked, "injective": injective}
            if injective and minimum is None:
                minimum = s
            if s == m:
                injective_at_m = injective
        assert minimum == m
        assert injective_at_m == factorial(m)
        rows.append({"messages": m, "minimum_memory_states": minimum, "injective_encodings_at_minimum": injective_at_m})
    assert total_encodings == 71992
    return {
        "encoding_checks": total_encodings,
        "rows": rows,
        "all_minimum_states_equal_message_count": True,
    }


def _score_policy(policy, route):
    correct = 0
    for x0, x1, q in product([0, 1], repeat=3):
        xs = (x0, x1)
        if route == "dynamic":
            observed = xs[q]
        else:
            observed = xs[int(route)]
        ctx = q * 2 + observed
        pred = policy[ctx]
        correct += int(pred == xs[q])
    return correct


def check_conditional_routing():
    policies = list(product([0, 1], repeat=4))
    rows = {}
    for route in ("0", "1", "dynamic"):
        scores = [_score_policy(p, route) for p in policies]
        best = max(scores)
        rows[route] = {
            "policies": len(policies),
            "best_correct_of_8": best,
            "best_accuracy": f"{best}/8",
            "number_of_best_policies": sum(s == best for s in scores),
        }
    assert rows["0"]["best_correct_of_8"] == 6
    assert rows["1"]["best_correct_of_8"] == 6
    assert rows["dynamic"]["best_correct_of_8"] == 8
    assert rows["dynamic"]["number_of_best_policies"] == 1
    return {"routes": rows, "dynamic_strictly_better_than_every_fixed_route": True}


def check_in_context_side_information():
    no_prompt_scores = []
    for policy in product([0, 1], repeat=2):
        correct = 0
        for t, x in product([0, 1], repeat=2):
            correct += int(policy[x] == (x ^ t))
        no_prompt_scores.append(correct)

    prompt_scores = []
    for policy in product([0, 1], repeat=4):
        correct = 0
        for t, x in product([0, 1], repeat=2):
            correct += int(policy[t * 2 + x] == (x ^ t))
        prompt_scores.append(correct)

    assert max(no_prompt_scores) == 2
    assert max(prompt_scores) == 4
    assert sum(s == 4 for s in prompt_scores) == 1
    return {
        "no_prompt_policies": 4,
        "no_prompt_best_correct_of_4": 2,
        "prompt_conditioned_policies": 16,
        "prompt_best_correct_of_4": 4,
        "perfect_prompt_policies": 1,
    }


def check_continual_retention():
    # Four joint histories (x,y) must be recoverable after the learning sequence.
    total = 0
    rows = {}
    for s in range(1, 5):
        injective = 0
        checked = 0
        for enc in product(range(s), repeat=4):
            checked += 1
            if len(set(enc)) == 4:
                injective += 1
        total += checked
        rows[str(s)] = {"encodings": checked, "exactly_decodable": injective}
    assert total == 354
    assert rows["1"]["exactly_decodable"] == 0
    assert rows["2"]["exactly_decodable"] == 0
    assert rows["3"]["exactly_decodable"] == 0
    assert rows["4"]["exactly_decodable"] == 24
    return {
        "encoding_checks": total,
        "by_final_state_count": rows,
        "minimum_final_states": 4,
        "minimum_bits": 2,
    }


def check_tool_parity_boundary():
    pivotal_checks = 0
    rows = []
    for n in range(1, 13):
        zero = [0] * n
        base = 0
        for i in range(n):
            other = list(zero)
            other[i] = 1
            parity = sum(other) % 2
            assert parity != base
            pivotal_checks += 1
        # In an exact bit-query decision tree, every leaf must have queried every bit:
        # if bit i is unqueried, flipping i preserves the path and flips parity.
        rows.append({"input_bits": n, "exact_worst_case_bit_queries_without_tool": n, "exact_parity_tool_calls": 1})
    assert pivotal_checks == 78
    return {
        "pivotal_bit_checks": pivotal_checks,
        "rows": rows,
        "external_tool_changes_transformation_query_resource": True,
    }


def check_feature_sufficiency():
    # Target parity y=x0 XOR x1. Fixed phi=x0 discards x1.
    fixed_scores = []
    for policy in product([0, 1], repeat=2):
        correct = 0
        for x0, x1 in product([0, 1], repeat=2):
            correct += int(policy[x0] == (x0 ^ x1))
        fixed_scores.append(correct)

    # Expanded feature z=parity itself. Two context values, four policies.
    expanded_scores = []
    for policy in product([0, 1], repeat=2):
        correct = 0
        for x0, x1 in product([0, 1], repeat=2):
            z = x0 ^ x1
            correct += int(policy[z] == z)
        expanded_scores.append(correct)

    assert max(fixed_scores) == 2
    assert max(expanded_scores) == 4
    return {
        "fixed_phi_x0_best_correct_of_4": 2,
        "semantic_sufficient_parity_feature_best_correct_of_4": 4,
        "feature_learning_value_requires_recovering_lost_obligation_distinction": True,
    }


def run():
    return {
        "terminal": "GRAND_GMI_PHENOMENOLOGY_REDUCTION_TRANCHE_ALL_GREEN",
        "temporal_memory": check_temporal_memory(),
        "conditional_routing": check_conditional_routing(),
        "in_context": check_in_context_side_information(),
        "continual_retention": check_continual_retention(),
        "tool_parity": check_tool_parity_boundary(),
        "feature_sufficiency": check_feature_sufficiency(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
