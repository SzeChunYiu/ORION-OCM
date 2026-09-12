#!/usr/bin/env python3
"""One K4 array task, with the brief's part-J execution discipline enforced rather than described.

Every task persists, in its own receipt: git commit SHA, both freeze artifact SHAs, SLURM job/array id,
interpreter and platform versions, the task hash, the seed and how it was derived, the resource request,
actual wall time, CPU time, peak memory, exit code, the complete raw result and the scored verdict.

TWO RULES THAT ARE ENFORCED IN CODE, NOT LEFT TO THE OPERATOR:

  * A FAILED TASK STILL WRITES A RECEIPT. The brief states that no successful aggregate may omit failed seeds. A task
    that raises writes a receipt with status=FAILED and the traceback, so the aggregate cannot silently lose it. An
    aggregator that finds a gap in the task index range is required to treat the gap as a failure, not as absence.

  * THE RUNNER NEVER READS `name_key`. The freeze carries the family-id -> architecture-name mapping for human
    adjudication afterwards. This module loads the freeze and deletes that key before anything else touches it, so a
    name leak would require editing this file, which shows up in the diff.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(ROOT, "GMI_K4_LOFO_FREEZE_V1.json")
GEN_FREEZE = os.path.join(ROOT, "GMI_K4_GENERATOR_FREEZE_V1.json")
RES = os.path.join(ROOT, "microscopes", "results", "k4")


def load_freeze():
    with open(FREEZE) as f:
        raw = f.read()
    body = json.loads(raw)
    body.pop("name_key", None)          # the name barrier, enforced here
    return body, hashlib.sha256(raw.encode()).hexdigest()


def load_generator_freeze():
    with open(GEN_FREEZE) as f:
        raw = f.read()
    body = json.loads(raw)
    if body.get("status") != "FROZEN_BEFORE_ANY_K4_SEARCH_RESULT":
        raise RuntimeError(f"unexpected generator freeze status: {body.get('status')}")
    return body, hashlib.sha256(raw.encode()).hexdigest()


def git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def task_plan(freeze):
    """the full task list, in a canonical order fixed by the freeze -- not by the runner's discretion."""
    fams = sorted(freeze["families"])
    grams = sorted(freeze["grammars"])
    plan = []
    for fid in fams:
        for g in grams:
            for cell in ("w1", "w2", "w4", "w8"):
                plan.append({"family": fid, "grammar": g, "cell": cell})
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-index", type=int, required=True)
    ap.add_argument("--job-id", default="local")
    ap.add_argument("--host", default="unknown")
    ap.add_argument("--budget", type=int, default=1000000)
    a = ap.parse_args()

    os.makedirs(RES, exist_ok=True)
    t0 = time.time()
    freeze, freeze_sha = load_freeze()
    gen_freeze, gen_freeze_sha = load_generator_freeze()
    plan = task_plan(freeze)
    rec = {
        "schema": "GMIK4TaskReceiptV2",
        "task_index": a.task_index, "slurm_job_id": a.job_id, "host": a.host,
        "git_commit_sha": git_sha(), "freeze_artifact_sha256": freeze_sha,
        "generator_freeze_sha256": gen_freeze_sha,
        "freeze_declared_sha256": freeze.get("freeze_sha256"),
        "generator_freeze_schema": gen_freeze.get("schema"),
        "python_version": sys.version.split()[0], "platform": platform.platform(),
        "resource_request": {"cpus": 1, "budget_scored_candidates": a.budget},
        "n_tasks_in_plan": len(plan),
    }
    try:
        if not 0 <= a.task_index < len(plan):
            raise IndexError(f"task index {a.task_index} outside plan of {len(plan)}")
        unit = plan[a.task_index]
        rec.update(unit)
        rec["task_hash"] = hashlib.sha256(
            json.dumps({**unit, "freeze": freeze_sha, "generator_freeze": gen_freeze_sha}, sort_keys=True).encode()).hexdigest()
        # seed derivation is recorded, not improvised (sub-gate IG-2)
        rec["seed"] = int(rec["task_hash"][:8], 16)
        rec["seed_derivation"] = "sha256(task_spec || family_freeze_sha || generator_freeze_sha)[:8]; deterministic given both frozen contracts"

        from gmi_k4_search import run_cell        # imported late so an import error is still receipted
        out = run_cell(unit["family"], unit["grammar"], unit["cell"],
                       freeze=freeze, seed=rec["seed"], budget=a.budget)
        rec["raw_result"] = out
        rec["verdict"] = out["verdict"]
        rec["status"] = "OK"
    except Exception:
        rec["status"] = "FAILED"
        rec["traceback"] = traceback.format_exc()
        rec["verdict"] = "TASK_FAILED"
    finally:
        ru = resource.getrusage(resource.RUSAGE_SELF)
        rec["wall_seconds"] = round(time.time() - t0, 3)
        rec["cpu_seconds"] = round(ru.ru_utime + ru.ru_stime, 3)
        rec["peak_rss_kb"] = ru.ru_maxrss
        rec["exit_code"] = 0 if rec.get("status") == "OK" else 1
        out_path = os.path.join(RES, f"K4_{a.host}_{a.job_id}_{a.task_index:05d}.json")
        with open(out_path, "w") as f:
            json.dump(rec, f, indent=1, sort_keys=True, default=str)
        print(json.dumps({k: rec.get(k) for k in
                          ("task_index", "family", "grammar", "cell", "verdict", "status",
                           "wall_seconds", "cpu_seconds")}))
    sys.exit(rec["exit_code"])


if __name__ == "__main__":
    main()
