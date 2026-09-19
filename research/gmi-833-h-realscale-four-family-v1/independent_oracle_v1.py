#!/usr/bin/env python3
"""Source-separated oracle: re-derives champion classes with different code
paths and NO import of search_realscale_v1 (the primary checker).

Independent routes used here:
- least squares via Cramer's rule (determinants) instead of elimination;
- the order-test cut via brute-force direct counting instead of a sweep;
- the monotone link via repeated-pass violator pooling instead of stack PAVA;
- the lag via direct column/response alignment instead of stratum search.

Vocabulary is stratum vocabulary only (screened).
"""
from __future__ import annotations

from fractions import Fraction
import json
from math import gcd
from pathlib import Path

import battery_realscale_v1 as bat

HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Cramer-rule least squares
# ---------------------------------------------------------------------------

def det(m: list[list[Fraction]]) -> Fraction:
    m = [row[:] for row in m]
    n = len(m)
    d = Fraction(1)
    for c in range(n):
        piv = next((i for i in range(c, n) if m[i][c] != 0), None)
        if piv is None:
            return Fraction(0)
        if piv != c:
            m[c], m[piv] = m[piv], m[c]
            d = -d
        d *= m[c][c]
        inv = m[c][c]
        for i in range(c + 1, n):
            if m[i][c] != 0:
                f = m[i][c] / inv
                m[i] = [m[i][j] - f * m[c][j] for j in range(n)]
    return d


def cramer_ls(feats: list[list[int]], resp: list[Fraction]) -> list[Fraction]:
    d = len(feats[0])
    A = [[Fraction(feats[i][j]) for j in range(d)] for i in range(len(feats))]
    b = list(resp)
    # normal equations A^T A x = A^T b, solved by Cramer with a 0-fill for
    # singular systems (repeat with the column removed, canonical order)
    def ata():
        return [[sum(A[i][j] * A[i][k] for i in range(len(A))) for k in range(d)]
                for j in range(d)]

    def atb():
        return [sum(A[i][j] * b[i] for i in range(len(A))) for j in range(d)]

    M = ata()
    v = atb()
    D = det(M)
    keep = list(range(d))
    if D == 0:
        # drop dependent columns in canonical order until nonsingular
        for dropc in range(d):
            trial = [c for c in keep if c != dropc]
            sub = [[M[r][c] for c in trial] for r in trial]
            if det(sub) != 0:
                keep = trial
                break
        sub = [[M[r][c] for c in keep] for r in keep]
        D = det(sub)
        xs = []
        vsub = [v[c] for c in keep]
        for k in range(len(keep)):
            Mk = [row[:] for row in sub]
            for r in range(len(keep)):
                Mk[r][k] = vsub[r]
            xs.append(det(Mk) / D)
        out = [Fraction(0)] * d
        for c, x in zip(keep, xs):
            out[c] = x
        return out
    xs = []
    for k in range(d):
        Mk = [row[:] for row in M]
        for r in range(d):
            Mk[r][k] = v[r]
        xs.append(det(Mk) / D)
    return xs


# ---------------------------------------------------------------------------
# brute-force cut scan
# ---------------------------------------------------------------------------

def brute_cut(scores: list[Fraction], ys: list[Fraction]) -> Fraction:
    best = None
    best_c = None
    for c in sorted(set(scores)):
        risk = sum(1 for s, y in zip(scores, ys)
                   if (Fraction(1) if s >= c else Fraction(0)) != y)
        if best is None or risk < best:
            best, best_c = risk, c
    return best_c if best_c is not None else Fraction(1, 2)


# ---------------------------------------------------------------------------
# repeated-pass violator pooling monotone fit on 3 levels
# ---------------------------------------------------------------------------

