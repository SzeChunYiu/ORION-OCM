#!/usr/bin/env python3
"""RV-377-180 (B6) driver: runs the frozen unit list on one host, NPROC at a time, under nice.

Usage: gmi_b6_driver.py HOST STAGE NPROC [SEEDS_CSV] [EVALS]
  STAGE  sources | arms | all | summary
Stage 1 (sources): E_smooth1, E_smooth3, E_rnd<s>, E_twin<s> for each seed.
Stage 2 (arms):    SAME  RESET/CONTINUED/TWIN, CROSS RESET/CONTINUED/TWIN, DISJ CONTINUED/TWIN (DISJ shares CROSS's RESET).
Every unit is one subprocess writing its own receipt with the host token in the name; logs in logs_b6/.
"""
import concurrent.futures
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def units(stage, seeds, evals):
    out = []
    if stage in ("sources", "all"):
        for s in seeds:
            for eco in ("E_smooth1", "E_smooth3", f"E_rnd{s}", f"E_twin{s}"):
                out.append((f"src_{eco}_S{s}", ["source", eco, str(s), "{HOST}", str(evals)]))
    if stage in ("arms", "all"):
        for s in seeds:
            for pair, arms in (("SAME", ("RESET", "CONTINUED", "TWIN")), ("CROSS", ("RESET", "CONTINUED", "TWIN")), ("DISJ", ("CONTINUED", "TWIN"))):
                for arm in arms:
                    out.append((f"arm_{pair}_{arm}_S{s}", ["arm", pair, arm, str(s), "{HOST}", str(evals)]))
    return out


def main():
    host, stage, nproc = sys.argv[1], sys.argv[2], int(sys.argv[3])
    seeds = [int(x) for x in (sys.argv[4] if len(sys.argv) > 4 else "0,1,2").split(",")]
    evals = int(sys.argv[5]) if len(sys.argv) > 5 else 20000
    if stage == "summary":
        subprocess.call(["nice", "-n", "10", PY, "-m", "gmi_microscope.b6_development", "summary", host], cwd=ROOT); return
    os.makedirs(os.path.join(ROOT, "logs_b6"), exist_ok=True)
    us = units(stage, seeds, evals)
    print(f"{host}: {len(us)} units, {nproc} workers, {evals} evaluations", flush=True)

    def run(u):
        uid, args = u
        cmd = ["nice", "-n", "10", PY, "-m", "gmi_microscope.b6_development"] + [a.replace("{HOST}", host) for a in args]
        logp = os.path.join(ROOT, "logs_b6", f"{uid}_{host}.log"); t0 = time.time()
        with open(logp, "w") as log:
            log.write("$ " + " ".join(cmd) + "\n"); log.flush()
            rc = subprocess.call(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        row = {"unit": uid, "rc": rc, "seconds": round(time.time() - t0, 1)}
        print(json.dumps(row), flush=True); return row

    rows = []
    if stage == "all":
        with concurrent.futures.ThreadPoolExecutor(nproc) as ex: rows += list(ex.map(run, units("sources", seeds, evals)))
        with concurrent.futures.ThreadPoolExecutor(nproc) as ex: rows += list(ex.map(run, units("arms", seeds, evals)))
    else:
        with concurrent.futures.ThreadPoolExecutor(nproc) as ex: rows += list(ex.map(run, us))
    json.dump({"host": host, "stage": stage, "rows": rows}, open(os.path.join(ROOT, "logs_b6", f"driver_{stage}_{host}.json"), "w"), indent=1)
    print(f"DONE {host} {stage}: {sum(r['rc'] == 0 for r in rows)}/{len(rows)} rc=0", flush=True)


if __name__ == "__main__":
    main()
