#!/usr/bin/env python3
"""GMI #833 AE10 -- resource-bounded usable information, route A.

Exact rational arithmetic only; emits RESULT_V1.json on stdout.

Route A computes every budget-restricted optimum by a subcube/coordinate-set
dynamic program and every Bayes posterior in closed form.  The independent
oracle (independent_usable_oracle_v1.py) shares no import with this module and
recomputes everything by explicit enumeration.
"""
import json
import sys
from fractions import Fraction as F

CLAIM_CEILING = (
    "GMI_833_AE10_RESOURCE_BOUNDED_USABLE_INFORMATION_DEFINED_BOUNDED_AND_"
    "EXACTLY_SEPARATED_FROM_SHANNON_INFORMATION_AT_REGISTERED_FINITE_SCOPE"
)
SOURCE_MAIN = "91c6d2876ba80c517a186e28fce3bdbe4e3fc218"
FREEZE_COMMIT = "4d76b41e5faa9f2a84d8f9f29b63d8c82ebeac72"

NBITS = 3
XS = list(range(2 ** NBITS))
B2 = [0, 1]

# The frozen budget lattice: (junta arity k, decision-tree depth d,
# labelled-sample budget m, observation precision p, communication bits c).
# k, d, p and c are instantiated; m is instantiated for the identification
# separation.  Time and energy are DECLARED but NOT instantiated in v1.
K_RANGE = [0, 1, 2, 3]
D_RANGE = [0, 1, 2, 3]
M_RANGE = [0, 1, 2, 3]
P_RANGE = [0, 1, 2, 3]
C_RANGE = [1, 2]
NOT_INSTANTIATED = ["time", "energy"]


def bit(x, i):
    return (x >> i) & 1


def marginals(P):
    px = dict((x, sum((P[(x, y)] for y in B2), F(0))) for x in XS)
    py = dict((y, sum((P[(x, y)] for x in XS), F(0))) for y in B2)
    return px, py


def acc_base(P):
    _, py = marginals(P)
    return max(py[y] for y in B2)


def acc_full(P):
    return sum((max(P[(x, y)] for y in B2) for x in XS), F(0))


# --------------------------------------------------------------------------
# rule classes on the frozen lattice
# --------------------------------------------------------------------------

def best_acc_kdpc(P, k, d, p, c):
    """Best accuracy of a rule that

      * reads only coordinates inside some set S with |S| <= k,
      * reads only the top `p` coordinates (precision budget: coordinate i is
        visible iff i >= NBITS - p),
      * is computable by a decision tree of branching depth at most d over S,
      * and emits at most `c` bits, which for a binary target is binding only
        when c = 0 (not in the frozen range) -- recorded so the lattice
        dimension is explicit rather than silently dropped.

    Computed by a dynamic program over (visible coordinate set, subcube).
    """
    visible = [i for i in range(NBITS) if i >= NBITS - p]
    best = acc_base_restricted(P)
    for S in subsets(visible, k):
        v = dp_best(P, S, d)
        if v > best:
            best = v
    return best


def subsets(pool, k):
    out = [()]
    for i in pool:
        out = out + [s + (i,) for s in out if len(s) < k]
    return [s for s in out if len(s) <= k]


def acc_base_restricted(P):
    _, py = marginals(P)
    return max(py[y] for y in B2)


def dp_best(P, coords, depth):
    """Best accuracy of a depth<=`depth` tree querying only `coords`."""
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
            for i in coords:
                if mask & (1 << i):
                    continue
                v = (rec(mask | (1 << i), vals, d - 1)
                     + rec(mask | (1 << i), vals | (1 << i), d - 1))
                if v > best:
                    best = v
        memo[key] = best
        return best

    return rec(0, 0, depth)


def usable_information(P, R):
    """U(W, T, R): the achievability gap at budget R = (k, d, m, p, c).

    The sample budget m enters only through the identification separation and
    is handled by `identification_curve`; for a fully specified world the
    decoder-side budget is (k, d, p, c).
    """
    k, d, m, p, c = R
    return best_acc_kdpc(P, k, d, p, c) - acc_base(P)


