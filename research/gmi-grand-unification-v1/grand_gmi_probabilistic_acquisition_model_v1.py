"""Finite known-kernel acquisition model; exact control-cost coordinates."""
from fractions import Fraction as F


class ContractError(ValueError):
    pass


def validate(model):
    if type(model) is not tuple or len(model) < 2 or model[-1] != ():
        raise ContractError("finite tuple of action rows, last state is stopped goal")
    for row in model[:-1]:
        if type(row) is not tuple or not row:
            raise ContractError("every nonterminal state needs a legal action")
        for cost, probs in row:
            if type(cost) not in (int, F) or cost <= 0:
                raise ContractError("strictly positive exact rational control cost")
            if type(probs) is not tuple or len(probs) != len(model):
                raise ContractError("one probability for every registered state")
            if any(type(p) not in (int, F) or p < 0 for p in probs) or sum(probs) != 1:
                raise ContractError("exact nonnegative normalized rational kernel")
    return model


def solve(matrix, rhs):
    """Independent exact Gaussian elimination; a singular system is rejected."""
    n = len(rhs)
    a = [[F(x) for x in row]+[F(b)] for row, b in zip(matrix, rhs)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col]), None)
        if pivot is None:
            raise ContractError("singular linear system")
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        a[col] = [x/scale for x in a[col]]
        for r in range(n):
            if r != col:
                scale = a[r][col]
                a[r] = [x-scale*y for x, y in zip(a[r], a[col])]
    return tuple(row[-1] for row in a)


def policy_kernel(model, policy):
    validate(model)
    if len(policy) != len(model)-1 or any(type(a) is not int or not 0 <= a < len(row)
                                        for a, row in zip(policy, model[:-1])):
        raise ContractError("one legal action index per nonterminal state")
    return tuple(model[s][a] for s, a in enumerate(policy))


def stationary(model, policy, start=0):
    kernel = policy_kernel(model, policy)
    n, goal = len(model), len(model)-1
    if type(start) is not int or not 0 <= start < n:
        raise ContractError("registered initial state required")
    edges = [set(j for j, p in enumerate(probs) if p) for _, probs in kernel]+[set()]
    reach = {start}
    while True:
        expanded = reach.union(*(edges[s] for s in reach))
        if expanded == reach:
            break
        reach = expanded
    possible, sure = {goal}, {goal}
    for _ in range(n):
        possible |= {s for s in range(goal) if edges[s] & possible}
        sure |= {s for s in range(goal) if edges[s] <= sure}
    relevant = sorted((reach & possible)-{goal})
    matrix = [[int(i == j)-kernel[i][1][j] for j in relevant] for i in relevant]
    probabilities = solve(matrix, [kernel[i][1][goal] for i in relevant])
    success = dict(zip(relevant, probabilities)) | {goal: F(1)}
    almost_sure = reach <= possible
    costs = {}
    if almost_sure:
        costs = dict(zip(relevant, solve(matrix, [kernel[i][0] for i in relevant])))
    return {"sure": start in sure, "almost_sure": almost_sure,
            "success": success.get(start, F(0)),
            "expected_cost": F(0) if start == goal else costs.get(start)}


def finite_horizon(model, horizon):
    validate(model)
    if type(horizon) is not int or horizon < 0:
        raise ContractError("nonnegative integer horizon required")
    n = len(model)
    success, sure_cost = [F(0)]*(n-1)+[F(1)], [None]*(n-1)+[F(0)]
    for _ in range(horizon):
        next_success, next_cost = [], []
        for row in model[:-1]:
            next_success.append(max(sum(p*v for p, v in zip(probs, success))
                                    for _, probs in row))
            feasible = [cost+sum(p*sure_cost[j] for j, p in enumerate(probs) if p)
                        for cost, probs in row
                        if all(not p or sure_cost[j] is not None for j, p in enumerate(probs))]
            next_cost.append(min(feasible) if feasible else None)
        success, sure_cost = next_success+[F(1)], next_cost+[F(0)]
    return tuple(success), tuple(sure_cost)


def bellman_certificate(model, values, policy):
    kernel = policy_kernel(model, policy)
    if len(values) != len(model) or values[-1] != 0:
        return False
    if any(type(v) not in (int, F) or v < 0 for v in values):
        return False
    for s, row in enumerate(model[:-1]):
        bounds = [c+sum(p*v for p, v in zip(probs, values)) for c, probs in row]
        if values[s] > min(bounds) or values[s] != bounds[policy[s]]:
            return False
        if not stationary(model, policy, s)["almost_sure"]:
            return False
    return True


def persistent_probe(recovery=False, fallback=False):
    """Observed sufficient states: fresh fair belief M, known failed mode B, goal G."""
    model = [[(F(1), (F(0), F(1, 2), F(1, 2)))],
             [(F(1), (F(0), F(1), F(0)))], []]
    if recovery:
        model[1].append((F(1), (F(1), F(0), F(0))))
    if fallback:
        for row in model[:2]:
            row.append((F(5), (F(0), F(0), F(1))))
    return validate(tuple(tuple(row) for row in model))
