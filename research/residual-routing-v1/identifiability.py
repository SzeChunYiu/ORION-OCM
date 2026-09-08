"""R0-D4: the counterfactual-identifiability audit.

#152 forbids inferring untried operator outcomes from incumbent traces, and lists
four admissible identification routes.  This study needs none of the risky ones,
for a reason that is itself the central finding:

    ``compose_stage`` has no ``break``.  It composes every structurally applicable
    candidate whose warrant and input atoms are live.  ``check_stage`` has no
    ``break`` either: it checks every composed candidate.  Only ``decide`` selects,
    and it selects ``passed[0]``.

So on every query the incumbent already executes and checks every admissible
alternative.  There are no untried actions to infer.  The counterfactual "what
would operator ``j`` have produced" is answered by the incumbent's own trace,
exactly, for every ``j`` -- which is route 3 of #152, an exact finite reference,
obtained at zero additional cost and with zero additional side effects.

This is a strong identification position and a weak routing position, and both
follow from the same fact. A policy that only reorders cannot change what work is
done, because the work is a sum over a set the order does not change. The only
transformation that can reduce work is one that stops early, and stopping early
is not routing -- it needs no scores, no features and no learner.

The audit below records that argument as a check rather than a claim: it verifies
against the harvested records that no candidate is ever left unexecuted, so the
identification route is established by the data and not only by reading the code.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

ROUTE = "EXACT_FINITE_REFERENCE_FROM_EXHAUSTIVE_INCUMBENT_EXECUTION"


def audit(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    checked, unchecked, ragged = 0, 0, []
    for r in records:
        verdicts = r["incumbent_order_and_choice"]["verdicts"]
        if not verdicts:
            unchecked += 1
            continue
        if any(v == "PENDING" for v in verdicts):
            ragged.append(r["source"])
            continue
        if len(verdicts) != r["A_admissible_count"]:
            ragged.append(r["source"])
            continue
        checked += 1
    total = len(records)
    return {
        "route": ROUTE,
        "records": total,
        "records_with_every_admissible_candidate_checked": checked,
        "records_with_no_admissible_candidate": unchecked,
        "records_where_composition_did_not_reach_check": sorted(set(ragged)),
        "identified_fraction": (checked + unchecked) / total if total else 0.0,
        "why_no_off_policy_inference_is_needed": (
            "Every admissible candidate is composed and checked by the incumbent on every "
            "query, so no alternative is untried and nothing has to be inferred. The "
            "counterfactual outcome of every candidate is a recorded fact of the incumbent "
            "run."),
        "why_this_is_also_the_routing_problem": (
            "The same exhaustiveness that makes the counterfactual free makes the routing "
            "opportunity empty on the work coordinates: composition and verification work "
            "are sums over the admissible set, and a permutation does not change a sum. "
            "Δ(q) under any pure reordering is therefore identically zero, for every query, "
            "without measuring anything."),
        "what_would_break_this": (
            "An early-exiting runtime. If compose or check stopped at the first pass, the "
            "outcomes of later candidates would be genuinely unobserved and this study "
            "would fall to CANNOT_CHECK_COUNTERFACTUAL_OPERATOR_OUTCOMES unless it "
            "re-executed them, which for side-effecting backends it could not safely do."),
    }


def order_invariance_argument() -> dict[str, str]:
    """The theorem the audit rests on, stated so it can be checked against the source."""
    return {
        "claim": (
            "For any permutation pi of the admissible candidate sequence, the incumbent's "
            "composition_work and verification_calls are unchanged."),
        "proof": (
            "compose_stage iterates candidate_ops in order and appends to `candidates` "
            "with no early termination, accumulating ResourceVector(composition_work="
            "len(op.input_atoms), verification_calls=1) per candidate that composes. "
            "check_stage iterates `candidates` with no early termination and returns "
            "ResourceVector(verification_calls=len(checked)). Both totals are sums over "
            "the same finite set with order-independent summands, hence invariant under "
            "permutation."),
        "consequence": (
            "No reordering policy -- learned or otherwise -- can reduce incumbent work on "
            "these coordinates. Any router with positive inference cost strictly increases "
            "total work on every query."),
        "what_it_does_not_say": (
            "It says nothing about policies that CHANGE THE SET examined. Early exit "
            "removes candidates from the set and does reduce work; that is why this study "
            "measures it. Early exit is an exact policy and requires no learner."),
    }
