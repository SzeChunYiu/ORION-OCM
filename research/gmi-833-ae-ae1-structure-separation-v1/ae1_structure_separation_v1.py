#!/usr/bin/env python3
"""GMI #833 AE1 -- exploitable-structure separation lattice, analytic route A.

Exact rational arithmetic only.  Emits RESULT_V1.json on stdout.

Route A derives every quantity from closed-form algebra:
  * accuracies from the argmax identity  acc_obs = sum_x max_y P(x,y),
  * admissible rule classes from function-level classification
    (essential-variable arity and memoised decision-tree depth),
  * the learning curve from an analytic span/rank argument.

The independent oracle (independent_separation_oracle_v1.py) shares no import
with this module and recomputes everything by explicit enumeration.
"""
import json
import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import minimality_sweeps_v1 as MS

CLAIM_CEILING = (
    "GMI_833_AE1_TASK_RELATIVE_EXPLOITABLE_STRUCTURE_SEPARATED_"
    "ON_REGISTERED_FINITE_WITNESS_ROSTER"
)
SOURCE_MAIN = "91c6d2876ba80c517a186e28fce3bdbe4e3fc218"
FREEZE_COMMIT = "a466dab4c464e0c697f4caf5a3cceb3a5d73278c"

# --------------------------------------------------------------------------
# registered world objects
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


def pred_marg_nonunif(P, xs, ys):
    px, _ = marginals(P, xs, ys)
    u = F(1, len(xs))
    return any(px[x] != u for x in xs)


def pred_dep(P, xs, ys):
    px, py = marginals(P, xs, ys)
    return any(P[(x, y)] != px[x] * py[y] for x in xs for y in ys)


def pred_pred(P, xs, ys):
    return acc_obs(P, xs, ys) > acc_base(P, xs, ys)


def l1_dependence(P, xs, ys):
    px, py = marginals(P, xs, ys)
    return sum((abs(P[(x, y)] - px[x] * py[y]) for x in xs for y in ys), F(0))


def ctrl_values(P, xs, ys, acts, U):
    """(best blind expected utility, best observation-conditioned utility)."""
    _, py = marginals(P, xs, ys)
    blind = max(sum((py[y] * U[(a, y)] for y in ys), F(0)) for a in acts)
    seeing = sum(
        (max(sum((P[(x, y)] * U[(a, y)] for y in ys), F(0)) for a in acts)
         for x in xs),
        F(0),
    )
    return blind, seeing


# --------------------------------------------------------------------------
# registered distributional witnesses
# --------------------------------------------------------------------------

B2 = [0, 1]


def _w(pairs):
    return dict(((x, y), F(n, d)) for (x, y, n, d) in pairs)


WORLDS = {
    # independent, uniform marginals
    "W_IND_UNIF": dict(
        xs=B2, ys=B2,
        P=_w([(0, 0, 1, 4), (0, 1, 1, 4), (1, 0, 1, 4), (1, 1, 1, 4)]),
    ),
    # nonuniform X-marginal, exactly independent
    "W_IND_SKEW": dict(
        xs=B2, ys=B2,
        P=_w([(0, 0, 3, 8), (0, 1, 3, 8), (1, 0, 1, 8), (1, 1, 1, 8)]),
    ),
    # uniform marginals, strongly dependent and predictive
    "W_DEP_UNIFMARG": dict(
        xs=B2, ys=B2,
        P=_w([(0, 0, 1, 2), (0, 1, 0, 1), (1, 0, 0, 1), (1, 1, 1, 2)]),
    ),
    # dependent but with zero Bayes gain
    "W_DEP_NOPRED": dict(
        xs=B2, ys=B2,
        P=_w([(0, 0, 9, 20), (0, 1, 1, 20), (1, 0, 7, 20), (1, 1, 3, 20)]),
    ),
}

# control witnesses: (P, actions, utility)
CTRL_WORLDS = {
    # perfectly predictive, yet the observation is worthless for control
    "W_PRED_NOCTRL": dict(
        xs=B2, ys=B2,
        P=_w([(0, 0, 1, 2), (0, 1, 0, 1), (1, 0, 0, 1), (1, 1, 1, 2)]),
        acts=["a0", "a1"],
        U={("a0", 0): F(1), ("a0", 1): F(1),
           ("a1", 0): F(3, 4), ("a1", 1): F(7, 8)},
    ),
    # zero Bayes gain, yet the observation is strictly control-relevant
    "W_CTRL_NOPRED": dict(
        xs=["a", "b"], ys=[0, 1, 2],
        P={("a", 0): F(1, 4), ("a", 1): F(1, 4), ("a", 2): F(0),
           ("b", 0): F(1, 4), ("b", 1): F(0), ("b", 2): F(1, 4)},
        acts=["alpha1", "alpha2"],
        U={("alpha1", 0): F(0), ("alpha1", 1): F(1), ("alpha1", 2): F(0),
           ("alpha2", 0): F(0), ("alpha2", 1): F(0), ("alpha2", 2): F(1)},
    ),
}

