#!/usr/bin/env python3
"""Exact hostile checks for planning reachability semantics and PSR-ID correction V1."""
from __future__ import annotations

import argparse
import json
import re
from functools import lru_cache
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLAIMS = ROOT / "PLANNING_SEMANTIC_RESOLUTION_CLAIMS_V1.md"
THEOREM = ROOT / "PLANNING_SEMANTIC_RESOLUTION_THEOREM_V1.md"
CORRECTION = ROOT / "PLANNING_REACHABILITY_SEMANTICS_AND_ID_CORRECTION_V1.md"


def partitions(n: int):
    """Enumerate set partitions as restricted-growth strings."""
    if n <= 0:
        yield ()
        return
    labels = [0] * n

    def rec(i: int, maximum: int):
        if i == n:
            yield tuple(labels)
            return
        for value in range(maximum + 2):
            labels[i] = value
            yield from rec(i + 1, max(maximum, value))

    labels[0] = 0
    yield from rec(1, 0)


def is_goal_respecting_right_congruence(labels, transition, goals, states, actions):
    for s in states:
        for t in states:
            if labels[s] != labels[t]:
                continue
            if (s in goals) != (t in goals):
                return False
            for action in actions:
                if labels[transition[(s, action)]] != labels[transition[(t, action)]]:
                    return False
    return True


def ground_solvers(transition, goals, actions):
    @lru_cache(maxsize=None)
    def exact(state, horizon):
        if horizon == 0:
            return state in goals
        return any(exact(transition[(state, action)], horizon - 1) for action in actions)

    @lru_cache(maxsize=None)
    def bounded(state, horizon):
        if state in goals:
            return True
        if horizon == 0:
            return False
        return any(bounded(transition[(state, action)], horizon - 1) for action in actions)

    return exact, bounded


def quotient_solvers(labels, transition, goals, states, actions):
    representative = {}
    for state in states:
        representative.setdefault(labels[state], state)

    qtransition = {
        (cell, action): labels[transition[(rep, action)]]
        for cell, rep in representative.items()
        for action in actions
    }
    qgoals = {labels[state] for state in goals}

    @lru_cache(maxsize=None)
    def exact(cell, horizon):
        if horizon == 0:
            return cell in qgoals
        return any(exact(qtransition[(cell, action)], horizon - 1) for action in actions)

    @lru_cache(maxsize=None)
    def bounded(cell, horizon):
        if cell in qgoals:
            return True
        if horizon == 0:
            return False
        return any(bounded(qtransition[(cell, action)], horizon - 1) for action in actions)

    return qtransition, exact, bounded


def exhaustive_semantics_checks():
    counts = {
        "transition_tables": 0,
        "valid_quotients": 0,
        "n2_valid_quotients": 0,
        "n3_valid_quotients": 0,
        "value_equalities_checked": 0,
        "first_action_equalities_checked": 0,
        "exact_vs_bounded_divergent_cells": 0,
    }

    for n in (2, 3):
        states = tuple(range(n))
        actions = (0, 1)
        for successors in product(states, repeat=n * len(actions)):
            transition = {
                (state, action): successors[state * len(actions) + action]
                for state in states
                for action in actions
            }
            counts["transition_tables"] += 1

            for mask in range(1 << n):
                goals = {state for state in states if (mask >> state) & 1}
                ground_exact, ground_bounded = ground_solvers(transition, goals, actions)

                for labels in partitions(n):
                    if not is_goal_respecting_right_congruence(
                        labels, transition, goals, states, actions
                    ):
                        continue

                    counts["valid_quotients"] += 1
                    counts[f"n{n}_valid_quotients"] += 1
                    qtransition, qexact, qbounded = quotient_solvers(
                        labels, transition, goals, states, actions
                    )

                    for horizon in range(4):
                        for state in states:
                            exact_value = ground_exact(state, horizon)
                            bounded_value = ground_bounded(state, horizon)

                            assert exact_value == qexact(labels[state], horizon)
                            assert bounded_value == qbounded(labels[state], horizon)
                            counts["value_equalities_checked"] += 2

                            if exact_value != bounded_value:
                                counts["exact_vs_bounded_divergent_cells"] += 1

                            if horizon == 0 or state in goals:
                                continue

                            exact_actions = tuple(
                                action
                                for action in actions
                                if ground_exact(transition[(state, action)], horizon - 1)
                            )
                            qexact_actions = tuple(
                                action
                                for action in actions
                                if qexact(qtransition[(labels[state], action)], horizon - 1)
                            )
                            bounded_actions = tuple(
                                action
                                for action in actions
                                if ground_bounded(transition[(state, action)], horizon - 1)
                            )
                            qbounded_actions = tuple(
                                action
                                for action in actions
                                if qbounded(qtransition[(labels[state], action)], horizon - 1)
                            )

                            assert exact_actions == qexact_actions
                            assert bounded_actions == qbounded_actions
                            counts["first_action_equalities_checked"] += 2

    return counts


