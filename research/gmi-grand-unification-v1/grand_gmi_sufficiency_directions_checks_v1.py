#!/usr/bin/env python3
"""Exact finite falsifiers for ACL-2, GEI-3, GR5 and ERI-5 proof direction.

Finite enumeration accompanies the analytic proofs. Hoeffding's numerical
value is used only for a wide-separated comparison, never as exact arithmetic.
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path


def active_policy_counts(sensed, memory_states):
    """Enumerate delayed controllers after all external evidence disappears."""
    if memory_states < 1:
        raise ValueError("At least one physical controller state is required")
    observations = (0, 1) if sensed else (0, 0)
    symbols = tuple(sorted(set(observations)))
    checked = 0
    exact = 0
    best_world_average = Fraction(0)
    for values in product(range(memory_states), repeat=len(symbols)):
        encode = dict(zip(symbols, values))
        for decode in product((0, 1), repeat=memory_states):
            checked += 1
            correct = tuple(decode[encode[observations[h]]] == h for h in (0, 1))
            exact += all(correct)
            best_world_average = max(best_world_average, Fraction(sum(correct), 2))
    return checked, exact, best_world_average


def exact_predictor_count(observation, target):
    """Count all predictors using only the declared binary self-probe output."""
    symbols = tuple(sorted(set(observation)))
    count = 0
    for values in product((0, 1), repeat=len(symbols)):
        predictor = dict(zip(symbols, values))
        count += all(predictor[observation[h]] == target[h] for h in range(len(target)))
    return count


def registered_two_sample_upper(losses):
    """Predeclared single-candidate rule: 96% coverage for iid [0,1] losses."""
    losses = tuple(Fraction(value) for value in losses)
    if len(losses) != 2 or any(value < 0 or value > 1 for value in losses):
        raise ValueError("This rule requires two bounded losses")
    return Fraction(4, 5) if all(value == 0 for value in losses) else Fraction(1)


def exact_miscoverage(loss_values, probabilities):
    """Exact probability of under-coverage for a supplied finite iid law."""
    values = tuple(Fraction(value) for value in loss_values)
    probabilities = tuple(Fraction(probability) for probability in probabilities)
    if len(values) != len(probabilities) or sum(probabilities) != 1 or any(p < 0 for p in probabilities):
        raise ValueError("Require a complete finite probability law")
    risk = sum(value * probability for value, probability in zip(values, probabilities))
    failure = Fraction(0)
    for i, j in product(range(len(values)), repeat=2):
        if risk > registered_two_sample_upper((values[i], values[j])):
            failure += probabilities[i] * probabilities[j]
    return failure


def nonempty_subsets(values):
    return tuple(subset for size in range(1, len(values) + 1) for subset in combinations(values, size))


def envelope(points):
    return tuple(map(min, zip(*points))), tuple(map(max, zip(*points)))


def run():
    active_cases = []
    for sensing_budget, memory_bit_budget in product((0, 1), repeat=2):
        sensed = sensing_budget >= 1
        counts = active_policy_counts(sensed, 2**memory_bit_budget)
        active_cases.append({
            "sensing_budget": sensing_budget,
            "memory_bit_budget": memory_bit_budget,
            "probe_affordable": sensed,
            "policies_checked": counts[0],
            "adequate_policy_count": counts[1],
            "best_average_success": str(counts[2]),
        })
    affordable_but_inadequate = active_cases[2]
    complete_feasible = active_cases[3]

    self_problems = 0
    nonidentifiable = 0
    self_gate_agreements = 0
    for observation, target in product(tuple(product((0, 1), repeat=2)), repeat=2):
        self_problems += 1
        exists = exact_predictor_count(observation, target) > 0
        identifiable = all(
            observation[i] != observation[j] or target[i] == target[j]
            for i, j in product(range(2), repeat=2)
        )
        self_gate_agreements += exists == identifiable
        nonidentifiable += not exists

    coverage_cases = 0
    all_coverage_valid = True
    max_grid_miscoverage = Fraction(0)
    for zero_weight in range(11):
        for half_weight in range(11 - zero_weight):
            one_weight = 10 - zero_weight - half_weight
            probabilities = tuple(Fraction(weight, 10) for weight in (zero_weight, half_weight, one_weight))
            failure = exact_miscoverage((0, Fraction(1, 2), 1), probabilities)
            coverage_cases += 1
            all_coverage_valid &= failure <= Fraction(1, 25)
            max_grid_miscoverage = max(max_grid_miscoverage, failure)
    raw_one_sample = math.sqrt(math.log(40) / 2)
    raw_two_samples = math.sqrt(math.log(40) / 4)

    nested_cases = 0
    envelope_directions_valid = True
    universe = ((0, 0), (0, 1), (1, 0), (1, 1))
    for outer in nonempty_subsets(universe):
        lower, upper = envelope(outer)
        for inner in nonempty_subsets(outer):
            refined_lower, refined_upper = envelope(inner)
            nested_cases += 1
            envelope_directions_valid &= all(a <= b for a, b in zip(lower, refined_lower))
            envelope_directions_valid &= all(a >= b for a, b in zip(upper, refined_upper))

    checks = {
        "ACL2_probe_only_sufficiency_refuted": (
            affordable_but_inadequate["probe_affordable"]
            and affordable_but_inadequate["adequate_policy_count"] == 0
        ),
        "ACL2_complete_memory_and_probe_policy_succeeds": complete_feasible["adequate_policy_count"] == 2,
        "ACL2_missing_probe_cannot_be_repaired_by_memory": active_cases[1]["adequate_policy_count"] == 0,
        "GEI3_raw_bound_failure_does_not_override_loss_range": raw_one_sample > 1,
        "GEI3_sharper_same_data_certificate_passes": (
            raw_two_samples > Fraction(4, 5)
            and registered_two_sample_upper((0, 0)) == Fraction(4, 5)
        ),
        "GEI3_registered_rule_has_exact_finite_law_coverage": coverage_cases == 66 and all_coverage_valid,
        "GR5_no_diagonal_does_not_imply_identifiability": exact_predictor_count((0, 0), (0, 1)) == 0,
        "GR5_declared_observation_refinement_restores_prediction": exact_predictor_count((0, 1), (0, 1)) == 1,
        "GR5_all_finite_gates_agree": self_gate_agreements == self_problems == 16 and nonidentifiable == 4,
        "ERI5_nested_coordinate_envelopes_have_fixed_directions": nested_cases == 65 and envelope_directions_valid,
    }
    green = all(checks.values())
    return {
        "terminal": "GRAND_GMI_SUFFICIENCY_DIRECTIONS_TRANCHE_" + ("ALL_GREEN" if green else "RED"),
        "all_checks_green": green,
        "determinism": "exact-enumeration-rational-coverage-and-declared-numerical-Hoeffding-comparison",
        "checks": checks,
        "active_budget_cases": active_cases,
        "generalization_witness": {
            "sample_count": 2,
            "empirical_loss": 0,
            "requested_failure_probability": "1/20",
            "raw_hoeffding_upper": raw_two_samples,
            "registered_zero_event_upper": "4/5",
            "registered_rule_failure_bound": "1/25",
            "finite_probability_laws_checked": coverage_cases,
            "maximum_grid_miscoverage": str(max_grid_miscoverage),
        },
        "self_prediction_witness": {
            "probe_target_problems": self_problems,
            "nonidentifiable_nonreactive_problems": nonidentifiable,
            "gate_agreements": self_gate_agreements,
        },
        "nested_resource_set_cases": nested_cases,
        "scope": "Finite counterexamples and analytic sufficient-condition directions; no general policy realization or statistical certification oracle",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    output = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if result["all_checks_green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
