"""Independent blockwise minimax and finite policy-certificate oracle.

Imports no decision implementation. The decomposition requires unrestricted
policies and the same nonempty action set available in every signal block.
"""
from fractions import Fraction
from itertools import product


def partitions(size):
    """Restricted-growth generation: canonical partitions without an outcome table."""
    if size == 0:
        return ((),)
    prefixes = [(0,)]
    for _ in range(size - 1):
        prefixes = [prefix + (label,) for prefix in prefixes
                    for label in range(max(prefix) + 2)]
    return tuple(prefixes)


def blocks(signal):
    labels = dict.fromkeys(signal)
    return tuple(frozenset(i for i, value in enumerate(signal) if value == label)
                 for label in labels)


def refinement(fine, coarse):
    coarse_blocks = blocks(coarse)
    return all(any(fibre <= other for other in coarse_blocks) for fibre in blocks(fine))


def blockwise_minimax(losses, signal, actions=None):
    actions = tuple(range(len(losses[0]))) if actions is None else tuple(actions)
    return max(min(max(Fraction(losses[world][action]) for world in fibre)
                   for action in actions) for fibre in blocks(signal))


def all_policies(signal, action_count):
    labels = tuple(dict.fromkeys(signal))
    return tuple(dict(zip(labels, choice))
                 for choice in product(range(action_count), repeat=len(labels)))


def policy_profile(losses, signal, policy):
    return tuple(Fraction(row[policy[label]]) for row, label in zip(losses, signal))


def separating_losses(fine, coarse):
    """Derive a binary-action separation from the first broken refinement pair."""
    for fibre in blocks(fine):
        for i, j in product(sorted(fibre), repeat=2):
            if coarse[i] != coarse[j]:
                # Every coarse cell has a perfect action, but this fine cell
                # contains worlds requiring both actions.
                desired = tuple(int(label != coarse[i]) for label in coarse)
                return tuple(tuple(int(action != wanted) for action in (0, 1))
                             for wanted in desired)
    raise ValueError("refinement has no separating witness")


def certificate_is_valid(losses, signal, result):
    """Check feasibility, attainment and an independently computed lower bound."""
    try:
        if type(result) is not dict or not {"value", "policy"} <= set(result):
            return False
        value, policy = result["value"], result["policy"]
        if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
            return False
        if type(policy) is not dict or set(policy) != set(signal):
            return False
        if any(type(label) not in (int, str) for label in policy):
            return False
        if any(type(action) is not int or not 0 <= action < len(losses[0])
               for action in policy.values()):
            return False
        return value == max(policy_profile(losses, signal, policy)) == blockwise_minimax(losses, signal)
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def randomized_worst_expected(losses, action_probabilities):
    """World chosen before the private random draw; not realized-action minimax."""
    return max(sum(Fraction(loss) * probability for loss, probability
                   in zip(row, action_probabilities)) for row in losses)
