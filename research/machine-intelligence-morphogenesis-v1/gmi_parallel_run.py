#!/usr/bin/env python3
"""Parallel driver for GMI_WORK_MANIFEST_V1 units on one host.

Usage: gmi_parallel_run.py HOST LANES NPROC [UNIT_IDS_CSV]
Runs each frozen, not-done unit of the given lanes with the {HOST} token substituted,
NPROC at a time, logging every unit to logs/unit_<id>_<host>.log and writing a summary
to logs/parallel_<host>.json. It never edits the manifest (the Mac worktree marks `done`
after receipts are collected), so two hosts can run disjoint unit sets with no collision.
"""
import concurrent.futures
import datetime
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    host = sys.argv[1]
    lanes = sys.argv[2].split(",")
    nproc = int(sys.argv[3])
    only = set(sys.argv[4].split(",")) if len(sys.argv) > 4 and sys.argv[4] else None
    m = json.load(open(os.path.join(ROOT, "GMI_WORK_MANIFEST_V1.json")))
    units = [u for u in m["units"] if u["lane"] in lanes and u["frozen"] and not u.get("done")
             and (only is None or u["unit_id"] in only)]
    if os.environ.get("SKIP_EXISTING"):   # re-launch: skip units whose receipt already exists
        units = [u for u in units if not os.path.exists(os.path.join(ROOT, u["receipt"].replace("{HOST}", host)))]
    os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
    print(f"{host}: {len(units)} units, {nproc} workers", flush=True)

    def run(u):
        cmd = [t.replace("{HOST}", host) for t in u["cmd"]]
        rec = u["receipt"].replace("{HOST}", host)
        logp = os.path.join(ROOT, "logs", f"unit_{u['unit_id']}_{host}.log")
        t0 = time.time()
        with open(logp, "w") as log:
            log.write("$ " + " ".join(cmd) + "\n")
            log.flush()
            rc = subprocess.call(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        ok = rc == 0 and os.path.exists(os.path.join(ROOT, rec))
        row = {"unit_id": u["unit_id"], "rc": rc, "ok": ok, "receipt": rec,
               "seconds": round(time.time() - t0, 1),
               "at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        print(json.dumps(row), flush=True)
        return row

    with concurrent.futures.ThreadPoolExecutor(nproc) as ex:
        rows = list(ex.map(run, units))
    summ = {"host": host, "lanes": lanes, "n": len(rows), "ok": sum(r["ok"] for r in rows), "rows": rows}
    json.dump(summ, open(os.path.join(ROOT, "logs", f"parallel_{host}.json"), "w"), indent=1)
    print(f"DONE {host}: {summ['ok']}/{summ['n']} ok", flush=True)


if __name__ == "__main__":
    main()
