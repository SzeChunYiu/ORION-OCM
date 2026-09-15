#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import json
from typing import Any, Mapping, Sequence

SOURCE_MAIN = "115145b60bae9d066d583a4c5d877ee59eb527ab"
FREEZE_COMMIT = "d62a842c7b07007c5f4402895c04a0fce4f8b476"
CLAIM_CEILING = "GMI_DERIVATION_ROBUSTNESS_CONTROL_REQUIREMENTS_FORMALIZED_AT_REGISTERED_FINITE_SCOPE"
FORBIDDEN_PROMOTIONS = [
    "ALL_GMI_RESULTS_ROBUST",
    "ALL_GRAMMARS_NEUTRAL",
    "ENCODING_INVARIANCE_UNIVERSAL",
    "SEARCH_ALGORITHM_INDEPENDENCE_UNIVERSAL",
    "SCALARIZATION_INDEPENDENCE_UNIVERSAL",
    "ALL_HISTORICAL_RESULTS_REPLICATED",
    "P3_RECOVERY_COMPLETE",
    "COMPLETE_GMI",
]
PARENT_PINS = [
    {
        "path": "research/gmi-833-foundation-v1/RESULT_V1.json",
        "blob": "c0c574c4ec6e237d5fdafa694eac131399625a70",
        "claim_ceiling": "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE",
    },
    {
        "path": "research/gmi-833-no-smuggling-audit-v1/RESULT_V1.json",
        "blob": "0d8b8c1dcd05512e2ec54db6bae872953daed87f",
        "claim_ceiling": "GMI_NO_SMUGGLING_AUDIT_TOOLING_VALIDATED_AT_REGISTERED_FINITE_FIXTURE_SCOPE",
    },
]


def frac(x: Any) -> Fraction:
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x, 1)
    if isinstance(x, str):
        return Fraction(x)
    raise TypeError(f"unsupported exact rational {x!r}")


