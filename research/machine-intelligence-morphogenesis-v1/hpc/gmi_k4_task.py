#!/usr/bin/env python3
"""One protected K4 V2 array task with fail-closed provenance and receipt discipline.

Every task persists: git SHA, prediction/generator/successor freeze SHAs, public-beacon SHA and round,
SLURM IDs, environment, task hash, protected seed, resource request, wall/CPU/RSS, complete raw result
and scored verdict. Failed tasks also persist a receipt and exit nonzero.

The runner strips `name_key` before search, uses the seed-dependent V2 engine, and refuses protected
execution until the one-shot future public beacon receipt exists.
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
SUCCESSOR_FREEZE = os.path.join(ROOT, "GMI_K4_PROTECTED_SUCCESSOR_FREEZE_V2.json")
BEACON = os.path.join(ROOT, "GMI_K4_PUBLIC_BEACON_V2.json")
RES = os.path.join(ROOT, "microscopes", "results", "k4_v2")


def read_json_hash(path):
    raw = open(path).read()
    return json.loads(raw), hashlib.sha256(raw.encode()).hexdigest()


def load_contracts():
    freeze, freeze_sha = read_json_hash(FREEZE); freeze.pop("name_key", None)
    gen, gen_sha = read_json_hash(GEN_FREEZE)
    succ, succ_sha = read_json_hash(SUCCESSOR_FREEZE)
    beacon, beacon_sha = read_json_hash(BEACON)
    if gen.get("status") != "FROZEN_BEFORE_ANY_K4_SEARCH_RESULT":
        raise RuntimeError(f"unexpected generator freeze status: {gen.get('status')}")
    if succ.get("status") != "FROZEN_BEFORE_PUBLIC_BEACON_AND_BEFORE_ANY_V2_PROTECTED_RESULT":
        raise RuntimeError(f"unexpected successor freeze status: {succ.get('status')}")
    if beacon.get("status") != "ACQUIRED_NO_REROLL" or not beacon.get("no_reroll"):
        raise RuntimeError(f"invalid beacon receipt status: {beacon.get('status')}")
    if not beacon.get("sha256_signature_consistency_verified"):
        raise RuntimeError("beacon SHA256(signature) consistency was not verified")
    return freeze, freeze_sha, gen, gen_sha, succ, succ_sha, beacon, beacon_sha


def git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def task_plan(freeze):
    return [
        {"family": fid, "grammar": gram, "cell": cell}
        for fid in sorted(freeze["families"])
        for gram in sorted(freeze["grammars"])
        for cell in ("w1", "w2", "w4", "w8")
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-index", type=int, required=True)
    ap.add_argument("--job-id", default="local")
    ap.add_argument("--host", default="unknown")
    ap.add_argument("--budget", type=int, default=1_000_000)
    a = ap.parse_args()

    os.makedirs(RES, exist_ok=True)
    t0 = time.time()
    rec = {"schema": "GMIK4TaskReceiptV3", "task_index": a.task_index, "slurm_job_id": a.job_id, "host": a.host}
    try:
        freeze, freeze_sha, gen, gen_sha, succ, succ_sha, beacon, beacon_sha = load_contracts()
        plan = task_plan(freeze)
        rec.update({
            "git_commit_sha": git_sha(),
            "freeze_artifact_sha256": freeze_sha,
            "generator_freeze_sha256": gen_sha,
            "successor_freeze_sha256": succ_sha,
            "public_beacon_sha256": beacon_sha,
            "public_beacon_round": beacon.get("target_round"),
            "public_beacon_randomness": beacon.get("randomness"),
            "freeze_declared_sha256": freeze.get("freeze_sha256"),
            "python_version": sys.version.split()[0], "platform": platform.platform(),
            "resource_request": {"cpus": 1, "budget_scored_candidates": a.budget},
            "n_tasks_in_plan": len(plan),
        })
        if not 0 <= a.task_index < len(plan):
            raise IndexError(f"task index {a.task_index} outside plan of {len(plan)}")
        unit = plan[a.task_index]; rec.update(unit)
        rec["task_hash"] = hashlib.sha256(json.dumps({
            **unit, "prediction_freeze": freeze_sha, "generator_freeze": gen_sha, "successor_freeze": succ_sha
        }, sort_keys=True).encode()).hexdigest()
        seed_hex = hashlib.sha256(("GMI-K4-V2" + rec["task_hash"] + beacon["randomness"]).encode()).hexdigest()[:16]
        rec["seed"] = int(seed_hex, 16) % (2**32)
        rec["seed_derivation"] = "int(SHA256('GMI-K4-V2'||task_hash||drand_randomness)[:16],16) mod 2^32"

        from gmi_k4_search_v2 import run_cell
        out = run_cell(unit["family"], unit["grammar"], unit["cell"], freeze=freeze, seed=rec["seed"], budget=a.budget)
        rec["raw_result"] = out; rec["verdict"] = out["verdict"]; rec["status"] = "OK"
    except Exception:
        rec["status"] = "FAILED"; rec["traceback"] = traceback.format_exc(); rec["verdict"] = "TASK_FAILED"
    finally:
        ru = resource.getrusage(resource.RUSAGE_SELF)
        rec["wall_seconds"] = round(time.time() - t0, 3)
        rec["cpu_seconds"] = round(ru.ru_utime + ru.ru_stime, 3)
        rec["peak_rss_kb"] = ru.ru_maxrss
        rec["exit_code"] = 0 if rec.get("status") == "OK" else 1
        out_path = os.path.join(RES, f"K4V2_{a.host}_{a.job_id}_{a.task_index:05d}.json")
        with open(out_path, "w") as f: json.dump(rec, f, indent=1, sort_keys=True, default=str)
        print(json.dumps({k: rec.get(k) for k in ("task_index", "family", "grammar", "cell", "verdict", "status", "public_beacon_round", "wall_seconds", "cpu_seconds")}))
    sys.exit(rec["exit_code"])


if __name__ == "__main__":
    main()
