# -*- coding: utf-8 -*-
"""Route B — materially independent oracle for gmi-833-mtg-groupoid-hom-v1.

Imports nothing from groupoid_hom_v1.py.  Differences from route A:
  * canonical form = breadth-first numbering from the initial state in action order
    (route A minimizes over all state permutations);
  * conclusions are compared across the EXPLICITLY ENUMERATED orbit with a separate
    interpreter (route A applies the action to the population and recomputes);
  * Hom sets are enumerated by integer index arithmetic (base-|Y| digits) and
    conjugation is an index map (route A builds maps from itertools.product);
  * the fixture literals are re-declared here from the freeze, not imported.

    python3 -I -B independent_oracle_v1.py    # writes ORACLE_RESULT_V1.json
"""
from __future__ import annotations

import json
import os
from fractions import Fraction
from itertools import permutations

HERE = os.path.dirname(os.path.abspath(__file__))
J = ("j1", "j2", "j3")
TOK = ("ADD_STATE", "ADD_EDGE")
A = ("x", "y")
X = ("s0", "s1", "s2")
LEVEL = Fraction(1, 2)


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def pres(name, x0, lab, tr, io, rho):
    return {"name": name, "x0": x0,
            "lab": {X[i]: lab[i] for i in range(3)},
            "tr": {(X[i], A[k]): tr[i][k] for i in range(3) for k in range(2)},
            "io": {(X[i], J[k]): io[i][k] for i in range(3) for k in range(3)},
            "rho": tuple(Fraction(v) for v in rho), "X": X}


def relabel(M, r):
    return {"name": M["name"], "x0": r[M["x0"]], "X": tuple(r[x] for x in M["X"]),
            "lab": {r[x]: M["lab"][x] for x in M["X"]},
            "tr": {(r[x], a): r[M["tr"][(x, a)]] for x in M["X"] for a in A},
            "io": {(r[x], j): M["io"][(x, j)] for x in M["X"] for j in J},
            "rho": M["rho"]}


def fixture():
    M1 = pres("M1", "s0", ("0", "1", "1"), (("s1", "s0"), ("s2", "s0"), ("s2", "s1")),
              (("lo", "a", "p"), ("hi", "a", "q"), ("hi", "b", "q")), (1, 1, 1))
    M2 = pres("M2", "s0", ("0", "1", "1"), (("s1", "s0"), ("s2", "s0"), ("s1", "s1")),
              (("lo", "a", "p"), ("hi", "a", "q"), ("hi", "b", "q")), (2, 1, 1))
    M3 = pres("M3", "s0", ("0", "1", "0"), (("s1", "s2"), ("s1", "s0"), ("s0", "s2")),
              (("lo", "a", "p"), ("hi", "b", "q"), ("lo", "a", "p")), (1, 2, 1))
    M4 = relabel(M1, {"s0": "s0", "s1": "s2", "s2": "s1"})
    M4["name"] = "M4"
    M5 = pres("M5", "s0", ("0", "0", "1"), (("s0", "s1"), ("s2", "s1"), ("s2", "s0")),
              (("lo", "a", "p"), ("lo", "a", "p"), ("hi", "b", "q")), (3, 3, 1))
    return [M1, M2, M3, M4, M5]


def run(M, word):
    """Own interpreter: list of labels along the word (initial label first)."""
    x = M["x0"]
    out = [M["lab"][x]]
    for a in word:
        x = M["tr"][(x, a)]
        out.append(M["lab"][x])
    return tuple(out)


def all_words(n=3):
    ws = [()]
    layer = [()]
    for _ in range(n):
        layer = [w + (a,) for w in layer for a in A]
        ws.extend(layer)
    return ws


def obs(M):
    return tuple(run(M, w) for w in all_words())


