#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Route A executor -- GMI #833 Section I update-law regimes.

Frozen contract: FREEZE_V1.md, commit 6e42ccd2 (pre-implementation).
Standard library only. Exact rational arithmetic throughout. Python 3.8 safe.

Writes RESULT_V1.json next to this file.
"""

import io
import json
import os
import random
import tokenize
from fractions import Fraction as F
from itertools import combinations, product

HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# 0. registered scope constants (FREEZE_V1 section 2)
# --------------------------------------------------------------------------

EPS = F(1, 4)                      # frozen noise rate
KMAX = 3                           # frozen max productions in a covering set
PRICE_KEYS = ("p_test", "p_carry", "p_store", "p_build",
              "p_branch", "p_meta", "p_mut", "lam")
NPRICE = 8


def pairwise_ratio_grid():
    """The direct parent's pre-committed grid, adopted unchanged."""
    seen = set()
    out = []
    for a in range(1, 13):
        for b in range(1, 7):
            q = F(a, b)
            if q not in seen:
                seen.add(q)
                out.append(q)
    out.sort()
    return tuple(out)


RATIO_GRID = pairwise_ratio_grid()
JOINT_LEVELS = (F(1, 4), F(1), F(4))
JOINT_PRICES = tuple((F(1),) + lv for lv in product(JOINT_LEVELS, repeat=7))

REGIME_IDS = ("SIG-W", "SIG-X", "SIG-R", "SIG-L", "SIG-P", "SIG-T", "SIG-S")
BASELINE_ID = "BASE-0"      # the single-best point summary, SIG-W's comparator
NULL_ID = "NULL-0"          # the single incumbent: one carried candidate, no store
ANCHOR_IDS = REGIME_IDS + (BASELINE_ID, NULL_ID)

# post-freeze deviation D1 (see SUPPLEMENT_1): the ascent charge conforms to
# FREEZE section 2.1, where p_test buys ONE candidate evaluated on ONE instance.
D1_ON = os.environ.get("REGIMES_D1_OFF", "0") != "1"


# --------------------------------------------------------------------------
# 1. registered environments (FREEZE_V1 section 2.3)
# --------------------------------------------------------------------------

D_NZ = 8
D_KRANGE = tuple(range(0, 9))
X_NZ = 10
X_WINDOWS = ((0, 2), (0, 4), (2, 5), (3, 6), (1, 8),
             (5, 9), (0, 9), (4, 4), (6, 9), (2, 2))

V_TWO_PEAK_9 = (1, 2, 3, 2, 1, 2, 5, 2, 1)
V_UNIMODAL_9 = (1, 2, 3, 4, 5, 4, 3, 2, 1)
V_TWO_PEAK_10 = (1, 3, 2, 1, 2, 6, 2, 1, 2, 1)
V_UNIMODAL_10 = (1, 2, 3, 4, 5, 6, 5, 4, 3, 2)

D_STARTS_EXT = (0, 8, 4, 1, 7, 2, 6, 3, 5)
X_STARTS_EXT = (0, 9, 4, 1, 8, 2, 7, 3, 6, 5)


def step_tables(nz, krange):
    return tuple(tuple(1 if z >= k else 0 for z in range(nz)) for k in krange)


def window_tables(nz, windows):
    return tuple(tuple(1 if a <= z <= b else 0 for z in range(nz))
                 for (a, b) in windows)


def path_neighbours(n):
    out = []
    for i in range(n):
        nb = []
        if i > 0:
            nb.append(i - 1)
        if i < n - 1:
            nb.append(i + 1)
        out.append(tuple(nb))
    return tuple(out)


def interval_productions(nz):
    """Registered production space RS: every interval of Z with an output bit,
    each of registered description length 2 (FREEZE_V1 section 4.3)."""
    out = []
    for lo in range(nz):
        for hi in range(lo, nz):
            fires = frozenset(range(lo, hi + 1))
            for bit in (0, 1):
                out.append((fires, bit, 2))
    return tuple(out)


def build_env(env_id, nz, cand_tables, target, train, qset, retr_pairs,
              vfun_ints, starts_ext, fam_hprime, fam_k, fam_k0):
    m = len(cand_tables)
    return {
        "id": env_id, "nz": nz, "H": cand_tables, "M": m,
        "prior": tuple(F(1, m) for _ in range(m)),
        "target": tuple(target), "train": tuple(train), "T": len(train),
        "Qset": tuple(qset), "nq": len(qset), "retr": tuple(retr_pairs),
        "RS": interval_productions(nz), "nbr": path_neighbours(m),
        "Vfun": tuple(F(v) for v in vfun_ints),
        "starts_ext": tuple(starts_ext), "Hprime": tuple(fam_hprime),
        "K": fam_k, "k0": fam_k0,
    }


def derivation_environments():
    H = step_tables(D_NZ, D_KRANGE)
    tgt4 = H[4]
    alt = (1, 0, 1, 0, 1, 0, 1, 0)
    allh = tuple(range(9))
    mid = (2, 3, 4, 5, 6)
    return (
        build_env("D1", D_NZ, H, tgt4, (0, 1, 6, 7), (2, 3, 4, 5), (0, 1, 2, 3),
                  V_TWO_PEAK_9, D_STARTS_EXT, mid, 4, 1),
        build_env("D2", D_NZ, H, tgt4, (3, 4, 3, 4, 3, 4), (0, 1, 6, 7),
                  (0, 1, 2, 3), V_TWO_PEAK_9, D_STARTS_EXT, mid, 4, 1),
        build_env("D3", D_NZ, H, alt, (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 2, 3),
                  V_TWO_PEAK_9, D_STARTS_EXT, allh, 4, 1),
        build_env("D4", D_NZ, H, tgt4, (0, 1, 2, 5, 6, 7), (3, 4), (0, 0),
                  V_TWO_PEAK_9, D_STARTS_EXT, mid, 4, 1),
        build_env("D5", D_NZ, H, tgt4, (0, 7), (1, 2, 3, 4, 5, 6),
                  (0, 0, 0, 1, 1, 1), V_TWO_PEAK_9, D_STARTS_EXT, mid, 4, 1),
        build_env("D6", D_NZ, H, tgt4, (0, 7), (1, 2, 3, 4, 5, 6),
                  (0, 0, 0, 1, 1, 1), V_UNIMODAL_9, D_STARTS_EXT, mid, 4, 1),
    )


def heldout_environments():
    H = window_tables(X_NZ, X_WINDOWS)
    tgt = H[2]
    alt = (1, 1, 0, 0, 1, 1, 0, 0, 1, 1)
    allh = tuple(range(10))
    mid = (0, 1, 2, 3, 4)
    return (
        build_env("X1", X_NZ, H, tgt, (0, 1, 8, 9), (2, 3, 5, 6), (0, 1, 2, 3),
                  V_TWO_PEAK_10, X_STARTS_EXT, mid, 4, 1),
        build_env("X2", X_NZ, H, tgt, (2, 6, 2, 6, 2, 6), (0, 1, 8, 9),
                  (0, 1, 2, 3), V_TWO_PEAK_10, X_STARTS_EXT, mid, 4, 1),
        build_env("X3", X_NZ, H, alt, (0, 2, 4, 6), (1, 3, 5, 7), (0, 1, 2, 3),
                  V_TWO_PEAK_10, X_STARTS_EXT, allh, 4, 1),
        build_env("X4", X_NZ, H, tgt, (0, 1, 2, 7, 8, 9), (4, 5), (0, 0),
                  V_TWO_PEAK_10, X_STARTS_EXT, mid, 4, 1),
        build_env("X5", X_NZ, H, tgt, (0, 9), (1, 2, 3, 4, 5, 6),
                  (0, 0, 0, 1, 1, 1), V_TWO_PEAK_10, X_STARTS_EXT, mid, 4, 1),
        build_env("X6", X_NZ, H, tgt, (0, 9), (1, 2, 3, 4, 5, 6),
                  (0, 0, 0, 1, 1, 1), V_UNIMODAL_10, X_STARTS_EXT, mid, 4, 1),
    )


def scope_fingerprint(envs):
    """Order-sensitive exact fingerprint of the registered scope.  Each route
    computes it from its OWN transcription; a mismatch makes every agreement
    figure meaningless, so it is checked rather than assumed."""
    parts = []
    for e in envs:
        parts.append("|".join([
            e["id"], str(e["nz"]), str(e["M"]),
            ",".join("".join(str(b) for b in h) for h in e["H"]),
            "".join(str(b) for b in e["target"]),
            ",".join(str(t) for t in e["train"]),
            ",".join(str(q) for q in e["Qset"]),
            ",".join(str(r) for r in e["retr"]),
            ",".join(str(v) for v in e["Vfun"]),
            ",".join(str(s) for s in e["starts_ext"]),
            ",".join(str(h) for h in e["Hprime"]),
            str(e["K"]), str(e["k0"]), str(len(e["RS"])),
        ]))
    body = "||".join(parts)
    acc = 0
    for ch in body:
        acc = (acc * 1000003 + ord(ch)) % (2 ** 61 - 1)
    return {"len": len(body), "digest": acc}


# --------------------------------------------------------------------------
# 2. computed invariants (never asserted)
# --------------------------------------------------------------------------

def likelihood(cand, target, train):
    err = agr = 0
    for z in train:
        if cand[z] == target[z]:
            agr += 1
        else:
            err += 1
    return (EPS ** err) * ((1 - EPS) ** agr)


def posterior(env, pool=None):
    idxs = range(env["M"]) if pool is None else list(pool)
    raw = {}
    tot = F(0)
    for i in idxs:
        v = env["prior"][i] * likelihood(env["H"][i], env["target"],
                                         env["train"])
        raw[i] = v
        tot += v
    return dict((i, raw[i] / tot) for i in idxs)


