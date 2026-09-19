#!/usr/bin/env python3
"""GMI #833 AE14 route B: independent taxonomy oracle.

This file imports nothing from route A (``ae14_generalization_taxonomy_v1.py``)
and recomputes every claimed quantity by a materially different algorithm:

* the spanned subcube by intersecting **every** subcube of the registered input
  space that contains the support, instead of fixing the constant coordinates;
* the recombination set by a pairwise search over training points, instead of
  block value sets;
* the analogy group by closing the generator under composition until the set
  stops growing, instead of taking its powers;
* the planning targets by a backward breadth-first search on an explicit
  primitive adjacency table, instead of a forward search from each query;
* the derivation depth of the Horn system by a memoised derivation-tree
  recursion, instead of iterating the round operator;
* class membership by filtering **all** 65536 functions on the registered input
  space with definitional tests (essential arity, the affine identity, the
  two-distinct-rows-and-columns criterion), instead of building the classes from
  their parameterisations;
* the composition class by applying explicit word sequences step by step with no
  cached word images;
* integer code lengths by a doubling loop instead of a bit-length call.

The registered pseudorandom stream is a frozen constant of the package rather
than a derived quantity, so route B reproduces it from the same registered
specification and recomputes every quantity derived from it independently.
"""
from __future__ import print_function

import json
import sys
from fractions import Fraction

XS = tuple(range(16))
CLASSES = ("L0", "L1", "L_lin", "L_mod", "L_search")
PREDICTION_ONLY = ("L0", "L1", "L_lin", "L_mod")
MODES = ("MEMORIZATION", "INTERPOLATION", "EXTRAPOLATION",
         "SYSTEMATIC_GENERALIZATION", "ANALOGY", "PLANNING_INFERENCE",
         "REASONING")
OP_ORDER = ("pi1", "pi2", "rho", "tau")
CAP = 3
NULL_TRIALS = 200
NULL_SEED = 5692689542 % (1 << 31)
RULES = (((0, 1), 4), ((2, 3), 4), ((4, 2), 5), ((0, 2), 5))
TARGET_ATOM = 5


def bits(x):
    return ((x >> 3) & 1, (x >> 2) & 1, (x >> 1) & 1, x & 1)


def bit(x, i):
    return (x >> (3 - i)) & 1


def rho(x):
    b = bits(x)
    return (b[1] << 3) | (b[2] << 2) | (b[3] << 1) | b[0]


def pi1(x):
    return 4 * (((x >> 2) + 1) % 4) + (x & 3)


def pi2(x):
    return 4 * (x & 3) + (x >> 2)


POINT_OPS = {"pi1": pi1, "pi2": pi2, "rho": rho}


# --- span by intersecting every subcube containing the support --------------
def all_subcubes():
    out = []
    for pattern in range(81):
        p = []
        r = pattern
        for _ in range(4):
            p.append(r % 3)
            r //= 3
        pts = []
        for x in XS:
            ok = True
            for i in range(4):
                if p[i] != 2 and bit(x, i) != p[i]:
                    ok = False
                    break
            if ok:
                pts.append(x)
        out.append(tuple(pts))
    return tuple(out)


SUBCUBES = all_subcubes()


def span(tr):
    best = None
    s = set(tr)
    for c in SUBCUBES:
        if s <= set(c):
            if best is None or len(c) < len(best):
                best = c
    return tuple(sorted(best))


# --- recombination by a pairwise search over training points ----------------
def recomb(tr):
    out = []
    for x in XS:
        hit1 = False
        hit2 = False
        for p in tr:
            if bit(x, 0) == bit(p, 0) and bit(x, 1) == bit(p, 1):
                hit1 = True
            if bit(x, 2) == bit(p, 2) and bit(x, 3) == bit(p, 3):
                hit2 = True
        if hit1 and hit2:
            out.append(x)
    return tuple(out)


# --- group by closure under composition ------------------------------------
def group_closure():
    ident = tuple(XS)
    gen = tuple(rho(x) for x in XS)
    elems = {ident, gen}
    changed = True
    while changed:
        changed = False
        for a in sorted(elems):
            for b in sorted(elems):
                c = tuple(a[b[x]] for x in XS)
                if c not in elems:
                    elems.add(c)
                    changed = True
    return tuple(sorted(elems))


GROUP = group_closure()


