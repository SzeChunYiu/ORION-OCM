#!/usr/bin/env python3
"""Exact developmental-geometry phase calibration.

Two morphologies share the SAME hypothesis space and legal move set over 4-bit
states. They differ only in proposal mass:

LOCAL: 90% over single-bit flips, 10% over aligned pair flips.
CHUNK: 10% over single-bit flips, 90% over aligned pair flips.

A proposal is accepted iff registered ecology quality strictly improves.
Target is 1111 from 0000. We compare dense additive feedback against chunk-level
feedback. Expected first-hit proposal counts are solved exactly as Fractions.
"""

from fractions import Fraction
from functools import lru_cache
import json

TARGET = (1, 1, 1, 1)
START = (0, 0, 0, 0)
SINGLE_MOVES = ((0,), (1,), (2,), (3,))
PAIR_MOVES = ((0, 1), (2, 3))
MOVES = SINGLE_MOVES + PAIR_MOVES

LOCAL_PROBS = (Fraction(9, 40),) * 4 + (Fraction(1, 20),) * 2
CHUNK_PROBS = (Fraction(1, 40),) * 4 + (Fraction(9, 20),) * 2


def flip(state, move):
    out = list(state)
    for i in move:
        out[i] ^= 1
    return tuple(out)


def additive_quality(state, target=TARGET):
    return sum(a == b for a, b in zip(state, target))


def chunk_quality(state, target=TARGET):
    return sum(
        all(state[i] == target[i] for i in pair)
        for pair in PAIR_MOVES
    )


def expected_first_hit(probs, quality_fn):
    @lru_cache(None)
    def T(state):
        if state == TARGET:
            return Fraction(0)
        q = quality_fn(state)
        improving = []
        p_improve = Fraction(0)
        for move, p in zip(MOVES, probs):
            nxt = flip(state, move)
            if quality_fn(nxt) > q:
                improving.append((p, nxt))
                p_improve += p
        if p_improve == 0:
            raise RuntimeError(f"no improving move from {state}")
        return (
            Fraction(1)
            + sum((p * T(nxt) for p, nxt in improving), Fraction(0))
        ) / p_improve

    return T(START)


def frac_record(x):
    return {"fraction": f"{x.numerator}/{x.denominator}", "decimal": float(x)}


def census():
    local_add = expected_first_hit(LOCAL_PROBS, additive_quality)
    chunk_add = expected_first_hit(CHUNK_PROBS, additive_quality)
    local_chunk = expected_first_hit(LOCAL_PROBS, chunk_quality)
    chunk_chunk = expected_first_hit(CHUNK_PROBS, chunk_quality)

    assert local_add < chunk_add
    assert chunk_chunk < local_chunk

    return {
        "schema": "ExactDevelopmentalGeometryPhaseV1",
        "same_hypothesis_space": True,
        "same_legal_move_set": True,
        "difference": "proposal-mass geometry only",
        "target": list(TARGET),
        "start": list(START),
        "local_geometry": {
            "single_move_total_mass": "9/10",
            "pair_move_total_mass": "1/10",
        },
        "chunk_geometry": {
            "single_move_total_mass": "1/10",
            "pair_move_total_mass": "9/10",
        },
        "expected_first_hit_proposals": {
            "additive_feedback": {
                "LOCAL": frac_record(local_add),
                "CHUNK": frac_record(chunk_add),
                "winner": "LOCAL",
            },
            "chunk_feedback": {
                "LOCAL": frac_record(local_chunk),
                "CHUNK": frac_record(chunk_chunk),
                "winner": "CHUNK",
            },
        },
        "terminal": "EXACT_DEVELOPMENTAL_GEOMETRY_PHASE_REVERSAL__PARENT_PRINCIPLE_CALIBRATION",
    }


if __name__ == "__main__":
    print(json.dumps(census(), indent=2, sort_keys=True))
