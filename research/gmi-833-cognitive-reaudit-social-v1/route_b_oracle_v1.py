#!/usr/bin/env python3
"""Route B: independent brute-force oracle for the #833 Section-M social tranche.

This module deliberately knows **none** of the analytic results it is used to
check. It contains no threshold, no closed form, no backward induction, no
refinement-value decomposition and no `a* = g / (1 - phi)` fixed point. Every
quantity it reports is obtained by exhaustive enumeration over the registered
policy space or by direct iteration of the registered recursion.

It imports only `registered_scopes_v1`, which is pure data construction. It does
not import `cognitive_reaudit_social_v1`, so the two routes share no decision
logic.

Exact arithmetic only.
"""

from __future__ import annotations

from fractions import Fraction as F
from itertools import product
from typing import Dict, List, Sequence, Tuple

import registered_scopes_v1 as scopes


# --------------------------------------------------------------------------
# MC-1 route B: exhaustive enumeration over every stop/continue policy
# --------------------------------------------------------------------------

def _policy_value(scope: Dict[str, object], policy: Dict[Tuple[int, ...], bool]) -> F:
    """Expected exact net value of one fixed stop/continue policy."""
    node_value = scope["node_value"]
    price = scope["price"]
    prob = scope["prob"]
    depth = scope["depth"]
    branch = scope["branch"]

    def walk(path: Tuple[int, ...], best: F) -> F:
        best2 = best if best >= node_value[path] else node_value[path]
        if len(path) == depth or not policy[path]:
            return best2
        total = F(0)
        for outcome in range(branch):
            total += prob[outcome] * walk(path + (outcome,), best2)
        return total - price[path]

    return walk((), F(0))


def brute_force_best_allocation(scope: Dict[str, object]) -> Tuple[F, Tuple[Tuple[Tuple[int, ...], bool], ...]]:
    """Enumerate every policy; return the exact optimum and the lexicographically
    first optimal policy under the registered stop-on-tie ordering.

    The registered tie rule is `stop on ties`, so policies are enumerated with
    `False` (stop) before `True` (continue) at every decision node and the first
    attaining policy is kept.
    """
    decisions = scopes.delib_decision_paths(scope["depth"], scope["branch"])
    best_value = None  # type: object
    best_policy = None  # type: object
    for flags in product((False, True), repeat=len(decisions)):
        policy = dict(zip(decisions, flags))
        value = _policy_value(scope, policy)
        if best_value is None or value > best_value:
            best_value = value
            best_policy = tuple(sorted(policy.items()))
    return best_value, best_policy


def brute_force_reachable_trace(
    scope: Dict[str, object],
    policy: Dict[Tuple[int, ...], bool],
) -> Tuple[Tuple[Tuple[int, ...], bool], ...]:
    """The externally visible allocation trace: the decisions actually taken on
    nodes the policy actually reaches. Unreached decisions emit nothing, because
    nothing is externally charged there."""
    depth = scope["depth"]
    branch = scope["branch"]
    seen = []  # type: List[Tuple[Tuple[int, ...], bool]]

    def walk(path: Tuple[int, ...]) -> None:
        if len(path) == depth:
            return
        decision = policy[path]
        seen.append((path, decision))
        if decision:
            for outcome in range(branch):
                walk(path + (outcome,))

    walk(())
    return tuple(seen)


def brute_force_all_matching_schedules(
    instance_scopes: Dict[str, Dict[str, object]],
    observed: Dict[str, Tuple[Tuple[Tuple[int, ...], bool], ...]],
) -> List[Dict[str, Tuple[Tuple[Tuple[int, ...], bool], ...]]]:
    """Exhaustively enumerate EVERY fixed schedule over the registered instance
    set and return those that reproduce `observed` trace-for-trace.

    A fixed schedule carries no internal estimate: it is any assignment of one
    registered allocation trace to each registered instance label. The registered
    trace alphabet is the set of traces realizable by some policy on that
    instance, so the enumeration is over `prod_i |traces(i)|` schedules and is
    exhaustive, not sampled.
    """
    labels = sorted(instance_scopes)
    alphabets = []  # type: List[List[Tuple[Tuple[Tuple[int, ...], bool], ...]]]
    for label in labels:
        scope = instance_scopes[label]
        decisions = scopes.delib_decision_paths(scope["depth"], scope["branch"])
        traces = []
        for flags in product((False, True), repeat=len(decisions)):
            trace = brute_force_reachable_trace(scope, dict(zip(decisions, flags)))
            if trace not in traces:
                traces.append(trace)
        alphabets.append(traces)
    matches = []
    for assignment in product(*alphabets):
        schedule = dict(zip(labels, assignment))
        if all(schedule[label] == observed[label] for label in labels):
            matches.append(schedule)
    return matches