def analogy_pts(tr):
    s = set(tr)
    ident = tuple(XS)
    out = set()
    for g in GROUP:
        if g == ident:
            continue
        if any(g[x] in s and g[x] != x for x in tr):
            continue
        for c in tr:
            if g[c] != c and g[c] not in s:
                out.add(g[c])
    return tuple(sorted(out))


# --- planning targets by a backward breadth-first search --------------------
def plan_pts(tr):
    s = set(tr)
    dist = {}
    frontier = set(tr)
    for d in range(1, CAP + 1):
        nxt = set()
        for y in sorted(frontier):
            for name in ("pi1", "pi2"):
                f = POINT_OPS[name]
                for x in XS:
                    if f(x) == y and x not in s and x not in dist:
                        nxt.add(x)
        for x in sorted(nxt):
            if x not in dist:
                dist[x] = d
        frontier = nxt
    return tuple(x for x in XS if dist.get(x, 0) >= 2)


# --- Horn depth by a memoised derivation-tree recursion ---------------------
def derivation_depth(x, atom):
    base = {0: bit(x, 0), 1: bit(x, 1), 2: bit(x, 2), 3: bit(x, 3)}
    memo = {}

    def depth(a, seen):
        if a in base:
            return 0 if base[a] else None
        if a in memo:
            return memo[a]
        if a in seen:
            return None
        best = None
        for ante, head in RULES:
            if head != a:
                continue
            ds = []
            ok = True
            for p in ante:
                dd = depth(p, seen | set([a]))
                if dd is None:
                    ok = False
                    break
                ds.append(dd)
            if ok:
                cand = max(ds) + 1
                if best is None or cand < best:
                    best = cand
        memo[a] = best
        return best

    return depth(atom, set())


def reason_eval(tr):
    s = set(tr)
    ent = tuple(x for x in XS
                if x not in s and (derivation_depth(x, TARGET_ATOM) or 0) >= 2)
    neg = set()
    for x in ent:
        for i in range(4):
            y = x ^ (1 << (3 - i))
            if y not in s and derivation_depth(y, TARGET_ATOM) is None:
                neg.add(y)
    return ent, tuple(sorted(neg))


# --- classes by filtering all 65536 functions ------------------------------
def val(m, x):
    return (m >> x) & 1


ALL = tuple(range(1 << 16))


def filter_L1():
    out = []
    for m in ALL:
        ess = 0
        for i in range(4):
            for x in XS:
                if val(m, x) != val(m, x ^ (1 << (3 - i))):
                    ess += 1
                    break
        if ess <= 2:
            out.append(m)
    return tuple(out)


def filter_L_lin():
    out = []
    for m in ALL:
        b = val(m, 0)
        a = 0
        for i in range(4):
            if val(m, 1 << (3 - i)) != b:
                a |= 1 << (3 - i)
        ok = True
        for x in XS:
            par = 0
            y = x & a
            while y:
                par ^= y & 1
                y >>= 1
            if val(m, x) != (par ^ b):
                ok = False
                break
        if ok:
            out.append(m)
    return tuple(out)


def filter_L_mod():
    out = []
    for m in ALL:
        rows = set()
        cols = set()
        for u in range(4):
            rows.add(tuple(val(m, 4 * u + v) for v in range(4)))
        for v in range(4):
            cols.add(tuple(val(m, 4 * u + v) for u in range(4)))
        if len(rows) <= 2 and len(cols) <= 2:
            out.append(m)
    return tuple(out)


L1_LIST = filter_L1()
L_LIN_LIST = filter_L_lin()
L_MOD_LIST = filter_L_mod()


def filter_L0(tr):
    off = 0
    for x in XS:
        if x not in tr:
            off |= 1 << x
    out = []
    for m in ALL:
        v = m & off
        if v == 0 or v == off:
            out.append(m)
    return tuple(out)


# --- composition class by explicit word sequences ---------------------------
def enumerate_words(subset):
    ops = [o for o in OP_ORDER if o in subset]
    out = [()]
    level = [()]
    for _ in range(CAP):
        nxt = []
        for w in level:
            for o in ops:
                nxt.append(tuple(list(w) + [o]))
        out += nxt
        level = nxt
    return out


def step(name, state):
    if name == "tau":
        new = list(state)
        for ante, head in RULES:
            hit = True
            for a in ante:
                if not state[a]:
                    hit = False
            if hit:
                new[head] = 1
        return tuple(new)
    f = POINT_OPS[name]
    x = (state[0] << 3) | (state[1] << 2) | (state[2] << 1) | state[3]
    y = f(x)
    b = bits(y)
    return (b[0], b[1], b[2], b[3], state[4], state[5])


