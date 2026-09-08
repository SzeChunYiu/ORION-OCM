"""R0B exact strategy-regime calibration: inverse search versus reusable semantic BFS.

This is deliberately a no-ML experiment.  It treats the two exact donor engines as
fixed strategies, derives a frontier-state metareasoning model, publishes raw
resource vectors, and computes a cost-informed oracle *upper bound* on the value
of per-query selection.  The oracle is not deployable: it receives exact per-task
costs and is used only to bound the residual that any legal selector could exploit.
"""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
from itertools import product
import json
from pathlib import Path
import random
import statistics

from ocm.learning import methods as M
from inverse_parent import InverseSession
from semantic_session import SemanticSearchSession

ROOT = Path(__file__).resolve().parent
PHASE_COORDS = ("transitions", "arithmetic_additions", "arithmetic_multiplications")
SEEDS = tuple(range(5201, 5209))
RESET_INTERVALS = (1, 2, 4, 8, 16, 32, 64, 142)
CHECKPOINT_INTERVALS = (4, 8, 16, 32, 64, 71)
MAX_HORIZON = 142


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def task_population():
    """All mathematical identities whose shortest primitive word has length four."""
    unique = {}
    for depth in range(5):
        for program in product(M.PRIMITIVES, repeat=depth):
            task = M.PolynomialTask("registered-polynomial", M.normal_form(program))
            unique.setdefault(task.fingerprint, (depth, task))
    tasks = tuple(task for _, (depth, task) in sorted(unique.items()) if depth == 4)
    if len(tasks) != 142:
        raise AssertionError(f"source drift: expected 142 depth-four identities, got {len(tasks)}")
    return tasks


def _snapshot(counter):
    return {key: int(value) for key, value in Counter(counter).items()}


def frontier_profile(tasks):
    """Expose the exact BFS build curve B(f), discovery rank R(q), and hit cost K(q).

    For PHASE_COORDS only, target lookups do not add work while the frontier is
    extended.  Therefore a stable semantic lifetime has exact cost
        B(max_q R(q)) + sum_q K(q)
    on those coordinates.  Other counters are still published but are not forced
    into this reduced identity.
    """
    task_by_coefficients = {task.coefficients: task for task in tasks}
    engine = SemanticSearchSession(4)
    ranks = {}
    build = [Counter(engine.work)]

    while len(ranks) < len(tasks):
        before_nodes = len(engine.nodes)
        if not engine._expand_one():  # research calibration of the frozen donor
            break
        build.append(Counter(engine.work))
        if len(engine.nodes) > before_nodes:
            coefficients = engine.nodes[-1][0]
            task = task_by_coefficients.get(coefficients)
            if task is not None:
                ranks[task.fingerprint] = engine.work["transitions"]

    if len(ranks) != len(tasks):
        raise AssertionError("semantic donor exhausted before covering the frozen population")
    if len(build) != engine.work["transitions"] + 1:
        raise AssertionError("build curve lost a transition")
    if max(ranks.values()) != engine.work["transitions"]:
        raise AssertionError("frozen target population no longer reaches the terminal frontier")

    hit = {}
    for task in tasks:
        result = engine.query(task, 0)
        if not result["verified"] or result["query_work"]["transitions"]:
            raise AssertionError("full semantic frontier did not answer as an exact zero-transition hit")
        hit[task.fingerprint] = Counter(result["query_work"])

    return {
        "ranks": ranks,
        "build": tuple(build),
        "hit": hit,
        "frontier_transitions": max(ranks.values()),
        "frontier_states": len(engine.nodes),
    }


def inverse_profile(tasks):
    """Exact target-directed cost vector I(q); no state is shared across queries."""
    engine = InverseSession(4)
    costs = {}
    for task in tasks:
        result = engine.query(task)
        if not result["verified"]:
            raise AssertionError("inverse donor failed a frozen reachable target")
        costs[task.fingerprint] = Counter(result["query_work"])
    return costs


def expected_static_rows(tasks, profile, inverse, max_horizon=MAX_HORIZON):
    """Exact finite-population i.i.d. expectation for the two static strategies."""
    n = len(tasks)
    ranked = sorted(tasks, key=lambda task: profile["ranks"][task.fingerprint])
    rows = []
    for horizon in range(1, max_horizon + 1):
        values = {"horizon": horizon, "semantic": {}, "inverse": {}, "difference_semantic_minus_inverse": {}}
        for coordinate in PHASE_COORDS:
            expected_build = 0.0
            for index, task in enumerate(ranked, start=1):
                probability = (index / n) ** horizon - ((index - 1) / n) ** horizon
                rank = profile["ranks"][task.fingerprint]
                expected_build += probability * profile["build"][rank].get(coordinate, 0)
            mean_hit = sum(profile["hit"][task.fingerprint].get(coordinate, 0) for task in tasks) / n
            mean_inverse = sum(inverse[task.fingerprint].get(coordinate, 0) for task in tasks) / n
            semantic = expected_build + horizon * mean_hit
            inverse_value = horizon * mean_inverse
            values["semantic"][coordinate] = semantic
            values["inverse"][coordinate] = inverse_value
            values["difference_semantic_minus_inverse"][coordinate] = semantic - inverse_value
        rows.append(values)
    return rows


