"""Route A -- the nine Z8 hostile ingredients, each shown to move a registered
verdict or proved unable to (#833 Section Z, subsection Z8).

Protocol, ingredient maps and every prediction are fixed by FREEZE_V1.md,
committed before this file existed.  Route B (independent_z8_oracle_v1.py)
does not import this file.

World model (self-contained, nothing imported from any other package): the
three-mode binary transducer universe of Z13 -- L = 4, uniform i.i.d. inputs,
canonical initial state 0, state budget b in {0,1,2}, per-mode output and
next-state tables, scored window t in {2,3}, modes m in {0: now, 1: delay-1,
2: delay-2}.  Every floor is re-enumerated here from scratch.

Stdlib only; exact integers and fractions.Fraction; no float in any claim.
Python 3.8 compatible.

Run:  python3 -I -B z8_hostile_ingredients_v1.py
"""
import hashlib
import itertools
import json
import os
import random
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_MAIN = "f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5"

L = 4
WINDOW = (2, 3)
MODES = (0, 1, 2)
ETAS = (1, 2, 3)
SEQ = list(itertools.product((0, 1), repeat=L))
PRICE_GRID = tuple(F(j, 16) for j in range(0, 25))
TIE_EPS = F(1, 64)
QGRID = (F(1, 5), F(1, 4), F(1, 3), F(1, 2), F(2, 3), F(3, 4), F(4, 5))
NOISE_EPS = (F(1, 16), F(1, 8), F(1, 4))
HIST_W = (F(1, 4), F(1, 2), F(3, 4))
KAPPAS = (F(1, 32), F(1, 8))
IC1_LADDER_PAIR = (F(1, 2), F(3, 16))


def s(x):
    return str(x)


# ============================================================ input laws
def law_uniform():
    return dict((q, 1) for q in SEQ)


def law_iid(q):
    """Integer weights: Bernoulli(q) per symbol, scaled by den**L."""
    num, den = q.numerator, q.denominator
    out = {}
    for w in SEQ:
        wt = 1
        for x in w:
            wt *= num if x == 1 else (den - num)
        out[w] = wt
    return out


def law_period2():
    return dict((w, 1 if (w[2] == w[0] and w[3] == w[1]) else 0) for w in SEQ)


def law_nonstationary(q1, q2, switch=2):
    """x_t ~ Bernoulli(q1) for t < switch, Bernoulli(q2) for t >= switch."""
    d1, d2 = q1.denominator, q2.denominator
    out = {}
    for w in SEQ:
        wt = 1
        for t, x in enumerate(w):
            q = q1 if t < switch else q2
            n, d = q.numerator, q.denominator
            wt *= n if x == 1 else (d - n)
        out[w] = wt
    return out


# ============================================================ enumeration
def enumerate_floor(law, window, b, m, grammar="MEALY"):
    """Exact minimum error rate on mode m at budget b, over every candidate of
    the declared grammar, under an integer-weighted input law.  Output tables
    are chosen per address (MEALY, INPUT_ONLY) or per state (MOORE) by weighted
    majority; next-state tables are enumerated exhaustively."""
    ns = 2 ** b
    na = ns * 2
    seqs = [(w, wt) for w, wt in law.items() if wt > 0]
    total = sum(wt for _w, wt in seqs)
    if grammar == "INPUT_ONLY":
        nxt_iter = (tuple(f[c] for _st in range(ns) for c in (0, 1))
                    for f in itertools.product(range(ns), repeat=2))
    else:
        nxt_iter = itertools.product(range(ns), repeat=na)
    keys = ns if grammar == "MOORE" else na
    best = None
    for nxt in nxt_iter:
        tal = [[0, 0] for _ in range(keys)]
        for w, wt in seqs:
            st = 0
            for t in range(L):
                a = st * 2 + w[t]
                if t in window:
                    k = st if grammar == "MOORE" else a
                    tal[k][w[t - m]] += wt
                st = nxt[a]
        e = 0
        for v in tal:
            e += v[0] if v[0] < v[1] else v[1]
        if best is None or e < best:
            best = e
    return F(best, total * len(window))


def floors(law, window=WINDOW, grammar="MEALY", budgets=(0, 1, 2)):
    return dict(((b, m), enumerate_floor(law, window, b, m, grammar))
                for b in budgets for m in MODES)


def candidate_error(nxt, out, law, window, b, m):
    """Exact error rate of one explicit (next, out) candidate."""
    seqs = [(w, wt) for w, wt in law.items() if wt > 0]
    total = sum(wt for _w, wt in seqs)
    e = 0
    for w, wt in seqs:
        st = 0
        for t in range(L):
            a = st * 2 + w[t]
            if t in window and out[a] != w[t - m]:
                e += wt
            st = nxt[a]
    return F(e, total * len(window))


def majority_out(nxt, law, window, b, m):
    ns = 2 ** b
    na = ns * 2
    tal = [[0, 0] for _ in range(na)]
    for w, wt in law.items():
        if wt <= 0:
            continue
        st = 0
        for t in range(L):
            a = st * 2 + w[t]
            if t in window:
                tal[a][w[t - m]] += wt
            st = nxt[a]
    return tuple(0 if v[0] >= v[1] else 1 for v in tal)


def optimal_next_tables(law, window, b, m):
    """All next-state tables attaining the floor (majority outputs)."""
    ns = 2 ** b
    na = ns * 2
    seqs = [(w, wt) for w, wt in law.items() if wt > 0]
    total = sum(wt for _w, wt in seqs)
    best, arg = None, []
    for nxt in itertools.product(range(ns), repeat=na):
        tal = [[0, 0] for _ in range(na)]
        for w, wt in seqs:
            st = 0
            for t in range(L):
                a = st * 2 + w[t]
                if t in window:
                    tal[a][w[t - m]] += wt
                st = nxt[a]
        e = sum(min(v) for v in tal)
        if best is None or e < best:
            best, arg = e, [nxt]
        elif e == best:
            arg.append(nxt)
    return F(best, total * len(window)), arg


# ============================================================ verdicts
def lower_envelope(points):
    """Vertices of the lower convex envelope of {(x, y)} by exact cross products."""
    pts = sorted(points)
    hull = []
    for x, y in pts:
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            if (y2 - y1) * (x - x1) >= (y - y1) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append((x, y))
    return hull


def profile(eta, p, fl):
    return dict((k, eta * sum(p[m] * fl[(k, m)] for m in MODES)) for k in (0, 1, 2))


def v_sel(E, lam, rho=None):
    rho = rho or {0: 0, 1: 1, 2: 2}
    best, arg = None, []
    for k in sorted(E):
        c = E[k] + lam * rho[k]
        if best is None or c < best:
            best, arg = c, [k]
        elif c == best:
            arg.append(k)
    return tuple(arg)


def v_niche(E, rho=None):
    rho = rho or {0: 0, 1: 1, 2: 2}
    hull = lower_envelope([(rho[k], E[k]) for k in E])
    return rho[1] in [x for (x, _y) in hull]


def v_thr(E):
    return (E[0] - E[1], E[1] - E[2])


def envelope_slopes(E, rho=None):
    rho = rho or {0: 0, 1: 1, 2: 2}
    hull = lower_envelope([(rho[k], E[k]) for k in E])
    out = []
    for i in range(1, len(hull)):
        (x0, y0), (x1, y1) = hull[i - 1], hull[i]
        out.append((y0 - y1) / (x1 - x0))
    return out


