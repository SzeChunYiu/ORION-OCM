"""DG-8 — the declared low-discrepancy sample of the OFF-DIAGONAL region of the closure lattice `A x d x p x F`.

THE GAP. `GMI-DA7` names four axes on which a kingdom can be gained: the primitive alphabet `A` (and the parameter
family within it), the structure-depth bound `d`, the arithmetic instrument `p`, and the ecology family `F`. The
programme's central negative is that none of them yields one. That negative is a conjunction of FOUR SWEEPS RUN ONE AT
A TIME, each strong on its own axis and sitting at an inherited default on the other three. `GMI-DA11` proves that a
negative claim is a universally quantified statement over a REGION of `K(A, d, p, F)` and is entitled to exactly the
region actually searched: monotonicity protects POSITIVES and gives negatives nothing. So four one-axis negatives do
not compose into a negative over the product, and `DG-8` records that no cell off the diagonal has ever been searched.

It is not a scruple. `RV-377-089b`'s six intervention-robust coefficient witnesses live at the PRODUCT of
`A`-parameter `h = 3` and ecology `E_sym3`; the parameter sweep ran the right parameters on the wrong ecologies and
the ecology enumeration ran all five at the default parameters. Both were correct on their own axis; neither could
see what the product contained.

THE LATTICE. Every ladder below is taken from an EXECUTED registered sweep. Nothing here is an invented range.

    A   the parameter family within the alphabet for the registered coefficient row, `zoo.gradient_net`:
        `H_GRID x LR_GRID` of `witness_dg7.py` (RV-377-089/-089b)             10 x 8   =  80
    d   the structure-depth bound: `d1`..`d6`, RV-377-065's executed depths                =   6
    p   the arithmetic instrument: RV-377-076's executed ladder `fx8`..`wide`              =   7
    F   the registered ecologies x the registered intervention set
        (`ecology.REGISTRY` x `ecology.INTERVENTIONS`)                         6 x 6   =  36

                                                            total cells      80*6*7*36 = 120 960

THE DIAGONAL. The registered default point is

    A0 = (h = 2, lr = 4)   the zoo's declared default coefficient row, `zoo.gradient_net()`
    d0 = 1                 GMI-DA7 section 10: "d = 1 for every executed candidate"
    p0 = fx8               GMI-DA7 section 10: 8-bit fixed point, FRAC_BITS = 4
    F0 = (E_smooth1, standard)   the frozen original D'/E' ecology (`smooth.COEFFS_V1`) under the registered protocol

A cell is ON the diagonal iff AT MOST ONE of its four coordinates differs from the default: the diagonal is the union
of the four one-axis lines through the default point, which is exactly what the four sweeps covered. A cell is OFF
the diagonal iff AT LEAST TWO coordinates differ.  126 cells are on the diagonal; 120 834 are off it.

WHAT THE d AXIS MEANS HERE. `deep_gradient_net(h, lr, depth)` stacks `depth` AFFINE+NONLIN blocks over the registered
alphabet and is EXACTLY `zoo.gradient_net(h, lr)` at `depth = 1` — asserted by `depth1_identity_check()`, which
compares canonical fingerprints, not behaviour. No new kind is introduced: raising `d` here is composition over the
same `A`, which is what GMI-DA7's monotonicity statement is about.

WHAT THE p AXIS MEANS HERE. `instrument(p)` rebinds the registered fixed-point universe (`core.TOTAL_BITS`,
`FRAC_BITS`, and the derived constants in `vm`, `smooth` and the basis description widths) to `fx(b)`: b total bits,
`b // 2` fractional bits, the same instrument family RV-377-076 executed. At `fx8` this must be BIT-IDENTICAL to the
unpatched registered universe — asserted by `fx8_identity_check()` against the full response signature, not merely
against the capability.

RULE 40. Every admissibility verdict here carries the best-constant control for its own `(p, F)` cell, and the margin
is reported in REGISTERED fx units, `1 / (1.5 * 16) = 0.0416667` of capability. The registered unit is used at every
instrument deliberately: reporting margins in the instrument's own (finer) unit would make a witness look better the
more precision it is given, which is the opposite of a control. A cell counts as a VALID WITNESS only if it is
admissible, its ecology is DISCRIMINATING at theta, and it beats the best constant by at least one registered fx unit.

The best constant is computed exactly rather than by grid scan: mean absolute error is minimized by a median of the
evaluation targets, so scanning the target values themselves attains the true optimum at every instrument.
`constant_control_agreement()` checks this against `constant_control.best_constant`'s fx8 grid scan.

RULE 39. The swept indices are `A`, `d`, `p` and `F` (ecology AND intervention). The indices held at a default are:
the basis column (`B0_LOCAL_ADAPTIVE_TRANSDUCERS`), the seed (0), the development length (16 events), the evaluation
criterion (`unseen`), theta (0.85), and the carrier family itself (the registered coefficient row). Those six are
named here and are not claimed to have been searched.

THE AFFORDABLE SUB-REGION. Charged replay cost grows with the genotype's declared parameter count
`P(h, d) = 5h + (d - 1) * h * (h + 1) + (h + 1)`, which is known before the cell is run. The sample is declared over
the sub-region `P <= P_MAX`; the complement is NOT evaluated and is NOT counted as a negative anywhere in the
receipt. Its exact measure is recorded so the region this run is entitled to speak about is written down.
"""
from __future__ import annotations

import contextlib
import json
import os
import time

from . import bases, core, ecology, morph, smooth, vm, zoo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "microscopes", "results")

# ------------------------------------------------------------------------------------------------------- the lattice
H_GRID = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32)          # witness_dg7.H_GRID (RV-377-089)
LR_GRID = (1, 2, 3, 4, 6, 8, 12, 16)                 # witness_dg7.LR_GRID
D_GRID = (1, 2, 3, 4, 5, 6)                          # RV-377-065's executed depths d1..d6
P_GRID = ("fx8", "fx10", "fx12", "fx16", "fx24", "fx32", "wide")   # RV-377-076's instrument ladder
ECOS = ("E_smooth1", "E_smooth3", "E_sym3", "E_sym5", "E_parity", "E_wit1")   # ecology.REGISTRY
IVS = ("standard", "no_revoke", "double_revoke", "half_events", "shuffled_events", "extra_unseen_feedback")

A_LADDER = tuple((h, lr) for h in H_GRID for lr in LR_GRID)        # 80, declared lexicographic order
F_LADDER = tuple((e, j) for e in ECOS for j in IVS)                # 36, declared lexicographic order

A_DEF, D_DEF, P_DEF, F_DEF = (2, 4), 1, "fx8", ("E_smooth1", "standard")

THETA = 0.85
FX_UNIT_REGISTERED = 1.0 / (1.5 * 16)                # protocol rule 40: 0.0416667 of capability
COL = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
SEED = 0
N_EVENTS = 16
CRITERION = "unseen"

# fx(b): b total bits, b // 2 fractional bits (RV-377-066/-076's instrument family).
# `wide` is the declared unbounded instrument: 128 total bits at scale 2^64, which no value in this ecology approaches.
INSTRUMENT_BITS = {"fx8": 8, "fx10": 10, "fx12": 12, "fx16": 16, "fx24": 24, "fx32": 32, "wide": 128}

