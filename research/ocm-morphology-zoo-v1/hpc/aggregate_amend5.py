"""Aggregate AMEND-5 runs ONLY when every expected task has an ok disposition,
a verifiable receipt chain, and every in-worker determinism xcheck true:

  4 arms x 3 seeds = 12 tasks (results/QDA5_*)
    G01_gate_D2d, G00_nogate_D2d, G01_gate_D3d, G00_nogate_D3d

plus archives/GATE_CEILING_TRUTH.json (unscored, frozen pre-score).
Refuses (exit 2) otherwise.  Emits results/AGGREGATE_AMEND5.json:

  - per-arm seed-means on the amend-5 axes (raw + junk-free own-axis
    recovery at the frozen admission bar, best_dev, pareto, elites);
  - the FIRST-MATCH terminal over FREEZE_V1_AMEND_5.
    scoring_rules_amend5.terminal_rule_FROZEN_first_match (sec-15
    vocabulary; verdict computed mechanically, never narrated);
  - gate-vs-control attribution per axis (the ONE varied dimension):
    seed-mean deltas G01 - G00 and the ceiling annotation from the frozen
    GATE-CEILING ladder (structural max reachable at the bar).

Usage: python3 hpc/aggregate_amend5.py <capsule_root>
"""
from __future__ import annotations

import json
import os
import sys

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)
with open(os.path.join(ROOT, "FREEZE_V1_AMEND_5.json")) as f:
    A5 = json.load(f)
ARMS = [a["arm_id"] for a in A5["arms_amend5"]["arms"]]
GATED = A5["arms_amend5"]["gated_arms"]
SEEDS = A5["arms_amend5"]["seeds"]
THR = A5["thresholds_amend5"]
QG = A5["quality_gate_amend5"]

from evaluation.receipts import verify_receipt  # noqa: E402

missing, failed, rows = [], [], []
for arm in ARMS:
    for seed in SEEDS:
        tag = "%s_s%d" % (arm, seed)
        status = os.path.join(ROOT, "results", "QDA5_%s.status" % tag)
        if not os.path.exists(status):
            missing.append(tag)
            continue
        sval = open(status).read().split()
        if sval[0] != "ok":
            failed.append((tag, open(status).read().strip()))
            continue
        with open(os.path.join(ROOT, "results", "QDA5_%s.json" % tag)) as f:
            r = json.load(f)
        rows.append(r)
        bad = [k for k, v in r.get("xchecks_passed", {}).items() if v is not True]
        if bad:
            failed.append((tag, "in-worker xcheck false: %s" % ",".join(bad)))
            continue
        with open(os.path.join(ROOT, "manifests", "receipts",
                               "QDA5_%s.receipt.json" % tag)) as f:
            if not verify_receipt(json.load(f)):
                failed.append((tag, "receipt chain invalid"))
TRUTH_GC = os.path.join(ROOT, "archives", "GATE_CEILING_TRUTH.json")
if not os.path.exists(TRUTH_GC):
    missing.append("archives/GATE_CEILING_TRUTH.json")
else:
    with open(TRUTH_GC) as f:
        GC = json.load(f)["summary"]
    for k, v in GC["xcheck_vs_P00C_HZD9"].items():
        if isinstance(v, bool) and v is not True:
            failed.append(("GATE_CEILING_TRUTH", "xcheck %s false" % k))
if missing or failed:
    print(json.dumps({"aggregate": "REFUSED", "missing": missing,
                      "failed": [f[0] for f in failed]}, indent=1))
    sys.exit(2)


def _mean(vals):
    xs = [v for v in vals if v is not None]
    return round(sum(xs) / len(xs), 6) if xs else None


METRICS = ("raw_own_axis_recovery", "junk_free_own_axis_recovery",
           "junk_free_ratio", "pareto_recovery_T2", "best_dev_T2",
           "min_dev_elite", "n_elites", "n_admissible_feasible",
           "feasible_found", "frontier_retention_fraction", "wall_s",
           "cpu_hours", "evals")
