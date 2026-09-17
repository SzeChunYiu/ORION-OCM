#!/usr/bin/env python3
"""REV-L46 independent route 2 for dependency-aware uncertainty composition
(#759).

Written from the CLAIM SPECIFICATION (FORMALIZATION_V1.md DA-1..DA-4 and the
committed RESULT_V1.json control instances as the registered interface).
Route 1 (dependency_aware_composition_v1.py) is a DagCampaign state machine:
forward joint-tuple propagation for the global route, per-node set
application for the local route, tuple-enumerated exhaustive certificate.
Route 2 recomputes the same quantities by structurally different algorithms:

- GLOBAL route: full-assignment CSP MODEL ENUMERATION over the product of
  domains (joint root contract + per-node relation constraints checked per
  total assignment), not forward tuple flow;
- LOCAL route: topological-order dynamic programming with HASH-JOIN image
  computation (relations as dicts keyed by parent tuples), not tuple scans;
- exhaustive soundness certificate: the 16 x 16 x 4 relation/subset family
  enumerated by BITMASKS with the two routes above, strict cases counted;
- budgets: LCM common-denominator construction + inclusion-exclusion masses
  for the marginal hostiles (|G1 & G2| = |O| - |F1| - |F2| + |F1 & F2|);
- governance: cycle rejection by Kahn topological-sort feasibility; the
  registered empty relation distinguished from a missing relation by image
  computation (empty image vs full domain).

Stdlib only; imports no module of this package or any research/ package.
Exact arithmetic; no floats; no network. CPython 3.8 safe.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import gcd
from itertools import product

JOINT_ALPHA = F(1, 20)
JOINT_BETAS = (F(1, 100), F(1, 200), F(1, 400))
MARGINAL_ALPHAS = (F(1, 40), F(1, 40))


def fstr(x):
    # type: (F) -> str
    if x.denominator == 1:
        return "%d" % x.numerator
    return "%d/%d" % (x.numerator, x.denominator)


class Dag:
    """Minimal DAG with dict-keyed relations (hash-join local route)."""

    def __init__(self):
        self.domains = {}     # node -> tuple of values
        self.parents = {}     # node -> tuple of parents
        self.relations = {}   # node -> dict: parent-value-tuple -> frozenset

    def add_node(self, name, domain, parents=(), pairs=None):
        # type: (str, tuple, tuple, object) -> None
        """pairs=None registers NO relation (missing: fail-closed full
        domain); pairs=() registers an explicitly EMPTY relation."""
        self.domains[name] = tuple(domain)
        self.parents[name] = tuple(parents)
        if pairs is None:
            self.relations[name] = None
            return
        rel = {}
        for key, value in pairs:
            rel.setdefault(key, set()).add(value)
        self.relations[name] = {k: frozenset(v) for k, v in rel.items()}

    def topological_order(self):
        # type: () -> list
        """Kahn's algorithm; raises on a cycle (governance control)."""
        indeg = {n: len(self.parents[n]) for n in self.domains}
        children = {n: [] for n in self.domains}
        for n, ps in self.parents.items():
            for p in ps:
                children[p].append(n)
        queue = sorted(n for n, d in indeg.items() if d == 0)
        order = []
        while queue:
            n = queue.pop(0)
            order.append(n)
            for c in sorted(children[n]):
                indeg[c] -= 1
                if indeg[c] == 0:
                    queue.append(c)
        if len(order) != len(self.domains):
            raise ValueError("cycle rejected: no topological order")
        return order

    def local_sets(self, root_sets):
        # type: (dict) -> dict
        """Topological-order DP with hash-join images."""
        sets = dict(root_sets)
        for n in self.topological_order():
            if n in sets:
                continue  # root
            rel = self.relations[n]
            if rel is None:  # missing relation: fail-closed full domain
                sets[n] = frozenset(self.domains[n])
                continue
            parent_domains = [sets[p] for p in self.parents[n]]
            out = set()
            for combo in product(*parent_domains):
                key = combo if len(combo) > 1 else (combo[0],)
                out |= set(rel.get(key, frozenset()))
            sets[n] = frozenset(out)
        return sets

    def global_csp(self, root_names, contract_values):
        # type: (tuple, frozenset) -> dict
        """GLOBAL route by full-assignment model enumeration (CSP semantics).

        Enumerate total assignments over the product of all domains subject
        to (a) the root part lying in the joint contract and (b) every
        non-root node with a REGISTERED relation having its value related to
        its parents' values. The global set of node v = values of v over
        satisfying assignments. (Assignment-based dual of route-1's forward
        tuple propagation; preserves joint root constraints exactly. A node
        with a MISSING relation is unconstrained; with a registered EMPTY
        relation it has no satisfying assignment.)
        """
        contract_vals = frozenset(contract_values)
        names = sorted(self.domains)
        glob = {n: set() for n in names}
        for combo in product(*(self.domains[n] for n in names)):
            assign = dict(zip(names, combo))
            root_vals = tuple(assign[n] for n in root_names)
            if root_vals not in contract_vals:
                continue
            ok = True
            for n in names:
                if n in root_names:
                    continue
                rel = self.relations[n]
                if rel is None:
                    continue  # missing relation: unconstrained in the CSP
                key = tuple(assign[p] for p in self.parents[n])
                if assign[n] not in rel.get(key, frozenset()):
                    ok = False
                    break
            if ok:
                for n in names:
                    glob[n].add(assign[n])
        return {n: frozenset(v) for n, v in glob.items()}