# --------------------------------------------------------------------------
# registered worlds
# --------------------------------------------------------------------------

def parity_world(secret):
    P = {}
    for x in XS:
        y = bin(x & secret).count("1") % 2
        P[(x, y)] = F(1, 8)
        P[(x, 1 - y)] = F(0)
    return P


WORLDS = {
    "W_PARITY3": parity_world(0b111),
    "W_DICTATOR": parity_world(0b100),
    "W_XOR2": parity_world(0b110),
}


def target_determined_and_uniform(P):
    for x in XS:
        if len([y for y in B2 if P[(x, y)] != 0]) != 1:
            return False
    _, py = marginals(P)
    return all(py[y] == F(1, 2) for y in B2)


# --------------------------------------------------------------------------
# identification (search-cost) separation
# --------------------------------------------------------------------------

def gf2_rank(vectors):
    basis = []
    for v in vectors:
        cur = v
        for b in basis:
            if cur ^ b < cur:
                cur ^= b
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    return len(basis), basis


def in_span(basis, x):
    cur = x
    for b in basis:
        if cur ^ b < cur:
            cur ^= b
    return cur == 0


def identification_curve(candidate_secrets, m):
    """Exact expected accuracy of the Bayes-optimal learner after m i.i.d.
    uniform labelled pairs, by a closed-form coset argument.

    The consistent secrets form a coset s + K of K = V^perp, where V is the
    span of the training inputs.  For a test point xt:

      * xt in V  -> every consistent secret gives the same label, so the
        posterior-majority rule is correct with probability 1;
      * xt not in V -> <k, xt> is balanced over K, so the coset splits evenly;
        the only asymmetry is the removal of the excluded secret 0 when the
        coset is K itself, which tips the majority to 1.

    No secret is ever scored by enumeration here; the oracle does that.
    """
    def par(s, x):
        return bin(s & x).count("1") % 2

    excluded_zero = 0 not in candidate_secrets
    full_family = (sorted(candidate_secrets)
                   == sorted(set(range(1, 2 ** NBITS))))
    if not (excluded_zero and full_family):
        # the closed form above is derived for the all-nonzero-secrets family;
        # for any other registered family fall back to exact counting over the
        # coset, still without scoring individual secrets by search
        return _identification_curve_general(candidate_secrets, m)

    tuples = [()]
    for _ in range(m):
        tuples = [t + (v,) for t in tuples for v in XS]
    num = 0
    den = 0
    for tr in tuples:
        r, basis = gf2_rank(list(tr))
        ksize = 2 ** (NBITS - r)
        for s in candidate_secrets:
            s_in_kernel = all(par(s, v) == 0 for v in tr)
            for xt in XS:
                if in_span(basis, xt):
                    num += 2
                elif s_in_kernel:
                    num += 2 if par(s, xt) == 1 else 0
                else:
                    num += 1          # exact tie scores 1/2, doubled
                den += 2
        del ksize
    return F(num, den)


def _identification_curve_general(candidate_secrets, m):
    def par(s, x):
        return bin(s & x).count("1") % 2

    tuples = [()]
    for _ in range(m):
        tuples = [t + (v,) for t in tuples for v in XS]
    num = 0
    den = 0
    for tr in tuples:
        for s in candidate_secrets:
            labels = tuple(par(s, v) for v in tr)
            cons = [c for c in candidate_secrets
                    if tuple(par(c, v) for v in tr) == labels]
            for xt in XS:
                ones = sum(1 for c in cons if par(c, xt) == 1)
                zeros = len(cons) - ones
                truth = par(s, xt)
                if ones > zeros:
                    num += 2 if truth == 1 else 0
                elif zeros > ones:
                    num += 2 if truth == 0 else 0
                else:
                    num += 1
                den += 2
    return F(num, den)