def brute_force_schedule_space_size(instance_scopes: Dict[str, Dict[str, object]]) -> int:
    total = 1
    for label in sorted(instance_scopes):
        scope = instance_scopes[label]
        decisions = scopes.delib_decision_paths(scope["depth"], scope["branch"])
        traces = set()
        for flags in product((False, True), repeat=len(decisions)):
            traces.add(brute_force_reachable_trace(scope, dict(zip(decisions, flags))))
        total *= len(traces)
    return total


# --------------------------------------------------------------------------
# MC-2 route B: exhaustive enumeration over every policy of each measurability
# --------------------------------------------------------------------------

def _expected_score(
    prior: Sequence[F],
    score: Sequence[Sequence[F]],
    action_of_state: Sequence[int],
) -> F:
    total = F(0)
    for state, weight in enumerate(prior):
        total += weight * score[state][action_of_state[state]]
    return total


def brute_force_channel_value(ecology: Dict[str, object]) -> F:
    """Best achievable exact score over ALL policies measurable in the other
    agent's observed-action channel: enumerate every function block -> action."""
    prior = ecology["prior"]
    score = ecology["score"]
    channel = ecology["channel"]
    n_actions = ecology["n_actions"]
    n_blocks = max(channel) + 1
    best = None  # type: object
    for assignment in product(range(n_actions), repeat=n_blocks):
        action_of_state = [assignment[channel[h]] for h in range(len(prior))]
        value = _expected_score(prior, score, action_of_state)
        if best is None or value > best:
            best = value
    return best


def brute_force_hidden_value(ecology: Dict[str, object]) -> F:
    """Best achievable exact score over ALL policies measurable in the other
    agent's hidden state: enumerate every function hidden state -> action."""
    prior = ecology["prior"]
    score = ecology["score"]
    n_actions = ecology["n_actions"]
    best = None  # type: object
    for assignment in product(range(n_actions), repeat=len(prior)):
        value = _expected_score(prior, score, list(assignment))
        if best is None or value > best:
            best = value
    return best


# --------------------------------------------------------------------------
# MC-3 route B: exhaustive enumeration over every receiver policy
# --------------------------------------------------------------------------

def brute_force_partition_value(
    prior: Sequence[F],
    score: Sequence[Sequence[F]],
    partition: Sequence[int],
    n_actions: int,
) -> F:
    n_blocks = max(partition) + 1
    best = None  # type: object
    for assignment in product(range(n_actions), repeat=n_blocks):
        action_of_state = [assignment[partition[s]] for s in range(len(prior))]
        value = _expected_score(prior, score, action_of_state)
        if best is None or value > best:
            best = value
    return best


def brute_force_silent_value(ecology: Dict[str, object]) -> F:
    """No channel: the receiver sees one undifferentiated block."""
    prior = ecology["prior"]
    trivial = tuple(0 for _ in prior)
    return brute_force_partition_value(prior, ecology["score"], trivial, ecology["n_actions"])

def brute_force_channel_partition_value(ecology: Dict[str, object]) -> F:
    return brute_force_partition_value(
        ecology["prior"], ecology["score"], ecology["partition"], ecology["n_actions"]
    )


def brute_force_shared_observation_value(ecology: Dict[str, object]) -> F:
    """Both parties see the sender's observation directly; no channel is used."""
    prior = ecology["prior"]
    finest = tuple(range(len(prior)))
    return brute_force_partition_value(prior, ecology["score"], finest, ecology["n_actions"])