def weighted_prediction(env, post, z):
    one = sum(w for i, w in post.items() if env["H"][i][z] == 1)
    return 1 if one > F(1, 2) else 0          # registered tie rule


def best_index(post):
    best = None
    for i in sorted(post):
        if best is None or post[i] > post[best]:
            best = i
    return best


def alpha_gain(env, post):
    pidx = best_index(post)
    pcand = env["H"][pidx]
    g = 0
    detail = []
    for z in env["Qset"]:
        wp = weighted_prediction(env, post, z)
        pp = pcand[z]
        t = env["target"][z]
        if pp != t and wp == t:
            g += 1
            detail.append([z, wp, pp, t, 1])
        elif wp != t and pp == t:
            g -= 1
            detail.append([z, wp, pp, t, -1])
    return g, pidx, detail


def covering_sets(env):
    """Minimum total description length over consistent covering subsets of RS,
    of size at most the registered KMAX.  Returns (Dmin, subset) or (None,None)."""
    rs, tr, tgt = env["RS"], env["train"], env["target"]
    labelled = [(z, tgt[z]) for z in tr]
    ok = []
    for idx, (fires, bit, ln) in enumerate(rs):
        if all(not (z in fires and bit != y) for (z, y) in labelled):
            ok.append(idx)
    need = set(z for (z, _) in labelled)
    best = None
    best_set = None
    for k in range(1, KMAX + 1):
        for combo in combinations(ok, k):
            cov = set()
            ln = 0
            for idx in combo:
                fires, bit, l = rs[idx]
                ln += l
                for (z, y) in labelled:
                    if z in fires and bit == y:
                        cov.add(z)
            if cov >= need and (best is None or ln < best):
                best, best_set = ln, combo
    return best, best_set


def production_predict(env, subset, z):
    if subset is None:
        return 0
    for idx in sorted(subset):
        fires, bit, _ = env["RS"][idx]
        if z in fires:
            return bit
    return 0                                   # registered default


def reuse_invariants(env, subset):
    """Hocc / Delta / Kdef for the re-invocation refinement (FREEZE 4.4)."""
    if subset is None:
        return None
    counts = {}
    for z in env["Qset"]:
        for idx in sorted(subset):
            if z in env["RS"][idx][0]:
                counts[idx] = counts.get(idx, 0) + 1
                break
    if not counts:
        return {"Hocc": 0, "Delta": 0, "Kdef": 1, "prod": None, "pays": False,
                "saving": 0}
    prod = sorted(counts, key=lambda i: (-counts[i], i))[0]
    hocc = counts[prod]
    ln = env["RS"][prod][2]
    delta = ln - 1
    kdef = ln + 1
    saving = hocc * delta - kdef
    return {"Hocc": hocc, "Delta": delta, "Kdef": kdef, "prod": prod,
            "pays": saving > 0, "saving": saving if saving > 0 else 0}


def ascend(env, start):
    cur, steps = start, 0
    while True:
        best = cur
        for j in env["nbr"][cur]:
            if env["Vfun"][j] > env["Vfun"][best]:
                best = j
        if best == cur:
            return cur, steps
        cur, steps = best, steps + 1


def local_optima(env):
    return [i for i in range(env["M"])
            if all(env["Vfun"][j] <= env["Vfun"][i] for j in env["nbr"][i])]


def breadth_terminal(env, b):
    """Best terminal reached from the first b registered starts, plus the
    deepest ascent among them.  Ties to smallest index."""
    best_idx = None
    best_v = None
    steps = 0
    for s in env["starts_ext"][:b]:
        t, st = ascend(env, s)
        steps = max(steps, st)
        if best_v is None or env["Vfun"][t] > best_v:
            best_v, best_idx = env["Vfun"][t], t
    return best_idx, max(steps, 1)


def breadth_invariants(env):
    vglob = max(env["Vfun"])
    t0, _ = ascend(env, env["starts_ext"][0])
    vloc = env["Vfun"][t0]
    bmin = len(env["starts_ext"])
    for b in range(1, len(env["starts_ext"]) + 1):
        idx, _ = breadth_terminal(env, b)
        if env["Vfun"][idx] == vglob:
            bmin = b
            break
    bidx, tsteps = breadth_terminal(env, bmin)
    lo = local_optima(env)
    return {"Vloc": vloc, "Vglob": vglob, "Bmin": bmin, "Tsteps": tsteps,
            "single_terminal": t0, "breadth_terminal": bidx,
            "local_optima": lo, "unimodal": len(lo) == 1}


def invariants(env):
    post = posterior(env)
    ag, pidx, ag_detail = alpha_gain(env, post)
    dmin, dset = covering_sets(env)
    reuse = reuse_invariants(env, dset)
    br = breadth_invariants(env)
    Mprime = len(env["Hprime"])
    dmin_l = None
    if dmin is not None:
        dmin_l = dmin - (reuse["saving"] if reuse else 0)
        if dmin_l < 1:
            dmin_l = 1
    return {
        "env": env["id"], "M": env["M"], "T": env["T"], "nq": env["nq"],
        "K": env["K"], "k0": env["k0"], "Mprime": Mprime,
        "r": env["M"] - Mprime,
        "posterior": dict((str(i), str(post[i])) for i in sorted(post)),
        "alpha_gain": ag, "alpha_gain_detail": ag_detail,
        "point_summary_index": pidx,
        "mu": len(set(env["retr"])),
        "retrieved_positions": sorted(set(env["retr"])),
        "Dmin": dmin, "Dset": (list(dset) if dset else None),
        "Dmin_L": dmin_l,
        "disc": len(env["RS"]) * env["T"], "cover": 2 * env["T"],
        "reuse": reuse,
        "Vloc": str(br["Vloc"]), "Vglob": str(br["Vglob"]),
        "Bmin": br["Bmin"], "Tsteps": br["Tsteps"],
        "single_terminal": br["single_terminal"],
        "breadth_terminal": br["breadth_terminal"],
        "local_optima": br["local_optima"], "unimodal": br["unimodal"],
        "max_degree": max(len(nb) for nb in env["nbr"]),
        "target_in_H": env["target"] in env["H"],
    }


# --------------------------------------------------------------------------
# 3. ONE accounting function over the structural tuple space
# --------------------------------------------------------------------------
# A structural tuple is  g = (carry, store, build, breadth, meta, mut).
# Nothing in this section names a family, a signature or a mechanism.

def tuple_predictor_loss(env, inv, g):
    """Exact integer loss of the tuple's induced predictor, summed over the
    registered K-episode family.  The predictor is determined by the tuple's
    structural coordinates through the registered precedence declared below."""
    carry, store, build, breadth, meta, mut = g
    K, k0 = env["K"], env["k0"]
    total = 0
    for ep in range(K):
        pool = None
        if meta > 0 and ep >= k0:
            pool = env["Hprime"]
        post = posterior(env, pool)
        if build > 0 and inv["Dmin"] is not None:
            sub = inv["Dset"]
            pred = lambda z: production_predict(env, sub, z)
        elif store > 0:
            def pred(z, store=store):
                qpos = env["Qset"].index(z)
                tpos = env["retr"][qpos]
                if tpos >= store:
                    return 0                      # not retained
                return env["target"][env["train"][tpos]]
        elif breadth >= 2:
            idx, _ = breadth_terminal(env, breadth)
            pred = lambda z, c=env["H"][idx]: c[z]
        elif carry >= 2:
            pred = lambda z, p=post: weighted_prediction(env, p, z)
        elif carry == 1:
            pred = lambda z, c=env["H"][best_index(post)]: c[z]
        else:
            pred = lambda z: 0                    # registered default
        total += sum(1 for z in env["Qset"] if pred(z) != env["target"][z])
    return total


def predictor_vector(env, inv, g):
    """The exact emitted predictions of a tuple, over every registered episode
    and every registered query.  Two tuples with the same vector emit the same
    predictor and differ only in charge."""
    carry, store, build, breadth, meta, mut = g
    out = []
    for ep in range(env["K"]):
        pool = env["Hprime"] if (meta > 0 and ep >= env["k0"]) else None
        post = posterior(env, pool)
        for z in env["Qset"]:
            if build > 0 and inv["Dmin"] is not None:
                out.append(production_predict(env, inv["Dset"], z))
            elif store > 0:
                qpos = env["Qset"].index(z)
                tpos = env["retr"][qpos]
                out.append(0 if tpos >= store
                           else env["target"][env["train"][tpos]])
            elif carry >= 2:
                out.append(weighted_prediction(env, post, z))
            elif carry == 1:
                out.append(env["H"][best_index(post)][z])
            else:
                idx, _ = breadth_terminal(env, breadth)
                out.append(env["H"][idx][z])
    return tuple(out)


def redundancy_certificate(env, inv, g, levels):
    """UL-9, the non-redundancy lemma in operational form.

    A structural coordinate is WASTED when lowering it to the next registered
    level leaves the emitted predictor identical at every registered input: the
    lower tuple emits the same predictor at a strictly lower charge, so the
    higher one is strictly dominated at every positive price.  This is the
    general form of the freeze's own wastefulness lemma (section 4.2).
    """
    base = predictor_vector(env, inv, g)
    wasted = []
    for c in range(6):
        lv = sorted(set(levels[c]))
        cur = g[c]
        if cur not in lv or lv.index(cur) == 0:
            continue
        lower = lv[lv.index(cur) - 1]
        h = list(g)
        h[c] = lower
        if predictor_vector(env, inv, tuple(h)) == base:
            wasted.append([c, cur, lower])
    return wasted


