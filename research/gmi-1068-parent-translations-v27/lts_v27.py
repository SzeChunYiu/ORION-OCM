"""Relation LTSs, actual free paths, and all exact finite path lifts."""
from dataclasses import dataclass
from core_v27 import index, nat, need, paths, tup


@dataclass(frozen=True)
class LTS:
    state_count: int
    label_count: int
    edges: tuple

    def __post_init__(self):
        nat(self.state_count)
        nat(self.label_count)
        edges = tup(self.edges)
        for edge in edges:
            need(type(edge) is tuple and len(edge) == 3, "edge triple required")
            index(edge[0], self.state_count)
            index(edge[1], self.label_count)
            index(edge[2], self.state_count)
        need(len(set(edges)) == len(edges), "duplicate transition triple")
        object.__setattr__(self, "edges", tuple(sorted(edges)))


def checked(system):
    need(type(system) is LTS, "actual LTS required")
    return system


def state_map(source, target, mapping):
    checked(source)
    checked(target)
    need(source.label_count == target.label_count, "fixed label set mismatch")
    tup(mapping)
    need(len(mapping) == source.state_count, "state map domain mismatch")
    for value in mapping:
        index(value, target.state_count)
    return mapping


def successors(system, state):
    checked(system)
    index(state, system.state_count)
    return tuple((a, t) for s, a, t in system.edges if s == state)


def forward(source, target, mapping):
    state_map(source, target, mapping)
    return all((mapping[s], a, mapping[t]) in target.edges for s, a, t in source.edges)


def back(source, target, mapping):
    state_map(source, target, mapping)
    return all(any((a, mapping[t]) == (label, end) for a, t in successors(source, s))
               for s in range(source.state_count)
               for label, end in successors(target, mapping[s]))


def hom(source, target, mapping):
    state_map(source, target, mapping)
    return all({(a, mapping[t]) for a, t in successors(source, s)}
               == set(successors(target, mapping[s])) for s in range(source.state_count))


def graph(system):
    checked(system)
    return paths.validate((system.state_count, tuple((s, t) for s, _, t in system.edges)))


def checked_path(system, path):
    checked(system)
    need(type(path) is tuple and len(path) == 2, "path pair required")
    start, word = path
    index(start, system.state_count)
    tup(word)
    for edge in word:
        index(edge, len(system.edges))
    paths.endpoint(graph(system), path)
    return start, word


def endpoint(system, path):
    checked_path(system, path)
    return paths.endpoint(graph(system), path)


def labels(system, path):
    _, word = checked_path(system, path)
    return tuple(system.edges[e][1] for e in word)


def compose_paths(system, first, second):
    checked_path(system, first)
    checked_path(system, second)
    return paths.compose(graph(system), first, second)


def map_path(source, target, mapping, path):
    state_map(source, target, mapping)
    start, word = checked_path(source, path)
    need(forward(source, target, mapping), "forward premise fails")
    edge_ids = {edge: i for i, edge in enumerate(target.edges)}
    return mapping[start], tuple(edge_ids[(mapping[s], a, mapping[t])]
                                 for e in word for s, a, t in (source.edges[e],))


def lift_path(source, target, mapping, start, target_path):
    state_map(source, target, mapping)
    index(start, source.state_count)
    target_start, word = checked_path(target, target_path)
    need(target_start == mapping[start], "target path starts at wrong image")
    need(hom(source, target, mapping), "coalgebra homomorphism premise fails")
    frontier = [(start, ())]
    for edge in word:
        source_label, label, target_label = target.edges[edge]
        frontier = [(t, lifted + (i,)) for current, lifted in frontier
                    for i, (s, a, t) in enumerate(source.edges)
                    if s == current and a == label
                    and mapping[s] == source_label and mapping[t] == target_label]
    return tuple(sorted((start, word) for _, word in frontier))
