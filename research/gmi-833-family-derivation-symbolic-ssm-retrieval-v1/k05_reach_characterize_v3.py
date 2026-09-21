"""K05 revival v3 - reachability structure of the frozen B_CONTR battery.

Decodes every frozen task layout into (t0, rule set, goal) with the generator
semantics (battery_generate_v1), recomputes the min-step reachability distance
with the generator's own one_step, cross-checks the frozen y, and reports:
  - positives by min-step distance (0/1/2) full battery + frozen 2000-subset;
  - the V2 reflexive [t0==g] witness errors by distance and by goal leaf count.
Output: k05_reach_characterize_v3.json  (tiny stdout)
"""
from __future__ import annotations
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import battery_generate_v1 as G
import posthoc_adjudicate_v1 as A
import proc2_v1 as P2

def toks2term(tk):
    tk = [int(t) for t in tk if t != -1]
    it = iter(tk)
    def go():
        nx = next(it)
        if nx == 2:
            return ["N", go(), go()]
        return nx
    return go()

def term_leaf_count(t):
    if isinstance(t, int):
        return 1
    return term_leaf_count(t[1]) + term_leaf_count(t[2])

def decode_rules(layout):
    rules = [(toks2term(layout[5:8]), int(layout[8]))]
    if int(layout[9]) != -1:
        rules.append((toks2term(layout[9:12]), int(layout[12])))
    return rules

def min_dist(t0, g, rules):
    if t0 == g:
        return 0
    seen = {t0}
    frontier = [t0]
    d = 0
    while frontier and d < 3:
        d += 1
        nxt = []
        for t in frontier:
            for lhs, rhs in rules:
                for u in G.one_step(t, lhs, rhs):
                    if u == g:
                        return d
                    if u not in seen:
                        seen.add(u)
                        nxt.append(u)
        frontier = nxt
    return None

bat = json.loads((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
bc = bat["batteries"]["B_CONTR"]
rows = bc["task_rows"]
layouts = bc["task_cell_layouts"]
n = len(rows)
idx = sorted(range(n), key=lambda i: P2.frozen_hash(i))
sub = set(idx[:2000])

dist = [None] * n
t0leaf = [0] * n
gleaf = [0] * n
mism = 0
for i in range(n):
    lay = layouts[i]
    t0 = toks2term(lay[0:5]); g = toks2term(lay[13:18])
    d = min_dist(t0, g, decode_rules(lay))
    dist[i] = d
    t0leaf[i] = term_leaf_count(t0); gleaf[i] = term_leaf_count(g)
    if (rows[i][3] == 1) != (d is not None):
        mism += 1

def pos_dist_counts(ids):
    c = {0: 0, 1: 0, 2: 0}
    for i in ids:
        if rows[i][3] == 1:
            c[dist[i]] += 1
    return c

full = list(range(n))
subset = list(sub)
out = {
    "schema": "K05_REACH_CHARACTERIZE_V3",
    "n_tasks": n,
    "truth_mismatch": mism,
    "positives_full_by_dist": pos_dist_counts(full),
    "positives_subset_by_dist": pos_dist_counts(subset),
    "negatives_full": n - sum(pos_dist_counts(full).values()),
    "negatives_subset": len(subset) - sum(pos_dist_counts(subset).values()),
    "one_tasks_full_by_t0g_leaf": {},
    "one_tasks_subset_by_t0g_leaf": {},
}
# dist-1/dist-2 positives: (t0leaf, gleaf) census
for tag, ids in (("full", full), ("subset", subset)):
    census = {}
    for i in ids:
        if rows[i][3] == 1 and dist[i] in (1, 2):
            k = "d%d_t0%d_g%d" % (dist[i], t0leaf[i], gleaf[i])
            census[k] = census.get(k, 0) + 1
    out["one_tasks_%s_by_t0g_leaf" % tag] = census

# V2 reflexive witness errors by distance and goal leaf count
rev = json.loads((HERE / "REVIVAL_V2.json").read_text())
m1 = rev["rows"]["Symbolic logic systems."]["constructive_witness"]["machine"]
errs_by = {"missed_pos_d0": 0, "missed_pos_d1": 0, "missed_pos_d2": 0,
           "false_pos": 0}
errs_by_gleaf = {}
for i in full:
    cells, _, lg = A.run_iter(m1, layouts[i])
    pred = cells[m1["output_cell"]] if lg else None
    if pred != rows[i][3]:
        if rows[i][3] == 1:
            errs_by["missed_pos_d%d" % dist[i]] += 1
            errs_by_gleaf.setdefault("pos_g%d" % gleaf[i], 0)
            errs_by_gleaf["pos_g%d" % gleaf[i]] += 1
        else:
            errs_by["false_pos"] += 1
            errs_by_gleaf.setdefault("neg_g%d" % gleaf[i], 0)
            errs_by_gleaf["neg_g%d" % gleaf[i]] += 1
out["reflexive_witness_errors_by_dist"] = errs_by
out["reflexive_witness_errors_by_gleaf"] = errs_by_gleaf
out["reflexive_witness_full_errors"] = sum(errs_by.values())

(HERE / "k05_reach_characterize_v3.json").write_text(json.dumps(out, indent=1))
print("K05_CHARACTERIZE_DONE n", n, "mism", mism)
print("pos_full_by_dist", out["positives_full_by_dist"])
print("pos_subset_by_dist", out["positives_subset_by_dist"])
print("reflexive_errors", out["reflexive_witness_errors_by_dist"])
print("one_tasks_full_t0g_leaf", out["one_tasks_full_by_t0g_leaf"])