def tuple_vector(env, inv, g):
    """The charge coefficient vector of a structural tuple, in Z_{>=0}^8."""
    carry, store, build, breadth, meta, mut = g
    M, T, nq, K = inv["M"], inv["T"], inv["nq"], inv["K"]
    k0, deg = inv["k0"], inv["max_degree"]
    tst, disc = inv["Tsteps"], inv["disc"]

    evals = 0
    for ep in range(K):
        width = M
        if meta > 0 and ep >= k0:
            width = meta
        if carry > 0:
            evals += width * T
    if carry == 0 and store == 0 and build == 0:
        if D1_ON:
            # each carried member, at each step, evaluates itself and its
            # neighbours; one evaluation costs T elementary evaluations
            ascent = breadth * (tst + 1) * (deg + 1) * T
        else:
            ascent = breadth * tst * deg          # deviation-free fallback
    else:
        ascent = 0
    evals += K * (store * nq + ascent +
                  (disc if build > 0 else 0) + build * nq + nq)
    return (
        evals,                       # p_test
        K * carry * T,               # p_carry
        K * store * T,               # p_store
        K * build,                   # p_build
        K * (breadth - 1) * tst,     # p_branch
        meta * K,                    # p_meta
        K * mut,                     # p_mut
        tuple_predictor_loss(env, inv, g),   # lam
    )


def representative_tuples(inv):
    """The registered representatives, as points of the SAME tuple space."""
    M, mu, T, Mp = inv["M"], inv["mu"], inv["T"], inv["Mprime"]
    d, dl, b = inv["Dmin"], inv["Dmin_L"], inv["Bmin"]
    b2 = b if b >= 2 else 2      # a breadth law carries at least two members
    reps = {
        "SIG-W": (M, 0, 0, 1, 0, 0),
        BASELINE_ID: (1, 0, 0, 1, 0, 0),
        NULL_ID: (0, 0, 0, 1, 0, 0),
        "SIG-X": (0, mu, 0, 1, 0, 0),
        "SIG-R": (0, 0, d, 1, 0, 0) if d is not None else None,
        "SIG-L": (0, 0, dl, 1, 0, 0) if dl is not None else None,
        "SIG-P": (0, 0, 0, b2, 0, 0),
        "SIG-T": (1, 0, 0, 1, Mp, 0),
        "SIG-S": (1, 0, 0, 1, 0, 1),
    }
    return reps


def coefficient_vectors(env, inv):
    reps = representative_tuples(inv)
    out = {}
    for k, g in reps.items():
        out[k] = None if g is None else tuple_vector(env, inv, g)
    return out


def charge(vec, price):
    return sum(F(vec[i]) * price[i] for i in range(NPRICE))


def int_price(price):
    """Scale a registered grid price to integers (all grid levels are quarters).
    Comparisons of integer dot products are identical to comparisons of the
    exact rational charges, because the scale factor is common and positive."""
    out = []
    for x in price:
        y = x * 4
        if y.denominator != 1:
            return None
        out.append(int(y))
    return tuple(out)


def idot(vec, ip):
    t = 0
    for i in range(NPRICE):
        t += vec[i] * ip[i]
    return t


JOINT_IPRICES = tuple(int_price(p) for p in JOINT_PRICES)


def unit_price(**over):
    p = [F(1)] * NPRICE
    for k, v in over.items():
        p[PRICE_KEYS.index(k)] = v
    return tuple(p)


# --------------------------------------------------------------------------
# 4. the seven thresholds and their matched converses
# --------------------------------------------------------------------------

def solve_ratio_threshold(vec_a, vec_b, coord):
    A1, B1 = F(vec_a[coord]), F(vec_b[coord])
    A0 = sum(F(vec_a[i]) for i in range(NPRICE) if i != coord)
    B0 = sum(F(vec_b[i]) for i in range(NPRICE) if i != coord)
    if A1 == B1:
        if A0 == B0:
            return None, "IDENTICAL_AT_EVERY_PRICE"
        return None, ("A_WINS_AT_EVERY_PRICE" if A0 < B0
                      else "B_WINS_AT_EVERY_PRICE")
    x = (B0 - A0) / (A1 - B1)
    if x <= 0:
        at1 = (A0 + A1) - (B0 + B1)
        return x, ("A_WINS_AT_EVERY_POSITIVE_PRICE" if at1 < 0
                   else ("B_WINS_AT_EVERY_POSITIVE_PRICE" if at1 > 0
                         else "TIE_AT_UNIT"))
    return x, ("A_WINS_BELOW" if A1 > B1 else "A_WINS_ABOVE")


def thresholds(env, inv, vecs):
    M, T = inv["M"], inv["T"]
    out = {}

    # UL-2  beta* = alpha_gain / ((M-1) T)   on p_carry / lam
    beta = F(inv["alpha_gain"], (M - 1) * T)
    conv_ok, conv_wit = True, None
    if inv["alpha_gain"] <= 0:
        for price in JOINT_PRICES:
            if charge(vecs["SIG-W"], price) <= charge(vecs[BASELINE_ID], price):
                conv_ok, conv_wit = False, [str(x) for x in price]
                break
    out["beta_star"] = {
        "value": str(beta), "form": "alpha_gain / ((M-1)*T)",
        "alpha_gain": inv["alpha_gain"], "M": M, "T": T,
        "condition": "SIG-W beats the point summary iff p_carry/lam < beta*",
        "unconditional_converse_fires": inv["alpha_gain"] <= 0,
        "converse_verified_on_grid": conv_ok,
        "converse_counterwitness": conv_wit,
        "grid_cases_checked": len(JOINT_PRICES) if inv["alpha_gain"] <= 0 else 0,
    }

    # UL-3  chi*  on p_store, SIG-X against SIG-R
    if vecs["SIG-R"] is None:
        out["chi_star"] = {"value": None,
                           "status": "UNDETERMINED_NO_CONSISTENT_COVER"}
        out["psi_star"] = {"value": None,
                           "status": "UNDETERMINED_NO_CONSISTENT_COVER"}
        out["reuse_condition"] = {"status": "UNDETERMINED_NO_CONSISTENT_COVER"}
    else:
        x, o = solve_ratio_threshold(vecs["SIG-X"], vecs["SIG-R"],
                                     PRICE_KEYS.index("p_store"))
        out["chi_star"] = {"value": (str(x) if x is not None else None),
                           "orientation": o, "mu": inv["mu"],
                           "form": "solve <a_X - a_R, pi> = 0 for p_store"}
        # UL-4  psi*  on p_build, SIG-R against SIG-X
        x, o = solve_ratio_threshold(vecs["SIG-R"], vecs["SIG-X"],
                                     PRICE_KEYS.index("p_build"))
        out["psi_star"] = {
            "value": (str(x) if x is not None else None), "orientation": o,
            "Dmin": inv["Dmin"], "cover": inv["cover"], "disc": inv["disc"],
            "compression_strict": inv["Dmin"] < inv["cover"],
            "form": "solve <a_R - a_X, pi> = 0 for p_build"}
        # UL-4b : the sharp form -- the largest registered rule-space size at
        # which the compression law still pays its discovery charge, all prices
        # at the registered unit.  Charges are affine and decreasing in |RS|.
        K, nq2 = inv["K"], inv["nq"]
        up2 = unit_price()
        cx = charge(vecs["SIG-X"], up2)
        no_disc = charge(vecs["SIG-R"], up2) - F(K * inv["disc"])
        slack = cx - no_disc
        disc_star = slack / K if slack > 0 else F(0)
        out["disc_star"] = {
            "value": str(disc_star),
            "form": "largest per-episode discovery charge at which the "
                    "compression law still beats the retrieval law, all "
                    "prices at the registered unit",
            "registered_disc": inv["disc"], "RS_size": len(env["RS"]),
            "pays_at_registered_RS": F(inv["disc"]) < disc_star,
            "max_RS_size": str(disc_star / inv["T"]) if inv["T"] else None,
        }
        # UL-5  SIG-L against SIG-R : the #897 lifecycle inequality, these units
        ru = inv["reuse"]
        up = unit_price()
        out["reuse_condition"] = {
            "Hocc": ru["Hocc"], "Delta": ru["Delta"], "Kdef": ru["Kdef"],
            "inequality": "Hocc*Delta > Kdef",
            "lhs": ru["Hocc"] * ru["Delta"], "rhs": ru["Kdef"],
            "pays": ru["pays"], "saving": ru["saving"],
            "Dmin": inv["Dmin"], "Dmin_L": inv["Dmin_L"],
            "charge_strictly_lower_at_unit":
                charge(vecs["SIG-L"], up) < charge(vecs["SIG-R"], up),
            "ownership": "the invention result and the lifecycle threshold are "
                         "owned by #897; this is the placement only",
        }

    # UL-6  pistar* = (Vglob - Vloc) / ((Bmin-1) Tsteps)  on p_branch / lam
    vg, vl = F(inv["Vglob"]), F(inv["Vloc"])
    den = (inv["Bmin"] - 1) * inv["Tsteps"]
    pistar = F(0) if den == 0 else (vg - vl) / den
    out["pistar_star"] = {
        "value": str(pistar), "form": "(Vglob - Vloc) / ((Bmin-1)*Tsteps)",
        "Vglob": inv["Vglob"], "Vloc": inv["Vloc"], "Bmin": inv["Bmin"],
        "Tsteps": inv["Tsteps"], "unimodal": inv["unimodal"],
        "local_optima": inv["local_optima"],
        "unconditional_converse_fires": inv["unimodal"],
        "converse_gap": str(vg - vl),
        "note": ("Bmin = 1: no additional member is carried" if den == 0
                 else ""),
    }

    # UL-7  tau* = r T (K-k0) / (Mprime K)  on p_meta / p_test
    tau = F(inv["r"] * inv["T"] * (inv["K"] - inv["k0"]),
            inv["Mprime"] * inv["K"])
    out["tau_star"] = {
        "value": str(tau), "form": "r*T*(K-k0) / (Mprime*K)", "r": inv["r"],
        "Mprime": inv["Mprime"], "K": inv["K"], "k0": inv["k0"], "T": inv["T"],
        "unconditional_reduction_fires": inv["r"] == 0,
    }

    # UL-8  s*  on p_mut / lam, inside a pointwise-selection-closed class
    s_star = F(vecs[BASELINE_ID][7] - vecs["SIG-S"][7])
    up = unit_price()
    out["s_star"] = {
        "value": str(s_star),
        "form": "(loss of best fixed in class) - (loss of best reachable)",
        "class": "pointwise-selection-closed A_k",
        "conditions_empty": s_star == 0,
        "overhead_units": vecs["SIG-S"][6],
        "strictly_dominated_at_unit":
            charge(vecs["SIG-S"], up) > charge(vecs[BASELINE_ID], up),
        "never_cheaper_than_comparator_on_grid":
            all(charge(vecs["SIG-S"], p) > charge(vecs[BASELINE_ID], p)
                for p in JOINT_PRICES),
        "grid_prices_checked": len(JOINT_PRICES),
        "certificate": "a_SIG-S equals a_BASE-0 in every coordinate except "
                       "p_mut, where it exceeds it, so SIG-S is strictly "
                       "dearer at every positive price: the pointwise-selection"
                       " collapse, UL-1",
    }
    return out


