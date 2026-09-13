"""Independent complete policy trees and direct fixed/switching path execution."""
from fractions import Fraction as F
from itertools import product


def policies(model, horizon, state=0):
    if state == model.goal or horizon == 0 or not model.actions[state]:
        return (("end", state),)
    result = []
    for index, action in enumerate(model.actions[state]):
        descendants = []
        for target in range(len(model.actions)):
            possible = any(row[target] > 0 for row in action.rows)
            descendants.append(policies(model, horizon-1, target) if possible else (None,))
        result.extend((state, index, branches) for branches in product(*descendants))
    return tuple(result)


def execute(model, tree, theta=None, nature=None):
    """Enumerate stochastic trajectories; fixed theta is never resampled."""
    stack = [(tree, (), F(1), F(0))]
    fail = total = F(0)
    paths = 0
    while stack:
        node, history, probability, bill = stack.pop()
        if node[0] == "end":
            state = node[1]
            fail += probability*(state != model.goal)
            total += probability*(bill+model.abort[state])
            paths += 1
            continue
        state, index, children = node
        action = model.actions[state][index]
        chosen = theta if theta is not None else nature[history]
        for target, chance in enumerate(action.rows[chosen]):
            if chance:
                stack.append((children[target], history+(target,), probability*chance, bill+action.cost))
    return (fail, total), paths


def fixed_points(model, horizon, state=0):
    points, paths = set(), 0
    trees = policies(model, horizon, state)
    for tree in trees:
        result = []
        for theta in range(model.models):
            pair, count = execute(model, tree, theta=theta)
            result.append(pair)
            paths += count
        points.add(tuple(v[0] for v in result)+tuple(v[1] for v in result))
    return points, dict(common_trees=len(trees), fixed_model_path_executions=paths)


def switching(model, horizon, state=0):
    best, failure_best, assignments = None, F(1), 0
    for tree in policies(model, horizon, state):
        locations, stack = [], [(tree, ())]
        while stack:
            node, history = stack.pop()
            if node[0] != "end":
                locations.append(history)
                stack.extend((child, history+(target,)) for target, child in enumerate(node[2]) if child is not None)
        outcomes = []
        for choices in product(range(model.models), repeat=len(locations)):
            nature = dict(zip(locations, choices))
            pair, _ = execute(model, tree, nature=nature)
            outcomes.append(pair)
            assignments += 1
        worst_failure = max(x[0] for x in outcomes)
        failure_best = min(failure_best, worst_failure)
        if worst_failure == 0:
            work = max(x[1] for x in outcomes)
            best = work if best is None else min(best, work)
    return dict(minimum_worst_failure=failure_best, successful_minimax_work=best,
                nature_table_assignments=assignments)


def independent_frontier(points):
    result = set(points)
    for v in points:
        for u in points:
            if u != v and all(a <= b for a, b in zip(u, v)):
                result.discard(v)
                break
    return result
