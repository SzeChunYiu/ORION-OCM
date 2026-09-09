"""Campaign driver: FREE the manifest, sync to LUNARC, smoke, then submit.

Sequence (run from the Mac worktree or laptop):
  1. write manifests/CAMPAIGN_MZD3_MANIFEST.json (frozen task list; sha256
     of FREEZE_V1.json + capsule code included; never rewritten in place)
  2. rsync capsule to <lunarc>:$HOME/zoo221/capsule (binary-safe, checksummed)
  3. sbatch smoke (--qos=test) and require "SMOKE OK"
  4. sbatch qd_generation array (production; %K concurrency cap)

Usage: python3 submit_campaign.py <capsule_root> <lunarc_host>
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time

ROOT, HOST = sys.argv[1], sys.argv[2]


def sh(cmd: str, check: bool = True):
    print("+ %s" % cmd, flush=True)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.strip()[-2000:])
    if r.returncode != 0 and check:
        print(r.stderr.strip()[-2000:])
        raise SystemExit("command failed: %s" % cmd)
    return r


def code_digest() -> str:
    h = hashlib.sha256()
    for d in ("morphology", "evaluation", "search", "hpc"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".py"):
                h.update(open(os.path.join(ROOT, d, fn), "rb").read())
    return h.hexdigest()


def main():
    with open(os.path.join(ROOT, "FREEZE_V1.json")) as f:
        freeze = json.load(f)
    arms = freeze["production_MZ_D3"]["arms"]
    seeds = freeze["production_MZ_D3"]["seeds"]
    tasks = [{"task_id": i, "arm": arm, "seed": seed, "budget":
              freeze["production_MZ_D3"]["budget_evals_per_arm_seed"]}
             for i, (arm, seed) in enumerate(
                 (arm, seed) for arm in arms for seed in seeds)]
    manifest = {
        "manifest_id": "CAMPAIGN_MZD3_V1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tasks": tasks,
        "n_tasks": len(tasks),
        "freeze_sha256": hashlib.sha256(
            open(os.path.join(ROOT, "FREEZE_V1.json"), "rb").read()).hexdigest(),
        "code_sha256": code_digest(),
        "truth_receipt_head": json.load(open(
            os.path.join(ROOT, "archives", "CENSUS_P00_TRUTH.json")))
            ["summary"]["receipt_head"],
    }
    mpath = os.path.join(ROOT, "manifests", "CAMPAIGN_MZD3_MANIFEST.json")
    if os.path.exists(mpath):
        old = json.load(open(mpath))
        if old["tasks"] != tasks:
            raise SystemExit("frozen manifest differs — write a numbered "
                             "amendment instead of overwriting")
    else:
        with open(mpath, "w") as f:
            json.dump(manifest, f, indent=1)
    print("manifest frozen: %d tasks" % len(tasks))

    # binary-safe sync (rsync, never ssh pipes) + checksum verification
    sh("ssh %s 'mkdir -p zoo221/capsule'" % HOST)
    sh("rsync -a --delete --exclude __pycache__ --exclude .pytest_cache "
       "--exclude logs %s/ %s:zoo221/capsule/" % (ROOT, HOST))
    chk_local = sh("cd %s && find . -name '*.py' -o -name '*.json' | sort | "
                   "xargs shasum -a 256 | shasum -a 256 | cut -d' ' -f1" % ROOT).stdout.strip()
    chk_remote = sh("ssh %s \"cd zoo221/capsule && find . -name '*.py' -o -name '*.json' | sort | "
                    "xargs sha256sum | sha256sum | cut -d' ' -f1\"" % HOST).stdout.strip()
    if chk_local != chk_remote:
        raise SystemExit("checksum mismatch after rsync: %s vs %s" % (chk_local, chk_remote))
    print("capsule synced, checksum %s" % chk_local[:16])

    # smoke first (--qos=test only for short smoke jobs)
    r = sh("ssh %s 'cd zoo221/capsule && sbatch --parsable hpc/smoke.sbatch'" % HOST)
    jid = r.stdout.strip().splitlines()[-1]
    print("smoke job %s submitted; waiting" % jid)
    state = "PENDING"
    while state in ("PENDING", "RUNNING", "COMPLETING", "REQUEUED"):
        time.sleep(20)
        st = sh("ssh %s 'sacct -j %s -n -o State%%30 | head -1'" % (HOST, jid), check=False)
        state = st.stdout.strip().split()[-1] if st.stdout.strip() else "UNKNOWN"
    ok = sh("ssh %s 'grep -c \"SMOKE OK\" zoo221/capsule/logs/smoke_%s.out'" % (HOST, jid), check=False)
    if "1" not in ok.stdout:
        raise SystemExit("smoke did not pass (state=%s) — refusing production submit" % state)
    print("smoke OK")

    # production array
    r = sh("ssh %s 'cd zoo221/capsule && sbatch --parsable hpc/qd_generation.sbatch'" % HOST)
    print("PRODUCTION ARRAY SUBMITTED:", r.stdout.strip())


if __name__ == "__main__":
    main()
