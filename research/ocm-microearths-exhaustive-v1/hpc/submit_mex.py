#!/usr/bin/env python3
"""Build the frozen EB-F0-X array manifest and submit it to LUNARC lu48.

The array index selects a manifest row. It never seeds an RNG: shards are
deterministic strides of the enumeration, so a rerun of any task reproduces
its output byte for byte.

Placement is pinned: partition lu48, account lu2026-2-51. There is deliberately
no fallback ladder. The nuc partition is refused for this project by a submit
plugin that neither sinfo nor scontrol reveals, so a ladder that tries nuc
first silently wastes the submission.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
sys.path.insert(0, LANE)

import binding       # noqa: E402
import worlds as W   # noqa: E402

PARTITION = "lu48"
ACCOUNT = "lu2026-2-51"
MEASURED_WORLDS_PER_SEC = 225.0   # measured on laptop billy, 6 ticks
N_RANGE = tuple(range(2, 9))


def build_manifest(mode: str, ticks: int, target_hours: float) -> dict:
    tasks = []
    for n in N_RANGE:
        total = W.enumeration_size(n, mode)
        core_hours = total / MEASURED_WORLDS_PER_SEC / 3600.0
        nsh = max(1, math.ceil(core_hours / target_hours))
        for s in range(nsh):
            tasks.append({"task_id": len(tasks), "n": n, "shard": s,
                          "nshards": nsh, "mode": mode, "ticks": ticks,
                          "est_hours": round(core_hours / nsh, 3)})
    return {
        "schema": "MEX_MANIFEST_V1",
        "protocol_sha256": binding.protocol_sha(LANE),
        "code_digest": binding.code_digest(LANE),
        "contract_commit": binding.CONTRACT_COMMIT,
        "partition": PARTITION, "account": ACCOUNT,
        "mode": mode, "ticks": ticks,
        "measured_worlds_per_sec": MEASURED_WORLDS_PER_SEC,
        "n_tasks": len(tasks),
        "total_worlds": sum(W.enumeration_size(n, mode) for n in N_RANGE),
        "total_core_hours": round(
            sum(W.enumeration_size(n, mode) for n in N_RANGE)
            / MEASURED_WORLDS_PER_SEC / 3600.0, 1),
        "tasks": tasks,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="MULTISET")
    ap.add_argument("--ticks", type=int, default=W.DEFAULT_TICKS)
    ap.add_argument("--target-hours", type=float, default=1.5)
    ap.add_argument("--concurrency", type=int, default=240)
    ap.add_argument("--time", default="04:00:00")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)

    man = build_manifest(a.mode, a.ticks, a.target_hours)
    path = a.manifest or os.path.join(LANE, "manifests",
                                      "MEX_MANIFEST_%s.json" % a.mode)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        old = json.load(open(path))
        if old.get("tasks") != man["tasks"]:
            print("REFUSED: frozen manifest exists with a different task list; "
                  "write a numbered amendment instead of overwriting")
            return 2
    else:
        with open(path + ".tmp", "w") as fh:
            json.dump(man, fh, indent=1, sort_keys=True)
        os.replace(path + ".tmp", path)

    print(json.dumps({k: v for k, v in man.items() if k != "tasks"}, indent=1))
    if a.dry:
        print("dry stop (manifest written; nothing submitted)")
        return 0

    cmd = ["sbatch", "-p", PARTITION, "-A", ACCOUNT, "-t", a.time,
           "--array=0-%d%%%d" % (man["n_tasks"] - 1, a.concurrency),
           os.path.join(HERE, "mex_array.sbatch"), path]
    print("SUBMIT:", " ".join(cmd))
    out = subprocess.run(cmd, capture_output=True, text=True)
    print(out.stdout.strip() or out.stderr.strip())
    return out.returncode


if __name__ == "__main__":
    sys.exit(main())
