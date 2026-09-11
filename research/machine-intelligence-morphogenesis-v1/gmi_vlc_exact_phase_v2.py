#!/usr/bin/env python3
"""Second exact VLC phase microscope, frozen after the V1 falsified twin.

Tests the corrected decomposition:
  - factorization granularity is not determined by invalidation rate alone;
  - versioning has an exact retention-vs-memory threshold for fixed k.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

N = 18
QUERY_ARITY = 5
MODULE_SIZES = (1, 2, 3, 6, 9, 18)
VERIFY_MULTIPLIER = Fraction(2, 5)  # 0.40
MEMORY_PRICE = 6
VERSIONED_EXPOSURE = Fraction(1, 50)  # 0.02
UPDATE_SWEEP = (0, 1, 2, 5, 10, 20, 50, 100, 200, 400, 900)


@dataclass(frozen=True)
class Regime:
    name: str
    horizon: int
    updates: int
    cone: int
    retention: Fraction
    coordination: Fraction


REGIMES = (
    Regime("R2_TARGET", 200_000, 900, 1, Fraction(3, 1), Fraction(3, 10)),
    Regime("S2_STATIONARY_HIGH_SIGMA", 200_000, 0, 1, Fraction(3, 1), Fraction(3, 10)),
    Regime("W2_WEAK_RETENTION", 200_000, 900, 1, Fraction(0, 1), Fraction(3, 10)),
    Regime("H2_SHORT_REUSE", 10_000, 900, 1, Fraction(3, 1), Fraction(3, 10)),
    Regime("C2_HIGH_COORDINATION", 200_000, 900, 1, Fraction(3, 1), Fraction(3, 2)),
)


def modules(k: int) -> list[set[int]]:
    assert N % k == 0
    return [set(range(i, i + k)) for i in range(0, N, k)]


def touched(scope: Iterable[int], ms: list[set[int]]) -> int:
    s = set(scope)
    return sum(bool(s & m) for m in ms)


def exact_avg_touched(k: int, scope_size: int) -> Fraction:
    ms = modules(k)
    vals = [touched(scope, ms) for scope in itertools.combinations(range(N), scope_size)]
    return Fraction(sum(vals), len(vals))


def materialization(k: int) -> int:
    return 2**k


def lifecycle(regime: Regime, k: int, versioned: bool) -> tuple[Fraction, dict]:
    ms = modules(k)
    m = len(ms)
    w = materialization(k)
    q = exact_avg_touched(k, QUERY_ARITY)
    u = exact_avg_touched(k, regime.cone)

    build = m * w
    serve_per_query = q + regime.coordination * max(Fraction(0), q - 1)
    serve = regime.horizon * serve_per_query
    rebuild = u * w
    update = regime.updates * rebuild * (1 + VERIFY_MULTIPLIER)
    memory = MEMORY_PRICE * m * w * (2 if versioned else 1)
    exposure = VERSIONED_EXPOSURE if versioned else Fraction(1, 1)
    retention = regime.updates * regime.retention * rebuild * exposure
    total = build + serve + update + memory + retention

    row = {
        "regime": regime.name,
        "module_size": k,
        "module_count": m,
        "versioned": versioned,
        "avg_query_modules": float(q),
        "avg_update_modules": float(u),
        "build": float(build),
        "serve": float(serve),
        "update": float(update),
        "memory": float(memory),
        "retention": float(retention),
        "total": float(total),
    }
    return total, row


def analytic_versioned_wins(k: int, updates: int, retention: Fraction, cone: int = 1) -> bool:
    m = N // k
    q_u = exact_avg_touched(k, cone)
    lhs = updates * retention
    rhs = Fraction(MEMORY_PRICE * m, 1) / ((1 - VERSIONED_EXPOSURE) * q_u)
    return lhs > rhs


def enumerated_versioned_wins(k: int, updates: int, retention: Fraction, cone: int = 1) -> bool:
    reg = Regime("THRESHOLD", 0, updates, cone, retention, Fraction(0, 1))
    c0, _ = lifecycle(reg, k, False)
    c1, _ = lifecycle(reg, k, True)
    return c1 < c0


def evaluate() -> dict:
    rows = []
    winners = {}
    for reg in REGIMES:
        rr = []
        for k in MODULE_SIZES:
            for v in (False, True):
                total, row = lifecycle(reg, k, v)
                rr.append((total, row))
                rows.append(row)
        rr.sort(key=lambda x: (x[0], x[1]["module_size"], x[1]["versioned"]))
        winners[reg.name] = rr[0][1]

    r2 = winners["R2_TARGET"]
    preds = {
        "R2_versioned": r2["versioned"] is True,
        "R2_intermediate": 1 < r2["module_size"] < N,
        "S2_unversioned_factorized": (
            winners["S2_STATIONARY_HIGH_SIGMA"]["versioned"] is False
            and winners["S2_STATIONARY_HIGH_SIGMA"]["module_size"] < N
        ),
        "W2_unversioned": winners["W2_WEAK_RETENTION"]["versioned"] is False,
        "H2_no_coarser": winners["H2_SHORT_REUSE"]["module_size"] <= r2["module_size"],
        "C2_no_finer": winners["C2_HIGH_COORDINATION"]["module_size"] >= r2["module_size"],
    }

    threshold_rows = []
    threshold_green = True
    for k in MODULE_SIZES:
        for u in UPDATE_SWEEP:
            analytic = analytic_versioned_wins(k, u, Fraction(3, 1), 1)
            enumerated = enumerated_versioned_wins(k, u, Fraction(3, 1), 1)
            same = analytic == enumerated
            threshold_green = threshold_green and same
            threshold_rows.append(
                {
                    "module_size": k,
                    "updates": u,
                    "analytic_versioned_wins": analytic,
                    "enumerated_versioned_wins": enumerated,
                    "agree": same,
                }
            )

    green = all(preds.values()) and threshold_green
    return {
        "schema": "GMIVLCExactPhaseReceiptV2",
        "predictions": preds,
        "threshold_green": threshold_green,
        "all_green": green,
        "terminal": (
            "VLC_PHASE_DECOMPOSITION_V2_EXACT_GREEN"
            if green
            else "VLC_PHASE_DECOMPOSITION_V2_EXACT_FAIL"
        ),
        "winners": winners,
        "threshold_rows": threshold_rows,
        "rows": rows,
        "claim_ceiling": "Exact finite correction/calibration only; no new morphology or general empirical GMI law established.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = evaluate()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
