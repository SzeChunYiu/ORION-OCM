"""E4 engineering-chain pass runner (post-freeze lever; frozen base results untouched).

Usage (laptop, repo root):

    python3.12 research/quantum-structural-ocm-v1/msc/run_e4_pass.py \
        research/quantum-structural-ocm-v1/msc/MSC_V1_RESULTS.json --commit <sha>

Appends one entry to results["engineering_chain"]: Q2_QUOTIENT_E4 and Q5_COMPOSED_E4 on
the SAME frozen stream/population (world defaults = frozen scored salts), with per-task
decision equivalence against the frozen base asserted before anything is recorded.

Python 3.8-compatible syntax (arms/quotient modules); runs under the 3.12 runtime.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "src"))

import run_msc  # noqa: E402  (frozen runner: reuse its replay/aggregate/charge logic)
import world  # noqa: E402
from lever_e4 import Q2E4, Q5E4  # noqa: E402

SIZING = run_msc.SIZING


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("results_path")
    ap.add_argument("--commit", default=None)
    args = ap.parse_args()
    results_path = Path(args.results_path)
    existing = json.loads(results_path.read_text())

    field, meta = world.build_field(**{k: SIZING[k] for k in
                                       ("n_atoms", "n_edges", "n_evidence")})
    stream = world.build_stream(field, n_tasks=SIZING["n_tasks"],
                                n_updates=SIZING["n_updates"])

    base_by_task = {n: {r["task_idx"]: r for r in recs}
                    for n, recs in existing["per_task"].items()}
    entry = {
        "pass": "E4_WORKLIST",
        "stage_attribution": "per-query counting-closure work: full-scan fixpoint schedule "
                             "+ eager all-block liveness dominate Q2/Q5 object cost at 482 "
                             "blocks over 488 atoms",
        "lever": "E4 work-list enabling (tail-incidence index, one examination per "
                 "count-growth event, fire-once reachability) + lazy memoized block "
                 "liveness; same counting semantics, same per-event charge rule",
        "equivalence_argument": "counting closure is a monotone update system: sequential "
                                "iteration computes the least fixpoint visit-order "
                                "independently; at fixpoint every reachable block saturates "
                                "to its size (any enabled qedge pumps +k per pass, capped by "
                                "size), so enabling {B:k} == reachable(B) and size>=k, and "
                                "fire-once reachability reproduces the counted-positive set, "
                                "refuted flag and decisions exactly",
        "commit": args.commit,
        "code_sha256": {p: sha256_file(HERE / p) for p in
                        ("lever_e4.py", "run_e4_pass.py", "quotient.py", "arms.py",
                         "run_msc.py", "world.py", "probing.py")},
        "arms": {}, "deltas_vs_base": {},
        "decision_equivalence_vs_base": {},
    }
    for arm, base_name in ((Q2E4(), "Q2_QUOTIENT"), (Q5E4(), "Q5_COMPOSED")):
        summary, records = run_msc.run_arm(arm, field, stream)
        base = base_by_task[base_name]
        same = all(str(r["decision"]) == str(base[r["task_idx"]]["decision"])
                   for r in records)
        entry["arms"][arm.name] = summary
        entry["decision_equivalence_vs_base"][arm.name] = same
        entry["deltas_vs_base"][arm.name] = run_msc._deltas(
            records, existing["arms"][base_name]["aggregates"], base)
        if not same:
            sys.stderr.write("DECISION_DIVERGENCE %s vs %s (refusing to record)\n"
                             % (arm.name, base_name))
            return 3
    entry["exactness_preserved"] = all(a["all_correct"] for a in entry["arms"].values())
    entry["parent_comparison"] = {
        name: {"objects_mean": a["aggregates"]["objects_touched"]["mean"],
               "edges_mean": a["aggregates"]["edges_touched"]["mean"],
               "Q1_parent_objects_mean":
                   existing["arms"]["Q1_INDEXED"]["aggregates"]["objects_touched"]["mean"],
               "Q1_parent_edges_mean":
                   existing["arms"]["Q1_INDEXED"]["aggregates"]["edges_touched"]["mean"],
               "beats_parent_on_objects":
                   a["aggregates"]["objects_touched"]["mean"] <
                   existing["arms"]["Q1_INDEXED"]["aggregates"]["objects_touched"]["mean"],
               "beats_parent_on_edges":
                   a["aggregates"]["edges_touched"]["mean"] <
                   existing["arms"]["Q1_INDEXED"]["aggregates"]["edges_touched"]["mean"]}
        for name, a in entry["arms"].items()}
    existing["engineering_chain"].append(entry)
    results_path.write_text(json.dumps(existing, indent=1, sort_keys=True, default=str))
    print("appended E4_WORKLIST to", results_path)
    for name, cmp in entry["parent_comparison"].items():
        print("%-16s objects %.1f (parent %.1f) edges %.1f (parent %.1f) beats_objects=%s beats_edges=%s"
              % (name, cmp["objects_mean"], cmp["Q1_parent_objects_mean"],
                 cmp["edges_mean"], cmp["Q1_parent_edges_mean"],
                 cmp["beats_parent_on_objects"], cmp["beats_parent_on_edges"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