def crossover_summary(rows):
    first_semantic_win = {}
    for coordinate in PHASE_COORDS:
        first = next(
            (row["horizon"] for row in rows
             if row["semantic"][coordinate] < row["inverse"][coordinate]),
            None,
        )
        first_semantic_win[coordinate] = first

    inverse_pareto_max = 0
    semantic_pareto_min = None
    for row in rows:
        differences = row["difference_semantic_minus_inverse"]
        if all(differences[c] > 0 for c in PHASE_COORDS):
            inverse_pareto_max = row["horizon"]
        if semantic_pareto_min is None and all(differences[c] < 0 for c in PHASE_COORDS):
            semantic_pareto_min = row["horizon"]
    return {
        "first_semantic_expected_win": first_semantic_win,
        "inverse_pareto_through_horizon": inverse_pareto_max,
        "semantic_pareto_from_horizon": semantic_pareto_min,
        "price_sensitive_band": (
            [inverse_pareto_max + 1, semantic_pareto_min - 1]
            if semantic_pareto_min is not None and semantic_pareto_min > inverse_pareto_max + 1
            else []
        ),
    }


def oracle_residual(tasks, profile, inverse, static_rows, max_horizon=MAX_HORIZON):
    """Cost-free task-aware DP upper-bound on residual selection value.

    The oracle sees exact R(q), I(q), K(q), and B(f) before choosing an arm.  A
    deployable policy does not get that information for free.  Hence any gain
    here is an upper bound before feature acquisition, inference, training, and
    maintenance are charged.
    """
    n = len(tasks)
    max_frontier = profile["frontier_transitions"]
    by_horizon = {row["horizon"]: row for row in static_rows}
    result = {}

    for coordinate in PHASE_COORDS:
        previous = [0.0] * (max_frontier + 1)
        rows = []
        best_gap = {"fraction": 0.0, "horizon": 1}
        for horizon in range(1, max_horizon + 1):
            current = [0.0] * (max_frontier + 1)
            for frontier in range(max_frontier + 1):
                future_same = previous[frontier]
                total = 0.0
                base_build = profile["build"][frontier].get(coordinate, 0)
                for task in tasks:
                    fingerprint = task.fingerprint
                    rank = profile["ranks"][fingerprint]
                    inverse_now = inverse[fingerprint].get(coordinate, 0) + future_same
                    next_frontier = max(frontier, rank)
                    semantic_now = (
                        profile["build"][next_frontier].get(coordinate, 0)
                        - base_build
                        + profile["hit"][fingerprint].get(coordinate, 0)
                        + previous[next_frontier]
                    )
                    total += min(inverse_now, semantic_now)
                current[frontier] = total / n
            previous = current
            static = by_horizon[horizon]
            best_static = min(static["semantic"][coordinate], static["inverse"][coordinate])
            oracle = current[0]
            gap = max(0.0, (best_static - oracle) / best_static) if best_static else 0.0
            rows.append({"horizon": horizon, "best_static": best_static, "oracle": oracle,
                         "residual_fraction": gap})
            if gap > best_gap["fraction"]:
                best_gap = {"fraction": gap, "horizon": horizon}
        result[coordinate] = {"max_residual": best_gap, "rows": rows}
    return result


def semantic_sequence(tasks, *, reset_every=None, checkpoint_every=None):
    if reset_every is not None and checkpoint_every is not None:
        raise ValueError("choose reset or checkpoint sweep, not both")
    engine = SemanticSearchSession(4)
    archived = Counter()
    for position, task in enumerate(tasks, start=1):
        result = engine.query(task, 200_000)
        if not result["verified"]:
            raise AssertionError("semantic donor failed a frozen target")
        if position == len(tasks):
            continue
        if reset_every is not None and position % reset_every == 0:
            engine.reset()
        if checkpoint_every is not None and position % checkpoint_every == 0:
            payload = engine.checkpoint()
            archived.update(engine.work)
            engine = SemanticSearchSession.restore(payload)
    total = archived + Counter(engine.work)
    persistent_bytes = len(json.dumps(engine._state(), sort_keys=True, separators=(",", ":")).encode())
    return {"work": total, "persistent_serialized_bytes": persistent_bytes}


def sum_inverse(tasks, inverse):
    total = Counter()
    peak = 0
    for task in tasks:
        work = inverse[task.fingerprint]
        peak = max(peak, work.get("peak_query_states", 0))
        total.update({key: value for key, value in work.items() if key != "peak_query_states"})
    total["peak_query_states"] = peak
    return total


