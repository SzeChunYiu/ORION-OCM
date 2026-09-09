"""POST-HOC analysis of the frozen R0 receipt. Declared as post-hoc, not evidence.

What this is and is not
-----------------------

`protocol.py` was frozen before scored execution and this file was written
AFTERWARDS, against data already published in
`results/RESIDUAL_ROUTING_OPPORTUNITY_V1.json`. It therefore carries none of the
authority of a pre-registered prediction. It changes no terminal, adds no
prediction, executes nothing, and computes only quantities derivable from the
receipt. It exists because the study named an open caveat and that caveat turns
out to be answerable from the data already collected.

The caveat, in the study's own words
------------------------------------

    "That the routing-specific residual is zero. It is zero here because the
    first admissible candidate passes on every answering query, which is
    plausibly an artifact of test fixtures supplying the intended operator
    first. A deployment ecology could place the passing candidate later, and
    then work WOULD be spent before the answer."

That diagnosis is wrong, and this file shows it is wrong using the receipt's own
rows. The residual is not zero because the fixtures got the order right. It is
zero because **no query in the population is mixed**: there is not one selection
point at which some admissible candidate passes and another does not. On all 24
answering single-passing queries |A^E| = 1, so there was never an order to get
lucky with in the first place.

Two consequences follow, and the second is the one worth having.

1. The adversarial bound. Reordering is answer-safe under contract C1 only where
   exactly one candidate passes; with two or more passing, reordering changes
   `chosen_operator_id` and leaves every registered contract. On the answer-safe
   subset, the worst ordering an adversary could choose puts every non-passing
   candidate before the passing one, costing exactly `total - chosen`. Summed
   over the subset this is the MAXIMUM routing-specific residual obtainable from
   these admissible sets under ANY ordering, not just the observed one. It is
   zero on both coordinates.

2. The precondition for #71. Routing is not merely unprofitable here, it is
   UNDEFINED here: the count of queries at which a router could prefer a passing
   candidate over a non-passing one is 0 of 96. That gives #71 a crisp thing to
   look for in any future ecology -- a selection point with |A^E| > 1 and a
   mixed verdict vector -- instead of the vague "a deployment ecology could
   place the passing candidate later".

This does not make the negative ecology-independent. A different workload could
produce mixed queries, and then the residual would have to be re-measured. What
it does is replace a speculative explanation with a measured one, and hand #71 a
checkable entry condition rather than a hunch.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

#: Reordering preserves `chosen_operator_id` only when at most one candidate
#: passes. With two or more, the first-pass semantics of `decide()` mean a
#: different order yields a different chosen operator, which contract C1
#: protects. Those queries are not opportunities; they are contract violations.
ANSWER_SAFE_MAX_PASSING = 1


def routing_is_definable(record: Mapping[str, Any]) -> bool:
    """Could a router even express a preference at this selection point?

    It could only if there is something to prefer: more than one admissible
    candidate, at least one that passes, and at least one that does not. Any
    other shape leaves nothing for a policy to decide.
    """
    admissible = record["A_admissible_count"]
    passing = record["passing_candidate_count"]
    return admissible > 1 and 0 < passing < admissible


def adversarial_residual(record: Mapping[str, Any]) -> dict[str, int] | None:
    """Worst-case routing-specific work over ALL orderings of this query.

    ``None`` where reordering is not answer-safe, so the query contributes
    nothing rather than being silently counted as zero.
    """
    if record["passing_candidate_count"] > ANSWER_SAFE_MAX_PASSING:
        return None
    split = record["work_split"]
    if not split.get("chosen_known") or record["passing_candidate_count"] == 0:
        return {"composition_work": 0, "verification_calls": 0}
    return {k: split["total"][k] - split["chosen"][k] for k in split["total"]}


def bound(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    contributing = [r for r in records if adversarial_residual(r) is not None]
    excluded = [r for r in records if adversarial_residual(r) is None]
    totals = {"composition_work": 0, "verification_calls": 0}
    for record in contributing:
        for k, v in adversarial_residual(record).items():
            totals[k] += v
    definable = [r for r in records if routing_is_definable(r)]
    shapes: dict[str, int] = {}
    for r in records:
        a, p = r["A_admissible_count"], r["passing_candidate_count"]
        key = ("at most one admissible candidate" if a <= 1 else
               "multiple admissible, none passing" if p == 0 else
               "multiple admissible, all passing" if p == a else
               "MIXED: some pass, some do not")
        shapes[key] = shapes.get(key, 0) + 1
    return {
        "analysis_status": "POST_HOC_ON_FROZEN_RECEIPT",
        "authority": (
            "Written after scored execution against published rows. Not a "
            "pre-registered prediction, changes no terminal, executes nothing."),
        "queries": len(records),
        "answer_safe_queries": len(contributing),
        "excluded_multiple_passing": len(excluded),
        "adversarial_routing_residual": totals,
        "worst_case_equals_observed": totals == {"composition_work": 0,
                                                 "verification_calls": 0},
        "queries_where_routing_is_definable": len(definable),
        "query_shapes": shapes,
        "corrects": (
            "The receipt attributed the zero residual to fixtures supplying the "
            "intended operator first, so that no work fell before the answer. "
            "That is not what the rows show. Every answering query with exactly "
            "one passing candidate has |A^E| = 1, so no ordering existed to be "
            "favourable, and the worst ordering of the recorded admissible sets "
            "yields the same zero. The residual is zero because the population "
            "contains no mixed query, not because the observed order was lucky."),
        "entry_condition_for_71": (
            "A selection point with |A^E| > 1 whose verdict vector is mixed -- "
            "at least one PASS and at least one non-PASS. There are 0 of these "
            "in 96 selection points. Until such a point exists, routing is not "
            "unprofitable, it is undefined, and no learner can be evaluated "
            "against it. This is the checkable condition #71 should test for "
            "before any further routing work, and it replaces the receipt's "
            "speculative 'a deployment ecology could place the passing candidate "
            "later'."),
        "what_this_still_does_not_establish": (
            "Ecology independence. A different workload could produce mixed "
            "queries and a positive residual. What is now established is that no "
            "REORDERING of this population can, which is a strictly stronger "
            "statement than the observed-order measurement it replaces."),
    }
