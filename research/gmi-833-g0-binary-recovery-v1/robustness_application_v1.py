from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Callable, Sequence

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from g0_binary_recovery_v1 import (
    Candidate,
    GRAMMARS,
    candidate_space,
    delay1_target,
    dominates,
    exact_solutions,
    identity_target,
    pareto_solutions,
    satisfies,
)

ROOT = Path(__file__).resolve().parents[1]
ROBUST_PATH = ROOT / "gmi-833-robustness-controls-v1" / "robustness_controls_v1.py"


def load_robustness_module():
    if not ROBUST_PATH.exists():
        raise RuntimeError("ROBUSTNESS_CONTROL_PARENT_MISSING")
    name = "gmi_833_robustness_controls_v1"
    spec = importlib.util.spec_from_file_location(name, ROBUST_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("ROBUSTNESS_CONTROL_PARENT_UNLOADABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canonical_semantic(candidate: Candidate) -> str:
    return json.dumps(
        [candidate.state_bits, candidate.next_truth, candidate.output_truth],
        separators=(",", ":"),
    )


def semantic_encoding(kind: str) -> tuple[dict[str, str], dict[str, str]]:
    candidates = sorted(candidate_space(kind), key=lambda c: canonical_semantic(c))
    encoding: dict[str, str] = {}
    reverse: dict[str, str] = {}
    for idx, candidate in enumerate(candidates):
        surface = f"{kind.lower()}_{idx:03d}"
        canonical = canonical_semantic(candidate)
        encoding[surface] = canonical
        reverse[canonical] = surface
    if len(encoding) != 260 or len(reverse) != 260:
        raise RuntimeError("ENCODING_NOT_BIJECTIVE_TO_REGISTERED_SEMANTICS")
    return encoding, reverse


def resource_branch_and_bound(
    kind: str,
    target: Callable[[Sequence[int]], tuple[int, ...]],
) -> tuple[tuple[Candidate, ...], int, int]:
    """Independent complete Pareto search using exact-resource dominance pruning."""
    ordered = sorted(candidate_space(kind), key=lambda c: (c.resources, canonical_semantic(c)))
    exact_front: tuple[Candidate, ...] = ()
    evaluated = 0
    pruned = 0
    for candidate in ordered:
        if any(dominates(best.resources, candidate.resources) for best in exact_front):
            pruned += 1
            continue
        evaluated += 1
        if satisfies(candidate, target):
            exact_front = pareto_solutions((*exact_front, candidate))
    return exact_front, evaluated, pruned


def grammar_twin_block(rob, kind: str, ecology: str):
    positive = []
    negative = []
    for idx, candidate in enumerate(candidate_space(kind)):
        canonical = canonical_semantic(candidate)
        entry = rob.Candidate(
            cid=f"p{idx:03d}",
            semantic_class=canonical,
            has_target_mechanism=candidate.state_bits == 1,
            background_signature=(canonical, f"gates={candidate.gate_count}"),
        )
        positive.append(entry)
        if candidate.state_bits == 0:
            negative.append(
                rob.Candidate(
                    cid=f"n{idx:03d}",
                    semantic_class=canonical,
                    has_target_mechanism=False,
                    background_signature=entry.background_signature,
                )
            )
    context = {
        "ecology": ecology,
        "evaluator": "exact_protected_output_sequence",
        "declared_budget": 260,
        "stopping": "complete_scientific_result",
    }
    return positive, negative, context


def build_record(rob, kind: str, ecology: str, target):
    other = "NOR" if kind == "NAND" else "NAND"
    enc1, rev1 = semantic_encoding(kind)
    enc2, rev2 = semantic_encoding(other)
    phi = {surface: rev2[canonical] for surface, canonical in enc1.items()}

    exhaustive = pareto_solutions(exact_solutions(kind, target))
    bnb, evaluated, pruned = resource_branch_and_bound(kind, target)
    if exhaustive != bnb or len(exhaustive) != 1:
        raise RuntimeError("ALTERNATE_SEARCH_DISAGREEMENT")
    winner = exhaustive[0]
    canonical_winner = canonical_semantic(winner)

    other_winner = pareto_solutions(exact_solutions(other, target))
    if len(other_winner) != 1 or canonical_semantic(other_winner[0]) != canonical_winner:
        raise RuntimeError("GRAMMAR_TWIN_CANONICAL_WINNER_MISMATCH")

    positive, negative, context = grammar_twin_block(rob, kind, ecology)

    exact = exact_solutions(kind, target)
    ordered_exact = sorted(exact, key=lambda c: canonical_semantic(c))
    vectors = {
        f"solution_{i:03d}": tuple(rob.frac(x) for x in candidate.resources)
        for i, candidate in enumerate(ordered_exact)
    }
    winner_name = next(
        name for name, candidate in zip(vectors, ordered_exact, strict=True)
        if candidate.semantic_id == winner.semantic_id
    )

    record = {
        "grammar_positive": positive,
        "grammar_negative": negative,
        "grammar_positive_context": context,
        "grammar_negative_context": dict(context),
        "encoding_1": enc1,
        "encoding_2": enc2,
        "remint_map": phi,
        "encoding_result_1": rev1[canonical_winner],
        "encoding_result_2": rev2[canonical_winner],
        "search_runs": [
            {
                "strategy_id": "complete_enumeration",
                "strategy_signature": ("evaluate_all", "semantic_candidate_space"),
                "objective_id": f"{ecology}_exact_then_pareto",
                "declared_budget": 260,
                "canonical_winner": canonical_winner,
            },
            {
                "strategy_id": "resource_branch_and_bound",
                "strategy_signature": ("resource_order", "dominance_prune", "exact_evaluator"),
                "objective_id": f"{ecology}_exact_then_pareto",
                "declared_budget": 260,
                "canonical_winner": canonical_winner,
            },
        ],
        "resource_vectors": vectors,
        "scalar_weights": [
            (rob.frac(1), rob.frac(1)),
            (rob.frac(3), rob.frac(1)),
            (rob.frac(1), rob.frac(3)),
        ],
        "price_conditional": False,
    }
    audit = rob.audit_record(record)
    return audit, {
        "exhaustive_evaluated": 260,
        "branch_and_bound_evaluated": evaluated,
        "branch_and_bound_pruned": pruned,
        "canonical_winner": canonical_winner,
        "resource_scalarization_expected_winner_name": winner_name,
        "exact_solution_count": len(exact),
    }


def finite_certificate() -> dict[str, object]:
    rob = load_robustness_module()
    audits: dict[str, object] = {}
    search_counts: dict[str, object] = {}
    for kind in GRAMMARS:
        for ecology, target in (("DELAY1", delay1_target), ("IDENTITY", identity_target)):
            audit, counts = build_record(rob, kind, ecology, target)
            key = f"{ecology}_{kind}"
            if audit["control_requirements_terminal"] != "CONTROL_REQUIREMENTS_SATISFIED":
                raise RuntimeError(f"ROBUSTNESS_CONTROLS_INCOMPLETE:{key}")
            if audit["terminal"] != "ROBUST_AT_REGISTERED_CONTROLS":
                raise RuntimeError(f"REGISTERED_CONTROL_SENSITIVITY:{key}:{audit['terminal']}")
            audits[key] = audit
            search_counts[key] = counts

    checks = {
        "four_required_controls_present_all_runs": True,
        "matched_state_removal_grammar_twins": all(
            a["subaudits"]["grammar"]["terminal"] == "GRAMMAR_TWIN_MATCHED" for a in audits.values()
        ),
        "nand_nor_semantic_encoding_invariant": all(
            a["subaudits"]["encoding"]["terminal"] == "ENCODING_INVARIANT_AT_REGISTERED_REMINTS" for a in audits.values()
        ),
        "alternate_search_algorithms_agree": all(
            a["subaudits"]["search"]["terminal"] == "SEARCH_INVARIANT_AT_REGISTERED_ALGORITHMS" for a in audits.values()
        ),
        "pareto_and_three_positive_scalarizations_agree": all(
            a["subaudits"]["scalarization"]["terminal"] == "SCALARIZATION_INVARIANT_AT_REGISTERED_WEIGHTS" for a in audits.values()
        ),
        "all_registered_controls_robust": all(a["terminal"] == "ROBUST_AT_REGISTERED_CONTROLS" for a in audits.values()),
    }
    if not all(checks.values()):
        raise RuntimeError("ROBUSTNESS_APPLICATION_CHECK_FAILED")

    return {
        "schema": "GMI_833_G0_BINARY_RECOVERY_ROBUSTNESS_APPLICATION_V1",
        "parent_control_claim": rob.CLAIM_CEILING,
        "scientific_claim": "GMI_P3_RELATIVE_BINARY_STATE_PROPERTY_RECOVERY_UNDER_NAND_NOR_GRAMMAR_TWINS_AT_REGISTERED_FINITE_SCOPE",
        "verdict": "GREEN",
        "checks": checks,
        "audits": audits,
        "search_counts": search_counts,
        "claim_boundary": [
            "registered_controls_only",
            "alternate_search_algorithms_are_complete_enumeration_and_resource_branch_and_bound",
            "finite_sampled_positive_scalarizations_do_not_prove_universal_price_invariance",
            "matched_negative_preserves_only_registered_mechanism_free_background_signatures",
        ],
    }


if __name__ == "__main__":
    rob = load_robustness_module()
    print(json.dumps(rob.canon(finite_certificate()), sort_keys=True, separators=(",", ":")))
