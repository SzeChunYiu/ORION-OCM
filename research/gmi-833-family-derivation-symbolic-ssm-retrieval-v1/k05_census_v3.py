"""K05 revival v3-c — B_CONTR positive census (GMI #833).

For every positive task in the full frozen battery (1176 pos) and in the
frozen 2000-task subset (133 pos):
  - t0 shape / g shape / rule-set size / min-step distance (0/1/2);
  - for one-step positives: which rule (1 / 2 / both) fires to produce g;
  - for two-step positives: the exact contraction chain (rule1 then rule2).
Cross-checks the committed characterization: reflexive witness [t0==g]
errors 45 subset / 384 full, 0 false positives. Also verifies a compact
1-cell reflexive machine (dummy-free) behaves identically.
Output: k05_census_v3.json
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
            return ("N", go(), go())
        return nx
    return go()


def tup(x):
    if isinstance(x, int):
        return x
    return ("N", tup(x[1]), tup(x[2]))


def shape(t):
    if isinstance(t, int):
        return "L"
    a, b = t[1], t[2]
    if isinstance(a, int) and isinstance(b, int):
        return "2"
    if isinstance(a, int):
        return "3R"
    return "3L"


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


def chain_of(t0, g, rules):
    """Return a (r1, r2) rule index sequence reaching g, or None."""
    if t0 == g:
        return []
    for i1, (l1, r1) in enumerate(rules):
        for u in G.one_step(t0, l1, r1):
            if u == g:
                return [i1]
            for i2, (l2, r2) in enumerate(rules):
                for w in G.one_step(u, l2, r2):
                    if w == g:
                        return [i1, i2]
    return None


bat = json.loads((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
bc = bat["batteries"]["B_CONTR"]
rows = bc["task_rows"]
layouts = bc["task_cell_layouts"]
n = len(rows)
idx = sorted(range(n), key=lambda i: P2.frozen_hash(i))
sub = set(idx[:2000])

rev = json.loads((HERE / "REVIVAL_V2.json").read_text())
m1 = rev["rows"]["Symbolic logic systems."]["constructive_witness"]["machine"]

census = {"one": {"3R->2": 0, "3L->2": 0, "2->L": 0, "other": 0},
          "two": {"3R->2->L": 0, "3L->2->L": 0, "other": 0},
          "refl": 0}
pos_detail = []
sub_pos_detail = []
w_errs_sub = 0
w_errs_full = 0
w_fp = 0
for i in range(n):
    lay = layouts[i]
    t0 = tup(toks2term(lay[0:5])); g = tup(toks2term(lay[13:18]))
    rules = decode_rules(lay)
    if rows[i][3] == 1:
        d = min_dist(t0, g, rules)
        ch = chain_of(t0, g, rules)
        sh = "%s->%s" % (shape(t0), shape(g))
        if d == 0:
            census["refl"] += 1
        elif d == 1:
            key = sh if sh in census["one"] else "other"
            census["one"][key] += 1
        elif d == 2:
            key = sh if sh in census["two"] else "other"
            census["two"][key] += 1
        rec = {"i": i, "t0": t0, "g": g, "sh": sh, "d": d, "chain": ch,
               "rules": rules, "in_sub": i in sub,
               "rules_n": len(rules)}
        pos_detail.append(rec)
        if i in sub:
            sub_pos_detail.append(rec)
    cells, _, lg = A.run_iter(m1, lay)
    pred = cells[m1["output_cell"]] if lg else None
    if pred != rows[i][3]:
        if rows[i][3] == 1:
            w_errs_full += 1
            if i in sub:
                w_errs_sub += 1
        else:
            w_fp += 1

# compact reflexive machine (dummy-free, 1 work cell) behaviour
def mism(i):
    return ["add",
            ["un", "GE+0", ["add", ["atom", "s%d" % i],
                            ["un", "NEG", ["atom", "s%d" % (13 + i)]]]],
            ["un", "GE+0", ["add", ["atom", "s%d" % (13 + i)],
                            ["un", "NEG", ["atom", "s%d" % i]]]]]

o = mism(0)
for k in (1, 2, 3, 4):
    o = ["un", "GE+1", ["add", o, mism(k)]]
reflexive = ["un", "GE+0", ["add", ["const", 1], ["un", "NEG", o]]]
m2 = {"model": "M_ITER", "input_cells": 18,
      "update": [reflexive] + [["atom", "s18"]] * 5,
      "output_cell": 18, "steps": 16, "rho": 1}
import machinery_v1 as M
c2_errs_sub = 0
c2_errs_full = 0
c2_fp = 0
for i in range(n):
    cells, _, lg = A.run_iter(m2, layouts[i])
    pred = cells[18] if lg else None
    if pred != rows[i][3]:
        if rows[i][3] == 1:
            c2_errs_full += 1
            if i in sub:
                c2_errs_sub += 1
        else:
            c2_fp += 1

out = {
    "schema": "K05_CENSUS_V3",
    "n_tasks": n,
    "positives_full": (sum(census["one"].values())
                          + sum(census["two"].values())
                          + census["refl"]),
    "positives_subset": len(sub_pos_detail),
    "census": census,
    "reflexive_witness": {"subset_errors": w_errs_sub,
                          "full_errors": w_errs_full, "false_pos": w_fp},
    "compact_reflexive": {"subset_errors": c2_errs_sub,
                          "full_errors": c2_errs_full, "false_pos": c2_fp,
                          "cost": M.machine_cost(m2),
                          "work_cells": 6,
                          "identical_behavior": (c2_errs_sub == w_errs_sub
                                                 and c2_errs_full == w_errs_full
                                                 and c2_fp == w_fp)},
    "one_step_rules_fired": {},
    "one_step_subset_shapes": {},
    "two_step_chains": [],
    "sub_pos_detail": sub_pos_detail[:40],
}
# which rule fired for one-step positives, and g leaf/value census
from collections import Counter
rf = Counter()
osub_shapes = Counter()
two_chains = []
for r in pos_detail:
    if r["d"] == 1:
        rf["%s" % "+".join(str(c) for c in r["chain"])] += 1
        if r["in_sub"]:
            osub_shapes[(r["sh"], r["rules_n"])] += 1
    elif r["d"] == 2:
        two_chains.append({"t0": r["t0"], "g": r["g"], "chain": r["chain"],
                           "rules": r["rules"]})
out["one_step_rules_fired"] = dict(rf)
out["one_step_subset_shapes"] = {str(k): v for k, v in osub_shapes.items()}
out["two_step_chains"] = two_chains[:12]

(HERE / "k05_census_v3.json").write_text(json.dumps(out, indent=1))
print("K05_CENSUS_DONE pos_full", (sum(census["one"].values())
                          + sum(census["two"].values())
                          + census["refl"]),
      "census", census)
print("reflexive_witness", w_errs_sub, w_errs_full, "fp", w_fp)
print("compact_reflexive", c2_errs_sub, c2_errs_full, "fp", c2_fp)
print("one_step_rules_fired", out["one_step_rules_fired"])
print("one_step_subset_shapes", out["one_step_subset_shapes"])
print("two_step_chains_n", len(two_chains))
for c in two_chains[:6]:
    print("  chain", c["t0"], c["g"], c["chain"], c["rules"])
