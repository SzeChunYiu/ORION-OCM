"""Persistent GS scored-lane runner for the laptops (#221 sec 18 / GS-R1h,
worker O).  Operator upgrade 2026-09-09: laptops are FULL scored compute
lanes (distinct seeds vs LUNARC), not just replicates.

Design
  * polls a local queue dir:  <queue>/incoming/*.json  (centre/operator
    drops hourly adaptive batch specs over ssh; no ceremony)
    <queue>/running/<spec_id>/shard<k>.json  (per-shard done markers ->
    crash-safe resume: only missing shards re-run)
    <queue>/done/ , <queue>/rejected/
  * every spec is appended to results/ADAPTIVITY_LEDGER.jsonl BEFORE any
    shard launches (decision-before-submission discipline; frozen rules
    never modified mid-run)
  * scored specs REQUIRE a sha-verified GRAND_SEARCH_R1_FREEZE.json in
    --freeze-dir; without it the spec is REJECTED (never silently scored)
  * shards run as independent `python3 -m gpu.firehose` subprocesses
    (distinct frozen seeds per shard; receipt-chained each), aggregated by
    the runner into results/GS_R1_CHECKPOINTS.jsonl +
    results/GS_R1_STATUS.json every batch (and firehose adds its own
    hourly mid-run lines)
  * kinds: firehose (default) | replicate (re-measurements, NEVER enter
    selection, labelled) | command (bridge to worker N's harness when his
    branch lands; argv list, ledgered, same freeze gate)

Spec schema (incoming/*.json):
  {"spec_id": "b1-laptop-0007", "kind": "firehose", "scored": true,
   "mode": "random", "n": 60000, "seed_base": 500001, "shards": 12,
   "chunk": 2048, "backend": "py",
   "sampling_weights": {"F_arch": {...}},          # optional GS-R1h
   "tier_promotions": [...],                        # recorded+forwarded
   "issued_by": "centre", "note": "..."}

Usage (nohup, persistent):
  nohup python3 hpc/laptop_runner.py --zoo-root ~/gs-run/zoo \
      --lane laptop_billy --workers 12 --queue ~/gs-run/queue \
      --freeze-dir ~/gs-run/freeze >> ~/gs-run/logs/runner.out 2>&1 &

Python compatibility: 3.8.10 .. 3.14.4, stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

ZOO_REL = "research/ocm-morphology-zoo-v1"
FREEZE_BASE = "GRAND_SEARCH_R1_FREEZE"


def log(msg: str) -> None:
    sys.stdout.write("[%s] %s\n" % (time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg))
    sys.stdout.flush()


def jdump(path: str, obj: Any) -> None:
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    os.replace(tmp, path)


def capsule_digest(zoo_root: str) -> str:
    """Content digest of the code the lane executes (no git on laptops)."""
    h = hashlib.sha256()
    files = []
    for sub in ("gpu", "evaluation", "morphology", "search", "hpc", "tests"):
        d = os.path.join(zoo_root, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".py"):
                files.append(os.path.join(d, fn))
    for p in sorted(files):
        h.update(os.path.basename(p).encode())
        with open(p, "rb") as f:
            h.update(f.read())
    return h.hexdigest()


def verified_freeze(freeze_dir: str) -> Optional[Tuple[str, str]]:
    p = os.path.join(freeze_dir, FREEZE_BASE + ".json")
    s = os.path.join(freeze_dir, FREEZE_BASE + ".sha256")
    if not (os.path.exists(p) and os.path.exists(s)):
        return None
    with open(s) as f:
        want = f.read().strip().split()[0]
    with open(p, "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    if got != want:
        return None
    return p, got


def append_ledger(zoo_root: str, lane: str, decision: Dict[str, Any]) -> None:
    path = os.path.join(zoo_root, "results", "ADAPTIVITY_LEDGER.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "lane": lane, "code_sha": decision.pop("code_sha", None)}
    rec.update(decision)
    with open(path, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def checkpoint_aggregate(zoo_root: str, lane: str, spec_id: str,
                         label: str, shard_summaries: List[Dict[str, Any]],
                         wall_s: float, spec: Dict[str, Any]) -> None:
    from gpu.firehose import checkpoint_line, status_write
    att = sum(s.get("n_attempted", 0) for s in shard_summaries)
    comp = sum(s.get("n_evaluated", 0) for s in shard_summaries)
    feas = sum(s.get("n_feasible", 0) for s in shard_summaries)
    enc = sum(s.get("costs", {}).get("encode_s", 0.0) for s in shard_summaries)
    tap = sum(s.get("costs", {}).get("tape_s", 0.0) for s in shard_summaries)
    fails = sum(s.get("n_failures", 0) for s in shard_summaries)
    heads = [s.get("receipt_head", "") for s in shard_summaries]
    line = checkpoint_line(
        zoo_root, lane, "spec:" + spec_id, label, spec_id, att, comp, feas,
        enc, tap, wall_s, fails, heads[0] if heads else "",
        shard_summaries[0].get("freeze_sha256") if shard_summaries else None,
        shard_summaries[0].get("backend", "?") if shard_summaries else "?")
    line["run_ids"] = [s.get("run_id") for s in shard_summaries]
    line["kinds"] = spec.get("kind", "firehose")
    status_write(zoo_root, lane, dict(line, state="batch_done"))


def process_spec(zoo_root: str, lane: str, spec_path: str, queue: str,
                 workers: int, backend: str, freeze_dir: str,
                 logs_dir: str) -> None:
    with open(spec_path) as f:
        spec = json.load(f)
    spec_id = str(spec.get("spec_id", os.path.basename(spec_path)))
    kind = spec.get("kind", "firehose")
    scored = bool(spec.get("scored", True))
    code_sha = capsule_digest(zoo_root)
    freeze = verified_freeze(freeze_dir)
    incoming = os.path.join(queue, "incoming")
    run_dir = os.path.join(queue, "running", spec_id)
    os.makedirs(run_dir, exist_ok=True)

    if scored and freeze is None:
        append_ledger(zoo_root, lane, {
            "action": "REJECT", "spec_id": spec_id,
            "reason": "NO_VERIFIED_FREEZE (scored batch requires "
                      "sha-verified %s)" % FREEZE_BASE,
            "code_sha": code_sha})
        os.replace(spec_path, os.path.join(queue, "rejected",
                                           os.path.basename(spec_path)))
        log("REJECTED %s (no verified freeze)" % spec_id)
        return

    if kind == "command":
        append_ledger(zoo_root, lane, {
            "action": "run_command", "spec_id": spec_id, "scored": scored,
            "argv": spec.get("argv"), "code_sha": code_sha,
            "freeze_sha256": freeze[1] if freeze else None})
        env = dict(os.environ)
        env["ZOO_HOST"] = lane
        env["ZOO_FREEZE_SHA"] = freeze[1] if freeze else ""
        logf = os.path.join(logs_dir, "%s.cmd.log" % spec_id)
        with open(logf, "w") as lf:
            rc = subprocess.call([str(a) for a in spec.get("argv", [])],
                                 cwd=zoo_root, stdout=lf, stderr=lf, env=env)
        append_ledger(zoo_root, lane, {
            "action": "command_done", "spec_id": spec_id, "rc": rc})
        os.replace(spec_path, os.path.join(queue, "done",
                                           os.path.basename(spec_path)))
        return

    # ---- firehose / replicate: shard spec into independent frozen runs
    shards = int(spec.get("shards", workers)) if kind == "firehose" else 1
    n_total = int(spec.get("n", 24000)) if kind == "firehose" \
        else int(spec.get("n", 256))
    n_per = (n_total + shards - 1) // shards
    seed_base = int(spec.get("seed_base", 2210))
    seeds = spec.get("seeds") or [seed_base + k for k in range(shards)]
    shard_lane = lane if kind == "firehose" else (lane + "_replicate")

    append_ledger(zoo_root, lane, {
        "action": "LAUNCH", "kind": kind, "spec_id": spec_id,
        "scored": scored, "shards": shards, "seeds": seeds,
        "n_total": n_total, "sampling_weights": spec.get("sampling_weights"),
        "tier_promotions_forwarded": spec.get("tier_promotions"),
        "freeze_sha256": freeze[1] if freeze else None,
        "code_sha": code_sha, "backend": backend,
        "note": spec.get("note", "")})

    t0 = time.time()
    summaries: List[Dict[str, Any]] = []

    def shard_cmd(spec: Dict[str, Any], ssp: str, seed: int,
                  k: int) -> Tuple[List[str], str]:
        cmd = [sys.executable, "-m", "gpu.firehose",
               "--root", zoo_root, "--mode", str(spec.get("mode", "random")),
               "--n", str(n_per), "--seed", str(seed), "--backend", backend,
               "--lane", shard_lane, "--chunk", str(spec.get("chunk", 2048)),
               "--run-spec", ssp]
        if freeze is not None:
            cmd += ["--freeze", freeze[0], "--freeze-sha", freeze[1]]
        return cmd, os.path.join(logs_dir, "%s.shard%d.log" % (spec_id, k))

    pending = list(enumerate(seeds[:shards]))
    active: List[Tuple[int, Any, Any, str]] = []  # (k, proc, logf, marker)
    env = dict(os.environ)
    env["ZOO_HOST"] = shard_lane
    while pending or active:
        while pending and len(active) < max(1, workers):
            k, seed = pending.pop(0)
            marker = os.path.join(run_dir, "shard%d.json" % k)
            if os.path.exists(marker):
                with open(marker) as f:
                    prev = json.load(f)
                if os.path.exists(os.path.join(
                        zoo_root, "results", prev["run_id"] + ".json")):
                    summaries.append(prev)
                    log("shard %d already done (%s)" % (k, prev["run_id"]))
                    continue
            shard_spec = {"spec_id": "%s.s%d" % (spec_id, k), "kind": kind,
                          "n": n_per,
                          "sampling_weights": spec.get("sampling_weights"),
                          "tier_promotions": spec.get("tier_promotions"),
                          "issued_by": spec.get("issued_by", "centre"),
                          "lane": shard_lane, "seed": seed}
            ssp = os.path.join(run_dir, "spec.s%d.json" % k)
            jdump(ssp, shard_spec)
            cmd, logf = shard_cmd(spec, ssp, seed, k)
            lf = open(logf, "w")
            proc = subprocess.Popen(cmd, cwd=zoo_root, stdout=lf,
                                    stderr=subprocess.STDOUT, env=env)
            active.append((k, proc, lf, marker))
            log("shard %d launched (pid %d, seed %d)" % (k, proc.pid, seed))
        time.sleep(1.0)
        still: List[Tuple[int, Any, Any, str]] = []
        for k, proc, lf, marker in active:
            if proc.poll() is None:
                still.append((k, proc, lf, marker))
                continue
            lf.close()
            # firehose composes run_id as
            #   [SMOKE_]GPU_FIREHOSE_<mode>_<seed>_<spec_id-from-run-spec>
            # with the shard run-spec's spec_id being "<spec_id>.s<k>"
            # (no --tag passed, so no trailing component).
            prefix = "" if freeze is not None else "SMOKE_"
            run_id = "%sGPU_FIREHOSE_%s_%s_%s.s%d" % (
                prefix, spec.get("mode", "random"), seeds[k], spec_id, k)
            rpath = os.path.join(zoo_root, "results", run_id + ".json")
            if proc.returncode == 0 and os.path.exists(rpath):
                with open(rpath) as f:
                    s = json.load(f)
                jdump(marker, s)
                summaries.append(s)
                log("shard %d done: %s completed=%d"
                    % (k, s["run_id"], s.get("n_evaluated", 0)))
            else:
                log("shard %d FAILED rc=%s (see logs)" % (k, proc.returncode))
        active = still

    label = (summaries[0]["label"] if summaries else
             ("SCORED_GS_R1" if scored else "SMOKE_NOT_SCORED"))
    if kind == "replicate":
        label = "REPLICATE_NEVER_SELECTION"
        manifest = {"label": label, "lane": lane,
                    "host": platform.node(),
                    "python": platform.python_version(),
                    "code_sha": code_sha,
                    "freeze_sha256": freeze[1] if freeze else None,
                    "runs": [{"run_id": s["run_id"],
                              "receipt_head": s.get("receipt_head"),
                              "seed": s.get("seed")} for s in summaries],
                    "note": "re-measurements for cross-host determinism; "
                            "NEVER enter selection"}
        jdump(os.path.join(zoo_root, "results",
                           "REPLICATE_MANIFEST_%s.json" % lane), manifest)
    if summaries:
        checkpoint_aggregate(zoo_root, lane, spec_id, label, summaries,
                             time.time() - t0, spec)
    append_ledger(zoo_root, lane, {
        "action": "SPEC_DONE", "spec_id": spec_id, "kind": kind,
        "n_shards_ok": len(summaries), "n_shards_total": shards,
        "wall_s": round(time.time() - t0, 1)})
    os.replace(spec_path, os.path.join(queue, "done",
                                       os.path.basename(spec_path)))


def selftest(zoo_root: str, lane: str, backend: str) -> bool:
    for sub in ("gpu", "evaluation", "morphology"):
        d = os.path.join(zoo_root, sub)
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".py"):
                r = subprocess.call([sys.executable, "-m", "py_compile",
                                     os.path.join(d, fn)])
                if r != 0:
                    log("SELFTEST FAIL py_compile %s/%s" % (sub, fn))
                    return False
    cmd = [sys.executable, "-m", "gpu.firehose", "--root", zoo_root,
           "--mode", "random", "--n", "16", "--seed", "2210",
           "--backend", backend, "--lane", lane,
           "--tag", "RUNNER_SELFTEST"]
    r = subprocess.call(cmd, cwd=zoo_root, stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
    if r != 0:
        log("SELFTEST FAIL firehose smoke")
        return False
    log("SELFTEST OK (py_compile + 16-eval smoke, lane %s)" % lane)
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zoo-root", required=True)
    ap.add_argument("--lane", required=True,
                    help="laptop_billy | laptop_old (checkpoint lane id)")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--queue", required=True)
    ap.add_argument("--freeze-dir", required=True)
    ap.add_argument("--poll", type=float, default=20.0)
    ap.add_argument("--backend", default="auto")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    zoo_root = os.path.abspath(args.zoo_root)
    sys.path.insert(0, zoo_root)
    for sub in ("incoming", "running", "done", "rejected"):
        os.makedirs(os.path.join(args.queue, sub), exist_ok=True)
    logs_dir = os.path.join(os.path.dirname(args.queue.rstrip("/")),
                            "logs")
    os.makedirs(logs_dir, exist_ok=True)
    pidf = os.path.join(logs_dir, "runner.pid")
    if os.path.exists(pidf) and not args.force:
        try:
            with open(pidf) as f:
                old = int(f.read().strip())
            os.kill(old, 0)
            log("runner already running (pid %d); use --force to replace"
                % old)
            return
        except (ValueError, ProcessLookupError, PermissionError):
            pass
    with open(pidf, "w") as f:
        f.write(str(os.getpid()))
    log("runner up lane=%s zoo=%s workers=%d queue=%s pid=%d py=%s"
        % (args.lane, zoo_root, args.workers, args.queue, os.getpid(),
           platform.python_version()))
    if not selftest(zoo_root, args.lane, args.backend):
        log("selftest failed — staying up but marking lane DOWN")
        from gpu.firehose import status_write
        status_write(zoo_root, args.lane, {"state": "DOWN_SELFTEST_FAILED"})

    backend = args.backend
    if backend == "auto":
        try:
            import numpy  # noqa: F401
            backend = "numpy"
        except Exception:
            backend = "py"
    last_heartbeat = 0.0
    while True:
        try:
            incoming = sorted(
                (os.path.getmtime(os.path.join(args.queue, "incoming", fn)),
                 fn) for fn in os.listdir(os.path.join(args.queue, "incoming"))
                if fn.endswith(".json"))
            for _, fn in incoming:
                p = os.path.join(args.queue, "incoming", fn)
                if not os.path.exists(p):
                    continue  # moved/processed in a previous iteration
                process_spec(zoo_root, args.lane, p,
                             args.queue, args.workers, backend,
                             args.freeze_dir, logs_dir)
        except Exception as exc:
            log("loop error: %s: %s" % (type(exc).__name__, exc))
        if time.time() - last_heartbeat > 3600.0:
            last_heartbeat = time.time()
            try:
                from gpu.firehose import status_write
                freeze = verified_freeze(args.freeze_dir)
                status_write(zoo_root, args.lane, {
                    "state": "idle", "py": platform.python_version(),
                    "code_sha": capsule_digest(zoo_root),
                    "freeze_verified": bool(freeze)})
            except Exception as exc:
                log("heartbeat error: %s" % exc)
        time.sleep(args.poll)


if __name__ == "__main__":
    main()
