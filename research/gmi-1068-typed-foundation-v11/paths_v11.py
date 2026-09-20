"""Constructive typed finite paths; empty paths retain their object."""
from collections import deque


def nat(value):
    return type(value) is int and value >= 0


def validate(graph):
    if not isinstance(graph, (list, tuple)) or len(graph) != 2:
        raise ValueError("graph requires object count and edge sequence")
    n, edges = graph
    if not nat(n) or not isinstance(edges, (list, tuple)):
        raise ValueError("invalid graph")
    for edge in edges:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            raise ValueError("edge requires two endpoints")
        if any(not nat(v) or v >= n for v in edge):
            raise ValueError("edge outside object set")
    return n, tuple(tuple(edge) for edge in edges)


def canonical(graph, path):
    n, edges = validate(graph)
    if not isinstance(path, (tuple, list)) or len(path) != 2:
        raise ValueError("path requires start and edge word")
    start, word = path
    if not nat(start) or start >= n or not isinstance(word, (tuple, list)):
        raise ValueError("invalid start or word")
    current = start
    for edge in word:
        if not nat(edge) or edge >= len(edges) or edges[edge][0] != current:
            raise ValueError("ill-typed edge occurrence")
        current = edges[edge][1]
    return (start, tuple(word)), current


def endpoint(graph, path):
    return canonical(graph, path)[1]


def identity(graph, obj):
    path, _ = canonical(graph, (obj, ()))
    return path


def compose(graph, first, second):
    left, middle = canonical(graph, first)
    right, _ = canonical(graph, second)
    if middle != right[0]:
        raise ValueError("incompatible endpoints")
    return left[0], left[1] + right[1]


def enumerate_dag(graph):
    n, edges = validate(graph)
    incoming, outgoing = [0] * n, [[] for _ in range(n)]
    for edge, (source, target) in enumerate(edges):
        incoming[target] += 1
        outgoing[source].append((edge, target))
    ready = deque(v for v in range(n) if incoming[v] == 0)
    order = []
    while ready:
        source = ready.popleft()
        order.append(source)
        for _, target in outgoing[source]:
            incoming[target] -= 1
            if incoming[target] == 0:
                ready.append(target)
    if len(order) != n:
        raise ValueError("cyclic graphs have no finite complete path enumeration")
    suffixes = {}
    for source in reversed(order):
        paths = [(source, ())]
        for edge, target in outgoing[source]:
            paths.extend((source, (edge,) + word) for _, word in suffixes[target])
        suffixes[source] = paths
    return tuple(path for source in range(n) for path in suffixes[source])


def interpret(graph, path, domains, edge_maps):
    n, edges = validate(graph)
    (start, word), _ = canonical(graph, path)
    if not isinstance(domains, (list, tuple)) or len(domains) != n or not all(map(nat, domains)):
        raise ValueError("one finite domain cardinality per object required")
    if not isinstance(edge_maps, (list, tuple)) or len(edge_maps) != len(edges):
        raise ValueError("complete generator interpretation required")
    for (source, target), mapping in zip(edges, edge_maps):
        if not isinstance(mapping, (list, tuple)) or len(mapping) != domains[source]:
            raise ValueError("generator map has wrong domain")
        if any(not nat(v) or v >= domains[target] for v in mapping):
            raise ValueError("generator map has wrong codomain")
    values = tuple(range(domains[start]))
    for edge in word:
        values = tuple(edge_maps[edge][v] for v in values)
    return values


def admitted(graph, path, allowed):
    _, edges = validate(graph)
    (_, word), _ = canonical(graph, path)
    if not isinstance(allowed, (set, frozenset)) or any(
        not nat(e) or e >= len(edges) for e in allowed
    ):
        raise ValueError("admitted generators must be an edge-id set")
    return all(e in allowed for e in word)


def quotient_dag(graph, labels):
    paths = enumerate_dag(graph)
    if not isinstance(labels, dict) or set(labels) != set(paths):
        raise ValueError("quotient must cover the complete path category")
    for supplied_path in labels:
        canonical(graph, supplied_path)
    if any(not nat(label) for label in labels.values()):
        raise ValueError("invalid quotient class")
    arrows, compositions = {}, {}
    ends = {path: endpoint(graph, path) for path in paths}
    for path in paths:
        label, hom = labels[path], (path[0], ends[path])
        if label in arrows and arrows[label] != hom:
            raise ValueError("quotient merges different hom sets")
        arrows[label] = hom
    for first in paths:
        for second in paths:
            if ends[first] != second[0]:
                continue
            key = labels[first], labels[second]
            result = labels[compose(graph, first, second)]
            if key in compositions and compositions[key] != result:
                raise ValueError("equivalence is not a typed congruence")
            compositions[key] = result
    return {"identities": tuple(labels[identity(graph, v)] for v in range(graph[0])),
            "arrows": arrows, "composition": compositions}
