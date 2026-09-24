#!/usr/bin/env python3
"""Route A: registered search procedures and their canonical traces (D-X3).

* S3 `BEST_FIRST_CERTIFICATE` is new in #859: a min-heap over the 146 compressed
  risk points keyed by the admissible lower bound LB3(x) = b*ed + c*s (it drops
  only the nonnegative a*en term), accept-on-optimality-certificate, with a
  mandatory tie sweep (points whose LB3 equals the incumbent are still
  evaluated, so the complete argmin set is returned).
* S1 (#901 FULL_ENUMERATION) and S2 (#901 RISK_FRONTIER_BRANCH_BOUND) are
  executed by #901's own code for their conclusions.  Their canonical traces
  are reconstructed here from their declared exploration orders (S1: census
  order; S2: the #901 sort key and strict lower-bound pruning) and validated
  against #901's returned counters by the executor.
* H3a `FIRST_ACCEPT_PRICE_SORTED` is the registered early-stopping hostile: S2's
  order, first evaluated point accepted, no certificate.
* H3b is the registered re-encoding masquerade: S2 run over re-labelled point
  ids, declared as a third procedure.

Canonical trace = ordered list of rho = (s, en, ed) of every evaluated item.
Acceptance sequence = one letter per evaluated item: N (new incumbent),
T (tie with incumbent), R (rejected).  Digest formats (route B reproduces them
byte-for-byte without importing this module):

    trace digest      sha256(json.dumps([[s,en,ed], ...], separators=(",",":")))[:16]
    acceptance digest sha256("".join(letters).encode("ascii"))[:16]

Exact rationals only; stdlib only; this module imports no other package module.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import heapq
import json
from typing import Any, Dict, List, Sequence, Tuple

Rho = Tuple[int, int, int]
Weights = Tuple[Fraction, Fraction, Fraction]  # on (en, ed, s)

DIFFERENCE_TABLES: Dict[str, Dict[str, str]] = {
    "S1_FULL_ENUMERATION": {
        "representation": "raw 65,552 candidates",
        "exploration_order": "census enumeration order",
        "pruning": "none",
        "acceptance_termination": "full-scan exact argmin plus tie set",
        "completeness_proof": "construction (evaluates every candidate)",
        "search_cost_unit": "candidate evaluations (65,552 per world)",
    },
    "S2_RISK_FRONTIER_BRANCH_BOUND": {
        "representation": "compressed 146 risk points",
        "exploration_order": "price-sorted order",
        "pruning": "admissible lower bound lambda*s (strict)",
        "acceptance_termination": "incumbent update plus tie set",
        "completeness_proof": "admissibility theorem",
        "search_cost_unit": "evaluated points (pruned reported)",
    },
    "S3_BEST_FIRST_CERTIFICATE": {
        "representation": "compressed 146 risk points",
        "exploration_order": "min-heap by admissible lower bound b*ed + c*s",
        "pruning": "none (early stop by certificate)",
        "acceptance_termination": "accept-on-optimality-certificate plus mandatory tie sweep",
        "completeness_proof": "dominance certificate plus tie sweep theorem",
        "search_cost_unit": "evaluations until certificate",
    },
    "H3A_FIRST_ACCEPT_PRICE_SORTED": {
        "representation": "compressed 146 risk points",
        "exploration_order": "price-sorted order",
        "pruning": "stop after the first evaluation",
        "acceptance_termination": "first-accept, no certificate",
        "completeness_proof": "none (explicitly incomplete)",
        "search_cost_unit": "one evaluation",
    },
    # the masquerade DECLARES two differing axes; the mechanical certificate
    # (identical canonical traces and acceptance sequences) must reject it
    "H3B_REENCODED_BRANCH_BOUND": {
        "representation": "re-labelled risk-point ids",
        "exploration_order": "id-keyed order",
        "pruning": "admissible lower bound lambda*s (strict)",
        "acceptance_termination": "incumbent update plus tie set",
        "completeness_proof": "admissibility theorem",
        "search_cost_unit": "evaluated points (pruned reported)",
    },
}


def value(rho: Rho, w: Weights) -> Fraction:
    s, en, ed = rho
    a, b, c = w
    return a * en + b * ed + c * s


def trace_digest(trace: Sequence[Rho]) -> str:
    raw = json.dumps([[int(s), int(en), int(ed)] for s, en, ed in trace], separators=(",", ":"))
    return hashlib.sha256(raw.encode("ascii")).hexdigest()[:16]


def acceptance_digest(letters: Sequence[str]) -> str:
    return hashlib.sha256("".join(letters).encode("ascii")).hexdigest()[:16]


def _scan(order: Sequence[Rho], w: Weights) -> Tuple[Fraction, List[Rho], List[str]]:
    best = None
    winners: List[Rho] = []
    letters: List[str] = []
    for rho in order:
        v = value(rho, w)
        if best is None or v < best:
            best, winners = v, [rho]
            letters.append("N")
        elif v == best:
            winners.append(rho)
            letters.append("T")
        else:
            letters.append("R")
    if best is None:
        raise ValueError("empty order")
    return best, winners, letters


def s1_run(census_rhos: Sequence[Rho], w: Weights) -> Dict[str, Any]:
    """S1 canonical trace: every candidate in census order."""
    best, winners, letters = _scan(census_rhos, w)
    return {"best": best, "winner_rhos": sorted(set(winners)), "winner_count": len(winners),
            "acceptance": letters, "evaluations": len(census_rhos)}


def s2_order(points: Sequence[Rho], price: Fraction) -> List[Rho]:
    """The #901 S2 exploration order (its declared sort key)."""
    return sorted(points, key=lambda z: (price * z[0], z[1] + z[2], z[0], z[1], z[2]))


