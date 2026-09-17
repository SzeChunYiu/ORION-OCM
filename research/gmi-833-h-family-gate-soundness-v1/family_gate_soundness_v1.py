#!/usr/bin/env python3
"""Exact executable witnesses for the Section-H family-gate soundness theorems."""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
CLAIM_CEILING = "H_FAMILY_GATE_SOUNDNESS_PROVED__NO_FAMILY_ROW_CLOSED"

GATES = (
    "property_prediction_from_specification_ecology",
    "p3_p4_grammar",
    "no_family_macros",
    "neutral_recovery",
    "negative_twin",
    "lower_bound_where_possible",
    "resource_crossover",
    "held_out_frozen_prediction",
    "remint",
    "independent_search",
    "real_scale_test",
)

FAMILY_ROWS = (
    "Finite-state/automata intelligence.",
    "Linear regression / linear classifiers.",
    "GLMs.",
    "Basis/kernel methods.",
    "Nearest-neighbor / exemplar memory.",
    "Associative memory.",
    "Retrieval-augmented systems.",
    "Decision trees/rule systems.",
    "Symbolic logic systems.",
    "Program synthesis/program induction.",
    "Library-learning/program-reuse systems.",
    "Search/frontier algorithms.",
    "Planning systems.",
    "Dynamic programming/control.",
    "Model-free RL-like learning.",
    "Model-based RL-like learning.",
    "Bayesian inference/belief-state systems.",
    "Probabilistic graphical models.",
    "Particle/population inference.",
    "Feed-forward neural networks.",
    "Backprop/reverse-mode credit assignment.",
    "CNN/equivariant local-weight-sharing systems.",
    "RNNs.",
    "LSTM/GRU-like gating.",
    "Attention mechanisms.",
    "Transformer-like dynamic routing/composition.",
    "Graph neural/message-passing systems.",
    "State-space models.",
    "Mixture-of-experts/routing systems.",
    "Autoregressive generative systems.",
    "Latent-variable generative systems.",
    "Flow-like transport systems.",
    "Diffusion/iterative-refinement systems.",
    "Energy-based systems.",
    "Evolutionary/population search.",
    "Cellular/local-field computation.",
    "Distributed/collective intelligence.",
    "Tool-using/solver-routing intelligence.",
    "Neuro-symbolic/statistical-symbolic hybrids.",
    "Continual-learning systems.",
    "Meta-learning systems.",
    "Self-modifying/morphogenetic systems.",
    "Multi-agent emergent communication systems.",
)

FORBIDDEN_PROMOTIONS = (
    "NAMED_FAMILY_RECOVERED",
    "UNIVERSAL_FAMILY_NONRECOVERABILITY",
    "OPERATIONAL_EQUIVALENCE_IMPLIES_FAMILY_IDENTITY",
    "FINITE_EVIDENCE_IMPLIES_REAL_SCALE",
    "INDEPENDENT_TEAM_REPLICATION",
    "REAL_SCALE_VALIDATION",
)


@dataclass(frozen=True, order=True)
class Scope:
    family_row: str
    grammar_digest: str
    ecology_digest: str
    budget: str
    freeze_digest: str
    protected_interface_digest: str


@dataclass(frozen=True)
class Certificate:
    gate: str
    status: str
    scope: Scope


PASS = "PASS"
NOT_APPLICABLE_PROVED = "NOT_APPLICABLE_PROVED"
FAIL = "FAIL"


def canonical_scope(family_row: str = FAMILY_ROWS[0]) -> Scope:
    return Scope(
        family_row=family_row,
        grammar_digest="grammar-v1:4f49",
        ecology_digest="ecology-v1:270c",
        budget="registered-bound-v1",
        freeze_digest="freeze-v1:78398c6a",
        protected_interface_digest="interface-v1:binary-sequence-response",
    )


def valid_status(gate: str, status: str) -> bool:
    if gate == "lower_bound_where_possible":
        return status in (PASS, NOT_APPLICABLE_PROVED)
    return status == PASS


def closure_eligible(certificates: Sequence[Certificate], target: Scope) -> bool:
    """The conjunction and scope-custody rule from FGS-1/FGS-2."""
    if len(certificates) != len(GATES):
        return False
    by_gate: dict[str, Certificate] = {}
    for certificate in certificates:
        if certificate.gate not in GATES or certificate.gate in by_gate:
            return False
        by_gate[certificate.gate] = certificate
    return all(
        by_gate[gate].scope == target and valid_status(gate, by_gate[gate].status)
        for gate in GATES
    )


def complete_bundle(scope: Scope, lower_bound_applicable: bool = True) -> tuple[Certificate, ...]:
    return tuple(
        Certificate(
            gate,
            PASS if gate != "lower_bound_where_possible" or lower_bound_applicable
            else NOT_APPLICABLE_PROVED,
            scope,
        )
        for gate in GATES
    )