def brute_force_channel_strictly_pays(ecology: Dict[str, object]) -> bool:
    gain = brute_force_channel_partition_value(ecology) - brute_force_silent_value(ecology)
    return gain > ecology["price"]


def brute_force_constant_action_is_blockwise_optimal(ecology: Dict[str, object]) -> bool:
    """Is some SINGLE action simultaneously optimal in every block?

    Enumerated directly: for each candidate action, check block by block whether
    it attains that block's brute-forced maximum."""
    prior = ecology["prior"]
    score = ecology["score"]
    partition = ecology["partition"]
    n_actions = ecology["n_actions"]
    n_blocks = max(partition) + 1
    for candidate in range(n_actions):
        ok = True
        for block in range(n_blocks):
            members = [s for s in range(len(prior)) if partition[s] == block]
            block_best = None  # type: object
            for action in range(n_actions):
                value = F(0)
                for s in members:
                    value += prior[s] * score[s][action]
                if block_best is None or value > block_best:
                    block_best = value
            candidate_value = F(0)
            for s in members:
                candidate_value += prior[s] * score[s][candidate]
            if candidate_value != block_best:
                ok = False
                break
        if ok:
            return True
    return False


# --------------------------------------------------------------------------
# MC-4 route B: direct total-charge comparison and direct cell classification
# --------------------------------------------------------------------------

def brute_force_totals(instance: Dict[str, object]) -> Tuple[F, F]:
    """(total charge with the demonstration, total charge without it)."""
    learners = instance["learners"]
    with_demo = instance["demonstrator"] + learners * instance["learner_demo"]
    without_demo = learners * instance["learner_control"]
    return with_demo, without_demo


def brute_force_teaching_worthwhile(instance: Dict[str, object]) -> bool:
    with_demo, without_demo = brute_force_totals(instance)
    return with_demo < without_demo


def brute_force_free_labour_worthwhile(instance: Dict[str, object]) -> bool:
    """The same comparison with the demonstrator's charge erased from the
    lifecycle vector (the free-labour accounting error)."""
    learners = instance["learners"]
    with_demo = learners * instance["learner_demo"]
    without_demo = learners * instance["learner_control"]
    return with_demo < without_demo


def brute_force_cell(instance: Dict[str, object]) -> Tuple[bool, bool]:
    """(imitation observed, demonstrator paid) by direct comparison."""
    imitation = instance["learner_demo"] < instance["learner_control"]
    paid = instance["demonstrator"] > F(0)
    return imitation, paid


# --------------------------------------------------------------------------
# MC-5 route B: direct iteration of the registered recursion
# --------------------------------------------------------------------------

def brute_force_trajectory(phi: F, g: F, a0: F, generations: int) -> Tuple[F, ...]:
    """Iterate a_{n+1} = phi * a_n + g in exact rationals. No fixed point, no
    closed form, no classification."""
    out = [a0]
    current = a0
    for _ in range(generations):
        current = phi * current + g
        out.append(current)
    return tuple(out)


def brute_force_ratchet_flags(trajectory: Sequence[F]) -> Tuple[bool, ...]:
    """Generation-by-generation strict increase, read straight off the iterated
    trajectory."""
    return tuple(
        trajectory[n + 1] > trajectory[n] for n in range(len(trajectory) - 1)
    )


def brute_force_rederivation_twin(trajectory: Sequence[F], generations: int) -> Tuple[F, ...]:
    """A zero-transmission population whose per-generation re-derivation budget
    is set to the target level. Iterated with phi = 0; no algebra is used."""
    budgets = list(trajectory[1:])
    out = [trajectory[0]]
    current = trajectory[0]
    for n in range(generations):
        current = F(0) * current + budgets[n]
        out.append(current)
    return tuple(out)


