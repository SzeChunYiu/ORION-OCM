#!/usr/bin/env python3
"""ROUTE A executor: exact capability-interaction partition (CIP-1..CIP-4).

Repairs CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1 Section 1.2 / Corollary CI-A4.

Exact arithmetic only (int / fractions.Fraction). Stdlib only. Deterministic.
Run: python3 -I -B partition_witness_v1.py
"""
from __future__ import annotations

import json
import os
import random
from fractions import Fraction
from typing import Dict, FrozenSet, List, Optional, Tuple

# =====================================================================
# 0. The A4 contract channel assignment (transcribed from the frozen
#    interactions_witness.py blob 70de5ec72f936bf1c309f0b0024eedf5e18f1c98).
#    Route B keeps its OWN independent transcription; test_partition_v1
#    asserts the two tables are identical.
# =====================================================================

RESOURCE_CHANNELS: Dict[str, FrozenSet[str]] = {
    "cap-perception":                frozenset({"S", "T"}),
    "cap-selective-attention":       frozenset({"S", "T"}),
    "cap-working-memory":            frozenset({"S", "T"}),
    "cap-episodic-memory":           frozenset({"S", "T"}),
    "cap-semantic-memory":           frozenset({"S", "T"}),
    "cap-procedural-memory":         frozenset({"S", "T"}),
    "cap-retrieval":                 frozenset({"S", "T", "M"}),
    "cap-consolidation":             frozenset({"S", "T"}),
    "cap-forgetting":                frozenset({"S", "T"}),
    "cap-prediction":                frozenset({"S", "T"}),
    "cap-abstraction-concept":       frozenset({"S", "T"}),
    "cap-compositional-reasoning":   frozenset({"S", "T"}),
    "cap-hierarchical-skill":        frozenset({"S", "T"}),
    "cap-planning":                  frozenset({"S", "T"}),
    "cap-exploration":               frozenset({"S", "T"}),
    "cap-causal-inference":          frozenset({"T"}),
    "cap-counterfactual-reasoning":  frozenset({"S", "T"}),
    "cap-metacognition":             frozenset({"T"}),
    "cap-social-cognition":          frozenset({"S", "T"}),
    "cap-communication":             frozenset({"S", "M"}),
    "cap-imitation":                 frozenset({"T"}),
    "cap-teaching":                  frozenset({"T", "M"}),
    "cap-cultural-accumulation":     frozenset({"S", "T"}),
    "cap-self-modeling":             frozenset({"S", "T"}),
    "cap-self-improvement":          frozenset({"T"}),
    "cap-tool-use":                  frozenset({"S", "T", "M"}),
    "cap-coordination":              frozenset({"S", "M"}),
}
CAPABILITY_IDS: Tuple[str, ...] = tuple(RESOURCE_CHANNELS.keys())

# The labels the shipped classifier (interactions_witness.interaction_type) emits,
# reproduced here as DATA so this executor never imports the defective logic.
# shipped(X, Y) = independent if channels disjoint
#               = synergistic if channel sets equal
#               = redundant   otherwise
def shipped_overlap_label(cx: FrozenSet[str], cy: FrozenSet[str]) -> str:
    shared = cx & cy
    if not shared:
        return "independent"
    if shared == cx and shared == cy:
        return "synergistic"
    return "redundant"


# =====================================================================
# 1. CIP-1 — the exact partition on the (max, joint, sum) burden lattice
# =====================================================================

CLASSES: Tuple[str, ...] = ("INDEPENDENT", "REDUNDANT", "PARTIAL_SHARING", "INTERFERING")


class Inadmissible(ValueError):
    """The burden triple violates an admissibility axiom of CIP-1."""


def admissible(b_x, b_y, joint) -> Tuple[bool, str]:
    """Axioms of CIP-1.

    (N) non-negativity : B(X) >= 0, B(Y) >= 0   =>  max <= sum
    (M) monotonicity   : joint >= max(B(X), B(Y))
        Justification: the joint system must satisfy both capabilities' claims, so its
        feasible set is contained in each single-capability feasible set (Lemma C's
        inclusion argument). Running the pair can never cost less than running the more
        expensive one alone.
    """
    if b_x < 0 or b_y < 0:
        return False, "AXIOM_N_VIOLATED: negative individual burden"
    if joint < max(b_x, b_y):
        return False, "AXIOM_M_VIOLATED: joint < max(individual)"
    return True, "ADMISSIBLE"


