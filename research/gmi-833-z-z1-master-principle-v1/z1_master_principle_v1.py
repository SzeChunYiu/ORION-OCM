"""Route A -- the Marginal Value Principle IC-1, its corollaries, and exact
incompressibility separations (#833 Section Z, subsection Z1).

Route A builds every instance by explicit candidate enumeration and reads the
resource-error profile off the enumeration.  Route B
(independent_compression_oracle_v1.py) never enumerates the candidate sets: it
recomputes each profile from the closed forms the instance declares, rebuilds the
lower convex envelope by a different algorithm, and finds the separation groups
by sorting rather than by hashing.

Protocol is fixed by FREEZE_V1.md, committed before this file existed.

Stdlib only; exact integers and fractions.Fraction; no float in any claim.
Python 3.8 compatible.

Run:  python3 -I -B z1_master_principle_v1.py
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

ETAS = (1, 2, 3)
PGRID = tuple(Fraction(k, 8) for k in range(0, 9))
QGRID = (Fraction(1, 5), Fraction(1, 4), Fraction(1, 3), Fraction(1, 2),
         Fraction(2, 3), Fraction(3, 4), Fraction(4, 5))
ALPHAS = (2, 3, 4)


# ==================================================== enumerated primitives
def binary_stateless_delay_floor(q):
    """Exhaustive over the 16 two-mode stateless tables of the L=3 binary
    universe; returns the minimum expected delayed-channel error rate under
    i.i.d. Bernoulli(q) inputs, and the table count."""
    L = 3
    seqs = list(itertools.product((0, 1), repeat=L))
    w = []
    for s in seqs:
        pr = Fraction(1)
        for x in s:
            pr *= q if x == 1 else (1 - q)
        w.append(pr)
    best = None
    n = 0
    for table in range(16):
        n += 1
        err = Fraction(0)
        for si, s in enumerate(seqs):
            e = 0
            for t in (1, 2):
                if ((table >> (2 * 1 + s[t])) & 1) != s[t - 1]:
                    e += 1
            err += w[si] * Fraction(e, 2)
        if best is None or err < best:
            best = err
    return best, n


def alphabet_stateless_delay_floor(A):
    """Exhaustive over the A**(2A) two-mode stateless tables of the alphabet-A
    universe (Z5's 16 / 729 / 65536 counts); uniform i.i.d. symbols."""
    L = 3
    seqs = list(itertools.product(range(A), repeat=L))
    best = None
    n = 0
    # the delayed channel only reads (mode=1, cur); enumerate that A-vector and
    # multiply the count by A**A for the unused immediate half, as Z5 does.
    for tab in itertools.product(range(A), repeat=A):
        n += 1
        e = 0
        for s in seqs:
            for t in (1, 2):
                if tab[s[t]] != s[t - 1]:
                    e += 1
        r = Fraction(e, len(seqs) * 2)
        if best is None or r < best:
            best = r
    return best, n * (A ** A)


def ladder_profile():
    """The Z13 three-mode ladder floors, re-enumerated here independently."""
    L, WIN, MODES = 4, (2, 3), (0, 1, 2)
    SEQ = list(itertools.product((0, 1), repeat=L))
    NS = len(SEQ) * len(WIN)

    def floor(b, m):
        ns = 2 ** b
        na = ns * 2
        best = None
        for nxt in itertools.product(range(ns), repeat=na):
            tal = [[0, 0] for _ in range(na)]
            for s in SEQ:
                st = 0
                for t in range(L):
                    a = st * 2 + s[t]
                    if t in WIN:
                        tal[a][s[t - m]] += 1
                    st = nxt[a]
            e = sum(min(v) for v in tal)
            if best is None or e < best:
                best = e
        return Fraction(best, NS)

    return dict(((b, m), floor(b, m)) for b in (0, 1, 2) for m in MODES)


# ======================================================= the principle IC-1
def lower_convex_envelope(E):
    """Vertices of the lower convex envelope of {(k, E[k])}, by exact rational
    cross products (monotone chain over k = 0..K)."""
    ks = sorted(E)
    hull = []
    for k in ks:
        while len(hull) >= 2:
            (k1, y1), (k2, y2) = hull[-2], hull[-1]
            # drop k2 if it is on or above the segment k1 -> k
            if (y2 - y1) * (k - k1) >= (E[k] - y1) * (k2 - k1):
                hull.pop()
            else:
                break
        hull.append((k, E[k]))
    return hull


def marginals(E):
    """Delta_k along the envelope: the marginal error mass bought by unit k."""
    hull = lower_convex_envelope(E)
    d = {}
    for i in range(1, len(hull)):
        (k0, y0), (k1, y1) = hull[i - 1], hull[i]
        d[(k0, k1)] = (y0 - y1) / (k1 - k0)
    return hull, d


def argmin_budget(E, lam):
    best, arg = None, []
    for k in sorted(E):
        c = E[k] + lam * k
        if best is None or c < best:
            best, arg = c, [k]
        elif c == best:
            arg.append(k)
    return arg


# ============================================================== instances
def build_instances():
    """The declared union population.  Every profile comes from enumeration."""
    inst = []
    bin_floor = dict((q, binary_stateless_delay_floor(q)) for q in QGRID)
    alpha_floor = dict((A, alphabet_stateless_delay_floor(A)) for A in ALPHAS)
    for eta in ETAS:
        for p in PGRID:
            # UNIF: uniform binary inputs
            r0, ncand = bin_floor[Fraction(1, 2)]
            inst.append({"family": "UNIF", "eta": eta, "p": p, "q": Fraction(1, 2),
                         "A": 2, "R0": r0, "n_stateless_candidates": ncand,
                         "E": {0: eta * p * r0, 1: Fraction(0)}})
            for q in QGRID:
                r0, ncand = bin_floor[q]
                inst.append({"family": "SKEW", "eta": eta, "p": p, "q": q, "A": 2,
                             "R0": r0, "n_stateless_candidates": ncand,
                             "E": {0: eta * p * r0, 1: Fraction(0)}})
            for A in ALPHAS:
                r0, ncand = alpha_floor[A]
                inst.append({"family": "ALPHA", "eta": eta, "p": p, "q": Fraction(1, 2),
                             "A": A, "R0": r0, "n_stateless_candidates": ncand,
                             "E": {0: eta * p * r0, 1: Fraction(0)}})
    return inst


# ========================================== named laws under incompressibility
def law_threshold(i):
    """L_THRESHOLD: the selection threshold predicted for this instance."""
    _h, d = marginals(i["E"])
    return str(d.get((0, 1)))


def law_argmin_at(i, lam):
    return tuple(argmin_budget(i["E"], lam))


def law_argmin_profile(i):
    """L_ARGMIN_BUDGET: the winning budget on a fixed rational lambda ladder."""
    return tuple(law_argmin_at(i, Fraction(k, 8)) for k in range(0, 9))


def law_degeneracy(i):
    """L_DEGENERACY: how many stateless candidates the instance's grammar holds."""
    return i["n_stateless_candidates"]


def law_mdl(i):
    """L_MDL: grammar-induced description length -- bits needed to index one
    candidate of the instance's stateless table space."""
    n = i["n_stateless_candidates"]
    b = 0
    while (1 << b) < n:
        b += 1
    return b


def law_reach(i):
    """L_REACH: grammar-induced reachability -- the fraction of the stateless
    table space within one single-address edit of any given table."""
    A = i["A"]
    n = i["n_stateless_candidates"]
    # a table has 2A addresses, each with A-1 alternative values
    return str(Fraction(2 * A * (A - 1), n)) if n else "0"


def law_distinct(i):
    """L_DISTINCT: is the alphabet distinction cost-relevant at this instance?
    A Z4-style morphology distinction, evaluated on the instance."""
    return i["A"] > 2


LAWS = {"L_THRESHOLD": law_threshold,
        "L_ARGMIN_BUDGET": law_argmin_profile,
        "L_DEGENERACY": law_degeneracy,
        "L_MDL": law_mdl,
        "L_REACH": law_reach,
        "L_DISTINCT": law_distinct}


def main():
    res = {"schema": "GMI_833_Z1_MASTER_PRINCIPLE_RESULT_V1", "issue": 833,
           "subsection": "Z1", "route": "A"}

    # -------------------------------------------------- corollaries IC-1a..d
    cor = {}
    ok = True
    # IC-1a / IC-1c : binary, input law q
    bad = []
    for q in QGRID:
        r0, _n = binary_stateless_delay_floor(q)
        if r0 != min(q, 1 - q):
            bad.append(str(q))
        for eta in ETAS:
            for p in PGRID:
                E = {0: eta * p * r0, 1: Fraction(0)}
                _h, d = marginals(E)
                if d.get((0, 1)) != eta * p * r0:
                    bad.append("threshold@%s" % q)
    cor["IC_1c_lambda_star_eq_eta_p_R0"] = {"violations": bad, "holds": not bad}
    uq = binary_stateless_delay_floor(Fraction(1, 2))[0]
    cor["IC_1a_uniform_case_is_eta_p_over_2"] = {"R0_at_q_half": str(uq),
                                                 "holds": uq == Fraction(1, 2)}
    # IC-1b : alphabet
    ab = []
    counts = {}
    for A in ALPHAS:
        r0, n = alphabet_stateless_delay_floor(A)
        counts[str(A)] = n
        if r0 != Fraction(A - 1, A):
            ab.append(str(A))
        for eta in ETAS:
            for p in PGRID:
                E = {0: eta * p * r0, 1: Fraction(0)}
                _h, d = marginals(E)
                if d.get((0, 1)) != eta * p * Fraction(A - 1, A):
                    ab.append("threshold@A=%d" % A)
    cor["IC_1b_lambda_star_eq_eta_p_one_minus_one_over_A"] = {
        "violations": ab, "holds": not ab, "enumerated_table_counts": counts,
        "floors": dict((str(A), str(Fraction(A - 1, A))) for A in ALPHAS)}
    # IC-1d : the Z13 ladder
    Rl = ladder_profile()
    ladder_rows = []
    lvl_eq_marg = 0
    tot_rows = 0
    for eta in ETAS:
        for a in range(9):
            for b2 in range(9 - a):
                c = 8 - a - b2
                p = (Fraction(a, 8), Fraction(b2, 8), Fraction(c, 8))
                E = dict((k, eta * sum(p[m] * Rl[(k, m)] for m in (0, 1, 2)))
                         for k in (0, 1, 2))
                hull, d = marginals(E)
                # MVP: level 1 wins on a non-empty interval iff it is a hull vertex
                hull_ks = [k for (k, _y) in hull]
                lo = E[1] - E[2]
                hi = E[0] - E[1]
                nonempty = hi > lo
                if (1 in hull_ks) != nonempty:
                    ladder_rows.append({"eta": eta, "p": [str(x) for x in p],
                                        "hull": hull_ks, "nonempty": nonempty})
                tot_rows += 1
                # clause 3: level != marginal on the delay-2 channel
                if eta * p[2] * Rl[(1, 2)] == hi:
                    lvl_eq_marg += 1
    cor["IC_1d_ladder"] = {
        "floors": dict(("b%d_m%d" % (b, m), str(Rl[(b, m)]))
                       for b in (0, 1, 2) for m in (0, 1, 2)),
        "worlds": tot_rows,
        "envelope_vs_interval_disagreements": len(ladder_rows),
        "holds": len(ladder_rows) == 0,
        "worlds_where_the_bare_level_formula_eta_p2_R0_matches_the_marginal": lvl_eq_marg,
        "clause3_level_is_not_marginal_witness":
            "R0(delay2|b=1) = %s but the marginal is %s"
            % (Rl[(1, 2)], Rl[(0, 2)] - Rl[(1, 2)])}
    ok = all(v.get("holds", True) for v in cor.values())
    res["corollaries"] = cor
    res["IC_1_all_corollaries_hold"] = ok

    # ------------------------------------------- incompressibility separations
    inst = build_instances()
    res["population"] = {"n_instances": len(inst),
                         "families": sorted(set(i["family"] for i in inst)),
                         "declared": "eta in {1,2,3} x p in k/8 (k=0..8) x "
                                     "{UNIF} + {SKEW over 7 input laws} + {ALPHA over A in 2,3,4}"}
    groups_all = {}
    for idx, i in enumerate(inst):
        key = (str(i["E"][0]), str(i["E"][1]), i["eta"])
        groups_all.setdefault(key, []).append(idx)
    # FREEZE_V1_AMENDMENT_1: the separation population is the NON-DEGENERATE slice
    nondeg = [idx for idx, i in enumerate(inst) if i["E"][0] > i["E"][1]]
    groups = {}
    for idx in nondeg:
        i = inst[idx]
        key = (str(i["E"][0]), str(i["E"][1]), i["eta"])
        groups.setdefault(key, []).append(idx)
    shared = dict((k, v) for k, v in groups.items() if len(v) > 1)
    shared_all = dict((k, v) for k, v in groups_all.items() if len(v) > 1)
    res["nonvacuity"] = {
        "separation_population": "non-degenerate instances only (E(0) > E(1)), per "
                                 "FREEZE_V1_AMENDMENT_1",
        "n_instances_all": len(inst),
        "n_instances_nondegenerate": len(nondeg),
        "n_profile_groups": len(groups),
        "n_groups_with_more_than_one_instance": len(shared),
        "n_instances_in_shared_groups": sum(len(v) for v in shared.values()),
        "largest_group": max(len(v) for v in groups.values()),
        "full_population_n_profile_groups": len(groups_all),
        "full_population_n_shared_groups": len(shared_all),
        "W_NONVACUITY_holds": len(shared) > 0}

    sep = {}
    for name, fn in LAWS.items():
        witness = None
        n_split = 0
        for key, idxs in sorted(shared.items()):
            vals = {}
            for j in idxs:
                vals.setdefault(fn(inst[j]), []).append(j)
            if len(vals) > 1:
                n_split += 1
                if witness is None:
                    vk = sorted(vals, key=lambda x: str(x))
                    a = inst[vals[vk[0]][0]]
                    b = inst[vals[vk[1]][0]]
                    witness = {
                        "profile": {"E0": key[0], "E1": key[1], "eta": key[2]},
                        "instance_A": {"family": a["family"], "eta": a["eta"],
                                       "p": str(a["p"]), "q": str(a["q"]), "A": a["A"],
                                       "law_value": str(fn(a))},
                        "instance_B": {"family": b["family"], "eta": b["eta"],
                                       "p": str(b["p"]), "q": str(b["q"]), "A": b["A"],
                                       "law_value": str(fn(b))}}
        sep[name] = {"n_shared_profile_groups_split": n_split,
                     "MVP_compressible": n_split == 0,
                     "separation_witness": witness}
    res["incompressibility"] = sep
    res["incompressible_laws"] = sorted(k for k, v in sep.items() if not v["MVP_compressible"])
    res["compressible_laws"] = sorted(k for k, v in sep.items() if v["MVP_compressible"])
    res["W_NOALARM_holds"] = len(res["compressible_laws"]) > 0

    # ------------------------------------------------ compression metrics
    # one cell per (instance, adjacent-threshold-pair): each 2-level instance has
    # exactly one adjacent pair; each ladder world has two.
    cells_pop = len(inst)
    cells_ladder = tot_rows * 2
    cells = cells_pop + cells_ladder
    bag = {
        "lambda_star_eq_eta_p_over_2": {"dof": 1, "scope": "A=2 and q=1/2 only"},
        "lambda_star_eq_eta_p_one_minus_one_over_A": {"dof": 1, "scope": "uniform inputs only"},
        "lambda_star_eq_eta_p_R0": {"dof": 1, "scope": "two levels only"},
        "Z13P1_two_price_ladder": {"dof": 2, "scope": "three levels, level-valued"},
    }
    res["compression"] = {
        "cell_rule": "one cell per (instance, adjacent-threshold-pair)",
        "independent_predictions": cells,
        "IC_1_free_theoretical_dof": 0,
        "IC_1_constants": [],
        "bag_of_laws_members": len(bag),
        "bag_free_theoretical_dof": sum(v["dof"] for v in bag.values()),
        "raw_pair_IC_1": [cells, 0],
        "raw_pair_bag": [cells, sum(v["dof"] for v in bag.values())],
        "ratio_note": "IC-1's dof is 0, so the ratio is not finite; the raw pair is "
                      "the reported quantity and the ratio is reported only for the bag",
        "bag_ratio": str(Fraction(cells, sum(v["dof"] for v in bag.values()))),
    }

    # ----- row 4: classify every constant in each registered closed form
    consts = {
        "1/2 in lambda* = eta*p/2": "COMPUTED_VALUE_OF_E: the uniform binary stateless "
                                    "delayed floor, enumerated over 16 tables",
        "1 - 1/A in lambda*(A)": "COMPUTED_VALUE_OF_E: the alphabet-A stateless floor, "
                                 "enumerated over A**(2A) tables",
        "R0 in lambda* = eta*p*R0": "COMPUTED_VALUE_OF_E: the stateless floor under the "
                                    "declared input law",
        "eta, p, lambda, q, A": "ENVIRONMENT_DECLARED",
        "the 5/16 level in Z13-P1's upper threshold": "ARBITRARY_UNDER_IC_1: it is a level, "
                                                      "not a marginal, and IC-1 forbids it",
    }
    res["constants_classification"] = consts
    res["arbitrary_constants_remaining"] = [k for k, v in consts.items()
                                            if v.startswith("ARBITRARY")]

    # ----- row 6: head-to-head against the bag
    def bag_predict(i, member):
        if member == "lambda_star_eq_eta_p_over_2":
            return i["eta"] * i["p"] * Fraction(1, 2)
        if member == "lambda_star_eq_eta_p_one_minus_one_over_A":
            return i["eta"] * i["p"] * Fraction(i["A"] - 1, i["A"])
        if member == "lambda_star_eq_eta_p_R0":
            return i["eta"] * i["p"] * i["R0"]
        return None

    truth = {}
    for i in inst:
        _h, d = marginals(i["E"])
        truth[id(i)] = d.get((0, 1))
    head = {}
    for member in ("lambda_star_eq_eta_p_over_2",
                   "lambda_star_eq_eta_p_one_minus_one_over_A",
                   "lambda_star_eq_eta_p_R0"):
        c = sum(1 for i in inst if bag_predict(i, member) == truth[id(i)])
        head[member] = "%d/%d" % (c, len(inst))
    head["IC_1_two_level"] = ("%d/%d TAUTOLOGICAL_AT_TWO_LEVELS: with E(1)=0 the marginal "
                              "and the level coincide, so this cell carries no weight; the "
                              "load-bearing comparison is the ladder below"
                              % (len(inst), len(inst)))
    # the ladder slice, where the bag's ladder member is the Z13-P1 closed form
    lad_ic = 0
    lad_bag = 0
    lad_n = 0
    for eta in ETAS:
        for a in range(9):
            for b2 in range(9 - a):
                c = 8 - a - b2
                p = (Fraction(a, 8), Fraction(b2, 8), Fraction(c, 8))
                E = dict((k, eta * sum(p[m] * Rl[(k, m)] for m in (0, 1, 2)))
                         for k in (0, 1, 2))
                hi = E[0] - E[1]
                lad_n += 1
                if eta * (p[1] * (Rl[(0, 1)] - Rl[(1, 1)])
                          + p[2] * (Rl[(0, 2)] - Rl[(1, 2)])) == hi:
                    lad_ic += 1
                if eta * p[2] * Rl[(1, 2)] + eta * p[1] * Rl[(0, 1)] == hi:
                    lad_bag += 1
    head["IC_1_on_ladder"] = "%d/%d" % (lad_ic, lad_n)
    head["Z13P1_two_price_ladder_on_ladder"] = "%d/%d" % (lad_bag, lad_n)
    res["head_to_head"] = head

    # ------------------------------------------------------------ hostiles
    host = {}
    # concave profile: the envelope must drop the interior level
    Ec = {0: Fraction(1), 1: Fraction(9, 10), 2: Fraction(0)}
    hull_c = [k for (k, _y) in lower_convex_envelope(Ec)]
    host["concave_profile_interior_level_dropped"] = {
        "detected": 1 not in hull_c, "hull": hull_c}
    # upper hull instead of lower: must change the vertex set somewhere
    Ev = {0: Fraction(1), 1: Fraction(1, 4), 2: Fraction(0)}
    hull_v = [k for (k, _y) in lower_convex_envelope(Ev)]
    host["convex_profile_interior_level_kept"] = {"detected": 1 in hull_v, "hull": hull_v}
    # level-instead-of-marginal, on the ladder
    host["level_instead_of_marginal"] = {
        "detected": Rl[(1, 2)] != Rl[(0, 2)] - Rl[(1, 2)],
        "level": str(Rl[(1, 2)]), "marginal": str(Rl[(0, 2)] - Rl[(1, 2)])}
    # grouping key stripped of eta: profiles must then collide across eta
    g2 = {}
    for idx, i in enumerate(inst):
        g2.setdefault((str(i["E"][0]), str(i["E"][1])), []).append(idx)
    host["profile_key_without_eta_overmerges"] = {
        "detected": len(g2) != len(groups_all), "groups_with_eta": len(groups_all),
        "groups_without_eta": len(g2)}
    # a law that is a pure function of the profile must never split a group
    host["planted_compressible_law_does_not_split"] = {
        "detected": sep["L_THRESHOLD"]["n_shared_profile_groups_split"] == 0}
    # a law that is a pure function of a NON-profile field must split some group
    host["planted_incompressible_law_splits"] = {
        "detected": sep["L_DEGENERACY"]["n_shared_profile_groups_split"] > 0}
    res["hostiles"] = host
    res["hostiles_all_detected"] = all(v["detected"] for v in host.values())

    # ---------------------------------------------------------------- null
    # Exhaustive rather than sampled: every law in the declared two-parameter
    # family is scored against the enumeration, and the null question is how many
    # of them the data cannot tell apart from IC-1.  A sampled null that happened
    # to contain the true law would report a meaningless "perfect null".
    GR = [Fraction(k, 16) for k in range(17)]
    perfect_2lvl = []
    best_2lvl = 0
    for a in GR:
        for bq in GR:
            cnt = 0
            for i in inst:
                if i["eta"] * i["p"] * (a + bq * i["R0"]) == truth[id(i)]:
                    cnt += 1
            best_2lvl = max(best_2lvl, cnt)
            if cnt == len(inst):
                perfect_2lvl.append((str(a), str(bq)))
    # the same identification test on the ladder slice, where level != marginal
    perfect_lad = []
    best_lad = 0
    lad_truth = []
    for eta in ETAS:
        for a2 in range(9):
            for b2 in range(9 - a2):
                c = 8 - a2 - b2
                p = (Fraction(a2, 8), Fraction(b2, 8), Fraction(c, 8))
                E = dict((k, eta * sum(p[m] * Rl[(k, m)] for m in (0, 1, 2)))
                         for k in (0, 1, 2))
                lad_truth.append((eta, p, E[0] - E[1]))
    for a in GR:
        for bq in GR:
            cnt = 0
            for (eta, p, hi) in lad_truth:
                if eta * (a * p[1] + bq * p[2]) == hi:
                    cnt += 1
            best_lad = max(best_lad, cnt)
            if cnt == len(lad_truth):
                perfect_lad.append((str(a), str(bq)))
    res["null"] = {
        "description": "exhaustive over the declared two-parameter law families: "
                       "eta*p*(a + b*R0) on the %d two-level instances and "
                       "eta*(a*p1 + b*p2) on the %d ladder worlds, a,b in k/16"
                       % (len(inst), len(lad_truth)),
        "n_laws_scored": len(GR) ** 2,
        "two_level_best": "%d/%d" % (best_2lvl, len(inst)),
        "two_level_laws_scoring_perfect": perfect_2lvl,
        "ladder_best": "%d/%d" % (best_lad, len(lad_truth)),
        "ladder_laws_scoring_perfect": perfect_lad,
        "IC_1_ladder_coefficients": [str(Rl[(0, 1)] - Rl[(1, 1)]),
                                     str(Rl[(0, 2)] - Rl[(1, 2)])],
        "Z13P1_ladder_coefficients": [str(Rl[(0, 1)]), str(Rl[(1, 2)])],
        "identified": len(perfect_2lvl) == 1 and len(perfect_lad) == 1,
        "note": "IC-1 is IDENTIFIED inside each family: exactly one law in each grid "
                "reproduces the enumeration, and it is IC-1's marginal pair."}

    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True, default=str)
        f.write("\n")
    print(json.dumps({"IC_1_all_corollaries_hold": res["IC_1_all_corollaries_hold"],
                      "incompressible": res["incompressible_laws"],
                      "compressible": res["compressible_laws"],
                      "nonvacuity": res["nonvacuity"],
                      "head_to_head": head,
                      "compression": res["compression"]["raw_pair_IC_1"],
                      "hostiles": res["hostiles_all_detected"],
                      "null_two_level": res["null"]["two_level_laws_scoring_perfect"],
                      "null_ladder": res["null"]["ladder_laws_scoring_perfect"],
                      "identified": res["null"]["identified"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
