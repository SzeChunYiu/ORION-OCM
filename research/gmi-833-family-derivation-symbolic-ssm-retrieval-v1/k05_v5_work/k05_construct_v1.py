"""K05 v5 — hand-constructed contraction-chain M_ITER for B_CONTR (GMI #833).

Constructs, on the witness's reflexive structure, a machine that decides
   y = (t0 == g) OR (g in one_step(t0)) OR (g in two_step(t0))
over the frozen 18-cell token layout, then verifies the FULL 17424-task
battery with the package's independent evaluator (posthoc_adjudicate_v1).

Token layout (per battery_generate_v1):
  0..4  t0 term   | 5..7 lhs0 (N(x0,y0)), 8 rhs0 | 9..11 lhs1, 12 rhs1 |
  13..17 g term
Term ADT: leaf 0/1; N(a,b) tokens [2,a,b]; padding -1.

Rule application contracts a subterm == lhs (a 2-node) to the leaf rhs.
With <=3-leaf terms, reachability is exactly {0,1,2}-step; the machine
encodes each step class structurally:
  - reflexive: 5-token equality (witness u0..u4 AND-ladder form)
  - one-step:  t0 2-node -> leaf rhs | t0 3R -> N(l,rhs) | t0 3L -> N(rhs,r)
  - two-step:  t0 3R -> N(l,rhs_r1) -> leaf rhs_r2 ; t0 3L analog
All expressions are guard-safe (inputs in {-1,0,1,2}; EQ outputs {0,1};
AND/OR via GE+2/GE+1 on sums of {0,1}).
"""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE if (HERE / "machinery_v1.py").exists() else HERE.parent
sys.path.insert(0, str(PROJ))
import machinery_v1 as M
import posthoc_adjudicate_v1 as A
import proc2_v1 as P2
import battery_generate_v1 as G

