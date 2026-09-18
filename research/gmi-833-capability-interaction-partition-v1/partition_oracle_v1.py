#!/usr/bin/env python3
"""ROUTE B + ROUTE C oracle for the corrected 27x27 capability-interaction census.

Materially independent of partition_witness_v1.py:
  * its OWN transcription of the A4 channel table (never imported);
  * burdens computed by explicit list de-duplication loops, no set algebra;
  * classification by a SIGN-VECTOR lookup table, not an if/elif equality cascade;
  * ROUTE C recomputes the same census in CLOSED FORM from the five distinct channel
    signatures, with no per-pair enumeration at all.

This file imports nothing from the main executor and nothing from
interactions_witness.py. Exact integers only. Stdlib only.
Run: python3 -I -B partition_oracle_v1.py
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# ROUTE B data: independent transcription of the A4 contract's channel usage.
# Written as ordered strings, not sets. test_partition_v1 asserts this table is
# identical to Route A's and to the shipped interactions_witness.RESOURCE_CHANNELS.
# ---------------------------------------------------------------------------
A4_TABLE: List[Tuple[str, str]] = [
    ("cap-perception", "ST"),
    ("cap-selective-attention", "ST"),
    ("cap-working-memory", "ST"),
    ("cap-episodic-memory", "ST"),
    ("cap-semantic-memory", "ST"),
    ("cap-procedural-memory", "ST"),
    ("cap-retrieval", "STM"),
    ("cap-consolidation", "ST"),
    ("cap-forgetting", "ST"),
    ("cap-prediction", "ST"),
    ("cap-abstraction-concept", "ST"),
    ("cap-compositional-reasoning", "ST"),
    ("cap-hierarchical-skill", "ST"),
    ("cap-planning", "ST"),
    ("cap-exploration", "ST"),
    ("cap-causal-inference", "T"),
    ("cap-counterfactual-reasoning", "ST"),
    ("cap-metacognition", "T"),
    ("cap-social-cognition", "ST"),
    ("cap-communication", "SM"),
    ("cap-imitation", "T"),
    ("cap-teaching", "TM"),
    ("cap-cultural-accumulation", "ST"),
    ("cap-self-modeling", "ST"),
    ("cap-self-improvement", "T"),
    ("cap-tool-use", "STM"),
    ("cap-coordination", "SM"),
]


# ---------------------------------------------------------------------------
# ROUTE B burden arithmetic: explicit list de-duplication, no set operations.
# The A4 accounting registers every channel as fully shareable: all capabilities
# using channel c claim the SAME unit of c, named "unit-<c>".
# ---------------------------------------------------------------------------

def claim_units(signature: str) -> List[str]:
    out: List[str] = []
    for ch in signature:
        out.append("unit-" + ch)
    return out


def dedup_count(units: List[str]) -> int:
    seen: List[str] = []
    for u in units:
        found = False
        for v in seen:
            if v == u:
                found = True
                break
        if not found:
            seen.append(u)
    return len(seen)


def burden_of(signature: str) -> int:
    return dedup_count(claim_units(signature))


def joint_burden_of(sig_x: str, sig_y: str) -> int:
    both: List[str] = []
    for u in claim_units(sig_x):
        both.append(u)
    for u in claim_units(sig_y):
        both.append(u)
    return dedup_count(both)


# ---------------------------------------------------------------------------
# ROUTE B decision procedure: sign-vector lookup.
#   v1 = sgn(joint - max),  v2 = sgn(joint - sum)
# ---------------------------------------------------------------------------

def sgn(a: int) -> int:
    if a < 0:
        return -1
    if a > 0:
        return 1
    return 0


SIGN_TABLE: Dict[Tuple[int, int], str] = {
    (0, -1): "REDUNDANT",        # joint == max  < sum   (strict saving, full sharing)
    (0, 0): "INDEPENDENT",       # joint == max == sum   (degenerate: zero-burden partner)
    (0, 1): "UNREACHABLE",       # joint == max  > sum   (needs max > sum: impossible for
                                 #                        non-negative burdens)
    (1, -1): "PARTIAL_SHARING",  # max < joint < sum
    (1, 0): "INDEPENDENT",       # max < joint == sum
    (1, 1): "INTERFERING",       # max < joint  > sum
}


def oracle_class(b_x: int, b_y: int, joint: int) -> Optional[str]:
    if b_x < 0 or b_y < 0:
        return None
    m = b_x if b_x > b_y else b_y
    s = b_x + b_y
    v = (sgn(joint - m), sgn(joint - s))
    if v[0] == -1:
        return None  # inadmissible: violates monotonicity axiom (M)
    k = SIGN_TABLE[v]
    if k == "UNREACHABLE":
        raise AssertionError("max > sum with non-negative burdens: %s" % (v,))
    return k


# ---------------------------------------------------------------------------
# ROUTE B census
# ---------------------------------------------------------------------------

def route_b_census() -> Dict[str, object]:
    counts: Dict[str, int] = {"INDEPENDENT": 0, "REDUNDANT": 0,
                              "PARTIAL_SHARING": 0, "INTERFERING": 0}
    rows: List[Dict[str, object]] = []
    n = len(A4_TABLE)
    for i in range(n):
        for j in range(i + 1, n):
            xid, xs = A4_TABLE[i]
            yid, ys = A4_TABLE[j]
            bx, by = burden_of(xs), burden_of(ys)
            jt = joint_burden_of(xs, ys)
            k = oracle_class(bx, by, jt)
            assert k is not None, "inadmissible A4 pair %s %s" % (xid, yid)
            counts[k] += 1
            rows.append({"x": xid, "y": yid, "B_x": bx, "B_y": by,
                         "joint": jt, "sum": bx + by, "max": max(bx, by),
                         "corrected_class": k})
    return {"pairs": len(rows), "counts": counts, "rows": rows}


# ---------------------------------------------------------------------------
# ROUTE C: closed form over the five distinct channel signatures. No per-pair
# enumeration; a pure combinatorial count. Catches an off-by-one that both
# enumeration routes could share.
# ---------------------------------------------------------------------------

def route_c_closed_form() -> Dict[str, object]:
    tally: Dict[str, int] = {}
    for _, sig in A4_TABLE:
        key = "".join(sorted(sig))
        tally[key] = tally.get(key, 0) + 1
    sigs = sorted(tally)

    def as_chars(s: str) -> List[str]:
        return [c for c in s]

    def inter_size(a: str, b: str) -> int:
        n = 0
        for c in as_chars(a):
            for d in as_chars(b):
                if c == d:
                    n += 1
                    break
        return n

    def relation(a: str, b: str) -> str:
        ia = inter_size(a, b)
        if ia == 0:
            return "disjoint"
        if a == b:
            return "equal"
        if ia == len(a) or ia == len(b):
            return "nested-proper"
        return "non-nested-overlap"

    # class as a function of the relation, proved in CIP-3
    rel_to_class = {
        "disjoint": "INDEPENDENT",
        "equal": "REDUNDANT",
        "nested-proper": "REDUNDANT",
        "non-nested-overlap": "PARTIAL_SHARING",
    }
    counts: Dict[str, int] = {"INDEPENDENT": 0, "REDUNDANT": 0,
                              "PARTIAL_SHARING": 0, "INTERFERING": 0}
    rel_counts: Dict[str, int] = {}
    total = 0
    for ai in range(len(sigs)):
        for bi in range(ai, len(sigs)):
            a, b = sigs[ai], sigs[bi]
            na, nb = tally[a], tally[b]
            if ai == bi:
                npairs = na * (na - 1) // 2
            else:
                npairs = na * nb
            if npairs == 0:
                continue
            rel = relation(a, b)
            rel_counts[rel] = rel_counts.get(rel, 0) + npairs
            counts[rel_to_class[rel]] += npairs
            total += npairs
    return {"signature_tally": tally, "pairs": total,
            "relation_counts": rel_counts, "counts": counts}


def main() -> int:
    b = route_b_census()
    c = route_c_closed_form()
    ok = True
    print("=== ROUTE B (independent enumeration oracle) ===")
    print("pairs: %d  counts: %s" % (b["pairs"], b["counts"]))
    print("=== ROUTE C (closed-form combinatorial) ===")
    print("signature tally: %s" % (c["signature_tally"],))
    print("pairs: %d  relations: %s" % (c["pairs"], c["relation_counts"]))
    print("counts: %s" % (c["counts"],))
    ok &= b["pairs"] == 351 and c["pairs"] == 351
    ok &= b["counts"] == c["counts"]
    print("ROUTE_B == ROUTE_C :", b["counts"] == c["counts"])
    out = os.environ.get("CIP_ORACLE_OUT")
    if out:
        with open(out, "w") as f:
            json.dump({"route_b": b, "route_c": c}, f, indent=2, sort_keys=True)
        print("wrote", out)
    print("PARTITION_ORACLE_V1:", "GREEN" if ok else "RED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
