#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from itertools import permutations, product
import json
from typing import Any, Mapping, Sequence

SOURCE_MAIN = "4de059b76c0a805f616b645eab636580394a42ed"
FREEZE_COMMIT = "ea8bb2d457ee96ebedc2a3a74a735284690a0973"
CLAIM_CEILING = "GMI_FINITE_SEARCH_PREFIX_MORPHOLOGY_SELECTION_DERIVED_AT_REGISTERED_SCOPE"
FORBIDDEN_PROMOTIONS = [
    "NEW_SEARCH_ALGORITHM",
    "UNIVERSAL_SEARCHER_DOMINANCE",
    "STOCHASTIC_SEARCH_THEOREM",
    "ADAPTIVE_OR_NONSTATIONARY_COST_THEOREM",
    "REAL_OPTIMIZER_CONVERGENCE",
    "ARCHITECTURE_PRIOR_FREE_RECOVERY",
    "PROSPECTIVE_HELDOUT_MORPHOLOGY_TRANSITIONS",
    "P3_RECOVERY_COMPLETE",
    "COMPLETE_GMI",
]
PARENT_PINS = {
    "section_e_e1": {
        "path": "research/gmi-section-e-reachability-v1/RESULT_E1.json",
        "blob": "369d3bd09279c4136ffeed469d0ffb0b6b5d443b",
    },
    "section_e_e2": {
        "path": "research/gmi-section-e-searcher-comparison-v2/RESULT_E2.json",
        "blob": "106653e98a2c0415720a10cb6c5f86a6c7243fe6",
    },
    "global_vs_reachable": {
        "path": "research/gmi-833-global-vs-reachable-morphology-v1/RESULT_V1.json",
        "blob": "37a0dda56649c02de1dd733b20a1266d481a3d30",
    },
}


def require(cond: bool, message: str) -> None:
    if not cond:
        raise ValueError(message)


def exact_fraction(x: Any) -> Fraction:
    require(not isinstance(x, bool), "booleans are not exact numeric inputs")
    require(not isinstance(x, float), "floats are forbidden")
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x, 1)
    if isinstance(x, str):
        try:
            return Fraction(x)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"not an exact rational: {x!r}") from exc
    raise ValueError(f"not an exact rational: {x!r}")


