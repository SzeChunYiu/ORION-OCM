#!/usr/bin/env python3
"""Exact checks for Grand GMI compositional language morphology V1."""
from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path


def set_partitions(n):
    out = []

    def rec(i, blocks):
        if i == n:
            out.append(tuple(tuple(b) for b in blocks))
            return
        for j in range(len(blocks)):
            blocks[j].append(i)
            rec(i + 1, blocks)
            blocks[j].pop()
        blocks.append([i])
        rec(i + 1, blocks)
        blocks.pop()

    rec(0, [])
    return tuple(out)


def partition_profile(sizes, partition):
    entries = 0
    for block in partition:
        block_values = 1
        for i in block:
            block_values *= sizes[i]
        entries += block_values
    return entries, len(partition)


def optimal_block_counts(sizes, lexicon_cost, transmission_cost):
    vals = []
    for part in set_partitions(len(sizes)):
        entries, length = partition_profile(sizes, part)
        cost = lexicon_cost * entries + transmission_cost * length
        vals.append((cost, entries, length, part))
    best = min(v[0] for v in vals)
    return tuple(sorted({v[2] for v in vals if v[0] == best})), best


def phase_checks():
    config_count = 0
    partition_profile_count = 0
    phase_cells = 0
    monotone_sweeps = 0
    monotone_sweeps_ok = 0
    optimal_hist = {}
    extreme_profile_ok = 0

    for k in (2, 3, 4):
        parts = set_partitions(k)
        for sizes in product(range(2, 6), repeat=k):
            config_count += 1
            n_full = 1
            for n in sizes:
                n_full *= n
            n_sum = sum(sizes)
            hol = (tuple(range(k)),)
            full = tuple((i,) for i in range(k))
            if (
                partition_profile(sizes, hol) == (n_full, 1)
                and partition_profile(sizes, full) == (n_sum, k)
            ):
                extreme_profile_ok += 1
            partition_profile_count += len(parts)

            for lam in range(1, 9):
                seq = []
                for c in range(1, 17):
                    counts, _ = optimal_block_counts(sizes, lam, c)
                    phase_cells += 1
                    optimal_hist[str(counts)] = optimal_hist.get(str(counts), 0) + 1
                    seq.append(counts)
                monotone_sweeps += 1
                if all(max(seq[i + 1]) <= min(seq[i]) for i in range(len(seq) - 1)):
                    monotone_sweeps_ok += 1

    return {
        "configuration_count": config_count,
        "partition_profile_count": partition_profile_count,
        "extreme_profile_ok": extreme_profile_ok,
        "phase_cells": phase_cells,
        "monotone_sweeps": monotone_sweeps,
        "monotone_sweeps_ok": monotone_sweeps_ok,
        "optimal_block_count_histogram": optimal_hist,
    }


def leave_one_out_recombination_checks():
    nonholistic_checks = 0
    nonholistic_success = 0
    holistic_missing = 0
    configurations = 0

    for k in (2, 3, 4):
        for sizes in product(range(2, 5), repeat=k):
            configurations += 1
            meanings = tuple(product(*[range(n) for n in sizes]))
            holistic = (tuple(range(k)),)
            for held in meanings:
                train = tuple(m for m in meanings if m != held)
                if held not in train:
                    holistic_missing += 1
                for part in set_partitions(k):
                    if part == holistic:
                        continue
                    nonholistic_checks += 1
                    ok = True
                    for block in part:
                        held_block = tuple(held[i] for i in block)
                        if not any(tuple(m[i] for i in block) == held_block for m in train):
                            ok = False
                            break
                    if ok:
                        nonholistic_success += 1

    return {
        "configurations": configurations,
        "nonholistic_leave_one_out_checks": nonholistic_checks,
        "nonholistic_recombination_success": nonholistic_success,
        "holistic_missing_entries": holistic_missing,
    }


def canonical_witness():
    sizes = (3, 3, 3)
    result = {}
    for c in (1, 5, 20):
        counts, cost = optimal_block_counts(sizes, 1, c)
        result[str(c)] = {"optimal_block_counts": list(counts), "optimal_cost": cost}
    result["profiles"] = {
        "holistic": {"entries": 27, "length": 1},
        "two_block": {"entries": 12, "length": 2},
        "fully_compositional": {"entries": 9, "length": 3},
    }
    return result


def run():
    phase = phase_checks()
    recomb = leave_one_out_recombination_checks()
    witness = canonical_witness()
    expected_phase = {
        "configuration_count": 336,
        "partition_profile_count": 4192,
        "extreme_profile_ok": 336,
        "phase_cells": 43008,
        "monotone_sweeps": 2688,
        "monotone_sweeps_ok": 2688,
    }
    expected_recomb = {
        "configurations": 117,
        "nonholistic_leave_one_out_checks": 94851,
        "nonholistic_recombination_success": 94851,
        "holistic_missing_entries": 7371,
    }
    ok = all(phase[k] == v for k, v in expected_phase.items())
    ok = ok and recomb == expected_recomb
    ok = ok and witness["1"]["optimal_block_counts"] == [3]
    ok = ok and witness["5"]["optimal_block_counts"] == [2]
    ok = ok and witness["20"]["optimal_block_counts"] == [1]
    return {
        "terminal": (
            "GRAND_GMI_COMPOSITIONAL_LANGUAGE_TRANCHE_ALL_GREEN"
            if ok
            else "GRAND_GMI_COMPOSITIONAL_LANGUAGE_TRANCHE_RED"
        ),
        "all_checks_green": ok,
        "determinism": "exact-integer-no-rng",
        "phase": phase,
        "expected_phase": expected_phase,
        "recombination": recomb,
        "expected_recombination": expected_recomb,
        "canonical_ternary_three_role_witness": witness,
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
