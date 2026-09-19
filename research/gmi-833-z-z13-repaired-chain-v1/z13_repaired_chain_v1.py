#!/usr/bin/env python3
"""Route A -- adjudication of the frozen prediction Z13-P3 (#833 Section Z,
Z13 rows 9-10 and the Z16 chain) on the L = 5 and L = 6 three-mode universes.

Protocol: FREEZE_V1.md, committed before this file existed. Nothing in the
freeze's section 3 was computed by this file before the freeze was committed.

Route A enumerates next-state functions with per-address majority outputs and
locates thresholds by differencing the resource-error profile. Route B
(independent_z13_oracle_v1.py) never enumerates a sequence: it propagates
address weights exactly, enumerates the full (output, next-state) product at
b = 1, and locates the niche by scanning an exact lambda grid.

Stdlib only; exact int / fractions.Fraction; Python 3.8.
Run:  python3 -I -B z13_repaired_chain_v1.py
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
F = Fraction
MODES = (0, 1, 2)
BUDGETS = (0, 1, 2)
ETAS = (1, 2, 3)
LENGTHS = (5, 6)
COPY_RESET = ((0, 1, 0, 0), (1, 0, 0, 0))          # predicted floor-attaining pair
COPY_SET = ((0, 1, 1, 1), (1, 0, 1, 1))            # the L = 4 tie partners predicted to drop out
PROBES = (("flip", (F(0), F(17, 81), F(64, 81))),
          ("boundary", (F(0), F(9, 41), F(32, 41))),
          ("control_never_flips", (F(0), F(1, 4), F(3, 4))),
          ("control_always_empty", (F(0), F(1, 8), F(7, 8))),
          ("retired_ecology_p2_zero", (F(1, 4), F(3, 4), F(0))))
# FREEZE_V1_AMENDMENT_1.md A1.3(2): two null-discriminating worlds (p0 = 0), ratios 18/64 and 19/64
NULL_DISCRIMINATING = (("null_disc_ratio_18_64", (F(0), F(18, 82), F(64, 82))),
                       ("null_disc_ratio_19_64", (F(0), F(19, 83), F(64, 83))))


# ------------------------------------------------------------- mechanics
def seqs(L):
    return tuple(itertools.product((0, 1), repeat=L))


def window(L):
    return tuple(range(2, L))


_SEQS = {}


def majority_errors(b, nxt, m, L, win=None, weights=None, init=0):
    """Minimum error count over all output tables for next-state `nxt`, mode m
    (per-address majority over the scored window). Uniform weights are counted
    as integers; a skewed input law is accumulated as exact Fractions."""
    win = window(L) if win is None else win
    ns = 2 ** b
    if L not in _SEQS:
        _SEQS[L] = seqs(L)
    if weights is None:
        tal = [[0, 0] for _ in range(ns * 2)]
        for seq in _SEQS[L]:
            st = init
            for t in range(L):
                a = st * 2 + seq[t]
                if t in win:
                    tal[a][seq[t - m]] += 1
                st = nxt[a]
        return sum(min(z, o) for z, o in tal)
    tal = [[F(0), F(0)] for _ in range(ns * 2)]
    for seq in _SEQS[L]:
        w = weights(seq)
        st = init
        for t in range(L):
            a = st * 2 + seq[t]
            if t in win:
                tal[a][seq[t - m]] += w
            st = nxt[a]
    return sum(min(z, o) for z, o in tal)


def nscored(L, win=None):
    win = window(L) if win is None else win
    return len(seqs(L)) * len(win)


_FLOOR_CACHE = {}


def floor_over_nxt(b, m, L, win=None, weights=None, init=0, restrict=None):
    """Exhaustive minimum over every next-state function of the budget (no
    early exit; the argmin list is complete). Uniform-window results are cached."""
    key = (b, m, L, win, init) if (weights is None and restrict is None) else None
    if key in _FLOOR_CACHE:
        return _FLOOR_CACHE[key]
    ns = 2 ** b
    best, arg = None, []
    space = restrict if restrict is not None else itertools.product(range(ns), repeat=2 * ns)
    for nxt in space:
        e = majority_errors(b, tuple(nxt), m, L, win, weights, init)
        if best is None or e < best:
            best, arg = e, [tuple(nxt)]
        elif e == best:
            arg.append(tuple(nxt))
    if key is not None:
        _FLOOR_CACHE[key] = (best, arg)
    return best, arg


def per_t_errors(nxt, m, L):
    """Per-moment error count of the majority-output machine for next-state nxt."""
    out = {}
    for t in window(L):
        out[t] = majority_errors(1, nxt, m, L, win=(t,))
    return out


# --------------------------------------------------------------- worlds
def eighths_worlds():
    out = []
    for a in range(9):
        for bb in range(9 - a):
            for eta in ETAS:
                out.append((F(eta), (F(a, 8), F(bb, 8), F(8 - a - bb, 8))))
    return out


def profile(R, eta, p):
    return dict((b, eta * sum(p[m] * R[(b, m)] for m in MODES)) for b in BUDGETS)


def endpoints(R, eta, p):
    E = profile(R, eta, p)
    return E[1] - E[2], E[0] - E[1]


def argmin_budgets(E, lam):
    best, arg = None, []
    for b in BUDGETS:
        c = E[b] + lam * b
        if best is None or c < best:
            best, arg = c, [b]
        elif c == best:
            arg.append(b)
    return arg


def unique_one_bit_somewhere(E):
    """Is budget 1 the strict argmin at some lambda >= 0? Scan the exact
    candidate points: midpoints between the two envelope crossings."""
    lo, hi = E[1] - E[2], E[0] - E[1]
    if hi <= lo or hi <= 0:
        return False
    mid = (max(lo, F(0)) + hi) / 2
    return argmin_budgets(E, mid) == [1]


# ----------------------------------------------------------------- main
def main():
    res = {"schema": "GMI_833_Z13_REPAIRED_CHAIN_RESULT_V1", "issue": 833, "subsection": "Z13/Z16", "route": "A",
           "prediction": "Z13-P3 (FREEZE_V1.md section 3)", "lengths": list(LENGTHS)}
    per_L = {}
    hit = {}
    closed_form = {}
    for L in LENGTHS:
        N = nscored(L)
        R, ARG = {}, {}
        for b in BUDGETS:
            for m in MODES:
                e, arg = floor_over_nxt(b, m, L)
                R[(b, m)] = F(e, N)
                ARG[(b, m)] = arg
        # closed form for the copy-then-reset delay-2 floor
        cf = F(1, 3) - (1 - F(-1, 2) ** (L - 2)) / (18 * (L - 2))
        closed_form[L] = str(cf)
        d2_arg = sorted(ARG[(1, 2)])
        pt = per_t_errors(COPY_RESET[0], 2, L)
        pt_pred = dict((t, F(1, 3) - F(1, 12) * F(-1, 2) ** (t - 2)) for t in window(L))
        set_err = F(majority_errors(1, COPY_SET[0], 2, L), N)
        W = eighths_worlds()
        nonempty = 0
        lo_ok = hi_ok = 0
        collapse_ok = 0
        coef = 4 * R[(1, 2)] - 1
        for eta, p in W:
            lo, hi = endpoints(R, eta, p)
            if lo == eta * p[2] * R[(1, 2)]:
                lo_ok += 1
            if hi == eta * (p[1] / 2 + p[2] * (F(1, 2) - R[(1, 2)])):
                hi_ok += 1
            ne = unique_one_bit_somewhere(profile(R, eta, p))
            nonempty += int(ne)
            if ne == (p[1] > p[2] * coef):
                collapse_ok += 1
        probes = []
        for name, p in PROBES:
            row = {"probe": name, "p": [str(x) for x in p], "by_eta": []}
            for eta in ETAS:
                E = profile(R, F(eta), p)
                lo, hi = endpoints(R, F(eta), p)
                row["by_eta"].append({"eta": eta, "lower": str(lo), "upper": str(hi), "width": str(hi - lo),
                                      "niche_nonempty": unique_one_bit_somewhere(E)})
            probes.append(row)
        # mechanism inside a niche world: the unique b=1 minimisers
        mech = None
        for eta, p in W:
            E = profile(R, eta, p)
            if unique_one_bit_somewhere(E) and p[1] > 0 and p[2] > 0:
                lo, hi = endpoints(R, eta, p)
                mech = {"world": {"eta": str(eta), "p": [str(x) for x in p]}, "lambda_probe": str((lo + hi) / 2),
                        "d2_next_state_functions": d2_arg, "d1_next_state_functions": sorted(ARG[(1, 1)]),
                        "d2_uses_copy_reset_pair_only": d2_arg == sorted(COPY_RESET),
                        "d1_identity_type": sorted(ARG[(1, 1)]) == [(0, 1, 0, 1), (1, 0, 1, 0)]}
                break
        per_L[L] = {"scored_moments_per_mode": N,
                    "floors": dict(("b%d_m%d" % k, str(v)) for k, v in R.items()),
                    "d2_b1_floor_attaining_next_state_functions": d2_arg,
                    "closed_form_R0_d2_b1": closed_form[L],
                    "per_t_copy_reset": dict((str(t), str(F(e, len(seqs(L))))) for t, e in pt.items()),
                    "per_t_predicted": dict((str(t), str(v)) for t, v in pt_pred.items()),
                    "copy_then_set_d2_error": str(set_err),
                    "worlds": len(W), "lower_endpoint_is_marginal": "%d/%d" % (lo_ok, len(W)),
                    "upper_endpoint_is_marginal": "%d/%d" % (hi_ok, len(W)),
                    "nonempty_niches": "%d/%d" % (nonempty, len(W)),
                    "collapse_rule_matches_enumeration": "%d/%d" % (collapse_ok, len(W)),
                    "collapse_coefficient_4R_minus_1": str(coef),
                    "probes": probes, "mechanism": mech}
        h = {}
        h["P3-a1"] = (R[(1, 2)] == cf) and (R[(1, 2)] == {5: F(5, 16), 6: F(41, 128)}[L])
        h["P3-a2"] = d2_arg == sorted(COPY_RESET)
        h["P3-a3"] = all(R[(b, 0)] == 0 for b in BUDGETS) and R[(0, 1)] == F(1, 2) and R[(1, 1)] == 0 and R[(2, 1)] == 0 \
            and R[(0, 2)] == F(1, 2) and R[(2, 2)] == 0
        h["P3-b"] = lo_ok == len(W) and hi_ok == len(W)
        h["P3-c"] = nonempty == 96 and collapse_ok == len(W) and mech is not None and mech["d2_uses_copy_reset_pair_only"] and mech["d1_identity_type"]
        expect = {5: {"flip": True, "boundary": True, "control_never_flips": True, "control_always_empty": False, "retired_ecology_p2_zero": True},
                  6: {"flip": False, "boundary": False, "control_never_flips": True, "control_always_empty": False, "retired_ecology_p2_zero": True}}[L]
        h["P3-d"] = all(all(r["niche_nonempty"] == expect[row["probe"]] for r in row["by_eta"]) for row in probes)
        h["P3-d_retired_ecology_width"] = all(r["width"] == str(F(eta) * F(3, 8)) for row in probes if row["probe"] == "retired_ecology_p2_zero" for eta, r in zip(ETAS, row["by_eta"]))
        h["P3-e"] = (L != 5) or set_err == F(17, 48)
        h["per_t_closed_form"] = all(F(pt[t], len(seqs(L))) == pt_pred[t] for t in window(L))
        hit[L] = h
    res["per_L"] = per_L
    res["hit_conditions"] = dict((str(L), h) for L, h in hit.items())
    res["verdict"] = "HIT" if all(all(h.values()) for h in hit.values()) else "MISS"

    # ------------------------------------------------------------ hostiles (L = 5)
    L = 5
    N = nscored(L)
    R5 = {}
    for b in BUDGETS:
        for m in MODES:
            R5[(b, m)] = F(floor_over_nxt(b, m, L)[0], N)
    W = eighths_worlds()
    true_hi = dict(((str(eta), tuple(str(x) for x in p)), endpoints(R5, eta, p)[1]) for eta, p in W)
    hostiles = {}
    # H1 level for marginal
    n = sum(1 for eta, p in W if eta * (p[2] * R5[(1, 2)] + p[1] * R5[(0, 1)]) == true_hi[(str(eta), tuple(str(x) for x in p))])
    hostiles["H1_level_for_marginal"] = {"matches": "%d/%d" % (n, len(W)), "moved": n != len(W)}
    # H2 window shifted to {1..L-1}
    win = tuple(range(1, L))
    e = floor_over_nxt(1, 2, L, win=win)[0]
    hostiles["H2_window_shift"] = {"d2_b1_floor": str(F(e, len(seqs(L)) * len(win))), "true": str(R5[(1, 2)]),
                                   "moved": F(e, len(seqs(L)) * len(win)) != R5[(1, 2)]}
    # H3 skewed input law q = 1/3
    q = F(1, 3)

    def wq(seq):
        w = F(1)
        for x in seq:
            w *= q if x else 1 - q
        return w
    e = floor_over_nxt(1, 2, L, weights=wq)[0] / len(window(L))
    hostiles["H3_skewed_input"] = {"d2_b1_floor": str(e), "true": str(R5[(1, 2)]), "moved": e != R5[(1, 2)]}
    # H4 template injection: identity-next-state family only
    e = floor_over_nxt(1, 2, L, restrict=[(0, 1, 0, 1), (1, 0, 1, 0)])[0]
    hostiles["H4_template_identity_family"] = {"d2_b1_floor": str(F(e, N)), "true": str(R5[(1, 2)]), "moved": F(e, N) != R5[(1, 2)]}
    # H5 set variant substituted
    e = majority_errors(1, COPY_SET[0], 2, L)
    hostiles["H5_set_for_reset"] = {"d2_error": str(F(e, N)), "true": str(R5[(1, 2)]), "moved": F(e, N) != R5[(1, 2)]}
    # H6 accounting lambda*(2^b - 1)
    n = 0
    for eta, p in W:
        E = profile(R5, eta, p)
        # under rho = 2^b - 1 the upper endpoint is E0 - E1 (same), the lower (E1 - E2)/2
        lo2 = (E[1] - E[2]) / 2
        if lo2 == E[1] - E[2]:
            n += 1
    hostiles["H6_accounting_states_minus_one"] = {"lower_endpoint_unchanged": "%d/%d" % (n, len(W)), "moved": n != len(W)}
    # H7 scoring the L-length floors on the L = 4 window {2, 3} (FREEZE section 5;
    # AMENDMENT_1 A1.3(3): run at both L, vacuous at L = 5 by the closed form)
    win4 = (2, 3)
    for LL in LENGTHS:
        e = floor_over_nxt(1, 2, LL, win=win4)[0]
        true_LL = F(floor_over_nxt(1, 2, LL)[0], nscored(LL))
        got = F(e, len(seqs(LL)) * len(win4))
        cf_win4 = (F(1, 4) + F(3, 8)) / 2
        hostiles["H7_L4_window_on_L%d" % LL] = {
            "d2_b1_floor": str(got), "true": str(true_LL), "moved": got != true_LL,
            "applicable": got != true_LL or cf_win4 != true_LL,
            "note": ("vacuous at L = 5: (e_2 + e_3)/2 = %s equals the L = 5 floor %s (FREEZE_V1_AMENDMENT_1.md A1.1)" % (cf_win4, true_LL))
                    if got == true_LL else "applicable; the L = 4 window average %s differs from the L = %d floor %s" % (cf_win4, LL, true_LL)}
    for h in hostiles.values():
        h.setdefault("applicable", True)
    res["hostiles"] = hostiles
    res["hostiles_applicable"] = sorted(k for k, h in hostiles.items() if h["applicable"])
    res["hostiles_vacuous"] = sorted(k for k, h in hostiles.items() if not h["applicable"])
    res["hostiles_all_moved"] = all(h["moved"] for h in hostiles.values() if h["applicable"]) and len(res["hostiles_applicable"]) >= 7
    # no-alarm control: initial state 0 -> 1 at b = 1
    e = floor_over_nxt(1, 2, L, init=1)[0]
    res["no_alarm_control"] = {"perturbation": "initial state 0 -> 1 at b = 1", "d2_b1_floor": str(F(e, N)),
                               "true": str(R5[(1, 2)]), "silent_as_required": F(e, N) == R5[(1, 2)]}

    # ------------------------------------------------------------ nulls (L = 6)
    L = 6
    N = nscored(L)
    R6 = {}
    for b in BUDGETS:
        for m in MODES:
            R6[(b, m)] = F(floor_over_nxt(b, m, L)[0], N)
    hi6 = [(eta, p, endpoints(R6, eta, p)[1]) for eta, p in W]
    true_pair = (F(1, 2), F(1, 2) - R6[(1, 2)])
    rng = random.Random(20260919)
    best = 0
    perfect = 0
    redraws = 0
    for _ in range(200):
        while True:
            a, b = F(rng.randrange(0, 129), 128), F(rng.randrange(0, 129), 128)
            if (a, b) != true_pair:
                break
            redraws += 1
        n = sum(1 for eta, p, hi in hi6 if eta * (a * p[1] + b * p[2]) == hi)
        best = max(best, n)
        perfect += int(n == len(W))
    marg = sum(1 for eta, p, hi in hi6 if eta * (true_pair[0] * p[1] + true_pair[1] * p[2]) == hi)
    res["null_upper_endpoint_L6"] = {"trials": 200, "best": "%d/%d" % (best, len(W)), "perfect": perfect,
                                     "pool": "(k/128, k/128), k in 0..128, minus the marginal pair (AMENDMENT_1 A1.3(1))",
                                     "redraws_of_excluded_point": redraws,
                                     "marginal_pair": [str(true_pair[0]), str(true_pair[1])],
                                     "marginal_score": "%d/%d" % (marg, len(W))}
    coef6 = 4 * R6[(1, 2)] - 1
    grid0 = [(F(eta), p) for eta, p in W] + [(F(eta), p) for _n, p in PROBES for eta in ETAS]
    truth0 = [(eta, p, unique_one_bit_somewhere(profile(R6, eta, p))) for eta, p in grid0]
    # (i) as first frozen (FREEZE section 5): pool includes the true coefficient, no discriminating worlds
    rng = random.Random(20260920)
    best = 0
    perfect = 0
    perfect_cs = set()
    for _ in range(200):
        c = F(rng.randrange(0, 65), 64)
        n = sum(1 for eta, p, ne in truth0 if (p[1] > c * p[2]) == ne)
        best = max(best, n)
        if n == len(truth0):
            perfect += 1
            perfect_cs.add(str(c))
    n_pred0 = sum(1 for eta, p, ne in truth0 if (p[1] > coef6 * p[2]) == ne)
    res["null_collapse_rule_L6_as_first_frozen"] = {
        "trials": 200, "worlds": len(truth0), "best": "%d/%d" % (best, len(truth0)), "perfect": perfect,
        "perfect_coefficients": sorted(perfect_cs, key=lambda x: F(x)),
        "predicted_coefficient": str(coef6), "predicted_score": "%d/%d" % (n_pred0, len(truth0)),
        "status": "MISS of the FREEZE section 5 uniqueness clause on the frozen grid (recorded, not repaired; see FREEZE_V1_AMENDMENT_1.md)"
                  if perfect > 0 else "uniqueness clause held on the frozen grid"}
    # (ii) amended (AMENDMENT_1 A1.3(1)-(2)): pool excludes 18/64; two null-discriminating worlds added
    disc = [(F(eta), p) for _n, p in NULL_DISCRIMINATING for eta in ETAS]
    disc_truth = [(eta, p, unique_one_bit_somewhere(profile(R6, eta, p))) for eta, p in disc]
    truth = truth0 + disc_truth
    rng = random.Random(20260920)
    best = 0
    perfect = 0
    redraws = 0
    for _ in range(200):
        while True:
            c = F(rng.randrange(0, 65), 64)
            if c != coef6:
                break
            redraws += 1
        n = sum(1 for eta, p, ne in truth if (p[1] > c * p[2]) == ne)
        best = max(best, n)
        perfect += int(n == len(truth))
    n_pred = sum(1 for eta, p, ne in truth if (p[1] > coef6 * p[2]) == ne)
    res["null_collapse_rule_L6"] = {"trials": 200, "worlds": len(truth), "best": "%d/%d" % (best, len(truth)), "perfect": perfect,
                                    "pool": "k/64, k in 0..64, minus the predicted coefficient (AMENDMENT_1 A1.3(1))",
                                    "redraws_of_excluded_point": redraws,
                                    "predicted_coefficient": str(coef6), "predicted_score": "%d/%d" % (n_pred, len(truth)),
                                    "coefficient_in_grid": coef6.denominator <= 64,
                                    "null_discriminating_worlds": [{"name": nm, "p": [str(x) for x in p], "by_eta": [
                                        {"eta": str(eta), "niche_nonempty_L6": ne, "endpoints": [str(x) for x in endpoints(R6, eta, p)]}
                                        for eta, pp, ne in disc_truth if pp == p]} for nm, p in NULL_DISCRIMINATING]}
    res["null_discriminating_worlds_prediction_hit"] = all(
        (ne is False) if p == NULL_DISCRIMINATING[0][1] else (ne is True) for eta, p, ne in disc_truth)
    res["vacuity"] = {"L5_nonempty_vs_empty": [per_L[5]["nonempty_niches"], "%d/135" % (135 - int(per_L[5]["nonempty_niches"].split("/")[0]))],
                      "L6_nonempty_vs_empty": [per_L[6]["nonempty_niches"], "%d/135" % (135 - int(per_L[6]["nonempty_niches"].split("/")[0]))],
                      "probes_both_outcomes_each_L": all(len(set(r["niche_nonempty"] for row in per_L[L]["probes"] for r in row["by_eta"])) == 2 for L in LENGTHS),
                      "every_bound_has_both_sides": True}
    res["vacuity"]["every_bound_has_both_sides"] = res["vacuity"]["probes_both_outcomes_each_L"] and all(
        0 < int(per_L[L]["nonempty_niches"].split("/")[0]) < 135 for L in LENGTHS)

    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        fh.write(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    sys.stdout.write(json.dumps({"verdict": res["verdict"], "hit": res["hit_conditions"], "hostiles_all_moved": res["hostiles_all_moved"],
                                 "no_alarm": res["no_alarm_control"]["silent_as_required"],
                                 "null1": res["null_upper_endpoint_L6"], "null2": res["null_collapse_rule_L6"]}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
