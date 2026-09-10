#!/usr/bin/env python3
"""Run a slice of the frozen manifest across a process pool.

The lu2026-2-51 association caps a user at 300 submitted jobs, and array tasks
count individually against it. So this lane spends CORES, not job slots: a
handful of jobs, each with -c N, each fanning its manifest slice across N
worker processes.

Determinism is unaffected: every task is still a deterministic stride of the
enumeration, and each writes its own result file. Pool order does not enter
any result.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _one(task: dict) -> dict:
    out = os.path.join(HERE, "results", "MEX_n%d_s%dof%d_%s.json" % (
        task["n"], task["shard"], task["nshards"], task["mode"]))
    status = out.replace(".json", ".status")
    if os.path.exists(status):
        with open(status) as fh:
            if fh.read().startswith("ok"):
                return {"task_id": task["task_id"], "state": "cached"}
    cmd = [sys.executable, os.path.join(HERE, "run_shard.py"),
           "--n", str(task["n"]), "--shard", str(task["shard"]),
           "--nshards", str(task["nshards"]), "--mode", task["mode"],
           "--ticks", str(task["ticks"]), "--out", out]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        with open(status, "w") as fh:      # retain the crash
            fh.write("fail rc=%d\n%s\n" % (r.returncode, r.stderr[-2000:]))
        return {"task_id": task["task_id"], "state": "fail",
                "rc": r.returncode, "stderr": r.stderr[-400:]}
    return {"task_id": task["task_id"], "state": "ok",
            "seconds": round(time.time() - t0, 1)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--slice", type=int, default=0)
    ap.add_argument("--nslices", type=int, default=1)
    ap.add_argument("--workers", type=int,
                    default=int(os.environ.get("SLURM_CPUS_PER_TASK", "8")))
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    with open(a.manifest) as fh:
        man = json.load(fh)
    tasks = [t for i, t in enumerate(man["tasks"]) if i % a.nslices == a.slice]
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    print("slice %d/%d: %d tasks on %d workers"
          % (a.slice, a.nslices, len(tasks), a.workers), flush=True)

    t0 = time.time()
    with mp.Pool(a.workers) as pool:
        done = []
        for res in pool.imap_unordered(_one, tasks):
            done.append(res)
            if len(done) % 5 == 0:
                print("  %d/%d done (%.1f min)"
                      % (len(done), len(tasks), (time.time() - t0) / 60),
                      flush=True)
    summary = {
        "schema": "MEX_POOL_V1", "slice": a.slice, "nslices": a.nslices,
        "workers": a.workers, "n_tasks": len(tasks),
        "n_ok": sum(1 for d in done if d["state"] in ("ok", "cached")),
        "n_fail": sum(1 for d in done if d["state"] == "fail"),
        "failures": [d for d in done if d["state"] == "fail"][:10],
        "minutes": round((time.time() - t0) / 60, 1),
        "protocol_sha256": man.get("protocol_sha256"),
        "code_digest": man.get("code_digest"),
    }
    text = json.dumps(summary, indent=1, sort_keys=True)
    print(text, flush=True)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text)
    return 0 if summary["n_fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
