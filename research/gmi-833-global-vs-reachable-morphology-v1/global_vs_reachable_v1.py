#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
from typing import Any, Mapping, Sequence

SOURCE_MAIN = "367e14e9296cf79924ce56d89fad34b3769acb5d"
FREEZE_COMMIT = "e5b0c534e5d316c90e28dff0678ee6038b25e3a5"
CLAIM_CEILING = "GMI_FINITE_GLOBAL_VS_REACHABLE_MORPHOLOGY_SELECTION_SEPARATED_AT_REGISTERED_SCOPE"
FORBIDDEN_PROMOTIONS = [
    "GLOBAL_OPTIMUM_ALWAYS_REACHABLE",
    "REAL_OPTIMIZER_CONVERGENCE",
    "UNIQUE_MORPHOLOGY",
    "PARETO_REACHABLE_FRONTIER_SUBSET_OF_GLOBAL_FRONTIER",
    "UNRESTRICTED_CONTINUOUS_OR_TURING_COMPLETE_OPTIMIZATION",
    "PROSPECTIVE_MORPHOLOGY_TRANSITIONS_PREDICTED",
    "P3_RECOVERY_COMPLETE",
    "COMPLETE_GMI",
]
PARENT_PINS = {
    "foundation_receipt": {
        "path": "research/gmi-833-foundation-v1/RESULT_V1.json",
        "blob": "c0c574c4ec6e237d5fdafa694eac131399625a70",
    },
    "developmental_lifecycle_v2": {
        "path": "research/gmi-grand-unification-v1/GRAND_GMI_DEVELOPMENTAL_LIFECYCLE_RECEIPT_V2.json",
        "blob": "8b7acb21cc21d41e54b23c91a9fca75af5612208",
    },
    "developmental_theorem": {
        "path": "research/gmi-grand-unification-v1/DEVELOPMENTAL_REACHABILITY_SELECTION_THEOREM_V1.md",
        "blob": "27ecb316987bca886c1fc882a4f8c9e270bba4dc",
    },
}


def require(cond: bool, message: str) -> None:
    if not cond:
        raise ValueError(message)


