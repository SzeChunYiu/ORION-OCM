#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
from typing import Any, Mapping, Sequence

SOURCE_MAIN = "497977a071f33a824628332caf1ccc44e077f924"
FREEZE_COMMIT = "1a0b8a7874bfc8de9c08f025e6340f5dc33df6ba"
CLAIM_CEILING = "GMI_FINITE_UPDATE_LAW_NO_FREE_LUNCH_BOUNDARY_AT_UNIFORM_COMPLETION_SCOPE"
FORBIDDEN_PROMOTIONS = [
    "ALL_ALGORITHMS_EQUAL_IN_REAL_WORLD",
    "UNIVERSAL_UNIFORM_ECOLOGY",
    "NO_ALGORITHM_CAN_OUTPERFORM_ANOTHER",
    "NO_USEFUL_LEARNING_LAW_SELECTION",
    "ALL_LEARNING_LAWS_COVERED",
    "PROSPECTIVE_SELECTOR_BUILT",
    "P3_RECOVERY_COMPLETE",
    "COMPLETE_GMI",
]


def require(cond: bool, message: str) -> None:
    if not cond:
        raise ValueError(message)


def exact_fraction(x: Any) -> Fraction:
    require(not isinstance(x, float), "floats are forbidden")
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x, 1)
    if isinstance(x, str):
        return Fraction(x)
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


