#!/usr/bin/env python3
"""GMI #833 AE2 -- predictive-information learnability boundary, route A.

Exact rational arithmetic only; emits RESULT_V1.json on stdout.

Route A derives everything from closed-form algebra and a subcube dynamic
program.  The independent oracle (independent_boundary_oracle_v1.py) shares no
import with this module and recomputes every quantity by enumeration.
"""
import json
import sys
from fractions import Fraction as F

CLAIM_CEILING = (
    "GMI_833_AE2_PREDICTIVE_INFORMATION_LEARNABILITY_BOUNDARY_PROVED_AND_"
    "EXACTLY_WITNESSED_AT_REGISTERED_FINITE_SCOPE"
)
SOURCE_MAIN = "91c6d2876ba80c517a186e28fce3bdbe4e3fc218"
FREEZE_COMMIT = "3901753eaa746cbe6ac3e18cd80034e728c1aead"

# --------------------------------------------------------------------------
# basic exact quantities
# --------------------------------------------------------------------------


def marginals(P, xs, ys):
    px = dict((x, sum((P[(x, y)] for y in ys), F(0))) for x in xs)
    py = dict((y, sum((P[(x, y)] for x in xs), F(0))) for y in ys)
    return px, py


def acc_base(P, xs, ys):
    _, py = marginals(P, xs, ys)
    return max(py[y] for y in ys)


def acc_obs(P, xs, ys):
    return sum((max(P[(x, y)] for y in ys) for x in xs), F(0))


def gain(P, xs, ys):
    return acc_obs(P, xs, ys) - acc_base(P, xs, ys)


def l1_dependence(P, xs, ys):
    px, py = marginals(P, xs, ys)
    return sum((abs(P[(x, y)] - px[x] * py[y]) for x in xs for y in ys), F(0))


def chi_squared(P, xs, ys):
    px, py = marginals(P, xs, ys)
    tot = F(0)
    for x in xs:
        for y in ys:
            if P[(x, y)] != 0:
                tot += P[(x, y)] * P[(x, y)] / (px[x] * py[y])
    return tot - F(1)


def is_independent(P, xs, ys):
    px, py = marginals(P, xs, ys)
    return all(P[(x, y)] == px[x] * py[y] for x in xs for y in ys)


# --------------------------------------------------------------------------
# PIB-3: certified rational enclosure of the natural logarithm
# --------------------------------------------------------------------------

LOG_TERMS = 48


def ln_bracket(t, terms=LOG_TERMS):
    """Exact rational [lo, hi] with lo <= ln(t) <= hi, for rational t > 0.

    Uses ln(t) = 2 atanh(z) with z = (t-1)/(t+1), |z| < 1.  The partial sum
    S_K = sum_{j<K} z^(2j+1)/(2j+1) has remainder of the same sign as z and
    magnitude at most |z|^(2K+1) / ((2K+1)(1 - z^2)).  No float is used.
    """
    t = F(t)
    if t <= 0:
        raise ValueError("ln of a non-positive rational")
    z = (t - 1) / (t + 1)
    s = F(0)
    zp = z
    z2 = z * z
    for j in range(terms):
        s += zp / (2 * j + 1)
        zp *= z2
    rem = abs(zp) / ((2 * terms + 1) * (F(1) - z2))
    if z >= 0:
        lo, hi = s, s + rem
    else:
        lo, hi = s - rem, s
    return 2 * lo, 2 * hi


def mutual_information_bracket(P, xs, ys):
    """Exact rational [lo, hi] bracketing I(X;Y) in nats."""
    px, py = marginals(P, xs, ys)
    lo = F(0)
    hi = F(0)
    for x in xs:
        for y in ys:
            p = P[(x, y)]
            if p == 0:
                continue
            a, b = ln_bracket(p / (px[x] * py[y]))
            lo += p * a
            hi += p * b
    return lo, hi


# --------------------------------------------------------------------------
# PIB-1: the no-predictive-information boundary
# --------------------------------------------------------------------------

B2 = [0, 1]


def iid_history_world(p1, hist_len):
    """Y = X_t from an i.i.d. Bernoulli(p1) source; the observation is the
    whole allowed history (X_{t-hist_len} .. X_{t-1})."""
    p1 = F(p1)
    hists = [()]
    for _ in range(hist_len):
        hists = [h + (b,) for h in hists for b in B2]
    P = {}
    for h in hists:
        w = F(1)
        for b in h:
            w *= p1 if b == 1 else (F(1) - p1)
        for y in B2:
            P[(h, y)] = w * (p1 if y == 1 else (F(1) - p1))
    return P, hists, B2


