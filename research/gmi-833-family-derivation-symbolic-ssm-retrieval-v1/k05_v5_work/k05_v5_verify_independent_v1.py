#!/usr/bin/env python3
"""Independent re-simulation of the K05 v5 machine (route-B style).

Imports NOTHING from posthoc_adjudicate_v1 or k05_construct_v1. Re-derives
the M_ITER run semantics from machinery_v1 (the frozen substrate) and the
battery predicate from battery_generate_v1 (the frozen generator) alone,
then simulates the committed machine from k05_v5_result_v1.json over all
17424 B_CONTR tasks."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG))
import machinery_v1 as M
import battery_generate_v1 as G

res = json.loads((HERE / "k05_v5_result_v1.json").read_text())
m = res["machine"]
bat = json.loads((PKG / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
bc = bat["batteries"]["B_CONTR"]
rows = bc["task_rows"]; lays = bc["task_cell_layouts"]
n = len(rows)

def toks2term(tk):
    tk = [int(t) for t in tk if t != -1]
    it = iter(tk)
    def go():
        nx = next(it)
        if nx == 2:
            return ("N", go(), go())
        return nx
    return go()

def sim(layout):
    cells = list(layout) + [0] * len(m["update"])
    for _ in range(m["steps"]):
        env = dict(("s%d" % i, cells[i]) for i in range(len(cells)))
        nc = list(cells)
        for wi, e in enumerate(m["update"]):
            v = M.expr_eval(e, env)
            if v is None:
                return None
            nc[m["input_cells"] + wi] = v
        cells = nc
    return cells[m["output_cell"]]

def truth(layout):
    t0 = toks2term(layout[0:5]); g = toks2term(layout[13:18])
    rules = [(toks2term(layout[5:8]), int(layout[8]))]
    if int(layout[9]) != -1:
        rules.append((toks2term(layout[9:12]), int(layout[12])))
    for l, r in rules:
        if g in G.reachable_set(t0, l, r):
            return 1
    return 0

pos_err = fp = illegal = 0
for i in range(n):
    y = rows[i][3]
    p = sim(lays[i])
    if p is None:
        illegal += 1
    elif p != y:
        if y == 1:
            pos_err += 1
        else:
            fp += 1

out = {"schema": "K05_V5_VERIFY_INDEPENDENT_V1",
       "row": "Symbolic logic systems.",
       "machine_ref": "k05_v5_result_v1.json",
       "battery_sha256": res["battery_sha256"],
       "n_tasks": n, "positive_errors": pos_err, "false_positives": fp,
       "illegal": illegal, "all_legal": illegal == 0,
       "matches_receipt": (pos_err == res["full_pos_errors"]
                           and fp == res["full_false_pos"]
                           and illegal == res["full_illegal"])}
(HERE / "k05_v5_verify_independent_v1.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
print("AGREES" if out["matches_receipt"] else "DISAGREES")