# Declarative class predicates. CIP-1 asserts exactly one holds on every
# admissible triple.
def p_independent(m, j, s):
    return j == s


def p_redundant(m, j, s):
    return j == m and m < s


def p_partial_sharing(m, j, s):
    return m < j < s


def p_interfering(m, j, s):
    return j > s


PREDICATES = {
    "INDEPENDENT": p_independent,
    "REDUNDANT": p_redundant,
    "PARTIAL_SHARING": p_partial_sharing,
    "INTERFERING": p_interfering,
}

# The aggregate class the original taxonomy called "Synergistic" survives as a
# named UNION, so nothing is deleted by the refinement:
#   SAVING := {joint < sum} = REDUNDANT  (disjoint union)  PARTIAL_SHARING
SAVING_CLASSES = ("REDUNDANT", "PARTIAL_SHARING")


def classify(b_x, b_y, joint) -> str:
    """CIP-1 classification. Operational form (trichotomy), not the predicate form."""
    ok, why = admissible(b_x, b_y, joint)
    if not ok:
        raise Inadmissible(why)
    m, s = max(b_x, b_y), b_x + b_y
    if joint > s:
        return "INTERFERING"
    if joint == s:
        return "INDEPENDENT"
    # joint < s, and joint >= m by (M), hence m < s: the REDUNDANT guard is satisfied
    # automatically on this branch.
    if joint == m:
        return "REDUNDANT"
    return "PARTIAL_SHARING"


def classes_holding(b_x, b_y, joint, predicates=None) -> List[str]:
    """Every class whose predicate holds. CIP-1 => exactly one, for the true map."""
    preds = PREDICATES if predicates is None else predicates
    m, s = max(b_x, b_y), b_x + b_y
    return [name for name, p in sorted(preds.items()) if p(m, joint, s)]


# ---- the SHIPPED Section 1.2 conditions, kept as data to measure DEF-2 ----
LEGACY_PREDICATES = {
    "independent": lambda m, j, s: j == s,
    "redundant": lambda m, j, s: j == m,
    "synergistic": lambda m, j, s: j < s,
    "interfering": lambda m, j, s: j > s,
}


def legacy_classes_holding(b_x, b_y, joint) -> List[str]:
    m, s = max(b_x, b_y), b_x + b_y
    return [n for n, p in sorted(LEGACY_PREDICATES.items()) if p(m, joint, s)]


def verify_partition_on_grid(lo: int = 0, hi: int = 6, predicates=None) -> Tuple[int, List[str]]:
    """Exhaustive finite check of CIP-1 over every admissible integer triple in range.

    Returns (n_admissible_checked, failures). A failure is a triple landing in
    != 1 class.
    """
    failures: List[str] = []
    n = 0
    for bx in range(lo, hi + 1):
        for by in range(lo, hi + 1):
            for j in range(lo, 2 * hi + 3):
                ok, _ = admissible(bx, by, j)
                if not ok:
                    continue
                n += 1
                held = classes_holding(bx, by, j, predicates)
                if len(held) != 1:
                    failures.append(
                        "B(X)=%s B(Y)=%s joint=%s -> %d classes %s"
                        % (bx, by, j, len(held), held)
                    )
                elif predicates is None and classify(bx, by, j) != held[0]:
                    failures.append(
                        "B(X)=%s B(Y)=%s joint=%s -> classify=%s predicate=%s"
                        % (bx, by, j, classify(bx, by, j), held[0])
                    )
    return n, failures


def verify_partition_on_rational_grid() -> Tuple[int, List[str]]:
    """Same check with exact Fraction burdens (CIP-1 is not an integer artefact)."""
    vals = [Fraction(0), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3), Fraction(1),
            Fraction(3, 2), Fraction(7, 3)]
    failures: List[str] = []
    n = 0
    for bx in vals:
        for by in vals:
            for j in vals + [bx + by, max(bx, by), bx + by + Fraction(1, 5)]:
                ok, _ = admissible(bx, by, j)
                if not ok:
                    continue
                n += 1
                held = classes_holding(bx, by, j)
                if len(held) != 1 or classify(bx, by, j) != held[0]:
                    failures.append("B(X)=%s B(Y)=%s joint=%s -> %s" % (bx, by, j, held))
    return n, failures


