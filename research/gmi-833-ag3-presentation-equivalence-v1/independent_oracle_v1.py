# -*- coding: utf-8 -*-
"""AG3 route B -- independent oracle.

Imports nothing from route A and no parent module.  It rebuilds the universe from
FREEZE_V1.md's own definitions and recomputes every published quantity by a
different mechanism:

  * state maps are packed base-n integers with a composition table, not tuples;
  * L1 and L2 are decided PAIRWISE by explicit search over bijections and then
    turned into classes by union-find, never by a canonical form;
  * model equivalence is decided by Moore minimization (partition refinement)
    and canonical BFS renumbering -- the Myhill-Nerode route -- not by comparing
    a table of behaviours over enumerated words;
  * compile lengths come from a single BFS distance map over the monoid graph,
    not from layered realizability sets;
  * transitive closure is computed by repeated relation squaring, not union-find;
  * the generated sublattice is closed by a worklist over an explicit queue.

    python3 -I -B independent_oracle_v1.py
"""

import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LETTERS = (0, 1)
START = 0
KS = (1, 2, 3, 5)
MAXLEN = 10


def gens_for(n):
    maps = []
    for t in (tuple(range(n)),
              tuple((s + 1) % n for s in range(n)),
              tuple((s - 1) % n for s in range(n)),
              tuple(0 for _ in range(n)),
              tuple({0: 1, 1: 0}.get(s, s) for s in range(n))):
        if t not in maps:
            maps.append(t)
    return maps


def pack(t, n):
    v = 0
    for s in range(n - 1, -1, -1):
        v = v * n + t[s]
    return v


def unpack(v, n):
    out = []
    for _ in range(n):
        out.append(v % n)
        v //= n
    return tuple(out)


def allwords(k, maxlen):
    acc = [()]
    cur = [()]
    for _ in range(maxlen):
        nxt = [w + (f,) for w in cur for f in range(k)]
        acc += nxt
        cur = nxt
    return acc


def build():
    pres = []
    for regime in ("BINARY", "FULL"):
        for n in (2, 3):
            G = gens_for(n)
            for i, j in itertools.permutations(range(len(G)), 2):
                for wa in allwords(2, 2):
                    for wb in allwords(2, 2):
                        pres.append((n, (G[i], G[j]), (wa, wb), regime))
    return pres


def observation(regime, n):
    return [1 if s == 0 else 0 for s in range(n)] if regime == "BINARY" else list(range(n))


def analyse(p):
    n, sig, prog, regime = p
    o = observation(regime, n)

    def apply_word(w):
        cur = list(range(n))
        for f in w:
            cur = [sig[f][x] for x in cur]
        return tuple(cur)

    letter = [apply_word(prog[x]) for x in LETTERS]

    # reachable part
    reach, stack = {START}, [START]
    while stack:
        s = stack.pop()
        for t in letter:
            if t[s] not in reach:
                reach.add(t[s])
                stack.append(t[s])

    # BFS distances over the monoid graph, keyed by packed integer
    dist = {pack(tuple(range(n)), n): 0}
    frontier = [tuple(range(n))]
    d = 0
    while frontier and d < MAXLEN:
        d += 1
        nxt = []
        for t in frontier:
            for g in sig:
                u = tuple(g[t[s]] for s in range(n))
                key = pack(u, n)
                if key not in dist:
                    dist[key] = d
                    nxt.append(u)
        frontier = nxt

    # Moore minimization of the reachable automaton, then canonical BFS labels
    states = sorted(reach)
    block = {}
    for s in states:
        block[s] = o[s]
    while True:
        sig_map = {}
        for s in states:
            sig_map[s] = (block[s], tuple(block[letter[x][s]] for x in LETTERS))
        classes = sorted(set(sig_map.values()))
        newblock = dict((s, classes.index(sig_map[s])) for s in states)
        if newblock == block:
            break
        block = newblock
    order, queue = {block[START]: 0}, [block[START]]
    while queue:
        b = queue.pop(0)
        rep = [s for s in states if block[s] == b][0]
        for x in LETTERS:
            nb = block[letter[x][rep]]
            if nb not in order:
                order[nb] = len(order)
                queue.append(nb)
    canon_out = {}
    for b, idx in order.items():
        rep = [s for s in states if block[s] == b][0]
        canon_out[idx] = (o[rep], tuple(order[block[letter[x][rep]]] for x in LETTERS))
    minimal = tuple(canon_out[i] for i in range(len(order)))

    return {"n": n, "sig": sig, "prog": prog, "regime": regime, "obs": o,
            "letter": letter, "reach": reach, "dist": dist, "minimal": minimal,
            "monoid": set(dist.keys())}


