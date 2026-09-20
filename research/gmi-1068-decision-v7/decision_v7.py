"""Exact finite deterministic minimax decisions; no distribution over worlds."""
from collections.abc import Mapping
from fractions import Fraction
from itertools import product


def _exact(value, name):
    if type(value) not in (int, Fraction):
        raise ValueError(f"{name} must be an exact int or Fraction (not bool/float)")
    return Fraction(value)


def _signals(signal):
    if type(signal) not in (tuple, list) or not signal:
        raise ValueError("signal must be a nonempty finite tuple/list")
    for label in signal:
        if type(label) not in (int, str):
            raise ValueError("signal labels must be exact ints or strings")
    return tuple(signal)


def _labels(signal):
    return tuple(dict.fromkeys(signal))


def validate_problem(losses, signal):
    """Rows are worlds, columns are actions; signed exact losses are allowed."""
    signal = _signals(signal)
    if type(losses) not in (tuple, list) or not losses:
        raise ValueError("losses must be a nonempty finite matrix")
    if len(losses) != len(signal):
        raise ValueError("one signal label is required per world")
    rows = []
    width = None
    for row in losses:
        if type(row) not in (tuple, list) or not row:
            raise ValueError("loss rows must be nonempty finite tuple/list values")
        if width is None:
            width = len(row)
        if len(row) != width:
            raise ValueError("loss matrix must be rectangular")
        rows.append(tuple(_exact(v, "loss") for v in row))
    return tuple(rows), signal


def _policy(policy, labels, action_count):
    if type(action_count) is not int or action_count < 1:
        raise ValueError("action_count must be a positive exact integer")
    if not isinstance(policy, Mapping):
        raise ValueError("policy must map every observed label to an action")
    for label, action in policy.items():
        if type(label) not in (int, str):
            raise ValueError("policy labels must be exact ints or strings")
        if type(action) is not int or not 0 <= action < action_count:
            raise ValueError("policy action must be an in-range exact integer")
    if set(policy) != set(labels):
        raise ValueError("policy domain must equal the observed label set")
    return {label: policy[label] for label in labels}


def policy_profile(losses, signal, policy):
    rows, signal = validate_problem(losses, signal)
    policy = _policy(policy, _labels(signal), len(rows[0]))
    return tuple(row[policy[label]] for row, label in zip(rows, signal))


def minimax(losses, signal, *, allowed_actions=None, policies=None):
    """Exhaust every admitted deterministic policy, returning its evaluation count."""
    rows, signal = validate_problem(losses, signal)
    labels, action_count = _labels(signal), len(rows[0])
    if allowed_actions is None:
        actions = tuple(range(action_count))
    else:
        if type(allowed_actions) not in (tuple, list) or not allowed_actions:
            raise ValueError("allowed_actions must be a nonempty finite tuple/list")
        for action in allowed_actions:
            if type(action) is not int or not 0 <= action < action_count:
                raise ValueError("allowed action must be an in-range exact integer")
        actions = tuple(allowed_actions)
        if len(set(actions)) != len(actions):
            raise ValueError("allowed_actions must contain distinct indices")
    if policies is None:
        candidates = (
            dict(zip(labels, choices))
            for choices in product(actions, repeat=len(labels))
        )
    else:
        if type(policies) not in (tuple, list) or not policies:
            raise ValueError("policies must be a nonempty finite tuple/list")
        candidates = policies
    best_value, best_policy, evaluated = None, None, 0
    for candidate in candidates:
        candidate = _policy(candidate, labels, action_count)
        if any(action not in actions for action in candidate.values()):
            raise ValueError("policy uses an unavailable action")
        value = max(row[candidate[label]] for row, label in zip(rows, signal))
        evaluated += 1
        if best_value is None or value < best_value:
            best_value, best_policy = value, candidate
    return {"value": best_value, "policy": best_policy, "policy_evaluations": evaluated}


def refinement_map(fine, coarse):
    """Return the induced coarse-label map, or None when refinement fails."""
    fine, coarse = _signals(fine), _signals(coarse)
    if len(fine) != len(coarse):
        raise ValueError("signals must describe the same nonempty world set")
    mapping = {}
    for observed, target in zip(fine, coarse):
        if observed in mapping and mapping[observed] != target:
            return None
        mapping[observed] = target
    return mapping


def refines(fine, coarse):
    return refinement_map(fine, coarse) is not None


def transport_policy(fine, coarse, coarse_policy, action_count):
    mapping = refinement_map(fine, coarse)
    if mapping is None:
        raise ValueError("fine signal does not refine the coarse signal")
    coarse = _signals(coarse)
    policy = _policy(coarse_policy, _labels(coarse), action_count)
    return {label: policy[target] for label, target in mapping.items()}


def separation_witness(fine, coarse):
    """Construct a binary loss separating every nonrefinement; no fixed templates."""
    mapping = refinement_map(fine, coarse)
    if mapping is not None:
        raise ValueError("a nonrefinement pair is required")
    fine, coarse = _signals(fine), _signals(coarse)
    pair = next(
        (i, j) for i in range(len(fine)) for j in range(i + 1, len(fine))
        if fine[i] == fine[j] and coarse[i] != coarse[j]
    )
    target_label = coarse[pair[1]]
    targets = tuple(int(label == target_label) for label in coarse)
    return {"merged_worlds": pair, "losses": tuple((z, 1 - z) for z in targets)}


def paid_information(coarse_value, fine_value, cost):
    """Compare paid fine-information value to coarse value, with smaller loss better."""
    coarse_value = _exact(coarse_value, "coarse_value")
    fine_value = _exact(fine_value, "fine_value")
    cost = _exact(cost, "cost")
    if cost < 0:
        raise ValueError("observation cost must be nonnegative")
    paid_value = fine_value + cost
    gain = coarse_value - paid_value
    classification = "IMPROVES" if gain > 0 else "WORSENS" if gain < 0 else "TIES"
    return {"classification": classification, "net_gain": gain, "paid_value": paid_value}
