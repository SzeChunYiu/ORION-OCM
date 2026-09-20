"""Route B -- materially independent oracle for the Z8 hostile ingredients.

Written from FREEZE_V1.md alone; imports nothing from Route A.  Where Route A
enumerates next-state tables with per-address majority outputs and scans the
price grid cell by cell, this file

  * enumerates FULL (output table, next-state table) pairs at b <= 1,
  * proves every b = 2 floor by an explicit constructive witness machine plus
    a closed-form lower bound, or by full enumeration where the grammar makes
    that feasible (INPUT_ONLY: 16 next functions x 256 output tables),
  * derives every argmin SET as a piecewise-constant function of the price from
    the lower convex envelope's supporting slopes (collinearity at breakpoints),
    and only then reads that function at the grid points.

Stdlib only; exact fractions.Fraction / int; Python 3.8 compatible.

Run:  python3 -I -B independent_z8_oracle_v1.py
"""
import itertools
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
L = 4
WIN = (2, 3)
MODES = (0, 1, 2)
ETAS = (1, 2, 3)
SEQS = list(itertools.product((0, 1), repeat=L))
GRID = [F(j, 16) for j in range(25)]
EPS = F(1, 64)
Q7 = [F(1, 5), F(1, 4), F(1, 3), F(1, 2), F(2, 3), F(3, 4), F(4, 5)]
NOISE = [F(1, 16), F(1, 8), F(1, 4)]
WEIGHTS = [F(1, 4), F(1, 2), F(3, 4)]
KAPPAS = [F(1, 32), F(1, 8)]
REGISTERED = {"b0_m0": "0", "b0_m1": "1/2", "b0_m2": "1/2", "b1_m0": "0", "b1_m1": "0",
              "b1_m2": "5/16", "b2_m0": "0", "b2_m1": "0", "b2_m2": "0"}


# ------------------------------------------------------------ laws (exact)
def bern(q, x):
    return q if x == 1 else 1 - q


def law_uniform():
    return dict((w, F(1, 16)) for w in SEQS)


def law_iid(q):
    out = {}
    for w in SEQS:
        pr = F(1)
        for x in w:
            pr *= bern(q, x)
        out[w] = pr
    return out


def law_period2():
    return dict((w, F(1, 4) if (w[2] == w[0] and w[3] == w[1]) else F(0)) for w in SEQS)


def law_switch(q, q2):
    out = {}
    for w in SEQS:
        pr = F(1)
        for t, x in enumerate(w):
            pr *= bern(q if t < 2 else q2, x)
        out[w] = pr
    return out


# ------------------------------------------------------------ machines
def run_error(law, window, m, b, nxt, out, grammar, start=0):
    """Error rate of one explicit machine.  out is indexed by state (MOORE)
    or by address (MEALY / INPUT_ONLY); nxt is indexed by address, or by cur
    alone for INPUT_ONLY."""
    err = F(0)
    for w, pr in law.items():
        if pr == 0:
            continue
        st = start
        e = 0
        for t in range(L):
            c = w[t]
            a = st * 2 + c
            if t in window:
                y = out[st] if grammar == "MOORE" else out[a]
                if y != w[t - m]:
                    e += 1
            st = nxt[c] if grammar == "INPUT_ONLY" else nxt[a]
        err += pr * e
    return err / len(window)


def all_machines(b, grammar):
    ns = 2 ** b
    na = ns * 2
    if grammar == "INPUT_ONLY":
        nxts = list(itertools.product(range(ns), repeat=2))
        outs = list(itertools.product((0, 1), repeat=na))
    elif grammar == "MOORE":
        nxts = list(itertools.product(range(ns), repeat=na))
        outs = list(itertools.product((0, 1), repeat=ns))
    else:
        nxts = list(itertools.product(range(ns), repeat=na))
        outs = list(itertools.product((0, 1), repeat=na))
    for nxt in nxts:
        for out in outs:
            yield nxt, out


def floor_full(law, window, m, b, grammar):
    best = None
    for nxt, out in all_machines(b, grammar):
        e = run_error(law, window, m, b, nxt, out, grammar)
        if best is None or e < best:
            best = e
    return best