N_TOTAL = len(A_LADDER) * len(D_GRID) * len(P_GRID) * len(F_LADDER)
N_DIAGONAL = 1 + (len(A_LADDER) - 1) + (len(D_GRID) - 1) + (len(P_GRID) - 1) + (len(F_LADDER) - 1)
N_OFFDIAGONAL = N_TOTAL - N_DIAGONAL


def n_off_default(cell):
    a, d, p, f = cell
    return (tuple(a) != A_DEF) + (d != D_DEF) + (p != P_DEF) + (tuple(f) != F_DEF)


def is_off_diagonal(cell):
    return n_off_default(cell) >= 2


def stratum(cell):
    """which coordinates are off their registered default, as a sorted label: 'AF', 'Adp', 'AdpF', ..."""
    a, d, p, f = cell
    return "".join(x for x, on in zip("AdpF", (tuple(a) != A_DEF, d != D_DEF, p != P_DEF, tuple(f) != F_DEF)) if on)


def param_count(h, depth):
    """declared DENSE cells of deep_gradient_net(h, ., depth) — known before the cell is run."""
    return 5 * h + (depth - 1) * h * (h + 1) + (h + 1)


# --------------------------------------------------------------------------------------------------- the p axis
# The registered `E_parity` spec does not hold a parity target. `ecology.spec_table` is called with the DICT returned
# by `smooth.make_parity_target()` and stores `[int(v) for v in table]`, which iterates the dict's KEYS: the stored
# table is the identity list 0..15, so `ecology.target_of` returns `{x: x}`. Every claim taken on `E_parity` THROUGH
# `ecology.REGISTRY` is therefore a claim about the binary-weighted linear target `y = x / 16`, not about parity.
# (Confirmation from a receipt that predates this module: STAGE_DG9_CONSTANT_CONTROL_V1 reports E_parity's best
# constant as 0.8333, which is the identity target's value on the unseen set; the true parity target's best constant
# there is 1.0, because all eight unseen inputs have odd parity.) `smooth.py`'s own parity runs are unaffected --
# they pass `make_parity_target()` straight to `smooth.main` and never go through the registry.
#
# This module does NOT repair that. Repairing it would silently change what `E_parity` means and would make these
# cells incomparable with every prior claim recorded on that name. It reproduces the registered semantics EXACTLY
# and records the defect in the result document instead.
E_PARITY_AS_REGISTERED_COEFFS = (1 / 16, 2 / 16, 4 / 16, 8 / 16)   # y = x / 16, identical to the stored table at fx8


def target_at_instrument(spec):
    """the ecology's target REBUILT at the current instrument.

    `ecology.REGISTRY` is constructed once at import, at fx8. A coefficient spec survives a change of instrument
    because `ecology.target_of` re-evaluates `smooth.make_target` from the declared float coefficients. A TABLE spec
    does NOT: its table is a frozen list of fx8 integers, and reading it at a wider instrument would reinterpret the
    stored integer 1 as 1 / 2^FRAC instead of 1 / 16. The table is therefore rebuilt from the real-valued target it
    encodes, which for the registered `E_parity` is `y = x / 16` (see the note above)."""
    if spec["family"] == "smooth":
        return smooth.make_target(tuple(spec["coeffs"]))
    if spec["family"] == "table":
        if spec["name"] != "E_parity":
            raise ValueError(f"no instrument-aware reconstruction declared for table spec {spec['name']!r}")
        return smooth.make_target(E_PARITY_AS_REGISTERED_COEFFS)
    raise ValueError(spec["family"])


@contextlib.contextmanager
def instrument(p):
    """rebind the registered fixed-point universe to instrument `p` for the duration of the block."""
    bits = INSTRUMENT_BITS[p]
    frac = bits // 2
    B0 = bases.ALL[COL]
    old = (core.TOTAL_BITS, core.FRAC_BITS, core.FX_ONE, core.FX_MAX, core.FX_MIN,
           vm.FX_ONE, vm._mul, smooth.FX_ONE, dict(B0._desc), B0.desc_store_entry, ecology.target_of)
    core.TOTAL_BITS, core.FRAC_BITS = bits, frac
    core.FX_ONE = 1 << frac
    core.FX_MAX = (1 << (bits - 1)) - 1
    core.FX_MIN = -(1 << (bits - 1))
    vm.FX_ONE = core.FX_ONE
    vm._mul = lambda a, b, _f=frac: core.clamp((a * b + (1 << (_f - 1))) >> _f)
    smooth.FX_ONE = core.FX_ONE
    B0._desc = dict(B0._desc)
    B0._desc["fx"] = bits
    B0.desc_store_entry = 2 + bits
    ecology.target_of = target_at_instrument
    try:
        yield
    finally:
        (core.TOTAL_BITS, core.FRAC_BITS, core.FX_ONE, core.FX_MAX, core.FX_MIN,
         vm.FX_ONE, vm._mul, smooth.FX_ONE, desc, dse, tgt) = old
        B0._desc = desc
        B0.desc_store_entry = dse
        ecology.target_of = tgt


# --------------------------------------------------------------------------------------------------- the d axis
def deep_gradient_net(h=2, lr=4, depth=1):
    """`zoo.gradient_net` generalized to `depth` stacked AFFINE+NONLIN blocks, over the registered alphabet only.

    depth = 1 reproduces `zoo.gradient_net(h, lr)` node for node and edge for edge (see depth1_identity_check)."""
    if depth < 1:
        raise ValueError(depth)
    nodes = {0: ("INPUT", {"width": 4}), 8: ("OUTPUT", {}), 9: ("TARGET", {}), 12: ("EVIDENCE", {"cap": 64})}
    edges = [(0, 12, 0), (9, 12, 1)]
    nid = 20
    prev, prev_w, dense_ids = 0, 4, []
    for L in range(depth):
        dsid, afid, nlid = (1, 2, 3) if L == 0 else (nid, nid + 1, nid + 2)
        if L > 0:
            nid += 3
        nodes[dsid] = ("DENSE", {"width": h * (prev_w + 1)})
        nodes[afid] = ("AFFINE", {"width": h})
        nodes[nlid] = ("NONLIN", {"fn": 0})
        edges += [(dsid, afid, 0), (prev, afid, 1), (afid, nlid, 0)]
        dense_ids.append(dsid)
        prev, prev_w = nlid, h
    nodes[4] = ("DENSE", {"width": h + 1})
    nodes[5] = ("LINEAR", {})
    edges += [(4, 5, 0), (prev, 5, 1), (5, 8, 0)]
    dense_ids.append(4)
    for i, dsid in enumerate(dense_ids):
        gid = (10 if dsid == 1 else 11) if depth == 1 else nid + 10 + i
        nodes[gid] = ("GRAD", {"lr": lr})
        edges += [(dsid, gid, 0), (5, gid, 1), (9, gid, 2)]
    return morph.make(nodes, edges, meta={"zoo": "deep_gradient_net", "depth": depth})