def brute_force_costs(
    trajectory: Sequence[F],
    phi: F,
    g: F,
    unit_transmit: F,
    unit_rederive: F,
    unit_innovate: F,
) -> Tuple[Tuple[F, ...], Tuple[F, ...]]:
    """Per-generation charged cost of the transmitting population and of its
    zero-transmission re-deriving twin, computed directly."""
    transmitting = []
    rederiving = []
    for n in range(len(trajectory) - 1):
        retained = phi * trajectory[n]
        transmitting.append(unit_transmit * retained + unit_innovate * g)
        rederiving.append(unit_rederive * trajectory[n + 1])
    return tuple(transmitting), tuple(rederiving)


def _subtree_policy_value(
    scope: Dict[str, object],
    root_path: Tuple[int, ...],
    incoming_best: F,
    policy: Dict[Tuple[int, ...], bool],
) -> F:
    """Exact expected net value of a policy evaluated from an interior node."""
    node_value = scope["node_value"]
    price = scope["price"]
    prob = scope["prob"]
    depth = scope["depth"]
    branch = scope["branch"]

    def walk(path: Tuple[int, ...], best: F) -> F:
        best2 = best if best >= node_value[path] else node_value[path]
        if len(path) == depth or not policy[path]:
            return best2
        total = F(0)
        for outcome in range(branch):
            total += prob[outcome] * walk(path + (outcome,), best2)
        return total - price[path]

    return walk(root_path, incoming_best)


def brute_force_myopic_step_worth(
    scope: Dict[str, object],
    path: Tuple[int, ...],
    incoming_best: F,
) -> Tuple[bool, F, F]:
    """Is exactly one further charged step worth its price at this node?

    Decided by directly evaluating the two concrete policies -- `stop here` and
    `take exactly one step, then stop` -- and comparing their exact expected net
    values. No threshold formula is used.
    """
    decisions = scopes.delib_decision_paths(scope["depth"], scope["branch"])
    stop_policy = dict((d, False) for d in decisions)
    one_step_policy = dict((d, False) for d in decisions)
    one_step_policy[path] = True
    stop_value = _subtree_policy_value(scope, path, incoming_best, stop_policy)
    step_value = _subtree_policy_value(scope, path, incoming_best, one_step_policy)
    return (step_value > stop_value, stop_value, step_value)


def brute_force_retained_best(scope: Dict[str, object], path: Tuple[int, ...]) -> F:
    """The value the system has already secured on the way to this node."""
    node_value = scope["node_value"]
    best = F(0)
    for cut in range(len(path) + 1):
        candidate = node_value[path[:cut]]
        if candidate > best:
            best = candidate
    return best


def brute_force_schedules_matching_trace_sets(
    instance_scopes: Dict[str, Dict[str, object]],
    observed_sets: Dict[str, List[Tuple[Tuple[Tuple[int, ...], bool], ...]]],
) -> List[Dict[str, Tuple[Tuple[Tuple[int, ...], bool], ...]]]:
    """Exhaustively enumerate EVERY fixed schedule and keep those reproducing the
    observed trace SET on every label.

    A fixed schedule emits exactly one trace per label, so it reproduces an
    observed set trace-for-trace only when that set is a singleton equal to the
    scheduled trace. This is the enumeration that decides the latent-draw
    boundary without assuming anything about it.
    """
    labels = sorted(instance_scopes)
    alphabets = []  # type: List[List[Tuple[Tuple[Tuple[int, ...], bool], ...]]]
    for label in labels:
        scope = instance_scopes[label]
        decisions = scopes.delib_decision_paths(scope["depth"], scope["branch"])
        traces = []
        for flags in product((False, True), repeat=len(decisions)):
            trace = brute_force_reachable_trace(scope, dict(zip(decisions, flags)))
            if trace not in traces:
                traces.append(trace)
        alphabets.append(traces)
    matches = []
    for assignment in product(*alphabets):
        schedule = dict(zip(labels, assignment))
        ok = True
        for label in labels:
            observed = observed_sets[label]
            distinct = []
            for trace in observed:
                if trace not in distinct:
                    distinct.append(trace)
            if len(distinct) != 1 or distinct[0] != schedule[label]:
                ok = False
                break
        if ok:
            matches.append(schedule)
    return matches
