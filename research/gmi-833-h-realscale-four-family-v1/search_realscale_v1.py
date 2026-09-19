#!/usr/bin/env python3
"""PROC1/PROC2 search over the frozen strata (FREEZE F1/F3/F5/F5b).

All arithmetic is exact: features/responses as common-shift integers,
solves in Fractions, risks as exact Fractions.  No floats anywhere.
Vocabulary is lower-process/stratum vocabulary only (screened).
"""
from __future__ import annotations

from fractions import Fraction
from math import gcd
import heapq
import json
from pathlib import Path

import battery_realscale_v1 as bat

HERE = Path(__file__).resolve().parent

STRATUM_ORDER = ["S_CONST", "S_ADD", "S_ORD", "S_MONO", "S_LIFT", "S_TABLE"]
STREAM_TABLE_BUDGET = 3 ** bat.P_DIM     # freeze F5b: 3^(c+1) <= 3^p
ROUND_BOUND = 1 << 7                     # freeze D-11
CONV_TOL = Fraction(1, 1 << 52)          # freeze D-11
PROC2_STEP_EXPS = range(-8, 63)          # F5b + conditioning-derived top (D-6)
BETA_SCALE = 64                          # PROC2 int beta scale 2^64 (> step top 62)


# ---------------------------------------------------------------------------
# exact linear algebra
# ---------------------------------------------------------------------------

def solve_exact(matrix: list[list[int]], rhs: list[int]) -> list[Fraction]:
    """Exact solve of a symmetric Gram system; dependent columns dropped in
    canonical index order (dropped slots get 0)."""
    n = len(rhs)
    m = [[Fraction(v) for v in row] for row in matrix]
    b = [Fraction(v) for v in rhs]
    keep = []
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, n) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        b[r], b[piv] = b[piv], b[r]
        inv = 1 / m[r][c]
        m[r] = [v * inv for v in m[r]]
        b[r] = b[r] * inv
        for i in range(n):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [m[i][j] - f * m[r][j] for j in range(n)]
                b[i] = b[i] - f * b[r]
        keep.append(c)
        r += 1
    out = [Fraction(0)] * n
    for i, c in enumerate(keep):
        out[c] = b[i]
    return out


def solve_bareiss(matrix: list[list[int]], rhs: list[int]) -> list[Fraction]:
    """Fraction-free (Bareiss) exact solve for integer systems.

    Forward elimination keeps every entry an exact minor of the original
    matrix (the //prev divisions are exact by the Bareiss identity);
    dependent columns are skipped (kept-column tracking); the kept system is
    upper triangular and solved by exact Fraction back-substitution.
    Dropped slots get 0.  Same result as solve_exact.
    """
    n = len(rhs)
    m = [row[:] + [rhs[j]] for j, row in enumerate(matrix)]
    keep = []
    r = 0
    prev = 1
    for c in range(n):
        piv = next((i for i in range(r, n) if m[i][c] != 0), None)
        if piv is None:
            continue
        if piv != r:
            m[r], m[piv] = m[piv], m[r]
        for i in range(r + 1, n):
            for j in range(c + 1, n + 1):
                m[i][j] = (m[i][j] * m[r][c] - m[i][c] * m[r][j]) // prev
            m[i][c] = 0
        prev = m[r][c]
        keep.append(c)
        r += 1
        if r == n:
            break
    out = [Fraction(0)] * n
    sol = [Fraction(0)] * r
    for i in range(r - 1, -1, -1):
        acc = Fraction(m[i][n])
        for k in range(i + 1, r):
            acc -= m[i][keep[k]] * sol[k]
        sol[i] = acc / m[i][keep[i]]
    for i, c in enumerate(keep):
        out[c] = sol[i]
    return out


def gram_ls(feats: list[list[int]], resp: list[int]) -> list[Fraction]:
    d = len(feats[0])
    gram = [[sum(feats[i][j] * feats[i][k] for i in range(len(feats)))
             for k in range(d)] for j in range(d)]
    rhs = [sum(feats[i][j] * resp[i] for i in range(len(feats))) for j in range(d)]
    return solve_bareiss(gram, rhs)


def gram_ls_frac(feats: list[list[int]], resp: list[Fraction]) -> list[Fraction]:
    d = len(feats[0])
    gram = [[sum(feats[i][j] * feats[i][k] for i in range(len(feats)))
             for k in range(d)] for j in range(d)]
    rhs = [sum(feats[i][j] * resp[i] for i in range(len(feats))) for j in range(d)]
    return solve_exact(gram, rhs)



