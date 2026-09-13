#!/usr/bin/env python3
"""Exact finite checks for CONTROLLED_ACQUISITION_INFORMATION_STATE_THEOREM_V1.

No RNG, no fitted thresholds, no external dependencies.
"""

from __future__ import annotations

import json
from functools import lru_cache
from itertools import product

INF = 10**9
ENTRIES = (None, (0, 0), (0, 1), (1, 0), (1, 1))


def common_actions(info_state, accepts):
    common = None
    for pair in info_state:
        actions = set(accepts[pair])
        common = actions if common is None else common & actions
    return frozenset(common or ())


def pair_value_from(info_state, kernel, accepts, horizon):
    @lru_cache(None)
    def value(info_tuple, h):
        info = frozenset(info_tuple)
        if common_actions(info, accepts):
            return 0
        if h == 0:
            return INF
        best = INF
        for test in range(len(kernel)):
            by_observation = {}
            legal = True
            for world, state in info:
                entry = kernel[test][2 * world + state]
                if entry is None:
                    legal = False
                    break
                observation, next_state = entry
                by_observation.setdefault(observation, set()).add((world, next_state))
            if not legal:
                continue
            worst = max(
                value(tuple(sorted(successor)), h - 1)
                for successor in by_observation.values()
            )
            if worst < INF:
                best = min(best, 1 + worst)
        return best

    return value(tuple(sorted(info_state)), horizon)


def pair_value(kernel, accepts, horizon):
    return pair_value_from(frozenset(((0, 0), (1, 0))), kernel, accepts, horizon)


def explicit_history_value(kernel, accepts, horizon):
    initial = ((0, 0, ()), (1, 0, ()))

    def recurse(trajectories, h):
        info = frozenset((world, state) for world, state, _ in trajectories)
        if common_actions(info, accepts):
            return 0
        if h == 0:
            return INF
        best = INF
        for test in range(len(kernel)):
            by_observation = {}
            legal = True
            for world, state, history in trajectories:
                entry = kernel[test][2 * world + state]
                if entry is None:
                    legal = False
                    break
                observation, next_state = entry
                by_observation.setdefault(observation, []).append(
                    (world, next_state, history + ((test, observation),))
                )
            if not legal:
                continue
            worst = max(
                recurse(tuple(successor), h - 1)
                for successor in by_observation.values()
            )
            if worst < INF:
                best = min(best, 1 + worst)
        return best

    return recurse(initial, horizon)


def exhaustive_pair_vs_history():
    exact_world_actions = {
        (world, state): frozenset({world})
        for world in (0, 1)
        for state in (0, 1)
    }
    value_counts = {"1": 0, "2": 0, "INF": 0}
    checked = 0
    mismatches = 0

    for flat in product(ENTRIES, repeat=8):
        kernel = (flat[:4], flat[4:])
        pair = pair_value(kernel, exact_world_actions, 2)
        history = explicit_history_value(kernel, exact_world_actions, 2)
        checked += 1
        if pair != history:
            mismatches += 1
            raise AssertionError((flat, pair, history))
        if pair >= INF:
            value_counts["INF"] += 1
        else:
            value_counts[str(pair)] += 1

    assert checked == 5**8 == 390625
    assert value_counts == {"1": 210000, "2": 60944, "INF": 119681}
    return {
        "kernels_checked": checked,
        "mismatches": mismatches,
        "value_counts": value_counts,
    }


def destructive_probe_counterexample():
    exact_world_actions = {
        (world, state): frozenset({world})
        for world in (0, 1)
        for state in (0, 1)
    }
    # Test 0 reveals the world, but only while state==fresh(0).
    # Test 1 emits observation 0 and irreversibly moves to burned(1).
    kernel = (
        ((0, 0), None, (1, 0), None),
        ((0, 1), (0, 1), (0, 1), (0, 1)),
    )
    fresh = frozenset(((0, 0), (1, 0)))
    burned = frozenset(((0, 1), (1, 1)))
    fresh_value = pair_value_from(fresh, kernel, exact_world_actions, 2)
    burned_value = pair_value_from(burned, kernel, exact_world_actions, 2)
    assert {w for w, _ in fresh} == {w for w, _ in burned} == {0, 1}
    assert fresh_value == 1
    assert burned_value >= INF
    return {
        "same_world_support": True,
        "world_support": [0, 1],
        "fresh_value": 1,
        "burned_value": "INF",
        "terminal": "WORLD_SUPPORT_ALONE_INSUFFICIENT_FOR_CONTROLLED_ACQUISITION",
    }


def control_to_compatibility_witness():
    accepts = {
        (0, 0): frozenset({0}),
        (1, 0): frozenset({1}),
        (0, 1): frozenset({2}),
        (1, 1): frozenset({2}),
    }
    # One uninformative transformation sends both worlds to state 1.
    kernel = (((0, 1), None, (0, 1), None),)
    before = frozenset(((0, 0), (1, 0)))
    after = frozenset(((0, 1), (1, 1)))
    value = pair_value(kernel, accepts, 1)
    assert not common_actions(before, accepts)
    assert common_actions(after, accepts) == frozenset({2})
    assert {w for w, _ in before} == {w for w, _ in after} == {0, 1}
    assert value == 1
    return {
        "world_support_before": [0, 1],
        "world_support_after": [0, 1],
        "terminal_before": False,
        "terminal_after": True,
        "common_action_after": 2,
        "value": 1,
    }


def budget_augmentation_witness():
    # Same hidden pair set. A one-step informative probe is feasible iff one unit remains.
    same_info_state = ((0, 0), (1, 0))
    accepts = {(w, s): frozenset({w}) for w in (0, 1) for s in (0, 1)}
    kernel = (((0, 0), None, (1, 0), None),)
    # Unit action cost makes the remaining budget an exact remaining horizon.
    values = [pair_value(kernel, accepts, remaining) for remaining in (0, 1)]
    histories = [explicit_history_value(kernel, accepts, remaining) for remaining in (0, 1)]
    if values != histories or values != [INF, 1]:
        raise AssertionError("budget witness disagrees with executed policies")
    return {
        "same_pair_state": [list(x) for x in same_info_state],
        "remaining_budget_0": "INF" if values[0] == INF else values[0],
        "remaining_budget_1": "INF" if values[1] == INF else values[1],
    }


def run_all():
    result = {
        "determinism": "exact-enumeration-no-rng",
        "pair_vs_history": exhaustive_pair_vs_history(),
        "destructive_probe": destructive_probe_counterexample(),
        "control_to_compatibility": control_to_compatibility_witness(),
        "budget_augmentation": budget_augmentation_witness(),
        "aggregate": "GRAND_GMI_CONTROLLED_ACQUISITION_TRANCHE_ALL_GREEN",
        "terminal": "GRAND_GMI_CONTROLLED_ACQUISITION_TRANCHE_ALL_GREEN",
    }
    return result


def main():
    print(json.dumps(run_all(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