# =====================================================================
# 2. CIP-2 — the A4 registered instance: burdens from claim sets
# =====================================================================
# Under the A4 contract's frozen accounting each capability's per-channel claim
# is registered as FULLY SHAREABLE: all capabilities that use channel c claim the
# SAME single unit of c. So Q_X(c) = {unit(c)} for c in R(X), and empty otherwise.
#   B(X)     = sum_c mu(Q_X(c))          = |R(X)|
#   B({X,Y}) = sum_c mu(Q_X(c) u Q_Y(c)) = |R(X) u R(Y)|

def a4_claims(cap: str) -> Dict[str, FrozenSet[str]]:
    return {c: frozenset({"unit-" + c}) for c in sorted(RESOURCE_CHANNELS[cap])}


def burden(claims: Dict[str, FrozenSet[str]]) -> int:
    return sum(len(v) for v in claims.values())


def joint_burden(cx: Dict[str, FrozenSet[str]], cy: Dict[str, FrozenSet[str]]) -> int:
    chans = set(cx) | set(cy)
    return sum(len(cx.get(c, frozenset()) | cy.get(c, frozenset())) for c in chans)


def census() -> Dict[str, object]:
    """Corrected 27x27 census + full per-pair delta against the shipped labels."""
    counts = dict((c, 0) for c in CLASSES)
    shipped_counts: Dict[str, int] = {"independent": 0, "synergistic": 0, "redundant": 0}
    rows: List[Dict[str, object]] = []
    n_multi_legacy = 0
    n_contradiction = 0
    changed = 0
    for i, x in enumerate(CAPABILITY_IDS):
        for y in CAPABILITY_IDS[i + 1:]:
            qx, qy = a4_claims(x), a4_claims(y)
            bx, by = burden(qx), burden(qy)
            j = joint_burden(qx, qy)
            k = classify(bx, by, j)
            counts[k] += 1
            old = shipped_overlap_label(RESOURCE_CHANNELS[x], RESOURCE_CHANNELS[y])
            shipped_counts[old] += 1
            legacy = legacy_classes_holding(bx, by, j)
            if len(legacy) > 1:
                n_multi_legacy += 1
            contradiction = old not in legacy
            if contradiction:
                n_contradiction += 1
            # relation of the two channel sets (drives CIP-3)
            rx, ry = RESOURCE_CHANNELS[x], RESOURCE_CHANNELS[y]
            if not (rx & ry):
                rel = "disjoint"
            elif rx == ry:
                rel = "equal"
            elif rx <= ry or ry <= rx:
                rel = "nested-proper"
            else:
                rel = "non-nested-overlap"
            if old.upper() != k:
                changed += 1
            rows.append({
                "x": x, "y": y,
                "channels_x": "".join(sorted(rx)), "channels_y": "".join(sorted(ry)),
                "relation": rel,
                "B_x": bx, "B_y": by, "max": max(bx, by), "joint": j, "sum": bx + by,
                "shipped_label": old,
                "corrected_class": k,
                "label_changed": old.upper() != k,
                "legacy_1_2_labels": legacy,
                "shipped_contradicts_1_2": contradiction,
            })
    return {
        "pairs": len(rows),
        "corrected_counts": counts,
        "shipped_counts": shipped_counts,
        "def1_shipped_contradicts_section_1_2": n_contradiction,
        "def2_pairs_with_non_unique_1_2_label": n_multi_legacy,
        "labels_changed": changed,
        "rows": rows,
    }


def delta_table(cen: Dict[str, object]) -> List[Dict[str, object]]:
    """Aggregate transition table: (shipped_label, relation) -> corrected_class."""
    agg: Dict[Tuple[str, str, str], int] = {}
    for r in cen["rows"]:  # type: ignore[index]
        key = (r["shipped_label"], r["relation"], r["corrected_class"])
        agg[key] = agg.get(key, 0) + 1
    out = []
    for (old, rel, new), n in sorted(agg.items()):
        out.append({"shipped_label": old, "channel_relation": rel,
                    "corrected_class": new, "pairs": n, "changed": old.upper() != new})
    return out


