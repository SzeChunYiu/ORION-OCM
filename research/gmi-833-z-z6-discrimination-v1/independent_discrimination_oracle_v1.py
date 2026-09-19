"""Route B -- independently written oracle for #833 Section Z, subsection Z6.

This file does not import, exec or read `z6_discrimination_v1.py`.  Differences
that matter:

  * the universe is rebuilt in output-table-major order;
  * behaviour is keyed by exact `Fraction` error rates and the costs are
    evaluated as exact rationals, with no clearing of denominators -- so Route
    A's integer-scaling transform is checked rather than trusted;
  * the ground-truth optimum is found by a two-stage scan (best within each
    state-bit block, then across blocks) instead of one flat argmin;
  * the selection boundary is re-derived analytically from the block optima
    rather than located by minimisation.

Run:  python3 -I -B independent_discrimination_oracle_v1.py
"""
import itertools
import json
import os
import sys
from fractions import Fraction
from math import factorial

HERE = os.path.dirname(os.path.abspath(__file__))
N = 3
S = tuple(itertools.product((0, 1), repeat=N))

LIN_P = ("1/5", "2/5", "1/2", "3/5", "4/5")
LIN_ETA = ("1", "2", "3", "4")
SKQ = ("1/5", "1/4", "1/3", "2/3", "3/4", "4/5")
SKP = ("2/5", "1/2", "3/5")
SKETA = ("1", "2")
COD = tuple(range(1, 21))
KAPPA = Fraction(1, 4)

CODE = {}
for k in range(17):
    c = factorial(16) // (factorial(k) * factorial(16 - k))
    CODE[k] = (c - 1).bit_length() if c > 1 else 0


def trace(bits, nxt, tab, mode, seq):
    o = []
    st = 0
    for t in range(N):
        x = seq[t]
        if bits == 0:
            o.append((tab >> (2 * mode + x)) & 1)
        else:
            a = 4 * st + 2 * mode + x
            o.append((tab >> a) & 1)
            st = (nxt >> a) & 1
    return o


def evec(bits, nxt, tab):
    v = [[0] * len(S), [0] * len(S)]
    for mode in (0, 1):
        for si, seq in enumerate(S):
            o = trace(bits, nxt, tab, mode, seq)
            for t in (1, 2):
                want = seq[t] if mode == 0 else seq[t - 1]
                if o[t] != want:
                    v[mode][si] += 1
    return v


def universe():
    out = []
    for tab in range(16):
        out.append((0, evec(0, None, tab)))
    for tab in range(256):
        for nxt in range(256):
            out.append((1, evec(1, nxt, tab)))
    return out


def rate_points(univ, q):
    """Exact rational (rate_now, rate_delay, bits) points with multiplicity."""
    w = []
    for seq in S:
        pr = Fraction(1)
        for b in seq:
            pr *= q if b == 1 else (1 - q)
        w.append(pr)
    acc = {}
    for (bits, v) in univ:
        rn = Fraction(0)
        rd = Fraction(0)
        for si in range(len(S)):
            rn += w[si] * Fraction(v[0][si], 2)
            rd += w[si] * Fraction(v[1][si], 2)
        acc[(rn, rd, bits)] = acc.get((rn, rd, bits), 0) + 1
    return tuple(sorted(acc))


def count_points(univ):
    acc = {}
    for (bits, v) in univ:
        acc[(sum(v[0]), sum(v[1]), bits)] = 1
    return tuple(sorted(acc))


def block_min(points, cost):
    """Best value and winner set within each state-bit block, then overall."""
    per = {0: (None, []), 1: (None, [])}
    for k in points:
        c = cost(k)
        b = k[2]
        best, win = per[b]
        if best is None or c < best:
            per[b] = (c, [k])
        elif c == best:
            per[b] = (best, win + [k])
    vals = [v for v, _w in per.values() if v is not None]
    m = min(vals)
    winners = []
    for b in (0, 1):
        v, wset = per[b]
        if v == m:
            winners.extend(wset)
    classes = set("PERSISTENT_STATE" if k[2] else "STATELESS" for k in winners)
    r1 = classes.pop() if len(classes) == 1 else "TIE"
    return r1, frozenset(winners), per