def pool_monotone(levels: list[int], ys: list[Fraction]) -> list[Fraction]:
    vals = [Fraction(0)] * 3
    while True:
        sums = [Fraction(0)] * 3
        cnt = [0] * 3
        for lv, y in zip(levels, ys):
            sums[lv] += y
            cnt[lv] += 1
        for k in range(3):
            if cnt[k]:
                vals[k] = sums[k] / cnt[k]
        viol = None
        for k in range(2):
            if cnt[k] and cnt[k + 1] and vals[k] > vals[k + 1]:
                viol = k
                break
        if viol is None:
            break
        # merge the violating pair by pooling (relabel upper level down)
        levels = [viol if lv == viol + 1 else lv for lv in levels]
    return [vals[lv] for lv in levels]


# ---------------------------------------------------------------------------
# oracle interface (mirrors battery materialization, its own int scaling)
# ---------------------------------------------------------------------------

class OracleIface:
    def __init__(self, task: dict):
        t = dict(task)
        data = bat.materialize(t)
        self.binary = bool(data.get("binary"))
        self.kind = data["kind"]
        if self.kind == "static":
            rows = data["X_train"] + data["X_test"]
            p = len(rows[0])
            sh = min(r[j].exp for r in rows for j in range(p))
            self.tr = [[r[j].mant << (r[j].exp - sh) for j in range(p)] for r in data["X_train"]]
            self.te = [[r[j].mant << (r[j].exp - sh) for j in range(p)] for r in data["X_test"]]
            yv = data["y_train"] + data["y_test"]
            ysh = min(v.exp for v in yv)
            self.y_tr = [Fraction(v.mant << (v.exp - ysh)) for v in data["y_train"]]
            self.y_te = [Fraction(v.mant << (v.exp - ysh)) for v in data["y_test"]]
            self.stream = None
            self.p = p
            self.c = 0
        else:
            self.stream = data["stream"]
            self.binary_stream = self.binary
            self.y_tr = [Fraction(v) for v in data["y_train"]]
            self.y_te = [Fraction(v) for v in data["y_test"]]
            self.half = data["half"]
            self.p = 1
            self.c = 0

    def with_cells(self, c: int):
        import copy
        o = copy.copy(self)
        o.c = c
        o.p = c + 1
        return o

    def rows(self, c: int, test: bool):
        st = self.stream
        if st is None:
            return self.te if test else self.tr
        half = self.half
        n = half * 2
        if self.binary_stream:
            rng = range(half, n) if test else range(half)
            return [[(st[i - k] if i >= k else 0) for k in range(c + 1)] for i in rng]
        rng = range(half, n) if test else range(half)
        return [[(st[i - k] if i >= k else 0).fraction() for k in range(c + 1)] for i in rng]

    def feats(self, stratum: str, test: bool):
        rows = self.rows(self.c, test)
        p = self.p
        if stratum == "S_CONST":
            return [[Fraction(1)] for _ in rows]
        if stratum in ("S_ADD", "S_ORD", "S_MONO"):
            return [[Fraction(1)] + [Fraction(v) for v in row] for row in rows]
        if stratum == "S_LIFT":
            out = []
            for row in rows:
                out.append([Fraction(1)] + [Fraction(v) for v in row] +
                           [Fraction(row[a]) * Fraction(row[b])
                            for a in range(p) for b in range(a + 1, p)])
            return out
        raise ValueError(stratum)