# --------------------------------------------------------------------------------------------- rule 40 control
def best_constant(target, eval_set):
    """capability of the strongest single constant, exactly. Mean absolute error is minimized by a median of the
    evaluation targets, so the optimum is attained at one of the target values; scanning them is exact at every
    instrument, where a fixed grid scan would not be."""
    fx_one = smooth.FX_ONE
    best = (-1.0, None)
    for c in sorted({target[x] for x in eval_set}):
        err = sum(abs(c - target[x]) for x in eval_set) / fx_one / len(eval_set)
        cap = round(max(0.0, 1 - err / 1.5), 4)
        if cap > best[0]:
            best = (cap, c)
    return best


# ----------------------------------------------------------------------------------------------- cell evaluation
def evaluate_cell(cell):
    """one cell of the lattice, charged exactly. Returns the full verdict dict."""
    (h, lr), d, p, (eco, iv) = tuple(cell[0]), cell[1], cell[2], tuple(cell[3])
    t0 = time.time()
    with instrument(p):
        spec = ecology.REGISTRY[eco]
        target = target_at_instrument(spec)
        ev = smooth.UNSEEN if spec["criterion"] == "unseen" else smooth.ALL_X
        const_cap, const_v = best_constant(target, ev)
        g = deep_gradient_net(h, lr, d)
        r = ecology.run_genotype(spec, g, bases.ALL[COL], iv, seed=SEED)
        cap = r["capability"]
        sig = ecology.response_signature(r)
    margin = round((cap - const_cap) / FX_UNIT_REGISTERED, 4)
    return {"A": [h, lr], "d": d, "p": p, "F": [eco, iv], "stratum": stratum(cell),
            "param_count": param_count(h, d), "capability": cap, "admissible": cap >= THETA,
            "best_constant_capability": const_cap, "best_constant_fx": const_v,
            "discriminating": const_cap < THETA, "margin_registered_fx_units": margin,
            "separates": margin >= 1.0,
            "valid_witness": bool(cap >= THETA and const_cap < THETA and margin >= 1.0),
            "response_signature": sig, "seconds": round(time.time() - t0, 3)}


def caps_all_interventions(h, lr, d, p, eco):
    """the full registered intervention family for one (A, d, p, ecology), charged only on a hit."""
    out = {}
    with instrument(p):
        spec = ecology.REGISTRY[eco]
        for j in IVS:
            try:
                out[j] = ecology.run_genotype(spec, deep_gradient_net(h, lr, d), bases.ALL[COL], j, seed=SEED)["capability"]
            except Exception:
                out[j] = None
    return out


# ------------------------------------------------------------------------------------------------- self-checks
def depth1_identity_check():
    """deep_gradient_net(h, lr, 1) must BE zoo.gradient_net(h, lr): identical canonical fingerprints."""
    bad = []
    for h in H_GRID:
        for lr in LR_GRID:
            if morph.canonical(deep_gradient_net(h, lr, 1)) != morph.canonical(zoo.gradient_net(h, lr)):
                bad.append([h, lr])
    return {"checked": len(H_GRID) * len(LR_GRID), "mismatches": bad, "holds": not bad}


def fx8_identity_check():
    """under instrument('fx8') the evaluator must be BIT-IDENTICAL to the unpatched registered universe, on the full
    response signature (served trace and capability), not merely on the capability."""
    rows = []
    for eco in ECOS:
        for j in IVS:
            spec = ecology.REGISTRY[eco]
            a = ecology.run_genotype(spec, zoo.gradient_net(*A_DEF), bases.ALL[COL], j, seed=SEED)
            with instrument("fx8"):
                b = ecology.run_genotype(spec, deep_gradient_net(A_DEF[0], A_DEF[1], 1), bases.ALL[COL], j, seed=SEED)
            rows.append({"F": [eco, j], "capability_equal": a["capability"] == b["capability"],
                         "signature_equal": ecology.response_signature(a) == ecology.response_signature(b)})
    return {"checked": len(rows), "holds": all(r["capability_equal"] and r["signature_equal"] for r in rows),
            "rows": rows}


def registered_target_reconstruction_check():
    """at fx8 the instrument-aware reconstruction must reproduce the REGISTERED target of every ecology exactly,
    including `E_parity`'s stored table with its defect intact."""
    rows = {}
    for eco in ECOS:
        spec = ecology.REGISTRY[eco]
        rows[eco] = {"equal": ecology.target_of(spec) == target_at_instrument(spec)}
    return {"holds": all(v["equal"] for v in rows.values()), "rows": rows}


def constant_control_agreement():
    """the exact median-based best constant must agree with constant_control's fx8 grid scan at fx8."""
    from . import constant_control as cc
    rows = {}
    for eco in ECOS:
        spec = ecology.REGISTRY[eco]
        t = ecology.target_of(spec)
        ev = smooth.UNSEEN if spec["criterion"] == "unseen" else smooth.ALL_X
        mine = best_constant(t, ev)
        theirs = cc.best_constant(t, ev)
        rows[eco] = {"exact": mine[0], "grid_scan": theirs[0], "equal": mine[0] == theirs[0]}
    return {"holds": all(v["equal"] for v in rows.values()), "rows": rows}


# ------------------------------------------------------------------------------------- the low-discrepancy sample
def radical_inverse(n, base):
    f, r = 1.0, 0.0
    while n > 0:
        f /= base
        r += f * (n % base)
        n //= base
    return r


def halton_point(i):
    """the i-th point of the 4-dimensional Halton sequence in bases 2, 3, 5, 7 (i counted from 1)."""
    return tuple(radical_inverse(i, b) for b in (2, 3, 5, 7))


def halton_cell(i):
    u = halton_point(i)
    return (A_LADDER[min(int(u[0] * len(A_LADDER)), len(A_LADDER) - 1)],
            D_GRID[min(int(u[1] * len(D_GRID)), len(D_GRID) - 1)],
            P_GRID[min(int(u[2] * len(P_GRID)), len(P_GRID) - 1)],
            F_LADDER[min(int(u[3] * len(F_LADDER)), len(F_LADDER) - 1)])


def draw_sample(n, p_max, already_evaluated, start=1, max_index=5_000_000):
    """the declared sample: Halton points in index order, keeping the first `n` distinct cells that are OFF the
    diagonal, are AFFORDABLE (param_count <= p_max) and have never been evaluated. Deterministic; no seed, no
    randomness, no discretion — the only inputs are `n`, `p_max` and the frozen evaluated set."""
    seen = set()
    out = []
    i = start
    while len(out) < n and i < max_index:
        c = halton_cell(i)
        key = (c[0], c[1], c[2], c[3])
        if (key not in seen and is_off_diagonal(c) and param_count(c[0][0], c[1]) <= p_max
                and key not in already_evaluated):
            seen.add(key)
            out.append({"halton_index": i, "A": list(c[0]), "d": c[1], "p": c[2], "F": list(c[3]),
                        "stratum": stratum(c), "param_count": param_count(c[0][0], c[1])})
        i += 1
    return out, i


