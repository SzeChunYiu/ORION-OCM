#!/usr/bin/env python3
"""GS-R1 aggregation + terminal verdict (#221 sec 18 GS-R1E inputs).

Runs AFTER every array task has a disposition (submit_gs.py chains it with
afterok/afterany dependency; tasks without results are counted as
attempted-not-completed — honest partials, no imputation).

Steps:
  1. verify freeze sha + manifest binding + code digest;
  2. per arm: completed/attempted tasks (frozen seeds PLUS GS-R1h batch
     tasks folded into their base_arm cell, all costs charged), distinct
     T2-viable phenotypes (union over seeds), CPU-hours charged,
     morphologies-per-CPU-hour;
  3. sweep arm: totals over completed shards (viable counts are exact —
     each grammar tuple appears exactly once in the flat enumeration, so
     per-shard viable counts sum without dedup);
  4. held-out T3 evaluation of every distinct survivor (freeze key);
  5. first-match terminal rule (frozen list) + per-survivor T3 verdicts;
  6. failure-memory summary (all shards merged);
  7. write results/GS_R1_AGGREGATE.json + receipt + status.
"""
from __future__ import annotations

import glob
import json
import os
import statistics
import sys
import time

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, ROOT)

import hashlib  # noqa: E402


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def code_digest(root: str) -> str:
    h = hashlib.sha256()
    for d in ("morphology", "evaluation", "search", "hpc"):
        for fn in sorted(os.listdir(os.path.join(root, d))):
            if fn.endswith(".py"):
                h.update(open(os.path.join(root, d, fn), "rb").read())
    return h.hexdigest()


SEARCH_ARMS = ["GSA1_units", "GSA2_hetero", "GSA3_farch", "GSA4_obasis",
               "GSA5_surrogate", "GSR_random_control"]
NOVELTY_ARMS = ["GSA1_units", "GSA2_hetero", "GSA3_farch", "GSA4_obasis"]


def _batch_tasks(root: str):
    """GS-R1h adaptive-batch tasks: (task_id, spec) pairs from the batch
    records AND the per-task spec dirs, deduped (per-task spec wins — it
    is the submission source of truth).  Search tasks declare base_arm;
    sweep tasks are extra/retry shards."""
    found = {}
    for record in sorted(glob.glob(os.path.join(
            root, "manifests", "GS_R1_BATCH_*.json"))):
        try:
            for t in json.load(open(record)).get("tasks", []):
                if t.get("task_id"):
                    found[t["task_id"]] = t
        except Exception:
            continue
    for spec_path in sorted(glob.glob(os.path.join(
            root, "manifests", "GS_R1_BATCH_*", "*.json"))):
        try:
            t = json.load(open(spec_path))
        except Exception:
            continue
        if t.get("task_id"):
            found[t["task_id"]] = t
    return sorted(found.items())


def _load_status(root: str, run_id: str):
    p = os.path.join(root, "results", run_id + ".status")
    if not os.path.exists(p):
        return "missing", None
    txt = open(p).read().strip()
    return ("ok" if txt == "ok" else "fail"), (txt or None)


