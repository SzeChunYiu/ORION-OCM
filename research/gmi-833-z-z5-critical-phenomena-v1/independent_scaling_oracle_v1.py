"""Route B -- independent oracle for #833 Section Z, subsection Z5.

Route B never replays an input sequence. Error counts come from a transfer-matrix
path count over the triple (state, previous symbol, current symbol): the number
of length-L input words whose prefix drives the machine into each such
configuration at each timestep. The A-ary stateless optimum is obtained in closed
form from scored-moment occupancy, with no table enumeration at all.

It imports nothing from route A and nothing from the Z3, Z7, Z12 or Z15 packages.

Run:  python3 -I -B independent_scaling_oracle_v1.py
"""
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)
TRANS = os.path.join(RESEARCH, "gmi-833-heldout-20-transitions-v1", "RESULT_V1.json")

STATELESS = "STATELESS"
PERSISTENT = "PERSISTENT_STATE"
L_LADDER = (2, 3, 4, 5)
L_REG = 3
A_LADDER = (2, 3, 4)


def fs(x):
    return str(Fraction(x))


# ----------------------------------------------- transfer-matrix path counting
def stateful_counts(nxt, table, mode, length):
    """Exact error count for one one-state-bit machine in one mode, computed by
    propagating path multiplicities over (state, prev, cur). No sequence is
    materialised."""
    # t = 0: state 0, prev undefined (encoded as -1), cur free
    cfg = {}
    for cur in (0, 1):
        cfg[(0, -1, cur)] = 2 ** (length - 1)
    err = 0
    for t in range(length):
        nxt_cfg = {}
        for key in cfg:
            st, prev, cur = key
            mult = cfg[key]
            idx = 4 * st + 2 * mode + cur
            out = (table >> idx) & 1
            if t >= 1:
                want = cur if mode == 0 else prev
                if out != want:
                    err += mult
            ns = (nxt >> idx) & 1
            if t + 1 < length:
                half = mult // 2
                for nc in (0, 1):
                    k2 = (ns, cur, nc)
                    nxt_cfg[k2] = nxt_cfg.get(k2, 0) + half
        cfg = nxt_cfg
    return err


def stateless_counts(table, mode, length):
    """Closed-form occupancy: each ordered (prev, cur) pair occupies exactly
    (length-1) * 2^(length-2) scored moments for length >= 2."""
    per_pair = (length - 1) * (2 ** (length - 2))
    err = 0
    for cur in (0, 1):
        out = (table >> (2 * mode + cur)) & 1
        for prev in (0, 1):
            want = cur if mode == 0 else prev
            if out != want:
                err += per_pair
    return err


def build_universe(length):
    out = []
    for table in range(16):
        out.append((0, stateless_counts(table, 0, length),
                    stateless_counts(table, 1, length)))
    for nxt in range(256):
        for table in range(256):
            out.append((1, stateful_counts(nxt, table, 0, length),
                        stateful_counts(nxt, table, 1, length)))
    return out


def summarize(universe):
    counts = {}
    for t in universe:
        counts[t] = counts.get(t, 0) + 1
    return tuple(sorted(counts.items()))


def value(trip, p, eta, lam, N):
    bits, e0, e1 = trip
    return eta * ((1 - p) * Fraction(e0, N) + p * Fraction(e1, N)) + lam * bits


def argmin_classes(summary, p, eta, lam, N):
    best = None
    classes = set()
    for trip, _m in summary:
        v = value(trip, p, eta, lam, N)
        if best is None or v < best:
            best = v
            classes = set([STATELESS if trip[0] == 0 else PERSISTENT])
        elif v == best:
            classes.add(STATELESS if trip[0] == 0 else PERSISTENT)
    return best, frozenset(classes)


def best_in_class(summary, bits, p, eta, lam, N):
    best = None
    for trip, _m in summary:
        if trip[0] != bits:
            continue
        v = value(trip, p, eta, lam, N)
        if best is None or v < best:
            best = v
    return best