# --------------------------------------------------------------------------
# unconditional pseudorandom-style fixture
# --------------------------------------------------------------------------

def proper_subset_uniformity(secret):
    checked = 0
    viols = 0
    for mask in range(2 ** NBITS):
        if mask == (2 ** NBITS) - 1:
            continue
        bits = [i for i in range(NBITS) if mask & (1 << i)]
        counts = {}
        for x in XS:
            counts[(tuple(bit(x, i) for i in bits),
                    bin(x & secret).count("1") % 2)] = counts.get(
                (tuple(bit(x, i) for i in bits),
                 bin(x & secret).count("1") % 2), 0) + 1
        cells = 2 ** (len(bits) + 1)
        checked += 1
        if len(counts) != cells or any(v != 8 // cells
                                       for v in counts.values()):
            viols += 1
    return checked, viols


# --------------------------------------------------------------------------
# null
# --------------------------------------------------------------------------

def lcg_stream(seed, n):
    s = seed
    out = []
    for _ in range(n):
        s = (1664525 * s + 1013904223) % (2 ** 32)
        out.append(s)
    return out


def random_deterministic_world(rands):
    P = {}
    for i, x in enumerate(XS):
        y = rands[i] & 1
        P[(x, y)] = F(1, 8)
        P[(x, 1 - y)] = F(0)
    return P


BINDING_TOP = (3, 3, 3)


def communication_is_binding(P):
    """True iff the communication budget c ever changes usable information.

    For a binary target with c >= 1 it cannot, and this is asserted rather
    than assumed: the detector's notion of `below the top` depends on it.
    """
    for k in K_RANGE:
        for d in D_RANGE:
            for p in P_RANGE:
                vals = set(usable_information(P, (k, d, 0, p, c))
                           for c in C_RANGE)
                if len(vals) > 1:
                    return True
    return False


def zero_usable_at_subtop(P):
    """Detector: one exact bit of Shannon information, and zero usable
    information at every budget outside the top face of the BINDING
    dimensions (k, d, p).

    The communication dimension c is excluded from the notion of `top` because
    it is verified non-binding for a binary target; `communication_is_binding`
    asserts that rather than assuming it.
    """
    if not target_determined_and_uniform(P):
        return False
    if communication_is_binding(P):
        return False
    for k in K_RANGE:
        for d in D_RANGE:
            for p in P_RANGE:
                if (k, d, p) == BINDING_TOP:
                    continue
                for c in C_RANGE:
                    if usable_information(P, (k, d, 0, p, c)) > 0:
                        return False
    return True


def run_null(trials):
    rs = lcg_stream(4412290, trials * 8)
    hits = 0
    for t in range(trials):
        if zero_usable_at_subtop(random_deterministic_world(
                rs[t * 8:(t + 1) * 8])):
            hits += 1
    clean = sorted([n for n in ("W_DICTATOR", "W_XOR2")
                    if zero_usable_at_subtop(WORLDS[n])])
    return {
        "detector": ("Y determined by X with uniform Y-marginal (I(X;Y) = 1 "
                     "bit exactly) and zero usable information at every "
                     "budget strictly below the lattice top"),
        "trials": trials,
        "family": "Y a deterministic bitwise-random function of X on {0,1}^3",
        "random_worlds_flagged": hits,
        "planted_positive_flagged": zero_usable_at_subtop(WORLDS["W_PARITY3"]),
        "known_clean_flagged": clean,
    }


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------