def main() -> None:
    freeze_path = os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json")
    freeze = json.load(open(freeze_path))
    fsha = sha256_file(freeze_path)
    env_sha = os.environ.get("GS_FREEZE_SHA", "")
    assert env_sha in ("", fsha), "freeze sha mismatch"
    manifest = json.load(open(os.path.join(ROOT, "manifests",
                                           "GS_R1_TASKS.json")))
    assert manifest["freeze_sha256"] == fsha, "manifest not bound to freeze"
    code_drift = code_digest(ROOT) != freeze["code_digest"]  # reported, not fatal

    res = os.path.join(ROOT, "results")
    arm_report = {}
    survivors_by_pheno = {}
    total_search_evals = 0
    # GS-R1h batch tasks fold into their base_arm cell: allocation-only
    # extensions charged at full cost (all evals, all CPU-hours, honest
    # partials — a batch task IS a scored disposition of that arm).
    batch_by_arm = {}
    for tid, t in _batch_tasks(ROOT):
        if t.get("kind", "search") == "search":
            batch_by_arm.setdefault(t["base_arm"], []).append(
                "GS_R1_" + tid)
    for arm in SEARCH_ARMS:
        seeds = freeze["arms"][arm]["seeds"]
        completed, attempted = [], 0
        cpu_h = 0.0
        phenos = set()
        fams = set()
        batch_ids = batch_by_arm.get(arm, [])

        def fold_run(rid):
            nonlocal completed, cpu_h, phenos, fams, total_search_evals
            d = json.load(open(os.path.join(res, rid + ".json")))
            completed.append(rid)
            cpu_h += float(d.get("cpu_hours") or 0.0)
            total_search_evals += int((d.get("counts") or {}).get("T0", 0))
            for sv in d.get("survivors", []):
                phenos.add(sv["phenotype_digest"])
                fams.add(sv.get("F_arch"))
                prev = survivors_by_pheno.get(sv["phenotype_digest"])
                if prev is None:
                    survivors_by_pheno[sv["phenotype_digest"]] = {
                        "phenotype_digest": sv["phenotype_digest"],
                        "genotype_digest": sv["genotype_digest"],
                        "genome": sv["genome"], "arms": [arm],
                        "t2": sv.get("t2")}
                else:
                    if arm not in prev["arms"]:
                        prev["arms"].append(arm)

        for s in seeds:
            rid = "GS_R1_%s_s%d" % (arm, s)
            st, _ = _load_status(ROOT, rid)
            attempted += 1
            if st == "ok":
                fold_run(rid)
        for rid in batch_ids:
            st, _ = _load_status(ROOT, rid)
            attempted += 1
            if st == "ok":
                fold_run(rid)
        mph = (len(phenos) / cpu_h) if cpu_h > 0 else None
        arm_report[arm] = {
            "attempted": attempted, "completed": len(completed),
            "completed_run_ids": completed,
            "batch_task_run_ids": batch_ids,
            "cpu_hours": round(cpu_h, 6),
            "distinct_t2_viable_phenotypes": len(phenos),
            "distinct_F_arch_among_survivors": len(fams),
            "morphologies_per_cpu_hour": round(mph, 6) if mph else None,
        }

    # ---- sweep (frozen 288 shards; batch shards beyond them are extra/
    # retry coverage, charged and counted — completeness stays frozen-only)
    n_shards = int(freeze["arms"]["GSE_sweep"]["shards"])
    frozen_ok = 0
    sweep_viable = 0
    sweep_evaluated = 0
    sweep_cpu_h = 0.0
    sweep_by_farch = {}
    batch_shard_ids = []

    def fold_shard(rid):
        nonlocal sweep_viable, sweep_evaluated, sweep_cpu_h
        d = json.load(open(os.path.join(res, rid + ".json")))
        sweep_viable += int(d["n_viable"])
        sweep_evaluated += int(d["n_evaluated"])
        sweep_cpu_h += float(d.get("cpu_hours") or 0.0)
        for k, v in d.get("by_F_arch", {}).items():
            sweep_by_farch[k] = sweep_by_farch.get(k, 0) + v

    for c in range(n_shards):
        rid = "GS_R1_GSE_c%d" % c
        if _load_status(ROOT, rid)[0] == "ok":
            frozen_ok += 1
            fold_shard(rid)
    for p in sorted(glob.glob(os.path.join(res, "GS_R1_GSE_c*.json"))):
        b = os.path.basename(p)[:-len(".json")]
        try:
            c = int(b[len("GS_R1_GSE_c"):])
        except ValueError:
            continue
        if c < n_shards:
            continue  # frozen id space: handled above, never double-counted
        batch_shard_ids.append(b)
        if _load_status(ROOT, b)[0] == "ok":
            fold_shard(b)
    sweep_ok = frozen_ok + sum(1 for b in batch_shard_ids
                               if _load_status(ROOT, b)[0] == "ok")
    sweep_attempted = n_shards + len(batch_shard_ids)
    sweep_complete = frozen_ok == n_shards
    sweep_mph = (sweep_viable / sweep_cpu_h) if sweep_cpu_h > 0 else None
    sweep_report = {
        "attempted": sweep_attempted, "completed": sweep_ok,
        "frozen_attempted": n_shards, "frozen_completed": frozen_ok,
        "batch_shard_run_ids": batch_shard_ids,
        "complete": sweep_complete,
        "n_evaluated": sweep_evaluated, "n_viable": sweep_viable,
        "cpu_hours": round(sweep_cpu_h, 6),
        "viable_per_cpu_hour": round(sweep_mph, 6) if sweep_mph else None,
        "viable_by_F_arch": dict(sorted(sweep_by_farch.items())),
    }

    # ---- held-out T3 on survivors (freeze key; evaluated ONLY here)
    from evaluation.t3_ecology import evaluate_t3
    from morphology.schema import OCMMorphologyGenomeV1
    t3_verdicts = []
    for ph, sv in sorted(survivors_by_pheno.items()):
        r3 = evaluate_t3(OCMMorphologyGenomeV1.from_json_obj(sv["genome"]),
                         freeze["t3_key"])
        t3_verdicts.append({
            "phenotype_digest": ph,
            "verdict": ("SURVIVOR_T3_GENERALIZATION_HOLD" if r3["feasible"]
                        else "SURVIVOR_T3_GENERALIZATION_FAIL"),
            "solved_fraction": r3["evaluation"]["solved_fraction"],
            "arms": sv["arms"],
        })

    # ---- first-match terminal rule (frozen)
    baseline = freeze["baselines_acceleration"]["frozen_baseline"]
    base_mph = baseline["morphologies_per_cpu_hour"]
    gsa_metrics = {a: arm_report[a]["morphologies_per_cpu_hour"]
                   for a in NOVELTY_ARMS + ["GSA5_surrogate"]
                   if arm_report[a]["completed"] > 0
                   and arm_report[a]["morphologies_per_cpu_hour"] is not None}
    best_arm = max(gsa_metrics, key=gsa_metrics.get) if gsa_metrics else None

    def _fams_of(arm):
        rid_phenos = set()
        run_ids = ["GS_R1_%s_s%d" % (arm, s)
                   for s in freeze["arms"][arm]["seeds"]]
        run_ids += batch_by_arm.get(arm, [])
        for rid in run_ids:
            if _load_status(ROOT, rid)[0] != "ok":
                continue
            d = json.load(open(os.path.join(res, rid + ".json")))
            for sv in d.get("survivors", []):
                rid_phenos.add((sv["phenotype_digest"], sv.get("F_arch")))
        fams = {f for _, f in rid_phenos}
        return len(fams)

    rule_ids = [r["id"] for r in freeze["terminal_rules_first_match"]]
    terminal = None
    if total_search_evals == 0:
        terminal = "CANNOT_CHECK_NO_SCORED_DISPOSITIONS"
    elif (sweep_complete and sweep_mph is not None and best_arm is not None
          and sweep_mph >= gsa_metrics[best_arm]):
        terminal = "MORPHOLOGY_SEARCH_COST_DOMINATES__SWEEP"
    elif (best_arm is not None and base_mph is not None
          and gsa_metrics[best_arm] > base_mph
          and _fams_of(best_arm) >= 2):
        terminal = "ACCELERATION_POSITIVE"
    elif (gsa_metrics and base_mph is not None
          and all(v <= base_mph for v in gsa_metrics.values())):
        terminal = "ACCELERATION_NEGATIVE"
    else:
        nov_done = [arm_report[a]["morphologies_per_cpu_hour"]
                    for a in NOVELTY_ARMS if arm_report[a]["completed"] > 0]
        g5 = arm_report["GSA5_surrogate"]
        if (g5["completed"] > 0 and len(nov_done) >= 2
                and g5["morphologies_per_cpu_hour"] is not None
                and g5["morphologies_per_cpu_hour"]
                < statistics.median(nov_done)):
            terminal = "SURROGATE_NOT_TRUSTWORTHY"
        else:
            terminal = "MIXED_INTERMEDIATE_NO_TERMINAL"
    vocab = {r["id"]: r["vocab"]
             for r in freeze["terminal_rules_first_match"]}

    from search.failure_memory import read_failures_summary
    fail_summary = read_failures_summary()

    out = {
        "aggregate_id": "GS_R1_AGGREGATE",
        "schema": "GS_R1_AGGREGATE_V1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "freeze_sha256": fsha,
        "manifest_sha256": sha256_file(os.path.join(
            ROOT, "manifests", "GS_R1_TASKS.json")),
        "code_digest_drift_vs_freeze": code_drift,
        "arms": arm_report,
        "sweep": sweep_report,
        "n_distinct_survivors": len(survivors_by_pheno),
        "heldout_t3_key_id": freeze["heldout_t3"]["t3_key_id"],
        "t3_verdicts": t3_verdicts,
        "t3_summary": {
            v: sum(1 for t in t3_verdicts if t["verdict"] == v)
            for v in ("SURVIVOR_T3_GENERALIZATION_HOLD",
                      "SURVIVOR_T3_GENERALIZATION_FAIL")},
        "acceleration_baseline": baseline,
        "best_gsa_arm": best_arm,
        "terminal_rule_id": terminal,
        "terminal_vocab": vocab.get(terminal),
        "frozen_rule_ids_in_order": rule_ids,
        "failure_summary": fail_summary,
    }
    path = os.path.join(res, "GS_R1_AGGREGATE.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    with open(os.path.join(res, "GS_R1_AGGREGATE.status"), "w") as fh:
        fh.write("ok\n")
    print(json.dumps({
        "terminal": terminal, "vocab": vocab.get(terminal),
        "best_gsa_arm": best_arm,
        "gsa_metrics": gsa_metrics,
        "baseline_mph": base_mph,
        "sweep": {"complete": sweep_complete,
                  "viable_per_cpu_hour": sweep_mph,
                  "n_viable": sweep_viable},
        "n_distinct_survivors": len(survivors_by_pheno),
        "t3": out["t3_summary"]}, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
