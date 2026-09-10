#!/usr/bin/env python3
"""GS-R1 exhaustive-sweep worker (GSE arm, #221 sec 18): deterministic
sharded enumeration of GS_BOUND_V1 (143,881,920 candidates), compile-
legality filtered exactly like the census, every legal genome evaluated at
T0 and charged.  Purpose: the definitive viable-morphology denominator
(sampling-breadth saturation test) at honest CPU cost.

Failure-ledger discipline for the sweep (frozen note): at ~144M candidates
a per-candidate FAILURES.jsonl line is a storage defect, so each shard
appends per-stage AGGREGATE counts + the top nogood grammar signatures
(schema GS_FAILURE_SWEEP_AGG_V1) plus per-candidate lines only for
crash-class failures.  Search arms keep the per-candidate ledger.
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(sys.argv[1])
SHARD = int(sys.argv[2])
N_SHARDS = int(sys.argv[3])
sys.path.insert(0, ROOT)
os.environ["ZOO_FAILURES_JSONL"] = os.path.join(
    ROOT, "results", "FAILURES_GSE_c%d.jsonl" % SHARD)

import hashlib  # noqa: E402

from evaluation.evaluate import evaluate_genome  # noqa: E402
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402
from morphology.compile import InvariantViolation  # noqa: E402
from morphology.gs_bound import (enumerate_gs_bound, gs_bound_closed_form_size,  # noqa: E402
                                 grammar_signature)
from search.failure_memory import append_failure  # noqa: E402

RUN_ID = "GS_R1_GSE_c%d" % SHARD


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def code_digest(root: str) -> str:
    h = hashlib.sha256()
    for d in ("morphology", "evaluation", "search", "hpc"):
        for fn in sorted(os.listdir(os.path.join(root, d))):
            if fn.endswith(".py"):
                h.update(open(os.path.join(root, d, fn), "rb").read())
    return h.hexdigest()


def main() -> None:
    freeze_path = os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json")
    freeze = json.load(open(freeze_path))
    fsha = sha256_file(freeze_path)
    env_sha = os.environ.get("GS_FREEZE_SHA", "")
    assert env_sha in ("", fsha), "freeze sha mismatch"
    assert code_digest(ROOT) == freeze["code_digest"], "code drift vs freeze"
    assert freeze["search_bound"]["size"] == gs_bound_closed_form_size()

    t_cpu = time.process_time()
    t_wall = time.time()
    n_seen = 0            # legal genomes evaluated
    n_viable = 0
    stage_counts = {"gate:GATE_CAPABILITY_FLOOR": 0,
                    "gate:GATE_CORRECTNESS": 0,
                    "gate:GATE_REVOCATION_FIDELITY": 0,
                    "gate:OTHER": 0}
    by_farch = {}
    by_extra_n = {}
    by_operator = {}
    nogood_sigs = {}
    sigs = {}

    for g in enumerate_gs_bound(shard=(SHARD, N_SHARDS)):
        n_seen += 1
        try:
            r = evaluate_genome(g, tier="T0")
        except Exception as e:
            append_failure({
                "candidate_id": g.digest(), "tier": "T0",
                "stage": "tier_eval",
                "counterexample": "exception:%s" % repr(e)[:180],
                "grammar_signature": grammar_signature(g)})
            stage_counts["crash"] = stage_counts.get("crash", 0) + 1
            continue
        if r["feasible"]:
            n_viable += 1
            sig = grammar_signature(g)
            sigs[sig] = True
            by_farch[g.F_arch] = by_farch.get(g.F_arch, 0) + 1
            n_extra = len(g.U) - 1
            by_extra_n[n_extra] = by_extra_n.get(n_extra, 0) + 1
            for op in g.O_basis:
                by_operator[op] = by_operator.get(op, 0) + 1
        else:
            stage = None
            for gate_name in ("GATE_CORRECTNESS", "GATE_REVOCATION_FIDELITY",
                              "GATE_CAPABILITY_FLOOR"):
                if r["gates"].get(gate_name) is False:
                    stage = "gate:%s" % gate_name
                    break
            stage = stage or "gate:OTHER"
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
            sig = grammar_signature(g)
            nogood_sigs[sig] = nogood_sigs.get(sig, 0) + 1

    cpu_s = time.process_time() - t_cpu
    wall_s = time.time() - t_wall

    # aggregate failure-memory entry (frozen sweep discipline)
    append_failure({
        "schema": "GS_FAILURE_SWEEP_AGG_V1",
        "candidate_id": RUN_ID, "tier": "T0", "shard": SHARD,
        "stage": "sweep_aggregate",
        "counterexample": json.dumps(stage_counts, sort_keys=True),
        "top_nogood_signatures": [
            {"grammar_signature": s, "count": c}
            for s, c in sorted(nogood_sigs.items(),
                               key=lambda kv: -kv[1])[:64]],
        "n_evaluated": n_seen, "n_viable": n_viable,
    })

    receipt = make_receipt(
        run_id=RUN_ID,
        created_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        host=os.environ.get("ZOO_HOST", os.uname().nodename),
        tier="T0", config_digest=fsha)
    receipt = append_record(receipt, 0, {
        "shard": SHARD, "n_shards": N_SHARDS,
        "n_evaluated": n_seen, "n_viable": n_viable})
    assert verify_receipt(receipt), "receipt verify failed"

    out = {
        "run_id": RUN_ID, "arm": "GSE_sweep", "shard": SHARD,
        "n_shards": N_SHARDS,
        "n_evaluated": n_seen, "n_viable": n_viable,
        "n_distinct_viable_signatures": len(sigs),
        "stage_counts": stage_counts,
        "by_F_arch": dict(sorted(by_farch.items())),
        "by_extra_units": {str(k): v for k, v in sorted(by_extra_n.items())},
        "by_operator": dict(sorted(by_operator.items())),
        "cpu_seconds": round(cpu_s, 3), "wall_seconds": round(wall_s, 3),
        "cpu_hours": round(cpu_s / 3600.0, 6),
        "viable_per_cpu_hour": (round(n_viable / (cpu_s / 3600.0), 6)
                                if cpu_s > 0 else None),
        "freeze_sha256": fsha, "receipt": receipt,
    }
    with open(os.path.join(ROOT, "results", RUN_ID + ".json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    with open(os.path.join(ROOT, "manifests", "receipts",
                           RUN_ID + ".json"), "w") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
    with open(os.path.join(ROOT, "results", RUN_ID + ".status"), "w") as fh:
        fh.write("ok\n")
    print("DONE %s evaluated=%d viable=%d cpu_h=%.4f" % (
        RUN_ID, n_seen, n_viable, cpu_s / 3600.0))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # retain crash evidence
        import traceback
        with open(os.path.join(
                ROOT, "results", RUN_ID + ".status"), "w") as fh:
            fh.write("fail %r\n" % (e,))
        with open(os.path.join(
                ROOT, "logs", RUN_ID + ".crash"), "w") as fh:
            fh.write(traceback.format_exc())
        raise
