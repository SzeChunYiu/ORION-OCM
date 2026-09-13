"""Fixed unknown versus rectangularly changing models: exact finite receipt."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fractions import Fraction as F
from itertools import product
import json
from unknown_model_frontier_v1 import Action, Model, frontier, successful_costs, rectangular, posterior
from unknown_model_mixtures_v1 import minimax_mixture, charged_minimax
from unknown_model_oracle_v1 import fixed_points, independent_frontier, switching, execute


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def apparatus(reset=True, fallback=True, reset_cost=1):
    # M=0, blocked=1, ready=2, stopped success=3.
    def row(target):
        return tuple(F(t == target) for t in range(4))
    a = Action("a", F(1), (row(2), row(1)))
    b = Action("b", F(1), (row(1), row(2)))
    certify = Action("fallback", F(5), (row(2), row(2)))
    redraw = Action("reset_preserves_model", F(reset_cost), (row(0), row(0)))
    finish = Action("finish", F(1), (row(3), row(3)))
    return Model(((a, b)+((certify,) if fallback else ()),
                  ((redraw,) if reset else ())+((certify,) if fallback else ()),
                  (finish,), ()), 2, 3, (F(1), F(1), F(1), F(0)))


def check(model, horizon):
    actual = frontier(model, horizon)
    expected, count = fixed_points(model, horizon)
    require(set(actual["points"]) == independent_frontier(expected), "full model vector frontier mismatch")
    for point, tree in actual["points"].items():
        outcomes = [execute(model, tree, theta=j)[0] for j in range(model.models)]
        require(point == tuple(x[0] for x in outcomes)+tuple(x[1] for x in outcomes), "constructed common tree failed direct execution")
    return actual, count


def census():
    cases = trees = paths = switches = 0
    for probabilities in product((F(0), F(1, 2), F(1)), repeat=4):
        actions = tuple(Action(str(a), F(a+1), tuple((1-probabilities[2*a+j], probabilities[2*a+j]) for j in range(2))) for a in range(2))
        model = Model((actions, ()), 2, 1, (F(1), F(0)))
        _, count = check(model, 3)
        robust, oracle = rectangular(model, 3), switching(model, 3)
        require(all(robust[k] == oracle[k] for k in robust), "rectangular minimax not matched to complete nature register")
        cases += 1
        trees += count["common_trees"]
        paths += count["fixed_model_path_executions"]
        switches += oracle["nature_table_assignments"]
    return dict(rational_two_model_kernels=cases, common_policy_trees=trees,
                fixed_model_terminal_path_executions=paths, changing_model_nature_tables=switches)


def run():
    model = apparatus()
    result, count = check(model, 4)
    costs = successful_costs(result["points"], 2)
    require(costs == ((F(2), F(4)), (F(4), F(2))), "fixed-model successful frontier changed")
    mix = minimax_mixture(costs)
    require(min(map(max, costs)) == 4 and mix["value"] == 3, "deterministic/private-mixture minimax mismatch")
    require(mix["mixture"] == ((0, F(1, 2)), (1, F(1, 2))), "fair mixture certificate missing")
    robust, nature = rectangular(model, 4), switching(model, 4)
    require(robust["successful_minimax_work"] == 6 and all(robust[k] == nature[k] for k in robust), "changing-model fallback control incorrect")
    no_reset, _ = check(apparatus(reset=False), 4)
    no_reset_costs = successful_costs(no_reset["points"], 2)
    require(min(map(max, no_reset_costs)) == 6 and minimax_mixture(no_reset_costs)["value"] == F(9, 2), "strong no-reset comparator omitted a policy")
    require(charged_minimax(costs, F(1, 4)) == F(13, 4), "sampler setup omitted")
    require(charged_minimax(no_reset_costs, F(1, 4)) == F(19, 4), "no-reset sampler setup omitted")
    no_fallback, _ = check(apparatus(fallback=False), 4)
    require(successful_costs(no_fallback["points"], 2) == costs, "fixed-model completion needs no fallback")
    require(rectangular(apparatus(fallback=False), 4)["minimum_worst_failure"] == 1, "switched models incorrectly inherit acquired identification")
    require(posterior((F(1, 2), F(1, 2)), (0, 1)) == (0, 1), "failed a did not identify fixed theta1")
    require(posterior((0, 1), (1, 1)) == (0, 1), "reset erased model information")
    short, _ = check(model, 3)
    require(min(map(max, successful_costs(short["points"], 2))) == 6, "finish received an uncharged horizon slot")
    return dict(schema="fixed-unknown-model-acquisition-v1", all_checks_green=True,
                terminal="FIXED_UNKNOWN_MODEL_ACQUISITION_FINITE_GREEN", horizon_charged_controls=4,
                successful_cost_vectors=[[str(x) for x in v] for v in costs],
                fixed_model_deterministic_minimax="4", fixed_model_private_randomized_minimax="3",
                private_sampler_setup_work="1/4", fixed_model_including_sampler_minimax="13/4",
                changing_model_minimax="6", no_reset_deterministic_minimax="6",
                no_reset_private_randomized_minimax="9/2", no_reset_including_sampler_minimax="19/4",
                no_fallback_changing_model_success="0", deadline3_deterministic_minimax="6",
                witness_policy_oracle=count, witness_nature_tables=nature["nature_table_assignments"],
                frontier_development=result["development"], mixture_development=mix["development"], census=census(),
                scope="finite supplied model hypotheses; one fixed hidden kernel; full observed physical state; finite-horizon common history policies; nature before private seed",
                cost_scope="probe, reset, fallback, explicit finish, deadline-abort and declared sampler setup work; model acquisition/confidence, representation and controller implementation are separate")


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
