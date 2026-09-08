"""Executable finite lemmas for FORMAL_DECISION_CORE_V2.md.

This module is deliberately small and stdlib-only.  It is not a production
router.  It keeps the finite identities used by the research note executable so
that future experiments cannot silently change the meaning of decision
sufficiency, feature regret, resource dominance, metalevel stopping, or
contract-bisimulation checks.
"""
from __future__ import annotations

from collections import defaultdict
from math import isclose


def common_actions(version, good_actions):
    """Return Gamma(V): protected actions common to every state in version."""
    version = tuple(version)
    if not version:
        raise ValueError("version must be nonempty")
    shared = set(good_actions[version[0]])
    for state in version[1:]:
        shared.intersection_update(good_actions[state])
    return frozenset(shared)


def decision_regions(states, actions, good_actions):
    """R_a = states in which action a is protected/acceptable."""
    return {
        action: frozenset(state for state in states if action in good_actions[state])
        for action in actions
    }


def contained_decision_actions(version, regions):
    """Actions whose decision region contains the whole version space."""
    version = frozenset(version)
    return frozenset(action for action, region in regions.items() if version <= region)


def optimal_actions(state, actions, costs):
    values = {action: costs[(state, action)] for action in actions}
    best = min(values.values())
    return frozenset(action for action, value in values.items() if value == best)


def feature_fibers(states, feature):
    buckets = defaultdict(list)
    for state in states:
        buckets[feature[state]].append(state)
    return {key: tuple(value) for key, value in buckets.items()}


def fiber_common_optima(states, actions, costs, feature):
    """Common optimal action set for each feature fiber."""
    result = {}
    for key, members in feature_fibers(states, feature).items():
        shared = set(actions)
        for state in members:
            shared.intersection_update(optimal_actions(state, actions, costs))
        result[key] = frozenset(shared)
    return result


def exact_feature_sufficient(states, actions, costs, feature):
    """Theorem 3 condition: every nonempty feature fiber has a common optimum."""
    return all(fiber_common_optima(states, actions, costs, feature).values())


def full_information_expected_cost(states, actions, costs, weights):
    return sum(weights[state] * min(costs[(state, action)] for action in actions)
               for state in states)


def best_feature_expected_cost(states, actions, costs, weights, feature):
    """Theorem 4 exact expected optimum among deterministic/randomized heads."""
    total = 0.0
    policy = {}
    for key, members in feature_fibers(states, feature).items():
        values = {
            action: sum(weights[state] * costs[(state, action)] for state in members)
            for action in actions
        }
        chosen = min(actions, key=lambda action: (values[action], repr(action)))
        policy[key] = chosen
        total += values[chosen]
    return total, policy


def feature_regret_floor(states, actions, costs, weights, feature):
    feature_cost, policy = best_feature_expected_cost(
        states, actions, costs, weights, feature
    )
    full_cost = full_information_expected_cost(states, actions, costs, weights)
    regret = feature_cost - full_cost
    if regret < 0 and isclose(regret, 0.0, abs_tol=1e-12):
        regret = 0.0
    if regret < 0:
        raise AssertionError("feature policy beat full information")
    return {
        "feature_cost": feature_cost,
        "full_information_cost": full_cost,
        "regret": regret,
        "policy": policy,
    }


def price_independent_dominates(cost_a, cost_b):
    """A <= B for every nonnegative scalarization iff componentwise A <= B."""
    if len(cost_a) != len(cost_b):
        raise ValueError("resource vectors must have equal dimension")
    return all(a <= b for a, b in zip(cost_a, cost_b))


def incomparable_price_witnesses(cost_a, cost_b):
    """Return unit-coordinate witnesses preferring A and B, if both exist."""
    if len(cost_a) != len(cost_b):
        raise ValueError("resource vectors must have equal dimension")
    a_wins = next((i for i, (a, b) in enumerate(zip(cost_a, cost_b)) if a < b), None)
    b_wins = next((i for i, (a, b) in enumerate(zip(cost_a, cost_b)) if b < a), None)
    return a_wins, b_wins


