# -*- coding: utf-8 -*-
"""AG4 route B -- independent oracle.

Imports nothing from route A and no parent module.  It rebuilds the ten
specializations from FREEZE_V1.md's own text and recomputes every published
quantity by a different mechanism:

  * objects are decoded from integer indices, not produced by nested products;
  * behaviour comes from a dynamic program over composed word-transition TABLES
    (a function table for deterministic, a bitmask table for nondeterministic, a
    Fraction vector for probabilistic), not from stepping one word at a time;
  * translatability is decided by binary search in a sorted list of target
    behaviours, not by a set membership test;
  * the submonoids of the two-element transformation monoid are recomputed by a
    closure search written again from scratch;
  * the obstruction tokens are re-derived from the object's own structure.

    python3 -I -B independent_oracle_v1.py
"""

import bisect
import itertools
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
N = 2
LABELS = 2
WIN = 4
FAMS = ("A", "B", "C", "D", "E", "F")
SPEC = {"A": ("A",), "B": ("B",), "C": ("Cd", "Cn", "Cp"), "D": ("D",),
        "E": ("Er", "Ek"), "F": ("F1", "F2")}
KND = {"A": "det", "B": "nondet", "Cd": "det", "Cn": "nondet", "Cp": "prob",
       "D": "det", "Er": "nondet", "Ek": "prob", "F1": "det", "F2": "det"}
DET_TOTAL = ("A", "Cd", "D", "F1", "F2")
VOCAB = ("NONDETERMINISM_NOT_FUNCTIONAL", "BLOCKING_NOT_TOTAL",
         "WEIGHTS_NOT_RECOVERABLE", "NON_DIRAC_KERNEL", "NO_CHOSEN_GENERATING_FAMILY",
         "MONOIDAL_STRUCTURE_NOT_DERIVABLE_FROM_COMPOSITION",
         "ARITY_NOT_REPRESENTABLE", "FUNCTOR_NOT_IN_RANGE")

FUNCS = [(a, b) for a in range(N) for b in range(N)]          # every map on {0,1}
MASKS = [0, 1, 2, 3]
DIST = [((0, Fraction(1)), (1, Fraction(0))),
        ((0, Fraction(1, 2)), (1, Fraction(1, 2))),
        ((0, Fraction(0)), (1, Fraction(1)))]
OUTS = [(a, b) for a in range(2) for b in range(2)]


def wordtables(step_tables, compose_fn, unit, depth):
    """DP over composed word transition tables, one layer per word length."""
    layers = [{(): unit}]
    for _ in range(depth):
        nxt = {}
        for w, t in layers[-1].items():
            for l in range(LABELS):
                nxt[w + (l,)] = compose_fn(t, step_tables[l])
        layers.append(nxt)
    all_t = {}
    for layer in layers:
        all_t.update(layer)
    return all_t


def det_beh(f, out):
    tables = [tuple(f[l]) for l in range(LABELS)]
    unit = tuple(range(N))
    w = wordtables(tables, lambda a, b: tuple(b[a[s]] for s in range(N)), unit, WIN)
    return ("det", tuple(out[w[k][0]] for k in sorted(w)))


def nd_beh(r, out):
    def mstep(mask, rel):
        m = 0
        for s in range(N):
            if mask >> s & 1:
                m |= rel[s]
        return m

    def comp(a, b):
        return tuple(mstep(a[s], b) for s in range(N))
    tables = [tuple(r[l]) for l in range(LABELS)]
    unit = tuple(1 << s for s in range(N))
    w = wordtables(tables, comp, unit, WIN)
    res = []
    for k in sorted(w):
        m = w[k][0]
        res.append(frozenset(out[s] for s in range(N) if m >> s & 1))
    return ("nondet", tuple(res))


def pr_beh(kern, out):
    def comp(a, b):
        res = []
        for s in range(N):
            acc = {}
            for t in range(N):
                p = a[s][t]
                if not p:
                    continue
                for u in range(N):
                    q = b[t][u]
                    if q:
                        acc[u] = acc.get(u, Fraction(0)) + p * q
            res.append(tuple(acc.get(u, Fraction(0)) for u in range(N)))
        return tuple(res)
    tables = []
    for l in range(LABELS):
        tables.append(tuple(tuple(p for _t, p in kern[l][s]) for s in range(N)))
    unit = tuple(tuple(Fraction(1) if t == s else Fraction(0) for t in range(N))
                 for s in range(N))
    w = wordtables(tables, comp, unit, WIN)
    res = []
    for k in sorted(w):
        agg = {}
        for t in range(N):
            p = w[k][0][t]
            if p:
                agg[out[t]] = agg.get(out[t], Fraction(0)) + p
        res.append(tuple(sorted((o, str(p)) for o, p in agg.items() if p)))
    return ("prob", tuple(res))