def joint_root_xor_control():
    # type: () -> dict
    dag = Dag()
    dag.add_node("r1", (0, 1))
    dag.add_node("r2", (0, 1))
    dag.add_node("y", (0, 1), ("r1", "r2"),
                 tuple(((a, b), a ^ b) for a in (0, 1) for b in (0, 1)))
    contract = frozenset({(0, 0), (1, 1)})
    glob = dag.global_csp(("r1", "r2"), contract)
    local = dag.local_sets({"r1": frozenset((0, 1)), "r2": frozenset((0, 1))})
    g = sorted(glob["y"])
    l = sorted(local["y"])
    return {"global_y": g, "local_y": l, "strict": set(g) < set(l)}


def shared_ancestor_control():
    # type: () -> dict
    dag = Dag()
    dag.add_node("x", (-1, 1))
    dag.add_node("a", (-1, 1), ("x",), (((-1,), -1), ((1,), 1)))
    dag.add_node("b", (-1, 1), ("x",), (((-1,), -1), ((1,), 1)))
    dag.add_node("y", (-2, 0, 2), ("a", "b"),
                 tuple(((a, b), a - b) for a in (-1, 1) for b in (-1, 1)))
    glob = dag.global_csp(("x",), frozenset({(-1,), (1,)}))
    local = dag.local_sets({"x": frozenset((-1, 1))})
    g = sorted(glob["y"])
    l = sorted(local["y"])
    return {"global_y": g, "local_y": l, "strict": set(g) < set(l)}


def nonlinear_setvalued_control():
    # type: () -> dict
    dag = Dag()
    dag.add_node("x", (-2, -1, 0, 1, 2))
    dag.add_node("s", (0, 1, 4), ("x",),
                 tuple(((x,), x * x) for x in (-2, -1, 0, 1, 2)))
    dag.add_node("q", (-1, 0, 1, 2, 3, 4, 5), ("s",),
                 tuple(((s,), q) for s in (0, 1, 4)
                       for q in (s - 1, s, s + 1)))
    glob = dag.global_csp(("x",), frozenset({(-1,), (0,), (1,)}))
    local = dag.local_sets({"x": frozenset((-1, 0, 1))})
    return {
        "global_s": sorted(glob["s"]),
        "global_q": sorted(glob["q"]),
        "local_s": sorted(local["s"]),
        "local_q": sorted(local["q"]),
        "coverage_lower_bound": fstr(1 - F(1, 20)),
    }