def local_gain_beats_overhead(method_a, overhead_a, method_b, overhead_b):
    """Lemma 13: method A yields a whole-machine win iff total cost is lower."""
    local_gain = method_b - method_a
    overhead_penalty = overhead_a - overhead_b
    return local_gain > overhead_penalty


def finite_meta_dp(states, stop_cost, cognitive_actions, action_cost, transitions, budget):
    """Theorem 9 finite paid-cognition dynamic program.

    transitions[(state, action)] is an iterable of (probability, next_state).
    `cognitive_actions[state]` may be empty.  Returns value/policy tables for all
    budgets 0..budget.  Policy value None means STOP.
    """
    if budget < 0:
        raise ValueError("budget must be nonnegative")
    states = tuple(states)
    values = [{state: float(stop_cost[state]) for state in states}]
    policies = [{state: None for state in states}]

    for remaining in range(1, budget + 1):
        previous = values[-1]
        current = {}
        current_policy = {}
        for state in states:
            best_cost = float(stop_cost[state])
            best_action = None
            for action in cognitive_actions[state]:
                outcomes = tuple(transitions[(state, action)])
                probability = sum(prob for prob, _ in outcomes)
                if not isclose(probability, 1.0, rel_tol=1e-12, abs_tol=1e-12):
                    raise ValueError("transition probabilities must sum to one")
                candidate = float(action_cost[(state, action)]) + sum(
                    prob * previous[next_state] for prob, next_state in outcomes
                )
                if candidate < best_cost:
                    best_cost = candidate
                    best_action = action
            current[state] = best_cost
            current_policy[state] = best_action
        values.append(current)
        policies.append(current_policy)
    return values, policies


def is_contract_bisimulation(states, actions_by_state, contract, transitions, block_of):
    """Check the exact finite protected-contract bisimulation conditions.

    `contract[(s,a)]` may be any equality-comparable tuple (output, authority,
    raw resource vector, etc.).  `transitions[(s,a)]` is (prob,next_state).
    """
    blocks = defaultdict(list)
    for state in states:
        blocks[block_of[state]].append(state)

    for members in blocks.values():
        reference = members[0]
        reference_actions = tuple(actions_by_state[reference])
        for state in members[1:]:
            if tuple(actions_by_state[state]) != reference_actions:
                return False
        for action in reference_actions:
            reference_contract = contract[(reference, action)]
            reference_mass = _block_transition_mass(
                transitions[(reference, action)], block_of
            )
            for state in members[1:]:
                if contract[(state, action)] != reference_contract:
                    return False
                if not _mass_equal(
                    reference_mass,
                    _block_transition_mass(transitions[(state, action)], block_of),
                ):
                    return False
    return True


def _block_transition_mass(outcomes, block_of):
    mass = defaultdict(float)
    total = 0.0
    for probability, next_state in outcomes:
        mass[block_of[next_state]] += probability
        total += probability
    if not isclose(total, 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError("transition probabilities must sum to one")
    return dict(mass)


def _mass_equal(left, right):
    keys = set(left) | set(right)
    return all(isclose(left.get(key, 0.0), right.get(key, 0.0),
                       rel_tol=1e-12, abs_tol=1e-12)
               for key in keys)


def prune_dominated_slopes(slopes):
    """Pareto-prune (setup, recurring, payload) options for Theorem 15 audits."""
    result = []
    for index, slope in enumerate(slopes):
        setup, recurring, _ = slope
        dominated = False
        for other_index, other in enumerate(slopes):
            if index == other_index:
                continue
            other_setup, other_recurring, _ = other
            if (other_setup <= setup and other_recurring <= recurring
                    and (other_setup < setup or other_recurring < recurring)):
                dominated = True
                break
        if not dominated:
            result.append(slope)
    return tuple(sorted(result, key=lambda item: (item[0], -item[1], repr(item[2]))))


def multislope_monotone(slopes):
    """After pruning, setup must increase while recurring rate decreases."""
    for left, right in zip(slopes, slopes[1:]):
        if not (left[0] < right[0] and left[1] > right[1]):
            return False
    return True