# =====================================================================
# 3. CIP-2b — under union accounting INTERFERING is provably EMPTY
#    (this replaces the shipped verify_no_interference(), which was vacuous:
#     the shipped interaction_type() has no "interfering" return path at all,
#     so it could never return False.)
# =====================================================================

def union_accounting_is_subadditive() -> Tuple[bool, int]:
    """Every A4 pair satisfies joint <= sum, checked by direct computation.

    Non-vacuous: classify() computes joint and sum and HAS a reachable INTERFERING
    branch (exercised by ce2_interfering_triple() below).
    """
    checked = 0
    for i, x in enumerate(CAPABILITY_IDS):
        for y in CAPABILITY_IDS[i + 1:]:
            qx, qy = a4_claims(x), a4_claims(y)
            if joint_burden(qx, qy) > burden(qx) + burden(qy):
                return False, checked
            checked += 1
    return True, checked


def ce2_interfering_triple(budget: int = 10, x_needs: int = 8, upkeep: int = 3,
                           contention: int = 2) -> Tuple[int, int, int]:
    """CE-2 accounting: Y carries MANDATORY upkeep charged from X's hard budget, so
    the joint burden is sum PLUS a contention surcharge. This is outside union/
    free-option accounting, which is exactly why INTERFERING must stay in CIP-1.
    Returns (B(X), B(Y), joint) with joint > sum.
    """
    b_x, b_y = x_needs, upkeep
    return b_x, b_y, b_x + b_y + contention


# =====================================================================
# 4. CIP-3 — correspondence and divergence with the channel-overlap predicate
# =====================================================================

def cip3_fibres(cen: Dict[str, object]) -> Dict[str, Dict[str, int]]:
    """For each channel-relation fibre, which corrected classes occur (and how often)."""
    fib: Dict[str, Dict[str, int]] = {}
    for r in cen["rows"]:  # type: ignore[index]
        fib.setdefault(r["relation"], {})
        k = r["corrected_class"]
        fib[r["relation"]][k] = fib[r["relation"]].get(k, 0) + 1
    return fib


def cip3_independent_coincidence(cen: Dict[str, object]) -> Tuple[bool, int]:
    """INDEPENDENT (burden) <=> disjoint channels (overlap predicate), exactly."""
    n = 0
    for r in cen["rows"]:  # type: ignore[index]
        lhs = r["corrected_class"] == "INDEPENDENT"
        rhs = r["relation"] == "disjoint"
        if lhs != rhs:
            return False, n
        if lhs:
            n += 1
    return True, n


# =====================================================================
# 5. CIP-4 — Lemma B precision: mu must be strictly positive
# =====================================================================

def mu_counting(subset: FrozenSet[str], weights: Dict[str, Fraction]) -> Fraction:
    return sum((weights[u] for u in subset), Fraction(0))


def lemma_b_nested_iff(weights: Dict[str, Fraction]) -> Tuple[bool, Optional[Tuple[str, str]]]:
    """Check `mu(Qx u Qy) == max(mu Qx, mu Qy)  iff  nested` over ALL subset pairs
    of the finite universe carrying the given unit weights.

    Returns (holds, counterexample). The `if` direction (nested => max) holds for any
    non-negative additive mu. The `only if` direction needs STRICT POSITIVITY:
    mu(A) = 0 => A = empty, i.e. every unit has weight > 0.
    """
    units = sorted(weights)
    n = len(units)
    subsets: List[FrozenSet[str]] = []
    for mask in range(1 << n):
        subsets.append(frozenset(units[k] for k in range(n) if mask >> k & 1))
    for qx in subsets:
        for qy in subsets:
            mx, my = mu_counting(qx, weights), mu_counting(qy, weights)
            mu_union = mu_counting(qx | qy, weights)
            is_max = mu_union == max(mx, my)
            nested = qx <= qy or qy <= qx
            if is_max != nested:
                return False, ("{" + ",".join(sorted(qx)) + "}",
                               "{" + ",".join(sorted(qy)) + "}")
    return True, None


COUNTING_WEIGHTS = {"u1": Fraction(1), "u2": Fraction(1), "u3": Fraction(1)}
NULL_UNIT_WEIGHTS = {"u1": Fraction(1), "u2": Fraction(1), "u3": Fraction(0)}


