#!/usr/bin/env python3
"""RV-A step A1: one-stage attribution of the GS-R2 T3 generalization negative.

Reads the GS-R2 per-seed survivor files (already on LUNARC) plus the committed
GS_R2_AGGREGATE.json verdicts, and cross-tabulates every distinct survivor's
T3 verdict against genome-derived capability bits taken from grammar_signature.

Pure offline data reduction: no network, no re-search, no re-evaluation.
Usage: python3 rva_attrib.py <CAPSULE_ROOT> <OUT_JSON>
"""
from __future__ import annotations

import collections
import glob
import json
import os
import sys

ROOT = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
RES = os.path.join(ROOT, "results")

# grammar_signature = "F_arch|extras_csv|T_family|Pi_arch|L|R|K"
SIG_FIELDS = ("F_arch", "extras", "T_family", "Pi_arch", "L", "R", "K")


def parse_sig(sig):
    parts = sig.split("|")
    if len(parts) != 7:
        raise ValueError("unexpected grammar_signature arity %d: %r" % (len(parts), sig))
    d = dict(zip(SIG_FIELDS, parts))
    d["extras_set"] = frozenset(x for x in d["extras"].split(",") if x)
    return d


def caps(d):
    """Capability predicates, verbatim from evaluation/lifetime2._capabilities
    and evaluation/t3_ecology.run_t3 (same source definitions)."""
    ex = d["extras_set"]
    return {
        "can_check": ("constraint_solver" in ex) or (d["L"] == "scoped_nogood"),
        "can_probe": ("diagnostic_probe" in ex) or (d["Pi_arch"] == "adaptive_probe_policy"),
        "fibred": d["F_arch"] == "hierarchical_fibred",
        "can_schema": ("abstraction_schema" in ex) or (
            d["L"] in ("anti_unification_schema", "consolidation_schema_residual")),
        "R_none": d["R"] == "none",
    }


def main():
    # ---- 1. distinct survivors from the per-seed files (phenotype-deduped)
    files = sorted(glob.glob(os.path.join(RES, "GS_R2_*_s?.json")))
    files = [f for f in files if "AGGREGATE" not in f and "RECEIPTS" not in f]
    by_pheno = {}
    per_file = []
    for fp in files:
        d = json.load(open(fp))
        arm = os.path.basename(fp)[len("GS_R2_"):].rsplit("_s", 1)[0]
        n = 0
        for sv in d.get("survivors", []):
            n += 1
            ph = sv["phenotype_digest"]
            if ph not in by_pheno:
                by_pheno[ph] = {"sig": sv["grammar_signature"],
                                "F_arch": sv["F_arch"],
                                "n_units": sv.get("n_units"),
                                "arms": set()}
            by_pheno[ph]["arms"].add(arm)
        per_file.append({"file": os.path.basename(fp), "arm": arm, "n_survivors": n})

    # ---- 2. verdicts from the committed aggregate
    agg = json.load(open(os.path.join(RES, "GS_R2_AGGREGATE.json")))
    verdict = {t["phenotype_digest"]: t for t in agg["t3_verdicts"]}

    # ---- 3. join + cross-tab
    joined, missing_v, missing_s = 0, 0, 0
    ct = collections.Counter()          # (can_check, fibred, FAIL/HOLD)
    farch_ct = collections.Counter()    # (F_arch, FAIL/HOLD)
    sf_by_cap = collections.Counter()   # (can_check, solved_fraction)
    m104fc = collections.Counter()      # (can_check, feasible_calls)
    contradictions = []
    for ph, rec in by_pheno.items():
        v = verdict.get(ph)
        if v is None:
            missing_v += 1
            continue
        joined += 1
        c = caps(parse_sig(rec["sig"]))
        f = "FAIL" if v["verdict"].endswith("FAIL") else "HOLD"
        ct[(c["can_check"], c["fibred"], f)] += 1
        farch_ct[(rec["F_arch"], f)] += 1
        sf_by_cap[(c["can_check"], round(v["solved_fraction"], 6))] += 1
        m104fc[(c["can_check"], v["m104"]["feasible_calls"])] += 1
        # falsifier: the claim is FAIL <=> not can_check
        if c["can_check"] == (f == "FAIL"):
            if len(contradictions) < 40:
                contradictions.append({"phenotype_digest": ph, "sig": rec["sig"],
                                       "verdict": f, "can_check": c["can_check"],
                                       "solved_fraction": v["solved_fraction"],
                                       "m104": v["m104"]})
    for ph in verdict:
        if ph not in by_pheno:
            missing_s += 1

    # ---- 4. predictor quality of the single bit can_check
    n_fail = sum(n for (cc, fb, f), n in ct.items() if f == "FAIL")
    n_hold = sum(n for (cc, fb, f), n in ct.items() if f == "HOLD")
    tp = sum(n for (cc, fb, f), n in ct.items() if (not cc) and f == "FAIL")
    fp = sum(n for (cc, fb, f), n in ct.items() if (not cc) and f == "HOLD")
    fn = sum(n for (cc, fb, f), n in ct.items() if cc and f == "FAIL")
    tn = sum(n for (cc, fb, f), n in ct.items() if cc and f == "HOLD")

    out = {
        "study_id": "RV_A_ATTRIBUTION_A1",
        "capsule_root": ROOT,
        "n_files": len(files),
        "per_file": per_file,
        "n_distinct_survivors_from_seed_files": len(by_pheno),
        "n_distinct_survivors_in_aggregate": len(verdict),
        "joined": joined,
        "in_seed_files_but_not_in_aggregate": missing_v,
        "in_aggregate_but_not_in_seed_files": missing_s,
        "crosstab_can_check_fibred_verdict": {
            "%s|%s|%s" % (cc, fb, f): n for (cc, fb, f), n in sorted(ct.items())},
        "crosstab_F_arch_verdict": {
            "%s|%s" % (fa, f): n for (fa, f), n in sorted(farch_ct.items())},
        "solved_fraction_by_can_check": {
            "%s|%s" % (cc, s): n for (cc, s), n in sorted(sf_by_cap.items())},
        "m104_feasible_calls_by_can_check": {
            "%s|%s" % (cc, k): n for (cc, k), n in sorted(m104fc.items())},
        "single_bit_predictor_not_can_check_predicts_FAIL": {
            "true_pos": tp, "false_pos": fp, "false_neg": fn, "true_neg": tn,
            "n_fail": n_fail, "n_hold": n_hold,
            "accuracy": round((tp + tn) / max(1, tp + tn + fp + fn), 8),
            "exact": (fp == 0 and fn == 0)},
        "contradiction_samples": contradictions,
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("per_file", "contradiction_samples")},
                     indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