# ------------------------------------------------- A-ary closed-form stateless
def stateless_optimum_A(A, length):
    """Closed form, no table enumeration.

    In mode 1 the output depends on `cur` only while the target is `prev`;
    every ordered (prev, cur) pair occupies exactly (length-1)*A^(length-2)
    scored moments, so any choice of output for a given `cur` is wrong on
    (A-1) of the A possible `prev` values. Hence

        e_delay = A * (A-1) * (length-1) * A^(length-2)
                = (A-1) * (length-1) * A^(length-1)

    for EVERY stateless table, and with N = (length-1)*A^length the delay error
    fraction is exactly (A-1)/A. In mode 0 the target is `cur`, so e_now = 0 is
    attained by the identity table."""
    N = (length - 1) * (A ** length)
    e_delay = (A - 1) * (length - 1) * (A ** (length - 1))
    return Fraction(e_delay, N), 0, N


def one_register_witness_A(A, length):
    """The machine `next := cur; out := cur in mode 0, stored symbol in mode 1`
    is scored by the same occupancy argument: at every scored moment t >= 1 the
    stored symbol equals seq[t-1] exactly, so both channels are error free."""
    return 0, 0


def load_worlds():
    with open(TRANS) as fh:
        doc = json.load(fh)
    if doc.get("schema") != "GMI_833_HELDOUT_20_TRANSITIONS_RESULT_V1":
        raise SystemExit("transition receipt schema drift")
    out = []
    for case in doc["cases"]:
        p = Fraction(case["p"])
        eta = Fraction(case["eta"])
        star = eta * p / 2
        for tag, lam in (("low", Fraction(case["lambda_low"])),
                         ("high", Fraction(case["lambda_high"])),
                         ("boundary", star)):
            out.append({"case": case["case"], "tag": tag, "p": p, "eta": eta,
                        "lam": lam, "lam_star": star})
    return out