def single_missing_gate_hostiles(scope: Scope) -> tuple[Mapping[str, object], ...]:
    rows = []
    complete = complete_bundle(scope)
    for missing in GATES:
        bundle = tuple(c for c in complete if c.gate != missing)
        rows.append({"missing": missing, "eligible": closure_eligible(bundle, scope)})
    return tuple(rows)


def single_failed_gate_hostiles(scope: Scope) -> tuple[Mapping[str, object], ...]:
    rows = []
    for failed in GATES:
        bundle = tuple(
            Certificate(c.gate, FAIL if c.gate == failed else c.status, c.scope)
            for c in complete_bundle(scope)
        )
        rows.append({"failed": failed, "eligible": closure_eligible(bundle, scope)})
    return tuple(rows)


def scope_gluing_hostiles(scope: Scope) -> tuple[Mapping[str, object], ...]:
    """Every single incompatible certificate defeats same-scope composition."""
    rows = []
    for shifted in GATES:
        incompatible = Scope(
            family_row=scope.family_row,
            grammar_digest=scope.grammar_digest,
            ecology_digest=scope.ecology_digest,
            budget=scope.budget + ":other",
            freeze_digest=scope.freeze_digest,
            protected_interface_digest=scope.protected_interface_digest,
        )
        bundle = tuple(
            Certificate(c.gate, c.status, incompatible if c.gate == shifted else c.scope)
            for c in complete_bundle(scope)
        )
        rows.append({"incompatible_gate": shifted, "eligible": closure_eligible(bundle, scope)})
    return tuple(rows)


def continuation_pair(observed: Sequence[int]) -> tuple[Callable[[int], int], Callable[[int], int]]:
    """Construct two total continuations agreeing on the finite observed prefix."""
    frozen = tuple(observed)
    if not frozen or any(bit not in (0, 1) for bit in frozen):
        raise ValueError("observed must be a nonempty binary prefix")

    def conservative(index: int) -> int:
        if index < 0:
            raise ValueError("index must be nonnegative")
        return frozen[index] if index < len(frozen) else 0

    def divergent(index: int) -> int:
        if index < 0:
            raise ValueError("index must be nonnegative")
        if index < len(frozen):
            return frozen[index]
        return 1 if index == len(frozen) else 0

    return conservative, divergent


def finite_evidence_census(max_bound: int = 7) -> Mapping[str, object]:
    cases = 0
    for bound in range(max_bound + 1):
        width = bound + 1
        for mask in range(1 << width):
            observed = tuple((mask >> i) & 1 for i in range(width))
            left, right = continuation_pair(observed)
            assert all(left(i) == right(i) == observed[i] for i in range(width))
            assert left(width) != right(width)
            cases += 1
    return {
        "bounds": [0, max_bound],
        "observed_prefixes_checked": cases,
        "expected_prefixes": sum(1 << (bound + 1) for bound in range(max_bound + 1)),
        "first_unobserved_disagreement_proved": True,
    }


def response_one_state(word: Sequence[int]) -> tuple[int, ...]:
    """Visible response of a one-hidden-state organization."""
    return tuple(word)


def response_two_state(word: Sequence[int]) -> tuple[int, ...]:
    """Distinct hidden organization: state toggles, output remains current input."""
    state = 0
    output = []
    for symbol in word:
        if symbol not in (0, 1):
            raise ValueError("binary words only")
        output.append(symbol)
        state = 1 - state
    return tuple(output)


def binary_words_through(max_length: int) -> Iterable[tuple[int, ...]]:
    for length in range(max_length + 1):
        yield from itertools.product((0, 1), repeat=length)


def observational_nonidentifiability_census(max_length: int = 8) -> Mapping[str, object]:
    words = tuple(binary_words_through(max_length))
    equal = all(response_one_state(word) == response_two_state(word) for word in words)
    return {
        "words_checked": len(words),
        "max_length": max_length,
        "profiles_equal": equal,
        "hidden_organizations_distinct": True,
        "one_state_hidden_count": 1,
        "two_state_hidden_count": 2,
        "general_proof": "BY_STEP_DEFINITION_OUTPUT_EQUALS_CURRENT_SYMBOL_IN_BOTH_ORGANIZATIONS",
    }


def remint_gate(gate: str) -> str:
    digest = hashlib.sha256(("gate-remint-v1:" + gate).encode()).hexdigest()[:16]
    return "G-" + digest


def remint_family(row: str) -> str:
    digest = hashlib.sha256(("family-remint-v1:" + row).encode()).hexdigest()[:16]
    return "F-" + digest