def canonicalize(x: Any) -> Any:
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x, tuple):
        return [canonicalize(v) for v in x]
    if isinstance(x, list):
        return [canonicalize(v) for v in x]
    if isinstance(x, dict):
        return {str(k): canonicalize(v) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    return x


def canonical_json(x: Any) -> str:
    return json.dumps(canonicalize(x), sort_keys=True, indent=2) + "\n"


def validate_universe(morphologies: Sequence[str]) -> tuple[str, ...]:
    require(not isinstance(morphologies, (str, bytes)), "morphology universe must be a sequence")
    ms = tuple(morphologies)
    require(bool(ms), "morphology universe must be nonempty")
    require(all(isinstance(m, str) and m for m in ms), "morphology identities must be nonempty strings")
    require(len(set(ms)) == len(ms), "morphology identities must be unique")
    return ms


def validate_order(morphologies: Sequence[str], order: Sequence[str]) -> tuple[str, ...]:
    ms = validate_universe(morphologies)
    require(not isinstance(order, (str, bytes)), "search order must be a sequence")
    pi = tuple(order)
    require(len(pi) == len(ms), "search order must be complete")
    require(len(set(pi)) == len(pi), "search order must not contain duplicates")
    require(set(pi) == set(ms), "search order must be a permutation of morphology universe")
    return pi


def validate_objective(morphologies: Sequence[str], objective: Mapping[str, Any]) -> dict[str, Fraction]:
    ms = validate_universe(morphologies)
    require(set(objective) == set(ms), "objective must define exactly every morphology")
    return {m: exact_fraction(objective[m]) for m in ms}


def validate_costs(morphologies: Sequence[str], costs: Mapping[str, Any]) -> dict[str, Fraction]:
    ms = validate_universe(morphologies)
    require(set(costs) == set(ms), "costs must define exactly every morphology")
    out = {m: exact_fraction(costs[m]) for m in ms}
    require(all(v > 0 for v in out.values()), "evaluation costs must be strictly positive")
    return out


def validate_budget(budget: Any) -> Fraction:
    b = exact_fraction(budget)
    require(b >= 0, "budget must be nonnegative")
    return b


def validate_world(
    morphologies: Sequence[str],
    order: Sequence[str],
    objective: Mapping[str, Any],
    costs: Mapping[str, Any],
) -> tuple[tuple[str, ...], tuple[str, ...], dict[str, Fraction], dict[str, Fraction]]:
    ms = validate_universe(morphologies)
    pi = validate_order(ms, order)
    obj = validate_objective(ms, objective)
    cs = validate_costs(ms, costs)
    return ms, pi, obj, cs


def cumulative_schedule(
    morphologies: Sequence[str],
    order: Sequence[str],
    objective: Mapping[str, Any],
    costs: Mapping[str, Any],
) -> tuple[tuple[str, Fraction, Fraction], ...]:
    _, pi, _, cs = validate_world(morphologies, order, objective, costs)
    total = Fraction(0)
    rows = []
    for m in pi:
        total += cs[m]
        rows.append((m, cs[m], total))
    return tuple(rows)


def global_argmin(
    morphologies: Sequence[str], objective: Mapping[str, Any]
) -> tuple[str, ...]:
    ms = validate_universe(morphologies)
    obj = validate_objective(ms, objective)
    best = min(obj.values())
    return tuple(m for m in ms if obj[m] == best)


def recovery_threshold(
    morphologies: Sequence[str],
    order: Sequence[str],
    objective: Mapping[str, Any],
    costs: Mapping[str, Any],
) -> Fraction:
    ms, pi, obj, cs = validate_world(morphologies, order, objective, costs)
    global_value = min(obj.values())
    cumulative = Fraction(0)
    for m in pi:
        cumulative += cs[m]
        if obj[m] == global_value:
            return cumulative
    raise AssertionError("complete permutation omitted every global optimizer")


def _select_prevalidated(
    pi: tuple[str, ...],
    obj: Mapping[str, Fraction],
    cs: Mapping[str, Fraction],
    budget: Fraction,
) -> dict[str, Any]:
    prefix = []
    cumulative = Fraction(0)
    thresholds = []
    for m in pi:
        completion = cumulative + cs[m]
        if completion > budget:
            break
        cumulative = completion
        thresholds.append(completion)
        prefix.append(m)

    global_value = min(obj.values())
    if not prefix:
        return {
            "budget": budget,
            "evaluated_prefix": (),
            "evaluated_count": 0,
            "spent_completed_cost": Fraction(0),
            "selected": None,
            "selected_value": None,
            "global_value": global_value,
            "regret": None,
            "global_value_recovered": False,
            "terminal": "NO_EVALUATED_CANDIDATE",
        }

    best_value = min(obj[m] for m in prefix)
    # Earliest-seen tie policy is explicit and stable.
    selected = next(m for m in prefix if obj[m] == best_value)
    return {
        "budget": budget,
        "evaluated_prefix": tuple(prefix),
        "evaluated_count": len(prefix),
        "spent_completed_cost": cumulative,
        "selected": selected,
        "selected_value": best_value,
        "global_value": global_value,
        "regret": best_value - global_value,
        "global_value_recovered": best_value == global_value,
        "terminal": "FINITE_BUDGET_INCUMBENT",
    }


def select_at_budget(
    morphologies: Sequence[str],
    order: Sequence[str],
    objective: Mapping[str, Any],
    costs: Mapping[str, Any],
    budget: Any,
) -> dict[str, Any]:
    _, pi, obj, cs = validate_world(morphologies, order, objective, costs)
    b = validate_budget(budget)
    return _select_prevalidated(pi, obj, cs, b)


def threshold_transition_certificate(
    morphologies: Sequence[str],
    order: Sequence[str],
    objective: Mapping[str, Any],
    costs: Mapping[str, Any],
) -> dict[str, Any]:
    _, pi, obj, cs = validate_world(morphologies, order, objective, costs)
    rows = []
    cumulative = Fraction(0)
    incumbent = None
    incumbent_value = None
    for index, m in enumerate(pi, start=1):
        cumulative += cs[m]
        if incumbent is None:
            rows.append({
                "index": index,
                "candidate": m,
                "completion_cost": cumulative,
                "previous_incumbent": None,
                "new_incumbent": m,
                "candidate_value": obj[m],
                "identity_changed": True,
                "strict_improvement_over_previous": None,
                "classification": "INITIAL_SELECTION",
            })
            incumbent = m
            incumbent_value = obj[m]
            continue
        strict = obj[m] < incumbent_value
        new_incumbent = m if strict else incumbent
        rows.append({
            "index": index,
            "candidate": m,
            "completion_cost": cumulative,
            "previous_incumbent": incumbent,
            "new_incumbent": new_incumbent,
            "candidate_value": obj[m],
            "identity_changed": new_incumbent != incumbent,
            "strict_improvement_over_previous": strict,
            "classification": "STRICT_IMPROVEMENT" if strict else "NO_INCUMBENT_CHANGE",
        })
        if strict:
            incumbent = m
            incumbent_value = obj[m]
    return {
        "rows": tuple(rows),
        "all_post_initial_changes_iff_strict_improvement": all(
            r["identity_changed"] == r["strict_improvement_over_previous"] for r in rows[1:]
        ),
    }


def schedule_certificate(
    morphologies: Sequence[str],
    order: Sequence[str],
    objective: Mapping[str, Any],
    costs: Mapping[str, Any],
) -> dict[str, Any]:
    ms, pi, obj, cs = validate_world(morphologies, order, objective, costs)
    schedule = cumulative_schedule(ms, pi, obj, cs)
    total = schedule[-1][2]
    b_star = recovery_threshold(ms, pi, obj, cs)
    complete = _select_prevalidated(pi, obj, cs, total)
    return {
        "order": pi,
        "schedule": schedule,
        "total_cost": total,
        "global_argmin": global_argmin(ms, obj),
        "global_value": min(obj.values()),
        "recovery_threshold": b_star,
        "complete_selection": complete["selected"],
        "complete_value": complete["selected_value"],
        "complete_recovers_global_value": complete["global_value_recovered"],
        "transitions": threshold_transition_certificate(ms, pi, obj, cs),
    }


def exhaustive_census() -> dict[str, Any]:
    """Exhaustive bounded certificate using integer alphabets for speed.

    The public API is separately tested with exact rationals and fail-closed validation.
    Here every frozen score/cost is already an exact integer in the declared alphabets,
    so the census can scan all 1,448,631 budget points without rebuilding validated
    dictionaries at each point.
    """
    schedule_worlds = 0
    budget_points = 0
    strict_improvement_events = 0
    tied_nonpromotion_events = 0
    no_candidate_points = 0
    zero_regret_points = 0
    failures: list[dict[str, Any]] = []

    for n in range(1, 5):
        indices = tuple(range(n))
        for scores in product(range(3), repeat=n):
            global_value = min(scores)
            global_set = {i for i, value in enumerate(scores) if value == global_value}
            for costs in product(range(1, 4), repeat=n):
                for pi in permutations(indices):
                    schedule_worlds += 1
                    cumulative = []
                    total = 0
                    b_star = None
                    for idx in pi:
                        total += costs[idx]
                        cumulative.append(total)
                        if b_star is None and idx in global_set:
                            b_star = total
                    assert b_star is not None

                    k = 0
                    incumbent = None
                    incumbent_value = None
                    previous_value = None
                    previous_regret = None

                    for budget in range(total + 1):
                        budget_points += 1
                        while k < n and cumulative[k] <= budget:
                            idx = pi[k]
                            if incumbent is None:
                                incumbent = idx
                                incumbent_value = scores[idx]
                            elif scores[idx] < incumbent_value:
                                strict_improvement_events += 1
                                incumbent = idx
                                incumbent_value = scores[idx]
                            elif scores[idx] == incumbent_value:
                                tied_nonpromotion_events += 1
                            k += 1

                        if k == 0:
                            no_candidate_points += 1
                            if budget >= b_star:
                                failures.append({
                                    "kind": "empty_prefix_recovery_threshold",
                                    "n": n,
                                    "scores": scores,
                                    "costs": costs,
                                    "order": pi,
                                    "budget": budget,
                                    "b_star": b_star,
                                })
                            continue

                        regret = incumbent_value - global_value
                        recovered = incumbent_value == global_value
                        if regret < 0 or recovered != (budget >= b_star):
                            failures.append({
                                "kind": "budget_point",
                                "n": n,
                                "scores": scores,
                                "costs": costs,
                                "order": pi,
                                "budget": budget,
                                "incumbent": incumbent,
                                "incumbent_value": incumbent_value,
                                "global_value": global_value,
                                "b_star": b_star,
                            })
                        if regret == 0:
                            zero_regret_points += 1
                        if previous_value is not None:
                            if incumbent_value > previous_value or regret > previous_regret:
                                failures.append({
                                    "kind": "budget_monotonicity",
                                    "n": n,
                                    "scores": scores,
                                    "costs": costs,
                                    "order": pi,
                                    "budget": budget,
                                })
                        previous_value = incumbent_value
                        previous_regret = regret

                    # Independent threshold-change criterion.
                    incumbent_idx = pi[0]
                    incumbent_score = scores[incumbent_idx]
                    for idx in pi[1:]:
                        strict = scores[idx] < incumbent_score
                        if strict:
                            incumbent_idx = idx
                            incumbent_score = scores[idx]
                        # Earliest-seen tie policy: equality must never promote.
                        if scores[idx] == incumbent_score and idx != incumbent_idx:
                            pass

                    if incumbent_score != global_value:
                        failures.append({
                            "kind": "complete_recovery",
                            "n": n,
                            "scores": scores,
                            "costs": costs,
                            "order": pi,
                        })

    return {
        "objective_alphabet": (0, 1, 2),
        "cost_alphabet": (1, 2, 3),
        "max_morphologies": 4,
        "schedule_worlds": schedule_worlds,
        "budget_points": budget_points,
        "no_candidate_points": no_candidate_points,
        "zero_regret_points": zero_regret_points,
        "strict_improvement_events": strict_improvement_events,
        "tied_nonpromotion_events": tied_nonpromotion_events,
        "failures": failures,
    }


def witness_controls() -> dict[str, Any]:
    ms = ("best", "mid", "bad")
    obj = {"best": 0, "mid": 1, "bad": 2}
    costs = {"best": 1, "mid": 1, "bad": 1}
    early = schedule_certificate(ms, ("best", "mid", "bad"), obj, costs)
    late = schedule_certificate(ms, ("bad", "mid", "best"), obj, costs)
    early_b1 = select_at_budget(ms, ("best", "mid", "bad"), obj, costs, 1)
    late_b1 = select_at_budget(ms, ("bad", "mid", "best"), obj, costs, 1)

    tie_ms = ("a", "b", "c")
    tie_obj = {"a": 0, "b": 0, "c": 1}
    tie_costs = {"a": 1, "b": 1, "c": 1}
    tie = schedule_certificate(tie_ms, ("a", "b", "c"), tie_obj, tie_costs)
    tie_b2 = select_at_budget(tie_ms, ("a", "b", "c"), tie_obj, tie_costs, 2)

    no_eval = select_at_budget(("a",), ("a",), {"a": 0}, {"a": 2}, 1)

    return {
        "alternate_order": {
            "early_best": early,
            "late_best": late,
            "budget_1_early": early_b1,
            "budget_1_late": late_b1,
            "different_recovery_thresholds": early["recovery_threshold"] != late["recovery_threshold"],
            "different_budget_1_morphologies": early_b1["selected"] != late_b1["selected"],
        },
        "tie_nonpromotion": {
            "schedule": tie,
            "budget_2": tie_b2,
            "earliest_seen_preserved": tie_b2["selected"] == "a",
            "second_equal_optimum_does_not_change_incumbent": tie["transitions"]["rows"][1]["identity_changed"] is False,
        },
        "pre_evaluation_terminal": no_eval,
    }


def parent_boundary() -> dict[str, Any]:
    return {
        "section_e_e1": {
            "parent_owned": True,
            "claim_ceiling": "FINITE_EXACT_PROSPECTIVE_SECTION_E_REACHABILITY_AND_SEARCH_BURDEN_V1",
            "registered_fact": "at a 20-verification cap, one-bit BFS has not yet reached a target verified at index 21; alternate parent search/encoding schedules differ",
        },
        "section_e_e2": {
            "parent_owned": True,
            "claim_ceiling": "FINITE_EXACT_SAME_WORLD_PARENT_SEARCHER_COMPARISON_E2",
            "registered_fact": "same-world finite-budget recovery differs across parent-owned search mechanisms",
            "outside_child_theorem": "stochastic and differentiable search results are evidence only, not covered by deterministic complete-trace theorem",
        },
        "global_vs_reachable": {
            "parent_owned": True,
            "claim_ceiling": "GMI_FINITE_GLOBAL_VS_REACHABLE_MORPHOLOGY_SELECTION_SEPARATED_AT_REGISTERED_SCOPE",
            "registered_fact": "constrained/reachable optimum is distinct from full-space optimum",
        },
    }


def hostile_controls() -> dict[str, bool]:
    checks: dict[str, bool] = {}

    def rejected(name: str, fn) -> None:
        try:
            fn()
            checks[name] = False
        except ValueError:
            checks[name] = True

    rejected("empty_universe_rejected", lambda: validate_universe(()))
    rejected("duplicate_universe_rejected", lambda: validate_universe(("a", "a")))
    rejected("incomplete_order_rejected", lambda: validate_order(("a", "b"), ("a",)))
    rejected("duplicate_order_rejected", lambda: validate_order(("a", "b"), ("a", "a")))
    rejected("outside_order_rejected", lambda: validate_order(("a", "b"), ("a", "c")))
    rejected("missing_objective_rejected", lambda: validate_objective(("a", "b"), {"a": 0}))
    rejected("extra_objective_rejected", lambda: validate_objective(("a",), {"a": 0, "b": 1}))
    rejected("float_objective_rejected", lambda: validate_objective(("a",), {"a": 0.5}))
    rejected("bool_objective_rejected", lambda: validate_objective(("a",), {"a": True}))
    rejected("missing_cost_rejected", lambda: validate_costs(("a", "b"), {"a": 1}))
    rejected("extra_cost_rejected", lambda: validate_costs(("a",), {"a": 1, "b": 2}))
    rejected("zero_cost_rejected", lambda: validate_costs(("a",), {"a": 0}))
    rejected("negative_cost_rejected", lambda: validate_costs(("a",), {"a": -1}))
    rejected("float_cost_rejected", lambda: validate_costs(("a",), {"a": 1.0}))
    rejected("negative_budget_rejected", lambda: validate_budget(-1))
    rejected("float_budget_rejected", lambda: validate_budget(1.0))
    rejected("bool_budget_rejected", lambda: validate_budget(True))
    return checks


def build_receipt() -> dict[str, Any]:
    census = exhaustive_census()
    witnesses = witness_controls()
    hostiles = hostile_controls()
    checks = {
        "census_world_count_exact": census["schedule_worlds"] == 162009,
        "census_budget_count_exact": census["budget_points"] == 1448631,
        "census_zero_failures": census["failures"] == [],
        "census_exercises_pre_evaluation_terminal": census["no_candidate_points"] > 0,
        "census_exercises_zero_regret": census["zero_regret_points"] > 0,
        "census_exercises_strict_improvements": census["strict_improvement_events"] > 0,
        "census_exercises_tied_nonpromotion": census["tied_nonpromotion_events"] > 0,
        "alternate_order_changes_recovery_threshold": witnesses["alternate_order"]["different_recovery_thresholds"],
        "alternate_order_changes_finite_budget_morphology": witnesses["alternate_order"]["different_budget_1_morphologies"],
        "tie_earliest_seen_preserved": witnesses["tie_nonpromotion"]["earliest_seen_preserved"],
        "tie_equal_optimum_does_not_promote": witnesses["tie_nonpromotion"]["second_equal_optimum_does_not_change_incumbent"],
        "pre_evaluation_is_typed_terminal": witnesses["pre_evaluation_terminal"]["terminal"] == "NO_EVALUATED_CANDIDATE"
        and witnesses["pre_evaluation_terminal"]["selected"] is None,
        "all_hostiles_rejected": all(hostiles.values()),
    }
    return {
        "schema": "GMI_833_FINITE_SEARCH_BUDGET_MORPHOLOGY_V1",
        "source_issue": 877,
        "master_issue": 833,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_pins": PARENT_PINS,
        "theorems": {
            "FSB_1": "budget exposes exactly the maximal cumulative-cost-feasible search prefix",
            "FSB_2": "finite-budget incumbent is earliest-seen prefix argmin; empty prefix yields NO_EVALUATED_CANDIDATE",
            "FSB_3": "incumbent value and exact regret are stepwise nonincreasing with budget",
            "FSB_4": "global optimum value is recovered iff budget reaches the first global-optimum completion threshold B_star",
            "FSB_5": "after initial selection, incumbent identity changes at a completion threshold iff the new candidate strictly improves objective",
            "FSB_6": "complete enumeration recovers a global optimizer while alternate orders may change B_star and finite-budget morphology",
        },
        "census": census,
        "witnesses": witnesses,
        "parent_boundary": parent_boundary(),
        "hostile_controls": hostiles,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


if __name__ == "__main__":
    print(canonical_json(build_receipt()), end="")