def embed(x):
    b = bits(x)
    return (b[0], b[1], b[2], b[3], 0, 0)


SUBSETS = tuple(tuple(OP_ORDER[i] for i in range(4) if (k >> i) & 1)
                for k in range(1, 16))


def build_search(tr, tmask, cap=CAP):
    """each member applies explicit word sequences step by step; no word image
    table is shared between calls."""
    anchors = {}
    for x in tr:
        anchors[embed(x)] = val(tmask, x)
    out = []
    for s in SUBSETS:
        ws = [w for w in enumerate_words(s) if len(w) <= cap]
        trace = []
        for x in XS:
            row = []
            for w in ws:
                z = embed(x)
                for o in w:
                    z = step(o, z)
                row.append(z)
            trace.append(row)
        for d in (0, 1):
            m = 0
            for x in XS:
                lab = d
                for z in trace[x]:
                    if z in anchors:
                        lab = anchors[z]
                        break
                if lab:
                    m |= 1 << x
            out.append(m)
        for j in range(6):
            m = 0
            for x in XS:
                for z in trace[x]:
                    if z[j]:
                        m |= 1 << x
                        break
            out.append(m)
    return tuple(out)


def members(name, tr, tmask):
    if name == "L0":
        return filter_L0(tr)
    if name == "L1":
        return L1_LIST
    if name == "L_lin":
        return L_LIN_LIST
    if name == "L_mod":
        return L_MOD_LIST
    return build_search(tr, tmask)


# --- mode predicates --------------------------------------------------------
def eval_points(mode, tr):
    s = set(tr)
    if mode == "MEMORIZATION":
        return tuple(x for x in XS if x not in s)
    if mode == "INTERPOLATION":
        return tuple(x for x in span(tr) if x not in s)
    if mode == "EXTRAPOLATION":
        sp = set(span(tr))
        return tuple(x for x in XS if x not in sp)
    if mode == "SYSTEMATIC_GENERALIZATION":
        return tuple(x for x in recomb(tr) if x not in s)
    if mode == "ANALOGY":
        return analogy_pts(tr)
    if mode == "PLANNING_INFERENCE":
        return plan_pts(tr)
    if mode == "REASONING":
        ent, neg = reason_eval(tr)
        return tuple(sorted(set(ent) | set(neg)))
    raise ValueError(mode)


def holds(mode, funcs, tmask, tr):
    ev = eval_points(mode, tr)
    if not ev:
        return False
    if mode == "MEMORIZATION":
        ones = 0
        for x in ev:
            ones += val(tmask, x)
        br = Fraction(max(ones, len(ev) - ones), len(ev))
        for m in funcs:
            bad = False
            for x in tr:
                if val(m, x) != val(tmask, x):
                    bad = True
                    break
            if bad:
                continue
            hit = 0
            for x in ev:
                if val(m, x) == val(tmask, x):
                    hit += 1
            if Fraction(hit, len(ev)) == br:
                return True
        return False
    if mode == "REASONING":
        ent, _n = reason_eval(tr)
        if not ent:
            return False
    need = sorted(set(tr) | set(ev))
    for m in funcs:
        ok = True
        for x in need:
            if val(m, x) != val(tmask, x):
                ok = False
                break
        if ok:
            return True
    return False


def best_accuracy(funcs, tmask, need):
    accs = []
    for m in funcs:
        hit = 0
        for x in need:
            if val(m, x) == val(tmask, x):
                hit += 1
        accs.append(Fraction(hit, len(need)))
    accs.sort()
    return accs[-1]


# --- registered roster (re-declared, not imported) --------------------------
def table(fn):
    m = 0
    for x in XS:
        if fn(x):
            m |= 1 << x
    return m


def horn_value(x):
    return 1 if derivation_depth(x, TARGET_ATOM) is not None else 0


