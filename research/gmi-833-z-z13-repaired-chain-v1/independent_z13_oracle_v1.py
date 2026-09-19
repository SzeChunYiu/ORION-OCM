#!/usr/bin/env python3
"""Route B -- independent oracle for the frozen prediction Z13-P3 (#833
Section Z, Z13 rows 9-10 and the Z16 chain) at L = 5 and L = 6.

Route B never enumerates a sequence. It propagates the exact joint law of
(state, x_{t-1}, x_{t-2}) through the one-bit / two-bit Markov chain, scores
every (output table, next-state function) pair at b <= 1 to re-verify the two
lemmas the adjudicated parent used (MAJORITY-OPTIMALITY, MODE-INDEPENDENCE)
by brute force at L = 5 before they are relied on, witnesses the b = 2 floors
constructively (a two-bit shift register) and matches them with a seeded
hill-climb, and locates the one-bit niche by scanning an exact lambda grid
over the combined three-mode universe instead of differencing the profile.

It imports nothing from z13_repaired_chain_v1.py and shares no code with it.
Stdlib only; exact int / fractions.Fraction; Python 3.8.
Run:  python3 -I -B independent_z13_oracle_v1.py
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
Fr = Fraction
MODES = (0, 1, 2)
BUDGETS = (0, 1, 2)
ETAS = (1, 2, 3)
LENGTHS = (5, 6)
PROBES = (("flip", (Fr(0), Fr(17, 81), Fr(64, 81))),
          ("boundary", (Fr(0), Fr(9, 41), Fr(32, 41))),
          ("control_never_flips", (Fr(0), Fr(1, 4), Fr(3, 4))),
          ("control_always_empty", (Fr(0), Fr(1, 8), Fr(7, 8))),
          ("retired_ecology_p2_zero", (Fr(1, 4), Fr(3, 4), Fr(0))))
NULL_DISCRIMINATING = (("null_disc_ratio_18_64", (Fr(0), Fr(18, 82), Fr(64, 82))),
                       ("null_disc_ratio_19_64", (Fr(0), Fr(19, 83), Fr(64, 83))))
COPY_RESET = ((0, 1, 0, 0), (1, 0, 0, 0))
COPY_SET = ((0, 1, 1, 1), (1, 0, 1, 1))


# ----------------------------------------------------- exact Markov propagation
def address_tallies(g, ns, m, L, win):
    """Joint law of (state, x_{t-1}, x_{t-2}) propagated exactly; returns the
    per-address tally tal[a][target] of scored mass, scaled by 2^L (integers).
    The state space is (s, x1, x2); inputs are uniform and independent."""
    total = 1 << L
    dist = {(0, 0, 0): total}          # x1, x2 placeholders are never read before t = 2
    tal = [[0, 0] for _ in range(2 * ns)]
    for t in range(L):
        nd = {}
        for (s, x1, x2), mass in dist.items():
            half = mass // 2
            for x in (0, 1):
                a = 2 * s + x
                if t in win:
                    target = x if m == 0 else (x1 if m == 1 else x2)
                    tal[a][target] += half
                key = (g[a], x, x1)
                nd[key] = nd.get(key, 0) + half
        dist = nd
    return tal


def majority_error(g, ns, m, L, win):
    tal = address_tallies(g, ns, m, L, win)
    return sum(min(z, o) for z, o in tal)


def table_error(g, o, ns, m, L, win):
    tal = address_tallies(g, ns, m, L, win)
    return sum(tal[a][1 - o[a]] for a in range(2 * ns))


def window(L):
    return tuple(range(2, L))


def scored_mass(L):
    return (1 << L) * (L - 2)


# --------------------------------------------------------------- floors (b <= 1)
def floors_b_le_1(L):
    """Exhaustive over next-state functions at b in {0, 1} with per-address
    majority; returns floors (as Fractions) and the complete argmin lists."""
    N = scored_mass(L)
    R, ARG = {}, {}
    for b in (0, 1):
        ns = 1 << b
        for m in MODES:
            best, arg = None, []
            for g in itertools.product(range(ns), repeat=2 * ns):
                e = majority_error(g, ns, m, L, window(L))
                if best is None or e < best:
                    best, arg = e, [g]
                elif e == best:
                    arg.append(g)
            R[(b, m)] = Fr(best, N)
            ARG[(b, m)] = sorted(arg)
    return R, ARG


def shift_register_witness(L):
    """Two-bit shift register: state s = 2*x_{t-1} + x_{t-2} (encoded as
    s = 2*prev + prevprev); next state on (s, x) = 2*x + (s >> 1).
    Output tables: mode 0 reads x, mode 1 reads bit 1 of s, mode 2 reads bit 0.
    Every mode attains zero error on the scored window."""
    g = tuple(2 * x + (s >> 1) for s in range(4) for x in (0, 1))
    N = scored_mass(L)
    out = {}
    for m in MODES:
        out[m] = Fr(majority_error(g, 4, m, L, window(L)), N)
    return g, out


def hillclimb_b2(m, L, seed, restarts=5, steps=200):
    rng = random.Random(seed)
    best = None
    win = window(L)
    for _ in range(restarts):
        g = [rng.randrange(4) for _ in range(8)]
        e = majority_error(g, 4, m, L, win)
        for _s in range(steps):
            i = rng.randrange(8)
            v = rng.randrange(4)
            h = list(g)
            h[i] = v
            e2 = majority_error(h, 4, m, L, win)
            if e2 <= e:
                g, e = h, e2
            if e == 0:
                break
        if best is None or e < best:
            best = e
        if best == 0:
            break
    return Fr(best, scored_mass(L))


# ------------------------------------------------------------------- lemmas
def lemma_majority_optimality(L):
    """For every next-state function at b <= 1 and every mode, the minimum over
    ALL output tables equals the per-address majority value."""
    checked = 0
    ok = True
    win = window(L)
    for b in (0, 1):
        ns = 1 << b
        for m in MODES:
            for g in itertools.product(range(ns), repeat=2 * ns):
                maj = majority_error(g, ns, m, L, win)
                full = min(table_error(g, o, ns, m, L, win) for o in itertools.product((0, 1), repeat=2 * ns))
                checked += 1
                if maj != full:
                    ok = False
    return {"L": L, "pairs_checked": checked, "holds": ok}


def lemma_mode_independence(L):
    """Brute force over the full product of per-mode (output, next-state) pairs
    at b = 1 (256^3 joint candidates) and at b = 0 (4^3): the joint minimum of
    the declared cost equals the sum of the per-mode minima, for a world with
    every p_m > 0 (eta = 1, p = (2/8, 3/8, 3/8))."""
    win = window(L)
    p8 = (2, 3, 3)                       # p_m * 8
    out = {}
    for b in (0, 1):
        ns = 1 << b
        per_mode = []
        for m in MODES:
            vals = []
            for g in itertools.product(range(ns), repeat=2 * ns):
                for o in itertools.product((0, 1), repeat=2 * ns):
                    vals.append(p8[m] * table_error(g, o, ns, m, L, win))
            per_mode.append(vals)
        joint = min(x + y + z for x in per_mode[0] for y in per_mode[1] for z in per_mode[2])
        separate = sum(min(v) for v in per_mode)
        out["b%d" % b] = {"joint_candidates": len(per_mode[0]) ** 3, "joint_min_scaled": joint,
                          "sum_of_per_mode_minima_scaled": separate, "holds": joint == separate}
    return out


# ------------------------------------------------------------- niche by scanning
def eighths_worlds():
    out = []
    for a in range(9):
        for bb in range(9 - a):
            for eta in ETAS:
                out.append((Fr(eta), (Fr(a, 8), Fr(bb, 8), Fr(8 - a - bb, 8))))
    return out


def lcm(a, b):
    return a * b // gcd(a, b)


def profile(R, eta, p):
    return dict((b, eta * sum(p[m] * R[(b, m)] for m in MODES)) for b in BUDGETS)


def scan_niche(E):
    """Scan lambda = k/D, D = 2 * lcm of the profile denominators, from 0 past
    E(0); the one-bit budget occupies a niche iff some grid point has it as the
    unique cost minimiser. Any open interval with endpoints in (1/(D/2))Z
    contains a grid point, so the scan cannot miss a non-empty niche."""
    D = 2
    for b in BUDGETS:
        D = lcm(D, E[b].denominator)
    D *= 2
    Ei = dict((b, int(E[b] * D)) for b in BUDGETS)
    kmax = Ei[0] + D
    ks = []
    for k in range(kmax + 1):
        c = dict((b, Ei[b] + k * b) for b in BUDGETS)
        mn = min(c.values())
        if c[1] == mn and c[0] > mn and c[2] > mn:
            ks.append(k)
    if not ks:
        return {"nonempty": False, "D": D, "grid_points_unique_b1": 0}
    return {"nonempty": True, "D": D, "grid_points_unique_b1": len(ks),
            "first": str(Fr(ks[0], D)), "last": str(Fr(ks[-1], D)),
            "contiguous": ks[-1] - ks[0] + 1 == len(ks)}


def predicted_endpoints(R, eta, p):
    """The freeze's marginal closed forms, evaluated with this route's own R."""
    Rd = R[(1, 2)]
    return eta * p[2] * Rd, eta * (p[1] / 2 + p[2] * (Fr(1, 2) - Rd))


def endpoints_consistent_with_scan(E, lo, hi):
    """Every grid point strictly inside (lo, hi) has b = 1 as the unique
    minimiser and every grid point outside does not."""
    D = 2
    for b in BUDGETS:
        D = lcm(D, E[b].denominator)
    D = lcm(D, lo.denominator)
    D = lcm(D, hi.denominator)
    D *= 2
    Ei = dict((b, int(E[b] * D)) for b in BUDGETS)
    for k in range(Ei[0] + D + 1):
        c = dict((b, Ei[b] + k * b) for b in BUDGETS)
        mn = min(c.values())
        uniq = c[1] == mn and c[0] > mn and c[2] > mn
        inside = lo * D < k < hi * D
        if uniq != inside:
            return False
    return True


# ------------------------------------------------------------------- main
def main():
    res = {"schema": "GMI_833_Z13_REPAIRED_CHAIN_ORACLE_V1", "issue": 833, "subsection": "Z13/Z16", "route": "B",
           "method": "exact Markov propagation of (state, x_{t-1}, x_{t-2}); no sequence enumeration; niche by lambda-grid scan"}
    res["lemmas_L5"] = {"majority_optimality": lemma_majority_optimality(5),
                        "mode_independence": lemma_mode_independence(5)}
    lemmas_ok = res["lemmas_L5"]["majority_optimality"]["holds"] and all(v["holds"] for v in res["lemmas_L5"]["mode_independence"].values())
    if not lemmas_ok:
        raise SystemExit("a lemma the parent relied on fails at L = 5 on Route B")
    per_L = {}
    hit = {}
    for L in LENGTHS:
        N = scored_mass(L)
        R, ARG = floors_b_le_1(L)
        g_sr, sr = shift_register_witness(L)
        hc = dict((m, hillclimb_b2(m, L, 4200 + 10 * L + m)) for m in MODES)
        for m in MODES:
            # 0 is the lower bound of an error mass; a witness attaining it is the floor
            R[(2, m)] = sr[m] if sr[m] == 0 else min(sr[m], hc[m])
        pt = dict((t, Fr(majority_error(COPY_RESET[0], 2, 2, L, (t,)), 1 << L)) for t in window(L))
        pt_pred = dict((t, Fr(1, 3) - Fr(1, 12) * Fr(-1, 2) ** (t - 2)) for t in window(L))
        set_err = Fr(majority_error(COPY_SET[0], 2, 2, L, window(L)), N)
        cf = Fr(1, 3) - (1 - Fr(-1, 2) ** (L - 2)) / (18 * (L - 2))
        W = eighths_worlds()
        nonempty = 0
        endpoint_ok = 0
        collapse_ok = 0
        coef = 4 * R[(1, 2)] - 1
        for eta, p in W:
            E = profile(R, eta, p)
            sc = scan_niche(E)
            nonempty += int(sc["nonempty"])
            lo, hi = predicted_endpoints(R, eta, p)
            if endpoints_consistent_with_scan(E, lo, hi):
                endpoint_ok += 1
            if sc["nonempty"] == (p[1] > p[2] * coef):
                collapse_ok += 1
        probes = []
        for name, p in PROBES:
            row = {"probe": name, "p": [str(x) for x in p], "by_eta": []}
            for eta in ETAS:
                E = profile(R, Fr(eta), p)
                sc = scan_niche(E)
                lo, hi = predicted_endpoints(R, Fr(eta), p)
                row["by_eta"].append({"eta": eta, "niche_nonempty": sc["nonempty"], "scan": sc,
                                      "predicted_width": str(hi - lo),
                                      "endpoints_consistent_with_scan": endpoints_consistent_with_scan(E, lo, hi)})
            probes.append(row)
        disc = []
        for name, p in NULL_DISCRIMINATING:
            row = {"world": name, "p": [str(x) for x in p], "by_eta": []}
            for eta in ETAS:
                E = profile(R, Fr(eta), p)
                sc = scan_niche(E)
                lo, hi = predicted_endpoints(R, Fr(eta), p)
                row["by_eta"].append({"eta": eta, "niche_nonempty": sc["nonempty"], "predicted_width": str(hi - lo),
                                      "endpoints_consistent_with_scan": endpoints_consistent_with_scan(E, lo, hi)})
            disc.append(row)
        per_L[L] = {"scored_mass_per_mode": N,
                    "null_discriminating_worlds": disc,
                    "floors": dict(("b%d_m%d" % k, str(v)) for k, v in R.items()),
                    "b2_floor_method": "constructive two-bit shift-register witness (error 0 = lower bound) matched by seeded hill-climb",
                    "shift_register_next_state": list(g_sr),
                    "shift_register_errors": dict(("m%d" % m, str(v)) for m, v in sr.items()),
                    "hillclimb_b2_errors": dict(("m%d" % m, str(v)) for m, v in hc.items()),
                    "d2_b1_floor_attaining_next_state_functions": ARG[(1, 2)],
                    "d1_b1_floor_attaining_next_state_functions": ARG[(1, 1)],
                    "closed_form_R0_d2_b1": str(cf),
                    "per_t_copy_reset": dict((str(t), str(v)) for t, v in pt.items()),
                    "per_t_predicted": dict((str(t), str(v)) for t, v in pt_pred.items()),
                    "copy_then_set_d2_error": str(set_err),
                    "worlds": len(W), "nonempty_niches": "%d/%d" % (nonempty, len(W)),
                    "marginal_endpoints_consistent_with_scan": "%d/%d" % (endpoint_ok, len(W)),
                    "collapse_rule_matches_scan": "%d/%d" % (collapse_ok, len(W)),
                    "collapse_coefficient_4R_minus_1": str(coef),
                    "probes": probes}
        h = {}
        h["P3-a1"] = R[(1, 2)] == cf and R[(1, 2)] == {5: Fr(5, 16), 6: Fr(41, 128)}[L]
        h["P3-a2"] = ARG[(1, 2)] == sorted(COPY_RESET)
        h["P3-a3"] = all(R[(b, 0)] == 0 for b in BUDGETS) and R[(0, 1)] == Fr(1, 2) and R[(1, 1)] == 0 and R[(2, 1)] == 0 \
            and R[(0, 2)] == Fr(1, 2) and R[(2, 2)] == 0
        h["P3-b"] = endpoint_ok == len(W)
        h["P3-c"] = nonempty == 96 and collapse_ok == len(W) and ARG[(1, 1)] == [(0, 1, 0, 1), (1, 0, 1, 0)]
        expect = {5: {"flip": True, "boundary": True, "control_never_flips": True, "control_always_empty": False, "retired_ecology_p2_zero": True},
                  6: {"flip": False, "boundary": False, "control_never_flips": True, "control_always_empty": False, "retired_ecology_p2_zero": True}}[L]
        h["P3-d"] = all(all(r["niche_nonempty"] == expect[row["probe"]] and r["endpoints_consistent_with_scan"] for r in row["by_eta"]) for row in probes)
        h["P3-d_retired_ecology_width"] = all(r["predicted_width"] == str(Fr(eta) * Fr(3, 8)) for row in probes if row["probe"] == "retired_ecology_p2_zero" for eta, r in zip(ETAS, row["by_eta"]))
        h["P3-e"] = (L != 5) or set_err == Fr(17, 48)
        h["per_t_closed_form"] = all(pt[t] == pt_pred[t] for t in window(L))
        hit[L] = h
    res["per_L"] = per_L
    res["hit_conditions"] = dict((str(L), h) for L, h in hit.items())
    res["verdict"] = "HIT" if all(all(h.values()) for h in hit.values()) else "MISS"
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        fh.write(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    sys.stdout.write(json.dumps({"verdict": res["verdict"], "hit": res["hit_conditions"], "lemmas": res["lemmas_L5"],
                                 "floors": dict((str(L), per_L[L]["floors"]) for L in LENGTHS)}, indent=1, default=str) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