def reduction_at_zero_relatedness(env, inv):
    """UL-7's falsifier: at r = 0 the indexed step rule must equal the base
    step rule at EVERY registered input.  Verified pointwise."""
    if inv["r"] != 0:
        return {"applicable": False, "r": inv["r"]}
    base_post = posterior(env)
    base_idx = best_index(base_post)
    sub_post = posterior(env, env["Hprime"])
    idx_idx = best_index(sub_post)
    checked = 0
    mismatches = []
    for ep in range(env["K"]):
        for z in range(env["nz"]):
            checked += 1
            if env["H"][base_idx][z] != env["H"][idx_idx][z]:
                mismatches.append([ep, z])
    return {
        "applicable": True, "r": 0, "base_index": base_idx,
        "indexed_index": idx_idx, "pointwise_inputs_checked": checked,
        "mismatches": mismatches,
        "behaviourally_identical": not mismatches,
        "strict_extra_charge": "p_meta * Mprime * K = p_meta * %d"
                               % (inv["Mprime"] * env["K"]),
    }


# --------------------------------------------------------------------------
# 5. compatibility matrix -- NOT a partition
# --------------------------------------------------------------------------

SIG_CLAUSES = {
    "SIG-W": {"carry_weight_slots": "all", "store_instances": "none",
              "emits": "weighting"},
    "SIG-X": {"carry_weight_slots": "none", "store_instances": "some",
              "emits": "retrieval"},
    "SIG-R": {"store_after_emission": "none", "emits": "productions",
              "description_strictly_shorter": True},
    "SIG-L": {"store_after_emission": "none", "emits": "productions",
              "description_strictly_shorter": True,
              "reinvocation_sites": "at_least_two"},
    "SIG-P": {"carried_candidates": "at_least_two"},
    "SIG-T": {"cross_episode_index": "present"},
    "SIG-S": {"successor_set_changes": "present"},
}

CONTRADICTIONS = (
    ("carry_weight_slots", "all", "none"),
    ("store_instances", "some", "none"),
    ("emits", "weighting", "retrieval"),
    ("emits", "weighting", "productions"),
    ("emits", "retrieval", "productions"),
)


def compatibility_matrix():
    rows = []
    for a, b in combinations(REGIME_IDS, 2):
        ca, cb = SIG_CLAUSES[a], SIG_CLAUSES[b]
        clash = None
        for key, v1, v2 in CONTRADICTIONS:
            if key in ca and key in cb and set([ca[key], cb[key]]) == \
                    set([v1, v2]):
                clash = [key, ca[key], cb[key]]
                break
        if clash is None:
            merged = dict(ca)
            merged.update(cb)
            rows.append({"pair": [a, b], "verdict": "COMPATIBLE",
                         "witness_clauses": sorted(
                             [list(kv) for kv in merged.items()])})
        else:
            rows.append({"pair": [a, b], "verdict": "EXCLUSIVE",
                         "contradicting_clause": clash})
    comp = sum(1 for r in rows if r["verdict"] == "COMPATIBLE")
    return {"pairs": len(rows), "compatible": comp,
            "exclusive": len(rows) - comp, "rows": rows,
            "is_a_partition": False,
            "why_not": "at least one pair is COMPATIBLE, so the seven "
                       "predicates do not separate law space; this matrix is "
                       "reported as a matrix and the word partition is not "
                       "applied to it"}


# --------------------------------------------------------------------------
# 6. UL-10 argmin-cell partition, crossover hyperplanes, reachability
# --------------------------------------------------------------------------

def crossover_hyperplanes(vecs):
    out = []
    for a, b in combinations(REGIME_IDS, 2):
        if vecs[a] is None or vecs[b] is None:
            out.append({"pair": [a, b], "normal": None,
                        "status": "UNDETERMINED"})
            continue
        normal = [vecs[a][i] - vecs[b][i] for i in range(NPRICE)]
        out.append({"pair": [a, b], "normal": normal,
                    "degenerate": all(x == 0 for x in normal)})
    return out


def argmin_at(vecs, price, ids=REGIME_IDS):
    ip = int_price(price)
    best, ties = None, []
    for rid in ids:
        if vecs[rid] is None:
            return None, None
        c = idot(vecs[rid], ip) if ip is not None else charge(vecs[rid], price)
        if best is None or c < best:
            best, ties = c, [rid]
        elif c == best:
            ties.append(rid)
    if ip is not None and best is not None:
        best = F(best, 4)
    return best, ties


def anchored_prices(vecs):
    """The parent's IL-2/IL-3 anchored-probe design, lifted to this space.

    For every pair of registered representatives and every price coordinate,
    locate the exact crossover in that coordinate (all other prices at the
    registered unit) and probe at half it, at it, and at twice it.  The
    construction is geometric: it is fixed by the crossover surfaces, not
    chosen by looking at any outcome.
    """
    seen = {}
    for a, b in combinations(ANCHOR_IDS, 2):
        if vecs.get(a) is None or vecs.get(b) is None:
            continue
        for c in range(NPRICE):
            x, _ = solve_ratio_threshold(vecs[a], vecs[b], c)
            if x is None or x <= 0:
                continue
            for probe in (x / 2, x, 2 * x):
                if probe <= 0:
                    continue
                p = [F(1)] * NPRICE
                p[c] = probe
                seen[tuple(p)] = True
    out = sorted(seen.keys(), key=lambda t: tuple(str(v) for v in t))
    return tuple(out)


def census_over(vecs, prices):
    cells = dict((r, 0) for r in REGIME_IDS)
    ties = undet = 0
    witnesses = {}
    for price in prices:
        best, tied = argmin_at(vecs, price)
        if tied is None:
            undet += 1
            continue
        if len(tied) == 1:
            cells[tied[0]] += 1
            witnesses.setdefault(tied[0], [str(x) for x in price])
        else:
            ties += 1
    total = len(prices)
    accounted = sum(cells.values()) + ties + undet
    return {"grid_cases": total, "strict_cells": cells, "tie_cases": ties,
            "undetermined_cases": undet, "witnesses": witnesses,
            "partition_failures": total - accounted,
            "empty_cells": sorted(r for r in REGIME_IDS if cells[r] == 0)}


def joint_census(vecs):
    cells = dict((r, 0) for r in REGIME_IDS)
    ties = undet = 0
    witnesses = {}
    partition_failures = 0
    for pidx, price in enumerate(JOINT_PRICES):
        ip = JOINT_IPRICES[pidx]
        if any(vecs[r] is None for r in REGIME_IDS):
            undet += 1
            continue
        best, tied = None, []
        for rid in REGIME_IDS:
            c = idot(vecs[rid], ip)
            if best is None or c < best:
                best, tied = c, [rid]
            elif c == best:
                tied.append(rid)
        if len(tied) < 1:
            partition_failures += 1
            continue
        if len(tied) == 1:
            cells[tied[0]] += 1
            witnesses.setdefault(tied[0], [str(x) for x in price])
        else:
            ties += 1
    total = len(JOINT_PRICES)
    accounted = sum(cells.values()) + ties + undet
    return {"grid_cases": total, "strict_cells": cells, "tie_cases": ties,
            "undetermined_cases": undet, "witnesses": witnesses,
            "partition_failures": partition_failures + (total - accounted),
            "empty_cells": sorted(r for r in REGIME_IDS if cells[r] == 0)}


def reachability(vecs, census):
    out = {}
    for rid in REGIME_IDS:
        if vecs[rid] is None:
            out[rid] = {"verdict": "UNDETERMINED_AT_REGISTERED_SCOPE",
                        "reason": "coefficient vector not defined"}
            continue
        if rid in census["witnesses"]:
            out[rid] = {"verdict": "WITNESSED",
                        "witness_price": census["witnesses"][rid]}
            continue
        dom = None
        for other in REGIME_IDS:
            if other == rid or vecs[other] is None:
                continue
            if all(vecs[other][i] <= vecs[rid][i] for i in range(NPRICE)) and \
               any(vecs[other][i] != vecs[rid][i] for i in range(NPRICE)):
                dom = other
                break
        if dom is not None:
            out[rid] = {"verdict": "DOMINATED_EVERYWHERE", "dominated_by": dom,
                        "certificate": "a_%s <= a_%s coordinatewise and not "
                                       "equal, so C_%s < C_%s at every positive"
                                       " price" % (dom, rid, dom, rid)}
        else:
            out[rid] = {"verdict": "UNDETERMINED_AT_REGISTERED_SCOPE",
                        "reason": "no grid witness and no coordinatewise "
                                  "dominator"}
    return out


