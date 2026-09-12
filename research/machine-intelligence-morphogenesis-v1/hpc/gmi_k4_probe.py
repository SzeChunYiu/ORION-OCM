#!/usr/bin/env python3
"""Measure the LUNARC environment before rendering the K4 array.

No partition/account is selected here. The probe records what the cluster reports and runs one tiny
name-blind K4 cell to measure wall/RSS. gmi_k4_submit.py requires an explicit account/partition that
must appear in this probe and derives time/memory sizing from the measured pilot with frozen safety factors.
Both the family prediction freeze and executable generator freeze are hashed into the probe receipt.
"""
from __future__ import annotations
import hashlib, json, os, platform, resource, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(ROOT, "GMI_K4_LOFO_FREEZE_V1.json")
GEN_FREEZE = os.path.join(ROOT, "GMI_K4_GENERATOR_FREEZE_V1.json")
OUT = os.path.join(ROOT, "LUNARC_ENV_PROBE_V1.json")


def sh(cmd):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
        return {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": repr(e)}


def main():
    raw = open(FREEZE).read(); freeze = json.loads(raw); freeze.pop("name_key", None)
    gen_raw = open(GEN_FREEZE).read(); gen = json.loads(gen_raw)
    if gen.get("status") != "FROZEN_BEFORE_ANY_K4_SEARCH_RESULT":
        raise SystemExit(f"unexpected generator freeze status: {gen.get('status')}")
    freeze_sha = hashlib.sha256(raw.encode()).hexdigest()
    gen_sha = hashlib.sha256(gen_raw.encode()).hexdigest()
    partitions = sh(["sinfo", "-h", "-o", "%P|%a|%l|%c|%m|%G"])
    assoc = sh(["sacctmgr", "-n", "-P", "show", "assoc", f"user={os.environ.get('USER','')}", "format=Account,Partition,QOS"])
    slurm_ver = sh(["sinfo", "--version"])

    # Tiny measured pilot: first canonical cell, full finite palette (currently << 1e6 candidates).
    fam = sorted(freeze["families"])[0]
    gram = sorted(freeze["grammars"])[0]
    from gmi_k4_search import run_cell
    t0 = time.perf_counter()
    r = run_cell(fam, gram, "w1", freeze=freeze, seed=0x4B345052, budget=1_000_000)
    wall = time.perf_counter() - t0
    ru = resource.getrusage(resource.RUSAGE_SELF)

    rec = {
        "schema": "LUNARCEnvProbeV2",
        "status": "MEASURED_NOT_SUBMITTED",
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "cwd": os.getcwd(),
        "freeze_sha256": freeze_sha,
        "generator_freeze_sha256": gen_sha,
        "slurm_version": slurm_ver,
        "partitions": partitions,
        "associations": assoc,
        "pilot": {
            "family": fam, "grammar": gram, "cell": "w1", "verdict": r.get("verdict"),
            "wall_seconds": wall, "peak_rss_kb": ru.ru_maxrss,
            "scored_candidates": r.get("coverage", {}).get("scored_candidates"),
            "palette_size": r.get("coverage", {}).get("palette_size"),
        },
        "sizing_rule_frozen_here": {
            "time_safety_factor": 50.0,
            "minimum_wall_seconds": 300,
            "memory_safety_factor": 4.0,
            "minimum_memory_mib": 512,
            "note": "Renderer uses measured pilot wall/RSS only; account and partition require explicit operator choice validated against this probe."
        }
    }
    with open(OUT, "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(json.dumps({"wrote": OUT, "pilot": rec["pilot"], "partition_probe_rc": partitions["returncode"], "assoc_probe_rc": assoc["returncode"]}))


if __name__ == "__main__":
    main()
