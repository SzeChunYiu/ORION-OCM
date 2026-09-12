#!/usr/bin/env python3
"""Exact finite microscope for GMI predictive-residual quotient theorem v1.

No ML library is used. The microscope exhaustively enumerates every pair of
set partitions on n=1..6 registered histories and verifies:

1. The minimum reusable residual alphabet size is the maximum number of target
   quotient classes inside any predictive quotient class.
2. A constructive residual code with exactly that many symbols decodes the
   target quotient exactly.
3. Zero residual is equivalent to target quotient factorization through the
   predictive quotient.
4. Under a uniform history distribution, H(S_O | S_P) is zero exactly at the
   zero-residual boundary and never exceeds log2(max fiber multiplicity).

The output is deterministic JSON suitable for comparison with the checked-in
receipt.
"""

from __future__ import annotations

from collections import defaultdict
from math import ceil, log2
import json


def set_partitions_rgs(n: int):
    """Yield canonical set partitions as restricted-growth strings."""
    if n < 1:
        return
    a = [0] * n
    a[0] = 0

    def rec(i: int, max_seen: int):
        if i == n:
            yield tuple(a)
            return
        for value in range(max_seen + 2):
            a[i] = value
            yield from rec(i + 1, max(max_seen, value))

    yield from rec(1, 0)


def multiplicities(pred, target):
    fibers = defaultdict(set)
    for p, s in zip(pred, target):
        fibers[p].add(s)
    return {p: len(states) for p, states in fibers.items()}


def construct_residual(pred, target):
    """Construct a residual alphabet reusing local labels across pred fibers."""
    local_maps = {}
    for p in sorted(set(pred)):
        target_states = []
        for i, p_i in enumerate(pred):
            s_i = target[i]
            if p_i == p and s_i not in target_states:
                target_states.append(s_i)
        local_maps[p] = {s: j for j, s in enumerate(target_states)}

    residual = tuple(local_maps[p][s] for p, s in zip(pred, target))
    decoder = {}
    for p, r, s in zip(pred, residual, target):
        old = decoder.setdefault((p, r), s)
        if old != s:
            raise AssertionError("residual decoder collision")
    return residual, decoder


def target_factors_through_predictor(pred, target):
    mapping = {}
    for p, s in zip(pred, target):
        if p in mapping and mapping[p] != s:
            return False
        mapping[p] = s
    return True


def conditional_entropy_uniform(pred, target):
    n = len(pred)
    pred_blocks = defaultdict(list)
    for i, p in enumerate(pred):
        pred_blocks[p].append(i)

    h = 0.0
    for indices in pred_blocks.values():
        block_weight = len(indices) / n
        counts = defaultdict(int)
        for i in indices:
            counts[target[i]] += 1
        h_block = 0.0
        for count in counts.values():
            q = count / len(indices)
            h_block -= q * log2(q)
        h += block_weight * h_block
    return h


def named_hostile(name, pred, target):
    mult = multiplicities(pred, target)
    max_m = max(mult.values())
    residual, decoder = construct_residual(pred, target)
    assert all(decoder[(p, r)] == s for p, r, s in zip(pred, residual, target))
    return {
        "name": name,
        "n": len(pred),
        "predictive_partition": list(pred),
        "target_partition": list(target),
        "max_target_multiplicity_inside_predictive_fiber": max_m,
        "minimum_residual_alphabet": max_m,
        "minimum_fixed_residual_bits": 0 if max_m == 1 else ceil(log2(max_m)),
        "target_factors_through_predictor": target_factors_through_predictor(pred, target),
        "conditional_entropy_uniform_bits": conditional_entropy_uniform(pred, target),
    }


def main():
    total_pairs = 0
    zero_residual_pairs = 0
    nonzero_residual_pairs = 0
    max_fixed_bits_seen = 0
    max_conditional_entropy_seen = 0.0
    by_n = {}

    for n in range(1, 7):
        parts = list(set_partitions_rgs(n))
        pair_count = 0

        for pred in parts:
            for target in parts:
                pair_count += 1
                total_pairs += 1

                mult = multiplicities(pred, target)
                max_m = max(mult.values())
                lower_bound_bits = 0 if max_m == 1 else ceil(log2(max_m))

                residual, decoder = construct_residual(pred, target)
                assert len(set(residual)) == max_m
                assert all(
                    decoder[(p, r)] == s
                    for p, r, s in zip(pred, residual, target)
                )

                factors = target_factors_through_predictor(pred, target)
                assert factors == (max_m == 1)

                h_cond = conditional_entropy_uniform(pred, target)
                assert (abs(h_cond) < 1e-12) == (max_m == 1)
                assert h_cond <= log2(max_m) + 1e-12

                if max_m == 1:
                    zero_residual_pairs += 1
                else:
                    nonzero_residual_pairs += 1

                max_fixed_bits_seen = max(max_fixed_bits_seen, lower_bound_bits)
                max_conditional_entropy_seen = max(max_conditional_entropy_seen, h_cond)

        by_n[str(n)] = {
            "bell_number_partitions": len(parts),
            "partition_pairs_checked": pair_count,
        }

    hostiles = [
        named_hostile(
            "ZERO_RESIDUAL_FACTORIZATION",
            (0, 0, 1, 1),
            (0, 0, 1, 1),
        ),
        named_hostile(
            "ONE_BIT_PREDICTIVE_ALIAS",
            (0, 0, 1, 1),
            (0, 1, 2, 2),
        ),
        named_hostile(
            "FIVE_WAY_RESIDUAL_FIBER",
            (0, 0, 0, 0, 0, 1),
            (0, 1, 2, 3, 4, 5),
        ),
        named_hostile(
            "LINEAGE_STYLE_ALIAS",
            (0, 0, 1, 1, 2, 2),
            (0, 1, 2, 3, 4, 5),
        ),
    ]

    receipt = {
        "schema": "GMI_PREDICTIVE_RESIDUAL_QUOTIENT_EXACT_V1",
        "status": "GREEN",
        "terminal": "PREDICTIVE_RESIDUAL_QUOTIENT_EXACT_FINITE_GREEN",
        "scope": "all set-partition pairs on n=1..6 labeled histories",
        "checks": {
            "residual_alphabet_equals_max_within_predictive_target_multiplicity": True,
            "constructive_decoder_exact": True,
            "zero_residual_iff_target_factors_through_predictive_quotient": True,
            "uniform_conditional_entropy_zero_iff_zero_residual": True,
            "uniform_conditional_entropy_le_log2_max_multiplicity": True,
        },
        "counts": {
            "partition_pairs_checked": total_pairs,
            "zero_residual_pairs": zero_residual_pairs,
            "nonzero_residual_pairs": nonzero_residual_pairs,
            "max_fixed_residual_bits_seen": max_fixed_bits_seen,
            "max_conditional_entropy_uniform_bits_seen": max_conditional_entropy_seen,
        },
        "by_n": by_n,
        "named_hostiles": hostiles,
        "claim_ceiling": (
            "Exact finite partition theorem calibration only; does not establish "
            "real-world quotient identifiability or empirical RQM superiority."
        ),
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
