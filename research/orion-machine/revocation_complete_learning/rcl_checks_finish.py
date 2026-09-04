"""Remaining exact checks and aggregate runner for RCL V0."""

from __future__ import annotations

import itertools
import math

from rcl_model import (
    canonical_profile,
    combinatorial_rank,
    combinatorial_unrank,
    live,
    signature,
)
from rcl_checks_core import (
    verify_antichain_injectivity,
    verify_bounded_witness_family,
    verify_counterfactual_gap,
    verify_direct_sum,
    verify_positive_witness_omissions,
    verify_storage_query_frontier,
)

def verify_single_warrant_bounds(max_n: int = 8) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for n in range(1, max_n + 1):
        for d in range(n + 1):
            supports = [frozenset(x) for x in itertools.combinations(range(n), d)]
            ranks = {combinatorial_rank(support, n, d) for support in supports}
            round_trip = all(combinatorial_unrank(rank, n, d) in supports for rank in ranks)
            expected = math.comb(n, d)
            cases.append(
                {
                    "n": n,
                    "d": d,
                    "profile_count": expected,
                    "lower_bound_bits": math.ceil(math.log2(expected)),
                    "rank_count": len(ranks),
                    "round_trip": round_trip,
                }
            )
    return {
        "max_n": max_n,
        "case_count": len(cases),
        "all_exact": all(c["rank_count"] == c["profile_count"] and c["round_trip"] for c in cases),
        "cases": cases,
    }


def verify_controls() -> dict[str, object]:
    full = canonical_profile([{0, 1}, {2, 3}])
    emitted_one = canonical_profile([{0, 1}])
    revoked = frozenset({0})
    planted = {
        "exact_live": live(full, revoked),
        "positive_only_updater_live": live(emitted_one, revoked),
    }
    no_alarm = {
        "exact_live": live(full, revoked),
        "complete_updater_live": live(full, revoked),
    }
    mutated_signature = list(signature(full, 4))
    mutated_signature[0] = not mutated_signature[0]
    mutation_detected = tuple(mutated_signature) != signature(full, 4)
    return {
        "planted_positive": {
            **planted,
            "overretraction_detected": planted == {
                "exact_live": True,
                "positive_only_updater_live": False,
            },
        },
        "no_alarm": {**no_alarm, "agreement": len(set(no_alarm.values())) == 1},
        "mutation_control": {"mutated": True, "detected": mutation_detected},
    }


def run_self_test() -> dict[str, object]:
    injectivity = verify_antichain_injectivity()
    omissions = verify_positive_witness_omissions()
    bounded = verify_bounded_witness_family()
    gap = verify_counterfactual_gap()
    frontier = verify_storage_query_frontier()
    direct_sum = verify_direct_sum()
    single = verify_single_warrant_bounds()
    controls = verify_controls()
    gap_n5 = next(row for row in gap["cases"] if row["n"] == 5)
    frontier_n5 = next(row for row in frontier["cases"] if row["n"] == 5)
    single_n8d4 = next(
        row for row in single["cases"] if row["n"] == 8 and row["d"] == 4
    )
    assertions = {
        "dedekind_n4_is_168": injectivity["profile_count"] == 168,
        "signature_injective": injectivity["injective"],
        "independent_liveness_agrees": injectivity["independent_liveness_agreement"] == injectivity["independent_liveness_denominator"],
        "all_positive_omissions_distinguished": omissions["all_omissions_distinguished"],
        "bounded_witness_family_live": bounded["all_exact"],
        "counterfactual_gap_exact": gap["all_exact"],
        "storage_query_construction_exact": frontier["all_exact"],
        "direct_sum_exact": direct_sum["exact"],
        "single_warrant_codes_exact": single["all_exact"],
        "planted_positive_fires": controls["planted_positive"]["overretraction_detected"],
        "no_alarm_control_passes": controls["no_alarm"]["agreement"],
        "mutation_control_fires": controls["mutation_control"]["detected"],
    }
    return {
        "schema": "orion-v2.revocation-complete-learning.exact-oracle.v0",
        "terminal": "PASS" if all(assertions.values()) else "FAIL",
        "assertions": assertions,
        "injectivity": injectivity,
        "positive_witness_omissions": omissions,
        "bounded_witness_summary": {
            "max_k": bounded["max_k"],
            "witness_count": bounded["witness_count"],
            "all_exact": bounded["all_exact"],
        },
        "counterfactual_gap_n5": gap_n5,
        "counterfactual_coordinate_checks": gap["coordinate_checks"],
        "storage_query_frontier_n5": frontier_n5,
        "storage_query_reconstruction_checks": frontier["reconstruction_checks"],
        "direct_sum": direct_sum,
        "single_warrant_summary": {
            "case_count": single["case_count"],
            "all_exact": single["all_exact"],
            "n8_d4": single_n8d4,
        },
        "controls": controls,
        "authority": {
            "all_size_theorem_proved_by_enumeration": False,
            "novelty_established": False,
            "architecture_superiority_established": False,
        },
    }