def bfs_canonical(M):
    """Canonical form for a complete deterministic system with a fixed initial state:
    number states in order of first reach (BFS, actions in registered order)."""
    order = [M["x0"]]
    i = 0
    while i < len(order):
        for a in A:
            y = M["tr"][(order[i], a)]
            if y not in order:
                order.append(y)
        i += 1
    check(len(order) == 3, "unreachable state in fixture")
    idx = {s: k for k, s in enumerate(order)}
    return json.dumps([[M["lab"][s] for s in order],
                       [[idx[M["tr"][(s, a)]] for a in A] for s in order],
                       [[M["io"][(s, j)] for j in J] for s in order],
                       [str(v) for v in M["rho"]]])


def main():
    pop = fixture()
    canon = [bfs_canonical(M) for M in pop]
    distinct = len(set(canon))
    m1_m4_equal = canon[0] == canon[3] and obs(pop[0]) == obs(pop[3])
    # explicit orbit enumeration: every conclusion equal across the orbit
    perms = list(permutations(X))
    tokperms = list(permutations(TOK))
    orbit_checks = 0
    orbit_ok = True
    orbit_sizes = []
    for M in pop:
        forms = set()
        for pr in perms:
            r = {X[i]: pr[i] for i in range(3)}
            M2 = relabel(M, r)
            for _pt in tokperms:
                orbit_ok &= obs(M2) == obs(M) and bfs_canonical(M2) == bfs_canonical(M)
                orbit_checks += 1
            forms.add(json.dumps(sorted((k[0] + k[1], v) for k, v in M2["tr"].items())
                                 + sorted(M2["lab"].items()) + [M2["x0"]]))
        orbit_sizes.append(len(forms) * len(tokperms))
    # first-hit statistic by serialization order, before and after the s1<->s2 swap
    def first_hit(P, target):
        key = lambda M: json.dumps([list(M["X"]), M["x0"], sorted(M["lab"].items()),
                                    sorted((x, a, y) for (x, a), y in M["tr"].items())])
        for M in sorted(P, key=key):
            if obs(M) == target:
                return M["name"]
        return None
    target = obs(pop[0])
    swap = {"s0": "s0", "s1": "s2", "s2": "s1"}
    before = first_hit(pop, target)
    after = first_hit([dict(relabel(M, swap), name=M["name"]) for M in pop], target)
    # Hom sets by index arithmetic
    P = {M["name"]: M for M in pop}
    names = ("M1", "M2", "M3", "M5")

    def decode(k):
        return {X[i]: X[(k // (3 ** i)) % 3] for i in range(3)}

    def label_ok(M, N, tau):
        return all(N["lab"][tau[x]] == M["lab"][x] for x in X)

    def gdist(N, y, y2):
        return Fraction(0) if y == y2 else (Fraction(1, 2) if N["lab"][y] == N["lab"][y2] else Fraction(1))

    def defect(M, N, tau):
        return max(gdist(N, tau[M["tr"][(x, a)]], N["tr"][(tau[x], a)]) for x in M["X"] for a in A)

    def tier_of(e):
        return "EXACT" if e == 0 else ("APPROX" if e <= LEVEL else "STATIC")

    def tier(M, N, tau):
        return tier_of(defect(M, N, tau))

    def contract(M, N, tau):
        return frozenset(j for j in J if all(N["io"][(tau[x], j)] == M["io"][(x, j)] for x in X))

    rank = {"STATIC": 0, "APPROX": 1, "EXACT": 2}
    homs = {}
    tier_census = {}
    for a in names:
        for b in names:
            H = [decode(k) for k in range(27) if label_ok(P[a], P[b], decode(k))]
            homs[(a, b)] = H
            for tau in H:
                t = tier(P[a], P[b], tau)
                tier_census[t] = tier_census.get(t, 0) + 1
    comp_pairs = min_strict = sum_coarser = strict_contract = subadd = bound_ok = 0
    for a in names:
        for b in names:
            for c in names:
                for tT in homs[(a, b)]:
                    for tU in homs[(b, c)]:
                        comp = {x: tU[tT[x]] for x in X}
                        comp_pairs += 1
                        eT, eU = defect(P[a], P[b], tT), defect(P[b], P[c], tU)
                        ec = defect(P[a], P[c], comp)
                        if ec <= eT + eU:
                            bound_ok += 1
                        dm = min(rank[tier(P[a], P[b], tT)], rank[tier(P[b], P[c], tU)])
                        ds = rank[tier_of(eT + eU)]
                        rt = rank[tier(P[a], P[c], comp)]
                        check(rt >= dm, "minimum rule unsound")
                        check(rt >= ds, "additive-bound rule unsound")
                        if rt != dm:
                            min_strict += 1
                        if ds < dm:
                            sum_coarser += 1
                        ic = contract(P[a], P[b], tT) & contract(P[b], P[c], tU)
                        rc = contract(P[a], P[c], comp)
                        check(ic <= rc, "intersection rule unsound")
                        if ic != rc:
                            strict_contract += 1
                        if defect(P[a], P[c], comp) <= defect(P[a], P[b], tT) + defect(P[b], P[c], tU):
                            subadd += 1
    assoc = len(homs[("M1", "M2")]) * len(homs[("M2", "M3")]) * len(homs[("M3", "M5")])
    # HOM-3 conjugation as an index map
    hom3_pairs = hom3_relab = hom3_maps = hom3_ok = hom3_bij = 0
    for a in names:
        for b in names:
            H = homs[(a, b)]
            for pr in perms:
                for ps in perms:
                    r = {X[i]: "u" + pr[i][1:] for i in range(3)}
                    s = {X[i]: "v" + ps[i][1:] for i in range(3)}
                    M2, N2 = relabel(P[a], r), relabel(P[b], s)
                    H2 = []
                    for k in range(27):
                        tau2 = {M2["X"][i]: N2["X"][(k // (3 ** i)) % 3] for i in range(3)}
                        if all(N2["lab"][tau2[x]] == M2["lab"][x] for x in M2["X"]):
                            H2.append(tau2)
                    hom3_relab += 1
                    imgs = set()
                    for tau in H:
                        tc = {r[x]: s[tau[x]] for x in X}
                        imgs.add(json.dumps(sorted(tc.items())))
                        hom3_maps += 1
                        # tier / contract / defect are computed on the relabeled presentations
                        e2 = defect(M2, N2, tc)
                        c2 = frozenset(j for j in J if all(N2["io"][(tc[x], j)] == M2["io"][(x, j)] for x in M2["X"]))
                        if e2 == defect(P[a], P[b], tau) and c2 == contract(P[a], P[b], tau) \
                                and any(q == tc for q in H2):
                            hom3_ok += 1
                    if len(imgs) == len(H) == len(H2):
                        hom3_bij += 1
            hom3_pairs += 1
    out = {
        "schema": "GMI_833_MTG_GROUPOID_HOM_ORACLE_RESULT_V1",
        "route": "BFS_CANONICAL_FORM_EXPLICIT_ORBIT_AND_INDEX_ARITHMETIC_HOM",
        "distinct_quotient_classes": distinct,
        "fingerprint_equal_M1_M4": m1_m4_equal,
        "orbit_conclusion_checks": orbit_checks,
        "orbit_conclusions_all_equal": orbit_ok,
        "orbit_size_max": max(orbit_sizes),
        "first_hit_before": before, "first_hit_after": after,
        "search_order_invariant": before == after,
        "hom_maps_total": sum(len(v) for v in homs.values()),
        "tier_census": tier_census,
        "composition_pairs": comp_pairs,
        "tier_min_rule_strict": min_strict,
        "tier_sum_bound_coarser_than_min": sum_coarser,
        "eps_bound_sound": bound_ok,
        "contract_rule_strict": strict_contract,
        "eps_subadditive": subadd,
        "associativity_triples": assoc,
        "hom3_pairs": hom3_pairs, "hom3_relabeling_pairs": hom3_relab,
        "hom3_maps_checked": hom3_maps, "hom3_fields_preserved": hom3_ok, "hom3_bijective": hom3_bij,
        "status": "GREEN" if (orbit_ok and m1_m4_equal and hom3_ok == hom3_maps and hom3_bij == hom3_relab
                              and subadd == comp_pairs and bound_ok == comp_pairs and before != after) else "RED",
    }
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, sort_keys=True))
    return 0 if out["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
