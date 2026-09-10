#!/usr/bin/env python3
"""GS-R2 aggregation + lever verdict (#221 sec 18 GS-R2, evidence class
EXPLORATORY_ADAPTIVE — decision support for the next allocation, never a
programme terminal).

Steps:
  1. verify freeze sha + manifest binding; report code drift;
  2. per arm: completed/attempted seeds, distinct T2-viable phenotypes,
     CPU-hours, morphologies-per-CPU-hour, mean distinct/seed,
     revival_levers echo, holdout_mae_t1 distribution (NaN-fix read);
  3. lever attribution table vs the frozen parents and the on-code
     GSA5P_fixed replication (one stage: the ranking/allocation stage);
  4. held-out T3 on every distinct survivor: R1 battery replication +
     the m>=104 battery (PAC-Bayes crossover read);
  5. first-match terminal rule (frozen list) + per-survivor verdicts;
  6. failure-memory summary;
  7. write results/GS_R2_AGGREGATE.json + .status.
Usage: python3 hpc/aggregate_gs_r2.py <CAPSULE_ROOT>
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, ROOT)

import hashlib  # noqa: E402

ARMS = ["GSA6_NG", "GSA6_DP", "GSA6_SC", "GSA6_ALL", "GSA5P_fixed"]
FN = "GRAND_SEARCH_R2_FREEZE.json"


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def code_digest(root):
    h = hashlib.sha256()
    for d in ("morphology", "evaluation", "search", "hpc"):
        for fn in sorted(os.listdir(os.path.join(root, d))):
            if fn.endswith(".py"):
                h.update(open(os.path.join(root, d, fn), "rb").read())
    return h.hexdigest()


def _load_status(root, rid):
    p = os.path.join(root, "results", rid + ".status")
    if not os.path.exists(p):
        return "missing", None
    txt = open(p).read().strip()
    return ("ok" if txt == "ok" else "fail"), (txt or None)


def _isfinite(x):
    try:
        return x is not None and x == x and abs(x) != float("inf")
    except TypeError:
        return False


def main():
    freeze = json.load(open(os.path.join(ROOT, FN)))
    fsha = sha256_file(os.path.join(ROOT, FN))
    env_sha = os.environ.get("GS_FREEZE_SHA", "")
    assert env_sha in ("", fsha), "freeze sha mismatch"
    manifest = json.load(open(os.path.join(
        ROOT, "manifests", "GS_R2_TASKS.json")))
    assert manifest["freeze_sha256"] == fsha, "manifest not bound to freeze"
    code_drift = code_digest(ROOT) != freeze["code_digest"]

    res = os.path.join(ROOT, "results")
    arm_report = {}
    survivors_by_pheno = {}
    mae_by_arm = {}
    for arm in ARMS:
        seeds = freeze["arms"][arm]["seeds"]
        completed, cpu_h, phenos = [], 0.0, set()
        dist_per_seed, maes = [], []
        for s in seeds:
            rid = "GS_R2_%s_s%d" % (arm, s)
            st, _ = _load_status(ROOT, rid)
            if st != "ok":
                continue
            completed.append(rid)
            d = json.load(open(os.path.join(res, rid + ".json")))
            cpu_h += float(d.get("cpu_hours") or 0.0)
            arm_phenos = {sv["phenotype_digest"]
                          for sv in d.get("survivors", [])}
            phenos |= arm_phenos
            dist_per_seed.append(len(arm_phenos))
            for sv in d.get("survivors", []):
                prev = survivors_by_pheno.get(sv["phenotype_digest"])
                if prev is None:
                    survivors_by_pheno[sv["phenotype_digest"]] = {
                        "phenotype_digest": sv["phenotype_digest"],
                        "genome": sv["genome"], "arms": [arm]}
                elif arm not in prev["arms"]:
                    prev["arms"].append(arm)
            ss = d.get("surrogate_stats") or {}
            if ss.get("holdout_mae_t1") is not None:
                maes.append(ss["holdout_mae_t1"])
        mph = (len(phenos) / cpu_h) if cpu_h > 0 else None
        arm_report[arm] = {
            "attempted": len(seeds), "completed": len(completed),
            "revival_levers": {k: bool(freeze["arms"][arm].get(k))
                               for k in ("novelty_gate", "dedup_promotion",
                                         "surrogate_cumulative")},
            "cpu_hours": round(cpu_h, 6),
            "distinct_t2_viable_phenotypes": len(phenos),
            "mean_distinct_per_seed": (
                round(statistics.mean(dist_per_seed), 2)
                if dist_per_seed else None),
            "morphologies_per_cpu_hour": (
                round(mph, 2) if mph else None),
            "holdout_mae_t1": {
                "n_finite": sum(1 for m in maes if _isfinite(m)),
                "n_nonfinite": sum(1 for m in maes if not _isfinite(m)),
                "mean": round(statistics.mean(maes), 6)
                if maes and all(_isfinite(m) for m in maes) else None},
        }
        mae_by_arm[arm] = maes

    # ---- lever attribution vs parents + on-code replication (one stage)
    par = freeze["parents"]
    g2 = par["GSA2_hetero"]
    g5 = par["GSA5_surrogate"]
    rep = arm_report["GSA5P_fixed"]
    rep_mph = (rep["morphologies_per_cpu_hour"]
               if rep["completed"] else None)

    def _d(arm):
        a = arm_report[arm]
        return None if not a["completed"] else {
            "mph": a["morphologies_per_cpu_hour"],
            "mean_distinct_per_seed": a["mean_distinct_per_seed"],
            "cpu_hours": a["cpu_hours"]}

    attribution = {
        "parents_frozen": {"GSA2_hetero": g2, "GSA5_surrogate": g5},
        "GSA5P_fixed_replication": _d("GSA5P_fixed"),
        "levers": {a: _d(a) for a in
                   ("GSA6_NG", "GSA6_DP", "GSA6_SC", "GSA6_ALL")},
        "reads": {
            "yield_recovery_vs_GSA5": {
                a: (round(arm_report[a]["mean_distinct_per_seed"]
                          / g5["distinct_t2_viable_per_seed"], 4)
                    if arm_report[a]["completed"] else None)
                for a in ARMS},
            "yield_vs_GSA2_parent": {
                a: (round(arm_report[a]["mean_distinct_per_seed"]
                          / g2["distinct_t2_viable_per_seed"], 4)
                    if arm_report[a]["completed"] else None)
                for a in ARMS},
            "note": "single-lever arms isolate one lever each; GSA6_ALL "
                    "is the package; GSA5P_fixed re-measures the parent "
                    "on this code digest (NaN fix always-on)",
        },
    }

    # ---- held-out T3 on survivors: R1 replication + m>=104 battery
    from evaluation.t3_ecology import evaluate_t3
    from evaluation.t3_ecology_m104 import evaluate_t3_m104
    from morphology.schema import OCMMorphologyGenomeV1
    t3_verdicts = []
    for ph, sv in sorted(survivors_by_pheno.items()):
        g = OCMMorphologyGenomeV1.from_json_obj(sv["genome"])
        r3 = evaluate_t3(g, freeze["t3_key"])
        rm = evaluate_t3_m104(g, freeze["t3_key"])
        t3_verdicts.append({
            "phenotype_digest": ph,
            "verdict": ("SURVIVOR_T3_GENERALIZATION_HOLD" if r3["feasible"]
                        else "SURVIVOR_T3_GENERALIZATION_FAIL"),
            "solved_fraction": r3["evaluation"]["solved_fraction"],
            "m104": {"m_total": rm["m_total"],
                     "m_ge_crossover": rm["m_ge_crossover"],
                     "solved_fraction": rm["solved_fraction"],
                     "feasible_calls": rm["feasible_calls"],
                     "n_calls": rm["n_calls"]},
            "arms": sv["arms"]})
    m104_all = [t["m104"] for t in t3_verdicts]
    t3_m104_read = {
        "crossover_m": freeze["heldout_t3"]["m104_extension"]["crossover_m"],
        "n_survivors": len(t3_verdicts),
        "all_m_ge_crossover": bool(m104_all) and all(
            m["m_ge_crossover"] for m in m104_all),
        "mean_m104_solved_fraction": (
            round(statistics.mean([m["solved_fraction"]
                                   for m in m104_all]), 6)
            if m104_all else None),
        "read": "per-survivor T3 empirical risk at m>=104: the PAC-Bayes "
                "transfer slack eps(m) <= admission bar 0.224507 only "
                "from m*=104 (HST_TRANSFER_BOUND_V1); at m=108+ the "
                "per-survivor T3 statement is non-vacuous, unlike the "
                "12-task T2 ecology scale",
    }

    # ---- first-match terminal rule (frozen; EXPLORATORY_ADAPTIVE)
    all_arm = arm_report["GSA6_ALL"]
    g5_bar = max(g5["morphologies_per_cpu_hour"],
                 rep_mph if rep_mph is not None else 0.0)
    g2_mph = g2["morphologies_per_cpu_hour"]
    if sum(arm_report[a]["completed"] for a in ARMS) == 0:
        terminal = "CANNOT_CHECK_NO_SCORED_DISPOSITIONS"
    elif (all_arm["completed"] and all_arm["morphologies_per_cpu_hour"]
          and all_arm["morphologies_per_cpu_hour"] > max(g2_mph, g5_bar)
          and all_arm["mean_distinct_per_seed"]
          > g2["distinct_t2_viable_per_seed"]):
        terminal = "LEVER_PACKAGE_BEATS_PARENTS"
    elif (all_arm["completed"] and all_arm["morphologies_per_cpu_hour"]
          and all_arm["morphologies_per_cpu_hour"] > g5_bar):
        terminal = "LEVER_PACKAGE_BEATS_SURROGATE_PARENT_ONLY"
    elif (all_arm["completed"]
          and (all_arm["morphologies_per_cpu_hour"] or 0.0) <= g5_bar):
        terminal = "LEVER_PACKAGE_NO_GAIN"
    else:
        terminal = "MIXED_INTERMEDIATE_NO_TERMINAL"
    vocab = {r["id"]: r["vocab"]
             for r in freeze["terminal_rules_first_match"]}
    nan_fix_read = {
        "defect": "GSA5_HOLDOUT_MAE_NAN",
        "finite_runs": sum(arm_report[a]["holdout_mae_t1"]["n_finite"]
                           for a in ARMS),
        "nonfinite_runs": sum(
            arm_report[a]["holdout_mae_t1"]["n_nonfinite"] for a in ARMS),
        "per_arm_mean": {a: arm_report[a]["holdout_mae_t1"]["mean"]
                         for a in ARMS}}

    from search.failure_memory import read_failures_summary
    out = {
        "aggregate_id": "GS_R2_AGGREGATE",
        "schema": "GS_R2_AGGREGATE_V1",
        "evidence_class": "EXPLORATORY_ADAPTIVE",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "freeze_sha256": fsha,
        "manifest_sha256": sha256_file(os.path.join(
            ROOT, "manifests", "GS_R2_TASKS.json")),
        "code_digest_drift_vs_freeze": code_drift,
        "arms": arm_report,
        "lever_attribution": attribution,
        "n_distinct_survivors": len(survivors_by_pheno),
        "heldout_t3_key_id": freeze["heldout_t3"]["t3_key_id"],
        "t3_verdicts": t3_verdicts,
        "t3_summary": {
            v: sum(1 for t in t3_verdicts if t["verdict"] == v)
            for v in ("SURVIVOR_T3_GENERALIZATION_HOLD",
                      "SURVIVOR_T3_GENERALIZATION_FAIL")},
        "t3_m104_read": t3_m104_read,
        "nan_fix_read": nan_fix_read,
        "terminal_rule_id": terminal,
        "terminal_vocab": vocab.get(terminal),
        "frozen_rule_ids_in_order": [r["id"] for r in
                                     freeze["terminal_rules_first_match"]],
        "failure_summary": read_failures_summary(),
    }
    with open(os.path.join(res, "GS_R2_AGGREGATE.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    with open(os.path.join(res, "GS_R2_AGGREGATE.status"), "w") as fh:
        fh.write("ok\n")
    print(json.dumps({
        "terminal": terminal, "vocab": vocab.get(terminal),
        "arms": {a: {"mph": arm_report[a]["morphologies_per_cpu_hour"],
                     "distinct_per_seed":
                         arm_report[a]["mean_distinct_per_seed"],
                     "completed": arm_report[a]["completed"]}
                 for a in ARMS},
        "nan_fix": [nan_fix_read["finite_runs"],
                    nan_fix_read["nonfinite_runs"]],
        "t3": out["t3_summary"], "t3_m104": t3_m104_read, "attrib":
        attribution["reads"]["yield_recovery_vs_GSA5"]}, indent=1,
        sort_keys=True))


if __name__ == "__main__":
    main()