def s2_run(points: Sequence[Rho], w: Weights) -> Dict[str, Any]:
    price = w[2]
    best = None
    winners: List[Rho] = []
    trace: List[Rho] = []
    letters: List[str] = []
    pruned: List[Rho] = []
    for rho in s2_order(points, price):
        lower = price * rho[0]
        if best is not None and lower > best:
            pruned.append(rho)
            continue
        v = value(rho, w)
        trace.append(rho)
        if best is None or v < best:
            best, winners = v, [rho]
            letters.append("N")
        elif v == best:
            winners.append(rho)
            letters.append("T")
        else:
            letters.append("R")
    if best is None:
        raise ValueError("empty frontier")
    certificate = all(price * r[0] > best for r in pruned) and len(pruned) + len(trace) == len(points)
    return {"best": best, "winner_rhos": sorted(winners), "trace": trace, "acceptance": letters,
            "evaluated_points": len(trace), "pruned_points": len(pruned), "certificate_verified": certificate}


def s3_run(points: Sequence[Rho], w: Weights) -> Dict[str, Any]:
    a, b, c = w

    def lb3(rho: Rho) -> Fraction:
        return b * rho[2] + c * rho[0]

    heap = [(lb3(r), r) for r in points]
    heapq.heapify(heap)
    best = None
    winners: List[Rho] = []
    trace: List[Rho] = []
    letters: List[str] = []
    while heap and (best is None or heap[0][0] <= best):
        _, rho = heapq.heappop(heap)
        v = value(rho, w)
        trace.append(rho)
        if best is None or v < best:
            best, winners = v, [rho]
            letters.append("N")
        elif v == best:
            winners.append(rho)
            letters.append("T")
        else:
            letters.append("R")
    if best is None:
        raise ValueError("empty frontier")
    remaining = [r for _, r in heap]
    admissible = all(lb3(r) <= value(r, w) for r in points)
    certificate = admissible and all(lb3(r) > best for r in remaining)
    return {"best": best, "winner_rhos": sorted(winners), "trace": trace, "acceptance": letters,
            "evaluations": len(trace), "pushes": len(points), "left_unevaluated": len(remaining),
            "certificate_verified": certificate,
            "certificate": {"incumbent": best, "min_remaining_lower_bound": min((lb3(r) for r in remaining), default=None)}}


def h3a_run(points: Sequence[Rho], w: Weights) -> Dict[str, Any]:
    first = s2_order(points, w[2])[0]
    return {"best": value(first, w), "winner_rhos": [first], "trace": [first], "acceptance": ["N"],
            "evaluations": 1, "certificate_verified": False}


def h3b_run(labelled_points: Sequence[Tuple[str, Rho]], w: Weights) -> Dict[str, Any]:
    """S2 over re-labelled ids; the canonical trace maps ids back to rho."""
    back = {pid: rho for pid, rho in labelled_points}
    if len(back) != len(labelled_points):
        raise ValueError("re-labelling is not injective")
    price = w[2]
    ordered = sorted(labelled_points, key=lambda z: (price * z[1][0], z[1][1] + z[1][2], z[1][0], z[1][1], z[1][2]))
    best = None
    winners: List[str] = []
    trace_ids: List[str] = []
    letters: List[str] = []
    pruned: List[Rho] = []
    for pid, rho in ordered:
        if best is not None and price * rho[0] > best:
            pruned.append(rho)
            continue
        v = value(rho, w)
        trace_ids.append(pid)
        if best is None or v < best:
            best, winners = v, [pid]
            letters.append("N")
        elif v == best:
            winners.append(pid)
            letters.append("T")
        else:
            letters.append("R")
    if best is None:
        raise ValueError("empty frontier")
    return {"best": best, "winner_rhos": sorted(back[x] for x in winners), "trace": [back[x] for x in trace_ids],
            "acceptance": letters, "evaluated_points": len(trace_ids), "pruned_points": len(pruned),
            "certificate_verified": all(price * r[0] > best for r in pruned) and len(pruned) + len(trace_ids) == len(labelled_points)}
