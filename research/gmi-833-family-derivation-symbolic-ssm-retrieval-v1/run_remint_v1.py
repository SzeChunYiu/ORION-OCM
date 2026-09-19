"""Remint runner v1 — opaque-token remint invariance (GMI #833, census scope).

BLIND: applies the canonical structure-preserving token remints to the frozen
batteries and re-runs the search at the declared budgets; the RECOVERY
VERDICT (0 errors + clause batteries) must be identical. Remints (canonical
involutions/bijections of the token sets, no family content):

  B_EP   full-token remint pi = transposition (0 1) of D applied to every
         stream token and required output (bijection of the class onto
         itself; key set {1,2} -> {0,2}, miss set to its complement).
  B_CONTR leaf tokens {0,1} -> {-1,1} (disjoint relabel of the two leaf
         symbols; constructor token unchanged; rule table correspondingly
         relabeled; reachability recomputed exactly by the generator).
  B_W2   input-bit complement on truth tables (f -> f(1-u, 1-v)); invariance
         is measured as equal minimal cost across complement-paired tasks
         from the frozen DP results (no new search).

Usage: python3 -B run_remint_v1.py   (writes REMINT_OUTCOME_V1.json)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import proc2_v1 as P2  # noqa: E402
import machinery_v1 as M  # noqa: E402

try:
    import numpy as np
except ImportError:
    np = None

BAT = json.loads((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())

BUDGET_EP = int(__import__("os").environ.get("FDT_REMINT_BUDGET_EP", 1_000_000))
BUDGET_CONTR = int(__import__("os").environ.get(
    "FDT_REMINT_BUDGET_CONTR", 100_000))


def remint_ep():
    """Full-token remint pi = transposition (0 1) of D, applied to EVERY
    stream token and to the required outputs. pi is a bijection of D, so the
    key set {1,2} maps to {0,2} and the miss set maps to its complement —
    the class maps bijectively onto itself and the reminted battery is
    satisfiable by the pi-image of any correct machine."""
    rows = BAT["batteries"]["B_EP"]["task_rows"]
    pi = {v: (1 if v == 0 else (0 if v == 1 else v))
          for v in range(-3, 4)}
    new_rows = []
    for r in rows:
        st = [pi[v] for v in r["stream"]]
        new_rows.append({"stream": st,
                         "required_final_output": pi[
                             r["required_final_output"]],
                         "order": r["order"], "values": r["values"]})
    return new_rows


def remint_contr():
    bc = BAT["batteries"]["B_CONTR"]
    leafmap = {0: -1, 1: 1}
    # recompute reachability exactly under relabeled tokens: import the
    # generator's term machinery and remint its leaf alphabet
    sys.path.insert(0, str(HERE))
    import battery_generate_v1 as G

    orig_all_terms = G.all_terms(3)

    def mint_term(t):
        if isinstance(t, int):
            return leafmap[t]
        return ("N", mint_term(t[1]), mint_term(t[2]))

    U = [mint_term(t) for t in orig_all_terms]
    idx = {t: i for i, t in enumerate(U)}
    two_leaf_orig = [t for t in orig_all_terms if G.term_leaves(t) == 2]
    rules = []
    for l in two_leaf_orig:
        for r in (0, 1):
            rules.append((mint_term(l), leafmap[r]))
    rulesets = [[r0] for r0 in rules]
    for i in range(len(rules)):
        for j in range(i + 1, len(rules)):
            rulesets.append([rules[i], rules[j]])
    assert len(rulesets) == 36

    def enc5(t):
        toks = G.term_tokens(t)
        return toks + [G.PAD] * (5 - len(toks))

    rows = []
    layouts = []
    for t0 in U:
        for rs in rulesets:
            reach = set()
            for lhs, rhs in rs:
                reach |= G.reachable_set(t0, lhs, rhs)
            slot1 = G.term_tokens(rs[0][0]) + [rs[0][1]]
            slot2 = (G.term_tokens(rs[1][0]) + [rs[1][1]]) \
                if len(rs) == 2 else [G.PAD] * 4
            pre = enc5(t0) + slot1 + slot2
            for g in U:
                rows.append([idx[t0], len(rs) - 1, idx[g],
                             1 if g in reach else 0])
                layouts.append(pre + enc5(g))
    return {"task_rows": rows, "task_cell_layouts": layouts,
            "n_tasks": len(rows)}


def remint_w2_pairs(out2):
    """Complement-pair cost equality from the frozen DP per-task results."""
    per = out2["per_task"]
    bw = BAT["batteries"]["B_W2"]
    rows = bw["task_rows"]
    tt_index = {tuple(r["truth_table"]): i for i, r in enumerate(rows)}
    n_pairs = 0
    n_equal = 0
    for i, r in enumerate(rows):
        tt = r["truth_table"]
        # complement both window bits: f(1-u,1-v): reorder truth table
        # (tt order: f(00),f(01),f(10),f(11)) -> f(11),f(10),f(01),f(00)
        ctt = [tt[3], tt[2], tt[1], tt[0]]
        j = tt_index.get(tuple(ctt))
        if j is None or j == i:
            continue
        ci = per.get(str(i))
        cj = per.get(str(j))
        if ci and cj:
            n_pairs += 1
            if ci["cost"] == cj["cost"]:
                n_equal += 1
    return {"pairs_compared": n_pairs, "pairs_equal_cost": n_equal}


def main():
    t0 = time.time()
    out = {"schema": "FDT_REMINT_OUTCOME_V1",
           "benchmark_or_family_data_used": False}
    # B_EP remint search
    rows = remint_ep()
    ts = P2.StreamTaskSet([r["stream"] for r in rows],
                          [r["required_final_output"] for r in rows], "final")
    r_ep = P2.evolve(ts, 0, BUDGET_EP, 8, genome="stream")
    errs = 0
    for r in rows:
        o, _, legal = M.sim_stream(r_ep["genome"], r["stream"])
        if not legal or o is None or o[-1] != r["required_final_output"]:
            errs += 1
    out["B_EP"] = {"budget": BUDGET_EP, "fitness": r_ep["fitness"],
                   "genome": r_ep["genome"], "verified_errors": errs}
    # B_CONTR remint search on the 2000-task frozen-hash subset
    rc = remint_contr()
    n = rc["n_tasks"]
    order = sorted(range(n), key=lambda i: P2.frozen_hash(i))[:2000]
    ts2 = P2.IterTaskSet([rc["task_cell_layouts"][i] for i in order],
                         [rc["task_rows"][i][3] for i in order], 16)
    r_c = P2.evolve(ts2, 0, BUDGET_CONTR, 6, genome="iter", n_in=18,
                    steps=16)
    out["B_CONTR"] = {"budget": BUDGET_CONTR, "n_tasks": n,
                      "fitness": r_c["fitness"], "genome": r_c["genome"]}
    # B_W2 complement-pair invariance from frozen results
    out2 = json.loads((HERE / "BLIND_OUTCOME_V1_T2.json").read_text())
    out["B_W2"] = remint_w2_pairs(out2)
    out["seconds"] = time.time() - t0
    (HERE / "REMINT_OUTCOME_V1.json").write_text(
        json.dumps(out, indent=1, sort_keys=True))
    print("remint done: EP fitness %s (verified errs %d), CONTR fitness %s, "
          "W2 pairs %d/%d equal" % (r_ep["fitness"], errs, r_c["fitness"],
                                    out["B_W2"]["pairs_equal_cost"],
                                    out["B_W2"]["pairs_compared"]))


if __name__ == "__main__":
    main()
