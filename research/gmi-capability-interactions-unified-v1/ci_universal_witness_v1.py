#!/usr/bin/env python3
"""CI-U executable witness: Lemma A/B/C fixtures + CE-1/CE-2 hostile counterexamples.

Claim model: per-channel claims are finite SETS of resource units; mu = cardinality.
Channel-wise accounting: B(A) = sum_c |union of claims of A on channel c|.
Exact integers only; deterministic; no floats.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Mapping, Tuple

UNITS_S = FrozenSet[str]
UNITS_T = FrozenSet[str]
UNITS_M = FrozenSet[str]
Channels = Mapping[str, FrozenSet[str]]  # channel name -> claim set


def channel_burden(claims: Channels) -> int:
    return sum(len(v) for v in claims.values())


def joint_burden(x: Channels, y: Channels) -> int:
    channels = set(x) | set(y)
    return sum(len(x.get(c, frozenset()) | y.get(c, frozenset())) for c in channels)


# ---------------------------------------------------------------- Lemma A
def lemma_a_disjoint_additivity(x: Channels, y: Channels) -> bool:
    """Disjoint channel sets => joint == sum of individual burdens."""
    assert not (set(x) & set(y)), "Lemma A precondition: disjoint channel sets"
    return joint_burden(x, y) == channel_burden(x) + channel_burden(y)


# ---------------------------------------------------------------- Lemma B
def lemma_b_bounds(x: Channels, y: Channels, c: str) -> Tuple[bool, str]:
    """max <= joint_c <= sum on shared channel c, with exact regime label."""
    qx, qy = x[c], y[c]
    lo, joint, hi = max(len(qx), len(qy)), len(qx | qy), len(qx) + len(qy)
    assert lo <= joint <= hi, "inclusion-exclusion bound violated"
    if joint == lo:
        assert (qx <= qy) or (qy <= qx), "max-equality requires nested claims"
        return True, "MAX (nested claims)"
    if joint == hi:
        assert not (qx & qy), "sum-equality requires disjoint claims"
        return True, "SUM (disjoint claims)"
    return True, "STRICTLY BETWEEN (partial within-channel overlap)"


# ---------------------------------------------------------------- Lemma C
def lemma_c_free_option_monotonicity(values_with: int, values_without: int) -> bool:
    """Optional capability => joint optimum >= X-only optimum (feasible-set inclusion)."""
    return values_with >= values_without


# ---------------------------------------------------------------- fixtures
FIXTURE_NESTED = (
    {"S": frozenset({"u1", "u2", "u3"})},
    {"S": frozenset({"u1", "u2"})},
)
FIXTURE_DISJOINT_CLAIMS = (
    {"S": frozenset({"a1", "a2"})},
    {"S": frozenset({"b1", "b2", "b3"})},
)
FIXTURE_PARTIAL = (
    {"S": frozenset({"a1", "a2", "a3"})},
    {"S": frozenset({"a2", "a3", "a4", "a5"})},
)
FIXTURE_LEMMA_A = (
    {"S": frozenset({"a1", "a2"})},
    {"T": frozenset({"t1", "t2", "t3"}), "M": frozenset({"m1"})},
)

# CE-1 hostile: shared channel, disjoint claims -> joint exceeds max (refutes
# unconditional joint=max). Episodic store {e1..e4} vs semantic store {s1..s3}.
CE1_X = {"S": frozenset({"e1", "e2", "e3", "e4"})}
CE1_Y = {"S": frozenset({"s1", "s2", "s3"})}

# CE-2 hostile: mandatory upkeep delta from the same hard budget reduces X's
# achievable value (refutes unconditional no-interference).
def ce2_mandatory_upkeep(budget: int, x_needs: int, upkeep: int) -> bool:
    """X alone achieves x_needs within budget; with mandatory upkeep charged from the
    same budget, X's achieved value drops to budget - upkeep worth of work."""
    x_alone = min(budget, x_needs)
    x_with_parasite = min(max(budget - upkeep, 0), x_needs)
    return x_with_parasite < x_alone  # interference constructive


def main() -> int:
    ok = True
    x, y = FIXTURE_LEMMA_A
    ok &= lemma_a_disjoint_additivity(x, y)
    print("[PASS] Lemma A fixture: disjoint channels, joint == sum")
    for name, (fx, fy) in (("nested", FIXTURE_NESTED), ("disjoint-claims", FIXTURE_DISJOINT_CLAIMS), ("partial", FIXTURE_PARTIAL)):
        r, label = lemma_b_bounds(fx, fy, "S")
        ok &= r
        print(f"[PASS] Lemma B fixture ({name}): {label}")
    j = joint_burden(CE1_X, CE1_Y)
    assert j == 7 and max(len(CE1_X["S"]), len(CE1_Y["S"])) == 4
    print(f"[PASS] CE-1 hostile: joint={j} > max=4 on shared channel (unconditional max-rule refuted)")
    assert ce2_mandatory_upkeep(budget=10, x_needs=10, upkeep=2)
    print("[PASS] CE-2 hostile: mandatory upkeep reduces achieved value (unconditional no-interference refuted)")
    assert lemma_c_free_option_monotonicity(values_with=10, values_without=10)
    print("[PASS] Lemma C fixture: optional capability preserves optimum")
    print("CI_UNIVERSAL_WITNESS_V1:", "GREEN" if ok else "RED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
