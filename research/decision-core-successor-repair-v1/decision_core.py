"""Executable finite lemmas for FORMAL_DECISION_CORE_V2.md.

Exact numeric domain: built-in int, Fraction, and finite built-in float.
Floats mean their exact stored binary rational, not an intended decimal or
arbitrary real. Numeric results use Fraction. NaN/infinity/bool/other numeric
types are rejected. Kernel/weight normalization is exact; no renormalization.

Inputs are finite, stable collections/mappings with hashable state/action IDs.
Iterables are materialized before reuse. None is reserved for STOP in meta-DP.
Contracts must have deterministic literal equality; they are not scalar costs.
This finite reference helper does not certify source costs or policy-model
adequacy, unbounded stopping, protected-action legality, or lifecycle coverage.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from math import isfinite


def _rational(value):
    if type(value) not in (int, Fraction, float):
        raise TypeError("numeric input must be int, Fraction, or finite float")
    if type(value) is float and not isfinite(value):
        raise ValueError("numeric input must be finite")
    return Fraction(value)


def _items(values, name, allow_empty=False):
    values = tuple(values)
    if len(set(values)) != len(values) or (not values and not allow_empty):
        raise ValueError(name + " must contain distinct IDs and be nonempty")
    return values


def _probabilities(values):
    values = tuple(_rational(value) for value in values)
    if any(value < 0 or value > 1 for value in values) or sum(values) != 1:
        raise ValueError("probabilities must be nonnegative and sum exactly to one")
    return values


def _weighted_problem(states, actions, costs, weights):
    states, actions = _items(states, "states"), _items(actions, "actions")
    probabilities = _probabilities(weights[state] for state in states)
    exact_costs = {(s, a): _rational(costs[s, a]) for s in states for a in actions}
    return states, actions, exact_costs, dict(zip(states, probabilities))


def _model(states, actions_by_state, transitions):
    states = _items(states, "states")
    state_set = set(states)
    actions = {s: _items(actions_by_state[s], "actions", True) for s in states}
    kernels = {}
    for state in states:
        for action in actions[state]:
            outcomes = tuple(transitions[state, action])
            probabilities = _probabilities(p for p, _ in outcomes)
            if any(successor not in state_set for _, successor in outcomes):
                raise ValueError("transition successor is outside the supplied state space")
            kernels[state, action] = tuple(zip(probabilities, (s for _, s in outcomes)))
    return states, actions, kernels


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
    states, actions = tuple(states), tuple(actions)
    acceptable = {state: frozenset(good_actions[state]) for state in states}
    return {
        action: frozenset(state for state in states if action in acceptable[state])
        for action in actions
    }


def contained_decision_actions(version, regions):
    """Actions whose decision region contains the whole version space."""
    version = frozenset(version)
    return frozenset(action for action, region in regions.items() if version <= region)


def optimal_actions(state, actions, costs):
    actions = _items(actions, "actions")
    values = {action: _rational(costs[state, action]) for action in actions}
    best = min(values.values())
    return frozenset(action for action, value in values.items() if value == best)


def feature_fibers(states, feature):
    buckets = defaultdict(list)
    for state in states:
        buckets[feature[state]].append(state)
    return {key: tuple(value) for key, value in buckets.items()}


def fiber_common_optima(states, actions, costs, feature):
    """Common optimal action set for each feature fiber."""
    states, actions = _items(states, "states"), _items(actions, "actions")
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
    states, actions, costs, weights = _weighted_problem(states, actions, costs, weights)
    return sum((weights[state] * min(costs[state, action] for action in actions)
                for state in states), Fraction())


def best_feature_expected_cost(states, actions, costs, weights, feature):
    """Theorem 4 optimum over the supplied exact rational decision problem."""
    states, actions, costs, weights = _weighted_problem(states, actions, costs, weights)
    total = Fraction()
    policy = {}
    for key, members in feature_fibers(states, feature).items():
        values = {
            action: sum(weights[state] * costs[state, action] for state in members)
            for action in actions
        }
        chosen = min(actions, key=lambda action: (values[action], repr(action)))
        policy[key] = chosen
        total += values[chosen]
    return total, policy


def feature_regret_floor(states, actions, costs, weights, feature):
    states, actions = tuple(states), tuple(actions)
    feature_cost, policy = best_feature_expected_cost(
        states, actions, costs, weights, feature
    )
    full_cost = full_information_expected_cost(states, actions, costs, weights)
    regret = feature_cost - full_cost
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
    cost_a, cost_b = tuple(map(_rational, cost_a)), tuple(map(_rational, cost_b))
    if len(cost_a) != len(cost_b):
        raise ValueError("resource vectors must have equal dimension")
    return all(a <= b for a, b in zip(cost_a, cost_b))


def incomparable_price_witnesses(cost_a, cost_b):
    """Return unit-coordinate witnesses preferring A and B, if both exist."""
    cost_a, cost_b = tuple(map(_rational, cost_a)), tuple(map(_rational, cost_b))
    if len(cost_a) != len(cost_b):
        raise ValueError("resource vectors must have equal dimension")
    a_wins = next((i for i, (a, b) in enumerate(zip(cost_a, cost_b)) if a < b), None)
    b_wins = next((i for i, (a, b) in enumerate(zip(cost_a, cost_b)) if b < a), None)
    return a_wins, b_wins


def local_gain_beats_overhead(method_a, overhead_a, method_b, overhead_b):
    """Lemma 13: method A yields a whole-machine win iff total cost is lower."""
    local_gain = _rational(method_b) - _rational(method_a)
    overhead_penalty = _rational(overhead_a) - _rational(overhead_b)
    return local_gain > overhead_penalty


def finite_meta_dp(states, stop_cost, cognitive_actions, action_cost, transitions, budget):
    """Theorem 9 for a finite model with at most budget cognitive actions.

    Every transition consumes one step; at zero, STOP is mandatory.
    Costs use the module's rational domain; cognitive costs must be nonnegative.
    Kernels are validated even for budget zero. Each iterable is consumed once.
    Returns exact value/policy tables; None means STOP and wins exact ties.
    """
    if type(budget) is not int:
        raise TypeError("budget must be a built-in integer")
    if budget < 0:
        raise ValueError("budget must be nonnegative")
    states, actions, kernels = _model(states, cognitive_actions, transitions)
    stop = {s: _rational(stop_cost[s]) for s in states}
    costs = {}
    for state in states:
        for action in actions[state]:
            if action is None:
                raise ValueError("None is reserved for STOP")
            cost = _rational(action_cost[state, action])
            if cost < 0:
                raise ValueError("cognitive costs must be nonnegative")
            costs[state, action] = cost
    values, policies = [stop.copy()], [{s: None for s in states}]
    for remaining in range(1, budget + 1):
        previous = values[-1]
        current, current_policy = {}, {}
        for state in states:
            best_cost, best_action = stop[state], None
            for action in actions[state]:
                candidate = costs[state, action] + sum(
                    prob * previous[next_state] for prob, next_state in kernels[state, action]
                )
                if candidate < best_cost:
                    best_cost, best_action = candidate, action
            current[state], current_policy[state] = best_cost, best_action
        values.append(current)
        policies.append(current_policy)
    return values, policies


def is_contract_bisimulation(states, actions_by_state, contract, transitions, block_of):
    """Check exact finite contract equality and successor block probabilities.

    Actions are sets of distinct IDs; their iteration order is irrelevant.
    Contract values must have deterministic equality semantics. Numeric kernels
    use the module's rational domain. All supplied kernels are validated first.
    Only supplied action contracts are checked; a separate meta-DP STOP is not.
    Combined use must also preserve stop outputs/costs within each block.
    """
    states, actions, kernels = _model(states, actions_by_state, transitions)
    blocks = defaultdict(list)
    for state in states:
        blocks[block_of[state]].append(state)
    for members in blocks.values():
        reference = members[0]
        reference_actions = frozenset(actions[reference])
        if any(frozenset(actions[state]) != reference_actions for state in members[1:]):
            return False
        for action in actions[reference]:
            reference_contract = contract[reference, action]
            reference_mass = _block_transition_mass(kernels[reference, action], block_of)
            for state in members[1:]:
                if contract[state, action] != reference_contract:
                    return False
                if reference_mass != _block_transition_mass(kernels[state, action], block_of):
                    return False
    return True


def _block_transition_mass(outcomes, block_of):
    """Aggregate already validated rational kernels; zero masses are omitted."""
    mass = defaultdict(Fraction)
    for probability, next_state in outcomes:
        if probability:
            mass[block_of[next_state]] += probability
    return dict(mass)


def prune_dominated_slopes(slopes):
    """Pareto-prune (setup, recurring, payload) options for Theorem 15 audits."""
    slopes = tuple((_rational(b), _rational(r), payload) for b, r, payload in slopes)
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
    slopes = tuple((_rational(b), _rational(r), payload) for b, r, payload in slopes)
    return all(left[0] < right[0] and left[1] > right[1]
               for left, right in zip(slopes, slopes[1:]))