def scaled_beta(beta: list[Fraction]) -> tuple[list[int], int]:
    """Common-denominator integer form of a Fraction vector."""
    D = 1
    for b in beta:
        d = b.denominator
        if D % d:
            D = D // gcd(D, d) * d
    return [int(b * D) for b in beta], D


def predict_scaled(beta: list[Fraction], rows: list[list[int]]) -> tuple[list[int], int]:
    """Exact predictions as integers over a common denominator."""
    bi, D = scaled_beta(beta)
    out = [sum(bi[j] * row[j] for j in range(len(bi))) for row in rows]
    return out, D


def pava_fit(xs: list[Fraction], ys: list[Fraction]) -> list[Fraction]:
    """Exact PAVA over pairs sorted by (x, index); fitted values in input order."""
    order = sorted(range(len(xs)), key=lambda i: (xs[i], i))
    blocks = []
    for i in order:
        blocks.append([ys[i], 1, [i]])
        while len(blocks) >= 2 and blocks[-2][0] / blocks[-2][1] > blocks[-1][0] / blocks[-1][1]:
            b2 = blocks.pop()
            b1 = blocks.pop()
            blocks.append([b1[0] + b2[0], b1[1] + b2[1], b1[2] + b2[2]])
    fitted = [Fraction(0)] * len(xs)
    for s, w, idxs in blocks:
        v = s / w
        for i in idxs:
            fitted[i] = v
    return fitted