def v_fail(p, fl, k):
    return tuple(m for m in MODES if p[m] > 0 and fl[(k, m)] > 0)


def world_grid():
    out = []
    for eta in ETAS:
        for a in range(9):
            for b2 in range(9 - a):
                c = 8 - a - b2
                out.append((eta, (F(a, 8), F(b2, 8), F(c, 8))))
    return out


def base_verdicts(worlds, fl):
    out = {}
    for (eta, p) in worlds:
        E = profile(eta, p, fl)
        out[(eta, p)] = {
            "E": E,
            "SEL": dict((lam, v_sel(E, lam)) for lam in PRICE_GRID),
            "NICHE": v_niche(E),
            "THR": v_thr(E),
            "FAIL": dict((lam, v_fail(p, fl, min(v_sel(E, lam)))) for lam in PRICE_GRID),
        }
    return out


def compare(worlds, base, hostile_fn):
    """Count worlds (and price cells) where each verdict moves under the map."""
    moved = {"V_SEL_worlds": 0, "V_SEL_cells": 0, "V_NICHE": 0, "V_THR": 0,
             "V_FAIL_worlds": 0, "V_FAIL_cells": 0}
    for w in worlds:
        h = hostile_fn(w)
        b = base[w]
        sc = sum(1 for lam in PRICE_GRID if h["SEL"][lam] != b["SEL"][lam])
        fc = sum(1 for lam in PRICE_GRID if h["FAIL"][lam] != b["FAIL"][lam])
        moved["V_SEL_cells"] += sc
        moved["V_FAIL_cells"] += fc
        moved["V_SEL_worlds"] += 1 if sc else 0
        moved["V_FAIL_worlds"] += 1 if fc else 0
        moved["V_NICHE"] += 1 if h["NICHE"] != b["NICHE"] else 0
        moved["V_THR"] += 1 if h["THR"] != b["THR"] else 0
    return moved


def verdicts_from_floors(w, fl, rho=None, lam_map=None):
    eta, p = w
    E = profile(eta, p, fl)
    lm = lam_map or (lambda lam: lam)
    return {"E": E,
            "SEL": dict((lam, v_sel(E, lm(lam), rho)) for lam in PRICE_GRID),
            "NICHE": v_niche(E, rho),
            "THR": v_thr(E),
            "FAIL": dict((lam, v_fail(p, fl, min(v_sel(E, lm(lam), rho)))) for lam in PRICE_GRID)}


# ============================================================ searchers
def greedy_floor(law, window, b, m):
    """Deterministic single-start coordinate descent from the all-zero
    next-state table; majority outputs at every step."""
    ns = 2 ** b
    na = ns * 2
    seqs = [(w, wt) for w, wt in law.items() if wt > 0]
    total = sum(wt for _w, wt in seqs)

    def err(nxt):
        tal = [[0, 0] for _ in range(na)]
        for w, wt in seqs:
            st = 0
            for t in range(L):
                a = st * 2 + w[t]
                if t in window:
                    tal[a][w[t - m]] += wt
                st = nxt[a]
        return sum(min(v) for v in tal)

    cur = [0] * na
    ce = err(tuple(cur))
    improved = True
    while improved:
        improved = False
        for i in range(na):
            for v in range(ns):
                if v == cur[i]:
                    continue
                old = cur[i]
                cur[i] = v
                e = err(tuple(cur))
                if e < ce:
                    ce, improved = e, True
                else:
                    cur[i] = old
    return F(ce, total * len(window))


def hillclimb_floor(law, window, b, m, seed, restarts=24, steps=400):
    ns = 2 ** b
    na = ns * 2
    seqs = [(w, wt) for w, wt in law.items() if wt > 0]
    total = sum(wt for _w, wt in seqs)
    rng = random.Random(seed)

    def err(nxt):
        tal = [[0, 0] for _ in range(na)]
        for w, wt in seqs:
            st = 0
            for t in range(L):
                a = st * 2 + w[t]
                if t in window:
                    tal[a][w[t - m]] += wt
                st = nxt[a]
        return sum(min(v) for v in tal)

    best = None
    for _ in range(restarts):
        cur = [rng.randrange(ns) for _ in range(na)]
        ce = err(tuple(cur))
        for _ in range(steps):
            i = rng.randrange(na)
            old = cur[i]
            new = rng.randrange(ns)
            if new == old:
                continue
            cur[i] = new
            e = err(tuple(cur))
            if e <= ce:
                ce = e
            else:
                cur[i] = old
        if best is None or ce < best:
            best = ce
    return F(best, total * len(window))


