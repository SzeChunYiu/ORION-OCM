"""Derived quantities for RESIDUAL_ROUTING_OPPORTUNITY_V1.

The decomposition this module exists for
----------------------------------------

The incumbent composes and checks every admissible candidate and then answers
with ``passed[0]``.  So on a query whose admissible sequence is
``c_0 ... c_{n-1}`` with first pass at index ``f``, the total work splits into
three parts, and only one of them is a routing opportunity:

    BEFORE   work on c_0 .. c_{f-1}   -- candidates examined and not used
    CHOSEN   work on c_f              -- the answer, irreducible
    AFTER    work on c_{f+1} .. c_n-1 -- examined after the answer was already found

``AFTER`` is recoverable by stopping at the first pass. That requires no scores,
no features and no learner: it is an exact policy, and under the C1 contract it
returns an identical decision, answer and chosen operator.

``BEFORE`` is the only part a router could claim. Recovering it means putting a
passing candidate first, which requires knowing which candidate passes before
checking it -- exactly what a learned proposal policy would predict. It is
therefore the residual routing opportunity, and it is realisable only where
reordering is answer-safe, which under ``decide``'s ``passed[0]`` semantics means
queries with at most one passing candidate.

Reporting ``AFTER + BEFORE`` as one number would be the central error available
here: it would credit a router with savings an exact early exit already takes.
"""
from __future__ import annotations

import math
import statistics
from collections import Counter
from typing import Any, Mapping, Sequence

COORDINATES = ("composition_work", "verification_calls")


def split_work(record: Mapping[str, Any]) -> dict[str, dict[str, int]]:
    order = record["incumbent_order_and_choice"]
    verdicts = order["verdicts"]
    f = order["first_passing_index"]
    per = record.get("per_candidate_work")
    if per is None:
        # reconstruct from the two totals the instrument stores
        total = record["incumbent_work_vector"]
        after = record["work_after_first_pass"]
        before = {c: 0 for c in COORDINATES}
        chosen = {c: 0 for c in COORDINATES}
        if f is not None:
            rest = {c: total[c] - after[c] for c in COORDINATES}
            # rest = BEFORE + CHOSEN; without per-candidate detail the split is
            # unavailable, so it is reported as a single bound rather than guessed
            return {"before_plus_chosen": rest, "after": dict(after),
                    "total": dict(total), "chosen_known": False}
        return {"before_plus_chosen": dict(total), "after": dict(after),
                "total": dict(total), "chosen_known": False}
    before = {c: sum(p[c] for p in per[:f]) for c in COORDINATES} if f else \
        {c: 0 for c in COORDINATES}
    chosen = {c: per[f][c] for c in COORDINATES} if f is not None else \
        {c: 0 for c in COORDINATES}
    after = {c: sum(p[c] for p in per[f + 1:]) for c in COORDINATES} if f is not None else \
        {c: 0 for c in COORDINATES}
    return {"before": before, "chosen": chosen, "after": after,
            "total": {c: before[c] + chosen[c] + after[c] for c in COORDINATES},
            "chosen_known": True}


def fano_lower_bound(m: int, k: int, epsilon: float) -> float | None:
    """List-decoding Fano bound on I(Z;X) for the uniform finite case.

    Returns None when the inequality is vacuous (m <= k means a top-k set can
    contain every candidate and no information is required)."""
    if m <= 1 or k >= m:
        return None
    h2 = 0.0 if epsilon in (0.0, 1.0) else -(
        epsilon * math.log2(epsilon) + (1 - epsilon) * math.log2(1 - epsilon))
    return (math.log2(m) - h2 - (1 - epsilon) * math.log2(k)
            - epsilon * math.log2(m - k))


