from __future__ import annotations

from collections import Counter
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
FREEZE_COMMIT = "ddb3df7a44a6a4fb47fdc362a1fa02e34b7a3a75"
CLAIM_CEILING = "GMI_20_HELDOUT_BINARY_MORPHOLOGY_TRANSITIONS_AND_INDEPENDENT_SEARCH_REPLICATION_AT_REGISTERED_FINITE_SCOPE"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


full = _load("heldout_full_v1", "full_enumeration_v1.py")
frontier = _load("heldout_frontier_v1", "frontier_branch_bound_v1.py")

F = Fraction

CASES = (
    (1,F(1,5),F(1),F(1,10),F(1,20),F(3,20)),
    (2,F(1,5),F(2),F(1,5),F(1,10),F(3,10)),
    (3,F(1,5),F(3),F(3,10),F(3,20),F(9,20)),
    (4,F(1,5),F(4),F(2,5),F(1,5),F(3,5)),
    (5,F(2,5),F(1),F(1,5),F(1,10),F(3,10)),
    (6,F(2,5),F(2),F(2,5),F(1,5),F(3,5)),
    (7,F(2,5),F(3),F(3,5),F(3,10),F(9,10)),
    (8,F(2,5),F(4),F(4,5),F(2,5),F(6,5)),
    (9,F(3,5),F(1),F(3,10),F(3,20),F(9,20)),
    (10,F(3,5),F(2),F(3,5),F(3,10),F(9,10)),
    (11,F(3,5),F(3),F(9,10),F(9,20),F(27,20)),
    (12,F(3,5),F(4),F(6,5),F(3,5),F(9,5)),
    (13,F(4,5),F(1),F(2,5),F(1,5),F(3,5)),
    (14,F(4,5),F(2),F(4,5),F(2,5),F(6,5)),
    (15,F(4,5),F(3),F(6,5),F(3,5),F(9,5)),
    (16,F(4,5),F(4),F(8,5),F(4,5),F(12,5)),
    (17,F(1),F(1),F(1,2),F(1,4),F(3,4)),
    (18,F(1),F(2),F(1),F(1,2),F(3,2)),
    (19,F(1),F(3),F(3,2),F(3,4),F(9,4)),
    (20,F(1),F(4),F(2),F(1),F(3)),
)


def classify(bits: tuple[int, ...]) -> tuple[str, ...]:
    mapping = {0: "STATELESS", 1: "PERSISTENT_STATE"}
    if any(b not in mapping for b in bits):
        raise AssertionError("unknown post-search state property")
    return tuple(sorted(mapping[b] for b in bits))


def _risk_histogram_from_full(universe) -> Counter:
    return Counter((x.state_bits, x.error_now_count, x.error_delay_count) for x in universe)


def _risk_histogram_from_frontier(points) -> Counter:
    return Counter({(x.state_bits, x.error_now_count, x.error_delay_count): x.multiplicity for x in points})