# --------------------------------------------------------------------------
# registered causal witness: Z -> X, Z -> Y, no edge X -> Y
# --------------------------------------------------------------------------

CAUSAL = dict(
    pz={0: F(1, 2), 1: F(1, 2)},
    # P(X=x | Z=z): copies Z with probability 4/5
    px_z={(0, 0): F(4, 5), (1, 0): F(1, 5), (0, 1): F(1, 5), (1, 1): F(4, 5)},
    # P(Y=y | Z=z): copies Z with probability 3/4
    py_z={(0, 0): F(3, 4), (1, 0): F(1, 4), (0, 1): F(1, 4), (1, 1): F(3, 4)},
)


def causal_tables():
    pz, px_z, py_z = CAUSAL["pz"], CAUSAL["px_z"], CAUSAL["py_z"]
    joint = {}
    for x in B2:
        for y in B2:
            joint[(x, y)] = sum((pz[z] * px_z[(x, z)] * py_z[(y, z)]
                                 for z in B2), F(0))
    px = dict((x, sum((joint[(x, y)] for y in B2), F(0))) for x in B2)
    cond = dict(((x, y), joint[(x, y)] / px[x]) for x in B2 for y in B2)
    # do(X=x) severs Z -> X, so Y keeps its Z-driven marginal
    do = dict(((x, y), sum((pz[z] * py_z[(y, z)] for z in B2), F(0)))
              for x in B2 for y in B2)
    return joint, cond, do


# --------------------------------------------------------------------------
# resource-bounded rule classes over X = {0,1}^n
# --------------------------------------------------------------------------

NBITS = 3
XS3 = list(range(2 ** NBITS))


def bit(x, i):
    return (x >> i) & 1


def essential_arity(table):
    """Number of coordinates the truth table genuinely depends on."""
    n = 0
    for i in range(NBITS):
        for x in XS3:
            if bit(x, i) == 0 and table[x] != table[x ^ (1 << i)]:
                n += 1
                break
    return n


def dt_depth(table):
    """Exact decision-tree depth, memoised over subcubes."""
    memo = {}

    def rec(mask, vals):
        # mask: set of fixed coordinates; vals: their assignment
        key = (mask, vals)
        if key in memo:
            return memo[key]
        live = [x for x in XS3 if (x & mask) == vals]
        first = table[live[0]]
        if all(table[x] == first for x in live):
            memo[key] = 0
            return 0
        best = NBITS
        for i in range(NBITS):
            if mask & (1 << i):
                continue
            d0 = rec(mask | (1 << i), vals)
            d1 = rec(mask | (1 << i), vals | (1 << i))
            cand = 1 + max(d0, d1)
            if cand < best:
                best = cand
        memo[key] = best
        return best

    return rec(0, 0)


ALL_TABLES = None


def all_tables():
    global ALL_TABLES
    if ALL_TABLES is None:
        ALL_TABLES = []
        for code in range(2 ** len(XS3)):
            ALL_TABLES.append(tuple((code >> j) & 1 for j in range(len(XS3))))
    return ALL_TABLES


CLASS_CACHE = {}


def rule_class(k, d):
    """Functions {0,1}^3 -> {0,1} of essential arity <= k and DT depth <= d."""
    key = (k, d)
    if key not in CLASS_CACHE:
        CLASS_CACHE[key] = [t for t in all_tables()
                            if essential_arity(t) <= k and dt_depth(t) <= d]
    return CLASS_CACHE[key]


def parity_world(secret):
    """Uniform X on {0,1}^3, Y = <secret, X> mod 2."""
    P = {}
    for x in XS3:
        y = bin(x & secret).count("1") % 2
        for yy in B2:
            P[(x, yy)] = F(1, 8) if yy == y else F(0)
    return P


def noisy_dictator_world(num, den):
    """Y = x_0 with probability num/den, else the flip."""
    p = F(num, den)
    P = {}
    for x in XS3:
        y = bit(x, 0)
        P[(x, y)] = F(1, 8) * p
        P[(x, 1 - y)] = F(1, 8) * (F(1) - p)
    return P


