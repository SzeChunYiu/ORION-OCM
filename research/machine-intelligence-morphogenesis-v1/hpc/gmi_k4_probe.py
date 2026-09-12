#!/usr/bin/env python3
"""Measure the LUNARC environment before rendering the protected K4 V2 array.

This probe is DEVELOPMENT-ONLY. It uses a fixed non-beacon seed solely to measure runtime/RSS and to
confirm the harness imports on the cluster. Its scientific verdict is never admitted to the protected
aggregate. The probe pins prediction, generator and successor freezes so the submitter can reject stale sizing.
"""
from __future__ import annotations
import hashlib, json, os, platform, resource, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(ROOT, "GMI_K4_LOFO_FREEZE_V1.json")
GEN_FREEZE = os.path.join(ROOT, "GMI_K4_GENERATOR_FREEZE_V1.json")
SUCCESSOR = os.path.join(ROOT, "GMI_K4_PROTECTED_SUCCESSOR_FREEZE_V2.json")
OUT = os.path.join(ROOT, "LUNARC_ENV_PROBE_V1.json")


def sh(cmd):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
        return {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": repr(e)}


def jhash(path):
    raw = open(path).read(); return json.loads(raw), hashlib.sha256(raw.encode()).hexdigest()


def main():
    full, freeze_sha = jhash(FREEZE); freeze = dict(full); freeze.pop("name_key", None)
    gen, gen_sha = jhash(GEN_FREEZE); succ, succ_sha = jhash(SUCCESSOR)
    if gen.get("status") != "FROZEN_BEFORE_ANY_K4_SEARCH_RESULT": raise SystemExit("bad generator freeze status")
    if succ.get("status") != "FROZEN_BEFORE_PUBLIC_BEACON_AND_BEFORE_ANY_V2_PROTECTED_RESULT": raise SystemExit("bad successor freeze status")

    partitions = sh(["sinfo", "-h", "-o", "%P|%a|%l|%c|%m|%G"])
    assoc = sh(["sacctmgr", "-n", "-P", "show", "assoc", f"user={os.environ.get('USER','')}", "format=Account,Partition,QOS"])
    slurm_ver = sh(["sinfo", "--version"])

    fam = sorted(freeze["families"])[0]; gram = sorted(freeze["grammars"])[0]
    from gmi_k4_search_v2 import run_cell
    development_seed = 0x4B345052
    t0 = time.perf_counter(); r = run_cell(fam, gram, "w1", freeze=freeze, seed=development_seed, budget=1_000_000)
    wall = time.perf_counter() - t0; ru = resource.getrusage(resource.RUSAGE_SELF)

    rec = {
        "schema": "LUNARCEnvProbeV3",
        "status": "DEVELOPMENT_ONLY_MEASURED_NOT_SUBMITTED",
        "scientific_use": "SIZING_AND_IMPORT_SMOKE_ONLY__VERDICT_EXCLUDED_FROM_PROTECTED_K4",
        "host": platform.node(), "platform": platform.platform(), "python": sys.version, "cwd": os.getcwd(),
        "freeze_sha256": freeze_sha, "generator_freeze_sha256": gen_sha, "successor_freeze_sha256": succ_sha,
        "slurm_version": slurm_ver, "partitions": partitions, "associations": assoc,
        "pilot": {"family": fam, "grammar": gram, "cell": "w1", "development_seed": development_seed,
                  "development_verdict_not_evidence": r.get("verdict"), "wall_seconds": wall, "peak_rss_kb": ru.ru_maxrss,
                  "scored_candidates": r.get("coverage", {}).get("scored_candidates"), "palette_size": r.get("coverage", {}).get("palette_size")},
        "sizing_rule_frozen_here": {"time_safety_factor": 50.0, "minimum_wall_seconds": 300,
                                     "memory_safety_factor": 4.0, "minimum_memory_mib": 512,
                                     "note": "Renderer uses measured pilot wall/RSS only; account and partition require explicit operator choice validated against this probe."}
    }
    with open(OUT, "w") as f: json.dump(rec, f, indent=1, sort_keys=True)
    print(json.dumps({"wrote": OUT, "status": rec["status"], "pilot_wall_seconds": wall,
                      "partition_probe_rc": partitions["returncode"], "assoc_probe_rc": assoc["returncode"]}))


if __name__ == "__main__": main()