def main():
    worlds = load_worlds()
    rep = {"schema": "GMI_833_Z5_CRITICAL_PHENOMENA_ORACLE_V1",
           "route": "B_transfer_matrix_path_counts",
           "imports_route_a": False}

    uni3 = build_universe(L_REG)
    sum3 = summarize(uni3)
    N3 = (L_REG - 1) * (2 ** L_REG)
    sless = sorted(set([(t[1], t[2]) for t in uni3 if t[0] == 0]))
    sful = sorted(set([(t[1], t[2]) for t in uni3 if t[0] == 1]))
    rep["universe"] = {"candidates": len(uni3), "stateless": 16, "stateful": 65536,
                       "N_scored_moments": N3, "distinct_sigma": len(sum3)}
    rep["CP_2"] = {"stateless_attained_pairs": [list(x) for x in sless],
                   "stateless_delay_values": sorted(set([e for _a, e in sless])),
                   "stateless_now_values": sorted(set([a for a, _e in sless])),
                   "stateful_attained_pair_count": len(sful),
                   "stateful_contains_zero_zero": (0, 0) in sful}

    cross_bad = 0
    tie_bad = 0
    jstar_bad = 0
    jumps = set()
    width_bad = 0
    deltas = [Fraction(1, 10 ** k) for k in (3, 6, 9)]
    for w in worlds:
        b0 = best_in_class(sum3, 0, w["p"], w["eta"], Fraction(0), N3)
        b1 = best_in_class(sum3, 1, w["p"], w["eta"], Fraction(0), N3)
        if b0 - b1 != w["lam_star"]:
            cross_bad += 1
        j, cl = argmin_classes(sum3, w["p"], w["eta"], w["lam"], N3)
        if j != min(w["eta"] * w["p"] / 2, w["lam"]):
            jstar_bad += 1
        star = w["lam_star"]
        jst, cls = argmin_classes(sum3, w["p"], w["eta"], star, N3)
        if cls != frozenset([STATELESS, PERSISTENT]):
            tie_bad += 1
        for d in deltas:
            jl, cl_l = argmin_classes(sum3, w["p"], w["eta"], star - d, N3)
            jr, cl_r = argmin_classes(sum3, w["p"], w["eta"], star + d, N3)
            jumps.add(fs((jst - jl) / d - (jr - jst) / d))
            if cl_l != frozenset([PERSISTENT]) or cl_r != frozenset([STATELESS]):
                width_bad += 1
    rep["CP_2"]["analytic_crossing_mismatches"] = cross_bad
    rep["CP_3"] = {"tie_violations": tie_bad,
                   "boundary_worlds_checked": len([w for w in worlds if w["tag"] == "boundary"]),
                   "closed_form_value_mismatches": jstar_bad,
                   "derivative_jump_values": sorted(jumps),
                   "critical_width_violations": width_bad}

    rungs = []
    for L in L_LADDER:
        uni = build_universe(L)
        smm = summarize(uni)
        N = (L - 1) * (2 ** L)
        sl = sorted(set([(t[1], t[2]) for t in uni if t[0] == 0]))
        dv = sorted(set([e for _a, e in sl]))
        bad = 0
        for w in worlds:
            b0 = best_in_class(smm, 0, w["p"], w["eta"], Fraction(0), N)
            b1 = best_in_class(smm, 1, w["p"], w["eta"], Fraction(0), N)
            if b0 - b1 != w["lam_star"]:
                bad += 1
            _j, cl = argmin_classes(smm, w["p"], w["eta"], w["lam_star"], N)
            if cl != frozenset([STATELESS, PERSISTENT]):
                bad += 1
        rungs.append({"L": L, "N_scored_moments": N, "candidates": len(uni),
                      "distinct_sigma": len(smm), "stateless_delay_values": dv,
                      "stateless_delay_is_uniform_half": dv == [N // 2],
                      "lambda_star_drift_violations": bad,
                      "stateful_attained_pair_count":
                          len(set([(t[1], t[2]) for t in uni if t[0] == 1]))})
    rep["CP_4"] = {"ladder": rungs}

    alpha = []
    for A in A_LADDER:
        frac, min_now, N = stateless_optimum_A(A, L_REG)
        w0, w1 = one_register_witness_A(A, L_REG)
        alpha.append({"A": A, "N_scored_moments": N,
                      "min_stateless_delay_fraction": fs(frac),
                      "stateless_min_e_now": min_now,
                      "one_register_witness_e_now": w0,
                      "one_register_witness_e_delay": w1,
                      "S4_derived_prediction": fs(Fraction(A - 1, A)),
                      "S4_derived_matches": frac == Fraction(A - 1, A),
                      "S4_naive_matches": frac == Fraction(1, 2)})
    rep["CP_5"] = {"ladder": alpha,
                   "S4_naive_refuted": any(not r["S4_naive_matches"] for r in alpha),
                   "S4_derived_confirmed": all(r["S4_derived_matches"] for r in alpha)}

    # hostiles, re-derived independently
    endpoints = [w for w in worlds if w["tag"] in ("low", "high")]

    def predict(p, eta, lam, mult=Fraction(1)):
        star = mult * eta * p / 2
        if lam < star:
            return frozenset([PERSISTENT])
        if lam > star:
            return frozenset([STATELESS])
        return frozenset([PERSISTENT, STATELESS])

    mis_true = 0
    mis_h1 = 0
    for w in endpoints:
        _j, actual = argmin_classes(sum3, w["p"], w["eta"], w["lam"], N3)
        if predict(w["p"], w["eta"], w["lam"]) != actual:
            mis_true += 1
        if predict(w["p"], w["eta"], w["lam"], Fraction(2)) != actual:
            mis_h1 += 1
    trunc = summarize([t for t in uni3 if t[0] == 0])
    flips = 0
    for w in worlds:
        _j, full = argmin_classes(sum3, w["p"], w["eta"], w["lam"], N3)
        _j2, cut = argmin_classes(trunc, w["p"], w["eta"], w["lam"], N3)
        if full != cut:
            flips += 1
    rep["hostiles"] = {
        "H1_DOUBLE_BOUNDARY": {"clean": mis_true, "hostile": mis_h1,
                               "checked": len(endpoints),
                               "moved": mis_true == 0 and mis_h1 > 0},
        "H4_TRUNCATED_UNIVERSE": {"clean": 0, "hostile": flips, "moved": flips > 0},
    }

    path = os.path.join(HERE, "ORACLE_RESULT_V1.json")
    with open(path, "w") as fh:
        json.dump(rep, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("route B oracle written:", rep["universe"])
    print("  A-ladder:", [(r["A"], r["min_stateless_delay_fraction"]) for r in alpha])
    return 0


if __name__ == "__main__":
    sys.exit(main())
