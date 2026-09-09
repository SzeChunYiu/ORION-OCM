"""AMEND-5 campaign driver: freeze the amend-5 manifest, sync to LUNARC,
smoke, submit the production array (quality-gated D-archive admission), and
chain the aggregate after it.

Sequence (run from the Mac worktree):
  0. gate: FREEZE_V1_AMEND_5.json exists (tool-stamped created_utc), the sha
     chain V1->A1->A2->A3->A4->A5 is intact (A4 bound to the merged-main
     freeze b51a9959...), archives/GATE_CEILING_TRUTH.json is present with
     every xcheck true, and the frozen bar == the ladder choice whose
     ceilings keep the 0.25 terminal bar reachable on both gated axes
  1. write manifests/CAMPAIGN_AMEND5_MANIFEST.json (frozen 12-task list:
     4 arms x 3 seeds; never rewritten in place once scored runs exist)
  2. rsync capsule to <lunarc>:$HOME/zoo221/capsule (binary-safe) with a
     sha256 listing diff gate
  3. sbatch smoke_amend5 (--qos=test) and require "SMOKE OK"
  4. sbatch qd_amend5 array (production; %8 concurrency cap)
  5. sbatch aggregate_amend5 with --dependency=afterok:<array>

Usage: python3 submit_amend5.py <capsule_root> <lunarc_host>
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
# Relay mode quotes the command TWICE so the laptop's shell re-parse strips
# exactly one layer: metacharacters (&& | >) must execute on LUNARC, never
# on the relay (verified live: single quoting runs && on the laptop).
_probe = subprocess.run("ssh -o ConnectTimeout=15 -o BatchMode=yes %s echo ok"
                        % HOST, shell=True, capture_output=True, text=True)
RELAY = None if _probe.returncode == 0 else "billy-laptop"


def lun(cmd: str, check: bool = True):
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
    # ---- gate 0: amendment + GATE-CEILING truth ------------------------
    fpath = os.path.join(ROOT, "FREEZE_V1_AMEND_5.json")
    if not os.path.exists(fpath):
        raise SystemExit("FREEZE_V1_AMEND_5.json missing — run "
                         "hpc/freeze_amend5.py after the gate-ceiling job")
    with open(fpath) as f:
        a5 = json.load(f)
    if "freeze_amend5.py" not in a5["created_utc_by"]:
        raise SystemExit("created_utc not tool-stamped — refusing (amend-3 "
                         "timing-erratum pattern)")
    for fn, key in (("FREEZE_V1.json", "freeze_v1_sha256"),
                    ("FREEZE_V1_AMEND_1.json", "amend_1_sha256"),
                    ("FREEZE_V1_AMEND_2.json", "amend_2_sha256"),
                    ("FREEZE_V1_AMEND_3.json", "amend_3_sha256"),
                    ("FREEZE_V1_AMEND_4.json", "amend_4_sha256")):
        d = hashlib.sha256(open(os.path.join(ROOT, fn), "rb").read()).hexdigest()
        if d != a5[key]:
            raise SystemExit("%s does not match the amend-5 chain" % fn)
    if not a5["amend_4_sha256"].startswith("b51a9959"):
        raise SystemExit("A4 sha is not the merged-main freeze (b51a9959...)")
    gc_path = os.path.join(ROOT, "archives", "GATE_CEILING_TRUTH.json")
    if not os.path.exists(gc_path):
        raise SystemExit("archives/GATE_CEILING_TRUTH.json missing — run the "
                         "gate-ceiling census job BEFORE submitting")
    gc = json.load(open(gc_path))["summary"]
    for k, v in gc["xcheck_vs_P00C_HZD9"].items():
        if isinstance(v, bool) and v is not True:
            raise SystemExit("GATE-CEILING xcheck %s false — census not "
                             "deterministic" % k)
    qg = a5["quality_gate_amend5"]
    if qg["ceiling_ladder"] != gc["ladder"]:
        raise SystemExit("freeze ladder != GATE-CEILING truth ladder")
    chosen = gc["ladder"][qg["admission_bar_quantile"]]
    if qg["admission_bar"] != chosen["bar"]:
        raise SystemExit("frozen bar != ladder choice")
    if not (chosen["ceil_D2d_recovery"] >= 0.25
            and chosen["ceil_D3d_recovery"] >= 0.25):
        raise SystemExit("chosen bar leaves 0.25 unreachable — refreeze")

    # ---- gate 1: frozen manifest --------------------------------------
    arms = a5["arms_amend5"]["arms"]
    seeds = a5["arms_amend5"]["seeds"]
    budget = a5["arms_amend5"]["budget"]
    tasks = [{"task_id": i, "arm": a["arm_id"], "seed": s,
              "gated": bool(a["gated"]), "budget": budget,
              "admission_bar": qg["admission_bar"] if a["gated"] else None,
              "worker": "hpc/qd_run_amend5.py"}
             for i, (a, s) in enumerate((a, s) for a in arms for s in seeds)]
    p00c_head = json.load(open(
        os.path.join(ROOT, "archives", "CENSUS_P00C_TRUTH.json"))
    )["summary"]["receipt_head"]
    manifest = {
        "manifest_id": "CAMPAIGN_AMEND5_V1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tasks": tasks,
        "n_tasks": len(tasks),
        "amendment_id": a5["amendment_id"],
        "amendment_sha256": hashlib.sha256(open(fpath, "rb").read()).hexdigest(),
        "amend_4_sha256": a5["amend_4_sha256"],
        "amend_3_sha256": a5["amend_3_sha256"],
        "amend_2_sha256": a5["amend_2_sha256"],
        "amend_1_sha256": a5["amend_1_sha256"],
        "freeze_v1_sha256": a5["freeze_v1_sha256"],
        "code_sha256": code_digest(),
        "truth_p00c_receipt_head": p00c_head,
        "truth_gate_ceiling_receipt_head": gc["receipt_head"],
        "admission_bar": qg["admission_bar"],
        "admission_bar_quantile": qg["admission_bar_quantile"],
    }
    mpath = os.path.join(ROOT, "manifests", "CAMPAIGN_AMEND5_MANIFEST.json")
    scored = [f for f in os.listdir(os.path.join(ROOT, "results"))
              if f.startswith("QDA5_") and f.endswith(".status")]
    if os.path.exists(mpath):
        old = json.load(open(mpath))
        if old["tasks"] != tasks:
            raise SystemExit("frozen manifest TASK LIST differs — write a "
                             "numbered amendment instead of overwriting")
        if old["code_sha256"] != manifest["code_sha256"]:
            if scored:
                raise SystemExit("code changed AFTER scored amend-5 runs "
                                 "exist — numbered amendment required")
            manifest["supersedes_manifest_sha256"] = hashlib.sha256(
                open(mpath, "rb").read()).hexdigest()
            manifest["refreeze_reason"] = (
                "supersession refreeze after a pre-scoring code fix; no "
                "scored amend-5 result existed (asserted)")
            with open(mpath, "w") as f:
                json.dump(manifest, f, indent=1)
            print("amend-5 manifest RE-FROZEN pre-scoring (code fix)")
    else:
        with open(mpath, "w") as f:
            json.dump(manifest, f, indent=1)
    print("amend-5 manifest frozen: %d tasks" % len(tasks))

    # ---- gate 2: binary-safe sync + checksum verification ------------
    lun("mkdir -p zoo221/capsule")
    rsync_e = "" if RELAY is None else '-e "ssh %s ssh" ' % RELAY
    sh("rsync -a %s--delete --exclude __pycache__ --exclude .pytest_cache "
       "--exclude logs --exclude .DS_Store %s/ %s:zoo221/capsule/"
       % (rsync_e, ROOT, HOST))
    sh("cd %s && find . \\( -name '*.py' -o -name '*.json' \\) | LC_ALL=C sort | "
       "xargs sha256sum > /tmp/zoo_a5_local.list" % ROOT)
    lun("cd zoo221/capsule && find . \\( -name '*.py' -o -name '*.json' \\) | "
        "LC_ALL=C sort | xargs sha256sum > /tmp/zoo_a5_remote.list")
    if RELAY is None:
        sh("scp -q %s:/tmp/zoo_a5_remote.list /tmp/zoo_a5_remote.list.local" % HOST)
    else:  # two text hops: lunarc -> laptop -> Mac (files are checksummed)
        sh("ssh %s 'scp -q %s:/tmp/zoo_a5_remote.list /tmp/zoo_a5_remote.list'"
           % (RELAY, HOST))
        sh("scp -q %s:/tmp/zoo_a5_remote.list /tmp/zoo_a5_remote.list.local" % RELAY)
    diff = sh("diff /tmp/zoo_a5_local.list /tmp/zoo_a5_remote.list.local", check=False)
    if diff.returncode != 0:
        print(diff.stdout[-3000:])
        raise SystemExit("capsule checksum mismatch after rsync (listing above)")
    chk = sh("sha256sum /tmp/zoo_a5_local.list | cut -d' ' -f1").stdout.strip()
    print("capsule synced byte-identical, listing digest %s" % chk[:16])

    # ---- gate 3: smoke first ------------------------------------------
    r = lun("cd zoo221/capsule && sbatch --parsable hpc/smoke_amend5.sbatch")
    jid = r.stdout.strip().splitlines()[-1]
    print("smoke job %s submitted; waiting" % jid)
    state = "PENDING"
    while state in ("PENDING", "RUNNING", "COMPLETING", "REQUEUED"):
        time.sleep(20)
        st = lun("sacct -j %s -n -o State%%30 | head -1" % jid, check=False)
        state = st.stdout.strip().split()[-1] if st.stdout.strip() else "UNKNOWN"
    ok = lun("grep -c \"SMOKE OK\" zoo221/capsule/logs/smoke_a5_%s.out" % jid,
             check=False)
    if "1" not in ok.stdout:
        raise SystemExit("amend-5 smoke did not pass (state=%s) — refusing "
                         "production submit" % state)
    print("smoke OK")

    # ---- gate 4: production array + chained aggregate -----------------
    r = lun("cd zoo221/capsule && sbatch --parsable hpc/qd_amend5.sbatch")
    aid = r.stdout.strip().splitlines()[-1]
    print("PRODUCTION ARRAY SUBMITTED:", aid)
    r = lun("cd zoo221/capsule && sbatch --parsable --dependency=afterok:%s "
            "hpc/aggregate_amend5.sbatch" % aid)
    print("AGGREGATE CHAINED:", r.stdout.strip())


if __name__ == "__main__":
    main()