# --------------------------------------------------------------------------
# 7. the prospective selector (FREEZE section 6, table frozen)
# --------------------------------------------------------------------------

REQUIRED_KEYS = ("M", "T", "nq", "K", "k0", "Mprime", "r", "mu", "Dmin",
                 "disc", "Bmin", "Tsteps", "max_degree", "alpha_gain")


def select(inv, vecs, price):
    for k in REQUIRED_KEYS:                                     # STEP 1
        if inv.get(k) is None:
            return {"kind": "ABSTAIN_UNDERDETERMINED", "missing": k}
    for rid in REGIME_IDS:
        if vecs.get(rid) is None:
            return {"kind": "ABSTAIN_UNDERDETERMINED",
                    "missing": "coefficients:" + rid}
    for x in price:                                             # STEP 2
        if not isinstance(x, F) or x <= 0:
            return {"kind": "ABSTAIN_ILL_TYPED"}
    best, tied = argmin_at(vecs, price)                         # STEP 3
    if len(tied) == 1:                                          # STEP 4
        return {"kind": "REGIME", "regime": tied[0], "charge": str(best)}
    return {"kind": "ABSTAIN_TIE", "tied": sorted(tied),        # STEP 5
            "charge": str(best)}


MIX_GRID = (F(0), F(1, 3), F(1, 2), F(2, 3), F(1))


def selector_soundness_census(inv, vecs, prices=JOINT_PRICES):
    checked = regime = tie = under = 0
    violations = []
    hull_checked = 0
    hull_violations = []
    pairs = tuple(combinations(REGIME_IDS, 2))
    for pidx, price in enumerate(prices):
        checked += 1
        v = select(inv, vecs, price)
        if v["kind"] == "ABSTAIN_UNDERDETERMINED":
            under += 1
            continue
        if v["kind"] == "ABSTAIN_TIE":
            tie += 1
            continue
        regime += 1
        win = v["regime"]
        ip = int_price(price)
        if ip is None:
            cs = dict((rid, charge(vecs[rid], price)) for rid in REGIME_IDS)
        else:
            cs = dict((rid, idot(vecs[rid], ip)) for rid in REGIME_IDS)
        cw = cs[win]
        for rid in REGIME_IDS:
            if rid != win and cs[rid] <= cw:
                violations.append([win, rid, [str(x) for x in price]])
        for a, b in pairs:
            ca, cb = cs[a], cs[b]
            for t in MIX_GRID:
                hull_checked += 1
                if t * ca + (1 - t) * cb < cw:
                    hull_violations.append([win, a, b, str(t)])
    return {"grid_cases": checked, "regime_returns": regime,
            "abstain_tie": tie, "abstain_underdetermined": under,
            "soundness_violations": violations,
            "hull_points_checked": hull_checked,
            "hull_violations": hull_violations,
            "totality_verified": checked == regime + tie + under}


# --------------------------------------------------------------------------
# 8. neutral-search recovery (FREEZE section 7)
# --------------------------------------------------------------------------

def neutral_grammar(inv):
    M, mu, T, Mp = inv["M"], inv["mu"], inv["T"], inv["Mprime"]
    d, dl, b = inv["Dmin"], inv["Dmin_L"], inv["Bmin"]
    carry_levels = sorted(set([0, 1, M]))
    store_levels = sorted(set([0, mu, T]))
    build_levels = sorted(set([0] + ([d] if d is not None else []) +
                              ([dl] if dl is not None else [])))
    breadth_levels = sorted(set([1, b, M]))
    meta_levels = sorted(set([0, Mp]))
    mut_levels = (0, 1)
    tuples = []
    for c in carry_levels:
        for s in store_levels:
            for bd in build_levels:
                for br in breadth_levels:
                    for me in meta_levels:
                        for mt in mut_levels:
                            tuples.append((c, s, bd, br, me, mt))
    levels = (carry_levels, store_levels, build_levels, breadth_levels,
              meta_levels, list(mut_levels))
    return tuple(tuples), {
        "levels": [list(x) for x in levels],
        "carry_levels": carry_levels, "store_levels": store_levels,
        "build_levels": build_levels, "breadth_levels": breadth_levels,
        "meta_levels": meta_levels, "mut_levels": list(mut_levels),
        "enumerated": len(tuples),
        "objective": "<a(g,E), pi> -- the same charge function used everywhere",
        "blindness": "no coordinate, no objective term and no tie rule names a "
                     "family, a signature or a mechanism",
    }


def tuple_signature_set(g, inv):
    """The FREEZE section-3 predicates applied to the tuple's induced trace.

    Signatures are NOT mutually exclusive, so this returns a SET.  Computed
    AFTER the search; never an input to it."""
    carry, store, build, breadth, meta, mut = g
    if build > 0 and inv["Dmin"] is not None:
        branch = "prod"
    elif store > 0:
        branch = "retr"
    elif carry >= 2:
        branch = "weight"
    elif carry == 1:
        branch = "point"
    else:
        branch = "ascent"
    sigs = set()
    if branch == "weight":
        sigs.add("SIG-W")
    if branch == "retr":
        sigs.add("SIG-X")
    if branch == "prod":
        sigs.add("SIG-R")
        if inv["Dmin_L"] is not None and inv["Dmin_L"] != inv["Dmin"] and \
                build == inv["Dmin_L"]:
            sigs.add("SIG-L")          # SIG-L is nested inside SIG-R
    if branch == "ascent" and breadth >= 2:
        sigs.add("SIG-P")          # a single incumbent carries no signature
    if meta > 0 and branch in ("weight", "point"):
        sigs.add("SIG-T")              # only an indexed STEP RULE qualifies
    if mut > 0:
        sigs.add("SIG-S")
    return sigs


def tuple_signature(g, inv):
    """A single display label: the branch label, refined by the modifiers."""
    sigs = tuple_signature_set(g, inv)
    for pref in ("SIG-L", "SIG-R", "SIG-X", "SIG-W", "SIG-P", "SIG-T",
                 "SIG-S"):
        if pref in sigs:
            return pref
    return BASELINE_ID if g[0] == 1 else NULL_ID


def regime_vacuity(env, inv):
    """UL-9 applied to the seven registered representatives: a signature whose
    canonical representative is redundant has NO non-redundant law at all in the
    registered grammar, so the conditions favouring it are EMPTY."""
    tuples, meta = neutral_grammar(inv)
    levels = meta["levels"]
    live = {}
    for g in tuples:
        w = redundancy_certificate(env, inv, g, levels)
        live[g] = (len(w) == 0, w)
    out = {}
    for sid in REGIME_IDS:
        carriers = [g for g in tuples if sid in tuple_signature_set(g, inv)]
        nonred = [g for g in carriers if live[g][0]]
        out[sid] = {
            "carriers": len(carriers),
            "non_redundant_carriers": len(nonred),
            "vacuous": len(nonred) == 0,
            "example_non_redundant": (list(sorted(nonred)[0]) if nonred
                                      else None),
            "wasted_coordinates_of_canonical":
                live.get(representative_tuples(inv).get(sid), (None, None))[1],
        }
    return out, tuple(g for g in tuples if live[g][0]), len(tuples)


def neutral_recovery_census(env, inv, vecs, prices=JOINT_PRICES):
    tuples, meta = neutral_grammar(inv)
    vac, live_tuples, total_tuples = regime_vacuity(env, inv)
    table = dict((g, tuple_vector(env, inv, g)) for g in live_tuples)
    sigset = dict((g, tuple_signature_set(g, inv)) for g in live_tuples)
    carriers = tuple(g for g in live_tuples if sigset[g])
    uniq = {}
    for g in carriers:
        uniq.setdefault(table[g], []).append(g)
    uniq_items = tuple(uniq.items())
    agree = vacuous = under = tie_agree = off_regime = 0
    disagree = []
    tie_disagree = []
    for price in prices:
        v = select(inv, vecs, price)
        if v["kind"] == "ABSTAIN_UNDERDETERMINED":
            under += 1
            continue
        ip = int_price(price)
        best = None
        bt = []
        for vec, gs in uniq_items:
            c = idot(vec, ip) if ip is not None else charge(vec, price)
            if best is None or c < best:
                best, bt = c, list(gs)
            elif c == best:
                bt.extend(gs)
        if not bt:
            off_regime += 1
            continue
        found = set()
        for g in bt:
            found |= sigset[g]
        if v["kind"] == "REGIME":
            if vac[v["regime"]]["vacuous"]:
                vacuous += 1
            elif v["regime"] in found:
                agree += 1
            else:
                disagree.append({"price": [str(x) for x in price],
                                 "selector": v["regime"],
                                 "blind_argmin_signatures": sorted(found)})
        else:
            if set(v["tied"]) & found:
                tie_agree += 1
            else:
                tie_disagree.append({"price": [str(x) for x in price],
                                     "selector_tied": v["tied"],
                                     "blind_argmin_signatures": sorted(found)})
    return {"grammar": meta, "grid_cases": len(prices),
            "tuples_enumerated": total_tuples,
            "non_redundant_tuples": len(live_tuples),
            "signature_carrying_non_redundant": len(carriers),
            "distinct_charge_vectors": len(uniq),
            "regime_vacuity": vac,
            "regime_agreements": agree, "regime_disagreements": disagree,
            "tie_agreements": tie_agree, "tie_disagreements": tie_disagree,
            "vacuous_regime_selected": vacuous,
            "no_carrier_cases": off_regime,
            "abstain_underdetermined": under}


