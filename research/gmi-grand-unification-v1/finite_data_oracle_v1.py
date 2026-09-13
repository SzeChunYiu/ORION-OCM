"""Independent complete policy syntax, path execution and ordered sample sequences."""
from collections import defaultdict
from fractions import Fraction as F
from itertools import product


def policy_syntax(actions, horizon, start):
    """Construct all action/observation trees without consulting any probabilities or costs."""
    if horizon == 0 or actions[start] == 0:
        return (("end",),)
    children = [policy_syntax(actions, horizon-1, s) for s in range(len(actions))]
    return tuple((a, tuple(branches)) for a in range(actions[start])
                 for branches in product(*children))


def path_evaluate(problem, policy):
    success = cost = F(0)
    terminals = 0
    stack = [(0, problem.start, policy, F(1), F(0))]
    while stack:
        t, state, node, probability, work = stack.pop()
        if t == len(problem.stage) or not problem.rows[state]:
            if node != ("end",):
                raise ValueError("policy must stop exactly at terminal/deadline")
            success += probability*(state in problem.goals)
            cost += probability*(work+problem.settlement[state])
            terminals += 1
            continue
        action, branches = node
        if action not in range(len(problem.rows[state])) or len(branches) != len(problem.rows):
            raise ValueError("incomplete or illegal policy")
        for target in range(len(problem.rows)):
            mass = probability*problem.rows[state][action][target]
            if mass:
                stack.append((t+1, target, branches[target], mass,
                              work+problem.stage[t][state][action]))
    return (success, cost), terminals


def all_profiles(problem):
    trees = policy_syntax(tuple(map(len, problem.rows)), len(problem.stage), problem.start)
    points, terminal_paths = {}, 0
    for tree in trees:
        point, count = path_evaluate(problem, tree)
        points.setdefault(point, tree)
        terminal_paths += count
    return points, dict(trees=len(trees), terminal_paths=terminal_paths)


def mixed_evaluate(problem, mixture):
    p = c = F(0)
    for weight, tree in mixture:
        point, _ = path_evaluate(problem, tree)
        p += weight*point[0]
        c += weight*point[1]
    return p, c


def ordered_count_law(distribution, samples):
    answer = defaultdict(F)
    for sequence in product(range(len(distribution)), repeat=samples):
        weight = F(1)
        counts = [0]*len(distribution)
        for value in sequence:
            weight *= distribution[value]
            counts[value] += 1
        answer[tuple(counts)] += weight
    return dict(answer)


def selected_sample_control(samples=4):
    """Two fair arms, full independent ordered data, choose greatest empirical success."""
    optimism = joint_bad = F(0)
    sequences = tuple(product((0, 1), repeat=samples))
    for a, b in product(sequences, repeat=2):
        estimates = (F(sum(a), samples), F(sum(b), samples))
        chosen = max(estimates)
        weight = F(1, 2**(2*samples))
        optimism += weight*(chosen-F(1, 2))
        joint_bad += weight*(max(abs(x-F(1, 2)) for x in estimates) > F(1, 4))
    return dict(ordered_datasets=len(sequences)**2, expected_selection_optimism=optimism,
                simultaneous_failure=joint_bad)


def dual_mixture_cost(points, threshold, seed_cost=0):
    """Independent LP dual envelope, never constructing primal mixture weights."""
    points = tuple(points)
    if not points or max(p for p, _ in points) < threshold:
        return None
    multipliers = {F(0)}
    for p, c in points:
        for q, d in points:
            if p != q:
                crossing = (d-c)/(q-p)
                if crossing >= 0:
                    multipliers.add(crossing)
    dual = max(min(c+lam*(threshold-p) for p, c in points) for lam in multipliers)
    pure = min(c for p, c in points if p >= threshold)
    return min(pure, dual+seed_cost)
