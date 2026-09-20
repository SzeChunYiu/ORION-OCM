"""Greatest same-word forward simulation for finite deterministic partial actions."""
from dataclasses import dataclass
from core_v20 import index, nat, need, order, relation, subset
from frontier_v20 import representatives


@dataclass(frozen=True)
class Machine:
    base: tuple
    transitions: tuple
    actions: int

    def __post_init__(self):
        order(self.base)
        nat(self.actions)
        size = len(self.base)
        need(type(self.transitions) is tuple and len(self.transitions) == size,
             "transition state dimension")
        for row in self.transitions:
            need(type(row) is tuple and len(row) == self.actions, "transition action dimension")
            for value in row:
                if value is not None:
                    index(value, size)


def checked(machine):
    need(type(machine) is Machine, "validated Machine required")
    return machine


def word_indices(machine, word):
    need(type(word) is tuple, "word tuple required")
    for action in word:
        index(action, machine.actions)
    return word


def run(machine, state, word):
    checked(machine)
    index(state, len(machine.base))
    word_indices(machine, word)
    for action in word:
        if state is None:
            return None
        state = machine.transitions[state][action]
    return state


def refine(machine):
    checked(machine)
    current = machine.base
    size = len(current)
    checks = deleted = 0
    while True:
        checks += 1
        updated = tuple(tuple(current[x][y] and all(
            machine.transitions[x][a] is None or
            (machine.transitions[y][a] is not None
             and current[machine.transitions[x][a]][machine.transitions[y][a]])
            for a in range(machine.actions)) for y in range(size)) for x in range(size))
        if updated == current:
            return current, checks, deleted
        deleted += sum(current[x][y] and not updated[x][y]
                       for x in range(size) for y in range(size))
        current = updated


def greatest(machine):
    return refine(machine)[0]


def is_simulation(machine, candidate):
    checked(machine)
    size = len(machine.base)
    candidate = relation(candidate, size)
    return all(not candidate[x][y] or (machine.base[x][y] and all(
        machine.transitions[x][a] is None or
        (machine.transitions[y][a] is not None
         and candidate[machine.transitions[x][a]][machine.transitions[y][a]])
        for a in range(machine.actions))) for x in range(size) for y in range(size))


def prune(machine, states):
    checked(machine)
    subset(states, len(machine.base))
    return representatives(greatest(machine), states)


def endpoints(machine, states, word):
    checked(machine)
    states = subset(states, len(machine.base))
    word_indices(machine, word)
    result = {run(machine, state, word) for state in states}
    return tuple(sorted(state for state in result if state is not None))