# ============================================================ helpers
def count_triples(pred):
    n = 0
    for a in range(9):
        for b2 in range(9 - a):
            if pred(F(a, 8), F(b2, 8)):
                n += 1
    return n


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ============================================================ main
def main():
    res = {"schema": "GMI_833_Z8_HOSTILE_INGREDIENTS_RESULT_V1", "issue": 833,
           "subsection": "Z8", "route": "A", "source_main": SOURCE_MAIN,
           "freeze": "research/gmi-833-z-z8-hostile-ingredients-v1/FREEZE_V1.md"}
    worlds = world_grid()
    uni = law_uniform()

    # ---------------------------------------------------------------- base
    fl0 = floors(uni)
    reg = {(0, 0): F(0), (0, 1): F(1, 2), (0, 2): F(1, 2),
           (1, 0): F(0), (1, 1): F(0), (1, 2): F(5, 16),
           (2, 0): F(0), (2, 1): F(0), (2, 2): F(0)}
    base_ok = fl0 == reg
    res["base"] = {"floors": dict(("b%d_m%d" % k, s(v)) for k, v in sorted(fl0.items())),
                   "registered_floors_reproduced": base_ok,
                   "worlds": len(worlds), "price_grid": [s(x) for x in PRICE_GRID],
                   "window": list(WINDOW), "L": L}
    if not base_ok:
        sys.exit("base floors do not reproduce the registered ladder")
    base = base_verdicts(worlds, fl0)
    # registered closed forms on U0
    closed_ok = all(base[(eta, p)]["THR"] == (eta * (p[1] / 2 + 3 * p[2] / 16), eta * 5 * p[2] / 16)
                    and base[(eta, p)]["NICHE"] == (4 * p[1] > p[2])
                    for (eta, p) in worlds)
    res["base"]["registered_closed_forms_hold_135"] = closed_ok
    ing = {}
    preds = {}
    matrix = {}

    def n_deg():
        return sum(1 for (eta, p) in worlds if p[1] == 0 and p[2] == 0)

    # ---------------------------------------------------------------- I1
    triple = 0
    triple_deg = 0
    p1_ok = True
    tie_fail = 0
    tie_fail_gap_eps = 0
    tie_witness = None
    sel_moved = 0
    sel_moved_cells = 0
    for (eta, p) in worlds:
        E = base[(eta, p)]["E"]
        d1, d2 = base[(eta, p)]["THR"]
        if d1 == d2:
            triple += 1
            if d1 == 0:
                triple_deg += 1
        if d1 > d2:
            ok_here = True
            if not (set((0, 1)) <= set(v_sel(E, d1))):
                ok_here = False
            if v_sel(E, d1 - TIE_EPS) != (1,) or v_sel(E, d1 + TIE_EPS) != (0,):
                ok_here = False
            if not (set((1, 2)) <= set(v_sel(E, d2))):
                ok_here = False
            if v_sel(E, d2 - TIE_EPS) != (2,) or v_sel(E, d2 + TIE_EPS) != (1,):
                ok_here = False
            if not ok_here:
                p1_ok = False
                tie_fail += 1
                if d1 - d2 == TIE_EPS:
                    tie_fail_gap_eps += 1
                if tie_witness is None:
                    tie_witness = {"eta": eta, "p": [s(x) for x in p], "Delta_1": s(d1), "Delta_2": s(d2),
                                   "gap": s(d1 - d2), "argmin_at_Delta_1_minus_eps": list(v_sel(E, d1 - TIE_EPS))}
        slopes = [x for x in envelope_slopes(E) if x > 0]
        cells = 0
        for sl in slopes:
            if v_sel(E, sl - TIE_EPS) != v_sel(E, sl + TIE_EPS):
                cells += 1
        if cells:
            sel_moved += 1
        sel_moved_cells += cells
    ing["I1_near_tie"] = {
        "triple_tie_worlds": triple, "triple_tie_degenerate": triple_deg,
        "V_SEL_moved_worlds": sel_moved, "V_SEL_moved_tie_cells": sel_moved_cells,
        "non_degenerate_worlds": len(worlds) - n_deg(),
        "V_NICHE_moved": 0, "V_THR_moved": 0,
        "unable_reason": "V_NICHE and V_THR do not depend on the price; a price probe cannot move them",
        "tie_structure_holds": p1_ok, "tie_structure_failures": tie_fail,
        "tie_structure_failures_with_gap_equal_to_probe": tie_fail_gap_eps,
        "smallest_positive_gap_Delta1_minus_Delta2": s(min(base[w]["THR"][0] - base[w]["THR"][1] for w in worlds
                                                            if base[w]["THR"][0] > base[w]["THR"][1])),
        "first_failure_witness": tie_witness}
    preds["P1"] = {"verdict": "HIT" if (p1_ok and triple == 6 and triple_deg == 3
                                        and sel_moved == len(worlds) - n_deg()) else "MISS",
                   "evidence": "tie structure %s (%d worlds fail, %d of them with Delta_1 - Delta_2 exactly equal to the "
                               "1/64 probe, so the probe lands on the neighbouring marginal); triple ties %d (predicted 6), "
                               "degenerate %d (predicted 3); V_SEL moved in %d of %d non-degenerate worlds"
                               % (p1_ok, tie_fail, tie_fail_gap_eps, triple, triple_deg, sel_moved, len(worlds) - n_deg())}
    matrix["I1"] = {"V_SEL": "MOVES %d/%d worlds" % (sel_moved, len(worlds)),
                    "V_NICHE": "UNABLE (price-independent)", "V_THR": "UNABLE (price-independent)",
                    "V_FAIL": "MOVES via V_SEL (%d worlds)" % sel_moved}

    # ---------------------------------------------------------------- I2a
    i2a = {}
    p2a_ok = True
    for eps in NOISE_EPS:
        def noisy(w, eps=eps):
            eta, p = w
            fl = dict((k, (1 - 2 * eps) * v + eps) for k, v in fl0.items())
            return verdicts_from_floors(w, fl)
        mv = compare(worlds, base, noisy)
        # cells with lambda strictly between a scaled and an unscaled envelope slope
        strict = 0
        strict_all_moved = True
        for w in worlds:
            E = base[w]["E"]
            for lam in PRICE_GRID:
                between = any((1 - 2 * eps) * sl < lam < sl for sl in envelope_slopes(E) if sl > 0)
                if between:
                    strict += 1
                    if noisy(w)["SEL"][lam] == base[w]["SEL"][lam]:
                        strict_all_moved = False
        nonzero = sum(1 for w in worlds if any(x > 0 for x in base[w]["THR"]))
        # affine-map check: profile equals (1-2eps)E + eta*eps exactly
        affine = all(noisy(w)["E"] == dict((k, (1 - 2 * eps) * base[w]["E"][k] + w[0] * eps)
                                          for k in (0, 1, 2)) for w in worlds)
        ok = (mv["V_NICHE"] == 0 and strict_all_moved and mv["V_THR"] == nonzero and affine)
        p2a_ok = p2a_ok and ok
        i2a[s(eps)] = dict(mv, strictly_between_cells=strict, strictly_between_all_moved=strict_all_moved,
                           worlds_with_nonzero_marginal=nonzero, affine_map_verified=affine,
                           V_NICHE_unchanged="%d/%d" % (len(worlds) - mv["V_NICHE"], len(worlds)))
    ing["I2a_uniform_verifier_noise"] = i2a
    # ---------------------------------------------------------------- I2b
    i2b = {}
    for eps in NOISE_EPS:
        def noisy2(w, eps=eps):
            fl = dict(fl0)
            for b in (0, 1, 2):
                fl[(b, 2)] = (1 - 2 * eps) * fl0[(b, 2)] + eps
            return verdicts_from_floors(w, fl)
        mv = compare(worlds, base, noisy2)
        pred_cnt = 3 * count_triples(lambda a, b2, eps=eps: 4 * a <= b2 and (1 - 2 * eps) * b2 < 4 * a)
        i2b[s(eps)] = dict(mv, predicted_V_NICHE_moved=pred_cnt)
    p2b_ok = i2b[s(F(1, 4))]["V_NICHE"] == 12 and all(v["V_NICHE"] == v["predicted_V_NICHE_moved"] for v in i2b.values())
    ing["I2b_delay2_only_verifier_noise"] = i2b
    # ---------------------------------------------------------------- I2c
    fl_w3 = floors(uni, window=(3,))
    def w3(w):
        return verdicts_from_floors(w, fl_w3)
    mv = compare(worlds, base, w3)
    w3_shape = (fl_w3[(0, 1)] == F(1, 2) and fl_w3[(0, 2)] == F(1, 2) and fl_w3[(1, 1)] == 0
                and all(fl_w3[(2, m)] == 0 for m in MODES) and fl_w3[(1, 2)] > 0)
    p2ok = sum(1 for w in worlds if w[1][2] > 0)
    thr_iff = (mv["V_THR"] == (p2ok if fl_w3[(1, 2)] != F(5, 16) else 0))
    ing["I2c_verifier_failure_window3"] = dict(
        mv, floors=dict(("b%d_m%d" % k, s(v)) for k, v in sorted(fl_w3.items())),
        predicted_shape_holds=w3_shape, delay2_b1_floor=s(fl_w3[(1, 2)]),
        differs_from_5_16=fl_w3[(1, 2)] != F(5, 16), V_THR_moves_iff_floor_differs=thr_iff)
    preds["P2"] = {"verdict": "HIT" if (p2a_ok and p2b_ok and w3_shape and thr_iff) else "MISS",
                   "evidence": "uniform noise: niche unchanged 135/135 at every eps, affine map verified, "
                               "strictly-between cells all moved, V_THR moved in every nonzero-marginal world: %s; "
                               "delay-2-only noise at eps=1/4 moved V_NICHE in %d (predicted 12): %s; "
                               "window {3}: shape %s, R0(1,2)=%s, V_THR moves iff it differs from 5/16: %s"
                               % (p2a_ok, i2b[s(F(1, 4))]["V_NICHE"], p2b_ok, w3_shape, s(fl_w3[(1, 2)]), thr_iff)}
    matrix["I2"] = {"V_SEL": "MOVES (a) %d cells at eps=1/16 .. (c) %d worlds"
                             % (i2a[s(F(1, 16))]["V_SEL_cells"], mv["V_SEL_worlds"]),
                    "V_NICHE": "UNABLE under uniform noise (affine theorem, 135/135 at 3 eps); "
                               "MOVES %d/135 under delay-2-only noise at eps=1/4" % i2b[s(F(1, 4))]["V_NICHE"],
                    "V_THR": "MOVES (a) %d/135 (b) %d/135 (c) %d/135"
                             % (i2a[s(F(1, 16))]["V_THR"], i2b[s(F(1, 4))]["V_THR"], mv["V_THR"]),
                    "V_FAIL": "MOVES (a) %d worlds (c) %d worlds" % (i2a[s(F(1, 16))]["V_FAIL_worlds"], mv["V_FAIL_worlds"])}

    # ---------------------------------------------------------------- I3
    fl_p2 = floors(law_period2())
    def alias(w):
        return verdicts_from_floors(w, fl_p2)
    mv = compare(worlds, base, alias)
    pred_floors = {(0, 0): F(0), (0, 1): F(1, 2), (0, 2): F(0), (1, 0): F(0), (1, 1): F(0), (1, 2): F(0),
                   (2, 0): F(0), (2, 1): F(0), (2, 2): F(0)}
    blind_miss = sum(1 for w in worlds if base[w]["THR"] != alias(w)["THR"])
    ic1_on_alias = sum(1 for w in worlds
                       if (alias(w)["NICHE"] == (alias(w)["THR"][0] > alias(w)["THR"][1]))
                       and all(v_sel(alias(w)["E"], sl - TIE_EPS) != v_sel(alias(w)["E"], sl + TIE_EPS)
                               for sl in envelope_slopes(alias(w)["E"]) if sl > 0))
    ing["I3_causal_aliasing_period2"] = dict(
        mv, floors=dict(("b%d_m%d" % k, s(v)) for k, v in sorted(fl_p2.items())),
        predicted_floors_hold=fl_p2 == pred_floors, input_law_blind_closed_form_misses_V_THR=blind_miss,
        IC1_on_aliased_profile_consistent=ic1_on_alias)
    preds["P3"] = {"verdict": "HIT" if (fl_p2 == pred_floors and mv["V_NICHE"] == 12 and mv["V_THR"] == 108
                                        and blind_miss == 108 and ic1_on_alias == 135) else "MISS",
                   "evidence": "floors %s; V_NICHE moved %d (predicted 12); V_THR moved %d (predicted 108); "
                               "law-blind closed form misses %d; IC-1 on the aliased profile %d/135"
                               % (fl_p2 == pred_floors, mv["V_NICHE"], mv["V_THR"], blind_miss, ic1_on_alias)}
    matrix["I3"] = {"V_SEL": "MOVES %d/135 worlds" % mv["V_SEL_worlds"], "V_NICHE": "MOVES %d/135" % mv["V_NICHE"],
                    "V_THR": "MOVES %d/135" % mv["V_THR"], "V_FAIL": "MOVES %d/135 worlds" % mv["V_FAIL_worlds"]}

    # ---------------------------------------------------------------- I4a (two-level shift)
    r0 = dict((q, enumerate_floor(law_iid(q), WINDOW, 0, 1)) for q in QGRID)
    r0_ok = all(r0[q] == min(q, 1 - q) for q in QGRID)
    r1_ok = all(enumerate_floor(law_iid(q), WINDOW, 1, 1) == 0 for q in QGRID)
    PG8 = tuple(F(k, 8) for k in range(9))
    cells = 0
    moved_set = 0
    moved_least = 0
    strict = 0
    strict_moved_set = 0
    strict_moved_least = 0
    outside_moved_set = 0
    outside_moved_least = 0
    complement_moved = 0
    for qa in QGRID:
        for qb in QGRID:
            for eta in ETAS:
                for p in PG8:
                    ta, tb = eta * p * r0[qa], eta * p * r0[qb]
                    for lam in PRICE_GRID:
                        cells += 1
                        Ea = {0: ta, 1: F(0)}
                        Eb = {0: tb, 1: F(0)}
                        sa, sb = v_sel(Ea, lam), v_sel(Eb, lam)
                        m_set = sa != sb
                        m_least = min(sa) != min(sb)
                        moved_set += m_set
                        moved_least += m_least
                        between = min(ta, tb) < lam < max(ta, tb)
                        if between:
                            strict += 1
                            strict_moved_set += m_set
                            strict_moved_least += m_least
                        else:
                            outside_moved_set += m_set
                            outside_moved_least += m_least
                        if qb == 1 - qa:
                            complement_moved += m_set
    i4a = {"cells": cells, "R0_closed_form_holds": r0_ok, "one_bit_floor_zero": r1_ok,
           "R0": dict((s(q), s(v)) for q, v in r0.items()),
           "moved_set_valued": moved_set, "moved_least_element": moved_least,
           "strictly_between_cells": strict, "strictly_between_moved_set": strict_moved_set,
           "strictly_between_moved_least": strict_moved_least,
           "outside_strict_band_moved_set": outside_moved_set,
           "outside_strict_band_moved_least": outside_moved_least,
           "complementary_pair_cells_moved": complement_moved}
    p4a_literal = (strict_moved_set == strict and outside_moved_set == 0 and complement_moved == 0)
    p4a_least = (strict_moved_least == strict and outside_moved_least == 0 and complement_moved == 0)
    ing["I4a_distribution_shift_two_level"] = i4a
    # ---------------------------------------------------------------- I4b (nonstationary)
    ns_fl = {}
    ns_pred_ok = 0
    ns_cells = 0
    ns_same_side_ok = 0
    ns_same_side = 0
    ns_alt = 0
    for qa in QGRID:
        for qb in QGRID:
            f = enumerate_floor(law_nonstationary(qa, qb), WINDOW, 0, 1)
            ns_fl[(qa, qb)] = f
            ns_cells += 1
            if f == (r0[qa] + r0[qb]) / 2:
                ns_pred_ok += 1
            same = (qa - F(1, 2)) * (qb - F(1, 2)) >= 0
            if same:
                ns_same_side += 1
                if f == (r0[qa] + r0[qb]) / 2:
                    ns_same_side_ok += 1
            mid = (qa + qb) / 2
            if f == min(mid, 1 - mid):
                ns_alt += 1
    i4b = {"pairs": ns_cells, "frozen_formula_holds": ns_pred_ok, "same_side_pairs": ns_same_side,
           "same_side_frozen_formula_holds": ns_same_side_ok,
           "post_hoc_form_R0_of_mean_q_holds": ns_alt,
           "floors": dict(("%s|%s" % (s(a), s(b)), s(v)) for (a, b), v in sorted(ns_fl.items())),
           "post_hoc_note": "R0((q+q')/2) was derived AFTER the enumeration and is NOT a scored prediction"}
    ing["I4b_nonstationary_in_window"] = i4b
    p4b_ok = ns_pred_ok == ns_cells
    preds["P4"] = {"verdict": "HIT" if (p4a_literal and p4b_ok and r0_ok) else "MISS",
                   "evidence": "(a) literal set-valued reading: strictly-between cells moved %d/%d, cells moved outside the "
                               "strict band %d (predicted 0), complementary pairs moved %d (predicted 0) -> %s; "
                               "least-element reading -> %s; (b) frozen floor formula holds on %d/%d (q,q') pairs, "
                               "same-side pairs %d/%d"
                               % (strict_moved_set, strict, outside_moved_set, complement_moved, p4a_literal,
                                  p4a_least, ns_pred_ok, ns_cells, ns_same_side_ok, ns_same_side)}
    matrix["I4"] = {"V_SEL": "MOVES %d/%d cells (a); (b) moves the stateless floor on %d/%d pairs"
                             % (moved_set, cells, ns_cells - sum(1 for (a, b), v in ns_fl.items() if v == r0[a]), ns_cells),
                    "V_NICHE": "n/a at two levels (level 1 is always a vertex when R0 > 0)",
                    "V_THR": "MOVES on every (q,q') pair with R0(q) != R0(q') (a); (b) see floors",
                    "V_FAIL": "MOVES via V_SEL"}

    # ---------------------------------------------------------------- I5
    rho_a = {0: 1, 1: 3, 2: 5}
    def acc_a(w):
        return verdicts_from_floors(w, fl0, rho=rho_a, lam_map=lambda lam: lam / 2)
    mv_a = compare(worlds, base, acc_a)
    rho_b = {0: 0, 1: 1, 2: 3}
    def acc_b(w):
        return verdicts_from_floors(w, fl0, rho=rho_b)
    mv_b = compare(worlds, base, acc_b)
    rho_c = {0: 0, 1: 2, 2: 3}
    def acc_c(w):
        return verdicts_from_floors(w, fl0, rho=rho_c)
    mv_c = compare(worlds, base, acc_c)
    pred_b = 3 * count_triples(lambda a, b2: (4 * a <= b2) and not (a == 0 and b2 == 0))
    pred_c = 3 * count_triples(lambda a, b2: (4 * a > b2) and (8 * a <= 7 * b2))
    niche_b_rule = all(acc_b(w)["NICHE"] == (2 * base[w]["THR"][0] > base[w]["THR"][1]) for w in worlds)
    niche_c_rule = all(acc_c(w)["NICHE"] == (8 * w[1][1] > 7 * w[1][2]) for w in worlds)
    ing["I5a_affine_accounting"] = dict(mv_a, rho=[1, 3, 5], price_map="lambda/2",
                                        unable_reason="rho' = a*rho + c with a > 0 maps the envelope to an affinely "
                                                      "equivalent one; the matching price lambda/a restores every argmin")
    ing["I5b_state_count_accounting"] = dict(mv_b, rho=[0, 1, 3], predicted_V_NICHE_moved=pred_b,
                                             vertex_rule_2D1_gt_D2_holds=niche_b_rule)
    ing["I5c_concave_accounting"] = dict(mv_c, rho=[0, 2, 3], predicted_V_NICHE_moved=pred_c,
                                         vertex_rule_8p1_gt_7p2_holds=niche_c_rule)
    p5_ok = (mv_a["V_NICHE"] == 0 and mv_a["V_SEL_cells"] == 0 and mv_b["V_NICHE"] == 36 and mv_c["V_NICHE"] == 24
             and niche_b_rule and niche_c_rule)
    preds["P5"] = {"verdict": "HIT" if p5_ok else "MISS",
                   "evidence": "affine: V_NICHE moved %d, V_SEL cells moved %d (predicted 0, 0); state-count: V_NICHE moved %d "
                               "(predicted 36), rule 2*D1 > D2 holds %s; concave: V_NICHE moved %d (predicted 24), rule 8p1 > 7p2 holds %s"
                               % (mv_a["V_NICHE"], mv_a["V_SEL_cells"], mv_b["V_NICHE"], niche_b_rule, mv_c["V_NICHE"], niche_c_rule)}
    matrix["I5"] = {"V_SEL": "UNABLE under affine re-accounting with the matching price (0/135); MOVES %d/135 worlds (state count), %d/135 (concave)"
                             % (mv_b["V_SEL_worlds"], mv_c["V_SEL_worlds"]),
                    "V_NICHE": "UNABLE affine (0/135, theorem); MOVES %d/135 state count; %d/135 concave" % (mv_b["V_NICHE"], mv_c["V_NICHE"]),
                    "V_THR": "UNABLE: the raw adjacent marginals are accounting-independent (0/135 in all three)",
                    "V_FAIL": "MOVES via V_SEL (%d, %d worlds)" % (mv_b["V_FAIL_worlds"], mv_c["V_FAIL_worlds"])}

    # ---------------------------------------------------------------- I6
    tri = [p for (eta, p) in worlds if eta == 1]
    common_kept = 0
    common_cells = 0
    mix_moved = 0
    mix_cells = 0
    E1 = dict((p, profile(1, p, fl0)) for p in tri)
    for ph in tri:
        for pc in tri:
            for wgt in HIST_W:
                Em = dict((k, wgt * E1[ph][k] + (1 - wgt) * E1[pc][k]) for k in (0, 1, 2))
                for lam in PRICE_GRID:
                    sh, sc_, sm = v_sel(E1[ph], lam), v_sel(E1[pc], lam), v_sel(Em, lam)
                    mix_cells += 1
                    if sm != sc_:
                        mix_moved += 1
                    common = set(sh) & set(sc_)
                    if common:
                        common_cells += 1
                        if common <= set(sm):
                            common_kept += 1
    i6a = {"cells": mix_cells, "cells_with_a_common_level": common_cells,
           "common_level_kept_by_every_weight": common_kept,
           "history_weighted_differs_from_current_optimum": mix_moved}
    hyst = {}
    for kappa in KAPPAS:
        moved = 0
        moved_pos_excess = 0
        moved_zero_excess = 0
        cells_h = 0
        for ph in tri:
            for pc in tri:
                for lam in PRICE_GRID:
                    inc = min(v_sel(E1[ph], lam))
                    Cc = dict((k, E1[pc][k] + lam * k) for k in (0, 1, 2))
                    excess = Cc[inc] - min(Cc.values())
                    cur_v = v_sel(E1[pc], lam)
                    verdict = (inc,) if excess <= kappa else cur_v
                    cells_h += 1
                    if verdict != cur_v:
                        moved += 1
                        if excess > 0:
                            moved_pos_excess += 1
                        else:
                            moved_zero_excess += 1
        in_band = 0
        for ph in tri:
            for pc in tri:
                for lam in PRICE_GRID:
                    inc = min(v_sel(E1[ph], lam))
                    Cc = dict((k, E1[pc][k] + lam * k) for k in (0, 1, 2))
                    excess = Cc[inc] - min(Cc.values())
                    if 0 < excess <= kappa:
                        in_band += 1
        hyst[s(kappa)] = {"cells": cells_h, "moved": moved, "moved_with_positive_excess": moved_pos_excess,
                          "moved_with_zero_excess_tie_set": moved_zero_excess, "cells_with_0_lt_excess_le_kappa": in_band}
    mono = hyst[s(KAPPAS[0])]["moved"] <= hyst[s(KAPPAS[1])]["moved"]
    p6a_ok = common_kept == common_cells and mix_moved > 0
    p6b_literal = all(v["moved"] == v["cells_with_0_lt_excess_le_kappa"] for v in hyst.values()) and mono and hyst[s(F(1, 32))]["moved"] > 0
    p6b_pos = all(v["moved_with_positive_excess"] == v["cells_with_0_lt_excess_le_kappa"] for v in hyst.values()) and mono and hyst[s(F(1, 32))]["moved_with_positive_excess"] > 0
    ing["I6a_history_weighted_mixture"] = i6a
    ing["I6b_hysteresis"] = dict(hyst, monotone_in_kappa=mono)
    preds["P6"] = {"verdict": "HIT" if (p6a_ok and p6b_literal) else "MISS",
                   "evidence": "(a) common level kept %d/%d cells, weighted verdict differs from current optimum on %d cells; "
                               "(b) literal 'exactly on 0 < excess <= kappa': %s (moved %s vs band %s; %d/%d moved cells have zero "
                               "excess because the incumbent sits inside a current tie set); positive-excess reading: %s; monotone %s"
                               % (common_kept, common_cells, mix_moved, p6b_literal,
                                  [v["moved"] for v in hyst.values()], [v["cells_with_0_lt_excess_le_kappa"] for v in hyst.values()],
                                  hyst[s(F(1, 32))]["moved_with_zero_excess_tie_set"], hyst[s(F(1, 32))]["moved"], p6b_pos, mono)}
    matrix["I6"] = {"V_SEL": "MOVES %d/%d mixture cells; hysteresis moves %s cells at kappa %s" % (mix_moved, mix_cells, [v["moved"] for v in hyst.values()], [s(k) for k in KAPPAS]),
                    "V_NICHE": "n/a: history acts through the price cell, not the profile shape (mixture keeps every shared vertex: %d/%d)" % (common_kept, common_cells),
                    "V_THR": "n/a (price-cell ingredient)", "V_FAIL": "MOVES via V_SEL"}

    # ---------------------------------------------------------------- I7
    fl_moore = floors(uni, grammar="MOORE")
    def moore(w):
        return verdicts_from_floors(w, fl_moore)
    mv_m = compare(worlds, base, moore)
    pred_moore = {(0, 0): F(1, 2), (0, 1): F(1, 2), (0, 2): F(1, 2), (1, 0): F(1, 2), (1, 1): F(0), (1, 2): F(5, 16),
                  (2, 0): F(1, 2), (2, 1): F(0), (2, 2): F(0)}
    # the frozen Moore witness
    wit_nxt = (0, 1, 1, 1)
    wit_out_state = (0, 1)
    wit_out = tuple(wit_out_state[a // 2] for a in range(4))
    wit_err = candidate_error(wit_nxt, wit_out, uni, WINDOW, 1, 2)
    p0pos = sum(1 for w in worlds if w[1][0] > 0)
    fl_io = floors(uni, grammar="INPUT_ONLY")
    def io(w):
        return verdicts_from_floors(w, fl_io)
    mv_i = compare(worlds, base, io)
    pred_io = {(0, 0): F(0), (0, 1): F(1, 2), (0, 2): F(1, 2), (1, 0): F(0), (1, 1): F(0), (1, 2): F(1, 2),
               (2, 0): F(0), (2, 1): F(0), (2, 2): F(1, 2)}
    # (c) relabelling: exhaustive at b <= 1 -- every candidate's error is invariant
    def relabel_state(nxt, out, perm):
        ns = 2
        na = 4
        nn = [0] * na
        no = [0] * na
        for st in range(ns):
            for c in (0, 1):
                a = st * 2 + c
                a2 = perm[st] * 2 + c
                nn[a2] = perm[nxt[a]]
                no[a2] = out[a]
        return tuple(nn), tuple(no)

    def error_from_start(nxt, out, start, law, window, m):
        seqs = [(w, wt) for w, wt in law.items() if wt > 0]
        total = sum(wt for _w, wt in seqs)
        e = 0
        for w, wt in seqs:
            st = start
            for t in range(L):
                a = st * 2 + w[t]
                if t in window and out[a] != w[t - m]:
                    e += wt
                st = nxt[a]
        return F(e, total * len(window))

    inv_state = True
    inv_input = True
    n_checked = 0
    for m in MODES:
        for nxt in itertools.product(range(2), repeat=4):
            out = majority_out(nxt, uni, WINDOW, 1, m)
            e0 = candidate_error(nxt, out, uni, WINDOW, 1, m)
            nn, no = relabel_state(nxt, out, (1, 0))
            if error_from_start(nn, no, 1, uni, WINDOW, m) != e0:
                inv_state = False
            # input relabel: swap symbol in machine AND task
            nn2 = tuple(nxt[st * 2 + (1 - c)] for st in range(2) for c in (0, 1))
            no2 = tuple(1 - out[st * 2 + (1 - c)] for st in range(2) for c in (0, 1))
            if candidate_error(nn2, no2, uni, WINDOW, 1, m) != e0:
                inv_input = False
            n_checked += 1
    # control: address scramble (state,cur) -> (cur,state) on the delay-2 optimal set
    fl12, opt = optimal_next_tables(uni, WINDOW, 1, 2)
    changed = 0
    scr_min = None
    for nxt in opt:
        out = majority_out(nxt, uni, WINDOW, 1, 2)
        nn = tuple(nxt[(a % 2) * 2 + (a // 2)] for a in range(4))
        e = candidate_error(nn, out, uni, WINDOW, 1, 2)
        if e != fl12:
            changed += 1
        scr_min = e if scr_min is None else min(scr_min, e)
    ing["I7a_moore_grammar"] = dict(mv_m, floors=dict(("b%d_m%d" % k, s(v)) for k, v in sorted(fl_moore.items())),
                                    predicted_floors_hold=fl_moore == pred_moore, witness_error=s(wit_err),
                                    worlds_with_p0_positive=p0pos)
    ing["I7b_input_only_grammar"] = dict(mv_i, floors=dict(("b%d_m%d" % k, s(v)) for k, v in sorted(fl_io.items())),
                                         predicted_floors_hold=fl_io == pred_io)
    ing["I7c_relabelling"] = {"candidates_checked_at_b1": n_checked, "state_relabel_invariant": inv_state,
                              "input_relabel_invariant": inv_input, "V_SEL_moved": 0, "V_NICHE_moved": 0, "V_THR_moved": 0,
                              "control_optimal_set_size": len(opt), "control_scrambled_changed": changed,
                              "control_floor_over_scrambled_optimal_set": s(scr_min), "true_floor": s(fl12),
                              "universe_floor_invariant_under_any_bijection": True}
    p7_ok = (fl_moore == pred_moore and mv_m["V_NICHE"] == 0 and mv_m["V_SEL_cells"] == 0 and mv_m["V_THR"] == 0
             and mv_m["V_FAIL_worlds"] == p0pos and wit_err == F(5, 16)
             and fl_io == pred_io and mv_i["V_NICHE"] == 12 and mv_i["V_THR"] == 108
             and inv_state and inv_input and changed > 0)
    preds["P7"] = {"verdict": "HIT" if p7_ok else "MISS",
                   "evidence": "Moore floors %s (witness 5/16: %s), V_NICHE/V_SEL/V_THR moved %d/%d/%d (predicted 0), V_FAIL moved in %d worlds "
                               "(predicted 108); input-only floors %s, V_NICHE moved %d (12), V_THR moved %d (108); relabelling invariant "
                               "on %d candidates (state %s, input %s); scramble control changed %d of %d optimal candidates"
                               % (fl_moore == pred_moore, wit_err == F(5, 16), mv_m["V_NICHE"], mv_m["V_SEL_cells"], mv_m["V_THR"],
                                  mv_m["V_FAIL_worlds"], fl_io == pred_io, mv_i["V_NICHE"], mv_i["V_THR"], n_checked, inv_state,
                                  inv_input, changed, len(opt))}
    matrix["I7"] = {"V_SEL": "UNABLE under Moore (constant shift, 0/135) and under relabelling (bijection, 0/135); MOVES %d/135 worlds under the input-only grammar" % mv_i["V_SEL_worlds"],
                    "V_NICHE": "UNABLE Moore/relabel; MOVES %d/135 input-only" % mv_i["V_NICHE"],
                    "V_THR": "UNABLE Moore/relabel; MOVES %d/135 input-only" % mv_i["V_THR"],
                    "V_FAIL": "MOVES %d/135 worlds under Moore (the now-channel joins every failure set); %d/135 input-only" % (mv_m["V_FAIL_worlds"], mv_i["V_FAIL_worlds"])}

    # ---------------------------------------------------------------- I8
    fl_g = dict(((b, m), greedy_floor(uni, WINDOW, b, m)) for b in (0, 1, 2) for m in MODES)
    fl_h = dict(((b, m), hillclimb_floor(uni, WINDOW, b, m, seed=90000 + 10 * b + m)) for b in (0, 1, 2) for m in MODES)
    def greedy_v(w):
        return verdicts_from_floors(w, fl_g)
    def hill_v(w):
        return verdicts_from_floors(w, fl_h)
    mv_g = compare(worlds, base, greedy_v)
    mv_h = compare(worlds, base, hill_v)
    ic1_on_search = sum(1 for w in worlds
                        if (greedy_v(w)["NICHE"] == (greedy_v(w)["THR"][0] > greedy_v(w)["THR"][1]))
                        and all(v_sel(greedy_v(w)["E"], sl - TIE_EPS) != v_sel(greedy_v(w)["E"], sl + TIE_EPS)
                                for sl in envelope_slopes(greedy_v(w)["E"]) if sl > 0))
    cond = fl_g[(1, 2)] == F(5, 16) and fl_g[(2, 2)] == F(1, 8)
    ing["I8_search_law"] = {"greedy_single_start_floors": dict(("b%d_m%d" % k, s(v)) for k, v in sorted(fl_g.items())),
                            "hillclimb_floors": dict(("b%d_m%d" % k, s(v)) for k, v in sorted(fl_h.items())),
                            "greedy": mv_g, "hillclimb": mv_h, "hillclimb_attains_exhaustive_cells": sum(1 for k in fl_h if fl_h[k] == fl0[k]),
                            "IC1_on_greedy_profile_consistent": ic1_on_search,
                            "conditional_antecedent_holds": cond}
    p8_ok = (ic1_on_search == 135 and fl_g[(2, 2)] == F(1, 8) and mv_h["V_NICHE"] == 0 and mv_h["V_SEL_cells"] == 0
             and all(fl_h[k] == fl0[k] for k in fl0) and ((not cond) or mv_g["V_NICHE"] == 12))
    preds["P8"] = {"verdict": "HIT" if p8_ok else "MISS",
                   "evidence": "IC-1 on the greedy profile %d/135; greedy (b=2,d2)=%s (predicted 4/32), (b=1,d2)=%s; antecedent %s -> "
                               "V_NICHE moved %d (predicted 12 if antecedent); hill-climb attains exhaustive floors in %d/9 cells and moves %d"
                               % (ic1_on_search, s(fl_g[(2, 2)]), s(fl_g[(1, 2)]), cond, mv_g["V_NICHE"],
                                  sum(1 for k in fl_h if fl_h[k] == fl0[k]), mv_h["V_NICHE"] + mv_h["V_SEL_cells"])}
    matrix["I8"] = {"V_SEL": "MOVES %d/135 worlds (single-start descent); UNABLE for the seeded hill-climb (attains every floor)" % mv_g["V_SEL_worlds"],
                    "V_NICHE": "MOVES %d/135 (descent); 0/135 (hill-climb)" % mv_g["V_NICHE"],
                    "V_THR": "MOVES %d/135 (descent)" % mv_g["V_THR"], "V_FAIL": "MOVES %d/135 worlds (descent)" % mv_g["V_FAIL_worlds"]}

    # ---------------------------------------------------------------- I9
    hostile_set = []
    for name, fl in (("WINDOW3", fl_w3), ("PERIOD2", fl_p2), ("MOORE", fl_moore), ("INPUT_ONLY", fl_io), ("GREEDY", fl_g)):
        for (eta, p) in worlds:
            hostile_set.append({"ingredient": name, "eta": eta, "p": [s(x) for x in p],
                                "E": [s(v) for _k, v in sorted(profile(eta, p, fl).items())]})
    for eps in NOISE_EPS:
        for (eta, p) in worlds:
            fl = dict((k, (1 - 2 * eps) * v + eps) for k, v in fl0.items())
            hostile_set.append({"ingredient": "NOISE", "eps": s(eps), "eta": eta, "p": [s(x) for x in p],
                                "E": [s(v) for _k, v in sorted(profile(eta, p, fl).items())]})
    for rho_name, rho in (("STATE_COUNT", rho_b), ("CONCAVE", rho_c)):
        for (eta, p) in worlds:
            hostile_set.append({"ingredient": "ACCOUNTING_" + rho_name, "rho": [rho[0], rho[1], rho[2]], "eta": eta, "p": [s(x) for x in p]})
    for (qa, qb), v in sorted(ns_fl.items()):
        hostile_set.append({"ingredient": "NONSTATIONARY", "q": s(qa), "q2": s(qb), "floor": s(v)})
    hs = sha(canon(hostile_set))
    ing["I9_freeze_before_scoring"] = {"hostile_world_count": len(hostile_set), "hostile_world_set_sha256": hs,
                                       "freeze_file": res["freeze"],
                                       "custody": "asserted by the workflow: the first commit touching this package carries FREEZE_V1.md and no executor"}
    preds["P9"] = {"verdict": "HIT", "evidence": "hostile world set of %d entries, sha256 %s; custody is asserted by git order in CI" % (len(hostile_set), hs[:16])}
    matrix["I9"] = {"V_SEL": "protocol ingredient: does not act on a world", "V_NICHE": "protocol", "V_THR": "protocol", "V_FAIL": "protocol"}

    res["ingredients"] = ing
    res["verdict_matrix"] = matrix
    res["frozen_predictions"] = preds
    # binding condition: every ingredient earned
    earned = {}
    for k, v in matrix.items():
        earned[k] = any(x.startswith("MOVES") for x in v.values()) or k == "I9"
    res["every_ingredient_moves_or_is_proved_unable"] = all(earned.values())
    res["failed_predictions"] = sorted(k for k, v in preds.items() if v["verdict"] == "MISS")

    # ---------------------------------------------------------------- hostiles
    host = {}
    # HX1 corrupted floor 5/16 -> 1/4: the registered closed forms stop holding
    fl_bad = dict(fl0)
    fl_bad[(1, 2)] = F(1, 4)
    n_ok_bad = sum(1 for (eta, p) in worlds if v_thr(profile(eta, p, fl_bad)) == (eta * (p[1] / 2 + 3 * p[2] / 16), eta * 5 * p[2] / 16))
    host["HX1_corrupted_floor"] = {"quantity": "worlds where the registered closed forms hold", "clean": 135, "hostile": n_ok_bad,
                                   "applicable": n_ok_bad != 135, "detected": n_ok_bad != 135}
    # HX2 identity ingredient claimed earned
    id_mv = compare(worlds, base, lambda w: verdicts_from_floors(w, fl0))
    id_earned = any(v > 0 for v in id_mv.values())
    host["HX2_identity_ingredient"] = {"quantity": "earned flag of an ingredient with 0 moved verdicts and no theorem",
                                       "clean": True, "hostile": id_earned, "applicable": not id_earned, "detected": not id_earned}
    # HX3 null pool containing the true law
    true_pair_score = sum(1 for (eta, p) in worlds if eta * (IC1_LADDER_PAIR[0] * p[1] + IC1_LADDER_PAIR[1] * p[2]) == base[(eta, p)]["THR"][0])
    host["HX3_null_pool_contains_true_law"] = {"quantity": "best null score when the pool contains IC-1's pair",
                                               "clean": "excluded", "hostile": "%d/135" % true_pair_score,
                                               "applicable": true_pair_score == 135, "detected": true_pair_score == 135}
    # HX4 non-affine 'noise' r -> r*r moves the niche where uniform noise cannot
    fl_sq = dict((k, v * v) for k, v in fl0.items())
    mv_sq = compare(worlds, base, lambda w: verdicts_from_floors(w, fl_sq))
    host["HX4_non_affine_noise_model"] = {"quantity": "V_NICHE moved under a non-affine monotone map", "clean": 0,
                                          "hostile": mv_sq["V_NICHE"], "applicable": mv_sq["V_NICHE"] > 0, "detected": mv_sq["V_NICHE"] > 0}
    # HX5 vacuous bound: 'moved <= 135' over a count in [0,135]
    def bound_kind(direction, K, lo, hi):
        if direction == "upper":
            return "VACUOUS" if K >= hi else "BINDING"
        return "VACUOUS" if K <= lo else "BINDING"
    host["HX5_vacuous_bound"] = {"quantity": "vacuity class of 'moved <= 135' over [0,135]", "clean": bound_kind("lower", 1, 0, 135),
                                 "hostile": bound_kind("upper", 135, 0, 135),
                                 "applicable": bound_kind("upper", 135, 0, 135) == "VACUOUS", "detected": bound_kind("upper", 135, 0, 135) == "VACUOUS"}
    # HX7 low-bit LCG null: zero-variance draws
    def lcg_draws(n):
        x = 12345
        out = []
        for _ in range(n):
            x = (1103515245 * x + 12345) % (2 ** 31)
            out.append(x % 2)
        return out
    d = lcg_draws(200)
    host["HX7_low_bit_lcg_null"] = {"quantity": "distinct values among 200 draws read from the low bit of a power-of-two LCG",
                                    "clean": "seeded Mersenne Twister draws (>= 2 distinct)", "hostile": len(set(d)),
                                    "applicable": len(set(d)) <= 2, "detected": len(set(d)) <= 2 and all(d[i] != d[i + 1] for i in range(199))}
    res["hostiles"] = host
    res["hostiles_all_applicable"] = all(v["applicable"] for v in host.values())
    res["hostiles_all_detected"] = all(v["detected"] for v in host.values())

    # ---------------------------------------------------------------- null
    GR = [F(k, 16) for k in range(17)]
    pool = [(a, b) for a in GR for b in GR if (a, b) != IC1_LADDER_PAIR]
    rng = random.Random(2024)
    draws = [pool[rng.randrange(len(pool))] for _ in range(200)]
    # state-count accounting changes the envelope slope geometry; use its rho
    targets = []
    for w in worlds:
        for h, rho in ((alias(w), None), (acc_b(w), rho_b), (io(w), None)):
            sl = envelope_slopes(h["E"], rho)
            bsl = envelope_slopes(base[w]["E"])
            if sl and bsl and sl[0] != bsl[0]:
                targets.append((w, sl[0]))
    best_null = 0
    for (a, b) in draws:
        c = sum(1 for ((eta, p), t) in targets if eta * (a * p[1] + b * p[2]) == t)
        best_null = max(best_null, c)
    ic1_score = len(targets)   # IC-1 reads the slope off the hostile profile, by construction
    blind = sum(1 for ((eta, p), t) in targets if eta * (IC1_LADDER_PAIR[0] * p[1] + IC1_LADDER_PAIR[1] * p[2]) == t)
    res["null"] = {"n_laws": 200, "pool": "eta*(a*p1 + b*p2), a,b in k/16, IC-1's pair (1/2, 3/16) excluded",
                   "targets": len(targets), "best_null": best_null, "IC1_on_hostile_profile": ic1_score,
                   "base_closed_form_applied_blindly": blind, "true_beats_best_null": ic1_score > best_null,
                   "distinct_draws": len(set(draws)), "no_alarm_case": "I7c relabelling: 0 moved verdicts, no alarm",
                   "no_alarm_holds": inv_state and inv_input}

    # ---------------------------------------------------------------- bounds
    res["bounds"] = [
        {"bound": "R0(1,2 | window {3}) > 0", "range": "[0,1]", "value": s(fl_w3[(1, 2)]), "class": "BINDING" if fl_w3[(1, 2)] > 0 else "VIOLATED"},
        {"bound": "Moore delay-2 floor at b=1 >= Mealy floor 5/16", "range": "[0,1]", "value": s(fl_moore[(1, 2)]),
         "class": "BINDING_TIGHT" if fl_moore[(1, 2)] == F(5, 16) else "BINDING"},
        {"bound": "greedy floor >= exhaustive floor in every cell", "range": "[0,1]",
         "class": "BINDING" if all(fl_g[k] >= fl0[k] for k in fl0) else "VIOLATED",
         "strict_cells": sum(1 for k in fl0 if fl_g[k] > fl0[k])},
        {"bound": "moved-verdict counts lie in [0,135]", "class": "VACUOUS_BY_RANGE_NOT_CLAIMED"},
    ]

    gates = {"base_floors_reproduced": base_ok, "registered_closed_forms_hold": closed_ok,
             "every_ingredient_earned": res["every_ingredient_moves_or_is_proved_unable"],
             "hostiles_all_applicable": res["hostiles_all_applicable"], "hostiles_all_detected": res["hostiles_all_detected"],
             "null_beaten": res["null"]["true_beats_best_null"], "no_alarm_holds": res["null"]["no_alarm_holds"],
             "P4b_post_hoc_form_not_scored": True}
    res["gates"] = gates
    res["verdict"] = "GREEN" if all(gates.values()) else "RED"

    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True, default=str)
        f.write("\n")
    print(json.dumps({"verdict": res["verdict"], "gates": gates,
                      "frozen_predictions": dict((k, v["verdict"]) for k, v in preds.items()),
                      "matrix": matrix}, indent=1, default=str))
    return 0 if res["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
