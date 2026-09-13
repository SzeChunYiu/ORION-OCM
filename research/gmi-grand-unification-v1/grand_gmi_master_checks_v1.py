#!/usr/bin/env python3
"""Integration checks for the Grand GMI V1 theorem stack."""

from fractions import Fraction
from itertools import combinations
import importlib.util
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

def check_receipt_stack(root=HERE):
    spec = importlib.util.spec_from_file_location(
        "grand_gmi_theorem_replay", HERE / "replay_theorem_capsule_v1.py"
    )
    module = importlib.util.module_from_spec(spec)
    # The aggregate may also be imported by a caller with ambient .pyc caches.
    # Compile the helper source directly rather than accepting cached bytecode.
    source = HERE / "replay_theorem_capsule_v1.py"
    exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
    # The outer replay verifies this aggregate against MASTER_RECEIPT_V2.
    # Re-entering it here would recursively execute the aggregate forever.
    return module.replay(root, include_aggregate=False)


def check_approximate_nontransitivity():
    eps = Fraction(1)
    q0, q1, q2 = Fraction(0), Fraction(1), Fraction(2)
    near01 = abs(q0 - q1) <= eps
    near12 = abs(q1 - q2) <= eps
    near02 = abs(q0 - q2) <= eps
    assert near01 and near12 and not near02
    return {
        "epsilon": "1",
        "q0_near_q1": near01,
        "q1_near_q2": near12,
        "q0_near_q2": near02,
        "distance_threshold_is_transitive": False,
    }


def covering_number(points, eps):
    n = len(points)
    for k in range(1, n + 1):
        for inds in combinations(range(n), k):
            covered = set()
            for i in inds:
                for j, p in enumerate(points):
                    if abs(points[i] - p) <= eps:
                        covered.add(j)
            if len(covered) == n:
                return k
    raise AssertionError("finite cover not found")


def check_approximate_cover_monotonicity():
    points = [Fraction(i) for i in range(4)]
    counts = [covering_number(points, Fraction(e)) for e in (0, 1, 2)]
    assert counts == [4, 2, 1]

    # Exact epsilon=0 complexity cannot decrease when a new response coordinate is added.
    coarse = {(0,), (0,), (1,)}
    rich = {(0, 0), (0, 1), (1, 0)}
    assert len(rich) >= len(coarse)
    return {
        "scalar_cover_counts_eps_0_1_2": counts,
        "richer_probe_exact_classes_coarse": len(coarse),
        "richer_probe_exact_classes_rich": len(rich),
        "monotonicity_green": True,
    }


def check_componentwise_infimum_not_attained():
    profiles = ((1, 3), (3, 1))
    ideal = tuple(min(profile[i] for profile in profiles) for i in range(2))
    frontier = tuple(p for p in profiles if not any(
        all(a <= b for a, b in zip(q, p)) and any(a < b for a, b in zip(q, p))
        for q in profiles
    ))
    if ideal != (1, 1) or ideal in profiles or frontier != profiles:
        raise AssertionError("componentwise infimum/Pareto witness failed")
    return {
        "attainable_profiles": [list(p) for p in profiles],
        "pareto_frontier": [list(p) for p in frontier],
        "componentwise_infimum": list(ideal),
        "componentwise_infimum_attained": False,
    }


def run():
    return {
        "terminal": "GRAND_GMI_MASTER_INTEGRATION_V2_ALL_GREEN",
        "receipt_stack": check_receipt_stack(),
        "approximate_nontransitivity": check_approximate_nontransitivity(),
        "approximate_cover_monotonicity": check_approximate_cover_monotonicity(),
        "componentwise_infimum_not_attained": check_componentwise_infimum_not_attained(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
