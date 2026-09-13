#!/usr/bin/env python3
"""Finite controlled beliefs versus explicitly executed complete policy trees."""
from functools import lru_cache
from itertools import product
import json


def beliefs(n):
    return tuple(tuple(s for s in range(n) if mask & (1 << s))
                 for mask in range(1, 1 << n))


def common(belief, success):
    return set.intersection(*(set(success[s]) for s in belief))


def successors(belief, transitions, observations, action):
    if any(transitions[s][action] is None for s in belief):
        return None
    return {o: tuple(sorted({transitions[s][action] for s in belief
                             if observations[s][action] == o}))
            for o in {observations[s][action] for s in belief}}


def synthesize(transitions, observations, success):
    domain = beliefs(len(transitions))
    ranks = {b: 0 for b in domain if common(b, success)}
    policy = {b: ("stop", min(common(b, success))) for b in ranks}
    for step in range(1, len(domain)):
        added = {}
        for b in domain:
            if b in ranks:
                continue
            for u in range(len(transitions[0])):
                cells = successors(b, transitions, observations, u)
                if cells is not None and all(child in ranks for child in cells.values()):
                    added[b] = step
                    policy[b] = ("act", u)
                    break
        if not added:
            break
        ranks.update(added)
    return {b: ranks.get(b) for b in domain}, policy


def bounded_cost(belief, transitions, observations, success, costs, horizon):
    @lru_cache(None)
    def solve(b, left):
        if common(b, success):
            return 0
        if not left:
            return None
        options = []
        for u, cost in enumerate(costs):
            cells = successors(b, transitions, observations, u)
            if cells is not None:
                child = [solve(c, left - 1) for c in cells.values()]
                if all(v is not None for v in child):
                    options.append(cost + max(child))
        return min(options, default=None)
    return solve(tuple(belief), horizon)


@lru_cache(None)
def policy_trees(depth):
    trees = [("stop", 0), ("stop", 1)]
    if depth:
        children = policy_trees(depth - 1)
        trees.extend((u, left, right) for u in (0, 1)
                     for left, right in product(children, repeat=2))
    return tuple(trees)


def execute_tree(tree, state, transitions, observations, costs):
    cost = 0
    while tree[0] != "stop":
        u = tree[0]
        target = transitions[state][u]
        if target is None:
            return None
        tree = tree[1 + observations[state][u]]
        state, cost = target, cost + costs[u]
    return state, tree[1], cost


def policy_profiles(transitions, observations, costs, depth):
    return {tuple(execute_tree(tree, s, transitions, observations, costs)
                  for s in range(len(transitions))) for tree in policy_trees(depth)}


def oracle_cost(profiles, belief, success):
    values = []
    for profile in profiles:
        if all(profile[s] is not None and profile[s][1] in success[profile[s][0]]
               for s in belief):
            values.append(max(profile[s][2] for s in belief))
    return min(values, default=None)


def execute_synthesis(initial, actual, policy, transitions, observations, success):
    belief = initial
    for step in range(len(beliefs(len(transitions))) + 1):
        if belief not in policy:
            return False
        kind, u = policy[belief]
        if kind == "stop":
            return u in success[actual]
        target = transitions[actual][u]
        cells = successors(belief, transitions, observations, u)
        if target is None or cells is None:
            return False
        belief, actual = cells[observations[actual][u]], target
    return False


def protection_instance(protect=True):
    # Indices F0,F1,P0,P1,D0,D1; controls protect,probe.
    transitions = ((2, 4), (3, 5), (2, 2), (3, 3), (4, 4), (5, 5))
    if not protect:
        transitions = tuple((None, probe) for _, probe in transitions)
    observations = tuple((0, s % 2) for s in range(6))
    success = ({0}, {1}, {0}, {1}, set(), set())
    return transitions, observations, success


def run_checks():
    count = {"instances": 0, "rank_oracle": 0, "winning": 0,
             "losing": 0, "constructed_world_runs": 0, "constructed_successes": 0}
    domain = beliefs(2)
    for flat_t in product((None, 0, 1), repeat=4):
        t = (flat_t[:2], flat_t[2:])
        for flat_o in product((0, 1), repeat=4):
            obs = (flat_o[:2], flat_o[2:])
            profiles = policy_profiles(t, obs, (1, 1), 2)
            for masks in product(range(4), repeat=2):
                success = tuple({a for a in (0, 1) if mask & (1 << a)} for mask in masks)
                ranks, policy = synthesize(t, obs, success)
                for b in domain:
                    count["instances"] += 1
                    count["rank_oracle"] += ranks[b] == oracle_cost(profiles, b, success)
                    count["winning" if ranks[b] is not None else "losing"] += 1
                    if ranks[b] is not None:
                        for actual in b:
                            count["constructed_world_runs"] += 1
                            count["constructed_successes"] += execute_synthesis(
                                b, actual, policy, t, obs, success)
    protection = {}
    for enabled in (False, True):
        t, obs, success = protection_instance(enabled)
        ranks, _ = synthesize(t, obs, success)
        protection[str(enabled)] = [ranks[(0, 1)],
            oracle_cost(policy_profiles(t, obs, (1, 1), 2), (0, 1), success)]
    t, obs, success = ((0, 1), (1, 1)), ((0, 0), (0, 0)), (set(), {0})
    weighted = []
    for costs in product((0, 1, 2), repeat=2):
        for horizon in range(3):
            actual = bounded_cost((0,), t, obs, success, costs, horizon)
            oracle = oracle_cost(policy_profiles(t, obs, costs, horizon), (0,), success)
            weighted.append([list(costs), horizon, actual, oracle])
    green = (count["instances"] == 62208 == count["rank_oracle"] and
             count["winning"] > 0 and count["losing"] > 0 and
             count["constructed_world_runs"] == count["constructed_successes"] and
             protection == {"False": [None, None], "True": [2, 2]} and
             all(row[-1] == row[-2] for row in weighted))
    return {"schema": "grand-gmi-controlled-acquisition-v1", "census": count,
            "policy_tree_count_depth_two": len(policy_trees(2)),
            "protection_revival": protection, "bounded_cost_controls": weighted,
            "scope": "complete two-state deterministic partial-transition universe; six-state witness",
            "all_checks_green": green,
            "terminal": "CONTROLLED_ACQUISITION_FINITE_GREEN" if green else "FAILED"}


if __name__ == "__main__":
    result = run_checks()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_checks_green"] else 1)