def run_certificate() -> dict[str, object]:
    checks: dict[str, bool] = {}

    universe = full.build_universe()
    reminted = full.build_universe(lambda i: f"z{full.CANDIDATE_COUNT - 1 - i:05d}")
    points, point_meta = frontier.build_risk_points()

    checks["candidate_census_exact"] = len(universe) == len(reminted) == 65552 == point_meta["raw_candidates"]
    checks["independent_risk_histograms_identical"] = _risk_histogram_from_full(universe) == _risk_histogram_from_frontier(points)
    checks["risk_summary_count"] = point_meta["risk_points"] == 146

    stateless = [x for x in universe if x.state_bits == 0]
    stateful = [x for x in universe if x.state_bits == 1]
    checks["stateless_min_delayed_error_half"] = min(x.error_delay_count for x in stateless) == 8
    checks["stateless_joint_now_zero_delay_half_exists"] = any(
        x.error_now_count == 0 and x.error_delay_count == 8 for x in stateless
    )
    checks["stateful_zero_zero_risk_exists"] = any(
        x.error_now_count == 0 and x.error_delay_count == 0 for x in stateful
    )

    endpoint_predictions = endpoint_correct = search_agreements = remint_agreements = 0
    transitions_correct = boundary_ties = shifted_threshold_failures = 0
    case_receipts = []
    branch_pruned_total = 0

    for case_id, p, eta, threshold, low_price, high_price in CASES:
        if threshold != eta * p / 2:
            raise AssertionError("frozen threshold arithmetic changed")
        if not (low_price < threshold < high_price):
            raise AssertionError("frozen endpoint no longer straddles threshold")

        endpoint_properties = []
        for label, price, expected in (
            ("low", low_price, ("PERSISTENT_STATE",)),
            ("high", high_price, ("STATELESS",)),
        ):
            a = full.search(universe, p, eta, price)
            b = frontier.search(points, p, eta, price)
            ar = full.search(reminted, p, eta, price)
            pa, pb, par = classify(a["winner_state_bits"]), classify(b["winner_state_bits"]), classify(ar["winner_state_bits"])
            endpoint_predictions += 1
            endpoint_correct += int(pa == expected)
            search_agreements += int(pa == pb and a["best"] == b["best"])
            remint_agreements += int(pa == par and a["best"] == ar["best"])
            branch_pruned_total += int(b["pruned_points"])
            endpoint_properties.append(pa)

        transitions_correct += int(endpoint_properties == [("PERSISTENT_STATE",), ("STATELESS",)])

        boundary_full = full.search(universe, p, eta, threshold)
        boundary_frontier = frontier.search(points, p, eta, threshold)
        boundary_expected = ("PERSISTENT_STATE", "STATELESS")
        boundary_ties += int(
            classify(boundary_full["winner_state_bits"]) == boundary_expected
            and classify(boundary_frontier["winner_state_bits"]) == boundary_expected
            and boundary_full["best"] == boundary_frontier["best"] == threshold
        )

        # Deliberately wrong threshold: 2 * true threshold. It predicts the high endpoint remains stateful.
        wrong_high_prediction = ("PERSISTENT_STATE",) if high_price < 2 * threshold else ("STATELESS",)
        shifted_threshold_failures += int(wrong_high_prediction != endpoint_properties[1])

        case_receipts.append({
            "case": case_id,
            "p": str(p),
            "eta": str(eta),
            "threshold": str(threshold),
            "lambda_low": str(low_price),
            "lambda_high": str(high_price),
            "observed_low": list(endpoint_properties[0]),
            "observed_high": list(endpoint_properties[1]),
        })

    checks["twenty_frozen_transitions_correct"] = transitions_correct == 20
    checks["forty_endpoint_predictions_correct"] = endpoint_predictions == endpoint_correct == 40
    checks["independent_search_agreement_all_endpoints"] = search_agreements == 40
    checks["surface_remint_invariant_all_endpoints"] = remint_agreements == 40
    checks["twenty_exact_boundary_ties"] = boundary_ties == 20
    checks["incorrect_shifted_threshold_falsified"] = shifted_threshold_failures == 20
    checks["branch_bound_actually_prunes"] = branch_pruned_total > 0
    checks["search_strategies_materially_distinct"] = (
        full.STRATEGY_SIGNATURE != frontier.STRATEGY_SIGNATURE
        and full.CANDIDATE_COUNT == frontier.RAW_CANDIDATE_BUDGET == 65552
    )

    # The two search implementations must not import or invoke one another.
    source_full = (ROOT / "full_enumeration_v1.py").read_text()
    source_frontier = (ROOT / "frontier_branch_bound_v1.py").read_text()
    checks["search_implementations_source_separated"] = (
        "frontier_branch_bound_v1" not in source_full and "full_enumeration_v1" not in source_frontier
    )

    if not all(checks.values()):
        raise AssertionError(checks)

    return {
        "schema": "GMI_833_HELDOUT_20_TRANSITIONS_RESULT_V1",
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN",
        "checks": checks,
        "counts": {
            "raw_candidates": 65552,
            "risk_points": point_meta["risk_points"],
            "heldout_transitions": transitions_correct,
            "endpoint_predictions": endpoint_predictions,
            "endpoint_correct": endpoint_correct,
            "independent_search_agreements": search_agreements,
            "remint_agreements": remint_agreements,
            "boundary_ties": boundary_ties,
            "shifted_threshold_failures": shifted_threshold_failures,
            "branch_pruned_points_total": branch_pruned_total,
        },
        "searchers": {
            "full": {"strategy_signature": list(full.STRATEGY_SIGNATURE), "declared_budget": full.CANDIDATE_COUNT},
            "frontier": {"strategy_signature": list(frontier.STRATEGY_SIGNATURE), "declared_budget": frontier.RAW_CANDIDATE_BUDGET},
        },
        "cases": case_receipts,
        "forbidden_promotions": [
            "REAL_SYSTEM_MORPHOLOGY_TRANSITIONS_VALIDATED",
            "UNIVERSAL_MORPHOLOGY_PHASE_LAW",
            "ALL_KNOWN_FORMS_PREDICTED",
            "COMPLETE_GMI",
        ],
    }


def main() -> None:
    print(json.dumps(run_certificate(), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