COMP = table(lambda x: (bit(x, 0) & bit(x, 1)) ^ (bit(x, 2) & bit(x, 3)))
TASKS = {
    "T_MEM": (table(lambda x: 1 if x in (0, 5, 6, 11, 13) else 0),
              (0, 3, 5, 9, 12)),
    "T_INTERP": (table(lambda x: bit(x, 1) & bit(x, 2)), (0, 2, 4, 8)),
    "T_EXTRAP": (table(lambda x: bit(x, 0) ^ bit(x, 1) ^ bit(x, 2)),
                 (0, 2, 4, 8)),
    "T_SYS": (table(lambda x: (bit(x, 0) ^ bit(x, 1)) & (bit(x, 2) ^ bit(x, 3))),
              (0, 5, 10, 15)),
    "T_ANALOGY": (table(lambda x: 1 if x in (1, 2, 3, 4, 6, 8, 9, 12) else 0),
                  (0, 1, 3, 5, 7)),
    "T_PLAN": (table(lambda x: 1 if ((x & 3) - (x >> 2)) % 4 in (0, 1) else 0),
               (0, 2, 3, 6, 14)),
    "T_REASON": (table(horn_value), (0, 4, 8, 10)),
    "T_MATCH_COMPOSITIONAL": (COMP, (0, 15)),
    "T_MATCH_LOOKUP": (COMP ^ (1 << 3) ^ (1 << 12), (0, 15)),
    "T_CODE_A": (table(lambda x: bit(x, 0)), (0, 7)),
    "T_CODE_B": (table(lambda x: bit(x, 0) ^ bit(x, 2)), (4, 5)),
}
HOME = {
    "AFFINE": ("T_EXTRAP", "EXTRAPOLATION", "L_lin"),
    "BLOCK_FACTORIZED": ("T_SYS", "SYSTEMATIC_GENERALIZATION", "L_mod"),
    "COMPOSITION_DEPTH_GE_2": ("T_PLAN", "PLANNING_INFERENCE", "L_search"),
    "DEDUCTIVE_CLOSURE": ("T_REASON", "REASONING", "L_search"),
    "GROUP_ORBIT": ("T_ANALOGY", "ANALOGY", "L_search"),
    "JUNTA": ("T_INTERP", "INTERPOLATION", "L1"),
    "LOOKUP_ONLY": ("T_MEM", "MEMORIZATION", "L0"),
}


# --- frozen model space and code lengths -----------------------------------
def ordered_affine():
    out = []
    for a in range(16):
        for b in range(2):
            m = 0
            for x in XS:
                par = 0
                y = x & a
                while y:
                    par ^= y & 1
                    y >>= 1
                if (par ^ b):
                    m |= 1 << x
            out.append(m)
    return out


def model_space():
    out = []
    seen = set()
    for m in ordered_affine() + sorted(L1_LIST) + sorted(L_MOD_LIST):
        if m not in seen:
            seen.add(m)
            out.append(m)
    return tuple(out)


MODEL_SPACE = model_space()


def ceil_log2(n):
    """smallest k with 2**k >= n, by doubling."""
    k = 0
    p = 1
    while p < n:
        p *= 2
        k += 1
    return k


def code_length(index):
    return 1 + 2 * ceil_log2(index + 2)


