from __future__ import annotations

import json
from typing import Dict, List, Mapping

FREEZE_COMMIT = "a57664ec99b143f5c56fdd2f058d1a3aa5e16bb7"
BASE_COMMIT = "54eea90557619b3864cb0cd5c0804942ee7dd67a"

FORBIDDEN_CASE_KEYS = {
    "family",
    "family_name",
    "architecture",
    "architecture_name",
    "phenotype",
    "donor_path",
    "donor_file",
    "measured",
    "outcome",
    "result",
}


def _case(case_id: str, object_kind: str, matched_fields: List[str], varying: str,
          semantics: Mapping[str, object], arms: List[Mapping[str, object]]) -> Dict[str, object]:
    row: Dict[str, object] = {
        "case_id": case_id,
        "object_kind": object_kind,
        "matched_fields": matched_fields,
        "varying_coordinate": varying,
        "semantics": dict(semantics),
        "arms": [dict(a) for a in arms],
    }
    if FORBIDDEN_CASE_KEYS.intersection(row):
        raise ValueError("forbidden predictor-visible field")
    return row


def build_predictions() -> Mapping[str, object]:
    cases = [
        _case(
            "N1", "finite_coefficient_identification_control",
            ["dimension", "coefficient_grid", "true_vector", "response_channel", "observation_count"],
            "observation_rank",
            {"dimension": 4, "coefficient_grid": [-3,-2,-1,0,1,2,3],
             "true_vector": [2,-1,3,0], "response_channel": "exact_inner_product",
             "observation_count": 4},
            [
                {"arm": "positive", "observation_rank": 4,
                 "expected": {"consistent_candidates": 1, "identified": True}},
                {"arm": "fail", "observation_rank": 3,
                 "expected": {"consistent_candidates": 7, "identified": False}},
            ],
        ),
        _case(
            "N2", "parameter_output_credit_control",
            ["graph_equation", "n_in", "n_hid", "parameterized_block", "parameter_count", "input_values", "operation_accounting"],
            "n_out",
            {"graph_equation": "fixed_readout_relu_two_layer", "n_in": 4, "n_hid": 1,
             "parameterized_block": "W_only", "parameter_count": 4,
             "input_values": [1,1,1,1], "operation_accounting": "multiply_accumulate"},
            [
                {"arm": "positive", "n_out": 1,
                 "expected": {"forward": 20, "reverse": 10, "winner": "reverse"}},
                {"arm": "boundary", "n_out": 6,
                 "expected": {"forward": 40, "reverse": 40, "winner": "tie"}},
                {"arm": "fail", "n_out": 8,
                 "expected": {"forward": 48, "reverse": 52, "winner": "forward"}},
            ],
        ),
        _case(
            "N3", "finite_update_landscape_control",
            ["dimension", "coordinate_values", "target", "start", "horizon", "per_eval_prices", "update_procedures"],
            "landscape_signal",
            {"dimension": 3, "coordinate_values": [0,1,2,3], "target": [3,3,3],
             "start": [0,0,0], "horizon": 16,
             "per_eval_prices": {"random": "1", "local": "1", "gradient": "3"},
             "update_procedures": "registered_random_local_gradient"},
            [
                {"arm": "positive", "landscape_signal": "coordinate_distance",
                 "expected": {"gradient_evals": 3, "gradient_charged_cost": "9",
                              "random_expected_evals": "65/2", "gradient_reaches": True,
                              "gradient_cheaper_than_random": True}},
                {"arm": "fail", "landscape_signal": "needle",
                 "expected": {"gradient_evals": None, "local_evals": None,
                              "random_expected_evals": "65/2", "gradient_reaches": False}},
            ],
        ),
        _case(
            "N4", "conditional_retention_control",
            ["alphabet_semantics", "maximum_gap", "payloads", "register_lengths", "shift_semantics", "conditional_write_semantics", "gate_price"],
            "duration_variability",
            {"alphabet_semantics": ["marker", "payload_bit", "filler", "query"],
             "maximum_gap": 4, "payloads": [0,1], "register_lengths": list(range(1,9)),
             "shift_semantics": "unconditional_last_L_symbols",
             "conditional_write_semantics": "write_payload_after_marker_else_hold", "gate_price": 2},
            [
                {"arm": "fail", "duration_variability": "fixed_gap_4",
                 "gap_set": [4],
                 "expected": {"working_register_lengths": [5], "gated_works": True,
                              "conditional_write_required": False}},
                {"arm": "positive", "duration_variability": "variable_gap_0_2_4",
                 "gap_set": [0,2,4],
                 "expected": {"working_register_lengths": [], "gated_works": True,
                              "conditional_write_required": True}},
            ],
        ),
        _case(
            "N5", "finite_transition_affinity_control",
            ["carrier_states", "alphabet_size", "encoding_width", "affine_search_space"],
            "transition_structure",
            {"carrier_states": 4, "alphabet_size": 2, "encoding_width": 2,
             "affine_search_space": "all_injective_codes_and_all_GF2_A_c_per_symbol"},
            [
                {"arm": "positive", "transition_structure": "four_cycle_with_identity",
                 "expected": {"affine_realizable": True}},
                {"arm": "fail", "transition_structure": "merging_suffix_update",
                 "expected": {"affine_realizable": False}},
            ],
        ),
        _case(
            "N6", "metric_local_lookup_control",
            ["universe", "metric", "k", "subset_cap", "tie_break", "lookup_semantics"],
            "response_geometry",
            {"universe": "boolean_4_cube", "metric": "hamming", "k": 1, "subset_cap": 8,
             "tie_break": "distance_then_surface_lexicographic", "lookup_semantics": "nearest_held_case"},
            [
                {"arm": "positive", "response_geometry": "threshold_sum_ge_2",
                 "expected": {"smallest_sufficient_subset": 4, "sufficient_within_cap": True}},
                {"arm": "fail", "response_geometry": "parity",
                 "expected": {"smallest_sufficient_subset": None, "sufficient_within_cap": False}},
            ],
        ),
        _case(
            "N7", "finite_joint_factorization_control",
            ["dimensions", "support_cells", "row_marginals", "column_marginals", "full_storage", "factored_storage"],
            "dependence_structure",
            {"dimensions": [3,3], "support_cells": 9,
             "row_marginals": ["1/3","1/3","1/3"],
             "column_marginals": ["1/3","1/3","1/3"],
             "full_storage": 9, "factored_storage": 6},
            [
                {"arm": "positive", "dependence_structure": "independent_uniform",
                 "expected": {"factorizes": True, "factored_storage_legal": True}},
                {"arm": "fail", "dependence_structure": "dependent_full_support_same_marginals",
                 "expected": {"factorizes": False, "factored_storage_legal": False}},
            ],
        ),
        _case(
            "N8", "finite_search_heuristic_control",
            ["branching", "depth", "node_count", "goal_path", "algorithm", "child_order", "tie_break", "heuristic_price"],
            "heuristic_informativeness",
            {"branching": 3, "depth": 4, "node_count": 121, "goal_path": [2,2,2,2],
             "algorithm": "best_first", "child_order": [0,1,2], "tie_break": "insertion_order",
             "heuristic_price": 1},
            [
                {"arm": "positive", "heuristic_informativeness": "goal_prefix_distance",
                 "expected": {"expansions": 5, "charged_work": 10,
                              "reduces_expansions_vs_fail": True}},
                {"arm": "fail", "heuristic_informativeness": "constant_zero",
                 "expected": {"expansions": 121, "charged_work": 242}},
            ],
        ),
    ]
    if len({c["case_id"] for c in cases}) != 8:
        raise AssertionError("expected eight unique controls")
    return {
        "schema": "B1MatchedNegativePredictionsV1",
        "issue": 786,
        "freeze_commit": FREEZE_COMMIT,
        "base_commit": BASE_COMMIT,
        "outcomes_seen": False,
        "scorer_exists": False,
        "surface_remints_materialized": False,
        "historical_measured_matched_negative_count": 11,
        "successor_control_count": 8,
        "effective_count_if_later_confirmed": 19,
        "cases": cases,
        "claim_ceiling_if_later_confirmed": "B1_MATCHED_NEGATIVE_CONTROLS_MEASURED_19_OF_19_AT_REGISTERED_EXACT_SCOPE",
        "nonclaims": [
            "B1_COMMON_PROTOCOL_CLOSED",
            "KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE",
            "ALL_KNOWN_FAMILIES_PROSPECTIVELY_VALIDATED",
            "REAL_REGIME_REPLICATION_COMPLETE",
            "COMPLETE_GMI",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(build_predictions(), indent=2, sort_keys=True))
