"""AMEND-3 campaign driver: freeze the amend-3 manifest, sync to LUNARC,
smoke, submit the production array, and chain the aggregate after it.

Sequence (run from the Mac worktree, over the billy-laptop LUNARC relay if
direct ssh is broken):
  1. write manifests/CAMPAIGN_AMEND3_MANIFEST.json (frozen task list;
     sha256 of FREEZE_V1_AMEND_3.json + the whole ancestor chain + capsule
     code + census truth receipt heads; never rewritten in place)
  2. rsync capsule to <lunarc>:$HOME/zoo221/capsule (binary-safe)
  3. sbatch smoke_amend3 (--qos=test) and require "SMOKE OK"
  4. sbatch qd_amend3 array (production; %8 concurrency cap)
  5. sbatch aggregate_amend3 with --dependency=afterok:<array>

Usage: python3 submit_amend3.py <capsule_root> <lunarc_host>
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
    with open(os.path.join(ROOT, "FREEZE_V1_AMEND_3.json")) as f:
        a3 = json.load(f)
    arms = [a["arm_id"] for a in a3["arms_amend3"]["arms"]]
    seeds = a3["arms_amend3"]["seeds"]
    budget = a3["arms_amend3"]["budget"]
    tasks = [{"task_id": i, "arm": arm, "seed": seed, "budget": budget}
             for i, (arm, seed) in enumerate(
                 (arm, seed) for arm in arms for seed in seeds)]
    p00c_head = json.load(open(
        os.path.join(ROOT, "archives", "CENSUS_P00C_TRUTH.json"))
    )["summary"]["receipt_head"]
    p00b_head = json.load(open(
        os.path.join(ROOT, "archives", "CENSUS_P00B_TRUTH.json"))
    )["summary"]["receipt_head"]
    manifest = {
        "manifest_id": "CAMPAIGN_AMEND3_V1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tasks": tasks,
        "n_tasks": len(tasks),
        "amendment_id": a3["amendment_id"],
        "amendment_sha256": hashlib.sha256(
            open(os.path.join(ROOT, "FREEZE_V1_AMEND_3.json"), "rb").read()).hexdigest(),
        "amend_2_sha256": hashlib.sha256(
            open(os.path.join(ROOT, "FREEZE_V1_AMEND_2.json"), "rb").read()).hexdigest(),
        "amend_1_sha256": hashlib.sha256(
            open(os.path.join(ROOT, "FREEZE_V1_AMEND_1.json"), "rb").read()).hexdigest(),
        "freeze_v1_sha256": a3["freeze_v1_sha256"],
        "code_sha256": code_digest(),
        "truth_p00c_receipt_head": p00c_head,
        "truth_p00b_receipt_head": p00b_head,
    }
    mpath = os.path.join(ROOT, "manifests", "CAMPAIGN_AMEND3_MANIFEST.json")
    scored = [f for f in os.listdir(os.path.join(ROOT, "results"))
              if f.startswith("QDA3_") and f.endswith(".status")]
    if os.path.exists(mpath):
        old = json.load(open(mpath))
        if old["tasks"] != tasks:
            raise SystemExit("frozen manifest TASK LIST differs — write a "
                             "numbered amendment instead of overwriting")
        if old["code_sha256"] != manifest["code_sha256"]:
            if scored:
                raise SystemExit("code changed AFTER scored amend-3 runs "
                                 "exist — numbered amendment required")
            manifest["supersedes_manifest_sha256"] = hashlib.sha256(
                open(mpath, "rb").read()).hexdigest()
            manifest["refreeze_reason"] = (
                "supersession refreeze after pre-scoring code fixes; no "
                "scored amend-3 runs exist")
            with open(mpath, "w") as f:
                json.dump(manifest, f, indent=1)
            print("amend-3 manifest RE-FROZEN pre-scoring (code fix)")
    else:
        with open(mpath, "w") as f:
            json.dump(manifest, f, indent=1)
    print("amend-3 manifest frozen: %d tasks" % len(tasks))

    # binary-safe sync (rsync, never ssh pipes) + checksum verification
    sh("ssh %s 'mkdir -p zoo221/capsule'" % HOST)
    sh("rsync -a --delete --exclude __pycache__ --exclude .pytest_cache "
       "--exclude logs --exclude .DS_Store %s/ %s:zoo221/capsule/" % (ROOT, HOST))
    sh("cd %s && find . \\( -name '*.py' -o -name '*.json' \\) | LC_ALL=C sort | "
       "xargs sha256sum > /tmp/zoo_a3_local.list" % ROOT)
    sh("ssh %s \"cd zoo221/capsule && find . \\\\( -name '*.py' -o -name '*.json' \\\\) | "
       "LC_ALL=C sort | xargs sha256sum > /tmp/zoo_a3_remote.list\"" % HOST)
    sh("scp -q %s:/tmp/zoo_a3_remote.list /tmp/zoo_a3_remote.list.local" % HOST)
    diff = sh("diff /tmp/zoo_a3_local.list /tmp/zoo_a3_remote.list.local", check=False)
    if diff.returncode != 0:
        print(diff.stdout[-3000:])
        raise SystemExit("capsule checksum mismatch after rsync (listing above)")
    chk = sh("sha256sum /tmp/zoo_a3_local.list | cut -d' ' -f1").stdout.strip()
    print("capsule synced byte-identical, listing digest %s" % chk[:16])

    # smoke first (--qos=test only for short smoke jobs)
    r = sh("ssh %s 'cd zoo221/capsule && sbatch --parsable hpc/smoke_amend3.sbatch'" % HOST)
    jid = r.stdout.strip().splitlines()[-1]
    print("smoke job %s submitted; waiting" % jid)
    state = "PENDING"
    while state in ("PENDING", "RUNNING", "COMPLETING", "REQUEUED"):
        time.sleep(20)
        st = sh("ssh %s 'sacct -j %s -n -o State%%30 | head -1'" % (HOST, jid), check=False)
        state = st.stdout.strip().split()[-1] if st.stdout.strip() else "UNKNOWN"
    ok = sh("ssh %s 'grep -c \"SMOKE OK\" zoo221/capsule/logs/smoke_a3_%s.out'" % (HOST, jid), check=False)
    if "1" not in ok.stdout:
        raise SystemExit("amend-3 smoke did not pass (state=%s) — refusing production submit" % state)
    print("smoke OK")

    # production array + chained aggregate
    r = sh("ssh %s 'cd zoo221/capsule && sbatch --parsable hpc/qd_amend3.sbatch'" % HOST)
    aid = r.stdout.strip().splitlines()[-1]
    print("PRODUCTION ARRAY SUBMITTED:", aid)
    r = sh("ssh %s 'cd zoo221/capsule && sbatch --parsable --dependency=afterok:%s "
           "hpc/aggregate_amend3.sbatch'" % (HOST, aid))
    print("AGGREGATE CHAINED:", r.stdout.strip())


if __name__ == "__main__":
    main()
