"""K05 analysis v1 — exact census of B_CONTR positives by (t0 shape, g shape,
distance) plus the V2 [t0==g] reflexive witness errors by the same census, and
a validation of my reading of the committed witness machine semantics.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import battery_generate_v1 as G
import posthoc_adjudicate_v1 as A

def toks2term(tk):
    tk = [int(t) for t in tk if t != -1]
    it = iter(tk)
    def go():
        nx = next(it)
        if nx == 2:
            return ["N", go(), go()]
        return nx
    return go()

def shape(t):
    if isinstance(t, int):
        return "leaf"
    a, b = t[1], t[2]
    if isinstance(a, int) and isinstance(b, int):
        return "N2"
    if isinstance(a, int):
        return "NLH"   # N(a, N(b,c))
    return "NRH"       # N(N(a,b), c)

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
    while frontier and d < 4:
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

census = {}
werr = {}
wfps = {}
for i in range(n):
    lay = layouts[i]
    t0 = toks2term(lay[0:5]); g = toks2term(lay[13:18])
    rules = decode_rules(lay)
    d = min_dist(t0, g, rules)
    sh = "%s->%s" % (shape(t0), shape(g))
    if rows[i][3] == 1:
        census.setdefault("d%d %s" % (d, sh), 0)
        census["d%d %s" % (d, sh)] += 1
    m1 = json.loads((HERE / "REVIVAL_V2.json").read_text())
    m1 = m1["rows"]["Symbolic logic systems."]["constructive_witness"]["machine"]
    cells, _, lg = A.run_iter(m1, lay)
    pred = cells[m1["output_cell"]] if lg else None
    if pred != rows[i][3]:
        if rows[i][3] == 1:
            werr.setdefault(sh, 0)
            werr[sh] += 1
        else:
            wfps.setdefault(sh, 0)
            wfps[sh] += 1

print("N_TASKS", n)
print("CENSUS_POS_BY_DIST_SHAPE")
for k in sorted(census):
    print(" ", k, census[k])
print("REFLEXIVE_WITNESS_MISSED_POS")
for k in sorted(werr):
    print(" ", k, werr[k])
print("REFLEXIVE_WITNESS_FALSE_POS")
for k in sorted(wfps):
    print(" ", k, wfps[k])
print("TOTAL_MISSED", sum(werr.values()), "TOTAL_FP", sum(wfps.values()))

# shape distribution of rules
from collections import Counter
rc = Counter()
for i in range(n):
    for lhs, rhs in decode_rules(layouts[i]):
        rc[shape(lhs)] += 1
print("RULE_LHS_SHAPES", dict(rc))
