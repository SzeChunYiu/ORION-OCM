"""Exact truth-table checks for partition-width/query-summary nondetermination."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate(n, truth):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative integer input dimension required")
    if len(truth) != 1 << n or any(type(v) is not int or v < 0 for v in truth):
        raise ValueError("one exact nonnegative output label per input required")
    return tuple(truth)


def response_rows(n, truth, subset):
    truth = validate(n, truth)
    if type(subset) is not int or not 0 <= subset < 1 << n:
        raise ValueError("subset must be an input-coordinate bit mask")
    left = [i for i in range(n) if subset >> i & 1]
    right = [i for i in range(n) if not subset >> i & 1]

    def codes(positions):
        return [sum(b << (n-1-i) for i, b in zip(positions, bits))
                for bits in product((0, 1), repeat=len(positions))]

    return tuple(tuple(truth[a | b] for b in codes(right)) for a in codes(left))


def partition_spectrum(n, truth):
    return tuple(len(set(response_rows(n, truth, subset))) for subset in range(1 << n))


def query_costs(n, truth):
    """All 3**n partial assignments and every useful first query, from actual outputs."""
    truth = validate(n, truth)
    bits = tuple(product((0, 1), repeat=n))
    policy, branch_checks = {}, 0

    @lru_cache(None)
    def solve(state):
        nonlocal branch_checks
        compatible = [j for j, x in enumerate(bits)
                      if all(v == -1 or v == x[i] for i, v in enumerate(state))]
        if len({truth[j] for j in compatible}) == 1:
            return F(0), 0
        options = []
        for i, value in enumerate(state):
            if value != -1:
                continue
            children = []
            for answer in (0, 1):
                child = list(state)
                child[i] = answer
                children.append(solve(tuple(child)))
                branch_checks += 1
            mean = 1+(children[0][0]+children[1][0])/2
            worst = 1+max(children[0][1], children[1][1])
            options.append((mean, worst, i))
        policy[state] = min(options, key=lambda row: (row[0], row[2]))[2]
        return min(row[0] for row in options), min(row[1] for row in options)

    for state in product((-1, 0, 1), repeat=n):
        solve(state)
    mean, worst = solve((-1,)*n)
    realized = []
    for j, x in enumerate(bits):
        state, depth = [-1]*n, 0
        while tuple(state) in policy:
            i = policy[tuple(state)]
            state[i] = x[i]
            depth += 1
        outputs = {truth[t] for t, y in enumerate(bits)
                   if all(v == -1 or v == y[i] for i, v in enumerate(state))}
        require(outputs == {truth[j]}, "policy terminated without exact output")
        realized.append(depth)
    require(sum(realized)/F(1 << n) == mean, "policy execution disagrees with DP mean")
    return {"expected": mean, "worstcase": worst, "states": solve.cache_info().currsize,
            "first_query_branches": branch_checks, "realized_depths": tuple(realized)}


def truth_tables(n):
    bits = tuple(product((0, 1), repeat=n))
    return {"or": tuple(int(any(x)) for x in bits),
            "parity": tuple(sum(x) % 2 for x in bits),
            "identity": tuple(range(1 << n)),
            "repeat_parity": tuple((sum(x) % 2)*((1 << n)-1) for x in bits)}


def run():
    rows, partitions, states, branches, cells = [], 0, 0, 0, 0
    for n in range(2, 9):
        tables = truth_tables(n)
        spectra = {name: partition_spectrum(n, truth) for name, truth in tables.items()}
        costs = {name: query_costs(n, truth) for name, truth in tables.items()}
        one_bit = (1,)+(2,)*((1 << n)-1)
        require(spectra["or"] == spectra["parity"] == spectra["repeat_parity"] == one_bit,
                "nonempty-partition one-bit law failed")
        require(spectra["identity"] == tuple(1 << s.bit_count() for s in range(1 << n)),
                "identity partition width failed")
        expected_or = 2-F(1, 1 << (n-1))
        require(costs["or"]["expected"] == expected_or, "OR average-query law failed")
        require(all(costs[name]["expected"] == n for name in tables if name != "or"),
                "parity/identity average-query law failed")
        require(all(row["worstcase"] == n for row in costs.values()), "worstcase law failed")
        require(costs["identity"]["realized_depths"] == costs["repeat_parity"]["realized_depths"]
                == (n,)*(1 << n), "reverse control differs on an input")
        require(all(row["states"] == 3**n for row in costs.values()), "partial states omitted")
        partitions += 4*(1 << n)
        states += sum(row["states"] for row in costs.values())
        branches += sum(row["first_query_branches"] for row in costs.values())
        cells += 4*(1 << (2*n))
        rows.append({"n": n, "or_expected_queries": str(costs["or"]["expected"]),
                     "parity_expected_queries": str(n), "all_worstcase_queries": n,
                     "identical_or_parity_partition_widths": True,
                     "identity_vs_repeat_parity_full_subset_widths": [n, 1],
                     "reverse_equal_query_cost_on_every_input": True})
    unequal_rows = response_rows(2, truth_tables(2)["or"], 1) != response_rows(2, truth_tables(2)["parity"], 1)
    require(unequal_rows, "width equality was incorrectly promoted to response-row equality")
    return {"schema": "full-partition-width-computation-v1", "all_checks_green": True,
            "terminal": "FULL_PARTITION_WIDTH_QUERY_SUMMARIES_FINITE_GREEN",
            "scope": "all input partitions, full complementary side information, uniform exact bit queries",
            "census": {"dimensions": 7, "functions_per_dimension": 4,
                       "partition_instances": partitions, "response_table_cells": cells,
                       "partial_assignment_states": states, "first_query_branches": branches},
            "equal_width_unequal_response_rows_control": unequal_rows, "rows": rows}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
