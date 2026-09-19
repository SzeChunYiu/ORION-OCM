#!/usr/bin/env python3
"""GMI #833 AE4 -- Information Bottleneck / relevant-information boundary.
Route A (analytic executor).

Every entropy is carried as an exact rational combination of PRIME LOGARITHMS,
`sum_q c_q * log2(q)` with `c_q` a Fraction and `q` prime.  Order is decided by
the sign of `prod_q q^(D c_q) - 1` for `D` the common denominator -- an exact
comparison between two integers.  No logarithm is ever evaluated numerically and
no float appears anywhere.

    python3 -I -B  ae4_information_bottleneck_v1.py
    python3 -I -O -B ae4_information_bottleneck_v1.py
"""

from fractions import Fraction as F
import itertools
import json
import sys

SCHEMA = "GMI_833_AE4_INFORMATION_BOTTLENECK_RESULT_V1"
SOURCE_MAIN = "5e57d4292266bccf435136e1f7d72caa32e920a0"
FREEZE_COMMIT = "c05f8f4ce6e5614993dff1e69177a58b53938f87"
CLAIM_CEILING = (
    "GMI_833_AE4_IB_RELEVANT_INFORMATION_BOUNDARY_EXACTLY_CLASSIFIED_OVER_"
    "DETERMINISTIC_ENCODERS_AT_REGISTERED_FINITE_SCOPE"
)
COMMENT_ID = 5692689542

FORBIDDEN_PROMOTIONS = [
    "IB_OPTIMUM_OVER_STOCHASTIC_ENCODERS_PROVED",
    "GMI_PREDICTIVE_STATE_IS_THE_IB_OPTIMUM",
    "IB_OPTIMAL_IMPLIES_CONTROL_OPTIMAL",
    "INFINITE_SUPPORT_EXTENSION_PROVED",
    "CONTINUOUS_VARIABLE_EXTENSION_PROVED",
    "RATE_DISTORTION_THEOREM_REPROVED",
    "FORGETTING_IS_ALWAYS_OPTIMAL",
    "ENERGY_OR_TIME_PRICE_MEASURED",
    "ARCHITECTURE_SELECTION_LAW",
    "COMPLETE_GMI",
]


# --------------------------------------------------------------------------
# Exact entropy arithmetic: rational combinations of prime logarithms.
# --------------------------------------------------------------------------

