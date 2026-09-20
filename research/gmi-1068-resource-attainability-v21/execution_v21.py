"""Weighted execution and endpoints of the actual finite V8 resource lift."""
from functools import lru_cache
from core_v21 import budget_lift, nat, word_checked


def weighted_run(machine, start, word):
    word_checked(machine, start, word)
    state, spent = start, 0
    for action in word:
        edge = machine.transitions[state][action]
        if edge is None:
            return None
        _, cost, state = edge
        spent += cost
    return state, spent


@lru_cache(maxsize=128)
def _lift(machine, capacity):
    return budget_lift(machine, capacity)


def budget_endpoint(machine, start, word, budget):
    word_checked(machine, start, word)
    nat(budget)
    lifted = _lift(machine, budget)
    stride = budget + 1
    state = start * stride + budget
    for action in word:
        edge = lifted.transitions[state][action]
        if edge is None:
            return None
        state = edge[2]
    return divmod(state, stride)