# =====================================================================
# 6. Hostiles (must be DETECTED) and the randomized null
# =====================================================================

def hostile_a_double_class() -> Tuple[bool, str]:
    """(a) a classifier that admits a pair into two classes.

    Variant A1: the REDUNDANT guard `max < sum` removed.
    Variant A2: the SHIPPED Section 1.2 map, measured on the real 351 A4 pairs.
    Detection = the partition checker reports >=1 triple in != 1 class.
    """
    broken = dict(PREDICATES)
    broken["REDUNDANT"] = lambda m, j, s: j == m  # guard removed
    _, fails = verify_partition_on_grid(predicates=broken)
    a1 = len(fails) > 0
    cen = census()
    a2 = cen["def2_pairs_with_non_unique_1_2_label"] > 0  # type: ignore[operator]
    return (a1 and a2), "A1 guardless-REDUNDANT failures=%d; A2 shipped-1.2 multi-label A4 pairs=%d" % (
        len(fails), cen["def2_pairs_with_non_unique_1_2_label"])


def hostile_b_missing_interfering() -> Tuple[bool, str]:
    """(b) a joint > sum pair a partition lacking INTERFERING cannot place."""
    bx, by, j = ce2_interfering_triple()
    three = dict((k, v) for k, v in PREDICATES.items() if k != "INTERFERING")
    held = classes_holding(bx, by, j, three)
    full = classes_holding(bx, by, j)
    return (len(held) == 0 and full == ["INTERFERING"]), \
        "CE-2 triple B(X)=%d B(Y)=%d joint=%d sum=%d: 3-class map places it in %d classes; CIP-1 places it in %s" % (
            bx, by, j, bx + by, len(held), full)


def hostile_c_degenerate_zero_burden() -> Tuple[bool, str]:
    """(c) the degenerate max == sum pair (one capability has zero burden)."""
    bx, by, j = 3, 0, 3
    m, s = max(bx, by), bx + by
    assert m == s == 3
    guardless = dict(PREDICATES)
    guardless["REDUNDANT"] = lambda mm, jj, ss: jj == mm
    bad = classes_holding(bx, by, j, guardless)
    good = classes_holding(bx, by, j)
    return (len(bad) == 2 and good == ["INDEPENDENT"] and classify(bx, by, j) == "INDEPENDENT"), \
        "zero-burden triple (3,0,3): max=sum=3; guardless map -> %s ; CIP-1 -> %s" % (bad, good)


def hostile_d_non_strictly_positive_mu() -> Tuple[bool, str]:
    """(d) a non-strictly-positive mu breaking Lemma B's `iff nested`."""
    ok_counting, _ = lemma_b_nested_iff(COUNTING_WEIGHTS)
    ok_null, ce = lemma_b_nested_iff(NULL_UNIT_WEIGHTS)
    return (ok_counting and not ok_null), \
        "counting measure: iff holds = %s ; measure with mu(u3)=0: iff holds = %s, counterexample Qx=%s Qy=%s" % (
            ok_counting, ok_null, ce[0] if ce else None, ce[1] if ce else None)


def hostile_e_inadmissible_functional() -> Tuple[bool, str]:
    """(e) a burden functional violating axiom (M): joint < max. Must be REJECTED,
    not silently swallowed into PARTIAL_SHARING."""
    bx, by, j = 4, 2, 3  # joint 3 < max 4
    held = classes_holding(bx, by, j)
    raised = False
    try:
        classify(bx, by, j)
    except Inadmissible:
        raised = True
    return (raised and held == []), \
        "triple (4,2,3): joint<max; classify raises Inadmissible=%s; predicates holding=%s" % (raised, held)


def no_alarm_control_disjoint_pairs() -> Tuple[bool, int]:
    """NO-ALARM: the 8 genuinely disjoint-channel A4 pairs must be INDEPENDENT under
    BOTH routes/readings, and must NOT be flagged as contradictions."""
    n = 0
    for i, x in enumerate(CAPABILITY_IDS):
        for y in CAPABILITY_IDS[i + 1:]:
            rx, ry = RESOURCE_CHANNELS[x], RESOURCE_CHANNELS[y]
            if rx & ry:
                continue
            n += 1
            qx, qy = a4_claims(x), a4_claims(y)
            if classify(burden(qx), burden(qy), joint_burden(qx, qy)) != "INDEPENDENT":
                return False, n
            if shipped_overlap_label(rx, ry) != "independent":
                return False, n
    return True, n