SHA = "5b385f0edfa035b28940f5dd982e0c69991a2ce6e0175e4c693073add26899f0"
bat = json.loads((PROJ / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
assert hashlib.sha256((PROJ / "NEUTRAL_BATTERY_FREEZE_V1.json").read_bytes()).hexdigest() == SHA
bc = bat["batteries"]["B_CONTR"]
rows = bc["task_rows"]
layouts = bc["task_cell_layouts"]
y = [r[3] for r in rows]
N = len(rows)

# --------------------------------------------------------------------------
# expression macros (guard-safe over the frozen domain)
# --------------------------------------------------------------------------

def T(i):
    return ["atom", "s%d" % i]

def EQ_T(i, j):
    """1 iff token value at layout position i == token value at position j."""
    return ["un", "GE+2", ["add",
                           ["un", "GE+0", ["add", T(i), ["un", "NEG", T(j)]]],
                           ["un", "GE+0", ["add", T(j), ["un", "NEG", T(i)]]]]]

def EQ_C(i, c):
    """1 iff token value at layout position i == constant c."""
    return ["un", "GE+2", ["add",
                           ["un", "GE+0", ["add", T(i), ["un", "NEG", ["const", c]]]],
                           ["un", "GE+0", ["add", ["const", c], ["un", "NEG", T(i)]]]]]

def AND(a, b):
    return ["un", "GE+2", ["add", a, b]]

def OR(a, b):
    return ["un", "GE+1", ["add", a, b]]

def ANDN(*args):
    e = args[0]
    for a in args[1:]:
        e = AND(e, a)
    return e

def ORN(*args):
    e = args[0]
    for a in args[1:]:
        e = OR(e, a)
    return e

# slot geometry: r in {0,1}; lhs_r = N at (6+4r, 7+4r); rhs at 8+4r.
def sx(r):  # lhs_x token position
    return 6 + 4 * r

def sy(r):  # lhs_y token position
    return 7 + 4 * r

def srhs(r):  # rhs token position
    return 8 + 4 * r

# --------------------------------------------------------------------------
# build the machine (14 work cells; output cell = 18 + 13 = 31)
# --------------------------------------------------------------------------

cells = []
def add(e):
    cells.append(e)
    return 18 + len(cells) - 1  # cell index

# shared shapes (t0 shape cells)
i_eq02 = add(EQ_C(0, 2))                      # 0: t0 root is constructor
i_2n = add(AND(T(i_eq02), EQ_C(3, -1)))       # 1: t0 is a 2-node
i_3R = add(AND(T(i_eq02), EQ_C(2, 2)))        # 2: t0 is N(l, N(a,b))
i_3L = add(AND(T(i_eq02), EQ_C(1, 2)))        # 3: t0 is N(N(a,b), r)

# shared per-slot detectors reused by one-step and two-step
# F_r: g is the leaf rhs_r
iF = {}
# A_r: 3R inner node N(layout[3],layout[4]) == lhs_r
iA = {}
# B_r: 3L inner-left node N(layout[2],layout[3]) == lhs_r
iB = {}
for r in (0, 1):
    iF[r] = add(AND(EQ_T(13, srhs(r)), EQ_C(14, -1)))
    iA[r] = add(AND(EQ_T(3, sx(r)), EQ_T(4, sy(r))))
    iB[r] = add(AND(EQ_T(2, sx(r)), EQ_T(3, sy(r))))

# reflexive: AND of 5 token equalities (witness structure, single cell)
iREF = add(ANDN(*(EQ_T(k, 13 + k) for k in range(5))))

# one-step detector: OR over both slots of [t0==lhs_r & g==leaf | inner==lhs_r & g==N(...)]
def one_step_r(r):
    x, yy, rhs = sx(r), sy(r), srhs(r)
    F, A_c, B_c = T(iF[r]), T(iA[r]), T(iB[r])
    c2L = ANDN(T(i_2n), AND(EQ_T(1, x), EQ_T(2, yy)), F)                 # 2->L
    D = ANDN(EQ_C(13, 2), EQ_T(14, 1), EQ_T(15, rhs), EQ_C(16, -1))      # g==N(l,rhs_r)
    c3R = ANDN(T(i_3R), A_c, D)                                          # 3R->2
    E = ANDN(EQ_C(13, 2), EQ_T(14, rhs), EQ_T(15, 4), EQ_C(16, -1))      # g==N(rhs_r, r)
    c3L = ANDN(T(i_3L), B_c, E)                                          # 3L->2
    return ORN(c2L, c3R, c3L)

iONE = add(OR(one_step_r(0), one_step_r(1)))

# two-step detector: OR over (r1, r2) of [3R: inner==lhs_r1 & N(l,rhs_r1)==lhs_r2 & g==leaf rhs_r2]
#                                         [3L: inner-left==lhs_r1 & N(rhs_r1,r)==lhs_r2 & g==leaf rhs_r2]
def two_step_r1r2(r1, r2):
    x2, y2, rhs2 = sx(r2), sy(r2), srhs(r2)
    rhs1 = srhs(r1)
    A1, B1, F2 = T(iA[r1]), T(iB[r1]), T(iF[r2])
    g3R = ANDN(A1, EQ_T(1, x2), EQ_T(rhs1, y2), F2)
    c3R = AND(T(i_3R), g3R)
    g3L = ANDN(B1, EQ_T(rhs1, x2), EQ_T(4, y2), F2)
    c3L = AND(T(i_3L), g3L)
    return OR(c3R, c3L)

two = two_step_r1r2(0, 0)
two = OR(two, two_step_r1r2(1, 1))   # battery = per-rule closure: SAME rule twice only
iTWO = add(two)

iOUT = add(ORN(T(iREF), T(iONE), T(iTWO)))   # final OR of the three detectors

machine = {"model": "M_ITER", "input_cells": 18, "update": list(cells),
           "output_cell": iOUT, "steps": 16, "rho": 1}

w = len(machine["update"])
assert w <= 24, w
assert machine["steps"] <= 16
cost = M.machine_cost(machine)
print("CELLS", w, "OUTPUT_CELL", iOUT, "COST", cost, flush=True)

# --------------------------------------------------------------------------
# independent-truth cross-check: does the battery's y == (d0 or d1 or d2)?
# --------------------------------------------------------------------------
def toks2term(tk):
    tk = [int(t) for t in tk if t != -1]
    it = iter(tk)
    def go():
        nx = next(it)
        if nx == 2:
            return ("N", go(), go())
        return nx
    return go()

def truth(i):
    """Exact battery ground truth: y=1 iff g in the union over rules of the
    full single-rule transitive closure (battery_generate_v1.reachable_set).
    NOTE: the battery does NOT count cross-rule alternating chains — only
    per-rule closures. (56 tasks have alternating 2-step paths to g that the
    battery does not register; the machine must not fire on those.)"""
    lay = layouts[i]
    t0 = toks2term(lay[0:5]); g = toks2term(lay[13:18])
    rules = [(toks2term(lay[5:8]), int(lay[8]))]
    if int(lay[9]) != -1:
        rules.append((toks2term(lay[9:12]), int(lay[12])))
    for l, r in rules:
        if g in G.reachable_set(t0, l, r):
            return 1
    return 0

t0 = time.time()
mismatch = 0
for i in range(N):
    d = truth(i)
    if (d > 0) != (y[i] == 1):
        mismatch += 1
        if mismatch <= 5:
            print("TRUTH_MISMATCH i", i, "d", d, "y", y[i])
print("TRUTH_CROSSCHECK mismatches:", mismatch, "time", round(time.time() - t0, 1), flush=True)
assert mismatch == 0

# --------------------------------------------------------------------------
# verification via the independent evaluator (posthoc_adjudicate_v1.run_iter)
# --------------------------------------------------------------------------

SUB = [i for i in sorted(range(N), key=lambda i: P2.frozen_hash(i))[:2000]]
SUB_SET = set(SUB)

def pred(g, i):
    c, _, lg = A.run_iter(g, layouts[i])
    return c[g["output_cell"]] if lg else None

# quick subset check first (catches bugs fast)
sub_errs = sub_pos = sub_fp = 0
for i in SUB:
    p = pred(machine, i)
    if p != y[i]:
        sub_errs += 1
        if y[i] == 1:
            sub_pos += 1
        else:
            sub_fp += 1
print("SUBSET errs", sub_errs, "pos_errs", sub_pos, "fp", sub_fp, flush=True)

def full_check(m):
    """Full 17424-task verification, single-process (mp.Pool forkserver
    crashes on this box). Uses the package's independent evaluator."""
    idxs = list(range(N))
    errs = pos_errs = fp = illegals = 0
    for i in idxs:
        c, _, lg = A.run_iter(m, layouts[i])
        if not lg:
            illegals += 1
            continue
        p = c[m["output_cell"]]
        if p != y[i]:
            errs += 1
            if y[i] == 1:
                pos_errs += 1
            else:
                fp += 1
    return errs, pos_errs, fp, illegals

t0 = time.time()
full_errs, full_pos, full_fp, full_illegal = full_check(machine)
print("FULL errs", full_errs, "pos_errs", full_pos, "fp", full_fp,
      "illegal", full_illegal, "time", round(time.time() - t0, 1), flush=True)

# subset positive composition from the machine's own predictions
sub_pos_by = {"refl": 0, "one": 0, "two": 0}
for i in SUB:
    if y[i] != 1:
        continue
    c, _, lg = A.run_iter(machine, layouts[i])
    # classify by running the three detector cells individually
    # cell map: 28=iREF, 29=iONE, 30=iTWO (see cell indices printed at build)
    refl = c[28]
    one = c[29]
    two = c[30]
    assert (refl or one or two) == 1
    if refl:
        sub_pos_by["refl"] += 1
    elif one:
        sub_pos_by["one"] += 1
    else:
        sub_pos_by["two"] += 1
print("SUBSET_POS composition", sub_pos_by, flush=True)

# witness reference numbers (registered)
witness = json.loads((PROJ / "REVIVAL_V2.json").read_text())["rows"]["Symbolic logic systems."]["constructive_witness"]["machine"]
wp = pred(witness, 0)  # warm

result = {
    "schema": "K05_V5_HAND_BUILT_CHAIN_MACHINE",
    "row": "Symbolic logic systems.",
    "battery_sha256": SHA,
    "machine": machine,
    "cost": cost,
    "work_cells": w,
    "steps": machine["steps"],
    "output_cell": machine["output_cell"],
    "full_errors": full_errs,
    "full_pos_errors": full_pos,
    "full_false_pos": full_fp,
    "full_illegal": full_illegal,
    "subset_errors": sub_errs,
    "subset_pos_errors": sub_pos,
    "subset_false_pos": sub_fp,
    "subset_pos_composition": sub_pos_by,
    "witness_reference": {"cost": M.machine_cost(witness), "errors_45_384_fp0": True},
    "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
(HERE / "k05_v5_result_v1.json").write_text(json.dumps(result, indent=1))
print("WROTE k05_v5_result_v1.json")
assert full_pos == 0 and full_fp == 0 and full_illegal == 0 and full_errs == 0
print("K05_V5_OK 0/1176 positives, 0 FP, 0 illegal, all legal on FULL battery")