def oracle_s_mono(iface: OracleIface):
    """Fit (beta, cuts, level values) for the monotone-link stratum."""
    tr = iface.feats("S_MONO", test=False)
    beta = cramer_ls(tr, iface.y_tr)
    for _ in range(64):
        sc = [sum(b * v for b, v in zip(beta, row)) for row in tr]
        srt = sorted(sc)
        k1 = (len(srt) + 2) // 3
        k2 = (len(srt) * 2 + 2) // 3
        c1, c2 = srt[k1 - 1], srt[k2 - 1]
        levels = [0 if s < c1 else 1 if s < c2 else 2 for s in sc]
        fitted = pool_monotone(levels, iface.y_tr)
        beta = cramer_ls(tr, fitted)
    sc = [sum(b * v for b, v in zip(beta, row)) for row in tr]
    srt = sorted(sc)
    k1 = (len(srt) + 2) // 3
    k2 = (len(srt) * 2 + 2) // 3
    c1, c2 = srt[k1 - 1], srt[k2 - 1]
    levels = [0 if s < c1 else 1 if s < c2 else 2 for s in sc]
    vals3 = [Fraction(0)] * 3
    sums = [Fraction(0)] * 3
    cnt = [0] * 3
    for lv, y in zip(levels, iface.y_tr):
        sums[lv] += y
        cnt[lv] += 1
    merged = list(zip(levels, iface.y_tr))

    def pool(pairs):
        while True:
            vals = {}
            for lv, y in pairs:
                vals.setdefault(lv, [Fraction(0), 0])
                vals[lv][0] += y
                vals[lv][1] += 1
            v = {k: s / c for k, (s, c) in vals.items()}
            bad = None
            ks = sorted(vals)
            for a, b in zip(ks, ks[1:]):
                if v[a] > v[b]:
                    bad = (a, b)
                    break
            if bad is None:
                return v
            pairs = [(bad[0] if lv == bad[1] else lv, y) for lv, y in pairs]

    vmap = pool(merged)
    for k in range(3):
        vals3[k] = vmap.get(k, vmap[min(vmap, key=lambda kk: abs(kk - k))])
    return beta, (c1, c2), vals3


def oracle_fit(iface: OracleIface, stratum: str):
    tr = iface.feats(stratum, test=False)
    if stratum in ("S_CONST", "S_ADD", "S_LIFT"):
        return cramer_ls(tr, iface.y_tr)
    if stratum == "S_ORD":
        beta = cramer_ls(tr, iface.y_tr)
        sc = [sum(b * v for b, v in zip(beta, row)) for row in tr]
        cut = brute_cut(sc, iface.y_tr)
        return beta + [cut]
    if stratum == "S_MONO":
        beta, cuts, vals3 = oracle_s_mono(iface)
        return (beta, cuts, vals3)
    raise ValueError(stratum)


def oracle_predict(iface: OracleIface, stratum: str) -> list[Fraction]:
    te = iface.feats(stratum, test=True)
    if stratum in ("S_CONST", "S_ADD", "S_LIFT"):
        beta = oracle_fit(iface, stratum)
        return [sum(b * v for b, v in zip(beta, row)) for row in te]
    if stratum == "S_ORD":
        beta = oracle_fit(iface, stratum)
        cut = beta[-1]
        sc = [sum(b * v for b, v in zip(beta[:-1], row)) for row in te]
        return [Fraction(1) if s >= cut else Fraction(0) for s in sc]
    if stratum == "S_MONO":
        beta, (c1, c2), vals3 = oracle_s_mono(iface)
        sc = [sum(b * v for b, v in zip(beta, row)) for row in te]
        return [vals3[0] if s < c1 else vals3[1] if s < c2 else vals3[2] for s in sc]
    raise ValueError(stratum)


def oracle_risk(iface: OracleIface, stratum: str) -> Fraction:
    pred = oracle_predict(iface, stratum)
    ys = iface.y_te
    n = len(ys)
    if iface.binary:
        hits = sum(1 for p_, t in zip(pred, ys)
                   if (Fraction(1) if p_ >= Fraction(1, 2) else Fraction(0)) != t)
        return Fraction(hits, n)
    return sum((p_ - t) ** 2 for p_, t in zip(pred, ys)) / n


def oracle_direct_lag(task: dict) -> int:
    """Direct alignment: the lag whose delayed stream equals the response."""
    data = bat.materialize(dict(task))
    st = data["stream"]
    ys = data["y_train"] + data["y_test"]
    n = len(st)
    for lag in range(bat.D_MAX + 1):
        ok = all((st[i - lag] if i >= lag else 0) == ys[i] for i in range(n))
        if ok:
            return lag
    return -1


