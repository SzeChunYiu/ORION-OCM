#!/usr/bin/env python3
"""Aggregate K4 array receipts without silently dropping failures or leaking names before scoring.

The aggregator reconstructs the frozen canonical 264-task plan independently of the task files,
requires exactly one receipt for every index, validates freeze hashes and task specifications, and
writes both machine-readable and human-readable reports. Architecture names are hidden by default;
`--reveal-names` may only be used after all scoring is complete.
"""
from __future__ import annotations

import argparse
import collections
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(ROOT, "GMI_K4_LOFO_FREEZE_V1.json")
RES = os.path.join(ROOT, "microscopes", "results", "k4")


def load_freeze():
    raw = open(FREEZE).read()
    full = json.loads(raw)
    safe = dict(full); safe.pop("name_key", None)
    return full, safe, hashlib.sha256(raw.encode()).hexdigest()


def task_plan(freeze):
    return [
        {"family": fid, "grammar": gram, "cell": cell}
        for fid in sorted(freeze["families"])
        for gram in sorted(freeze["grammars"])
        for cell in ("w1", "w2", "w4", "w8")
    ]


def load_receipts(pattern):
    files = sorted(glob.glob(pattern))
    recs = []
    parse_fail = []
    for p in files:
        try:
            r = json.load(open(p)); r["_path"] = p; recs.append(r)
        except Exception as e:
            parse_fail.append({"path": p, "error": repr(e)})
    return recs, parse_fail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", default=os.path.join(RES, "K4_*.json"))
    ap.add_argument("--out-json", default=os.path.join(RES, "K4_AGGREGATE_V1.json"))
    ap.add_argument("--out-md", default=os.path.join(RES, "K4_AGGREGATE_V1.md"))
    ap.add_argument("--reveal-names", action="store_true")
    a = ap.parse_args()

    full, freeze, freeze_sha = load_freeze()
    plan = task_plan(freeze)
    recs, parse_fail = load_receipts(a.pattern)
    by_idx = collections.defaultdict(list)
    for r in recs:
        if isinstance(r.get("task_index"), int):
            by_idx[r["task_index"]].append(r)

    structural_errors = []
    if parse_fail:
        structural_errors.append({"parse_failures": parse_fail})
    missing = [i for i in range(len(plan)) if i not in by_idx]
    duplicate = {str(i): [x.get("_path") for x in xs] for i, xs in by_idx.items() if len(xs) != 1}
    extra = sorted(i for i in by_idx if not 0 <= i < len(plan))
    if missing: structural_errors.append({"missing_task_indices": missing})
    if duplicate: structural_errors.append({"duplicate_task_indices": duplicate})
    if extra: structural_errors.append({"extra_task_indices": extra})

    ordered = []
    for i, spec in enumerate(plan):
        if len(by_idx.get(i, [])) != 1:
            continue
        r = by_idx[i][0]
        err = []
        if any(r.get(k) != v for k, v in spec.items()): err.append("task_spec_mismatch")
        if r.get("n_tasks_in_plan") != len(plan): err.append("plan_length_mismatch")
        if r.get("freeze_artifact_sha256") != freeze_sha: err.append("freeze_sha_mismatch")
        expected_hash = hashlib.sha256(json.dumps({**spec, "freeze": freeze_sha}, sort_keys=True).encode()).hexdigest()
        if r.get("task_hash") != expected_hash: err.append("task_hash_mismatch")
        if r.get("seed") != int(expected_hash[:8], 16): err.append("seed_mismatch")
        if r.get("status") != "OK": err.append("task_failed")
        if r.get("exit_code") != 0: err.append("nonzero_exit")
        if not isinstance(r.get("raw_result"), dict): err.append("missing_raw_result")
        if err: structural_errors.append({"task_index": i, "path": r.get("_path"), "errors": err})
        ordered.append(r)

    counts = collections.Counter(r.get("verdict", "MISSING") for r in ordered)
    family_counts = {}
    grammar_counts = {}
    cell_counts = {}
    for r in ordered:
        fid = r.get("family"); g = r.get("grammar"); c = r.get("cell"); v = r.get("verdict")
        family_counts.setdefault(fid, collections.Counter())[v] += 1
        grammar_counts.setdefault(g, collections.Counter())[v] += 1
        cell_counts.setdefault(c, collections.Counter())[v] += 1

    def plain(d): return {k: dict(v) if isinstance(v, collections.Counter) else v for k, v in d.items()}

    all_complete = not structural_errors and len(ordered) == len(plan)
    all_green = all_complete and counts.get("K4_RECOVERY_GREEN", 0) == len(plan)
    any_red = counts.get("THEORY_RED", 0) > 0
    any_inconclusive = sum(counts.get(x, 0) for x in ("INCONCLUSIVE_GRAMMAR", "INCONCLUSIVE_SEARCH", "TASK_FAILED")) > 0

    terminal = (
        "K4_EXECUTION_INVALID_STRUCTURAL_ERROR" if structural_errors else
        "K4_REGISTERED_SCOPE_ALL_GREEN__INDEPENDENT_PRIMITIVES_STILL_PENDING" if all_green else
        "K4_REGISTERED_SCOPE_CONTAINS_THEORY_RED" if any_red else
        "K4_REGISTERED_SCOPE_INCONCLUSIVE" if any_inconclusive else
        "K4_REGISTERED_SCOPE_MIXED"
    )

    names = full.get("name_key", {}) if a.reveal_names else {}
    family_summary = {}
    for fid in sorted(freeze["families"]):
        row = dict(family_counts.get(fid, {}))
        if a.reveal_names: row["revealed_name"] = names.get(fid)
        family_summary[fid] = row

    git_shas = sorted(set(r.get("git_commit_sha") for r in ordered if r.get("git_commit_sha")))
    report = {
        "schema": "GMIK4AggregateReceiptV1",
        "freeze_sha256": freeze_sha,
        "expected_tasks": len(plan),
        "receipts_found": len(recs),
        "valid_indexed_receipts": len(ordered),
        "structural_errors": structural_errors,
        "verdict_counts": dict(counts),
        "family_summary": family_summary,
        "grammar_summary": plain(grammar_counts),
        "cell_summary": plain(cell_counts),
        "git_commit_shas_seen": git_shas,
        "all_complete": all_complete,
        "all_green_at_registered_same_author_scope": all_green,
        "contains_theory_red": any_red,
        "contains_inconclusive": any_inconclusive,
        "independence_residue": {
            "IG-4_meter_bucketing": "PENDING_INDEPENDENT_BUCKETING",
            "IG-5_primitive_selection": "PENDING_INDEPENDENT_PRIMITIVES",
        },
        "known_form_global_terminal": False,
        "terminal": terminal,
        "claim_ceiling": "An all-green same-author finite-palette run is K4 evidence only at the frozen engine scope. It cannot self-close IG-4/IG-5, K5 held-family prediction, or real/hardware transfer.",
    }
    os.makedirs(os.path.dirname(a.out_json), exist_ok=True)
    json.dump(report, open(a.out_json, "w"), indent=1, sort_keys=True)

    lines = [
        "# K4 leave-one-family-out aggregate v1", "",
        f"Terminal: `{terminal}`", "",
        f"Expected tasks: **{len(plan)}**; indexed receipts: **{len(ordered)}**; structural errors: **{len(structural_errors)}**.", "",
        "## Verdict counts", "",
    ]
    for k in sorted(counts): lines.append(f"- `{k}`: {counts[k]}")
    lines += ["", "## Families", ""]
    for fid, row in family_summary.items():
        nm = f" — {row.get('revealed_name')}" if a.reveal_names else ""
        vals = ", ".join(f"{k}={v}" for k, v in row.items() if k != "revealed_name") or "no valid receipts"
        lines.append(f"- `{fid}`{nm}: {vals}")
    lines += ["", "## Independence / claim ceiling", "",
              "IG-4 meter bucketing and IG-5 primitive selection remain externally authored gates.",
              "This aggregate never flips the global known-form or no-gap terminals by itself.", ""]
    open(a.out_md, "w").write("\n".join(lines))
    print(json.dumps({"terminal": terminal, "counts": dict(counts), "structural_errors": len(structural_errors), "out_json": a.out_json, "out_md": a.out_md}, sort_keys=True))
    return 0 if not structural_errors else 2


if __name__ == "__main__":
    sys.exit(main())