def pc_parent(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The mandatory p/c diagnostic: static order by decreasing pass rate over cost.

    Estimated from the harvested population, per operator identity. This is the
    explicit parent #152 requires before any nonlinear routing claim, and it is
    the policy a router would have to beat rather than the incumbent."""
    passes: Counter = Counter()
    trials: Counter = Counter()
    cost: dict[str, int] = {}
    for r in records:
        order = r["incumbent_order_and_choice"]
        for op, verdict in zip(order["order"], order["verdicts"]):
            trials[op] += 1
            if verdict == "PASS":
                passes[op] += 1
    ratios = {op: (passes[op] / trials[op]) for op in trials}
    return {
        "distinct_operator_identities": len(trials),
        "operators_that_ever_pass": sum(1 for op in trials if passes[op]),
        "operators_that_never_pass": sum(1 for op in trials if not passes[op]),
        "pass_rate_is_degenerate": all(v in (0.0, 1.0) for v in ratios.values()),
        "note": (
            "Where every operator's empirical pass rate is 0 or 1, the static p/c order is "
            "determined without any learning: put the always-passing operators first. A "
            "learner cannot beat a rule that is already exact, and #152 requires reporting "
            "parent sufficiency rather than escalating model class when this holds."),
    }


def summarise(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    n = len(records)
    admissible = [r["A_admissible_count"] for r in records]
    passing = [r["passing_candidate_count"] for r in records]
    after = [r["work_after_first_pass"] for r in records]
    total = [r["incumbent_work_vector"] for r in records]

    multi = [r for r in records if r["A_admissible_count"] > 1]
    multi_pass = [r for r in records if r["passing_candidate_count"] > 1]
    exit_positive = [r for r in records
                     if any(r["work_after_first_pass"][c] > 0 for c in COORDINATES)]
    # BEFORE > 0 means the incumbent examined a non-passing candidate before its
    # answer; that is the only work a router could claim.
    route_positive = [r for r in records
                      if r["incumbent_order_and_choice"]["first_passing_index"] not in (None, 0)]
    route_safe = [r for r in route_positive if r["passing_candidate_count"] <= 1]

    def q(values, p):
        if not values:
            return None
        s = sorted(values)
        return s[min(len(s) - 1, int(p * (len(s) - 1)))]

    return {
        "queries": n,
        "distinct_sources": len({r["source"] for r in records}),
        "A_admissible_distribution": dict(Counter(admissible)),
        "passing_distribution": dict(Counter(passing)),
        "fraction_admissible_le_1": sum(1 for a in admissible if a <= 1) / n if n else 0.0,
        "fraction_admissible_gt_1": len(multi) / n if n else 0.0,
        "fraction_with_multiple_passing": len(multi_pass) / n if n else 0.0,
        "catalogue_sizes": dict(Counter(r["N_total"] for r in records)),
        "selection_modes": dict(Counter(r["selection_mode"] for r in records)),
        "exact_early_exit": {
            "queries_with_recoverable_work": len(exit_positive),
            "rho_exit": len(exit_positive) / n if n else 0.0,
            "total_composition_work": sum(a["composition_work"] for a in after),
            "total_verification_calls": sum(a["verification_calls"] for a in after),
            "median_verification_calls": q([a["verification_calls"] for a in after], 0.5),
            "p95_verification_calls": q([a["verification_calls"] for a in after], 0.95),
            "note": "recoverable by an exact policy with no learner, under contract C1",
        },
        "residual_routing": {
            "queries_where_a_non_passing_candidate_precedes_the_answer": len(route_positive),
            "of_which_reordering_is_answer_safe": len(route_safe),
            "rho_R": len(route_safe) / n if n else 0.0,
            "note": (
                "rho_R counts only queries where a router could BOTH save work and preserve "
                "the chosen operator. A query with two passing candidates is excluded "
                "because reordering there changes the answer under decide()'s passed[0] "
                "semantics, which is a selection-contract violation and not an opportunity."),
        },
        "incumbent_totals": {
            "composition_work": sum(t["composition_work"] for t in total),
            "verification_calls": sum(t["verification_calls"] for t in total),
        },
    }
