#!/usr/bin/env python3
"""Executor for the Section-M hierarchy/planning/causal re-audit implementation v1.

Issue #833 Section M ("Cognitive-function derivation upgrade"), rows
``Re-audit hierarchical skills/chunking.``, ``Re-audit planning and stopping.``
and ``Re-audit causal cognition/intervention/counterfactuals.`` under the
registered freeze (research/gmi-833-cognitive-reaudit-v2/FREEZE_V1.md, commit
cb6d6a590535e8660559b143cbe32308a880c482, PR #927).

Runnable with no third-party dependency:

    python3 -I -B  research/gmi-833-cognitive-reaudit-v2-implementation-v1/executor_v1.py
    python3 -I -O -B research/gmi-833-cognitive-reaudit-v2-implementation-v1/executor_v1.py

Both modes must write a byte-identical RESULT_V1.json (CI cmp).  Any failed
check raises ValueError (non-zero exit) so a red result is explicit.  All
arithmetic is exact rational; no float literal appears in any source file.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import parents_v1 as parents          # noqa: E402
import stopping_bellman_v1 as bellman  # noqa: E402

ISSUE = 833
SECTION = "M"
PACKAGE = "gmi-833-cognitive-reaudit-v2-implementation-v1"
FREEZE_COMMIT = "cb6d6a590535e8660559b143cbe32308a880c482"
FREEZE_BLOB = "b436513f28b06269c060a34c0ac635e44a23ce63"
CLAIM_CEILING = "GMI_833_HIERARCHY_PLANNING_CAUSAL_REAUDIT_AT_REGISTERED_EXACT_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "UNIVERSAL_HIERARCHY_DEPTH",
    "GOALS_DERIVED_FROM_DYNAMICS",
    "MYOPIC_EVC_IS_UNIVERSALLY_OPTIMAL",
    "OBSERVATION_IDENTIFIES_CAUSATION",
    "GENERAL_CAUSAL_DISCOVERY_SOLVED",
    "EMPIRICAL_COGNITIVE_VALIDATION",
    "COMPLETE_GMI",
)
LEDGER_KEYS = {
    "hierarchy": "b54aa4a07f07",
    "planning": "cae1b23a7b71",
    "causal": "363a75a09b44",
}
# origin/main at the time this implementation branch was cut (set before push).
SOURCE_MAIN = "aaabf8741041d659151860404d82dc5e14c7c021"


def _raise_red(failed: list[str]) -> None:
    raise ValueError("executor RED: %s" % ", ".join(failed))


def build_result() -> dict:
    parent_pins = parents.audit_parent_pins()
    legacy = parents.legacy_replays()
    parents_exercised = parents.exercise_parents()
    hierarchy = parents.exercise_hierarchy()
    causal = parents.exercise_causal()
    planning = bellman.planning_row_full()

    checks = {
        "parent_pins_all_match": parent_pins["all_pinned"],
        "foundation_receipt_regenerated": parents_exercised["foundation"]["regenerated_matches_committed"],
        "foundation_forbidden_registry_loaded": parents_exercised["foundation"]["contains_COMPLETE_GMI"],
        "axiom_core_receipt_regenerated": parents_exercised["axiom_core"]["regenerated_matches_committed"],
        "axiom_core_base_model_satisfies_ax1_ax6": parents_exercised["axiom_core"]["base_model_satisfies_all_axioms"],
        "axiom_core_dependency_graph_acyclic": parents_exercised["axiom_core"]["dependency_graph_acyclic"],
        "axiom_core_hostile_hypercube_complete": (
            parents_exercised["axiom_core"]["hostile_hypercube_cases"] == 128
            and parents_exercised["axiom_core"]["hostile_hypercube_satisfying_cases"] == 1),
        "hierarchy_replay_byte_exact": legacy["hierarchy"]["isolated_replay_byte_exact"]
        and legacy["hierarchy"]["receipt_sha256_ok"],
        "causal_replay_byte_exact": legacy["causal"]["isolated_replay_byte_exact"]
        and legacy["causal"]["receipt_sha256_ok"],
        "hierarchy_lifecycle_3060_3032_1233": hierarchy["lifecycle"] == [3060, 3032, 1233],
        "hierarchy_greedy_longest_match_fails": hierarchy["greedy_exact_cost"] == 2
        and hierarchy["source_greedy_cost"] == 3,
        "hierarchy_loses_workload_solver": hierarchy["h_freezer_2_hierarchy_loses"]["solver_cost"] == 2,
        "hierarchy_policy_census_complete": hierarchy["policy_census_executions"] == 3456,
        "hierarchy_parsing_census_complete": hierarchy["parsing_census_parses"] == 3136,
        "planning_hostile_fired": planning["report"]["hostile_fired"],
        "planning_clean_variant_no_alarm": planning["report"]["clean_variant_no_alarm"],
        "planning_ties_preserved": planning["report"]["ties_preserved"],
        "planning_refusals_enforced": planning["report"]["refusals_enforced"],
        "planning_myopic_scope_13_of_35": planning["legacy_myopic_scope"]["myopic_greedy_optimality_13_of_35"] == [13, 35],
        "planning_policy_search_matches_bellman": (
            planning["report"]["hostile"]["policy_search_optimal_value"]
            == planning["report"]["hostile"]["optimal_value_vstar_root"]),
        "causal_observation_equivalent_different_targets": (
            causal["c_freezer_1"]["six_original_all_nine_joint_laws_equal"]
            and causal["c_freezer_1"]["six_original_left_pn"] != causal["c_freezer_1"]["six_original_right_pn"]
            and causal["c_freezer_1"]["two_smaller_left_pn"] != causal["c_freezer_1"]["two_smaller_right_pn"]
            and causal["c_freezer_1"]["three_treatment_supported"]),
        "causal_incompatible_evidence_refused": (
            causal["c_freezer_2"]["empty_compatible_class_refused"]
            and causal["c_freezer_2"]["disjoint_class_status"] == "INCOMPATIBLE"),
        "causal_identified_constant_on_fiber_control": (
            causal["c_freezer_3"]["uniform_n1_status"] == "IDENTIFIED"
            and causal["c_freezer_3"]["lower"] == "1"
            and causal["c_freezer_3"]["upper"] == "1"
            and causal["c_freezer_3"]["point_identification_status"] == "IDENTIFIED"),
        "causal_faithfulness_does_not_orient": (
            causal["c_freezer_4"]["same_full_support_observed"]
            and causal["c_freezer_4"]["dependent"]
            and causal["c_freezer_4"]["forward_do1"] == "3/4"
            and causal["c_freezer_4"]["reverse_do1"] == "1/2"),
        "causal_undefined_conditioning_distinct_refusal": causal["c_freezer_5"]["undefined_conditioning_refused"],
        "causal_census_complete": causal["census"][-1]["models"] == 1716,
    }

    failed = [k for k, v in checks.items() if not v]
    if failed:
        _raise_red(failed)

    hostiles_detected = {
        "hierarchy_longest_match_greedy_failure": 1,
        "hierarchy_loses_after_complete_charges": 1,
        "planning_myopic_one_step_stops_two_step_pays": 1,
        "causal_observation_equivalent_different_targets": 3,
        "causal_incompatible_evidence_refused": 2,
        "causal_undefined_conditioning_distinct_refusal": 1,
    }
    nulls = {
        "planning_clean_variant_false_alarms": 0,
        "causal_identified_control_false_alarms": 0,
        "hierarchy_exact_parser_oracle_mismatches": 0,
    }

    bounded_censuses = {
        "planning_policies_enumerated": planning["report"]["policy_enumerations_total"],
        "planning_myopic_legacy_subsets": planning["legacy_myopic_scope"]["subset_census"],
        "planning_controls": 3,
        "planning_refusal_probes": 2,
        "hierarchy_register_cases": hierarchy["policy_census_cases"],
        "hierarchy_complete_executions": hierarchy["policy_census_executions"],
        "hierarchy_word_cases": hierarchy["parsing_census_cases"],
        "hierarchy_complete_parses": hierarchy["parsing_census_parses"],
        "causal_models": causal["census_models_total"],
        "causal_joint_law_comparisons": causal["census_joint_law_comparisons_total"],
        "causal_attainment_checks": causal["census_attainment_checks_total"],
        "causal_hosted_controls": 6,
    }
    total_registered_cases = sum(bounded_censuses.values())

    rows = {
        "hierarchy": {
            "row": "Re-audit hierarchical skills/chunking.",
            "results": ["HCR-1", "HCR-2", "HCR-3", "HCR-4"],
            "reparenting": "gmi-hierarchical-chunking-repair-v1 re-parented to upgraded foundation/axiom core; "
                           "frozen blobs re-checked and isolated replay byte-exact",
            "lifecycle": hierarchy["lifecycle"],
            "first_gain": hierarchy["first_gain"],
            "second_gain": hierarchy["second_gain"],
            "hostiles_detected": {
                "longest_match_greedy_countermodel": {"x": "abcde", "greedy_cost": 3, "exact_cost": 2},
                "hierarchy_loses_workload": hierarchy["h_freezer_2_hierarchy_loses"],
            },
            "census": {
                "policy_register_cases": hierarchy["policy_census_cases"],
                "complete_executions": hierarchy["policy_census_executions"],
                "word_dictionary_cases": hierarchy["parsing_census_cases"],
                "complete_parses": hierarchy["parsing_census_parses"],
            },
            "ledger_key": LEDGER_KEYS["hierarchy"],
            "verdict": "GREEN",
        },
        "planning": {
            "row": "Re-audit planning and stopping.",
            "results": ["PS-1", "PS-2"],
            "theorem_scope": "forall[finite acyclic computation graphs, all costs charged]",
            "hostile": planning["report"]["hostile"],
            "clean_variant": planning["report"]["clean_variant"],
            "tie_control": planning["report"]["tie_control"],
            "refusals": planning["report"]["refusals"],
            "legacy_myopic_scope": planning["legacy_myopic_scope"],
            "hostile_fired": planning["report"]["hostile_fired"],
            "clean_variant_no_alarm": planning["report"]["clean_variant_no_alarm"],
            "ledger_key": LEDGER_KEYS["planning"],
            "verdict": "GREEN",
        },
        "causal": {
            "row": "Re-audit causal cognition/intervention/counterfactuals.",
            "results": ["CRR1", "CRR2"],
            "reparenting": "gmi-causal-rung-repair-v1 re-parented to upgraded foundation/axiom core; "
                           "frozen blobs re-checked and isolated replay byte-exact",
            "hostiles_detected": {
                "observation_equivalent_different_targets": {
                    "six_original_left_pn": causal["c_freezer_1"]["six_original_left_pn"],
                    "six_original_right_pn": causal["c_freezer_1"]["six_original_right_pn"],
                    "two_smaller_left_pn": causal["c_freezer_1"]["two_smaller_left_pn"],
                    "two_smaller_right_pn": causal["c_freezer_1"]["two_smaller_right_pn"],
                },
                "incompatible_evidence": "refused (empty compatible class; disjoint class INCOMPATIBLE)",
                "undefined_conditioning_distinct": causal["c_freezer_5"]["undefined_conditioning_refused"],
            },
            "controls": {
                "identified_constant_on_fiber": causal["c_freezer_3"],
                "faithfulness_does_not_orient": causal["c_freezer_4"],
            },
            "census": causal["census"],
            "census_models_total": causal["census_models_total"],
            "ledger_key": LEDGER_KEYS["causal"],
            "verdict": "GREEN",
        },
    }

    return {
        "schema": "GMI833ReauditHierarchyPlanningCausalResultV1",
        "package": PACKAGE,
        "issue": ISSUE,
        "section": SECTION,
        "freeze_commit": FREEZE_COMMIT,
        "freeze_blob": FREEZE_BLOB,
        "source_main": SOURCE_MAIN,
        "claim_ceiling": CLAIM_CEILING,
        "terminal": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "evidence_level": "EV2",
        "maturity": "M2",
        "domain_tag": "forall[finite acyclic computation graphs] + forall_fin[registered exact finite scopes]",
        "verdict": "GREEN" if not failed else "RED",
        "checks": checks,
        "parents": {
            "pins": parent_pins,
            "legacy_replays": legacy,
            "exercised": parents_exercised,
        },
        "rows": rows,
        "hostiles_detected": hostiles_detected,
        "nulls": nulls,
        "bounded_censuses": bounded_censuses,
        "total_registered_cases": total_registered_cases,
        "ledger_keys": LEDGER_KEYS,
        "reconciliations": [
            "ISSUE_833_RECONCILIATION_HIERARCHY_V2.json",
            "ISSUE_833_RECONCILIATION_PLANNING_V2.json",
            "ISSUE_833_RECONCILIATION_CAUSAL_V2.json",
        ],
        "demarcations": {
            "metacognition_social_communication_imitation_teaching_culture": "gmi-833-cognitive-reaudit-social-v1 (PR #942)",
            "memory_attention_concept_formation": "gmi-833-cognitive-reaudit-v1 (PR #919 / #917)",
            "within_lifetime_library_growth": "#897",
        },
    }


def main() -> None:
    result = build_result()
    data = (json.dumps(result, sort_keys=True, indent=2, default=str) + "\n").encode()
    (HERE / "RESULT_V1.json").write_bytes(data)


if __name__ == "__main__":
    main()
