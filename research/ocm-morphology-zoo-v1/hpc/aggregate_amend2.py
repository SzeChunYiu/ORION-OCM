"""Aggregate AMEND-2 runs ONLY when every expected (pair, encoding, seed)
has an ok disposition and a verifiable receipt chain.

Emits results/AGGREGATE_AMEND2.json: per-(pair,encoding) means on the
AMEND_1 axes, the FROZEN matched-pair winner rule, the section-15 terminal
per FREEZE_V1_AMEND_2.scoring_rules_amend2.terminal_rule_FROZEN, codec cost
charging, and an E0-vs-AMEND_1 determinism cross-check (E0 tasks recompute
the identical amend-1 configurations, so their metric fields must match the
QDA1 production results bit-for-bit).
"""
from __future__ import annotations

import json
import os
import sys

ROOT = sys.argv[1]
with open(os.path.join(ROOT, "FREEZE_V1_AMEND_2.json")) as f:
    A2 = json.load(f)
PAIRS = [p["pair_id"] for p in A2["arms_amend2"]["pairs"]]
# the freeze names encodings E0_direct/E1_cgp; workers tag files with the
# internal short codes (same normalization as qd_run_amend2.py)
ENCS = [e.split("_")[0] for e in A2["arms_amend2"]["encodings"]]
assert sorted(ENCS) == ["E0", "E1"], "unexpected encodings in freeze"
SEEDS = A2["arms_amend2"]["seeds"]
OWN = {"R01": "pareto_recovery", "M03": "S3d10_cell_recovery",
       "M05": "B2d20_cell_recovery", "M06": "CVT_census_niche_recovery"}
# amend-1 arm each E0 pair recomputes (determinism cross-check)
A1_ARM = {"R01": "P01_random_search", "M03": "P03_map_elites",
          "M05": "P05_map_elites_B", "M06": "P06_cvt_map_elites"}
XCHECK_FIELDS = ("evals", "n_elites", "pareto_recovery", "S3d10_cells_hit",
                 "B2d20_cells_hit", "CVT_census_niches_hit", "best_dev",
                 "qd_score")

from evaluation.receipts import verify_receipt  # noqa: E402

missing, failed, rows = [], [], []
for pair in PAIRS:
    for enc in ENCS:
        for seed in SEEDS:
            tag = "%s_%s_s%d" % (pair, enc, seed)
            status = os.path.join(ROOT, "results", "QDA2_%s.status" % tag)
            if not os.path.exists(status):
                missing.append(tag)
                continue
            if open(status).read().split()[0] != "ok":
                failed.append((tag, open(status).read().strip()))
                continue
            with open(os.path.join(ROOT, "results", "QDA2_%s.json" % tag)) as f:
                rows.append(json.load(f))
            with open(os.path.join(ROOT, "manifests", "receipts", "QDA2_%s.receipt.json" % tag)) as f:
                rcpt = json.load(f)
            if not verify_receipt(rcpt):
                failed.append((tag, "receipt chain invalid"))
if missing or failed:
    print(json.dumps({"aggregate": "REFUSED", "missing": missing,
                      "failed": [f[0] for f in failed]}, indent=1))
    sys.exit(2)

METRICS = ("pareto_recovery", "S3d10_cell_recovery", "B2d20_cell_recovery",
           "CVT_census_niche_recovery", "best_dev", "n_elites", "wall_s",
           "cpu_hours", "codec_seconds", "codec_share", "unique_phenotypes")
def _mean(vals):
    """Mean over present values; metrics absent from an arm's result
    (e.g. unique_phenotypes for map_elites arms) yield None, not a crash."""
    xs = [v for v in vals if v is not None]
    return round(sum(xs) / len(xs), 6) if xs else None


cells_out = {}
for pair in PAIRS:
    for enc in ENCS:
        rs = [r for r in rows if r["pair"] == pair and r["encoding"] == enc]
        m = {k: _mean([r.get(k) for r in rs]) for k in METRICS}
        m.update({"seeds": len(rs), "evals_per_seed": rs[0]["evals"],
                  "budget": rs[0]["budget"],
                  "best_dev_max": max(r["best_dev"] for r in rs),
                  "per_seed": {str(r["seed"]): {k: r[k] for k in
                                                ("evals", "wall_s", "n_elites",
                                                 "pareto_recovery", OWN[pair],
                                                 "best_dev", "codec_seconds",
                                                 "codec_share")} for r in rs}})
        cells_out["%s_%s" % (pair, enc)] = m


