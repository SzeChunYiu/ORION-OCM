"""Exact partition reconstruction receipt with independent exhaustive tree syntax."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import json
from fractions import Fraction as F
from grand_gmi_query_partition_model_v1 import canonical, optimize, pointwise_frontier, feasible, execute, pareto
from grand_gmi_query_partition_oracle_v1 import oracle, partitions, executed_shapes


def require(value, message):
    if not value:
        raise AssertionError(message)


def check_instance(table, costs, prior):
    result = optimize(table, costs, prior)
    front = pointwise_frontier(table, costs)["frontier"]
    independent = oracle(table, costs)
    require(front == independent["frontier"], "pointwise frontier disagrees with complete syntax oracle")
    require(result["mean"] == min(sum(p*c for p, c in zip(prior, v)) for v in front), "mean mismatch")
    require(result["worst"] == min(max(v) for v in front), "worstcase mismatch")
    n = len(costs)
    for key, expected in (("mean_tree", result["mean"]), ("worst_tree", result["worst"])):
        actual = [execute(result[key], x, n, costs) for x in range(1 << n)]
        require(tuple(a[0] for a in actual) == canonical(table), "constructed tree output incorrect")
        bill = sum(prior[x]*actual[x][1] for x in range(1 << n)) if key == "mean_tree" else max(a[1] for a in actual)
        require(bill == expected, "constructed tree cost incorrect")
    return independent


def census():
    instances = syntax_checks = admitted = 0
    by_n = {}
    for n in range(4):
        count = 0
        for table in partitions(1 << n):
            costs, prior = (F(1),)*n, (F(1, 1 << n),)*(1 << n)
            result = check_instance(table, costs, prior)
            renamed = tuple(7+11*x for x in table)
            require(canonical(renamed) == table, "injective relabelling changed the partition")
            require(optimize(renamed)["mean"] == optimize(table)["mean"], "relabelling changed query optimum")
            instances += 1
            count += 1
            syntax_checks += result["shapes"]
            admitted += result["admitted"]
        by_n[str(n)] = count
    weighted = 0
    for table in partitions(4):
        for costs in ((0, 2), (1, 3)):
            for prior in ((F(1, 4),)*4, (F(1), F(0), F(0), F(0))):
                check_instance(table, costs, prior)
                weighted += 1
    return dict(all_labelled_partitions=instances, partitions_by_dimension=by_n,
                obligation_tree_syntax_checks=syntax_checks, admitted_exact_trees=admitted,
                extra_weighted_or_zero_mass_instances=weighted,
                unique_unit_cost_syntax_input_executions=sum(len(executed_shapes(n, (F(1),)*n))*(1 << n) for n in range(4)))


def run():
    mux = (0, 0, 1, 1, 0, 1, 0, 1)
    costs, prior = (1, 2, 3), tuple(F(x, 15) for x in (1, 1, 1, 1, 1, 1, 1, 8))
    result = optimize(mux, costs, prior)
    profile_result = pointwise_frontier(mux, costs)
    front = profile_result["frontier"]
    joint = pareto((sum(p*c for p, c in zip(prior, v)), max(v)) for v in front)
    require(joint == {(F(19, 5), F(6)), (F(64, 15), F(5))}, "selector joint frontier changed")
    require(not feasible(front, prior, result["mean"], result["worst"]), "separate minima falsely certified a common tree")
    projection, parity = (0, 1, 0, 1), (0, 1, 1, 0)
    require(sorted(projection.count(i) for i in (0, 1)) == sorted(parity.count(i) for i in (0, 1)), "abstract partition control not matched")
    require((optimize(projection)["worst"], optimize(parity)["worst"]) == (1, 2), "unlabelled partition falsely reconstructs queries")
    or2 = (0, 1, 1, 1)
    require((optimize(or2)["mean"], optimize(parity)["mean"]) == (F(3, 2), F(2)), "FPW contrast changed")
    require(optimize(parity, prior=(1, 0, 0, 0))["mean"] == 2, "zero prior erased all-input correctness")
    require(optimize(or2, (1, 3))["mean"] == F(5, 2), "query cost register omitted")
    require(optimize(or2, prior=(0, 0, 0, 1))["mean"] == 1, "prior dependency omitted")
    return dict(schema="labelled-partition-query-reconstruction-v1", all_checks_green=True,
                terminal="LABELLED_PARTITION_QUERY_RECONSTRUCTION_FINITE_GREEN",
                oracle=census(), selector_joint_frontier=[[str(x), str(y)] for x, y in sorted(joint)],
                selector_separate_minima_feasible=False, selector_development=result["development"],
                selector_profile_development=profile_result["development"], selector_pointwise_frontier_size=len(front),
                unlabelled_balanced_partition_worstcase=["1", "2"], equal_width_or_parity_mean=["3/2", "2"],
                scope="exact deterministic coordinate queries on a fixed labelled Boolean cube; supplied complete output partition, rational costs/prior; free output relabelling",
                cost_scope="query costs only; explicit development operation categories; partition, solver/controller/code and output representation are separately charged")


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