def affordable_measure(p_max):
    """the exact measure of the affordable sub-region within the off-diagonal region."""
    n_aff = n_aff_off = 0
    for a in A_LADDER:
        for d in D_GRID:
            if param_count(a[0], d) > p_max:
                continue
            for p in P_GRID:
                for f in F_LADDER:
                    n_aff += 1
                    if is_off_diagonal((a, d, p, f)):
                        n_aff_off += 1
    return {"p_max": p_max, "affordable_cells": n_aff, "affordable_offdiagonal_cells": n_aff_off,
            "offdiagonal_cells": N_OFFDIAGONAL,
            "fraction_of_offdiagonal_region_affordable": round(n_aff_off / N_OFFDIAGONAL, 6)}


# --------------------------------------------------------------------- what has ever been evaluated in this lattice
COVERAGE_SOURCES = ("STAGE_B1_V31_DG7_COEFFICIENT_WITNESS.json",
                    "STAGE_B1_V31b_DG7_COEFFICIENT_WITNESS_ALL5.json",
                    "STAGE_ECO_V32_ECO_AXIS.json",
                    "STAGE_RULE36_INTERVENTION_ADMISSIBILITY_V1.json")


def coverage_census():
    """every cell of this lattice for which a receipt in microscopes/results records a capability.

    The scan procedure, so the number can be checked: a receipt contributes a cell only when it names the cell's four
    coordinates explicitly. All 241 receipts were first scanned for any declaration of a non-`fx8` instrument or a
    structure depth above 1 IN COMBINATION with a registered smooth ecology; none exists. The instrument ladder is
    exercised only by RV-377-066/-075/-076 on the `dk_precision` ambiguous/noisy ecologies, and the depth ladder only
    by RV-377-065 on `E_rolefill` -- two obligation families outside this lattice. So the `d` and `p` coordinates of
    every cell this lattice has ever seen are pinned at their defaults, and the four receipts below carry all of it."""
    ev, prov = set(), {}

    def add(cell, src):
        ev.add(cell)
        prov.setdefault(src, set()).add(cell)

    for fn in COVERAGE_SOURCES[:2]:
        d = json.load(open(os.path.join(RES, fn)))
        for eco, v in d["ecologies"].items():
            if eco not in ECOS:
                continue
            for c in v["cells"].values():
                a = (c["h"], c["lr"])
                if a[0] not in H_GRID or a[1] not in LR_GRID:
                    continue
                add((a, 1, "fx8", (eco, "standard")), fn)
                for j, cap in c.get("by_intervention", {}).items():
                    if cap is not None and j in IVS:
                        add((a, 1, "fx8", (eco, j)), fn)

    # the ecology-axis sweep enumerated coefficient targets on the grid v/16, v in (-8,-6,...,8); of the registered
    # ecologies only E_wit1's coefficients lie on that grid (E_sym3 and E_sym5 use odd numerators, E_parity is a table)
    d = json.load(open(os.path.join(RES, COVERAGE_SOURCES[2])))
    wit1 = list(ecology.WITNESS_COEFFS_V1)
    for w in d["witnesses"]:
        if w.get("coeffs") != wit1:
            continue
        a = (w["h"], w["lr"])
        if a[0] in H_GRID and a[1] in LR_GRID:
            for j in w["by_intervention"]:
                if j in IVS:
                    add((a, 1, "fx8", ("E_wit1", j)), COVERAGE_SOURCES[2])

    d = json.load(open(os.path.join(RES, COVERAGE_SOURCES[3])))
    for eco, v in d.items():
        if eco not in ECOS or not isinstance(v, dict):
            continue
        for row, caps in v.get("caps", {}).items():
            if not row.startswith("gradient_net_h"):
                continue
            h = int(row.split("_h")[1])
            if h not in H_GRID:
                continue
            for j in (caps if isinstance(caps, dict) else {"standard": caps}):
                if j in IVS:
                    add(((h, 4), 1, "fx8", (eco, j)), COVERAGE_SOURCES[3])

    diag = {c for c in ev if n_off_default(c) <= 1}
    offd = ev - diag
    strata = {}
    for c in offd:
        strata[stratum(c)] = strata.get(stratum(c), 0) + 1
    n_dp_crossed = sum(1 for c in ev if (c[1] != D_DEF or c[2] != P_DEF) and n_off_default(c) >= 2)
    return {
        "sources": {k: len(v) for k, v in sorted(prov.items())},
        "lattice_total_cells": N_TOTAL, "diagonal_cells": N_DIAGONAL, "offdiagonal_cells": N_OFFDIAGONAL,
        "evaluated_cells": len(ev),
        "true_coverage_fraction": round(len(ev) / N_TOTAL, 8),
        "evaluated_on_diagonal": len(diag), "diagonal_coverage_fraction": round(len(diag) / N_DIAGONAL, 6),
        "evaluated_off_diagonal": len(offd),
        "offdiagonal_coverage_fraction": round(len(offd) / N_OFFDIAGONAL, 10),
        "offdiagonal_evaluated_by_stratum": dict(sorted(strata.items())),
        "distinct_d_ever_evaluated": sorted({c[1] for c in ev}),
        "distinct_p_ever_evaluated": sorted({c[2] for c in ev}),
        "offdiagonal_cells_crossing_d_or_p_with_anything": n_dp_crossed,
        "cells": sorted([[list(a), dd, p, list(f)] for (a, dd, p, f) in ev]),
    }


# ------------------------------------------------------------------------------------------------- one-axis shadows
def shadows(cell):
    """the one-axis shadows of an off-diagonal cell: for each coordinate that is OFF its default, the DIAGONAL cell
    that keeps only that coordinate and returns the other three to their registered defaults.

    This is the exact test DG-8 is about. If an off-diagonal cell is admissible and every one of its shadows is not,
    the product holds something that no single-axis sweep through the default point could have found -- the
    RV-377-089b pattern, reproduced deliberately instead of by accident."""
    a, d, p, f = tuple(cell[0]), cell[1], cell[2], tuple(cell[3])
    out = []
    if a != A_DEF:
        out.append((a, D_DEF, P_DEF, F_DEF))
    if d != D_DEF:
        out.append((A_DEF, d, P_DEF, F_DEF))
    if p != P_DEF:
        out.append((A_DEF, D_DEF, p, F_DEF))
    if f != F_DEF:
        out.append((A_DEF, D_DEF, P_DEF, f))
    return out


# ================================================================================================== THE FROZEN DESIGN
P_MAX = 400            # declared affordability bound on the genotype's parameter count
N_SAMPLE = 900         # declared sample size (see SIZING below)
PRIMARY_WALLCLOCK_GUARD_S = 2100
FOLLOWUP_WALLCLOCK_GUARD_S = 700

SAMPLE_PATH = os.path.join(ROOT, "GMI_DG8_OFFDIAGONAL_SAMPLE_V1.json")
RESULT_MD = os.path.join(ROOT, "GMI_DG8_OFFDIAGONAL_RESULT_V1.md")
RECEIPT_PATH = os.path.join(RES, "STAGE_DG8_OFFDIAGONAL_V1.json")


