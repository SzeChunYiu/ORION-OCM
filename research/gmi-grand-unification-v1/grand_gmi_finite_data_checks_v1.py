#!/usr/bin/env python3
"""Complete exact finite checks for FMT; no random experiments or timings."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from finite_data_model_v1 import (Problem, cheapest_mixture, model_distance,
                                 synthesize, transfer_bounds)
from finite_data_oracle_v1 import (all_profiles, dual_mixture_cost, mixed_evaluate,
                                  ordered_count_law, path_evaluate, policy_syntax)
from finite_data_sampling_v1 import confidence_upper, count_law, simultaneous_failure
from finite_data_witnesses_v1 import (falsifying_controls, positive_certificate, register_controls,
                                     require, sharp_controls)


def models(values, horizon=2):
    for probabilities in product(values, repeat=4):
        rows = tuple(tuple(((1-p)/2, (1-p)/2, p, F(0))
                           for p in probabilities[2*s:2*s+2]) for s in range(2))+((), ())
        stage = tuple(((F(t+1), F(2*t+2)), (F(2*t+2), F(t+1)), (), ())
                      for t in range(horizon))
        yield Problem(rows, stage, (2, 3, 1, 4), frozenset({2}))


def policy_census():
    stats = dict(models=0, syntax_trees=0, terminal_paths=0, model_pairs=0,
                 common_policy_comparisons=0, lp_comparisons=0, transferred_policies=0,
                 buffered_comparators=0, synthesis_states=0, child_combinations=0, transition_terms=0)
    for grid in ((F(0), F(1, 2), F(1)), (F(3, 4), F(7, 8), F(1))):
        register = tuple(models(grid))
        trees = policy_syntax((2, 2, 0, 0), 2, 0)
        cache = []
        for model in register:
            points, operations = synthesize(model)
            independent, counts = all_profiles(model)
            require(set(points) == set(independent), "DP differs from complete policy syntax")
            for point, tree in points.items():
                require(path_evaluate(model, tree)[0] == point, "synthesized tree does not execute")
            cache.append((points, independent, tuple(path_evaluate(model, t)[0] for t in trees)))
            stats["models"] += 1
            stats["syntax_trees"] += counts["trees"]
            stats["terminal_paths"] += counts["terminal_paths"]
            stats["synthesis_states"] += operations["states"]
            stats["child_combinations"] += operations["child_combinations"]
            stats["transition_terms"] += operations["transition_terms"]
            for q, fee in product((F(0), F(1, 4), F(1, 2), F(3, 4), F(1)), (F(0), F(1, 10))):
                got = cheapest_mixture(points, q, fee)
                expected = dual_mixture_cost(independent, q, fee)
                require((got["cost"] if got else None) == expected, "primal/independent dual LP")
                stats["lp_comparisons"] += 1
        for i, true in enumerate(register):
            for j, empirical in enumerate(register):
                eps = model_distance(true, empirical)
                drift, work = transfer_bounds(empirical, eps)
                stats["model_pairs"] += 1
                for p, q in zip(cache[i][2], cache[j][2]):
                    require(abs(p[0]-q[0]) <= drift and abs(p[1]-q[1]) <= work,
                            "common-history probability/work transfer")
                    stats["common_policy_comparisons"] += 1
                # Keep this complete-model paired transfer census modest and exact.
                target, fee = F(1, 2), F(1, 10)
                choice = cheapest_mixture(cache[j][0], target+drift, fee)
                if choice is not None:
                    actual_p, actual_j = mixed_evaluate(true, choice["policies"])
                    actual_j += choice["seed_charge"]
                    require(actual_p >= target and actual_j <= choice["cost"]+work,
                            "selected empirical policy fails transferred certificate")
                    stats["transferred_policies"] += 1
                    comparator = dual_mixture_cost(cache[i][1], target+2*drift, fee)
                    if comparator is not None:
                        require(actual_j <= comparator+2*work, "strongest buffered comparison")
                        stats["buffered_comparators"] += 1
    # Repeated current states reached through distinct observation histories at H=3.
    mixed_models = tuple(models((F(1, 2), F(1)), 3))[:3]
    for model in mixed_models:
        points, operations = synthesize(model)
        independent, counts = all_profiles(model)
        require(set(points) == set(independent), "full-history H3 reconstruction")
        stats["models"] += 1
        stats["syntax_trees"] += counts["trees"]
        stats["terminal_paths"] += counts["terminal_paths"]
        stats["synthesis_states"] += operations["states"]
        stats["child_combinations"] += operations["child_combinations"]
        stats["transition_terms"] += operations["transition_terms"]
    return stats


def sampling_census():
    checks = laws = 0
    for k in (1, 2, 3):
        rows = [tuple(F(c, 4) for c in counts) for counts in product(range(5), repeat=k)
                if sum(counts) == 4]
        for row, n in product(rows, range(1, 5)):
            counted = count_law(row, n)
            ordered = ordered_count_law(row, n)
            require(counted == ordered and sum(counted.values()) == 1, "multinomial/ordered sample law")
            laws += 1
            for epsilon in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
                tail = simultaneous_failure((row,), n, epsilon)
                require(tail <= confidence_upper(1, k, n, epsilon), "single-row confidence violation")
                checks += 1
    binary = tuple((F(a, 4), 1-F(a, 4)) for a in range(5))
    for a, b, n, epsilon in product(binary, binary, range(1, 5), (F(1, 4), F(1, 2), F(3, 4))):
        tail = simultaneous_failure((a, b), n, epsilon)
        require(tail <= confidence_upper(2, 2, n, epsilon), "simultaneous confidence violation")
        checks += 1
    return dict(ordered_multinomial_law_comparisons=laws, exact_tail_bounds=checks)


def json_ready(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {k: json_ready(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_ready(v) for v in value]
    return value


def run():
    return json_ready(dict(schema="finite-data-model-transfer-v1", policy_census=policy_census(),
        sampling_census=sampling_census(), sharpness=sharp_controls(),
        positive_certificate=positive_certificate(), falsification=falsifying_controls(),
        register_controls=register_controls(),
        claim_ceiling="Finite supplied-register confidence and common-policy transfer; no support or physical-completeness guarantee.",
        terminal="FINITE_DATA_MODEL_TRANSFER_FINITE_GREEN"))


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
