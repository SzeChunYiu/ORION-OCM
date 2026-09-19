#!/usr/bin/env python3
"""Route B - independent oracle for AE12 (issue #833).

This module contains NO executable import of `ae12_fep_audit_v1`; the package
test parses this file with `ast` and asserts that.  Every quantity route A
claims is recomputed here by a materially different algorithm:

* exact log2 of a dyadic rational by an integer halving loop, not by
  `int.bit_length`;
* the variational free energy from its RAW definition
  `KL(q||P0) - E_q[log2 L(o|s)]`, evaluated on every member of the registered
  family and minimised by a linear scan, where route A uses the surprisal +
  divergence-to-posterior decomposition;
* posteriors by normalising the joint column directly;
* conditional independence for the blanket predicate by comparing conditional
  distributions `P(i | b, e)` across values of `e`, where route A compares the
  cross-product identity `p * P(b) == P(i,b) * P(e,b)`;
* the mean-field family by filtering the full family with an explicit
  factorisation test, where route A builds it as a Cartesian product;
* every choice rule by an explicit sort of (value, name) pairs.

stdlib only; python3.8 compatible.

Usage:
  independent_fep_oracle_v1.py       emit the oracle's own JSON on stdout
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER = os.path.join(HERE, "PROSPECTIVE_REGISTER_V1.json")
INF = "INF"


def register(path=REGISTER):
    with open(path, "r") as fh:
        reg = json.load(fh)
    body = dict(reg)
    claimed = body.pop("self_digest_sha256")
    body.pop("self_digest_note")
    canon = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if hashlib.sha256(canon).hexdigest() != claimed:
        raise RuntimeError("register digest mismatch")
    return reg


def q_(x):
    return Fraction(x)


def log2_dyadic(p):
    """Exact log2 of p = 2**-k by an integer halving loop (no bit tricks)."""
    if p <= 0:
        raise ValueError("log2 of a non-positive value")
    if p.numerator != 1:
        raise ValueError("not a power of one half: %s" % p)
    d = p.denominator
    k = 0
    while d > 1:
        if d % 2 != 0:
            raise ValueError("not a power of one half: %s" % p)
        d //= 2
        k += 1
    return -k


def ent(dist):
    t = Fraction(0)
    for p in dist:
        if p > 0:
            t -= p * log2_dyadic(p)
    return t


def kl(q, p):
    t = Fraction(0)
    for a, b in zip(q, p):
        if a == 0:
            continue
        if b == 0:
            return INF
        t += a * log2_dyadic(a) - a * log2_dyadic(b)
    return t


def family(n, dmax, positive_only=False):
    vals = [Fraction(1, 2 ** k) for k in range(0, dmax + 1)]
    if not positive_only:
        vals = [Fraction(0)] + vals
    out = []
    for c in itertools.product(vals, repeat=n):
        if sum(c) == 1:
            out.append(tuple(c))
    return sorted(out, key=lambda t: tuple(str(x) for x in t))


def is_product(vec, split):
    """Explicit factorisation test: vec factorises over the registered split."""
    a, b = split
    na, nb = len(a), len(b)
    if na * nb != len(vec):
        return False
    m1 = [sum(vec[i * nb + j] for j in range(nb)) for i in range(na)]
    m2 = [sum(vec[i * nb + j] for i in range(na)) for j in range(nb)]
    for i in range(na):
        for j in range(nb):
            if vec[i * nb + j] != m1[i] * m2[j]:
                return False
    return True


def posterior(P0, L, oi):
    col = [P0[i] * L[i][oi] for i in range(len(P0))]
    z = sum(col)
    return [c / z for c in col], z


def raw_free_energy(P0, L, q, oi):
    """The raw definition, with no appeal to any decomposition."""
    a = kl(q, P0)
    if a == INF:
        return INF
    t = Fraction(0)
    for i, qi in enumerate(q):
        if qi == 0:
            continue
        if L[i][oi] == 0:
            return INF
        t += qi * log2_dyadic(L[i][oi])
    return a - t


def pick_min(names, vals):
    order = []
    for nm, v in zip(names, vals):
        order.append(((1, 0) if v == INF else (0, v), nm))
    order.sort(key=lambda t: (t[0][0], t[0][1] if t[0][0] == 0 else 0, t[1]))
    return order[0][1]


def predicted(L, d):
    return [sum(d[i] * L[i][oi] for i in range(len(d))) for oi in range(len(L[0]))]


def ambiguity(L, d):
    return sum(d[i] * ent(L[i]) for i in range(len(d)))


def ci_holds(support, internal, blanket, external):
    """Conditional independence by comparing P(i | b, e) across values of e."""
    mass = Fraction(1, len(support))
    cond = {}
    for pt in support:
        a = tuple(pt[i] for i in internal)
        b = tuple(pt[i] for i in blanket)
        c = tuple(pt[i] for i in external)
        cond.setdefault((b, c), {})
        cond[(b, c)][a] = cond[(b, c)].get(a, Fraction(0)) + mass
    bykey = {}
    for (b, c), tab in cond.items():
        z = sum(tab.values())
        norm = tuple(sorted((k, str(v / z)) for k, v in tab.items()))
        bykey.setdefault(b, set()).add(norm)
    return all(len(v) == 1 for v in bykey.values())


def blanket_exists(support):
    nvars = len(support[0])
    for assign in itertools.product(range(3), repeat=nvars):
        parts = [[i for i in range(nvars) if assign[i] == k] for k in range(3)]
        if not (parts[0] and parts[1] and parts[2]):
            continue
        if ci_holds(support, parts[0], parts[1], parts[2]):
            return True
    return False


def lgrid():
    out = []
    for a in range(9):
        for b in range(9 - a):
            out.append((Fraction(a, 8), Fraction(b, 8), Fraction(8 - a - b, 8)))
    return out


def main():
    reg = register()
    dmax = int(reg["registered_constants"]["DMAX"])
    r = reg["roster"]
    out = {"schema": "GMI_833_AE12_ORACLE_V1", "route": "B"}

    # perception ---------------------------------------------------------
    perception = {}
    for nm in ("W_SPLIT", "W_TRI", "W_CORR"):
        w = r[nm]
        P0 = [q_(x) for x in w["P0"]]
        L = [[q_(x) for x in row] for row in w["L"]]
        fam = family(len(w["S"]), dmax)
        per = {}
        for oi, oname in enumerate(w["O"]):
            post, z = posterior(P0, L, oi)
            vals = [raw_free_energy(P0, L, q, oi) for q in fam]
            best = None
            arg = None
            for q, v in zip(fam, vals):
                if v == INF:
                    continue
                if best is None or v < best:
                    best, arg = v, q
            per[oname] = {
                "exact_posterior": [str(x) for x in post],
                "argmin_q": [str(x) for x in arg],
                "min_free_energy_bits": str(best),
                "surprisal_bits": str(Fraction(-log2_dyadic(z))),
                "argmin_equals_posterior": list(arg) == list(post),
                "min_equals_surprisal": best == Fraction(-log2_dyadic(z)),
            }
        perception[nm] = per
    out["perception"] = perception

    # mean field ---------------------------------------------------------
    w = r["W_CORR"]
    P0 = [q_(x) for x in w["P0"]]
    L = [[q_(x) for x in row] for row in w["L"]]
    fam = family(4, dmax)
    split = ([0, 1], [0, 1])
    mf = [q for q in fam if is_product(q, split)]
    fv = [raw_free_energy(P0, L, q, 0) for q in fam]
    mv = [raw_free_energy(P0, L, q, 0) for q in mf]
    fmin = min(v for v in fv if v != INF)
    mmin = min(v for v in mv if v != INF)
    post0, _z = posterior(P0, L, 0)
    out["mean_field"] = {
        "min_full_bits": str(fmin),
        "min_mean_field_bits": str(mmin),
        "excess_bits": str(mmin - fmin),
        "mean_field_family_size": len(mf),
        "posterior_is_a_product": is_product(tuple(post0), split),
    }

    # misspecification ---------------------------------------------------
    t = r["W_TRI_MIS"]
    P0 = [q_(x) for x in t["P0"]]
    Lt = [[q_(x) for x in row] for row in t["L_true"]]
    Lm = [[q_(x) for x in row] for row in t["L_model"]]
    mis = {}
    for oi, oname in enumerate(t["O"]):
        pt, _ = posterior(P0, Lt, oi)
        pm, _ = posterior(P0, Lm, oi)
        mis[oname] = {"true_posterior": [str(x) for x in pt],
                      "model_posterior": [str(x) for x in pm],
                      "posteriors_differ": list(pt) != list(pm)}
    out["misspecification"] = mis

    # preference prior ---------------------------------------------------
    a = r["W_AMB"]
    La = [[q_(x) for x in row] for row in a["L"]]
    d0 = [q_(x) for x in a["action_state_dist"][0]]
    d1 = [q_(x) for x in a["action_state_dist"][1]]
    U = [q_(x) for x in a["U_state"]]
    Cf = family(len(a["O"]), dmax, positive_only=True)
    diffs = sorted({str((kl(predicted(La, d0), C) + ambiguity(La, d0))
                        - (kl(predicted(La, d1), C) + ambiguity(La, d1))) for C in Cf})
    eu0 = sum(d0[i] * U[i] for i in range(len(U)))
    eu1 = sum(d1[i] * U[i] for i in range(len(U)))
    strict = []
    for perm in sorted(set(itertools.permutations(range(len(U))))):
        Up = [U[i] for i in perm]
        e0 = sum(d0[i] * Up[i] for i in range(len(Up)))
        e1 = sum(d1[i] * Up[i] for i in range(len(Up)))
        if e0 > e1:
            strict.append([str(x) for x in Up])
    strict = sorted(set(tuple(x) for x in strict))
    out["preference_prior"] = {
        "predicted_outcomes_identical": predicted(La, d0) == predicted(La, d1),
        "ambiguity_gap_bits": str(ambiguity(La, d0) - ambiguity(La, d1)),
        "preference_family_size": len(Cf),
        "efe_difference_over_all_C": diffs,
        "registered_utility_difference": str(eu0 - eu1),
        "strict_contradiction_witnesses": [list(x) for x in strict],
    }

    # selectors ----------------------------------------------------------
    sel = {}
    for nm in ("W_DISC1", "W_AGREE1"):
        w = r[nm]
        Lw = [[q_(x) for x in row] for row in w["L"]]
        C = [q_(x) for x in w["C"]]
        names = list(w["A"])
        ds = [[q_(x) for x in row] for row in w["action_state_dist"]]
        Uw = [q_(x) for x in w["U_state"]]
        cost = [Fraction(c) for c in w["cost_bits"]]
        po = [predicted(Lw, d) for d in ds]
        g = []
        for i, d in enumerate(ds):
            k = kl(po[i], C)
            g.append(INF if k == INF else k + ambiguity(Lw, d))
        eu = [sum(d[i] * Uw[i] for i in range(len(Uw))) for d in ds]
        best = max(eu)
        ctrl = [best - x for x in eu]
        pl = [Fraction(1) - max(p) for p in po]
        picks = set()
        for (lc, lp, lk) in lgrid():
            j = [lc * cost[i] + lp * pl[i] + lk * ctrl[i] for i in range(len(names))]
            picks.add(pick_min(names, j))
        sel[nm] = {
            "expected_free_energy_bits": [str(x) if x != INF else INF for x in g],
            "efe_choice": pick_min(names, g),
            "rd_choice": pick_min(names, [-x for x in eu]),
            "cpc_choices": sorted(picks),
            "control_regret": [str(x) for x in ctrl],
            "predictive_loss": [str(x) for x in pl],
        }
    out["selectors"] = sel

    # blanket ------------------------------------------------------------
    out["blanket"] = {nm: blanket_exists(r[nm]["support_uniform"])
                      for nm in ("SYS_MB_OK", "SYS_MB_FAIL")}

    sys.stdout.write(json.dumps(out, sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
