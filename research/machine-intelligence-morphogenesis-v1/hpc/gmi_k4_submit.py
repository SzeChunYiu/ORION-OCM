#!/usr/bin/env python3
"""Render and optionally submit the protected K4 V2 LUNARC array from a measured development-only probe.

The renderer refuses guessed cluster sizing and refuses protected submission until prediction, generator,
successor and public-beacon contracts all match the checked-out tree. Account and partition are explicit
operator inputs but must appear in the measured LUNARC probe. Default is render-only.
"""
from __future__ import annotations

import argparse, hashlib, json, math, os, re, subprocess, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE = os.path.join(ROOT, "LUNARC_ENV_PROBE_V1.json")
TEMPLATE = os.path.join(ROOT, "hpc", "gmi_k4_array.sbatch")
FREEZE = os.path.join(ROOT, "GMI_K4_LOFO_FREEZE_V1.json")
GEN_FREEZE = os.path.join(ROOT, "GMI_K4_GENERATOR_FREEZE_V1.json")
SUCCESSOR = os.path.join(ROOT, "GMI_K4_PROTECTED_SUCCESSOR_FREEZE_V2.json")
BEACON = os.path.join(ROOT, "GMI_K4_PUBLIC_BEACON_V2.json")
RENDERED = os.path.join(ROOT, "hpc", "gmi_k4_array.rendered.sbatch")
RECEIPT = os.path.join(ROOT, "hpc", "GMI_K4_SUBMISSION_RECEIPT_V2.json")


def h(path): return hashlib.sha256(open(path, "rb").read()).hexdigest()
def hhmmss(seconds):
    sec = max(60, int(math.ceil(seconds / 60.0) * 60)); hr, rem = divmod(sec, 3600); mi, se = divmod(rem, 60)
    return f"{hr:02d}:{mi:02d}:{se:02d}"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--account", required=True); ap.add_argument("--partition", required=True)
    ap.add_argument("--submit", action="store_true"); ap.add_argument("--array-concurrency", type=int, default=64); a = ap.parse_args()
    for p in (PROBE, FREEZE, GEN_FREEZE, SUCCESSOR, BEACON, TEMPLATE):
        if not os.path.exists(p): raise SystemExit(f"required protected-execution artifact absent: {p}")

    probe = json.load(open(PROBE)); beacon = json.load(open(BEACON)); succ = json.load(open(SUCCESSOR))
    if probe.get("status") != "DEVELOPMENT_ONLY_MEASURED_NOT_SUBMITTED": raise SystemExit(f"unexpected probe status {probe.get('status')}")
    if succ.get("status") != "FROZEN_BEFORE_PUBLIC_BEACON_AND_BEFORE_ANY_V2_PROTECTED_RESULT": raise SystemExit("unexpected successor freeze status")
    if beacon.get("status") != "ACQUIRED_NO_REROLL" or not beacon.get("no_reroll") or not beacon.get("sha256_signature_consistency_verified"):
        raise SystemExit("invalid protected public beacon receipt")

    hashes = {"freeze_sha256": h(FREEZE), "generator_freeze_sha256": h(GEN_FREEZE), "successor_freeze_sha256": h(SUCCESSOR)}
    for key, val in hashes.items():
        if probe.get(key) != val: raise SystemExit(f"stale LUNARC probe: {key} differs; rerun development-only probe")
    ptxt = probe.get("partitions", {}).get("stdout", ""); atxt = probe.get("associations", {}).get("stdout", "")
    if a.partition not in ptxt: raise SystemExit(f"partition {a.partition!r} absent from measured sinfo output")
    if a.account not in atxt: raise SystemExit(f"account {a.account!r} absent from measured association output")

    pilot = probe["pilot"]; sizing = probe["sizing_rule_frozen_here"]
    wall = max(float(sizing["minimum_wall_seconds"]), float(pilot["wall_seconds"]) * float(sizing["time_safety_factor"]))
    mem_mib = max(int(sizing["minimum_memory_mib"]), int(math.ceil((max(1.0, float(pilot["peak_rss_kb"])) / 1024.0) * float(sizing["memory_safety_factor"]))))
    n_tasks = 22 * 3 * 4; conc = max(1, min(a.array_concurrency, n_tasks)); array = f"0-{n_tasks-1}%{conc}"
    src = open(TEMPLATE).read(); replacements = {"__ACCOUNT__": a.account, "__PARTITION__": a.partition, "__WALLTIME__": hhmmss(wall), "__MEM__": f"{mem_mib}M", "__ARRAY__": array}
    for old, new in replacements.items(): src = src.replace(old, new)
    leftovers = sorted(set(re.findall(r"__[A-Z_]+__", src)))
    if leftovers: raise SystemExit(f"unrendered placeholders remain: {leftovers}")
    open(RENDERED, "w").write(src)

    rec = {"schema": "GMIK4SubmissionReceiptV3", "status": "RENDERED_NOT_SUBMITTED", **hashes,
           "public_beacon_sha256": h(BEACON), "public_beacon_round": beacon.get("target_round"),
           "probe_path": os.path.relpath(PROBE, ROOT), "probe_host": probe.get("host"), "pilot": pilot,
           "account": a.account, "partition": a.partition,
           "rendered": {"walltime": replacements["__WALLTIME__"], "mem_per_cpu": replacements["__MEM__"], "array": array},
           "rendered_sha256": hashlib.sha256(src.encode()).hexdigest(), "submitted_at_unix": None,
           "sbatch_stdout": None, "sbatch_stderr": None, "job_id": None}
    if a.submit:
        p = subprocess.run(["sbatch", RENDERED], cwd=ROOT, text=True, capture_output=True); rec["submitted_at_unix"] = time.time(); rec["sbatch_stdout"] = p.stdout.strip(); rec["sbatch_stderr"] = p.stderr.strip()
        if p.returncode != 0: rec["status"] = "SUBMISSION_FAILED"
        else:
            m = re.search(r"Submitted batch job\s+(\d+)", p.stdout); rec["job_id"] = None if not m else int(m.group(1)); rec["status"] = "SUBMITTED"
    json.dump(rec, open(RECEIPT, "w"), indent=1, sort_keys=True)
    print(json.dumps({"status": rec["status"], "rendered": rec["rendered"], "job_id": rec["job_id"], "beacon_round": rec["public_beacon_round"], "receipt": RECEIPT}, sort_keys=True))
    return 0 if rec["status"] != "SUBMISSION_FAILED" else 3


if __name__ == "__main__": raise SystemExit(main())
