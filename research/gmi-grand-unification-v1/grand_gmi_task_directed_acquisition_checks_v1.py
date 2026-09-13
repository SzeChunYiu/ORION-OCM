#!/usr/bin/env python3
"""Finite task acquisition, independently simulated policy tables and retention."""
from functools import lru_cache
from itertools import combinations, product
import json


def acquisition_cost(matrix, success, costs):
    """Exact minimax recurrence; None denotes infeasible, including empty rows."""
    @lru_cache(None)
    def solve(state):
        common = set(success[state[0]])
        for w in state[1:]:
            common.intersection_update(success[w])
        if common:
            return 0
        options = []
        for x, cost in enumerate(costs):
            cells = tuple(tuple(w for w in state if matrix[w][x] == y)
                          for y in sorted({matrix[w][x] for w in state}))
            if len(cells) < 2:
                continue
            child = [solve(cell) for cell in cells]
            if all(v is not None for v in child):
                options.append(cost + max(child))
        return min(options, default=None)
    return solve(tuple(range(len(matrix))))


def retained_cost(matrix, success, costs, symbols):
    actions = sorted(set().union(*map(set, success)))
    values = []
    for size in range(1, min(symbols, len(actions)) + 1):
        for subset in combinations(actions, size):
            restricted = tuple(frozenset(row).intersection(subset) for row in success)
            value = acquisition_cost(matrix, restricted, costs)
            if value is not None:
                values.append(value)
    return min(values, default=None)


@lru_cache(None)
def policy_trees(arities, depth):
    """All bounded syntactic experiment trees, without task/compatibility pruning."""
    trees = [None]
    if depth:
        children = policy_trees(arities, depth - 1)
        for x, arity in enumerate(arities):
            trees.extend((x, branches) for branches in product(children, repeat=arity))
    return tuple(trees)


def execute(tree, row, costs):
    path, cost = (), 0
    while tree is not None:
        x, children = tree
        path += (row[x],)
        cost += costs[x]
        tree = children[row[x]]
    return path, cost


def policy_oracle(matrix, costs, actions, depth):
    """Execute every syntax tree; enumerate outputs constant at each reached leaf."""
    arities = tuple(max(row[x] for row in matrix) + 1 for x in range(len(costs)))
    outputs = tuple(product(actions, repeat=len(matrix)))
    best = {}
    for tree in policy_trees(arities, depth):
        traces = [execute(tree, row, costs) for row in matrix]
        same_leaf = [(i, j) for i in range(len(matrix)) for j in range(i)
                     if traces[i][0] == traces[j][0]]
        cost = max(trace[1] for trace in traces)
        for output in outputs:
            if all(output[i] == output[j] for i, j in same_leaf):
                best[output] = min(cost, best.get(output, cost))
    return best


def oracle_cost(profiles, success, symbols=None):
    return min((cost for out, cost in profiles.items()
                if (symbols is None or len(set(out)) <= symbols)
                and all(a in row for a, row in zip(out, success))), default=None)


def observable_adequate(matrix, success):
    for row in set(matrix):
        candidates = [success[w] for w, value in enumerate(matrix) if value == row]
        if not set.intersection(*map(set, candidates)):
            return False
    return True


def tradeoff_witness():
    matrix = tuple((i,) + tuple(int(i == j and b == 1) for j in range(3))
                   for i in range(3) for b in range(2))
    success = tuple(frozenset((i, 3 + b)) for i in range(3) for b in range(2))
    # Enumerate 201 trees to depth 2 and every 5^6 world-output table.
    profiles = policy_oracle(matrix, (1, 1, 1, 1), tuple(range(5)), 2)
    records = []
    for m in range(1, 6):
        records.append([m, retained_cost(matrix, success, (1, 1, 1, 1), m),
                        oracle_cost(profiles, success, m)])
    return {"capacity_cost_oracle": records,
            "expected": [[1, None, None], [2, 2, 2], [3, 1, 1],
                         [4, 1, 1], [5, 1, 1]],
            "frontier": [[1, 3], [2, 2]]}


def run_checks():
    action_rows = tuple(frozenset(a for a in range(3) if mask & (1 << a))
                        for mask in range(1, 8))
    cost_register = ((1, 1), (0, 1), (1, 0), (1, 2))
    census = {"instances": 0, "recurrence_oracle": 0,
              "identifiability_iff": 0, "memory_checks": 0,
              "memory_oracle": 0, "adequate": 0, "inadequate": 0,
              "action_without_profile_identification": 0}
    for bits in product((0, 1), repeat=6):
        matrix = tuple(tuple(bits[2*w:2*w+2]) for w in range(3))
        for costs in cost_register:
            profiles = policy_oracle(matrix, costs, (0, 1, 2), 2)
            for success in product(action_rows, repeat=3):
                value = acquisition_cost(matrix, success, costs)
                census["instances"] += 1
                census["recurrence_oracle"] += value == oracle_cost(profiles, success)
                census["identifiability_iff"] += ((value is not None) ==
                                                  observable_adequate(matrix, success))
                census["adequate" if value is not None else "inadequate"] += 1
                profile_possible = all(matrix[i] != matrix[j] or success[i] == success[j]
                                       for i in range(3) for j in range(i))
                census["action_without_profile_identification"] += (
                    value is not None and not profile_possible)
                for m in (1, 2, 3):
                    census["memory_checks"] += 1
                    census["memory_oracle"] += (
                        retained_cost(matrix, success, costs, m) ==
                        oracle_cost(profiles, success, m))
    witness = tradeoff_witness()
    green = (census["instances"] == 87808 == census["recurrence_oracle"] ==
             census["identifiability_iff"] and census["memory_checks"] ==
             263424 == census["memory_oracle"] and
             census["adequate"] > 0 and census["inadequate"] > 0 and
             census["action_without_profile_identification"] > 0 and
             witness["capacity_cost_oracle"] == witness["expected"])
    return {"schema": "grand-gmi-task-directed-acquisition-v1", "census": census,
            "cost_register": cost_register, "tradeoff_witness": witness,
            "scope": "finite exact 3-world/2-binary-test/3-action census; six-world bridge witness",
            "all_checks_green": green,
            "terminal": "TASK_DIRECTED_ACQUISITION_FINITE_GREEN" if green else "FAILED"}


if __name__ == "__main__":
    result = run_checks()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_checks_green"] else 1)