LOSSES = {
    "zero_one": lambda a, y: F(0) if a == y else F(1),
    "asymmetric": lambda a, y: F(0) if a == y else (F(3) if y == 1 else F(1)),
    "squared": lambda a, y: F((a - y) ** 2),
}


def blind_risk(P, xs, ys, loss):
    _, py = marginals(P, xs, ys)
    return min(sum((py[y] * loss(a, y) for y in ys), F(0)) for a in ys)


def informed_risk(P, xs, ys, loss):
    return sum(
        (min(sum((P[(x, y)] * loss(a, y) for y in ys), F(0)) for a in ys)
         for x in xs),
        F(0),
    )


# --------------------------------------------------------------------------
# PIB-2: gain <= D/2, verified exhaustively on an integer grid
# --------------------------------------------------------------------------

GRID_DEN = 8
GRID_MAX_SHAPE = 4


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def sweep_gain_bound():
    """Exhaustively verify 2*gain <= D over the frozen integer grid.

    Cleared of denominators: with n(x,y) integers summing to `den`,
      gain = [sum_x max_y n(x,y) - max_y ny] / den
      D    = sum_{x,y} |n(x,y)*den - nx*ny| / den^2
    so 2*gain <= D  <=>  2*den*[...] <= sum |n*den - nx*ny|.
    """
    cases = 0
    violations = 0
    tight = 0
    for a in range(1, GRID_MAX_SHAPE + 1):
        for b in range(1, GRID_MAX_SHAPE + 1):
            for comp in compositions(GRID_DEN, a * b):
                rows = [comp[x * b:(x + 1) * b] for x in range(a)]
                nx = [sum(r) for r in rows]
                ny = [sum(rows[x][y] for x in range(a)) for y in range(b)]
                g = sum(max(r) for r in rows) - max(ny)
                d = 0
                for x in range(a):
                    for y in range(b):
                        d += abs(rows[x][y] * GRID_DEN - nx[x] * ny[y])
                cases += 1
                lhs = 2 * GRID_DEN * g
                if lhs > d:
                    violations += 1
                elif lhs == d and g > 0:
                    tight += 1
    return cases, violations, tight


# --------------------------------------------------------------------------
# PIB-4: decoder-complexity accessible information
# --------------------------------------------------------------------------

NBITS = 3
XS = list(range(2 ** NBITS))


def bit(x, i):
    return (x >> i) & 1


def parity_world(secret):
    P = {}
    for x in XS:
        y = bin(x & secret).count("1") % 2
        P[(x, y)] = F(1, 8)
        P[(x, 1 - y)] = F(0)
    return P


def best_depth_bounded_accuracy(P, depth):
    """Subcube dynamic program: the best accuracy of any decision tree of
    branching depth at most `depth`.

    best(S, d) = max( best constant on S,
                      max_i [ best(S|x_i=0, d-1) + best(S|x_i=1, d-1) ] ).
    No function class is enumerated and no tree object is built.
    """
    memo = {}

    def rec(mask, vals, d):
        key = (mask, vals, d)
        if key in memo:
            return memo[key]
        live = [x for x in XS if (x & mask) == vals]
        c0 = sum((P[(x, 0)] for x in live), F(0))
        c1 = sum((P[(x, 1)] for x in live), F(0))
        best = c0 if c0 > c1 else c1
        if d > 0:
            for i in range(NBITS):
                if mask & (1 << i):
                    continue
                v = (rec(mask | (1 << i), vals, d - 1)
                     + rec(mask | (1 << i), vals | (1 << i), d - 1))
                if v > best:
                    best = v
        memo[key] = best
        return best

    return rec(0, 0, depth)


def determined_and_uniform_target(P):
    """True iff Y is a function of X and the Y-marginal is uniform.

    Under both conditions I(X;Y) = H(Y) - H(Y|X) = 1 bit exactly for binary Y,
    with no logarithm evaluated anywhere.
    """
    for x in XS:
        nz = [y for y in B2 if P[(x, y)] != 0]
        if len(nz) != 1:
            return False
    _, py = marginals(P, XS, B2)
    return all(py[y] == F(1, 2) for y in B2)