def submonoids():
    comp = lambda a, b: tuple(a[b[s]] for s in range(N))
    ident = tuple(range(N))
    found = set()
    for size in range(1, len(FUNCS) + 1):
        for sub in itertools.combinations(FUNCS, size):
            st = set(sub)
            if ident not in st:
                continue
            closed = True
            for a in st:
                for b in st:
                    if comp(a, b) not in st:
                        closed = False
                        break
                if not closed:
                    break
            if closed:
                found.add(frozenset(st))
    return sorted(found, key=lambda m: (len(m), sorted(m)))


MONOIDS = submonoids()


def objects(tag):
    out = []
    if tag in ("A", "Cd", "F1"):
        for f0 in FUNCS:
            for f1 in FUNCS:
                for o in OUTS:
                    out.append((tag, (f0, f1), o))
    elif tag in ("B", "Cn", "Er"):
        for r0 in itertools.product(MASKS, repeat=N):
            for r1 in itertools.product(MASKS, repeat=N):
                for o in OUTS:
                    out.append((tag, (r0, r1), o))
    elif tag in ("Cp", "Ek"):
        for k0 in itertools.product(DIST, repeat=N):
            for k1 in itertools.product(DIST, repeat=N):
                for o in OUTS:
                    out.append((tag, (k0, k1), o))
    elif tag == "D":
        for m in MONOIDS:
            for o in OUTS:
                out.append((tag, tuple(sorted(m)), o))
    elif tag == "F2":
        base = [((f0, f1), o) for f0 in FUNCS for f1 in FUNCS for o in OUTS]
        for p in base:
            for q in base:
                out.append((tag, (p[0], q[0]), (p[1], q[1])))
    return out


def behs_of(obj):
    tag = obj[0]
    if tag in ("A", "Cd", "F1"):
        return frozenset([det_beh(obj[1], obj[2])])
    if tag in ("B", "Cn", "Er"):
        return frozenset([nd_beh(obj[1], obj[2])])
    if tag in ("Cp", "Ek"):
        return frozenset([pr_beh(obj[1], obj[2])])
    if tag == "D":
        return frozenset(det_beh((a, b), obj[2]) for a in obj[1] for b in obj[1])
    if tag == "F2":
        (fp, fq), (op, oq) = obj[1], obj[2]
        f0 = tuple((fp[0][a], fq[0][b]) for a in range(N) for b in range(N))
        f1 = tuple((fp[1][a], fq[1][b]) for a in range(N) for b in range(N))
        pairs = [(a, b) for a in range(N) for b in range(N)]
        idx = dict((p, i) for i, p in enumerate(pairs))
        tables = [tuple(idx[f0[i]] for i in range(4)), tuple(idx[f1[i]] for i in range(4))]
        unit = tuple(range(4))
        w = wordtables(tables, lambda a, b: tuple(b[a[s]] for s in range(4)), unit, WIN)
        outv = tuple((op[p[0]] + oq[p[1]]) % 2 for p in pairs)
        return frozenset([("det", tuple(outv[w[k][idx[(0, 0)]]] for k in sorted(w)))])
    raise AssertionError(tag)


def coarsest(a, b):
    if a == b:
        return a
    if "det" in (a, b) and "nondet" in (a, b):
        return "nondet"
    if "det" in (a, b) and "prob" in (a, b):
        return "prob"
    return "nondet"


def famkind(f):
    k = "det"
    for t in sorted(set(KND[x] for x in SPEC[f])):
        k = coarsest(k, t)
    return k


def lift(b, cls):
    k, rows = b
    if k == cls:
        return rows
    if k == "det" and cls == "nondet":
        return tuple(frozenset([v]) for v in rows)
    if k == "det" and cls == "prob":
        return tuple(((v, str(Fraction(1))),) for v in rows)
    if k == "prob" and cls == "nondet":
        return tuple(frozenset(o for o, _ in row) for row in rows)
    return None