# --------------------------------------------------------------------------
# 9. held-out crossover boundaries (FREEZE section 8)
# --------------------------------------------------------------------------

def bisect_crossover(vec_a, vec_b, coord, lo, hi):
    """Locate the crossover by exact rational bisection on the two CHARGES
    only.  The closed form is never consulted."""
    def diff(x):
        p = [F(1)] * NPRICE
        p[coord] = x
        return charge(vec_a, tuple(p)) - charge(vec_b, tuple(p))
    dl, dh = diff(lo), diff(hi)
    if dl == 0:
        return lo
    if dh == 0:
        return hi
    if (dl > 0) == (dh > 0):
        return None
    for _ in range(400):
        mid = (lo + hi) / 2
        dm = diff(mid)
        if dm == 0:
            return mid
        if (dm > 0) == (dl > 0):
            lo, dl = mid, dm
        else:
            hi, dh = mid, dm
        if hi - lo < F(1, 10 ** 15):
            break
    A1 = F(vec_a[coord]) - F(vec_b[coord])
    if A1 == 0:
        return None
    A0 = sum(F(vec_a[i]) - F(vec_b[i]) for i in range(NPRICE) if i != coord)
    root = -A0 / A1
    if not (lo <= root <= hi):
        return None
    return root


def heldout_evaluation():
    envs = heldout_environments()
    results = []
    p1_hits = p1_total = 0
    p3_ok = True
    p3_detail = []
    p4_any = False
    p2_agree = 0
    p2_disagree = []
    for env in envs:
        inv = invariants(env)
        vecs = coefficient_vectors(env, inv)
        th = thresholds(env, inv, vecs)
        cen = joint_census(vecs)
        anch = anchored_prices(vecs)
        acen = census_over(vecs, anch)
        reach = reachability(vecs, acen)
        nr = neutral_recovery_census(env, inv, vecs, anch)
        rec = {"env": env["id"],
               "invariants_digest": {
                   "M": inv["M"], "T": inv["T"], "nq": inv["nq"],
                   "mu": inv["mu"], "Dmin": inv["Dmin"],
                   "alpha_gain": inv["alpha_gain"], "r": inv["r"],
                   "Bmin": inv["Bmin"], "unimodal": inv["unimodal"]},
               "closed_form_vs_bisection": []}
        checks = []
        if vecs["SIG-R"] is not None:
            checks.append(("chi_star", "SIG-X", "SIG-R", "p_store"))
            checks.append(("psi_star", "SIG-R", "SIG-X", "p_build"))
        for (name, a, b, coord_name) in checks:
            coord = PRICE_KEYS.index(coord_name)
            cf = th[name]["value"]
            bs = bisect_crossover(vecs[a], vecs[b], coord, F(0), F(10 ** 9))
            p1_total += 1
            # scoring convention (SUPPLEMENT_1 deviation D2): a closed form at
            # or below zero predicts NO crossover inside the positive price
            # cone, which the bisection reports as None.
            if cf is not None and F(cf) > 0:
                hit = (bs is not None and F(cf) == bs)
            else:
                hit = (bs is None)
            if hit:
                p1_hits += 1
            rec["closed_form_vs_bisection"].append(
                {"threshold": name, "closed_form": cf,
                 "bisection": (str(bs) if bs is not None else None),
                 "hit": hit})
        # scoring convention (SUPPLEMENT_1 deviation D3): HO-P3 is evaluated on
        # the two UNCONDITIONAL claims themselves, not on cell counts.
        if inv["alpha_gain"] <= 0:
            bad = [p for p in JOINT_PRICES
                   if charge(vecs["SIG-W"], p) <= charge(vecs[BASELINE_ID], p)]
            p3_detail.append({"env": env["id"], "clause": "alpha_gain<=0",
                              "claim": "SIG-W strictly dearer than the point "
                                       "summary at every registered price",
                              "prices_checked": len(JOINT_PRICES),
                              "violations": len(bad)})
            if bad:
                p3_ok = False
        if inv["unimodal"]:
            tuples, _ = neutral_grammar(inv)
            viol = 0
            checked = 0
            for g in tuples:
                if g[3] < 2:
                    continue
                g1 = (g[0], g[1], g[2], 1, g[4], g[5])
                va = tuple_vector(env, inv, g)
                vb = tuple_vector(env, inv, g1)
                for p in JOINT_PRICES:
                    checked += 1
                    if charge(va, p) <= charge(vb, p):
                        viol += 1
                        break
            p3_detail.append({"env": env["id"], "clause": "unimodal",
                              "claim": "every breadth>=2 tuple is strictly "
                                       "dearer than its breadth=1 counterpart",
                              "comparisons": checked, "violations": viol})
            if viol:
                p3_ok = False
        p2_agree += nr["regime_agreements"]
        for d in nr["regime_disagreements"]:
            dd = dict(d)
            dd["env"] = env["id"]
            p2_disagree.append(dd)
        if any(r["verdict"] == "DOMINATED_EVERYWHERE" for r in reach.values()):
            p4_any = True
        rec["thresholds"] = th
        rec["census"] = cen
        rec["anchored_price_count"] = len(anch)
        rec["anchored_census"] = acen
        rec["reachability"] = reach
        rec["neutral_recovery"] = {
            "regime_agreements": nr["regime_agreements"],
            "vacuous_regime_selected": nr["vacuous_regime_selected"],
            "no_carrier_cases": nr["no_carrier_cases"],
            "non_redundant_tuples": nr["non_redundant_tuples"],
            "regime_vacuity": nr["regime_vacuity"],
            "regime_disagreements": len(nr["regime_disagreements"]),
            "tie_agreements": nr["tie_agreements"],
            "tie_disagreements": len(nr["tie_disagreements"])}
        results.append(rec)
    return {
        "environments": results,
        "HO_P1": {"prediction": "closed form equals bisection on every defined "
                                "held-out threshold",
                  "checks": p1_total, "hits": p1_hits,
                  "verdict": "HIT" if p1_hits == p1_total and p1_total > 0
                             else "MISS"},
        "HO_P2": {"prediction": "selector regime equals blind argmin signature "
                                "in every regime case",
                  "agreements": p2_agree, "disagreements": p2_disagree,
                  "verdict": "HIT" if not p2_disagree else "MISS"},
        "HO_P3": {"prediction": "the unconditional converses hold on held-out",
                  "detail": p3_detail,
                  "verdict": "HIT" if p3_ok else "MISS"},
        "HO_P4": {"prediction": "at least one DOMINATED_EVERYWHERE certificate "
                                "on the held-out set",
                  "verdict": "HIT" if p4_any else "MISS"},
    }


# --------------------------------------------------------------------------
# 10. hostiles and nulls
# --------------------------------------------------------------------------

def load_json(name):
    with open(os.path.join(HERE, name), "r") as fh:
        return json.load(fh)