def best_cut(scores: list[Fraction], ys: list[Fraction]) -> Fraction:
    """Complete U_ORD cut scan at every distinct score; median-position tie
    rule (F5b).  Exact; O(n log n) via sorted sweep."""
    pairs = sorted(zip(scores, ys), key=lambda t: (t[0], t[1]))
    n = len(pairs)
    pos_above = sum(1 for _, y in pairs if y == 1)
    # candidate cut at value c: predict 1 iff s >= c.  Sweep distinct values
    # ascending, moving points from above to below.
    best_risks = []
    cur_above = pos_above
    cur_below_1 = 0
    i = 0
    vals = []
    risks = []
    while i < n:
        v = pairs[i][0]
        while i < n and pairs[i][0] == v:
            if pairs[i][1] == 1:
                cur_above -= 1
                cur_below_1 += 1
            i += 1
        # cut exactly at v: points with s >= v are predicted 1
        above = n - (i - 0)  # points with s >= v
        ones_above = cur_above
        zeros_above = above - ones_above
        below = n - above
        ones_below = cur_below_1
        risk = zeros_above + ones_below
        vals.append(v)
        risks.append(risk)
    mn = min(risks)
    tied = [v for v, r in zip(vals, risks) if r == mn]
    return tied[len(tied) // 2]


# ---------------------------------------------------------------------------
# interface construction (int-scaled features)
# ---------------------------------------------------------------------------

class Interface:
    """Int-scaled train/test feature interface for one task and delay c."""

    def __init__(self, data: dict, c: int = 0):
        self.binary = bool(data.get("binary"))
        if data["kind"] == "static":
            dtr, dte = data["X_train"], data["X_test"]
            p = len(dtr[0])
            all_rows = dtr + dte
            fshift = min(row[j].exp for row in all_rows for j in range(p))
            self.cols_tr = [[row[j].mant << (row[j].exp - fshift) for row in dtr] for j in range(p)]
            self.cols_te = [[row[j].mant << (row[j].exp - fshift) for row in dte] for j in range(p)]
            y_all = data["y_train"] + data["y_test"]
            yshift = min(v.exp for v in y_all)
            self.y_tr = [v.mant << (v.exp - yshift) for v in data["y_train"]]
            self.y_te = [v.mant << (v.exp - yshift) for v in data["y_test"]]
            self.y_shift = yshift
            self.shift = fshift
            self.p = p
        else:
            stream = data["stream"]
            half = data["half"]
            n = len(stream)
            if self.binary:
                self.shift = 0
                self.y_shift = 0
                self.cols_tr = [[(stream[i - k] if i >= k else 0) for i in range(half)]
                                for k in range(c + 1)]
                self.cols_te = [[(stream[i - k] if i >= k else 0) for i in range(half, n)]
                                for k in range(c + 1)]
                self.y_tr = list(data["y_train"])
                self.y_te = list(data["y_test"])
            else:
                cols_d = [[(stream[i - k] if i >= k else bat.Dyadic(0, 0)) for i in range(n)]
                          for k in range(c + 1)]
                fshift = min(v.exp for col in cols_d for v in col)
                self.shift = fshift
                self.cols_tr = [[v.mant << (v.exp - fshift) for v in col[:half]] for col in cols_d]
                self.cols_te = [[v.mant << (v.exp - fshift) for v in col[half:]] for col in cols_d]
                y_all = data["y_train"] + data["y_test"]
                yshift = min(v.exp for v in y_all)
                self.y_tr = [v.mant << (v.exp - yshift) for v in data["y_train"]]
                self.y_te = [v.mant << (v.exp - yshift) for v in data["y_test"]]
                self.y_shift = yshift
            self.p = c + 1
        self.n_tr = len(self.y_tr)
        self.n_te = len(self.y_te)
        self._enc_cuts = None

    def features(self, stratum: str):
        """(train_rows, test_rows, meta) integer feature rows."""
        p = self.p
        if stratum == "S_CONST":
            return ([[1]] * self.n_tr, [[1]] * self.n_te, {})
        if stratum in ("S_ADD", "S_ORD", "S_MONO"):
            tr = [[1] + [self.cols_tr[j][i] for j in range(p)] for i in range(self.n_tr)]
            te = [[1] + [self.cols_te[j][i] for j in range(p)] for i in range(self.n_te)]
            return tr, te, {}
        if stratum == "S_LIFT":
            pairs = [(a, b) for a in range(p) for b in range(a + 1, p)]
            tr = [[1] + [self.cols_tr[j][i] for j in range(p)] +
                  [self.cols_tr[a][i] * self.cols_tr[b][i] for a, b in pairs]
                  for i in range(self.n_tr)]
            te = [[1] + [self.cols_te[j][i] for j in range(p)] +
                  [self.cols_te[a][i] * self.cols_te[b][i] for a, b in pairs]
                  for i in range(self.n_te)]
            return tr, te, {"pairs": [list(x) for x in pairs]}
        if stratum == "S_TABLE":
            enc_tr = self._encode_cells(self.cols_tr, train=True)
            enc_te = self._encode_cells(self.cols_te, train=False)
            return (enc_tr, enc_te, {"encoding": "tercile_cells"})
        raise ValueError(stratum)

    def _encode_cells(self, cols, train):
        if train:
            cuts = []
            for j in range(self.p):
                s = sorted(cols[j])
                k1 = (len(s) + 2) // 3
                k2 = (len(s) * 2 + 2) // 3
                cuts.append((s[k1 - 1], s[k2 - 1]))
            self._enc_cuts = cuts
        cuts = self._enc_cuts
        out = []
        for i in range(len(cols[0])):
            cell = 0
            for j in range(self.p):
                v = cols[j][i]
                lev = 0 if v < cuts[j][0] else 1 if v < cuts[j][1] else 2
                cell = 3 * cell + lev
            out.append(cell)
        return out


# ---------------------------------------------------------------------------
# stratum fits (PROC1 canonical solvers, FREEZE F3)
# ---------------------------------------------------------------------------

def score_tercile_levels(scores: list[Fraction]) -> tuple[list[int], list[Fraction]]:
    """Encode scores by train tercile cuts (D-1); returns (levels, cuts)."""
    s = sorted(scores)
    k1 = (len(s) + 2) // 3
    k2 = (len(s) * 2 + 2) // 3
    c1, c2 = s[k1 - 1], s[k2 - 1]
    levels = [0 if v < c1 else 1 if v < c2 else 2 for v in scores]
    return levels, [c1, c2]


def level_pava(levels: list[int], ys: list[Fraction]) -> list[Fraction]:
    """Monotone fit on the 3-level encoded grid (exact 3-block PAVA)."""
    sums = [Fraction(0)] * 3
    cnt = [0] * 3
    for lv, y in zip(levels, ys):
        sums[lv] += y
        cnt[lv] += 1
    blocks = [[sums[k], cnt[k], [k]] for k in range(3) if cnt[k] > 0]
    i = 0
    while i + 1 < len(blocks):
        if blocks[i][0] / blocks[i][1] > blocks[i + 1][0] / blocks[i + 1][1]:
            b2 = blocks.pop(i + 1)
            b1 = blocks.pop(i)
            blocks.insert(i, [b1[0] + b2[0], b1[1] + b2[1], b1[2] + b2[2]])
            i = max(0, i - 1)
        else:
            i += 1
    vals = [Fraction(0)] * 3
    for s, w, ks in blocks:
        for k in ks:
            vals[k] = s / w
    return [vals[lv] for lv in levels], vals


def fit_stratum(iface: Interface, stratum: str) -> dict:
    tr, te, meta = iface.features(stratum)
    y_tr = [Fraction(v) for v in iface.y_tr]
    y_te = [Fraction(v) for v in iface.y_te]
    if stratum == "S_CONST":
        mu = sum(y_tr) / len(y_tr)
        return {"pred_tr": [mu] * iface.n_tr, "pred_te": [mu] * iface.n_te,
                "params": {"const": mu}}
    if stratum in ("S_ADD", "S_LIFT"):
        beta = gram_ls(tr, iface.y_tr)
        p_tr, d1 = predict_scaled(beta, tr)
        p_te, d2 = predict_scaled(beta, te)
        assert d1 == d2
        return {"pred_tr": (p_tr, d1), "pred_te": (p_te, d2),
                "params": {"beta": beta, **meta}}
    if stratum == "S_ORD":
        beta = gram_ls(tr, iface.y_tr)
        si, sd = predict_scaled(beta, tr)
        score_tr = [Fraction(v, sd) for v in si]
        si_te, sd_te = predict_scaled(beta, te)
        score_te = [Fraction(v, sd_te) for v in si_te]
        cut = best_cut(score_tr, y_tr)
        pred_tr = [Fraction(1) if s >= cut else Fraction(0) for s in score_tr]
        pred_te = [Fraction(1) if s >= cut else Fraction(0) for s in score_te]
        return {"pred_tr": pred_tr, "pred_te": pred_te,
                "params": {"beta": beta, "cut": cut}}
    if stratum == "S_MONO":
        beta = gram_ls(tr, iface.y_tr)
        rounds = 0
        prev = None
        vals3 = None
        while rounds < ROUND_BOUND:
            si, sd = predict_scaled(beta, tr)
            score_tr = [Fraction(v, sd) for v in si]
            levels, _ = score_tercile_levels(score_tr)
            fitted, vals3 = level_pava(levels, y_tr)
            obj = sum((fitted[i] - y_tr[i]) ** 2 for i in range(iface.n_tr))
            if prev is not None and (prev - obj) <= CONV_TOL * (Fraction(1) if prev == 0 else prev):
                break
            prev = obj
            rounds += 1
            beta = gram_ls_frac(tr, fitted)
        si, sd = predict_scaled(beta, tr)
        score_tr = [Fraction(v, sd) for v in si]
        si_te, sd_te = predict_scaled(beta, te)
        score_te = [Fraction(v, sd_te) for v in si_te]
        levels_tr, cuts3 = score_tercile_levels(score_tr)
        fitted, vals3 = level_pava(levels_tr, y_tr)
        levels_te = [0 if v < cuts3[0] else 1 if v < cuts3[1] else 2 for v in score_te]
        pred_te = [vals3[lv] for lv in levels_te]
        return {"pred_tr": list(fitted), "pred_te": pred_te,
                "params": {"beta": beta, "link_values": list(vals3), "rounds": rounds}}
    if stratum == "S_TABLE":
        enc_tr, enc_te, meta2 = iface.features("S_TABLE")
        mu = sum(y_tr) / len(y_tr)
        cell_sums = {}
        cell_cnt = {}
        for cell, y in zip(enc_tr, y_tr):
            cell_sums[cell] = cell_sums.get(cell, Fraction(0)) + y
            cell_cnt[cell] = cell_cnt.get(cell, 0) + 1
        means = {k: cell_sums[k] / cell_cnt[k] for k in cell_sums}
        pred_tr = [means.get(cell, mu) for cell in enc_tr]
        pred_te = [means.get(cell, mu) for cell in enc_te]
        return {"pred_tr": pred_tr, "pred_te": pred_te,
                "params": {"cells": len(means), "fallback_const": mu == 0}}
    raise ValueError(stratum)


def risk_of(iface: Interface, pred) -> Fraction:
    """Held-out risk under the frozen arm metric (F5), in VALUE units.

    Fits and predictions live in the shared y-int space (value = int *
    2**y_shift); the squared-risk conversion 2**(2*y_shift) is applied here
    so risks compare directly against the AMENDMENT A band.  pred is either
    a Fraction list or the scaled form (int list, D)."""
    n = iface.n_te
    if iface.binary:
        if isinstance(pred, tuple):
            ints, D = pred
            hits = sum(1 for v, t in zip(ints, iface.y_te)
                       if (1 if 2 * v >= D else 0) != t)
        else:
            hits = sum(1 for p_, t in zip(pred, iface.y_te)
                       if (Fraction(1) if p_ >= Fraction(1, 2) else Fraction(0)) != Fraction(t))
        return Fraction(hits, n)
    unit = Fraction(2) ** (2 * iface.y_shift)
    if isinstance(pred, tuple):
        ints, D = pred
        acc = 0
        for v, t in zip(ints, iface.y_te):
            r = v - t * D
            acc += r * r
        return Fraction(acc, D * D * n) * unit
    return sum((p_ - Fraction(t)) ** 2 for p_, t in zip(pred, iface.y_te)) / n * unit


def costs(stratum: str, p: int) -> tuple[int, int]:
    """(description, serve) per the F1 table (streams pass p = c+1)."""
    if stratum == "S_CONST":
        return 1, 0
    if stratum == "S_ADD":
        return 1 + p, 2 * p
    if stratum == "S_ORD":
        return 2 + p, 2 * p + 1
    if stratum == "S_MONO":
        return 1 + p + 3, 2 * p + 3   # affine slots + 3-level link slots
    if stratum == "S_LIFT":
        return 1 + p + p * (p - 1) // 2, 2 * (p + p * (p - 1) // 2)
    if stratum == "S_TABLE":
        return 3 ** p, 1
    raise ValueError(stratum)


# ---------------------------------------------------------------------------
# PROC1: full-space fiber selection (F5)
# ---------------------------------------------------------------------------

def make_band(task: dict) -> dict:
    """AMENDMENT A band: ('zero',) for noise-free; ('dyadic', band) for the
    real arm; ('sqrt4', 4q) for binary arms (membership test
    (risk-min)^2 <= 4q keeps the irrational sqrt exact)."""
    if task.get("binary"):
        e = task.get("eps_exp")
        if e is None:
            return {"mode": "zero"}
        eps = Fraction(1) / (1 << (-e)) if e < 0 else Fraction(1, 2 if e == 1 else 1)
        q = eps * (1 - eps) / 2048
        return {"mode": "sqrt4", "four_q": 4 * q}
    e = task.get("sigma_exp")
    if e is None:
        return {"mode": "zero"}
    sigma2 = Fraction(1) / (1 << (-2 * e)) if e < 0 else Fraction(1, 4) if e == 1 else Fraction(1)
    return {"mode": "dyadic", "band": sigma2 / 16}


def band_member(risk: Fraction, min_risk: Fraction, band: dict) -> bool:
    if band["mode"] == "zero":
        return risk == min_risk
    if band["mode"] == "dyadic":
        return risk <= min_risk + band["band"]
    delta = risk - min_risk
    return delta * delta <= band["four_q"]


def proc1_select(data: dict, band: dict) -> dict:
    machines = {}
    if data["kind"] == "static":
        iface = Interface(data, 0)
        for s in STRATUM_ORDER:
            fit = fit_stratum(iface, s)
            machines[s + "#0"] = {
                "stratum": s, "cells": 0,
                "risk": risk_of(iface, fit["pred_te"]),
                "desc": costs(s, iface.p)[0], "serve": costs(s, iface.p)[1],
                "params": summarize(s, fit)}
    else:
        for c in range(bat.D_MAX + 1):
            iface = Interface(data, c)
            for s in STRATUM_ORDER:
                desc, serve = costs(s, iface.p)
                if s == "S_TABLE" and desc > STREAM_TABLE_BUDGET:
                    continue
                fit = fit_stratum(iface, s)
                machines["%s#%d" % (s, c)] = {
                    "stratum": s, "cells": c,
                    "risk": risk_of(iface, fit["pred_te"]),
                    "desc": desc + c, "serve": serve + c,
                    "params": summarize(s, fit)}
    return select_from(machines, band)


def select_from(machines: dict, band: dict) -> dict:
    min_risk = min(m["risk"] for m in machines.values())
    fiber = {k: v for k, v in machines.items() if band_member(v["risk"], min_risk, band)}
    min_cost = min((v["desc"], v["serve"]) for v in fiber.values())
    cost_min = {k: v for k, v in fiber.items() if (v["desc"], v["serve"]) == min_cost}
    order = sorted(cost_min.keys(),
                   key=lambda k: (STRATUM_ORDER.index(cost_min[k]["stratum"]),
                                  cost_min[k]["cells"], k))
    champ = order[0]
    drift = {}
    for k in cost_min:
        s = cost_min[k]["stratum"]
        drift[s] = drift.get(s, 0) + 1
    tot = sum(drift.values())
    return {
        "champion": champ,
        "champion_stratum": cost_min[champ]["stratum"],
        "champion_cells": cost_min[champ]["cells"],
        "champion_risk": cost_min[champ]["risk"],
        "champion_desc": cost_min[champ]["desc"],
        "champion_serve": cost_min[champ]["serve"],
        "champion_params": cost_min[champ]["params"],
        "fiber_size": len(fiber),
        "cost_minimal_tie_count": len(cost_min),
        "drift_strata": {k: Fraction(v, tot) for k, v in sorted(drift.items())},
        "machine_count": len(machines),
        "machines": {k: {"risk": v["risk"], "desc": v["desc"], "serve": v["serve"]}
                     for k, v in sorted(machines.items())},
    }


def summarize(stratum: str, fit: dict) -> dict:
    p = fit["params"]
    if stratum in ("S_ADD", "S_LIFT"):
        beta = p["beta"]
        out = {"support": [i - 1 for i in range(1, len(beta)) if beta[i] != 0]}
        if stratum == "S_LIFT":
            pairs = p["pairs"]
            npairs = len(pairs)
            atoms = len(beta) - npairs - 1
            out["pair_support"] = [pairs[i] for i in range(npairs) if beta[1 + atoms + i] != 0]
        return out
    if stratum == "S_CONST":
        return {"const_zero": p["const"] == 0}
    if stratum == "S_ORD":
        return {"support": [i - 1 for i in range(1, len(p["beta"])) if p["beta"][i] != 0]}
    if stratum == "S_MONO":
        return {"support": [i - 1 for i in range(1, len(p["beta"])) if p["beta"][i] != 0],
                "link_values": list(p["link_values"]), "rounds": p["rounds"]}
    if stratum == "S_TABLE":
        return {"cells_used": p["cells"]}
    return {}


# ---------------------------------------------------------------------------
# PROC2: best-first tier growth with exact dyadic line search
# ---------------------------------------------------------------------------

def coordinate_exact_fit(tr: list[list[int]], resp: list[Fraction]) -> list[Fraction]:
    """PROC2 affine solver: EXACT conjugate gradients on the normal
    equations from initialization 0 (the additive identity).

    In exact arithmetic CG terminates at the unique minimizer in at most d
    steps (finite termination); the Krylov path is materially different
    from PROC1's direct elimination.  The ROUND_BOUND sweep cap cannot bind
    before termination (d < ROUND_BOUND at every registered stratum).
    """
    d = len(tr[0])
    n = len(tr)
    beta = [Fraction(0)] * d
    # Gram form: r = A^T y - G beta with beta = 0; Ap = G p (integer G)
    G = [[sum(tr[i][j] * tr[i][k] for i in range(n)) for k in range(d)]
         for j in range(d)]
    r = [sum(tr[i][j] * resp[i] for i in range(n)) for j in range(d)]
    p = list(r)
    rs_old = sum(x * x for x in r)
    for _ in range(d + 1):
        if rs_old == 0:
            break
        ap = [sum(G[j][k] * p[k] for k in range(d)) for j in range(d)]
        denom = sum(pj * apj for pj, apj in zip(p, ap))
        if denom == 0:
            break
        alpha = rs_old / denom
        beta = [b + alpha * pj for b, pj in zip(beta, p)]
        r = [x - alpha * y for x, y in zip(r, ap)]
        rs_new = sum(x * x for x in r)
        if rs_new == 0:
            break
        mu = Fraction(rs_new, rs_old)
        p = [x + mu * y for x, y in zip(r, p)]
        rs_old = rs_new
    return beta


def proc2_fit(iface: Interface, stratum: str) -> dict:
    """PROC2's independent path: dyadic line search for the affine part;
    canonical order-free fits (cut scan / 3-level link / cell means) where
    the exact ERM is unique (declared in FREEZE F3/PROC2)."""
    tr, te, meta = iface.features(stratum)
    if stratum == "S_TABLE":
        return fit_stratum(iface, stratum)  # cell means: unique order-free ERM
    y_frac = [Fraction(v) for v in iface.y_tr]
    if stratum in ("S_CONST", "S_ADD", "S_LIFT"):
        beta = coordinate_exact_fit(tr, y_frac)
        p_tr, d1 = predict_scaled(beta, tr)
        p_te, d2 = predict_scaled(beta, te)
        assert d1 == d2
        return {"pred_tr": (p_tr, d1), "pred_te": (p_te, d2), "params": {"beta": beta}}
    if stratum == "S_ORD":
        beta = coordinate_exact_fit(tr, y_frac)
        si, sd = predict_scaled(beta, tr)
        score_tr = [Fraction(v, sd) for v in si]
        si_te, sd_te = predict_scaled(beta, te)
        score_te = [Fraction(v, sd_te) for v in si_te]
        cut = best_cut(score_tr, y_frac)
        return {"pred_tr": [Fraction(1) if s >= cut else Fraction(0) for s in score_tr],
                "pred_te": [Fraction(1) if s >= cut else Fraction(0) for s in score_te],
                "params": {"beta": beta, "cut": cut}}
    if stratum == "S_MONO":
        y_tr = y_frac
        beta = coordinate_exact_fit(tr, y_tr)
        for _ in range(ROUND_BOUND):
            si, sd = predict_scaled(beta, tr)
            score_tr = [Fraction(v, sd) for v in si]
            levels, _ = score_tercile_levels(score_tr)
            fitted, vals3 = level_pava(levels, y_tr)
            beta = coordinate_exact_fit(tr, fitted)
        si, sd = predict_scaled(beta, tr)
        score_tr = [Fraction(v, sd) for v in si]
        si_te, sd_te = predict_scaled(beta, te)
        score_te = [Fraction(v, sd_te) for v in si_te]
        levels_tr, cuts3 = score_tercile_levels(score_tr)
        fitted, vals3 = level_pava(levels_tr, y_tr)
        levels_te = [0 if v < cuts3[0] else 1 if v < cuts3[1] else 2 for v in score_te]
        return {"pred_tr": list(fitted), "pred_te": [vals3[lv] for lv in levels_te],
                "params": {"beta": beta, "link_values": list(vals3)}}
    raise ValueError(stratum)


def proc2_select(data: dict, band: dict) -> dict:
    """Band-pruned best-first tier growth (grammar-growth admission mechanic).

    Children are expanded only when their held-out risk stays within the
    AMENDMENT A band of the parent (frontier admission); selection among
    evaluated nodes uses the SAME frozen fiber rule (band + cost), so the
    two procedures share the objective but not the exploration.
    """
    start = ("S_CONST", 0)
    fits = {}
    queue = []
    counter = 0

    def evaluate(node):
        if node not in fits:
            s, c = node
            iface = Interface(data, c)
            fit = proc2_fit(iface, s)
            r = risk_of(iface, fit["pred_te"])
            desc, serve = costs(s, iface.p)
            if data["kind"] == "stream":
                desc, serve = desc + c, serve + c
            fits[node] = {"risk": r, "desc": desc, "serve": serve,
                          "stratum": s, "cells": c, "params": {}}
        return fits[node]

    def children(node):
        s, c = node
        out = []
        if data["kind"] == "stream" and c + 1 <= bat.D_MAX:
            out.append((s, c + 1))
        if s == "S_CONST":
            out += [("S_ADD", c), ("S_TABLE", c)]
        elif s == "S_ADD":
            out += [("S_ORD", c), ("S_MONO", c), ("S_LIFT", c), ("S_TABLE", c)]
        elif s in ("S_ORD", "S_MONO"):
            out.append(("S_LIFT", c))
        return out

    def push(node):
        f = evaluate(node)
        nonlocal counter
        heapq.heappush(queue, (f["risk"], f["desc"], f["serve"],
                               STRATUM_ORDER.index(f["stratum"]), f["cells"],
                               counter, node))
        counter += 1

    push(start)
    while queue:
        item = heapq.heappop(queue)
        node = item[6]
        f = fits[node]
        for ch in children(node):
            s, c = ch
            d, sv = costs(s, c + 1)
            if data["kind"] == "stream":
                d, sv = d + c, sv + c
            if s == "S_TABLE" and d > STREAM_TABLE_BUDGET:
                continue
            if ch in fits:
                continue
            g = evaluate(ch)
            if band_member(g["risk"], f["risk"], band) or g["risk"] < f["risk"]:
                push(ch)
    machines = {"%s#%d" % (v["stratum"], v["cells"]): v for v in fits.values()}
    sel = select_from(machines, band)
    return {"champion": sel["champion"],
            "champion_stratum": sel["champion_stratum"],
            "champion_cells": sel["champion_cells"],
            "champion_risk": sel["champion_risk"],
            "champion_desc": sel["champion_desc"],
            "champion_serve": sel["champion_serve"],
            "evaluated_nodes": len(fits)}


# ---------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------

def frac_str(f: Fraction) -> str:
    return "%d/%d" % (f.numerator, f.denominator)


def proc2_applies(task: dict) -> bool:
    """PROC2 executes on the claim-bearing cells (FREEZE, robustness scope):
    every seed-census, perm-null, de Bruijn, boundary-anchor, and D-14 cell."""
    arm = task.get("arm")
    if arm in ("seed_census", "perm_null", "dbjni_arm"):
        return True
    if task["id"].startswith(("NONMONO_ANCHOR_", "MONO_AFFINE_", "PAIR_CENSUS_0")):
        return True
    return False


def run_task(task: dict) -> dict:
    data = bat.materialize(task)
    band = make_band(task)
    sel = proc1_select(data, band)
    out = {
        "id": task["id"], "kind": task["kind"], "arm": task.get("arm"),
        "gen": task["gen"], "binary": bool(task.get("binary")),
        "kappa_exp": task.get("kappa_exp"), "sigma_exp": task.get("sigma_exp"),
        "eps_exp": task.get("eps_exp"),
        "champion": sel["champion"],
        "champion_stratum": sel["champion_stratum"],
        "champion_cells": sel["champion_cells"],
        "champion_risk": frac_str(sel["champion_risk"]),
        "champion_desc": sel["champion_desc"],
        "champion_serve": sel["champion_serve"],
        "champion_params": jsonable(sel["champion_params"]),
        "fiber_size": sel["fiber_size"],
        "cost_minimal_tie_count": sel["cost_minimal_tie_count"],
        "drift_strata": {k: frac_str(v) for k, v in sel["drift_strata"].items()},
        "machine_risks": {k: {"risk": frac_str(v["risk"]), "desc": v["desc"],
                              "serve": v["serve"]}
                          for k, v in sel["machines"].items()},
    }
    if proc2_applies(task):
        p2 = proc2_select(data, band)
        out["proc2"] = {"champion": p2["champion"],
                        "champion_stratum": p2["champion_stratum"],
                        "champion_cells": p2["champion_cells"],
                        "champion_risk": frac_str(p2["champion_risk"]),
                        "agree": p2["champion_stratum"] == sel["champion_stratum"]}
    return out


def jsonable(params: dict) -> dict:
    out = {}
    for k, v in params.items():
        if isinstance(v, Fraction):
            out[k] = frac_str(v)
        elif isinstance(v, list) and v and isinstance(v[0], Fraction):
            out[k] = [frac_str(x) for x in v]
        elif isinstance(v, list) and v and isinstance(v[0], list):
            out[k] = v
        else:
            out[k] = v
    return out


def ci_scope_ids(reg: dict, per_gen: int = 16) -> list[str]:
    """D-14: stride-sampled subcensus with at most per_gen ids per generator."""
    arms = {}
    for t in reg["tasks"]:
        arms.setdefault(t["gen"], []).append(t["id"])
    out = []
    for gen, ids in arms.items():
        stride = max(1, len(ids) // per_gen)
        out.extend(ids[::stride][:per_gen])
    return out


def run_scope(scope: str, jobs: int = 1) -> list[dict]:
    reg = json.loads((HERE / "BATTERY_REGISTRY_V1.json").read_text())
    ids = set(ci_scope_ids(reg)) if scope == "ci" else None
    tasks = [t for t in reg["tasks"] if ids is None or t["id"] in ids]
    if jobs > 1:
        import multiprocessing as mp
        with mp.Pool(jobs) as pool:
            rows = pool.map(_run_task_star, tasks, chunksize=4)
    else:
        rows = [run_task(t) for t in tasks]
    rows.sort(key=lambda r: r["id"])
    return rows


def _run_task_star(task):
    return run_task(task)


if __name__ == "__main__":
    import sys
    scope = sys.argv[1] if len(sys.argv) > 1 else "ci"
    jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    print(json.dumps({"schema": "GMI833HRealScaleOutcomeV1", "scope": scope,
                      "rows": run_scope(scope, jobs)}, sort_keys=True, indent=1))
