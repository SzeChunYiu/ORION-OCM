"""Route B -- independent oracle for #833 Section Z, subsection Z7.

Route B never replays an input sequence and never iterates over candidates one at
a time to obtain their error counts. It factorises the problem: the state
trajectory depends only on the next-state table and the mode, so the exact
occupancy of each scored moment over the index (state, previous symbol, current
symbol) is computed once per (nxt, mode) by a path-count recurrence, and every
output table is then scored against that occupancy tensor by a sum.

It imports nothing from route A and nothing from the Z3, Z5, Z12 or Z15 packages.

Run:  python3 -I -B independent_impossibility_oracle_v1.py
"""
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)
TRANS = os.path.join(RESEARCH, "gmi-833-heldout-20-transitions-v1", "RESULT_V1.json")

L = 3
N = (L - 1) * (2 ** L)

GRID_P = ("1/5", "2/5", "1/2", "3/5", "4/5")
GRID_ETA = ("1", "2", "3")
GRID_LAM = ("1/20", "1/10", "1/5", "1/2")
GRID_ANOW = (0, 4, 8, 16)
GRID_ADELAY = (0, 4, 8, 16)
GRID_C = ("1/10", "1/5", "1/2", "1")
GRID_B = (0, 1)


def fs(x):
    return str(Fraction(x))


def occupancy(nxt, mode):
    """Exact number of scored moments (t >= 1) landing on each
    (state, prev, cur) configuration, for the given next-state table and mode.
    Depends on `nxt` and `mode` only -- never on the output table."""
    occ = {}
    cfg = {}
    for cur in (0, 1):
        cfg[(0, -1, cur)] = 2 ** (L - 1)
    for t in range(L):
        nxt_cfg = {}
        for key in cfg:
            st, prev, cur = key
            mult = cfg[key]
            if t >= 1:
                occ[key] = occ.get(key, 0) + mult
            idx = 4 * st + 2 * mode + cur
            ns = (nxt >> idx) & 1
            if t + 1 < L:
                half = mult // 2
                for nc in (0, 1):
                    k2 = (ns, cur, nc)
                    nxt_cfg[k2] = nxt_cfg.get(k2, 0) + half
        cfg = nxt_cfg
    return occ


def stateless_occupancy(mode):
    """For a stateless candidate the state is irrelevant; the occupancy of each
    ordered (prev, cur) pair is (L-1) * 2^(L-2)."""
    per = (L - 1) * (2 ** (L - 2))
    occ = {}
    for prev in (0, 1):
        for cur in (0, 1):
            occ[(0, prev, cur)] = per
    return occ


def score(occ, table, mode):
    err = 0
    for key in occ:
        st, prev, cur = key
        idx = 4 * st + 2 * mode + cur
        out = (table >> idx) & 1
        want = cur if mode == 0 else prev
        if out != want:
            err += occ[key]
    return err


def score_stateless(occ, table, mode):
    err = 0
    for key in occ:
        _st, prev, cur = key
        out = (table >> (2 * mode + cur)) & 1
        want = cur if mode == 0 else prev
        if out != want:
            err += occ[key]
    return err


def build():
    recs = []
    occ_sl = dict([(m, stateless_occupancy(m)) for m in (0, 1)])
    for table in range(16):
        recs.append((0, None, table,
                     score_stateless(occ_sl[0], table, 0),
                     score_stateless(occ_sl[1], table, 1)))
    for nxt in range(256):
        o0 = occupancy(nxt, 0)
        o1 = occupancy(nxt, 1)
        for table in range(256):
            recs.append((1, nxt, table, score(o0, table, 0), score(o1, table, 1)))
    return recs


def is_dead_table(table):
    for m in (0, 1):
        for c in (0, 1):
            if ((table >> (2 * m + c)) & 1) != ((table >> (4 + 2 * m + c)) & 1):
                return False
    return True


def is_moore(table):
    for s in (0, 1):
        for m in (0, 1):
            if ((table >> (4 * s + 2 * m)) & 1) != ((table >> (4 * s + 2 * m + 1)) & 1):
                return False
    return True


def pareto_min(pairs):
    out = []
    for a in sorted(pairs):
        dominated = False
        for b in pairs:
            if b != a and b[0] <= a[0] and b[1] <= a[1]:
                dominated = True
                break
        if not dominated:
            out.append(list(a))
    return out


def load_worlds():
    with open(TRANS) as fh:
        doc = json.load(fh)
    out = []
    for case in doc["cases"]:
        p = Fraction(case["p"])
        eta = Fraction(case["eta"])
        star = eta * p / 2
        for tag, lam in (("low", Fraction(case["lambda_low"])),
                         ("high", Fraction(case["lambda_high"])),
                         ("boundary", star)):
            out.append({"case": case["case"], "tag": tag, "p": p, "eta": eta, "lam": lam})
    return out


