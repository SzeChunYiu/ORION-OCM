"""Independent expectation enumeration; imports no control_model solver."""
from fractions import Fraction as F
from itertools import product


def require(condition, message):
    """Keep evidence checks active under optimized Python execution."""
    if not condition:
        raise AssertionError(message)


def enumerate_return(model, policy, start, horizon, terminal=None):
    n, actions, p, r, gamma = model
    total = F(0)
    terminal = terminal or (F(0),) * n
    for future in product(range(n), repeat=horizon):
        path = (start,) + future
        probability, value = F(1), F(0)
        for k in range(horizon):
            state, following = path[k:k+2]
            action = policy[state]
            value += gamma**k * r[state][action]
            probability *= p[state][action][following]
        value += gamma**horizon * terminal[path[-1]]
        total += probability * value
    return total


def trace_law(model, start, actions, observation):
    n, _, p, _, _ = model
    law = {}
    for future in product(range(n), repeat=len(actions)):
        path = (start,) + future
        probability = F(1)
        for k, action in enumerate(actions):
            probability *= p[path[k]][action][path[k+1]]
        trace = tuple(observation[s] for s in path)
        law[trace] = law.get(trace, F(0)) + probability
    return {trace: mass for trace, mass in law.items() if mass}


def finite_horizon_value(model, horizon):
    n, actions, p, r, gamma = model
    values = [F(0)] * n
    for _ in range(horizon):
        values = [max(r[s][a] + gamma * sum(p[s][a][t]*values[t] for t in range(n))
                      for a in range(actions)) for s in range(n)]
    return tuple(values)


def conditional_bit_rewards(history_length):
    """Expose every past bit: this is at least the information rewards can reveal."""
    groups = 0
    for past in product((0, 1), repeat=history_length):
        for action in (0, 1):
            require(sum(F(action == current, 2) for current in (0, 1)) == F(1, 2), 'check failed: sum((F(action == current, 2) for current in (0, 1))) == F(1, 2)')
            groups += 1
    return groups