cells = {}
for arm in ARMS:
    rs = [r for r in rows if r["arm"] == arm]
    m = {k: _mean([r.get(k) for r in rs]) for k in METRICS}
    m.update({"seeds": len(rs), "gated": rs[0]["gated"],
              "own_axis": rs[0]["own_axis"], "budget": rs[0]["budget"],
              "best_dev_T2_all_seeds_nonnull": all(
                  r.get("best_dev_T2") is not None for r in rs),
              "per_seed": {str(r["seed"]): {
                  k: r.get(k) for k in ("raw_own_axis_recovery",
                                        "junk_free_own_axis_recovery",
                                        "junk_free_ratio", "best_dev_T2",
                                        "min_dev_elite", "n_elites",
                                        "n_admissible_feasible",
                                        "xchecks_passed")}
                  for r in rs}})
    cells[arm] = m

# ------------------------------------------------ first-match terminal rules
rule_hits = {}
for arm in GATED:
    m = cells[arm]
    rule_hits["%s_own_axis_ge_%s" % (arm, THR["own_axis_absolute_bar"])] = (
        m["raw_own_axis_recovery"] is not None
        and m["raw_own_axis_recovery"] >= THR["own_axis_absolute_bar"])
    rule_hits["%s_best_dev_ge_%s" % (arm, THR["best_dev_bar"])] = (
        m["best_dev_T2"] is not None and m["best_dev_T2_all_seeds_nonnull"]
        and m["best_dev_T2"] >= THR["best_dev_bar"])
restored_arm = next((a for a in GATED
                     if rule_hits["%s_own_axis_ge_%s"
                                  % (a, THR["own_axis_absolute_bar"])]
                     and rule_hits["%s_best_dev_ge_%s"
                                   % (a, THR["best_dev_bar"])]), None)
all_gated_below_bar = all(
    not rule_hits["%s_own_axis_ge_%s" % (a, THR["own_axis_absolute_bar"])]
    for a in GATED)

if restored_arm is not None:
    verdict = "DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE"
    amend5_status = "RESTORED_QUALITY_GATED_AT_SCOPE"
    basis = ("gated arm %s: seed-mean own_axis_recovery %r >= %r AND "
             "seed-mean best_dev_T2 %r >= %r (P01 %r - %r, the amend-3 "
             "DIVERSE clause verbatim); junk-free by construction "
             "(junk_free_ratio 1.0 asserted per task at bar %r)"
             % (restored_arm, cells[restored_arm]["raw_own_axis_recovery"],
                THR["own_axis_absolute_bar"], cells[restored_arm]["best_dev_T2"],
                THR["best_dev_bar"], THR["best_dev_ref_P01"],
                THR["best_dev_slack"], QG["admission_bar"]))
elif all_gated_below_bar:
    verdict = "NO_MEANINGFUL_BEHAVIORAL_DIVERSITY"
    amend5_status = "REVISED_QUALITY_CONDITIONAL"
    basis = ("every gated arm seed-mean own_axis_recovery < %r "
             "(G01_gate_D2d %r, G01_gate_D3d %r; ceilings at the frozen bar "
             "%r / %r) — under the census-quality bar the D-archive coverage "
             "collapses below the scope bar; the amend-3 diversity terminal "
             "is revised to quality-conditional (raw coverage was junk-borne)"
             % (THR["own_axis_absolute_bar"],
                cells["G01_gate_D2d"]["raw_own_axis_recovery"],
                cells["G01_gate_D3d"]["raw_own_axis_recovery"],
                QG["chosen_bar_ceilings"]["D2d_recovery"],
                QG["chosen_bar_ceilings"]["D3d_recovery"]))
else:
    verdict = "MIXED_INTERMEDIATE_NO_TERMINAL"
    amend5_status = "PARTIAL_RESTORATION"
    basis = ("rule 1 partially met (own-axis hits %s; best-dev hits %s) but "
             "no single gated arm satisfied both clauses"
             % ({a: rule_hits["%s_own_axis_ge_%s"
                              % (a, THR["own_axis_absolute_bar"])] for a in GATED},
                {a: rule_hits["%s_best_dev_ge_%s"
                              % (a, THR["best_dev_bar"])] for a in GATED}))

