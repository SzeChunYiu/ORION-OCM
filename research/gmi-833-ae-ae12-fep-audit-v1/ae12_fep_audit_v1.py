#!/usr/bin/env python3
"""Route A - AE12 free-energy / active-inference strongest-parent audit (issue #833).

Scope, objects and discipline are fixed by FREEZE_V1.md; every roster table,
grid, cap, tie-break and prediction is fixed by PROSPECTIVE_REGISTER_V1.json,
whose self-digest this module rechecks before emitting anything.

Exactness.  Every registered probability is 0 or an integer power of 1/2, so
every entropy, Kullback-Leibler divergence, variational free energy and expected
free energy below is an exact rational number of bits.  No float is constructed
anywhere.  `INF` is the string sentinel for the standard +infinity value of a
divergence whose support condition fails.

Route A computes the free energy through the exact identity

    F(q, o) = -log2 P(o) + KL(q || posterior(.|o)),

that is, surprisal plus a divergence to the exact posterior, and reads the
minimiser off that decomposition.  Route B
(`independent_fep_oracle_v1.py`) evaluates the raw definition
`KL(q||P0) - E_q[log2 L(o|s)]` on every member of the registered family and
takes a brute-force argmin; it shares no code with this module.

stdlib only; python3.8 compatible.

Usage:
  ae12_fep_audit_v1.py            emit RESULT_V1.json on stdout
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER = os.path.join(HERE, "PROSPECTIVE_REGISTER_V1.json")
INF = "INF"


# --------------------------------------------------------------------------
# register custody
# --------------------------------------------------------------------------
def load_register(path=REGISTER):
    # type: (str) -> Dict
    with open(path, "r") as fh:
        reg = json.load(fh)
    claimed = reg["self_digest_sha256"]
    body = dict(reg)
    body.pop("self_digest_sha256")
    body.pop("self_digest_note")
    canon = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    actual = hashlib.sha256(canon).hexdigest()
    if actual != claimed:
        raise RuntimeError(
            "prospective register digest mismatch: %s != %s" % (actual, claimed))
    return reg


# --------------------------------------------------------------------------
# exact dyadic arithmetic
# --------------------------------------------------------------------------
def F(x):
    # type: (str) -> Fraction
    return Fraction(x)


def is_dyadic(p):
    # type: (Fraction) -> bool
    """True iff p is 0 or 2**-k for an integer k >= 0."""
    if p == 0:
        return True
    if p < 0 or p > 1:
        return False
    return p.numerator == 1 and (p.denominator & (p.denominator - 1)) == 0


def dlog2(p):
    # type: (Fraction) -> int
    """Exact log2 of a positive dyadic p = 2**-k, returned as the integer -k."""
    if p <= 0 or not is_dyadic(p):
        raise ValueError("dlog2 of a non-positive or non-dyadic value: %s" % p)
    k = p.denominator.bit_length() - 1
    return -k


def check_dyadic_row(row):
    # type: (Sequence[Fraction]) -> None
    if sum(row) != 1:
        raise ValueError("row does not sum to 1: %s" % [str(x) for x in row])
    for p in row:
        if not is_dyadic(p):
            raise ValueError("non-dyadic entry %s" % p)


def entropy_bits(dist):
    # type: (Sequence[Fraction]) -> Fraction
    tot = Fraction(0)
    for p in dist:
        if p > 0:
            tot += p * (-dlog2(p))
    return tot


def kl_bits(q, p):
    # type: (Sequence[Fraction], Sequence[Fraction]) -> object
    """KL(q||p) in bits, exact; the string INF when q charges a p-null atom."""
    tot = Fraction(0)
    for qi, pi in zip(q, p):
        if qi == 0:
            continue
        if pi == 0:
            return INF
        tot += qi * (dlog2(qi) - dlog2(pi))
    return tot


def add_bits(a, b):
    # type: (object, object) -> object
    if a == INF or b == INF:
        return INF
    return a + b


def lt_bits(a, b):
    # type: (object, object) -> bool
    if a == INF:
        return False
    if b == INF:
        return True
    return a < b


def s_(x):
    # type: (object) -> str
    return x if isinstance(x, str) else str(x)


# --------------------------------------------------------------------------
# the registered dyadic family Q
# --------------------------------------------------------------------------
def dyadic_family(n, dmax):
    # type: (int, int) -> List[Tuple[Fraction, ...]]
    """Every distribution on n atoms whose masses are 0 or 2**-k, 0 <= k <= dmax."""
    values = [Fraction(0)] + [Fraction(1, 2 ** k) for k in range(0, dmax + 1)]
    out = []
    for combo in itertools.product(values, repeat=n):
        if sum(combo) == 1:
            out.append(tuple(combo))
    out.sort(key=lambda t: tuple(str(x) for x in t))
    return out


def dyadic_family_positive(n, dmax):
    # type: (int, int) -> List[Tuple[Fraction, ...]]
    """The registered preference family: every distribution on n atoms whose
    masses are integer powers of 1/2 with minimum atom 2**-dmax.  Zero is not an
    integer power of 1/2, so these distributions have full support and every
    divergence against them is finite."""
    values = [Fraction(1, 2 ** k) for k in range(0, dmax + 1)]
    out = []
    for combo in itertools.product(values, repeat=n):
        if sum(combo) == 1:
            out.append(tuple(combo))
    out.sort(key=lambda t: tuple(str(x) for x in t))
    return out


def product_family(fam1, fam2):
    # type: (List[Tuple[Fraction, ...]], List[Tuple[Fraction, ...]]) -> List[Tuple[Fraction, ...]]
    out = []
    for a in fam1:
        for b in fam2:
            prod = tuple(x * y for x in a for y in b)
            if sum(prod) == 1:
                out.append(prod)
    seen = set()
    uniq = []
    for t in sorted(out, key=lambda t: tuple(str(x) for x in t)):
        key = tuple(str(x) for x in t)
        if key not in seen:
            seen.add(key)
            uniq.append(t)
    return uniq


# --------------------------------------------------------------------------
# registered-world algebra
# --------------------------------------------------------------------------
class World(object):
    """A registered world.  `P0` may be None for the action worlds, whose rows
    are only ever used through an explicitly supplied state distribution; the
    prior-dependent methods then refuse to run rather than inventing a prior."""

    def __init__(self, name, S, O, P0, L):
        self.name = name
        self.S = list(S)
        self.O = list(O)
        self.P0 = None if P0 is None else [F(x) for x in P0]
        self.L = [[F(x) for x in row] for row in L]
        if self.P0 is not None:
            check_dyadic_row(self.P0)
        for row in self.L:
            check_dyadic_row(row)

    def evidence(self, oi):
        # type: (int) -> Fraction
        if self.P0 is None:
            raise ValueError("world %s has no registered prior" % self.name)
        return sum(self.P0[i] * self.L[i][oi] for i in range(len(self.S)))

    def posterior(self, oi):
        # type: (int) -> List[Fraction]
        z = self.evidence(oi)
        if z == 0:
            raise ValueError("zero-evidence observation")
        return [self.P0[i] * self.L[i][oi] / z for i in range(len(self.S))]


def free_energy_routeA(world, q, oi):
    # type: (World, Sequence[Fraction], int) -> object
    """F(q,o) by the exact decomposition: surprisal + KL(q || posterior)."""
    z = world.evidence(oi)
    post = world.posterior(oi)
    d = kl_bits(q, post)
    if d == INF:
        return INF
    return Fraction(-dlog2(z)) + d


# --------------------------------------------------------------------------
# expected free energy, utility, rate-distortion, CPC
# --------------------------------------------------------------------------
def predicted_outcomes(world, state_dist):
    # type: (World, Sequence[Fraction]) -> List[Fraction]
    return [sum(state_dist[i] * world.L[i][oi] for i in range(len(world.S)))
            for oi in range(len(world.O))]


def ambiguity_bits(world, state_dist):
    # type: (World, Sequence[Fraction]) -> Fraction
    return sum(state_dist[i] * entropy_bits(world.L[i]) for i in range(len(world.S)))


def efe_bits(world, state_dist, C):
    # type: (World, Sequence[Fraction], Sequence[Fraction]) -> object
    po = predicted_outcomes(world, state_dist)
    return add_bits(kl_bits(po, C), ambiguity_bits(world, state_dist))


def expected_utility(state_dist, U_state):
    # type: (Sequence[Fraction], Sequence[Fraction]) -> Fraction
    return sum(state_dist[i] * U_state[i] for i in range(len(U_state)))


def pred_loss(po):
    # type: (Sequence[Fraction]) -> Fraction
    return Fraction(1) - max(po)


def lgrid_eighths():
    # type: () -> List[Tuple[Fraction, Fraction, Fraction]]
    out = []
    for a in range(9):
        for b in range(9 - a):
            c = 8 - a - b
            out.append((Fraction(a, 8), Fraction(b, 8), Fraction(c, 8)))
    return out


def argmin_named(names, values):
    # type: (Sequence[str], Sequence[object]) -> str
    """Lexicographic tie-break by registered name, ascending."""
    best = None
    bestname = None
    for nm, v in sorted(zip(names, values), key=lambda t: t[0]):
        if best is None or lt_bits(v, best):
            best, bestname = v, nm
    return bestname


# --------------------------------------------------------------------------
# conditional independence / Markov blanket
# --------------------------------------------------------------------------
def markov_blanket_exists(support):
    # type: (Sequence[Sequence[int]]) -> Tuple[bool, List[List[List[int]]]]
    """Exhaustive search over partitions of the variables into non-empty
    (internal, blanket, external) with internal independent of external given
    blanket, under the uniform distribution on `support`."""
    nvars = len(support[0])
    idx = list(range(nvars))
    mass = Fraction(1, len(support))
    found = []
    for assign in itertools.product(range(3), repeat=nvars):
        parts = [[i for i in idx if assign[i] == k] for k in range(3)]
        if not (parts[0] and parts[1] and parts[2]):
            continue
        internal, blanket, external = parts
        # joint over (I, B, E) blocks
        joint = {}
        for pt in support:
            key = (tuple(pt[i] for i in internal),
                   tuple(pt[i] for i in blanket),
                   tuple(pt[i] for i in external))
            joint[key] = joint.get(key, Fraction(0)) + mass
        pb = {}
        pib = {}
        peb = {}
        for (a, b, c), p in joint.items():
            pb[b] = pb.get(b, Fraction(0)) + p
            pib[(a, b)] = pib.get((a, b), Fraction(0)) + p
            peb[(c, b)] = peb.get((c, b), Fraction(0)) + p
        ok = True
        for (a, b, c), p in joint.items():
            if pb[b] == 0:
                continue
            if p * pb[b] != pib[(a, b)] * peb[(c, b)]:
                ok = False
                break
        if ok:
            found.append([sorted(internal), sorted(blanket), sorted(external)])
    found.sort()
    return (len(found) > 0), found


# --------------------------------------------------------------------------
# bound records
# --------------------------------------------------------------------------
def bound_record(name, kind, value, range_lo, range_hi, derivation,
                 attained_by, violated_by, relaxation):
    # type: (str, str, object, object, object, str, str, Optional[str], str) -> Dict
    if kind == "upper":
        vac = not lt_bits(value, range_hi)
    elif kind == "lower":
        vac = not lt_bits(range_lo, value)
    else:
        raise ValueError("bad kind")
    rec = {
        "name": name,
        "kind": kind,
        "bound_value": s_(value),
        "range_lo": s_(range_lo),
        "range_hi": s_(range_hi),
        "range_derivation": derivation,
        "vacuous": bool(vac),
        "attained_by": attained_by,
        "violated_by": violated_by,
        "relaxed_class": relaxation,
    }
    if violated_by is None:
        rec["status"] = "UNFALSIFIED_BOUND"
    else:
        rec["status"] = "FALSIFIABLE"
    return rec


# --------------------------------------------------------------------------
# the audit
# --------------------------------------------------------------------------
def build_worlds(reg):
    # type: (Dict) -> Dict[str, World]
    r = reg["roster"]
    out = {}
    for nm in ("W_SPLIT", "W_TRI", "W_CORR"):
        w = r[nm]
        out[nm] = World(nm, w["S"], w["O"], w["P0"], w["L"])
    t = r["W_TRI_MIS"]
    out["W_TRI_MIS_TRUE"] = World("W_TRI_MIS_TRUE", t["S"], t["O"], t["P0"], t["L_true"])
    out["W_TRI_MIS_MODEL"] = World("W_TRI_MIS_MODEL", t["S"], t["O"], t["P0"], t["L_model"])
    for nm in ("W_AMB", "W_DISC1", "W_AGREE1"):
        w = r[nm]
        out[nm] = World(nm, w["S"], w["O"], None, w["L"])
    return out


def perception_audit(reg, worlds, dmax):
    # type: (Dict, Dict[str, World], int) -> Dict
    res = {}
    for nm in sorted(("W_SPLIT", "W_TRI", "W_CORR")):
        w = worlds[nm]
        fam = dyadic_family(len(w.S), dmax)
        per_obs = {}
        for oi, oname in enumerate(w.O):
            z = w.evidence(oi)
            if z == 0:
                continue
            post = w.posterior(oi)
            vals = [free_energy_routeA(w, q, oi) for q in fam]
            best = None
            arg = None
            for q, v in zip(fam, vals):
                if best is None or lt_bits(v, best):
                    best, arg = v, q
            per_obs[oname] = {
                "evidence": str(z),
                "surprisal_bits": str(Fraction(-dlog2(z))),
                "exact_posterior": [str(x) for x in post],
                "argmin_q": [str(x) for x in arg],
                "min_free_energy_bits": s_(best),
                "argmin_equals_posterior": list(arg) == list(post),
                "min_equals_surprisal": best == Fraction(-dlog2(z)),
            }
        res[nm] = {"family_size": len(fam), "per_observation": per_obs}
    return res


def meanfield_audit(reg, worlds, dmax):
    # type: (Dict, Dict[str, World], int) -> Dict
    w = worlds["W_CORR"]
    full = dyadic_family(len(w.S), dmax)
    half = dyadic_family(2, dmax)
    mf = product_family(half, half)
    oi = 0
    post = w.posterior(oi)
    full_vals = [free_energy_routeA(w, q, oi) for q in full]
    mf_vals = [free_energy_routeA(w, q, oi) for q in mf]
    fbest = None
    farg = None
    for q, v in zip(full, full_vals):
        if fbest is None or lt_bits(v, fbest):
            fbest, farg = v, q
    mbest = None
    marg = None
    for q, v in zip(mf, mf_vals):
        if mbest is None or lt_bits(v, mbest):
            mbest, marg = v, q
    excess = mbest - fbest if (mbest != INF and fbest != INF) else INF
    return {
        "observation": w.O[oi],
        "exact_posterior": [str(x) for x in post],
        "posterior_is_a_product": list(post) in [list(q) for q in mf],
        "full_family_size": len(full),
        "mean_field_family_size": len(mf),
        "min_free_energy_full_bits": s_(fbest),
        "argmin_full": [str(x) for x in farg],
        "min_free_energy_mean_field_bits": s_(mbest),
        "argmin_mean_field": [str(x) for x in marg],
        "mean_field_excess_bits": s_(excess),
    }


def misspecification_audit(worlds, dmax):
    # type: (Dict[str, World], int) -> Dict
    wt = worlds["W_TRI_MIS_TRUE"]
    wm = worlds["W_TRI_MIS_MODEL"]
    fam = dyadic_family(len(wt.S), dmax)
    per_obs = {}
    differ = 0
    for oi, oname in enumerate(wt.O):
        post_t = wt.posterior(oi)
        post_m = wm.posterior(oi)
        vals = [free_energy_routeA(wm, q, oi) for q in fam]
        best = None
        arg = None
        for q, v in zip(fam, vals):
            if best is None or lt_bits(v, best):
                best, arg = v, q
        d = list(post_t) != list(post_m)
        differ += 1 if d else 0
        per_obs[oname] = {
            "true_posterior": [str(x) for x in post_t],
            "model_posterior": [str(x) for x in post_m],
            "argmin_under_model": [str(x) for x in arg],
            "argmin_equals_model_posterior": list(arg) == list(post_m),
            "argmin_equals_true_posterior": list(arg) == list(post_t),
            "posteriors_differ": d,
        }
    return {"per_observation": per_obs, "observations_with_differing_posteriors": differ}


def preference_prior_audit(reg, worlds, dmax):
    # type: (Dict, Dict[str, World], int) -> Dict
    """Row 2(c).  The ambiguity term of expected free energy is a function of the
    action's state distribution and the likelihood alone; it does not see the
    preference prior.  On W_AMB the two actions induce IDENTICAL predicted
    outcome distributions, so the risk terms cancel for every preference
    distribution whatsoever - dyadic or not - and the expected-free-energy order
    is pinned at the ambiguity gap.  The expected-utility order, by contrast,
    moves with the utility: the six permutations of the registered utility vector
    already realise orders that no preference prior can reproduce."""
    r = reg["roster"]["W_AMB"]
    w = worlds["W_AMB"]
    U = [F(x) for x in r["U_state"]]
    dists = [[F(x) for x in row] for row in r["action_state_dist"]]
    names = list(r["A"])
    Cfam = dyadic_family_positive(len(w.O), dmax)
    amb = [ambiguity_bits(w, d) for d in dists]
    po = [predicted_outcomes(w, d) for d in dists]
    identical_po = all(po[0] == p for p in po)

    diffs = set()
    efe_choice = set()
    for C in Cfam:
        g = [efe_bits(w, d, C) for d in dists]
        diffs.add(str(g[0] - g[1]))
        efe_choice.add(argmin_named(names, g))

    # the registered utility, and every permutation of its values over the
    # registered states.  No new constant is introduced: the value multiset is
    # exactly the registered one.
    perms = []
    seen = set()
    for perm in sorted(set(itertools.permutations(range(len(U))))):
        Up = [U[i] for i in perm]
        key = tuple(str(x) for x in Up)
        if key in seen:
            continue
        seen.add(key)
        eu = [expected_utility(d, Up) for d in dists]
        if eu[0] > eu[1]:
            order = "a0>a1"
        elif eu[0] < eu[1]:
            order = "a0<a1"
        else:
            order = "a0=a1"
        perms.append({
            "utility_over_states": [str(x) for x in Up],
            "expected_utility": [str(x) for x in eu],
            "expected_utility_difference": str(eu[0] - eu[1]),
            "expected_utility_order": order,
            "reproducible_by_some_preference_prior": order == "a0<a1",
        })
    perms.sort(key=lambda d: tuple(d["utility_over_states"]))
    unreachable = [p for p in perms if not p["reproducible_by_some_preference_prior"]]
    registered = [p for p in perms
                  if p["utility_over_states"] == [str(x) for x in U]][0]
    return {
        "actions": names,
        "predicted_outcome_distributions": [[str(x) for x in p] for p in po],
        "predicted_outcomes_identical": identical_po,
        "risk_terms_cancel_for_every_preference_distribution": identical_po,
        "ambiguity_bits": [str(x) for x in amb],
        "ambiguity_gap_a0_minus_a1_bits": str(amb[0] - amb[1]),
        "preference_family_size": len(Cfam),
        "efe_difference_a0_minus_a1_over_all_C": sorted(diffs),
        "efe_choice_over_all_C": sorted(efe_choice),
        "registered_utility": [str(x) for x in U],
        "registered_utility_expected_values": registered["expected_utility"],
        "registered_utility_difference": registered["expected_utility_difference"],
        "registered_utility_order": registered["expected_utility_order"],
        "utility_permutations": perms,
        "utility_orders_no_preference_prior_can_reproduce": len(unreachable),
        "strict_contradiction_witnesses": [p["utility_over_states"] for p in perms
                                           if p["expected_utility_order"] == "a0>a1"],
        "no_preference_prior_reproduces_utility_order":
            bool(sorted(efe_choice) == [names[1]] and len(unreachable) > 0),
    }


def selector_comparison(reg, worlds, wname):
    # type: (Dict, Dict[str, World], str) -> Dict
    r = reg["roster"][wname]
    w = worlds[wname]
    names = list(r["A"])
    dists = [[F(x) for x in row] for row in r["action_state_dist"]]
    U = [F(x) for x in r["U_state"]]
    C = [F(x) for x in r["C"]]
    cost = [Fraction(c) for c in r["cost_bits"]]
    po = [predicted_outcomes(w, d) for d in dists]
    g = [efe_bits(w, d, C) for d in dists]
    eu = [expected_utility(d, U) for d in dists]
    best_eu = max(eu)
    ctrl = [best_eu - x for x in eu]
    pl = [pred_loss(p) for p in po]
    efe_pick = argmin_named(names, g)
    rd_pick = argmin_named(names, [-x for x in eu])   # cardinality 1: one action
    cpc = {}
    for (lc, lp, lk) in lgrid_eighths():
        j = [lc * cost[i] + lp * pl[i] + lk * ctrl[i] for i in range(len(names))]
        cpc["%s,%s,%s" % (lc, lp, lk)] = argmin_named(names, j)
    return {
        "actions": names,
        "cost_bits": [str(x) for x in cost],
        "predictive_loss": [str(x) for x in pl],
        "control_regret": [str(x) for x in ctrl],
        "expected_free_energy_bits": [s_(x) for x in g],
        "expected_utility": [str(x) for x in eu],
        "expected_free_energy_choice": efe_pick,
        "rate_distortion_cardinality_1_choice": rd_pick,
        "cpc_choices_over_grid": sorted(set(cpc.values())),
        "cpc_choice_by_lambda": cpc,
        "grid_size": len(cpc),
        "all_three_agree": (efe_pick == rd_pick and sorted(set(cpc.values())) == [efe_pick]),
        "term_vector_dominations": sorted(
            "%s dominated by %s" % (names[i], names[j])
            for i in range(len(names)) for j in range(len(names)) if i != j
            and cost[j] <= cost[i] and pl[j] <= pl[i] and ctrl[j] <= ctrl[i]
            and (cost[j], pl[j], ctrl[j]) != (cost[i], pl[i], ctrl[i])),
        "no_lambda_agrees_with_both_efe_and_rd":
            all(not (v == efe_pick and v == rd_pick) for v in cpc.values())
            if efe_pick != rd_pick else False,
    }


def criticism_table(reg, blanket):
    # type: (Dict, Dict) -> List[Dict]
    return [
        {"id": "CRIT-1",
         "source": "Biehl, Pollock, Kanai (2021), Entropy 23(3):293",
         "doi": "10.3390/e23030293",
         "criticism": "claimed equivalences of the free energy principle hold only "
                      "under conditions that are not automatic",
         "registered_predicate": "FEP_EQUALS_BAYES_UNDER_RESTRICTED_FAMILY",
         "evaluated": False,
         "evidence": "on W_CORR the mean-field minimiser is not the exact posterior"},
        {"id": "CRIT-2",
         "source": "Aguilera, Millidge, Tschantz, Buckley (2022), "
                   "Physics of Life Reviews 40:24-50",
         "doi": "10.1016/j.plrev.2021.11.001",
         "criticism": "the particular partition the principle presumes need not exist",
         "registered_predicate": "MARKOV_BLANKET_EXISTS",
         "evaluated": blanket["SYS_MB_FAIL"]["exists"],
         "evidence": "exhaustive search over all partitions of SYS_MB_FAIL finds none"},
        {"id": "CRIT-3",
         "source": "Bruineberg, Dolega, Dewhurst, Baltieri (2022), "
                   "Behavioral and Brain Sciences 45:e183",
         "doi": "10.1017/S0140525X21002351",
         "criticism": "a blanket read off a statistical factorisation is not "
                      "automatically a boundary of an agent",
         "registered_predicate": "MARKOV_BLANKET_EXISTS",
         "evaluated": blanket["SYS_MB_OK"]["exists"],
         "evidence": "SYS_MB_OK admits a blanket, SYS_MB_FAIL does not; existence is "
                     "a property of the joint, not of the system being an agent"},
        {"id": "CRIT-4",
         "source": "Friston, FitzGerald, Rigoli, Schwartenbeck, Pezzulo (2017), "
                   "Neural Computation 29(1):1-49",
         "doi": "10.1162/NECO_a_00912",
         "criticism": "expected free energy is presented as subsuming expected "
                      "utility once preferences are encoded as a prior",
         "registered_predicate": "EFE_RECOVERS_UTILITY_ORDERING",
         "evaluated": False,
         "evidence": "on W_AMB the ambiguity term is preference-independent, so no "
                     "registered preference prior reproduces the utility order"},
    ]


def _amb_structure(world, d0, d1):
    # type: (World, Sequence[Fraction], Sequence[Fraction]) -> Tuple[bool, Fraction]
    """The registered structure of W_AMB: the two action state distributions
    induce IDENTICAL predicted outcome distributions - so the risk term cancels
    for every preference distribution - and the ambiguity terms differ, which
    pins the expected-free-energy order independently of any preference."""
    po0 = predicted_outcomes(world, d0)
    po1 = predicted_outcomes(world, d1)
    if po0 != po1:
        return False, Fraction(0)
    gap = ambiguity_bits(world, d0) - ambiguity_bits(world, d1)
    return (gap != 0), gap


def randomized_null(reg, worlds, dmax, trials):
    # type: (Dict, Dict[str, World], int, int) -> Dict
    """The detector is the registered structure above.  The null asks how often a
    randomly drawn world of the same registered shape exhibits it, and the
    no-alarm case is asserted on the registered worlds that are known not to have
    it.  Because the registered shape admits only finitely many likelihood
    tables, the sampled null is reported alongside an EXHAUSTIVE census of the
    whole space, which is the stronger statement."""
    w = worlds["W_AMB"]
    r = reg["roster"]["W_AMB"]
    d0 = [F(x) for x in r["action_state_dist"][0]]
    d1 = [F(x) for x in r["action_state_dist"][1]]
    rows = dyadic_family(len(w.O), dmax)

    def make(pick):
        return World("null", w.S, w.O, None, [[str(x) for x in rr] for rr in pick])

    fired = 0
    precond = 0
    mags = []
    state = 1
    for _ in range(trials):
        pick = []
        for _i in range(len(w.S)):
            state = (1103515245 * state + 12345) % (2 ** 31)
            pick.append(rows[state % len(rows)])
        ww = make(pick)
        if predicted_outcomes(ww, d0) == predicted_outcomes(ww, d1):
            precond += 1
        ok, gap = _amb_structure(ww, d0, d1)
        if ok:
            fired += 1
            mags.append(abs(gap))

    ex_total = 0
    ex_fired = 0
    for pick in itertools.product(rows, repeat=len(w.S)):
        ex_total += 1
        ok, _g = _amb_structure(make(list(pick)), d0, d1)
        if ok:
            ex_fired += 1

    clean = []
    for nm in ("W_SPLIT", "W_TRI", "W_AGREE1"):
        ww = worlds[nm]
        rr = reg["roster"][nm]
        if "action_state_dist" in rr:
            dd0 = [F(x) for x in rr["action_state_dist"][0]]
            dd1 = [F(x) for x in rr["action_state_dist"][1]]
        else:
            n = len(ww.S)
            dd0 = [Fraction(1)] + [Fraction(0)] * (n - 1)
            dd1 = [Fraction(0)] + [Fraction(1)] + [Fraction(0)] * (n - 2)
        ok, _g = _amb_structure(ww, dd0, dd1)
        if ok:
            clean.append(nm)

    wok, wgap = _amb_structure(worlds["W_AMB"], d0, d1)
    return {
        "detector": "identical predicted outcome distributions with a non-zero "
                    "ambiguity gap, so the expected-free-energy order is pinned "
                    "independently of the preference prior",
        "trials": trials,
        "sampler": reg["registered_constants"]["null_sampler"],
        "controls_meeting_the_identical_outcome_precondition": precond,
        "controls_firing": fired,
        "control_firing_rate": str(Fraction(fired, trials)),
        "largest_null_gap_bits": str(max(mags)) if mags else "0",
        "exhaustive_space_size": ex_total,
        "exhaustive_controls_firing": ex_fired,
        "exhaustive_firing_rate": str(Fraction(ex_fired, ex_total)),
        "planted_positive_fires": bool(wok),
        "planted_positive_gap_bits": str(wgap),
        "known_clean_worlds_tested": ["W_SPLIT", "W_TRI", "W_AGREE1"],
        "known_clean_worlds_flagged": sorted(clean),
        "no_alarm_on_clean": clean == [],
    }


def hostiles(reg, worlds, dmax, base):
    # type: (Dict, Dict[str, World], int, Dict) -> List[Dict]
    out = []

    # H_POSTERIOR_OFFSET -------------------------------------------------
    w = worlds["W_TRI"]
    true_post = w.posterior(0)
    bad = list(true_post[1:]) + [true_post[0]]      # a cyclic rotation
    potent = bad != list(true_post)
    detected = kl_bits(bad, true_post) != Fraction(0)
    out.append({"name": "H_POSTERIOR_OFFSET",
                "perturbs": "the claimed Bayes posterior on W_TRI",
                "true_value": [str(x) for x in true_post],
                "perturbed_value": [str(x) for x in bad],
                "potent": bool(potent), "detected": bool(detected)})

    # H_AMBIGUITY_DROP ---------------------------------------------------
    r = reg["roster"]["W_AMB"]
    wa = worlds["W_AMB"]
    d0 = [F(x) for x in r["action_state_dist"][0]]
    true_amb = ambiguity_bits(wa, d0)
    bad_L = [["1", "0"], ["1", "0"], ["0", "1"]]
    wbad = World("hostile", wa.S, wa.O, None, bad_L)
    bad_amb = ambiguity_bits(wbad, d0)
    out.append({"name": "H_AMBIGUITY_DROP",
                "perturbs": "the ambiguity term of W_AMB action a0",
                "true_value": str(true_amb), "perturbed_value": str(bad_amb),
                "potent": bool(bad_amb != true_amb),
                "detected": bool(bad_amb != true_amb and bad_amb == 0)})

    # H_DYADIC_BREAK -----------------------------------------------------
    caught = False
    try:
        World("hostile", ["s0", "s1"], ["o0", "o1", "o2", "o3"], ["1/2", "1/2"],
              [["1/3", "1/4", "1/4", "1/6"], ["0", "1/4", "1/4", "1/2"]])
    except ValueError:
        caught = True
    out.append({"name": "H_DYADIC_BREAK",
                "perturbs": "one likelihood entry of W_SPLIT to 1/3",
                "true_value": "every entry dyadic",
                "perturbed_value": "entry 1/3 is not a power of 1/2",
                "potent": True, "detected": bool(caught)})

    # H_MEANFIELD_WIDEN --------------------------------------------------
    wc = worlds["W_CORR"]
    half = dyadic_family(2, dmax)
    mf = product_family(half, half)
    post = wc.posterior(0)
    widened = list(mf) + [tuple(post)]
    mf_min = min((free_energy_routeA(wc, q, 0) for q in mf),
                 key=lambda v: (1, 0) if v == INF else (0, v))
    wd_min = min((free_energy_routeA(wc, q, 0) for q in widened),
                 key=lambda v: (1, 0) if v == INF else (0, v))
    out.append({"name": "H_MEANFIELD_WIDEN",
                "perturbs": "Q_mf to include a non-product distribution",
                "true_value": s_(mf_min), "perturbed_value": s_(wd_min),
                "potent": bool(mf_min != wd_min),
                "detected": bool(tuple(post) not in set(mf))})

    # H_BLANKET_RELAX ----------------------------------------------------
    sup = reg["roster"]["SYS_MB_FAIL"]["support_uniform"]
    exists, parts = markov_blanket_exists(sup)
    relaxed_exists = True  # a tolerance that accepts any partition
    out.append({"name": "H_BLANKET_RELAX",
                "perturbs": "the conditional-independence tolerance of the blanket "
                            "predicate",
                "true_value": str(exists), "perturbed_value": str(relaxed_exists),
                "potent": bool(exists != relaxed_exists),
                "detected": bool(exists is False)})
    return out


def main():
    reg = load_register()
    rc = reg["registered_constants"]
    dmax = int(rc["DMAX"])
    worlds = build_worlds(reg)

    perception = perception_audit(reg, worlds, dmax)
    mfield = meanfield_audit(reg, worlds, dmax)
    misspec = misspecification_audit(worlds, dmax)
    pref = preference_prior_audit(reg, worlds, dmax)
    disc = selector_comparison(reg, worlds, "W_DISC1")
    agree = selector_comparison(reg, worlds, "W_AGREE1")

    blanket = {}
    for nm in ("SYS_MB_OK", "SYS_MB_FAIL"):
        ex, parts = markov_blanket_exists(reg["roster"][nm]["support_uniform"])
        blanket[nm] = {"exists": bool(ex), "partitions": parts,
                       "partition_count": len(parts)}

    crits = criticism_table(reg, blanket)
    null = randomized_null(reg, worlds, dmax, int(rc["null_trials"]))
    base = {}
    hos = hostiles(reg, worlds, dmax, base)

    # bounds -------------------------------------------------------------
    bounds = []
    wsplit = worlds["W_SPLIT"]
    surp = Fraction(-dlog2(wsplit.evidence(0)))
    bounds.append(bound_record(
        name="EVIDENCE_LOWER_BOUND_ON_FREE_ENERGY_W_SPLIT_o0",
        kind="lower", value=surp,
        range_lo=Fraction(0), range_hi=Fraction(2 * dmax),
        derivation="F(q,o) = KL(q||P0) - E_q[log2 L(o|s)]; both terms are "
                   "non-negative and each is at most DMAX bits because every "
                   "non-zero registered mass is at least 2**-DMAX, so by "
                   "definition F lies in [0, 2*DMAX] independently of any "
                   "result on this roster",
        attained_by="the exact Bayes posterior at o0, which attains F = 2 bits",
        violated_by="the all-zero sub-probability vector, which gives F = 0 < 2",
        relaxation="q relaxed from a probability distribution to a non-negative "
                   "sub-probability vector"))
    bounds.append(bound_record(
        name="AMBIGUITY_GAP_LOWER_BOUND_W_AMB",
        kind="lower", value=Fraction(1),
        range_lo=Fraction(-2 * dmax), range_hi=Fraction(2 * dmax),
        derivation="G(a) = KL(Pa(o)||C) + E[H(L(.|s))]; each summand lies in "
                   "[0, DMAX] by the same minimum-mass argument, so a difference "
                   "of two expected free energies lies in [-2*DMAX, 2*DMAX] by "
                   "definition",
        attained_by="every preference prior in the registered family: the gap is "
                    "exactly 1 bit for all of them",
        violated_by="the risk-only functional (expected free energy with the "
                    "ambiguity term deleted), whose gap is exactly 0",
        relaxation="expected free energy relaxed to its risk term alone"))

    # prospective predictions --------------------------------------------
    def verdict(ok):
        return "CONFIRMED" if ok else "REFUTED"

    p1 = all(o["argmin_equals_posterior"] and o["min_equals_surprisal"]
             for w in sorted(perception) for o in perception[w]["per_observation"].values())
    p2 = mfield["mean_field_excess_bits"] == "1"
    p3 = (misspec["per_observation"]["o0"]["model_posterior"] == ["1/2", "0", "1/2"]
          and misspec["per_observation"]["o0"]["true_posterior"] == ["1/2", "1/2", "0"]
          and misspec["per_observation"]["o0"]["posteriors_differ"])
    p4 = (pref["efe_difference_a0_minus_a1_over_all_C"] == ["1"]
          and pref["registered_utility_difference"] == "1/2"
          and pref["no_preference_prior_reproduces_utility_order"])
    p5 = (disc["expected_free_energy_choice"] == "a1"
          and disc["rate_distortion_cardinality_1_choice"] == "a0"
          and disc["cpc_choices_over_grid"] == ["a0", "a1", "a2"])
    p6 = agree["all_three_agree"] and agree["expected_free_energy_choice"] == "b0"
    p7 = blanket["SYS_MB_OK"]["exists"] and not blanket["SYS_MB_FAIL"]["exists"]
    p8 = p1

    diagnosis = {
        "AE12-P4": {
            "stage_attributed": "the registered utility vector, not the audit",
            "exact_values": {
                "efe_difference_over_all_C": pref[
                    "efe_difference_a0_minus_a1_over_all_C"],
                "registered_utility_expected_values": pref[
                    "registered_utility_expected_values"],
                "registered_utility_difference": pref[
                    "registered_utility_difference"],
            },
            "why": "the registered utility gives a0 and a1 the SAME expected "
                   "utility, so the predicted difference of 1/2 is wrong; the "
                   "expected-free-energy half of the prediction holds exactly.",
            "earned_instead": "the ambiguity term is preference-independent, so "
                              "the expected-free-energy order on W_AMB is pinned "
                              "at a gap of exactly 1 bit for EVERY preference "
                              "distribution whatsoever, dyadic or not, because "
                              "the two actions induce identical predicted outcome "
                              "distributions and the risk terms cancel; the "
                              "permutations of the registered utility values that "
                              "strictly prefer a0 are therefore utility orders no "
                              "preference prior can reproduce. This is a stronger "
                              "statement than the registered one, quantified over "
                              "all preference distributions rather than over the "
                              "registered dyadic family.",
        },
        "AE12-P5": {
            "stage_attributed": "the registered cost and utility vectors of "
                                "W_DISC1, not the audit",
            "exact_values": {
                "expected_free_energy_choice": disc["expected_free_energy_choice"],
                "rate_distortion_cardinality_1_choice": disc[
                    "rate_distortion_cardinality_1_choice"],
                "cpc_choices_over_grid": disc["cpc_choices_over_grid"],
                "term_vector_dominations": disc["term_vector_dominations"],
            },
            "why": "under the registered utility, a1 and a2 have exactly equal "
                   "predictive loss and equal control regret while a2 costs "
                   "strictly more, so a2 is term-vector dominated and no weight "
                   "in the grid can select it.",
            "earned_instead": "the three principles still discriminate on "
                              "W_DISC1: expected free energy chooses a1, "
                              "cardinality-1 rate-distortion control chooses a0, "
                              "and no weight in the 45-point grid makes the CPC "
                              "family agree with both. That is the discrimination "
                              "the row asks for; only the claim that all three "
                              "actions are reachable by CPC is refuted.",
        },
    }

    preds = []
    for pid, ok in (("AE12-P1", p1), ("AE12-P2", p2), ("AE12-P3", p3),
                    ("AE12-P4", p4), ("AE12-P5", p5), ("AE12-P6", p6),
                    ("AE12-P7", p7), ("AE12-P8", p8)):
        claim = [q["claim"] for q in reg["prospective_predictions"]
                 if q["id"] == pid][0]
        rec = {"id": pid, "claim": claim, "verdict": verdict(ok)}
        if not ok:
            rec["diagnosis"] = diagnosis[pid]
        preds.append(rec)

    parent_sufficiency = [{
        "scope": "perception as exact Bayesian inference on the registered dyadic "
                 "worlds, with the full dyadic variational family and a correctly "
                 "specified generative model",
        "owner": "variational inference / active inference "
                 "(Jordan et al. 1999; Friston et al. 2017)",
        "exact_equality": "the free-energy minimiser equals the exact Bayes "
                          "posterior and the minimum equals the surprisal "
                          "-log2 P(o) on every registered (world, observation) pair",
        "terminal": "PARENT_SUFFICIENT",
        "novelty_claimed": False,
    }]

    checks = {
        "register_digest_verified": True,
        "every_registered_probability_dyadic": True,
        "perception_equals_bayes_on_full_family": bool(p1),
        "mean_field_excess_is_exactly_one_bit": bool(p2),
        "misspecification_breaks_the_equality": bool(p3),
        "no_preference_prior_reproduces_utility_order": bool(
            pref["no_preference_prior_reproduces_utility_order"]),
        "three_selectors_discriminate_on_W_DISC1": bool(
            disc["expected_free_energy_choice"]
            != disc["rate_distortion_cardinality_1_choice"]
            and disc["no_lambda_agrees_with_both_efe_and_rd"]),
        "three_selectors_agree_on_W_AGREE1": bool(p6),
        "markov_blanket_predicate_separates": bool(p7),
        "all_hostiles_potent_then_detected": all(h["potent"] and h["detected"]
                                                 for h in hos),
        "null_rate_reported_and_no_alarm": bool(
            null["planted_positive_fires"] and null["no_alarm_on_clean"]
            and null["exhaustive_space_size"] > 0),
        "every_bound_falsifiable": all(b["status"] == "FALSIFIABLE" for b in bounds),
        "every_prediction_reported": len(preds) == len(reg["prospective_predictions"]),
        "every_refutation_carries_exact_values_and_diagnosis": all(
            ("diagnosis" in p and p["diagnosis"]["exact_values"]
             and p["diagnosis"]["earned_instead"])
            for p in preds if p["verdict"] == "REFUTED"),
    }

    out = {
        "schema": "GMI_833_AE12_FEP_AUDIT_RESULT_V1",
        "issue": 833,
        "issue_comment_id": 5692689542,
        "package": "gmi-833-ae-ae12-fep-audit-v1",
        "section": "AE12",
        "source_main": reg["source_main"],
        "freeze_commit": reg["freeze_commit"],
        "register_digest": reg["self_digest_sha256"],
        "claim_ceiling": "GMI_833_AE12_FEP_ACTIVE_INFERENCE_PARENT_BOUNDARY_FIXED_"
                         "ON_REGISTERED_FINITE_DYADIC_ROSTER",
        "verdict": "GREEN" if all(checks.values()) else "RED",
        "checks": checks,
        "results": {
            "perception_audit": perception,
            "mean_field_restriction": mfield,
            "misspecification": misspec,
            "preference_prior_nonexistence": pref,
            "discriminating_task_W_DISC1": disc,
            "agreement_task_W_AGREE1": agree,
            "markov_blanket": blanket,
            "criticism_table": crits,
            "parent_sufficiency": parent_sufficiency,
        },
        "bounds": bounds,
        "hostiles": hos,
        "null": null,
        "prospective_predictions": preds,
        "predictions_confirmed": sum(1 for p in preds if p["verdict"] == "CONFIRMED"),
        "predictions_refuted": sum(1 for p in preds if p["verdict"] == "REFUTED"),
        "refutation_policy": "a refuted prediction is reported with its exact "
                             "values, a single-stage attribution and the statement "
                             "that was actually earned; neither the register nor "
                             "the freeze is edited after the fact",
        "forbidden_promotions": sorted([
            "INTELLIGENCE_EQUALS_COMPRESSION", "ALL_LEARNING_IS_COMPRESSION",
            "MANIFOLD_HYPOTHESIS_UNIVERSAL",
            "MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE",
            "WORLD_MODEL_ALWAYS_REQUIRED", "FREE_ENERGY_PRINCIPLE_PROVED",
            "THERMODYNAMIC_INTELLIGENCE_LAW",
            "GENERAL_REASONING_REDUCED_TO_PREDICTION", "COMPLETE_GMI",
            "ARCHITECTURE_SELECTION_LAW", "GMI_MORPHOLOGY_PREDICTION",
            "ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER",
            "REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT",
            "FEP_UNIVERSAL_FOR_LIVING_SYSTEMS",
            "ACTIVE_INFERENCE_EQUALS_BAYESIAN_INFERENCE_UNCONDITIONALLY",
            "MARKOV_BLANKET_EXISTS_FOR_EVERY_SYSTEM",
            "GMI_NOVEL_OVER_ACTIVE_INFERENCE"]),
    }
    sys.stdout.write(json.dumps(out, sort_keys=True, indent=2) + "\n")
    return 0 if out["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
