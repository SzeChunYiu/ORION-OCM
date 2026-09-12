#!/usr/bin/env python3
"""Render and optionally submit the frozen K4 LUNARC array from a measured probe.

The renderer refuses guessed cluster sizing. Account and partition are explicit operator inputs but
must appear in `LUNARC_ENV_PROBE_V1.json`. Wall time and memory come only from the measured pilot and
the safety factors frozen by `gmi_k4_probe.py`. Both the family freeze and generator freeze must match
the measured probe. Default is render-only; `--submit` is an explicit action.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE = os.path.join(ROOT, "LUNARC_ENV_PROBE_V1.json")
TEMPLATE = os.path.join(ROOT, "hpc", "gmi_k4_array.sbatch")
FREEZE = os.path.join(ROOT, "GMI_K4_LOFO_FREEZE_V1.json")
GEN_FREEZE = os.path.join(ROOT, "GMI_K4_GENERATOR_FREEZE_V1.json")
RENDERED = os.path.join(ROOT, "hpc", "gmi_k4_array.rendered.sbatch")
RECEIPT = os.path.join(ROOT, "hpc", "GMI_K4_SUBMISSION_RECEIPT_V1.json")


def hhmmss(seconds):
    sec = max(60, int(math.ceil(seconds / 60.0) * 60))
    h, rem = divmod(sec, 3600); m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--partition", required=True)
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--array-concurrency", type=int, default=64)
    a = ap.parse_args()

    if not os.path.exists(PROBE):
        raise SystemExit("LUNARC_ENV_PROBE_V1.json absent; run hpc/gmi_k4_probe.py on LUNARC first")
    probe = json.load(open(PROBE))
    if probe.get("status") != "MEASURED_NOT_SUBMITTED":
        raise SystemExit(f"unexpected probe status: {probe.get('status')}")
    ptxt = probe.get("partitions", {}).get("stdout", "")
    atxt = probe.get("associations", {}).get("stdout", "")
    if a.partition not in ptxt:
        raise SystemExit(f"partition {a.partition!r} not present in measured sinfo output")
    if a.account not in atxt:
        raise SystemExit(f"account {a.account!r} not present in measured association output")

    freeze_raw = open(FREEZE).read(); freeze_sha = hashlib.sha256(freeze_raw.encode()).hexdigest()
    gen_raw = open(GEN_FREEZE).read(); gen_sha = hashlib.sha256(gen_raw.encode()).hexdigest()
    if probe.get("freeze_sha256") != freeze_sha:
        raise SystemExit("probe family-freeze SHA does not match current freeze; reprobe after code/freeze change")
    if probe.get("generator_freeze_sha256") != gen_sha:
        raise SystemExit("probe generator-freeze SHA does not match current freeze; reprobe after generator change")

    pilot = probe["pilot"]; sizing = probe["sizing_rule_frozen_here"]
    wall = max(float(sizing["minimum_wall_seconds"]), float(pilot["wall_seconds"]) * float(sizing["time_safety_factor"]))
    rss_kb = max(1.0, float(pilot["peak_rss_kb"]))
    mem_mib = max(int(sizing["minimum_memory_mib"]), int(math.ceil((rss_kb / 1024.0) * float(sizing["memory_safety_factor"]))))
    n_tasks = 22 * 3 * 4
    conc = max(1, min(a.array_concurrency, n_tasks))
    array = f"0-{n_tasks-1}%{conc}"

    src = open(TEMPLATE).read()
    replacements = {
        "__ACCOUNT__": a.account,
        "__PARTITION__": a.partition,
        "__WALLTIME__": hhmmss(wall),
        "__MEM__": f"{mem_mib}M",
        "__ARRAY__": array,
    }
    for old, new in replacements.items(): src = src.replace(old, new)
    leftovers = sorted(set(re.findall(r"__[A-Z_]+__", src)))
    if leftovers:
        raise SystemExit(f"unrendered placeholders remain: {leftovers}")
    open(RENDERED, "w").write(src)

    rec = {
        "schema": "GMIK4SubmissionReceiptV2",
        "status": "RENDERED_NOT_SUBMITTED",
        "freeze_sha256": freeze_sha,
        "generator_freeze_sha256": gen_sha,
        "probe_path": os.path.relpath(PROBE, ROOT),
        "probe_host": probe.get("host"),
        "pilot": pilot,
        "account": a.account, "partition": a.partition,
        "rendered": {"walltime": replacements["__WALLTIME__"], "mem_per_cpu": replacements["__MEM__"], "array": array},
        "rendered_sha256": hashlib.sha256(src.encode()).hexdigest(),
        "submitted_at_unix": None,
        "sbatch_stdout": None,
        "sbatch_stderr": None,
        "job_id": None,
    }
    if a.submit:
        p = subprocess.run(["sbatch", RENDERED], cwd=ROOT, text=True, capture_output=True)
        rec["submitted_at_unix"] = time.time(); rec["sbatch_stdout"] = p.stdout.strip(); rec["sbatch_stderr"] = p.stderr.strip()
        if p.returncode != 0:
            rec["status"] = "SUBMISSION_FAILED"
        else:
            m = re.search(r"Submitted batch job\s+(\d+)", p.stdout)
            rec["job_id"] = None if not m else int(m.group(1)); rec["status"] = "SUBMITTED"
    json.dump(rec, open(RECEIPT, "w"), indent=1, sort_keys=True)
    print(json.dumps({"status": rec["status"], "rendered": rec["rendered"], "job_id": rec["job_id"], "receipt": RECEIPT}, sort_keys=True))
    return 0 if rec["status"] not in ("SUBMISSION_FAILED",) else 3


if __name__ == "__main__":
    raise SystemExit(main())
