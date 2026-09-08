"""Finite exact Decision Region Determination / paid-cognition primitives.

Conventional decision theory only.  This module is intentionally independent of
DEV-5's implementation so the theorems can be unit-tested on hostile finite
examples before they are mapped back to the donor.
"""
from __future__ import annotations

from functools import lru_cache

from exact_numeric import _rational
from drd_model import prepare_model


INF = float("inf")


def common_actions(version, safe_actions):
    """Protected actions safe under every surviving hypothesis."""
    version = tuple(version)
    if not version:
        return frozenset()
    result = set(safe_actions[version[0]])
    for hypothesis in version[1:]:
        result.intersection_update(safe_actions[hypothesis])
    return frozenset(result)


def robust_stop_cost(version, safe_actions, action_cost):
    """Worst-case cost of the cheapest currently common protected action."""
    version = tuple(version)
    actions = common_actions(version, safe_actions)
    if not actions:
        return INF, None
    best = min(
        (
            max(_rational(action_cost[(hypothesis, action)]) for hypothesis in version),
            str(action),
            action,
        )
        for action in actions
    )
    return best[0], best[2]


def probe_partitions(version, outcomes, probe):
    """Partition a version space by one deterministic legal probe."""
    partitions = {}
    for hypothesis in version:
        outcome = outcomes[(probe, hypothesis)]
        partitions.setdefault(outcome, []).append(hypothesis)
    return tuple(
        (outcome, tuple(sorted(block)))
        for outcome, block in sorted(partitions.items(), key=lambda item: repr(item[0]))
    )


def solve_worst_case_drd(
    hypotheses,
    safe_actions,
    action_cost,
    probes,
    outcomes,
    probe_cost,
    *,
    identification_only=False,
):
    """Exact represented-rational optimum over finite terminating decision trees.

    Uninformative probes are omitted; other probes strictly shrink each branch.
    Nonnegative probe costs are checked before that omission. Exact ties retain
    STOP. Action costs may be signed and must be finite in the shared domain.

    With ``identification_only=True``, stopping is forbidden until one hypothesis
    remains.  Otherwise a common safe action may be taken at any version space,
    but the DP can still choose to probe when information is worth more than the
    cost of acting conservatively now.

    The mathematical policy is a normative exact parent.  If deployed as a table
    or solver, its own build/lookup/storage/update costs must be charged separately.
    """
    initial, safe_actions, action_cost, probes, outcomes, probe_cost = prepare_model(
        hypotheses, safe_actions, action_cost, probes, outcomes, probe_cost
    )

    @lru_cache(maxsize=None)
    def value(version):
        version = tuple(version)
        stop_value, stop_action = robust_stop_cost(version, safe_actions, action_cost)
        if identification_only and len(version) != 1:
            stop_value, stop_action = INF, None

        best_value = stop_value
        best_decision = ("stop", stop_action) if stop_action is not None else None

        for probe in probes:
            parts = probe_partitions(version, outcomes, probe)
            # An uninformative probe cannot improve a nonnegative-cost Bellman
            # problem and would create a self-loop in the recursion.
            if len(parts) <= 1:
                continue
            candidate = probe_cost[probe] + max(
                value(block)[0] for _outcome, block in parts
            )
            if candidate < best_value:
                best_value = candidate
                best_decision = ("probe", probe)

        if best_decision is None:
            raise ValueError("no finite protected policy exists for a reachable version space")
        return best_value, best_decision

    result = value(initial)
    policy = {version: value(version) for version in value.cache_info() and _reachable_versions(initial, probes, outcomes)}
    return {
        "value": result[0],
        "first_decision": result[1],
        "policy": policy,
    }


def _reachable_versions(initial, probes, outcomes):
    seen = set()
    stack = [tuple(initial)]
    while stack:
        version = stack.pop()
        if version in seen:
            continue
        seen.add(version)
        for probe in probes:
            parts = probe_partitions(version, outcomes, probe)
            if len(parts) > 1:
                stack.extend(block for _outcome, block in parts)
    return tuple(sorted(seen, key=lambda value: (len(value), value)))


def unanimous_verdict(version, verdict):
    """Return the common verdict, or None when survivors disagree."""
    version = tuple(version)
    if not version:
        return None
    first = verdict[version[0]]
    for hypothesis in version[1:]:
        if verdict[hypothesis] != first:
            return None
    return first


def condition_on_verdict(version, verdict, observed):
    return tuple(
        hypothesis for hypothesis in version if verdict[hypothesis] == observed
    )


def sequential_unanimity_cost(version, verdict, order=None):
    """Unit-cost exact evaluator for TRUE/FALSE/MIXED under a fixed order.

    Returns the result and number of hypothesis verdicts inspected.  The evaluator
    stops at the first disagreement.  If no disagreement occurs, all survivors
    must be inspected to certify unanimity.
    """
    version = tuple(version)
    if not version:
        return None, 0
    order = tuple(version if order is None else order)
    if set(order) != set(version) or len(order) != len(version):
        raise ValueError("order must be a permutation of the version space")
    first = verdict[order[0]]
    examined = 1
    for hypothesis in order[1:]:
        examined += 1
        if verdict[hypothesis] != first:
            return None, examined
    return first, examined


def fixed_order_unanimity_certificate(version, verdict, order=None):
    """Explain why sequential short-circuiting is pointwise minimal for this order.

    Before the first disagreement, a completion of the unseen suffix can still
    make the final result either unanimous or mixed.  Therefore no correct
    prefix-respecting evaluator can stop earlier.  On a unanimous input every
    element must be inspected.
    """
    result, examined = sequential_unanimity_cost(version, verdict, order)
    return {
        "result": result,
        "examined": examined,
        "minimum_for_fixed_prefix_order": examined,
        "reason": (
            "before the first disagreement the unseen suffix can change unanimous to mixed; "
            "if no disagreement exists every survivor is necessary to certify unanimity"
        ),
    }
