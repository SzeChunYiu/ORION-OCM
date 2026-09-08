"""R0B Phase-2A prospective legal-feature audit; deliberately no ML.

The Phase-1 DP receives exact target-specific discovery/cost information for free.
This script keeps that full-information DP only as an exposed oracle, then asks how
much of its *cold-frontier entry decision* can be represented by frozen legal
pre-outcome feature schemas.  It reports decision collisions and the exact
feature-conditional regret floor before selector inference/training cost.

Scope is intentionally narrow: frontier f=0, known remaining horizon, i.i.d.
frozen demand.  This is an information audit, not a deployable selector result.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path

import regime_sweep as R


SCHEMAS = ("F0", "F1", "F2", "F3")
ACTIONS = ("inverse", "semantic")


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def _sign(value):
    return 1 if value > 0 else -1 if value < 0 else 0


def target_features(task, schema):
    """Frozen prospective task features.

    F0 contains no target-derived feature.  Horizon/frontier/resource coordinate
    are experiment state and are kept outside this tuple.  F3 uses the full task
    input only as an information-sufficiency upper bound; it is not a deployable
    memorization key.
    """
    if schema not in SCHEMAS:
        raise ValueError(f"unknown feature schema {schema!r}")
    if schema == "F0":
        return ()

    coefficients = task.coefficients
    signs = tuple(_sign(value) for value in coefficients)
    f1 = (
        len(coefficients) - 1,
        sum(value != 0 for value in coefficients),
        signs.count(1),
        signs.count(-1),
        signs.count(0),
    )
    if schema == "F1":
        return f1

    numerator_bits = tuple(abs(value.numerator).bit_length() for value in coefficients)
    denominator_bits = tuple(value.denominator.bit_length() for value in coefficients)
    f2 = f1 + (
        max(numerator_bits, default=0),
        max(denominator_bits, default=0),
        sum(numerator_bits),
        sum(denominator_bits),
        signs[0],
        signs[-1],
    )
    if schema == "F2":
        return f2

    # Identity-saturated information upper bound.  Do not treat this as a
    # generalizing selector feature or fit an evaluation-target lookup table.
    return f2 + tuple(str(value) for value in coefficients)


def target_feature_work(task, schema):
    """Explicit acquisition counters for the frozen deterministic summaries."""
    if schema not in SCHEMAS:
        raise ValueError(f"unknown feature schema {schema!r}")
    if schema == "F0":
        return Counter()

    width = len(task.coefficients)
    work = Counter({"feature_coefficient_visits": width, "feature_sign_tests": width})
    if schema in ("F2", "F3"):
        work.update({
            "feature_numerator_bit_length_reads": width,
            "feature_denominator_bit_length_reads": width,
            "feature_integer_accumulations": 2 * width,
        })
    if schema == "F3":
        work["feature_identity_key_coefficients"] += width
    return work


def _optimal_action(inverse_value, semantic_value):
    scale = max(1.0, abs(inverse_value), abs(semantic_value))
    if math.isclose(inverse_value, semantic_value, rel_tol=1e-12, abs_tol=1e-12 * scale):
        return "tie"
    return "inverse" if inverse_value < semantic_value else "semantic"


def cold_full_information_rows(tasks, profile, inverse, max_horizon=R.MAX_HORIZON):
    """Full-information DP labels at cold frontier f=0.

    State transitions are realizable: choosing inverse leaves the semantic
    frontier unchanged; choosing semantic advances it to max(f, R(q)).  The
    oracle remains nondeployable because exact R/I/K are supplied for free.
    """
    n = len(tasks)
    max_frontier = profile["frontier_transitions"]
    result = {}

    for coordinate in R.PHASE_COORDS:
        previous = [0.0] * (max_frontier + 1)
        horizon_rows = []
        for horizon in range(1, max_horizon + 1):
            current = [0.0] * (max_frontier + 1)
            cold_states = None
            for frontier in range(max_frontier + 1):
                future_same = previous[frontier]
                base_build = profile["build"][frontier].get(coordinate, 0)
                total = 0.0
                if frontier == 0:
                    cold_states = []
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
                    if frontier == 0:
                        cold_states.append({
                            "task": task,
                            "inverse": inverse_now,
                            "semantic": semantic_now,
                            "optimal": _optimal_action(inverse_now, semantic_now),
                        })
                current[frontier] = total / n
            previous = current
            if cold_states is None or len(cold_states) != n:
                raise AssertionError("cold-frontier DP labels were not recorded")
            horizon_rows.append({"horizon": horizon, "states": cold_states})
        result[coordinate] = horizon_rows
    return result


def audit_feature_partition(states, schema):
    """Exact best deterministic policy inside one frozen legal-feature partition."""
    buckets = defaultdict(list)
    for state in states:
        buckets[target_features(state["task"], schema)].append(state)

    collision_buckets = 0
    collision_states = 0
    inverse_only = semantic_only = ties = 0
    oracle_total = 0.0
    feature_conditional_total = 0.0

    for members in buckets.values():
        labels = {state["optimal"] for state in members}
        has_inverse_only = "inverse" in labels
        has_semantic_only = "semantic" in labels
        if has_inverse_only and has_semantic_only:
            collision_buckets += 1
            collision_states += len(members)

        inverse_only += sum(state["optimal"] == "inverse" for state in members)
        semantic_only += sum(state["optimal"] == "semantic" for state in members)
        ties += sum(state["optimal"] == "tie" for state in members)

        inverse_sum = sum(state["inverse"] for state in members)
        semantic_sum = sum(state["semantic"] for state in members)
        oracle_sum = sum(min(state["inverse"], state["semantic"]) for state in members)
        feature_conditional_total += min(inverse_sum, semantic_sum)
        oracle_total += oracle_sum

    regret = max(0.0, feature_conditional_total - oracle_total)
    n = len(states)
    return {
        "feature_buckets": len(buckets),
        "collision_buckets": collision_buckets,
        "collision_states": collision_states,
        "collision_state_fraction": collision_states / n if n else 0.0,
        "action_mass": {
            "inverse_only": inverse_only,
            "semantic_only": semantic_only,
            "tie": ties,
        },
        "oracle_expected_cost": oracle_total / n if n else 0.0,
        "best_feature_conditional_expected_cost": feature_conditional_total / n if n else 0.0,
        "regret_expected_cost": regret / n if n else 0.0,
        "regret_fraction_of_oracle": regret / oracle_total if oracle_total else 0.0,
    }


def summarize_rows(rows):
    summary = {}
    for coordinate, coordinate_rows in rows.items():
        summary[coordinate] = {}
        for schema in SCHEMAS:
            selected = [row["features"][schema] | {"horizon": row["horizon"]}
                        for row in coordinate_rows]
            max_collision = max(selected, key=lambda row: row["collision_state_fraction"])
            max_regret = max(selected, key=lambda row: row["regret_fraction_of_oracle"])
            zero_collision = [row["horizon"] for row in selected if row["collision_states"] == 0]
            summary[coordinate][schema] = {
                "max_collision_state_fraction": max_collision["collision_state_fraction"],
                "max_collision_horizon": max_collision["horizon"],
                "max_regret_fraction_of_oracle": max_regret["regret_fraction_of_oracle"],
                "max_regret_horizon": max_regret["horizon"],
                "zero_collision_horizons": zero_collision,
            }
    return summary


def summarize_feature_work(tasks):
    result = {}
    for schema in SCHEMAS:
        total = Counter()
        for task in tasks:
            total.update(target_feature_work(task, schema))
        result[schema] = {
            key: value / len(tasks)
            for key, value in sorted(total.items())
        }
    return result


def build_report(max_horizon=R.MAX_HORIZON):
    tasks, profile, inverse, _, _, _ = R.calibrate()
    labels = cold_full_information_rows(tasks, profile, inverse, max_horizon=max_horizon)
    rows = {}
    for coordinate, horizon_rows in labels.items():
        rows[coordinate] = []
        for horizon_row in horizon_rows:
            rows[coordinate].append({
                "horizon": horizon_row["horizon"],
                "features": {
                    schema: audit_feature_partition(horizon_row["states"], schema)
                    for schema in SCHEMAS
                },
            })

    return {
        "schema": "ocm.residual-strategy-regime.r0b.phase2a.cold.v1",
        "study": "Prospective legal-feature decision-collision audit; no ML",
        "scope": {
            "frontier": 0,
            "known_remaining_horizon": True,
            "max_horizon": max_horizon,
            "demand": "iid uniform frozen 142-target population",
            "resource_coordinates": list(R.PHASE_COORDS),
            "feature_schemas": list(SCHEMAS),
            "not_yet_tested": [
                "nonzero/reachable frontier feature partitions",
                "unknown-horizon online policy",
                "selector inference/training/update cost",
                "runtime admission lifecycle",
            ],
        },
        "feature_work_mean_per_query": summarize_feature_work(tasks),
        "rows": rows,
        "summary": summarize_rows(rows),
        "claim_boundary": {
            "full_information_oracle_deployable": False,
            "f3_is_information_upper_bound_only": True,
            "ml_authorized": False,
            "interpretation": (
                "A collision proves the frozen feature schema cannot exactly reproduce the "
                "full-information cold-entry decision. Zero collision does not prove a cheap "
                "generalizing selector exists, and this cold-frontier audit is not a complete "
                "state-aware policy study."
            ),
        },
        "terminal": "LEARNED_ROUTER_NOT_AUTHORIZED_R0B_PHASE2A_COLD_AUDIT",
    }


def _notice_payload(report):
    compact = {}
    for coordinate in R.PHASE_COORDS:
        compact[coordinate] = {
            schema: {
                "max_collision": round(
                    report["summary"][coordinate][schema]["max_collision_state_fraction"], 6
                ),
                "max_regret": round(
                    report["summary"][coordinate][schema]["max_regret_fraction_of_oracle"], 6
                ),
            }
            for schema in SCHEMAS
        }
    return compact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--max-horizon", type=int, default=R.MAX_HORIZON)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.max_horizon <= R.MAX_HORIZON:
        raise SystemExit(f"--max-horizon must be in 1..{R.MAX_HORIZON}")
    report = build_report(max_horizon=args.max_horizon)
    write_json(args.out, report)
    compact = {
        "terminal": report["terminal"],
        "summary": _notice_payload(report),
    }
    rendered = json.dumps(compact, sort_keys=True, separators=(",", ":"))
    if args.github_notice:
        print(f"::notice title=R0B Phase 2A cold feature audit::{rendered}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