def validate_problem(n_contexts: int, k: int, observed: Mapping[int, int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    require(isinstance(n_contexts, int) and n_contexts >= 1, "n_contexts must be positive int")
    require(isinstance(k, int) and k >= 2, "k must be integer >= 2")
    xs = tuple(range(n_contexts))
    for x, y in observed.items():
        require(isinstance(x, int) and x in xs, "observed context outside X")
        require(isinstance(y, int) and 0 <= y < k, "observed label outside Y")
    obs = tuple(sorted(observed))
    held = tuple(x for x in xs if x not in observed)
    return obs, held


def enumerate_completions(n_contexts: int, k: int, observed: Mapping[int, int]) -> tuple[tuple[int, ...], ...]:
    _, held = validate_problem(n_contexts, k, observed)
    if not held:
        return ()
    out = []
    for ys in product(range(k), repeat=len(held)):
        target = [None] * n_contexts
        for x, y in observed.items():
            target[x] = y
        for x, y in zip(held, ys):
            target[x] = y
        out.append(tuple(target))
    return tuple(out)


def validate_law(
    n_contexts: int,
    k: int,
    observed: Mapping[int, int],
    law: Mapping[int, Sequence[Any]],
) -> dict[int, tuple[Fraction, ...]]:
    _, held = validate_problem(n_contexts, k, observed)
    require(bool(held), "NOT_APPLICABLE_NO_HELDOUT")
    require(set(law) == set(held), "law must define exactly every held-out context")
    out: dict[int, tuple[Fraction, ...]] = {}
    for x in held:
        probs = tuple(exact_fraction(v) for v in law[x])
        require(len(probs) == k, "predictive vector length must equal k")
        require(all(p >= 0 for p in probs), "negative predictive probability")
        require(sum(probs, Fraction(0)) == 1, "predictive probabilities must normalize")
        out[x] = probs
    return out


def deterministic_law(held: Sequence[int], k: int, labels: Sequence[int]) -> dict[int, tuple[Fraction, ...]]:
    require(len(held) == len(labels), "deterministic labels length mismatch")
    out = {}
    for x, label in zip(held, labels):
        require(0 <= label < k, "deterministic label outside Y")
        out[x] = tuple(Fraction(int(y == label), 1) for y in range(k))
    return out


def uniform_ecology(completions: Sequence[tuple[int, ...]]) -> dict[tuple[int, ...], Fraction]:
    require(bool(completions), "NOT_APPLICABLE_NO_HELDOUT")
    w = Fraction(1, len(completions))
    return {f: w for f in completions}


def validate_ecology(
    completions: Sequence[tuple[int, ...]],
    weights: Mapping[tuple[int, ...], Any],
    declared_uniform: bool = False,
) -> dict[tuple[int, ...], Fraction]:
    require(bool(completions), "NOT_APPLICABLE_NO_HELDOUT")
    support = set(completions)
    require(set(weights) == support, "ecology support must equal registered completion support")
    out = {f: exact_fraction(w) for f, w in weights.items()}
    require(all(w >= 0 for w in out.values()), "negative ecology weight")
    require(sum(out.values(), Fraction(0)) == 1, "ecology weights must normalize")
    if declared_uniform:
        expected = Fraction(1, len(completions))
        require(all(w == expected for w in out.values()), "declared UNIFORM ecology has nonuniform weights")
    return out


def expected_accuracy(
    n_contexts: int,
    k: int,
    observed: Mapping[int, int],
    law: Mapping[int, Sequence[Any]],
    ecology_weights: Mapping[tuple[int, ...], Any],
    *,
    declared_uniform: bool = False,
) -> Fraction:
    _, held = validate_problem(n_contexts, k, observed)
    require(bool(held), "NOT_APPLICABLE_NO_HELDOUT")
    validated_law = validate_law(n_contexts, k, observed, law)
    completions = enumerate_completions(n_contexts, k, observed)
    weights = validate_ecology(completions, ecology_weights, declared_uniform=declared_uniform)
    total = Fraction(0)
    for f, w in weights.items():
        per = sum((validated_law[x][f[x]] for x in held), Fraction(0)) / len(held)
        total += w * per
    return total


def uniform_nfl_certificate(
    n_contexts: int,
    k: int,
    observed: Mapping[int, int],
    law: Mapping[int, Sequence[Any]],
) -> dict[str, Any]:
    _, held = validate_problem(n_contexts, k, observed)
    if not held:
        return {
            "terminal": "NOT_APPLICABLE_NO_HELDOUT",
            "heldout_count": 0,
        }
    completions = enumerate_completions(n_contexts, k, observed)
    acc = expected_accuracy(
        n_contexts, k, observed, law, uniform_ecology(completions), declared_uniform=True
    )
    expected = Fraction(1, k)
    return {
        "terminal": "UNIFORM_COMPLETION_NFL_EQUALITY" if acc == expected else "NFL_EQUALITY_FAILURE",
        "completion_count": len(completions),
        "heldout_count": len(held),
        "k": k,
        "accuracy": acc,
        "error": 1 - acc,
        "expected_accuracy": expected,
        "equality": acc == expected,
    }


def deterministic_exhaustive_census() -> dict[str, Any]:
    configs = (
        (1, 0, 1, 2),
        (2, 1, 1, 2),
        (3, 1, 2, 2),
        (5, 2, 3, 2),
        (2, 1, 1, 3),
        (4, 2, 2, 3),
    )
    cases = 0
    failures = []
    completion_total = 0
    for n, nobs, expected_held, k in configs:
        obs_x = tuple(range(nobs))
        for obs_labels in product(range(k), repeat=nobs):
            observed = dict(zip(obs_x, obs_labels))
            _, held = validate_problem(n, k, observed)
            require(len(held) == expected_held, "internal census heldout mismatch")
            completions = enumerate_completions(n, k, observed)
            completion_total += len(completions)
            for labels in product(range(k), repeat=len(held)):
                law = deterministic_law(held, k, labels)
                cert = uniform_nfl_certificate(n, k, observed, law)
                cases += 1
                if cert["accuracy"] != Fraction(1, k):
                    failures.append({
                        "config": (n, nobs, expected_held, k),
                        "observed": tuple(sorted(observed.items())),
                        "labels": labels,
                        "accuracy": cert["accuracy"],
                    })
    return {
        "configs": configs,
        "law_history_cases": cases,
        "completion_sets_total": completion_total,
        "failures": failures,
    }


def randomized_controls() -> dict[str, Any]:
    controls = []
    specs = [
        (2, {0: 0}, {1: (Fraction(1, 3), Fraction(2, 3))}),
        (2, {0: 1}, {1: (Fraction(5, 8), Fraction(3, 8))}),
        (3, {0: 0}, {1: (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7))}),
        (3, {0: 2}, {1: (Fraction(1, 5), Fraction(3, 10), Fraction(1, 2))}),
        (3, {}, {
            0: (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7)),
            1: (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
        }),
    ]
    for k, observed, law in specs:
        n = max(set(observed) | set(law)) + 1
        cert = uniform_nfl_certificate(n, k, observed, law)
        controls.append(cert)
    return {
        "cases": len(controls),
        "all_equal": all(c["equality"] for c in controls),
        "controls": controls,
    }


def preference_reversal() -> dict[str, Any]:
    n, k, observed = 1, 2, {}
    completions = enumerate_completions(n, k, observed)
    held = (0,)
    a0 = deterministic_law(held, k, (0,))
    a1 = deterministic_law(held, k, (1,))
    f0 = tuple([0])
    f1 = tuple([1])
    p0 = {f0: Fraction(3, 4), f1: Fraction(1, 4)}
    p1 = {f0: Fraction(1, 4), f1: Fraction(3, 4)}
    r = {
        "P0": {
            "A0": expected_accuracy(n, k, observed, a0, p0),
            "A1": expected_accuracy(n, k, observed, a1, p0),
        },
        "P1": {
            "A0": expected_accuracy(n, k, observed, a0, p1),
            "A1": expected_accuracy(n, k, observed, a1, p1),
        },
        "completion_count": len(completions),
    }
    r["P0_prefers_A0"] = r["P0"]["A0"] > r["P0"]["A1"]
    r["P1_prefers_A1"] = r["P1"]["A1"] > r["P1"]["A0"]
    r["terminal"] = "NONUNIFORM_ECOLOGY_PREFERENCE" if r["P0_prefers_A0"] and r["P1_prefers_A1"] else "PREFERENCE_REVERSAL_FAILURE"
    return r


def pairwise_ecology_reversal(
    n_contexts: int,
    k: int,
    observed: Mapping[int, int],
    law_a: Mapping[int, Sequence[Any]],
    law_b: Mapping[int, Sequence[Any]],
) -> dict[str, Any]:
    """Construct point ecologies preferring each of two distinct update laws."""
    _, held = validate_problem(n_contexts, k, observed)
    require(bool(held), "NOT_APPLICABLE_NO_HELDOUT")
    a = validate_law(n_contexts, k, observed, law_a)
    b = validate_law(n_contexts, k, observed, law_b)
    require(any(a[x] != b[x] for x in held), "laws must be predictively distinct")

    target_a = [None] * n_contexts
    target_b = [None] * n_contexts
    for x, y in observed.items():
        target_a[x] = y
        target_b[x] = y

    for x in held:
        diffs = tuple(a[x][y] - b[x][y] for y in range(k))
        y_for_a = max(range(k), key=lambda y: (diffs[y], -y))
        y_for_b = min(range(k), key=lambda y: (diffs[y], y))
        target_a[x] = y_for_a
        target_b[x] = y_for_b

    fa = tuple(target_a)
    fb = tuple(target_b)
    pa = {f: Fraction(int(f == fa), 1) for f in enumerate_completions(n_contexts, k, observed)}
    pb = {f: Fraction(int(f == fb), 1) for f in enumerate_completions(n_contexts, k, observed)}

    aa = expected_accuracy(n_contexts, k, observed, a, pa)
    ba = expected_accuracy(n_contexts, k, observed, b, pa)
    ab = expected_accuracy(n_contexts, k, observed, a, pb)
    bb = expected_accuracy(n_contexts, k, observed, b, pb)
    require(aa > ba, "constructed ecology failed to prefer law A")
    require(bb > ab, "constructed ecology failed to prefer law B")
    return {
        "terminal": "PAIRWISE_ECOLOGY_PREFERENCE_REVERSAL",
        "ecology_for_A_target": fa,
        "ecology_for_B_target": fb,
        "A_under_PA": aa,
        "B_under_PA": ba,
        "A_under_PB": ab,
        "B_under_PB": bb,
        "A_preferred_under_PA": aa > ba,
        "B_preferred_under_PB": bb > ab,
    }


def hostile_controls() -> dict[str, Any]:
    no_held = uniform_nfl_certificate(1, 2, {0: 0}, {})
    completions = enumerate_completions(1, 2, {})
    bad = {}
    try:
        validate_law(1, 2, {}, {0: (Fraction(2, 3), Fraction(2, 3))})
        bad["unnormalized_law_rejected"] = False
    except ValueError:
        bad["unnormalized_law_rejected"] = True
    try:
        validate_law(1, 2, {}, {0: (Fraction(-1, 3), Fraction(4, 3))})
        bad["negative_law_rejected"] = False
    except ValueError:
        bad["negative_law_rejected"] = True
    try:
        validate_law(1, 2, {}, {0: (0.5, 0.5)})
        bad["float_law_rejected"] = False
    except ValueError:
        bad["float_law_rejected"] = True
    try:
        validate_ecology(completions, {completions[0]: Fraction(3, 4), completions[1]: Fraction(1, 4)}, declared_uniform=True)
        bad["false_uniform_rejected"] = False
    except ValueError:
        bad["false_uniform_rejected"] = True
    try:
        validate_ecology(completions, {completions[0]: Fraction(1)}, declared_uniform=True)
        bad["incomplete_support_rejected"] = False
    except ValueError:
        bad["incomplete_support_rejected"] = True
    try:
        validate_ecology(completions, {completions[0]: Fraction(1, 3), completions[1]: Fraction(1, 3)})
        bad["unnormalized_ecology_rejected"] = False
    except ValueError:
        bad["unnormalized_ecology_rejected"] = True
    try:
        validate_ecology(completions, {completions[0]: Fraction(-1, 4), completions[1]: Fraction(5, 4)})
        bad["negative_ecology_rejected"] = False
    except ValueError:
        bad["negative_ecology_rejected"] = True
    try:
        validate_problem(1, 1, {})
        bad["k_lt_2_rejected"] = False
    except ValueError:
        bad["k_lt_2_rejected"] = True
    try:
        validate_problem(1, 2, {0: 2})
        bad["bad_observed_label_rejected"] = False
    except ValueError:
        bad["bad_observed_label_rejected"] = True
    bad["no_heldout_terminal"] = no_held["terminal"]
    return bad


def build_receipt() -> dict[str, Any]:
    census = deterministic_exhaustive_census()
    randoms = randomized_controls()
    reversal = preference_reversal()
    general_reversal = pairwise_ecology_reversal(
        2,
        3,
        {},
        {
            0: (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7)),
            1: (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
        },
        {
            0: (Fraction(4, 7), Fraction(2, 7), Fraction(1, 7)),
            1: (Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)),
        },
    )
    hostiles = hostile_controls()
    checks = {
        "analytic_expected_binary": uniform_nfl_certificate(2, 2, {0: 0}, {1: (Fraction(1), Fraction(0))})["accuracy"] == Fraction(1, 2),
        "analytic_expected_ternary_randomized": uniform_nfl_certificate(2, 3, {0: 1}, {1: (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7))})["accuracy"] == Fraction(1, 3),
        "deterministic_exhaustive_no_failures": not census["failures"],
        "deterministic_exhaustive_nontrivial": census["law_history_cases"] >= 100,
        "randomized_controls_equal": randoms["all_equal"],
        "nonuniform_preference_reverses": reversal["terminal"] == "NONUNIFORM_ECOLOGY_PREFERENCE",
        "general_distinct_law_reversal_constructed": general_reversal["terminal"] == "PAIRWISE_ECOLOGY_PREFERENCE_REVERSAL",
        "no_heldout_not_applicable": hostiles["no_heldout_terminal"] == "NOT_APPLICABLE_NO_HELDOUT",
        "unnormalized_law_rejected": hostiles["unnormalized_law_rejected"],
        "negative_law_rejected": hostiles["negative_law_rejected"],
        "float_law_rejected": hostiles["float_law_rejected"],
        "false_uniform_rejected": hostiles["false_uniform_rejected"],
        "incomplete_uniform_support_rejected": hostiles["incomplete_support_rejected"],
        "unnormalized_ecology_rejected": hostiles["unnormalized_ecology_rejected"],
        "negative_ecology_rejected": hostiles["negative_ecology_rejected"],
        "k_lt_2_rejected": hostiles["k_lt_2_rejected"],
        "bad_observed_label_rejected": hostiles["bad_observed_label_rejected"],
    }
    return {
        "schema": "GMI833FiniteUpdateLawNFLResultV1",
        "issue": 870,
        "parent_issue": 833,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "analytic_theorem": {
            "terminal": "UNIFORM_COMPLETION_NFL_EQUALITY",
            "scope": "finite X; finite Y with k>=2; nonempty heldout; uniform completions consistent with fixed history; normalized possibly-randomized update law",
            "per_context_expected_accuracy": "1/k",
            "mean_error": "1-1/k",
            "randomization_escape": False,
        },
        "deterministic_census": census,
        "randomized_controls": randoms,
        "preference_reversal": reversal,
        "general_pairwise_reversal": general_reversal,
        "hostiles": hostiles,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


if __name__ == "__main__":
    print(canonical_json(build_receipt()), end="")
