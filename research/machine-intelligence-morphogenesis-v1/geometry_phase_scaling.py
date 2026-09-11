#!/usr/bin/env python3
"""Evaluate the prospectively frozen GeometryPhaseScalingFreezeV1 ladder.

Uses dynamic programming for ADDITIVE feedback and the closed form m*H_m/p_pair
for CHUNK feedback. No stochastic sampling.
"""

from functools import lru_cache
from fractions import Fraction
import json

PROTECTED_M = (7, 8, 9, 10)


def expected_additive(m, single_mass):
    pair_mass = 1.0 - single_mass

    @lru_cache(None)
    def T(completed_pairs, half_pairs):
        if completed_pairs == m:
            return 0.0
        zero_pairs = m - completed_pairs - half_pairs
        p_single_zero = single_mass * zero_pairs / m
        p_single_half = single_mass * half_pairs / (2 * m)
        p_pair_zero = pair_mass * zero_pairs / m
        p_improve = p_single_zero + p_single_half + p_pair_zero
        value = 1.0
        if p_single_zero:
            value += p_single_zero * T(completed_pairs, half_pairs + 1)
        if p_single_half:
            value += p_single_half * T(completed_pairs + 1, half_pairs - 1)
        if p_pair_zero:
            value += p_pair_zero * T(completed_pairs + 1, half_pairs)
        return value / p_improve

    return T(0, 0)


def harmonic_fraction(m):
    return sum((Fraction(1, k) for k in range(1, m + 1)), Fraction(0))


def expected_chunk_exact(m, pair_mass):
    return Fraction(m, 1) * harmonic_fraction(m) / Fraction(str(pair_mass))


def evaluate():
    rows = []
    held = True
    for m in PROTECTED_M:
        local_add = expected_additive(m, 0.9)
        chunk_add = expected_additive(m, 0.1)
        local_chunk = expected_chunk_exact(m, 0.1)
        chunk_chunk = expected_chunk_exact(m, 0.9)
        row = {
            "m": m,
            "additive": {
                "LOCAL": local_add,
                "CHUNK": chunk_add,
                "CHUNK_over_LOCAL": chunk_add / local_add,
                "winner": "LOCAL" if local_add < chunk_add else "CHUNK",
            },
            "chunk": {
                "LOCAL_fraction": f"{local_chunk.numerator}/{local_chunk.denominator}",
                "CHUNK_fraction": f"{chunk_chunk.numerator}/{chunk_chunk.denominator}",
                "LOCAL": float(local_chunk),
                "CHUNK": float(chunk_chunk),
                "LOCAL_over_CHUNK": float(local_chunk / chunk_chunk),
                "winner": "CHUNK" if chunk_chunk < local_chunk else "LOCAL",
            },
        }
        if row["additive"]["winner"] != "LOCAL": held = False
        if row["chunk"]["winner"] != "CHUNK": held = False
        if local_chunk / chunk_chunk != 9: held = False
        rows.append(row)
    return {
        "schema": "GeometryPhaseScalingResultV1",
        "freeze": "GEOMETRY_PHASE_SCALING_FREEZE_V1.json",
        "rows": rows,
        "terminal": (
            "GEOMETRY_PHASE_SCALING_PREDICTION_HELD_AT_REGISTERED_SIZES"
            if held else "GEOMETRY_PHASE_SCALING_PREDICTION_FALSIFIED"
        ),
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