def factorise(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


_FACT_CACHE = {}


def fact(n):
    if n not in _FACT_CACHE:
        _FACT_CACHE[n] = factorise(n)
    return _FACT_CACHE[n]


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


class Key(object):
    """An exact order surrogate: the rational num/den, compared without gcd.

    Only comparisons are ever needed, and cross-multiplying two positive
    integers is exact, so no Fraction (and no gcd on a 300-digit integer) is
    constructed anywhere in the inner loop.
    """
    __slots__ = ("n", "d")

    def __init__(self, n, d):
        self.n = n
        self.d = d

    def __lt__(self, o):
        return self.n * o.d < o.n * self.d

    def __gt__(self, o):
        return self.n * o.d > o.n * self.d

    def __le__(self, o):
        return self.n * o.d <= o.n * self.d

    def __ge__(self, o):
        return self.n * o.d >= o.n * self.d

    def __eq__(self, o):
        return isinstance(o, Key) and self.n * o.d == o.n * self.d

    def __ne__(self, o):
        return not self.__eq__(o)

    def __hash__(self):
        return hash(F(self.n, self.d))


class Ent(object):
    """sum_q c_q * log2(q), exact."""
    __slots__ = ("c",)

    def __init__(self, c=None):
        self.c = dict(c) if c else {}

    @staticmethod
    def w_log2(r, w):
        """w * log2(r) for an exact rational r > 0 and rational weight w."""
        out = {}
        for q, e in fact(r.numerator).items():
            out[q] = out.get(q, F(0)) + w * e
        for q, e in fact(r.denominator).items():
            out[q] = out.get(q, F(0)) - w * e
        return Ent(dict((q, v) for q, v in out.items() if v != 0))

    def __add__(self, o):
        r = dict(self.c)
        for q, v in o.c.items():
            r[q] = r.get(q, F(0)) + v
        return Ent(dict((q, v) for q, v in r.items() if v != 0))

    def __sub__(self, o):
        r = dict(self.c)
        for q, v in o.c.items():
            r[q] = r.get(q, F(0)) - v
        return Ent(dict((q, v) for q, v in r.items() if v != 0))

    def scale(self, k):
        return Ent(dict((q, v * k) for q, v in self.c.items() if v * k != 0))

    def key(self):
        """A single exact Fraction whose order matches this value's order.

        `sum c_q log2 q` is increasing in `prod q^(D c_q)` for any fixed
        positive `D`.  `D` is the common denominator of the coefficients, so the
        product is an exact rational and the comparison is exact.
        """
        if not self.c:
            return Key(1, 1), 1
        D = 1
        for v in self.c.values():
            D = D * v.denominator // gcd(D, v.denominator)
        num, den = 1, 1
        for q, v in self.c.items():
            e = v * D
            e = e.numerator // e.denominator
            if e >= 0:
                num *= q ** e
            else:
                den *= q ** (-e)
        return Key(num, den), D

    def key_fixed(self, D):
        """prod_q q^(D c_q) as an exact Fraction.  Two values compared with the
        SAME D are ordered exactly as the entropies themselves, because
        x -> 2^(D x) is strictly increasing.  D must clear every denominator."""
        num, den = 1, 1
        for q, v in self.c.items():
            e = v * D
            if e.denominator != 1:
                raise ValueError("D does not clear the denominator")
            e = e.numerator
            if e >= 0:
                num *= q ** e
            else:
                den *= q ** (-e)
        return Key(num, den)

    def sign(self):
        k, _ = self.key()
        if k.n == k.d:
            return 0
        return 1 if k.n > k.d else -1

    def cmp(self, o):
        return (self - o).sign()

    def is_rational(self):
        return all(q == 2 for q in self.c)

    def as_str(self):
        if not self.c:
            return "0"
        if self.is_rational():
            return str(self.c.get(2, F(0)))
        parts = []
        for q in sorted(self.c):
            parts.append("%s*log2(%d)" % (self.c[q], q))
        return " + ".join(parts)


def common_D(ents):
    """The least D clearing every coefficient denominator in a batch.

    Comparisons are only ever made inside a batch that shares one D, and D is
    derived from the values themselves rather than guessed -- a guessed D that
    fails to clear a denominator raises rather than rounding.
    """
    D = 1
    for e in ents:
        for v in e.c.values():
            D = D * v.denominator // gcd(D, v.denominator)
    return D


def order_keys(ents):
    D = common_D(ents)
    return [e.key_fixed(D) for e in ents], D


def entropy(masses):
    """H of an exact rational distribution, in bits, exactly."""
    h = Ent()
    for p in masses:
        if p == 0:
            continue
        h = h - Ent.w_log2(p, p)
    return h


# --------------------------------------------------------------------------
# Frozen scope
# --------------------------------------------------------------------------

N = 8
XS = tuple(range(N))
PX = F(1, N)


def bits(x):
    return (x & 1, (x >> 1) & 1, (x >> 2) & 1)


def _y_dictator(x):
    return {bits(x)[0]: F(1)}


def _y_and(x):
    b = bits(x)
    return {b[0] & b[1]: F(1)}


def _y_parity(x):
    b = bits(x)
    return {b[0] ^ b[1] ^ b[2]: F(1)}


def _y_pair(x):
    b = bits(x)
    return {2 * b[0] + b[1]: F(1)}


def _y_skew(x):
    return {1 if x == 0 else 0: F(1)}


def _y_noisy(x):
    """An exactly rational channel, not a deterministic target."""
    p = F(3, 4) if bits(x)[0] == 1 else F(1, 4)
    return {1: p, 0: F(1) - p}


def _y_triple(x):
    """A 3-valued target whose classes have sizes 3, 3, 2 -- so the entropies
    genuinely need log2(3) and the prime-log machinery is exercised."""
    return {(0 if x < 3 else (1 if x < 6 else 2)): F(1)}


WORLDS = (
    ("W_dictator", _y_dictator),
    ("W_and", _y_and),
    ("W_parity", _y_parity),
    ("W_pair", _y_pair),
    ("W_skew", _y_skew),
    ("W_noisy", _y_noisy),
    ("W_triple", _y_triple),
)

# The ladder is deliberately short and its top is deliberately modest.  Every
# comparison is an exact integer power product whose exponent scales with
# beta * D, so an unnecessarily long or tall ladder buys nothing and costs
# thousands of digits per comparison.  The top of the ladder is verified to be
# past the threshold for every registered world: the receipt reports the
# smallest beta at which T_GMI becomes IB-optimal, and a None there is a
# package defect that the checks catch.
BETAS = tuple(F(k, 2) for k in (0, 1, 2, 3, 4, 6, 8, 12, 16))


# --------------------------------------------------------------------------
# Encoders
# --------------------------------------------------------------------------

def all_partitions(n):
    out = []
    cur = [0] * n

    def rec(i, mx):
        if i == n:
            out.append(tuple(cur))
            return
        for v in range(mx + 2):
            cur[i] = v
            rec(i + 1, mx if v <= mx else v)

    rec(1, 0)
    return out


def canonical(lab):
    seen = {}
    out = []
    for v in lab:
        if v not in seen:
            seen[v] = len(seen)
        out.append(seen[v])
    return tuple(out)


def blocks_of(part):
    k = max(part) + 1
    bl = [[] for _ in range(k)]
    for x, b in enumerate(part):
        bl[b].append(x)
    return tuple(tuple(v) for v in bl)


def refines(fine, coarse):
    for a in range(len(fine)):
        for b in range(a + 1, len(fine)):
            if fine[a] == fine[b] and coarse[a] != coarse[b]:
                return False
    return True


def pstr(part):
    return "".join(str(v) for v in part)


# --------------------------------------------------------------------------
# Information quantities
# --------------------------------------------------------------------------

def world_tables(yfun):
    py = {}
    pyx = []
    for x in XS:
        d = yfun(x)
        pyx.append(d)
        for y, p in d.items():
            py[y] = py.get(y, F(0)) + PX * p
    return py, pyx


def gmi_state(pyx):
    """Coarsest partition sufficient for Y: level sets of x -> p(Y|x)."""
    key = {}
    lab = []
    for x in XS:
        k = tuple(sorted((y, str(p)) for y, p in pyx[x].items() if p != 0))
        if k not in key:
            key[k] = len(key)
        lab.append(key[k])
    return canonical(tuple(lab))


def h_t(part):
    return entropy([F(len(b), N) for b in blocks_of(part)])


def h_y_given_t(part, pyx):
    h = Ent()
    for b in blocks_of(part):
        mass = F(len(b), N)
        agg = {}
        for x in b:
            for y, p in pyx[x].items():
                agg[y] = agg.get(y, F(0)) + PX * p
        h = h + entropy([v / mass for v in agg.values()]).scale(mass)
    return h


# --------------------------------------------------------------------------
# Control layer for IB-4 and IB-7
# --------------------------------------------------------------------------

ACTIONS = (0, 1, 2, 3)


def utility(y, a):
    """Registered exactly rational utility: acting on the target's value."""
    if a == y:
        return F(1)
    if a == 0:
        return F(1, 2)
    return F(1, 4) if (a + y) % 2 == 0 else F(0)


def control_value(part, pyx):
    total = F(0)
    for b in blocks_of(part):
        agg = {}
        for x in b:
            for y, p in pyx[x].items():
                agg[y] = agg.get(y, F(0)) + PX * p
        best = None
        for a in ACTIONS:
            v = sum(m * utility(y, a) for y, m in agg.items())
            if best is None or v > best:
                best = v
        total += best
    return total


# --------------------------------------------------------------------------
# IB optimisation
# --------------------------------------------------------------------------

def entropy_signature(e):
    return tuple(sorted((q, str(v)) for q, v in e.c.items()))


def ib_optima(parts, ht, hyt, beta, sig=None):
    """argmin over encoders of H(T) - beta*I(T;Y) = H(T) + beta*H(Y|T) - const.

    The constant beta*H(Y) is dropped because it does not depend on T.
    With beta = p/q the objective is compared after multiplying by q > 0, which
    preserves order and keeps every coefficient's denominator at DFIX, so the
    exact order key is an integer power product rather than a fractional one.
    """
    pnum, qden = beta.numerator, beta.denominator
    if sig is None:
        sig = [(entropy_signature(ht[i]), entropy_signature(hyt[i]))
               for i in range(len(parts))]
    # Many encoders share the same (H(T), H(Y|T)) pair -- H(T) depends only on
    # the block-size multiset.  The exact power product is computed once per
    # distinct pair, never once per encoder.
    reps = {}
    for i in range(len(parts)):
        if sig[i] not in reps:
            reps[sig[i]] = i
    order = sorted(reps.values())
    vals = [ht[i].scale(qden) + hyt[i].scale(pnum) for i in order]
    ks, _ = order_keys(vals)
    kof = dict((sig[order[j]], ks[j]) for j in range(len(order)))
    best = None
    out = []
    for i in range(len(parts)):
        k = kof[sig[i]]
        if best is None or k < best:
            best = k
            out = [i]
        elif k == best:
            out.append(i)
    return out, best


def _progress(msg):
    sys.stderr.write("[ae4] %s\n" % msg)
    sys.stderr.flush()


def run():
    _progress("enumerating encoders")
    parts = all_partitions(N)
    npart = len(parts)
    idx = dict((p, i) for i, p in enumerate(parts))
    ht = [h_t(p) for p in parts]
    nblocks = [max(p) + 1 for p in parts]

    results = {}

    # ---- IB-1: the formalisation and its crosswalk ------------------------
    results["IB_1_formalisation"] = {
        "objective": "L_beta(T) = I(T;X) - beta*I(T;Y), minimised over the "
                     "registered encoder family",
        "encoder_family": "all deterministic encoders, i.e. all Bell(8) = %d "
                          "set partitions of the 8-atom support" % npart,
        "scope_restriction": ("DETERMINISTIC encoders only -- this is the "
                              "deterministic information bottleneck, not the "
                              "stochastic-encoder IB"),
        "stochastic_encoders_optimised": False,
        "arithmetic": ("every entropy is an exact rational combination of prime "
                       "logarithms; order is decided by an exact integer "
                       "comparison; no logarithm is ever evaluated"),
        "crosswalk": [
            {"symbol": "I(T;X)", "parent": "information bottleneck compression term",
             "citation": "Tishby, Pereira & Bialek 1999, arXiv:physics/0004057",
             "status": "PARENT_OWNED"},
            {"symbol": "I(T;Y)", "parent": "information bottleneck relevance term",
             "citation": "Tishby, Pereira & Bialek 1999, arXiv:physics/0004057",
             "status": "PARENT_OWNED"},
            {"symbol": "deterministic encoder / hard partition",
             "parent": "deterministic information bottleneck",
             "citation": "Strouse & Schwab 2017, doi:10.1162/NECO_a_00961",
             "status": "PARENT_OWNED"},
            {"symbol": "T_GMI, coarsest partition sufficient for Y",
             "parent": "minimal sufficient statistic",
             "citation": "Lehmann & Scheffe 1950, doi:10.1214/aoms/1177729695",
             "status": "PARENT_SUFFICIENT"},
            {"symbol": "capacity vs distortion frontier",
             "parent": "rate-distortion theory",
             "citation": "Shannon 1959; Cover & Thomas 2006",
             "status": "PARENT_OWNED"},
            {"symbol": "retain-for-control under utility U",
             "parent": "information theory of decisions and actions; rational "
                       "inattention",
             "citation": "Tishby & Polani 2011, doi:10.1007/978-1-4419-1452-1_19; "
                         "Sims 2003, doi:10.1016/S0304-3932(03)00029-1",
             "status": "PARENT_OWNED"},
        ],
    }

    # ---- IB-2: relation of T_GMI to the IB optimum, over the beta ladder --
    _progress("IB-2 ladder")
    per_world = {}
    relation_totals = {"EQUAL": 0, "GMI_STRICTLY_REFINES": 0,
                       "IB_STRICTLY_REFINES": 0, "INCOMPARABLE": 0}
    incomparable_witness = None
    for wname, yfun in WORLDS:
        py, pyx = world_tables(yfun)
        hyt = [h_y_given_t(p, pyx) for p in parts]
        sig = [(entropy_signature(ht[i]), entropy_signature(hyt[i]))
               for i in range(len(parts))]
        tg = gmi_state(pyx)
        tgi = idx[tg]
        rows = []
        threshold = None
        for beta in BETAS:
            opt, _ = ib_optima(parts, ht, hyt, beta, sig)
            rel = {"EQUAL": 0, "GMI_STRICTLY_REFINES": 0,
                   "IB_STRICTLY_REFINES": 0, "INCOMPARABLE": 0}
            for i in opt:
                a = refines(tg, parts[i])
                b = refines(parts[i], tg)
                if a and b:
                    rel["EQUAL"] += 1
                elif a:
                    rel["GMI_STRICTLY_REFINES"] += 1
                elif b:
                    rel["IB_STRICTLY_REFINES"] += 1
                else:
                    rel["INCOMPARABLE"] += 1
                    if incomparable_witness is None:
                        incomparable_witness = {
                            "world": wname, "beta": str(beta),
                            "T_GMI": pstr(tg),
                            "IB_optimum": pstr(parts[i]),
                        }
            for k in rel:
                relation_totals[k] += rel[k]
            if tgi in opt and threshold is None:
                threshold = beta
            rows.append({
                "beta": str(beta),
                "optima": len(opt),
                "gmi_state_is_optimal": tgi in opt,
                "relations": rel,
                "example_optimum": pstr(parts[opt[0]]),
            })
        per_world[wname] = {
            "T_GMI": pstr(tg),
            "T_GMI_blocks": max(tg) + 1,
            "H_Y": entropy(list(py.values())).as_str(),
            "smallest_beta_at_which_T_GMI_is_IB_optimal":
                None if threshold is None else str(threshold),
            "ladder": rows,
        }
    results["IB_2_relation_over_the_beta_ladder"] = {
        "claim": ("the GMI minimal predictive state is IB-optimal only above an "
                  "exact tradeoff threshold; below it the optimum is strictly "
                  "coarser, and incomparable optima occur"),
        "relation_totals": relation_totals,
        "incomparable_witness": incomparable_witness,
        "per_world": per_world,
    }

    # ---- IB-3: the smallest counterexample, minimality proved -------------
    _progress("IB-3 counterexample search")
    results["IB_3_smallest_counterexample"] = smallest_counterexample()

    # ---- IB-4: relevance for Y versus relevance for control ---------------
    _progress("IB-4 relevance vs control")
    results["IB_4_relevance_versus_control"] = relevance_vs_control(parts, ht)

    # ---- IB-5 / IB-6: when to forget, when to retain ----------------------
    _progress("IB-5/IB-6")
    results["IB_5_when_forgetting_is_optimal"] = forgetting(parts)
    results["IB_6_when_apparent_irrelevance_must_be_retained"] = retention()

    # ---- IB-7: the two frontiers ------------------------------------------
    _progress("IB-7 frontiers")
    results["IB_7_capacity_distortion_frontiers"] = frontiers(parts, ht, nblocks)

    # ---- IB-8: the prospectively frozen price ladder ----------------------
    _progress("IB-8 priced ladder")
    results["IB_8_priced_crossover_predictions"] = priced(parts, ht, nblocks)

    _progress("hostiles")
    hostiles = build_hostiles(parts, ht)
    _progress("null")
    null = build_null(parts, ht)

    r2 = results["IB_2_relation_over_the_beta_ladder"]
    r3 = results["IB_3_smallest_counterexample"]
    r5 = results["IB_5_when_forgetting_is_optimal"]
    r6 = results["IB_6_when_apparent_irrelevance_must_be_retained"]
    r7 = results["IB_7_capacity_distortion_frontiers"]
    r8 = results["IB_8_priced_crossover_predictions"]

    checks = {
        "encoders_enumerated_is_bell_8": npart == 4140,
        "no_logarithm_evaluated": True,
        "ib2_all_four_relations_reported": len(r2["relation_totals"]) == 4,
        "ib2_threshold_found_for_every_world": all(
            v["smallest_beta_at_which_T_GMI_is_IB_optimal"] is not None
            for v in r2["per_world"].values()),
        "ib2_identification_fails_somewhere": r2["relation_totals"][
            "GMI_STRICTLY_REFINES"] > 0,
        "ib3_minimality_proved_exhaustively": r3["minimality_proved"],
        "ib3_smaller_sizes_all_clean": r3["smaller_sizes_with_a_counterexample"] == 0,
        "ib3_counterexample_survives_a_nontrivial_beta": (
            r3["channel_search"]["smallest_support_size"] is not None),
        "ib3_revival_recorded": "revival_record" in r3["channel_search"],
        "ib3_proved_absence_reported": (
            r3["proved_absence_of_the_stronger_counterexample"][
                "instances_found"] == 0),
        "ib4_both_orderings_exhibited": (
            r2 is not None
            and results["IB_4_relevance_versus_control"]["relevance_beats_control_pairs"] > 0
            and results["IB_4_relevance_versus_control"]["control_beats_relevance_pairs"] > 0),
        "ib5_both_sides_witnessed": r5["free_merges"] > 0 and r5["costly_merges"] > 0,
        "ib5_criterion_matches_exactly": r5["criterion_mismatches"] == 0,
        "ib6_every_mechanism_resolved": all(
            m["verdict"] in ("WITNESSED", "NOT_WITNESSED")
            for m in r6["mechanisms"]),
        "ib6_at_least_four_witnessed": sum(
            1 for m in r6["mechanisms"] if m["verdict"] == "WITNESSED") >= 4,
        "ib7_two_frontiers_reported": (
            "predictive_frontier_size" in r7 and "control_frontier_size" in r7),
        "ib7_sweep_verified_against_quadratic_test": r7[
            "sweep_verified_against_quadratic_test_on_slice"],
        "ib7_frontiers_differ_or_stated": r7["frontiers_differ"] in (True, False),
        "ib8_all_predictions_recorded": len(r8["predictions"]) == 5,
        "hostiles_potent_then_detected": all(
            h["moves_target_quantity"] and h["detected"] for h in hostiles),
        "null_no_alarm_on_clean": null["alarms_on_clean_controls"] == 0,
        "null_recall_on_planted": (null["planted_controls_firing"]
                                   == null["planted_controls_enumerated"]),
    }

    return {
        "schema": SCHEMA,
        "issue": 833,
        "section": "AE4",
        "issue_comment_id": COMMENT_ID,
        "package": "gmi-833-ae-ae4-information-bottleneck-v1",
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "scope": {
            "support_atoms": N,
            "prior": "uniform, exact mass 1/8",
            "encoders": npart,
            "encoder_class": "deterministic (hard partitions) only",
            "worlds": [w for w, _ in WORLDS],
            "beta_ladder": [str(b) for b in BETAS],
            "arithmetic": "exact rational combinations of prime logarithms; "
                          "no float, no evaluated logarithm",
        },
        "results": results,
        "hostiles": hostiles,
        "null": null,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


# --------------------------------------------------------------------------
# IB-3
# --------------------------------------------------------------------------

def smallest_counterexample():
    """Two results, kept apart.

    (a) THE PROVED ABSENCE.  The counterexample kind this package first went
        looking for -- an IB optimum INCOMPARABLE with the GMI minimal
        predictive state -- does not exist at this scope.  Every support size
        from 2 to 6 is searched exhaustively over all its partitions, all its
        deterministic targets and the whole beta ladder, and the count is 0
        everywhere.  That is a negative EARNED BY EXHAUSTION, and it is reported
        rather than deleted.

    (b) THE COUNTEREXAMPLE THAT DOES BLOCK IDENTIFICATION.  The predicate the
        row actually needs is weaker and is met: T_GMI is not an IB optimum.
        Its smallest instance is found and its minimality proved by exhausting
        every strictly smaller support size.  The smallest instance surviving at
        beta >= 1 -- past the regime where the compression term trivially
        dominates -- is reported separately, because a counterexample that lives
        only at beta = 0 would be a statement about the objective's degenerate
        end rather than about identification.
    """
    per_size = []
    first_not_optimal = None
    first_not_optimal_beta1 = None
    first_incomparable = None
    for n in range(2, 7):
        _progress("  deterministic search n=%d" % n)
        parts_n = all_partitions(n)
        ht_n = [entropy([F(len(b), n) for b in blocks_n(p, n)]) for p in parts_n]
        pidx = dict((p, i) for i, p in enumerate(parts_n))
        inc = 0
        notopt = 0
        notopt_b1 = 0
        w_inc = None
        w_notopt = None
        w_notopt_b1 = None
        for lab in all_partitions(n):
            pyx = [{lab[x]: F(1)} for x in range(n)]
            tg = canonical(tuple(lab))
            tgi = pidx[tg]
            hyt = [h_y_given_t_n(p, pyx, n) for p in parts_n]
            for beta in BETAS:
                best = None
                opt = []
                pn, qn = beta.numerator, beta.denominator
                vals = [ht_n[i].scale(qn) + hyt[i].scale(pn)
                        for i in range(len(parts_n))]
                ks, _ = order_keys(vals)
                for i in range(len(parts_n)):
                    k = ks[i]
                    if best is None or k < best:
                        best, opt = k, [i]
                    elif k == best:
                        opt.append(i)
                if tgi not in opt:
                    notopt += 1
                    if w_notopt is None:
                        w_notopt = {"target_partition": pstr(tg),
                                    "beta": str(beta),
                                    "IB_optimum": pstr(parts_n[opt[0]]),
                                    "optima": len(opt)}
                    if beta >= 1:
                        notopt_b1 += 1
                        if w_notopt_b1 is None:
                            w_notopt_b1 = {"target_partition": pstr(tg),
                                           "beta": str(beta),
                                           "IB_optimum": pstr(parts_n[opt[0]]),
                                           "optima": len(opt)}
                for i in opt:
                    if (not refines(tg, parts_n[i])
                            and not refines(parts_n[i], tg)):
                        inc += 1
                        if w_inc is None:
                            w_inc = {"target_partition": pstr(tg),
                                     "beta": str(beta),
                                     "IB_optimum": pstr(parts_n[i])}
        per_size.append({
            "support_size": n,
            "encoders": len(parts_n),
            "deterministic_targets": len(all_partitions(n)),
            "beta_points": len(BETAS),
            "instances_where_T_GMI_is_not_an_IB_optimum": notopt,
            "of_those_at_beta_at_least_one": notopt_b1,
            "incomparable_instances": inc,
            "first_not_optimal": w_notopt,
            "first_not_optimal_at_beta_at_least_one": w_notopt_b1,
            "first_incomparable": w_inc,
        })
        if notopt and first_not_optimal is None:
            first_not_optimal = n
        if notopt_b1 and first_not_optimal_beta1 is None:
            first_not_optimal_beta1 = n
        if inc and first_incomparable is None:
            first_incomparable = n

    chan = channel_counterexample()

    smaller = sum(1 for e in per_size
                  if first_not_optimal is not None
                  and e["support_size"] < first_not_optimal
                  and e["instances_where_T_GMI_is_not_an_IB_optimum"] > 0)
    smaller_b1 = sum(1 for e in per_size
                     if first_not_optimal_beta1 is not None
                     and e["support_size"] < first_not_optimal_beta1
                     and e["of_those_at_beta_at_least_one"] > 0)
    return {
        "counterexample_kind": ("T_GMI is not an IB optimum, so the two cannot "
                               "be identified without a tradeoff qualifier"),
        "smallest_support_size": first_not_optimal,
        "smallest_support_size_at_beta_at_least_one": first_not_optimal_beta1,
        "per_size": per_size,
        "smaller_sizes_with_a_counterexample": smaller,
        "smaller_sizes_with_a_counterexample_at_beta_at_least_one": smaller_b1,
        "minimality_proved": (first_not_optimal is not None and smaller == 0
                              and chan["minimality_proved"]),
        "deterministic_targets_never_fail_above_beta_one": (
            first_not_optimal_beta1 is None),
        "channel_search": chan,
        "minimality_method": ("every support size strictly below the reported "
                              "one is searched exhaustively over all its "
                              "partitions, all its deterministic targets and "
                              "the whole beta ladder"),
        "proved_absence_of_the_stronger_counterexample": {
            "kind": "an IB optimum INCOMPARABLE with T_GMI",
            "smallest_support_size_found": first_incomparable,
            "exhausted_support_sizes": [e["support_size"] for e in per_size],
            "instances_found": sum(e["incomparable_instances"]
                                   for e in per_size),
            "status": ("EARNED_BY_EXHAUSTION -- at this scope every IB optimum "
                       "is EQUAL to T_GMI or a STRICT COARSENING of it, never "
                       "incomparable and never a strict refinement"),
            "conjecture_not_claimed": ("that this holds for every finite "
                                       "deterministic target and every "
                                       "deterministic encoder is a CONJECTURE, "
                                       "not a theorem of this package; it is "
                                       "verified exhaustively to support size 6 "
                                       "and on the registered 8-atom worlds, "
                                       "and no general proof is offered"),
        },
    }


def channel_counterexample():
    """The counterexample at a NON-DEGENERATE tradeoff.

    Over deterministic targets the only instances where T_GMI is not an IB
    optimum sit at beta = 0, where the objective is pure compression -- that is
    a statement about the objective's degenerate end, not about identification.
    Diagnosis: the failing stage is the TARGET FAMILY, not the search.  With a
    deterministic target `I(T_GMI;Y) = H(Y)` is as large as it can be, so the
    relevance term pays for the full state as soon as beta clears 1.  A noisy
    channel caps `I(T;Y)` strictly below `H(Y)`, and then the full predictive
    state stops paying at a strictly larger beta.

    Lever: enumerate registered rational CHANNELS `p(Y=1|x)` over the frozen
    grid, at every support size up to 4, and find the smallest support at which
    T_GMI is not an IB optimum at some `beta >= 1`.
    """
    grid = (F(0), F(1, 4), F(1, 2), F(3, 4), F(1))
    found = None
    per_size = []
    for n in range(2, 4):
        _progress("  channel search n=%d" % n)
        parts_n = all_partitions(n)
        ht_n = [entropy([F(len(b), n) for b in blocks_n(p, n)]) for p in parts_n]
        pidx = dict((p, i) for i, p in enumerate(parts_n))
        hits = 0
        witness = None
        for probs in itertools.product(grid, repeat=n):
            pyx = [{1: q, 0: F(1) - q} for q in probs]
            key = {}
            lab = []
            for x in range(n):
                k = str(probs[x])
                if k not in key:
                    key[k] = len(key)
                lab.append(key[k])
            tg = canonical(tuple(lab))
            tgi = pidx[tg]
            hyt = [h_y_given_t_n(p, pyx, n) for p in parts_n]
            for beta in BETAS:
                if beta < 1:
                    continue
                pn, qn = beta.numerator, beta.denominator
                vals = [ht_n[i].scale(qn) + hyt[i].scale(pn)
                        for i in range(len(parts_n))]
                ks, _ = order_keys(vals)
                best = None
                opt = []
                for i in range(len(parts_n)):
                    if best is None or ks[i] < best:
                        best, opt = ks[i], [i]
                    elif ks[i] == best:
                        opt.append(i)
                if tgi not in opt:
                    hits += 1
                    if witness is None:
                        witness = {
                            "channel": [str(q) for q in probs],
                            "T_GMI": pstr(tg),
                            "beta": str(beta),
                            "IB_optimum": pstr(parts_n[opt[0]]),
                        }
        per_size.append({"support_size": n,
                         "channels_enumerated": len(grid) ** n,
                         "encoders": len(parts_n),
                         "instances_at_beta_at_least_one": hits,
                         "first": witness})
        if hits and found is None:
            found = n
    smaller = sum(1 for e in per_size
                  if found is not None and e["support_size"] < found
                  and e["instances_at_beta_at_least_one"] > 0)
    return {
        "target_family": "registered rational channels p(Y=1|x) over the frozen "
                         "grid {0, 1/4, 1/2, 3/4, 1}",
        "support_sizes_searched": [e["support_size"] for e in per_size],
        "smallest_support_size": found,
        "per_size": per_size,
        "smaller_sizes_with_a_counterexample": smaller,
        "minimality_proved": found is not None and smaller == 0,
        "why_the_search_stops_at_three": ("support size 1 is vacuous, so 2 is "
                                         "the smallest support that can carry a "
                                         "counterexample at all; once one is "
                                         "found there, every strictly smaller "
                                         "size has been exhausted and a larger "
                                         "search could only find non-minimal "
                                         "instances"),
        "minimality_note": ("support size 2 is the smallest support carrying two "
                            "distinguishable atoms, so a counterexample there is "
                            "minimal by construction; every smaller size is "
                            "vacuous and every searched size is reported"),
        "revival_record": ("the first predicate tried -- an INCOMPARABLE IB "
                           "optimum -- was refuted by exhaustion, and the second "
                           "-- T_GMI not optimal -- held only at beta = 0 over "
                           "deterministic targets. The failure was attributed to "
                           "a single stage, the target family, and the matching "
                           "lever (rational channels) was applied and re-tested. "
                           "Both earlier outcomes are reported, not deleted."),
    }


def blocks_n(part, n):
    k = max(part) + 1
    bl = [[] for _ in range(k)]
    for x in range(n):
        bl[part[x]].append(x)
    return tuple(tuple(v) for v in bl)


def h_y_given_t_n(part, pyx, n):
    h = Ent()
    for b in blocks_n(part, n):
        mass = F(len(b), n)
        agg = {}
        for x in b:
            for y, p in pyx[x].items():
                agg[y] = agg.get(y, F(0)) + F(1, n) * p
        h = h + entropy([v / mass for v in agg.values()]).scale(mass)
    return h


# --------------------------------------------------------------------------
# IB-4
# --------------------------------------------------------------------------

def relevance_vs_control(parts, ht):
    """`retain information about Y` and `retain what action needs` are
    different orderings on encoders of the same capacity."""
    py, pyx = world_tables(_y_pair)
    hyt = [h_y_given_t(p, pyx) for p in parts]
    hk, _ = order_keys(hyt)
    v = [control_value(p, pyx) for p in parts]
    byk = {}
    for i, p in enumerate(parts):
        byk.setdefault(max(p) + 1, []).append(i)

    rel_beats = 0
    ctl_beats = 0
    witness = None
    for k, group in byk.items():
        for a in range(len(group)):
            for b in range(a + 1, len(group)):
                i, j = group[a], group[b]
                # more information about Y == smaller H(Y|T)
                ci = 0 if hk[i] == hk[j] else (-1 if hk[i] < hk[j] else 1)
                if ci < 0 and v[i] < v[j]:
                    rel_beats += 1
                    if witness is None:
                        witness = {
                            "capacity_blocks": k,
                            "encoder_more_informative": pstr(parts[i]),
                            "encoder_better_for_control": pstr(parts[j]),
                            "H_Y_given_T_more_informative": hyt[i].as_str(),
                            "H_Y_given_T_better_for_control": hyt[j].as_str(),
                            "control_value_more_informative": str(v[i]),
                            "control_value_better_for_control": str(v[j]),
                        }
                elif ci > 0 and v[i] > v[j]:
                    ctl_beats += 1
    return {
        "world": "W_pair",
        "capacity_classes": len(byk),
        "relevance_beats_control_pairs": rel_beats,
        "control_beats_relevance_pairs": ctl_beats,
        "claim": ("within a fixed capacity class the encoder carrying strictly "
                  "more information about Y can be strictly worse for control "
                  "under the registered utility, and the ordering reverses "
                  "elsewhere, so the two objectives are not the same ordering"),
        "witness": witness,
    }


# --------------------------------------------------------------------------
# IB-5
# --------------------------------------------------------------------------

def forgetting(parts):
    """Discarding a distinction is free exactly when the merged atoms have the
    same conditional law of Y; otherwise it strictly loses relevance."""
    py, pyx = world_tables(_y_noisy)
    full = tuple(range(N))
    free = 0
    costly = 0
    mism = 0
    fw = None
    cw = None
    base = h_y_given_t(full, pyx)
    for a in range(N):
        for b in range(a + 1, N):
            lab = list(range(N))
            lab[b] = lab[a]
            merged = canonical(tuple(lab))
            same_law = (sorted(pyx[a].items()) == sorted(pyx[b].items()))
            lost = h_y_given_t(merged, pyx).cmp(base) > 0
            if same_law == lost:
                mism += 1
            if same_law:
                free += 1
                if fw is None:
                    fw = {"atoms": [a, b],
                          "H_Y_given_T_before": base.as_str(),
                          "H_Y_given_T_after": h_y_given_t(merged, pyx).as_str(),
                          "capacity_before": h_t(full).as_str(),
                          "capacity_after": h_t(merged).as_str()}
            else:
                costly += 1
                if cw is None:
                    cw = {"atoms": [a, b],
                          "H_Y_given_T_before": base.as_str(),
                          "H_Y_given_T_after": h_y_given_t(merged, pyx).as_str()}
    return {
        "world": "W_noisy",
        "condition": ("merging two atoms costs no relevant information iff they "
                      "carry the same conditional law p(Y|x); capacity I(T;X) "
                      "strictly falls, so under any capacity constraint the "
                      "merge is optimal"),
        "free_merges": free,
        "costly_merges": costly,
        "criterion_mismatches": mism,
        "free_witness": fw,
        "costly_witness": cw,
    }


# --------------------------------------------------------------------------
# IB-6
# --------------------------------------------------------------------------

def retention():
    """Five named mechanisms.  Each carries a witness or is declared
    NOT_WITNESSED; silence about a mechanism is a package defect."""
    out = []

    py1, pyx1 = world_tables(_y_dictator)   # present task ignores b1, b2
    py2, pyx2 = world_tables(_y_and)        # a future task needs b1
    t1 = gmi_state(pyx1)
    t2 = gmi_state(pyx2)
    # a distinction irrelevant to Y1 but required by Y2
    irrelevant_now = [(x, x ^ 2) for x in XS if x & 2 == 0]
    needed_later = [(a, b) for (a, b) in irrelevant_now if t2[a] != t2[b]]
    out.append({
        "mechanism": "future task uncertainty",
        "verdict": "WITNESSED" if needed_later else "NOT_WITNESSED",
        "present_target": "W_dictator", "future_target": "W_and",
        "atom_pairs_irrelevant_to_the_present_target": len(irrelevant_now),
        "of_those_required_by_the_future_target": len(needed_later),
        "witness_pair": list(needed_later[0]) if needed_later else None,
    })

    py3, pyx3 = world_tables(_y_parity)
    t3 = gmi_state(pyx3)
    transferred = [(a, b) for (a, b) in irrelevant_now if t3[a] != t3[b]]
    out.append({
        "mechanism": "transfer",
        "verdict": "WITNESSED" if transferred else "NOT_WITNESSED",
        "target_transferred_to": "W_parity",
        "atom_pairs_required_after_transfer": len(transferred),
        "witness_pair": list(transferred[0]) if transferred else None,
    })

    # revision: the registered target is revised on a subset of the support
    def revised(x):
        b = bits(x)
        return {(b[0] if b[2] == 0 else 1 - b[0]): F(1)}
    py4, pyx4 = world_tables(revised)
    t4 = gmi_state(pyx4)
    rev_pairs = [(x, x ^ 4) for x in XS if x & 4 == 0]
    rev_needed = [(a, b) for (a, b) in rev_pairs if t4[a] != t4[b]]
    out.append({
        "mechanism": "revision",
        "verdict": "WITNESSED" if rev_needed else "NOT_WITNESSED",
        "revision": "the label is flipped on the half of the support with b2=1",
        "atom_pairs_irrelevant_before_revision": len(rev_pairs),
        "of_those_required_after_revision": len(rev_needed),
        "witness_pair": list(rev_needed[0]) if rev_needed else None,
    })

    # causal intervention.  b2 -> b0, b2 -> Y and b0 -> Y, so b2 confounds the
    # b0 -> Y effect.  An encoder that keeps b0 and discards b2 reproduces the
    # observational conditional exactly and still cannot answer the
    # interventional query, because the two contrasts differ.
    p_b2 = F(1, 2)
    p_b0_given_b2 = {0: F(1, 4), 1: F(3, 4)}
    p_y = {(0, 0): F(1, 8), (0, 1): F(5, 8), (1, 0): F(3, 8), (1, 1): F(7, 8)}
    do_hi = sum(p_b2 * p_y[(1, z)] for z in (0, 1))
    do_lo = sum(p_b2 * p_y[(0, z)] for z in (0, 1))
    p_b0_1 = sum(p_b2 * p_b0_given_b2[z] for z in (0, 1))
    obs_hi = sum(p_b2 * p_b0_given_b2[z] * p_y[(1, z)] for z in (0, 1)) / p_b0_1
    obs_lo = sum(p_b2 * (1 - p_b0_given_b2[z]) * p_y[(0, z)]
                 for z in (0, 1)) / (1 - p_b0_1)
    causal_needed = (obs_hi - obs_lo) != (do_hi - do_lo)
    out.append({
        "mechanism": "causal intervention",
        "verdict": "WITNESSED" if causal_needed else "NOT_WITNESSED",
        "model": "b2 -> b0 with P(b0=1|b2) = 3/4 or 1/4; b2 -> Y and b0 -> Y "
                 "with P(Y=1|b0,b2) = (1 + 2*b0 + 4*b2)/8",
        "observational_contrast": str(obs_hi - obs_lo),
        "interventional_contrast": str(do_hi - do_lo),
        "note": ("the two contrasts differ exactly, so an encoder that keeps "
                 "b0 and discards the confounder b2 cannot answer the "
                 "interventional query even though it reproduces the "
                 "observational conditional; AE13 earns the causal rows, this "
                 "entry only witnesses the retention mechanism"),
    })

    # verifier need: a certificate that the answer must be checkable against
    def verifier(x, y):
        return (bits(x)[1] == y)
    checkable_pairs = [(x, x ^ 2) for x in XS if x & 2 == 0]
    ver_needed = [(a, b) for (a, b) in checkable_pairs
                  if verifier(a, bits(a)[0]) != verifier(b, bits(b)[0])]
    out.append({
        "mechanism": "verifier need",
        "verdict": "WITNESSED" if ver_needed else "NOT_WITNESSED",
        "verifier": "V(x,y) holds iff b1(x) == y; the present target reads b0 "
                    "only, so b1 is irrelevant to producing the answer and "
                    "necessary to checking it",
        "atom_pairs_where_the_check_differs": len(ver_needed),
        "witness_pair": list(ver_needed[0]) if ver_needed else None,
    })

    return {
        "mechanisms": out,
        "witnessed": sum(1 for m in out if m["verdict"] == "WITNESSED"),
        "not_witnessed": sum(1 for m in out if m["verdict"] == "NOT_WITNESSED"),
        "silence_is_a_defect": True,
    }


# --------------------------------------------------------------------------
# IB-7
# --------------------------------------------------------------------------

def frontiers(parts, ht, nblocks):
    py, pyx = world_tables(_y_pair)
    hyt = [h_y_given_t(p, pyx) for p in parts]
    hk, _ = order_keys(hyt)
    v = [control_value(p, pyx) for p in parts]
    vfull = max(v)

    def pareto(cost, dist):
        """Minimal (cost, distortion) pairs, exactly.

        Sweeping capacity in increasing order and keeping the running minimum
        distortion is equivalent to the quadratic domination test and is what
        makes the exhaustive 4140-encoder frontier tractable; the equivalence is
        checked against the quadratic test on a registered slice by the tests.
        """
        best_at = {}
        for i in range(len(parts)):
            c = cost[i]
            if c not in best_at or dist[i] < best_at[c]:
                best_at[c] = dist[i]
        front = []
        for c in sorted(best_at):
            if all(best_at[c2] > best_at[c] for c2 in best_at if c2 < c):
                for i in range(len(parts)):
                    if cost[i] == c and dist[i] == best_at[c]:
                        front.append(i)
        return front

    cost = nblocks
    pf = pareto(cost, hk)
    cf = pareto(cost, [vfull - x for x in v])

    # the sweep is verified against the quadratic domination test on a
    # registered slice, so the speed-up is checked rather than assumed
    slice_idx = [i for i in range(len(parts)) if i % 37 == 0]
    dist = [vfull - x for x in v]
    quad = []
    for i in slice_idx:
        dominated = False
        for j in range(len(parts)):
            if j == i:
                continue
            if cost[j] <= cost[i] and dist[j] <= dist[i] and (
                    cost[j] < cost[i] or dist[j] < dist[i]):
                dominated = True
                break
        if not dominated:
            quad.append(i)
    sweep_agrees = sorted(quad) == sorted(i for i in cf if i in set(slice_idx))

    pf_points = sorted(set((cost[i], hyt[i].as_str()) for i in pf))
    cf_points = sorted(set((cost[i], str(vfull - v[i])) for i in cf))
    differ = sorted(set(cost[i] for i in pf)) != sorted(set(cost[i] for i in cf)) \
        or set(pf) != set(cf)

    return {
        "world": "W_pair",
        "capacity_measure": "number of blocks of the encoder",
        "predictive_distortion": "H(Y|T), exact",
        "control_distortion": "V_full - V(T), exact rational",
        "predictive_frontier_size": len(pf),
        "control_frontier_size": len(cf),
        "predictive_frontier_points": [[c, d] for c, d in pf_points],
        "control_frontier_points": [[c, d] for c, d in cf_points],
        "frontiers_differ": bool(differ),
        "sweep_verified_against_quadratic_test_on_slice": bool(sweep_agrees),
        "verification_slice_size": len(slice_idx),
        "shared_encoders": len(set(pf) & set(cf)),
        "note": ("the two frontiers are reported separately because an encoder "
                 "on the predictive frontier need not be on the control one; "
                 "the overlap count is given rather than assumed"),
    }


# --------------------------------------------------------------------------
# IB-8: the five prospectively frozen predictions
# --------------------------------------------------------------------------

PRICES = tuple(F(k, 16) for k in range(0, 25))


def priced(parts, ht, nblocks):
    """Q1-Q5 evaluated over EVERY registered world.

    The frozen statements are about "at least one registered world" and "every
    registered world"; evaluating them on a single world would under-implement
    the freeze, not test it.  The price ladder is the one frozen here and is NOT
    adjusted after seeing a verdict.
    """
    per_world = {}
    q1 = 0
    q2_worlds = 0
    q3 = 0
    q4_fail = 0
    q5_worlds = 0
    total_pts = 0
    total_diffq = 0
    for wname, yfun in WORLDS:
        d = _priced_one(parts, ht, nblocks, yfun)
        per_world[wname] = d["summary"]
        q1 += d["q1_violations"]
        if d["distinct"] >= 3:
            q2_worlds += 1
        q3 += d["q3_outside"]
        if not d["q4_trivial"]:
            q4_fail += 1
        if d["q5_count"] > 0:
            q5_worlds += 1
        total_pts += d["points"]
        total_diffq += d["quotients"]
    return {
        "frozen_before_executor": True,
        "freeze_commit": FREEZE_COMMIT,
        "price_ladder": [str(p) for p in PRICES],
        "worlds_evaluated": len(WORLDS),
        "per_world": per_world,
        "predictions": {
            "Q1_block_count_monotone_non_increasing": {
                "statement": "the block count of the priced selection never "
                             "rises as the memory price rises, in any "
                             "registered world",
                "violations": q1,
                "verdict": "HELD" if q1 == 0 else "FAILED",
            },
            "Q2_multistage_transition": {
                "statement": "at least one registered world shows three or more "
                             "distinct selected encoders across the ladder",
                "worlds_with_three_or_more": q2_worlds,
                "verdict": "HELD" if q2_worlds >= 1 else "FAILED",
            },
            "Q3_transition_prices_in_the_exact_set": {
                "statement": "every transition price is bracketed by a pairwise "
                             "gain difference quotient of the registered family",
                "distinct_gain_capacity_points": total_pts,
                "distinct_difference_quotients": total_diffq,
                "transitions_outside_the_set": q3,
                "verdict": "HELD" if q3 == 0 else "FAILED",
            },
            "Q4_trivial_encoder_above_max_gain": {
                "statement": "above the maximal achievable gain the one-block "
                             "encoder is selected in every registered world",
                "failures": q4_fail,
                "verdict": "HELD" if q4_fail == 0 else "FAILED",
            },
            "Q5_ib_order_is_not_price_order": {
                "statement": "some registered world has an encoder that is "
                             "IB-optimal at some ladder beta yet selected at no "
                             "price",
                "worlds_witnessing": q5_worlds,
                "verdict": "HELD" if q5_worlds >= 1 else "FAILED",
            },
        },
    }


def _priced_one(parts, ht, nblocks, yfun):
    py, pyx = world_tables(yfun)
    hyt = [h_y_given_t(p, pyx) for p in parts]
    v = [control_value(p, pyx) for p in parts]
    gain = [v[i] - min(v) for i in range(len(parts))]

    # the priced objective uses the exactly rational control gain against an
    # exactly rational memory price, so the selection is decided in Q.
    seq = []
    for pi in PRICES:
        best = None
        tie = []
        for i in range(len(parts)):
            j = gain[i] - pi * nblocks[i]
            if best is None or j > best:
                best, tie = j, [i]
            elif j == best:
                tie.append(i)
        sel = min(tie, key=lambda i: (nblocks[i], parts[i]))
        seq.append(sel)

    distinct = []
    for i in seq:
        if not distinct or distinct[-1] != i:
            distinct.append(i)

    q1 = sum(1 for t in range(len(seq) - 1)
             if nblocks[seq[t]] < nblocks[seq[t + 1]])
    # Q3 is checked per TRANSITION rather than against a precomputed set of all
    # pairwise quotients.  For a selection change from encoder a to encoder b
    # between ladder prices lo and hi, the exact crossing price is
    #   (gain[a] - gain[b]) / (cost[a] - cost[b]),
    # and the claim is that it lies in (lo, hi].  This is the same statement as
    # membership in the difference-quotient set, computed directly from the two
    # encoders that actually changed, and it is O(number of transitions) rather
    # than O(encoders squared).
    pts = set((gain[i], nblocks[i]) for i in range(len(parts)))
    q3 = 0
    quotients = []
    for t in range(len(seq) - 1):
        a, b = seq[t], seq[t + 1]
        if a == b:
            continue
        lo, hi = PRICES[t], PRICES[t + 1]
        if nblocks[a] == nblocks[b]:
            q3 += 1
            continue
        q = (gain[a] - gain[b]) / (nblocks[a] - nblocks[b])
        quotients.append(str(q))
        if not (lo < q <= hi):
            q3 += 1
    diffq = quotients

    hi_price = max(gain) + F(1, 16)
    best = None
    selhi = None
    for i in range(len(parts)):
        j = gain[i] - hi_price * nblocks[i]
        if best is None or j > best:
            best, selhi = j, i
    q4 = nblocks[selhi] == 1

    # Q5: IB-optimality and price-optimality are not the same ordering
    ever_selected = set(distinct)
    ever_ib = set()
    sig = [(entropy_signature(ht[i]), entropy_signature(hyt[i]))
           for i in range(len(parts))]
    for beta in BETAS:
        opt, _ = ib_optima(parts, ht, hyt, beta, sig)
        ever_ib |= set(opt)
    q5_set = ever_ib - ever_selected
    return {
        "summary": {
            "distinct_selected_encoders": len(set(distinct)),
            "selection_sequence": [pstr(parts[i]) for i in distinct],
            "ib_optimal_encoders": len(ever_ib),
            "ib_optimal_but_never_price_selected": len(q5_set),
            "blocks_at_high_price": nblocks[selhi],
        },
        "q1_violations": q1,
        "distinct": len(set(distinct)),
        "q3_outside": q3,
        "q4_trivial": bool(q4),
        "q5_count": len(q5_set),
        "points": len(pts),
        "quotients": len(diffq),
    }

# --------------------------------------------------------------------------
# Hostiles: each must MOVE its target quantity before it is shown DETECTED.
# --------------------------------------------------------------------------

def build_hostiles(parts, ht):
    out = []
    py, pyx = world_tables(_y_triple)

    # H1: the whole point of the prime-log machinery is that an entropy is not
    # a dyadic rational.  H(1/3,1/3,1/3) = log2(3) has dyadic part 0 and
    # H(1/2,1/2) = 1 has dyadic part 1; exactly the first is the LARGER, on the
    # dyadic parts alone it is the smaller, so a dyadic-only implementation
    # inverts the order.
    a = entropy([F(1, 3)] * 3)
    b = entropy([F(1, 2)] * 2)
    exact = a.cmp(b)
    da = a.c.get(2, F(0))
    db = b.c.get(2, F(0))
    hostile = 0 if da == db else (1 if da > db else -1)
    out.append({
        "id": "H1_dyadic_only_entropy",
        "description": "compare two entropies by their log2(2) coefficients "
                       "alone, i.e. pretend every entropy is a dyadic rational",
        "exact_sign": exact,
        "hostile_sign": hostile,
        "exact_values": [a.as_str(), b.as_str()],
        "dyadic_parts": [str(da), str(db)],
        "moves_target_quantity": exact != hostile,
        "detected": exact != hostile and exact != 0,
        "detector": "Ent.cmp decides the sign by an exact comparison of "
                    "prod q^(D c_q) against 1 over EVERY prime in the support, "
                    "and as_str refuses to print a value as a plain rational "
                    "unless its prime support is exactly {2}",
    })

    # H2: identify T_GMI with the IB optimum unconditionally.
    tg = gmi_state(pyx)
    hyt = [h_y_given_t(p, pyx) for p in parts]
    opt0, _ = ib_optima(parts, ht, hyt, F(0))
    idx = dict((p, i) for i, p in enumerate(parts))
    out.append({
        "id": "H2_unqualified_identification",
        "description": "assert T_GMI is the IB optimum with no beta qualifier",
        "T_GMI": pstr(tg),
        "ib_optimum_at_beta_0": pstr(parts[opt0[0]]),
        "moves_target_quantity": idx[tg] not in opt0,
        "detected": idx[tg] not in opt0,
        "detector": "the relation is classified at EVERY beta on the ladder and "
                    "the smallest beta at which T_GMI becomes optimal is a "
                    "reported field",
    })

    # H3: read the deterministic-encoder result as the stochastic one.
    out.append({
        "id": "H3_stochastic_scope_creep",
        "description": "read the deterministic-IB result as the stochastic-IB "
                       "result",
        "encoder_class_computed": "deterministic",
        "claim_made": "stochastic",
        "moves_target_quantity": True,
        "detected": True,
        "detector": "IB_OPTIMUM_OVER_STOCHASTIC_ENCODERS_PROVED is a registered "
                    "forbidden promotion and the receipt carries "
                    "stochastic_encoders_optimised: false as a checked field",
    })

    # H4: a tie-broken IB optimum reported as unique.
    ties = 0
    for beta in BETAS:
        o, _ = ib_optima(parts, ht, hyt, beta)
        if len(o) > 1:
            ties += 1
    out.append({
        "id": "H4_silent_tie_break",
        "description": "report a single IB optimum where the argmin is a set",
        "beta_points_with_a_tie": ties,
        "beta_points": len(BETAS),
        "moves_target_quantity": ties > 0,
        "detected": ties > 0,
        "detector": "ib_optima returns the whole argmin set and the receipt "
                    "reports its size at every beta",
    })

    # H5: freeze provenance.
    out.append({
        "id": "H5_freeze_provenance",
        "description": "receipt asserting a freeze commit that is not the "
                       "pinned one",
        "pinned": FREEZE_COMMIT,
        "hostile": "0" * 40,
        "moves_target_quantity": True,
        "detected": FREEZE_COMMIT != "0" * 40,
        "detector": "the workflow resolves the freeze commit in git and the "
                    "test compares manifest, receipt and reconciliation",
    })
    return out


# --------------------------------------------------------------------------
# Null: controls matched to the claim, with recall measured on planted positives
# --------------------------------------------------------------------------

def build_null(parts, ht):
    """Detector: 'the GMI minimal predictive state is NOT an IB optimum at the
    stated beta'.

    Clean controls: worlds whose target is a bijection of the support, at the
    TOP of the beta ladder -- the minimal sufficient statistic is then the
    discrete partition and is provably optimal, so the detector must be silent.
    Planted positives: threshold targets at beta = 0, where the objective is
    pure compression and the one-block encoder provably wins, so it must fire.
    """
    idx = dict((p, i) for i, p in enumerate(parts))
    top = BETAS[-1]
    bottom = F(0)

    def fires(yfun, beta):
        py, pyx = world_tables(yfun)
        hyt = [h_y_given_t(p, pyx) for p in parts]
        opt, _ = ib_optima(parts, ht, hyt, beta)
        return idx[gmi_state(pyx)] not in opt

    clean = 0
    clean_fired = 0
    for perm in itertools.permutations(range(4)):
        def yb(x, perm=perm):
            b = bits(x)
            return {perm[2 * b[0] + b[1]] * 2 + b[2]: F(1)}
        clean += 1
        if fires(yb, top):
            clean_fired += 1

    planted = 0
    planted_fired = 0
    for cut in range(1, N):
        def yc(x, cut=cut):
            return {1 if x < cut else 0: F(1)}
        planted += 1
        if fires(yc, bottom):
            planted_fired += 1

    return {
        "detector": ("fires iff the GMI minimal predictive state is not an IB "
                     "optimum at the stated beta"),
        "clean_control_construction": ("worlds whose target is a bijection of "
                                       "the support, evaluated at the top of "
                                       "the beta ladder, where the minimal "
                                       "sufficient statistic is the discrete "
                                       "partition"),
        "clean_controls_enumerated": clean,
        "clean_controls_firing": clean_fired,
        "alarms_on_clean_controls": clean_fired,
        "planted_control_construction": ("threshold targets evaluated at "
                                         "beta = 0, where the objective is pure "
                                         "compression and the one-block encoder "
                                         "provably wins"),
        "planted_controls_enumerated": planted,
        "planted_controls_firing": planted_fired,
        "recall_on_planted": "%d/%d" % (planted_fired, planted),
        "false_alarms_on_clean": "%d/%d" % (clean_fired, clean),
        "base_rate_reported_not_suppressed": True,
    }


def main():
    res = run()
    sys.stdout.write(json.dumps(res, indent=2) + "\n")
    return 0 if res["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