def no_alarm_control_chain_contract() -> Tuple[bool, int]:
    """NO-ALARM 2: on a synthetic contract whose channel sets form a CHAIN (every pair
    nested), the shipped overlap predicate has ZERO Section-1.2 contradictions.
    The DEF-1 detector must stay silent here — it is not crying wolf."""
    chain = [frozenset(), frozenset({"S"}), frozenset({"S", "T"}), frozenset({"S", "T", "M"})]
    contradictions = 0
    n = 0
    for i in range(len(chain)):
        for jx in range(i + 1, len(chain)):
            rx, ry = chain[i], chain[jx]
            n += 1
            bx, by = len(rx), len(ry)
            jt = len(rx | ry)
            old = shipped_overlap_label(rx, ry)
            if old not in legacy_classes_holding(bx, by, jt):
                contradictions += 1
    return contradictions == 0, n


def null_random_classifiers(trials: int = 200, seed: int = 8331) -> Tuple[int, int]:
    """NULL the true result beats: random label assignments over the 351 A4 pairs.
    Returns (n_fully_justified, trials). Expect 0/trials."""
    rng = random.Random(seed)
    triples = []
    for i, x in enumerate(CAPABILITY_IDS):
        for y in CAPABILITY_IDS[i + 1:]:
            qx, qy = a4_claims(x), a4_claims(y)
            triples.append((burden(qx), burden(qy), joint_burden(qx, qy)))
    good = 0
    for _ in range(trials):
        if all(PREDICATES[rng.choice(CLASSES)](max(bx, by), j, bx + by) for bx, by, j in triples):
            good += 1
    return good, trials


# =====================================================================
# 7. main
# =====================================================================

def build_result() -> Dict[str, object]:
    cen = census()
    n_grid, grid_fails = verify_partition_on_grid()
    n_rat, rat_fails = verify_partition_on_rational_grid()
    sub_ok, sub_n = union_accounting_is_subadditive()
    cip3_ok, cip3_n = cip3_independent_coincidence(cen)
    ctrl_ok, ctrl_n = no_alarm_control_disjoint_pairs()
    chain_ok, chain_n = no_alarm_control_chain_contract()
    null_good, null_n = null_random_classifiers()
    hostiles = {
        "a_double_class": hostile_a_double_class(),
        "b_missing_interfering": hostile_b_missing_interfering(),
        "c_degenerate_zero_burden": hostile_c_degenerate_zero_burden(),
        "d_non_strictly_positive_mu": hostile_d_non_strictly_positive_mu(),
        "e_inadmissible_functional": hostile_e_inadmissible_functional(),
    }
    return {
        "package": "gmi-833-capability-interaction-partition-v1",
        "route": "A (partition_witness_v1)",
        "cip1_partition_grid": {"admissible_triples_checked": n_grid, "failures": grid_fails},
        "cip1_partition_rational_grid": {"admissible_triples_checked": n_rat, "failures": rat_fails},
        "cip2_census": {
            "pairs": cen["pairs"],
            "corrected_counts": cen["corrected_counts"],
            "shipped_counts": cen["shipped_counts"],
            "labels_changed": cen["labels_changed"],
            "def1_shipped_contradicts_section_1_2": cen["def1_shipped_contradicts_section_1_2"],
            "def2_pairs_with_non_unique_1_2_label": cen["def2_pairs_with_non_unique_1_2_label"],
        },
        "cip2b_union_accounting_subadditive": {"holds": sub_ok, "pairs_checked": sub_n},
        "cip3": {
            "independent_coincides_with_disjoint": cip3_ok,
            "independent_pairs": cip3_n,
            "fibres": cip3_fibres(cen),
        },
        "cip4_lemma_b": {
            "counting_measure_iff_nested": lemma_b_nested_iff(COUNTING_WEIGHTS)[0],
            "null_unit_measure_iff_nested": lemma_b_nested_iff(NULL_UNIT_WEIGHTS)[0],
        },
        "controls": {
            "no_alarm_disjoint_pairs": {"ok": ctrl_ok, "pairs": ctrl_n},
            "no_alarm_chain_contract_zero_def1": {"ok": chain_ok, "pairs": chain_n},
        },
        "null_random_classifiers_fully_justified": {"good": null_good, "trials": null_n},
        "hostiles_detected": dict((k, {"detected": v[0], "detail": v[1]}) for k, v in hostiles.items()),
        "delta_table": delta_table(cen),
        "per_pair": cen["rows"],
    }