def predicted_admissible(cell):
    """THE FROZEN PER-CELL PREDICTOR, declared before the run and applied to every cell of the frozen list.

    A cell is predicted ADMISSIBLE iff

        the ecology is E_sym3 or E_wit1,   OR   (d >= 3 and p in {fx8, fx10, fx12}).

    Reasons, stated so the predictor can be blamed:
      * `E_sym3`'s best constant is 0.8750, ABOVE theta -- the ecology does not discriminate, so nearly anything that
        does not diverge clears the bar there. `E_wit1` was constructed by RV-377-102 precisely because the
        coefficient carrier has separating witnesses on it.
      * depth helps and precision hurts. The registered 8-bit instrument SATURATES, and saturation is doing real work
        for a deep net: it bounds a divergent forward pass. Remove the bound and the same net runs away. So capability
        should rise with d at low precision and collapse at high precision.
    This predictor is deliberately crude. If it scores near chance, that is the record."""
    (h, lr), d, p, (eco, iv) = tuple(cell[0]), cell[1], cell[2], tuple(cell[3])
    return bool(eco in ("E_sym3", "E_wit1") or (d >= 3 and p in ("fx8", "fx10", "fx12")))


FROZEN_PREDICTIONS = {
    "C1_COVERAGE": {
        "kind": "measurement recorded before the run, not a prediction",
        "text": "The lattice holds 120 960 cells. 541 have ever been evaluated (0.4473 %). 84 of the 126 diagonal "
                "cells are covered. 457 off-diagonal cells are covered, ALL of them in the AF stratum. The number of "
                "evaluated cells in which d or p is off its default TOGETHER WITH any other off-default coordinate "
                "is EXACTLY ZERO: d has only ever been 1 and p has only ever been fx8 anywhere in this lattice."},
    "C2_CEILING_FALLS_OFF_THE_DIAGONAL": {
        "predict": "FAILS for the ceiling: at least one sampled off-diagonal cell whose ecology is E_smooth3 or "
                   "E_sym5 reaches capability >= theta = 0.85.",
        "target_negative": "RV-377-089, terminal RV_377_082_S_CEILING_IS_CONFIRMED_AND_PROPERLY_SWEPT__NO_"
                           "COEFFICIENT_WITNESS_ON_E_SMOOTH3_OR_E_SYM5_OVER_80_ROWS_TO_H_32",
        "falsifier": "ZERO such cells. Then RV-377-089's ceiling is UPHELD over a region three orders of magnitude "
                     "larger than the one it searched, and this record says so in those words."},
    "C3_DEPTH_HELPS": {
        "predict": "median capability over sampled cells with d >= 4 is STRICTLY GREATER than median capability over "
                   "sampled cells with d = 1.",
        "falsifier": "median(d >= 4) <= median(d = 1)."},
    "C4_PRECISION_HURTS": {
        "predict": "mean capability over sampled cells with p in {fx24, fx32, wide} is STRICTLY LESS than mean "
                   "capability over sampled cells with p in {fx8, fx10}. The 8-bit instrument's SATURATION is load-"
                   "bearing for a deep net; removing it lets the forward pass diverge.",
        "falsifier": "mean(high precision) >= mean(low precision). That would support the corpus's own reading "
                     "(GMI-DA7 section 10b: 'raise p and D3 should become non-empty') against this record's."},
    "C5_PRODUCT_EFFECT": {
        "predict": "at least one sampled off-diagonal cell is ADMISSIBLE while EVERY ONE of its one-axis shadows -- "
                   "the diagonal cells that keep one off-default coordinate and return the other three to their "
                   "registered defaults -- is INADMISSIBLE. This is DG-8's own premise, executed: the product holds "
                   "something no single-axis sweep through the default point could have found.",
        "falsifier": "no such cell. Then the off-diagonal region adds nothing beyond the diagonal at this scope, "
                     "DG-8 is a BOOKKEEPING gap rather than an empirical one, and this record must say so."},
    "C6_VALID_WITNESS_COUNT": {
        "predict": "the number of sampled off-diagonal cells that are RULE-40 VALID WITNESSES on one of the five "
                   "pre-E_wit1 registered ecologies (admissible AND discriminating ecology AND margin >= 1 "
                   "registered fx unit over the best constant) is between 1 and 25 INCLUSIVE.",
        "falsifier": "0, or more than 25."},
    "C7_ADMISSIBLE_RATE": {
        "predict": "the fraction of EVALUATED sampled off-diagonal cells with capability >= theta lies in "
                   "[0.04, 0.22].",
        "falsifier": "outside that interval."},
    "C8_PER_CELL_PREDICTOR": {
        "predict": "the frozen per-cell predictor `predicted_admissible` (its rule is stated in the module and its "
                   "label is attached to every cell of the frozen list below) scores BALANCED ACCURACY >= 0.70 "
                   "against the executed admissibility of the sample.",
        "falsifier": "balanced accuracy below 0.70."},
    "C9_PROCEDURE": {
        "kind": "procedural commitment, not a prediction",
        "text": "No RED or negative result is deleted, weakened or rewritten by this run. Where an off-diagonal cell "
                "contradicts a diagonal-derived negative, the falsification is RECORDED and the original negative "
                "stands with its scope narrowed IN THIS RECORD to the region it actually searched. The measured "
                "points of every prior sweep stand exactly as measured; only the implicature falls."},
}

WHAT_WOULD_FALSIFY_THE_DIAGONAL_NEGATIVES = [
    "An off-diagonal cell with ecology in {E_smooth3, E_sym5} and capability >= 0.85 falsifies, AS A REGION CLAIM, "
    "RV-377-089's 'no coefficient witness on E_smooth3 or E_sym5'. Its 80 measured rows at (d = 1, p = fx8) stand "
    "exactly as measured. What falls is the unstated quantifier that carried the claim beyond that pair of defaults.",
    "An off-diagonal cell on one of the five pre-E_wit1 registered ecologies that is admissible under ALL SIX "
    "registered interventions, on a DISCRIMINATING ecology, with margin >= 1 registered fx unit, falsifies AS A "
    "REGION CLAIM RV-377-102's invariant 'the coefficient carrier is fragile on all five registered ecologies'.",
    "An admissible off-diagonal cell all of whose one-axis shadows are inadmissible falsifies, as an empirical "
    "matter, the composition of the four one-axis negatives into a negative over the product -- which is the exact "
    "inference GMI-DA11 forbids and DG-8 records as unsearched.",
    "CONVERSELY: if no off-diagonal cell is admissible where its shadows are not, then nothing in the product "
    "exceeds the diagonal at this scope, and the four one-axis negatives lose no ground. That outcome is recorded "
    "with the same weight as the other.",
]

SIZING = {
    "measured_cost_of_one_cell": "the cost grid below, 47 cells, measured on this machine before the freeze",
    "cost_law": "wall-clock is driven by the structure depth, roughly x3.2 per depth level, and only linearly by h: "
                "at h = 8 one cell costs 0.11 / 0.33 / 0.78 / 2.11 / 6.83 / 25.36 s at d = 1..6.",
    "mean_cost_per_cell_over_the_affordable_offdiagonal_region_s": 1.29,
    "sample_size": N_SAMPLE,
    "expected_primary_stage_s": round(N_SAMPLE * 1.29),
    "budget": "about 40 minutes total on this machine, shared with other work. The primary stage is sized at about "
              "19 minutes and the two follow-up stages at about 10, leaving margin.",
    "stop_rule": "if the primary stage exceeds 2100 s it stops and the receipt records exactly how many cells were "
                 "evaluated. ANY PREFIX OF A HALTON SEQUENCE IS ITSELF LOW-DISCREPANCY, so an early stop leaves a "
                 "valid smaller sample rather than a biased one. Cells not reached are recorded as NOT_REACHED and "
                 "are never counted as negatives.",
}