def winner(pair, enc):
    """+1 enc wins the pair, 0 no winner, -1 other wins (frozen rule)."""
    a = cells_out["%s_%s" % (pair, enc)]
    b = cells_out["%s_%s" % (pair, "E1" if enc == "E0" else "E0")]
    crit = ["pareto_recovery", OWN[pair], "best_dev"]
    ge = all(a[c] >= b[c] for c in crit)
    gt = any(a[c] > b[c] for c in crit)
    if ge and gt:
        return 1
    le = all(a[c] <= b[c] for c in crit)
    if le and any(a[c] < b[c] for c in crit):
        return -1
    return 0


pair_results = {}
cgp_wins = direct_wins = 0
for pair in PAIRS:
    w = winner(pair, "E1")
    if w == 1:
        label = "CGP"
        cgp_wins += 1
    elif w == -1:
        label = "DIRECT"
        direct_wins += 1
    else:
        label = "TIE"
    a = cells_out["%s_E0" % pair]
    b = cells_out["%s_E1" % pair]
    pair_results[pair] = {
        "winner": label, "own_axis": OWN[pair],
        "direct": {k: a[k] for k in ("pareto_recovery", OWN[pair], "best_dev",
                                     "n_elites", "cpu_hours")},
        "cgp": {k: b[k] for k in ("pareto_recovery", OWN[pair], "best_dev",
                                  "n_elites", "cpu_hours", "codec_share")},
        "cgp_minus_direct": {k: round(b[k] - a[k], 6) for k in
                             ("pareto_recovery", OWN[pair], "best_dev", "n_elites")},
    }

if cgp_wins == len(PAIRS):
    verdict = "ENCODING_CHOICE_DOMINATES"
elif cgp_wins == 0 and direct_wins >= 1:
    verdict = "PARENT_ARCHITECTURE_SUFFICIENT"
else:
    verdict = "MIXED_INTERMEDIATE_NO_TERMINAL"

# E0 determinism cross-check vs amend-1 production results
xcheck = {"compared": 0, "matches": 0, "drifts": []}
for pair, a1arm in A1_ARM.items():
    for seed in SEEDS:
        q2 = os.path.join(ROOT, "results", "QDA2_%s_E0_s%d.json" % (pair, seed))
        q1 = os.path.join(ROOT, "results", "QDA1_%s_s%d.json" % (a1arm, seed))
        if not (os.path.exists(q2) and os.path.exists(q1)):
            continue
        with open(q2) as f:
            r2 = json.load(f)
        with open(q1) as f:
            r1 = json.load(f)
        for k in XCHECK_FIELDS:
            xcheck["compared"] += 1
            if r2.get(k) == r1.get(k):
                xcheck["matches"] += 1
            else:
                xcheck["drifts"].append({"pair": pair, "seed": seed, "field": k,
                                         "amend2": r2.get(k), "amend1": r1.get(k)})

out = {
    "aggregate_id": "MZD5_AMEND2_ENCODING",
    "amendment": A2["amendment_id"],
    "n_runs": len(rows),
    "budget_per_task": rows[0]["budget"],
    "cells": cells_out,
    "pair_results": pair_results,
    "pair_wins": {"CGP": cgp_wins, "DIRECT": direct_wins,
                  "TIE": len(PAIRS) - cgp_wins - direct_wins},
    "verdict_terminal": verdict,
    "terminal_rule_source": "FREEZE_V1_AMEND_2.json scoring_rules_amend2.terminal_rule_FROZEN",
    "codec_charging": "codec_seconds accumulated inside the E1 arm wall time; same-eval-count view runs both encodings at budget 40000, same-CPU-hour view charges codec to E1",
    "e0_vs_amend1_determinism": xcheck,
}
with open(os.path.join(ROOT, "results", "AGGREGATE_AMEND2.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({"aggregate": "OK", "runs": len(rows), "verdict": verdict,
                  "pair_wins": out["pair_wins"],
                  "xcheck_drifts": len(xcheck["drifts"])}))