def bijections(a, b):
    if a["n"] != b["n"]:
        return []
    n = a["n"]
    out = []
    for perm in itertools.permutations(range(n)):
        if perm[START] != START:
            continue
        if any(b["obs"][perm[s]] != a["obs"][s] for s in range(n)):
            continue
        out.append(perm)
    return out


def rel_l1(a, b):
    if a["regime"] != b["regime"] or a["n"] != b["n"]:
        return False
    n = a["n"]
    for perm in bijections(a, b):
        inv = [0] * n
        for s in range(n):
            inv[perm[s]] = s
        for rho in itertools.permutations(range(2)):
            ok = True
            for f in range(2):
                want = b["sig"][rho[f]]
                if any(want[perm[s]] != perm[a["sig"][f][s]] for s in range(n)):
                    ok = False
                    break
            if not ok:
                continue
            if all(tuple(rho[f] for f in a["prog"][x]) == b["prog"][x] for x in LETTERS):
                return True
    return False


def rel_l2(a, b):
    if a["regime"] != b["regime"] or a["n"] != b["n"]:
        return False
    n = a["n"]
    for perm in bijections(a, b):
        inv = [0] * n
        for s in range(n):
            inv[perm[s]] = s
        conj = set()
        for key in a["monoid"]:
            t = unpack(key, n)
            conj.add(pack(tuple(perm[t[inv[s]]] for s in range(n)), n))
        if conj != b["monoid"]:
            continue
        if all(all(b["letter"][x][perm[s]] == perm[a["letter"][x][s]] for s in range(n))
               for x in LETTERS):
            return True
    return False


