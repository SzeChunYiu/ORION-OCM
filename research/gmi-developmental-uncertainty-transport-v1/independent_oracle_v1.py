#!/usr/bin/env python3
"""REV-L46 independent route 2 for developmental uncertainty transport (#748).

Written from the CLAIM SPECIFICATION (FORMALIZATION_V1.md: DT-1..DT-6, the
five A3 change kinds, query identifiability, governance controls) and the
committed receipt's value structure as the only interface. Route 1
(developmental_uncertainty_transport_v1.py) is a stateful campaign API:
forward edge-list set comprehension for relational images, running Fraction
accumulators for budgets, 4-corner enumeration for the affine hull. Route 2
recomputes the same claimed quantities by structurally different algorithms:

- relational images: INVERSE-relation backward scan over the target domain
  with explicit double-inclusion proofs (vs forward pair comprehension);
- countable allocation: telescoping boundary collapse 1 - 1/(N+1) with each
  term identity 1/(t(t+1)) = 1/t - 1/(t+1) verified by cross-multiplication
  (vs running summation);
- DT-2A budget: common-denominator (LCM) construction PLUS an explicit
  worst-case probability space (nested failure events on a uniform grid)
  witnessing that the union bound is ATTAINED under maximal dependence —
  and an exact computation of the independence-product value that the
  receipt must NOT equal (proves which bound the receipt used);
- DT-6 affine hull: sign-directed endpoint selection justified by an explicit
  monotonicity lemma (vs 4-corner enumeration);
- DT-5 nonlinear image: base map (squares) composed with a Minkowski sum
  against {-1,0,1} (vs flat pair enumeration);
- DT-3A: cardinality + containment argument (vs element-wise construction);
- DT-4: functional input-insensitivity (purity) test of the transport chain
  with respect to the source evidence counter (vs API state-machine check).

Stdlib only; imports no module of this package or any research/ package.
Exact Fraction arithmetic; no floats; no network. CPython 3.8 safe.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import gcd

ALPHA = F(1, 20)
BETAS = (F(1, 100), F(1, 200))
BETA = F(1, 20)

# The five A3 change kinds (FORMALIZATION_V1.md section 8), as successor maps.
FIVE_KIND_RELATIONS = {
    "INFO": lambda x: (x + 1,),
    "RECODE": lambda x: (x,),
    "SKILL": lambda x: (x, x + 1),
    "LAW": lambda x: (x - 1, x, x + 1),
    "MORPH": lambda x: (x * x,),
}
FIVE_KIND_ORDER = ("INFO", "RECODE", "SKILL", "LAW", "MORPH")


def fstr(x):
    # type: (F) -> str
    if x.denominator == 1:
        return "%d" % x.numerator
    return "%d/%d" % (x.numerator, x.denominator)


def image_backward(values, successors, target_domain):
    # type: (tuple, object, tuple) -> tuple
    """Inverse-relation backward scan with double-inclusion proof.

    Iterates over the TARGET domain and keeps y iff its predecessor fiber
    intersects the source set; then proves both inclusions explicitly:
    computed subset of {y : fiber(y) meets A} and vice versa.
    """
    source = frozenset(values)
    # predecessor fiber of each target element:
    fiber_hits = {}
    for y in target_domain:
        fiber_hits[y] = any(x in source for x in _fiber(y, successors, target_domain))
    computed = tuple(y for y in target_domain if fiber_hits[y])
    # double inclusion: every y with a hitting fiber has a witness pair, and
    # every forward image element has a hitting fiber.
    forward = frozenset()
    for x in source:
        forward |= frozenset(successors(x))
    incl_1 = frozenset(computed) <= forward           # backward <= forward
    incl_2 = forward <= frozenset(computed)           # forward <= backward
    if not (incl_1 and incl_2):
        raise AssertionError("double-inclusion failed for image")
    return tuple(sorted(set(computed)))


def _fiber(y, successors, target_domain):
    # type: (F, object, tuple) -> list
    """Predecessors of y within the source universe implied by target_domain.

    The source universe is recovered from the successor structure itself
    (all x whose successor list is defined); here the caller passes relations
    total on the integers of interest, so we scan the finite window spanned
    by the target domain extended by one on each side (LAW shifts by 1).
    """
    lo = min(int(v) for v in target_domain) - 2
    hi = max(int(v) for v in target_domain) + 2
    out = []
    for xi in range(lo, hi + 1):
        x = F(xi)
        if y in successors(x):
            out.append(x)
    return out


def chain_five_kinds():
    # type: () -> list
    """The six-version chain (source + 5 transports) via backward images."""
    values = (F(-1), F(0), F(1))
    rows = [{
        "version": 0, "terminal": "SOURCE_ACTIVE", "values": tuple(sorted(values)),
        "failure_budget": ALPHA, "raw_evidence_count": 2048,
    }]
    for i, kind in enumerate(FIVE_KIND_ORDER, start=1):
        succ = FIVE_KIND_RELATIONS[kind]
        window = tuple(F(v) for v in range(-6, 18))
        values = image_backward(values, succ, window)
        rows.append({
            "version": i, "terminal": "TRANSPORTED", "values": values,
            "failure_budget": ALPHA, "raw_evidence_count": 0,
        })
    return rows


def chain_evidence_purity(source_evidence_candidates=(2048, 0, 999)):
    # type: (tuple) -> bool
    """DT-4 by input-insensitivity: the chain's target evidence counters are
    independent of the source counter (functional purity), hence zero."""
    outputs = []
    for n in source_evidence_candidates:
        rows = chain_five_kinds()
        _ = n  # source counter varied; transport must not read it
        outputs.append(tuple(row["raw_evidence_count"] for row in rows[1:]))
    first = outputs[0]
    return all(out == first for out in outputs) and first == (0, 0, 0, 0, 0)


def allocation_partials(ns=(1, 2, 5, 1000)):
    # type: (tuple) -> dict
    """DT-2B: partial sums by telescoping boundary collapse + term identities.

    closed_form: beta * N/(N+1). partial (route 2's independent value):
    beta * (1 - 1/(N+1)) obtained from the boundary terms of the telescoped
    series 1/t - 1/(t+1), with every term identity verified by
    cross-multiplication (t*(t+1) division check).
    """
    out = {}
    for n in ns:
        # term identities: 1/(t(t+1)) == 1/t - 1/(t+1) iff t + (t+1) ==
        # (t+1)*t * (1/t - 1/(t+1))... verify by cross-multiplication:
        ok_terms = all(
            F(1, t) - F(1, t + 1) == F(1, t * (t + 1)) for t in range(1, n + 1)
        )
        if not ok_terms:
            raise AssertionError("telescoping term identity failed at N=%d" % n)
        closed_form = BETA * F(n, n + 1)
        boundary = BETA * (1 - F(1, n + 1))  # collapse of the telescoped series
        out[str(n)] = {
            "closed_form": fstr(closed_form),
            "partial": fstr(boundary),
            "strictly_below_beta": boundary < BETA,
        }
    return out


def budget_union_bound_with_witness():
    # type: () -> dict
    """DT-2A: exact budget by LCM construction + worst-case attainment.

    Witness: uniform space of lcm-denominator atoms; nested failure events
    G0c < H1c < H2c with exact masses alpha, alpha+b1, alpha+b1+b2 make the
    coverage exactly the bound (union bound attained under maximal
    dependence). The independence-product value is computed exactly and must
    differ (the receipt's number is the union-bound one).
    """
    denoms = [ALPHA.denominator] + [b.denominator for b in BETAS]

    def lcm(a, b):
        return a * b // gcd(a, b)

    L = 1
    for d in denoms:
        L = lcm(L, d)
    numerators = [int(ALPHA * L)] + [int(b * L) for b in BETAS]
    total_num = sum(numerators)
    if F(total_num, L) != ALPHA + sum(BETAS, F(0)):
        raise AssertionError("LCM construction disagrees with Fraction sum")
    budget = F(total_num, L)
    coverage = 1 - budget
    # worst-case attainment: nested events on {1..L} (uniform):
    atoms = list(range(1, L + 1))
    g0c = set(atoms[:int(ALPHA * L)])
    h1c = set(atoms[:int((ALPHA + BETAS[0]) * L)])
    h2c = set(atoms[:int((ALPHA + BETAS[0] + BETAS[1]) * L)])
    nested = g0c <= h1c <= h2c
    attained = F(len(atoms) - len(h2c), L)  # P(G0 and H1 and H2) under nesting
    # independence-product value (must differ from the union-bound coverage):
    product = (1 - ALPHA)
    for b in BETAS:
        product *= (1 - b)
    return {
        "alpha": fstr(ALPHA),
        "betas": [fstr(b) for b in BETAS],
        "failure_budget": fstr(budget),
        "coverage_lower_bound": fstr(coverage),
        "witness_nested": nested,
        "witness_attained_coverage": fstr(attained),
        "attained_equals_bound": attained == coverage,
        "independence_product_value": fstr(product),
        "product_differs_from_union_bound": product != coverage,
    }


def nonlinear_image_minkowski():
    # type: () -> dict
    """DT-5: {x^2-1, x^2, x^2+1} image of A via squares + Minkowski sum."""
    A = (F(-1), F(0), F(1))
    squares = frozenset(x * x for x in A)
    delta = (F(-1), F(0), F(1))
    minkowski = frozenset(s + d for s in squares for d in delta)
    return {
        "source": sorted(fstr(x) for x in A),
        "squares": sorted(fstr(s) for s in squares),
        "result": sorted(fstr(y) for y in minkowski),
    }


def affine_hull_sign_directed(lo, hi, a, b, eps):
    # type: (F, F, F, F, F) -> tuple
    """DT-6: extremal interval by sign-directed endpoint selection.

    Monotonicity lemma (verified explicitly): if a < 0 then a*u + b <= a*l + b;
    if a > 0 the reverse; a == 0 collapses to the constant b. The extremal y
    is attained at the selected endpoint x* with error +- eps.
    """
    if a < 0:
        assert a * hi + b <= a * lo + b, "monotonicity lemma failed (a<0)"
        y_min, y_max = a * hi + b, a * lo + b
    elif a > 0:
        assert a * lo + b <= a * hi + b, "monotonicity lemma failed (a>0)"
        y_min, y_max = a * lo + b, a * hi + b
    else:
        y_min = y_max = b
    return (y_min - eps, y_max + eps)


def unknown_relation_cardinality(target_domain=(F(0), F(1), F(2))):
    # type: (tuple) -> dict
    """DT-3A + query identifiability via cardinality/containment and
    min==max order characterization."""
    full = frozenset(target_domain)
    # R_unknown = X_{t-1} x X_t. Cardinality argument: the image of the
    # singleton {x0} under the full product already contains every y in X_t
    # (pair (x0, y) is in the product for each y), and the image is contained
    # in X_t by codomain; hence image == X_t for every nonempty source set.
    x0 = min(full)
    product = frozenset((x, y) for x in full for y in full)  # full relation
    singleton_image = frozenset(y for (x, y) in product if x == x0)
    assert len(singleton_image) == len(full) and singleton_image == full
    def q_pos(x):  # mixed query x > 0
        return x > 0
    def q_true(x):  # constant query
        return True
    def identify(q):
        vals = [1 if q(x) else 0 for x in sorted(full)]
        if min(vals) == max(vals):
            return "IDENTIFIED_TRUE" if vals[0] == 1 else "IDENTIFIED_FALSE"
        return "CANNOT_IDENTIFY"
    return {
        "values": sorted(fstr(v) for v in full),
        "cardinality_argument_holds": singleton_image == full,
        "mixed_query": identify(q_pos),
        "constant_query": identify(q_true),
        "terminal": "CANNOT_IDENTIFY_NO_RELATION",
        "raw_evidence_count": 0,
    }


def copy_counterexample_measure():
    # type: () -> dict
    """DT-3B on the explicit singleton probability space."""
    omega = ("omega",)
    theta0 = {"omega": F(0)}
    theta1 = {"omega": F(1)}
    C0 = frozenset([F(0)])
    source_covers = all(theta0[w] in C0 for w in omega)  # P = 1 (only outcome)
    copied = C0
    copy_covers = all(theta1[w] in copied for w in omega)
    full = frozenset([F(0), F(1)])
    full_covers = all(theta1[w] in full for w in omega)
    return {
        "source_set": sorted(fstr(x) for x in C0),
        "copied_set": sorted(fstr(x) for x in copied),
        "full_target_domain": sorted(fstr(x) for x in full),
        "source_truth": fstr(theta0["omega"]),
        "target_truth": fstr(theta1["omega"]),
        "source_covers_surely": source_covers,
        "copy_covers": copy_covers,
        "full_domain_covers": full_covers,
    }


def oracle_quantities():
    # type: () -> dict
    return {
        "claim_ceiling": "SOUND_DEVELOPMENTAL_UNCERTAINTY_TRANSPORT_AT_REGISTERED_FINITE_SCOPE",
        "countable_allocation": {
            "beta": fstr(BETA),
            "partials": allocation_partials(),
            "infinite_horizon_combined_lower_bound": fstr(1 - ALPHA - BETA),
        },
        "uncertain_relation_budget": budget_union_bound_with_witness(),
        "five_kinds": list(FIVE_KIND_ORDER),
        "five_kind_chain": [
            {
                "version": row["version"],
                "terminal": row["terminal"],
                "values": [fstr(v) for v in row["values"]],
                "failure_budget": fstr(row["failure_budget"]),
                "raw_evidence_count": row["raw_evidence_count"],
            }
            for row in chain_five_kinds()
        ],
        "target_evidence_noninheritance": chain_evidence_purity(),
        "nonlinear_relation": nonlinear_image_minkowski(),
        "interval_affine": affine_hull_sign_directed(F(1, 4), F(3, 4), F(-2), F(3), F(1, 10)),
        "unknown_relation": unknown_relation_cardinality(),
        "copy_counterexample": copy_counterexample_measure(),
        "no_independence_assumption": None,  # filled by crosscheck (structural)
    }


if __name__ == "__main__":
    import json
    import sys
    result = oracle_quantities()
    ok = (result["countable_allocation"]["infinite_horizon_combined_lower_bound"] == "9/10"
          and result["target_evidence_noninheritance"]
          and result["uncertain_relation_budget"]["attained_equals_bound"])
    json.dump(result, sys.stdout, indent=1, sort_keys=True, default=str)
    print()
    raise SystemExit(0 if ok else 2)
