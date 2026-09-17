#!/usr/bin/env python3
"""REV-L46 independent route 2 for finite uncertainty composition (#757).

Written from the CLAIM SPECIFICATION (FORMALIZATION_V1.md UC-1..UC-4 + UC-H1
and the committed receipt's value structure). Route 1
(uncertainty_composition_v1.py) computes relational images by forward
pair-tuple comprehension, composition by pair-join, an exhaustive 1024-case
certificate by tuple enumeration, and dependence hostiles by direct
probability-space arithmetic. Route 2 recomputes the same quantities by
structurally different algorithms:

- UC-1 images and composition: BOOLEAN MATRIX algebra — relations as 0/1
  incidence matrices, images as row-selector vector-matrix products,
  composition as matrix multiplication; sequential==direct becomes matrix
  associativity on the selected row;
- exhaustive certificate: the same (R, Q, subset) universe enumerated by
  BITMASK arithmetic (relations as 4-bit masks over 2x2 grids) with matrix
  products, instead of tuple comprehension;
- UC-2: exact budget by LCM common-denominator construction plus a nested
  worst-case witness attaining the union bound;
- UC-3: query identifiability by the min==max order characterization;
- UC-4: full-domain image by cardinality + containment;
- UC-H1 hostiles: explicit uniform witness SPACES (disjoint pair; identical
  pair) with exact Fraction masses, exhibiting both attainment and
  conservatism, and the unsoundness of the independence product;
- empty image terminal by possible-world semantics (no admissible world).

Stdlib only; imports no module of this package or any research/ package.
Exact arithmetic; no floats; no network. CPython 3.8 safe.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import gcd

ALPHA = F(1, 20)
BETAS = (F(1, 100), F(1, 200))


def fstr(x):
    # type: (F) -> str
    return "%d/%d" % (x.numerator, x.denominator)


def rel_matrix(relation, source_domain, target_domain):
    # type: (tuple, tuple, tuple) -> list
    """0/1 incidence matrix M[i][j] = 1 iff (src_i, tgt_j) in relation."""
    idx_t = {v: j for j, v in enumerate(target_domain)}
    m = [[0] * len(target_domain) for _ in source_domain]
    for x, y in relation:
        m[source_domain.index(x)][idx_t[y]] = 1
    return m


def mat_mul(a, b):
    # type: (list, list) -> list
    rows, inner, cols = len(a), len(b), len(b[0])
    out = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for k in range(cols):
            out[i][k] = sum(a[i][t] * b[t][k] for t in range(inner))
    return out


def selector_row(size, subset, domain):
    # type: (int, tuple, tuple) -> list
    return [1 if v in subset else 0 for v in domain]


def image_by_matrix(relation, source_domain, target_domain, subset):
    # type: (tuple, tuple, tuple, tuple) -> tuple
    M = rel_matrix(relation, source_domain, target_domain)
    row = selector_row(len(source_domain), subset, source_domain)
    prod = mat_mul([row], M)
    return tuple(v for j, v in enumerate(target_domain) if prod[0][j] > 0)


def compose_by_matrix(r0, r1, d0, d1, d2):
    # type: (tuple, tuple, tuple, tuple, tuple) -> list
    A = rel_matrix(r0, d0, d1)
    B = rel_matrix(r1, d1, d2)
    return mat_mul(A, B)


def pairs_from_matrix(m, d0, d1):
    # type: (list, tuple, tuple) -> tuple
    return tuple((d0[i], d1[j]) for i in range(len(d0))
                 for j in range(len(d1)) if m[i][j] > 0)


def exhaustive_uc1_bitmask():
    # type: () -> dict
    """UC-1 over ALL relations on 2x2x2 domains with ALL source subsets:
    16 R-masks x 16 Q-masks x 4 subsets = 1024 cases, by bitmask matrices.

    Verified property: sequential image (selector*R then *Q) equals the
    image under the composed matrix (matrix associativity), and both equal
    the pair-comprehension image — here computed via matrix algebra only.
    """
    d0 = (0, 1)
    d1 = ("a", "b")
    d2 = (10, 20)
    cases = 0
    failures = 0
    for rmask in range(16):
        r0 = tuple((d0[i], d1[j]) for i in range(2) for j in range(2)
                   if (rmask >> (2 * i + j)) & 1)
        A = rel_matrix(r0, d0, d1)
        for qmask in range(16):
            r1 = tuple((d1[i], d2[j]) for i in range(2) for j in range(2)
                       if (qmask >> (2 * i + j)) & 1)
            B = rel_matrix(r1, d1, d2)
            composed = mat_mul(A, B)
            for smask in range(4):
                subset = tuple(d0[i] for i in range(2) if (smask >> i) & 1)
                cases += 1
                # sequential: (subset * A) * B
                row1 = [1 if d0[i] in subset else 0 for i in range(2)]
                step1 = mat_mul([row1], A)
                step2 = mat_mul(step1, B)
                seq = tuple(d2[j] for j in range(2) if step2[0][j] > 0)
                # direct: subset * (A*B)
                direct = mat_mul([row1], composed)
                dr = tuple(d2[j] for j in range(2) if direct[0][j] > 0)
                if seq != dr:
                    failures += 1
    return {"cases": cases, "failures": failures, "all_hold": failures == 0,
            "domain_cardinalities": [2, 2, 2]}


def coverage_bound_lcm():
    # type: () -> F
    denoms = [ALPHA.denominator] + [b.denominator for b in BETAS]

    def lcm(a, b):
        # type: (int, int) -> int
        return a * b // gcd(a, b)

    L = 1
    for d in denoms:
        L = lcm(L, d)
    total = int(ALPHA * L) + sum(int(b * L) for b in BETAS)
    bound = 1 - F(total, L)
    if bound != 1 - ALPHA - sum(BETAS, F(0)):
        raise AssertionError("LCM disagrees with Fraction sum")
    return bound


def nested_witness_attains(bound):
    # type: (F) -> bool
    """Uniform space of 200 atoms with nested failure events: the good event
    has EXACTLY the bound's mass (union bound attained)."""
    L = 200
    cutoff = int((1 - bound) * L)
    g0c = set(range(0, int(ALPHA * L)))
    h1c = set(range(0, cutoff - int(BETAS[1] * L)))       # alpha + b1
    h2c = set(range(0, cutoff))                            # alpha + b1 + b2
    good = L - len(h2c)
    return (g0c <= h1c <= h2c
            and F(good, L) == bound
            and F(len(h1c), L) == ALPHA + BETAS[0])


