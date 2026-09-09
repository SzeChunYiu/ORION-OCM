"""AMEND-4 campaign driver: freeze the amend-4 manifest, sync to LUNARC,
smoke, submit the production array (MZ-D8 islands + MZ-D9 recompute), and
chain the aggregate after it.

Sequence (run from the Mac worktree):
  0. gate: FREEZE_V1_AMEND_4.json exists (tool-stamped created_utc), the
     sha chain V1->A1->A2->A3->A4 is intact, and archives/HZD9_TRUTH.json is
     present with every P00C xcheck true (unscored truth precedes the freeze,
     the freeze precedes every scored run)
  1. write manifests/CAMPAIGN_AMEND4_MANIFEST.json (frozen 21-task list:
     2 island arms x 3 seeds + 5 amend-3 arms x 3 seeds; never rewritten in
     place once scored runs exist)
  2. rsync capsule to <lunarc>:$HOME/zoo221/capsule (binary-safe) with a
     sha256 listing diff gate
  3. sbatch smoke_amend4 (--qos=test) and require "SMOKE OK"
  4. sbatch qd_amend4 array (production; %8 concurrency cap)
  5. sbatch aggregate_amend4 with --dependency=afterok:<array>

Usage: python3 submit_amend4.py <capsule_root> <lunarc_host>
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time

ROOT, HOST = sys.argv[1], sys.argv[2]
import shlex  # noqa: E402


def sh(cmd: str, check: bool = True):
    print("+ %s" % cmd, flush=True)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.strip()[-2000:])
    if r.returncode != 0 and check:
        print(r.stderr.strip()[-2000:])
        raise SystemExit("command failed: %s" % cmd)
    return r


# LUNARC requires keyboard-interactive 2FA from the Mac; when the direct
# ProxyJump is unavailable, every remote op goes through the billy-laptop
# ControlMaster relay (binary-safe: rsync -e double-hop, never ssh pipes).
_probe = subprocess.run("ssh -o ConnectTimeout=15 -o BatchMode=yes %s echo ok"
                        % HOST, shell=True, capture_output=True, text=True)
RELAY = None if _probe.returncode == 0 else "billy-laptop"


def lun(cmd: str, check: bool = True):
    """Run cmd on LUNARC (direct, or through the laptop relay).  Relay mode
    quotes TWICE: the command string is re-parsed by the laptop's shell before
    reaching lunarc's shell, so a single quote layer is stripped en route and
    operators like && / | / () would execute on the RELAY instead."""
    if RELAY is None:
        return sh("ssh %s %s" % (HOST, shlex.quote(cmd)), check)
    return sh("ssh %s ssh %s %s" % (RELAY, HOST, shlex.quote(shlex.quote(cmd))),
              check)


def code_digest() -> str:
    h = hashlib.sha256()
    for d in ("morphology", "evaluation", "search", "hpc"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".py"):
                h.update(open(os.path.join(ROOT, d, fn), "rb").read())
    return h.hexdigest()


def main():
    # ---- gate 0: amendment + HZD9 truth ------------------------------
    fpath = os.path.join(ROOT, "FREEZE_V1_AMEND_4.json")
    if not os.path.exists(fpath):
        raise SystemExit("FREEZE_V1_AMEND_4.json missing — run "
                         "hpc/freeze_amend4.py after the HZD9 census job")
    with open(fpath) as f:
        a4 = json.load(f)
    if "freeze_amend4.py" not in a4["created_utc_by"]:
        raise SystemExit("created_utc not tool-stamped — refusing (amend-3 "
                         "timing-erratum pattern)")
    for fn, key in (("FREEZE_V1.json", "freeze_v1_sha256"),
                    ("FREEZE_V1_AMEND_1.json", "amend_1_sha256"),
                    ("FREEZE_V1_AMEND_2.json", "amend_2_sha256"),
                    ("FREEZE_V1_AMEND_3.json", "amend_3_sha256")):
        d = hashlib.sha256(open(os.path.join(ROOT, fn), "rb").read()).hexdigest()
        if d != a4[key]:
            raise SystemExit("%s does not match the amend-4 chain" % fn)
    hz_path = os.path.join(ROOT, "archives", "HZD9_TRUTH.json")
    if not os.path.exists(hz_path):
        raise SystemExit("archives/HZD9_TRUTH.json missing — run the HZD9 "
                         "census job and pull the truth BEFORE submitting")
    hz = json.load(open(hz_path))["summary"]
    for k, v in hz["xcheck_vs_P00C"].items():
        if isinstance(v, bool):
            if v is not True:
                raise SystemExit("HZD9 xcheck %s false — census not "
                                 "deterministic" % k)
    if a4["quality_bar_T2"] != hz["quality_bar_T2"]:
        raise SystemExit("A4 quality bar != HZD9 truth quality bar")

    # ---- gate 1: frozen manifest -------------------------------------
    islands = a4["arms_amend4"]["island_arms"]
    hz_arms = a4["arms_amend4"]["hzd9_recompute_arms"]
    seeds = a4["arms_amend4"]["seeds"]
    budget = a4["arms_amend4"]["budget"]
    tasks = ([{"task_id": i, "kind": "islands", "arm": a["arm_id"],
               "seed": s, "budget": budget, "worker": "hpc/qd_run_amend4.py"}
              for i, (a, s) in enumerate((a, s) for a in islands
                                         for s in seeds)]
             + [{"task_id": 6 + i, "kind": "hzd9r", "arm": arm, "seed": s,
                 "budget": None, "worker": "hpc/hzd9_recompute.py"}
                for i, (arm, s) in enumerate((arm, s) for arm in hz_arms
                                             for s in seeds)])
    p00c_head = json.load(open(
        os.path.join(ROOT, "archives", "CENSUS_P00C_TRUTH.json"))
    )["summary"]["receipt_head"]
    p00b_head = json.load(open(
        os.path.join(ROOT, "archives", "CENSUS_P00B_TRUTH.json"))
    )["summary"]["receipt_head"]
    manifest = {
        "manifest_id": "CAMPAIGN_AMEND4_V1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tasks": tasks,
        "n_tasks": len(tasks),
        "amendment_id": a4["amendment_id"],
        "amendment_sha256": hashlib.sha256(open(fpath, "rb").read()).hexdigest(),
        "amend_3_sha256": hashlib.sha256(
            open(os.path.join(ROOT, "FREEZE_V1_AMEND_3.json"), "rb").read()
        ).hexdigest(),
        "amend_2_sha256": hashlib.sha256(
            open(os.path.join(ROOT, "FREEZE_V1_AMEND_2.json"), "rb").read()
        ).hexdigest(),
        "amend_1_sha256": hashlib.sha256(
            open(os.path.join(ROOT, "FREEZE_V1_AMEND_1.json"), "rb").read()
        ).hexdigest(),
        "freeze_v1_sha256": a4["freeze_v1_sha256"],
        "code_sha256": code_digest(),
        "truth_p00c_receipt_head": p00c_head,
        "truth_p00b_receipt_head": p00b_head,
        "truth_hz9_receipt_head": hz["receipt_head"],
        "quality_bar_T2": hz["quality_bar_T2"],
    }
    mpath = os.path.join(ROOT, "manifests", "CAMPAIGN_AMEND4_MANIFEST.json")
    scored = [f for f in os.listdir(os.path.join(ROOT, "results"))
              if (f.startswith("QDA4_") or f.startswith("HZD9R_"))
              and f.endswith(".status")]
    if os.path.exists(mpath):
        old = json.load(open(mpath))
        if old["tasks"] != tasks:
            raise SystemExit("frozen manifest TASK LIST differs — write a "
                             "numbered amendment instead of overwriting")
        if old["code_sha256"] != manifest["code_sha256"]:
            if scored:
                raise SystemExit("code changed AFTER scored amend-4 runs "
                                 "exist — numbered amendment required")
            manifest["supersedes_manifest_sha256"] = hashlib.sha256(
                open(mpath, "rb").read()).hexdigest()
            manifest["refreeze_reason"] = (
                "supersession refreeze after pre-scoring code fix: island "
                "worker read migration_interval_rounds from the wrong A4 "
                "block (array 3587115: 6 island tasks failed at 0 s before "
                "writing any result; the 15 hzd9r results of that failed "
                "array were purged and are regenerated deterministically on "
                "resubmit; no aggregate ever consumed them)")
            with open(mpath, "w") as f:
                json.dump(manifest, f, indent=1)
            print("amend-4 manifest RE-FROZEN pre-scoring (code fix)")
    else:
        with open(mpath, "w") as f:
            json.dump(manifest, f, indent=1)
    print("amend-4 manifest frozen: %d tasks" % len(tasks))

    # ---- gate 2: binary-safe sync + checksum verification ------------
    lun("mkdir -p zoo221/capsule")
    rsync_e = "" if RELAY is None else '-e "ssh %s ssh" ' % RELAY
    sh("rsync -a %s--delete --exclude __pycache__ --exclude .pytest_cache "
       "--exclude logs --exclude .DS_Store %s/ %s:zoo221/capsule/"
       % (rsync_e, ROOT, HOST))
    sh("cd %s && find . \\( -name '*.py' -o -name '*.json' \\) | LC_ALL=C sort | "
       "xargs sha256sum > /tmp/zoo_a4_local.list" % ROOT)
    lun("cd zoo221/capsule && find . \\( -name '*.py' -o -name '*.json' \\) | "
        "LC_ALL=C sort | xargs sha256sum > /tmp/zoo_a4_remote.list")
    if RELAY is None:
        sh("scp -q %s:/tmp/zoo_a4_remote.list /tmp/zoo_a4_remote.list.local" % HOST)
    else:  # two text hops: lunarc -> laptop -> Mac (files are checksummed)
        sh("ssh %s 'scp -q %s:/tmp/zoo_a4_remote.list /tmp/zoo_a4_remote.list'"
           % (RELAY, HOST))
        sh("scp -q %s:/tmp/zoo_a4_remote.list /tmp/zoo_a4_remote.list.local" % RELAY)
    diff = sh("diff /tmp/zoo_a4_local.list /tmp/zoo_a4_remote.list.local", check=False)
    if diff.returncode != 0:
        print(diff.stdout[-3000:])
        raise SystemExit("capsule checksum mismatch after rsync (listing above)")
    chk = sh("sha256sum /tmp/zoo_a4_local.list | cut -d' ' -f1").stdout.strip()
    print("capsule synced byte-identical, listing digest %s" % chk[:16])

    # ---- gate 3: smoke first ------------------------------------------
    r = lun("cd zoo221/capsule && sbatch --parsable hpc/smoke_amend4.sbatch")
    jid = r.stdout.strip().splitlines()[-1]
    print("smoke job %s submitted; waiting" % jid)
    state = "PENDING"
    while state in ("PENDING", "RUNNING", "COMPLETING", "REQUEUED"):
        time.sleep(20)
        st = lun("sacct -j %s -n -o State%%30 | head -1" % jid, check=False)
        state = st.stdout.strip().split()[-1] if st.stdout.strip() else "UNKNOWN"
    ok = lun("grep -c \"SMOKE OK\" zoo221/capsule/logs/smoke_a4_%s.out" % jid,
             check=False)
    if "1" not in ok.stdout:
        raise SystemExit("amend-4 smoke did not pass (state=%s) — refusing production submit" % state)
    print("smoke OK")

    # ---- gate 4: production array + chained aggregate -----------------
    r = lun("cd zoo221/capsule && sbatch --parsable hpc/qd_amend4.sbatch")
    aid = r.stdout.strip().splitlines()[-1]
    print("PRODUCTION ARRAY SUBMITTED:", aid)
    r = lun("cd zoo221/capsule && sbatch --parsable --dependency=afterok:%s "
            "hpc/aggregate_amend4.sbatch" % aid)
    print("AGGREGATE CHAINED:", r.stdout.strip())


if __name__ == "__main__":
    main()