def witness_b2(m, grammar):
    """Four-state machine whose state stores (x_{t-1}, x_{t-2}): s = 2*x_{t-1} + x_{t-2}."""
    nxt = tuple(2 * (a % 2) + ((a // 2) // 2) for a in range(8))
    if grammar == "MOORE":
        out = tuple((s // 2) if m == 1 else (s % 2) if m == 2 else 0 for s in range(4))
    else:
        out = tuple((a % 2) if m == 0 else ((a // 2) // 2) if m == 1 else ((a // 2) % 2) for a in range(8))
    return nxt, out


def floors_for(law, window, grammar):
    """All nine floors; records the method used at b = 2."""
    fl = {}
    method = {}
    for b in (0, 1):
        for m in MODES:
            fl["b%d_m%d" % (b, m)] = floor_full(law, window, m, b, grammar)
    for m in MODES:
        key = "b2_m%d" % m
        if grammar == "INPUT_ONLY":
            fl[key] = floor_full(law, window, m, 2, grammar)
            method[key] = "full enumeration of 16 next functions x 256 output tables"
        elif grammar == "MOORE" and m == 0:
            # closed form: a Moore output at time t is a function of x_0..x_{t-1};
            # under every law here x_t is independent of that prefix with
            # P(x_t = 1 | prefix) in {q, 1-q, 1/2}, so no output beats min(q, 1-q)
            # per scored moment; the constant output attains it.
            nxt, _o = witness_b2(m, grammar)
            best = None
            for out in itertools.product((0, 1), repeat=4):
                e = run_error(law, window, m, 2, nxt, out, grammar)
                if best is None or e < best:
                    best = e
            lb = F(0)
            for t in window:
                # exact Bayes error of predicting x_t from the prefix under `law`
                pref = {}
                for w, pr in law.items():
                    pref.setdefault(w[:t], [F(0), F(0)])[w[t]] += pr
                lb += sum(min(v) for v in pref.values())
            lb = lb / len(window)
            fl[key] = lb
            method[key] = ("closed-form lower bound (Bayes error of x_t given the prefix) = %s; "
                           "best Moore output on the shift-register witness attains %s" % (lb, best))
            if best != lb:
                sys.exit("Moore now-channel: witness %s does not attain the bound %s" % (best, lb))
        else:
            nxt, out = witness_b2(m, grammar)
            e = run_error(law, window, m, 2, nxt, out, grammar)
            fl[key] = e
            method[key] = "constructive shift-register witness attains %s (a floor is >= 0, so 0 is exact)" % e
            if e != 0:
                sys.exit("b=2 witness for %s/%s does not attain zero: %s" % (grammar, key, e))
    return fl, method


# ------------------------------------------------------------ envelope algebra
def hull(points):
    pts = sorted(points)
    h = []
    for x, y in pts:
        while len(h) >= 2:
            (x1, y1), (x2, y2) = h[-2], h[-1]
            if (y2 - y1) * (x - x1) >= (y - y1) * (x2 - x1):
                h.pop()
            else:
                break
        h.append((x, y))
    return h


def argmin_function(E, rho):
    """Return (breakpoints desc, sets) describing the argmin SET as a
    piecewise-constant function of the price, derived from supporting lines:
    strictly between consecutive slopes the unique hull vertex wins; at a slope
    every level collinear with that supporting line ties."""
    pts = [(rho[k], E[k], k) for k in E]
    h = hull([(x, y) for x, y, _k in pts])
    slopes = []
    for i in range(1, len(h)):
        (x0, y0), (x1, y1) = h[i - 1], h[i]
        slopes.append((y0 - y1) / (x1 - x0))
    # slopes are decreasing along the hull (convexity); vertices in hull order
    verts = []
    for (x, y) in h:
        verts.append(tuple(sorted(k for (xx, yy, k) in pts if xx == x and yy == y)))

    def at(lam):
        # find the hull segment whose slope brackets lam
        if not slopes or lam > slopes[0]:
            return verts[0]
        for i, sl in enumerate(slopes):
            if lam == sl:
                (x0, y0) = h[i]
                # every level on the supporting line y = y0 - lam*(x - x0)
                return tuple(sorted(k for (x, y, k) in pts if y == y0 - lam * (x - x0)))
            if lam > sl:
                return verts[i]
        return verts[-1]
    return slopes, at


def prof(eta, p, fl):
    return dict((k, eta * sum(p[m] * fl["b%d_m%d" % (k, m)] for m in MODES)) for k in (0, 1, 2))


def niche(E, rho):
    h = hull([(rho[k], E[k]) for k in E])
    return rho[1] in [x for (x, _y) in h]


def raw_pair(E):
    return (E[0] - E[1], E[1] - E[2])


def fail_set(p, fl, k):
    return tuple(m for m in MODES if p[m] > 0 and fl["b%d_m%d" % (k, m)] > 0)


def worlds():
    out = []
    for eta in ETAS:
        for a in range(9):
            for b in range(9 - a):
                out.append((eta, (F(a, 8), F(b, 8), F(8 - a - b, 8))))
    return out


RHO = {0: 0, 1: 1, 2: 2}


def view(w, fl, rho=RHO, pricemap=None):
    eta, p = w
    E = prof(eta, p, fl)
    _sl, at = argmin_function(E, rho)
    pm = pricemap or (lambda x: x)
    sel = dict((lam, at(pm(lam))) for lam in GRID)
    return {"E": E, "SEL": sel, "NICHE": niche(E, rho), "THR": raw_pair(E),
            "FAIL": dict((lam, fail_set(p, fl, min(sel[lam]))) for lam in GRID)}


def moved(ws, base, other):
    r = {"V_SEL_cells": 0, "V_SEL_worlds": 0, "V_NICHE": 0, "V_THR": 0, "V_FAIL_worlds": 0}
    for w in ws:
        b, o = base[w], other(w)
        sc = sum(1 for lam in GRID if b["SEL"][lam] != o["SEL"][lam])
        fc = sum(1 for lam in GRID if b["FAIL"][lam] != o["FAIL"][lam])
        r["V_SEL_cells"] += sc
        r["V_SEL_worlds"] += 1 if sc else 0
        r["V_FAIL_worlds"] += 1 if fc else 0
        r["V_NICHE"] += 1 if b["NICHE"] != o["NICHE"] else 0
        r["V_THR"] += 1 if b["THR"] != o["THR"] else 0
    return r


def two_level_set(T, lam):
    if lam < T:
        return (1,)
    if lam == T:
        return (0, 1)
    return (0,)


# ------------------------------------------------------------ greedy
def greedy_floors(law, window):
    out = {}
    for b in (0, 1, 2):
        ns = 2 ** b
        na = ns * 2
        outs = list(itertools.product((0, 1), repeat=na))
        for m in MODES:
            def best_out(nxt):
                return min(run_error(law, window, m, b, nxt, o, "MEALY") for o in outs)
            cur = [0] * na
            ce = best_out(tuple(cur))
            improved = True
            while improved:
                improved = False
                for i in range(na):
                    for v in range(ns):
                        if v == cur[i]:
                            continue
                        old = cur[i]
                        cur[i] = v
                        e = best_out(tuple(cur))
                        if e < ce:
                            ce, improved = e, True
                        else:
                            cur[i] = old
            out["b%d_m%d" % (b, m)] = ce
    return out


def main():
    res = {"schema": "GMI_833_Z8_HOSTILE_INGREDIENTS_ORACLE_V1", "route": "B", "imports_route_A": False}
    uni = law_uniform()
    fl_base, meth_base = floors_for(uni, WIN, "MEALY")
    if dict((k, str(v)) for k, v in fl_base.items()) != REGISTERED:
        sys.exit("registered floors not reproduced: %s" % fl_base)
    fl_w3, meth_w3 = floors_for(uni, (3,), "MEALY")
    fl_p2, meth_p2 = floors_for(law_period2(), WIN, "MEALY")
    fl_mo, meth_mo = floors_for(uni, WIN, "MOORE")
    fl_io, meth_io = floors_for(uni, WIN, "INPUT_ONLY")
    res["floors"] = dict((name, dict((k, str(v)) for k, v in fl.items()))
                         for name, fl in (("BASE", fl_base), ("WINDOW3", fl_w3), ("PERIOD2", fl_p2),
                                          ("MOORE", fl_mo), ("INPUT_ONLY", fl_io)))
    res["b2_method"] = {"BASE": meth_base, "WINDOW3": meth_w3, "PERIOD2": meth_p2, "MOORE": meth_mo, "INPUT_ONLY": meth_io}

    ws = worlds()
    base = dict((w, view(w, fl_base)) for w in ws)
    mv = {}

    # I1
    triple = 0
    tdeg = 0
    selm = 0
    tfail = 0
    for w in ws:
        E = base[w]["E"]
        d1, d2 = raw_pair(E)
        if d1 == d2:
            triple += 1
            if d1 == 0:
                tdeg += 1
        sl, at = argmin_function(E, RHO)
        if any(at(s0 - EPS) != at(s0 + EPS) for s0 in sl if s0 > 0):
            selm += 1
        if d1 > d2:
            ok = (set((0, 1)) <= set(at(d1)) and at(d1 - EPS) == (1,) and at(d1 + EPS) == (0,)
                  and set((1, 2)) <= set(at(d2)) and at(d2 - EPS) == (2,) and at(d2 + EPS) == (1,))
            if not ok:
                tfail += 1
    mv["I1"] = {"triple_tie_worlds": triple, "triple_tie_degenerate": tdeg, "V_SEL_moved_worlds": selm,
                "tie_structure_failures": tfail}

    # I2a / I2b
    mv["I2a"] = {}
    mv["I2b"] = {}
    for eps in NOISE:
        fla = dict((k, (1 - 2 * eps) * v + eps) for k, v in fl_base.items())
        r = moved(ws, base, lambda w, fla=fla: view(w, fla))
        mv["I2a"][str(eps)] = {"V_NICHE": r["V_NICHE"], "V_SEL_cells": r["V_SEL_cells"], "V_THR": r["V_THR"]}
        flb = dict(fl_base)
        for b in (0, 1, 2):
            flb["b%d_m2" % b] = (1 - 2 * eps) * fl_base["b%d_m2" % b] + eps
        r = moved(ws, base, lambda w, flb=flb: view(w, flb))
        mv["I2b"][str(eps)] = {"V_NICHE": r["V_NICHE"]}
    r = moved(ws, base, lambda w: view(w, fl_w3))
    mv["I2c"] = {"V_NICHE": r["V_NICHE"], "V_THR": r["V_THR"], "V_SEL_worlds": r["V_SEL_worlds"]}
    r = moved(ws, base, lambda w: view(w, fl_p2))
    mv["I3"] = {"V_NICHE": r["V_NICHE"], "V_THR": r["V_THR"], "V_SEL_worlds": r["V_SEL_worlds"], "V_FAIL_worlds": r["V_FAIL_worlds"]}

    # I4a: two-level shift, argmin sets in closed form
    r0 = dict((q, floor_full(law_iid(q), WIN, 1, 0, "MEALY")) for q in Q7)
    one_bit_zero = all(floor_full(law_iid(q), WIN, 1, 1, "MEALY") == 0 for q in Q7)
    cells = ms = sb = outside = comp = 0
    for qa in Q7:
        for qb in Q7:
            for eta in ETAS:
                for k in range(9):
                    p = F(k, 8)
                    Ta, Tb = eta * p * r0[qa], eta * p * r0[qb]
                    for lam in GRID:
                        cells += 1
                        m_ = two_level_set(Ta, lam) != two_level_set(Tb, lam)
                        ms += m_
                        if min(Ta, Tb) < lam < max(Ta, Tb):
                            sb += 1
                        else:
                            outside += m_
                        if qb == 1 - qa:
                            comp += m_
    mv["I4a"] = {"cells": cells, "moved_set_valued": ms, "strictly_between_cells": sb,
                 "outside_strict_band_moved_set": outside, "complementary_pair_cells_moved": comp}
    res["two_level_R0"] = dict((str(q), str(v)) for q, v in r0.items())
    res["two_level_one_bit_floor_zero"] = one_bit_zero
    res["nonstationary_floors"] = dict(("%s|%s" % (qa, qb), str(floor_full(law_switch(qa, qb), WIN, 1, 0, "MEALY")))
                                       for qa in Q7 for qb in Q7)

    # I5
    ra = {0: 1, 1: 3, 2: 5}
    r = moved(ws, base, lambda w: view(w, fl_base, ra, lambda x: x / 2))
    mv["I5a"] = {"V_NICHE": r["V_NICHE"], "V_SEL_cells": r["V_SEL_cells"]}
    rb = {0: 0, 1: 1, 2: 3}
    r = moved(ws, base, lambda w: view(w, fl_base, rb))
    mv["I5b"] = {"V_NICHE": r["V_NICHE"], "V_SEL_cells": r["V_SEL_cells"]}
    rc = {0: 0, 1: 2, 2: 3}
    r = moved(ws, base, lambda w: view(w, fl_base, rc))
    mv["I5c"] = {"V_NICHE": r["V_NICHE"], "V_SEL_cells": r["V_SEL_cells"]}

    # I6
    tri = [p for (eta, p) in ws if eta == 1]
    E1 = dict((p, prof(1, p, fl_base)) for p in tri)
    AT = dict((p, argmin_function(E1[p], RHO)[1]) for p in tri)
    cells = common = kept = differs = 0
    for ph in tri:
        for pc in tri:
            for wgt in WEIGHTS:
                Em = dict((k, wgt * E1[ph][k] + (1 - wgt) * E1[pc][k]) for k in (0, 1, 2))
                _s, atm = argmin_function(Em, RHO)
                for lam in GRID:
                    cells += 1
                    sh, sc_, sm = AT[ph](lam), AT[pc](lam), atm(lam)
                    if sm != sc_:
                        differs += 1
                    c = set(sh) & set(sc_)
                    if c:
                        common += 1
                        if c <= set(sm):
                            kept += 1
    mv["I6a"] = {"cells": cells, "cells_with_a_common_level": common, "common_level_kept_by_every_weight": kept,
                 "history_weighted_differs_from_current_optimum": differs}
    mv["I6b"] = {}
    for kappa in KAPPAS:
        cells = mvd = mvpos = band = 0
        for ph in tri:
            for pc in tri:
                for lam in GRID:
                    inc = min(AT[ph](lam))
                    costs = dict((k, E1[pc][k] + lam * k) for k in (0, 1, 2))
                    ex = costs[inc] - min(costs.values())
                    curset = AT[pc](lam)
                    verdict = (inc,) if ex <= kappa else curset
                    cells += 1
                    if verdict != curset:
                        mvd += 1
                        if ex > 0:
                            mvpos += 1
                    if 0 < ex <= kappa:
                        band += 1
        mv["I6b"][str(kappa)] = {"cells": cells, "moved": mvd, "moved_with_positive_excess": mvpos,
                                 "cells_with_0_lt_excess_le_kappa": band}

    # I7
    r = moved(ws, base, lambda w: view(w, fl_mo))
    mv["I7a"] = {"V_NICHE": r["V_NICHE"], "V_SEL_cells": r["V_SEL_cells"], "V_THR": r["V_THR"], "V_FAIL_worlds": r["V_FAIL_worlds"]}
    r = moved(ws, base, lambda w: view(w, fl_io))
    mv["I7b"] = {"V_NICHE": r["V_NICHE"], "V_SEL_cells": r["V_SEL_cells"], "V_THR": r["V_THR"], "V_FAIL_worlds": r["V_FAIL_worlds"]}
    st_inv = True
    in_inv = True
    for m in MODES:
        for nxt, out in all_machines(1, "MEALY"):
            e0 = run_error(uni, WIN, m, 1, nxt, out, "MEALY")
            # states relabelled 0<->1, start state carried to 1
            nn = [0] * 4
            no = [0] * 4
            for st in (0, 1):
                for c in (0, 1):
                    nn[(1 - st) * 2 + c] = 1 - nxt[st * 2 + c]
                    no[(1 - st) * 2 + c] = out[st * 2 + c]
            if run_error(uni, WIN, m, 1, tuple(nn), tuple(no), "MEALY", start=1) != e0:
                st_inv = False
            # symbol swap in machine and task: relabel the input alphabet everywhere
            nn2 = tuple(nxt[st * 2 + (1 - c)] for st in (0, 1) for c in (0, 1))
            no2 = tuple(1 - out[st * 2 + (1 - c)] for st in (0, 1) for c in (0, 1))
            law_sw = dict((tuple(1 - x for x in w), pr) for w, pr in uni.items())
            if run_error(law_sw, WIN, m, 1, nn2, no2, "MEALY") != e0:
                in_inv = False
    mv["I7c"] = {"state_relabel_invariant": st_inv, "input_relabel_invariant": in_inv}

    # I8
    mv["I8"] = {"greedy_single_start_floors": dict((k, str(v)) for k, v in greedy_floors(uni, WIN).items())}

    res["moved"] = mv
    res["counts_check"] = {"worlds": len(ws), "price_grid": len(GRID)}
    # self-checks: piecewise argmin agrees with brute force on every base cell
    brute_ok = True
    for w in ws:
        E = base[w]["E"]
        for lam in GRID:
            costs = dict((k, E[k] + lam * k) for k in E)
            mn = min(costs.values())
            if tuple(sorted(k for k in E if costs[k] == mn)) != base[w]["SEL"][lam]:
                brute_ok = False
    res["self_checks"] = {"piecewise_argmin_equals_brute_force_on_base": brute_ok,
                          "registered_floors_reproduced": True}
    res["verdict"] = "GREEN" if brute_ok else "RED"
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True, default=str)
        f.write("\n")
    print(json.dumps({"verdict": res["verdict"], "floors": res["floors"], "moved": mv}, indent=1, default=str))
    return 0 if res["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