def one_way(a, b, need_obs=True):
    dom = sorted(a["reach"])
    others = [s for s in dom if s != START]
    targets = [t for t in range(b["n"]) if t != START]
    if len(dom) > b["n"]:
        return None
    best = None
    for pick in itertools.permutations(targets, len(others)):
        e = {START: START}
        for s, t in zip(others, pick):
            e[s] = t
        if need_obs and any(b["obs"][e[s]] != a["obs"][s] for s in dom):
            continue
        worst, ok = 0, True
        for x in LETTERS:
            L = len(a["prog"][x])
            if L == 0:
                continue
            want = dict((e[s], e[a["letter"][x][s]]) for s in dom)
            shortest = None
            for key, dd in b["dist"].items():
                t = unpack(key, b["n"])
                if all(t[u] == v for u, v in want.items()):
                    if shortest is None or dd < shortest:
                        shortest = dd
            if shortest is None:
                ok = False
                break
            need = -(-shortest // L)
            if need > worst:
                worst = need
        if ok and (best is None or worst < best):
            best = worst
    return best


def kmin(a, b, need_obs=True):
    x = one_way(a, b, need_obs)
    if x is None:
        return None
    y = one_way(b, a, need_obs)
    if y is None:
        return None
    return x if x > y else y


def classes_from_pairs(items, rel, bucket):
    """Pairwise decision, then classes by union-find over the decided pairs."""
    parent = list(range(len(items)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pairs = 0
    for _, ids in sorted(bucket.items()):
        for i, j in itertools.combinations(ids, 2):
            if rel(items[i], items[j]):
                pairs += 1
                a, b = find(i), find(j)
                if a != b:
                    parent[max(a, b)] = min(a, b)
    labels = [find(i) for i in range(len(items))]
    return labels, pairs


def canon_labels(labels):
    first, out = {}, []
    for i, lab in enumerate(labels):
        if lab not in first:
            first[lab] = i
        out.append(first[lab])
    return tuple(out)


def close_edges(nelem, edges):
    parent = list(range(nelem))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i, j in edges:
        a, b = find(i), find(j)
        if a != b:
            parent[max(a, b)] = min(a, b)
    return canon_labels([find(i) for i in range(nelem)])


def npairs(part):
    c = {}
    for lab in part:
        c[lab] = c.get(lab, 0) + 1
    return sum(v * (v - 1) // 2 for v in c.values())


def refines(p, q):
    seen = {}
    for a, b in zip(p, q):
        if a in seen and seen[a] != b:
            return False
        seen[a] = b
    return True


def meet(p, q):
    return canon_labels(list(zip(p, q)))


def join(p, q):
    edges, first = [], {}
    for part in (p, q):
        first = {}
        for i, lab in enumerate(part):
            if lab in first:
                edges.append((first[lab], i))
            else:
                first[lab] = i
    return close_edges(len(p), edges)


def main():                                                    # noqa: C901
    uni = build()
    A = [analyse(p) for p in uni]
    N = len(A)

    bucket = {}
    for i, a in enumerate(A):
        bucket.setdefault((a["regime"], a["n"]), []).append(i)
    regbucket = {}
    for i, a in enumerate(A):
        regbucket.setdefault(a["regime"], []).append(i)

    lab1, pairs1 = classes_from_pairs(A, rel_l1, bucket)
    lab2, pairs2 = classes_from_pairs(A, rel_l2, bucket)
    p1, p2 = canon_labels(lab1), canon_labels(lab2)
    p4 = canon_labels([(a["regime"], a["minimal"]) for a in A])

    byclass = {}
    for i, lab in enumerate(p4):
        byclass.setdefault(lab, []).append(i)

    kedge = {}
    for lab in sorted(byclass):
        for i, j in itertools.combinations(byclass[lab], 2):
            k = kmin(A[i], A[j])
            if k is not None:
                kedge[(i, j)] = k

    raw_cross = 0
    for r in sorted(regbucket):
        for i, j in itertools.combinations(regbucket[r], 2):
            if p4[i] == p4[j]:
                continue
            if kmin(A[i], A[j]) is not None:
                raw_cross += 1

    l3 = {}
    for k in KS:
        e = [ij for ij, kk in kedge.items() if kk <= k]
        l3[k] = (len(e), close_edges(N, e))

    named = [("L1", p1), ("L2", p2)] + [("L3*(%d)" % k, l3[k][1]) for k in KS] + [("L4", p4)]

    kstar = None
    for k in KS:
        if refines(p2, l3[k][1]):
            kstar = k
            break

    incomparable = sorted("%s~%s" % (na, nb)
                          for (na, pa), (nb, pb) in itertools.combinations(named, 2)
                          if not refines(pa, pb) and not refines(pb, pa))
    equalities = sorted("%s == %s" % (na, nb)
                        for (na, pa), (nb, pb) in itertools.combinations(named, 2)
                        if pa == pb)

    elems, queue = set(p for _, p in named), list(set(p for _, p in named))
    while queue:
        cur = queue.pop()
        for other in list(elems):
            for r in (meet(cur, other), join(cur, other)):
                if r not in elems:
                    elems.add(r)
                    queue.append(r)

    out = {
        "schema": "AG3_PRESENTATION_EQUIVALENCE_ORACLE_V1",
        "universe_size": N,
        "comparable_pairs": sum(len(v) * (len(v) - 1) // 2 for v in regbucket.values()),
        "level_classes": dict((nm, len(set(p))) for nm, p in named),
        "level_related_pairs": dict((nm, npairs(p)) for nm, p in named),
        "l1_pairwise_decisions_true": pairs1,
        "l2_pairwise_decisions_true": pairs2,
        "l3_tolerance_edges": dict((str(k), l3[k][0]) for k in KS),
        "l3_raw_clause_cross_object_pairs": raw_cross,
        "k_star_l2_inside_l3": kstar,
        "incomparable_pairs": incomparable,
        "level_equalities_on_this_universe": equalities,
        "generated_sublattice_size": len(elems),
    }
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