def canon(x: Any) -> Any:
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x, tuple):
        return [canon(v) for v in x]
    if isinstance(x, list):
        return [canon(v) for v in x]
    if isinstance(x, (set, frozenset)):
        return [canon(v) for v in sorted(x, key=repr)]
    if isinstance(x, dict):
        return {str(k): canon(v) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    return x


def canonical_json(x: Any) -> str:
    return json.dumps(canon(x), sort_keys=True, indent=2) + "\n"


@dataclass(frozen=True)
class Candidate:
    cid: str
    semantic_class: str
    has_target_mechanism: bool
    background_signature: tuple[str, ...]


def grammar_twin_audit(
    positive: Sequence[Candidate] | None,
    negative: Sequence[Candidate] | None,
    positive_context: Mapping[str, Any] | None,
    negative_context: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if positive is None or negative is None or positive_context is None or negative_context is None:
        return {"terminal": "CANNOT_AUDIT_GRAMMAR_TWIN", "matched": False}
    if len({c.cid for c in positive}) != len(positive) or len({c.cid for c in negative}) != len(negative):
        return {"terminal": "GRAMMAR_TWIN_UNMATCHED", "matched": False, "reason": "DUPLICATE_CANDIDATE_ID"}
    target_positive = [c for c in positive if c.has_target_mechanism]
    if not target_positive:
        return {"terminal": "GRAMMAR_TWIN_UNMATCHED", "matched": False, "reason": "NO_TARGET_MECHANISM_IN_POSITIVE"}
    if any(c.has_target_mechanism for c in negative):
        return {"terminal": "GRAMMAR_TWIN_UNMATCHED", "matched": False, "reason": "TARGET_MECHANISM_REMAINS_IN_NEGATIVE"}
    pos_bg = Counter(c.background_signature for c in positive if not c.has_target_mechanism)
    neg_bg = Counter(c.background_signature for c in negative)
    context_equal = dict(positive_context) == dict(negative_context)
    matched = pos_bg == neg_bg and context_equal
    return {
        "terminal": "GRAMMAR_TWIN_MATCHED" if matched else "GRAMMAR_TWIN_UNMATCHED",
        "matched": matched,
        "target_candidates_removed": len(target_positive),
        "mechanism_free_positive": sum(pos_bg.values()),
        "mechanism_free_negative": sum(neg_bg.values()),
        "background_multiset_equal": pos_bg == neg_bg,
        "context_equal": context_equal,
        "positive_total": len(positive),
        "negative_total": len(negative),
    }


def encoding_audit(
    enc1: Mapping[str, str] | None,
    enc2: Mapping[str, str] | None,
    phi: Mapping[str, str] | None,
    result1: str | None,
    result2: str | None,
) -> dict[str, Any]:
    if enc1 is None or enc2 is None or phi is None or result1 is None or result2 is None:
        return {"terminal": "CANNOT_AUDIT_ENCODING"}
    if set(phi) != set(enc1) or set(phi.values()) != set(enc2) or len(set(phi.values())) != len(phi):
        return {"terminal": "CANNOT_AUDIT_ENCODING", "reason": "REMINT_NOT_BIJECTIVE"}
    if any(enc1[k] != enc2[phi[k]] for k in enc1):
        return {"terminal": "CANNOT_AUDIT_ENCODING", "reason": "REMINT_NOT_SEMANTICS_PRESERVING"}
    if result1 not in enc1 or result2 not in enc2:
        return {"terminal": "CANNOT_AUDIT_ENCODING", "reason": "RESULT_OUTSIDE_ENCODING"}
    sem1 = enc1[result1]
    sem2 = enc2[result2]
    same = sem1 == sem2
    return {
        "terminal": "ENCODING_INVARIANT_AT_REGISTERED_REMINTS" if same else "ENCODING_SENSITIVE",
        "canonical_result_1": sem1,
        "canonical_result_2": sem2,
        "semantics_preserving_bijection": True,
    }


def lexicographic_surface_choice(encoding: Mapping[str, str]) -> str:
    if not encoding:
        raise ValueError("encoding must be nonempty")
    return min(encoding)


def exhaustive_search(scores: Mapping[str, Fraction]) -> str:
    if not scores:
        raise ValueError("scores must be nonempty")
    best = min(scores.values())
    winners = sorted(k for k, v in scores.items() if v == best)
    if len(winners) != 1:
        raise ValueError("positive control requires unique optimum")
    return winners[0]


def branch_and_bound_search(
    scores: Mapping[str, Fraction],
    lower_bounds: Mapping[str, Fraction],
    order: Sequence[str],
) -> tuple[str, int, int]:
    if set(scores) != set(lower_bounds) or set(order) != set(scores) or len(order) != len(scores):
        raise ValueError("branch-and-bound domains must match")
    for k in scores:
        if lower_bounds[k] > scores[k]:
            raise ValueError("lower bound exceeds exact score")
    best_id: str | None = None
    best_score: Fraction | None = None
    evaluated = 0
    pruned = 0
    for k in order:
        lb = lower_bounds[k]
        if best_score is not None and lb >= best_score:
            pruned += 1
            continue
        evaluated += 1
        s = scores[k]
        if best_score is None or s < best_score:
            best_id, best_score = k, s
    if best_id is None:
        raise RuntimeError("no candidate evaluated")
    return best_id, evaluated, pruned


def early_stop_search(order: Sequence[str], budget: int) -> str:
    if budget < 1 or not order:
        raise ValueError("positive budget and nonempty order required")
    return order[0]


def search_audit(runs: Sequence[Mapping[str, Any]] | None) -> dict[str, Any]:
    if runs is None or len(runs) < 2:
        return {"terminal": "CANNOT_AUDIT_SEARCH"}
    strategy_ids = [str(r.get("strategy_id", "")) for r in runs]
    signatures = [tuple(r.get("strategy_signature", ())) for r in runs]
    if any(not s for s in strategy_ids) or len(set(strategy_ids)) != len(strategy_ids):
        return {"terminal": "CANNOT_AUDIT_SEARCH", "reason": "INVALID_SEARCHER_IDS"}
    if any(not sig for sig in signatures) or len(set(signatures)) < 2:
        return {"terminal": "CANNOT_AUDIT_SEARCH", "reason": "SEARCHERS_NOT_MATERIALLY_DISTINCT"}
    objective_ids = {r.get("objective_id") for r in runs}
    budgets = {r.get("declared_budget") for r in runs}
    if len(objective_ids) != 1 or None in objective_ids:
        return {"terminal": "CANNOT_AUDIT_SEARCH", "reason": "OBJECTIVE_MISMATCH"}
    if len(budgets) != 1 or None in budgets:
        return {"terminal": "CANNOT_COMPARE_SEARCH_BUDGETS"}
    winners = [r.get("canonical_winner") for r in runs]
    if any(w is None for w in winners):
        return {"terminal": "CANNOT_AUDIT_SEARCH", "reason": "MISSING_CANONICAL_WINNER"}
    invariant = len(set(winners)) == 1
    return {
        "terminal": "SEARCH_INVARIANT_AT_REGISTERED_ALGORITHMS" if invariant else "SEARCH_ALGORITHM_SENSITIVE",
        "strategies": strategy_ids,
        "strategy_signatures": signatures,
        "declared_budget": next(iter(budgets)),
        "winners": winners,
    }


def dominates(a: Sequence[Fraction], b: Sequence[Fraction]) -> bool:
    if len(a) != len(b):
        raise ValueError("dimension mismatch")
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def pareto_front(vectors: Mapping[str, Sequence[Fraction]]) -> tuple[str, ...]:
    names = sorted(vectors)
    out = []
    for name in names:
        v = vectors[name]
        if not any(other != name and dominates(vectors[other], v) for other in names):
            out.append(name)
    return tuple(out)


def scalarization_audit(
    vectors: Mapping[str, Sequence[Fraction]] | None,
    weights: Sequence[Sequence[Fraction]] | None,
    price_conditional: bool = False,
) -> dict[str, Any]:
    if vectors is None or weights is None or len(weights) < 2 or not vectors:
        return {"terminal": "CANNOT_AUDIT_SCALARIZATION"}
    dims = {len(v) for v in vectors.values()}
    if len(dims) != 1:
        return {"terminal": "CANNOT_AUDIT_SCALARIZATION", "reason": "VECTOR_DIMENSION_MISMATCH"}
    d = next(iter(dims))
    if d == 0 or any(frac(x) < 0 for v in vectors.values() for x in v):
        return {"terminal": "CANNOT_AUDIT_SCALARIZATION", "reason": "INVALID_RESOURCE_VECTOR"}
    exact_vectors = {k: tuple(frac(x) for x in v) for k, v in vectors.items()}
    exact_weights: list[tuple[Fraction, ...]] = []
    for w in weights:
        ww = tuple(frac(x) for x in w)
        if len(ww) != d or any(x <= 0 for x in ww):
            return {"terminal": "CANNOT_AUDIT_SCALARIZATION", "reason": "WEIGHTS_MUST_BE_STRICTLY_POSITIVE"}
        exact_weights.append(ww)
    if len(set(exact_weights)) < 2:
        return {"terminal": "CANNOT_AUDIT_SCALARIZATION", "reason": "SCALARIZATIONS_NOT_DISTINCT"}
    frontier = pareto_front(exact_vectors)
    winners: list[tuple[str, ...]] = []
    for w in exact_weights:
        scores = {k: sum((wi * xi for wi, xi in zip(w, v)), Fraction(0)) for k, v in exact_vectors.items()}
        best = min(scores.values())
        win = tuple(sorted(k for k, s in scores.items() if s == best))
        if any(k not in frontier for k in win):
            raise AssertionError("positive scalarization selected dominated candidate")
        winners.append(win)
    sensitive = len(set(winners)) > 1
    terminal = "PRICE_SENSITIVE" if sensitive else "SCALARIZATION_INVARIANT_AT_REGISTERED_WEIGHTS"
    return {
        "terminal": terminal,
        "pareto_front": frontier,
        "weights": tuple(exact_weights),
        "winners": tuple(winners),
        "price_conditional": bool(price_conditional),
    }


def audit_record(record: Mapping[str, Any]) -> dict[str, Any]:
    grammar = grammar_twin_audit(
        record.get("grammar_positive"),
        record.get("grammar_negative"),
        record.get("grammar_positive_context"),
        record.get("grammar_negative_context"),
    )
    encoding = encoding_audit(
        record.get("encoding_1"), record.get("encoding_2"), record.get("remint_map"),
        record.get("encoding_result_1"), record.get("encoding_result_2"),
    )
    search = search_audit(record.get("search_runs"))
    scalar = scalarization_audit(
        record.get("resource_vectors"), record.get("scalar_weights"), bool(record.get("price_conditional", False))
    )
    subs = {"grammar": grammar, "encoding": encoding, "search": search, "scalarization": scalar}
    cannot = [name for name, res in subs.items() if str(res["terminal"]).startswith("CANNOT_") or res["terminal"] == "GRAMMAR_TWIN_UNMATCHED"]
    requirements = not cannot
    sensitive_terms = {"ENCODING_SENSITIVE", "SEARCH_ALGORITHM_SENSITIVE", "PRICE_SENSITIVE"}
    sensitive = requirements and any(res["terminal"] in sensitive_terms for res in subs.values())
    if not requirements:
        global_terminal = "CANNOT_AUDIT_REQUIRED_CONTROLS"
    elif sensitive:
        global_terminal = "SENSITIVE_AT_REGISTERED_CONTROLS"
    else:
        global_terminal = "ROBUST_AT_REGISTERED_CONTROLS"
    return {
        "terminal": global_terminal,
        "control_requirements_terminal": "CONTROL_REQUIREMENTS_SATISFIED" if requirements else "CONTROL_REQUIREMENTS_INCOMPLETE",
        "requirements_satisfied": requirements,
        "sensitive": sensitive,
        "subaudits": subs,
    }


def positive_fixture() -> dict[str, Any]:
    positive = [
        Candidate("t0", "target-a", True, ("depth1", "arith")),
        Candidate("t1", "target-b", True, ("depth2", "arith")),
        Candidate("n0", "plain-0", False, ("depth1", "arith")),
        Candidate("n1", "plain-1", False, ("depth1", "logic")),
        Candidate("n2", "plain-2", False, ("depth2", "arith")),
        Candidate("n3", "plain-3", False, ("depth2", "logic")),
    ]
    negative = [c for c in positive if not c.has_target_mechanism]
    context = {"ecology": "E0", "evaluator": "V0", "budget": 6, "stop": "exhaustive"}
    enc1 = {"alpha": "A", "beta": "B", "gamma": "C"}
    enc2 = {"q7": "A", "q2": "B", "q9": "C"}
    phi = {"alpha": "q7", "beta": "q2", "gamma": "q9"}
    scores = {"A": Fraction(3), "B": Fraction(1), "C": Fraction(2)}
    bnb_winner, evaluated, pruned = branch_and_bound_search(scores, {"A": Fraction(0), "B": Fraction(1), "C": Fraction(2)}, ["A", "B", "C"])
    search_runs = [
        {"strategy_id": "exhaustive", "strategy_signature": ("enumerate_all", "no_pruning"), "objective_id": "loss", "declared_budget": 3, "canonical_winner": exhaustive_search(scores)},
        {"strategy_id": "branch_bound", "strategy_signature": ("admissible_lower_bound", "prune"), "objective_id": "loss", "declared_budget": 3, "canonical_winner": bnb_winner, "evaluated": evaluated, "pruned": pruned},
    ]
    return {
        "grammar_positive": positive,
        "grammar_negative": negative,
        "grammar_positive_context": context,
        "grammar_negative_context": dict(context),
        "encoding_1": enc1,
        "encoding_2": enc2,
        "remint_map": phi,
        "encoding_result_1": "beta",
        "encoding_result_2": "q2",
        "search_runs": search_runs,
        "resource_vectors": {"efficient": (Fraction(1), Fraction(1)), "dominated": (Fraction(2), Fraction(3))},
        "scalar_weights": [(Fraction(1), Fraction(2)), (Fraction(3), Fraction(1))],
        "price_conditional": False,
    }


def sensitive_fixture() -> dict[str, Any]:
    rec = positive_fixture()
    enc1 = {"a": "A", "z": "B"}
    enc2 = {"z": "A", "a": "B"}
    rec["encoding_1"] = enc1
    rec["encoding_2"] = enc2
    rec["remint_map"] = {"a": "z", "z": "a"}
    rec["encoding_result_1"] = lexicographic_surface_choice(enc1)
    rec["encoding_result_2"] = lexicographic_surface_choice(enc2)
    rec["search_runs"] = [
        {"strategy_id": "forward_early", "strategy_signature": ("early_stop", "forward_order"), "objective_id": "tie", "declared_budget": 1, "canonical_winner": early_stop_search(["A", "B"], 1)},
        {"strategy_id": "reverse_early", "strategy_signature": ("early_stop", "reverse_order"), "objective_id": "tie", "declared_budget": 1, "canonical_winner": early_stop_search(["B", "A"], 1)},
    ]
    rec["resource_vectors"] = {"a": (Fraction(1), Fraction(4)), "b": (Fraction(4), Fraction(1))}
    rec["scalar_weights"] = [(Fraction(4), Fraction(1)), (Fraction(1), Fraction(4))]
    rec["price_conditional"] = False
    return rec


def unmatched_grammar_fixture() -> tuple[list[Candidate], list[Candidate], dict[str, Any]]:
    rec = positive_fixture()
    positive = list(rec["grammar_positive"])
    negative = list(rec["grammar_negative"])[1:]
    return positive, negative, dict(rec["grammar_positive_context"])


def missing_control_census() -> dict[str, Any]:
    base = positive_fixture()
    control_fields = {
        "grammar": ["grammar_positive", "grammar_negative", "grammar_positive_context", "grammar_negative_context"],
        "encoding": ["encoding_1", "encoding_2", "remint_map", "encoding_result_1", "encoding_result_2"],
        "search": ["search_runs"],
        "scalarization": ["resource_vectors", "scalar_weights"],
    }
    names = tuple(control_fields)
    cases = 0
    satisfied = 0
    failures: list[dict[str, Any]] = []
    for mask in range(1 << len(names)):
        rec = dict(base)
        present = []
        for i, name in enumerate(names):
            if mask & (1 << i):
                present.append(name)
            else:
                for field in control_fields[name]:
                    rec.pop(field, None)
        outcome = audit_record(rec)
        expected = len(present) == len(names)
        cases += 1
        satisfied += int(outcome["requirements_satisfied"])
        if outcome["requirements_satisfied"] != expected:
            failures.append({"mask": mask, "present": present, "terminal": outcome["terminal"]})
    return {"cases": cases, "satisfying_cases": satisfied, "failures": failures}


def build_receipt() -> dict[str, Any]:
    pos = audit_record(positive_fixture())
    sens = audit_record(sensitive_fixture())
    p, n, ctx = unmatched_grammar_fixture()
    unmatched = grammar_twin_audit(p, n, ctx, dict(ctx))
    nonbijective = encoding_audit({"a": "A", "b": "B"}, {"x": "A", "y": "B"}, {"a": "x", "b": "x"}, "a", "x")
    budget_mismatch = search_audit([
        {"strategy_id": "s1", "strategy_signature": ("s1",), "objective_id": "o", "declared_budget": 1, "canonical_winner": "A"},
        {"strategy_id": "s2", "strategy_signature": ("s2",), "objective_id": "o", "declared_budget": 2, "canonical_winner": "A"},
    ])
    renamed_same_search = search_audit([
        {"strategy_id": "renamed_a", "strategy_signature": ("same_algorithm", "same_order"), "objective_id": "o", "declared_budget": 2, "canonical_winner": "A"},
        {"strategy_id": "renamed_b", "strategy_signature": ("same_algorithm", "same_order"), "objective_id": "o", "declared_budget": 2, "canonical_winner": "A"},
    ])
    bad_weight = scalarization_audit({"a": (Fraction(1), Fraction(2)), "b": (Fraction(2), Fraction(1))}, [(1, 1), (1, 0)])
    duplicate_weights = scalarization_audit({"a": (Fraction(1), Fraction(2)), "b": (Fraction(2), Fraction(1))}, [(1, 1), (1, 1)])
    census = missing_control_census()
    checks = {
        "positive_requirements_satisfied": pos["requirements_satisfied"],
        "positive_global_robust": pos["terminal"] == "ROBUST_AT_REGISTERED_CONTROLS",
        "sensitive_requirements_still_satisfied": sens["requirements_satisfied"],
        "sensitive_global_not_laundered": sens["terminal"] == "SENSITIVE_AT_REGISTERED_CONTROLS",
        "matched_twin_detected": pos["subaudits"]["grammar"]["terminal"] == "GRAMMAR_TWIN_MATCHED",
        "unmatched_background_rejected": unmatched["terminal"] == "GRAMMAR_TWIN_UNMATCHED",
        "encoding_remint_positive": pos["subaudits"]["encoding"]["terminal"] == "ENCODING_INVARIANT_AT_REGISTERED_REMINTS",
        "encoding_surface_tie_hostile": sens["subaudits"]["encoding"]["terminal"] == "ENCODING_SENSITIVE",
        "nonbijective_remint_rejected": nonbijective["terminal"] == "CANNOT_AUDIT_ENCODING",
        "alternate_search_positive": pos["subaudits"]["search"]["terminal"] == "SEARCH_INVARIANT_AT_REGISTERED_ALGORITHMS",
        "alternate_search_hostile": sens["subaudits"]["search"]["terminal"] == "SEARCH_ALGORITHM_SENSITIVE",
        "search_budget_mismatch_abstains": budget_mismatch["terminal"] == "CANNOT_COMPARE_SEARCH_BUDGETS",
        "search_rename_not_distinct": renamed_same_search.get("reason") == "SEARCHERS_NOT_MATERIALLY_DISTINCT",
        "pareto_dominance_positive": pos["subaudits"]["scalarization"]["pareto_front"] == ("efficient",),
        "scalarization_reversal_hostile": sens["subaudits"]["scalarization"]["terminal"] == "PRICE_SENSITIVE",
        "nonpositive_weight_rejected": bad_weight["terminal"] == "CANNOT_AUDIT_SCALARIZATION",
        "duplicate_weights_not_alternates": duplicate_weights.get("reason") == "SCALARIZATIONS_NOT_DISTINCT",
        "missing_controls_fail_closed": census["cases"] == 16 and census["satisfying_cases"] == 1 and not census["failures"],
    }
    return {
        "schema": "GMI833DerivationRobustnessControlsResultV1",
        "issue": 863,
        "parent_issue": 833,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_pins": PARENT_PINS,
        "checks": checks,
        "positive_control": pos,
        "sensitivity_hostile": sens,
        "unmatched_grammar_hostile": unmatched,
        "nonbijective_encoding_hostile": nonbijective,
        "search_budget_hostile": budget_mismatch,
        "renamed_same_search_hostile": renamed_same_search,
        "invalid_weight_hostile": bad_weight,
        "duplicate_weights_hostile": duplicate_weights,
        "missing_control_census": census,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


if __name__ == "__main__":
    print(canonical_json(build_receipt()), end="")