def lifecycle_sweeps(tasks, profile, inverse):
    rows = []
    for seed in SEEDS:
        ordered = list(tasks)
        random.Random(seed).shuffle(ordered)
        inverse_total = sum_inverse(ordered, inverse)
        for interval in RESET_INTERVALS:
            semantic = semantic_sequence(ordered, reset_every=interval)
            expected_transitions = sum(
                max(profile["ranks"][task.fingerprint] for task in ordered[start:start + interval])
                for start in range(0, len(ordered), interval)
            )
            if semantic["work"]["transitions"] != expected_transitions:
                raise AssertionError("reset epoch frontier identity failed")
            rows.append({
                "kind": "reset", "seed": seed, "interval": interval,
                "semantic_work": _snapshot(semantic["work"]),
                "inverse_work": _snapshot(inverse_total),
                "semantic_persistent_serialized_bytes": semantic["persistent_serialized_bytes"],
                "expected_frontier_transitions": expected_transitions,
            })
        for interval in CHECKPOINT_INTERVALS:
            semantic = semantic_sequence(ordered, checkpoint_every=interval)
            rows.append({
                "kind": "checkpoint_replay", "seed": seed, "interval": interval,
                "semantic_work": _snapshot(semantic["work"]),
                "inverse_work": _snapshot(inverse_total),
                "semantic_persistent_serialized_bytes": semantic["persistent_serialized_bytes"],
            })
    return rows


def summarize_lifecycle(rows):
    out = {}
    for kind, intervals in (("reset", RESET_INTERVALS), ("checkpoint_replay", CHECKPOINT_INTERVALS)):
        out[kind] = {}
        for interval in intervals:
            selected = [row for row in rows if row["kind"] == kind and row["interval"] == interval]
            out[kind][str(interval)] = {}
            for coordinate in PHASE_COORDS:
                semantic_values = [row["semantic_work"].get(coordinate, 0) for row in selected]
                inverse_values = [row["inverse_work"].get(coordinate, 0) for row in selected]
                out[kind][str(interval)][coordinate] = {
                    "semantic_median": statistics.median(semantic_values),
                    "semantic_min": min(semantic_values),
                    "semantic_max": max(semantic_values),
                    "inverse_median": statistics.median(inverse_values),
                    "semantic_minus_inverse_median":
                        statistics.median(s - i for s, i in zip(semantic_values, inverse_values)),
                }
    return out


@lru_cache(maxsize=1)
def calibrate():
    tasks = task_population()
    profile = frontier_profile(tasks)
    inverse = inverse_profile(tasks)
    static_rows = expected_static_rows(tasks, profile, inverse)
    crossover = crossover_summary(static_rows)
    oracle = oracle_residual(tasks, profile, inverse, static_rows)
    return tasks, profile, inverse, static_rows, crossover, oracle


def build_report(include_lifecycle=True):
    tasks, profile, inverse, static_rows, crossover, oracle = calibrate()
    report = {
        "schema": "ocm.residual-strategy-regime.r0b.v1",
        "study": "R0B exact lifetime strategy regime; no ML",
        "population": {
            "targets": len(tasks),
            "shortest_primitive_length": 4,
            "frontier_transitions": profile["frontier_transitions"],
            "frontier_states": profile["frontier_states"],
            "discovery_ranks_unique": len(set(profile["ranks"].values())),
        },
        "formal_reduction": {
            "coordinates": list(PHASE_COORDS),
            "stable_semantic":
                "B_r(max_i R(q_i)) + sum_i K_r(q_i)",
            "inverse":
                "sum_i I_r(q_i)",
            "reset_epochs":
                "sum_e B_r(max_{i in e} R(q_i)) + sum_i K_r(q_i)",
            "scope":
                "Exact on the declared phase coordinates for the frozen semantic donor; all other raw counters remain unsimplified.",
        },
        "iid_static": {
            "crossover": crossover,
            "rows": static_rows,
        },
        "cost_informed_oracle": {
            coordinate: {
                "max_residual": value["max_residual"],
                "rows": value["rows"],
            }
            for coordinate, value in oracle.items()
        },
        "claim_boundary": {
            "selector_is_deployable": False,
            "selector_cost_charged": False,
            "ml_authorized": False,
            "protected_143_run": False,
            "runtime_admission_lifecycle": "NOT_RUN_IN_THIS_TRANCHE",
            "interpretation":
                "The oracle is a residual upper bound. A legal selector must acquire predictive features and pay all policy costs.",
        },
        "terminal": "LEARNED_ROUTER_NOT_AUTHORIZED_R0B_PHASE1",
    }
    if include_lifecycle:
        lifecycle = lifecycle_sweeps(tasks, profile, inverse)
        report["lifecycle"] = {
            "seeds": list(SEEDS),
            "raw": lifecycle,
            "summary": summarize_lifecycle(lifecycle),
        }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--skip-lifecycle", action="store_true")
    args = parser.parse_args()
    report = build_report(include_lifecycle=not args.skip_lifecycle)
    write_json(args.out, report)
    print(json.dumps({
        "terminal": report["terminal"],
        "population": report["population"],
        "crossover": report["iid_static"]["crossover"],
        "oracle_max_residual": {
            coordinate: value["max_residual"]
            for coordinate, value in report["cost_informed_oracle"].items()
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
