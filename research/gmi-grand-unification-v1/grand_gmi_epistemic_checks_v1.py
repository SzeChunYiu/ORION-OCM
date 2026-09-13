#!/usr/bin/env python3
"""Exact finite checks for Grand GMI epistemic acquisition V1.

No RNG, no fitted parameters, no tolerance-band verdicts.
The finite microscope exhausts all 4-world x 3-binary-experiment tables and all
binary obligation partitions of the four worlds.
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from itertools import combinations, product
from math import ceil, log2
from pathlib import Path


HYPOTHESES = tuple(range(4))
EXPERIMENTS = tuple(range(3))


def _row_labels(matrix):
    rows = [tuple(matrix[h]) for h in HYPOTHESES]
    unique = {row: i for i, row in enumerate(sorted(set(rows)))}
    return tuple(unique[row] for row in rows)


def semantic_adaptive_depth(matrix, labels):
    """Minimum worst-case adaptive experiment depth, or None if unidentifiable."""
    rows = [tuple(matrix[h]) for h in HYPOTHESES]
    for i in HYPOTHESES:
        for j in HYPOTHESES:
            if rows[i] == rows[j] and labels[i] != labels[j]:
                return None

    @lru_cache(maxsize=None)
    def solve(state, remaining):
        state = tuple(state)
        if len({labels[h] for h in state}) <= 1:
            return 0
        best = None
        for experiment in remaining:
            parts = {0: [], 1: []}
            for h in state:
                parts[matrix[h][experiment]].append(h)
            if not parts[0] or not parts[1]:
                continue
            nxt = tuple(e for e in remaining if e != experiment)
            child_depths = []
            for part in parts.values():
                depth = solve(tuple(part), nxt)
                if depth is None:
                    break
                child_depths.append(depth)
            else:
                candidate = 1 + max(child_depths)
                best = candidate if best is None else min(best, candidate)
        return best

    return solve(HYPOTHESES, EXPERIMENTS)


def semantic_nonadaptive_size(matrix, labels):
    """Minimum fixed experiment-panel size, or None if unidentifiable."""
    for k in range(len(EXPERIMENTS) + 1):
        for panel in combinations(EXPERIMENTS, k):
            seen = {}
            ok = True
            for h in HYPOTHESES:
                signature = tuple(matrix[h][e] for e in panel)
                label = labels[h]
                if signature in seen and seen[signature] != label:
                    ok = False
                    break
                seen[signature] = label
            if ok:
                return k
    return None


def enumerate_checks():
    matrix_count = 0
    adaptive_le_nonadaptive = 0
    information_lower_bound_ok = 0
    strict_adaptive_advantage = 0

    semantic_instances = 0
    semantic_identifiable = 0
    semantic_unidentifiable = 0
    semantic_nontrivial_identifiable = 0
    semantic_cheaper_than_full_world = 0

    adaptive_witness = None
    obligation_witness = None

    for bits in product((0, 1), repeat=12):
        matrix = tuple(tuple(bits[3*h:3*h+3]) for h in HYPOTHESES)
        row_labels = _row_labels(matrix)
        full_depth = semantic_adaptive_depth(matrix, row_labels)
        fixed_full = semantic_nonadaptive_size(matrix, row_labels)
        num_observational_classes = len(set(matrix))

        matrix_count += 1
        if full_depth <= fixed_full:
            adaptive_le_nonadaptive += 1
        lower_bound = ceil(log2(num_observational_classes)) if num_observational_classes else 0
        if full_depth >= lower_bound:
            information_lower_bound_ok += 1
        if full_depth < fixed_full:
            strict_adaptive_advantage += 1
            if adaptive_witness is None:
                adaptive_witness = {
                    "matrix": [list(row) for row in matrix],
                    "adaptive_depth": full_depth,
                    "fixed_panel_size": fixed_full,
                    "observational_classes": num_observational_classes,
                }

        for labels in product((0, 1), repeat=4):
            semantic_instances += 1
            depth = semantic_adaptive_depth(matrix, labels)
            if depth is None:
                semantic_unidentifiable += 1
                continue

            semantic_identifiable += 1
            if len(set(labels)) > 1:
                semantic_nontrivial_identifiable += 1
            if depth < full_depth:
                semantic_cheaper_than_full_world += 1

            target_matrix = (
                (0, 0, 0),
                (0, 1, 0),
                (1, 0, 0),
                (1, 0, 1),
            )
            target_labels = (0, 0, 1, 1)
            if matrix == target_matrix and labels == target_labels:
                obligation_witness = {
                    "matrix": [list(row) for row in matrix],
                    "semantic_labels": list(labels),
                    "semantic_adaptive_depth": depth,
                    "full_world_adaptive_depth": full_depth,
                    "full_world_fixed_panel_size": fixed_full,
                }

    expected = {
        "matrix_count": 4096,
        "adaptive_le_nonadaptive": 4096,
        "information_lower_bound_ok": 4096,
        "strict_adaptive_advantage": 576,
        "semantic_instances": 65536,
        "semantic_identifiable": 44592,
        "semantic_unidentifiable": 20944,
        "semantic_nontrivial_identifiable": 36400,
        "semantic_cheaper_than_full_world": 27472,
    }
    observed = {
        "matrix_count": matrix_count,
        "adaptive_le_nonadaptive": adaptive_le_nonadaptive,
        "information_lower_bound_ok": information_lower_bound_ok,
        "strict_adaptive_advantage": strict_adaptive_advantage,
        "semantic_instances": semantic_instances,
        "semantic_identifiable": semantic_identifiable,
        "semantic_unidentifiable": semantic_unidentifiable,
        "semantic_nontrivial_identifiable": semantic_nontrivial_identifiable,
        "semantic_cheaper_than_full_world": semantic_cheaper_than_full_world,
    }
    all_checks_green = observed == expected
    all_checks_green = all_checks_green and obligation_witness == {
        "matrix": [[0, 0, 0], [0, 1, 0], [1, 0, 0], [1, 0, 1]],
        "semantic_labels": [0, 0, 1, 1],
        "semantic_adaptive_depth": 1,
        "full_world_adaptive_depth": 2,
        "full_world_fixed_panel_size": 3,
    }
    all_checks_green = all_checks_green and adaptive_witness is not None

    return {
        "terminal": (
            "GRAND_GMI_EPISTEMIC_ACQUISITION_TRANCHE_ALL_GREEN"
            if all_checks_green
            else "GRAND_GMI_EPISTEMIC_ACQUISITION_TRANCHE_RED"
        ),
        "all_checks_green": all_checks_green,
        "determinism": "exhaustive-no-rng",
        "observed": observed,
        "expected": expected,
        "canonical_obligation_witness": obligation_witness,
        "first_strict_adaptive_witness": adaptive_witness,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = enumerate_checks()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
