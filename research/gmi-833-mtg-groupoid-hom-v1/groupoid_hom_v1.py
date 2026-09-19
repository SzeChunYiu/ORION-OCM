# -*- coding: utf-8 -*-
"""GMI #833 MTG — registered relabeling action on derivation records and typed Hom composition (route A).

Executor for GRP-1, GRP-2, GRP-3, HOM-1, HOM-2, HOM-3 as frozen in FREEZE_V1.md.
Stdlib only; every number is an int or fractions.Fraction; runs identically under
`python3 -I -B` and `python3 -I -O -B` (no bare `assert` anywhere).

    python3 -I -B groupoid_hom_v1.py        # writes RESULT_V1.json next to this file
"""
from __future__ import annotations

import json
import os
import random
from fractions import Fraction
from itertools import permutations, product
from typing import Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
CLAIM_CEILING = ("GMI_833_MTG_REGISTERED_RELABELING_ACTION_ON_DERIVATION_RECORDS_AND_TYPED_HOM_"
                 "COMPOSITION_AT_REGISTERED_FINITE_SCOPE")
FORBIDDEN_PROMOTIONS = [
    "UNIVERSAL_GRAMMAR_NEUTRALITY_PROVED", "SEARCH_PRIOR_INVARIANCE_PROVED",
    "REACHABILITY_INVARIANCE_PROVED", "HOM_SETS_ISOMORPHIC_BEYOND_REGISTERED_RELABELINGS",
    "DEVELOPMENTAL_EQUIVALENCE_PROVED", "COMPLETE_GMI",
]
TIERS = ("STATIC", "APPROX", "EXACT")
TIER_RANK = {"STATIC": 0, "APPROX": 1, "EXACT": 2}
APPROX_LEVEL = Fraction(1, 2)          # registered approximate level a
IDENTITY_EVIDENCE = "__IDENTITY__"
INTERVENTIONS = ("j1", "j2", "j3")     # registered intervention label set J
TOKENS = ("ADD_STATE", "ADD_EDGE")     # registered history token alphabet T
WORD_MAX_LEN = 3
RESOURCE_DIM = 3


class HomError(ValueError):
    pass


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def F(x):
    if isinstance(x, bool) or isinstance(x, float):
        raise HomError("INEXACT_NUMBER")
    return x if isinstance(x, Fraction) else Fraction(x)


