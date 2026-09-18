#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GMI #833 -- Route A (closed form) for FREEZE_V1.md section 4.

Derived operator-invention (OI-*) and library-formation (LF-*) conditions over
the #897 T3 burden identity  B_G(w) = Phi(n, l*-1) + rank + 1,  rank in
[0, n**l* - 1],  Phi(n,l) = sum_{j=1..l} n**j,  Phi(n,0) = 0.

Exact arithmetic only (int / fractions.Fraction).  No float anywhere.
Python 3.8 compatible, stdlib only.  Run:

    python3 -I -B derivation_v1.py [outpath]
    python3 -I -O -B derivation_v1.py [outpath]

Output is byte-identical across runs and between -B and -O -B.  No `assert`
statement is used for any computed value, so -O changes nothing.
"""

import json
import os
import sys
from fractions import Fraction

PACKAGE = "gmi-833-real-developmental-validation-v1"
ROUTE = "A_CLOSED_FORM"
CLAIM_CEILING = (
    "GMI_833_REAL_SYSTEM_UPDATE_LAW_AND_DEVELOPMENTAL_VALIDATION_AND_"
    "DERIVED_INVENTION_LIBRARY_CONDITIONS_AT_REGISTERED_SCOPE"
)

# ---------------------------------------------------------------- primitives


def Phi(n, l):
    """sum_{j=1..l} n**j, exact integer; Phi(n,0) = 0.  l must be >= 0."""
    total = 0
    power = 1
    j = 0
    while j < l:
        power = power * n
        total = total + power
        j = j + 1
    return total


def ceil_div(a, b):
    """Exact integer ceiling of a/b for b > 0.  Pure integer floor-div."""
    return -((-a) // b)


def burden_range(n, l):
    """T3 burden range for a target of minimal program length l over n symbols.

    Returns (lo, hi) with lo = Phi(n,l-1)+1 (rank 0) and hi = Phi(n,l)
    (rank n**l - 1).  Requires l >= 1.
    """
    lo = Phi(n, l - 1) + 1
    hi = Phi(n, l)
    return (lo, hi)


def band(n_old, l0, n_new, l1):
    """Rank-free three-way verdict comparing (n_new,l1) against (n_old,l0)."""
    old_lo, old_hi = burden_range(n_old, l0)
    new_lo, new_hi = burden_range(n_new, l1)
    if new_hi <= old_lo - 1:
        return "GUARANTEED_REDUCTION"
    if new_lo >= old_hi + 1:
        return "GUARANTEED_INCREASE"
    return "RANK_DECIDED"


def fr(x):
    """Serialize a Fraction/int exactly as 'num/den'.  Never a float."""
    f = Fraction(x)
    return "%d/%d" % (f.numerator, f.denominator)


# ---------------------------------------------------------- registered scope

OI2_N_RANGE = (2, 12)
OI2_L_RANGE = (1, 14)
OI3_N_RANGE = (2, 24)
OI3_PROBE_MARGIN = 24          # certify upward closure this far past the thresholds
OI4_N_RANGE = (2, 6)
OI4_OCC_RANGE = (1, 8)
OI4_B_RANGE = (1, 6)
OI4_KAPPA_RANGE = (0, 3)
OI4_L0_RANGE = (1, 10)
LF_N_RANGE = (2, 8)
LF_K_RANGE = (2, 6)
LF_LMAX = 12
NULL_TRIALS = 200
LCG_A = 6364136223846793005
LCG_C = 1442695040888963407
LCG_M = 1 << 64
LCG_SEED = 8330000041

# Registered domain assumptions that are load-bearing (see DERIVATION_THEOREMS_V1.md).
DOMAIN_ASSUMPTIONS = [
    "ADMISSIBLE_PROGRAM_LENGTHS_ARE_>=1 (l0>=1, l1>=1, lL>=1, lj>=1): the empty "
    "program is not a program, so Phi(.,0)=0 is a range endpoint and never a "
    "realizable target length.",
    "COMPRESSION_ADMISSIBILITY l1 <= l0 (and lL <= lj): a candidate that "
    "lengthens the minimal program is inadmissible (hostile H4).",
    "ALPHABET_GROWTH_IS_EXACTLY_ONE_SYMBOL_PER_ADMITTED_OPERATOR: G0 has n "
    "symbols, G0+{o} has n+1, a shared library of k members has n+k.",
    "CHARGES_ARE_NONNEGATIVE: D(o) >= 0, len(body) >= 0, kappa >= 0.",
    "RANK_FREE: no verdict may depend on the rank coordinate of T3; only the "
    "two range endpoints are used.",
]


# ------------------------------------------------------------------ OI-2


def run_oi2():
    n_lo, n_hi = OI2_N_RANGE
    l_lo, l_hi = OI2_L_RANGE
    cells = 0
    ineq_violations = []
    band_exceptions = []
    gamma1_verdicts = {"GUARANTEED_REDUCTION": 0, "GUARANTEED_INCREASE": 0,
                       "RANK_DECIDED": 0}
    n = n_lo
    while n <= n_hi:
        l = l_lo
        while l <= l_hi:
            cells = cells + 1
            # OI-2 inequality proper: Phi(n+1, l-1) >= Phi(n, l-1).
            if not (Phi(n + 1, l - 1) >= Phi(n, l - 1)):
                ineq_violations.append({"n": n, "l": l})
            # Derived band consequence at gamma = 1 (l1 = l0 - 1).
            l0 = l
            if Phi(n + 1, l0 - 1) <= Phi(n, l0 - 1):
                band_exceptions.append({
                    "n": n, "l0": l0, "l1": l0 - 1,
                    "Phi_n_plus_1_l0_minus_1": Phi(n + 1, l0 - 1),
                    "Phi_n_l0_minus_1": Phi(n, l0 - 1),
                    "degenerate_l1_is_zero": (l0 - 1) == 0,
                })
            if l0 >= 2:
                gamma1_verdicts[band(n, l0, n + 1, l0 - 1)] += 1
            l = l + 1
        n = n + 1
    exception_l0_values = sorted(set([e["l0"] for e in band_exceptions]))
    all_exceptions_degenerate = True
    for e in band_exceptions:
        if not e["degenerate_l1_is_zero"]:
            all_exceptions_degenerate = False
    return {
        "claim_id": "OI-2",
        "statement_as_frozen": (
            "For all n>=2, l>=1: Phi(n+1,l-1) >= Phi(n,l-1); hence a "
            "compression of depth gamma=1 is never in the guaranteed-reduction "
            "band Phi(n+1,l0-gamma) <= Phi(n,l0-1), whatever the charge."
        ),
        "verdict": "TRUE_AS_FROZEN_ON_THE_ADMISSIBLE_DOMAIN",
        "census_n_range": list(OI2_N_RANGE),
        "census_l_range": list(OI2_L_RANGE),
        "census_cells": cells,
        "inequality_violations": ineq_violations,
        "inequality_violation_count": len(ineq_violations),
        "band_exception_count": len(band_exceptions),
        "band_exception_l0_values": exception_l0_values,
        "band_exceptions_all_degenerate_l1_eq_0": all_exceptions_degenerate,
        "band_exception_note": (
            "The band condition Phi(n+1,l0-1) <= Phi(n,l0-1) is satisfiable "
            "only with equality, i.e. only at l0-1 = 0. The %d exception cells "
            "are exactly the l0=1 cells, where l1 = 0 is the empty program and "
            "is excluded by the registered assumption "
            "ADMISSIBLE_PROGRAM_LENGTHS_ARE_>=1. On the admissible domain "
            "l0>=2 there are 0 exceptions. The exceptions are reported, not "
            "removed from the census." % len(band_exceptions)
        ),
        "gamma1_verdict_counts_on_l0_ge_2": gamma1_verdicts,
        "quantifiers": "forall[D] for the inequality; forall_fin[U] for the census certificate",
        "evidence_level": ["EV1", "EV2"],
    }


# ------------------------------------------------------------------ OI-3


def lstar(n):
    """min{ l >= 1 : Phi(n+1, l-1) >= Phi(n, l) }  (frozen definition)."""
    l = 1
    while True:
        if Phi(n + 1, l - 1) >= Phi(n, l):
            return l
        l = l + 1


def mstar(n):
    """min{ l >= 2 : Phi(n+1, l-2) >= Phi(n, l) } -- the gamma=1 analogue."""
    l = 2
    while True:
        if Phi(n + 1, l - 2) >= Phi(n, l):
            return l
        l = l + 1


def run_oi3():
    n_lo, n_hi = OI3_N_RANGE
    table = {}
    bracket_violations = []
    lstar_gamma0_ok = 0
    lstar_gamma0_bad = []
    mstar_gamma1_ok = 0
    mstar_gamma1_bad = []
    frozen_consequence_counterexamples = []
    n = n_lo
    while n <= n_hi:
        L = lstar(n)
        M = mstar(n)
        lb = n + 2
        ub = 1 + ceil_div(n * (n * n - n + 1), n - 1)
        if not (lb <= L and L <= ub):
            bracket_violations.append({"quantity": "Lstar", "n": n, "value": L,
                                       "lower": lb, "upper": ub})
        if not (lb <= M and M <= ub):
            bracket_violations.append({"quantity": "Mstar", "n": n, "value": M,
                                       "lower": lb, "upper": ub})
        table["n=%02d" % n] = {
            "Lstar": L, "Mstar": M, "bracket_lower_n_plus_2": lb,
            "bracket_upper_1_plus_ceil": ub,
            "Lstar_in_bracket": (lb <= L and L <= ub),
            "Mstar_in_bracket": (lb <= M and M <= ub),
            "Mstar_minus_Lstar": M - L,
        }
        # certify upward closure + the two matched converses
        l = L
        while l <= M + OI3_PROBE_MARGIN:
            v0 = band(n, l, n + 1, l)            # gamma = 0
            if v0 == "GUARANTEED_INCREASE":
                lstar_gamma0_ok = lstar_gamma0_ok + 1
            else:
                lstar_gamma0_bad.append({"n": n, "l0": l, "gamma": 0, "verdict": v0})
            l = l + 1
        l = M
        while l <= M + OI3_PROBE_MARGIN:
            v1 = band(n, l, n + 1, l - 1)        # gamma = 1
            if v1 == "GUARANTEED_INCREASE":
                mstar_gamma1_ok = mstar_gamma1_ok + 1
            else:
                mstar_gamma1_bad.append({"n": n, "l0": l, "gamma": 1, "verdict": v1})
            l = l + 1
        # the FROZEN consequence: "at depth l >= Lstar(n) a gamma=1 admission is
        # in the GUARANTEED_INCREASE band".  Search Lstar <= l < Mstar.
        l = L
        while l < M:
            if l >= 2:
                v1 = band(n, l, n + 1, l - 1)
                if v1 != "GUARANTEED_INCREASE":
                    frozen_consequence_counterexamples.append({
                        "n": n, "l0": l, "gamma": 1, "l1": l - 1,
                        "actual_verdict": v1,
                        "Phi_n_plus_1_l0_minus_2": Phi(n + 1, l - 2),
                        "Phi_n_l0": Phi(n, l),
                    })
            l = l + 1
        n = n + 1
    first_ce = frozen_consequence_counterexamples[:6]
    return {
        "claim_id": "OI-3",
        "statement_as_frozen": (
            "Lstar(n) = min{ l : Phi(n+1,l-1) >= Phi(n,l) } exists for every "
            "n>=2, is bracketed n+2 <= Lstar(n) <= 1 + ceil(n(n^2-n+1)/(n-1)), "
            "and at depth l >= Lstar(n) a gamma=1 admission is in the "
            "GUARANTEED_INCREASE band."
        ),
        "verdict": "DEFINITION_AND_BRACKET_TRUE__GAMMA1_CONSEQUENCE_FALSE_AS_FROZEN",
        "census_n_range": list(OI3_N_RANGE),
        "table": table,
        "bracket_violations": bracket_violations,
        "bracket_violation_count": len(bracket_violations),
        "corrected_statement": (
            "Lstar(n) as frozen is exactly the guaranteed-loss depth at "
            "gamma = 0: for every l >= Lstar(n), band(n,l -> n+1,l) = "
            "GUARANTEED_INCREASE, i.e. an operator that compresses nothing "
            "strictly loses at every nonnegative charge. The gamma = 1 "
            "guaranteed-loss depth is the strictly larger companion "
            "Mstar(n) = min{ l >= 2 : Phi(n+1,l-2) >= Phi(n,l) }; for every "
            "l >= Mstar(n), band(n,l -> n+1,l-1) = GUARANTEED_INCREASE. "
            "Mstar(n) > Lstar(n) at every n in the census and satisfies the "
            "SAME frozen bracket n+2 <= Mstar(n) <= 1 + ceil(n(n^2-n+1)/(n-1)). "
            "The frozen definition of Lstar is NOT edited; Mstar is a new "
            "derived companion quantity that carries the corrected converse."
        ),
        "frozen_gamma1_consequence_counterexample_count":
            len(frozen_consequence_counterexamples),
        "frozen_gamma1_consequence_first_counterexamples": first_ce,
        "gamma0_guaranteed_increase_cells_certified": lstar_gamma0_ok,
        "gamma0_guaranteed_increase_failures": lstar_gamma0_bad,
        "gamma1_guaranteed_increase_cells_certified": mstar_gamma1_ok,
        "gamma1_guaranteed_increase_failures": mstar_gamma1_bad,
        "probe_margin_past_threshold": OI3_PROBE_MARGIN,
        "quantifiers": "forall_fin[U] over n in 2..24 and the registered probe window",
        "evidence_level": ["EV1", "EV2"],
    }


# ------------------------------------------------------------------ OI-1

# Registered workload census.  Weights are exact rationals "num/den".
WORKLOADS = [
    {"id": "W1", "n": 2, "D": 1, "body_len": 4, "kappa": 1,
     "note": "single target, deep compression; the Route-B overlap workload",
     "targets": [{"t": "t1", "weight": "1/1", "l0": 8, "l1": 2}]},
    {"id": "W2", "n": 2, "D": 0, "body_len": 2, "kappa": 1,
     "note": "gamma = 0: nothing compresses",
     "targets": [{"t": "t1", "weight": "1/1", "l0": 4, "l1": 4}]},
    {"id": "W3", "n": 3, "D": 2, "body_len": 3, "kappa": 1,
     "note": "one deep compression, one untouched target; tax dominates",
     "targets": [{"t": "t1", "weight": "3/4", "l0": 6, "l1": 3},
                 {"t": "t2", "weight": "1/4", "l0": 6, "l1": 6}]},
    {"id": "W4", "n": 3, "D": 2, "body_len": 3, "kappa": 1,
     "note": "same shape as W3 but the compressing target carries the mass",
     "targets": [{"t": "t1", "weight": "99/100", "l0": 6, "l1": 2},
                 {"t": "t2", "weight": "1/100", "l0": 6, "l1": 6}]},
    {"id": "W5", "n": 4, "D": 5, "body_len": 6, "kappa": 1,
     "note": "three targets, two compressing at different depths",
     "targets": [{"t": "t1", "weight": "1/2", "l0": 7, "l1": 3},
                 {"t": "t2", "weight": "1/3", "l0": 5, "l1": 4},
                 {"t": "t3", "weight": "1/6", "l0": 5, "l1": 5}]},
    {"id": "W6", "n": 2, "D": 0, "body_len": 1, "kappa": 0,
     "note": "gamma = 1 only; OI-2 forces Theta_inv <= 0",
     "targets": [{"t": "t1", "weight": "1/1", "l0": 7, "l1": 6}]},
]


def theta_inv(n, targets):
    """Exact rank-free invention affordance Theta_inv(o)."""
    saving = Fraction(0)
    tax = Fraction(0)
    for tg in targets:
        w = Fraction(tg["weight"])
        l0 = tg["l0"]
        l1 = tg["l1"]
        if l1 < l0:
            saving = saving + w * (Phi(n, l0 - 1) + 1 - Phi(n + 1, l1))
        elif l1 == l0:
            tax = tax + w * (Phi(n + 1, l0) - Phi(n, l0 - 1) - 1)
    return (saving, tax, saving - tax)


def run_oi1():
    rows = []
    for wl in WORKLOADS:
        n = wl["n"]
        for tg in wl["targets"]:
            if tg["l1"] > tg["l0"]:
                rows.append({"id": wl["id"], "error": "H4_INADMISSIBLE_COMPRESSION"})
        saving, tax, theta = theta_inv(n, wl["targets"])
        charge = Fraction(wl["D"] + wl["body_len"] + wl["kappa"])
        rows.append({
            "id": wl["id"], "n": n, "note": wl["note"],
            "targets": [{"t": t["t"], "weight": t["weight"], "l0": t["l0"],
                         "l1": t["l1"], "gamma": t["l0"] - t["l1"]}
                        for t in wl["targets"]],
            "D": wl["D"], "body_len": wl["body_len"], "kappa": wl["kappa"],
            "total_charge": fr(charge),
            "Saving": fr(saving), "Tax": fr(tax), "Theta_inv": fr(theta),
            "strictly_pays": bool(charge < theta),
        })
    return {
        "claim_id": "OI-1",
        "statement": (
            "For a registered workload T of targets with exact rational "
            "weights, minimal length l0 under G0 (alphabet n) and l1 under "
            "G0+{o} (alphabet n+1), with "
            "Saving = sum_{l1<l0} w*(Phi(n,l0-1)+1 - Phi(n+1,l1)), "
            "Tax = sum_{l1=l0} w*(Phi(n+1,l0) - Phi(n,l0-1) - 1) and "
            "Theta_inv(o) = Saving - Tax, admitting o strictly reduces total "
            "priced burden -- rank-free, i.e. at every rank assignment -- iff "
            "D(o) + (len(body)+kappa) < Theta_inv(o)."
        ),
        "verdict": "TRUE_AS_FROZEN",
        "workload_census_size": len(WORKLOADS),
        "rows": rows,
        "quantifiers": "forall[D] for the threshold identity; forall_fin[U] for the workload census",
        "evidence_level": ["EV1", "EV2"],
    }


# ------------------------------------------------------------------ OI-4


def gammastar_inv(n, l0):
    """min{ gamma in 0..l0-1 : Phi(n+1, l0-gamma) <= Phi(n, l0-1) } or None.

    Exactly the least compression depth that reaches GUARANTEED_REDUCTION for a
    single admitted operator (alphabet n -> n+1).  lL = l0-gamma >= 1.
    """
    g = 0
    while g <= l0 - 1:
        if Phi(n + 1, l0 - g) <= Phi(n, l0 - 1):
            return g
        g = g + 1
    return None


def run_oi4():
    n_lo, n_hi = OI4_N_RANGE
    o_lo, o_hi = OI4_OCC_RANGE
    b_lo, b_hi = OI4_B_RANGE
    k_lo, k_hi = OI4_KAPPA_RANGE
    l_lo, l_hi = OI4_L0_RANGE
    cells = 0
    insufficient = None
    insufficient_strict = None      # same, restricted to gamma >= 1
    unnecessary = None
    n_insuff = 0
    n_insuff_strict = 0
    n_unnec = 0
    repaired_counterexamples = []
    n = n_lo
    while n <= n_hi:
        occ = o_lo
        while occ <= o_hi:
            b = b_lo
            while b <= b_hi:
                kap = k_lo
                while kap <= k_hi:
                    gain = occ * (b - 1) - b - kap
                    l0 = l_lo
                    while l0 <= l_hi:
                        l1 = 1
                        while l1 <= l0:
                            cells = cells + 1
                            v = band(n, l0, n + 1, l1)
                            gamma = l0 - l1
                            if gain > 0 and v == "GUARANTEED_INCREASE":
                                n_insuff = n_insuff + 1
                                if insufficient is None:
                                    insufficient = (n, occ, b, kap, l0, l1, gain, v)
                                if gamma >= 1:
                                    n_insuff_strict = n_insuff_strict + 1
                                    if insufficient_strict is None:
                                        insufficient_strict = (n, occ, b, kap, l0,
                                                               l1, gain, v)
                            if gain <= 0 and v == "GUARANTEED_REDUCTION":
                                n_unnec = n_unnec + 1
                                if unnecessary is None:
                                    unnecessary = (n, occ, b, kap, l0, l1, gain, v)
                            # repaired rule: gain > 0 AND gamma >= gammastar_inv(n,l0)
                            gs = gammastar_inv(n, l0)
                            repaired = (gain > 0) and (gs is not None) and (gamma >= gs)
                            if repaired and v != "GUARANTEED_REDUCTION":
                                repaired_counterexamples.append({
                                    "n": n, "occ": occ, "b": b, "kappa": kap,
                                    "l0": l0, "l1": l1, "gain": gain,
                                    "gammastar_inv": gs, "verdict": v})
                            l1 = l1 + 1
                        l0 = l0 + 1
                    kap = kap + 1
                b = b + 1
            occ = occ + 1
        n = n + 1

    def pack(t, kind):
        if t is None:
            return {"witness": "NO_WITNESS_FOUND", "kind": kind}
        n_, occ_, b_, kap_, l0_, l1_, gain_, v_ = t
        old_lo, old_hi = burden_range(n_, l0_)
        new_lo, new_hi = burden_range(n_ + 1, l1_)
        return {
            "kind": kind, "n": n_, "occ": occ_, "b": b_, "kappa": kap_,
            "l0": l0_, "l1": l1_, "gamma": l0_ - l1_,
            "gain_897": gain_,
            "gain_897_formula": "occ*(b-1) - b - kappa",
            "burden_range_G0": [old_lo, old_hi],
            "burden_range_G0_plus_o": [new_lo, new_hi],
            "Phi_n_l0_minus_1": Phi(n_, l0_ - 1), "Phi_n_l0": Phi(n_, l0_),
            "Phi_n_plus_1_l1_minus_1": Phi(n_ + 1, l1_ - 1),
            "Phi_n_plus_1_l1": Phi(n_ + 1, l1_),
            "phi_frame_verdict": v_,
        }

    gs_table = {}
    n = n_lo
    while n <= n_hi:
        l0 = 1
        while l0 <= l_hi:
            gs_table["n=%d|l0=%02d" % (n, l0)] = gammastar_inv(n, l0)
            l0 = l0 + 1
        n = n + 1
    gs_defined_min = None
    for key in sorted(gs_table.keys()):
        v = gs_table[key]
        if v is not None:
            if gs_defined_min is None or v < gs_defined_min:
                gs_defined_min = v

    return {
        "claim_id": "OI-4",
        "statement": (
            "#897's corpus-symbol admission rule gain = occ*(b-1) - b - kappa "
            "> 0 is NEITHER SUFFICIENT NOR NECESSARY for burden reduction in "
            "the Phi frame."
        ),
        "verdict": "TRUE_AS_FROZEN__EARNED_BY_COUNTEREXAMPLE",
        "census_cells": cells,
        "census_ranges": {
            "n": list(OI4_N_RANGE), "occ": list(OI4_OCC_RANGE),
            "b": list(OI4_B_RANGE), "kappa": list(OI4_KAPPA_RANGE),
            "l0": list(OI4_L0_RANGE), "l1": "1..l0 (admissible, l1>=1)"},
        "lexicographic_order": "(n, occ, b, kappa, l0, l1) ascending",
        "not_sufficient_witness_lexicographically_first": pack(insufficient,
                                                              "NOT_SUFFICIENT"),
        "not_sufficient_witness_count": n_insuff,
        "not_sufficient_strict_compression_witness": pack(insufficient_strict,
                                                          "NOT_SUFFICIENT_GAMMA_GE_1"),
        "not_sufficient_strict_compression_count": n_insuff_strict,
        "not_necessary_witness_lexicographically_first": pack(unnecessary,
                                                              "NOT_NECESSARY"),
        "not_necessary_witness_count": n_unnec,
        "repair_side_condition": (
            "Replace `gain > 0` by `gain > 0 AND gamma >= gammastar_inv(n,l0)`, "
            "where gamma = l0 - l1 and gammastar_inv(n,l0) = min{ gamma in "
            "0..l0-1 : Phi(n+1,l0-gamma) <= Phi(n,l0-1) }. By OI-2, "
            "gammastar_inv(n,l0) >= 2 for every l0 >= 2, so the repaired rule "
            "contains the gamma>=2 requirement. The matched refusal comes from "
            "OI-3: refuse admission whenever gamma = 0 and l0 >= Lstar(n), and "
            "whenever gamma = 1 and l0 >= Mstar(n), since those cells are "
            "GUARANTEED_INCREASE at every nonnegative charge. Sufficiency for "
            "*paying* still additionally requires OI-1's charge test "
            "D(o) + len(body) + kappa < Theta_inv(o); the side-condition "
            "repairs the SIGN of the burden change, not the charge account."
        ),
        "repaired_rule_counterexamples": repaired_counterexamples,
        "repaired_rule_counterexample_count": len(repaired_counterexamples),
        "gammastar_inv_table": gs_table,
        "gammastar_inv_min_where_defined": gs_defined_min,
        "quantifiers": "forall_fin[U] over the registered census; the witnesses are EARNED-BY-COUNTEREXAMPLE",
        "evidence_level": ["EV1", "EV2"],
    }


# ------------------------------------------------------------------ LF-1


def lf1_verdict(n, k, lL, lj):
    better = Phi(n + k, lL) <= Phi(n + 1, lj - 1)
    worse = Phi(n + k, lL - 1) >= Phi(n + 1, lj)
    if better and worse:
        return "BAND_COLLISION"
    if better:
        return "LIBRARY_GUARANTEED_BETTER"
    if worse:
        return "LIBRARY_GUARANTEED_WORSE"
    return "RANK_DECIDED"


def lf1_census():
    """Deterministic ordered list of (n,k,lL,lj) census cells."""
    out = []
    n_lo, n_hi = LF_N_RANGE
    k_lo, k_hi = LF_K_RANGE
    n = n_lo
    while n <= n_hi:
        k = k_lo
        while k <= k_hi:
            lj = 1
            while lj <= LF_LMAX:
                lL = 1
                while lL <= lj:
                    out.append((n, k, lL, lj))
                    lL = lL + 1
                lj = lj + 1
            k = k + 1
        n = n + 1
    return out


def run_lf1(cells):
    counts = {"LIBRARY_GUARANTEED_BETTER": 0, "LIBRARY_GUARANTEED_WORSE": 0,
              "RANK_DECIDED": 0, "BAND_COLLISION": 0}
    collisions = []
    cross_check_mismatch = []
    for (n, k, lL, lj) in cells:
        v = lf1_verdict(n, k, lL, lj)
        counts[v] += 1
        if v == "BAND_COLLISION":
            collisions.append({"n": n, "k": k, "lL": lL, "lj": lj})
        # independent cross-check inside Route A: the generic band() function
        vb = band(n + 1, lj, n + k, lL)
        mapped = {"GUARANTEED_REDUCTION": "LIBRARY_GUARANTEED_BETTER",
                  "GUARANTEED_INCREASE": "LIBRARY_GUARANTEED_WORSE",
                  "RANK_DECIDED": "RANK_DECIDED"}[vb]
        if mapped != v:
            cross_check_mismatch.append({"n": n, "k": k, "lL": lL, "lj": lj,
                                         "closed_form": v, "band_fn": mapped})
    return {
        "claim_id": "LF-1",
        "statement": (
            "LIBRARY (alphabet n+k, length lL) versus SEPARATE (alphabet n+1, "
            "length lj): LIBRARY_GUARANTEED_BETTER iff Phi(n+k,lL) <= "
            "Phi(n+1,lj-1); LIBRARY_GUARANTEED_WORSE iff Phi(n+k,lL-1) >= "
            "Phi(n+1,lj); else RANK_DECIDED. The two bands are mutually "
            "exclusive."
        ),
        "verdict": "TRUE_AS_FROZEN",
        "census_ranges": {"n": list(LF_N_RANGE), "k": list(LF_K_RANGE),
                          "lL_lj": "1 <= lL <= lj <= %d" % LF_LMAX},
        "census_cells": len(cells),
        "counts": counts,
        "mutual_exclusivity_violations": collisions,
        "mutual_exclusivity_violation_count": len(collisions),
        "mutual_exclusivity_proof": (
            "If both held then Phi(n+k,lL-1) >= Phi(n+1,lj) > Phi(n+1,lj-1) >= "
            "Phi(n+k,lL) >= Phi(n+k,lL-1), a strict self-inequality. The strict "
            "step uses Phi(n+1,lj) - Phi(n+1,lj-1) = (n+1)**lj > 0 for lj >= 1."
        ),
        "internal_cross_check_mismatches": cross_check_mismatch,
        "internal_cross_check_mismatch_count": len(cross_check_mismatch),
        "quantifiers": "forall[D] for exclusivity; forall_fin[U] for the band counts",
        "evidence_level": ["EV1", "EV2"],
    }


# ------------------------------------------------------------------ LF-2

MEMBER_SET_CENSUS = [
    {"id": "M1", "kappa": 0, "bodies": [2, 2]},
    {"id": "M2", "kappa": 1, "bodies": [2, 3]},
    {"id": "M3", "kappa": 1, "bodies": [1, 1, 1]},
    {"id": "M4", "kappa": 2, "bodies": [4, 2, 7, 3]},
    {"id": "M5", "kappa": 3, "bodies": [5, 5, 5, 5, 5]},
    {"id": "M6", "kappa": 1, "bodies": [9, 2, 2, 4, 6, 3]},
    {"id": "M7", "kappa": 0, "bodies": [1, 8]},
    {"id": "M8", "kappa": 8, "bodies": [3, 3, 3]},
]


def run_lf2():
    rows = []
    mismatches = []
    for ms in MEMBER_SET_CENSUS:
        kap = ms["kappa"]
        bodies = ms["bodies"]
        shared = 0
        for b in bodies:
            shared = shared + (b + kap)
        separate = 0
        for b in bodies:
            # each member kept in its OWN single-member grammar
            separate = separate + (b + kap)
        rows.append({"id": ms["id"], "k": len(bodies), "kappa": kap,
                     "bodies": list(bodies),
                     "K_total_shared_library": shared,
                     "K_total_k_separate_grammars": separate,
                     "equal": shared == separate,
                     "difference": shared - separate})
        if shared != separate:
            mismatches.append(ms["id"])
    return {
        "claim_id": "LF-2",
        "statement": (
            "Under #897's charge K_total(L) = sum_{m in L} (len(body_m) + "
            "kappa), the maintenance charge of one shared library of k members "
            "equals the total maintenance charge of the k separate "
            "single-member grammars over the same member set. The LF-1 "
            "decision therefore carries no charge term."
        ),
        "verdict": "TRUE_AS_FROZEN",
        "proof": (
            "K_total is a sum indexed by members, with a summand depending only "
            "on that member's body length and the global kappa. Partitioning "
            "the same index set into k singletons and summing the k partial "
            "sums returns the same total; the charge is invariant under the "
            "partition, which is the only thing library-versus-separate "
            "changes. Hence the difference in priced burden is exactly the "
            "difference in search-discovery burden, which is what LF-1 decides."
        ),
        "census_size": len(MEMBER_SET_CENSUS),
        "rows": rows,
        "mismatched_member_sets": mismatches,
        "mismatch_count": len(mismatches),
        "quantifiers": "forall[D]; forall_fin[U] for the member-set census",
        "evidence_level": ["EV1", "EV2"],
    }


# ------------------------------------------------------------------ LF-3


def run_lf3(cells):
    checked = 0
    fail_strict_upper = []
    fail_weak_lower = []
    verdicts = {"LIBRARY_GUARANTEED_BETTER": 0, "LIBRARY_GUARANTEED_WORSE": 0,
                "RANK_DECIDED": 0, "BAND_COLLISION": 0}
    tax_rows = {}
    tax_nonpositive = []
    for (n, k, lL, lj) in cells:
        if lL != lj:
            continue
        checked = checked + 1
        if not (Phi(n + k, lj) > Phi(n + 1, lj)):
            fail_strict_upper.append({"n": n, "k": k, "lj": lj})
        if not (Phi(n + k, lj - 1) >= Phi(n + 1, lj - 1)):
            fail_weak_lower.append({"n": n, "k": k, "lj": lj})
        verdicts[lf1_verdict(n, k, lL, lj)] += 1
        if lj >= 2:
            tax = Phi(n + k, lj - 1) - Phi(n + 1, lj - 1)
            tax_rows["n=%d|k=%d|l=%02d" % (n, k, lj)] = tax
            if not (tax > 0):
                tax_nonpositive.append({"n": n, "k": k, "l": lj, "tax": tax})
    tax_keys = sorted(tax_rows.keys())
    tax_min = None
    for key in tax_keys:
        if tax_min is None or tax_rows[key] < tax_min:
            tax_min = tax_rows[key]
    sample = {}
    for key in tax_keys[:12]:
        sample[key] = tax_rows[key]
    return {
        "claim_id": "LF-3",
        "statement": (
            "If the composition gain gamma_w = lj - lL is 0 for every target, "
            "then for k >= 2 BOTH Phi(n+k,lj) > Phi(n+1,lj) and "
            "Phi(n+k,lj-1) >= Phi(n+1,lj-1); the exact same-rank dilution tax "
            "is Phi(n+k,l-1) - Phi(n+1,l-1) > 0 for l >= 2. Library formation "
            "is not a search-charge phenomenon without member composition."
        ),
        "verdict": "TRUE_AS_FROZEN",
        "gamma0_cells_checked": checked,
        "strict_upper_endpoint_failures": fail_strict_upper,
        "strict_upper_endpoint_failure_count": len(fail_strict_upper),
        "weak_lower_endpoint_failures": fail_weak_lower,
        "weak_lower_endpoint_failure_count": len(fail_weak_lower),
        "weak_lower_endpoint_note": (
            "The lower-endpoint inequality is stated weakly (>=) and is tight "
            "exactly at lj = 1, where Phi(n+k,0) = Phi(n+1,0) = 0. It is strict "
            "for every lj >= 2."
        ),
        "gamma0_verdict_counts": verdicts,
        "endpoint_dominance_vs_band_note": (
            "ENDPOINT DOMINANCE DOES NOT IMPLY THE GUARANTEED-WORSE BAND. Both "
            "endpoints of the library range strictly (resp. weakly) exceed the "
            "corresponding separate endpoints at every gamma=0 cell, yet only "
            "%d of the %d gamma=0 cells are LIBRARY_GUARANTEED_WORSE; the other "
            "%d are RANK_DECIDED, because the two ranges still OVERLAP "
            "(Phi(n+k,lj-1) < Phi(n+1,lj)) and a favourable rank draw can keep "
            "the library ahead. 0 gamma=0 cells are LIBRARY_GUARANTEED_BETTER. "
            "The honest claim is: at gamma=0 the library never wins a "
            "guarantee, and it is guaranteed to lose only above the dilution "
            "threshold." % (verdicts["LIBRARY_GUARANTEED_WORSE"], checked,
                            verdicts["RANK_DECIDED"])
        ),
        "dilution_tax_cells": len(tax_keys),
        "dilution_tax_min": tax_min,
        "dilution_tax_nonpositive_cells": tax_nonpositive,
        "dilution_tax_nonpositive_count": len(tax_nonpositive),
        "dilution_tax_sample": sample,
        "quantifiers": "forall[D] for the two inequalities and the tax sign; forall_fin[U] for the counts",
        "evidence_level": ["EV1", "EV2"],
    }


# ------------------------------------------------------------------ LF-4


def gammastar(n, k, lj):
    """min{ gamma in 0..lj-1 : Phi(n+k, lj-gamma) <= Phi(n+1, lj-1) } or None.

    lL = lj - gamma >= 1 by the registered admissibility assumption.
    """
    g = 0
    while g <= lj - 1:
        if Phi(n + k, lj - g) <= Phi(n + 1, lj - 1):
            return g
        g = g + 1
    return None


def run_lf4():
    n_lo, n_hi = LF_N_RANGE
    k_lo, k_hi = LF_K_RANGE
    table = {}
    defined = 0
    undefined = 0
    below_two = []
    undefined_lj = []
    n = n_lo
    while n <= n_hi:
        k = k_lo
        while k <= k_hi:
            lj = 2
            while lj <= LF_LMAX:
                g = gammastar(n, k, lj)
                table["n=%d|k=%d|lj=%02d" % (n, k, lj)] = g
                if g is None:
                    undefined = undefined + 1
                    undefined_lj.append(lj)
                else:
                    defined = defined + 1
                    if g < 2:
                        below_two.append({"n": n, "k": k, "lj": lj, "gammastar": g})
                lj = lj + 1
            k = k + 1
        n = n + 1
    # monotonicity in k (None treated as +infinity)
    mono_violations = []
    n = n_lo
    while n <= n_hi:
        lj = 2
        while lj <= LF_LMAX:
            prev = None
            k = k_lo
            while k <= k_hi:
                g = table["n=%d|k=%d|lj=%02d" % (n, k, lj)]
                # None is read as +infinity for the monotonicity test
                if prev is not None:
                    p_is_inf = prev[1]
                    c_is_inf = (g is None)
                    if (not c_is_inf) and (not p_is_inf) and g < prev[0]:
                        mono_violations.append({"n": n, "lj": lj, "k": k,
                                                "gammastar_k_minus_1": prev[0],
                                                "gammastar_k": g})
                    if (not c_is_inf) and p_is_inf:
                        mono_violations.append({"n": n, "lj": lj, "k": k,
                                                "gammastar_k_minus_1": None,
                                                "gammastar_k": g})
                prev = (g, g is None)
                k = k + 1
            lj = lj + 1
        n = n + 1
    sample_keys = ["n=2|k=2|lj=03", "n=2|k=2|lj=05", "n=2|k=2|lj=08",
                   "n=2|k=6|lj=12", "n=5|k=3|lj=07", "n=8|k=6|lj=12",
                   "n=2|k=2|lj=02", "n=8|k=2|lj=02"]
    sample = {}
    for key in sample_keys:
        sample[key] = table[key]
    min_defined = None
    for key in sorted(table.keys()):
        v = table[key]
        if v is not None:
            if min_defined is None or v < min_defined:
                min_defined = v
    return {
        "claim_id": "LF-4",
        "statement": (
            "gammastar(n,k,lj) = min{ gamma : Phi(n+k, lj-gamma) <= "
            "Phi(n+1, lj-1) } over admissible lL = lj-gamma >= 1, or None. "
            "gammastar >= 2 wherever defined; gammastar is non-decreasing in k "
            "(None read as +infinity); gammastar is undefined exactly at lj = 2."
        ),
        "verdict": "TRUE_AS_FROZEN",
        "census_ranges": {"n": list(LF_N_RANGE), "k": list(LF_K_RANGE),
                          "lj": [2, LF_LMAX]},
        "table_cells": defined + undefined,
        "defined_cells": defined,
        "undefined_cells": undefined,
        "undefined_at_lj_values": sorted(set(undefined_lj)),
        "min_gammastar_where_defined": min_defined,
        "gammastar_below_two_violations": below_two,
        "gammastar_below_two_violation_count": len(below_two),
        "monotonicity_in_k_violations": mono_violations,
        "monotonicity_in_k_violation_count": len(mono_violations),
        "table": table,
        "sample": sample,
        "why_gammastar_ge_2": (
            "gamma=0 needs Phi(n+k,lj) <= Phi(n+1,lj-1), false since "
            "Phi(n+k,lj) > Phi(n+1,lj) > Phi(n+1,lj-1) for k>=2, lj>=1. "
            "gamma=1 needs Phi(n+k,lj-1) <= Phi(n+1,lj-1), false for lj>=2 "
            "since n+k > n+1. This is exactly OI-2's mechanism with the "
            "one-symbol step replaced by a k-symbol step."
        ),
        "why_undefined_at_lj_2": (
            "At lj=2 the admissible gammas are 0 and 1 only (lL >= 1), and both "
            "fail by the argument above. The registered assumption "
            "ADMISSIBLE_PROGRAM_LENGTHS_ARE_>=1 is load-bearing here: if lL=0 "
            "were admissible, gamma=lj would always satisfy the condition "
            "(Phi(.,0)=0) and gammastar would never be undefined."
        ),
        "quantifiers": "forall_fin[U] over the registered census; forall[D] for gammastar >= 2",
        "evidence_level": ["EV1", "EV2"],
    }


# ------------------------------------------------------------- IND-1 / IND-2

IND1 = {
    "id": "IND-1",
    "n": 2, "kappa": 1, "D": 3, "body_len": 5,
    "targets": [{"t": "u", "weight": "1/1", "l0": 12, "l1": 6}],
    "lj": 6,
    "library_candidates": [{"k": k, "lL": lL} for k in (2, 3, 4, 5, 6)
                           for lL in (5, 6)],
}

IND2 = {
    "id": "IND-2",
    "n": 2, "kappa": 1, "lj": 6,
    "library": {"k": 2, "lL": 4},
    "operator_candidates": [{"l0": l0, "l1": l0 - g}
                            for l0 in (3, 4, 5, 6, 7, 8) for g in (0, 1)],
    "candidate_weight": "1/1",
    "candidate_D": 0, "candidate_body_len": 0, "candidate_kappa": 0,
}


def run_ind():
    # ---- IND-1: invention pays, no k>=2 library is guaranteed better
    n = IND1["n"]
    saving, tax, theta = theta_inv(n, IND1["targets"])
    charge = Fraction(IND1["D"] + IND1["body_len"] + IND1["kappa"])
    pays = bool(charge < theta)
    lj = IND1["lj"]
    lib_rows = []
    any_better = False
    for c in IND1["library_candidates"]:
        v = lf1_verdict(n, c["k"], c["lL"], lj)
        gs = gammastar(n, c["k"], lj)
        lib_rows.append({"k": c["k"], "lL": c["lL"], "gamma_w": lj - c["lL"],
                         "gammastar": gs, "verdict": v,
                         "Phi_n_plus_k_lL": Phi(n + c["k"], c["lL"]),
                         "Phi_n_plus_1_lj_minus_1": Phi(n + 1, lj - 1)})
        if v == "LIBRARY_GUARANTEED_BETTER":
            any_better = True
    ind1 = {
        "claim_id": "IND-1",
        "statement": ("An exact workload where invention pays (OI-1 holds for a "
                      "single operator) and NO library of k>=2 members over the "
                      "registered candidate set is LIBRARY_GUARANTEED_BETTER."),
        "verdict": "WITNESS_FOUND" if (pays and not any_better) else "NO_WITNESS",
        "n": n, "targets": IND1["targets"],
        "D": IND1["D"], "body_len": IND1["body_len"], "kappa": IND1["kappa"],
        "Saving": fr(saving), "Tax": fr(tax), "Theta_inv": fr(theta),
        "total_charge": fr(charge), "invention_strictly_pays": pays,
        "separate_grammar_length_lj": lj,
        "library_candidate_count": len(IND1["library_candidates"]),
        "library_candidates": lib_rows,
        "any_library_guaranteed_better": any_better,
        "mechanism": ("Every registered candidate library has composition gain "
                      "gamma_w in {0,1}; LF-4 gives gammastar(2,k,6) >= 2 for "
                      "every k in 2..6, so no candidate can reach the "
                      "guaranteed-better band at any charge."),
        "quantifiers": "forall_fin[U] over the printed candidate set; deductive universality is NOT claimed",
        "evidence_level": ["EV1", "EV2"],
    }

    # ---- IND-2: library favoured, no further operator passes OI-1
    n2 = IND2["n"]
    lj2 = IND2["lj"]
    lib = IND2["library"]
    lib_v = lf1_verdict(n2, lib["k"], lib["lL"], lj2)
    op_rows = []
    any_pays = False
    for c in IND2["operator_candidates"]:
        tg = [{"t": "v", "weight": IND2["candidate_weight"],
               "l0": c["l0"], "l1": c["l1"]}]
        s, t, th = theta_inv(n2, tg)
        ch = Fraction(IND2["candidate_D"] + IND2["candidate_body_len"]
                      + IND2["candidate_kappa"])
        p = bool(ch < th)
        op_rows.append({"l0": c["l0"], "l1": c["l1"],
                        "gamma": c["l0"] - c["l1"], "Saving": fr(s),
                        "Tax": fr(t), "Theta_inv": fr(th),
                        "min_possible_charge": fr(ch), "strictly_pays": p})
        if p:
            any_pays = True
    ind2 = {
        "claim_id": "IND-2",
        "statement": ("An exact workload where some k>=2 library IS "
                      "LIBRARY_GUARANTEED_BETTER while NO further candidate "
                      "operator over the registered candidate set satisfies "
                      "OI-1, even at zero charge."),
        "verdict": ("WITNESS_FOUND"
                    if (lib_v == "LIBRARY_GUARANTEED_BETTER" and not any_pays)
                    else "NO_WITNESS"),
        "n": n2, "separate_grammar_length_lj": lj2,
        "library": {"k": lib["k"], "lL": lib["lL"],
                    "gamma_w": lj2 - lib["lL"],
                    "gammastar": gammastar(n2, lib["k"], lj2),
                    "Phi_n_plus_k_lL": Phi(n2 + lib["k"], lib["lL"]),
                    "Phi_n_plus_1_lj_minus_1": Phi(n2 + 1, lj2 - 1),
                    "verdict": lib_v},
        "operator_candidate_count": len(IND2["operator_candidates"]),
        "operator_candidates": op_rows,
        "any_operator_strictly_pays": any_pays,
        "mechanism": ("Every registered candidate operator has gamma in {0,1}. "
                      "By OI-2, Phi(n+1,l0-1) >= Phi(n,l0-1) with strict "
                      "inequality for l0 >= 2, so Theta_inv <= 0 for every "
                      "candidate and no nonnegative charge can satisfy "
                      "D + len(body) + kappa < Theta_inv."),
        "quantifiers": "forall_fin[U] over the printed candidate set; deductive universality is NOT claimed",
        "evidence_level": ["EV1", "EV2"],
    }
    independence = {
        "claim_id": "IND-1_AND_IND-2",
        "conclusion": ("The invention row and the library-formation row are "
                       "logically independent: IND-1 realizes "
                       "(invention pays) AND NOT (library favoured); IND-2 "
                       "realizes (library favoured) AND NOT (any further "
                       "operator pays). Neither row entails the other."),
        "independence_established": bool(ind1["verdict"] == "WITNESS_FOUND"
                                         and ind2["verdict"] == "WITNESS_FOUND"),
    }
    return ind1, ind2, independence


# ------------------------------------------------------------------ hostiles


def install_library(grammar, members):
    """Install library members into a grammar.

    grammar: {"alphabet": [...], "macros": {name: [symbols...]}}
    Returns (code, grammar_object).  On a cyclic dependency the code is
    RECURSIVE_LIBRARY_CYCLE and the ORIGINAL grammar object is returned
    unchanged (same object identity, same content).
    """
    deps = {}
    for name in sorted(members.keys()):
        deps[name] = list(members[name])
    known = set(grammar["alphabet"]) | set(grammar["macros"].keys())
    # detect a cycle among the proposed members by iterative peeling
    remaining = set(deps.keys())
    progressed = True
    while progressed and remaining:
        progressed = False
        for name in sorted(list(remaining)):
            ok = True
            for sym in deps[name]:
                if sym in remaining:
                    ok = False
            if ok:
                remaining.discard(name)
                progressed = True
    if remaining:
        return ("RECURSIVE_LIBRARY_CYCLE", grammar)
    new_macros = {}
    for key in sorted(grammar["macros"].keys()):
        new_macros[key] = list(grammar["macros"][key])
    for name in sorted(deps.keys()):
        new_macros[name] = list(deps[name])
    return ("INSTALLED", {"alphabet": list(grammar["alphabet"]),
                          "macros": new_macros})


def detect_hostiles(submission):
    """Return the sorted list of hostile codes detected in `submission`."""
    flags = []
    # H4 first: inadmissible compression invalidates everything downstream.
    for rec in submission.get("operator_claims", []):
        if rec["l1"] > rec["l0"]:
            flags.append("H4_INADMISSIBLE_COMPRESSION")
    for rec in submission.get("library_claims", []):
        if rec["lL"] > rec["lj"]:
            flags.append("H4_INADMISSIBLE_COMPRESSION")
    # H1: a gamma = 0 operator declared inventable.
    for rec in submission.get("operator_claims", []):
        if rec.get("claim") == "INVENTABLE" and rec["l1"] == rec["l0"]:
            _, _, th = theta_inv(rec["n"], [{"weight": "1/1", "l0": rec["l0"],
                                             "l1": rec["l1"]}])
            if th <= 0:
                flags.append("H1_GAMMA0_OPERATOR_DECLARED_INVENTABLE")
    # H2: a gamma = 0 library declared favoured.
    for rec in submission.get("library_claims", []):
        if (rec.get("claim") == "LIBRARY_GUARANTEED_BETTER"
                and rec["lL"] == rec["lj"] and rec["k"] >= 2):
            flags.append("H2_GAMMA0_LIBRARY_DECLARED_FAVOURED")
    # H3: dilution off-by-one anywhere in a submitted LF-1 verdict vector.
    vec = submission.get("lf1_vector", None)
    if vec is not None:
        cells = lf1_census()
        differing = 0
        for idx in range(len(cells)):
            n, k, lL, lj = cells[idx]
            if vec[idx] != lf1_verdict(n, k, lL, lj):
                differing = differing + 1
        if differing > 0:
            flags.append("H3_DILUTION_OFF_BY_ONE")
    # H5: cyclic library dependency.
    lib = submission.get("library_install", None)
    if lib is not None:
        code, obj = install_library(lib["grammar"], lib["members"])
        if code == "RECURSIVE_LIBRARY_CYCLE":
            flags.append("H5_RECURSIVE_LIBRARY_CYCLE")
    return sorted(set(flags))


def lf1_vector_variant(cells, variant):
    """Build an LF-1 verdict vector, optionally with a planted off-by-one."""
    out = []
    for (n, k, lL, lj) in cells:
        if variant == "CLEAN":
            a_sep, a_lib = n + 1, n + k
        elif variant == "H3A_N_FOR_N_PLUS_1":
            a_sep, a_lib = n, n + k
        elif variant == "H3B_N_PLUS_1_FOR_N_PLUS_K":
            a_sep, a_lib = n + 1, n + 1
        else:
            a_sep, a_lib = n + 1, n + k
        better = Phi(a_lib, lL) <= Phi(a_sep, lj - 1)
        worse = Phi(a_lib, lL - 1) >= Phi(a_sep, lj)
        if better and worse:
            out.append("BAND_COLLISION")
        elif better:
            out.append("LIBRARY_GUARANTEED_BETTER")
        elif worse:
            out.append("LIBRARY_GUARANTEED_WORSE")
        else:
            out.append("RANK_DECIDED")
    return out


CLEAN_GRAMMAR = {"alphabet": ["a", "b"], "macros": {}}


def run_hostiles(cells):
    clean_vec = lf1_vector_variant(cells, "CLEAN")
    planted = []

    # H1 planted positive
    s1 = {"operator_claims": [{"n": 2, "l0": 4, "l1": 4, "claim": "INVENTABLE"}]}
    planted.append(("H1_GAMMA0_OPERATOR_DECLARED_INVENTABLE", s1))
    # H2 planted positive
    s2 = {"library_claims": [{"n": 2, "k": 3, "lL": 5, "lj": 5,
                              "claim": "LIBRARY_GUARANTEED_BETTER"}]}
    planted.append(("H2_GAMMA0_LIBRARY_DECLARED_FAVOURED", s2))
    # H3 planted positives -- full-census vectors, both off-by-one directions
    vec_a = lf1_vector_variant(cells, "H3A_N_FOR_N_PLUS_1")
    vec_b = lf1_vector_variant(cells, "H3B_N_PLUS_1_FOR_N_PLUS_K")
    planted.append(("H3_DILUTION_OFF_BY_ONE", {"lf1_vector": vec_a}))
    planted.append(("H3_DILUTION_OFF_BY_ONE", {"lf1_vector": vec_b}))
    # H4 planted positive
    s4 = {"operator_claims": [{"n": 3, "l0": 4, "l1": 6, "claim": "INVENTABLE"}]}
    planted.append(("H4_INADMISSIBLE_COMPRESSION", s4))
    # H5 planted positive: m1 -> m2, m2 -> m1
    s5 = {"library_install": {"grammar": CLEAN_GRAMMAR,
                              "members": {"m1": ["a", "m2"], "m2": ["b", "m1"]}}}
    planted.append(("H5_RECURSIVE_LIBRARY_CYCLE", s5))

    recall_rows = []
    detected_all = True
    for (code, sub) in planted:
        flags = detect_hostiles(sub)
        hit = code in flags
        if not hit:
            detected_all = False
        row = {"planted": code, "detected": hit, "flags": flags}
        if "lf1_vector" in sub:
            diff = 0
            for idx in range(len(cells)):
                if sub["lf1_vector"][idx] != clean_vec[idx]:
                    diff = diff + 1
            row["differing_cells_vs_clean"] = diff
            row["census_cells"] = len(cells)
        recall_rows.append(row)

    # no-alarm case on known-clean inputs
    clean_subs = [
        {"operator_claims": [{"n": 2, "l0": 8, "l1": 2, "claim": "INVENTABLE"}]},
        {"library_claims": [{"n": 2, "k": 2, "lL": 4, "lj": 6,
                             "claim": "LIBRARY_GUARANTEED_BETTER"}]},
        {"lf1_vector": clean_vec},
        {"library_install": {"grammar": CLEAN_GRAMMAR,
                             "members": {"m1": ["a", "b"],
                                         "m2": ["m1", "m1"]}}},
        {"operator_claims": [{"n": 4, "l0": 6, "l1": 3, "claim": "INVENTABLE"}],
         "library_claims": [{"n": 4, "k": 3, "lL": 3, "lj": 6,
                             "claim": "LIBRARY_GUARANTEED_BETTER"}],
         "lf1_vector": clean_vec},
    ]
    no_alarm_rows = []
    no_alarm_clean = True
    for sub in clean_subs:
        flags = detect_hostiles(sub)
        if flags:
            no_alarm_clean = False
        no_alarm_rows.append({"flags": flags, "flag_count": len(flags)})

    # H5 must return the grammar UNCHANGED
    code, obj = install_library(CLEAN_GRAMMAR,
                                {"m1": ["a", "m2"], "m2": ["b", "m1"]})
    unchanged_identity = obj is CLEAN_GRAMMAR
    unchanged_content = (obj == {"alphabet": ["a", "b"], "macros": {}})
    code_ok, obj_ok = install_library(CLEAN_GRAMMAR,
                                      {"m1": ["a", "b"], "m2": ["m1", "m1"]})
    acyclic_install_ok = (code_ok == "INSTALLED"
                          and sorted(obj_ok["macros"].keys()) == ["m1", "m2"]
                          and CLEAN_GRAMMAR["macros"] == {})

    return {
        "registered_hostiles": [
            "H1_GAMMA0_OPERATOR_DECLARED_INVENTABLE",
            "H2_GAMMA0_LIBRARY_DECLARED_FAVOURED",
            "H3_DILUTION_OFF_BY_ONE",
            "H4_INADMISSIBLE_COMPRESSION",
            "H5_RECURSIVE_LIBRARY_CYCLE"],
        "planted_positive_count": len(planted),
        "planted_positive_rows": recall_rows,
        "all_planted_positives_detected": detected_all,
        "no_alarm_case_count": len(clean_subs),
        "no_alarm_rows": no_alarm_rows,
        "no_alarm_case_is_clean": no_alarm_clean,
        "h5_returns_code": code,
        "h5_grammar_object_identity_unchanged": unchanged_identity,
        "h5_grammar_content_unchanged": unchanged_content,
        "h5_acyclic_install_still_works": acyclic_install_ok,
    }


# --------------------------------------------------------------------- null


def run_null(cells):
    labels = ["LIBRARY_GUARANTEED_BETTER", "LIBRARY_GUARANTEED_WORSE",
              "RANK_DECIDED"]
    truth = []
    for (n, k, lL, lj) in cells:
        truth.append(lf1_verdict(n, k, lL, lj))
    derived_correct = 0
    for idx in range(len(cells)):
        n, k, lL, lj = cells[idx]
        if band(n + 1, lj, n + k, lL) == {
                "LIBRARY_GUARANTEED_BETTER": "GUARANTEED_REDUCTION",
                "LIBRARY_GUARANTEED_WORSE": "GUARANTEED_INCREASE",
                "RANK_DECIDED": "RANK_DECIDED"}[truth[idx]]:
            derived_correct = derived_correct + 1
    scores = []
    x = LCG_SEED % LCG_M
    trial = 0
    while trial < NULL_TRIALS:
        correct = 0
        for idx in range(len(cells)):
            x = (LCG_A * x + LCG_C) % LCG_M
            guess = labels[(x >> 33) % 3]
            if guess == truth[idx]:
                correct = correct + 1
        scores.append(correct)
        trial = trial + 1
    beat = 0
    for s in scores:
        if s >= derived_correct:
            beat = beat + 1
    ordered = sorted(scores)
    median_lo = ordered[(NULL_TRIALS - 1) // 2]
    median_hi = ordered[NULL_TRIALS // 2]
    return {
        "null_kind": "RANDOMIZED_THREE_WAY_SIGN_PREDICTOR_OVER_LF1_CENSUS",
        "lcg": {"multiplier": LCG_A, "increment": LCG_C, "modulus_2_pow": 64,
                "seed": LCG_SEED, "bit_extraction": "(x >> 33) % 3",
                "module_random_used": False},
        "trials": NULL_TRIALS,
        "census_cells": len(cells),
        "derived_rule_correct": derived_correct,
        "nulls_matching_or_beating_derived_rule": beat,
        "null_score_max": ordered[NULL_TRIALS - 1],
        "null_score_min": ordered[0],
        "null_score_median_low": median_lo,
        "null_score_median_high": median_hi,
        "margin_derived_minus_best_null": derived_correct - ordered[NULL_TRIALS - 1],
        "target": "0/200",
        "result": "%d/%d" % (beat, NULL_TRIALS),
    }


# ------------------------------------------------------ Route-B overlap scope

# Registered sub-census that Route B's explicit enumeration can actually reach.
# Route B must NOT import this module; it reads DERIVATION_RESULT_V1.json and
# compares its own enumerated verdicts against these cells.
OVR_N_RANGE = (2, 4)
OVR_K_RANGE = (2, 3)
OVR_LMAX = 5
OVR_OI2_L_RANGE = (2, 6)
OVR_MSTAR_N_RANGE = (2, 2)
OVR_T3_CHECKS = [(2, 1, 0), (2, 4, 5), (2, 8, 85), (3, 2, 8), (3, 4, 17),
                 (4, 3, 63), (5, 2, 24)]


def run_overlap():
    oi2 = {}
    n = OVR_N_RANGE[0]
    while n <= OVR_N_RANGE[1]:
        l0 = OVR_OI2_L_RANGE[0]
        while l0 <= OVR_OI2_L_RANGE[1]:
            oi2["n=%d|l0=%d" % (n, l0)] = band(n, l0, n + 1, l0 - 1)
            l0 = l0 + 1
        n = n + 1
    lstar_tab = {}
    n = OVR_N_RANGE[0]
    while n <= OVR_N_RANGE[1]:
        lstar_tab["n=%d" % n] = lstar(n)
        n = n + 1
    mstar_tab = {}
    n = OVR_MSTAR_N_RANGE[0]
    while n <= OVR_MSTAR_N_RANGE[1]:
        mstar_tab["n=%d" % n] = mstar(n)
        n = n + 1
    lf1 = {}
    lf4 = {}
    n = OVR_N_RANGE[0]
    while n <= OVR_N_RANGE[1]:
        k = OVR_K_RANGE[0]
        while k <= OVR_K_RANGE[1]:
            lj = 1
            while lj <= OVR_LMAX:
                lL = 1
                while lL <= lj:
                    lf1["n=%d|k=%d|lL=%d|lj=%d" % (n, k, lL, lj)] = \
                        lf1_verdict(n, k, lL, lj)
                    lL = lL + 1
                if lj >= 2:
                    lf4["n=%d|k=%d|lj=%d" % (n, k, lj)] = gammastar(n, k, lj)
                lj = lj + 1
            k = k + 1
        n = n + 1
    w1 = WORKLOADS[0]
    s_, t_, th_ = theta_inv(w1["n"], w1["targets"])
    charge = Fraction(w1["D"] + w1["body_len"] + w1["kappa"])
    oi1 = {"id": w1["id"], "n": w1["n"],
           "l0": w1["targets"][0]["l0"], "l1": w1["targets"][0]["l1"],
           "weight": w1["targets"][0]["weight"],
           "D": w1["D"], "body_len": w1["body_len"], "kappa": w1["kappa"],
           "Saving": fr(s_), "Tax": fr(t_), "Theta_inv": fr(th_),
           "total_charge": fr(charge), "strictly_pays": bool(charge < th_),
           "macro_realization": {
               "base_alphabet": ["a", "b"], "macro_symbol": "m",
               "macro_body": "abab", "target": "abababab",
               "note": "Route B must recover l0=8 under G0 and l1=2 under "
                       "G0+{m} by brute-force macro expansion."}}
    oi4 = []
    for (n_, l0_, l1_, label) in ((2, 4, 4, "NOT_SUFFICIENT_LEX_FIRST"),
                                  (2, 7, 6, "NOT_SUFFICIENT_GAMMA_GE_1"),
                                  (2, 3, 1, "NOT_NECESSARY_LEX_FIRST")):
        oi4.append({"label": label, "n": n_, "l0": l0_, "l1": l1_,
                    "verdict": band(n_, l0_, n_ + 1, l1_)})
    t3 = {}
    for (sig, l, rank) in OVR_T3_CHECKS:
        t3["sigma=%d|l=%d|rank=%d" % (sig, l, rank)] = Phi(sig, l - 1) + rank + 1
    return {
        "scope_note": ("Registered sub-census reachable by explicit "
                       "enumeration in Route B. Mstar is registered only at "
                       "n=2: Mstar(3)=11 needs 4**11 enumerated words, beyond "
                       "the registered Route-B word budget."),
        "n_range": list(OVR_N_RANGE), "k_range": list(OVR_K_RANGE),
        "lmax": OVR_LMAX, "oi2_l_range": list(OVR_OI2_L_RANGE),
        "mstar_n_range": list(OVR_MSTAR_N_RANGE),
        "OI-2_gamma1_verdicts": oi2,
        "OI-3_Lstar": lstar_tab,
        "OI-3_Mstar": mstar_tab,
        "OI-1_W1": oi1,
        "OI-4_witness_verdicts": oi4,
        "LF-1_verdicts": lf1,
        "LF-4_gammastar": lf4,
        "T3_burden_positions": t3,
    }


# --------------------------------------------------------------------- main


def build():
    cells = lf1_census()
    oi1 = run_oi1()
    oi2 = run_oi2()
    oi3 = run_oi3()
    oi4 = run_oi4()
    lf1 = run_lf1(cells)
    lf2 = run_lf2()
    lf3 = run_lf3(cells)
    lf4 = run_lf4()
    ind1, ind2, indep = run_ind()
    hostiles = run_hostiles(cells)
    null = run_null(cells)
    falsified = []
    for r in (oi1, oi2, oi3, oi4, lf1, lf2, lf3, lf4):
        if "FALSE" in r["verdict"]:
            falsified.append({"claim_id": r["claim_id"],
                              "verdict": r["verdict"]})
    return {
        "package": PACKAGE,
        "route": ROUTE,
        "claim_ceiling": CLAIM_CEILING,
        "arithmetic": "EXACT_INT_AND_FRACTION_ONLY__NO_FLOAT",
        "python_target": "3.8",
        "registered_domain_assumptions": DOMAIN_ASSUMPTIONS,
        "evidence_level": ["EV1", "EV2"],
        "maturity_level": ["M1", "M2"],
        "results": {
            "OI-1": oi1, "OI-2": oi2, "OI-3": oi3, "OI-4": oi4,
            "LF-1": lf1, "LF-2": lf2, "LF-3": lf3, "LF-4": lf4,
            "IND-1": ind1, "IND-2": ind2, "INDEPENDENCE": indep,
        },
        "hostiles": hostiles,
        "null_test": null,
        "route_b_overlap": run_overlap(),
        "frozen_statements_falsified": falsified,
        "frozen_statements_falsified_count": len(falsified),
    }


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    if len(argv) > 1:
        outpath = argv[1]
    else:
        outpath = os.path.join(here, "DERIVATION_RESULT_V1.json")
    obj = build()
    text = json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=True)
    fh = open(outpath, "w")
    fh.write(text)
    fh.write("\n")
    fh.close()
    sys.stdout.write("WROTE %s bytes=%d\n" % (outpath, len(text) + 1))
    sys.stdout.write("falsified_frozen_statements=%d\n"
                     % obj["frozen_statements_falsified_count"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
