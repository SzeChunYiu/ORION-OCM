"""One fresh process, two complete current-SV calls; no output or factor cache."""
from pathlib import Path
import argparse
import copy
import json
from dataclasses import asdict
import os
import resource
import sys
import time
import traceback
from trial_common import ROOT, canonical, digest, origins, read, sha, verify_freeze, write

def state(runtime):
    s = runtime.state
    return {"kso_state_hash": s.kso_state_hash, "registry_revision": s.registry_revision,
            "evidence_epoch": s.evidence_epoch, "ks_digest": s.ks.digest(),
            "revoked": sorted(s.revoked), "N": len(s.ks.ids), "edges": len(s.ks.hyperedges)}

def delta(before, after):
    return {k: after[k][len(before[k]):] if isinstance(after[k], list) else after[k]-before[k]
            for k in before}

def run(case_path):
    case = read(case_path); output = Path(case["output"])
    manifest_path = Path(case["manifest"]); m = verify_freeze(manifest_path)
    if sha(manifest_path) != case["manifest_sha256"]: raise ValueError("MANIFEST_DRIFT")
    if case["assignment"] != m["assignments"][case["assignment"]["index"]]: raise ValueError("UNREGISTERED_CASE")
    arm = case["assignment"]["arm"]
    if sys.executable != m["python"]: raise ValueError("WRONG_PYTHON")
    if os.sched_getaffinity(0) != {m["cpu"]}: raise ValueError("WRONG_CPU_AFFINITY")
    if resource.getrlimit(resource.RLIMIT_AS) != (m["address_bytes"], m["address_bytes"]):
        raise ValueError("WRONG_ADDRESS_ENVELOPE")
    ctx = Path(m["context_root"])
    sys.path[:0] = [str(ROOT/"source"), str(ctx), str(ctx/"source/src"), str(ctx/"source/research/ocm-prototype")]
    from bound_context import load
    from clia_reuse_study_common import InvocationMeter
    from representation_donor_grade import wire
    events = []; calls = []; start = time.perf_counter_ns()
    before_import = origins(m, arm)
    with InvocationMeter(events):
        kwargs, meter = load(ctx, output/"private")
        prep_state = state(meter["runtime"])
        prep = {"state": prep_state, "catalogue": meter["catalogue"],
                "task": wire(asdict(kwargs["task"])), "config": wire(asdict(kwargs["config"])),
                "request": json.loads(kwargs["task"].parts[0].text),
                "binding_receipts": meter["binding_receipts"], "events": wire(events),
                "origins": origins(m, arm), "elapsed_ns": time.perf_counter_ns()-start}
        write(output/"preparation.json", prep)
        from exact_sparse_donor_consumer import evaluate
        for index in range(2):
            t = time.perf_counter_ns(); cpu = resource.getrusage(resource.RUSAGE_SELF)
            before = state(meter["runtime"]); counts = copy.deepcopy(meter["counters"])
            check_start, event_start = len(meter["checks"]), len(events)
            result = evaluate(**kwargs, arm=arm)
            after = state(meter["runtime"])
            payload = {"index": index, "assignment": case["assignment"],
                       "state_before": before, "state_after": after, "result": result,
                       "application_checks": wire(meter["checks"][check_start:]),
                       "counter_delta": delta(counts, meter["counters"]),
                       "invocations": wire(events[event_start:])}
            path = output/f"call-{index}.json"; write(path, payload)
            elapsed = time.perf_counter_ns()-t; end = resource.getrusage(resource.RUSAGE_SELF)
            calls.append({"index": index, "path": path.name, "sha256": sha(path),
                          "bytes": path.stat().st_size, "wall_ns": elapsed,
                          "self_user_seconds": end.ru_utime-cpu.ru_utime,
                          "self_system_seconds": end.ru_stime-cpu.ru_stime,
                          "scope": "state/counter snapshots + complete evaluate/checker + canonical payload serialization and file close"})
    final_origins = origins(m, arm)
    if before_import["sympy_imported"] or prep["origins"]["sympy_imported"]:
        raise ValueError("SYMPY_IMPORTED_DURING_SHARED_PREPARATION")
    if arm == "sympy" and not final_origins["sympy_imported"]: raise ValueError("DONOR_NOT_IMPORTED")
    verify_freeze(manifest_path)
    self_cpu, children = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"status": "COMPLETED", "assignment": case["assignment"], "pid": os.getpid(),
            "case_sha256": sha(case_path), "manifest_sha256": sha(manifest_path),
            "calls": calls, "preparation_sha256": sha(output/"preparation.json"),
            "final_state": state(meter["runtime"]), "origins": final_origins,
            "self_cpu": {"user": self_cpu.ru_utime, "system": self_cpu.ru_stime, "maxrss_kib": self_cpu.ru_maxrss},
            "reaped_children_cpu": {"user": children.ru_utime, "system": children.ru_stime},
            "cpu_scope": "self and reaped children separately; no full process-tree guarantee",
            "assigned_calls": 2, "consumer_scope": "DIRECT_SV_SOLVE_WITH_COMMITMENT_DECISION; no durable query/result append; binder persistence included"}

def error_record(case_path, exc):
    case=read(case_path); manifest=Path(case["manifest"])
    return {"status":"ERROR","type":type(exc).__name__,"message":str(exc),"pid":os.getpid(),
            "case_sha256":sha(case_path),"manifest_sha256":sha(manifest),"assignment":case["assignment"],
            "assigned_calls":2,"consumer_scope":"DIRECT_SV_SOLVE_WITH_COMMITMENT_DECISION; no durable query/result append; binder persistence included"}

def main():
    p = argparse.ArgumentParser(); p.add_argument("--case", type=Path, required=True); args = p.parse_args()
    try:
        record = run(args.case); status = 0
    except BaseException as exc:
        traceback.print_exc()
        record = error_record(args.case, exc)
        status = 2
    print(canonical(record).decode(), flush=True)
    return status

if __name__ == "__main__": raise SystemExit(main())