def subset_uniformity(secret):
    """For every PROPER subset S of the coordinates, (x_S, y) is exactly
    uniform on {0,1}^(|S|+1).  Returned as (checked, violations)."""
    checked = 0
    viols = 0
    for mask in range(2 ** NBITS):
        if mask == (2 ** NBITS) - 1:
            continue          # the full set is not proper
        bits = [i for i in range(NBITS) if mask & (1 << i)]
        counts = {}
        for x in XS:
            key = (tuple(bit(x, i) for i in bits),
                   bin(x & secret).count("1") % 2)
            counts[key] = counts.get(key, 0) + 1
        cells = 2 ** (len(bits) + 1)
        expected = 8 // cells
        checked += 1
        if len(counts) != cells or any(v != expected
                                       for v in counts.values()):
            viols += 1
    return checked, viols


# --------------------------------------------------------------------------
# PIB-5: the registered fixture roster
# --------------------------------------------------------------------------

def fixture_lowent_iid():
    p = F(1, 10)
    P = {}
    for a in B2:
        for b in B2:
            wa = p if a == 1 else F(1) - p
            wb = p if b == 1 else F(1) - p
            P[(a, b)] = wa * wb
    lo, hi = mutual_information_bracket(P, B2, B2)
    ent_lo, ent_hi = entropy_bracket({0: F(9, 10), 1: F(1, 10)})
    return {
        "world": "X_{t-1} -> X_t, i.i.d. Bernoulli(1/10)",
        "marginal": ["9/10", "1/10"],
        "marginal_is_uniform": False,
        "exactly_independent": is_independent(P, B2, B2),
        "l1_dependence": str(l1_dependence(P, B2, B2)),
        "mutual_information_nats_bracket": [str(lo), str(hi)],
        "mutual_information_is_exactly_zero": (
            is_independent(P, B2, B2) and lo == 0 and hi == 0),
        "predictive_gain": str(gain(P, B2, B2)),
        "marginal_entropy_nats_bracket": [str(ent_lo), str(ent_hi)],
        "max_entropy_nats_bracket": [str(x) for x in ln_bracket(F(2))],
    }


def entropy_bracket(pmf):
    lo = F(0)
    hi = F(0)
    for v in pmf.values():
        if v == 0:
            continue
        a, b = ln_bracket(F(1) / v)
        lo += v * a
        hi += v * b
    return lo, hi


def fixture_highent_cyclic():
    """X_t uniform on Z_4 with X_t = X_{t-1} + 1 mod 4."""
    zs = [0, 1, 2, 3]
    P = {}
    for a in zs:
        for b in zs:
            P[(a, b)] = F(1, 4) if b == (a + 1) % 4 else F(0)
    return {
        "world": "X_t = X_{t-1} + 1 (mod 4), X uniform on Z_4",
        "marginal_is_uniform": True,
        "marginal_entropy_bits_exact": "2",
        "acc_base": str(acc_base(P, zs, zs)),
        "acc_obs": str(acc_obs(P, zs, zs)),
        "predictive_gain": str(gain(P, zs, zs)),
        "mutual_information_bits_exact": "2",
        "target_determined_by_history": True,
    }


def fixture_drift_invert():
    """Phase 1: Y = X.  Phase 2: Y = 1 - X.  Phases equiprobable."""
    ph1 = dict(((x, y), F(1, 2) if y == x else F(0)) for x in B2 for y in B2)
    ph2 = dict(((x, y), F(1, 2) if y != x else F(0)) for x in B2 for y in B2)
    pooled = dict(((x, y), (ph1[(x, y)] + ph2[(x, y)]) / 2)
                  for x in B2 for y in B2)
    # the rule fitted on phase 1 is h(x) = x
    acc1 = sum((ph1[(x, x)] for x in B2), F(0))
    acc2 = sum((ph2[(x, x)] for x in B2), F(0))
    lo, hi = mutual_information_bracket(pooled, B2, B2)
    return {
        "world": "two-phase source, Y = X then Y = 1 - X",
        "phase1_gain": str(gain(ph1, B2, B2)),
        "phase2_gain": str(gain(ph2, B2, B2)),
        "phase1_mutual_information_bits_exact": "1",
        "phase2_mutual_information_bits_exact": "1",
        "pooled_exactly_independent": is_independent(pooled, B2, B2),
        "pooled_l1_dependence": str(l1_dependence(pooled, B2, B2)),
        "pooled_mutual_information_nats_bracket": [str(lo), str(hi)],
        "phase1_fitted_rule_accuracy_in_phase1": str(acc1),
        "phase1_fitted_rule_accuracy_in_phase2": str(acc2),
        "phase2_base_rate": str(acc_base(ph2, B2, B2)),
        "historical_dependence_becomes_harmful": acc2 < acc_base(ph2, B2, B2),
    }