def hit_probabilities(n, m_region):
    """DG-8's closure criterion: 'sized so that a kingdom-bearing cell of stated minimum measure is hit with stated
    probability'. The sample is drawn WITHOUT replacement, so the with-replacement bound 1 - (1 - mu)^n below is
    CONSERVATIVE (sampling without replacement can only raise the hit probability of a fixed subset)."""
    out = {}
    for mu in (0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02):
        out[f"measure_{mu}"] = {"subregion_cells_at_least": int(mu * m_region),
                                "hit_probability_at_least": round(1 - (1 - mu) ** n, 6)}
    return out


def freeze(cost_grid=None):
    """build and write the frozen sample. MUST be committed before `run()` is called."""
    from .core import sha256_of
    cov = coverage_census()
    aff = affordable_measure(P_MAX)
    cells, last_index = draw_sample(N_SAMPLE, P_MAX, {(tuple(a), d, p, tuple(f)) for a, d, p, f in cov["cells"]})
    for c in cells:
        c["predicted_admissible"] = predicted_admissible([c["A"], c["d"], c["p"], c["F"]])
    strata = {}
    for c in cells:
        strata[c["stratum"]] = strata.get(c["stratum"], 0) + 1
    doc = {
        "schema": "GMIDG8OffDiagonalSampleV1",
        "gap": "DG-8",
        "governing_rules": ["GMI-DA7 (the four axes and monotonicity of K(A, d, p, F))",
                            "GMI-DA11 (a negative is a claim about a REGION; monotonicity protects positives only)",
                            "protocol rule 39 (the sweep obligation applies to every index; name the swept and the "
                            "defaulted)",
                            "protocol rule 40 (every admissibility claim carries the best-constant control; margins "
                            "in fx units, one fx unit = 1 / (1.5 * 16) = 0.0416667)"],
        "status": "FROZEN_BEFORE_THE_RUN",
        "lattice": {
            "A_ladder_h": list(H_GRID), "A_ladder_lr": list(LR_GRID), "A_ladder_size": len(A_LADDER),
            "d_ladder": list(D_GRID), "p_ladder": list(P_GRID),
            "F_ladder_ecologies": list(ECOS), "F_ladder_interventions": list(IVS), "F_ladder_size": len(F_LADDER),
            "total_cells": N_TOTAL, "diagonal_cells": N_DIAGONAL, "offdiagonal_cells": N_OFFDIAGONAL,
            "ladder_provenance": {
                "A": "witness_dg7.H_GRID x witness_dg7.LR_GRID, the grid RV-377-089/-089b executed",
                "d": "RV-377-065's executed structure depths d1..d6 (STAGE_DK_V1_DEPTH_GATED.json)",
                "p": "RV-377-076's executed instrument ladder (STAGE_DK_V5_PRECISION_RESIDUAL_V1.json)",
                "F": "ecology.REGISTRY x ecology.INTERVENTIONS, the registered family"}},
        "defaults_defining_the_diagonal": {"A": list(A_DEF), "d": D_DEF, "p": P_DEF, "F": list(F_DEF),
                                           "rule": "ON the diagonal iff at most ONE coordinate is off default"},
        "indices_swept": ["A (h and lr)", "d", "p", "F (ecology and intervention)"],
        "indices_held_at_a_default": {
            "basis_column": COL, "seed": SEED, "development_events": N_EVENTS, "criterion": CRITERION,
            "theta": THETA, "carrier_family": "the registered coefficient row zoo.gradient_net, generalized in depth",
            "note": "rule 39: these six are NAMED as defaults and are NOT claimed to have been searched."},
        "coverage_before_the_run": cov,
        "affordable_subregion": aff,
        "self_checks": {"depth1_identity": depth1_identity_check(),
                        "fx8_identity": fx8_identity_check(),
                        "registered_target_reconstruction": registered_target_reconstruction_check(),
                        "constant_control_agreement": constant_control_agreement()},
        "defect_found_in_the_registered_registry": {
            "what": "ecology.REGISTRY['E_parity'] does not hold a parity target. ecology.spec_table is called with "
                    "the DICT returned by smooth.make_parity_target() and stores [int(v) for v in table], which "
                    "iterates the dict's KEYS; the stored table is the identity list 0..15 and ecology.target_of "
                    "returns {x: x}. Every claim taken on E_parity THROUGH the registry is a claim about the "
                    "binary-weighted linear target y = x / 16.",
            "independent_confirmation": "STAGE_DG9_CONSTANT_CONTROL_V1 reports E_parity's best constant as 0.8333, "
                                        "which is the identity target's value on the unseen set. The true parity "
                                        "target's best constant on that set is 1.0, because all eight unseen inputs "
                                        "have odd parity -- a NON-DISCRIMINATING ecology that the corpus has been "
                                        "recording as discriminating.",
            "not_affected": "smooth.py's own parity runs pass make_parity_target() straight to smooth.main and "
                            "never go through the registry.",
            "what_this_run_does": "NOTHING is repaired. Repairing it would change what E_parity means and make "
                                  "these cells incomparable with every prior claim recorded on that name. This run "
                                  "reproduces the registered semantics exactly and records the defect."},
        "cost_calibration_disclosure": {
            "why": "these cells were EXECUTED BEFORE THE FREEZE, to measure the cost of one cell and size the "
                   "sample. The frozen predictions below are therefore informed by them and that is disclosed here "
                   "rather than left for a reader to discover, as RV-377-082 disclosed its own unfrozen scan.",
            "cells": "every (h, d) with param_count <= 1500, at p = fx12, A-lr = 2, F = (E_smooth3, no_revoke)",
            "grid": cost_grid or {}},
        "sampling": {
            "construction": "4-dimensional Halton sequence in bases 2, 3, 5, 7, indices 1, 2, 3, ... in order; "
                            "coordinate k of point i is the radical inverse phi_b(i) mapped by floor(u * |ladder|) "
                            "onto the declared ladder order. Deterministic: no seed, no randomness, no discretion.",
            "acceptance": "a point is KEPT iff it is off the diagonal (>= 2 coordinates off default), affordable "
                          "(param_count <= P_MAX), never previously evaluated (the frozen coverage set above), and "
                          "not already drawn.",
            "P_MAX": P_MAX, "n_requested": N_SAMPLE, "n_drawn": len(cells),
            "halton_indices_consumed": last_index - 1,
            "strata_drawn": dict(sorted(strata.items())),
            "hit_probabilities": hit_probabilities(len(cells), aff["affordable_offdiagonal_cells"]),
            "closure_criterion_statement":
                "DG-8 closes on a declared low-discrepancy sample sized so that a kingdom-bearing cell of stated "
                "minimum measure is hit with stated probability. THIS SAMPLE: a sub-region of relative measure "
                "0.5 % of the affordable off-diagonal region is hit with probability >= 0.988; 0.2 % with "
                ">= 0.835; 0.1 % with >= 0.593. Measures are of the AFFORDABLE off-diagonal region "
                f"({aff['affordable_offdiagonal_cells']} cells, "
                f"{aff['fraction_of_offdiagonal_region_affordable']:.3f} of the whole off-diagonal region); the "
                "unaffordable complement is NOT sampled and NOT spoken about."},
        "evaluation_of_a_cell": {
            "capability": "ecology.run_genotype on the charged Machine under the cell's instrument, its intervention "
                          "and its ecology, with deep_gradient_net(h, lr, d) as the genotype; capability is the "
                          "registered 1 - mean_abs_error / 1.5 on the unseen criterion",
            "admissible": "capability >= theta = 0.85",
            "best_constant_control": "rule 40: the strongest single constant on the SAME (p, F) cell, computed "
                                     "exactly as a median of the evaluation targets",
            "margin_unit": "REGISTERED fx units, 1 / (1.5 * 16) = 0.0416667 of capability, at every instrument -- "
                           "using the instrument's own finer unit would flatter a witness for being given more bits",
            "valid_witness": "admissible AND the ecology is DISCRIMINATING at theta AND margin >= 1 registered fx "
                             "unit"},
        "sizing": SIZING,
        "frozen_predictions": FROZEN_PREDICTIONS,
        "what_would_falsify_the_diagonal_derived_negatives": WHAT_WOULD_FALSIFY_THE_DIAGONAL_NEGATIVES,
        "follow_up_stages_declared_in_advance": {
            "stage_2_intervention_family": "for every cell that is a VALID WITNESS under its own sampled "
                                           "intervention, the full six-intervention family is charged at the same "
                                           "(A, d, p, ecology).",
            "stage_3_one_axis_shadows": "for every ADMISSIBLE off-diagonal cell, its one-axis shadows are evaluated, "
                                        "so C5 can be decided. Shadows are DIAGONAL cells and their results are "
                                        "reported separately from the sample.",
            "guard": f"the two follow-up stages share a {FOLLOWUP_WALLCLOCK_GUARD_S} s wall-clock guard; anything "
                     "not reached is recorded as NOT_REACHED."},
        "cells": cells,
    }
    doc["sample_sha256"] = sha256_of({k: v for k, v in doc.items() if k != "sample_sha256"})
    json.dump(doc, open(SAMPLE_PATH, "w"), indent=1, sort_keys=True, default=str)
    return doc


