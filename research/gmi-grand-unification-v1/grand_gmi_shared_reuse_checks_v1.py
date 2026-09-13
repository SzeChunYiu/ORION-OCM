"""Decisive shared-dependency witnesses plus exact adaptive-policy census."""
import json
from pathlib import Path
import sys
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
sys.path.insert(0, str(Path(__file__).resolve().parent))
from grand_gmi_shared_reuse_model_v1 import Register, distances, graph, mass, solve
from grand_gmi_shared_reuse_oracle_v1 import execute_synthesized, policy_oracle, simple_traces


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def shared_register():
    return Register((0, 1, 1), (1, 1, 1), (4, 1, 1), (0, 1, 1), (0, 0, 0), (0, 0, 0))


def hazards(intervals, seeds=0, q=F(0)):
    return (((0, 1-q), (seeds, q)),)*intervals


def configuration_census():
    pairs = traces_checked = 0
    for p1, p2, memory in product(range(2), range(4), (1, 2, 3)):
        model = Register((0, p1, p2), (1, 1, 1), (1, 2, 3), (1, 1, 1), (0, 0, 0), (F(1, 4),)*3)
        states, edges = graph(model, memory)
        actual, _, _ = distances(states, edges)
        for start in states:
            oracle = {}
            initial = frozenset(v for v in range(3) if start & (1 << v))
            for actions, resident in simple_traces(model, memory, initial):
                target = sum(1 << v for v in resident)
                cost = sum((F(model.build[v] if action == "build" else model.release[v])
                            for action, v in actions), F(0))
                oracle[target] = min(oracle.get(target, cost), cost)
                traces_checked += 1
            require(actual[start] == oracle, "shared-DAG shortest paths disagree with explicit traces")
            pairs += len(states)
    return {"topologically_indexed_three_node_DAGs": 8, "memory_values": 3,
            "configuration_pair_comparisons": pairs, "simple_action_traces": traces_checked}


def adaptive_census():
    count = trees = executions = feasible = 0
    for parents, memory, alternative, q in product(((0, 0), (0, 1)), (1, 2), (False, True), (F(0), F(1, 2), F(1))):
        model = Register(parents, (1, 1), (0, 1) if alternative else (2, 1),
                         (1, 1), (0, 0), (F(1, 4),)*2 if alternative else (0, 0),
                         holding=F(1, 4) if alternative else F(0), observe=F(1, 4) if alternative else F(0))
        events = hazards(1, 1, q)
        oracle = policy_oracle(model, memory, (1, 1), events)
        for objective in ("expected", "worstcase"):
            result = solve(model, memory, (1, 1), events, objective=objective)
            require(result["value"] == oracle[objective], "exact adaptive parent disagrees with configuration DP")
            if result["value"] is not None:
                actual = execute_synthesized(model, memory, (1, 1), events, result)
                require(actual[objective] == result["value"] and actual["peak"] <= memory,
                        "constructed policy has wrong path costs or workspace")
        count += 1
        feasible += oracle["expected"] is not None
        trees += oracle["policies"]
        executions += oracle["policies"]*oracle["histories"]
    return {"instances": count, "feasible_instances": feasible, "infeasible_instances": count-feasible,
            "complete_policy_trees": trees, "direct_history_executions": executions,
            "expected_matches": count, "support_worstcase_matches": count}


def run():
    model, requests = shared_register(), (1, 2, 1, 2)
    states2, edges2 = graph(model, 2)
    dist2, _, _ = distances(states2, edges2)
    states3, edges3 = graph(model, 3)
    dist3, _, _ = distances(states3, edges3)
    require(mass(model, 6) == 2 and 6 not in dist2[0], "independent-cache reachability falsifier lost")
    require(dist3[0][6] == 6 and dist3[0][2]+dist3[0][4] == 10,
            "shared acquisition was charged independently")
    require(solve(model, 1, requests, hazards(3))["value"] is None, "operand/output coexistence bypassed")
    witnesses = []
    expected = {(2, F(0)): F(12), (3, F(0)): F(10), (2, F(1, 2)): F(18),
                (3, F(1, 2)): F(35, 2), (2, F(1)): F(24), (3, F(1)): F(24)}
    for memory, q in product((2, 3), (F(0), F(1, 2), F(1))):
        events = hazards(3, 1, q)
        result = solve(model, memory, requests, events)
        actual = execute_synthesized(model, memory, requests, events, result)
        require(result["value"] == actual["expected"] == expected[memory, q], "shared lifetime witness cost changed")
        robust = solve(model, memory, requests, events, objective="worstcase")
        checked = execute_synthesized(model, memory, requests, events, robust)
        require(robust["value"] == checked["worstcase"], "robust policy failed support path")
        witnesses.append({"memory": memory, "root_hazard": str(q), "optimal_expected_work": str(result["value"]),
                          "optimal_support_worstcase_work": str(robust["value"]),
                          "constructed_peak": actual["peak"], "event_histories": actual["histories"],
                          "development_operations": result["development"]})
    fresh = solve(model, 2, requests, hazards(3), release_all=True)
    require(fresh["value"] == 24, "matched forced-release reference changed")
    leaf = solve(model, 2, (1, 1), hazards(1, 2, F(1)))
    root = solve(model, 2, (1, 1), hazards(1, 1, F(1)))
    require((leaf["value"], root["value"]) == (8, 12), "shared-scaffold repair or descendant invalidation failed")
    require(solve(replace(model, admitted=0b110), 3, (1,), ())["value"] is None,
            "unadmitted root acquisition supplied a certificate")
    prefetch_model = replace(model, sizes=(2, 1, 1), holding=F(1))
    prefetch = solve(prefetch_model, 3, (1, 2), hazards(1))
    require(prefetch["value"] == 9 and ("build", 2) in prefetch["policy"][0, 0][2],
            "post-service prefetch was omitted from the adaptive parent")
    require(execute_synthesized(prefetch_model, 3, (1, 2), hazards(1), prefetch)["expected"] == 9,
            "prefetch program failed direct execution")
    return {"schema": "shared-dependency-reuse-v1", "all_checks_green": True,
            "terminal": "SHARED_DEPENDENCY_MEMORY_REUSE_FINITE_GREEN",
            "knapsack_counterexample": {"leaf_cache_size": 2, "available_memory": 2,
                "leaf_cache_reachable_from_empty": False, "reachable_at_memory_3": True,
                "joint_acquisition_work_at_3": "6", "sum_independent_acquisitions": "10"},
            "witnesses": witnesses, "forced_release_reference_work": str(fresh["value"]),
            "post_service_prefetch_work": "9", "release_only_after_service_control_work": "10",
            "leaf_invalidation_repair_work": str(leaf["value"]),
            "root_invalidation_rebuild_work": str(root["value"]), "adaptive_oracle": adaptive_census(),
            "configuration_oracle": configuration_census(),
            "scope": "authored deterministic certified-DAG operations; observed interval invalidation; non-sliding operand/output/workspace memory; exact expected and support-worstcase policies",
            "cost_scope": "build/certification, service, release, holding and observation work; controller/code/base workspace reserved separately; development counters are explicit categories, not total CPU instructions"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
