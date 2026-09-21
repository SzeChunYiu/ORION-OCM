"""Isolate the K05 reachability mismatch: stored battery vs generator-recompute
vs my reach_dist. Output small."""
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/billy/fdt-k58-revive/ORION-OCM/research/gmi-833-family-derivation-symbolic-ssm-retrieval-v1")
import battery_generate_v1 as G

bat = json.load(open("/home/billy/fdt-k58-revive/ORION-OCM/research/gmi-833-family-derivation-symbolic-ssm-retrieval-v1/NEUTRAL_BATTERY_FREEZE_V1.json"))
bc = bat["batteries"]["B_CONTR"]
rows = bc["task_rows"]
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

# exact generator recompute of y for every row
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
                ntk = tuple(term_tokens_l(new))
                if ntk in UT:
                    outs.add(UT.index(ntk))
    return outs

def term_tokens_l(x):
    if isinstance(x, int):
        return [x]
    return [2] + term_tokens_l(x[1]) + term_tokens_l(x[2])

def reach_dist(t0i, rule_ids):
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

# generator-exact: use the battery generator module itself
gen_rows = G.contr_battery()
gr = gen_rows["task_rows"]
assert len(gr) == len(rows)
mismatch_gen = sum(1 for i in range(len(rows)) if gr[i][3] != rows[i][3])
print("stored vs generator-recompute mismatches:", mismatch_gen)

# my reach_dist vs stored
bad = []
for i in range(len(rows)):
    t0i, rsi, gi, y = rows[i]
    rids = [x[0] for x in bc["rule_set_table"][rsi]]
    rd = reach_dist(t0i, rids)
    ym = 1 if gi in rd else 0
    if ym != y:
        bad.append((i, t0i, rsi, gi, y, ym, len(rd)))
        if len(bad) >= 5:
            break
print("my reach_dist mismatches (first 5):", bad)
# check rsi indexing: is rows[i][1] a rule_set index or set_flag?
from collections import Counter
c = Counter(r[1] for r in rows)
print("distribution of rows[i][1]:", dict(c))
print("rule_set_table len:", len(bc["rule_set_table"]))
print("n rows with each rsi in rule_set_table order check: first 10 rows[r][0:3]:", [tuple(r[:3]) for r in rows[:10]])