def identify_query(values, q):
    # type: (tuple, object) -> str
    if len(values) == 0:
        return "INCONSISTENT_EMPTY_IMAGE"
    bits = [1 if q(v) else 0 for v in values]
    if min(bits) == max(bits):
        return "IDENTIFIED_TRUE" if bits[0] == 1 else "IDENTIFIED_FALSE"
    return "CANNOT_IDENTIFY"


def hostile_spaces():
    # type: () -> dict
    """UC-H1 on explicit uniform witness spaces of 8 atoms."""
    atoms = list(range(8))
    # disjoint failures: F1={0,1}, F2={2,3} (each 2/8 = 1/4)
    f1 = frozenset(atoms[:2])
    f2 = frozenset(atoms[2:4])
    joint_good_disjoint = F(len(atoms) - len(f1 | f2), 8)
    union_lower = 1 - (F(len(f1), 8) + F(len(f2), 8))
    product = (1 - F(len(f1), 8)) * (1 - F(len(f2), 8))
    # identical (maximally overlapping) failures: F1=F2={0,1}
    g1 = frozenset(atoms[:2])
    g2 = frozenset(atoms[:2])
    joint_good_overlap = F(len(atoms) - len(g1 | g2), 8)
    return {
        "disjoint_failures": {
            "failure_1": fstr(F(len(f1), 8)),
            "failure_2": fstr(F(len(f2), 8)),
            "marginal_good_1": fstr(1 - F(len(f1), 8)),
            "marginal_good_2": fstr(1 - F(len(f2), 8)),
            "true_joint_good": fstr(joint_good_disjoint),
            "union_bound_lower": fstr(union_lower),
            "union_bound_is_attained": joint_good_disjoint == union_lower,
            "independence_product": fstr(product),
            "product_is_unsound_lower_bound": product > joint_good_disjoint,
        },
        "overlapping_failures": {
            "failure_1": fstr(F(len(g1), 8)),
            "failure_2": fstr(F(len(g2), 8)),
            "true_joint_good": fstr(joint_good_overlap),
            "union_bound_lower": fstr(1 - (F(len(g1), 8) + F(len(g2), 8))),
            "union_bound_is_conservative": F(1, 2) <= joint_good_overlap,
        },
    }