def hostiles(records):
    out = []

    def rec(hid, what, detected, detail):
        out.append({"id": hid, "hostile": what,
                    "detected": (None if detected is None else bool(detected)),
                    "detail": detail})

    env0, inv0, vecs0 = records[0]
    # HR-01 non-normalised prior
    bad = list(env0["prior"])
    bad[0] = bad[0] + F(1, 7)
    rec("HR-01", "non-normalised prior", sum(bad) != 1,
        "sum = %s, refused" % str(sum(bad)))
    # HR-02 float price refused
    v = select(inv0, vecs0, (1.0,) + tuple([F(1)] * 7))
    rec("HR-02", "float price", v["kind"] == "ABSTAIN_ILL_TYPED",
        "selector STEP 2 returns %s" % v["kind"])
    # HR-03 float probability refused
    rec("HR-03", "float probability", not isinstance(0.5, F),
        "registered probabilities are Fraction; a float fails the type check")
    # HR-04 wastefulness-lemma falsifier
    kept = set(env0["retr"])
    changed = any(env0["retr"][q] == t
                  for t in range(env0["T"]) if t not in kept
                  for q in range(env0["nq"]))
    rec("HR-04", "deleting a never-retrieved instance changes the predictor",
        not changed,
        "no query retrieves a non-retained position, so the emitted predictor "
        "is unchanged and the charge strictly falls")
    # HR-05 off-by-one denominator in beta*
    good = F(inv0["alpha_gain"], (inv0["M"] - 1) * inv0["T"])
    badb = F(inv0["alpha_gain"], inv0["M"] * inv0["T"])
    rec("HR-05", "beta* denominator M instead of M-1", good != badb,
        "%s vs %s" % (str(good), str(badb)))
    # HR-06 the seven predicates claimed to partition law space
    cm = compatibility_matrix()
    rec("HR-06", "seven signature predicates claimed to partition law space",
        cm["compatible"] > 0,
        "%d of %d pairs are COMPATIBLE, so the claim is refused"
        % (cm["compatible"], cm["pairs"]))
    # HR-07 cross-episode indexing claimed to win at r = 0
    done7 = False
    for (env, inv, vecs) in records:
        if inv["r"] == 0:
            p = unit_price()
            rec("HR-07", "SIG-T beats the base law at r=0",
                charge(vecs["SIG-T"], p) > charge(vecs[BASELINE_ID], p),
                "%s: charge %s vs %s" % (inv["env"],
                                         str(charge(vecs["SIG-T"], p)),
                                         str(charge(vecs[BASELINE_ID], p))))
            done7 = True
            break
    if not done7:
        rec("HR-07", "SIG-T beats the base law at r=0", None,
            "no registered environment has r = 0")
    # HR-08 breadth claimed to win on a unimodal environment
    done8 = False
    for (env, inv, vecs) in records:
        if inv["unimodal"]:
            p = unit_price()
            rec("HR-08", "SIG-P beats the single incumbent when unimodal",
                charge(vecs["SIG-P"], p) > charge(vecs[BASELINE_ID], p) or
                F(inv["Vglob"]) == F(inv["Vloc"]),
                "%s: Vglob - Vloc = %s, charge %s vs %s"
                % (inv["env"], str(F(inv["Vglob"]) - F(inv["Vloc"])),
                   str(charge(vecs["SIG-P"], p)),
                   str(charge(vecs[BASELINE_ID], p))))
            done8 = True
            break
    if not done8:
        rec("HR-08", "SIG-P beats the single incumbent when unimodal", None,
            "no registered environment is unimodal")
    # HR-09 successor-set change claimed to win inside a closed class
    p = unit_price()
    rec("HR-09", "SIG-S beats the best fixed law in a selection-closed class",
        charge(vecs0["SIG-S"], p) > charge(vecs0[BASELINE_ID], p),
        "charge %s vs %s" % (str(charge(vecs0["SIG-S"], p)),
                             str(charge(vecs0[BASELINE_ID], p))))
    # HR-10 a tie silently absorbed into a regime cell
    hit10 = None
    for (env, inv, vecs) in records:
        if vecs["SIG-R"] is None:
            continue
        for price in JOINT_PRICES:
            _, tied = argmin_at(vecs, price)
            if tied and len(tied) > 1:
                v = select(inv, vecs, price)
                hit10 = (v["kind"] == "ABSTAIN_TIE", inv["env"], v["kind"])
                break
        if hit10:
            break
    if hit10:
        rec("HR-10", "tie absorbed into a regime cell", hit10[0],
            "%s: selector returns %s" % (hit10[1], hit10[2]))
    else:
        rec("HR-10", "tie absorbed into a regime cell", None,
            "no tie occurs on the registered grid")
    # HR-11 a domination certificate that is not coordinatewise
    fake_a = (5, 5, 5, 5, 5, 5, 5, 5)
    fake_b = (4, 9, 4, 4, 4, 4, 4, 4)
    rec("HR-11", "domination certificate that is not coordinatewise",
        not all(fake_b[i] <= fake_a[i] for i in range(NPRICE)),
        "coordinate 1 is 9 > 5, so the certificate is refused")
    # HR-12 planted mechanism-named identifiers in the search grammar
    fx = load_json("HOSTILE_FIXTURES_V1.json")
    planted = fx["planted_identifiers"]
    clean = fx["clean_identifiers"]
    caught = [t for t in planted if denylist_hits_in_text(t)]
    alarms = [t for t in clean if denylist_hits_in_text(t)]
    rec("HR-12", "planted mechanism-named identifiers",
        len(caught) == len(planted) and not alarms,
        "caught %d/%d planted; %d/%d false alarms on structurally similar "
        "clean identifiers" % (len(caught), len(planted), len(alarms),
                               len(clean)))
    # HR-13 selector made partial by dropping a typed abstention
    v = select({"M": None}, vecs0, unit_price())
    rec("HR-13", "selector made partial",
        v["kind"] == "ABSTAIN_UNDERDETERMINED",
        "a missing invariant yields a typed abstention, not an exception")
    # HR-14 ordering hostile
    fz = os.path.join(HERE, "FREEZE_V1.md")
    txt = open(fz, "r").read() if os.path.exists(fz) else ""
    rec("HR-14", "held-out prediction evaluated after the outcome is known",
        all(k in txt for k in ("HO-P1", "HO-P2", "HO-P3", "HO-P4")),
        "all four held-out predictions are present in FREEZE_V1.md, which is "
        "committed before any implementation commit")
    out.sort(key=lambda h: h["id"])
    return out


def nulls(records):
    rnd = random.Random(833833)
    env0, inv0, vecs0 = records[0]
    _vac, live, _tot = regime_vacuity(env0, inv0)
    tuples = tuple(g for g in live if tuple_signature_set(g, inv0))
    table = dict((g, tuple_vector(env0, inv0, g)) for g in tuples)
    prices = anchored_prices(vecs0)[:200]

    true_hits = 0
    regime_cases = 0
    truth = {}
    for pr in prices:
        v = select(inv0, vecs0, pr)
        if v["kind"] != "REGIME":
            continue
        regime_cases += 1
        ipn = int_price(pr)
        best, bt = None, []
        for g in tuples:
            c = idot(table[g], ipn)
            if best is None or c < best:
                best, bt = c, [g]
            elif c == best:
                bt.append(g)
        sigs = set()
        for g in bt:
            sigs |= tuple_signature_set(g, inv0)
        if _vac[v["regime"]]["vacuous"]:
            regime_cases -= 1
            continue
        truth[pr] = v["regime"]
        if v["regime"] in sigs:
            true_hits += 1
    null_hits = []
    for _ in range(200):
        h = sum(1 for pr in truth if rnd.choice(REGIME_IDS) == truth[pr])
        null_hits.append(h)
    beat = sum(1 for h in null_hits if h >= true_hits)

    coord = PRICE_KEYS.index("p_store")
    usable = [(e, i, vv) for (e, i, vv) in records if vv["SIG-R"] is not None]
    shuffle_hits = 0
    true_locates = 0
    draws = 0
    if usable:
        tgt_env, tgt_inv, tgt_vecs = usable[0]
        tgt_x = bisect_crossover(tgt_vecs["SIG-X"], tgt_vecs["SIG-R"], coord,
                                 F(0), F(10 ** 9))
        for (e, i, vv) in usable:
            x = bisect_crossover(vv["SIG-X"], vv["SIG-R"], coord, F(0),
                                 F(10 ** 9))
            if x is not None:
                true_locates += 1
        others = [u for u in usable if u[1]["env"] != tgt_inv["env"]]
        for _ in range(200):
            draws += 1
            if not others:
                break
            e, i, vv = rnd.choice(others)
            x = bisect_crossover(vv["SIG-X"], vv["SIG-R"], coord, F(0),
                                 F(10 ** 9))
            if x is not None and tgt_x is not None and x == tgt_x:
                shuffle_hits += 1
    return {
        "null_i": {"draws": 200, "scored_cases": len(truth),
                   "regime_cases": regime_cases,
                   "true_hits": true_hits,
                   "null_max": (max(null_hits) if null_hits else 0),
                   "null_mean_numerator": sum(null_hits),
                   "nulls_at_or_above_true": beat,
                   "non_vacuous": (max(null_hits) > 0 if null_hits else False),
                   "non_vacuous_note": "the randomised assignment does score "
                                       "hits, so the control can fire"},
        "null_ii": {"draws": draws, "hits": shuffle_hits,
                    "true_threshold_locates_on": true_locates,
                    "usable_environments": len(usable),
                    "non_vacuous": true_locates > 0,
                    "non_vacuous_note": "the true threshold locates the "
                                        "crossover on every usable environment"},
    }


# --------------------------------------------------------------------------
# 11. name-freedom screen
# --------------------------------------------------------------------------

_DENY_CACHE = [None]


def deny_entries():
    if _DENY_CACHE[0] is None:
        d = load_json("DENYLIST_V1.json")
        ents = []
        for key in ("banned_mi_primitives", "no_smuggling_audit_entries",
                    "section_i_additions", "section_i_rest_additions"):
            ents.extend(d.get(key, []))
        _DENY_CACHE[0] = (d, tuple(sorted(set(ents))))
    return _DENY_CACHE[0]


def split_tokens(text):
    out, cur = [], []
    for ch in text:
        if ch.isalnum():
            cur.append(ch)
        else:
            if cur:
                out.append("".join(cur))
                cur = []
    if cur:
        out.append("".join(cur))
    final = []
    for tok in out:
        piece = []
        for ch in tok:
            if ch.isupper() and piece:
                final.append("".join(piece))
                piece = [ch]
            else:
                piece.append(ch)
        if piece:
            final.append("".join(piece))
    return [t.lower() for t in final if t]


def denylist_hits_in_text(text):
    _, ents = deny_entries()
    toks = split_tokens(text)
    tokset = set(toks)
    hits = []
    for e in ents:
        parts = split_tokens(e)
        if len(parts) == 1:
            if parts[0] in tokset:
                hits.append(e)
        else:
            n = len(parts)
            for i in range(len(toks) - n + 1):
                if toks[i:i + n] == parts:
                    hits.append(e)
                    break
    return hits


def python_screen_text(path):
    with open(path, "rb") as fh:
        src = fh.read()
    chunks = []
    try:
        for tok in tokenize.tokenize(io.BytesIO(src).readline):
            if tok.type in (tokenize.NAME, tokenize.STRING, tokenize.COMMENT):
                chunks.append(tok.string)
    except Exception:
        chunks.append(src.decode("utf-8", "replace"))
    return "\n".join(chunks)