def canonical_divergence_witness():
    states = (0, 1)  # 0 = goal g, 1 = bad b
    actions = (0,)
    transition = {(0, 0): 1, (1, 0): 1}
    goals = {0}
    exact, bounded = ground_solvers(transition, goals, actions)
    witness = {
        "exact_horizon_1_from_goal": exact(0, 1),
        "bounded_horizon_1_from_goal": bounded(0, 1),
    }
    assert witness == {
        "exact_horizon_1_from_goal": False,
        "bounded_horizon_1_from_goal": True,
    }
    return witness


def document_audit():
    claims = CLAIMS.read_text(encoding="utf-8")
    theorem = THEOREM.read_text(encoding="utf-8")
    correction = CORRECTION.read_text(encoding="utf-8")

    claim_ids = re.findall(r"\|\s*(PSR-\d+)\s*\|", claims)
    theorem_labels = re.findall(r"\*\*(PSR-\d+)\s+—", theorem)
    correction_ids = re.findall(r"\|\s*`(PSR-\d+)`\s*\|", correction)

    expected = [f"PSR-{i}" for i in range(1, 6)]
    legacy_drift_detected = (
        claim_ids == expected
        and theorem_labels == ["PSR-1", "PSR-2", "PSR-3"]
        and "PSR-3 — Semantic Quotient Planning Theorem" in theorem
        and "PSR-3" in claims
        and "information and planning transformation cost can separate exponentially" in claims
    )
    correction_complete = correction_ids == expected

    return {
        "claims_ids": claim_ids,
        "legacy_theorem_labels": theorem_labels,
        "canonical_correction_ids": correction_ids,
        "legacy_identifier_drift_detected": legacy_drift_detected,
        "canonical_correction_complete": correction_complete,
    }


def run():
    semantics = exhaustive_semantics_checks()
    witness = canonical_divergence_witness()
    docs = document_audit()

    expected_semantics = {
        "transition_tables": 745,
        "valid_quotients": 10086,
        "n2_valid_quotients": 96,
        "n3_valid_quotients": 9990,
        "value_equalities_checked": 241296,
        "first_action_equalities_checked": 90486,
        "exact_vs_bounded_divergent_cells": 3820,
    }

    ok = semantics == expected_semantics
    ok = ok and witness["exact_horizon_1_from_goal"] is False
    ok = ok and witness["bounded_horizon_1_from_goal"] is True
    ok = ok and docs["legacy_identifier_drift_detected"]
    ok = ok and docs["canonical_correction_complete"]

    return {
        "terminal": (
            "GRAND_GMI_PLANNING_REACHABILITY_SEMANTICS_CORRECTION_ALL_GREEN"
            if ok
            else "GRAND_GMI_PLANNING_REACHABILITY_SEMANTICS_CORRECTION_RED"
        ),
        "all_checks_green": ok,
        "determinism": "exact-exhaustive-no-rng",
        "semantics": semantics,
        "canonical_divergence_witness": witness,
        "document_audit": docs,
        "scope": "finite deterministic total-action systems, n in {2,3}, horizons 0..3",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