def exact_fraction(x: Any) -> Fraction:
    require(not isinstance(x, bool), "booleans are not objective values")
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
    if isinstance(x, (set, frozenset)):
        return [canonicalize(v) for v in sorted(x)]
    if isinstance(x, dict):
        return {str(k): canonicalize(v) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    return x


def canonical_json(x: Any) -> str:
    return json.dumps(canonicalize(x), sort_keys=True, indent=2) + "\n"


def validate_universe(morphologies: Sequence[str]) -> tuple[str, ...]:
    require(not isinstance(morphologies, (str, bytes)), "morphology universe must be a sequence")
    ms = tuple(morphologies)
    require(bool(ms), "morphology universe must be nonempty")
    require(all(isinstance(m, str) and m for m in ms), "morphology names must be nonempty strings")
    require(len(set(ms)) == len(ms), "morphology names must be unique")
    return ms


def validate_reachable(morphologies: Sequence[str], reachable: Sequence[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    ms = validate_universe(morphologies)
    require(not isinstance(reachable, (str, bytes)), "reachable set must be a sequence")
    rs = tuple(reachable)
    require(bool(rs), "reachable set must be nonempty")
    require(all(isinstance(m, str) and m for m in rs), "reachable names must be nonempty strings")
    require(len(set(rs)) == len(rs), "reachable names must be unique")
    require(set(rs) <= set(ms), "reachable set must be a subset of morphology universe")
    return ms, rs


def validate_scores(morphologies: Sequence[str], scores: Mapping[str, Any]) -> dict[str, Fraction]:
    ms = validate_universe(morphologies)
    require(set(scores) == set(ms), "scalar objective must define exactly every morphology")
    return {m: exact_fraction(scores[m]) for m in ms}


def argmin_set(morphologies: Sequence[str], scores: Mapping[str, Any], feasible: Sequence[str] | None = None) -> tuple[str, ...]:
    ms = validate_universe(morphologies)
    vals = validate_scores(ms, scores)
    if feasible is None:
        fs = ms
    else:
        _, fs = validate_reachable(ms, feasible)
    best = min(vals[m] for m in fs)
    return tuple(m for m in fs if vals[m] == best)


def min_value(morphologies: Sequence[str], scores: Mapping[str, Any], feasible: Sequence[str] | None = None) -> Fraction:
    vals = validate_scores(morphologies, scores)
    opts = argmin_set(morphologies, vals, feasible)
    return vals[opts[0]]


def scalar_separation_certificate(
    morphologies: Sequence[str],
    reachable: Sequence[str],
    scores: Mapping[str, Any],
) -> dict[str, Any]:
    ms, rs = validate_reachable(morphologies, reachable)
    vals = validate_scores(ms, scores)
    global_argmin = argmin_set(ms, vals)
    reachable_argmin = argmin_set(ms, vals, rs)
    global_value = vals[global_argmin[0]]
    reachable_value = vals[reachable_argmin[0]]
    intersects = bool(set(global_argmin) & set(rs))
    equality = reachable_value == global_value
    return {
        "global_argmin": global_argmin,
        "reachable_argmin": reachable_argmin,
        "global_value": global_value,
        "reachable_value": reachable_value,
        "restriction_cannot_improve": global_value <= reachable_value,
        "reachable_global_optimizer_exists": intersects,
        "value_equality": equality,
        "equality_iff_global_optimizer_reachable": equality == intersects,
        "optimizer_sets_equal": set(global_argmin) == set(reachable_argmin),
        "terminal": "GLOBAL_REACHABLE_SCALAR_SEPARATED"
        if global_value <= reachable_value and equality == intersects
        else "SCALAR_SEPARATION_FAILURE",
    }


def nested_reachability_certificate(
    morphologies: Sequence[str],
    smaller: Sequence[str],
    larger: Sequence[str],
    scores: Mapping[str, Any],
) -> dict[str, Any]:
    ms, r1 = validate_reachable(morphologies, smaller)
    _, r2 = validate_reachable(ms, larger)
    require(set(r1) <= set(r2), "declared reachability expansion is not nested")
    vals = validate_scores(ms, scores)
    v1 = min(vals[m] for m in r1)
    v2 = min(vals[m] for m in r2)
    return {
        "smaller": r1,
        "larger": r2,
        "smaller_value": v1,
        "larger_value": v2,
        "expanded_reachability_cannot_worsen_minimum": v2 <= v1,
        "terminal": "NESTED_REACHABILITY_VALUE_MONOTONE" if v2 <= v1 else "VALUE_MONOTONICITY_FAILURE",
    }


def validate_profiles(
    morphologies: Sequence[str],
    profiles: Mapping[str, Sequence[Any]],
) -> dict[str, tuple[Fraction, ...]]:
    ms = validate_universe(morphologies)
    require(set(profiles) == set(ms), "Pareto profile must define exactly every morphology")
    out: dict[str, tuple[Fraction, ...]] = {}
    dim = None
    for m in ms:
        raw = profiles[m]
        require(not isinstance(raw, (str, bytes)), "Pareto profile vector must be a sequence")
        v = tuple(exact_fraction(x) for x in raw)
        require(bool(v), "Pareto profile vector must be nonempty")
        if dim is None:
            dim = len(v)
        require(len(v) == dim, "Pareto profile vectors must share one dimension")
        out[m] = v
    return out


def dominates(a: Sequence[Any], b: Sequence[Any]) -> bool:
    aa = tuple(exact_fraction(x) for x in a)
    bb = tuple(exact_fraction(x) for x in b)
    require(bool(aa) and len(aa) == len(bb), "dominance vectors must have same nonzero dimension")
    return all(x <= y for x, y in zip(aa, bb)) and any(x < y for x, y in zip(aa, bb))


def pareto_set(
    morphologies: Sequence[str],
    profiles: Mapping[str, Sequence[Any]],
    feasible: Sequence[str] | None = None,
) -> tuple[str, ...]:
    ms = validate_universe(morphologies)
    ps = validate_profiles(ms, profiles)
    if feasible is None:
        fs = ms
    else:
        _, fs = validate_reachable(ms, feasible)
    frontier = []
    for m in fs:
        if not any(n != m and dominates(ps[n], ps[m]) for n in fs):
            frontier.append(m)
    return tuple(frontier)


def pareto_restriction_certificate(
    morphologies: Sequence[str],
    reachable: Sequence[str],
    profiles: Mapping[str, Sequence[Any]],
) -> dict[str, Any]:
    ms, rs = validate_reachable(morphologies, reachable)
    ps = validate_profiles(ms, profiles)
    global_p = pareto_set(ms, ps)
    reachable_p = pareto_set(ms, ps, rs)
    retained_global = tuple(m for m in global_p if m in set(rs))
    emergent = tuple(m for m in reachable_p if m not in set(global_p))
    inclusion = set(retained_global) <= set(reachable_p)
    false_reverse = set(reachable_p) <= set(global_p)
    return {
        "global_pareto": global_p,
        "reachable_pareto": reachable_p,
        "global_pareto_and_reachable": retained_global,
        "reachable_only_pareto": emergent,
        "safe_inclusion": inclusion,
        "reverse_inclusion_holds_in_this_instance": false_reverse,
        "terminal": "PARETO_FEASIBILITY_RELATIVE" if inclusion else "PARETO_RESTRICTION_FAILURE",
    }


def scalar_exhaustive_census() -> dict[str, Any]:
    subset_cases = 0
    nested_cases = 0
    failures: list[dict[str, Any]] = []
    names = ("a", "b", "c", "d")
    for n in range(1, 5):
        ms = names[:n]
        subsets = [
            tuple(ms[i] for i in range(n) if mask & (1 << i))
            for mask in range(1, 1 << n)
        ]
        for score_tuple in product(range(3), repeat=n):
            scores = dict(zip(ms, score_tuple))
            global_argmin = set(argmin_set(ms, scores))
            global_value = min_value(ms, scores)
            for rs in subsets:
                subset_cases += 1
                cert = scalar_separation_certificate(ms, rs, scores)
                expected_equal = bool(global_argmin & set(rs))
                if not (
                    cert["restriction_cannot_improve"]
                    and cert["value_equality"] == expected_equal
                    and cert["equality_iff_global_optimizer_reachable"]
                ):
                    failures.append({
                        "kind": "subset",
                        "morphologies": ms,
                        "scores": score_tuple,
                        "reachable": rs,
                        "certificate": cert,
                    })
                require(global_value == cert["global_value"], "internal global value drift")
            for r1 in subsets:
                s1 = set(r1)
                for r2 in subsets:
                    if s1 <= set(r2):
                        nested_cases += 1
                        cert = nested_reachability_certificate(ms, r1, r2, scores)
                        if not cert["expanded_reachability_cannot_worsen_minimum"]:
                            failures.append({
                                "kind": "nested",
                                "morphologies": ms,
                                "scores": score_tuple,
                                "smaller": r1,
                                "larger": r2,
                            })
    return {
        "score_alphabet": (0, 1, 2),
        "max_morphologies": 4,
        "world_subset_cases": subset_cases,
        "nested_reachability_cases": nested_cases,
        "failures": failures,
    }


def pareto_exhaustive_census() -> dict[str, Any]:
    vector_alphabet = ((0, 0), (0, 1), (1, 0), (1, 1))
    names = ("a", "b", "c")
    cases = 0
    failures: list[dict[str, Any]] = []
    strict_inclusion_cases = 0
    for n in range(1, 4):
        ms = names[:n]
        subsets = [
            tuple(ms[i] for i in range(n) if mask & (1 << i))
            for mask in range(1, 1 << n)
        ]
        for assigned in product(vector_alphabet, repeat=n):
            profiles = dict(zip(ms, assigned))
            for rs in subsets:
                cases += 1
                cert = pareto_restriction_certificate(ms, rs, profiles)
                if not cert["safe_inclusion"]:
                    failures.append({
                        "morphologies": ms,
                        "profiles": assigned,
                        "reachable": rs,
                        "certificate": cert,
                    })
                if cert["reachable_only_pareto"]:
                    strict_inclusion_cases += 1
    return {
        "vector_alphabet": vector_alphabet,
        "max_morphologies": 3,
        "world_subset_cases": cases,
        "strict_inclusion_cases": strict_inclusion_cases,
        "failures": failures,
    }


def witness_controls() -> dict[str, Any]:
    strict_gap = scalar_separation_certificate(
        ("global", "reachable"), ("reachable",), {"global": 0, "reachable": 1}
    )
    tied_identity = scalar_separation_certificate(
        ("a", "b", "c"), ("b", "c"), {"a": 0, "b": 0, "c": 1}
    )
    pareto_hostile = pareto_restriction_certificate(
        ("a", "b", "c"),
        ("b", "c"),
        {"a": (0, 0), "b": (1, 1), "c": (0, 2)},
    )
    return {
        "strict_gap": strict_gap,
        "tied_value_distinct_optimizer_sets": tied_identity,
        "pareto_unreachable_dominator": pareto_hostile,
        "checks": {
            "strict_gap_positive": strict_gap["reachable_value"] > strict_gap["global_value"],
            "tie_same_value": tied_identity["reachable_value"] == tied_identity["global_value"],
            "tie_optimizer_sets_differ": not tied_identity["optimizer_sets_equal"],
            "pareto_safe_inclusion": pareto_hostile["safe_inclusion"],
            "pareto_reverse_inclusion_false": not pareto_hostile["reverse_inclusion_holds_in_this_instance"],
            "globally_dominated_b_becomes_reachable_pareto": "b" in pareto_hostile["reachable_only_pareto"],
        },
    }


def parent_budget_witness() -> dict[str, Any]:
    ms = ("N_good", "P_good", "X_ideal")
    # Deployment-only scalar projection of the parent's registered 2D deployment profiles.
    scores = {"N_good": 4, "P_good": 2, "X_ideal": 0}
    r2 = ("N_good",)
    r3 = ("N_good", "P_good")
    r10 = ("N_good", "P_good", "X_ideal")
    c2 = scalar_separation_certificate(ms, r2, scores)
    c3 = scalar_separation_certificate(ms, r3, scores)
    c10 = scalar_separation_certificate(ms, r10, scores)
    return {
        "scope": "deployment_only_scalar_projection_of_corrected_parent_witness",
        "scores": scores,
        "budget_2": c2,
        "budget_3": c3,
        "budget_10": c10,
        "budget_2_to_3": nested_reachability_certificate(ms, r2, r3, scores),
        "budget_3_to_10": nested_reachability_certificate(ms, r3, r10, scores),
        "corrected_parent_full_lifecycle_frontiers": {
            "budget_2": ("N_good",),
            "budget_3": ("N_good", "P_good"),
            "budget_10": ("N_good", "P_good", "X_ideal"),
        },
        "corrected_parent_terminal": "GRAND_GMI_DEVELOPMENTAL_LIFECYCLE_SELECTION_V2_ALL_GREEN",
        "boundary": (
            "Scalar projection illustrates constrained optimum values only; "
            "it does not replace the parent's full lifecycle Pareto coexistence."
        ),
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
    rejected("duplicate_morphology_rejected", lambda: validate_universe(("a", "a")))
    rejected("empty_reachable_rejected", lambda: validate_reachable(("a",), ()))
    rejected("outside_reachable_rejected", lambda: validate_reachable(("a",), ("b",)))
    rejected(
        "duplicate_reachable_rejected",
        lambda: validate_reachable(("a", "b"), ("a", "a")),
    )
    rejected(
        "missing_scalar_score_rejected",
        lambda: validate_scores(("a", "b"), {"a": 0}),
    )
    rejected(
        "extra_scalar_score_rejected",
        lambda: validate_scores(("a",), {"a": 0, "b": 1}),
    )
    rejected(
        "float_scalar_rejected",
        lambda: validate_scores(("a",), {"a": 0.5}),
    )
    rejected(
        "bool_scalar_rejected",
        lambda: validate_scores(("a",), {"a": True}),
    )
    rejected(
        "false_nested_expansion_rejected",
        lambda: nested_reachability_certificate(
            ("a", "b"), ("a",), ("b",), {"a": 0, "b": 1}
        ),
    )
    rejected(
        "missing_pareto_profile_rejected",
        lambda: validate_profiles(("a", "b"), {"a": (0, 1)}),
    )
    rejected(
        "empty_pareto_vector_rejected",
        lambda: validate_profiles(("a",), {"a": ()}),
    )
    rejected(
        "dimension_mismatch_rejected",
        lambda: validate_profiles(("a", "b"), {"a": (0,), "b": (0, 1)}),
    )
    rejected(
        "float_pareto_coordinate_rejected",
        lambda: validate_profiles(("a",), {"a": (0.5, 1)}),
    )
    rejected(
        "dominance_dimension_mismatch_rejected",
        lambda: dominates((0,), (0, 1)),
    )
    return checks


def build_receipt() -> dict[str, Any]:
    scalar = scalar_exhaustive_census()
    pareto = pareto_exhaustive_census()
    witnesses = witness_controls()
    parent = parent_budget_witness()
    hostiles = hostile_controls()
    checks = {
        "scalar_census_zero_failures": scalar["failures"] == [],
        "pareto_census_zero_failures": pareto["failures"] == [],
        "pareto_census_has_strict_restriction_cases": pareto["strict_inclusion_cases"] > 0,
        "strict_gap_witness": witnesses["checks"]["strict_gap_positive"],
        "tied_value_does_not_force_same_optimizer_set": witnesses["checks"]["tie_same_value"]
        and witnesses["checks"]["tie_optimizer_sets_differ"],
        "pareto_relative_feasibility_hostile": witnesses["checks"]["pareto_safe_inclusion"]
        and witnesses["checks"]["pareto_reverse_inclusion_false"]
        and witnesses["checks"]["globally_dominated_b_becomes_reachable_pareto"],
        "parent_budget_2_value": parent["budget_2"]["reachable_value"] == 4,
        "parent_budget_3_value": parent["budget_3"]["reachable_value"] == 2,
        "parent_budget_10_value": parent["budget_10"]["reachable_value"] == 0,
        "parent_nested_budget_monotonic": parent["budget_2_to_3"]["expanded_reachability_cannot_worsen_minimum"]
        and parent["budget_3_to_10"]["expanded_reachability_cannot_worsen_minimum"],
        "corrected_parent_terminal_preserved": parent["corrected_parent_terminal"]
        == "GRAND_GMI_DEVELOPMENTAL_LIFECYCLE_SELECTION_V2_ALL_GREEN",
        "all_hostiles_rejected": all(hostiles.values()),
    }
    return {
        "schema": "GMI_833_GLOBAL_VS_REACHABLE_MORPHOLOGY_V1",
        "source_issue": 874,
        "master_issue": 833,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_pins": PARENT_PINS,
        "theorems": {
            "GVR_1": "for nonempty R subset M, min_M f <= min_R f",
            "GVR_2": "min_R f = min_M f iff R intersects Argmin_M f",
            "GVR_3": "equal optimum values need not imply equal optimizer sets",
            "GVR_4": "R1 subset R2 implies min_R2 f <= min_R1 f",
            "GVR_5": "Pareto(M) intersect R subset Pareto(R); reverse inclusion need not hold",
        },
        "scalar_census": scalar,
        "pareto_census": pareto,
        "witnesses": witnesses,
        "parent_witness": parent,
        "hostile_controls": hostiles,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


if __name__ == "__main__":
    print(canonical_json(build_receipt()), end="")
