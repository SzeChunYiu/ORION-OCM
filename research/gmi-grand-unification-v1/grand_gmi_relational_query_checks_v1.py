#!/usr/bin/env python3
"""Bounded exhaustive reconstruction checks; exact arithmetic, no empirical timing."""
from fractions import Fraction as F
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from relational_query_model_v1 import Problem, feasible, joint, synthesize
from relational_query_oracle_v1 import (equality_partition, execute_constructed,
                                      graph_gamma, oracle, pair_graph)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def compare(problem):
    result = synthesize(problem)
    independent = oracle(problem.actions, problem.outputs, problem.costs)
    require(set(result["profiles"]) == independent["profiles"], "full profile census differs")
    for vector, tree in result["profiles"].items():
        for x, expected in enumerate(vector):
            action, charge = execute_constructed(tree, x, problem.costs)
            require(bool(problem.actions[x] & (1 << action)) and charge == expected,
                    "constructed action or charged execution differs")
    return result, independent


def witnesses():
    r = Problem((3, 6, 13, 3), 4, (1, 1))
    s = Problem((3, 5, 11, 3), 4, (1, 1))
    require(pair_graph(r.actions) == pair_graph(s.actions), "pair graphs differ")
    require(equality_partition(r.actions) == equality_partition(s.actions), "partitions differ")
    require(tuple(a.bit_count() for a in r.actions) == tuple(a.bit_count() for a in s.actions),
            "row cardinalities differ")
    require((r.actions[0] | r.actions[1] | r.actions[2]) ==
            (s.actions[0] | s.actions[1] | s.actions[2]) == 15, "used alphabets differ")
    rr, _ = compare(r)
    ss, _ = compare(s)
    require(joint(rr["profiles"], (F(1, 4),)*4) == {(F(1), F(1))}, "R cost law")
    require(joint(ss["profiles"], (F(1, 4),)*4) == {(F(0), F(0))}, "S cost law")
    n, costs = 3, (1, 2, 3)
    labels = tuple(((x >> 1) & 1) if not (x & 4) else (x & 1) for x in range(8))
    relation = Problem(tuple((1 << y) | (1 << (x+2)) for x, y in enumerate(labels)), 10, costs)
    exact = Problem(tuple(1 << y for y in labels), 10, costs)
    relational, oracle_result = compare(relation)
    functional, _ = compare(exact)
    require(relational["gamma"] == functional["gamma"], "private-action lift changes stopping")
    require(set(relational["profiles"]) == set(functional["profiles"]), "lift changes full profiles")
    prior = (F(1, 15),)*7 + (F(8, 15),)
    expected = frozenset(((F(19, 5), F(6)), (F(64, 15), F(5))))
    require(joint(relational["profiles"], prior) == expected, "joint relational frontier differs")
    require(not feasible(relational["profiles"], prior, F(19, 5), 5), "incompatible minima admitted")
    return {"summary_collision": {"R_mean_worst": ["1", "1"], "S_mean_worst": ["0", "0"]},
            "ambiguous_selector_frontier": [[str(a), str(b)] for a, b in sorted(expected)],
            "selector_syntax_shapes": oracle_result["shapes"],
            "selector_admitted_shapes": oracle_result["admitted"],
            "selector_development_operations": relational["stats"]}


def run():
    census = dict(instances=0, syntax_obligation_checks=0, admitted_shapes=0,
                  leaf_label_checks=0, infeasible_instances=0)
    signatures = {}
    for n in range(3):
        for actions in product(range(8), repeat=1 << n):
            problem = Problem(actions, 3, (1,)*n)
            result, independent = compare(problem)
            census["instances"] += 1
            census["syntax_obligation_checks"] += independent["shapes"]
            census["admitted_shapes"] += independent["admitted"]
            census["leaf_label_checks"] += independent["leaf_label_checks"]
            census["infeasible_instances"] += not bool(result["profiles"])
            key = (n, result["gamma"])
            value = frozenset(result["profiles"])
            require(signatures.setdefault(key, value) == value, "equal Gamma changed profiles")
    intervals = tuple(sum(1 << a for a in range(lo, hi+1))
                      for lo in range(3) for hi in range(lo, 3))
    interval_groups = {}
    for actions in product(intervals, repeat=4):
        result, _ = compare(Problem(actions, 3, (1, 2)))
        require(result["gamma"] == graph_gamma(actions, 2), "interval pairwise repair failed")
        graph, profile = pair_graph(actions), frozenset(result["profiles"])
        require(interval_groups.setdefault(graph, profile) == profile, "same graph differs for intervals")
    weighted = 0
    for actions in product(range(4), repeat=4):
        for costs in ((0, 2), (F(1, 2), F(3, 2))):
            result, _ = compare(Problem(actions, 2, costs))
            for prior in ((F(1, 4),)*4, (F(1), F(0), F(0), F(0))):
                joint(result["profiles"], prior)
            weighted += 1
    # Sharp finite-alphabet obstruction: every proper subfamily intersects, the whole does not.
    for k in (3, 4):
        sets = tuple(((1 << k)-1) ^ (1 << i) for i in range(k))
        require(all(any(all(a & (1 << z) for a in group) for z in range(k))
                    for group in combinations(sets, k-1)), "proper subfamily conflict")
        require(not any(all(a & (1 << z) for a in sets) for z in range(k)), "full conflict missing")
    return {"schema": "relational-query-reconstruction-v1",
            "terminal": "RELATIONAL_QUERY_RECONSTRUCTION_FINITE_GREEN",
            "parent_subtraction": "immediate DRD/TDA/LQR specialization, no novelty claim",
            "census": census, "distinct_gamma_groups": len(signatures),
            "interval_instances": len(intervals)**4, "interval_pair_graph_groups": len(interval_groups),
            "weighted_zero_cost_instances": weighted, "witnesses": witnesses(),
            "scope": "finite labelled cube, fixed coordinate queries, output/controller costs excluded"}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