DOUBLING_BITS = 8
DOUBLING_OBS = 4


def fixture_chaos_doubling():
    """x_{t+1} = 2 x_t mod 1 on b-bit dyadic states, observed to c bits.

    The emitted symbol at time t is bit (b-1-t) of the integer state.  An
    observer given the top c bits predicts the next c symbols with certainty
    and is at exactly the base rate afterwards.  Verified by enumerating all
    2^b states.
    """
    b, c = DOUBLING_BITS, DOUBLING_OBS
    states = list(range(2 ** b))
    horizon = []
    for t in range(b):
        # conditional on the observed top c bits, is symbol t determined?
        groups = {}
        for s in states:
            obs = s >> (b - c)
            sym = (s >> (b - 1 - t)) & 1
            groups.setdefault(obs, set()).add(sym)
        determined = all(len(v) == 1 for v in groups.values())
        # exact accuracy of the Bayes rule given the observation
        num = 0
        for obs in groups:
            members = [s for s in states if (s >> (b - c)) == obs]
            ones = sum(1 for s in members if (s >> (b - 1 - t)) & 1)
            num += max(ones, len(members) - ones)
        horizon.append({
            "t": t,
            "determined": determined,
            "bayes_accuracy": str(F(num, len(states))),
        })
    first_undetermined = min(h["t"] for h in horizon if not h["determined"])
    return {
        "world": "doubling map on %d-bit dyadic states, top %d bits observed"
                 % (b, c),
        "states_enumerated": len(states),
        "per_step": horizon,
        "certainty_horizon": first_undetermined,
        "accuracy_beyond_horizon": str(F(1, 2)),
        "deterministic_dynamics": True,
    }


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------

REGISTERED_ROSTER = {
    "W_INDEP": dict(((x, y), F(1, 4)) for x in B2 for y in B2),
    "W_DEP_NOPRED": {(0, 0): F(9, 20), (0, 1): F(1, 20),
                     (1, 0): F(7, 20), (1, 1): F(3, 20)},
    "W_TIGHT": {(0, 0): F(1, 2), (0, 1): F(0),
                (1, 0): F(0), (1, 1): F(1, 2)},
    "W_MILD": {(0, 0): F(3, 8), (0, 1): F(1, 8),
               (1, 0): F(1, 8), (1, 1): F(3, 8)},
}