def main():
    univ = universe()
    cpts = count_points(univ)
    cache = {}

    def pts(q):
        if q not in cache:
            cache[q] = rate_points(univ, q)
        return cache[q]

    worlds = []
    half = Fraction(1, 2)
    for ps in LIN_P:
        for es in LIN_ETA:
            p, eta = Fraction(ps), Fraction(es)
            ls = eta * p / 2
            for tag, lam in (("low", ls / 2), ("at", ls), ("high", ls * 3 / 2)):
                worlds.append(("E-LIN", p, eta, half, lam, tag, None))
    for qs in SKQ:
        q = Fraction(qs)
        for ps in SKP:
            for es in SKETA:
                p, eta = Fraction(ps), Fraction(es)
                for k in range(1, 10):
                    worlds.append(("E-SKEW", p, eta, q,
                                   Fraction(k, 10) * eta * p, "k%d" % k, None))
    for c in COD:
        worlds.append(("E-COD", None, None, half, None, "c%d" % c, c))

    def cost_declared(w):
        fam, p, eta, q, lam, _tag, cs = w
        if fam == "E-COD":
            return lambda k: cs * k[2] + CODE[k[0]] + CODE[k[1]]
        return lambda k: eta * p * k[1] + eta * (1 - p) * k[0] + lam * k[2]

    def cost_mdl(w):
        fam, _p, _e, _q, _l, _t, cs = w
        if fam == "E-COD":
            return lambda k: cs * k[2] + CODE[k[0]] + CODE[k[1]]

        def f(k):
            kn = int(-((-k[0] * 16).__floor__()))
            kd = int(-((-k[1] * 16).__floor__()))
            kn = max(0, min(16, kn))
            kd = max(0, min(16, kd))
            return k[2] + CODE[kn] + CODE[kd]
        return f

    def cost_occam(w):
        fam, p, eta, _q, _l, _t, _c = w
        if fam == "E-COD":
            return lambda k: (k[2], k[0] + k[1])
        return lambda k: (k[2], eta * p * k[1] + eta * (1 - p) * k[0])

    def cost_srm(w):
        fam, p, eta, _q, _l, _t, _c = w
        if fam == "E-COD":
            return lambda k: Fraction(k[0] + k[1], 32) + KAPPA * k[2]
        return lambda k: (eta * p * k[1] + eta * (1 - p) * k[0]
                          + KAPPA * k[2])

    def gmi_reg(w):
        fam, p, eta, _q, lam, _t, _c = w
        if fam == "E-COD":
            return "ABSTAIN"
        ls = eta * p / 2
        return ("PERSISTENT_STATE" if lam < ls
                else "STATELESS" if lam > ls else "TIE")

    def gmi_rep(w):
        fam, p, eta, q, lam, _t, cs = w
        if fam == "E-COD":
            sv = CODE[8] - CODE[0]
            return ("PERSISTENT_STATE" if cs < sv
                    else "STATELESS" if cs > sv else "TIE")
        thr = eta * p * min(q, 1 - q)
        return ("PERSISTENT_STATE" if lam < thr
                else "STATELESS" if lam > thr else "TIE")

    tally = {}

    def add(name, fam, got, want):
        s = tally.setdefault(name, {}).setdefault(
            fam, {"win": 0, "loss": 0, "abstain": 0, "tie": 0})
        if got == "ABSTAIN":
            s["abstain"] += 1
            return
        if got == want:
            s["win"] += 1
            if want == "TIE":
                s["tie"] += 1
        else:
            s["loss"] += 1

    r2_mismatch = {"T09_MDL": 0, "T10_OCCAM_HARD": 0, "T12_SRM": 0,
                   "T02_BAYES": 0}
    analytic_agree = 0
    for w in worlds:
        fam, p, eta, q, lam, _tag, cs = w
        P = cpts if fam == "E-COD" else pts(q)
        t1, t2, per = block_min(P, cost_declared(w))
        add("TRUTH", fam, t1, t1)
        add("T01_GMI", fam, gmi_reg(w), t1)
        add("GMI_REPAIRED", fam, gmi_rep(w), t1)
        add("T02_BAYES", fam, t1, t1)
        for nm, cf in (("T09_MDL", cost_mdl), ("T10_OCCAM_HARD", cost_occam),
                       ("T12_SRM", cost_srm)):
            r1, r2, _ = block_min(P, cf(w))
            add(nm, fam, r1, t1)
            if r2 != t2:
                r2_mismatch[nm] += 1
        # analytic re-derivation of the boundary from the block optima
        if fam != "E-COD":
            v0 = per[0][0]
            v1_no_price = per[1][0] - lam
            thr = v0 - v1_no_price
            pred = ("PERSISTENT_STATE" if lam < thr
                    else "STATELESS" if lam > thr else "TIE")
            if pred == t1:
                analytic_agree += 1

    out = {
        "schema": "GMI_833_Z6_DISCRIMINATION_ORACLE_V1",
        "route": "B_independent",
        "universe_candidates": len(univ),
        "worlds_total": len(worlds),
        "uniform_points": len(pts(half)),
        "integer_points": len(cpts),
        "scores": tally,
        "R2_mismatch_vs_truth": r2_mismatch,
        "analytic_boundary_agreements": analytic_agree,
        "analytic_boundary_worlds": sum(1 for w in worlds if w[0] != "E-COD"),
    }
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    print(json.dumps({"GMI": tally["T01_GMI"], "REP": tally["GMI_REPAIRED"],
                      "MDL": tally["T09_MDL"], "r2": r2_mismatch,
                      "analytic": analytic_agree}, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
