#!/usr/bin/env python3
"""Exact finite checks for Grand GMI generalization identifiability radius V1."""
from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path

WORLDS = tuple(range(4))
TARGET_VALUES = (0, 1, 2)


def radius(observation, target):
    worst = 0
    for z in set(observation):
        inds = [i for i in WORLDS if observation[i] == z]
        local = min(
            max(abs(y - target[i]) for i in inds)
            for y in TARGET_VALUES
        )
        worst = max(worst, local)
    return worst


def brute_predictor_error(observation, target):
    symbols = tuple(sorted(set(observation)))
    best = None
    for outputs in product(TARGET_VALUES, repeat=len(symbols)):
        pred = dict(zip(symbols, outputs))
        error = max(abs(pred[observation[i]] - target[i]) for i in WORLDS)
        best = error if best is None else min(best, error)
    return best


def refines(fine, coarse):
    for i in WORLDS:
        for j in WORLDS:
            if fine[i] == fine[j] and coarse[i] != coarse[j]:
                return False
    return True


def run():
    binary_observations = tuple(product((0, 1), repeat=4))
    ternary_targets = tuple(product(TARGET_VALUES, repeat=4))
    ternary_observations = tuple(product(TARGET_VALUES, repeat=4))

    direct_cases = 0
    direct_exact = 0
    exact_identifiable = 0
    radius_histogram = {}
    impossible_witness = None

    for obs in binary_observations:
        for target in ternary_targets:
            direct_cases += 1
            r = radius(obs, target)
            b = brute_predictor_error(obs, target)
            direct_exact += r == b
            exact_identifiable += r == 0
            radius_histogram[str(r)] = radius_histogram.get(str(r), 0) + 1
            if impossible_witness is None and r > 0:
                for i in WORLDS:
                    for j in WORLDS:
                        if i < j and obs[i] == obs[j] and target[i] != target[j]:
                            impossible_witness = {
                                "observation": list(obs),
                                "target": list(target),
                                "world_pair": [i, j],
                                "shared_observation": obs[i],
                                "target_values": [target[i], target[j]],
                                "minimax_radius": r,
                            }
                            break
                    if impossible_witness is not None:
                        break

    refinement_pairs = []
    for coarse in binary_observations:
        for fine in ternary_observations:
            if refines(fine, coarse):
                refinement_pairs.append((coarse, fine))

    refinement_cases = 0
    refinement_monotone = 0
    strict_improvements = 0
    strict_witness = None
    for coarse, fine in refinement_pairs:
        for target in ternary_targets:
            rc = radius(coarse, target)
            rf = radius(fine, target)
            refinement_cases += 1
            refinement_monotone += rf <= rc
            if rf < rc:
                strict_improvements += 1
                if strict_witness is None:
                    strict_witness = {
                        "coarse_observation": list(coarse),
                        "fine_observation": list(fine),
                        "target": list(target),
                        "coarse_radius": rc,
                        "fine_radius": rf,
                    }

    observed = {
        "direct_cases": direct_cases,
        "direct_radius_equals_bruteforce": direct_exact,
        "exact_identifiable": exact_identifiable,
        "radius_histogram": radius_histogram,
        "refinement_pairs": len(refinement_pairs),
        "refinement_target_cases": refinement_cases,
        "refinement_monotone": refinement_monotone,
        "strict_refinement_improvements": strict_improvements,
    }
    expected = {
        "direct_cases": 1296,
        "direct_radius_equals_bruteforce": 1296,
        "exact_identifiable": 132,
        "radius_histogram": {"0": 132, "1": 1164},
        "refinement_pairs": 462,
        "refinement_target_cases": 37422,
        "refinement_monotone": 37422,
        "strict_refinement_improvements": 6120,
    }
    ok = observed == expected and impossible_witness is not None and strict_witness is not None
    return {
        "terminal": (
            "GRAND_GMI_GENERALIZATION_RADIUS_TRANCHE_ALL_GREEN"
            if ok else "GRAND_GMI_GENERALIZATION_RADIUS_TRANCHE_RED"
        ),
        "all_checks_green": ok,
        "determinism": "exact-exhaustive-no-rng",
        "observed": observed,
        "expected": expected,
        "first_nonidentifiable_witness": impossible_witness,
        "first_strict_refinement_witness": strict_witness,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
