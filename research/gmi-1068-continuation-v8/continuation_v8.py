"""Complete finite continuation semantics for declared deterministic machines."""
from dataclasses import dataclass


def need(condition, message):
    if not condition:
        raise ValueError(message)


def nat(x):
    return type(x) is int and x >= 0


@dataclass(frozen=True)
class Machine:
    observations: tuple
    transitions: tuple

    def __post_init__(self):
        need(type(self.observations) is tuple and bool(self.observations),
             "nonempty tuple of observations required")
        n = len(self.observations)
        need(all(x is None or nat(x) for x in self.observations), "invalid observation")
        need(type(self.transitions) is tuple and len(self.transitions) == n,
             "transition rows must cover states")
        need(all(type(row) is tuple and bool(row) for row in self.transitions),
             "nonempty tuple rows required")
        width = len(self.transitions[0])
        need(all(len(row) == width for row in self.transitions), "ragged action set")
        for row in self.transitions:
            for edge in row:
                need(edge is None or
                     (type(edge) is tuple and len(edge) == 3 and
                      all(nat(v) for v in edge) and edge[2] < n), "invalid edge")


def run(machine, state, word, budget=None):
    """Every intermediate observation remains visible even after later failure."""
    need(isinstance(machine, Machine), "invalid machine")
    need(nat(state) and state < len(machine.observations), "invalid state")
    need(type(word) is tuple and all(nat(a) and a < len(machine.transitions[0])
                                    for a in word), "invalid word")
    need(budget is None or nat(budget), "invalid residual budget")
    response = [("OBS", machine.observations[state])]
    for action in word:
        edge = machine.transitions[state][action]
        if edge is None or (budget is not None and edge[1] > budget):
            response.append(("ILLEGAL",))
            break
        output, cost, state = edge
        if budget is not None:
            budget -= cost
        response.extend((("EDGE", output, cost), ("OBS", machine.observations[state])))
    return tuple(response)


def canonical(values):
    table = {}
    result = []
    for value in values:
        if value not in table:
            table[value] = len(table)
        result.append(table[value])
    return tuple(result)


def coarsest_partition(machine):
    """P_i contains exactly the equal responses to words of length at most i."""
    need(isinstance(machine, Machine), "invalid machine")
    part = canonical(machine.observations)
    while True:
        signatures = []
        for state, row in enumerate(machine.transitions):
            signatures.append((machine.observations[state], tuple(
                None if edge is None else (edge[0], edge[1], part[edge[2]])
                for edge in row)))
        updated = canonical(signatures)
        if updated == part:
            return part
        part = updated


def quotient(machine, partition):
    """Validate any stable partition; construct executable induced dynamics."""
    need(isinstance(machine, Machine), "invalid machine")
    need(type(partition) is tuple and len(partition) == len(machine.observations),
         "partition must cover states")
    need(all(nat(c) for c in partition), "invalid class")
    need(canonical(partition) == partition, "classes must be canonically numbered")
    representatives = {}
    signatures = {}
    for s, c in enumerate(partition):
        sig = (machine.observations[s], tuple(
            None if e is None else (e[0], e[1], partition[e[2]])
            for e in machine.transitions[s]))
        if c in signatures:
            need(signatures[c] == sig, "partition is not a congruence")
        signatures[c] = sig
        representatives.setdefault(c, s)
    obs = tuple(machine.observations[representatives[c]] for c in representatives)
    rows = tuple(signatures[c][1] for c in representatives)
    return Machine(obs, rows), partition


def budget_lift(machine, max_budget):
    """Product state index is s*(B+1)+b; unaffordable edges are not admitted."""
    need(isinstance(machine, Machine), "invalid machine")
    need(nat(max_budget), "invalid maximum budget")
    stride = max_budget + 1
    obs, rows = [], []
    for s in range(len(machine.observations)):
        for b in range(stride):
            obs.append(machine.observations[s])
            rows.append(tuple(
                None if e is None or e[1] > b
                else (e[0], e[1], e[2]*stride + b-e[1])
                for e in machine.transitions[s]))
    return Machine(tuple(obs), tuple(rows))


def transport_partition_to_budget(partition, max_budget):
    """Same original class and same remaining budget are always sufficient."""
    need(type(partition) is tuple and bool(partition) and all(nat(c) for c in partition),
         "invalid partition")
    need(canonical(partition) == partition and nat(max_budget), "invalid lift")
    return canonical((c, b) for c in partition for b in range(max_budget + 1))
