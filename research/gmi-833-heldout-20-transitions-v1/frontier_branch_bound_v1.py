from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

SEQS = tuple(product((0, 1), repeat=3))
RAW_CANDIDATE_BUDGET = 65552
STRATEGY_SIGNATURE = ("enumerate_risk_summary", "compress_equivalent_risks", "lower_bound_prune")


@dataclass(frozen=True)
class RiskPoint:
    state_bits: int
    error_now_count: int
    error_delay_count: int
    multiplicity: int


def _truth_bit(code: int, s: int, m: int, x: int) -> int:
    return (code >> (4 * s + 2 * m + x)) & 1


def _small_truth_bit(code: int, m: int, x: int) -> int:
    return (code >> (2 * m + x)) & 1


def build_risk_points() -> tuple[tuple[RiskPoint, ...], dict[str, int]]:
    counts: dict[tuple[int, int, int], int] = {}
    raw = 0

    for output in range(16):
        en = ed = 0
        for seq in SEQS:
            for t in (1, 2):
                x = seq[t]
                en += int(_small_truth_bit(output, 0, x) != x)
                ed += int(_small_truth_bit(output, 1, x) != seq[t - 1])
        key = (0, en, ed)
        counts[key] = counts.get(key, 0) + 1
        raw += 1

    for transition in range(256):
        for output in range(256):
            en = ed = 0
            for mode in (0, 1):
                for seq in SEQS:
                    state = 0
                    for t, x in enumerate(seq):
                        y = _truth_bit(output, state, mode, x)
                        if t >= 1:
                            target = x if mode == 0 else seq[t - 1]
                            if y != target:
                                if mode == 0:
                                    en += 1
                                else:
                                    ed += 1
                        state = _truth_bit(transition, state, mode, x)
            key = (1, en, ed)
            counts[key] = counts.get(key, 0) + 1
            raw += 1

    if raw != RAW_CANDIDATE_BUDGET or sum(counts.values()) != RAW_CANDIDATE_BUDGET:
        raise AssertionError("raw census mismatch")
    points = tuple(
        RiskPoint(k[0], k[1], k[2], multiplicity)
        for k, multiplicity in sorted(counts.items())
    )
    return points, {"raw_candidates": raw, "risk_points": len(points)}


def _score(point: RiskPoint, p: Fraction, eta: Fraction, state_price: Fraction) -> Fraction:
    e_now = Fraction(point.error_now_count, 16)
    e_delay = Fraction(point.error_delay_count, 16)
    return eta * ((1 - p) * e_now + p * e_delay) + state_price * point.state_bits


def search(points: tuple[RiskPoint, ...], p: Fraction, eta: Fraction, state_price: Fraction) -> dict[str, object]:
    if not (Fraction(0) <= p <= Fraction(1)) or eta <= 0 or state_price <= 0:
        raise ValueError("invalid registered world")

    # Lower bound is the unavoidable state-price term; all error contribution is nonnegative.
    ordered = sorted(points, key=lambda z: (state_price * z.state_bits, z.error_now_count + z.error_delay_count,
                                            z.state_bits, z.error_now_count, z.error_delay_count))
    incumbent: Fraction | None = None
    winner_state_bits: set[int] = set()
    evaluated_points = 0
    pruned_points = 0
    represented_winner_candidates = 0

    for point in ordered:
        lower_bound = state_price * point.state_bits
        if incumbent is not None and lower_bound > incumbent:
            pruned_points += 1
            continue
        value = _score(point, p, eta, state_price)
        evaluated_points += 1
        if incumbent is None or value < incumbent:
            incumbent = value
            winner_state_bits = {point.state_bits}
            represented_winner_candidates = point.multiplicity
        elif value == incumbent:
            winner_state_bits.add(point.state_bits)
            represented_winner_candidates += point.multiplicity

    if incumbent is None:
        raise AssertionError("empty risk frontier")
    return {
        "best": incumbent,
        "winner_state_bits": tuple(sorted(winner_state_bits)),
        "evaluated_points": evaluated_points,
        "pruned_points": pruned_points,
        "represented_winner_candidates": represented_winner_candidates,
        "declared_budget": RAW_CANDIDATE_BUDGET,
        "strategy_signature": STRATEGY_SIGNATURE,
    }
