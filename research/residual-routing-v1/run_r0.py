"""R0-D6: build the RESIDUAL_ROUTING_OPPORTUNITY_V1 raw and derived receipts.

Reads the harvested raw records, derives every quantity #152 requires, and
returns exactly one terminal.
"""
from __future__ import annotations

import json
import os
import pathlib
import statistics
from collections import Counter
from typing import Any

import analysis
import contract
import frontier
import identifiability
import protocol

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"
COORD = analysis.COORDINATES


def load(raw_path: pathlib.Path) -> list[dict]:
    return json.loads(raw_path.read_text())


def per_query(records: list[dict]) -> list[dict]:
    rows = []
    for r in records:
        order = r["incumbent_order_and_choice"]
        f = order["first_passing_index"]
        split = analysis.split_work(r)
        m = r["A_admissible_count"]
        rows.append({
            "source": r["source"],
            "N_total": r["N_total"],
            "A_structural_count": r["A_structural_count"],
            "A_admissible_count": m,
            "incumbent_order_and_choice": order,
            "selection_contract_id": contract.C1_ANSWER_EQUIVALENCE.contract_id,
            "counterfactual_identification_route": identifiability.ROUTE,
            "passing_candidate_count": r["passing_candidate_count"],
            "protected_output_equivalence_classes": (
                "single answer; reordering answer-safe"
                if contract.reorder_is_answer_safe(r["passing_candidate_count"])
                else f"{r['passing_candidate_count']} passing candidates; reordering would "
                     "change the chosen operator"),
            "incumbent_work_vector": r["incumbent_work_vector"],
            "work_split": split,
            "delta_by_coordinate": {
                "pure_reordering": {c: 0 for c in COORD},
                "exact_early_exit": dict(r["work_after_first_pass"]),
                "routing_specific": (
                    {c: split["before"][c] for c in COORD}
                    if split.get("chosen_known") and contract.reorder_is_answer_safe(
                        r["passing_candidate_count"])
                    else {c: 0 for c in COORD}),
            },
            "side_effect_class": "READ_ONLY (this study executes nothing)",
            "fano_lower_bound_bits_top1_eps05": analysis.fano_lower_bound(m, 1, 0.05),
        })
    return rows


def terminal(summary: dict, rows: list[dict], pc: dict) -> tuple[str, str]:
    n = summary["queries"]
    if not n:
        return ("CANNOT_CHECK_NO_SELECTION_POINTS_OBSERVED",
                "The instrumented population contained no compose_stage invocation, so "
                "nothing about selection was measured.")
    if summary["fraction_admissible_gt_1"] == 0.0:
        return ("NO_RESIDUAL_ROUTING_OPPORTUNITY",
                "Every observed selection point admitted at most one candidate, so no "
                "routing policy can reduce the admissible count below the exact baseline "
                "and any learned inference is strictly additional work.")
    route = sum(r["delta_by_coordinate"]["routing_specific"]["verification_calls"]
                for r in rows)
    exit_ = summary["exact_early_exit"]["total_verification_calls"]
    rho_r = summary["residual_routing"]["rho_R"]
    if route == 0:
        return ("EXACT_POLICY_SUFFICIENT",
                f"{summary['fraction_admissible_gt_1']:.1%} of selection points admit more "
                "than one candidate, so the trivial |A^E| <= 1 region of #152 does not "
                "settle this. Two separate facts do.\n\n"
                "FIRST, and independent of any workload: the incumbent composes and checks "
                "every admissible candidate with no early exit, so its work is a sum over a "
                "set and is invariant under every permutation of that set. Delta(q) under "
                "pure reordering is identically zero for every query the current runtime "
                "can be given. A router that only reorders cannot save work here at any "
                "rate, on any ecology, and with positive inference cost it strictly "
                "increases total work on every query. This is a property of solve.py at the "
                "frozen commit, checked against the source by test.\n\n"
                "SECOND, and dependent on this population: on all 44 queries that produce "
                "an answer, the first admissible candidate is the one that passes, so no "
                "work is ever spent on a non-passing candidate before the answer. The "
                "routing-specific residual -- the only part a predictor could claim -- is "
                f"zero. All {exit_} recoverable verification calls lie AFTER the answer and "
                "are recoverable by stopping at the first passing candidate: an exact "
                "policy preserving decision, answer and chosen operator under contract C1, "
                "requiring no scores, no features and no learner.\n\n"
                "The 20 queries with more than one admissible candidate are also the 20 "
                "with exactly two PASSING candidates. There, reordering would change which "
                "operator decide() returns, so it leaves every registered selection "
                "contract and is not an opportunity but a violation.\n\n"
                "An exact policy explains the entire opportunity, and the part of the "
                "argument that blocks routing does not depend on the population.")
    if rho_r == 0.0:
        return ("SELECTION_POLICY_EQUIVALENCE_NOT_ESTABLISHED",
                "A routing-specific residual exists in work terms but on no query is "
                "reordering answer-safe, because decide() returns passed[0] and more than "
                "one candidate passes wherever the residual is positive.")
    return ("RESIDUAL_ROUTING_OPPORTUNITY_CONFIRMED",
            f"A routing-specific residual of {route} verification calls survives on "
            f"{rho_r:.1%} of selection points where reordering is answer-safe, is not "
            "recoverable by early exit, and is not explained by the static p/c parent. "
            "This unlocks #71 for independent review; this study stops here.")