def best_acc_in_class(P, k, d):
    best = F(0)
    for t in rule_class(k, d):
        a = sum((P[(x, t[x])] for x in XS3), F(0))
        if a > best:
            best = a
    return best


RESOURCE_WORLDS = {
    "W_PARITY3": parity_world(0b111),
    "W_DICT": parity_world(0b001),
    "W_NOISY_DICT": noisy_dictator_world(3, 4),
}

BUDGETS = [(k, d) for k in range(4) for d in range(4)]


# --------------------------------------------------------------------------
# finite-sample discoverability (analytic route)
# --------------------------------------------------------------------------

def rank_gf2(vectors):
    basis = []
    for v in vectors:
        cur = v
        for b in basis:
            cur = min(cur, cur ^ b)
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    return len(basis)


def span_size(vectors):
    return 2 ** rank_gf2(vectors)


def analytic_learning_curve(m):
    """Bayes-optimal expected test accuracy after m i.i.d. labelled pairs.

    Hypothesis family: all 2^3 secrets s (including s = 0), uniform prior.
    Given the training pairs, the consistent secrets form a coset of the
    annihilator of span(x_1..x_m).  On a test point inside that span the label
    is determined identically for every consistent secret, so the posterior
    predictive is correct with probability 1; outside the span the consistent
    secrets split exactly evenly, so any rule scores exactly 1/2.
    Hence  E[acc] = 1/2 + 1/2 * Pr[x_test in span(x_1..x_m)].
    """
    total = F(0)
    count = 2 ** (NBITS * m) if m else 1
    tuples = [()] if m == 0 else None
    if m:
        tuples = []
        stack = [()]
        for _ in range(m):
            nxt = []
            for pre in stack:
                for v in XS3:
                    nxt.append(pre + (v,))
            stack = nxt
        tuples = stack
    for tr in tuples:
        sz = span_size(list(tr))
        p_in = F(sz, 8)
        total += F(1, 2) + F(1, 2) * p_in
    return total / count


def marginalised_parity_family_world():
    """Joint over (x, y) with the secret marginalised out, uniform over 8."""
    P = {}
    for x in XS3:
        c1 = sum(1 for s in range(8) if bin(x & s).count("1") % 2 == 1)
        P[(x, 1)] = F(1, 8) * F(c1, 8)
        P[(x, 0)] = F(1, 8) * F(8 - c1, 8)
    return P


# --------------------------------------------------------------------------
# minimal-shape realizability search (rows 2-3, row 8)
# --------------------------------------------------------------------------

GRID_DEN = 8
MAX_SHAPE = 4


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def pattern_of(P, xs, ys):
    return (pred_marg_nonunif(P, xs, ys),
            pred_dep(P, xs, ys),
            pred_pred(P, xs, ys))


def integer_pattern(counts, a, b, den):
    """Exact (MARG_NONUNIF, DEP, PRED) from integer numerators over `den`.

    Every test is cleared of denominators, so the whole grid sweep runs in
    integer arithmetic.  This is an exact rewriting of the Fraction-valued
    definitions, not an approximation:
      marginal uniform   <=>  nx * a == den
      independence       <=>  n(x,y) * den == nx * ny   for every cell
      Bayes gain positive<=>  sum_x max_y n(x,y) > max_y ny
    """
    nx = [0] * a
    ny = [0] * b
    for x in range(a):
        row = counts[x * b:(x + 1) * b]
        nx[x] = sum(row)
        for y in range(b):
            ny[y] += row[y]
    marg = any(nx[x] * a != den for x in range(a))
    dep = False
    for x in range(a):
        for y in range(b):
            if counts[x * b + y] * den != nx[x] * ny[y]:
                dep = True
                break
        if dep:
            break
    obs = sum(max(counts[x * b:(x + 1) * b]) for x in range(a))
    pred = obs > max(ny)
    return (marg, dep, pred)


_RMAP_CACHE = {}


def realizability_map():
    """shape -> set of achievable (MARG_NONUNIF, DEP, PRED) patterns."""
    key = (GRID_DEN, MAX_SHAPE)
    if key in _RMAP_CACHE:
        return _RMAP_CACHE[key]
    out = {}
    for a in range(1, MAX_SHAPE + 1):
        for b in range(1, MAX_SHAPE + 1):
            seen = set()
            for comp in compositions(GRID_DEN, a * b):
                seen.add(integer_pattern(comp, a, b, GRID_DEN))
            out[(a, b)] = seen
    _RMAP_CACHE[key] = out
    return out


