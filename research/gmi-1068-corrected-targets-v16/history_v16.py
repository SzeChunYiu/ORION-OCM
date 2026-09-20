"""Typed raw paths; singleton extraction requires a generated-domain premise."""
from dataclasses import dataclass


def integer(value, bound):
    if type(value) is not int or not 0 <= value < bound:
        raise ValueError("index outside declared finite domain")
    return value


@dataclass(frozen=True)
class Graph:
    vertices: int
    edges: tuple

    def __post_init__(self):
        if type(self.vertices) is not int or self.vertices < 0:
            raise ValueError("nonnegative vertex count required")
        if type(self.edges) is not tuple:
            raise ValueError("canonical edge tuple required")
        for edge in self.edges:
            if type(edge) is not tuple or len(edge) != 2:
                raise ValueError("edge needs source and target")
            for endpoint in edge:
                integer(endpoint, self.vertices)


def validate_history(graph, history):
    if type(graph) is not Graph:
        raise ValueError("Graph required")
    if (type(history) is not tuple or len(history) != 2
            or type(history[1]) is not tuple):
        raise ValueError("history is (start, edge-index tuple)")
    current = integer(history[0], graph.vertices)
    for edge in history[1]:
        source, target = graph.edges[integer(edge, len(graph.edges))]
        if current != source:
            raise ValueError("noncomposable typed history")
        current = target
    return current


def admitted(graph, mask, history):
    validate_history(graph, history)
    if (type(mask) is not tuple or len(mask) != len(graph.edges)
            or any(type(value) is not bool for value in mask)):
        raise ValueError("one strict Boolean per edge required")
    return all(mask[edge] for edge in history[1])


def decode_admission(graph, contains):
    if type(graph) is not Graph or not callable(contains):
        raise ValueError("Graph and source-membership callable required")
    answer = []
    for edge, (source, _) in enumerate(graph.edges):
        value = contains((source, (edge,)))
        if type(value) is not bool:
            raise ValueError("membership must return a strict Boolean")
        answer.append(value)
    return tuple(answer)
