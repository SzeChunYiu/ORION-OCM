"""E5 engineering-chain pass runner (post-freeze lever; frozen base results untouched).

Usage (laptop, repo root):

    python3.12 research/quantum-structural-ocm-v1/msc/run_e5_pass.py \
        research/quantum-structural-ocm-v1/msc/MSC_V1_RESULTS.json --commit <sha>

Appends one entry to results["engineering_chain"]: Q2_QUOTIENT_E4E5 and Q5_COMPOSED_E4E5
on the SAME frozen stream/population (world defaults = frozen scored salts), with
per-task decision equivalence against the frozen base asserted before anything is
recorded (exit 3, nothing written, on any divergence).

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
from lever_e5 import Q2E5, Q5E5  # noqa: E402

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
        "pass": "E5_CONE_CONFIRM",
        "stage_attribution": "witness extraction, not counting: E4 objects decompose as "
                             "839.34 = 540.94 counting + 8.66 path-member fetch + 289.75 "
                             "charged full-closure fallback (488 atoms x 19 positives / 32 "
                             "tasks); the counting stage alone already beat the parent "
                             "(540.94 vs 767.88), but path_blocks never confirmed (19/19 "
                             "positives fell back) because the fully-inside induced-subfield "
                             "restriction drops any derivation edge carrying a side-head "
                             "outside the extracted region, while production gated_closure "
                             "admits heads individually",
        "lever": "E5 cone confirmation: witness region = the counted cone (every block with "
                 "count > 0 at early stop) instead of one backward-walk path, confirmed under "
                 "the production-faithful tail projection (an edge is kept when all tails are "
                 "in-region; heads are admitted individually in-region). The charged "
                 "full-closure fallback is kept for residual non-singleton ambiguity and its "
                 "counter recorded; member fetch and projected-edge charges mirror "
                 "confirm_on_induced",
        "equivalence_argument": "decisions cannot change sign: negative refutation is "
                                "untouched (count([t]) == 0 exact); a SUPPORTED answer "
                                "requires t reached by gated_closure inside the projected "
                                "subfield, and any firing there (tails reached in-region, "
                                "warrant live, heads a subset of the field heads) is a firing "
                                "in the full field, so confirmation never affirms a "
                                "non-derivation; per-task decision equality vs the frozen "
                                "base is asserted before recording",
        "component_decomposition_of_E4_objects": {
            "objects_mean": 839.34,
            "counting_objects_mean": 540.94,
            "path_member_fetch_mean": 8.66,
            "fallback_objects_mean": 289.75,
            "Q1_parent_objects_mean": 767.88,
            "note": "measured on the frozen stream by wrapping split_singletons / "
                    "counting_closure / confirm_on_induced; fallback reconciles exactly as "
                    "488 atoms x 19 positive tasks / 32 tasks"
        },
        "commit": args.commit,
        "code_sha256": {p: sha256_file(HERE / p) for p in
                        ("lever_e5.py", "run_e5_pass.py", "lever_e4.py", "quotient.py",
                         "arms.py", "run_msc.py", "world.py", "probing.py")},
        "arms": {}, "deltas_vs_base": {},
        "decision_equivalence_vs_base": {},
    }
    for arm, base_name in ((Q2E5(), "Q2_QUOTIENT"), (Q5E5(), "Q5_COMPOSED")):
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
    entry["cone_confirmation_counters"] = {
        name: {"confirmations_used": a["mechanism_counters"].get("confirmations_used"),
               "confirmation_fallbacks": a["mechanism_counters"].get("confirmation_fallbacks")}
        for name, a in entry["arms"].items()}
    entry["parent_comparison"] = {
        name: {"objects_mean": a["aggregates"]["objects_touched"]["mean"],
               "edges_mean": a["aggregates"]["edges_touched"]["mean"],
               "probes_mean": a["aggregates"].get("probes", {}).get("mean", 0.0),
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
    print("appended E5_CONE_CONFIRM to", results_path)
    for name, a in entry["arms"].items():
        cmp = entry["parent_comparison"][name]
        print("%-16s objects %.1f (parent %.1f) edges %.1f (parent %.1f) probes %.1f "
              "beats_objects=%s beats_edges=%s fallbacks=%d"
              % (name, cmp["objects_mean"], cmp["Q1_parent_objects_mean"],
                 cmp["edges_mean"], cmp["Q1_parent_edges_mean"], cmp["probes_mean"],
                 cmp["beats_parent_on_objects"], cmp["beats_parent_on_edges"],
                 a["mechanism_counters"].get("confirmation_fallbacks", -1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
