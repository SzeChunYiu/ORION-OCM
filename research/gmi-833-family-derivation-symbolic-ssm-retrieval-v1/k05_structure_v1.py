"""K05 revival v3 — B_CONTR ground-truth reachability structure (GMI #833).

Recomputes the exact reachability relation of the frozen B_CONTR class from
the battery generator semantics (terms, 8 constant contractions, 36 rule
sets, up to 2-step chains) and decomposes the V2 reflexive witness [t0==g]
errors by reachability distance. Tells us the exact structure a full solver
must cover (0-step / 1-step / 2-step positives), and how far the reflexive
witness is from full reachability.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import machinery_v1 as M
import posthoc_adjudicate_v1 as A

bat = json.loads((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
bc = bat["batteries"]["B_CONTR"]
rows = bc["task_rows"]
layouts = bc["task_cell_layouts"]
U = bc["universe_tokens"]
rt = bc["rule_table"]
UT = [tuple(t) for t in U]

def toks2term(tk):
    it = iter(tk)
    def go():
        nx = next(it)
        if nx == 2:
            return ["N", go(), go()]
        return nx
    return go()

def term_tokens(x):
    if isinstance(x, int):
        return [x]
    return [2] + term_tokens(x[1]) + term_tokens(x[2])

def one_step_ids(t_idx, rule_ids):
    term = toks2term(U[t_idx])
    outs = set()
    def subterms(x):
        if isinstance(x, int):
            return [x]
        return [x] + subterms(x[1]) + subterms(x[2])
    def replace(x, old, new):
        if x == old:
            return new
        if isinstance(x, int):
            return x
        return ["N", replace(x[1], old, new), replace(x[2], old, new)]
    for ri in rule_ids:
        lhs, rhs = rt[ri]
        lhs_term = toks2term(U[lhs])
        for st in subterms(term):
            if st == lhs_term:
                new = replace(term, st, rhs)
                ntk = tuple(term_tokens(new))
                if ntk in UT:
                    outs.add(UT.index(ntk))
    return outs

def reach_dist(t0i, rule_ids):
    """min distance from t0 to each reachable term index (0,1,2)."""
    d = {t0i: 0}
    l1 = {}
    for u in one_step_ids(t0i, rule_ids):
        l1.setdefault(u, 1)
    for u in l1:
        d.setdefault(u, 1)
    for u in list(l1):
        for w in one_step_ids(u, rule_ids):
            if w not in d:
                d[w] = 2
    return d

# ground truth over the battery enumeration order (mirror the generator)
truth = []
for t0i in range(len(U)):
    for rsi in range(len(bc["rule_set_table"])):
        rids = [x[0] for x in bc["rule_set_table"][rsi]]
        rd = reach_dist(t0i, rids)
        for gi in range(len(U)):
            truth.append((t0i, rsi, gi, 1 if gi in rd else 0))
assert len(truth) == len(rows)
assert all(truth[i][3] == rows[i][3] for i in range(len(rows))), "truth mismatch"

pos = [i for i in range(len(rows)) if rows[i][3] == 1]
print("total tasks", len(rows), "positives", len(pos),
      "positives_by_dist",
      {k: sum(1 for i in pos if reach_dist(rows[i][0], [x[0] for x in bc["rule_set_table"][rows[i][1]]]).get(rows[i][2], 99) == k)
       for k in (0, 1, 2)})

# V2 reflexive witness error decomposition
rev = json.loads((HERE / "REVIVAL_V2.json").read_text())
m1 = rev["rows"]["Symbolic logic systems."]["constructive_witness"]["machine"]
n = len(rows)
dist_truth = []
pred = []
for i in range(n):
    cells, _, lg = A.run_iter(m1, layouts[i])
    p = cells[m1["output_cell"]] if lg else None
    pred.append(p)
    dist_truth.append(reach_dist(rows[i][0], [x[0] for x in bc["rule_set_table"][rows[i][1]]]).get(rows[i][2], 99))
idx = sorted(range(n), key=lambda i: P.frozen_hash(i))
sub = set(idx[:2000])
errs = 0
by_dist = {0: 0, 1: 0, 2: 0, "neg": 0}
errs_sub = 0
by_dist_sub = {0: 0, 1: 0, 2: 0, "neg": 0}
for i in range(n):
    if pred[i] != rows[i][3]:
        errs += 1
        if rows[i][3] == 0:
            by_dist["neg"] += 1
        else:
            by_dist[dist_truth[i]] += 1
        if i in sub:
            errs_sub += 1
            if rows[i][3] == 0:
                by_dist_sub["neg"] += 1
            else:
                by_dist_sub[dist_truth[i]] += 1
print("reflexive full errs", errs, "by_dist", by_dist)
print("reflexive subset errs", errs_sub, "by_dist", by_dist_sub)
# how many errors would a 0+1-step solver have (i.e. dist-2 positives)?
d2_full = sum(1 for i in range(n) if rows[i][3] == 1 and dist_truth[i] == 2)
d2_sub = sum(1 for i in sub if rows[i][3] == 1 and dist_truth[i] == 2)
print("dist-2 positives full", d2_full, "subset", d2_sub)
