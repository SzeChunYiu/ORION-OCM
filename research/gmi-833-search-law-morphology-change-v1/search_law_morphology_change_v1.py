#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from itertools import permutations, product
import json
from typing import Any, Mapping, Sequence

SOURCE_MAIN = "6368cda406d8e3395283049abacb36129ae94637"
FREEZE_COMMIT = "619e44aca017d288435afce6e6f9765e675dde6a"
CLAIM_CEILING = "GMI_FINITE_DETERMINISTIC_SEARCH_LAW_MORPHOLOGY_DISAGREEMENT_DERIVED_AT_REGISTERED_SCOPE"
FORBIDDEN_PROMOTIONS = [
    "ANY_SEARCH_LAW_CHANGE_ALTERS_MORPHOLOGY",
    "SEARCH_LAW_INVARIANT_IDENTITY_UNDER_GLOBAL_TIES",
    "STOCHASTIC_SEARCH_LAW_THEOREM",
    "UNIVERSAL_SEARCHER_DOMINANCE",
    "REAL_OPTIMIZER_CONVERGENCE",
    "PROSPECTIVE_MORPHOLOGY_TRANSITIONS_PREDICTED",
    "P3_RECOVERY_COMPLETE",
    "COMPLETE_GMI",
]
PARENT_PINS = {
    "finite_search_budget": {
        "path": "research/gmi-833-finite-search-budget-morphology-v1/RESULT_V1.json",
        "blob": "4ea315e651475cc8afcc39860a0d2ac621e9f571",
    },
    "section_e_e1": {
        "path": "research/gmi-section-e-reachability-v1/RESULT_E1.json",
        "blob": "369d3bd09279c4136ffeed469d0ffb0b6b5d443b",
    },
    "section_e_e2": {
        "path": "research/gmi-section-e-searcher-comparison-v2/RESULT_E2.json",
        "blob": "106653e98a2c0415720a10cb6c5f86a6c7243fe6",
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


def validate_objective(morphologies: Sequence[str], objective: Mapping[str, Any]) -> dict[str, Fraction]:
    ms = validate_universe(morphologies)
    require(set(objective) == set(ms), "objective must define exactly every morphology")
    return {m: exact_fraction(objective[m]) for m in ms}


def validate_order(morphologies: Sequence[str], order: Sequence[str]) -> tuple[str, ...]:
    ms = validate_universe(morphologies)
    require(not isinstance(order, (str, bytes)), "search order must be a sequence")
    pi = tuple(order)
    require(len(pi) == len(ms), "search order must be complete")
    require(len(set(pi)) == len(pi), "search order must not contain duplicates")
    require(set(pi) == set(ms), "search order must be a permutation of morphology universe")
    return pi


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


def validate_law(
    morphologies: Sequence[str],
    order: Sequence[str],
    costs: Mapping[str, Any],
) -> tuple[tuple[str, ...], dict[str, Fraction]]:
    ms = validate_universe(morphologies)
    pi = validate_order(ms, order)
    cs = validate_costs(ms, costs)
    return pi, cs


def completion_thresholds(
    morphologies: Sequence[str], order: Sequence[str], costs: Mapping[str, Any]
) -> tuple[Fraction, ...]:
    pi, cs = validate_law(morphologies, order, costs)
    total = Fraction(0)
    out = []
    for m in pi:
        total += cs[m]
        out.append(total)
    return tuple(out)


def select_at_budget(
    morphologies: Sequence[str],
    objective: Mapping[str, Any],
    order: Sequence[str],
    costs: Mapping[str, Any],
    budget: Any,
) -> dict[str, Any]:
    ms = validate_universe(morphologies)
    obj = validate_objective(ms, objective)
    pi, cs = validate_law(ms, order, costs)
    b = validate_budget(budget)
    prefix = []
    spent = Fraction(0)
    for m in pi:
        completion = spent + cs[m]
        if completion > b:
            break
        spent = completion
        prefix.append(m)
    global_value = min(obj.values())
    if not prefix:
        return {
            "budget": b,
            "evaluated_prefix": (),
            "selected": None,
            "selected_value": None,
            "regret": None,
            "global_value": global_value,
            "terminal": "NO_EVALUATED_CANDIDATE",
        }
    best = min(obj[m] for m in prefix)
    selected = next(m for m in prefix if obj[m] == best)
    return {
        "budget": b,
        "evaluated_prefix": tuple(prefix),
        "selected": selected,
        "selected_value": best,
        "regret": best - global_value,
        "global_value": global_value,
        "terminal": "FINITE_BUDGET_INCUMBENT",
    }


def recovery_threshold(
    morphologies: Sequence[str],
    objective: Mapping[str, Any],
    order: Sequence[str],
    costs: Mapping[str, Any],
) -> Fraction:
    ms = validate_universe(morphologies)
    obj = validate_objective(ms, objective)
    pi, cs = validate_law(ms, order, costs)
    g = min(obj.values())
    total = Fraction(0)
    for m in pi:
        total += cs[m]
        if obj[m] == g:
            return total
    raise AssertionError("complete law omitted every global optimizer")


def compare_at_budget(
    morphologies: Sequence[str],
    objective: Mapping[str, Any],
    law1_order: Sequence[str],
    law1_costs: Mapping[str, Any],
    law2_order: Sequence[str],
    law2_costs: Mapping[str, Any],
    budget: Any,
) -> dict[str, Any]:
    ms = validate_universe(morphologies)
    obj = validate_objective(ms, objective)
    # Both laws are forced through the same universe/objective contract.
    validate_law(ms, law1_order, law1_costs)
    validate_law(ms, law2_order, law2_costs)
    b = validate_budget(budget)
    a = select_at_budget(ms, obj, law1_order, law1_costs, b)
    c = select_at_budget(ms, obj, law2_order, law2_costs, b)
    s1, s2 = a["selected"], c["selected"]
    v1, v2 = a["selected_value"], c["selected_value"]
    if s1 is None and s2 is None:
        classification = "AGREEMENT_NO_EVALUATED_CANDIDATE"
    elif (s1 is None) != (s2 is None):
        classification = "DISAGREEMENT_AVAILABILITY"
    elif s1 == s2:
        classification = "AGREEMENT_IDENTITY"
    elif v1 != v2:
        classification = "DISAGREEMENT_VALUE"
    else:
        classification = "DISAGREEMENT_EQUAL_VALUE_IDENTITY"
    disagree = s1 != s2
    decomposition_ok = (
        (not disagree and classification.startswith("AGREEMENT"))
        or (disagree and classification in {
            "DISAGREEMENT_AVAILABILITY",
            "DISAGREEMENT_VALUE",
            "DISAGREEMENT_EQUAL_VALUE_IDENTITY",
        })
    )
    return {
        "budget": b,
        "law1": a,
        "law2": c,
        "identity_disagreement": disagree,
        "value_disagreement": (v1 != v2) if (v1 is not None and v2 is not None) else None,
        "classification": classification,
        "decomposition_ok": decomposition_ok,
    }


def compare_registered_worlds(world1: Mapping[str, Any], world2: Mapping[str, Any], budget: Any) -> dict[str, Any]:
    m1 = validate_universe(world1.get("morphologies", ()))
    m2 = validate_universe(world2.get("morphologies", ()))
    require(m1 == m2, "compared laws must use the same morphology universe and ordering of identities")
    o1 = validate_objective(m1, world1.get("objective", {}))
    o2 = validate_objective(m2, world2.get("objective", {}))
    require(o1 == o2, "compared laws must use identical objective semantics")
    return compare_at_budget(
        m1, o1,
        world1.get("order", ()), world1.get("costs", {}),
        world2.get("order", ()), world2.get("costs", {}),
        budget,
    )


def combined_threshold_cells(
    morphologies: Sequence[str],
    law1_order: Sequence[str], law1_costs: Mapping[str, Any],
    law2_order: Sequence[str], law2_costs: Mapping[str, Any],
) -> tuple[tuple[Fraction, Fraction | None], ...]:
    t = sorted(set(completion_thresholds(morphologies, law1_order, law1_costs)) |
               set(completion_thresholds(morphologies, law2_order, law2_costs)))
    if not t:
        return ((Fraction(0), None),)
    cells = []
    start = Fraction(0)
    for threshold in t:
        if threshold > start:
            cells.append((start, threshold))
        start = threshold
    cells.append((start, None))
    return tuple(cells)


def _cell_representatives(start: Fraction, end: Fraction | None) -> tuple[Fraction, ...]:
    if end is None:
        return (start, start + 1, start + Fraction(7, 3))
    if start == end:
        return (start,)
    mid = (start + end) / 2
    # Half-open cell includes start and excludes end.
    return tuple(dict.fromkeys((start, mid, (2 * start + end) / 3)))


def threshold_cell_certificate(
    morphologies: Sequence[str], objective: Mapping[str, Any],
    law1_order: Sequence[str], law1_costs: Mapping[str, Any],
    law2_order: Sequence[str], law2_costs: Mapping[str, Any],
) -> dict[str, Any]:
    cells = combined_threshold_cells(morphologies, law1_order, law1_costs, law2_order, law2_costs)
    rows = []
    all_constant = True
    for start, end in cells:
        reps = _cell_representatives(start, end)
        results = [compare_at_budget(
            morphologies, objective,
            law1_order, law1_costs, law2_order, law2_costs, b
        ) for b in reps]
        signatures = [(r["law1"]["selected"], r["law2"]["selected"], r["classification"]) for r in results]
        constant = len(set(signatures)) == 1
        all_constant = all_constant and constant
        rows.append({
            "start": start,
            "end": end,
            "representatives": reps,
            "signature": signatures[0],
            "constant": constant,
        })
    return {"cells": tuple(rows), "all_cells_constant": all_constant}


def eventual_agreement_certificate(
    morphologies: Sequence[str], objective: Mapping[str, Any],
    law1_order: Sequence[str], law1_costs: Mapping[str, Any],
    law2_order: Sequence[str], law2_costs: Mapping[str, Any],
) -> dict[str, Any]:
    ms = validate_universe(morphologies)
    obj = validate_objective(ms, objective)
    global_value = min(obj.values())
    global_argmin = tuple(m for m in ms if obj[m] == global_value)
    b1 = recovery_threshold(ms, obj, law1_order, law1_costs)
    b2 = recovery_threshold(ms, obj, law2_order, law2_costs)
    threshold = max(b1, b2)
    at_threshold = compare_at_budget(ms, obj, law1_order, law1_costs, law2_order, law2_costs, threshold)
    unique = len(global_argmin) == 1
    return {
        "global_argmin": global_argmin,
        "global_value": global_value,
        "law1_recovery_threshold": b1,
        "law2_recovery_threshold": b2,
        "joint_recovery_threshold": threshold,
        "unique_global_optimum": unique,
        "at_joint_threshold": at_threshold,
        "unique_optimum_eventual_identity_agreement": (not unique) or (
            at_threshold["law1"]["selected"] == global_argmin[0]
            and at_threshold["law2"]["selected"] == global_argmin[0]
        ),
    }


def exhaustive_census() -> dict[str, Any]:
    names = ("a", "b", "c", "d")
    schedule_pairs = 0
    budget_points = 0
    identity_agreement_points = 0
    value_disagreement_points = 0
    equal_value_identity_disagreement_points = 0
    failures: list[dict[str, Any]] = []
    changed_law_all_budget_agreement_worlds = 0
    tied_complete_identity_disagreement_worlds = 0
    unique_worlds = 0
    unique_eventual_agreement_checks = 0
    injective_disagreement_checks = 0

    for n in range(1, 5):
        ms = names[:n]
        unit = {m: 1 for m in ms}
        pis = tuple(permutations(ms))
        for scores_tuple in product(range(3), repeat=n):
            obj = dict(zip(ms, scores_tuple))
            global_value = min(scores_tuple)
            global_argmin = {ms[i] for i, v in enumerate(scores_tuple) if v == global_value}
            unique = len(global_argmin) == 1
            injective = len(set(scores_tuple)) == n
            if unique:
                unique_worlds += 1
            for pi1 in pis:
                b1 = next(i + 1 for i, m in enumerate(pi1) if obj[m] == global_value)
                for pi2 in pis:
                    schedule_pairs += 1
                    b2 = next(i + 1 for i, m in enumerate(pi2) if obj[m] == global_value)
                    all_agree = True
                    complete_cmp = None
                    for budget in range(n + 1):
                        budget_points += 1
                        r = compare_at_budget(ms, obj, pi1, unit, pi2, unit, budget)
                        if not r["decomposition_ok"]:
                            failures.append({"kind": "decomposition", "n": n, "scores": scores_tuple, "pi1": pi1, "pi2": pi2, "budget": budget})
                        if r["identity_disagreement"]:
                            all_agree = False
                            if r["classification"] == "DISAGREEMENT_VALUE":
                                value_disagreement_points += 1
                            elif r["classification"] == "DISAGREEMENT_EQUAL_VALUE_IDENTITY":
                                equal_value_identity_disagreement_points += 1
                                if injective:
                                    failures.append({"kind": "injective_equal_value_identity", "n": n, "scores": scores_tuple, "pi1": pi1, "pi2": pi2, "budget": budget})
                            if injective and budget > 0:
                                injective_disagreement_checks += 1
                                if r["classification"] != "DISAGREEMENT_VALUE":
                                    failures.append({"kind": "injective_disagreement_not_value", "n": n, "scores": scores_tuple, "pi1": pi1, "pi2": pi2, "budget": budget})
                        else:
                            identity_agreement_points += 1
                        if unique and budget >= max(b1, b2):
                            unique_eventual_agreement_checks += 1
                            g = next(iter(global_argmin))
                            if r["law1"]["selected"] != g or r["law2"]["selected"] != g:
                                failures.append({"kind": "unique_eventual_agreement", "n": n, "scores": scores_tuple, "pi1": pi1, "pi2": pi2, "budget": budget})
                        if budget == n:
                            complete_cmp = r
                    if pi1 != pi2 and all_agree:
                        changed_law_all_budget_agreement_worlds += 1
                    if len(global_argmin) > 1 and complete_cmp and complete_cmp["identity_disagreement"]:
                        tied_complete_identity_disagreement_worlds += 1
    return {
        "objective_alphabet": (0, 1, 2),
        "max_morphologies": 4,
        "schedule_pairs": schedule_pairs,
        "budget_points": budget_points,
        "identity_agreement_points": identity_agreement_points,
        "value_disagreement_points": value_disagreement_points,
        "equal_value_identity_disagreement_points": equal_value_identity_disagreement_points,
        "changed_law_all_budget_agreement_worlds": changed_law_all_budget_agreement_worlds,
        "tied_complete_identity_disagreement_worlds": tied_complete_identity_disagreement_worlds,
        "unique_worlds": unique_worlds,
        "unique_eventual_agreement_checks": unique_eventual_agreement_checks,
        "injective_disagreement_checks": injective_disagreement_checks,
        "failures": failures,
    }


def witness_controls() -> dict[str, Any]:
    # Value disagreement under a unique global optimum.
    ms = ("best", "mid", "bad")
    obj = {"best": 0, "mid": 1, "bad": 2}
    unit = {m: 1 for m in ms}
    value = compare_at_budget(ms, obj, ("best", "mid", "bad"), unit, ("bad", "mid", "best"), unit, 1)

    # Equal value but different identity due to tied optima.
    tie_obj = {"a": 0, "b": 0, "c": 1}
    tie_unit = {"a": 1, "b": 1, "c": 1}
    identity_only = compare_at_budget(("a", "b", "c"), tie_obj, ("a", "b", "c"), tie_unit, ("b", "a", "c"), tie_unit, 3)

    # Law changed but selected morphology agrees for all budgets.
    no_change = [compare_at_budget(ms, obj, ("best", "mid", "bad"), unit, ("best", "bad", "mid"), unit, b) for b in range(4)]

    # Rational, non-aligned thresholds exercise threshold-cell geometry and availability disagreement.
    rational_ms = ("a", "b", "c")
    rational_obj = {"a": 2, "b": 1, "c": 0}
    costs1 = {"a": "1/2", "b": "3/2", "c": "1"}
    costs2 = {"a": "1/2", "b": "3/2", "c": "2"}
    rational_cells = threshold_cell_certificate(
        rational_ms, rational_obj,
        ("a", "b", "c"), costs1,
        ("b", "a", "c"), costs2,
    )
    availability = compare_at_budget(
        rational_ms, rational_obj,
        ("a", "b", "c"), costs1,
        ("b", "a", "c"), costs2,
        1,
    )

    unique_eventual = eventual_agreement_certificate(
        ms, obj,
        ("best", "mid", "bad"), unit,
        ("bad", "mid", "best"), unit,
    )
    tie_eventual = eventual_agreement_certificate(
        ("a", "b", "c"), tie_obj,
        ("a", "b", "c"), tie_unit,
        ("b", "a", "c"), tie_unit,
    )

    return {
        "value_disagreement": value,
        "equal_value_identity_disagreement": identity_only,
        "changed_law_no_morphology_change": no_change,
        "rational_threshold_cells": rational_cells,
        "availability_disagreement": availability,
        "unique_global_eventual_agreement": unique_eventual,
        "tied_global_complete_identity_persistence": tie_eventual,
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
    rejected("zero_cost_rejected", lambda: validate_costs(("a",), {"a": 0}))
    rejected("negative_cost_rejected", lambda: validate_costs(("a",), {"a": -1}))
    rejected("float_cost_rejected", lambda: validate_costs(("a",), {"a": 1.0}))
    rejected("negative_budget_rejected", lambda: validate_budget(-1))
    rejected("float_budget_rejected", lambda: validate_budget(1.0))
    rejected("bool_budget_rejected", lambda: validate_budget(True))
    rejected(
        "mismatched_universe_rejected",
        lambda: compare_registered_worlds(
            {"morphologies": ("a", "b"), "objective": {"a": 0, "b": 1}, "order": ("a", "b"), "costs": {"a": 1, "b": 1}},
            {"morphologies": ("a", "c"), "objective": {"a": 0, "c": 1}, "order": ("a", "c"), "costs": {"a": 1, "c": 1}},
            1,
        ),
    )
    rejected(
        "mismatched_objective_semantics_rejected",
        lambda: compare_registered_worlds(
            {"morphologies": ("a", "b"), "objective": {"a": 0, "b": 1}, "order": ("a", "b"), "costs": {"a": 1, "b": 1}},
            {"morphologies": ("a", "b"), "objective": {"a": 1, "b": 0}, "order": ("a", "b"), "costs": {"a": 1, "b": 1}},
            1,
        ),
    )
    return checks


def parent_boundary() -> dict[str, Any]:
    return {
        "finite_search_budget_877": {
            "parent_owned": True,
            "claim_ceiling": "GMI_FINITE_SEARCH_PREFIX_MORPHOLOGY_SELECTION_DERIVED_AT_REGISTERED_SCOPE",
            "registered_fact": "single-law finite-budget prefix selection and exact first-global-optimum recovery threshold",
        },
        "section_e_712_724": {
            "parent_owned": True,
            "registered_fact": "same-world finite-budget search and encoding dependence is already evidenced across parent search mechanisms",
            "outside_child_theorem": "stochastic and differentiable search mechanisms remain parent evidence only",
        },
        "residual": "exact deterministic two-law identity/value disagreement decomposition, threshold-cell geometry, and eventual-agreement versus tie-persistence conditions",
    }


def build_receipt() -> dict[str, Any]:
    census = exhaustive_census()
    w = witness_controls()
    hostiles = hostile_controls()
    no_change_all = all(not r["identity_disagreement"] for r in w["changed_law_no_morphology_change"])
    tie = w["equal_value_identity_disagreement"]
    tied_complete = w["tied_global_complete_identity_persistence"]["at_joint_threshold"]
    checks = {
        "census_schedule_pairs_exact": census["schedule_pairs"] == 47667,
        "census_budget_points_exact": census["budget_points"] == 237282,
        "census_zero_failures": census["failures"] == [],
        "census_exercises_value_disagreement": census["value_disagreement_points"] > 0,
        "census_exercises_equal_value_identity_disagreement": census["equal_value_identity_disagreement_points"] > 0,
        "census_exercises_changed_law_no_change": census["changed_law_all_budget_agreement_worlds"] > 0,
        "census_exercises_tied_complete_persistence": census["tied_complete_identity_disagreement_worlds"] > 0,
        "census_exercises_unique_eventual_agreement": census["unique_eventual_agreement_checks"] > 0,
        "value_disagreement_witness": w["value_disagreement"]["classification"] == "DISAGREEMENT_VALUE",
        "equal_value_identity_witness": tie["classification"] == "DISAGREEMENT_EQUAL_VALUE_IDENTITY" and tie["law1"]["selected_value"] == tie["law2"]["selected_value"],
        "changed_law_need_not_change_morphology": no_change_all,
        "threshold_cells_piecewise_constant": w["rational_threshold_cells"]["all_cells_constant"],
        "availability_disagreement_typed": w["availability_disagreement"]["classification"] == "DISAGREEMENT_AVAILABILITY",
        "unique_global_eventual_agreement": w["unique_global_eventual_agreement"]["unique_optimum_eventual_identity_agreement"],
        "global_ties_can_preserve_identity_disagreement": tied_complete["identity_disagreement"] and tied_complete["law1"]["regret"] == 0 and tied_complete["law2"]["regret"] == 0,
        "all_hostiles_rejected": all(hostiles.values()),
    }
    return {
        "schema": "GMI_833_SEARCH_LAW_MORPHOLOGY_CHANGE_V1",
        "source_issue": 879,
        "master_issue": 833,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_pins": PARENT_PINS,
        "parent_boundary": parent_boundary(),
        "theorems": {
            "SLM_1": "two-law morphology disagreement is piecewise constant between the sorted union of law completion thresholds",
            "SLM_2": "when both incumbents exist, identity disagreement is exactly value disagreement or equal-value identity disagreement",
            "SLM_3": "a changed deterministic search law need not change observed morphology",
            "SLM_4": "with a unique global optimizer, both laws agree on it after max(B*_1,B*_2)",
            "SLM_5": "with tied global optima, complete zero-regret search can retain morphology identity disagreement",
            "SLM_6": "injective objectives exclude equal-value different-identity disagreement",
        },
        "census": census,
        "witnesses": w,
        "hostile_controls": hostiles,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


if __name__ == "__main__":
    print(canonical_json(build_receipt()), end="")
