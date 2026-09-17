#!/usr/bin/env python3
"""REV-L46 independent route 2 for the canonical T602 formal-proof audit.

Written from the CLAIM SPECIFICATION (FORMAL_PROOF_AUDIT_V1.md: the closed
corpus is exactly T602-01..T602-38 plus T602-17b; P1-P5 rungs; the six finite
proof schemas; universal-limit families; Section-O ledger) — NOT from the
route-1 executor's code paths. Route 1 (formal_proof_audit_v1.py) is an
exhaustive instance sweep (itertools.product over full finite grids, direct
lambda evaluation, full trace listing) validated against the grand-unification
closure files. This module recomputes the same claimed quantities by
structurally different algorithms:

- corpus inventory: arithmetic construction of the identifier set + sorted
  bijection (no dependency-file read; the closed-corpus invariant is quoted in
  the claim spec);
- integer crossover: division-algorithm decomposition (quotient/remainder
  inequality chain) instead of predicate-truth enumeration;
- interaction signs: witness construction from the affine form plus an
  extremal bound (parabola maximum) instead of a bare set equality;
- finite factorization: kernel-partition refinement + constructive canonical
  factor instead of brute-force over candidate functions;
- extrapolation countermodel: product-form zero-factor property and magnitude
  bound instead of point evaluation of the expanded polynomial;
- closure conjunction: permutation-symmetry reduction to the (n, k) multiset
  family instead of the full 2^6 tuple sweep;
- eventual periodicity: Floyd two-pointer cycle detection with the pigeonhole
  bound instead of visited-set counting.

Stdlib only; imports no module of this package or any research/ package.
Exact integer arithmetic throughout; no floats; no network. CPython 3.8 safe.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

ALLOWED_TAGS = frozenset({"P1", "P2", "P3", "P4", "P5"})
P1_MODES = frozenset({"EXECUTABLE_SCHEMA", "FORMAL_DERIVATION_WITH_STRUCTURAL_GATE",
                      "DEFINITIONAL_GATE", "PARENT_REDUCTION_CHECK"})
LIMIT_FAMILIES = frozenset({"NFL", "RICE_HALTING", "GODEL", "BLUM_SPEEDUP",
                            "FINITE_STATE_OEE"})


def corpus_identifiers():
    # type: () -> frozenset
    """The closed canonical corpus, constructed arithmetically from the spec.

    FORMAL_PROOF_AUDIT_V1.md: 'exactly the 39 theorem identifiers ... T602-01
    through T602-38 plus T602-17b'.
    """
    ids = {"T602-%02d" % i for i in range(1, 39)}
    ids.add("T602-17b")
    return frozenset(ids)


def schema_crossover_algebraic():
    # type: () -> bool
    """h*delta > cost  <=>  h >= floor(cost/delta) + 1, by the division algorithm.

    Route 2 verifies the inequality CHAIN (not the two predicates' truth
    tables): write cost = q*delta + r with q = cost//delta, r in [0, delta).
    Then q*delta <= cost < (q+1)*delta because (q+1)*delta = cost - r + delta
    and delta - r >= 1. Hence the least h with h*delta > cost is q+1.
    """
    for cost in range(1, 12):
        for delta in range(1, 8):
            q, r = divmod(cost, delta)
            if not (0 <= r <= delta - 1):
                return False
            if (q + 1) * delta != cost - r + delta:
                return False
            if not (q * delta <= cost < (q + 1) * delta):
                return False
            # the equivalence claim itself, at the boundary only:
            for h in (q - 1, q, q + 1, q + 2):
                lhs = h * delta > cost
                rhs = h >= q + 1
                if lhs != rhs:
                    return False
    return True


def schema_signs_witness_and_bound():
    # type: () -> bool
    """All three interaction signs reachable, and 3 is the maximum, via the
    affine form s(j) = 8 + 8 - j - 10 = 6 - j on the joint costs {3, 6, 7}.

    Route 2 constructs the witnesses from the affine form and proves the
    extremal bound (downward parabola in j is impossible here since s is
    affine decreasing: max at min j) instead of comparing two literal sets.
    """
    def s(j):  # affine form quoted in the claim spec
        return 8 + 8 - j - 10

    witnesses = {3: s(3), 6: s(6), 7: s(7)}  # joint -> sign value
    if set(witnesses.values()) != {3, 0, -1}:
        return False
    # extremal bound: s decreasing (slope -1), min joint = 3 -> max value = 3,
    # so no integer joint in [3, 7] yields a sign > 3: domination check.
    for j in range(3, 8):
        if s(j) > s(3):
            return False
    # reachability of each sign by an explicit witness in the domain:
    for sign in (3, 0, -1):
        if not any(s(j) == sign for j in (3, 6, 7)):
            return False
    return True


def schema_factorization_partition(observation, target):
    # type: (tuple, tuple) -> bool
    """constant-on-fibers <=> a factor exists, via kernel partition refinement
    and CONSTRUCTIVE canonical factor (no candidate search).

    The observation's kernel partition is computed by transitive closure of
    the equivalence 'same observation value'; target factors through the
    observation iff target is constant on each block. The canonical factor is
    built directly from block representatives.
    """
    n = len(observation)
    # union-find closure (route 1 used pairwise 'all' over states; here the
    # partition is computed by merging, then only block representatives are
    # inspected).
    parent = list(range(n))

    def find(a):
        # type: (int) -> int
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a in range(n):
        for b in range(a + 1, n):
            if observation[a] == observation[b]:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[max(ra, rb)] = min(ra, rb)

    blocks = {}
    for a in range(n):
        blocks.setdefault(find(a), []).append(a)

    constant = all(len({target[a] for a in block}) == 1 for block in blocks.values())
    # canonical constructive factor: value -> target of the fiber's
    # least-index representative (no search over candidate functions).
    representative = {}
    for a in range(n):
        representative.setdefault(observation[a], a)
    factor = {v: target[rep] for v, rep in representative.items()}
    consistent = all(factor[observation[a]] == target[a] for a in range(n))
    # constant-on-fibers iff the canonical factor is consistent:
    return constant == consistent


def schema_extrapolation_product_form():
    # type: () -> bool
    """p(x) = (x+1) * x * (x-2) vanishes exactly by the zero-factor property
    at the observed points {-1, 0, 2} and is nonzero at 3 by a magnitude bound.

    Route 1 evaluated the expanded lambda at each point; route 2 uses the
    multiplicative structure: a product is zero iff some factor is zero, and
    |p(3)| = 4*3*1 = 12 > 0 without evaluating the polynomial.
    """
    observed = (-1, 0, 2)

    def factors(x):
        return (x + 1, x, x - 2)

    vanishes = all(0 in factors(x) for x in observed)  # zero-factor property
    magnitude = abs(4 * 3 * 1)  # |factors(3)| componentwise = (4, 3, 1)
    nonzero_at_3 = all(f != 0 for f in factors(3)) and magnitude > 0
    return vanishes and nonzero_at_3


def schema_conjunction_symmetry_reduced():
    # type: () -> bool
    """all(bits) <=> sum(bits) == len(bits), by permutation symmetry.

    Both sides are symmetric functions of the bit tuple, so the equivalence
    need only be verified on the (n, k) multiset family (k ones followed by
    n-k zeros) instead of route 1's full 2^6 product sweep.
    """
    for n in range(0, 9):
        for k in range(0, n + 1):
            bits = [1] * k + [0] * (n - k)
            lhs = all(bits)
            rhs = sum(bits) == len(bits)
            if lhs != rhs:
                return False
    return True


def _floyd_cycle(transition, start):
    # type: (tuple, int) -> tuple
    """Two-pointer cycle detection; returns (mu, lam) or (None, None)."""
    tortoise = transition[start]
    hare = transition[transition[start]]
    while tortoise != hare:
        tortoise = transition[tortoise]
        hare = transition[transition[hare]]
    # find cycle entry mu
    mu = 0
    tortoise = start
    while tortoise != hare:
        tortoise = transition[tortoise]
        hare = transition[hare]
        mu += 1
    # find cycle length lam
    lam = 1
    hare = transition[tortoise]
    while tortoise != hare:
        hare = transition[hare]
        lam += 1
    return mu, lam


def schema_periodicity_floyd():
    # type: () -> bool
    """Every map on 4 states revisits within 5 visited states: Floyd
    two-pointer detection with the pigeonhole bound mu + 1 <= 4 < 5.

    Route 1 listed the full trace and counted distinct visited states; route 2
    detects the cycle structurally.
    """
    from itertools import product
    for t in product(range(4), repeat=4):
        mu, lam = _floyd_cycle(t, 0)
        # orbit of 0 has mu pre-period states then a lam-cycle; distinct
        # states visited in 5 steps is at most min(mu + lam, 5) and the first
        # repeat happens at step mu + lam <= 4 (pigeonhole on 4 states).
        if mu is None or mu + lam > 4:
            return False
        if not (lam >= 1 and mu >= 0):
            return False
    return True


def finite_schema_checks():
    # type: () -> dict
    return {
        "integer_crossover": schema_crossover_algebraic(),
        "interaction_signs": schema_signs_witness_and_bound(),
        "finite_factorization": all(
            schema_factorization_partition(observation, target)
            for observation in _all_functions(4, 2)
            for target in _all_functions(4, 2)
        ),
        "finite_extrapolation_countermodel": schema_extrapolation_product_form(),
        "closure_conjunction": schema_conjunction_symmetry_reduced(),
        "finite_eventual_periodicity": schema_periodicity_floyd(),
    }


def _all_functions(domain, codomain):
    # type: (int, int) -> list
    from itertools import product
    return [tuple(p) for p in product(range(codomain), repeat=domain)]


def oracle_quantities():
    # type: () -> dict
    """Every derived quantity route 1's validation asserts, recomputed here."""
    audit = json.loads((HERE / "THEOREM_AUDIT_V1.json").read_text(encoding="utf-8"))
    ledger = json.loads((HERE / "FORMAL_PROOF_AUDIT_LEDGER_V1.json").read_text(encoding="utf-8"))
    rows = audit["rows"]
    ids = frozenset(row["id"] for row in rows)
    corpus = corpus_identifiers()
    tag_sets = {tag: {row["id"] for row in rows if tag in row["tags"]}
                for tag in sorted(ALLOWED_TAGS)}
    p1_modes = {}
    for row in rows:
        if "P1" in row["tags"]:
            p1_modes[row["proof_mode"]] = p1_modes.get(row["proof_mode"], 0) + 1
    limits = audit["universal_limit_audit"]
    return {
        "theorems": len(rows),
        "inventory_is_closed_corpus": (len(rows) == 39 and len(ids) == 39
                                       and ids == corpus),
        "tag_counts": {tag: len(members) for tag, members in tag_sets.items()},
        "tags_valid_nonempty": all(members and members <= ids for members in tag_sets.values()),
        "p1_proof_modes": dict(sorted(p1_modes.items())),
        "p2_map_matches_tag_set": frozenset(audit["p2_certificates"]) == frozenset(tag_sets["P2"]),
        "p3_map_matches_tag_set": frozenset(audit["p3_assumptions"]) == frozenset(tag_sets["P3"]),
        "p4_map_matches_tag_set": frozenset(audit["p4_experiments"]) == frozenset(tag_sets["P4"]),
        "p5_map_matches_tag_set": frozenset(audit["p5_consequences"]) == frozenset(tag_sets["P5"]),
        "domains_quantified": all(row["domain"].startswith("for ") for row in rows),
        "counterexamples_present": all(len(row["counterexample"]) >= 30 for row in rows),
        "p1_modes_registered": all(row["proof_mode"] in P1_MODES for row in rows
                                   if "P1" in row["tags"]),
        "limit_families": len(limits),
        "limit_inventory_exact": frozenset(limits) == LIMIT_FAMILIES,
        "limit_relevance_subset": all(row["relevant"] and set(row["relevant"]) <= corpus
                                      for row in limits.values()),
        "ledger_rows": len(ledger["rows"]),
        "ledger_all_green": all(row["status"] == "GREEN" for row in ledger["rows"]),
        "schemas": finite_schema_checks(),
    }


if __name__ == "__main__":
    import sys
    result = oracle_quantities()
    ok = (result["inventory_is_closed_corpus"] and result["theorems"] == 39
          and all(result["schemas"].values()) and result["ledger_all_green"])
    json.dump({"oracle": result}, sys.stdout, indent=1, sort_keys=True)
    print()
    raise SystemExit(0 if ok else 2)
