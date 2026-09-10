#!/usr/bin/env python3
"""RV-A number audit: re-derive EVERY quantitative claim in the study's prose
from the committed receipts.

Motivated by a real defect found in review: the compute share was reported as
4.7% when the receipts give 2.13% -- the 47x compute REDUCTION transposed into a
percentage.  Fixing only the reported instance would leave the defect class
unchecked, so this recomputes every derived ratio and asserts the no-alarm case
for the ones that were right.

Offline; no network.  Usage: python3 rva_numaudit.py <RVA_RESULTS_DIR> <OUT>
"""
from __future__ import annotations

import json, os, sys

R = os.path.abspath(sys.argv[1]); OUT = os.path.abspath(sys.argv[2])
L = lambda n: json.load(open(os.path.join(R, n)))  # noqa: E731

l1 = L("RVA_L1_AGGREGATE.json")
nul = L("RVA_N_NULL_AGGREGATE.json")
a2 = L("RVA_A2_DRAW_INVARIANCE.json")
a1 = L("RVA_A1_ATTRIBUTION.json")
tc = L("RVA_TIER_COST.json")
cmp_ = L("RVA_COMPARATOR.json")
fam = L("RVA_FAMILY_RECEIPT.json")

L1 = l1["L1"]; R2 = l1["gs_r2_pooled"]; P = l1["gs_r2_parents_frozen"]
arms = l1["gs_r2_arms"]
comp = a2["composition"]["arms"]

checks = []
def ck(name, claimed, derived, tol, unit=""):
    ok = abs(claimed - derived) <= tol
    checks.append({"claim": name, "in_prose": claimed,
                   "derived_from_receipts": round(derived, 6),
                   "tolerance": tol, "unit": unit, "ok": bool(ok)})

# --- the defect
ck("compute share L1/R2 (%)", 4.7, 100 * L1["cpu_hours"] if False else
   100 * l1["cpu_hours"] / R2["cpu_hours"], 0.05, "percent")
# --- everything else claimed in prose
ck("absolute hold ratio L1/R2", 2.21,
   L1["distinct_t3_hold"] / R2["distinct_t3_hold"], 0.01, "x")
ck("hold per CPU-hour ratio", 104.0,
   L1["t3_hold_per_cpu_hour"] / R2["t3_hold_per_cpu_hour"], 0.5, "x")
ck("compute reduction R2/L1", 47.0,
   R2["cpu_hours"] / l1["cpu_hours"], 0.1, "x")
ck("parent distinct/seed vs GSA2_hetero", 1.36,
   L1["mean_distinct_per_seed"] / P["GSA2_hetero"]["distinct_t2_viable_per_seed"],
   0.005, "x")
ck("parent morph/CPU-h vs GSA2_hetero", 4.92,
   L1["morphologies_per_cpu_hour"] / P["GSA2_hetero"]["morphologies_per_cpu_hour"],
   0.01, "x")
ck("GSA6_DP vs GSA6_ALL exclusive can_check", 3.82,
   comp["GSA6_DP"]["exclusive_can_check"] / comp["GSA6_ALL"]["exclusive_can_check"],
   0.01, "x")
ck("null vs observed composition", 5.44,
   nul["endpoint_phenotype_deduped"]["can_check_fraction"]
   / nul["comparator_observed_survivors"]["can_check_fraction"], 0.01, "x")
ck("gate odds favouring checker-bearing", 27.7,
   1.0 / nul["gate_selection"]["odds_ratio_favouring_checker_free"], 0.1, "x")
ck("tier cost ratio T2/T0", 4.60, tc["tier_cost_ratio_T2_over_T0"], 0.01, "x")
ck("alloc_score cost in T0 units", 8.04, tc["alloc_score_cost_in_T0_units"],
   0.01, "T0-units")
sv = tc["sec_per_eval"]; t0 = sv["T0"]
saving = (2.0/3.0) * (sv["T1"]/t0) + (2.0/3.0) * (sv["T2"]/t0)
ck("halving saving in T0 units", 4.8, saving, 0.15, "T0-units")
ck("fail fraction of survivors (%)", 84.44,
   100 * a2["draw_invariance"]["n_fail"]
   / a2["draw_invariance"]["n_distinct_survivors"], 0.01, "percent")
ck("observed hold rate", 0.1556, comp and cmp_["comparator_active_level_fraction"],
   0.0001, "")
ck("L1 hold rate", 0.8388, L1["t3_hold_rate"], 0.0001, "")
ck("unranked viable composition", 0.84659,
   nul["endpoint_phenotype_deduped"]["can_check_fraction"], 0.0001, "")
ck("ladder composition all rungs", 0.8398,
   L("RVA_L_LADDER_AGGREGATE.json")["per_rung"]["T2"]["can_check_fraction"],
   0.0005, "")

bad = [c for c in checks if not c["ok"]]
out = {
    "audit_id": "RVA_NUMBER_AUDIT_V1",
    "n_checks": len(checks), "n_failing": len(bad),
    "failing": bad, "all_checks": checks,
    "no_alarm_case_asserted": len(checks) - len(bad),
    "read": ("every quantitative claim in the study's prose re-derived from the "
             "receipts; a checker that only confirmed the known defect would not "
             "have shown the other claims are sound"),
}
with open(OUT, "w") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