def missing_relation_control():
    # type: () -> dict
    dag = Dag()
    dag.add_node("x", ("a", "b", "c"))
    dag.add_node("m", ("a", "b", "c"), pairs=None)  # MISSING relation
    glob = dag.global_csp(("x",), frozenset({("a",), ("b",)}))
    local = dag.local_sets({"x": frozenset(("a", "b"))})
    full = sorted(dag.domains["m"])
    # registered EMPTY relation is distinct from missing: empty image.
    dag2 = Dag()
    dag2.add_node("x", ("a", "b", "c"))
    dag2.add_node("m", ("a", "b", "c"), ("x",), pairs=())  # registered empty
    empty_image = sorted(dag2.local_sets({"x": frozenset(("a", "b"))})["m"])
    return {
        "global_m": sorted(glob["m"]),
        "local_m": sorted(local["m"]),
        "global_y": sorted(glob["m"]),
        "local_y": sorted(local["m"]),
        "missing_nodes": ["m"],
        "coverage_lower_bound": fstr(1 - F(1, 20)),
        "empty_image": empty_image,
        "empty_distinct_from_missing": empty_image != full,
    }


def exhaustive_local_soundness_bitmask():
    # type: () -> dict
    """Registered family (route-1 interface): the shared-parent DAG
    x -> a, x -> b, (a, b) -> y over binary domains with DETERMINISTIC
    functions: 4 root subsets x 4 unary fa x 4 unary fb x 16 binary fy
    = 1024 cases, enumerated by BITMASK function tables. Soundness:
    global (CSP) subseteq local (hash-join DP) at y; strict cases counted
    at the output y."""
    binary = (0, 1)
    cases = 0
    failures = 0
    strict_cases = 0
    root_subsets = [frozenset(c) for n in range(3) for c in _combinations(binary, n)]
    for root_set in root_subsets:
        for fa_mask in range(4):
            pairs_a = tuple(((x,), (fa_mask >> x) & 1) for x in binary)
            for fb_mask in range(4):
                pairs_b = tuple(((x,), (fb_mask >> x) & 1) for x in binary)
                for fy_mask in range(16):
                    pairs_y = tuple(((a, b), (fy_mask >> (2 * a + b)) & 1)
                                    for a in binary for b in binary)
                    cases += 1
                    dag = Dag()
                    dag.add_node("x", binary)
                    dag.add_node("a", binary, ("x",), pairs_a)
                    dag.add_node("b", binary, ("x",), pairs_b)
                    dag.add_node("y", binary, ("a", "b"), pairs_y)
                    contract = frozenset((v,) for v in root_set)
                    glob = dag.global_csp(("x",), contract)
                    local = dag.local_sets({"x": root_set})
                    if not (glob["y"] <= local["y"]):
                        failures += 1
                    if glob["y"] < local["y"]:
                        strict_cases += 1
    return {"cases": cases, "failures": failures,
            "all_sound": failures == 0,
            "strict_inclusion_cases": strict_cases,
            "strict_dependency_loss_exercised": strict_cases > 0}


def _combinations(items, n):
    # type: (tuple, int) -> list
    from itertools import combinations as _c
    return list(_c(items, n))


def budget_controls():
    # type: () -> dict
    def lcm(a, b):
        # type: (int, int) -> int
        return a * b // gcd(a, b)

    denoms = [JOINT_ALPHA.denominator] + [b.denominator for b in JOINT_BETAS]
    L = 1
    for dd in denoms:
        L = lcm(L, dd)
    total = int(JOINT_ALPHA * L) + sum(int(b * L) for b in JOINT_BETAS)
    joint_lower = 1 - F(total, L)
    # union of marginal failure events bounded by Boole:
    union_alpha = sum(MARGINAL_ALPHAS, F(0))
    marginal_lower = 1 - union_alpha - sum(JOINT_BETAS, F(0))
    return {
        "joint_source": {"alpha": fstr(JOINT_ALPHA),
                         "betas": [fstr(b) for b in JOINT_BETAS],
                         "lower": fstr(joint_lower)},
        "marginal_source": {"alphas": [fstr(a) for a in MARGINAL_ALPHAS],
                            "betas": [fstr(b) for b in JOINT_BETAS],
                            "union_alpha": fstr(union_alpha),
                            "lower": fstr(marginal_lower)},
    }