# ------------------------------------- gate-vs-control attribution (one dim)
ATTR = ("raw_own_axis_recovery", "junk_free_own_axis_recovery",
        "pareto_recovery_T2", "best_dev_T2", "n_elites",
        "n_admissible_feasible")
attribution = {}
for axis, gate_arm, ctrl_arm in (("D2d", "G01_gate_D2d", "G00_nogate_D2d"),
                                 ("D3d", "G01_gate_D3d", "G00_nogate_D3d")):
    ceils = QG["chosen_bar_ceilings"]
    ckey = "%s_recovery" % axis  # chosen_bar_ceilings keys: D2d/D3d/CVTD
    attribution[axis] = {
        "gate_minus_control": {
            k: (round(cells[gate_arm][k] - cells[ctrl_arm][k], 6)
                if cells[gate_arm][k] is not None
                and cells[ctrl_arm][k] is not None else None)
            for k in ATTR},
        "gate": {k: cells[gate_arm][k] for k in ATTR},
        "control": {k: cells[ctrl_arm][k] for k in ATTR},
        "ceiling_recovery_at_bar": ceils[ckey],
        "ceiling_semantics": "census-subset maximum at the bar (per-cell max "
                             "dev over the enumerated default-theta census), "
                             "NOT a bound on the searched space — see "
                             "results/GRAMMAR_ESCAPE_DIAGNOSTIC.json",
        "gate_recovery_over_ceiling": round(
            cells[gate_arm]["raw_own_axis_recovery"] / ceils[ckey], 6)
        if cells[gate_arm]["raw_own_axis_recovery"] is not None else None,
        "control_g00_byte_identity": "asserted in-worker vs the frozen QDA3 "
                                     "twin archive (xchecks_passed)",
    }

out = {
    "aggregate_id": "QUALITY_GATE_AMEND5",
    "amendment": A5["amendment_id"],
    "tier": "T2",
    "n_runs": len(rows),
    "budget_per_task": rows[0]["budget"],
    "admission_bar": QG["admission_bar"],
    "admission_bar_quantile": QG["admission_bar_quantile"],
    "census_median_bar_hz9": QG["census_median_bar_hz9"],
    "bar_selection_rule": QG["bar_selection_rule_FROZEN"],
    "bar_selection_basis": QG["bar_selection_basis"],
    "ceiling_ladder": QG["ceiling_ladder"],
    "cells": cells,
    "rule_hits": rule_hits,
    "verdict_terminal": verdict,
    "amend5_terminal_status": amend5_status,
    "verdict_basis": basis,
    "terminal_rule_source": "FREEZE_V1_AMEND_5.json scoring_rules_amend5."
                            "terminal_rule_FROZEN_first_match",
    "amend3_diverse_rule_verbatim": A5["scoring_rules_amend5"]
                                     ["amend3_diverse_rule_verbatim"],
    "gate_vs_control_attribution": attribution,
    "amend4_context": "revival iteration owed by FREEZE_V1_AMEND_4 mzd9 rule "
                      "3 (UNDERMINED_QUALITY: P05/P09 junk_free_ratio "
                      "0.326667/0.288597 < 0.5 at this same census-median bar)",
}
with open(os.path.join(ROOT, "results", "AGGREGATE_AMEND5.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({"aggregate": "OK", "runs": len(rows), "bar": QG["admission_bar"],
                  "verdict": verdict, "amend5_status": amend5_status,
                  "gate_D2d_recovery": cells["G01_gate_D2d"]["raw_own_axis_recovery"],
                  "gate_D3d_recovery": cells["G01_gate_D3d"]["raw_own_axis_recovery"],
                  "gate_D2d_best_dev": cells["G01_gate_D2d"]["best_dev_T2"],
                  "gate_D3d_best_dev": cells["G01_gate_D3d"]["best_dev_T2"],
                  "rule_hits": rule_hits}))