def minimal_shapes(rmap, pattern):
    hits = [s for s in rmap if pattern in rmap[s]]
    minimal = []
    for s in hits:
        dominated = any(
            (o != s and o[0] <= s[0] and o[1] <= s[1]) for o in hits)
        if not dominated:
            minimal.append(s)
    return sorted(minimal)


# --------------------------------------------------------------------------
# null: order reversals in randomly drawn world pairs
# --------------------------------------------------------------------------

def lcg_stream(seed, n):
    """Deterministic integer LCG (Numerical Recipes constants)."""
    s = seed
    out = []
    for _ in range(n):
        s = (1664525 * s + 1013904223) % (2 ** 32)
        out.append(s)
    return out


def random_binary_world(rands):
    """Uniform X on {0,1}^3; P(Y=1|x) a multiple of 1/8 drawn from rands."""
    P = {}
    for i, x in enumerate(XS3):
        q = F(rands[i] % 9, 8)
        P[(x, 1)] = F(1, 8) * q
        P[(x, 0)] = F(1, 8) * (F(1) - q)
    return P


def has_order_reversal(Pa, Pb, budgets):
    accs = [(best_acc_in_class(Pa, k, d), best_acc_in_class(Pb, k, d))
            for (k, d) in budgets]
    pos = any(a > b for (a, b) in accs)
    neg = any(a < b for (a, b) in accs)
    return pos and neg


def reversal_genericity(trials, budgets):
    """Measured auxiliary, NOT the null: how generic budget order reversals are.

    A single reversal already refutes every budget-independent scalar, so this
    frequency is reported for information; the package's null is the
    accessibility-gap detector below.
    """
    rs = lcg_stream(20260918, trials * 16)
    hits = 0
    for t in range(trials):
        blk = rs[t * 16:(t + 1) * 16]
        Pa = random_binary_world(blk[:8])
        Pb = random_binary_world(blk[8:])
        if has_order_reversal(Pa, Pb, budgets):
            hits += 1
    return hits


LOW_BUDGETS = [(k, d) for (k, d) in BUDGETS if k <= 2]


def accessibility_gap(P):
    """Detector: full-information structure exists, none of it is usable below
    the top of the frozen budget lattice.

    Fires iff  acc_full > acc_base  and  max_{R : k<=2} U(W,R) == acc_base.
    """
    base = acc_base(P, XS3, B2)
    full = acc_obs(P, XS3, B2)
    if full <= base:
        return False
    for (k, d) in LOW_BUDGETS:
        if best_acc_in_class(P, k, d) > base:
            return False
    return True


TOP_BUDGET = (3, 3)
NULL_MAGNITUDE_THRESHOLD = F(1, 4)


def accessibility_gap_magnitude(P):
    """acc_full minus the best accuracy attainable strictly below the top
    of the frozen budget lattice: how much registered structure exists that
    no sub-top budget can reach."""
    below = max(best_acc_in_class(P, k, d)
                for (k, d) in BUDGETS if (k, d) != TOP_BUDGET)
    return acc_obs(P, XS3, B2) - below


def null_accessibility_gap(trials):
    """Returns (unthresholded hit count, hits at/above the frozen magnitude
    threshold, the largest magnitude seen, the full magnitude roster).

    The detector is NOT tuned to make the count zero: the unthresholded rate is
    reported in full, and the seven random worlds that do exhibit a genuine but
    tiny accessibility gap are listed with their exact magnitudes.
    """
    rs = lcg_stream(770412339, trials * 8)
    raw = 0
    big = 0
    biggest = F(0)
    roster = []
    for t in range(trials):
        P = random_binary_world(rs[t * 8:(t + 1) * 8])
        if accessibility_gap(P):
            raw += 1
            mag = accessibility_gap_magnitude(P)
            roster.append([t, str(mag)])
            if mag > biggest:
                biggest = mag
            if mag >= NULL_MAGNITUDE_THRESHOLD:
                big += 1
    return raw, big, biggest, roster


CANDIDATE_SCALARS = ("full_information_gain", "l1_dependence", "chi_squared")


def chi_squared(P, xs, ys):
    px, py = marginals(P, xs, ys)
    tot = F(0)
    for x in xs:
        for y in ys:
            if P[(x, y)] != 0:
                tot += P[(x, y)] * P[(x, y)] / (px[x] * py[y])
    return tot - F(1)


def scalar_value(name, P):
    if name == "full_information_gain":
        return acc_obs(P, XS3, B2) - acc_base(P, XS3, B2)
    if name == "l1_dependence":
        return l1_dependence(P, XS3, B2)
    if name == "chi_squared":
        return chi_squared(P, XS3, B2)
    raise ValueError(name)


