"""Aggregate AMEND-4 runs ONLY when every expected task has an ok disposition
and a verifiable receipt chain:
  MZ-D8 islands  2 arms x 3 seeds =  6 tasks (results/QDA4_*)
  MZ-D9 recompute 5 arms x 3 seeds = 15 tasks (results/HZD9R_*)
plus archives/HZD9_TRUTH.json (frozen pre-score).  Refuses (exit 2) otherwise.

Emits results/AGGREGATE_AMEND4.json:
  - per-arm seed-means on the amend-4 axes;
  - MZ-D8: the FROZEN matched pair (I01 ring-migration vs I02 no-migration on
    [D2d_cell_recovery_pooled, pareto_recovery_T2_pooled, best_dev_T2_pooled])
    and the first-match terminal over
    FREEZE_V1_AMEND_4.scoring_rules_amend4.mzd8_terminal_rule_FROZEN_first_match;
  - MZ-D9: census truth lens (collapse, purity, eta^2) + per-arm recompute
    seed-means and the first-match terminal over mzd9_terminal_rule_FROZEN
    (which also sets amend3_terminal_status);
  - the unrestricted single-population reference (QDA3 P05) descriptive only.

Verdicts are computed mechanically from the frozen thresholds — never narrated.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)
with open(os.path.join(ROOT, "FREEZE_V1_AMEND_4.json")) as f:
    A4 = json.load(f)
ISLAND_ARMS = [a["arm_id"] for a in A4["arms_amend4"]["island_arms"]]
HZD9_ARMS = A4["arms_amend4"]["hzd9_recompute_arms"]
SEEDS = A4["arms_amend4"]["seeds"]
THR = A4["thresholds_amend4"]
D_ARCHIVE_ARMS = ("P05_map_elites_D2d", "P06_cvt_map_elites_D", "P09_map_elites_D3d")

from evaluation.receipts import verify_receipt  # noqa: E402

missing, failed, irows, hrows = [], [], [], []
for arm in ISLAND_ARMS:
    for seed in SEEDS:
        tag = "%s_s%d" % (arm, seed)
        status = os.path.join(ROOT, "results", "QDA4_%s.status" % tag)
        if not os.path.exists(status):
            missing.append(tag)
            continue
        if open(status).read().split()[0] != "ok":
            failed.append((tag, open(status).read().strip()))
            continue
        with open(os.path.join(ROOT, "results", "QDA4_%s.json" % tag)) as f:
            irows.append(json.load(f))
        with open(os.path.join(ROOT, "manifests", "receipts",
                               "QDA4_%s.receipt.json" % tag)) as f:
            if not verify_receipt(json.load(f)):
                failed.append((tag, "receipt chain invalid"))
for arm in HZD9_ARMS:
    for seed in SEEDS:
        tag = "%s_s%d" % (arm, seed)
        status = os.path.join(ROOT, "results", "HZD9R_%s.status" % tag)
        if not os.path.exists(status):
            missing.append(tag)
            continue
        if open(status).read().split()[0] != "ok":
            failed.append((tag, open(status).read().strip()))
            continue
        with open(os.path.join(ROOT, "results", "HZD9R_%s.json" % tag)) as f:
            hrows.append(json.load(f))
        with open(os.path.join(ROOT, "manifests", "receipts",
                               "HZD9R_%s.receipt.json" % tag)) as f:
            if not verify_receipt(json.load(f)):
                failed.append((tag, "receipt chain invalid"))
TRUTH_HZ = os.path.join(ROOT, "archives", "HZD9_TRUTH.json")
if not os.path.exists(TRUTH_HZ):
    missing.append("archives/HZD9_TRUTH.json")
if missing or failed:
    print(json.dumps({"aggregate": "REFUSED", "missing": missing,
                      "failed": [f[0] for f in failed]}, indent=1))
    sys.exit(2)
with open(TRUTH_HZ) as f:
    HZ = json.load(f)["summary"]


def _mean(vals):
    xs = [v for v in vals if v is not None]
    return round(sum(xs) / len(xs), 6) if xs else None


# ------------------------------------------------------------- MZ-D8 islands
IMETRICS = ("D2d_cell_recovery_pooled", "pareto_recovery_T2_pooled",
            "best_dev_T2_pooled", "CVTD_niche_recovery_pooled",
            "n_elites_pooled", "island_entropy_mid", "island_entropy_final",
            "diversity_retention_final_over_mid", "frontier_birth_concentration",
            "cross_island_survivor_fraction", "n_migrants_planted",
            "n_migration_events", "frontier_retention_fraction", "wall_s",
            "cpu_hours", "evals")
icells = {}
for arm in ISLAND_ARMS:
    rs = [r for r in irows if r["arm"] == arm]
    m = {k: _mean([r.get(k) for r in rs]) for k in IMETRICS}
    m.update({"seeds": len(rs), "budget": rs[0]["budget"],
              "determinism_xchecks_passed": all(
                  r.get("best_dev_T2_pooled") is not None for r in rs),
              "per_seed": {str(r["seed"]): {
                  k: r[k] for k in ("evals", "n_elites_pooled",
                                    "D2d_cell_recovery_pooled",
                                    "pareto_recovery_T2_pooled",
                                    "best_dev_T2_pooled", "island_entropy_mid",
                                    "island_entropy_final",
                                    "frontier_birth_concentration",
                                    "n_migrants_planted")}
                  for r in rs}})
    icells[arm] = m

MIG, NOMIG = "I01_islands_ring_mig", "I02_islands_nomig"
PAIR = ("D2d_cell_recovery_pooled", "pareto_recovery_T2_pooled",
        "best_dev_T2_pooled")


def winner(a_arm, b_arm):
    """+1 a wins, 0 TIE, -1 b wins (frozen matched-pair rule); None on null."""
    a, b = icells[a_arm], icells[b_arm]
    if any(a[c] is None or b[c] is None for c in PAIR):
        return None
    if all(a[c] >= b[c] for c in PAIR) and any(a[c] > b[c] for c in PAIR):
        return 1
    if all(a[c] <= b[c] for c in PAIR) and any(a[c] < b[c] for c in PAIR):
        return -1
    return 0


w = winner(MIG, NOMIG)
pair_label = {1: MIG, -1: NOMIG, 0: "TIE", None: "NO_CONTEST_NULL"}[w]
pair_out = {
    "winner": pair_label, "criteria": list(PAIR),
    MIG: {c: icells[MIG][c] for c in PAIR},
    NOMIG: {c: icells[NOMIG][c] for c in PAIR},
    "mig_minus_nomig": {c: (round(icells[MIG][c] - icells[NOMIG][c], 6)
                            if icells[MIG][c] is not None
                            and icells[NOMIG][c] is not None else None)
                        for c in PAIR},
}

t8 = THR["mzd8"]
e_mig, e_nomig = (icells[MIG]["island_entropy_final"],
                  icells[NOMIG]["island_entropy_final"])
fbc = icells[MIG]["frontier_birth_concentration"]
entropy_ratio = (round(e_mig / e_nomig, 6)
                 if e_mig is not None and e_nomig else None)
rule_hits = {
    "1_frontier_birth_concentration_ge_%s" % t8["frontier_birth_concentration_ge"]:
        fbc is not None and
        fbc >= t8["frontier_birth_concentration_ge"],
    "2_entropy_final_mig_over_nomig_lt_%s" %
    t8["entropy_ratio_final_mig_over_nomig_lt"]:
        entropy_ratio is not None and
        entropy_ratio < t8["entropy_ratio_final_mig_over_nomig_lt"],
}
if rule_hits["1_frontier_birth_concentration_ge_%s"
             % t8["frontier_birth_concentration_ge"]]:
    verdict_mzd8 = "ONE_ARCHITECTURE_FAMILY_DOMINATES"
    mzd8_basis = ("seed-mean frontier_birth_concentration(I01)=%r >= %r "
                  "[one mature parent architecture reproduces the frontier]"
                  % (fbc, t8["frontier_birth_concentration_ge"]))
elif rule_hits["2_entropy_final_mig_over_nomig_lt_%s"
               % t8["entropy_ratio_final_mig_over_nomig_lt"]]:
    verdict_mzd8 = "ONE_ARCHITECTURE_FAMILY_DOMINATES"
    mzd8_basis = ("seed-mean island_entropy_final ratio mig/nomig=%r < %r "
                  "[island diversity disappears after migration]"
                  % (entropy_ratio,
                     t8["entropy_ratio_final_mig_over_nomig_lt"]))
elif (w == 1 and entropy_ratio is not None
      and entropy_ratio >= t8["entropy_ratio_final_mig_over_nomig_lt"]
      and icells[MIG]["D2d_cell_recovery_pooled"] is not None
      and icells[MIG]["D2d_cell_recovery_pooled"] >= t8["own_axis_absolute_bar"]):
    verdict_mzd8 = "MORPHOLOGY_FAMILY_TRANSFER_SUPPORTED_AT_SCOPE"
    mzd8_basis = ("I01 wins the frozen pair, entropy retained (ratio %r), "
                  "D2d_cell_recovery_pooled %r >= %r"
                  % (entropy_ratio, icells[MIG]["D2d_cell_recovery_pooled"],
                     t8["own_axis_absolute_bar"]))
else:
    verdict_mzd8 = "MIXED_INTERMEDIATE_NO_TERMINAL"
    mzd8_basis = ("no frozen rule fired (frontier_birth_concentration=%r, "
                  "entropy ratio=%r, pair winner=%s)"
                  % (fbc, entropy_ratio, pair_label))

# ------------------------------------------------- MZ-D9 hostile subset
t9 = THR["mzd9"]
hcells = {}
for arm in HZD9_ARMS:
    rs = [r for r in hrows if r["arm"] == arm]
    m = {k: _mean([r.get(k) for r in rs]) for k in
         ("archive_genotype_to_phenotype_collapse_ratio",
          "raw_own_axis_recovery", "junk_free_own_axis_recovery",
          "junk_free_ratio", "n_elites", "distinct_genotypes",
          "distinct_phenotypes", "best_dev_T2", "n_elites_above_bar")}
    m.update({"seeds": len(rs), "own_axis": rs[0]["own_axis"],
              "quality_bar_T2": rs[0]["quality_bar_T2"],
              "per_seed": {str(r["seed"]): {
                  k: r[k] for k in ("raw_own_axis_recovery",
                                    "junk_free_own_axis_recovery",
                                    "junk_free_ratio",
                                    "archive_genotype_to_phenotype_collapse_ratio")}
                  for r in rs}})
    hcells[arm] = m

collapse = HZ["collapse"]
phen_frac = (collapse["distinct_phenotype_digests"]
             / collapse["feasible_genotypes"]) \
    if collapse["feasible_genotypes"] else None
d_grid_collapse = [hcells[a]["archive_genotype_to_phenotype_collapse_ratio"]
                   for a in D_ARCHIVE_ARMS[:2]]  # P05, P09 (D-grid arms)
d_grid_collapse = [c for c in d_grid_collapse if c is not None]
archive_collapse_max = max(d_grid_collapse) if d_grid_collapse else None
purity_frac = HZ["descriptor_purity_D2d"]["frac_cells_purity_F_arch_ge_0.9"]
eta2_vals = [v for v in HZ["eta_squared_F_arch"].values() if v is not None]
eta2_max = max(eta2_vals) if eta2_vals else None
junk_min_arm = min(
    (a for a in D_ARCHIVE_ARMS if hcells[a]["junk_free_ratio"] is not None),
    key=lambda a: hcells[a]["junk_free_ratio"], default=None)
junk_min = hcells[junk_min_arm]["junk_free_ratio"] if junk_min_arm else None

mzd9_checks = {
    "census_distinct_phenotype_fraction": phen_frac,
    "archive_collapse_max_D_grid_arms": archive_collapse_max,
    "purity_frac_cells_F_arch_ge_0.9": purity_frac,
    "eta2_F_arch_max": eta2_max,
    "junk_free_ratio_min_D_arms": junk_min,
    "junk_free_ratio_min_arm": junk_min_arm,
}
if (phen_frac is not None and phen_frac < t9["census_distinct_phenotype_fraction_lt"]) \
        or (archive_collapse_max is not None
            and archive_collapse_max >= t9["archive_collapse_ratio_ge"]):
    verdict_mzd9 = "NO_MEANINGFUL_BEHAVIORAL_DIVERSITY"
    amend3_status = "UNDERMINED_DIVERSITY"
elif (purity_frac is not None and purity_frac >= t9["purity_frac_cells_ge"]) \
        or (eta2_max is not None and eta2_max >= t9["eta2_max_ge"]):
    verdict_mzd9 = "DESCRIPTOR_CHOICE_DOMINATES"
    amend3_status = "RETAINED_DESCRIPTOR_CONFOUNDED"
elif junk_min is not None and junk_min < t9["junk_free_ratio_lt"]:
    verdict_mzd9 = "MIXED_INTERMEDIATE_NO_TERMINAL"
    amend3_status = "UNDERMINED_QUALITY"
else:
    verdict_mzd9 = "DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE"
    amend3_status = "RETAINED"

# ------------------------------- unrestricted reference (descriptive only)
ref = None
agg3_path = os.path.join(ROOT, "results", "AGGREGATE_AMEND3.json")
if os.path.exists(agg3_path):
    with open(agg3_path) as f:
        a3 = json.load(f)
    p05 = a3["cells"].get("P05_map_elites_D2d", {})
    ref = {"arm": "P05_map_elites_D2d", "budget": 40000,
           "seeds": p05.get("seeds"),
           "D2d_cell_recovery": p05.get("D2d_cell_recovery"),
           "pareto_recovery_T2": p05.get("pareto_recovery_T2"),
           "best_dev_T2": p05.get("best_dev_T2"),
           "role": "DESCRIPTIVE ONLY (no frozen rule)"}

out = {
    "aggregate_id": "MZD8_MZD9_AMEND4_ISLANDS_HOSTILE",
    "amendment": A4["amendment_id"],
    "tier": "T2",
    "n_runs_islands": len(irows),
    "n_runs_hzd9": len(hrows),
    "budget_per_task": irows[0]["budget"],
    "per_island_budget": A4["arms_amend4"]["per_island_budget"],
    "quality_bar_T2": A4["quality_bar_T2"],
    "mzd8": {
        "cells": icells, "pair": pair_out,
        "entropy_final_ratio_mig_over_nomig": entropy_ratio,
        "rule_hits": rule_hits,
        "verdict_terminal": verdict_mzd8,
        "verdict_basis": mzd8_basis,
        "terminal_rule_source": "FREEZE_V1_AMEND_4.json "
                                "scoring_rules_amend4."
                                "mzd8_terminal_rule_FROZEN_first_match",
    },
    "mzd9": {
        "census_truth": {
            "run_id": HZ["run_id"], "feasible": HZ["feasible"],
            "collapse": collapse, "quality_bar_T2": HZ["quality_bar_T2"],
            "purity_D2d_frac_ge_0.9": purity_frac,
            "eta_squared_F_arch": HZ["eta_squared_F_arch"],
            "xcheck_vs_P00C": HZ["xcheck_vs_P00C"]},
        "cells": hcells, "checks": mzd9_checks,
        "verdict_terminal": verdict_mzd9,
        "amend3_terminal_status": amend3_status,
        "terminal_rule_source": "FREEZE_V1_AMEND_4.json "
                                "scoring_rules_amend4."
                                "mzd9_terminal_rule_FROZEN_first_match",
    },
    "unrestricted_reference_descriptive": ref,
}
with open(os.path.join(ROOT, "results", "AGGREGATE_AMEND4.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({"aggregate": "OK", "runs": len(irows) + len(hrows),
                  "verdict_mzd8": verdict_mzd8,
                  "verdict_mzd9": verdict_mzd9,
                  "amend3_terminal_status": amend3_status,
                  "pair_winner": pair_label,
                  "entropy_ratio": entropy_ratio,
                  "checks": mzd9_checks}))
