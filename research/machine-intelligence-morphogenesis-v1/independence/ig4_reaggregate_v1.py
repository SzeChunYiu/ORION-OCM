#!/usr/bin/env python3
"""RV-377-160 IG-4 comparison: independent-meter buckets vs native V4 buckets on the protected K4 V7 set.

Inputs: k4_v7_native_buckets_v1.json (native buckets + verdict inputs) and the blind meter's output
(GMIIG4IndependentBucketsV1). Output: IG4_INDEPENDENT_METER_AGREEMENT_<host>.json.

Verdict re-aggregation reproduces the V4/V5 cell adjudication with the property vectors swapped for the
independent buckets and every cost, score, control and budget input held fixed. The re-implementation is
validated first by re-deriving the native verdicts from the native buckets: any mismatch aborts.
"""
from __future__ import annotations

import collections
import hashlib
import json
import platform
import sys

AXES = ("state_scales_with", "serve_scales_with", "update_locality", "routing", "sharing",
        "retrieval", "serve_iterations", "stochastic_serve", "verifier_gated", "external_authority")
MEASURED_AXES = ("state_scales_with", "serve_scales_with", "update_locality", "routing", "verifier_gated", "external_authority")
DECLARED_AXES = ("sharing", "retrieval", "serve_iterations", "stochastic_serve")
VOCAB = {
    "update_locality": {"none", "local", "global"}, "routing": {"none", "input_dependent"},
    "sharing": {"shared", "unshared"}, "retrieval": {"none", "exact_key", "metric"},
    "serve_iterations": {"one", "many"}, "stochastic_serve": {True, False},
    "verifier_gated": {True, False}, "external_authority": {True, False},
}


def adjudicate(task: dict, vec_of, threshold: float) -> str:
    """V5 cell verdict with property vectors supplied by `vec_of(ref)`."""
    target = task["target_vector"]
    if not task["controls_recovered"]:
        return "INCONCLUSIVE_GRAMMAR"
    wit = task["witness"]
    if wit is None:
        return "INCONCLUSIVE_GRAMMAR"
    witness_ok = vec_of(wit["ref"]) == target and wit["semantic_score"] >= threshold
    wc = wit["scalar_lifecycle_cost"]
    adm = [n for n in task["nulls"] if n["admissible"]]
    if adm and witness_ok:
        best = min(adm, key=lambda n: (n["scalar_lifecycle_cost"], n["null_id"]))
        if best["scalar_lifecycle_cost"] + 1e-12 < wc:
            return "THEORY_RED_NULL_DOMINATES"
    if not witness_ok:
        return "INCONCLUSIVE_GRAMMAR"
    win = task["winner"]
    if win is None:
        return "INCONCLUSIVE_SEARCH"
    if vec_of(win["ref"]) != target:
        return "THEORY_RED" if win["scalar_lifecycle_cost"] + 1e-12 < wc else "INCONCLUSIVE_SEARCH"
    tw = task["twin"]
    if tw is None:
        return "INCONCLUSIVE_SEARCH"
    if vec_of(tw["ref"]) == target:
        return "THEORY_RED"
    if not task["budget_met"]:
        return "INCONCLUSIVE_SEARCH"
    return "K4_RECOVERY_GREEN"


