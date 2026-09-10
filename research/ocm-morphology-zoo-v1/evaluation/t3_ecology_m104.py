"""GS-R2 held-out T3 m>=104 battery (JOB B endpoint, #221 sec 18 GS-R2).

Why: HST_TRANSFER_BOUND_V1 (PAC-Bayes lane) prices the transfer guarantee
at eps(m) = sqrt((ln K + ln(2 sqrt(m)/delta)) / (2m)) with K = 83, delta
= 0.05: at the zoo's 12-task ecology scale the bound is
BOUND_DERIVED_VACUOUS_AT_SCOPE (eps(12) = 0.62 vs the 0.224507 admission
bar), and it first crosses the admission bar at the crossover
m* = 104 tasks (eps(104) = 0.22393).  The R1 held-out T3 battery
(evaluated_only_on R1 survivors) draws ONE instance per family from
sha256(T3_KEY || family) — 6 tasks, far below m*.  This module replicates
the SAME frozen battery n_calls times with per-call keys derived
deterministically from the SAME R1 T3 key (no new randomness, no new
families, no new physics — every call is the frozen run_t3 on a key-
derived sub-key), yielding n_calls x 6 >= 104 task instances per survivor
so the per-survivor T3 solved-fraction can be read against the m >= m*
crossover regime.

Deterministic pure function of (genome, key) — the draw is a pure
function of the key, nobody chooses instances (#221 held-out contract).
"""
from __future__ import annotations

from typing import Any, Dict

from evaluation.t3_ecology import T3_FAMILIES, evaluate_t3

M104_SUBKEY_TAG = "m104v1"
DEFAULT_N_CALLS = 18  # 18 x 6 families = 108 >= 104 (crossover m*)
CROSSOVER_M = 104


def t3_m104_subkeys(key: str, n_calls: int = DEFAULT_N_CALLS):
    """Deterministic sub-key list: key|tag|i for i in range(n_calls)."""
    return ["%s|%s|%d" % (key, M104_SUBKEY_TAG, i) for i in range(n_calls)]


def evaluate_t3_m104(genome, key: str,
                     n_calls: int = DEFAULT_N_CALLS) -> Dict[str, Any]:
    """m>=104 held-out T3 evaluation: n_calls frozen batteries on
    key-derived sub-keys; aggregate + per-family rollups.  Hard gates are
    applied verbatim per call (same gate code path as T0/T1/T2)."""
    assert n_calls * len(T3_FAMILIES) >= CROSSOVER_M, (
        "n_calls=%d gives m=%d < crossover %d" % (
            n_calls, n_calls * len(T3_FAMILIES), CROSSOVER_M))
    solved = 0
    total = 0
    feasible_calls = 0
    cap = None
    per_family: Dict[str, Dict[str, int]] = {}
    calls = []
    for sub in t3_m104_subkeys(key, n_calls):
        r = evaluate_t3(genome, sub)
        ev = r["evaluation"]
        if cap is None:
            cap = r.get("capability_floor", 0.5)
        solved += int(ev["solved"])
        total += int(ev["total_tasks"])
        feasible_calls += 1 if r["feasible"] else 0
        for fam, st in ev["per_family"].items():
            agg = per_family.setdefault(
                fam, {"solved": 0, "total": 0})
            agg["solved"] += int(st["solved"])
            agg["total"] += int(st["total"])
        calls.append({"subkey": sub, "feasible": r["feasible"],
                      "solved_fraction": ev["solved_fraction"]})
    return {
        "ecology_id": "GSHeldoutT3M104V1",
        "base_t3_key_id_source": "GRAND_SEARCH_R1_FREEZE.json heldout_t3 "
                                 "(replication; subkeys deterministic)",
        "n_calls": n_calls, "n_families": len(T3_FAMILIES),
        "m_total": total, "crossover_m": CROSSOVER_M,
        "m_ge_crossover": total >= CROSSOVER_M,
        "solved": solved, "solved_fraction": round(solved / max(1, total), 6),
        "feasible_calls": feasible_calls, "n_calls_total": n_calls,
        "capability_floor": cap,
        "per_family": {k: dict(v) for k, v in sorted(per_family.items())},
        "calls": calls,
        "tier": "T3-m104",
    }
