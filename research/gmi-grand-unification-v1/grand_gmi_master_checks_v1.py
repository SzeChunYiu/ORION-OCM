#!/usr/bin/env python3
"""Integration checks for the Grand GMI V1 theorem stack."""

from fractions import Fraction
from itertools import combinations
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

EXPECTED_TERMINALS = {
    "GRAND_GMI_SEMANTIC_CUT_RECEIPT_V1.json": "GRAND_GMI_SEMANTIC_CUT_TRANCHE_ALL_GREEN",
    "GRAND_GMI_RECURSIVE_RECEIPT_V1.json": "GRAND_GMI_RECURSIVE_MORPHOGENESIS_TRANCHE_ALL_GREEN",
    "GRAND_GMI_SUBSTRATE_SYMMETRY_RECEIPT_V1.json": "GRAND_GMI_SUBSTRATE_SYMMETRY_TRANCHE_ALL_GREEN",
    "GRAND_GMI_COMPOSITIONAL_RECEIPT_V1.json": "GRAND_GMI_COMPOSITIONAL_DISTRIBUTED_TRANCHE_ALL_GREEN",
    "GRAND_GMI_MEANING_RECEIPT_V1.json": "GRAND_GMI_CAUSAL_SEMANTIC_VIABILITY_TRANCHE_ALL_GREEN",
}


def check_receipt_stack():
    observed = {}
    for name, expected in EXPECTED_TERMINALS.items():
        data = json.loads((HERE / name).read_text(encoding="utf-8"))
        terminal = data["terminal"]
        assert terminal == expected
        observed[name] = terminal
    return {"receipts": len(observed), "terminals": observed, "all_green": True}


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


def run():
    return {
        "terminal": "GRAND_GMI_MASTER_INTEGRATION_ALL_GREEN",
        "receipt_stack": check_receipt_stack(),
        "approximate_nontransitivity": check_approximate_nontransitivity(),
        "approximate_cover_monotonicity": check_approximate_cover_monotonicity(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