# --- registered stream ------------------------------------------------------
class Stream(object):
    def __init__(self, seed):
        self.s = seed % (1 << 31)

    def byte(self):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return (self.s // 65536) % 256

    def below(self, n):
        limit = 256 - (256 % n)
        b = self.byte()
        while b >= limit:
            b = self.byte()
        return b % n

    def permutation(self, k):
        arr = list(range(k))
        i = k - 1
        while i > 0:
            j = self.below(i + 1)
            arr[i], arr[j] = arr[j], arr[i]
            i -= 1
        return tuple(arr)


def minimal_class(mode, tmask, tr):
    for c in CLASSES:
        if holds(mode, members(c, tr, tmask), tmask, tr):
            return c
    return None


def detector(tmask, tr, mode):
    for c in PREDICTION_ONLY:
        if holds(mode, members(c, tr, tmask), tmask, tr):
            return False
    return holds(mode, members("L_search", tr, tmask), tmask, tr)


# --- assembly ---------------------------------------------------------------
def compute():
    out = {"structures": {}, "home": {}, "cube": {}}
    for name in sorted(TASKS):
        tmask, tr = TASKS[name]
        out["structures"][name] = {
            "span": list(span(tr)),
            "recomb": list(recomb(tr)),
            "analogy": list(analogy_pts(tr)),
            "plan": list(plan_pts(tr)),
            "reason": list(eval_points("REASONING", tr))}
        row = {}
        for mode in MODES:
            cell = {"n_eval": len(eval_points(mode, tr))}
            for c in CLASSES:
                cell[c] = holds(mode, members(c, tr, tmask), tmask, tr)
            row[mode] = cell
        out["cube"][name] = row
    for st in sorted(HOME):
        task, mode, predicted = HOME[st]
        tmask, tr = TASKS[task]
        need = tuple(sorted(set(tr) | set(eval_points(mode, tr))))
        entry = {"task": task, "mode": mode, "predicted": predicted,
                 "constraint_points": len(need), "best": {}, "distinct": {}}
        for c in CLASSES:
            fs = members(c, tr, tmask)
            entry["best"][c] = str(best_accuracy(fs, tmask, need))
            entry["distinct"][c] = len(set(fs))
        entry["minimal"] = minimal_class(mode, tmask, tr)
        entry["hit"] = entry["minimal"] == predicted
        out["home"][st] = entry

    # row 3
    tr = TASKS["T_MATCH_COMPOSITIONAL"][1]
    held = tuple(x for x in recomb(tr) if x not in set(tr))
    view = tuple(sorted(set(tr) | set((5, 6, 9, 10))))
    mdl = None
    for i, m in enumerate(MODEL_SPACE):
        ok = True
        for x in view:
            if val(m, x) != val(TASKS["T_MATCH_COMPOSITIONAL"][0], x):
                ok = False
                break
        if ok:
            mdl = i
            break
    r3 = {"held": list(held), "mdl_index": mdl,
          "mdl_length": code_length(mdl),
          "bayes": str(Fraction(3, 4)), "recomb_acc": {}}
    for nm in ("T_MATCH_COMPOSITIONAL", "T_MATCH_LOOKUP"):
        tm = TASKS[nm][0]
        hit = 0
        for x in held:
            if val(MODEL_SPACE[mdl], x) == val(tm, x):
                hit += 1
        r3["recomb_acc"][nm] = str(Fraction(hit, len(held)))
    out["row3"] = r3

    # row 4
    ia = MODEL_SPACE.index(TASKS["T_CODE_A"][0])
    ib = MODEL_SPACE.index(TASKS["T_CODE_B"][0])
    tgt = TASKS["T_ANALOGY"][0]
    ta = Fraction(sum(1 for x in XS if val(TASKS["T_CODE_A"][0], x)
                      == val(tgt, x)), 16)
    tb = Fraction(sum(1 for x in XS if val(TASKS["T_CODE_B"][0], x)
                      == val(tgt, x)), 16)
    kraft = Fraction(0)
    for i in range(len(MODEL_SPACE)):
        kraft += Fraction(1, 2 ** code_length(i))
    out["row4"] = {"model_space_size": len(MODEL_SPACE),
                   "index_a": ia, "index_b": ib,
                   "length_a": code_length(ia), "length_b": code_length(ib),
                   "transfer_a": str(ta), "transfer_b": str(tb),
                   "kraft_sum": str(kraft)}

    # row 5 null
    actual = dict((st, out["home"][st]["minimal"]) for st in sorted(HOME))
    hits = sum(1 for st in sorted(HOME)
               if actual[st] == HOME[st][2])
    stream = Stream(NULL_SEED)
    counts = []
    for _ in range(NULL_TRIALS):
        h = 0
        for st in sorted(HOME):
            if CLASSES[stream.below(5)] == actual[st]:
                h += 1
        counts.append(h)
    out["row5"] = {"hit_count": hits, "null_largest": max(counts),
                   "null_at_or_above": str(Fraction(
                       sum(1 for c in counts if c >= hits), NULL_TRIALS))}

    # separation null
    specs = (("T_ANALOGY", "ANALOGY"), ("T_PLAN", "PLANNING_INFERENCE"),
             ("T_REASON", "REASONING"))
    witness = sum(1 for task, mode in specs
                  if detector(TASKS[task][0], TASKS[task][1], mode))
    stream = Stream(NULL_SEED)
    mags = []
    for _ in range(NULL_TRIALS):
        perm = stream.permutation(16)
        mag = 0
        for task, mode in specs:
            base = TASKS[task][0]
            scrambled = 0
            for x in XS:
                if val(base, perm[x]):
                    scrambled |= 1 << x
            if detector(scrambled, TASKS[task][1], mode):
                mag += 1
        mags.append(mag)
    out["separation_null"] = {"witness": witness, "largest": max(mags),
                              "at_or_above": str(Fraction(
                                  sum(1 for m in mags if m >= witness),
                                  NULL_TRIALS))}
    return out


def main():
    sys.stdout.write(json.dumps(compute(), sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    main()