def oracle_champion(task: dict) -> dict:
    """Independent selection: best (risk, cost) over the oracle-fitted space
    with the frozen band (recomputed here from first principles)."""
    iface = OracleIface(task)
    risks = {}
    if iface.kind == "static":
        for s in ("S_CONST", "S_ADD", "S_ORD", "S_MONO", "S_LIFT"):
            risks[s + "#0"] = oracle_risk(iface, s)
    else:
        for c in range(bat.D_MAX + 1):
            ic = iface.with_cells(c)
            for s in ("S_CONST", "S_ADD", "S_ORD", "S_MONO", "S_LIFT"):
                risks["%s#%d" % (s, c)] = oracle_risk(ic, s)
    # noise-free oracle: exact-tie selection with its own declared order
    # ((risk, then description cost from the F1 table, then id)).  The oracle
    # audits the noise-free champion class; band-free = mode zero.
    def desc_of(key):
        s, c = key.split("#")
        p = int(c) + 1 if iface.kind == "stream" else 4
        d = {"S_CONST": 1, "S_ADD": 1 + p, "S_ORD": 2 + p, "S_MONO": 4 + p,
             "S_LIFT": 1 + p + p * (p - 1) // 2}[s]
        return d + int(c)
    mn = min(risks.values())
    tied = {k: v for k, v in risks.items() if v == mn}
    champ = min(tied, key=lambda k: (desc_of(k), k))
    return {"champion": champ, "risk_min": mn,
            "oracle_direct_lag": oracle_direct_lag(task) if iface.kind == "stream" else None}


def build_scope(reg: dict) -> dict:
    """Derived oracle audit scope (D-14 stride rule): static CI ids for the
    agreement audit + the de Bruijn lags for the direct-alignment audit."""
    static_gens = ("affine", "decision", "mono_step", "pair_lift", "constant")
    ids = []
    for gen in static_gens:
        gen_ids = [t["id"] for t in reg["tasks"] if t["gen"] == gen]
        stride = max(1, len(gen_ids) // 8)
        ids.extend(gen_ids[::stride][:8])
    lag_ids = [t["id"] for t in reg["tasks"] if t["gen"] == "delay_binary"]
    return {"schema": "GMI833HRealScaleOracleScopeV1",
            "agreement_ids": sorted(ids), "direct_lag_ids": sorted(lag_ids)}


def build_result() -> dict:
    reg = json.loads((HERE / "BATTERY_REGISTRY_V1.json").read_text())
    scope = json.loads((HERE / "ORACLE_SCOPE_V1.json").read_text())
    preds = {p["id"]: p for p in
             json.loads((HERE / "FROZEN_PREDICTIONS_V1.json").read_text())["rows"]}
    rows = []
    agree = []
    lag_ok = []
    by_id = {t["id"]: t for t in reg["tasks"]}
    for tid in scope["agreement_ids"]:
        t = by_id[tid]
        noiseless = dict(t)
        noiseless["sigma_exp"] = None
        noiseless["eps_exp"] = None
        ch = oracle_champion(noiseless)
        rows.append({"id": tid, "oracle_champion": ch["champion"],
                     "oracle_direct_lag": None})
        agree.append(ch["champion"].split("#")[0] == preds[tid]["predicted_stratum"])
    for tid in scope["direct_lag_ids"]:
        t = by_id[tid]
        noiseless = dict(t)
        noiseless["sigma_exp"] = None
        noiseless["eps_exp"] = None
        lag = oracle_direct_lag(noiseless)
        rows.append({"id": tid, "oracle_champion": None, "oracle_direct_lag": lag})
        lag_ok.append(lag == t["lag"])
    return {
        "schema": "GMI833HRealScaleOracleV1",
        "imports_primary_checker": False,
        "agreement_rows": len(agree),
        "all_agree": all(agree) and len(agree) > 0,
        "direct_lag_rows": len(lag_ok),
        "direct_lag_ok": all(lag_ok) and len(lag_ok) > 0,
        "rows": sorted(rows, key=lambda r: r["id"]),
    }


if __name__ == "__main__":
    doc = build_result()
    (HERE / "ORACLE_RESULT_V1.json").write_text(json.dumps(doc, sort_keys=True, indent=1) + "\n")
    print(json.dumps({k: doc[k] for k in ("all_agree", "direct_lag_ok")}))
