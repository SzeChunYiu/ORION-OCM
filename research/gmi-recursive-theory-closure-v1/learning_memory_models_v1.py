"""Exact finite controls for scoped learning/memory claims, not a learner."""
from fractions import Fraction as F
from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def law(weights):
    result = {k: F(v) for k, v in weights.items()}
    require(bool(result) and all(v >= 0 for v in result.values()), "invalid law")
    require(sum(result.values()) == 1, "law must sum to one")
    return result


def pushforward(weights, mapping):
    out = {}
    for value, mass in law(weights).items():
        target = mapping(value)
        out[target] = out.get(target, F(0)) + mass
    return out


def output_law(view_law, decoder):
    result = {}
    for view, mass in law(view_law).items():
        for output, conditional in law(decoder[view]).items():
            result[output] = result.get(output, F(0)) + mass * conditional
    return result


def success(view_law, decoder, target):
    return output_law(view_law, decoder).get(target, F(0))


def deterministic_decoders(views, outputs=(0, 1, "abstain")):
    views = tuple(views)
    for choices in product(outputs, repeat=len(views)):
        yield {v: {a: F(1)} for v, a in zip(views, choices)}


def private_action_view(world):
    require(world in (0, 1), "binary world")
    return {(a, a ^ world): F(1, 2) for a in (0, 1)}


def external_regret(loss_rows, chosen):
    require(bool(loss_rows) and len(loss_rows) == len(chosen), "time mismatch")
    width = len(loss_rows[0])
    require(width > 0 and all(len(row) == width for row in loss_rows), "shape")
    require(all(type(a) is int and 0 <= a < width for a in chosen), "action")
    rows = [tuple(F(x) for x in row) for row in loss_rows]
    require(all(0 <= x <= 1 for row in rows for x in row), "loss range")
    learner = sum(row[a] for row, a in zip(rows, chosen))
    comparator = min(sum(row[j] for row in rows) for j in range(width))
    return learner - comparator


def empirical_risks(hypotheses, sample):
    require(bool(hypotheses) and bool(sample), "empty register or sample")
    n = len(next(iter(hypotheses.values())))
    require(n > 0 and all(len(row) == n for row in hypotheses.values()), "shape")
    require(all(0 <= x <= 1 for row in hypotheses.values() for x in row), "loss")
    require(all(type(x) is int and 0 <= x < n for x in sample), "sample domain")
    return {h: sum((F(row[x]) for x in sample), F(0)) / len(sample)
            for h, row in hypotheses.items()}


def population_risks(hypotheses, probabilities):
    p = law(dict(enumerate(probabilities)))
    require(all(len(row) == len(p) for row in hypotheses.values()), "shape")
    return {h: sum((F(value) * p[x] for x, value in enumerate(row)), F(0))
            for h, row in hypotheses.items()}


def proper_erm(hypotheses, sample):
    risks = empirical_risks(hypotheses, sample)
    return min(risks, key=risks.get)  # Register order is the declared tie rule.


def memorizer_losses(domain_size, sample):
    require(domain_size > 0 and all(0 <= x < domain_size for x in sample),
            "sample domain")
    observed = frozenset(sample)
    return tuple(int(x not in observed) for x in range(domain_size))