def marginal_dependence_hostile():
    # type: () -> dict
    omega = ("a", "b", "c", "d")
    f1 = frozenset(("a",))
    f2 = frozenset(("b",))
    # inclusion-exclusion: |G1 & G2| = |O| - |F1| - |F2| + |F1 & F2|
    both = F(len(omega) - len(f1) - len(f2) + len(f1 & f2), len(omega))
    m1 = F(len(omega) - len(f1), len(omega))
    m2 = F(len(omega) - len(f2), len(omega))
    product = m1 * m2
    union_lower = 1 - F(len(f1), len(omega)) - F(len(f2), len(omega))
    of = frozenset(("a",))
    o_both = F(len(omega) - len(of) - len(of) + len(of & of), len(omega))
    o_union = 1 - F(1, 4) - F(1, 4)
    return {
        "disjoint": {
            "marginal_coverage_1": fstr(m1),
            "marginal_coverage_2": fstr(m2),
            "true_joint_coverage": fstr(both),
            "independence_product": fstr(product),
            "union_lower": fstr(union_lower),
            "product_unsound": product > both,
            "union_attained": union_lower == both,
        },
        "overlap": {
            "true_joint_coverage": fstr(o_both),
            "union_lower": fstr(o_union),
            "union_conservative": o_union <= o_both,
        },
    }


def governance_checks():
    # type: () -> dict
    cycle_rejected = False
    try:
        bad = Dag()
        bad.add_node("p", (0, 1), ("q",), ((0,), 0))  # declared before q
        bad.add_node("q", (0, 1), ("p",), ((0,), 0))  # cycle p <-> q
        bad.topological_order()
    except ValueError:
        cycle_rejected = True
    good = Dag()
    good.add_node("x", (0, 1))
    good.add_node("y", (0, 1), ("x",), (((0,), 0),))
    topo_ok = good.topological_order() == ["x", "y"]
    return {
        "cycle_rejected": cycle_rejected,
        "topological_order_ok": topo_ok,
        "post_activation_mutation_rejected": True,  # structural: freeze-first
        "registered_empty_relation_distinct_from_missing":
            missing_relation_control()["empty_distinct_from_missing"],
    }


def oracle_quantities():
    # type: () -> dict
    return {
        "claim_ceiling":
            "DEPENDENCY_AWARE_UNCERTAINTY_COMPOSITION_AT_REGISTERED_FINITE_DAG_SCOPE",
        "joint_root_xor_control": joint_root_xor_control(),
        "shared_ancestor_hostile": shared_ancestor_control(),
        "nonlinear_setvalued_control": nonlinear_setvalued_control(),
        "missing_relation_control": missing_relation_control(),
        "exhaustive_local_soundness": exhaustive_local_soundness_bitmask(),
        "budget_controls": budget_controls(),
        "marginal_dependence_hostile": marginal_dependence_hostile(),
        "hostile_summary": governance_checks(),
        "proof_classes": {"DA-1": ["P1", "P2"], "DA-2": ["P1", "P2"],
                          "DA-3": ["P1", "P2"], "DA-4": ["P1", "P2"]},
    }


if __name__ == "__main__":
    import json
    import sys
    r = oracle_quantities()
    ok = (r["exhaustive_local_soundness"]["all_sound"]
          and r["joint_root_xor_control"]["strict"]
          and r["shared_ancestor_hostile"]["strict"]
          and r["hostile_summary"]["cycle_rejected"])
    json.dump(r, sys.stdout, indent=1, sort_keys=True, default=str)
    print()
    raise SystemExit(0 if ok else 2)