def main():
    recs = build()
    st0 = [r for r in recs if r[0] == 0]
    st1 = [r for r in recs if r[0] == 1]
    S0 = set([(r[3], r[4]) for r in st0])
    S1 = set([(r[3], r[4]) for r in st1])
    triples = {0: sorted(set([(r[0], r[3], r[4]) for r in st0])),
               1: sorted(set([(r[0], r[3], r[4]) for r in recs]))}

    rep = {"schema": "GMI_833_Z7_IMPOSSIBILITY_ORACLE_V1",
           "route": "B_occupancy_factorisation", "imports_route_a": False,
           "universe": {"candidates": len(recs), "stateless": len(st0),
                        "stateful": len(st1), "N_scored_moments": N}}
    rep["IM_1"] = {"stateless_delay_values": sorted(set([r[4] for r in st0])),
                   "zero_error_delay_possible_at_bits_0": any(r[4] == 0 for r in st0),
                   "zero_error_delay_possible_at_bits_1": any(r[4] == 0 for r in st1)}
    rep["IM_2"] = {"S0": sorted([list(x) for x in S0]), "S0_size": len(S0),
                   "S1_size": len(S1),
                   "S0_pareto_frontier": pareto_min(S0),
                   "S1_pareto_frontier": pareto_min(S1)}

    # grid
    def obj(bits, e0, e1, p, eta, lam):
        return eta * ((1 - p) * Fraction(e0, N) + p * Fraction(e1, N)) + lam * bits

    infeasible = 0
    feasible = 0
    infeas_by_b = {0: 0, 1: 0}
    total = 0
    for ps in GRID_P:
        p = Fraction(ps)
        for es in GRID_ETA:
            eta = Fraction(es)
            for ls in GRID_LAM:
                lam = Fraction(ls)
                for an in GRID_ANOW:
                    for ad in GRID_ADELAY:
                        for cs in GRID_C:
                            C = Fraction(cs)
                            for b in GRID_B:
                                total += 1
                                ok = False
                                for tr in triples[b]:
                                    if tr[1] <= an and tr[2] <= ad and \
                                            obj(tr[0], tr[1], tr[2], p, eta, lam) <= C:
                                        ok = True
                                        break
                                if ok:
                                    feasible += 1
                                else:
                                    infeasible += 1
                                    infeas_by_b[b] += 1
    rep["IM_2"]["R2_cost_grid"] = {"cells": total, "feasible": feasible,
                                   "infeasible": infeasible,
                                   "infeasible_by_budget": {"0": infeas_by_b[0],
                                                            "1": infeas_by_b[1]}}

    hist = {}
    for r in st1:
        k = (r[3], r[4])
        hist[k] = hist.get(k, 0) + 1
    modal = max(hist.items(), key=lambda kv: (kv[1], -kv[0][0], -kv[0][1]))
    q4 = [r for r in st1 if r[4] == 0 and r[3] == 16]
    rep["IM_3"] = {"modal_pair": list(modal[0]), "modal_multiplicity": modal[1],
                   "Q4_witness_count": len(q4),
                   "Q4_refuted": len(q4) > 0,
                   "Q5_confirmed": any(r[4] > 8 for r in st1),
                   "stateless_e_now_values": sorted(set([r[3] for r in st0]))}

    fam = {"F_STATELESS": st0, "F_DEAD_TABLE": [], "F_FROZEN_STATE": [],
           "F_MOORE": [], "F_MEALY_PURE": [], "F_IDENTITY_STATE": []}
    for r in st1:
        _b, nxt, table, _e0, _e1 = r
        if is_dead_table(table):
            fam["F_DEAD_TABLE"].append(r)
        if nxt == 0 or nxt == 255:
            fam["F_FROZEN_STATE"].append(r)
        if is_moore(table):
            fam["F_MOORE"].append(r)
        else:
            fam["F_MEALY_PURE"].append(r)
        if nxt == 0b10101010:
            fam["F_IDENTITY_STATE"].append(r)
    rep["IM_5"] = dict([(k, {"size": len(v),
                             "min_e_now": min([r[3] for r in v]),
                             "min_e_delay": min([r[4] for r in v]),
                             "attained_pair_count": len(set([(r[3], r[4]) for r in v])),
                             "pareto_frontier": pareto_min(set([(r[3], r[4]) for r in v]))})
                        for k, v in fam.items()])

    worlds = load_worlds()
    c6_bad = 0
    for w in worlds:
        mn = min([obj(t[0], t[1], t[2], w["p"], w["eta"], w["lam"]) for t in triples[1]])
        if mn != min(w["eta"] * w["p"] / 2, w["lam"]):
            c6_bad += 1
    rep["IM_4"] = {"C1_attained_min": min([r[4] for r in st0]),
                   "C4_K4": max([min(r[3], r[4]) for r in st1]),
                   "C5_K5": len(S1),
                   "C6_violations": c6_bad}

    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(rep, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("route B oracle written:", rep["universe"])
    print("  |S0|=%d |S1|=%d grid infeasible=%d" % (len(S0), len(S1), infeasible))
    return 0


if __name__ == "__main__":
    sys.exit(main())