def main() -> int:
    res = build_result()
    ok = True
    print("=== CIP partition witness (ROUTE A) ===")
    print("CIP-1 integer grid : %d admissible triples, %d failures"
          % (res["cip1_partition_grid"]["admissible_triples_checked"],
             len(res["cip1_partition_grid"]["failures"])))
    ok &= not res["cip1_partition_grid"]["failures"]
    print("CIP-1 rational grid: %d admissible triples, %d failures"
          % (res["cip1_partition_rational_grid"]["admissible_triples_checked"],
             len(res["cip1_partition_rational_grid"]["failures"])))
    ok &= not res["cip1_partition_rational_grid"]["failures"]
    c = res["cip2_census"]
    print("CIP-2 census (%d pairs): %s" % (c["pairs"], c["corrected_counts"]))
    print("      shipped        : %s" % (c["shipped_counts"],))
    print("      labels changed : %d" % c["labels_changed"])
    print("      DEF-1 shipped-contradicts-1.2 : %d/%d" % (c["def1_shipped_contradicts_section_1_2"], c["pairs"]))
    print("      DEF-2 non-unique 1.2 label    : %d/%d" % (c["def2_pairs_with_non_unique_1_2_label"], c["pairs"]))
    ok &= c["pairs"] == 351
    print("CIP-2b union accounting subadditive: %s (%d pairs)"
          % (res["cip2b_union_accounting_subadditive"]["holds"],
             res["cip2b_union_accounting_subadditive"]["pairs_checked"]))
    ok &= res["cip2b_union_accounting_subadditive"]["holds"]
    print("CIP-3 INDEPENDENT <=> disjoint channels: %s (%d pairs); fibres: %s"
          % (res["cip3"]["independent_coincides_with_disjoint"], res["cip3"]["independent_pairs"],
             res["cip3"]["fibres"]))
    ok &= res["cip3"]["independent_coincides_with_disjoint"]
    print("CIP-4 iff-nested under counting mu: %s ; under mu with a null unit: %s"
          % (res["cip4_lemma_b"]["counting_measure_iff_nested"],
             res["cip4_lemma_b"]["null_unit_measure_iff_nested"]))
    ok &= res["cip4_lemma_b"]["counting_measure_iff_nested"]
    ok &= not res["cip4_lemma_b"]["null_unit_measure_iff_nested"]
    for k, v in sorted(res["hostiles_detected"].items()):
        print("HOSTILE %-28s DETECTED=%s | %s" % (k, v["detected"], v["detail"]))
        ok &= v["detected"]
    ctl = res["controls"]
    print("CONTROL no-alarm disjoint pairs      : ok=%s n=%d" % (ctl["no_alarm_disjoint_pairs"]["ok"], ctl["no_alarm_disjoint_pairs"]["pairs"]))
    print("CONTROL no-alarm chain contract      : ok=%s n=%d (DEF-1 detector silent on clean data)" % (ctl["no_alarm_chain_contract_zero_def1"]["ok"], ctl["no_alarm_chain_contract_zero_def1"]["pairs"]))
    ok &= ctl["no_alarm_disjoint_pairs"]["ok"] and ctl["no_alarm_chain_contract_zero_def1"]["ok"]
    nl = res["null_random_classifiers_fully_justified"]
    print("NULL random classifiers fully justified: %d/%d (CIP-1 classifier: 351/351)" % (nl["good"], nl["trials"]))
    ok &= nl["good"] == 0
    out = os.environ.get("CIP_RESULT_OUT")
    if out:
        with open(out, "w") as f:
            json.dump(res, f, indent=2, sort_keys=True)
        print("wrote", out)
    print("PARTITION_WITNESS_V1:", "GREEN" if ok else "RED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
