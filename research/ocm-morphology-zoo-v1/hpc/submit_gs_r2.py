#!/usr/bin/env python3
"""GS-R2 campaign driver (JOB B, #221 sec 18 GS-R2) — Mac-side
orchestration only: code sync -> laptop tests -> LUNARC sync -> env probe
-> FREEZE -> manifest -> laptop determinism probe -> LEDGER DECISION LINE
(BEFORE any sbatch) -> smoke (qos=test) + cross-host digest match ->
production array + afterany aggregate.  Every step appends an event line
to EVENTS.jsonl (append-only trace, continuous/-lane convention).

All execution happens off-Mac: tests on billy-laptop; probe/freeze/
manifest light on the LUNARC login node; scoring on LUNARC compute.
Binary-safe transfers only (rsync + md5 verify; never cat|ssh pipes).

Usage: python3 hpc/submit_gs_r2.py <CAPSULE_ROOT> [HOST] [--dry]
                                       [--skip-tests]
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
HOST = next((a for a in sys.argv[2:] if not a.startswith("-")), "lunarc")
DRY = "--dry" in sys.argv
SKIP_TESTS = "--skip-tests" in sys.argv
LAPTOP = "billy-laptop"
LAPTOP_DIR = "pmci-gs/capsule_r2"
REMOTE_ROOT = "$HOME/zoo221/gs_r2"
FREEZE_NAME = "GRAND_SEARCH_R2_FREEZE.json"
ARMS = ["GSA6_NG", "GSA6_DP", "GSA6_SC", "GSA6_ALL", "GSA5P_fixed"]
SEEDS = list(range(6))
PLACEMENT = [("nuc", "lu2026-2-51"), ("lu48", "lu2026-2-51"),
             ("hep", "hep2023-1-3")]
LEDGER = "ADAPTIVITY_LEDGER.jsonl"
EVENTS = os.path.join(ROOT, "EVENTS.jsonl")
RSYNC_FILTERS = [
    "--include=results/AGGREGATE_AMEND*.json",
    "--include=results/REUSE_VECTORIZE_MEASUREMENT.json",
    "--include=results/GSA5_RATE_READ_V1.json",
    "--include=results/GSA5_RATE_READ_V1.md",
    "--exclude=results/*", "--exclude=archives/", "--exclude=logs/",
    "--exclude=manifests/receipts/", "--exclude=__pycache__/",
]

_probe = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o",
                         "ConnectTimeout=8", HOST, "true"],
                         capture_output=True)
RELAY = None if _probe.returncode == 0 else "billy-laptop"


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def event(kind: str, **kv) -> None:
    line = dict(kind=kind, **kv)
    with open(EVENTS, "a") as fh:
        fh.write(json.dumps(dict(ts=now(), **line), sort_keys=True) + "\n")


def sh(cmd, via_relay_lunarc=False, check=True):
    if via_relay_lunarc and RELAY:
        cmd = "ssh %s ssh %s %s" % (RELAY, HOST,
                                    shlex.quote(shlex.quote(cmd)))
    elif via_relay_lunarc:
        cmd = "ssh %s %s" % (HOST, shlex.quote(cmd))
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise SystemExit("FAILED [%s]:\n%s\n%s" % (cmd, p.stdout[-800:],
                                                   p.stderr[-800:]))
    return p.stdout.strip()


def laptop(cmd, check=True):
    p = subprocess.run(["ssh", LAPTOP, cmd], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise SystemExit("LAPTOP FAILED [%s]:\n%s\n%s" % (
            cmd, p.stdout[-800:], p.stderr[-800:]))
    return p.stdout.strip()


_remote_abs = None


def remote_root() -> str:
    global _remote_abs
    if _remote_abs is None:
        _remote_abs = sh('printf %s "$HOME"', via_relay_lunarc=True) \
            + "/zoo221/gs_r2"
    return _remote_abs


def gate(msg):
    print("\n=== %s" % msg)


def remote_md5(path):
    return sh("md5sum %s | awk '{print $1}'" % path,
              via_relay_lunarc=True).split()[0]


def local_md5(path):
    return subprocess.run(["md5", "-q", path],
                          capture_output=True, text=True).stdout.strip()


def ledger_append(line):
    sh("printf '%%s\\n' %s >> %s/%s"
       % (shlex.quote(json.dumps(line, sort_keys=True)), REMOTE_ROOT,
          LEDGER), via_relay_lunarc=True)


def main():
    gate("0. preflight")
    assert os.path.isdir(os.path.join(ROOT, "hpc"))
    assert os.path.exists(os.path.join(ROOT, "evaluation",
                                       "t3_ecology_m104.py"))
    print("capsule=%s host=%s relay=%s dry=%s" % (ROOT, HOST,
                                                  RELAY or "direct", DRY))
    event("preflight", host=HOST, relay=bool(RELAY),
          root=os.path.relpath(ROOT, os.path.dirname(ROOT)))

    gate("1. sync capsule -> %s:%s" % (LAPTOP, LAPTOP_DIR))
    laptop("mkdir -p %s" % LAPTOP_DIR)
    r = subprocess.run(["rsync", "-a"] + RSYNC_FILTERS +
                       ["%s/" % ROOT.rstrip("/"),
                        "%s:%s/" % (LAPTOP, LAPTOP_DIR)],
                       capture_output=True, text=True)
    assert r.returncode == 0, "rsync to laptop failed: %s" % r.stderr[-500:]
    event("sync_laptop", dir=LAPTOP_DIR)

    if not SKIP_TESTS:
        gate("2. unit tests on %s (NOT the Mac)" % LAPTOP)
        out = laptop("cd %s && python3 -m pytest tests/test_gs.py -q"
                     % LAPTOP_DIR)
        print(out[-1500:])
        assert "passed" in out.split("\n")[-1], out[-500:]
        event("tests_laptop", result="passed")

    gate("3. sync capsule -> %s:%s (no scored GS_R2_* artifacts)"
         % (HOST, REMOTE_ROOT))
    scored = sh("ls %s/results 2>/dev/null | grep -c '^GS_R2_' || true"
                % REMOTE_ROOT, via_relay_lunarc=True)
    assert int(scored.strip() or "0") == 0, \
        "REFUSED: %s scored GS_R2 artifacts already on %s" % (scored, HOST)
    sh("mkdir -p %s/logs %s/results %s/archives %s/manifests/receipts"
       % (REMOTE_ROOT, REMOTE_ROOT, REMOTE_ROOT, REMOTE_ROOT),
       via_relay_lunarc=True)
    rsync_e = "" if RELAY is None else '-e "ssh %s ssh" ' % RELAY
    filters = " ".join(RSYNC_FILTERS + [
        "--exclude=" + FREEZE_NAME, "--exclude=GS_ENV_PROBE.json",
        "--exclude=ADAPTIVITY_LEDGER.jsonl",
        "--exclude=manifests/GS_R2_TASKS.json"])
    r = subprocess.run(
        'rsync -a %s%s "%s/" %s:%s/'
        % (rsync_e, filters, ROOT.rstrip("/"), HOST, remote_root()),
        shell=True, capture_output=True, text=True)
    assert r.returncode == 0, "rsync mac->lunarc failed: %s" % r.stderr[-500:]
    event("sync_lunarc", root=REMOTE_ROOT)

    gate("4. environment probe on %s (BEFORE freeze)" % HOST)
    probe = sh("cd %s && python3 hpc/env_probe.py %s" % (REMOTE_ROOT,
                                                         REMOTE_ROOT),
               via_relay_lunarc=True)
    print(probe)
    assert "ENV PROBE" in probe
    event("env_probe", host=HOST)

    gate("5. FREEZE on %s (tool-stamped; refuses on scored artifacts)"
         % HOST)
    have = sh("test -f %s/%s && echo yes || echo no" % (REMOTE_ROOT,
                                                        FREEZE_NAME),
              via_relay_lunarc=True)
    if have.strip() == "no":
        out = sh("cd %s && python3 hpc/freeze_gs_r2.py %s" % (REMOTE_ROOT,
                                                              REMOTE_ROOT),
                 via_relay_lunarc=True)
        print(out)
    else:
        print("freeze already exists — binding check only")
        out = sh("cd %s && python3 -c \"import json,hashlib;"
                 "f=json.load(open('%s'));"
                 "assert f['status']=='frozen_before_scored_runs';"
                 "print('freeze_sha256='+hashlib.sha256(open('%s','rb')"
                 ".read()).hexdigest())\""
                 % (REMOTE_ROOT, FREEZE_NAME, FREEZE_NAME),
                 via_relay_lunarc=True)
        print(out)
    m = re.search(r"freeze_sha256=([0-9a-f]{64})", out)
    assert m, "no freeze sha in:\n%s" % out
    fsha = m.group(1)
    print("freeze_sha256=%s" % fsha)

    gate("6. frozen task manifest (built locally, rsynced; never rewritten)")
    have_m = sh("test -f %s/manifests/GS_R2_TASKS.json && echo yes || echo no"
                % REMOTE_ROOT, via_relay_lunarc=True)
    if have_m.strip() == "no":
        import hashlib as _hl
        tasks = [{"kind": "search", "arm": arm, "seed": s}
                 for arm in ARMS for s in SEEDS]
        h = _hl.sha256()
        for d in ("morphology", "evaluation", "search", "hpc"):
            for fn in sorted(os.listdir(os.path.join(ROOT, d))):
                if fn.endswith(".py"):
                    h.update(open(os.path.join(ROOT, d, fn),
                                  "rb").read())
        man = {
            "manifest_id": "GS_R2_TASKS_V1", "created_utc": now(),
            "created_utc_by": "hpc/submit_gs_r2.py manifest gate",
            "freeze_sha256": fsha, "code_digest": h.hexdigest(),
            "campaign_start_utc": now(),
            "stop_ts": time.time() + 2 * 3600,
            "wall_clock_budget_h": 2,
            "n_tasks": len(tasks), "tasks": tasks,
        }
        mtmp = "/tmp/gs2_manifest_%d.json" % int(time.time())
        with open(mtmp, "w") as fh:
            json.dump(man, fh, indent=1, sort_keys=True)
        r = subprocess.run(
            'rsync -a %s"%s" %s:%s/manifests/GS_R2_TASKS.json'
            % (rsync_e, mtmp, HOST, remote_root()),
            shell=True, capture_output=True, text=True)
        os.unlink(mtmp)
        assert r.returncode == 0, "rsync manifest failed: %s" % r.stderr[-400:]
        print("manifest tasks=%d (5 arms x 6 seeds)" % len(tasks))
    n_tasks = int(sh("python3 -c \"import json;print(json.load(open('%s/"
                     "manifests/GS_R2_TASKS.json'))['n_tasks'])\""
                     % REMOTE_ROOT, via_relay_lunarc=True))
    assert n_tasks == 30, "expected 30 tasks, manifest says %d" % n_tasks
    stop_ts = sh("python3 -c \"import json;print(json.load(open('%s/"
                 "manifests/GS_R2_TASKS.json'))['stop_ts'])\"" % REMOTE_ROOT,
                 via_relay_lunarc=True).strip()
    print("manifest tasks=%d stop_ts=%s" % (n_tasks, stop_ts))
    event("frozen", freeze_sha256=fsha, n_tasks=n_tasks)
    if DRY:
        print("dry stop (freeze + manifest exist; nothing submitted)")
        event("dry_stop")
        return

    gate("7. sync frozen artifacts back (Mac + laptop, md5-verified)")
    for rel in (FREEZE_NAME, "GS_ENV_PROBE.json",
                "manifests/GS_R2_TASKS.json"):
        rmd5 = remote_md5("%s/%s" % (REMOTE_ROOT, rel))
        subprocess.run('rsync -a %s"%s:%s/%s" "%s/%s"'
                       % (rsync_e, HOST, remote_root(), rel,
                          ROOT.rstrip("/"), rel),
                       shell=True, capture_output=True, text=True, check=False)
        assert local_md5(os.path.join(ROOT, rel)) == rmd5, \
            "md5 mismatch on %s (Mac copy)" % rel
        laptop("mkdir -p %s" % os.path.dirname(os.path.join(LAPTOP_DIR, rel)))
        r2 = subprocess.run(["rsync", "-a", os.path.join(ROOT, rel),
                             "%s:%s/%s" % (LAPTOP, LAPTOP_DIR, rel)],
                            capture_output=True, text=True)
        assert r2.returncode == 0, "rsync %s -> laptop failed" % rel
        lm = laptop("md5sum %s/%s | awk '{print $1}'"
                    % (LAPTOP_DIR, rel)).split()[0]
        assert lm == rmd5, "md5 mismatch on %s (laptop copy)" % rel
        print("%s md5=%s verified on 3 hosts" % (rel, rmd5[:12]))
    event("frozen_artifacts_synced", freeze_sha256=fsha)

    gate("8. determinism probe on %s (builtin impls, cross-host)" % LAPTOP)
    lout = laptop("cd %s && python3 hpc/determinism_probe_r2.py %s"
                  % (LAPTOP_DIR, LAPTOP_DIR))
    print(lout)
    lm2 = re.search(r"PROBE_DIGEST=([0-9a-f]{64})", lout)
    assert lm2, "no laptop probe digest:\n%s" % lout
    laptop_digest = lm2.group(1)
    event("probe_laptop", digest=laptop_digest)

    gate("9. DECISION LEDGER LINE BEFORE ANY SBATCH (GS-R1h discipline)")
    ledger_append({
        "schema": "GS_R2_ADAPTIVITY_V1", "event": "decision",
        "ts": now(), "campaign": "GS_R2 (JOB B)",
        "governing_plan": "issue #221 sec 18 GS-R2 + GSA5_RATE_READ_V1 "
                          "implications 1-3 (revival levers)",
        "freeze_sha256": fsha, "n_tasks": n_tasks,
        "arms": ARMS, "seeds": SEEDS,
        "rationale": "R1 bottleneck table: promotion/parent-allocation "
                     "ranking stage owned both the 2.267x distinct-yield "
                     "collapse and the 2.171x CPU factor; test the three "
                     "named revival levers single-lever + package against "
                     "the on-code GSA5P_fixed replication",
        "job_ids": None, "submitted": False,
    })
    le = sh("wc -l < %s/%s" % (REMOTE_ROOT, LEDGER),
            via_relay_lunarc=True)
    print("ledger lines=%s (decision line durable before sbatch)" % le)
    event("ledger_decision", lines=le.strip())

    gate("10. smoke (qos=test) on %s + cross-host digest match" % HOST)
    placement = None
    for part, acct in PLACEMENT:
        jid = sh("cd %s && sbatch -p %s -A %s "
                 "--export=ALL,GS_FREEZE_SHA=%s,ZOO_ROOT=%s "
                 "hpc/smoke_gs_r2.sbatch"
                 % (REMOTE_ROOT, part, acct, fsha, REMOTE_ROOT),
                 via_relay_lunarc=True, check=False)
        jm = re.search(r"(?:^|\s)(\d+)$", jid.strip())
        if jm:
            placement = (part, acct)
            smoke_jid = jm.group(1)
            print("smoke job=%s on %s/%s" % (smoke_jid, part, acct))
            break
        print("placement rejected %s/%s: %s" % (part, acct, jid[-200:]))
    assert placement, "no working partition/account among %s" % (PLACEMENT,)
    part, acct = placement
    event("smoke_submitted", job_id=smoke_jid, partition=part, account=acct)
    deadline = time.time() + 900
    smoke_state = ""
    while time.time() < deadline:
        st = sh("sacct -j %s -n -o State | head -1" % smoke_jid,
                via_relay_lunarc=True)
        smoke_state = st.strip().split()[0] if st.strip() else ""
        if smoke_state in ("COMPLETED", "FAILED", "CANCELLED", "TIMEOUT",
                           "OUT_OF_MEMORY"):
            break
        time.sleep(20)
    smoke_out = sh("cat %s/logs/gs2smoke_%s.out 2>/dev/null | tail -12"
                   % (REMOTE_ROOT, smoke_jid), via_relay_lunarc=True)
    print(smoke_out)
    assert "SMOKE2 OK" in smoke_out, "smoke gate failed (%s)" % smoke_state
    assert smoke_state == "COMPLETED", "smoke state %s" % smoke_state
    lun_digest = re.search(r"PROBE_DIGEST=([0-9a-f]{64})", smoke_out)
    lun_pinned = re.search(r"PROBE_PINNED_DIGEST=([0-9a-f]{64})", smoke_out)
    assert lun_digest, "no LUNARC builtin probe digest in smoke output"
    assert lun_digest.group(1) == laptop_digest, (
        "CROSS-HOST DETERMINISM MISMATCH: laptop %s != LUNARC %s — HALT, "
        "no scored runs submitted" % (laptop_digest, lun_digest.group(1)))
    print("cross-host determinism OK (builtin impls): %s" % laptop_digest)
    if lun_pinned:
        print("on-host pinned-impl digest: %s" % lun_pinned.group(1))
    event("smoke_ok", job_id=smoke_jid, state=smoke_state,
          digest_builtin=laptop_digest,
          digest_pinned=lun_pinned.group(1) if lun_pinned else None)

    gate("11. production array + afterany aggregate (per frozen spec)")
    sub = sh("cd %s && sbatch -p %s -A %s -t 02:00:00 -c 1 "
             "--array=0-%d%%48 "
             "--export=ALL,GS_FREEZE_SHA=%s,ZOO_ROOT=%s,GS_STOP_TS=%s "
             "hpc/grand_search_r2.sbatch"
             % (REMOTE_ROOT, part, acct, n_tasks - 1, fsha, REMOTE_ROOT,
                stop_ts), via_relay_lunarc=True)
    array_jid = re.search(r"(?:^|\s)(\d+)$", sub.strip()).group(1)
    print("array job=%s tasks=%d (%s/%s)" % (array_jid, n_tasks, part, acct))
    agg = sh("cd %s && sbatch -p %s -A %s -t 00:40:00 -c 1 "
             "--dependency=afterany:%s "
             "--export=ALL,GS_FREEZE_SHA=%s,ZOO_ROOT=%s "
             "--wrap='python3 hpc/aggregate_gs_r2.py %s'"
             % (REMOTE_ROOT, part, acct, array_jid, fsha, REMOTE_ROOT,
                REMOTE_ROOT), via_relay_lunarc=True)
    agg_jid = re.search(r"(?:^|\s)(\d+)$", agg.strip()).group(1)
    print("aggregate job=%s (afterany array %s)" % (agg_jid, array_jid))
    ledger_append({
        "schema": "GS_R2_ADAPTIVITY_V1", "event": "submitted",
        "ts": now(), "freeze_sha256": fsha,
        "array_job_id": array_jid, "aggregate_job_id": agg_jid,
        "smoke_job_id": smoke_jid, "n_tasks": n_tasks,
        "placement": [part, acct], "submitted": True,
        "determinism_builtin_digest": laptop_digest,
    })
    event("submitted", array_job_id=array_jid, aggregate_job_id=agg_jid,
          smoke_job_id=smoke_jid, partition=part, account=acct,
          n_tasks=n_tasks, freeze_sha256=fsha,
          digest_builtin=laptop_digest)
    print(json.dumps({
        "freeze_sha256": fsha,
        "placement": {"partition": part, "account": acct},
        "array_job_id": array_jid, "aggregate_job_id": agg_jid,
        "smoke_job_id": smoke_jid, "n_tasks": n_tasks,
        "results_prefix": "GS_R2_", "aggregate": "results/GS_R2_AGGREGATE.json",
        "adaptivity_ledger": LEDGER, "events": "EVENTS.jsonl",
    }, indent=1))


if __name__ == "__main__":
    main()
