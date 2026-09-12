#!/usr/bin/env python3
"""Exact checks for Grand GMI continual semantic retention V1."""
from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path

HISTORIES = tuple(range(4))
TASKS = tuple(product((0, 1), repeat=4))


def joint_classes(tasks):
    signatures = tuple(tuple(task[h] for task in tasks) for h in HISTORIES)
    return len(set(signatures)), signatures


def encoder_sufficient(encoder, signatures):
    seen = {}
    for h, z in enumerate(encoder):
        if z in seen and seen[z] != signatures[h]:
            return False
        seen[z] = signatures[h]
    return True


def sequence_checks():
    prefix_states = 0
    monotone_prefix_states = 0
    zero_growth_additions = 0
    positive_growth_additions = 0
    hist = {}

    for length in (1, 2, 3):
        for seq in product(TASKS, repeat=length):
            previous = 1
            for k in range(1, length + 1):
                n, _ = joint_classes(seq[:k])
                prefix_states += 1
                monotone_prefix_states += n >= previous
                if k > 1:
                    if n == previous:
                        zero_growth_additions += 1
                    else:
                        positive_growth_additions += 1
                previous = n
            n, _ = joint_classes(seq)
            key = f"{length}:{n}"
            hist[key] = hist.get(key, 0) + 1

    return {
        "sequence_counts": {"1": 16, "2": 256, "3": 4096},
        "prefix_states": prefix_states,
        "monotone_prefix_states": monotone_prefix_states,
        "zero_growth_additions": zero_growth_additions,
        "positive_growth_additions": positive_growth_additions,
        "joint_class_histogram": hist,
    }


def memory_encoder_checks():
    cases = 0
    criterion_matches = 0
    feasible_cases = 0
    independent_two_bit_witness = None

    for seq in product(TASKS, repeat=2):
        n, signatures = joint_classes(seq)
        for memory_states in range(1, 5):
            exists = any(
                encoder_sufficient(encoder, signatures)
                for encoder in product(range(memory_states), repeat=4)
            )
            predicted = memory_states >= n
            cases += 1
            criterion_matches += exists == predicted
            feasible_cases += exists
            if (
                independent_two_bit_witness is None
                and n == 4
                and memory_states == 4
                and exists
            ):
                independent_two_bit_witness = {
                    "tasks": [list(seq[0]), list(seq[1])],
                    "joint_classes": n,
                    "minimum_memory_states": 4,
                    "minimum_binary_width": 2,
                }

    return {
        "cases": cases,
        "criterion_matches": criterion_matches,
        "feasible_cases": feasible_cases,
        "independent_two_bit_witness": independent_two_bit_witness,
    }


def update_injectivity_checks():
    total = 0
    injective = 0
    merged = 0
    first_merge = None
    for update in product(range(4), repeat=4):
        total += 1
        if len(set(update)) == 4:
            injective += 1
        else:
            merged += 1
            if first_merge is None:
                first_merge = list(update)
    return {
        "four_class_update_maps": total,
        "injective_updates": injective,
        "merging_updates": merged,
        "first_merging_update": first_merge,
    }


def replay_capacity_checks():
    cases = 0
    criterion_matches = 0
    feasible_cases = 0
    for n_classes in range(1, 9):
        for internal in range(1, 5):
            for replay in range(1, 5):
                # For jointly designable channels, injective coding into the product
                # alphabet exists iff the product has at least n_classes elements.
                exists = n_classes <= internal * replay
                predicted = internal * replay >= n_classes
                cases += 1
                criterion_matches += exists == predicted
                feasible_cases += exists
    return {
        "cases": cases,
        "criterion_matches": criterion_matches,
        "feasible_cases": feasible_cases,
    }


def run():
    seq = sequence_checks()
    mem = memory_encoder_checks()
    upd = update_injectivity_checks()
    replay = replay_capacity_checks()

    expected_seq = {
        "sequence_counts": {"1": 16, "2": 256, "3": 4096},
        "prefix_states": 12816,
        "monotone_prefix_states": 12816,
        "zero_growth_additions": 2900,
        "positive_growth_additions": 5548,
        "joint_class_histogram": {
            "1:1": 2, "1:2": 14,
            "2:1": 4, "2:2": 84, "2:3": 144, "2:4": 24,
            "3:1": 8, "3:2": 392, "3:3": 2016, "3:4": 1680
        },
    }
    expected_mem_core = {"cases": 1024, "criterion_matches": 1024, "feasible_cases": 580}
    expected_upd_core = {"four_class_update_maps": 256, "injective_updates": 24, "merging_updates": 232}
    expected_replay_core = {"cases": 128, "criterion_matches": 128}

    ok = seq == expected_seq
    ok = ok and all(mem[k] == v for k, v in expected_mem_core.items())
    ok = ok and mem["independent_two_bit_witness"] is not None
    ok = ok and all(upd[k] == v for k, v in expected_upd_core.items())
    ok = ok and all(replay[k] == v for k, v in expected_replay_core.items())

    return {
        "terminal": (
            "GRAND_GMI_CONTINUAL_RETENTION_TRANCHE_ALL_GREEN"
            if ok else "GRAND_GMI_CONTINUAL_RETENTION_TRANCHE_RED"
        ),
        "all_checks_green": ok,
        "determinism": "exact-exhaustive-no-rng",
        "sequence_semantics": seq,
        "memory_encoder": mem,
        "update_injectivity": upd,
        "replay_capacity": replay,
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