def remint_census() -> Mapping[str, object]:
    gate_ids = tuple(remint_gate(g) for g in GATES)
    family_ids = tuple(remint_family(row) for row in FAMILY_ROWS)
    scope = canonical_scope()
    original = complete_bundle(scope)
    reminted_statuses = {remint_gate(c.gate): c.status for c in original}
    reconstructed = tuple(
        Certificate(gate, reminted_statuses[remint_gate(gate)], scope) for gate in GATES
    )
    return {
        "gate_ids_unique": len(set(gate_ids)) == len(GATES),
        "family_ids_unique": len(set(family_ids)) == len(FAMILY_ROWS),
        "closure_invariant": closure_eligible(original, scope) == closure_eligible(reconstructed, scope),
        "gate_count": len(gate_ids),
        "family_count": len(family_ids),
    }


def reconciliation_preview() -> Mapping[str, object]:
    return {
        "schema": "GMI_833_RECONCILIATION_H_FAMILY_GATE_SOUNDNESS_V1",
        "issue": 833,
        "mode": "NO_MUTATION_PREVIEW",
        "mutations": [],
        "named_rows": [
            {
                "text": "- [ ] " + row,
                "close": False,
                "reason": "this theorem package furnishes no same-scope eleven-gate family evidence bundle",
            }
            for row in FAMILY_ROWS
        ],
        "aggregate_row": {
            "text": "- [ ] Quantify which families cannot be recovered and why.",
            "close": False,
            "owner_pr": 987,
            "reason": "non-overlap: PR #987 owns the aggregate obstruction census",
        },
    }


def build_result() -> Mapping[str, object]:
    scope = canonical_scope()
    complete_pass = closure_eligible(complete_bundle(scope), scope)
    lower_bound_na_pass = closure_eligible(complete_bundle(scope, lower_bound_applicable=False), scope)
    missing = single_missing_gate_hostiles(scope)
    failed = single_failed_gate_hostiles(scope)
    gluing = scope_gluing_hostiles(scope)
    finite = finite_evidence_census()
    observational = observational_nonidentifiability_census()
    remint = remint_census()
    preview = reconciliation_preview()
    checks = {
        "complete_conjunction_eligible": complete_pass,
        "proved_lower_bound_na_eligible": lower_bound_na_pass,
        "every_single_missing_gate_blocks": all(not row["eligible"] for row in missing),
        "every_single_failed_gate_blocks": all(not row["eligible"] for row in failed),
        "every_incompatible_scope_gate_blocks": all(not row["eligible"] for row in gluing),
        "finite_evidence_has_divergent_continuations": finite["first_unobserved_disagreement_proved"],
        "observational_profile_does_not_identify_hidden_organization": (
            observational["profiles_equal"] and observational["hidden_organizations_distinct"]
        ),
        "remint_invariant": all(
            remint[key] for key in ("gate_ids_unique", "family_ids_unique", "closure_invariant")
        ),
        "all_43_named_rows_audited_open": (
            len(preview["named_rows"]) == 43
            and all(not row["close"] for row in preview["named_rows"])
        ),
        "no_reconciliation_mutation": preview["mutations"] == [],
        "aggregate_row_left_to_pr_987": preview["aggregate_row"]["owner_pr"] == 987,
    }
    return {
        "schema": "GMI_833_H_FAMILY_GATE_SOUNDNESS_RESULT_V1",
        "verdict": "GREEN" if all(checks.values()) else "RED",
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "checks": checks,
        "gate_model": {
            "gate_count": len(GATES),
            "gates": list(GATES),
            "closure_operator": "SAME_SCOPE_CONJUNCTION",
            "lower_bound_rule": "PASS_OR_PROVED_NOT_APPLICABLE",
            "single_missing_hostiles": list(missing),
            "single_failed_hostiles": list(failed),
            "scope_gluing_hostiles": list(gluing),
        },
        "finite_evidence_non_promotion": finite,
        "observational_family_nonidentifiability": observational,
        "remint": remint,
        "section_h_audit": {
            "named_family_row_count": len(FAMILY_ROWS),
            "rows_closed_by_package": 0,
            "aggregate_obstruction_owner_pr": 987,
        },
    }


def canonical_bytes(value: Mapping[str, object]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    result = build_result()
    preview = reconciliation_preview()
    (ROOT / "RESULT_V1.json").write_bytes(canonical_bytes(result))
    (ROOT / "ISSUE_833_RECONCILIATION_H_FAMILY_GATE_SOUNDNESS_V1.json").write_bytes(
        canonical_bytes(preview)
    )
    print(json.dumps({
        "verdict": result["verdict"],
        "result_sha256": hashlib.sha256(canonical_bytes(result)).hexdigest(),
        "named_rows_closed": result["section_h_audit"]["rows_closed_by_package"],
    }, sort_keys=True))
    return 0 if result["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