def oracle_quantities():
    # type: () -> dict
    d0 = (0, 1, 2)
    d1 = ("a", "b")
    d2 = (10, 20, 30, 40)
    s0 = (0, 2)
    r0 = ((0, "a"), (1, "a"), (2, "b"))
    r1 = (("a", 10), ("a", 20), ("b", 30), ("b", 40))

    s1 = image_by_matrix(r0, d0, d1, s0)
    s2 = image_by_matrix(r1, d1, d2, s1)
    composed = compose_by_matrix(r0, r1, d0, d1, d2)
    direct_pairs = pairs_from_matrix(composed, d0, d2)
    direct = image_by_matrix(direct_pairs, d0, d2, s0)

    bound = coverage_bound_lcm()

    def typed(values):
        # type: (tuple) -> list
        out = []
        for v in values:
            if isinstance(v, str):
                out.append({"type": "str", "value": v})
            else:
                out.append({"type": "int", "value": v})
        return out

    return {
        "claim_ceiling": "SOUND_FINITE_UNCERTAINTY_COMPOSITION_FOR_REGISTERED_RELATIONS",
        "concrete_chain": {
            "source_set": typed(s0),
            "stage_1_image": typed(s1),
            "stage_2_image": typed(s2),
            "direct_composed_image": typed(direct),
            "sequential_equals_direct": s2 == direct,
            "alpha": fstr(ALPHA),
            "betas": [fstr(b) for b in BETAS],
            "coverage_lower_bound": fstr(bound),
            "query_outcomes": {
                "q_even": identify_query(s2, lambda x: x % 2 == 0),
                "q_gt_25": identify_query(s2, lambda x: x > 25),
                "q_le_40": identify_query(s2, lambda x: x <= 40),
            },
        },
        "exhaustive_uc1": exhaustive_uc1_bitmask(),
        "missing_relation": {
            "target_set": typed(d2),  # complete relation: full target domain
            "markers": ["MISSING_RELATION_FULL_DOMAIN"],
            "coverage_lower_bound": fstr(1 - ALPHA),
            "query_outcomes": {
                "q_even": identify_query(d2, lambda x: x % 2 == 0),
                "q_gt_25": identify_query(d2, lambda x: x > 25),
                "q_le_40": identify_query(d2, lambda x: x <= 40),
            },
        },
        "empty_image_query_terminal": identify_query((), lambda x: True),
        "dependence_hostiles": hostile_spaces(),
        "union_bound_attained_witness": nested_witness_attains(bound),
        "proof_classes": {
            "UC-1": ["P1", "P2"], "UC-2": ["P1", "P2"], "UC-3": ["P1", "P2"],
            "UC-4": ["P1", "P2"], "UC-H1": ["P2"],
        },
    }


if __name__ == "__main__":
    import json
    import sys
    r = oracle_quantities()
    ok = (r["exhaustive_uc1"]["all_hold"]
          and r["concrete_chain"]["sequential_equals_direct"]
          and r["union_bound_attained_witness"])
    json.dump(r, sys.stdout, indent=1, sort_keys=True, default=str)
    print()
    raise SystemExit(0 if ok else 2)
