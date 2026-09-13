"""Finite observed-state policy profiles; all arithmetic is exact."""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import product


def rational(x, lower=0, upper=None):
    try:
        value = F(x)
    except (ValueError, OverflowError, TypeError) as exc:
        raise ValueError("finite rational required") from exc
    if value < lower or (upper is not None and value > upper):
        raise ValueError("rational outside registered range")
    return value


@dataclass(frozen=True)
class Problem:
    rows: tuple
    stage: tuple
    settlement: tuple
    goals: frozenset
    start: int = 0

    def __post_init__(self):
        rows = tuple(tuple(tuple(rational(p, upper=1) for p in row) for row in state)
                     for state in self.rows)
        n = len(rows)
        if not n or not 0 <= self.start < n:
            raise ValueError("nonempty alphabet and admitted initial state required")
        if any(len(row) != n or sum(row) != 1 for state in rows for row in state):
            raise ValueError("complete probability rows required")
        goals = frozenset(self.goals)
        if any(g not in range(n) or rows[g] for g in goals):
            raise ValueError("success states must be stopped states")
        stage = tuple(tuple(tuple(rational(c) for c in state) for state in slot)
                      for slot in self.stage)
        if any(len(slot) != n or any(len(slot[s]) != len(rows[s]) for s in range(n))
               for slot in stage):
            raise ValueError("stage costs must cover every legal action")
        settlement = tuple(rational(x) for x in self.settlement)
        if len(settlement) != n:
            raise ValueError("settlement must cover every state")
        object.__setattr__(self, "rows", rows)
        object.__setattr__(self, "stage", stage)
        object.__setattr__(self, "settlement", settlement)
        object.__setattr__(self, "goals", goals)


def tv(p, q):
    if len(p) != len(q):
        raise ValueError("different alphabets")
    return sum(abs(a-b) for a, b in zip(p, q))/2


def model_distance(p, q):
    if (p.stage, p.settlement, p.goals, p.start) != (q.stage, q.settlement, q.goals, q.start):
        raise ValueError("common costs, success obligation and start required")
    if tuple(map(len, p.rows)) != tuple(map(len, q.rows)):
        raise ValueError("common labelled state and legal-action register required")
    return max((tv(a, b) for x, y in zip(p.rows, q.rows) for a, b in zip(x, y)), default=F(0))


def transfer_bounds(problem, epsilon):
    epsilon = rational(epsilon, upper=1)
    h = len(problem.stage)
    drift = tuple(1-(1-epsilon)**t for t in range(h+1))
    ceilings = [max((v for row in slot for v in row), default=F(0)) for slot in problem.stage]
    error = sum(c*drift[t] for t, c in enumerate(ceilings))
    error += max(problem.settlement)*drift[h]
    return drift[h], error


def intervals(problem, profile, epsilon, seed_charge=0):
    probability, cost = profile
    slack, work_slack = transfer_bounds(problem, epsilon)
    seed_charge = rational(seed_charge)
    ceiling = sum(max((c for row in slot for c in row), default=F(0)) for slot in problem.stage)
    ceiling += max(problem.settlement)+seed_charge
    return (max(F(0), probability-slack), min(F(1), probability+slack)), (
        max(seed_charge, cost-work_slack), min(ceiling, cost+work_slack))


def synthesize(problem):
    stats = dict(states=0, child_combinations=0, transition_terms=0)
    @lru_cache(None)
    def visit(t, s):
        stats["states"] += 1
        if t == len(problem.stage) or not problem.rows[s]:
            return {(F(s in problem.goals), problem.settlement[s]): ("end",)}
        children = [visit(t+1, z) for z in range(len(problem.rows))]
        profiles = {}
        for a, row in enumerate(problem.rows[s]):
            for choice in product(*(tuple(c.items()) for c in children)):
                stats["child_combinations"] += 1
                stats["transition_terms"] += len(row)
                probability = sum(w*entry[0][0] for w, entry in zip(row, choice))
                cost = problem.stage[t][s][a]+sum(w*entry[0][1] for w, entry in zip(row, choice))
                profiles.setdefault((probability, cost), (a, tuple(entry[1] for entry in choice)))
        return profiles
    return visit(0, problem.start), stats


def cheapest_mixture(profiles, threshold, seed_cost=0):
    """Complete one-constraint LP: a minimizing mixture needs at most two points."""
    threshold = rational(threshold)
    seed_cost = rational(seed_cost)
    points = tuple(sorted(profiles))
    options = [(c, ((F(1), i),)) for i, (p, c) in enumerate(points) if p >= threshold]
    for i, (p, c) in enumerate(points):
        for j, (q, d) in enumerate(points):
            if p < threshold < q:
                w = (q-threshold)/(q-p)
                options.append((w*c+(1-w)*d+seed_cost, ((w, i), (1-w, j))))
    if not options:
        return None
    cost, mixture = min(options)
    return dict(cost=cost, seed_charge=seed_cost if len(mixture)>1 else F(0),
                probability=sum(w*points[i][0] for w, i in mixture),
                policies=tuple((w, profiles[points[i]]) for w, i in mixture))


def certificate(problem, epsilon, required_success, seed_cost=0):
    probability_slack, cost_slack = transfer_bounds(problem, epsilon)
    points, stats = synthesize(problem)
    policy = cheapest_mixture(points, rational(required_success, upper=1)+probability_slack, seed_cost)
    if policy is None:
        return None, stats
    probability_interval, cost_interval = intervals(
        problem, (policy["probability"], policy["cost"]), epsilon, policy["seed_charge"])
    return dict(policy=policy, success_interval=probability_interval,
                cost_interval=cost_interval), stats
