"""Full candidate-ID frontiers under declared resource and positive-price orders."""
from dataclasses import dataclass
from fractions import Fraction
from core_v24 import need, ids as check_ids, rational, code_context, frontier


@dataclass(frozen=True)
class Candidates:
    ids: tuple
    resources: tuple
    viable: tuple
    reachable: tuple
    dimension: int

    def __post_init__(self):
        check_ids(self.ids)
        need(type(self.dimension) is int and self.dimension > 0, "positive resource dimension required")
        fields = (self.resources, self.viable, self.reachable)
        need(all(type(v) is tuple and len(v) == len(self.ids) for v in fields), "candidate dimension")
        need(all(type(v) is bool for v in self.viable + self.reachable), "Boolean flags required")
        for row in self.resources:
            need(type(row) is tuple and len(row) == self.dimension, "resource dimension")
            for value in row:
                rational(value)
                need(value >= 0, "negative resource")


def _active(candidates, reachable_only):
    need(type(candidates) is Candidates, "validated Candidates required")
    need(type(reachable_only) is bool, "Boolean reachability mode required")
    return tuple(v and (r or not reachable_only) for v, r in zip(candidates.viable, candidates.reachable))


def resource_context(candidates, reachable_only):
    admitted = _active(candidates, reachable_only)
    resources = candidates.resources
    relation = tuple(tuple(all(y <= x for x, y in zip(a, b)) for b in resources) for a in resources)
    decoder = tuple(zip(candidates.ids, resources))
    return code_context(admitted, (True,) * len(admitted), relation), decoder


def scalar_context(candidates, weights, reachable_only):
    admitted = _active(candidates, reachable_only)
    need(type(weights) is tuple and len(weights) == candidates.dimension, "price dimension")
    for weight in weights:
        rational(weight)
        need(weight > 0, "strictly positive prices required")
    scores = tuple(sum((w * x for w, x in zip(weights, row)), Fraction(0))
                   for row in candidates.resources)
    relation = tuple(tuple(b <= a for b in scores) for a in scores)
    return code_context(admitted, (True,) * len(admitted), relation), tuple(zip(candidates.ids, scores))


def _winners(context, decoder):
    values = frontier.attained(context, tuple(range(context.n)))
    return sorted(decoder[i][0] for i in frontier.maximal(context.order, values))


def preference(candidates, weights, reachable_only=True):
    scalar, scalar_decoder = scalar_context(candidates, weights, reachable_only)
    resource, resource_decoder = resource_context(candidates, reachable_only)
    pareto = _winners(resource, resource_decoder)
    argmin = _winners(scalar, scalar_decoder)
    return {"terminal": "SELECTION_DEFINED" if pareto else "NO_VIABLE_MORPHOLOGY",
            "pareto_front": pareto, "scalar_argmin": argmin}
