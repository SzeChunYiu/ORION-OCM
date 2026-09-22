#!/usr/bin/env python3
"""K05 fingerprint clauses C1-C3 executed as REAL interventions on the v5
machine (k05_v5_result_v1.json), mirroring revival_verify_v2.py's TR1/TR3
pattern and PRIOR_DISCLOSURE_V1.md's intervention contract.

  C1  machine state contains explicitly compositional discrete
      expressions/terms/structures;
  C2  legal transformations include rule-based rewrite/inference over those
      structures;
  C3  control chooses among more than one legal successor: the battery's
      successor_census counts 20 (t0, ruleset) pairs with >= 2 distinct
      one-step successors (multi-redex states); for each such pair the
      machine's one-step detector must fire on EVERY distinct one-step
      successor (each successor is a y=1 task).

Imports only the package's frozen battery generator (for the term universe
and the one-step rewrite semantics) and the package's evaluator (for the
M_ITER run). Writes k05_v5_clauses_v1.json next to itself.

Task indexing follows battery_generate_v1.contr_battery EXACTLY: the loop is
  for t0 in U: for rs in rulesets: for g in U
so task index i = (ti * 36 + ri) * 22 + gi, where ti/gi are universe indices
and ri is the ruleset-table index. Rows carry only set_flag, not ri, so the
index is derived arithmetically, not from row fields.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG))
import battery_generate_v1 as G       # noqa: E402
import posthoc_adjudicate_v1 as A     # noqa: E402

res = json.loads((HERE / "k05_v5_result_v1.json").read_text())
m = res["machine"]
bat = json.loads((PKG / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
bc = bat["batteries"]["B_CONTR"]
rows = bc["task_rows"]
lays = bc["task_cell_layouts"]
n = len(rows)

# term universe: token-list form (universe_tokens are already canonical
# token lists), hashable tuple form, and index maps
U = [list(t) for t in bc["universe_tokens"]]
UIDX = {tuple(tk): i for i, tk in enumerate(U)}


def toks2term(tk):
    tk = [int(t) for t in tk if t != -1]
    it = iter(tk)

    def go():
        nx = next(it)
        if nx == 2:
            return ("N", go(), go())
        return nx

    return go()


UT = [toks2term(u) for u in U]                      # hashable term tuples
RULESETS = [[(UT[lidx], r) for lidx, r in rs]
            for rs in bc["rule_set_table"]]
N_RSETS = len(RULESETS)                             # 36
N_GOALS = len(UT)                                   # 22


def run(i):
    cells, traj, lg = A.run_iter(m, lays[i])
    return cells, traj, lg


def find(t0, g, want_y=None):
    for i in range(n):
        if toks2term(lays[i][0:5]) == t0 and toks2term(lays[i][13:18]) == g:
            if want_y is None or rows[i][3] == want_y:
                return i
    return None


out = {"schema": "K05_V5_CLAUSES_V1", "row": "Symbolic logic systems.",
       "machine_ref": "k05_v5_result_v1.json",
       "battery_sha256": res["battery_sha256"]}

# ---------------------------------------------------------------------------
# C1: compositional discrete structure in machine state
# ---------------------------------------------------------------------------
t0 = ("N", 0, ("N", 0, 0))
i1 = find(t0, t0, 1)                 # reflexive positive
c1 = run(i1)
out["C1"] = {"task": i1, "y": rows[i1][3], "legal": c1[2],
             "final_cells": c1[0],
             "note": ("cell values are the token-equality / t0-shape / g-shape "
                      "bits of the compositional term encoding; the output cell "
                      "holds the reflexive decision"),
             "output_cell": m["output_cell"],
             "output": c1[0][m["output_cell"]]}

# ---------------------------------------------------------------------------
# C2: rule-based contraction rewrites detected
# ---------------------------------------------------------------------------
i2a = find(("N", 0, ("N", 0, 0)), ("N", 0, 0), 1)     # one-step 3R->2
i2b = find(("N", 0, ("N", 0, 0)), 0, 1)               # two-step same-rule chain
c2a = run(i2a)
c2b = run(i2b)
out["C2"] = {
    "one_step_3R_to_2": {"task": i2a, "t0": ["N", 0, ["N", 0, 0]],
                         "g": ["N", 0, 0], "legal": c2a[2],
                         "output": c2a[0][m["output_cell"]], "y": rows[i2a][3]},
    "two_step_same_rule": {"task": i2b, "t0": ["N", 0, ["N", 0, 0]], "g": 0,
                           "legal": c2b[2],
                           "output": c2b[0][m["output_cell"]],
                           "y": rows[i2b][3]},
    "note": ("the one-step detector (2->L / 3R->2 / 3L->2 per rule slot) and "
             "the same-rule two-step detector fire on the executed contraction "
             "rewrites")}

# ---------------------------------------------------------------------------
# C3: control chooses among > 1 legal successor
# ---------------------------------------------------------------------------
pairs = []
for ti in range(len(UT)):
    for ri in range(N_RSETS):
        succ = set()
        for lhs, rhs in RULESETS[ri]:
            for u in G.one_step(UT[ti], lhs, rhs):
                succ.add(u)
        if len(succ) >= 2:
            pairs.append((ti, ri, sorted(succ, key=G.term_tokens)))

census_n = bc["successor_census"]["pairs_with_two_plus_distinct_successors"]
assert len(pairs) == census_n, (len(pairs), census_n)

cases = []
all_fire = True
for ti, ri, succ in pairs:
    case = {"t0_idx": ti, "ruleset_idx": ri, "t0": U[ti],
            "rules": [G.term_tokens(l) + [r] for l, r in RULESETS[ri]],
            "n_distinct_successors": len(succ),
            "successors": [G.term_tokens(s) for s in succ],
            "firings": []}
    for s in succ:
        gi = UIDX[tuple(G.term_tokens(s))]
        i = (ti * N_RSETS + ri) * N_GOALS + gi
        assert rows[i][3] == 1, (ti, ri, gi, i)   # successor => y=1
        cells, _, lg = run(i)
        fired = bool(lg and cells[m["output_cell"]] == 1)
        case["firings"].append({"g": G.term_tokens(s), "task": i,
                                "y": rows[i][3],
                                "output": (cells[m["output_cell"]] if lg
                                           else None),
                                "fired": fired})
        if not fired:
            all_fire = False
    cases.append(case)

out["C3"] = {"pairs_with_two_plus_distinct_successors": len(pairs),
             "census_reported": census_n,
             "all_one_step_successors_fire": all_fire,
             "cases": cases}

(HERE / "k05_v5_clauses_v1.json").write_text(json.dumps(out, indent=1))
print("C1 task", i1, "legal", c1[2], "out", c1[0][m["output_cell"]])
print("C2 one-step task", i2a, "out", c2a[0][m["output_cell"]],
      "two-step task", i2b, "out", c2b[0][m["output_cell"]])
print("C3 multi pairs", len(pairs), "(census", str(census_n) + ")",
      "all one-step successors fire:", all_fire)