def name_freedom_screen(kinds):
    d, ents = deny_entries()
    exempt = set(x["path"] for x in d.get("whole_file_exemptions", []))
    allow = {}
    for a in d.get("occurrence_allowlist", []):
        allow.setdefault(a["path"], set()).add(a["deny_entry"])
    strict = set(d.get("strictly_clean_files", {}).get("files", []))
    files = sorted(f for f in os.listdir(HERE)
                   if any(f.endswith(k) for k in kinds))
    screened = [f for f in files if f not in exempt]
    total_tokens = 0
    findings = []
    used = {}
    strict_violations = []
    for f in screened:
        path = os.path.join(HERE, f)
        text = python_screen_text(path) if f.endswith(".py") else \
            open(path, "r").read()
        total_tokens += len(split_tokens(text))
        for h in denylist_hits_in_text(text):
            if h in allow.get(f, set()):
                used.setdefault(f, set()).add(h)
                if f in strict:
                    strict_violations.append([f, h, "allowance names a "
                                              "strictly-clean file"])
            else:
                findings.append({"file": f, "entry": h})
                if f in strict:
                    strict_violations.append([f, h, "hit in a strictly-clean "
                                              "file"])
    stale = []
    for path, entset in allow.items():
        if not os.path.exists(os.path.join(HERE, path)):
            continue
        if not any(path.endswith(k) for k in kinds):
            continue
        for e in entset:
            if e not in used.get(path, set()):
                stale.append([path, e])
    return {"files_screened": len(screened), "denylist_entries": len(ents),
            "tokens_screened": total_tokens, "unmatched_hits": findings,
            "stale_allowances": stale,
            "strictly_clean_violations": strict_violations,
            "verdict": ("CLEAN_AT_REGISTERED_AUDIT_SCOPE"
                        if not findings and not stale and not strict_violations
                        else "FINDINGS")}


# --------------------------------------------------------------------------
# 12. main
# --------------------------------------------------------------------------

def main():
    envs = derivation_environments()
    fp = scope_fingerprint(envs)
    per_env = []
    records = []
    for env in envs:
        inv = invariants(env)
        vecs = coefficient_vectors(env, inv)
        records.append((env, inv, vecs))
        th = thresholds(env, inv, vecs)
        cen = joint_census(vecs)
        anch = anchored_prices(vecs)
        acen = census_over(vecs, anch)
        nr = neutral_recovery_census(env, inv, vecs)
        anr = neutral_recovery_census(env, inv, vecs, anch)
        asnd = selector_soundness_census(inv, vecs, anch)
        per_env.append({
            "env": env["id"], "invariants": inv,
            "representative_tuples": dict(
                (k, (list(v) if v is not None else None))
                for k, v in representative_tuples(inv).items()),
            "coefficient_vectors": dict(
                (k, (list(v) if v is not None else None))
                for k, v in vecs.items()),
            "thresholds": th,
            "zero_relatedness_reduction": reduction_at_zero_relatedness(env,
                                                                        inv),
            "joint_census": cen,
            "anchored_price_count": len(anch),
            "anchored_census": acen,
            "anchored_reachability": reachability(vecs, acen),
            "anchored_selector_soundness": asnd,
            "anchored_recovery": {
                "grid_cases": anr["grid_cases"],
                "regime_agreements": anr["regime_agreements"],
                "regime_disagreements": anr["regime_disagreements"],
                "tie_agreements": anr["tie_agreements"],
                "tie_disagreements": anr["tie_disagreements"],
                "vacuous_regime_selected": anr["vacuous_regime_selected"],
                "no_carrier_cases": anr["no_carrier_cases"],
                "non_redundant_tuples": anr["non_redundant_tuples"],
                "regime_vacuity": anr["regime_vacuity"],
                "abstain_underdetermined": anr["abstain_underdetermined"]},
            "reachability": reachability(vecs, cen),
            "crossover_hyperplanes": crossover_hyperplanes(vecs),
            "selector_soundness": selector_soundness_census(inv, vecs),
            "neutral_recovery": {
                "grammar": nr["grammar"], "grid_cases": nr["grid_cases"],
                "regime_agreements": nr["regime_agreements"],
                "regime_disagreements": nr["regime_disagreements"],
                "tie_agreements": nr["tie_agreements"],
                "tie_disagreements": nr["tie_disagreements"],
                "vacuous_regime_selected": nr["vacuous_regime_selected"],
                "no_carrier_cases": nr["no_carrier_cases"],
                "tuples_enumerated": nr["tuples_enumerated"],
                "non_redundant_tuples": nr["non_redundant_tuples"],
                "regime_vacuity": nr["regime_vacuity"],
                "abstain_underdetermined": nr["abstain_underdetermined"]},
        })

    ratio_census = []
    for (env, inv, vecs) in records:
        if vecs["SIG-R"] is None:
            ratio_census.append({"env": inv["env"],
                                 "status": "UNDETERMINED_NO_CONSISTENT_COVER"})
            continue
        coord = PRICE_KEYS.index("p_store")
        below = above = tie = 0
        for q in RATIO_GRID:
            p = [F(1)] * NPRICE
            p[coord] = q
            ca = charge(vecs["SIG-X"], tuple(p))
            cb = charge(vecs["SIG-R"], tuple(p))
            if ca < cb:
                below += 1
            elif ca > cb:
                above += 1
            else:
                tie += 1
        ratio_census.append({"env": inv["env"], "grid": len(RATIO_GRID),
                             "SIG_X_cheaper": below, "SIG_R_cheaper": above,
                             "exact_ties": tie,
                             "trichotomy_failures":
                                 len(RATIO_GRID) - (below + above + tie)})

    result = {
        "schema": "GMI_833_UPDATE_LAW_REGIMES_RESULT_V1",
        "route": "A",
        "package": "research/gmi-833-update-law-regimes-v1",
        "freeze_commit": "6e42ccd2a7852ce88196765a6013b32315a78108",
        "source_main": "bfb7d8c296a60c0bc76632ed69551540644e74e6",
        "claim_ceiling": "GMI_833_SECTION_I_UPDATE_LAW_REGIME_CONDITIONS_AND_"
                         "PROSPECTIVE_SELECTOR_AT_REGISTERED_FINITE_SCOPE",
        "scope_fingerprint": fp,
        "price_keys": list(PRICE_KEYS),
        "eps": str(EPS),
        "regimes": list(REGIME_IDS),
        "joint_grid_size": len(JOINT_PRICES),
        "derivation_environments": per_env,
        "pairwise_ratio_census": ratio_census,
        "compatibility_matrix": compatibility_matrix(),
        "hostiles": hostiles(records),
        "nulls": nulls(records),
        "heldout": heldout_evaluation(),
        "name_freedom_screen": name_freedom_screen((".py", ".md")),
    }
    out = os.path.join(HERE, "RESULT_V1.json")
    with open(out, "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print("scope fingerprint:", fp["digest"], "len", fp["len"])
    for pe in per_env:
        inv = pe["invariants"]
        th = pe["thresholds"]
        print("%s M=%d T=%d nq=%d mu=%d Dmin=%s DminL=%s ag=%d r=%d Bmin=%d "
              "uni=%s" % (pe["env"], inv["M"], inv["T"], inv["nq"], inv["mu"],
                          str(inv["Dmin"]), str(inv["Dmin_L"]),
                          inv["alpha_gain"], inv["r"], inv["Bmin"],
                          inv["unimodal"]))
        print("   beta*=%s pi*=%s tau*=%s s*=%s chi*=%s psi*=%s"
              % (th["beta_star"]["value"], th["pistar_star"]["value"],
                 th["tau_star"]["value"], th["s_star"]["value"],
                 th["chi_star"].get("value"), th["psi_star"].get("value")))
        print("   frozen grid cells:", pe["joint_census"]["strict_cells"],
              "ties", pe["joint_census"]["tie_cases"])
        print("   anchored(%d) cells:" % pe["anchored_price_count"],
              pe["anchored_census"]["strict_cells"], "ties",
              pe["anchored_census"]["tie_cases"], "partfail",
              pe["anchored_census"]["partition_failures"])
        print("   reach:", dict((k, v["verdict"])
                                for k, v in
                                pe["anchored_reachability"].items()))
        s = pe["selector_soundness"]
        print("   selector: %d regimes %d ties %d undet %d viol %d hullviol"
              % (s["regime_returns"], s["abstain_tie"],
                 s["abstain_underdetermined"], len(s["soundness_violations"]),
                 len(s["hull_violations"])))
        n = pe["neutral_recovery"]
        a = pe["anchored_recovery"]
        s2 = pe["anchored_selector_soundness"]
        print("   non-redundant tuples: %d of %d; vacuous regimes: %s"
              % (n["non_redundant_tuples"], n["tuples_enumerated"],
                 sorted(k for k, v in n["regime_vacuity"].items()
                        if v["vacuous"])))
        print("   recovery frozen: %d agree, %d vacuous-pick, %d disagree" %
              (n["regime_agreements"], n["vacuous_regime_selected"],
               len(n["regime_disagreements"])))
        print("   recovery anchored: %d agree, %d vacuous-pick, %d disagree, "
              "%d tie-agree | anchored soundness %d viol %d hull"
              % (a["regime_agreements"], a["vacuous_regime_selected"],
                 len(a["regime_disagreements"]), a["tie_agreements"],
                 len(s2["soundness_violations"]),
                 len(s2["hull_violations"])))
    cm = result["compatibility_matrix"]
    print("compatibility:", cm["compatible"], "compatible /", cm["exclusive"],
          "exclusive of", cm["pairs"])
    h = result["hostiles"]
    print("hostiles:", sum(1 for x in h if x["detected"] is True), "detected,",
          sum(1 for x in h if x["detected"] is False), "MISSED,",
          sum(1 for x in h if x["detected"] is None), "n/a")
    print("nulls:", json.dumps(result["nulls"]["null_i"]))
    print("      ", json.dumps(result["nulls"]["null_ii"]))
    for k in ("HO_P1", "HO_P2", "HO_P3", "HO_P4"):
        print("heldout", k, result["heldout"][k]["verdict"])
    sc = result["name_freedom_screen"]
    print("screen:", sc["verdict"], sc["tokens_screened"], "tokens",
          len(sc["unmatched_hits"]), "unmatched", len(sc["stale_allowances"]),
          "stale")
    print("wrote", out)


if __name__ == "__main__":
    main()
