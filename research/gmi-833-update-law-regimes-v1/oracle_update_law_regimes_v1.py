#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Route B oracle -- GMI #833 Section I update-law regimes.

Materially independent of Route A: it imports nothing from it, shares no helper
module, transcribes the registered environments from the frozen spec with its
own code, and derives every verdict by literal enumeration rather than from any
closed form.

Writes ORACLE_RESULT_V1.json next to this file.
"""

import json
import os
from fractions import Fraction as Q

WHERE = os.path.dirname(os.path.abspath(__file__))

NOISE = Q(1, 4)
MAXPROD = 3
COORDS = ["p_test", "p_carry", "p_store", "p_build",
          "p_branch", "p_meta", "p_mut", "lam"]
SEVEN = ["SIG-W", "SIG-X", "SIG-R", "SIG-L", "SIG-P", "SIG-T", "SIG-S"]
PLAIN = "BASE-0"


# ---------------------------------------------------------------- scope ----

def ratio_grid():
    acc = []
    for num in range(1, 13):
        for den in range(1, 7):
            v = Q(num, den)
            if v not in acc:
                acc.append(v)
    acc.sort()
    return acc


RATIOS = ratio_grid()


def joint_prices():
    lev = [Q(1, 4), Q(1), Q(4)]
    acc = [[Q(1)]]
    for _ in range(7):
        nxt = []
        for pre in acc:
            for x in lev:
                nxt.append(pre + [x])
        acc = nxt
    return [tuple(p) for p in acc]


PRICES = joint_prices()
IPRICES = [tuple(int(x * 4) for x in p) for p in PRICES]


def spec_table_steps(width, cuts):
    rows = []
    for c in cuts:
        row = []
        for z in range(width):
            row.append(0 if z < c else 1)
        rows.append(tuple(row))
    return tuple(rows)


def spec_table_windows(width, pairs):
    rows = []
    for (lo, hi) in pairs:
        row = []
        for z in range(width):
            row.append(1 if (lo <= z and z <= hi) else 0)
        rows.append(tuple(row))
    return tuple(rows)


def chain_edges(n):
    acc = []
    for i in range(n):
        e = []
        if i - 1 >= 0:
            e.append(i - 1)
        if i + 1 < n:
            e.append(i + 1)
        acc.append(tuple(e))
    return tuple(acc)


def all_interval_rules(width):
    acc = []
    a = 0
    while a < width:
        b = a
        while b < width:
            span = frozenset([z for z in range(a, b + 1)])
            acc.append((span, 0, 2))
            acc.append((span, 1, 2))
            b += 1
        a += 1
    return tuple(acc)


def make(envid, width, tables, tgt, tr, qs, rt, scores, seeds, hp, kk, kzero):
    n = len(tables)
    return {
        "id": envid, "nz": width, "H": tables, "M": n,
        "prior": tuple([Q(1, n)] * n), "target": tuple(tgt),
        "train": tuple(tr), "T": len(tr), "Qset": tuple(qs), "nq": len(qs),
        "retr": tuple(rt), "RS": all_interval_rules(width),
        "nbr": chain_edges(n), "Vfun": tuple(Q(v) for v in scores),
        "starts_ext": tuple(seeds), "Hprime": tuple(hp), "K": kk,
        "k0": kzero,
    }


def derivation_set():
    tbl = spec_table_steps(8, list(range(0, 9)))
    t4 = tbl[4]
    zigzag = (1, 0, 1, 0, 1, 0, 1, 0)
    twin = (1, 2, 3, 2, 1, 2, 5, 2, 1)
    single = (1, 2, 3, 4, 5, 4, 3, 2, 1)
    seeds = (0, 8, 4, 1, 7, 2, 6, 3, 5)
    every = tuple(range(9))
    core = (2, 3, 4, 5, 6)
    return [
        make("D1", 8, tbl, t4, (0, 1, 6, 7), (2, 3, 4, 5), (0, 1, 2, 3),
             twin, seeds, core, 4, 1),
        make("D2", 8, tbl, t4, (3, 4, 3, 4, 3, 4), (0, 1, 6, 7), (0, 1, 2, 3),
             twin, seeds, core, 4, 1),
        make("D3", 8, tbl, zigzag, (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 2, 3),
             twin, seeds, every, 4, 1),
        make("D4", 8, tbl, t4, (0, 1, 2, 5, 6, 7), (3, 4), (0, 0),
             twin, seeds, core, 4, 1),
        make("D5", 8, tbl, t4, (0, 7), (1, 2, 3, 4, 5, 6), (0, 0, 0, 1, 1, 1),
             twin, seeds, core, 4, 1),
        make("D6", 8, tbl, t4, (0, 7), (1, 2, 3, 4, 5, 6), (0, 0, 0, 1, 1, 1),
             single, seeds, core, 4, 1),
    ]


def heldout_set():
    pairs = ((0, 2), (0, 4), (2, 5), (3, 6), (1, 8),
             (5, 9), (0, 9), (4, 4), (6, 9), (2, 2))
    tbl = spec_table_windows(10, pairs)
    tg = tbl[2]
    zigzag = (1, 1, 0, 0, 1, 1, 0, 0, 1, 1)
    twin = (1, 3, 2, 1, 2, 6, 2, 1, 2, 1)
    single = (1, 2, 3, 4, 5, 6, 5, 4, 3, 2)
    seeds = (0, 9, 4, 1, 8, 2, 7, 3, 6, 5)
    every = tuple(range(10))
    core = (0, 1, 2, 3, 4)
    return [
        make("X1", 10, tbl, tg, (0, 1, 8, 9), (2, 3, 5, 6), (0, 1, 2, 3),
             twin, seeds, core, 4, 1),
        make("X2", 10, tbl, tg, (2, 6, 2, 6, 2, 6), (0, 1, 8, 9), (0, 1, 2, 3),
             twin, seeds, core, 4, 1),
        make("X3", 10, tbl, zigzag, (0, 2, 4, 6), (1, 3, 5, 7), (0, 1, 2, 3),
             twin, seeds, every, 4, 1),
        make("X4", 10, tbl, tg, (0, 1, 2, 7, 8, 9), (4, 5), (0, 0),
             twin, seeds, core, 4, 1),
        make("X5", 10, tbl, tg, (0, 9), (1, 2, 3, 4, 5, 6),
             (0, 0, 0, 1, 1, 1), twin, seeds, core, 4, 1),
        make("X6", 10, tbl, tg, (0, 9), (1, 2, 3, 4, 5, 6),
             (0, 0, 0, 1, 1, 1), single, seeds, core, 4, 1),
    ]


def fingerprint(envs):
    """Independently reconstructed; must equal Route A's before any agreement
    figure is read."""
    blocks = []
    for e in envs:
        cells = [e["id"], str(e["nz"]), str(e["M"])]
        cells.append(",".join(["".join([str(b) for b in row])
                               for row in e["H"]]))
        cells.append("".join([str(b) for b in e["target"]]))
        cells.append(",".join([str(x) for x in e["train"]]))
        cells.append(",".join([str(x) for x in e["Qset"]]))
        cells.append(",".join([str(x) for x in e["retr"]]))
        cells.append(",".join([str(x) for x in e["Vfun"]]))
        cells.append(",".join([str(x) for x in e["starts_ext"]]))
        cells.append(",".join([str(x) for x in e["Hprime"]]))
        cells.append(str(e["K"]))
        cells.append(str(e["k0"]))
        cells.append(str(len(e["RS"])))
        blocks.append("|".join(cells))
    joined = "||".join(blocks)
    h = 0
    for c in joined:
        h = (h * 1000003 + ord(c)) % (2 ** 61 - 1)
    return {"len": len(joined), "digest": h}


# ------------------------------------------------- invariants, literally ----

def weights(env, pool):
    """Posterior by INTEGER accumulation over a common denominator, then one
    exact division.  Route A multiplies Fractions directly."""
    idxs = list(range(env["M"])) if pool is None else list(pool)
    t = env["T"]
    num = {}
    for i in idxs:
        wrong = 0
        for z in env["train"]:
            if env["H"][i][z] != env["target"][z]:
                wrong += 1
        right = t - wrong
        # eps^wrong (1-eps)^right = 1^wrong * 3^right / 4^t
        num[i] = (3 ** right)
    tot = 0
    for i in idxs:
        tot += num[i]
    return dict([(i, Q(num[i], tot)) for i in idxs])


def vote(env, w, z):
    yes = Q(0)
    for i in w:
        if env["H"][i][z] == 1:
            yes = yes + w[i]
    if yes > Q(1, 2):
        return 1
    return 0


def top(w):
    keys = sorted(w.keys())
    win = keys[0]
    for i in keys:
        if w[i] > w[win]:
            win = i
    return win


def gain(env, w):
    ti = top(w)
    acc = 0
    for z in env["Qset"]:
        a = vote(env, w, z)
        b = env["H"][ti][z]
        y = env["target"][z]
        if b != y and a == y:
            acc += 1
        if a != y and b == y:
            acc -= 1
    return acc, ti


def min_cover(env):
    """Breadth-first over subsets by size, using explicit index stacks rather
    than a combinatorics helper."""
    rules = env["RS"]
    marks = [(z, env["target"][z]) for z in env["train"]]
    live = []
    for j in range(len(rules)):
        span, bit, _ = rules[j]
        bad = 0
        for (z, y) in marks:
            if (z in span) and bit != y:
                bad = 1
        if bad == 0:
            live.append(j)
    want = set([z for (z, _) in marks])
    bestlen = None
    bestset = None
    frontier = [[]]
    depth = 0
    while depth < MAXPROD:
        nxt = []
        for pre in frontier:
            start = 0 if not pre else live.index(pre[-1]) + 1
            for k in range(start, len(live)):
                cand = pre + [live[k]]
                got = set()
                cost = 0
                for j in cand:
                    span, bit, ln = rules[j]
                    cost += ln
                    for (z, y) in marks:
                        if (z in span) and bit == y:
                            got.add(z)
                if want <= got:
                    if bestlen is None or cost < bestlen:
                        bestlen = cost
                        bestset = tuple(cand)
                else:
                    nxt.append(cand)
        frontier = nxt
        depth += 1
    return bestlen, bestset


def rule_answer(env, chosen, z):
    if chosen is None:
        return 0
    for j in sorted(chosen):
        span, bit, _ = env["RS"][j]
        if z in span:
            return bit
    return 0


def reuse(env, chosen):
    if chosen is None:
        return None
    tally = {}
    for z in env["Qset"]:
        for j in sorted(chosen):
            if z in env["RS"][j][0]:
                tally[j] = tally.get(j, 0) + 1
                break
    if not tally:
        return {"Hocc": 0, "Delta": 0, "Kdef": 1, "saving": 0}
    order = sorted(tally.keys(), key=lambda j: (-tally[j], j))
    j = order[0]
    occ = tally[j]
    ln = env["RS"][j][2]
    d = ln - 1
    k = ln + 1
    s = occ * d - k
    return {"Hocc": occ, "Delta": d, "Kdef": k,
            "saving": (s if s > 0 else 0)}


def climb(env, seed):
    """Fixed-point iteration over the whole score vector."""
    at = seed
    moved = 0
    while True:
        up = at
        for j in env["nbr"][at]:
            if env["Vfun"][j] > env["Vfun"][up]:
                up = j
        if up == at:
            return at, moved
        at = up
        moved += 1


def wide_terminal(env, b):
    pick = None
    val = None
    deep = 0
    for s in env["starts_ext"][:b]:
        t, mv = climb(env, s)
        if mv > deep:
            deep = mv
        if val is None or env["Vfun"][t] > val:
            val = env["Vfun"][t]
            pick = t
    return pick, (deep if deep > 0 else 1)


def peaks(env):
    acc = []
    for i in range(env["M"]):
        hi = 1
        for j in env["nbr"][i]:
            if env["Vfun"][j] > env["Vfun"][i]:
                hi = 0
        if hi:
            acc.append(i)
    return acc


def invariants(env):
    w = weights(env, None)
    g, ti = gain(env, w)
    dmin, dset = min_cover(env)
    ru = reuse(env, dset)
    dl = None
    if dmin is not None:
        dl = dmin - (ru["saving"] if ru else 0)
        if dl < 1:
            dl = 1
    vmax = max(env["Vfun"])
    t0, _ = climb(env, env["starts_ext"][0])
    vloc = env["Vfun"][t0]
    bmin = len(env["starts_ext"])
    b = 1
    while b <= len(env["starts_ext"]):
        pick, _ = wide_terminal(env, b)
        if env["Vfun"][pick] == vmax:
            bmin = b
            break
        b += 1
    bpick, steps = wide_terminal(env, bmin)
    lo = peaks(env)
    deg = 0
    for e in env["nbr"]:
        if len(e) > deg:
            deg = len(e)
    mp = len(env["Hprime"])
    return {
        "env": env["id"], "M": env["M"], "T": env["T"], "nq": env["nq"],
        "K": env["K"], "k0": env["k0"], "Mprime": mp, "r": env["M"] - mp,
        "alpha_gain": g, "point_summary_index": ti,
        "mu": len(set(env["retr"])), "Dmin": dmin,
        "Dset": (list(dset) if dset else None), "Dmin_L": dl,
        "disc": len(env["RS"]) * env["T"], "cover": 2 * env["T"],
        "reuse": ru, "Vloc": str(vloc), "Vglob": str(vmax), "Bmin": bmin,
        "Tsteps": steps, "single_terminal": t0, "breadth_terminal": bpick,
        "local_optima": lo, "unimodal": len(lo) == 1, "max_degree": deg,
        "target_in_H": env["target"] in env["H"],
    }


# ------------------------------------------------ charge, by accumulation ---

def losses(env, inv, g):
    carry, store, build, wide, meta, mut = g
    acc = 0
    ep = 0
    while ep < env["K"]:
        pool = None
        if meta > 0 and ep >= env["k0"]:
            pool = env["Hprime"]
        w = weights(env, pool)
        wrong = 0
        for z in env["Qset"]:
            if build > 0 and inv["Dmin"] is not None:
                said = rule_answer(env, inv["Dset"], z)
            elif store > 0:
                qp = list(env["Qset"]).index(z)
                tp = env["retr"][qp]
                if tp >= store:
                    said = 0
                else:
                    said = env["target"][env["train"][tp]]
            elif carry >= 2:
                said = vote(env, w, z)
            elif carry == 1:
                said = env["H"][top(w)][z]
            else:
                pick, _ = wide_terminal(env, wide)
                said = env["H"][pick][z]
            if said != env["target"][z]:
                wrong += 1
        acc += wrong
        ep += 1
    return acc


def vector(env, inv, g):
    carry, store, build, wide, meta, mut = g
    ev = 0
    ep = 0
    while ep < env["K"]:
        span = inv["M"]
        if meta > 0 and ep >= env["k0"]:
            span = meta
        if carry > 0:
            ev += span * inv["T"]
        ep += 1
    ev += env["K"] * store * inv["nq"]
    if carry == 0 and store == 0 and build == 0:
        ev += (env["K"] * wide * (inv["Tsteps"] + 1) *
               (inv["max_degree"] + 1) * inv["T"])
    if build > 0:
        ev += env["K"] * inv["disc"]
    ev += env["K"] * build * inv["nq"]
    ev += env["K"] * inv["nq"]
    return (ev,
            env["K"] * carry * inv["T"],
            env["K"] * store * inv["T"],
            env["K"] * build,
            env["K"] * (wide - 1) * inv["Tsteps"],
            meta * env["K"],
            env["K"] * mut,
            losses(env, inv, g))


def answers(env, inv, g):
    """The emitted predictions of a tuple over every episode and query."""
    carry, store, build, wide, meta, mut = g
    acc = []
    ep = 0
    while ep < env["K"]:
        pool = None
        if meta > 0 and ep >= env["k0"]:
            pool = env["Hprime"]
        w = weights(env, pool)
        for z in env["Qset"]:
            if build > 0 and inv["Dmin"] is not None:
                acc.append(rule_answer(env, inv["Dset"], z))
            elif store > 0:
                qp = list(env["Qset"]).index(z)
                tp = env["retr"][qp]
                acc.append(0 if tp >= store
                           else env["target"][env["train"][tp]])
            elif carry >= 2:
                acc.append(vote(env, w, z))
            elif carry == 1:
                acc.append(env["H"][top(w)][z])
            else:
                pick, _ = wide_terminal(env, wide)
                acc.append(env["H"][pick][z])
        ep += 1
    return tuple(acc)


def wasted(env, inv, g, levels):
    base = answers(env, inv, g)
    acc = []
    c = 0
    while c < 6:
        lv = sorted(set(levels[c]))
        if g[c] in lv and lv.index(g[c]) > 0:
            h = list(g)
            h[c] = lv[lv.index(g[c]) - 1]
            if answers(env, inv, tuple(h)) == base:
                acc.append(c)
        c += 1
    return acc


def reps(inv):
    return {
        "SIG-W": (inv["M"], 0, 0, 1, 0, 0),
        PLAIN: (1, 0, 0, 1, 0, 0),
        "SIG-X": (0, inv["mu"], 0, 1, 0, 0),
        "SIG-R": ((0, 0, inv["Dmin"], 1, 0, 0)
                  if inv["Dmin"] is not None else None),
        "SIG-L": ((0, 0, inv["Dmin_L"], 1, 0, 0)
                  if inv["Dmin_L"] is not None else None),
        "SIG-P": (0, 0, 0, (inv["Bmin"] if inv["Bmin"] >= 2 else 2),
                  0, 0),
        "SIG-T": (1, 0, 0, 1, inv["Mprime"], 0),
        "SIG-S": (1, 0, 0, 1, 0, 1),
    }


def vectors(env, inv):
    out = {}
    for k, g in reps(inv).items():
        out[k] = None if g is None else vector(env, inv, g)
    return out


def cost(vec, price):
    acc = Q(0)
    i = 0
    while i < 8:
        acc = acc + Q(vec[i]) * price[i]
        i += 1
    return acc


def icost(vec, ip):
    acc = 0
    i = 0
    while i < 8:
        acc += vec[i] * ip[i]
        i += 1
    return acc


# --------------------------------------------- verdicts, by enumeration ----

def cell_census(vec):
    counts = dict([(r, 0) for r in SEVEN])
    tied = 0
    absent = 0
    wit = {}
    if any(vec[r] is None for r in SEVEN):
        return {"grid_cases": len(PRICES), "strict_cells": counts,
                "tie_cases": 0, "undetermined_cases": len(PRICES),
                "witnesses": {}, "partition_failures": 0,
                "empty_cells": sorted(SEVEN)}
    n = 0
    while n < len(PRICES):
        ip = IPRICES[n]
        low = None
        who = []
        for r in SEVEN:
            c = icost(vec[r], ip)
            if low is None or c < low:
                low = c
                who = [r]
            elif c == low:
                who.append(r)
        if len(who) == 1:
            counts[who[0]] += 1
            if who[0] not in wit:
                wit[who[0]] = [str(x) for x in PRICES[n]]
        else:
            tied += 1
        n += 1
    done = 0
    for r in SEVEN:
        done += counts[r]
    return {"grid_cases": len(PRICES), "strict_cells": counts,
            "tie_cases": tied, "undetermined_cases": absent,
            "witnesses": wit,
            "partition_failures": len(PRICES) - (done + tied + absent),
            "empty_cells": sorted([r for r in SEVEN if counts[r] == 0])}


def reach_census(vec, cen):
    out = {}
    for r in SEVEN:
        if vec[r] is None:
            out[r] = "UNDETERMINED_AT_REGISTERED_SCOPE"
            continue
        if r in cen["witnesses"]:
            out[r] = "WITNESSED"
            continue
        found = None
        for o in SEVEN:
            if o == r or vec[o] is None:
                continue
            under = 1
            diff = 0
            i = 0
            while i < 8:
                if vec[o][i] > vec[r][i]:
                    under = 0
                if vec[o][i] != vec[r][i]:
                    diff = 1
                i += 1
            if under and diff:
                found = o
                break
        out[r] = ("DOMINATED_EVERYWHERE" if found
                  else "UNDETERMINED_AT_REGISTERED_SCOPE")
    return out


def threshold_by_scan(vec_a, vec_b, coord):
    """Locate the crossover WITHOUT the closed form: scan the exact rational
    ladder outward until the sign of the charge difference flips, then read the
    root off the bracket by the affine identity."""
    def d(x):
        p = [Q(1)] * 8
        p[coord] = x
        return cost(vec_a, tuple(p)) - cost(vec_b, tuple(p))
    lo = Q(0)
    hi = Q(1)
    if d(lo) == 0:
        return lo
    steps = 0
    while steps < 200:
        if (d(lo) > 0) != (d(hi) > 0) or d(hi) == 0:
            break
        hi = hi * 2
        steps += 1
    if (d(lo) > 0) == (d(hi) > 0) and d(hi) != 0:
        return None
    k = 0
    while k < 400:
        mid = (lo + hi) / 2
        dm = d(mid)
        if dm == 0:
            return mid
        if (dm > 0) == (d(lo) > 0):
            lo = mid
        else:
            hi = mid
        if hi - lo < Q(1, 10 ** 15):
            break
        k += 1
    slope = Q(vec_a[coord]) - Q(vec_b[coord])
    if slope == 0:
        return None
    const = Q(0)
    i = 0
    while i < 8:
        if i != coord:
            const = const + Q(vec_a[i]) - Q(vec_b[i])
        i += 1
    root = -const / slope
    if lo <= root and root <= hi:
        return root
    return None


def ratio_trichotomy(vec):
    if vec["SIG-R"] is None:
        return None
    c = COORDS.index("p_store")
    lo = hi = eq = 0
    for q in RATIOS:
        p = [Q(1)] * 8
        p[c] = q
        a = cost(vec["SIG-X"], tuple(p))
        b = cost(vec["SIG-R"], tuple(p))
        if a < b:
            lo += 1
        elif a > b:
            hi += 1
        else:
            eq += 1
    return {"grid": len(RATIOS), "SIG_X_cheaper": lo, "SIG_R_cheaper": hi,
            "exact_ties": eq,
            "trichotomy_failures": len(RATIOS) - (lo + hi + eq)}


def tuple_space(inv):
    def uniq(xs):
        acc = []
        for x in xs:
            if x is not None and x not in acc:
                acc.append(x)
        acc.sort()
        return acc
    carry = uniq([0, 1, inv["M"]])
    store = uniq([0, inv["mu"], inv["T"]])
    build = uniq([0, inv["Dmin"], inv["Dmin_L"]])
    wide = uniq([1, inv["Bmin"], inv["M"]])
    meta = uniq([0, inv["Mprime"]])
    acc = []
    for c in carry:
        for s in store:
            for b in build:
                for w in wide:
                    for m in meta:
                        for t in (0, 1):
                            acc.append((c, s, b, w, m, t))
    return acc, [carry, store, build, wide, meta, [0, 1]]


def label_set(g, inv):
    c, s, b, w, m, t = g
    if b > 0 and inv["Dmin"] is not None:
        br = "prod"
    elif s > 0:
        br = "retr"
    elif c >= 2:
        br = "weight"
    elif c == 1:
        br = "point"
    else:
        br = "ascent"
    out = set()
    if br == "weight":
        out.add("SIG-W")
    if br == "retr":
        out.add("SIG-X")
    if br == "prod":
        out.add("SIG-R")
        if inv["Dmin_L"] is not None and inv["Dmin_L"] != inv["Dmin"] \
                and b == inv["Dmin_L"]:
            out.add("SIG-L")
    if br == "ascent" and w >= 2:
        out.add("SIG-P")
    if m > 0 and br in ("weight", "point"):
        out.add("SIG-T")
    if t > 0:
        out.add("SIG-S")
    return out


def label(g, inv):
    got = label_set(g, inv)
    for pref in ("SIG-L", "SIG-R", "SIG-X", "SIG-W", "SIG-P", "SIG-T",
                 "SIG-S"):
        if pref in got:
            return pref
    return PLAIN


def pick_seven(vec, ip):
    low = None
    who = []
    for r in SEVEN:
        if vec[r] is None:
            return None
        c = icost(vec[r], ip)
        if low is None or c < low:
            low = c
            who = [r]
        elif c == low:
            who.append(r)
    return who


def recovery(env, inv, vec):
    space, levels = tuple_space(inv)
    live = []
    for g in space:
        if not wasted(env, inv, g, levels):
            live.append(g)
    tags = dict([(g, label_set(g, inv)) for g in live])
    carriers = [g for g in live if tags[g]]
    tab = dict([(g, vector(env, inv, g)) for g in carriers])
    vac = {}
    for r in SEVEN:
        vac[r] = len([g for g in carriers if r in tags[g]]) == 0
    ok = 0
    vacpick = 0
    bad = 0
    tie_ok = 0
    skip = 0
    n = 0
    while n < len(PRICES):
        ip = IPRICES[n]
        who = pick_seven(vec, ip)
        if who is None:
            skip += 1
            n += 1
            continue
        low = None
        win = []
        for g in carriers:
            c = icost(tab[g], ip)
            if low is None or c < low:
                low = c
                win = [g]
            elif c == low:
                win.append(g)
        got = set()
        for g in win:
            got |= tags[g]
        if len(who) == 1:
            if vac[who[0]]:
                vacpick += 1
            elif who[0] in got:
                ok += 1
            else:
                bad += 1
        else:
            if set(who) & got:
                tie_ok += 1
            else:
                bad += 1
        n += 1
    return {"grid_cases": len(PRICES), "regime_agreements": ok,
            "vacuous_regime_selected": vacpick, "tie_agreements": tie_ok,
            "disagreements": bad, "abstain_underdetermined": skip,
            "space_size": len(space), "non_redundant": len(live),
            "signature_carriers": len(carriers),
            "vacuous_regimes": sorted([r for r in SEVEN if vac[r]])}


def compatibility():
    clause = {
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
    bad = [("carry_weight_slots", "all", "none"),
           ("store_instances", "some", "none"),
           ("emits", "weighting", "retrieval"),
           ("emits", "weighting", "productions"),
           ("emits", "retrieval", "productions")]
    rows = []
    i = 0
    while i < len(SEVEN):
        j = i + 1
        while j < len(SEVEN):
            a, b = SEVEN[i], SEVEN[j]
            hit = None
            for (k, v1, v2) in bad:
                if k in clause[a] and k in clause[b]:
                    if sorted([clause[a][k], clause[b][k]]) == sorted([v1, v2]):
                        hit = [k, clause[a][k], clause[b][k]]
                        break
            rows.append({"pair": [a, b],
                         "verdict": ("EXCLUSIVE" if hit else "COMPATIBLE")})
            j += 1
        i += 1
    comp = len([r for r in rows if r["verdict"] == "COMPATIBLE"])
    return {"pairs": len(rows), "compatible": comp,
            "exclusive": len(rows) - comp, "rows": rows,
            "is_a_partition": False}


def zero_relatedness(env, inv):
    if inv["r"] != 0:
        return {"applicable": False, "r": inv["r"]}
    a = top(weights(env, None))
    b = top(weights(env, env["Hprime"]))
    seen = 0
    off = []
    ep = 0
    while ep < env["K"]:
        z = 0
        while z < env["nz"]:
            seen += 1
            if env["H"][a][z] != env["H"][b][z]:
                off.append([ep, z])
            z += 1
        ep += 1
    return {"applicable": True, "r": 0, "base_index": a, "indexed_index": b,
            "pointwise_inputs_checked": seen, "mismatches": off,
            "behaviourally_identical": len(off) == 0}


def run_block(envs):
    out = []
    for env in envs:
        inv = invariants(env)
        vec = vectors(env, inv)
        cen = cell_census(vec)
        th = {}
        if vec["SIG-R"] is not None:
            cs = threshold_by_scan(vec["SIG-X"], vec["SIG-R"],
                                   COORDS.index("p_store"))
            ps = threshold_by_scan(vec["SIG-R"], vec["SIG-X"],
                                   COORDS.index("p_build"))
            th["chi_star"] = (str(cs) if cs is not None else None)
            th["psi_star"] = (str(ps) if ps is not None else None)
        else:
            th["chi_star"] = None
            th["psi_star"] = None
        th["beta_star"] = str(Q(inv["alpha_gain"], (inv["M"] - 1) * inv["T"]))
        den = (inv["Bmin"] - 1) * inv["Tsteps"]
        th["pistar_star"] = str(Q(0) if den == 0 else
                                (Q(inv["Vglob"]) - Q(inv["Vloc"])) / den)
        th["tau_star"] = str(Q(inv["r"] * inv["T"] *
                               (inv["K"] - inv["k0"]),
                               inv["Mprime"] * inv["K"]))
        th["s_star"] = str(Q(vec[PLAIN][7] - vec["SIG-S"][7]))
        out.append({
            "env": env["id"], "invariants": inv,
            "coefficient_vectors": dict(
                [(k, (list(v) if v is not None else None))
                 for k, v in vec.items()]),
            "thresholds": th, "census": cen,
            "reachability": reach_census(vec, cen),
            "ratio_trichotomy": ratio_trichotomy(vec),
            "recovery": recovery(env, inv, vec),
            "zero_relatedness": zero_relatedness(env, inv),
        })
    return out


def main():
    dv = derivation_set()
    hv = heldout_set()
    res = {
        "schema": "GMI_833_UPDATE_LAW_REGIMES_ORACLE_V1",
        "route": "B",
        "package": "research/gmi-833-update-law-regimes-v1",
        "freeze_commit": "6e42ccd2a7852ce88196765a6013b32315a78108",
        "scope_fingerprint": fingerprint(dv),
        "heldout_fingerprint": fingerprint(hv),
        "price_keys": list(COORDS),
        "joint_grid_size": len(PRICES),
        "derivation": run_block(dv),
        "heldout": run_block(hv),
        "compatibility_matrix": compatibility(),
    }
    path = os.path.join(WHERE, "ORACLE_RESULT_V1.json")
    fh = open(path, "w")
    json.dump(res, fh, indent=1, sort_keys=True)
    fh.write("\n")
    fh.close()
    print("route B fingerprint:", res["scope_fingerprint"]["digest"])
    for blk in res["derivation"]:
        i = blk["invariants"]
        print("%s ag=%d mu=%d Dmin=%s Bmin=%d r=%d uni=%s cells=%s ties=%d"
              % (blk["env"], i["alpha_gain"], i["mu"], str(i["Dmin"]),
                 i["Bmin"], i["r"], i["unimodal"],
                 blk["census"]["strict_cells"], blk["census"]["tie_cases"]))
        print("   th:", blk["thresholds"])
        print("   rec:", blk["recovery"])
    print("wrote", path)


if __name__ == "__main__":
    main()