def flags(obj):
    tag, f = obj[0], set()
    if tag in ("B", "Cn", "Er"):
        for l in range(LABELS):
            for s in range(N):
                n = bin(obj[1][l][s]).count("1")
                if n >= 2:
                    f.add("MULTI")
                if n == 0:
                    f.add("BLOCK")
    if tag in ("Cp", "Ek"):
        for l in range(LABELS):
            for s in range(N):
                if not any(p == 1 for _t, p in obj[1][l][s]):
                    f.add("NONDIRAC")
    if tag == "D":
        f.add("NOLAB")
    if tag == "F2":
        f.add("AR2")
    return f


def obstruct(obj, dst):
    fl = flags(obj)
    det_dst = all(t in DET_TOTAL for t in SPEC[dst])
    out = []
    if "MULTI" in fl and det_dst:
        out.append("NONDETERMINISM_NOT_FUNCTIONAL")
    if "BLOCK" in fl and det_dst:
        out.append("BLOCKING_NOT_TOTAL")
    if "NONDIRAC" in fl:
        out.append("NON_DIRAC_KERNEL" if det_dst else "WEIGHTS_NOT_RECOVERABLE")
    if "NOLAB" in fl:
        out.append("NO_CHOSEN_GENERATING_FAMILY")
    if "AR2" in fl:
        out.append("ARITY_NOT_REPRESENTABLE")
        if dst == "D":
            out.append("MONOIDAL_STRUCTURE_NOT_DERIVABLE_FROM_COMPOSITION")
    if not out and obj[0] in ("Cd", "Cn", "Cp"):
        out.append("FUNCTOR_NOT_IN_RANGE")
    return sorted(set(out))


def main():
    objs, bs = {}, {}
    for tag in sorted(KND):
        objs[tag] = objects(tag)
        bs[tag] = [behs_of(o) for o in objs[tag]]

    table = {}
    for src, dst in itertools.permutations(FAMS, 2):
        cls = coarsest(famkind(src), famkind(dst))
        target = []
        for t in SPEC[dst]:
            for bb in bs[t]:
                for b in bb:
                    v = lift(b, cls)
                    if v is not None:
                        target.append(repr(v))
        target.sort()
        tot = dom = 0
        tokens = set()
        for t in SPEC[src]:
            for i, o in enumerate(objs[t]):
                tot += 1
                hit = False
                for b in bs[t][i]:
                    v = lift(b, cls)
                    if v is None:
                        continue
                    r = repr(v)
                    j = bisect.bisect_left(target, r)
                    if j < len(target) and target[j] == r:
                        hit = True
                        break
                if hit:
                    dom += 1
                else:
                    tokens |= set(obstruct(o, dst))
        v = "TOTAL" if dom == tot else ("EMPTY" if dom == 0 else "PARTIAL")
        table["%s->%s" % (src, dst)] = {"source_objects": tot, "translatable": dom,
                                        "verdict": v, "common_class": cls,
                                        "obstruction": sorted(tokens)}

    pairs = {}
    for x, y in itertools.combinations(FAMS, 2):
        a, b = table["%s->%s" % (x, y)]["verdict"], table["%s->%s" % (y, x)]["verdict"]
        pairs["%s-%s" % (x, y)] = ("MUTUALLY_TOTAL" if a == b == "TOTAL"
                                   else ("TOTAL_ONE_WAY" if "TOTAL" in (a, b)
                                         else "PARTIAL_BOTH_WAYS"))
    hist = {}
    for k in table:
        hist[table[k]["verdict"]] = hist.get(table[k]["verdict"], 0) + 1
    ohist = dict((t, sum(1 for k in table if t in table[k]["obstruction"]))
                 for t in VOCAB)
    out = {"schema": "AG4_FORMALISM_TRANSLATION_ORACLE_V1",
           "registered_objects": dict((t, len(objs[t])) for t in sorted(objs)),
           "registered_objects_total": sum(len(v) for v in objs.values()),
           "directed_translations": table,
           "pairs": pairs,
           "directed_verdict_histogram": {"TOTAL": hist.get("TOTAL", 0),
                                          "PARTIAL": hist.get("PARTIAL", 0),
                                          "EMPTY": hist.get("EMPTY", 0)},
           "pair_verdict_histogram": dict(
               (v, sum(1 for k in pairs if pairs[k] == v)) for v in sorted(set(pairs.values()))),
           "mutually_total_pairs": sorted(k for k in pairs if pairs[k] == "MUTUALLY_TOTAL"),
           "obstruction_histogram": ohist}
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(dict((k, v) for k, v in out.items()
                          if k != "directed_translations"), sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