def main() -> int:
    native_path, ind_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    native = json.load(open(native_path))
    ind = json.load(open(ind_path))
    if ind.get("schema") != "GMIIG4IndependentBucketsV1":
        raise SystemExit("independent file has wrong schema")
    nat_c = native["candidates"]
    buckets = ind["buckets"]
    missing = sorted(r for r in nat_c if r not in buckets)
    if missing:
        raise SystemExit(f"independent buckets missing {len(missing)} refs, first {missing[:3]}")

    def nat_vec(ref):
        return nat_c[ref]["native_vector"]

    # validate the re-implementation against the receipts' own verdicts (fail closed)
    for t in native["tasks"]:
        v = adjudicate(t, nat_vec, native["threshold"])
        if v != t["native_verdict"]:
            raise SystemExit(f"re-adjudication mismatch on task {t['task_index']}: {v} != {t['native_verdict']}")

    # bucket validity + per-axis agreement
    invalid = collections.Counter()
    agree = {pop: {a: [0, 0] for a in AXES} for pop in ("all", "winner", "witness", "twin", "null")}
    confusion = {a: collections.Counter() for a in AXES}
    for ref, nc in nat_c.items():
        b = buckets[ref]
        for a in AXES:
            iv = b.get(a, "MISSING")
            if a in VOCAB and iv not in VOCAB[a]:
                invalid[a] += 1
            ok = (iv == nc["native_vector"][a])
            for pop in ("all", nc["role"]):
                agree[pop][a][0] += int(ok)
                agree[pop][a][1] += 1
            if not ok:
                confusion[a][f"native={nc['native_vector'][a]} | independent={iv}"] += 1
    rates = {pop: {a: (c[0] / c[1] if c[1] else None) for a, c in d.items()} for pop, d in agree.items()}

    def ind_vec(ref):
        b = buckets[ref]
        return {a: b.get(a) for a in AXES}

    transitions = collections.Counter()
    moved = []
    ind_counts = collections.Counter()
    for t in native["tasks"]:
        v = adjudicate(t, ind_vec, native["threshold"])
        ind_counts[v] += 1
        transitions[f"{t['native_verdict']} -> {v}"] += 1
        if v != t["native_verdict"]:
            moved.append({"task_index": t["task_index"], "family": t["family"], "grammar": t["grammar"], "cell": t["cell"],
                          "native": t["native_verdict"], "independent": v})
    n_axes_ge80_all = sum(1 for a in AXES if rates["all"][a] is not None and rates["all"][a] >= 0.80)
    n_axes_ge80_win = sum(1 for a in AXES if rates["winner"][a] is not None and rates["winner"][a] >= 0.80)
    n_meas_ge80 = sum(1 for a in MEASURED_AXES if rates["all"][a] >= 0.80)
    scaling_ok = all(rates["all"][a] >= 0.80 for a in ("state_scales_with", "serve_scales_with"))
    greens = ind_counts.get("K4_RECOVERY_GREEN", 0)
    p1a = n_axes_ge80_all >= 8 and greens == 0
    p1b = n_meas_ge80 >= 4 and scaling_ok and greens == 0
    rep = {
        "schema": "GMIIG4IndependentMeterAgreementV1",
        "revival_id": "RV-377-160",
        "label": "HUMAN_GATE_BYPASSED__MODEL_PROXY",
        "served_model_asserted_by_blind_author": ind.get("served_model"),
        "host": platform.node(), "python": platform.python_version(),
        "inputs": {"native_sha256": hashlib.sha256(open(native_path, "rb").read()).hexdigest(),
                   "independent_sha256": hashlib.sha256(open(ind_path, "rb").read()).hexdigest()},
        "n_candidates": len(nat_c), "n_tasks": len(native["tasks"]),
        "reimplementation_reproduces_native_verdicts": True,
        "invalid_bucket_values_per_axis": dict(invalid),
        "agreement_counts": agree, "agreement_rates": rates,
        "disagreement_confusion": {a: dict(c.most_common(12)) for a, c in confusion.items() if c},
        "native_verdict_counts": dict(collections.Counter(t["native_verdict"] for t in native["tasks"])),
        "independent_verdict_counts": dict(ind_counts),
        "verdict_transitions": dict(transitions), "verdict_moves": moved,
        "cells_flipped_to_green": greens,
        "P1_axes_ge_80pct_all_candidates": n_axes_ge80_all,
        "P1_axes_ge_80pct_winners": n_axes_ge80_win,
        "P1b_measured_axes_ge_80pct": n_meas_ge80, "P1b_both_scaling_axes_ge_80pct": scaling_ok,
        "P1_HELD": p1a, "P1b_HELD": p1b,
        "independent_rules": ind.get("rules"),
    }
    json.dump(rep, open(out_path, "w"), indent=1, sort_keys=True)
    print(json.dumps({"P1_HELD": p1a, "P1b_HELD": p1b, "greens": greens, "axes_ge80_all": n_axes_ge80_all,
                      "rates_all": {a: round(rates["all"][a], 4) for a in AXES}, "moves": len(moved)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