def build():
    res = {}

    # --- PIB-1 -------------------------------------------------------------
    pib1 = {}
    for hist_len in (1, 2):
        P, hists, ys = iid_history_world(F(3, 10), hist_len)
        entry = {"history_length": hist_len,
                 "observation_alphabet": len(hists),
                 "deterministic_rules": len(ys) ** len(hists),
                 "exactly_independent": is_independent(P, hists, ys),
                 "losses": {}}
        for lname, loss in sorted(LOSSES.items()):
            br = blind_risk(P, hists, ys, loss)
            ir = informed_risk(P, hists, ys, loss)
            entry["losses"][lname] = {
                "blind_optimal_risk": str(br),
                "observation_conditioned_optimal_risk": str(ir),
                "improvement": str(br - ir),
            }
        entry["no_loss_improves"] = all(
            F(v["improvement"]) == 0 for v in entry["losses"].values())
        pib1["hist%d" % hist_len] = entry
    res["PIB_1_no_predictive_information"] = pib1

    # --- PIB-2 -------------------------------------------------------------
    cases, viols, tight = sweep_gain_bound()
    roster = {}
    for name, P in sorted(REGISTERED_ROSTER.items()):
        g = gain(P, B2, B2)
        d = l1_dependence(P, B2, B2)
        lo, hi = mutual_information_bracket(P, B2, B2)
        roster[name] = {
            "gain": str(g),
            "l1_dependence": str(d),
            "two_gain_le_D": (2 * g <= d),
            "four_gain_sq_le_D_sq": (4 * g * g <= d * d),
            "chi_squared": str(chi_squared(P, B2, B2)),
            "mutual_information_nats_bracket": [str(lo), str(hi)],
            "pinsker_D_sq_over_two_le_MI_lower": (d * d / 2 <= lo),
            "MI_upper_le_chi_squared": (hi <= chi_squared(P, B2, B2)),
            "two_gain_sq_le_MI_lower": (2 * g * g <= lo),
        }
    res["PIB_2_bounded_predictive_information"] = {
        "theorem": "gain <= D/2, with D = sum |P(x,y) - P_X(x) P_Y(y)|",
        "exhaustive_grid_cases": cases,
        "grid_denominator": GRID_DEN,
        "grid_max_shape": GRID_MAX_SHAPE,
        "violations": viols,
        "cases_attaining_equality_with_positive_gain": tight,
        "tightness_witness": "W_TIGHT: gain = 1/2, D = 1",
        "roster": roster,
        "performance_bound": (
            "2*gain^2 <= D^2/2 <= I(X;Y) in nats, the second step by the "
            "parent-owned Csiszar-Kullback-Pinsker inequality"),
    }

    # --- PIB-3 -------------------------------------------------------------
    probes = [F(2), F(3, 2), F(1, 2), F(4, 3), F(9, 10), F(10, 9)]
    brackets = []
    for t in probes:
        lo, hi = ln_bracket(t)
        brackets.append({
            "t": str(t), "lo": str(lo), "hi": str(hi),
            "width_below_1e-9": (hi - lo) < F(1, 10 ** 9),
            "monotone": lo <= hi,
        })
    # ln(a*b) = ln a + ln b must hold within the brackets
    la = ln_bracket(F(2))
    lb = ln_bracket(F(3))
    lab = ln_bracket(F(6))
    res["PIB_3_log_bracket"] = {
        "series": "ln t = 2 atanh((t-1)/(t+1)), truncated at %d terms with an "
                  "exact rational remainder bound" % LOG_TERMS,
        "terms": LOG_TERMS,
        "probes": brackets,
        "additivity_holds": (la[0] + lb[0] <= lab[1]
                             and lab[0] <= la[1] + lb[1]),
        "all_widths_below_1e-9": all(b["width_below_1e-9"] for b in brackets),
    }

    # --- PIB-4 -------------------------------------------------------------
    par = parity_world(0b111)
    dic = parity_world(0b001)
    depths = {}
    for d in range(NBITS + 1):
        depths["depth%d" % d] = {
            "parity": str(best_depth_bounded_accuracy(par, d)),
            "dictator": str(best_depth_bounded_accuracy(dic, d)),
        }
    checked, viols4 = subset_uniformity(0b111)
    res["PIB_4_decoder_complexity"] = {
        "world": "X uniform on {0,1}^3, Y = x_0 xor x_1 xor x_2",
        "target_determined_and_uniform": determined_and_uniform_target(par),
        "mutual_information_bits_exact": "1",
        "mutual_information_argument": (
            "Y is a function of X and the Y-marginal is uniform, so "
            "I(X;Y) = H(Y) - H(Y|X) = 1 - 0 = 1 bit; no logarithm is "
            "evaluated"),
        "acc_base": str(acc_base(par, XS, B2)),
        "best_accuracy_by_depth": depths,
        "accuracy_below_full_depth_equals_base_rate": all(
            F(depths["depth%d" % d]["parity"]) == acc_base(par, XS, B2)
            for d in range(NBITS)),
        "proper_subsets_checked": checked,
        "proper_subset_uniformity_violations": viols4,
        "unconditional": True,
        "cryptographic_assumption_used": False,
    }

    # --- PIB-5 -------------------------------------------------------------
    res["PIB_5_fixtures"] = {
        "LOWENT_IID": fixture_lowent_iid(),
        "HIGHENT_CYCLIC": fixture_highent_cyclic(),
        "DRIFT_INVERT": fixture_drift_invert(),
        "CHAOS_DOUBLING": fixture_chaos_doubling(),
    }

    # --- null --------------------------------------------------------------
    nullres = null_independence_detector(200)
    res["null"] = nullres

    f = res["PIB_5_fixtures"]
    checks = {
        "PIB_1_no_learner_beats_base_rate": all(
            v["no_loss_improves"] and v["exactly_independent"]
            for v in pib1.values()),
        "PIB_2_gain_bound_holds_everywhere": (viols == 0),
        "PIB_2_bound_is_tight": (tight > 0),
        "PIB_2_pinsker_chain_holds": all(
            r["two_gain_le_D"] and r["pinsker_D_sq_over_two_le_MI_lower"]
            and r["MI_upper_le_chi_squared"] and r["two_gain_sq_le_MI_lower"]
            for r in roster.values()),
        "PIB_3_brackets_valid": (res["PIB_3_log_bracket"]["additivity_holds"]
                                 and res["PIB_3_log_bracket"][
                                     "all_widths_below_1e-9"]),
        "PIB_4_shannon_vs_accessible": (
            res["PIB_4_decoder_complexity"][
                "target_determined_and_uniform"] and
            res["PIB_4_decoder_complexity"][
                "accuracy_below_full_depth_equals_base_rate"] and
            viols4 == 0),
        "PIB_5_lowent_iid_valid": (
            f["LOWENT_IID"]["mutual_information_is_exactly_zero"] and
            not f["LOWENT_IID"]["marginal_is_uniform"] and
            f["LOWENT_IID"]["predictive_gain"] == "0"),
        "PIB_5_highent_cyclic_valid": (
            f["HIGHENT_CYCLIC"]["marginal_is_uniform"] and
            f["HIGHENT_CYCLIC"]["predictive_gain"] == "3/4"),
        "PIB_5_drift_valid": (
            f["DRIFT_INVERT"]["pooled_exactly_independent"] and
            f["DRIFT_INVERT"]["historical_dependence_becomes_harmful"]),
        "PIB_5_chaos_valid": (
            f["CHAOS_DOUBLING"]["certainty_horizon"] == DOUBLING_OBS and
            all(h["determined"] for h in f["CHAOS_DOUBLING"]["per_step"]
                if h["t"] < DOUBLING_OBS) and
            all(h["bayes_accuracy"] == "1/2"
                for h in f["CHAOS_DOUBLING"]["per_step"]
                if h["t"] >= DOUBLING_OBS)),
        "null_beaten": (nullres["random_worlds_flagged"] == 0
                        and nullres["planted_positive_flagged"]),
        "null_no_alarm_on_clean": (nullres["known_clean_flagged"] == []),
    }

    return {
        "schema": "GMI_833_AE2_PREDICTIVE_BOUNDARY_RESULT_V1",
        "issue": 833,
        "section": "AE2",
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "theorems": ["PIB-1", "PIB-2", "PIB-3", "PIB-4", "PIB-5"],
        "results": res,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


# --------------------------------------------------------------------------
# null: a detector for "maximal Shannon information, zero accessible gain"
# --------------------------------------------------------------------------

def lcg_stream(seed, n):
    s = seed
    out = []
    for _ in range(n):
        s = (1664525 * s + 1013904223) % (2 ** 32)
        out.append(s)
    return out


def random_deterministic_world(rands):
    """Y a deterministic function of X, chosen bitwise from the LCG."""
    P = {}
    for i, x in enumerate(XS):
        y = rands[i] & 1
        P[(x, y)] = F(1, 8)
        P[(x, 1 - y)] = F(0)
    return P


def hidden_information_detector(P):
    """Fires iff Y is determined by X with a uniform marginal (so I(X;Y) is
    exactly one bit) while no depth-2 decision tree beats the base rate."""
    if not determined_and_uniform_target(P):
        return False
    return best_depth_bounded_accuracy(P, NBITS - 1) == acc_base(P, XS, B2)


def null_independence_detector(trials):
    rs = lcg_stream(88117723, trials * 8)
    hits = 0
    for t in range(trials):
        P = random_deterministic_world(rs[t * 8:(t + 1) * 8])
        if hidden_information_detector(P):
            hits += 1
    clean = []
    for nm, sec in (("W_DICT", 0b001), ("W_XOR2", 0b011)):
        if hidden_information_detector(parity_world(sec)):
            clean.append(nm)
    return {
        "detector": ("Y determined by X with uniform Y-marginal (I(X;Y) = 1 "
                     "bit exactly) while no depth-2 decision tree beats the "
                     "base rate"),
        "trials": trials,
        "family": "Y a deterministic bitwise-random function of X on {0,1}^3",
        "random_worlds_flagged": hits,
        "planted_positive_flagged": hidden_information_detector(
            parity_world(0b111)),
        "known_clean_flagged": sorted(clean),
    }


def main():
    out = build()
    sys.stdout.write(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return 0 if out["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
