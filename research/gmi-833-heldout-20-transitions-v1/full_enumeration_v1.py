from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Callable, Iterable

SEQUENCES = tuple(product((0, 1), repeat=3))
CANDIDATE_COUNT = 16 + 256 * 256
STRATEGY_SIGNATURE = ("enumerate_raw_semantics", "exact_score", "complete_argmin")


@dataclass(frozen=True)
class Summary:
    surface_id: str
    state_bits: int
    error_now_count: int
    error_delay_count: int


def _bit(table: int, index: int) -> int:
    return (table >> index) & 1


def _stateless_errors(output_table: int) -> tuple[int, int]:
    errors = [0, 0]
    for mode in (0, 1):
        for seq in SEQUENCES:
            for t in (1, 2):
                current = seq[t]
                output = _bit(output_table, 2 * mode + current)
                target = current if mode == 0 else seq[t - 1]
                errors[mode] += int(output != target)
    return errors[0], errors[1]


def _stateful_errors(next_table: int, output_table: int) -> tuple[int, int]:
    errors = [0, 0]
    for mode in (0, 1):
        for seq in SEQUENCES:
            state = 0
            for t, current in enumerate(seq):
                index = 4 * state + 2 * mode + current
                output = _bit(output_table, index)
                if t in (1, 2):
                    target = current if mode == 0 else seq[t - 1]
                    errors[mode] += int(output != target)
                state = _bit(next_table, index)
    return errors[0], errors[1]


def build_universe(id_remint: Callable[[int], str] | None = None) -> tuple[Summary, ...]:
    if id_remint is None:
        id_remint = lambda i: f"q{i:05d}"
    out: list[Summary] = []
    raw_id = 0
    for output_table in range(16):
        e0, e1 = _stateless_errors(output_table)
        out.append(Summary(id_remint(raw_id), 0, e0, e1))
        raw_id += 1
    for next_table in range(256):
        for output_table in range(256):
            e0, e1 = _stateful_errors(next_table, output_table)
            out.append(Summary(id_remint(raw_id), 1, e0, e1))
            raw_id += 1
    if len(out) != CANDIDATE_COUNT or len({x.surface_id for x in out}) != CANDIDATE_COUNT:
        raise AssertionError("candidate census/remint failure")
    return tuple(out)


def objective(summary: Summary, p: Fraction, eta: Fraction, state_price: Fraction) -> Fraction:
    if not (Fraction(0) <= p <= Fraction(1)) or eta <= 0 or state_price <= 0:
        raise ValueError("invalid registered world")
    e0 = Fraction(summary.error_now_count, 16)
    e1 = Fraction(summary.error_delay_count, 16)
    return eta * ((1 - p) * e0 + p * e1) + state_price * summary.state_bits


def search(universe: Iterable[Summary], p: Fraction, eta: Fraction, state_price: Fraction) -> dict[str, object]:
    best: Fraction | None = None
    winner_ids: list[str] = []
    winner_state_bits: set[int] = set()
    evaluated = 0
    for summary in universe:
        value = objective(summary, p, eta, state_price)
        evaluated += 1
        if best is None or value < best:
            best = value
            winner_ids = [summary.surface_id]
            winner_state_bits = {summary.state_bits}
        elif value == best:
            winner_ids.append(summary.surface_id)
            winner_state_bits.add(summary.state_bits)
    if best is None:
        raise AssertionError("empty candidate universe")
    return {
        "best": best,
        "winner_ids": tuple(sorted(winner_ids)),
        "winner_state_bits": tuple(sorted(winner_state_bits)),
        "evaluated": evaluated,
        "declared_budget": CANDIDATE_COUNT,
        "strategy_signature": STRATEGY_SIGNATURE,
    }
