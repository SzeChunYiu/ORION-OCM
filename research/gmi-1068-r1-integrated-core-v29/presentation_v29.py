"""Actual path evaluation and finite DAG evaluation-kernel presentations."""
from dataclasses import dataclass
from core_v29 import (categories, checked_graph, checked_path, functors, index,
                      need, partial, paths, same_record, tup)


@dataclass(frozen=True)
class GeneratorMap:
    graph: tuple
    target: object
    generator_arrows: tuple

    def __post_init__(self):
        n, edges = checked_graph(self.graph)
        categories.validate_category(self.target)
        need(self.target.object_count == n, "object-fixing target required")
        tup(self.generator_arrows)
        need(len(self.generator_arrows) == len(edges), "complete generator map required")
        for edge, arrow in zip(edges, self.generator_arrows):
            index(arrow, len(self.target.table.rows))
            need(edge == (self.target.source[arrow], self.target.target[arrow]),
                 "generator endpoint mismatch")


def checked_mapping(mapping):
    need(type(mapping) is GeneratorMap, "actual GeneratorMap required")
    mapping.__post_init__()
    return mapping


def evaluate_path(mapping, path):
    checked_mapping(mapping)
    (start, word), endpoint = checked_path(mapping.graph, path)
    target = mapping.target
    value = target.identities[start]
    for edge in word:
        value = target.table.rows[value][mapping.generator_arrows[edge]]
        need(value is not None, "lawful typed evaluation unexpectedly failed")
    need(target.source[value] == start and target.target[value] == endpoint,
         "evaluated endpoints drift")
    return start, endpoint, value


@dataclass(frozen=True)
class DAGPresentation:
    mapping: GeneratorMap
    paths: tuple
    class_of: tuple
    representatives: tuple
    category: object
    lower: object
    generates: bool
    quote: object


def dag_presentation(mapping):
    checked_mapping(mapping)
    roster = paths.enumerate_dag(mapping.graph)
    labels, classes, representatives = {}, {}, []
    for path in roster:
        value = evaluate_path(mapping, path)
        if value not in classes:
            classes[value] = len(classes)
            representatives.append(path)
        labels[path] = classes[value]
    quotient = paths.quotient_dag(mapping.graph, labels)
    size = len(classes)
    source = tuple(quotient["arrows"][i][0] for i in range(size))
    target = tuple(quotient["arrows"][i][1] for i in range(size))
    rows = tuple(tuple(quotient["composition"].get((i, j)) for j in range(size))
                 for i in range(size))
    category = categories.Typed(mapping.graph[0], source, target,
                                quotient["identities"], partial.Table(rows))
    categories.validate_category(category)
    lower_arrows = tuple(evaluate_path(mapping, path)[2] for path in representatives)
    lower = functors.Functor(category, mapping.target, tuple(range(mapping.graph[0])),
                             lower_arrows)
    generates = set(lower_arrows) == set(range(len(mapping.target.table.rows)))
    quote = None
    if generates:
        inverse = tuple(lower_arrows.index(i) for i in range(len(mapping.target.table.rows)))
        quote = functors.Functor(mapping.target, category, tuple(range(mapping.graph[0])), inverse)
    return DAGPresentation(mapping, roster, tuple(labels[p] for p in roster),
                           tuple(representatives), category, lower, generates, quote)


def verify_presentation(mapping, certificate):
    need(type(certificate) is DAGPresentation, "actual DAGPresentation certificate required")
    same_record(certificate, dag_presentation(mapping))
    return True
