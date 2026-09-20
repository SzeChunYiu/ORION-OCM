"""Actual edge gating and state/action-sensitive permission accumulation."""
from core_v22 import LegacyMachine, permissions, spec_checked, word_checked


def gate(spec, enabled):
    allowed = permissions(spec, enabled)
    rows = tuple(tuple(
        edge if edge is not None and set(spec.requirements[s][a]) <= allowed else None
        for a, edge in enumerate(row))
        for s, row in enumerate(spec.base.transitions))
    return LegacyMachine(spec.base.observations, rows)


def support(spec, start, word):
    spec_checked(spec)
    word_checked(spec.base, start, word)
    state, required = start, set()
    for action in word:
        edge = spec.base.transitions[state][action]
        if edge is None:
            return None
        required.update(spec.requirements[state][action])
        state = edge[2]
    return state, tuple(sorted(required))