# ============================================================================================================ THE RUN
def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def _balanced_accuracy(pairs):
    """pairs of (predicted: bool, actual: bool)."""
    tp = sum(1 for p, a in pairs if p and a)
    fn = sum(1 for p, a in pairs if not p and a)
    tn = sum(1 for p, a in pairs if not p and not a)
    fp = sum(1 for p, a in pairs if p and not a)
    tpr = tp / (tp + fn) if tp + fn else None
    tnr = tn / (tn + fp) if tn + fp else None
    ba = None if tpr is None or tnr is None else round((tpr + tnr) / 2, 4)
    return {"TP": tp, "FP": fp, "TN": tn, "FN": fn, "TPR": None if tpr is None else round(tpr, 4),
            "TNR": None if tnr is None else round(tnr, 4), "balanced_accuracy": ba}


PRE_WIT1_ECOS = ("E_smooth1", "E_smooth3", "E_sym3", "E_sym5", "E_parity")   # the five of RV-377-102's invariant
CEILING_ECOS = ("E_smooth3", "E_sym5")                                       # the two of RV-377-089's ceiling


def run(freeze_commit="UNRECORDED"):
    from .core import sha256_of
    doc = json.load(open(SAMPLE_PATH))
    check = sha256_of({k: v for k, v in doc.items() if k != "sample_sha256"})
    if check != doc["sample_sha256"]:
        raise RuntimeError("the frozen sample does not match its own sha256; refusing to run")

    t0 = time.time()
    results, not_reached = [], []
    for c in doc["cells"]:
        if time.time() - t0 > PRIMARY_WALLCLOCK_GUARD_S:
            not_reached.append(c)
            continue
        r = evaluate_cell([c["A"], c["d"], c["p"], c["F"]])
        r["halton_index"] = c["halton_index"]
        r["predicted_admissible"] = c["predicted_admissible"]
        results.append(r)
        if len(results) % 50 == 0:
            print(f"  {len(results)}/{len(doc['cells'])}  {time.time() - t0:.0f}s  "
                  f"admissible so far {sum(1 for x in results if x['admissible'])}", flush=True)
    t_primary = time.time() - t0

    # ------------------------------------------------------------------- stage 2: the full intervention family
    t1 = time.time()
    stage2, stage2_skipped = [], []
    for r in [x for x in results if x["valid_witness"]]:
        if time.time() - t1 > FOLLOWUP_WALLCLOCK_GUARD_S * 0.5:
            stage2_skipped.append(r)
            continue
        caps = caps_all_interventions(r["A"][0], r["A"][1], r["d"], r["p"], r["F"][0])
        vals = [v for v in caps.values() if v is not None]
        stage2.append({"A": r["A"], "d": r["d"], "p": r["p"], "ecology": r["F"][0],
                       "sampled_intervention": r["F"][1], "by_intervention": caps,
                       "min_over_six": min(vals) if vals else None,
                       "admissible_all_six": bool(vals) and len(vals) == len(IVS) and min(vals) >= THETA,
                       "best_constant_capability": r["best_constant_capability"],
                       "margin_of_min_registered_fx_units":
                           None if not vals else round((min(vals) - r["best_constant_capability"])
                                                       / FX_UNIT_REGISTERED, 4)})

    # ------------------------------------------------------------------- stage 3: the one-axis shadows
    shadow_cache, stage3, stage3_skipped = {}, [], []
    for r in [x for x in results if x["admissible"]]:
        if time.time() - t1 > FOLLOWUP_WALLCLOCK_GUARD_S:
            stage3_skipped.append(r)
            continue
        sh = []
        for s in shadows([r["A"], r["d"], r["p"], r["F"]]):
            key = json.dumps([list(s[0]), s[1], s[2], list(s[3])])
            if key not in shadow_cache:
                shadow_cache[key] = evaluate_cell([list(s[0]), s[1], s[2], list(s[3])])
            sr = shadow_cache[key]
            sh.append({"A": sr["A"], "d": sr["d"], "p": sr["p"], "F": sr["F"],
                       "capability": sr["capability"], "admissible": sr["admissible"]})
        stage3.append({"cell": {"A": r["A"], "d": r["d"], "p": r["p"], "F": r["F"]},
                       "capability": r["capability"], "shadows": sh,
                       "n_shadows": len(sh),
                       "all_shadows_inadmissible": bool(sh) and not any(s["admissible"] for s in sh),
                       "product_effect": bool(sh) and not any(s["admissible"] for s in sh)})
    t_followup = time.time() - t1

    # ------------------------------------------------------------------------------------------------ scoring
    ev = results
    adm = [r for r in ev if r["admissible"]]
    ceiling_hits = sorted([r for r in ev if r["F"][0] in CEILING_ECOS and r["admissible"]],
                          key=lambda r: -r["capability"])
    valid_pre_wit1 = sorted([r for r in ev if r["valid_witness"] and r["F"][0] in PRE_WIT1_ECOS],
                            key=lambda r: -r["margin_registered_fx_units"])
    robust_pre_wit1 = [s for s in stage2 if s["ecology"] in PRE_WIT1_ECOS and s["admissible_all_six"]
                       and (s["margin_of_min_registered_fx_units"] or 0) >= 1.0]
    product_cells = [s for s in stage3 if s["product_effect"]]

    d_hi = [r["capability"] for r in ev if r["d"] >= 4]
    d_lo = [r["capability"] for r in ev if r["d"] == 1]
    p_hi = [r["capability"] for r in ev if r["p"] in ("fx24", "fx32", "wide")]
    p_lo = [r["capability"] for r in ev if r["p"] in ("fx8", "fx10")]
    ba = _balanced_accuracy([(r["predicted_admissible"], r["admissible"]) for r in ev])

    def mean(xs):
        return round(sum(xs) / len(xs), 6) if xs else None

    scores = {
        "C2_CEILING_FALLS_OFF_THE_DIAGONAL": {
            "n_cells_on_E_smooth3_or_E_sym5_evaluated": sum(1 for r in ev if r["F"][0] in CEILING_ECOS),
            "n_admissible": len(ceiling_hits),
            "verdict": "PREDICTION HOLDS -- the ceiling does not survive off the diagonal" if ceiling_hits
                       else "PREDICTION FAILS -- the ceiling is UPHELD over the sampled off-diagonal region"},
        "C3_DEPTH_HELPS": {
            "median_capability_d_ge_4": _median(d_hi), "n_d_ge_4": len(d_hi),
            "median_capability_d_eq_1": _median(d_lo), "n_d_eq_1": len(d_lo),
            "verdict": "HOLDS" if (d_hi and d_lo and _median(d_hi) > _median(d_lo)) else "FAILS"},
        "C4_PRECISION_HURTS": {
            "mean_capability_fx24_fx32_wide": mean(p_hi), "n_high": len(p_hi),
            "mean_capability_fx8_fx10": mean(p_lo), "n_low": len(p_lo),
            "verdict": "HOLDS" if (p_hi and p_lo and mean(p_hi) < mean(p_lo)) else "FAILS"},
        "C5_PRODUCT_EFFECT": {
            "n_admissible_cells_with_shadows_evaluated": len(stage3),
            "n_with_every_shadow_inadmissible": len(product_cells),
            "verdict": "HOLDS -- the product holds what no single axis reaches" if product_cells
                       else "FAILS -- nothing in the sampled product exceeds the diagonal"},
        "C6_VALID_WITNESS_COUNT": {
            "n_valid_witnesses_on_the_five_pre_E_wit1_ecologies": len(valid_pre_wit1),
            "predicted_interval": [1, 25],
            "verdict": "HOLDS" if 1 <= len(valid_pre_wit1) <= 25 else "FAILS"},
        "C7_ADMISSIBLE_RATE": {
            "n_evaluated": len(ev), "n_admissible": len(adm),
            "fraction": round(len(adm) / len(ev), 6) if ev else None,
            "predicted_interval": [0.04, 0.22],
            "verdict": "HOLDS" if ev and 0.04 <= len(adm) / len(ev) <= 0.22 else "FAILS"},
        "C8_PER_CELL_PREDICTOR": {
            **ba, "predicted_threshold": 0.70,
            "verdict": "HOLDS" if (ba["balanced_accuracy"] or 0) >= 0.70 else "FAILS"},
    }

    by_stratum = {}
    for r in ev:
        s = by_stratum.setdefault(r["stratum"], {"n": 0, "admissible": 0, "valid_witness": 0, "best": -1.0})
        s["n"] += 1
        s["admissible"] += r["admissible"]
        s["valid_witness"] += r["valid_witness"]
        s["best"] = max(s["best"], r["capability"])
    by_axis = {}
    for key, get in (("d", lambda r: r["d"]), ("p", lambda r: r["p"]),
                     ("ecology", lambda r: r["F"][0]), ("intervention", lambda r: r["F"][1])):
        t = {}
        for r in ev:
            k = str(get(r))
            u = t.setdefault(k, {"n": 0, "admissible": 0, "best": -1.0, "sum": 0.0})
            u["n"] += 1
            u["admissible"] += r["admissible"]
            u["best"] = max(u["best"], r["capability"])
            u["sum"] += r["capability"]
        for k, u in t.items():
            u["mean"] = round(u["sum"] / u["n"], 4)
            del u["sum"]
        by_axis[key] = dict(sorted(t.items()))

    receipt = {
        "schema": "GMIDG8OffDiagonalResultV1", "gap": "DG-8",
        "frozen_sample_sha256": doc["sample_sha256"],
        "freeze_commit": freeze_commit,
        "n_cells_frozen": len(doc["cells"]), "n_evaluated": len(ev), "n_not_reached": len(not_reached),
        "primary_seconds": round(t_primary, 1), "followup_seconds": round(t_followup, 1),
        "coverage_before_the_run": doc["coverage_before_the_run"]["true_coverage_fraction"],
        "offdiagonal_coverage_before_the_run": doc["coverage_before_the_run"]["offdiagonal_coverage_fraction"],
        "scores": scores,
        "summary_by_stratum": dict(sorted(by_stratum.items())),
        "summary_by_axis": by_axis,
        "cells_contradicting_a_diagonal_derived_negative": {
            "RV_377_089_ceiling_on_E_smooth3_and_E_sym5": ceiling_hits,
            "RV_377_102_fragility_on_the_five_registered_ecologies__single_intervention_valid_witnesses":
                valid_pre_wit1,
            "RV_377_102_fragility__intervention_robust_under_all_six": robust_pre_wit1},
        "product_effect_cells": product_cells,
        "stage_2_intervention_family": stage2,
        "stage_3_shadows": stage3,
        "stage_2_skipped_for_budget": len(stage2_skipped), "stage_3_skipped_for_budget": len(stage3_skipped),
        "not_reached": not_reached,
        "claim_ceiling": "exact charged replay at scope. One carrier family (the registered coefficient row, "
                         "generalized in depth), one basis column, one seed, the registered 16-event protocol and "
                         "the unseen criterion. A hit here is an EXISTENCE result about the off-diagonal region of "
                         "the closure lattice. It is not a kingdom claim: nothing here shows a carrier that resists "
                         "bounded reduction, only that admissibility verdicts recorded on the diagonal do not "
                         "transport off it.",
        "cells": ev,
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    os.makedirs(RES, exist_ok=True)
    json.dump(receipt, open(RECEIPT_PATH, "w"), indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["freeze"]:
        grid = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
        d = freeze(cost_grid=grid)
        print("frozen", len(d["cells"]), "cells; sha", d["sample_sha256"][:16])
        print("coverage before the run:", d["coverage_before_the_run"]["true_coverage_fraction"])
    elif sys.argv[1:2] == ["run"]:
        r = run(freeze_commit=sys.argv[2] if len(sys.argv) > 2 else "UNRECORDED")
        print(json.dumps(r["scores"], indent=1))
