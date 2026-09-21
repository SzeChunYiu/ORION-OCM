"""K05 revival v3 - B_CONTR reachability structure (GMI #833).
rows[i][1] is a SET_FLAG (0=single,1=pair), NOT a rule-set index. Rules are
reconstructed from the 18-cell layout: t0=cells0:5, lhs1=5:8,rhs1=8,
lhs2=9:12,rhs2=12 (absent if cell9==-1), g=13:18. Decomposes positives by
min-step reachability distance and the reflexive witness errors by distance.
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

def toks2term(tk):
    it = iter(tk)
    def go():
        nx = next(it)
        if nx == 2:
            return ["N", go(), go()]
        return nx
    return go()

def tup(x):
    if isinstance(x, int):
        return x
    return (tup(x[1]), tup(x[2]))

def decode(sl):
    toks = [int(v) for v in sl]
    if toks[0] == -1:
        return None
    return tup(toks2term(toks))

def subterms(x):
    if isinstance(x, int):
        return [x]
    return [x] + subterms(x[1]) + subterms(x[2])

def replace(x, old, new):
    if x == old:
        return new
    if isinstance(x, int):
        return x
    return (replace(x[1], old, new), replace(x[2], old, new))

def one_step(t0, rules):
    outs = set()
    for lhs, rhs in rules:
        for st in subterms(t0):
            if st == lhs:
                outs.add(replace(t0, st, rhs))
    return outs

def reach_map(t0, rules):
    d = {t0: 0}
    frontier = [t0]
    step = 0
    while frontier:
        step += 1
        nxt = []
        for t in frontier:
            for u in one_step(t, rules):
                if u not in d:
                    d[u] = step
                    nxt.append(u)
        frontier = nxt
    return d

def rules_of(i):
    lhs1 = decode(layouts[i][5:8]); rhs1 = decode([layouts[i][8]])
    rules = [(lhs1, rhs1)]
    lhs2 = decode(layouts[i][9:12])
    if lhs2 is not None:
        rules.append((lhs2, decode([layouts[i][12]])))
    return rules

pos_by_dist = {0: 0, 1: 0, 2: 0, "ge3": 0}
mismatch = 0
for i, r in enumerate(rows):
    t0 = decode(layouts[i][0:5])
    g = decode(layouts[i][13:18])
    rm = reach_map(t0, rules_of(i))
    d = rm.get(g)
    if r[3] == 1:
        k = "ge3" if (d is None or d >= 3) else d
        pos_by_dist[k] += 1
        if d is None:
            mismatch += 1
    else:
        if d is not None:
            mismatch += 1
print("positives_by_minstep", pos_by_dist, "truth_mismatch", mismatch, "n", len(rows))

rev = json.loads((HERE / "REVIVAL_V2.json").read_text())
m1 = rev["rows"]["Symbolic logic systems."]["constructive_witness"]["machine"]
errs_by_dist = {0: 0, 1: 0, 2: 0, "neg": 0}
for i, r in enumerate(rows):
    cells, _, lg = A.run_iter(m1, layouts[i])
    pred = cells[m1["output_cell"]] if lg else None
    if pred != r[3]:
        if r[3] == 0:
            errs_by_dist["neg"] += 1
        else:
            d = reach_map(decode(layouts[i][0:5]), rules_of(i)).get(
                decode(layouts[i][13:18]))
            errs_by_dist[d if d in (0, 1, 2) else 2] += 1
print("reflexive_full_errors_by_dist", errs_by_dist)