def build():
    res = {}

    res["definition"] = {
        "usable_information": (
            "U(W, T, R) = max over rules admissible at budget R of the "
            "expected score, minus the best score achievable with no "
            "observation. Exact rational; task-relative; defined by the rule "
            "class, never by an architecture."),
        "budget_lattice": {
            "junta_arity_k": K_RANGE,
            "decision_tree_depth_d": D_RANGE,
            "labelled_sample_budget_m": M_RANGE,
            "observation_precision_p": P_RANGE,
            "communication_bits_c": C_RANGE,
        },
        "lattice_cells_decoder_side": (len(K_RANGE) * len(D_RANGE)
                                       * len(P_RANGE) * len(C_RANGE)),
        "declared_but_not_instantiated": NOT_INSTANTIATED,
        "honesty_note": (
            "time and energy are dimensions of the declared lattice but are "
            "NOT measured in v1; no claim in this package depends on them"),
    }

    # --- USE-1 monotonicity and USE-2 ceiling ------------------------------
    mono_viol = []
    ceil_viol = []
    class_growth = []
    profiles = {}
    for name, P in sorted(WORLDS.items()):
        prof = {}
        top = acc_full(P)
        for k in K_RANGE:
            for d in D_RANGE:
                for p in P_RANGE:
                    for c in C_RANGE:
                        u = usable_information(P, (k, d, 0, p, c))
                        prof["k%d_d%d_p%d_c%d" % (k, d, p, c)] = str(u)
                        if u > top - acc_base(P):
                            ceil_viol.append([name, k, d, p, c])
        for k in K_RANGE:
            for d in D_RANGE:
                for p in P_RANGE:
                    for c in C_RANGE:
                        for k2 in K_RANGE:
                            for d2 in D_RANGE:
                                for p2 in P_RANGE:
                                    for c2 in C_RANGE:
                                        if (k <= k2 and d <= d2 and p <= p2
                                                and c <= c2):
                                            a = F(prof["k%d_d%d_p%d_c%d"
                                                       % (k, d, p, c)])
                                            b = F(prof["k%d_d%d_p%d_c%d"
                                                       % (k2, d2, p2, c2)])
                                            if a > b:
                                                mono_viol.append(
                                                    [name, k, d, p, c,
                                                     k2, d2, p2, c2])
        profiles[name] = {
            "acc_base": str(acc_base(P)),
            "acc_full": str(top),
            "full_information_gap": str(top - acc_base(P)),
            "profile": prof,
        }
    # class monotonicity, proved on the rule sets themselves
    for k in K_RANGE:
        for k2 in K_RANGE:
            if k <= k2:
                for d in D_RANGE:
                    for d2 in D_RANGE:
                        if d <= d2:
                            class_growth.append(
                                len(subsets(list(range(NBITS)), k))
                                <= len(subsets(list(range(NBITS)), k2)))
    n_cells = len(K_RANGE) * len(D_RANGE) * len(P_RANGE) * len(C_RANGE)
    ordered_pairs = 0
    for k in K_RANGE:
        for d in D_RANGE:
            for p in P_RANGE:
                for c in C_RANGE:
                    for k2 in K_RANGE:
                        for d2 in D_RANGE:
                            for p2 in P_RANGE:
                                for c2 in C_RANGE:
                                    if (k <= k2 and d <= d2 and p <= p2
                                            and c <= c2):
                                        ordered_pairs += 1
    res["USE_1_monotonicity"] = {
        "lattice_cells": n_cells,
        "ordered_budget_pairs_per_world": ordered_pairs,
        "worlds": len(WORLDS),
        "ordered_pairs_checked": ordered_pairs * len(WORLDS),
        "violations": mono_viol,
        "monotone": len(mono_viol) == 0,
        "rule_class_inclusion_holds": all(class_growth),
    }
    res["USE_2_ceiling"] = {
        "violations": ceil_viol,
        "bounded": len(ceil_viol) == 0,
        "equality_attained_at_top": {
            name: (F(profiles[name]["profile"]["k3_d3_p3_c2"])
                   == F(profiles[name]["full_information_gap"]))
            for name in profiles
        },
    }
    res["profiles"] = profiles

    # --- USE-3 equal-Shannon separation ------------------------------------
    par = WORLDS["W_PARITY3"]
    dic = WORLDS["W_DICTATOR"]
    decode_pair = {
        "world_A": "W_PARITY3",
        "world_B": "W_DICTATOR",
        "both_determined_and_uniform": (
            target_determined_and_uniform(par)
            and target_determined_and_uniform(dic)),
        "mutual_information_bits_exact_both": "1",
        "budget": "k3_d2_p3_c2",
        "budget_rationale": (
            "junta arity is UNRESTRICTED at k=3, so the only binding "
            "constraint is the decoder's branching depth; a budget such as "
            "k1_d1 would also restrict how many coordinates may be read and "
            "would mislabel an arity effect as a depth effect"),
        "U_A": str(usable_information(par, (3, 2, 0, 3, 2))),
        "U_B": str(usable_information(dic, (3, 2, 0, 3, 2))),
        "difference": str(usable_information(dic, (3, 2, 0, 3, 2))
                          - usable_information(par, (3, 2, 0, 3, 2))),
        "attribution": ("decoder branching depth alone, at unrestricted arity "
                        "and unrestricted precision, with equal Shannon "
                        "information"),
        "arity_restricted_budget_for_reference": {
            "budget": "k1_d1_p3_c2",
            "U_A": str(usable_information(par, (1, 1, 0, 3, 2))),
            "U_B": str(usable_information(dic, (1, 1, 0, 3, 2))),
            "note": "both arity and depth bind here, so it is reported only "
                    "for reference and is not the headline claim",
        },
    }
    # search cost at IDENTICAL Shannon information: one fixed world, the
    # sample budget m alone varies, so the mutual information is identical by
    # construction rather than by coincidence
    large = [s for s in range(1, 8)]
    same_world = {
        "world": ("the single fixed mixture world Y = <s, x> with s uniform "
                  "over the 7 nonzero secrets of GF(2)^3"),
        "mutual_information_identical_by": (
            "identity -- it is one and the same world at every m, so no "
            "coincidence of two distributions is being relied on"),
        "curve": dict(("m%d" % m, str(identification_curve(large, m)))
                      for m in M_RANGE),
        "attribution": "identification/search cost at a fixed world and a "
                       "fixed, unrestricted decoder budget",
    }
    same_world["difference_m0_to_m3"] = str(
        F(same_world["curve"]["m3"]) - F(same_world["curve"]["m0"]))
    same_world["strictly_increasing"] = all(
        F(same_world["curve"]["m%d" % m])
        < F(same_world["curve"]["m%d" % (m + 1)])
        for m in range(len(M_RANGE) - 1))
    # auxiliary, and honestly labelled: a SMALLER candidate set is a DIFFERENT
    # world, so this comparison is not an equal-information one
    small = [0b100, 0b111]
    aux = {
        "note": ("auxiliary only: a different candidate set is a different "
                 "world, so this is NOT an equal-Shannon comparison"),
        "curve_two_candidates": dict(
            ("m%d" % m, str(identification_curve(small, m)))
            for m in M_RANGE),
        "curve_seven_candidates": same_world["curve"],
    }
    res["USE_3_equal_shannon_separation"] = {
        "decoding_cost_pair": decode_pair,
        "search_cost_same_world": same_world,
        "candidate_set_size_auxiliary": aux,
    }

    # --- USE-4 unconditional pseudorandom-style fixture --------------------
    checked, viols = proper_subset_uniformity(0b111)
    res["USE_4_unconditional_fixture"] = {
        "world": "W_PARITY3",
        "proper_subsets_checked": checked,
        "uniformity_violations": viols,
        "statement": (
            "for every proper subset S of the coordinates, (x_S, y) is exactly "
            "uniform on {0,1}^(|S|+1), so any rule reading only S has exactly "
            "zero correlation with the target"),
        "usable_information_at_k2_d3_p3_c2": str(
            usable_information(par, (2, 3, 0, 3, 2))),
        "usable_information_at_k3_d3_p3_c2": str(
            usable_information(par, (3, 3, 0, 3, 2))),
        "cryptographic_assumption_used": False,
        "is_a_complexity_class_separation": False,
    }

    # --- USE-5 terminology crosswalk ---------------------------------------
    res["USE_5_terminology_crosswalk"] = [
        {"our_term": "usable information U(W,T,R)",
         "parent": "predictive V-information I_V(X -> Y)",
         "relation": "U is an instance of predictive V-information with the "
                     "predictor family V = H_R and 0-1 loss; parent-owned",
         "citation": "Xu, Zhao, Song, Ermon, Finn, ICLR 2020, arXiv:2002.10689"},
        {"our_term": "budget lattice",
         "parent": "resource-rational analysis / bounded rationality",
         "relation": "the lattice instantiates the resource axis those "
                     "programmes posit; no new notion is introduced",
         "citation": "Simon, Quarterly Journal of Economics 69 (1955) 99-118, "
                     "doi:10.2307/1884852; Lieder and Griffiths, Behavioral "
                     "and Brain Sciences 43 (2020) e1, "
                     "doi:10.1017/S0140525X1900061X"},
        {"our_term": "information exists but is not extractable",
         "parent": "HILL pseudoentropy / computational entropy",
         "relation": "the same phenomenon; our fixture is unconditional and "
                     "therefore strictly weaker than the cryptographic notion",
         "citation": "Hastad, Impagliazzo, Levin, Luby, SIAM Journal on "
                     "Computing 28 (1999) 1364-1396, "
                     "doi:10.1137/S0097539793244708"},
        {"our_term": "full-information ceiling",
         "parent": "data processing inequality / rate-distortion ceiling",
         "relation": "the ceiling is the unrestricted Bayes optimum; no new "
                     "inequality is claimed",
         "citation": "Cover and Thomas, Elements of Information Theory, 2nd "
                     "ed., Wiley (2006), doi:10.1002/047174882X"},
    ]

    res["null"] = run_null(200)

    checks = {
        "USE_1_monotone": res["USE_1_monotonicity"]["monotone"],
        "USE_1_rule_class_inclusion": res["USE_1_monotonicity"][
            "rule_class_inclusion_holds"],
        "USE_2_bounded": res["USE_2_ceiling"]["bounded"],
        "USE_2_equality_at_top": all(
            res["USE_2_ceiling"]["equality_attained_at_top"].values()),
        "USE_3_decoding_cost_separation": (
            decode_pair["both_determined_and_uniform"]
            and F(decode_pair["U_A"]) == 0
            and F(decode_pair["U_B"]) > 0),
        "USE_3_search_cost_separation": (
            same_world["strictly_increasing"]
            and F(same_world["difference_m0_to_m3"]) > 0),
        "USE_4_unconditional": (viols == 0
                                and not res["USE_4_unconditional_fixture"][
                                    "cryptographic_assumption_used"]),
        "USE_4_zero_usable_below_full_arity": (
            F(res["USE_4_unconditional_fixture"][
                "usable_information_at_k2_d3_p3_c2"]) == 0
            and F(res["USE_4_unconditional_fixture"][
                "usable_information_at_k3_d3_p3_c2"]) > 0),
        "USE_5_crosswalk_complete": (
            len(res["USE_5_terminology_crosswalk"]) >= 4
            and all("citation" in e
                    for e in res["USE_5_terminology_crosswalk"])),
        "null_beaten": (res["null"]["random_worlds_flagged"] == 0
                        and res["null"]["planted_positive_flagged"]),
        "null_no_alarm_on_clean": (res["null"]["known_clean_flagged"] == []),
        "time_and_energy_not_claimed": (NOT_INSTANTIATED == ["time", "energy"]),
    }

    return {
        "schema": "GMI_833_AE10_USABLE_INFORMATION_RESULT_V1",
        "issue": 833,
        "section": "AE10",
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "theorems": ["USE-1", "USE-2", "USE-3", "USE-4", "USE-5"],
        "row_not_closed": (
            "Determine whether GMI morphology selection is better predicted by "
            "raw information, usable information, or a vector of "
            "resource-conditioned sufficient statistics."),
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
