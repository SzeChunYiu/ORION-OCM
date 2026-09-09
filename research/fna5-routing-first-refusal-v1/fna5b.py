"""FNA-5/D7 revival pass 1 (negative-results directive): minimal-information A1B.

V1 scored terminal (frozen run): NO_FUNCTIONAL_PARITY_ROUTING -- no arm met the frozen
sufficiency on protected EVAL. One-stage attribution: the ACQUISITION stage dominates.
Every arm's charged 12-feature extraction (~697/query) is ~11x the entire permissible
budget (1.05 x oracle exec = 61.28) before a single operator runs; even a perfect router
paying the full surface cannot pass. Secondary: declared-only routing's exec penalty
(71.4 vs oracle 58.4) alone also exceeds the budget; the learned arms' pass-floor misses
are operational (A1's declared guard already reaches fp=0.996 without learning).

Lever (frozen in FREEZE_FNA5B_ADDENDUM_V1.json BEFORE this run): shrink the information
contract to the minimum the guarded rule reads -- 24-atom subsampled dispersion +
15-pair subsampled alias, single pass, every counted op charged. World physics still
evaluates on TRUE dispersion/alias: the arm sees only estimates. Also measured: the
perfect-router bound (oracle exec + minimal extraction + minimal inference), i.e. the
least total work ANY information-carrying router could achieve at this contract.

Python 3.8 stdlib only. Deterministic under the frozen salt. Study-only; #71 unchanged.
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import fna5_world as W
from fna5 import (EPS_MARGIN, PASS_FLOOR, FORBIDDEN, evaluate_rows, sufficiency,
                  harness_validation, refresh_records)

SCHEMA = "ocm.fna.fna5-routing-first-refusal.revival1.v1"
SUB_N = 24      # frozen in the addendum
PAIR_N = 15     # frozen in the addendum
ANALYTIC_MARGIN = 0.06  # same frozen margin as A1 v1


def minimal_features(world, q):
    """Minimum information the guarded rule reads, honestly charged per counted op.
    No median (the full extractor bills n for an O(1) median over pre-sorted weights),
    no entropy/counts/skew, no index statistics."""
    rng = random.Random(W.derive_seed("a1b-min-feat", q.qid))
    atoms = list(q.atoms)
    sub = rng.sample(atoms, min(SUB_N, len(atoms)))
    w = [world["weights"][a] for a in sub]
    mean = sum(w) / len(w)
    var = sum((x - mean) ** 2 for x in w) / len(w)
    disp = min(max(math.sqrt(var) / 0.30, 0.0), 1.2)
    work = len(w) + 2 * len(w) + 3          # mean pass, var pass, sqrt+norm+clamp
    pairs = min(PAIR_N, len(atoms) * (len(atoms) - 1) // 2)
    ndup = 0
    for _ in range(pairs):
        a, b = rng.sample(atoms, 2)
        if abs(world["weights"][a] - world["weights"][b]) < 0.02:
            ndup += 1
        work += 3
    alias = ndup / max(pairs, 1)
    work += 2
    return disp, alias, work


def a1b_choice(world, q, insts, disp, alias):
    """The frozen A1 guarded rule, driven by the SUBSAMPLED estimates."""
    state = world["state"]
    work = 2
    target = None
    if disp <= 0.35 - ANALYTIC_MARGIN:
        target = "window"; work += 1
    elif disp >= 0.55 + ANALYTIC_MARGIN and alias <= 0.30 - ANALYTIC_MARGIN:
        target = "deepwindow"; work += 2
    elif 0.42 + ANALYTIC_MARGIN <= disp <= 0.65 - ANALYTIC_MARGIN and alias <= 0.32 - ANALYTIC_MARGIN:
        target = "sample"; work += 3
    exact = min((it for it in insts if it.family in W.EXACT_FAMILIES),
                key=lambda it: (it.declared_cost_estimate(q, state), it.op_id))
    exact_cost = exact.declared_cost_estimate(q, state)
    work += 3
    if target is not None:
        cand = W.cheapest(insts, q, state, target)
        if cand is not None:
            work += 3
            if cand.declared_cost_estimate(q, state) < exact_cost:
                return cand, work
    return exact, work


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tiny", action="store_true")
    args = ap.parse_args()
    t0 = time.perf_counter()
    params = W.WorldParams.tiny_params() if args.tiny else W.WorldParams()
    world = W.build_world(params)
    queries = [W.make_query(world, i) for i in range(params.n_queries)]
    if not harness_validation(world, queries[:60]):
        args.out.write_text(json.dumps({"schema": SCHEMA,
                                        "terminal": "CANNOT_CHECK_HARNESS_DISAGREES_WITH_NAIVE_SCAN"}))
        return
    records, oracle_diag = refresh_records(world, queries)
    ev = [r for r in records if W.split_of(r["qid"]) == "EVAL"]
    oracle_exec_mean = sum(r["oracle_exec"] for r in ev) / len(ev)
    budget = (1.0 + EPS_MARGIN) * oracle_exec_mean

    def row_a1b(rec):
        q = rec["query"]
        disp, alias, feat_work = minimal_features(world, q)
        choice, inf = a1b_choice(world, q, rec["insts"], disp, alias)
        return W.run_arm_choice(world, q, rec["insts"], choice, inf, feat_work)

    block = evaluate_rows(world, ev, "A1B_MINIMAL_INFO", row_a1b)
    s = sufficiency(block, oracle_exec_mean)
    min_feat_mean = sum(minimal_features(world, r["query"])[2] for r in ev) / len(ev)
    full_feat_mean = sum(r["query"].feature_work for r in ev) / len(ev)
    perfect_bound = oracle_exec_mean + min_feat_mean + 2      # minimal inference = 2 ops
    baseline_mean = evaluate_rows(
        world, ev, "BASELINE_INCUMBENT",
        lambda rec: W.run_baseline(world, rec["query"], rec["insts"]))["mean_total_work"]

    if s["sufficient"]:
        verdict = "A1B_SUFFICIENT: v1 terminal superseded -> PARENT_SUFFICIENT_FOR_ROUTING (analytic/guarded rule, minimal information contract)"
    elif perfect_bound > budget:
        verdict = ("STRUCTURAL_OBSTRUCTION_PROVEN: perfect-router bound %.2f > budget %.2f; "
                   "the minimum information price of safe routing exceeds the whole budget "
                   "(and the routing residual itself: decision value %.2f/query). Study "
                   "terminal stays NO_FUNCTIONAL_PARITY_ROUTING; mechanism ACQUISITION_COST_DOMINATES."
                   % (perfect_bound, budget, baseline_mean - oracle_exec_mean))
    else:
        verdict = ("A1B insufficient but the perfect-router bound %.2f <= budget %.2f: "
                   "obstruction NOT proven structural; lane needs another lever"
                   % (perfect_bound, budget))

    receipt = {
        "schema": SCHEMA, "salt": W.SALT, "parent_run": "FNA5_RESULTS_V1.json",
        "addendum": "FREEZE_FNA5B_ADDENDUM_V1.json",
        "oracle_exec_mean_EVAL": round(oracle_exec_mean, 2),
        "budget": round(budget, 2),
        "A1B_EVAL": block,
        "A1B_sufficiency": s,
        "minimal_feature_work_mean": round(min_feat_mean, 2),
        "full_feature_work_mean_v1": round(full_feat_mean, 2),
        "perfect_router_bound": {"rule": "oracle exec + minimal extraction + 2 ops inference",
                                 "work": round(perfect_bound, 2),
                                 "exceeds_budget": bool(perfect_bound > budget)},
        "decision_value_vs_baseline": round(baseline_mean - oracle_exec_mean, 2),
        "baseline_mean_total": round(baseline_mean, 2),
        "verdict": verdict,
        "gate_71": "LEARNED_ROUTER_NOT_YET_AUTHORIZED (unchanged; study-only, nothing deployed)",
        "host": {"python": platform.python_version(), "platform": platform.platform()},
        "wall_seconds": round(time.perf_counter() - t0, 3),
    }
    blob = json.dumps(receipt, indent=2) + "\n"
    for bad in FORBIDDEN:
        assert bad not in blob, "FORBIDDEN_CLAIM_IN_RECEIPT"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(blob)
    print(json.dumps({"output": str(args.out), "verdict": verdict[:120]}))


if __name__ == "__main__":
    main()