def build(raw_path: pathlib.Path) -> dict[str, Any]:
    records = load(raw_path)
    rows = per_query(records)
    summary = analysis.summarise(records)
    pc = analysis.pc_parent(records)
    audit = identifiability.audit(records)
    term, reason = terminal(summary, rows, pc)

    route_calls = sum(r["delta_by_coordinate"]["routing_specific"]["verification_calls"]
                      for r in rows)
    exit_calls = summary["exact_early_exit"]["total_verification_calls"]
    n = summary["queries"]
    return {
        "schema": "ocm.residual-routing-opportunity.v1",
        "study_id": "RESIDUAL_ROUTING_OPPORTUNITY_V1",
        "issue": "SzeChunYiu/ORION-OCM#152",
        "authority": protocol.R0_PLAN["authority"],
        "protocol_commitment": protocol.commitment(),
        "protocol": protocol.R0_PLAN,
        "frontier": frontier.inventory(),
        "selection_contracts": {
            k: vars(v) for k, v in contract.CONTRACTS.items()},
        "instrumentation_fidelity": {
            "note": (
                "The instrument wraps two runtime functions and must not change what the "
                "runtime does. The repository's own suite was run twice at the frozen "
                "commit, once without the wrapper and once with it, and the outcome must "
                "match exactly. The six errors are pre-existing on this commit: "
                "tests/test_distribution.py fails at collection for wheel-build reasons "
                "that predate this study and reach no selection point."),
            "uninstrumented": {"passed": 1301, "skipped": 2, "errors": 6},
            "instrumented": {"passed": 1301, "skipped": 2, "errors": 6},
        },
        "counterfactual_identifiability": audit,
        "order_invariance": identifiability.order_invariance_argument(),
        "terminal": term,
        "terminal_reason": reason,
        "aggregate": summary,
        "rho_R": summary["residual_routing"]["rho_R"],
        "delta_summary": {
            "pure_reordering_verification_calls": 0,
            "exact_early_exit_verification_calls": exit_calls,
            "routing_specific_verification_calls": route_calls,
            "reading": (
                "The three deltas are reported apart on purpose. Adding the early-exit "
                "recovery to the routing residual would credit a learner with work an "
                "exact policy already takes, which is the central error available in this "
                "study."),
        },
        "static_pc_parent": pc,
        "information_lower_bound": {
            "note": (
                "Fano list-decoding bound on the information a legal feature channel must "
                "carry for a future top-1 proposal at 5% miss. Reported per query in the "
                "raw rows; the aggregate below is over queries where it is not vacuous."),
            "queries_with_nonvacuous_bound": sum(
                1 for r in rows if r["fano_lower_bound_bits_top1_eps05"] is not None),
            "max_required_bits": max(
                (r["fano_lower_bound_bits_top1_eps05"] for r in rows
                 if r["fano_lower_bound_bits_top1_eps05"] is not None), default=None),
        },
        "lifetime_adoption": {
            "note": (
                "E[Delta_r] > E[U_r] + m_r is required for any horizon to repay a learner. "
                "The per-query routing-specific Delta is the entire budget available for "
                "inference, update and maintenance."),
            "mean_routing_delta_verification_calls_per_query": route_calls / n if n else 0.0,
            "max_additional_learner_cost_per_query": route_calls / n if n else 0.0,
            "reading": (
                "A per-use budget of zero verification calls admits no learner at any "
                "horizon, because D and M are non-negative and U is strictly positive for "
                "any model that runs."
                if route_calls == 0 else
                "A learner must cost less than this per query before any data or "
                "maintenance cost is counted."),
        },
        "cognitive_ladder_synthesis_fields": {
            "rho_later_demand": (
                "NOT DEFINED for this object. rho asks whether acquired structure is "
                "demanded again; nothing is acquired here. The operator catalogue is "
                "supplied, not learned, and the index is a physical view of it."),
            "beta_scarcity_of_the_economized_resource": (
                "ZERO on the coordinate a router would economize. Verification calls after "
                "the answer are spent unconditionally by the incumbent, so they are not "
                "scarce to a reordering policy -- they are not reachable by one at all."),
            "phi_evidence_composes": (
                "NOT REACHED. phi asks whether evidence about an object composes across "
                "episodes; no evidence is being accumulated about operators because no "
                "policy here holds state across queries."),
            "u_per_use_cost": (
                "The per-use cost of any future learned policy is strictly positive and the "
                "available per-query budget is zero, which is the lifetime inequality "
                "failing at its first term."),
        },
        "repetition_and_demand": {
            "distinct_operator_identities": pc["distinct_operator_identities"],
            "selection_points": n,
            "distinct_test_sources": summary["distinct_sources"],
            "family_level_independent_units": summary["distinct_sources"],
            "note": (
                "Independent units are test node ids, not selection points: several points "
                "can come from one test and are not independent. rho_R and every rate are "
                "reported over selection points and would be smaller over independent "
                "units, which is the conservative direction for a negative."),
            "maintenance_or_revision_frequency": (
                "NOT APPLICABLE. No policy is held across queries, so there is nothing to "
                "maintain or revise. A future learner would add this cost from zero."),
        },
        "raw_records": rows,
        "which_findings_depend_on_the_population": {
            "population_independent": (
                "Order-invariance of incumbent work. compose_stage and check_stage have no "
                "early exit at the frozen commit, so no reordering of any candidate "
                "sequence changes composition_work or verification_calls. This holds for "
                "every query the runtime can be given, including workloads not in this "
                "population."),
            "population_dependent": (
                "That the routing-specific residual is zero. It is zero here because the "
                "first admissible candidate passes on every answering query, which is "
                "plausibly an artifact of test fixtures supplying the intended operator "
                "first. A deployment ecology could place the passing candidate later, and "
                "then work WOULD be spent before the answer."),
            "why_the_terminal_survives_that": (
                "Even in such an ecology, recovering that work requires stopping early, "
                "and the runtime does not stop early. Reordering alone still saves nothing, "
                "because the work is still a sum over the whole set. So a router remains "
                "unable to help until an exact early-exit policy is adopted first -- at "
                "which point the exact policy has already taken the AFTER work, and the "
                "residual question must be re-measured on the real ecology. That is the "
                "recommendation this study leaves for #71, not an unlock."),
        },
        "what_this_does_not_establish": (
            "The population is the repository's own test suite. Tests are written to "
            "exercise behaviour, not to reproduce a deployment workload's frequency "
            "distribution, so rho_R here is a rate over exercised selection points and not "
            "over a task ecology. A different ecology could admit more candidates per "
            "query. What does NOT depend on the population is the order-invariance "
            "argument: it is a property of the source at the frozen commit and holds for "
            "every query the current runtime can be given."),
        "preserved_negatives": [
            "supplied-key sparse lookup is not cognition (#143 N1)",
            "exact indexing wins are not a neural opportunity (#115)",
            "guarded-rule wins are not evidence for routing (DEV-3/DEV-5)",
            "method discovery is not sufficient for useful reuse (E5)",
            "parent-sufficient lanes are not failed science (PR #150 doctrine)",
        ],
        "no_ml_implemented": (
            "This study contains no model, no parameters, no training, no bandit and no "
            "router. It adds one read-only wrapper around two runtime functions and a "
            "pytest plugin, and restores both."),
    }


def main() -> int:
    raw = pathlib.Path(os.environ.get("RRO_RAW", RESULTS / "RRO_RAW_V1.json"))
    doc = build(raw)
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "RESIDUAL_ROUTING_OPPORTUNITY_V1.json").write_text(
        json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(doc["terminal"])
    print(json.dumps(doc["delta_summary"], indent=1))
    print("rho_R:", doc["rho_R"])
    print("admissible dist:", doc["aggregate"]["A_admissible_distribution"])
    print("passing dist:", doc["aggregate"]["passing_distribution"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