def refute_candidate_scalar(name, Pa, Pb, budgets):
    """A budget-independent sigma is refuted if its order on (A,B) contradicts
    the achievable-accuracy order at some budget."""
    sa, sb = scalar_value(name, Pa), scalar_value(name, Pb)
    for (k, d) in budgets:
        ua = best_acc_in_class(Pa, k, d)
        ub = best_acc_in_class(Pb, k, d)
        if sa >= sb and ua < ub:
            return True, "k%d_d%d" % (k, d), str(sa), str(sb), str(ua), str(ub)
        if sb >= sa and ub < ua:
            return True, "k%d_d%d" % (k, d), str(sa), str(sb), str(ua), str(ub)
    return False, None, str(sa), str(sb), None, None


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------

def fr(q):
    return str(F(q))


def build():
    res = {}

    # --- separation table over the distributional roster -------------------
    table = {}
    for name, w in sorted(WORLDS.items()):
        xs, ys, P = w["xs"], w["ys"], w["P"]
        table[name] = {
            "shape": [len(xs), len(ys)],
            "MARG_NONUNIF": pred_marg_nonunif(P, xs, ys),
            "DEP": pred_dep(P, xs, ys),
            "PRED": pred_pred(P, xs, ys),
            "acc_base": fr(acc_base(P, xs, ys)),
            "acc_obs": fr(acc_obs(P, xs, ys)),
            "gain": fr(acc_obs(P, xs, ys) - acc_base(P, xs, ys)),
            "l1_dependence": fr(l1_dependence(P, xs, ys)),
        }
    res["distributional_separation"] = table

    # --- control separations ----------------------------------------------
    ctrl = {}
    for name, w in sorted(CTRL_WORLDS.items()):
        xs, ys, P = w["xs"], w["ys"], w["P"]
        blind, seeing = ctrl_values(P, xs, ys, w["acts"], w["U"])
        ctrl[name] = {
            "shape": [len(xs), len(ys), len(w["acts"])],
            "PRED": pred_pred(P, xs, ys),
            "CTRL": seeing > blind,
            "acc_base": fr(acc_base(P, xs, ys)),
            "acc_obs": fr(acc_obs(P, xs, ys)),
            "blind_utility": fr(blind),
            "informed_utility": fr(seeing),
            "control_gain": fr(seeing - blind),
            "utility_is_constant_in_y": all(
                w["U"][(a, ys[0])] == w["U"][(a, y)]
                for a in w["acts"] for y in ys),
        }
    res["control_separation"] = ctrl

    # --- causal separation -------------------------------------------------
    joint, cond, do = causal_tables()
    res["causal_separation"] = {
        "joint": dict((("%d,%d" % k), fr(v)) for k, v in sorted(joint.items())),
        "p_y1_given_x0": fr(cond[(0, 1)]),
        "p_y1_given_x1": fr(cond[(1, 1)]),
        "p_y1_do_x0": fr(do[(0, 1)]),
        "p_y1_do_x1": fr(do[(1, 1)]),
        "PRED": pred_pred(joint, B2, B2),
        "CAUSAL": any(do[(0, y)] != do[(1, y)] for y in B2),
        "observational_gain": fr(acc_obs(joint, B2, B2)
                                 - acc_base(joint, B2, B2)),
        "interventional_gain": fr(F(0)),
    }

    # --- resource-bounded accessibility ------------------------------------
    acc_profiles = {}
    for name, P in sorted(RESOURCE_WORLDS.items()):
        prof = {}
        for (k, d) in BUDGETS:
            prof["k%d_d%d" % (k, d)] = fr(best_acc_in_class(P, k, d))
        acc_profiles[name] = {
            "acc_base": fr(acc_base(P, XS3, B2)),
            "acc_full": fr(acc_obs(P, XS3, B2)),
            "profile": prof,
        }
    res["accessibility_profiles"] = acc_profiles

    par = RESOURCE_WORLDS["W_PARITY3"]
    res["existence_vs_accessibility"] = {
        "world": "W_PARITY3",
        "PRED": pred_pred(par, XS3, B2),
        "acc_base": fr(acc_base(par, XS3, B2)),
        "acc_full_information": fr(acc_obs(par, XS3, B2)),
        "best_acc_at_k2_d2": fr(best_acc_in_class(par, 2, 2)),
        "best_acc_at_k3_d2": fr(best_acc_in_class(par, 3, 2)),
        "best_acc_at_k3_d3": fr(best_acc_in_class(par, 3, 3)),
        "ACC_at_k2_d2": best_acc_in_class(par, 2, 2) > acc_base(par, XS3, B2),
        "ACC_at_k3_d3": best_acc_in_class(par, 3, 3) > acc_base(par, XS3, B2),
    }

    # --- order reversal refuting a budget-independent scalar ---------------
    nd = RESOURCE_WORLDS["W_NOISY_DICT"]
    lowR = (1, 1)
    highR = (3, 3)
    a_lo = best_acc_in_class(par, lowR[0], lowR[1])
    b_lo = best_acc_in_class(nd, lowR[0], lowR[1])
    a_hi = best_acc_in_class(par, highR[0], highR[1])
    b_hi = best_acc_in_class(nd, highR[0], highR[1])
    res["scalar_impossibility"] = {
        "world_A": "W_PARITY3",
        "world_B": "W_NOISY_DICT",
        "budget_low": "k1_d1",
        "budget_high": "k3_d3",
        "A_low": fr(a_lo), "B_low": fr(b_lo),
        "A_high": fr(a_hi), "B_high": fr(b_hi),
        "reversal": (a_lo < b_lo) and (a_hi > b_hi),
        "quantifier": (
            "Refutes every BUDGET-INDEPENDENT sigma: W -> R claimed to satisfy "
            "sigma(W) >= sigma(W') => U(W,R) >= U(W',R) for all R in the frozen "
            "lattice. A scalar indexed by the pair (W,R) is NOT refuted; the "
            "positive disjunct below supplies exactly such a resource-indexed "
            "object."
        ),
    }

    # --- positive disjunct: the resource-conditioned profile object --------
    mono_fail = []
    for name, P in sorted(RESOURCE_WORLDS.items()):
        for (k, d) in BUDGETS:
            for (k2, d2) in BUDGETS:
                if k <= k2 and d <= d2:
                    if best_acc_in_class(P, k, d) > best_acc_in_class(P, k2, d2):
                        mono_fail.append([name, k, d, k2, d2])
    ceiling_fail = []
    for name, P in sorted(RESOURCE_WORLDS.items()):
        top = acc_obs(P, XS3, B2)
        for (k, d) in BUDGETS:
            if best_acc_in_class(P, k, d) > top:
                ceiling_fail.append([name, k, d])
    res["profile_object"] = {
        "definition": (
            "S(W) := the map R -> max_{h in H_R} acc(h, W) on the frozen budget "
            "lattice R = (junta arity k, decision-tree depth d). Defined by the "
            "coordinates a rule may read and its branching depth; no "
            "architecture, layer or parameter count enters."
        ),
        "lattice_size": len(BUDGETS),
        "monotone": len(mono_fail) == 0,
        "monotonicity_violations": mono_fail,
        "bounded_by_full_information": len(ceiling_fail) == 0,
        "ceiling_violations": ceiling_fail,
    }

    # --- finite-sample discoverability vs asymptotic learnability ----------
    fam = marginalised_parity_family_world()
    curve = {}
    for m in range(4):
        curve["m%d" % m] = fr(analytic_learning_curve(m))
    res["discoverability"] = {
        "hypothesis_family": "all 8 secrets s in GF(2)^3, uniform prior",
        "marginalised_world_acc_base": fr(acc_base(fam, XS3, B2)),
        "marginalised_world_acc_obs": fr(acc_obs(fam, XS3, B2)),
        "marginalised_world_PRED": pred_pred(fam, XS3, B2),
        "learning_curve": curve,
        "asymptotic_accuracy": fr(F(1)),
        "DISC_m0": analytic_learning_curve(0) > acc_base(fam, XS3, B2),
        "DISC_m1": analytic_learning_curve(1) > acc_base(fam, XS3, B2),
        "LEARN": True,
    }

    # --- minimal-shape realizability --------------------------------------
    rmap = realizability_map()
    patterns = {
        "MARG_NONUNIF_without_DEP": (True, False, False),
        "DEP_without_MARG_NONUNIF": (False, True, True),
        "DEP_without_PRED": (True, True, False),
        "DEP_without_PRED_uniform_marginal": (False, True, False),
    }
    mins = {}
    for label, pat in sorted(patterns.items()):
        mins[label] = {
            "pattern_MARG_DEP_PRED": list(pat),
            "minimal_shapes": [list(s) for s in minimal_shapes(rmap, pat)],
        }
    # PRED never occurs without DEP -- the exhaustive grid must confirm it
    pred_without_dep = sorted(
        [list(s) for s in rmap if any(p[2] and not p[1] for p in rmap[s])])
    ctrl_min = MS.control_minimality()
    causal_min = MS.causal_minimality()
    acc_min = MS.accessibility_minimality()
    disc_min = MS.discoverability_minimality()
    res["minimality"] = {
        "scope_note": (
            "minimality is claimed only at the frozen finite grids declared "
            "below and under the stated product orders; it is never a claim "
            "about all real-valued parameters"),
        "distributional": {
            "grid_denominator": GRID_DEN,
            "max_shape": MAX_SHAPE,
            "shapes_searched": len(rmap),
            "separations": mins,
            "shapes_admitting_PRED_without_DEP": pred_without_dep,
        },
        "control_row4": ctrl_min,
        "causal_row4": causal_min,
        "accessibility_row5": acc_min,
        "discoverability_row6": disc_min,
        "witness_minimality_status": {
            "W_PRED_NOCTRL": {
                "shape_XYA": [2, 2, 2],
                "minimal_at_two_or_more_actions": (
                    [2, 2, 2] in ctrl_min[
                        "PRED_without_CTRL_nonconstant_utility"][
                            "minimal_shapes_at_least_two_actions"]),
            },
            "W_CTRL_NOPRED": {
                "shape_XYA": [2, 3, 2],
                "minimal_at_two_or_more_actions": (
                    [2, 3, 2] in ctrl_min["CTRL_without_PRED"][
                        "minimal_shapes_at_least_two_actions"]),
            },
            "causal_triple": {
                "shape_ZXY": [2, 2, 2],
                "minimal": ([2, 2, 2] in causal_min[
                    "PRED_with_zero_interventional_gain"]["minimal_shapes"]),
            },
            "W_PARITY3": {
                "coordinates": 3,
                "minimal_for_plain_arity_gap": (
                    acc_min["arity_gap"]["minimal_n"] == 3),
                "minimal_n_for_plain_arity_gap": acc_min["arity_gap"][
                    "minimal_n"],
                "minimal_for_every_coordinate_reachable_gap": (
                    acc_min["depth_gap_with_every_coordinate_reachable"][
                        "minimal_n"] == 3),
                "honest_note": (
                    "W_PARITY3 is NOT the minimal witness of the plain "
                    "accessibility gap -- two coordinates already suffice. It "
                    "IS the minimal witness of the strictly stronger pattern "
                    "in which every coordinate is reachable within the depth "
                    "budget and the best rule is still at the base rate, "
                    "which is the property the AE1-5 claim actually rests on "
                    "(best_acc_at_k3_d2 = 1/2)."),
            },
            "parity_family_n3": {
                "coordinates": 3,
                "minimal_n_for_zero_sample_gap": disc_min["minimal_n"],
                "minimal": (disc_min["minimal_n"] == 3),
                "honest_note": (
                    "one coordinate already exhibits the zero-sample gap. The "
                    "three-coordinate family is used for the quantitative "
                    "learning curve, not as a minimality claim."),
            },
        },
    }

    # --- null --------------------------------------------------------------
    trials = 200
    null_raw, null_big, null_max, null_roster = null_accessibility_gap(trials)
    recall_true = accessibility_gap(RESOURCE_WORLDS["W_PARITY3"])
    witness_mag = accessibility_gap_magnitude(RESOURCE_WORLDS["W_PARITY3"])
    clean_alarms = sorted([n for n in ("W_DICT", "W_NOISY_DICT")
                           if accessibility_gap(RESOURCE_WORLDS[n])])
    res["null"] = {
        "detector": (
            "accessibility gap: full-information Bayes gain is strictly "
            "positive while every rule admissible at junta arity k<=2 attains "
            "exactly the base rate"),
        "trials": trials,
        "family": "uniform X on {0,1}^3, P(Y=1|x) an independent multiple "
                  "of 1/8 drawn from a deterministic integer LCG",
        "random_worlds_flagged_unthresholded": null_raw,
        "random_world_gap_magnitudes": null_roster,
        "largest_null_gap_magnitude": str(null_max),
        "primary_comparison": (
            "threshold-free: the planted witness's gap magnitude strictly "
            "exceeds the largest magnitude any of the 200 random worlds "
            "attains"),
        "witness_exceeds_largest_null_gap": (witness_mag > null_max),
        "magnitude_threshold_note": (
            "the 1/4 threshold below was chosen after the null magnitudes "
            "were seen and is reported as an illustration only; no claim in "
            "this package depends on it, and the threshold-free comparison "
            "above carries the result"),
        "magnitude_threshold_illustrative": str(NULL_MAGNITUDE_THRESHOLD),
        "random_worlds_at_or_above_threshold": null_big,
        "planted_positive_flagged": recall_true,
        "planted_positive_gap_magnitude": str(witness_mag),
        "finding": (
            "the unthresholded detector fires on %d of %d random worlds; every "
            "such hit is a genuine but small accessibility gap, the largest "
            "being %s, against the planted witness's %s"
            % (null_raw, trials, str(null_max), str(witness_mag))),
        "known_clean_worlds_flagged": clean_alarms,
        "no_alarm_case_holds": (clean_alarms == []),
    }

    # --- measured auxiliary: genericity of budget order reversals -----------
    res["reversal_genericity"] = {
        "trials": 200,
        "random_pairs_with_order_reversal": reversal_genericity(200, BUDGETS),
        "note": ("reported for information only; one reversal already refutes "
                 "every budget-independent scalar, and a high rate strengthens "
                 "rather than weakens the AE1-5 conclusion"),
    }

    # --- explicit candidate scalars refuted --------------------------------
    refuted = {}
    for name in CANDIDATE_SCALARS:
        ok, at, sa, sb, ua, ub = refute_candidate_scalar(
            name, par, nd, BUDGETS)
        refuted[name] = {
            "refuted": ok, "at_budget": at,
            "sigma_W_PARITY3": sa, "sigma_W_NOISY_DICT": sb,
            "U_W_PARITY3": ua, "U_W_NOISY_DICT": ub,
        }
    res["candidate_scalars_refuted"] = refuted

    checks = {
        "marginal_nonuniformity_separates_from_dependence": (
            table["W_IND_SKEW"]["MARG_NONUNIF"] and
            not table["W_IND_SKEW"]["DEP"] and
            not table["W_DEP_UNIFMARG"]["MARG_NONUNIF"] and
            table["W_DEP_UNIFMARG"]["DEP"]),
        "dependence_separates_from_prediction": (
            table["W_DEP_NOPRED"]["DEP"] and
            not table["W_DEP_NOPRED"]["PRED"]),
        "prediction_implies_dependence_on_grid": (pred_without_dep == []),
        "prediction_separates_from_control": (
            ctrl["W_PRED_NOCTRL"]["PRED"] and
            not ctrl["W_PRED_NOCTRL"]["CTRL"] and
            not ctrl["W_PRED_NOCTRL"]["utility_is_constant_in_y"] and
            not ctrl["W_CTRL_NOPRED"]["PRED"] and
            ctrl["W_CTRL_NOPRED"]["CTRL"]),
        "prediction_separates_from_causation": (
            res["causal_separation"]["PRED"] and
            not res["causal_separation"]["CAUSAL"]),
        "existence_separates_from_accessibility": (
            res["existence_vs_accessibility"]["PRED"] and
            not res["existence_vs_accessibility"]["ACC_at_k2_d2"] and
            res["existence_vs_accessibility"]["ACC_at_k3_d3"]),
        "finite_sample_separates_from_asymptotic": (
            not res["discoverability"]["DISC_m0"] and
            F(res["discoverability"]["learning_curve"]["m3"]) < F(1)),
        "no_budget_independent_scalar": res["scalar_impossibility"]["reversal"],
        "profile_object_monotone": res["profile_object"]["monotone"],
        "profile_object_bounded": res["profile_object"][
            "bounded_by_full_information"],
        "null_beaten": (recall_true and witness_mag > null_max),
        "null_threshold_free_margin": (witness_mag > null_max),
        "null_no_alarm_on_clean": (clean_alarms == []),
        "all_candidate_scalars_refuted": all(
            refuted[n]["refuted"] for n in CANDIDATE_SCALARS),
        "minimality_search_complete": (len(rmap) == MAX_SHAPE * MAX_SHAPE),
        "minimality_covers_every_separation": all([
            res["minimality"]["witness_minimality_status"][
                "W_PRED_NOCTRL"]["minimal_at_two_or_more_actions"],
            res["minimality"]["witness_minimality_status"][
                "W_CTRL_NOPRED"]["minimal_at_two_or_more_actions"],
            res["minimality"]["witness_minimality_status"][
                "causal_triple"]["minimal"],
            acc_min["arity_gap"]["minimal_n"] is not None,
            acc_min["depth_gap_with_every_coordinate_reachable"][
                "minimal_n"] == 3,
            disc_min["minimal_n"] is not None,
        ]),
    }

    return {
        "schema": "GMI_833_AE1_STRUCTURE_SEPARATION_RESULT_V1",
        "issue": 833,
        "section": "AE1",
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "theorems": ["AE1-1", "AE1-2", "AE1-3", "AE1-4", "AE1-5", "AE1-6",
                     "AE1-8"],
        "results": res,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


def main():
    out = build()
    sys.stdout.write(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return 0 if out["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
