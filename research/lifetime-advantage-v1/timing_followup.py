"""Exposed-data measurement audit: remove baseline arithmetic-counting wrappers.

This does not edit or replace the frozen experiment. It reuses its manifest and
all eight orderings. Engines keep their existing inline counters; baseline
normal-form/execute/evaluate functions are now unwrapped. No new efficacy claim,
protected evaluation, population inference or protocol promotion is intended.
"""
from contextlib import nullcontext
import json
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys
import time

import benchmark as B


if "--worker" in sys.argv:
    B.baseline_accounting = lambda work: nullcontext()
    result = B.worker(json.load(sys.stdin))
    result["accounting"] = "BASELINE_ARITHMETIC_WRAPPERS_DISABLED; ENGINE_INLINE_COUNTERS_RETAINED"
    print(json.dumps(result))
else:
    root = Path(__file__).resolve().parent
    out = root/"results"/"timing-audit-v1"
    if out.exists():
        raise ValueError("preserve previous audit results; output already exists")
    manifest = json.loads((root/"results"/"run-v1"/"manifest.json").read_text())
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root.parents[1]/"src") + os.pathsep + str(root)
    runs = []
    for seed in B.SEEDS:
        targets = list(manifest["targets"])
        random.Random(seed).shuffle(targets)
        for arm in B.ARMS:
            request = {"arm": arm, "kind": "lifetime", "seed": seed,
                       "training": manifest["training"], "targets": targets}
            started = time.perf_counter()
            process = subprocess.run([sys.executable, str(Path(__file__)), "--worker"],
                                     input=json.dumps(request), capture_output=True, text=True, env=env)
            elapsed = time.perf_counter()-started
            if process.returncode:
                result = {"arm": arm, "seed": seed, "error": "WORKER_FAILED", "stdout": process.stdout,
                          "stderr": process.stderr, "returncode": process.returncode}
            else:
                full = json.loads(process.stdout)
                result = {key: full[key] for key in ("arm", "seed", "accounting", "training_count", "evaluation_count",
                          "verified_count", "wall_s", "cpu_s", "peak_rss_kib", "checkpoint", "persistent_serialized_bytes")}
                result["answers"] = [{key: row[key] for key in ("phase", "fingerprint", "status", "program", "verified")}
                                     for row in full["rows"]]
            result["subprocess_elapsed_s"] = elapsed
            B.write_json(out/"raw"/f"{seed}-{arm}.json", result)
            runs.append(result)
            print(json.dumps({"arm": arm, "seed": seed, "wall_s": result.get("wall_s"), "error": result.get("error")}), flush=True)
    summary = {}
    for arm in B.ARMS:
        chosen = [row for row in runs if row["arm"] == arm and "error" not in row]
        summary[arm] = {"runs": len(chosen), "verified": sum(row["verified_count"] for row in chosen),
                        "tasks": sum(row["evaluation_count"] for row in chosen)}
        for metric in ("wall_s", "cpu_s", "subprocess_elapsed_s", "peak_rss_kib"):
            values = [row[metric] for row in chosen]
            summary[arm][metric] = {"median": statistics.median(values), "min": min(values), "max": max(values)}
    B.write_json(out/"summary.json", {"evidence": "E2 EXPOSED-DATA MEASUREMENT AUDIT",
                 "freeze_commit_of_original_experiment": manifest["freeze_commit"],
                 "accounting": "BASELINE_ARITHMETIC_WRAPPERS_DISABLED; ENGINE_INLINE_COUNTERS_RETAINED",
                 "summary": summary, "errors": [row for row in runs if "error" in row],
                 "correctness_gate": all("error" not in row and row["verified_count"] == row["evaluation_count"] for row in runs)})
