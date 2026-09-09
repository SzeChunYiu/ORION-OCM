#!/usr/bin/env python3
"""GS-R1 campaign driver (#221 sec 18, GS-R1h adaptive protocol) —
code sync -> env probe (scoring host) -> freeze -> manifest -> smoke ->
production arrays -> HOURLY checkpoint chain -> chained aggregate.

Runs on the Mac mini (git/gh host).  ALL execution happens elsewhere:
tests run on billy-laptop; probe/freeze/manifest are light (seconds) on
the LUNARC login node; scoring arrays on LUNARC compute (reached via the
billy-laptop relay when direct ssh is unavailable).  Binary-safe
transfers only (rsync + sha256/md5 verify; never cat|ssh pipes).

Usage:
  submit_gs.py ROOT HOST [--dry]            full campaign
  submit_gs.py ROOT HOST --checkpoint       force one checkpoint now,
                                            print results/GS_R1_STATUS.json
  submit_gs.py ROOT HOST --batch SPEC.json  adaptive batch (GS-R1h):
                                            ledger BEFORE sbatch, spec
                                            files under
                                            manifests/GS_R1_BATCH_<id>/
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import time

ROOT = os.path.abspath(sys.argv[1])
HOST = sys.argv[2] if len(sys.argv) > 2 else "lunarc"
DRY = "--dry" in sys.argv
MODE = ("batch" if "--batch" in sys.argv else
        "checkpoint" if "--checkpoint" in sys.argv else "campaign")
BATCH_SPEC = (sys.argv[sys.argv.index("--batch") + 1]
              if MODE == "batch" else None)
LAPTOP = "billy-laptop"
LAPTOP_DIR = "pmci-gs/capsule"
REMOTE_ROOT = "$HOME/zoo221/gs"
SEARCH_ARMS = ["GSA1_units", "GSA2_hetero", "GSA3_farch", "GSA4_obasis",
               "GSA5_surrogate", "GSR_random_control"]
SEEDS = list(range(6))
N_SWEEP_SHARDS = 288
# partition/account priority (operator directive): nuc, then lu48, then hep
PLACEMENT = [("nuc", "lu2026-2-51"), ("lu48", "lu2026-2-51"),
             ("hep", "hep2023-1-3")]
LEDGER = "ADAPTIVITY_LEDGER.jsonl"  # capsule ROOT, append-only
# freeze inputs that live under results/ (baselines + reuse measurement):
# shipped to every host; all OTHER results/ files stay host-local (the
# refusal guards assert no scored GS artifacts travel)
RSYNC_FILTERS = [
    "--include=results/AGGREGATE_AMEND*.json",
    "--include=results/REUSE_VECTORIZE_MEASUREMENT.json",
    "--exclude=results/*", "--exclude=archives/", "--exclude=logs/",
    "--exclude=manifests/receipts/", "--exclude=__pycache__/",
]

_probe = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o",
                         "ConnectTimeout=8", HOST, "true"],
                         capture_output=True)
RELAY = None if _probe.returncode == 0 else LAPTOP


def sh(cmd: str, via_relay_lunarc: bool = False, check: bool = True):
    """Run cmd.  Direct locally; via laptop for LUNARC when relayed."""
    if via_relay_lunarc and RELAY:
        cmd = "ssh %s ssh %s %s" % (RELAY, HOST,
                                    shlex.quote(shlex.quote(cmd)))
    elif via_relay_lunarc:
        cmd = "ssh %s %s" % (HOST, shlex.quote(cmd))
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise SystemExit("FAILED [%s]: %s\n%s" % (cmd, p.stdout[-800:],
                                                 p.stderr[-800:]))
    return p.stdout.strip()


def laptop(cmd: str, check: bool = True):
    p = subprocess.run(["ssh", LAPTOP, cmd], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise SystemExit("LAPTOP FAILED [%s]: %s\n%s" % (
            cmd, p.stdout[-800:], p.stderr[-800:]))
    return p.stdout.strip()


def gate(msg: str) -> None:
    print("\n=== %s" % msg)


def remote_md5(path: str) -> str:
    return sh("md5sum %s | awk '{print $1}'" % path,
              via_relay_lunarc=True).split()[0]


def local_md5(path: str) -> str:
    return subprocess.run(["md5", "-q", path],
                          capture_output=True, text=True).stdout.strip()


def ledger_append(line: dict) -> None:
    """Append one JSON line to ROOT/ADAPTIVITY_LEDGER.jsonl on LUNARC.
    printf with a pre-quoted arg (heredocs through the relay are fragile)."""
    sh("printf '%%s\\n' %s >> %s/%s"
        % (shlex.quote(json.dumps(line, sort_keys=True)), REMOTE_ROOT,
           LEDGER), via_relay_lunarc=True)


# ---------------------------------------------------------------- batch
def validate_batch_spec(spec: dict) -> None:
    for k in ("batch_id", "rationale", "checkpoint_consumed", "tasks"):
        assert k in spec, "batch spec missing %s" % k
    assert isinstance(spec["tasks"], list) and spec["tasks"], "no tasks"
    seen = set()
    for t in spec["tasks"]:
        tid = t.get("task_id")
        assert tid and re.fullmatch(r"[A-Za-z0-9_]+", tid), \
            "bad task_id %r" % tid
        assert tid not in seen, "duplicate task_id %s" % tid
        seen.add(tid)
        assert not re.match(r"GSA[1-5]_|GSR_|GSE_", tid), \
            "task_id %s collides with frozen array id space" % tid
        if t.get("kind", "search") == "search":
            assert t.get("base_arm") in SEARCH_ARMS, \
                "base_arm %r not a frozen search arm" % t.get("base_arm")
        else:
            assert int(t["shard"]) >= 0 and int(t["n_shards"]) > 0
        frozen = {"eta", "insurance_fraction", "gates", "terminal_rules",
                  "t3_key", "freeze"}
        bad = frozen & set(t)
        assert not bad, "batch task touches frozen keys: %s" % bad


def run_batch() -> None:
    """GS-R1h adaptive batch: validate -> sync spec -> LEDGER DECISION LINE
    (before any sbatch) -> per-task sbatch -> LEDGER SUBMISSION LINE."""
    spec = json.load(open(BATCH_SPEC))
    validate_batch_spec(spec)
    fsha = sh("sha256sum %s/GRAND_SEARCH_R1_FREEZE.json | awk '{print $1}'"
              % REMOTE_ROOT, via_relay_lunarc=True)
    assert len(fsha) == 64, "freeze not found on %s" % HOST
    bid = spec["batch_id"]
    gate("batch %s (%d tasks) -> %s" % (bid, len(spec["tasks"]), HOST))
    # ship the full decision record + per-task specs
    rdir = "%s/manifests/GS_R1_BATCH_%s" % (REMOTE_ROOT, bid)
    sh("mkdir -p %s" % rdir, via_relay_lunarc=True)
    tmp = "/tmp/gs_batch_%d.json" % int(time.time())
    with open(tmp, "w") as fh:
        json.dump(spec, fh, indent=1, sort_keys=True)
    rsync_e = "" if RELAY is None else '-e "ssh %s ssh" ' % RELAY
    r = subprocess.run('rsync -a %s"%s" %s:%s/manifests/GS_R1_BATCH_%s.json'
                       % (rsync_e, tmp, HOST, REMOTE_ROOT, bid),
                       shell=True, capture_output=True, text=True)
    assert r.returncode == 0, "rsync batch record failed: %s" % r.stderr
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for t in spec["tasks"]:
        ts = dict(t)
        ts.update({"schema": "GS_R1_BATCH_TASK_V1", "batch_id": bid,
                   "created_utc": now, "freeze_sha256": fsha})
        with open(tmp, "w") as fh:
            json.dump(ts, fh, indent=1, sort_keys=True)
        r = subprocess.run(
            'rsync -a %s"%s" %s:%s/%s.json'
            % (rsync_e, tmp, HOST, rdir, t["task_id"]),
            shell=True, capture_output=True, text=True)
        assert r.returncode == 0, "rsync task spec failed: %s" % r.stderr
    os.unlink(tmp)
    # ledger DECISION line — durably on disk BEFORE any sbatch
    ledger_append({
        "schema": "GS_R1_ADAPTIVITY_V1", "event": "decision",
        "ts": now, "batch_id": bid,
        "checkpoint_consumed": spec["checkpoint_consumed"],
        "rationale": spec["rationale"],
        "n_tasks": len(spec["tasks"]), "tasks": spec["tasks"],
        "job_ids": None, "submitted": False,
    })
    # place + submit each task
    part, acct = resolve_placement()
    stop_ts = sh("python3 -c \"import json;print(json.load(open('%s/manifests/"
                 "GS_R1_TASKS.json'))['stop_ts'])\"" % REMOTE_ROOT,
                 via_relay_lunarc=True).strip()
    jids = []
    for t in spec["tasks"]:
        spec_rel = "manifests/GS_R1_BATCH_%s/%s.json" % (bid, t["task_id"])
        out = sh("cd %s && sbatch -p %s -A %s -t 04:00:00 -c 1 "
                 "--export=ALL,ZOO_ROOT=%s,GS_BATCH_SPEC=%s,"
                 "GS_FREEZE_SHA=%s,GS_STOP_TS=%s "
                 "hpc/batch_task.sbatch"
                 % (REMOTE_ROOT, part, acct, REMOTE_ROOT, spec_rel, fsha,
                    stop_ts),
                 via_relay_lunarc=True, check=False)
        jm = re.search(r"(?:^|\s)(\d+)$", out.strip())
        assert jm, "batch task %s submission failed: %s" % (t["task_id"],
                                                            out[-300:])
        jids.append(jm.group(1))
        print("batch task %s -> job %s (%s/%s)" % (t["task_id"], jm.group(1),
                                                   part, acct))
    ledger_append({
        "schema": "GS_R1_ADAPTIVITY_V1", "event": "submitted",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "batch_id": bid, "job_ids": jids, "submitted": True,
        "placement": [part, acct],
    })
    print(json.dumps({"batch_id": bid, "job_ids": jids,
                      "placement": [part, acct], "ledger": LEDGER},
                     indent=1))


def resolve_placement():
    """First (partition, account) that accepts a test-only submit; falls
    back to sinfo partition state when --test-only is unavailable."""
    for part, acct in PLACEMENT:
        out = sh("cd %s && sbatch --test-only -p %s -A %s -t 04:00:00 "
                 "hpc/grand_search.sbatch 2>&1 | head -2"
                 % (REMOTE_ROOT, part, acct), via_relay_lunarc=True,
                 check=False)
        if "invalid" not in out.lower() and "error" not in out.lower():
            return part, acct
        print("placement test-only rejected %s/%s: %s" % (part, acct,
                                                          out[-160:]))
    for part, acct in PLACEMENT:
        info = sh("sinfo -p %s -h -o %%P 2>/dev/null" % part,
                  via_relay_lunarc=True, check=False)
        if info.strip():
            print("placement fallback via sinfo: %s/%s" % (part, acct))
            return part, acct
    raise SystemExit("no working partition/account among %s" % (PLACEMENT,))


def run_checkpoint_now() -> None:
    """Force one checkpoint (light, login-safe) + print the status file."""
    gate("forced checkpoint on %s" % HOST)
    sh("cd %s && python3 hpc/checkpoint_gs.py %s" % (REMOTE_ROOT,
                                                     REMOTE_ROOT),
       via_relay_lunarc=True)
    print(sh("cat %s/results/GS_R1_STATUS.json" % REMOTE_ROOT,
             via_relay_lunarc=True))


# ------------------------------------------------------------- campaign
def main() -> None:
    if MODE == "batch":
        run_batch()
        return
    if MODE == "checkpoint":
        run_checkpoint_now()
        return

    gate("0. preflight")
    assert os.path.isdir(os.path.join(ROOT, "hpc"))
    print("capsule=%s host=%s relay=%s mode=%s" % (ROOT, HOST,
                                                   RELAY or "direct", MODE))

    gate("1. sync capsule -> %s:%s (code staging for tests)" % (LAPTOP,
                                                                LAPTOP_DIR))
    laptop("mkdir -p %s" % os.path.dirname(LAPTOP_DIR))
    r = subprocess.run(["rsync", "-a"] + RSYNC_FILTERS +
                       ["%s/" % ROOT.rstrip("/"),
                        "%s:%s/" % (LAPTOP, LAPTOP_DIR)],
                       capture_output=True, text=True)
    assert r.returncode == 0, "rsync to laptop failed: %s" % r.stderr[-500:]

    gate("2. unit tests on %s (NOT the Mac)" % LAPTOP)
    out = laptop("cd %s && python3 -m pytest tests/test_gs.py -q" % LAPTOP_DIR)
    print(out[-1500:])
    assert "passed" in out.split("\n")[-1], out[-500:]

    gate("3. sync capsule -> %s:%s (code; scored artifacts must be absent)"
         % (HOST, REMOTE_ROOT))
    scored = sh("ls %s/results 2>/dev/null | grep -c '^GS_R1_' || true"
                % REMOTE_ROOT, via_relay_lunarc=True)
    assert int(scored.strip() or "0") == 0, \
        "REFUSED: %s scored GS artifacts already on %s" % (scored, HOST)
    sh("mkdir -p %s/logs %s/results %s/archives %s/manifests/receipts"
        % (REMOTE_ROOT, REMOTE_ROOT, REMOTE_ROOT, REMOTE_ROOT),
       via_relay_lunarc=True)
    rsync_e = "" if RELAY is None else '-e "ssh %s ssh" ' % RELAY
    filters = " ".join(RSYNC_FILTERS + [
        "--exclude=GRAND_SEARCH_R1_FREEZE.json", "--exclude=GS_ENV_PROBE.json",
        "--exclude=ADAPTIVITY_LEDGER.jsonl",
        "--exclude=manifests/GS_R1_TASKS.json",
        "--exclude=manifests/GS_R1_BATCH_*"])
    r = subprocess.run(
        'rsync -a %s%s %s "%s/" %s:%s/'
        % (rsync_e, filters, "", ROOT.rstrip("/"), HOST, REMOTE_ROOT),
        shell=True, capture_output=True, text=True)
    assert r.returncode == 0, "rsync mac->lunarc failed: %s" % r.stderr[-500:]

    gate("4. environment probe on %s (scoring host, BEFORE freeze)" % HOST)
    probe = sh("cd %s && python3 hpc/env_probe.py %s" % (REMOTE_ROOT,
                                                         REMOTE_ROOT),
               via_relay_lunarc=True)
    print(probe)
    assert "ENV PROBE" in probe

    gate("5. freeze on %s (tool-stamped; reads the probe, refuses without)"
         % HOST)
    frz = sh("test -f %s/GRAND_SEARCH_R1_FREEZE.json && echo yes || echo no"
             % REMOTE_ROOT, via_relay_lunarc=True)
    if frz.strip() == "no":
        out = sh("cd %s && python3 hpc/freeze_gs.py %s" % (REMOTE_ROOT,
                                                           REMOTE_ROOT),
                 via_relay_lunarc=True)
        print(out)
    else:
        print("freeze already exists — verifying binding")
        out = sh("cd %s && python3 -c \"import json,hashlib;"
                 "f=json.load(open('GRAND_SEARCH_R1_FREEZE.json'));"
                 "assert f['status']=='frozen_before_scored_runs';"
                 "print(hashlib.sha256(open('GRAND_SEARCH_R1_FREEZE.json',"
                 "'rb').read()).hexdigest());print(f['created_utc'])\""
                 % REMOTE_ROOT, via_relay_lunarc=True)
        print(out)
    m = re.search(r"freeze_sha256=([0-9a-f]{64})", out)
    if not m:
        m2 = re.search(r"^([0-9a-f]{64})$", out.strip(), re.M)
        assert m2, "no freeze sha found in:\n%s" % out
        fsha = m2.group(1)
    else:
        fsha = m.group(1)
    print("freeze_sha256=%s" % fsha)

    gate("6. frozen task manifest on %s (never rewritten once scored)" % HOST)
    have = sh("test -f %s/manifests/GS_R1_TASKS.json && echo yes || echo no"
              % REMOTE_ROOT, via_relay_lunarc=True)
    if have.strip() == "no":
        sh("cd %s && python3 - <<'PY'\n"
           "import hashlib, json, os, time\n"
           "ROOT=%r\n"
           "tasks=[]\n"
           "for arm in %r:\n"
           "    for s in %r:\n"
           "        tasks.append({'kind':'search','arm':arm,'seed':s})\n"
           "for c in range(%d):\n"
           "    tasks.append({'kind':'sweep','shard':c,'n_shards':%d})\n"
           "h=hashlib.sha256()\n"
           "for d in ('morphology','evaluation','search','hpc'):\n"
           "    for fn in sorted(os.listdir(os.path.join(ROOT,d))):\n"
           "        if fn.endswith('.py'):\n"
           "            h.update(open(os.path.join(ROOT,d,fn),'rb').read())\n"
           "start=time.time()\n"
           "m={'manifest_id':'GS_R1_TASKS_V1',\n"
           "   'created_utc':time.strftime('%%Y-%%m-%%dT%%H:%%M:%%SZ',time.gmtime()),\n"
           "   'created_utc_by':'hpc/submit_gs.py manifest gate',\n"
           "   'freeze_sha256':hashlib.sha256(open(ROOT+'/GRAND_SEARCH_R1_FREEZE.json','rb').read()).hexdigest(),\n"
           "   'code_digest':h.hexdigest(),\n"
           "   'campaign_start_utc':time.strftime('%%Y-%%m-%%dT%%H:%%M:%%SZ',time.gmtime()),\n"
           "   'stop_ts':start+24*3600,\n"
           "   'wall_clock_budget_h':24,\n"
           "   'n_tasks':len(tasks),'tasks':tasks}\n"
           "json.dump(m,open(ROOT+'/manifests/GS_R1_TASKS.json','w'),indent=1,sort_keys=True)\n"
           "print('manifest tasks',len(tasks))\n"
           "PY" % (REMOTE_ROOT, SEARCH_ARMS, SEEDS, N_SWEEP_SHARDS,
                   N_SWEEP_SHARDS), via_relay_lunarc=True)
    n_tasks = int(sh("python3 -c \"import json;print(json.load(open('%s/"
                     "manifests/GS_R1_TASKS.json'))['n_tasks'])\"" % REMOTE_ROOT,
                     via_relay_lunarc=True))
    stop_ts = sh("python3 -c \"import json;print(json.load(open('%s/"
                 "manifests/GS_R1_TASKS.json'))['stop_ts'])\"" % REMOTE_ROOT,
                 via_relay_lunarc=True).strip()
    print("manifest tasks=%d stop_ts=%s" % (n_tasks, stop_ts))
    if DRY:
        print("dry stop")
        return

    gate("7. sync frozen artifacts back (laptop + Mac, md5-verified)")
    for rel in ("GRAND_SEARCH_R1_FREEZE.json", "GS_ENV_PROBE.json",
                "manifests/GS_R1_TASKS.json"):
        rmd5 = remote_md5("%s/%s" % (REMOTE_ROOT, rel))
        subprocess.run('rsync -a %s"%s:%s/%s" "%s/%s"'
                       % (rsync_e, HOST, REMOTE_ROOT, rel,
                          ROOT.rstrip("/"), rel),
                       shell=True, capture_output=True, text=True, check=False)
        subprocess.run('rsync -a %s"%s:%s/%s" "%s:%s/%s"'
                       % (rsync_e, HOST, REMOTE_ROOT, rel, LAPTOP,
                          LAPTOP_DIR, rel),
                       shell=True, capture_output=True, text=True, check=False)
        assert local_md5(os.path.join(ROOT, rel)) == rmd5, \
            "md5 mismatch on %s (Mac copy)" % rel
        lm = laptop("md5sum %s/%s | awk '{print $1}'"
                    % (LAPTOP_DIR, rel)).split()[0]
        assert lm == rmd5, "md5 mismatch on %s (laptop copy)" % rel
        print("%s md5=%s verified on 3 hosts" % (rel, rmd5[:12]))

    gate("8. smoke (qos=test) + placement resolution")
    placement = None
    for part, acct in PLACEMENT:
        jid = sh("cd %s && sbatch -p %s -A %s --export=ALL,GS_FREEZE_SHA=%s "
                 "hpc/smoke_gs.sbatch" % (REMOTE_ROOT, part, acct, fsha),
                 via_relay_lunarc=True, check=False)
        jm = re.search(r"(?:^|\s)(\d+)$", jid.strip())
        if jm:
            placement = (part, acct)
            smoke_jid = jm.group(1)
            print("smoke submitted job=%s on %s/%s" % (smoke_jid, part, acct))
            break
        print("placement rejected %s/%s: %s" % (part, acct, jid[-200:]))
    assert placement, "no working partition/account among %s" % (PLACEMENT,)
    part, acct = placement
    deadline = time.time() + 900
    smoke_state = ""
    while time.time() < deadline:
        st = sh("sacct -j %s -n -o State --name= | head -1" % smoke_jid,
                via_relay_lunarc=True)
        smoke_state = st.strip().split()[0] if st.strip() else ""
        if smoke_state in ("COMPLETED", "FAILED", "CANCELLED", "TIMEOUT",
                           "OUT_OF_MEMORY"):
            break
        time.sleep(20)
    smoke_out = sh("cat %s/logs/gsmoke_%s.out 2>/dev/null | tail -5"
                   % (REMOTE_ROOT, smoke_jid), via_relay_lunarc=True)
    print(smoke_out)
    assert "SMOKE OK" in smoke_out, "smoke gate failed (%s)" % smoke_state
    print("SMOKE OK on %s/%s" % (part, acct))

    gate("9. production arrays + hourly checkpoint chain + aggregate")
    sub = sh("cd %s && sbatch -p %s -A %s -t 04:00:00 -c 1 "
             "--array=0-%d%%48 --export=ALL,GS_FREEZE_SHA=%s,GS_STOP_TS=%s "
             "hpc/grand_search.sbatch"
             % (REMOTE_ROOT, part, acct, n_tasks - 1, fsha, stop_ts),
             via_relay_lunarc=True)
    array_jid = re.search(r"(?:^|\s)(\d+)$", sub.strip()).group(1)
    print("array job=%s tasks=%d" % (array_jid, n_tasks))
    ck = sh("cd %s && sbatch -p %s -A %s -t 00:10:00 -c 1 "
            "--export=ALL,GS_FREEZE_SHA=%s,GS_STOP_TS=%s,"
            "GSCK_PARTITION=%s,GSCK_ACCOUNT=%s hpc/checkpoint_gs.sbatch"
            % (REMOTE_ROOT, part, acct, fsha, stop_ts, part, acct),
            via_relay_lunarc=True)
    ck_jid = re.search(r"(?:^|\s)(\d+)$", ck.strip()).group(1)
    print("checkpoint chain job=%s (self-resubmits +55min until terminal)"
          % ck_jid)
    agg = sh("cd %s && sbatch -p %s -A %s -t 01:00:00 -c 1 "
             "--dependency=afterany:%s "
             "--export=ALL,GS_FREEZE_SHA=%s "
             "--wrap='python3 hpc/aggregate_gs.py %s'"
             % (REMOTE_ROOT, part, acct, array_jid, fsha, REMOTE_ROOT),
             via_relay_lunarc=True)
    agg_jid = re.search(r"(?:^|\s)(\d+)$", agg.strip()).group(1)
    print("aggregate job=%s (afterany array %s)" % (agg_jid, array_jid))
    print(json.dumps({
        "freeze_sha256": fsha,
        "placement": {"partition": part, "account": acct},
        "array_job_id": array_jid, "checkpoint_chain_job_id": ck_jid,
        "aggregate_job_id": agg_jid,
        "n_tasks": n_tasks, "stop_ts": stop_ts,
        "hourly_checkpoint": "results/GS_R1_CHECKPOINTS.jsonl",
        "status_file": "results/GS_R1_STATUS.json",
        "adaptivity_ledger": LEDGER,
        "adaptive_batch_cmd": "python3 hpc/submit_gs.py %s %s --batch "
                              "<spec.json>" % (ROOT, HOST),
    }, indent=1))


if __name__ == "__main__":
    main()
