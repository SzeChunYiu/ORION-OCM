#!/usr/bin/env python3
"""GS-R1h hourly checkpoint (#221 sec 18 GS-R1h): append-only honest
partials for mid-run assessment.  One line per invocation per arm/tier
in results/GS_R1_CHECKPOINTS.jsonl + a cheap one-cat status file
results/GS_R1_STATUS.json the centre polls from the login node.

No imputation: completed tasks report their result JSON; running tasks
report their LAST progress line (as_of its ts); missing tasks count as
attempted-not-started.  Frozen rules never evaluate here — the terminal
preview is explicitly labelled PARTIAL.
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time

ROOT = os.path.abspath(sys.argv[1])

SEARCH_ARMS = ["GSA1_units", "GSA2_hetero", "GSA3_farch", "GSA4_obasis",
               "GSA5_surrogate", "GSR_random_control"]


def _status(rid: str) -> str:
    p = os.path.join(ROOT, "results", rid + ".status")
    if not os.path.exists(p):
        return "missing"
    t = open(p).read().strip()
    return "ok" if t == "ok" else "fail"


def _last_progress(rid: str):
    p = os.path.join(ROOT, "results", rid + ".progress.jsonl")
    if not os.path.exists(p):
        return None
    last = None
    try:
        with open(p) as fh:
            for line in fh:
                if line.strip():
                    last = line
    except OSError:
        return None
    try:
        return json.loads(last)
    except Exception:
        return None


def _task_ids():
    """All task ids: frozen manifest first, then every adaptive batch
    (GS-R1h) — batch record files (manifests/GS_R1_BATCH_*.json) AND the
    per-task spec dirs (manifests/GS_R1_BATCH_*/*.json).  Batches are
    allocation-only additions; dedup keeps re-run records honest."""
    ids = []
    m = os.path.join(ROOT, "manifests", "GS_R1_TASKS.json")
    if os.path.exists(m):
        for t in json.load(open(m))["tasks"]:
            if t["kind"] == "search":
                ids.append("%s_s%d" % (t["arm"], t["seed"]))
    for bm in sorted(glob.glob(os.path.join(
            ROOT, "manifests", "GS_R1_BATCH_*.json"))):
        try:
            for t in json.load(open(bm)).get("tasks", []):
                if t.get("task_id"):
                    ids.append(t["task_id"])
        except Exception:
            continue
    for ts in sorted(glob.glob(os.path.join(
            ROOT, "manifests", "GS_R1_BATCH_*", "*.json"))):
        try:
            t = json.load(open(ts))
            if t.get("task_id"):
                ids.append(t["task_id"])
        except Exception:
            continue
    seen, out = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def _arm_rollup(run_ids):
    tasks = {}
    tot = {"T0": 0, "T1": 0, "T2": 0, "viable_T0": 0, "cpu_hours": 0.0,
           "completed": 0, "running": 0, "failed": 0, "missing": 0,
           "distinct_t2_viable": 0, "archives": [], "deadline_hit": 0}
    phenos = set()
    for rid in run_ids:
        st = _status(rid)
        pr = _last_progress(rid)
        tasks[rid] = {"status": st,
                      "as_of": (pr or {}).get("ts"),
                      "counts": (pr or {}).get("counts")}
        if st == "ok":
            d = json.load(open(os.path.join(ROOT, "results", rid + ".json")))
            c = d.get("counts") or {}
            for t in ("T0", "T1", "T2"):
                tot[t] += int(c.get(t, 0))
            tot["viable_T0"] += int((d.get("viable_counts") or {}).get("T0", 0))
            tot["cpu_hours"] += float(d.get("cpu_hours") or 0.0)
            tot["completed"] += 1
            tot["deadline_hit"] += 1 if d.get("deadline_hit") else 0
            for sv in d.get("survivors", []):
                phenos.add(sv["phenotype_digest"])
            tot["archives"].append(int((d.get("n_archive") or 0)))
        elif st == "fail":
            tot["failed"] += 1
        elif pr is not None:
            tot["running"] += 1
            c = pr.get("counts") or {}
            for t in ("T0", "T1", "T2"):
                tot[t] += int(c.get(t, 0))
            vc = (pr.get("viable_counts") or {})
            tot["viable_T0"] += int(vc.get("T0", 0))
            if pr.get("novelty_archive_size") is not None:
                tot["archives"].append(int(pr["novelty_archive_size"]))
        else:
            tot["missing"] += 1
    tot["distinct_t2_viable"] = len(phenos)
    mph = (len(phenos) / tot["cpu_hours"]
           if tot["cpu_hours"] > 0 else None)
    return {
        "tasks": len(run_ids), "completed": tot["completed"],
        "running": tot["running"], "failed": tot["failed"],
        "missing": tot["missing"],
        "tier_counts": {t: tot[t] for t in ("T0", "T1", "T2")},
        "viable_T0": tot["viable_T0"],
        "viability_rate": (round(tot["viable_T0"] / tot["T0"], 6)
                           if tot["T0"] else None),
        "distinct_t2_viable": tot["distinct_t2_viable"],
        "novelty_archive_sizes": sorted(tot["archives"])[-3:],
        "cpu_hours_partial": round(tot["cpu_hours"], 4),
        "morphologies_per_cpu_hour_partial": (round(mph, 6)
                                              if mph else None),
        "deadline_hit_tasks": tot["deadline_hit"],
        "per_task": tasks,
    }


def _sweep_rollup(n_shards):
    """Frozen shards 0..n_shards-1 PLUS any adaptive-batch sweep shards
    (results/GS_R1_GSE_c*.json — batch shards reuse the id space with
    shard ids >= n_shards, discovered by glob, never imputed)."""
    frozen = {"GS_R1_GSE_c%d" % c for c in range(n_shards)}
    seen = set(frozen)
    for p in glob.glob(os.path.join(ROOT, "results",
                                    "GS_R1_GSE_c*.json")):
        b = os.path.basename(p)[:-len(".json")]
        if b.startswith("GS_R1_GSE_c"):
            try:
                seen.add("GS_R1_GSE_c%d" % int(b[len("GS_R1_GSE_c"):]))
            except ValueError:
                continue
    done = ev = vi = 0
    cpu_h = 0.0
    running = 0
    for rid in sorted(seen, key=lambda r: int(r.rsplit("c", 1)[1])):
        if _status(rid) == "ok":
            d = json.load(open(os.path.join(ROOT, "results", rid + ".json")))
            done += 1
            ev += int(d["n_evaluated"])
            vi += int(d["n_viable"])
            cpu_h += float(d.get("cpu_hours") or 0.0)
        elif os.path.exists(os.path.join(ROOT, "results", rid + ".status")):
            running += 1
    return {"shards_frozen": n_shards, "shards_discovered": len(seen),
            "shards_completed": done,
            "shards_terminal_not_ok": running,
            "n_evaluated": ev, "n_viable": vi,
            "cpu_hours_partial": round(cpu_h, 4),
            "viable_per_cpu_hour_partial": (round(vi / cpu_h, 6)
                                            if cpu_h > 0 else None)}


def _partial_terminal(arms, sweep, freeze):
    """First-match preview over partials — every label carries PARTIAL_."""
    base = ((freeze.get("baselines_acceleration") or {})
            .get("frozen_baseline") or {}).get("morphologies_per_cpu_hour")
    tot_t0 = sum(a["tier_counts"]["T0"] for a in arms.values())
    if tot_t0 == 0:
        return "PARTIAL_CANNOT_CHECK_NO_SCORED_DISPOSITIONS"
    mphs = {a: v["morphologies_per_cpu_hour_partial"] for a, v in
            arms.items() if v["morphologies_per_cpu_hour_partial"]}
    if base is not None and mphs and all(v <= base for v in mphs.values()):
        return "PARTIAL_ACCELERATION_NEGATIVE_TREND"
    if mphs and base is not None and max(mphs.values()) > base:
        return "PARTIAL_ACCELERATION_POSITIVE_TREND"
    return "PARTIAL_MIXED_INTERMEDIATE"


def main() -> None:
    freeze_path = os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json")
    freeze = json.load(open(freeze_path))
    manifest = json.load(open(os.path.join(ROOT, "manifests",
                                           "GS_R1_TASKS.json")))
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    all_ids = _task_ids()
    arms = {}
    for arm in SEARCH_ARMS:
        rids = [i for i in all_ids if i.startswith(arm)]
        if rids:
            arms[arm] = _arm_rollup(["GS_R1_%s" % r for r in rids])
    # batch task ids (GS-R1h) roll up under their own label
    batch_ids = [i for i in all_ids
                 if not any(i.startswith(a) for a in SEARCH_ARMS)]
    if batch_ids:
        arms["BATCH"] = _arm_rollup(["GS_R1_%s" % r for r in batch_ids])

    n_shards = int(freeze["arms"]["GSE_sweep"]["shards"])
    sweep = _sweep_rollup(n_shards)

    ck_path = os.path.join(ROOT, "results", "GS_R1_CHECKPOINTS.jsonl")
    n_prev = 0
    if os.path.exists(ck_path):
        with open(ck_path) as fh:
            n_prev = sum(1 for line in fh if line.strip())
    line = {
        "schema": "GS_R1_CHECKPOINT_V1", "checkpoint": n_prev + 1,
        "ts": now, "freeze_sha256": manifest["freeze_sha256"],
        "arms": arms, "sweep": sweep,
        "totals": {
            "t0_evals": sum(a["tier_counts"]["T0"] for a in arms.values()),
            "t1_evals": sum(a["tier_counts"]["T1"] for a in arms.values()),
            "t2_evals": sum(a["tier_counts"]["T2"] for a in arms.values()),
            "cpu_hours": round(sum(a["cpu_hours_partial"]
                                   for a in arms.values())
                               + sweep["cpu_hours_partial"], 4)},
        "partial_terminal_preview": _partial_terminal(arms, sweep, freeze),
    }
    with open(ck_path, "a") as fh:
        fh.write(json.dumps(line, sort_keys=True) + "\n")

    status = {
        "schema": "GS_R1_STATUS_V1", "updated_utc": now,
        "freeze_sha256": manifest["freeze_sha256"],
        "campaign_stop_ts": manifest.get("stop_ts"),
        "checkpoint": line["checkpoint"],
        "search_tasks": {
            "total": len(all_ids),
            "completed": sum(a["completed"] for a in arms.values()),
            "running": sum(a["running"] for a in arms.values()),
            "failed": sum(a["failed"] for a in arms.values())},
        "arms_brief": {a: {"t0": v["tier_counts"]["T0"],
                           "viable_rate": v["viability_rate"],
                           "distinct_t2_viable": v["distinct_t2_viable"],
                           "mph_partial": v["morphologies_per_cpu_hour_partial"]}
                       for a, v in arms.items()},
        "sweep_brief": {"shards_done": sweep["shards_completed"],
                        "shards_discovered": sweep["shards_discovered"],
                        "shards_frozen": sweep["shards_frozen"],
                        "n_evaluated": sweep["n_evaluated"],
                        "n_viable": sweep["n_viable"]},
        "totals": line["totals"],
        "partial_terminal_preview": line["partial_terminal_preview"],
    }
    with open(os.path.join(ROOT, "results", "GS_R1_STATUS.json"), "w") as fh:
        json.dump(status, fh, indent=1, sort_keys=True)
    print("CHECKPOINT %d %s arms=%d sweep_done=%d/%d t0=%d" % (
        line["checkpoint"], now, len(arms), sweep["shards_completed"],
        sweep["shards_discovered"], line["totals"]["t0_evals"]))


if __name__ == "__main__":
    main()