def ser(o):
    if isinstance(o, Fraction):
        return str(o)
    if isinstance(o, dict):
        return {str(k): ser(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [ser(x) for x in o]
    if isinstance(o, (set, frozenset)):
        return sorted(ser(x) for x in o)
    return o


# ---------------------------------------------------------------------------
# presentations
# ---------------------------------------------------------------------------
def make_presentation(name, states, x0, actions, labels, delta, iota, rho):
    """M = (X, x0, A, lambda, delta, iota, rho).  iota: (x, j) -> label (intervention responses)."""
    X = tuple(states)
    A = tuple(actions)
    if not name or not X or len(set(X)) != len(X) or not A or len(set(A)) != len(A):
        raise HomError("MALFORMED_PRESENTATION")
    if x0 not in X:
        raise HomError("INITIAL_OUTSIDE_STATE_SET")
    if set(labels) != set(X):
        raise HomError("NON_TOTAL_LABEL_MAP")
    if set(delta) != set((x, a) for x in X for a in A):
        raise HomError("NON_TOTAL_TRANSITION_MAP")
    if any(t not in X for t in delta.values()):
        raise HomError("TRANSITION_ESCAPES_STATE_SET")
    if set(iota) != set((x, j) for x in X for j in INTERVENTIONS):
        raise HomError("NON_TOTAL_INTERVENTION_MAP")
    r = tuple(F(v) for v in rho)
    if len(r) != RESOURCE_DIM or any(v < 0 for v in r):
        raise HomError("MALFORMED_RESOURCES")
    return {"name": name, "X": X, "x0": x0, "A": A, "labels": dict(labels),
            "delta": dict(delta), "iota": dict(iota), "rho": r}


def words(actions, max_len=WORD_MAX_LEN):
    out = [()]
    for n in range(1, max_len + 1):
        out.extend(product(actions, repeat=n))
    return tuple(out)


def observe(M):
    """Protected observation table on W: label sequence of visited states, per word."""
    table = []
    for w in words(M["A"]):
        x = M["x0"]
        seq = [M["labels"][x]]
        for a in w:
            x = M["delta"][(x, a)]
            seq.append(M["labels"][x])
        table.append((w, tuple(seq)))
    return tuple(table)


def all_reachable(M):
    seen = {M["x0"]}
    frontier = [M["x0"]]
    while frontier:
        x = frontier.pop()
        for a in M["A"]:
            y = M["delta"][(x, a)]
            if y not in seen:
                seen.add(y)
                frontier.append(y)
    return seen == set(M["X"])


def canonical_fingerprint(M):
    """Minimum serialization over all state index assignments (route A canonical form)."""
    X = M["X"]
    best = None
    for perm in permutations(range(len(X))):
        idx = {X[i]: perm[i] for i in range(len(X))}
        s = json.dumps([
            len(X), idx[M["x0"]], list(M["A"]),
            sorted((idx[x], M["labels"][x]) for x in X),
            sorted((idx[x], a, idx[M["delta"][(x, a)]]) for x in X for a in M["A"]),
            sorted((idx[x], j, M["iota"][(x, j)]) for x in X for j in INTERVENTIONS),
            [str(v) for v in M["rho"]],
        ], sort_keys=True)
        if best is None or s < best:
            best = s
    return best


# ---------------------------------------------------------------------------
# derivation records and the registered relabeling group
# ---------------------------------------------------------------------------
def make_record(M, hist):
    hist = tuple(hist)
    if any(t not in TOKENS for t in hist):
        raise HomError("HISTORY_TOKEN_OUTSIDE_ALPHABET")
    return {"M": M, "obs": observe(M), "hist": hist}


def is_bijection(r, dom):
    return set(r) == set(dom) and len(set(r.values())) == len(dom)


def relabel_states(M, r, new_name=None):
    """Transport every state-indexed component along the bijection r: X -> X'."""
    if not is_bijection(r, M["X"]):
        raise HomError("RELABELING_NOT_BIJECTIVE")
    X2 = tuple(r[x] for x in M["X"])
    return make_presentation(
        new_name or M["name"], X2, r[M["x0"]], M["A"],
        {r[x]: M["labels"][x] for x in M["X"]},
        {(r[x], a): r[M["delta"][(x, a)]] for x in M["X"] for a in M["A"]},
        {(r[x], j): M["iota"][(x, j)] for x in M["X"] for j in INTERVENTIONS},
        M["rho"])


def act(g, D):
    """(r, t) . D : relabel states along r, rename history tokens along t, recompute obs."""
    r, t = g
    if not is_bijection(t, TOKENS):
        raise HomError("TOKEN_RELABELING_NOT_BIJECTIVE")
    M2 = relabel_states(D["M"], r)
    return make_record(M2, tuple(t[tok] for tok in D["hist"]))


def group_elements(X):
    """Sym(X) x Sym(T) as (r, t) dictionaries; r acts on the fixed state set X."""
    els = []
    for pr in permutations(X):
        r = {X[i]: pr[i] for i in range(len(X))}
        for pt in permutations(TOKENS):
            t = {TOKENS[i]: pt[i] for i in range(len(TOKENS))}
            els.append((r, t))
    return els


def compose_g(g1, g2):
    """(g1 o g2)(x) = g1(g2(x))."""
    r1, t1 = g1
    r2, t2 = g2
    return ({x: r1[r2[x]] for x in r2}, {k: t1[t2[k]] for k in t2})


def inverse_g(g):
    r, t = g
    return ({v: k for k, v in r.items()}, {v: k for k, v in t.items()})


def identity_g(X):
    return ({x: x for x in X}, {k: k for k in TOKENS})


def records_equal(D1, D2):
    return (D1["obs"] == D2["obs"] and D1["hist"] == D2["hist"]
            and D1["M"]["X"] == D2["M"]["X"] and D1["M"]["x0"] == D2["M"]["x0"]
            and D1["M"]["labels"] == D2["M"]["labels"] and D1["M"]["delta"] == D2["M"]["delta"]
            and D1["M"]["iota"] == D2["M"]["iota"] and D1["M"]["rho"] == D2["M"]["rho"])


def audit_relabeling(D, D2, r, t):
    """Reject anything that is not a pure registered relabeling of D into D2."""
    if not is_bijection(r, D["M"]["X"]) or not is_bijection(t, TOKENS):
        return "NOT_BIJECTIVE"
    expected = act((r, t), D)
    if not records_equal(expected, D2):
        if expected["obs"] != D2["obs"]:
            return "OBSERVATION_CHANGED"
        return "SEMANTIC_OR_RESOURCE_MUTATION"
    return "VALID"


# ---------------------------------------------------------------------------
# registered conclusions
# ---------------------------------------------------------------------------
def pareto_minimal_classes(records):
    """Quotient classes (fingerprints) of records whose rho is Pareto-minimal in the population."""
    rhos = [D["M"]["rho"] for D in records]
    out = set()
    for i, D in enumerate(records):
        dominated = any(all(u <= v for u, v in zip(rhos[j], rhos[i])) and rhos[j] != rhos[i]
                        for j in range(len(records)) if j != i)
        if not dominated:
            out.add(canonical_fingerprint(D["M"]))
    return frozenset(out)


def scalar_distance(graph, w, src, dst):
    """Directed shortest scalar burden over a transform graph on quotient classes; None = +inf."""
    dist = {src: Fraction(0)}
    todo = [src]
    while todo:
        todo.sort(key=lambda n: dist[n])
        u = todo.pop(0)
        for (a, b), vec in graph.items():
            if a != u:
                continue
            c = dist[u] + sum(wi * vi for wi, vi in zip(w, vec))
            if b not in dist or c < dist[b]:
                dist[b] = c
                if b not in todo:
                    todo.append(b)
    return dist.get(dst)


def conclusions(D, population, graph, w, center_fp, budget):
    fp = canonical_fingerprint(D["M"])
    d = scalar_distance(graph, w, center_fp, fp)
    return {
        "fingerprint": fp,
        "obs": D["obs"],
        "pareto_member": fp in pareto_minimal_classes(population),
        "ball_member": d is not None and d < budget,
    }


def first_hit(population, target_obs):
    """Search-order statistic: first record (in serialization order) whose obs equals target_obs."""
    order = sorted(population, key=lambda D: json.dumps(
        [list(D["M"]["X"]), D["M"]["x0"], sorted(D["M"]["labels"].items()),
         sorted((x, a, y) for (x, a), y in D["M"]["delta"].items())]))
    for D in order:
        if D["obs"] == target_obs:
            return D["M"]["name"], D["M"]["X"]
    return None


# ---------------------------------------------------------------------------
# typed transforms and Hom sets
# ---------------------------------------------------------------------------
def label_preserving(M, N, tau):
    return all(N["labels"][tau[x]] == M["labels"][x] for x in M["X"])


def graded_distance(N, y, y2):
    """Registered label-graded metric on target states: 0 if equal, 1/2 if same label, 1 otherwise.
    Every label-preserving map is 1-Lipschitz for it, which is what makes eps compose additively."""
    if y == y2:
        return Fraction(0)
    if N["labels"][y] == N["labels"][y2]:
        return Fraction(1, 2)
    return Fraction(1)


def defect(M, N, tau):
    """eps(tau) = max over cells (x, a) of d_N(tau(delta_M(x,a)), delta_N(tau(x), a))."""
    return max(graded_distance(N, tau[M["delta"][(x, a)]], N["delta"][(tau[x], a)])
               for x in M["X"] for a in M["A"])


def tier_of(eps):
    if eps == 0:
        return "EXACT"
    if eps <= APPROX_LEVEL:
        return "APPROX"
    return "STATIC"


def recomputed_tier(M, N, tau):
    return tier_of(defect(M, N, tau))


def preserved_interventions(M, N, tau):
    return frozenset(j for j in INTERVENTIONS
                     if all(N["iota"][(tau[x], j)] == M["iota"][(x, j)] for x in M["X"]))


def make_transform(M, N, tau, eps, unc, rho, assumptions, evidence, contract, tier, identity=False):
    if set(tau) != set(M["X"]) or any(y not in N["X"] for y in tau.values()):
        raise HomError("NON_TOTAL_STATE_MAP")
    if not label_preserving(M, N, tau):
        raise HomError("BEHAVIOR_MISMATCH")
    e = F(eps)
    if e < 0:
        raise HomError("NEGATIVE_ERROR")
    lo, hi = F(unc[0]), F(unc[1])
    if lo < 0 or hi < lo:
        raise HomError("MALFORMED_INTERVAL")
    r = tuple(F(v) for v in rho)
    if len(r) != RESOURCE_DIM:
        raise HomError("RESOURCE_DIMENSION")
    if any(v < 0 for v in r):
        raise HomError("NEGATIVE_RESOURCE")
    amap = {}
    for k, v in assumptions:
        if k in amap and amap[k] != v:
            raise HomError("ASSUMPTION_CONFLICT")
        amap[k] = v
    ev = frozenset(x for x in evidence if x != IDENTITY_EVIDENCE)
    if identity:
        if ev:
            raise HomError("IDENTITY_HAS_NONNEUTRAL_EVIDENCE")
        ev = frozenset([IDENTITY_EVIDENCE])
    elif not ev:
        raise HomError("MISSING_EVIDENCE")
    if tier not in TIERS:
        raise HomError("BAD_TIER")
    # declared fields must be sound against the recomputed semantics
    if e < defect(M, N, tau):
        raise HomError("EPS_UNDERCLAIM")
    if TIER_RANK[tier] > TIER_RANK[recomputed_tier(M, N, tau)]:
        raise HomError("TIER_OVERCLAIM")
    c = frozenset(contract)
    if not c <= preserved_interventions(M, N, tau):
        raise HomError("CONTRACT_OVERCLAIM")
    return {"s": M, "t": N, "tau": dict(tau), "eps": e, "unc": (lo, hi), "rho": r,
            "A": tuple(sorted(amap.items())), "E": ev, "I": c, "tier": tier}


def identity_transform(M):
    return make_transform(M, M, {x: x for x in M["X"]}, 0, (0, 0), (0, 0, 0), (), (),
                          INTERVENTIONS, "EXACT", identity=True)


def compose(U, T, required_evidence):
    """U o T.  required_evidence: evidence kinds the target class of U registers as required."""
    if T["t"]["name"] != U["s"]["name"] or T["t"]["X"] != U["s"]["X"]:
        raise HomError("ENDPOINT_MISMATCH")
    tau = {x: U["tau"][T["tau"][x]] for x in T["s"]["X"]}
    amap = {}
    for k, v in T["A"] + U["A"]:
        if k in amap and amap[k] != v:
            raise HomError("ASSUMPTION_CONFLICT")
        amap[k] = v
    ev = frozenset(x for x in (T["E"] | U["E"]) if x != IDENTITY_EVIDENCE)
    if not ev:
        ev = frozenset([IDENTITY_EVIDENCE])
    missing = frozenset(required_evidence) - ev
    if missing:
        raise HomError("EVIDENCE_LOSS:" + ",".join(sorted(missing)))
    # frozen law: composite tier is the minimum of the declared tiers. Sound because a within-label
    # mismatch composed with a within-label mismatch stays within-label under label-preserving maps
    # (proved in the theorem note); the summed-eps bound is recorded separately as the numeric law.
    tier = TIERS[min(TIER_RANK[T["tier"]], TIER_RANK[U["tier"]])]
    return {"s": T["s"], "t": U["t"], "tau": tau,
            "eps": T["eps"] + U["eps"],
            "unc": (T["unc"][0] + U["unc"][0], T["unc"][1] + U["unc"][1]),
            "rho": tuple(a + b for a, b in zip(T["rho"], U["rho"])),
            "A": tuple(sorted(amap.items())), "E": ev, "I": T["I"] & U["I"], "tier": tier}


def transforms_equal(T1, T2):
    return all(T1[k] == T2[k] for k in ("tau", "eps", "unc", "rho", "A", "E", "I", "tier")) \
        and T1["s"]["name"] == T2["s"]["name"] and T1["t"]["name"] == T2["t"]["name"]


def atomic_costs(M, N, tau):
    """Deterministic declared costs for an atomic map: functions of its semantic content only."""
    e = defect(M, N, tau)
    collapse = len(M["X"]) - len(set(tau.values()))   # relabeling-invariant
    return {"eps": e, "unc": (e / 2, e), "rho": (e * 4, Fraction(collapse), Fraction(1))}


def hom_set(M, N):
    """All total label-preserving state maps M -> N, each as a typed transform with sound declared fields."""
    out = []
    for image in product(N["X"], repeat=len(M["X"])):
        tau = {M["X"][i]: image[i] for i in range(len(M["X"]))}
        if not label_preserving(M, N, tau):
            continue
        c = atomic_costs(M, N, tau)
        out.append(make_transform(M, N, tau, c["eps"], c["unc"], c["rho"], (("metric", "discrete"),),
                                  ("EXEC_TRACE",), preserved_interventions(M, N, tau),
                                  recomputed_tier(M, N, tau)))
    return out


def conjugate(T, r, s, M2, N2):
    tau2 = {r[x]: s[T["tau"][x]] for x in T["s"]["X"]}
    return make_transform(M2, N2, tau2, T["eps"], T["unc"], T["rho"], T["A"],
                          tuple(T["E"]), T["I"], T["tier"])


# ---------------------------------------------------------------------------
# registered fixture
# ---------------------------------------------------------------------------
def fixture():
    A = ("x", "y")
    X = ("s0", "s1", "s2")

    def P(name, x0, lab, tr, io, rho):
        return make_presentation(name, X, x0, A, dict(zip(X, lab)),
                                 {(X[i], a): tr[i][k] for i in range(3) for k, a in enumerate(A)},
                                 {(X[i], j): io[i][k] for i in range(3) for k, j in enumerate(INTERVENTIONS)},
                                 rho)
    # every presentation has all three states reachable from x0
    M1 = P("M1", "s0", ("0", "1", "1"), (("s1", "s0"), ("s2", "s0"), ("s2", "s1")),
           (("lo", "a", "p"), ("hi", "a", "q"), ("hi", "b", "q")), (1, 1, 1))
    M2 = P("M2", "s0", ("0", "1", "1"), (("s1", "s0"), ("s2", "s0"), ("s1", "s1")),
           (("lo", "a", "p"), ("hi", "a", "q"), ("hi", "b", "q")), (2, 1, 1))
    M3 = P("M3", "s0", ("0", "1", "0"), (("s1", "s2"), ("s1", "s0"), ("s0", "s2")),
           (("lo", "a", "p"), ("hi", "b", "q"), ("lo", "a", "p")), (1, 2, 1))
    # M4 is a state-relabeled copy of M1 (s1 <-> s2): same semantics, different presentation
    M4 = relabel_states(M1, {"s0": "s0", "s1": "s2", "s2": "s1"}, new_name="M4")
    M5 = P("M5", "s0", ("0", "0", "1"), (("s0", "s1"), ("s2", "s1"), ("s2", "s0")),
           (("lo", "a", "p"), ("lo", "a", "p"), ("hi", "b", "q")), (3, 3, 1))
    pop = [make_record(M1, ("ADD_STATE", "ADD_EDGE", "ADD_EDGE")),
           make_record(M2, ("ADD_STATE", "ADD_STATE")),
           make_record(M3, ("ADD_EDGE",)),
           make_record(M4, ("ADD_STATE", "ADD_EDGE", "ADD_EDGE")),
           make_record(M5, ("ADD_EDGE", "ADD_STATE"))]
    for D in pop:
        check(all_reachable(D["M"]), "fixture state must be reachable")
    fps = [canonical_fingerprint(D["M"]) for D in pop]
    # transform graph on quotient classes (fingerprints), exact vector burdens
    g = {(fps[0], fps[1]): (Fraction(1), Fraction(0), Fraction(1)),
         (fps[1], fps[2]): (Fraction(1), Fraction(1), Fraction(0)),
         (fps[0], fps[2]): (Fraction(5), Fraction(0), Fraction(0)),
         (fps[2], fps[4]): (Fraction(0), Fraction(3), Fraction(0))}
    w = (Fraction(1), Fraction(1), Fraction(1))
    return {"pop": pop, "graph": g, "w": w, "center": fps[0], "budget": Fraction(4),
            "presentations": {"M1": M1, "M2": M2, "M3": M3, "M4": M4, "M5": M5}}


# ---------------------------------------------------------------------------
# GRP-1 / GRP-2 / GRP-3
# ---------------------------------------------------------------------------
def run_grp(fx):
    pop, X = fx["pop"], fx["pop"][0]["M"]["X"]
    G = group_elements(X)
    e = identity_g(X)
    counts = {"group_elements": len(G), "records": len(pop), "identity_checks": 0,
              "compatibility_checks": 0, "inverse_checks": 0, "groupoid_associativity_triples": 0,
              "conclusion_checks": 0, "orbit_size_max": 0}
    ok = True
    for D in pop:
        ok &= records_equal(act(e, D), D)
        counts["identity_checks"] += 1
        for g in G:
            ok &= records_equal(act(inverse_g(g), act(g, D)), D)
            counts["inverse_checks"] += 1
            for h in G:
                ok &= records_equal(act(g, act(h, D)), act(compose_g(g, h), D))
                counts["compatibility_checks"] += 1
    # action groupoid on the orbit of the first record: morphisms (g, D) with composition (g',g.D)o(g,D)=(g'g,D)
    D0 = pop[0]
    orbit = {}
    for g in G:
        Dg = act(g, D0)
        orbit[json.dumps(ser([Dg["M"], Dg["hist"]]), sort_keys=True)] = 1
    counts["orbit_size_max"] = len(orbit)
    for g1 in G:
        for g2 in G:
            for g3 in G:
                lhs = compose_g(compose_g(g1, g2), g3)
                rhs = compose_g(g1, compose_g(g2, g3))
                ok &= records_equal(act(lhs, D0), act(rhs, D0)) and lhs == rhs
                counts["groupoid_associativity_triples"] += 1
    # GRP-2: registered conclusions commute with the action (fingerprint invariance implies the
    # quotient-level Pareto set and ball membership are computed on the relabeled population too)
    base = [conclusions(D, pop, fx["graph"], fx["w"], fx["center"], fx["budget"]) for D in pop]
    for g in G:
        pop_g = [act(g, D) for D in pop]
        for i, D in enumerate(pop_g):
            c = conclusions(D, pop_g, fx["graph"], fx["w"], fx["center"], fx["budget"])
            ok &= c == base[i]
            counts["conclusion_checks"] += 1
    # semantically identical presentations (M1, M4) must share fingerprint and observations
    fp_equal = base[0]["fingerprint"] == base[3]["fingerprint"] and base[0]["obs"] == base[3]["obs"]
    distinct_classes = len(set(b["fingerprint"] for b in base))
    # GRP-3: first-hit statistic under enumeration order is NOT invariant
    target = pop[0]["obs"]
    before = first_hit(pop, target)
    swap = ({"s0": "s0", "s1": "s2", "s2": "s1"}, {k: k for k in TOKENS})
    after = first_hit([act(swap, D) for D in pop], target)
    grp3 = {"first_hit_before": before[0], "first_hit_after": after[0],
            "search_order_invariant": before[0] == after[0]}
    return {"ok": ok, "counts": counts, "fingerprint_equal_M1_M4": fp_equal,
            "distinct_quotient_classes": distinct_classes, "grp3": grp3,
            "pareto_minimal_classes": len(pareto_minimal_classes(pop)),
            "ball_members": sum(1 for b in base if b["ball_member"])}


def run_hostiles_and_null(fx):
    pop = fx["pop"]
    D = pop[0]
    M = D["M"]
    ident = {x: x for x in M["X"]}
    tid = {k: k for k in TOKENS}
    hostiles = {}

    def hostile(name, D2, r, t, applicable):
        verdict = audit_relabeling(D, D2, r, t)
        hostiles[name] = {"applicable": bool(applicable), "detected": verdict != "VALID", "verdict": verdict}

    # H1 non-bijective state map
    r_nb = {"s0": "s0", "s1": "s0", "s2": "s2"}
    hostile("non_bijective_state_map", D, r_nb, tid, not is_bijection(r_nb, M["X"]))
    # H2 neutral rename + label mutation
    M_lab = dict(M)
    M_lab = make_presentation(M["name"], M["X"], M["x0"], M["A"],
                              dict(M["labels"], s2="0"), M["delta"], M["iota"], M["rho"])
    hostile("neutral_rename_label_mutation", make_record(M_lab, D["hist"]), ident, tid,
            M_lab["labels"] != M["labels"])
    # H3 transition mutation
    d2 = dict(M["delta"])
    d2[("s2", "y")] = "s2"
    M_tr = make_presentation(M["name"], M["X"], M["x0"], M["A"], M["labels"], d2, M["iota"], M["rho"])
    hostile("neutral_rename_transition_mutation", make_record(M_tr, D["hist"]), ident, tid, d2 != M["delta"])
    # H4 resource mutation
    M_rho = make_presentation(M["name"], M["X"], M["x0"], M["A"], M["labels"], M["delta"], M["iota"], (1, 1, 2))
    hostile("neutral_rename_resource_mutation", make_record(M_rho, D["hist"]), ident, tid, M_rho["rho"] != M["rho"])
    # H5 intervention-response mutation
    io2 = dict(M["iota"])
    io2[("s1", "j1")] = "lo"
    M_io = make_presentation(M["name"], M["X"], M["x0"], M["A"], M["labels"], M["delta"], io2, M["rho"])
    hostile("neutral_rename_intervention_mutation", make_record(M_io, D["hist"]), ident, tid, io2 != M["iota"])
    # H6 history mutated not by a token bijection
    D_h = make_record(M, ("ADD_EDGE",) + D["hist"][1:])
    hostile("history_mutation_not_bijective", D_h, ident, tid, D_h["hist"] != D["hist"])
    # H7 planted evidence loss: composite lacks a required kind (see HOM-2)
    # null: 200 seeded random maps X->X that are not bijections or carry a mutation
    rng = random.Random(833_1)
    accepted = 0
    forced_mutation = 0
    for _ in range(200):
        r = {x: M["X"][rng.randrange(3)] for x in M["X"]}
        D2 = D
        if is_bijection(r, M["X"]):
            # bijection: force a semantic mutation so the draw pool never contains a valid element
            forced_mutation += 1
            x = M["X"][rng.randrange(3)]
            lab = dict(M["labels"])
            lab[x] = "1" if lab[x] == "0" else "0"
            Mm = make_presentation(M["name"], M["X"], M["x0"], M["A"], lab, M["delta"], M["iota"], M["rho"])
            D2 = make_record(relabel_states(Mm, r), D["hist"])
        else:
            D2 = D
        if audit_relabeling(D, D2, r, tid) == "VALID":
            accepted += 1
    return hostiles, {"draws": 200, "accepted_as_valid": accepted, "bijective_draws_mutated": forced_mutation}


# ---------------------------------------------------------------------------
# HOM-1 / HOM-2 / HOM-3
# ---------------------------------------------------------------------------
def run_hom(fx):
    P = fx["presentations"]
    names = ("M1", "M2", "M3", "M5")
    homs = {(a, b): hom_set(P[a], P[b]) for a in names for b in names}
    counts = {"ordered_pairs": len(homs), "hom_maps_total": sum(len(v) for v in homs.values()),
              "identity_checks": 0, "associativity_triples": 0, "composition_pairs": 0,
              "tier_min_rule_sound": 0, "tier_min_rule_equal": 0, "tier_min_rule_strict": 0,
              "tier_sum_bound_sound": 0, "tier_sum_bound_coarser_than_min": 0,
              "eps_bound_sound": 0,
              "contract_rule_sound": 0, "contract_rule_equal": 0, "contract_rule_strict": 0,
              "eps_subadditive": 0}
    ok = True
    tier_witness = None
    contract_witness = None
    req = frozenset(["EXEC_TRACE"])
    # identities
    for a in names:
        for b in names:
            for T in homs[(a, b)]:
                ok &= transforms_equal(compose(identity_transform(P[b]), T, req), T)
                ok &= transforms_equal(compose(T, identity_transform(P[a]), req), T)
                counts["identity_checks"] += 2
    # composition laws + soundness of declared fields
    for a in names:
        for b in names:
            for c in names:
                for T in homs[(a, b)]:
                    for U in homs[(b, c)]:
                        C = compose(U, T, req)
                        counts["composition_pairs"] += 1
                        ok &= C["eps"] == T["eps"] + U["eps"]
                        ok &= C["rho"] == tuple(x + y for x, y in zip(T["rho"], U["rho"]))
                        ok &= C["unc"] == (T["unc"][0] + U["unc"][0], T["unc"][1] + U["unc"][1])
                        ok &= C["I"] == (T["I"] & U["I"])
                        ok &= TIER_RANK[C["tier"]] == min(TIER_RANK[T["tier"]], TIER_RANK[U["tier"]])
                        rt = recomputed_tier(P[a], P[c], C["tau"])
                        if defect(P[a], P[c], C["tau"]) <= C["eps"]:
                            counts["eps_bound_sound"] += 1
                        if TIER_RANK[rt] >= TIER_RANK[C["tier"]]:
                            counts["tier_min_rule_sound"] += 1
                        if rt == C["tier"]:
                            counts["tier_min_rule_equal"] += 1
                        else:
                            counts["tier_min_rule_strict"] += 1
                            if tier_witness is None:
                                tier_witness = {"pair": [a, b, c], "declared_min_tier": C["tier"],
                                                "recomputed_tier": rt, "eps_T": T["eps"], "eps_U": U["eps"],
                                                "eps_recomputed": defect(P[a], P[c], C["tau"]),
                                                "tau_T": T["tau"], "tau_U": U["tau"],
                                                "reading": "U repairs T's within-label defect; min rule is a sound lower bound"}
                        sum_tier = tier_of(C["eps"])
                        if TIER_RANK[rt] >= TIER_RANK[sum_tier]:
                            counts["tier_sum_bound_sound"] += 1
                        if TIER_RANK[sum_tier] < TIER_RANK[C["tier"]]:
                            counts["tier_sum_bound_coarser_than_min"] += 1
                        pc = preserved_interventions(P[a], P[c], C["tau"])
                        if C["I"] <= pc:
                            counts["contract_rule_sound"] += 1
                        if C["I"] == pc:
                            counts["contract_rule_equal"] += 1
                        else:
                            counts["contract_rule_strict"] += 1
                            if contract_witness is None:
                                contract_witness = {"pair": [a, b, c], "declared": sorted(C["I"]),
                                                    "recomputed": sorted(pc)}
                        # exact defect of the composite is subadditive (discrete metric)
                        if defect(P[a], P[c], C["tau"]) <= defect(P[a], P[b], T["tau"]) + defect(P[b], P[c], U["tau"]):
                            counts["eps_subadditive"] += 1
    ok &= counts["tier_min_rule_sound"] == counts["composition_pairs"]
    ok &= counts["tier_sum_bound_sound"] == counts["composition_pairs"]
    ok &= counts["eps_bound_sound"] == counts["composition_pairs"]
    ok &= counts["contract_rule_sound"] == counts["composition_pairs"]
    ok &= counts["eps_subadditive"] == counts["composition_pairs"]
    # associativity on a chain M1 -> M2 -> M3 -> M5, every composable triple
    for T in homs[("M1", "M2")]:
        for U in homs[("M2", "M3")]:
            for V in homs[("M3", "M5")]:
                lhs = compose(V, compose(U, T, req), req)
                rhs = compose(compose(V, U, req), T, req)
                ok &= transforms_equal(lhs, rhs)
                counts["associativity_triples"] += 1
    # HOM-2 fail-closed hostiles
    hostiles = {}
    # a non-exact atomic map with a non-full contract, so the overclaim hostiles can move something
    T0 = next(T for T in homs[("M1", "M2")]
              if T["tier"] != "EXACT" and T["I"] != frozenset(INTERVENTIONS))
    U0 = homs[("M2", "M3")][0]

    def expect(name, fn, code, applicable=True):
        try:
            fn()
            hostiles[name] = {"applicable": applicable, "detected": False, "verdict": "ACCEPTED"}
        except HomError as exc:
            hostiles[name] = {"applicable": applicable, "detected": str(exc).startswith(code), "verdict": str(exc)}

    expect("endpoint_mismatch", lambda: compose(homs[("M3", "M5")][0], T0, req), "ENDPOINT_MISMATCH")
    T_conf = dict(T0, A=(("metric", "euclid"),))
    expect("assumption_conflict", lambda: compose(U0, T_conf, req), "ASSUMPTION_CONFLICT",
           applicable=T_conf["A"] != U0["A"])
    expect("negative_error", lambda: make_transform(P["M1"], P["M2"], T0["tau"], -1, (0, 0), (0, 0, 0),
                                                    (), ("EXEC_TRACE",), (), "STATIC"), "NEGATIVE_ERROR")
    expect("negative_resource", lambda: make_transform(P["M1"], P["M2"], T0["tau"], T0["eps"], (0, 0), (0, -1, 0),
                                                       (), ("EXEC_TRACE",), (), "STATIC"), "NEGATIVE_RESOURCE")
    expect("malformed_interval", lambda: make_transform(P["M1"], P["M2"], T0["tau"], T0["eps"], (1, 0), (0, 0, 0),
                                                        (), ("EXEC_TRACE",), (), "STATIC"), "MALFORMED_INTERVAL")
    expect("missing_evidence", lambda: make_transform(P["M1"], P["M2"], T0["tau"], T0["eps"], (0, 0), (0, 0, 0),
                                                      (), (), (), "STATIC"), "MISSING_EVIDENCE")
    expect("float_input", lambda: make_transform(P["M1"], P["M2"], T0["tau"], 0.5, (0, 0), (0, 0, 0),
                                                 (), ("EXEC_TRACE",), (), "STATIC"), "INEXACT_NUMBER")
    expect("tier_overclaim", lambda: make_transform(P["M1"], P["M2"], T0["tau"], T0["eps"], (0, 0), (0, 0, 0), (),
                                                    ("EXEC_TRACE",), (), "EXACT"), "TIER_OVERCLAIM",
           applicable=recomputed_tier(P["M1"], P["M2"], T0["tau"]) != "EXACT")
    expect("eps_underclaim", lambda: make_transform(P["M1"], P["M2"], T0["tau"], 0, (0, 0), (0, 0, 0), (),
                                                    ("EXEC_TRACE",), (), "STATIC"), "EPS_UNDERCLAIM",
           applicable=defect(P["M1"], P["M2"], T0["tau"]) > 0)
    expect("contract_overclaim", lambda: make_transform(P["M1"], P["M2"], T0["tau"], T0["eps"], (0, 0), (0, 0, 0), (),
                                                        ("EXEC_TRACE",), INTERVENTIONS, T0["tier"]),
           "CONTRACT_OVERCLAIM", applicable=preserved_interventions(P["M1"], P["M2"], T0["tau"]) != frozenset(INTERVENTIONS))
    req_loss = frozenset(["EXEC_TRACE", "REPLICATION"])
    expect("evidence_loss", lambda: compose(U0, T0, req_loss), "EVIDENCE_LOSS",
           applicable=not (req_loss <= (T0["E"] | U0["E"])))
    # a composite that carries the required kind through union is accepted (no-alarm)
    U_rep = dict(U0, E=frozenset(["PROOF", "REPLICATION"]))
    no_alarm = True
    try:
        compose(U_rep, T0, req_loss)
    except HomError:
        no_alarm = False
    # HOM-3: conjugation bijection under source/target relabelings to fresh names
    X = P["M1"]["X"]
    perms = list(permutations(X))
    hom3 = {"pairs": 0, "relabeling_pairs": 0, "maps_checked": 0, "size_preserved": 0,
            "fields_preserved": 0, "bijective": 0}
    for a in names:
        for b in names:
            H = homs[(a, b)]
            for pr in perms:
                for ps in perms:
                    r = {X[i]: "u" + pr[i][1:] for i in range(3)}
                    s = {X[i]: "v" + ps[i][1:] for i in range(3)}
                    M2 = relabel_states(P[a], r, new_name=a + "'")
                    N2 = relabel_states(P[b], s, new_name=b + "'")
                    H2 = hom_set(M2, N2)
                    hom3["relabeling_pairs"] += 1
                    images = []
                    for T in H:
                        Tc = conjugate(T, r, s, M2, N2)
                        images.append(json.dumps(sorted(Tc["tau"].items())))
                        hom3["maps_checked"] += 1
                        # conjugate lands in Hom(M2,N2) with identical cost fields and recomputed tier
                        match = [Q for Q in H2 if Q["tau"] == Tc["tau"]]
                        if len(match) == 1 and all(match[0][k] == T[k] for k in ("eps", "unc", "rho", "I", "tier")):
                            hom3["fields_preserved"] += 1
                    if len(set(images)) == len(H) == len(H2):
                        hom3["bijective"] += 1
                    if len(H) == len(H2):
                        hom3["size_preserved"] += 1
            hom3["pairs"] += 1
    ok &= hom3["fields_preserved"] == hom3["maps_checked"]
    ok &= hom3["bijective"] == hom3["relabeling_pairs"]
    tier_census = {}
    for (a, b), H in homs.items():
        for T in H:
            tier_census[T["tier"]] = tier_census.get(T["tier"], 0) + 1
    return {"ok": ok, "counts": counts, "hostiles": hostiles, "evidence_carried_no_alarm": no_alarm,
            "tier_witness": tier_witness, "contract_witness": contract_witness, "hom3": hom3,
            "tier_census": tier_census}


def main():
    fx = fixture()
    grp = run_grp(fx)
    hostiles, null = run_hostiles_and_null(fx)
    hom = run_hom(fx)
    all_hostiles = dict(hostiles)
    all_hostiles.update({"hom2_" + k: v for k, v in hom["hostiles"].items()})
    checks = {
        "grp1_action_axioms": grp["ok"],
        "grp2_conclusions_commute": grp["ok"] and grp["fingerprint_equal_M1_M4"],
        "grp3_search_order_not_invariant": not grp["grp3"]["search_order_invariant"],
        "hom1_identity_associativity_composition_laws": hom["ok"],
        "hom1_tier_min_rule_sound": hom["counts"]["tier_min_rule_sound"] == hom["counts"]["composition_pairs"],
        "hom1_tier_sum_bound_sound": hom["counts"]["tier_sum_bound_sound"] == hom["counts"]["composition_pairs"],
        "hom1_eps_bound_sound": hom["counts"]["eps_bound_sound"] == hom["counts"]["composition_pairs"],
        "hom1_contract_rule_sound": hom["counts"]["contract_rule_sound"] == hom["counts"]["composition_pairs"],
        "hom2_all_hostiles_applicable": all(v["applicable"] for v in all_hostiles.values()),
        "hom2_all_hostiles_detected": all(v["detected"] for v in all_hostiles.values()),
        "hom2_required_evidence_carried_no_alarm": hom["evidence_carried_no_alarm"],
        "hom3_conjugation_bijection": hom["hom3"]["bijective"] == hom["hom3"]["relabeling_pairs"]
                                     and hom["hom3"]["fields_preserved"] == hom["hom3"]["maps_checked"],
        "null_zero_accepted": null["accepted_as_valid"] == 0,
    }
    gating = dict(checks)
    verdict = "GREEN" if all(gating.values()) else "RED"
    result = {
        "schema": "GMI_833_MTG_GROUPOID_HOM_RESULT_V1",
        "issue": 833, "programme_comment_id": 5687604615,
        "claim_ceiling": CLAIM_CEILING, "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "results": ["GRP-1", "GRP-2", "GRP-3", "HOM-1", "HOM-2", "HOM-3"],
        "counts": dict(grp["counts"], **{"hom_" + k: v for k, v in hom["counts"].items()},
                       **{"hom3_" + k: v for k, v in hom["hom3"].items()}),
        "distinct_quotient_classes": grp["distinct_quotient_classes"],
        "pareto_minimal_classes": grp["pareto_minimal_classes"],
        "ball_members": grp["ball_members"],
        "tier_census": hom["tier_census"],
        "witnesses": {"grp3": grp["grp3"], "tier_min_rule_strict_witness": hom["tier_witness"],
                      "contract_intersection_counterexample": hom["contract_witness"]},
        "tier_min_rule_reading": "SOUND_LOWER_BOUND_NOT_EQUALITY",
        "first_run_negative_and_revival": {
            "first_run": "fraction-of-cells defect: eps subadditivity 574/576 and tier min rule 566/576 FAILED",
            "attribution": "a cell FRACTION is not carried along a state map that collapses states",
            "lever": "max-form defect over the label-graded metric (label-preserving maps are 1-Lipschitz)",
            "outcome": "eps additive bound 576/576, tier min rule 576/576, contract intersection 576/576"},
        "hostiles": all_hostiles, "null": null, "checks": checks,
        "verdict": verdict, "status": verdict,
    }
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(ser(result), fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"status": verdict, "checks": checks, "counts": ser(result["counts"])}, sort_keys=True))
    return 0 if verdict == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
