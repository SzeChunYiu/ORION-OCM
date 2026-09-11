#!/usr/bin/env python3
"""Exact finite phase microscope for the frozen VLC prediction.

This is a deterministic calibration model, not an unknown-form search and not
an empirical claim about real machine intelligence.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

N = 15
QUERY_ARITY = 4
MODULE_SIZES = (1, 3, 5, 15)
COORDINATION_COST = Fraction(1, 4)
VERIFY_MULTIPLIER = Fraction(1, 2)
MEMORY_PRICE = 8
VERSIONED_COPIES = 2
UNVERSIONED_COPIES = 1
VERSIONED_EXPOSURE = Fraction(1, 20)  # 0.05
UNVERSIONED_EXPOSURE = 1


@dataclass(frozen=True)
class Regime:
    name: str
    horizon_queries: int
    update_events: int
    update_cone: int
    retention_price: Fraction


REGIMES = (
    Regime("R_STAR_TARGET", 120_000, 600, 1, Fraction(5, 2)),
    Regime("T1_STATIONARY", 120_000, 0, 1, Fraction(5, 2)),
    Regime("T2_DENSE_DEPENDENCY", 120_000, 600, 12, Fraction(5, 2)),
    Regime("T3_WEAK_RETENTION", 120_000, 600, 1, Fraction(0, 1)),
    Regime("T4_SHORT_REUSE", 6_000, 600, 1, Fraction(5, 2)),
)


def partitions_for_k(k: int) -> list[set[int]]:
    assert N % k == 0
    return [set(range(start, start + k)) for start in range(0, N, k)]


def touched_modules(scope: Iterable[int], modules: list[set[int]]) -> int:
    s = set(scope)
    return sum(bool(s & m) for m in modules)


def exact_average_module_count(k: int, scope_size: int) -> Fraction:
    modules = partitions_for_k(k)
    counts = [
        touched_modules(scope, modules)
        for scope in itertools.combinations(range(N), scope_size)
    ]
    return Fraction(sum(counts), len(counts))


def candidate_row(regime: Regime, k: int, versioned: bool) -> dict:
    modules = partitions_for_k(k)
    module_count = len(modules)
    local_materialization = 2**k
    build_work = module_count * local_materialization

    avg_query_modules = exact_average_module_count(k, QUERY_ARITY)
    avg_update_modules = exact_average_module_count(k, regime.update_cone)

    serve_per_query = avg_query_modules + COORDINATION_COST * max(
        Fraction(0, 1), avg_query_modules - 1
    )
    serving_work = regime.horizon_queries * serve_per_query

    rebuild_per_update = avg_update_modules * local_materialization
    update_per_event = rebuild_per_update * (1 + VERIFY_MULTIPLIER)
    update_work = regime.update_events * update_per_event

    copies = VERSIONED_COPIES if versioned else UNVERSIONED_COPIES
    memory_charge = MEMORY_PRICE * module_count * local_materialization * copies

    exposure = VERSIONED_EXPOSURE if versioned else UNVERSIONED_EXPOSURE
    retention_per_event = regime.retention_price * rebuild_per_update * exposure
    retention_penalty = regime.update_events * retention_per_event

    total = build_work + serving_work + update_work + memory_charge + retention_penalty

    def f(x: Fraction | int) -> float:
        return float(x)

    return {
        "regime": regime.name,
        "module_size": k,
        "module_count": module_count,
        "versioned": versioned,
        "avg_query_modules": f(avg_query_modules),
        "avg_update_modules": f(avg_update_modules),
        "build_work": f(build_work),
        "serving_work": f(serving_work),
        "update_work": f(update_work),
        "memory_charge": f(memory_charge),
        "retention_penalty": f(retention_penalty),
        "total_cost": f(total),
        "_total_fraction": total,
    }


def evaluate() -> dict:
    rows: list[dict] = []
    winners: dict[str, dict] = {}

    for regime in REGIMES:
        regime_rows = [
            candidate_row(regime, k, versioned)
            for k in MODULE_SIZES
            for versioned in (False, True)
        ]
        regime_rows.sort(key=lambda r: (r["_total_fraction"], r["module_size"], r["versioned"]))
        winners[regime.name] = {
            k: v for k, v in regime_rows[0].items() if not k.startswith("_")
        }
        rows.extend(regime_rows)

    r = winners["R_STAR_TARGET"]
    t1 = winners["T1_STATIONARY"]
    t2 = winners["T2_DENSE_DEPENDENCY"]
    t3 = winners["T3_WEAK_RETENTION"]
    t4 = winners["T4_SHORT_REUSE"]

    predictions = {
        "R_STAR_versioned": r["versioned"] is True,
        "R_STAR_intermediate_module_size": 1 < r["module_size"] < N,
        "T1_stationary_monolithic_unversioned": (
            t1["module_size"] == N and t1["versioned"] is False
        ),
        "T2_dense_is_no_finer_than_target": t2["module_size"] >= r["module_size"],
        "T3_weak_retention_unversioned": t3["versioned"] is False,
        "T4_short_reuse_no_coarser_than_target": t4["module_size"] <= r["module_size"],
    }

    green = all(predictions.values())
    terminal = (
        "VLC_PHASE_PREDICTION_EXACT_MICROSCOPE_GREEN"
        if green
        else "VLC_PHASE_PREDICTION_EXACT_MICROSCOPE_FAIL"
    )

    clean_rows = [
        {k: v for k, v in row.items() if not k.startswith("_")}
        for row in rows
    ]

    return {
        "schema": "GMIVLCExactPhaseReceiptV1",
        "status": "confirmatory exact finite calibration",
        "constants": {
            "N": N,
            "query_arity": QUERY_ARITY,
            "module_sizes": list(MODULE_SIZES),
            "coordination_cost": float(COORDINATION_COST),
            "verify_multiplier": float(VERIFY_MULTIPLIER),
            "memory_price": MEMORY_PRICE,
            "versioned_copies": VERSIONED_COPIES,
            "unversioned_copies": UNVERSIONED_COPIES,
            "versioned_exposure": float(VERSIONED_EXPOSURE),
            "unversioned_exposure": UNVERSIONED_EXPOSURE,
        },
        "regimes": [
            {
                **asdict(reg),
                "retention_price": float(reg.retention_price),
            }
            for reg in REGIMES
        ],
        "winners": winners,
        "predictions": predictions,
        "all_predictions_green": green,
        "terminal": terminal,
        "rows": clean_rows,
        "claim_ceiling": (
            "Exact finite lifecycle calibration only. Generic amortization/locality economics "
            "remain parent-owned; this does not establish a new machine-intelligence morphology."
        ),
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
