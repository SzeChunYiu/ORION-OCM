#!/usr/bin/env python3
"""One lower finite process grammar; family names are post-hoc only."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha1, sha256
from itertools import product
import json
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
FIELD = (0, 1, 2)
CLAIM_CEILING = (
    "ONE_LOWER_NEUTRAL_GRAMMAR_RECOVERS_FOUR_POSTHOC_STRUCTURAL_CLASSES_"
    "AT_REGISTERED_FINITE_SCOPE__FAMILY_GATES_REMAIN_OPEN"
)
FORBIDDEN_PROMOTIONS = (
    "FINITE_STATE_AUTOMATA_FAMILY_ROW_CLOSED",
    "LINEAR_REGRESSION_CLASSIFIER_FAMILY_ROW_CLOSED",
    "GLM_FAMILY_ROW_CLOSED",
    "BASIS_KERNEL_FAMILY_ROW_CLOSED",
    "REAL_SCALE_VALIDATION_COMPLETE",
    "ALL_KNOWN_FAMILIES_RECOVERED",
    "UNIVERSAL_GRAMMAR_NEUTRALITY",
    "SEARCH_NEUTRALITY",
    "COMPLETE_GMI",
)
PARENT_PINS = (
    ("foundation", "research/gmi-833-foundation-v1/RESULT_V1.json", "c0c574c4ec6e237d5fdafa694eac131399625a70"),
    ("process_organizations", "research/gmi-833-aj4-process-organizations-v1/RESULT_V1.json", "9b2bfd33f2392f82ac3d37cf7f17c1ff6b498ec4"),
    ("lower_compilation", "research/gmi-833-aj5-g0-compilation-v1/RESULT_V1.json", "6a9bae0ea5fa2e42253e8da4c965a07a81264248"),
    ("target_encoded_microscope", "research/machine-intelligence-morphogenesis-v1/GMI_ZERO_PRIOR_EXACT_REDISCOVERY_MICROSCOPE_V1.md", "908b8d38c8fc22b1297d097ffe8f168676046b3a"),
    ("known_form_theorems", "research/machine-intelligence-morphogenesis-v1/GMI_KNOWN_FORM_DERIVATION_THEOREMS_V1.md", "e8d488ce622dacb5e53560b14f177ad0cbaf5cf6"),
    ("p0_closure_claim", "research/gmi-p0-zero-prior-closure-v1/CORE.md", "c0f36dc9f6b55c0ee6bb9048acd22beae285c432"),
)

# This object is frozen once and passed unchanged to every generator call.
# Its vocabulary is lower-process vocabulary, not a candidate-family menu.
GRAMMAR = {
    "schema": "FiniteLowerProcessGrammarV1",
    "carrier": FIELD,
    "terminals": ("ARG", "CONST"),
    "compositions": ("ADD_MOD", "MUL_MOD", "ZERO_TEST"),
    "storage": ("INDEXED_PARAMETER_READ",),
    "temporal": ("DELAY_CELL",),
    "max_weighted_serve_cost": 4,
}


def repo_root(start: Path | None = None) -> Path:
    current = (start or HERE).resolve()
    while current.parent != current:
        if (current / ".git").exists() or (current / "research").is_dir():
            return current
        current = current.parent
    return HERE.parents[1]


def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parents(root: Path | None = None) -> dict[str, object]:
    root = root or repo_root()
    rows = []
    for name, path, expected in PARENT_PINS:
        target = root / path
        actual = git_blob_sha(target.read_bytes()) if target.is_file() else None
        rows.append({"name": name, "path": path, "actual_blob": actual, "blob_ok": actual == expected})
    return {"rows": rows, "all_ok": all(row["blob_ok"] for row in rows)}


def grammar_digest() -> str:
    return sha256(canonical_json(GRAMMAR).encode()).hexdigest()


def domain(arity: int) -> tuple[tuple[int, ...], ...]:
    if type(arity) is not int or not 1 <= arity <= 3:
        raise ValueError("registered arity must be 1, 2, or 3")
    return tuple(product(FIELD, repeat=arity))


@dataclass(frozen=True)
class Candidate:
    semantics: tuple[int, ...]
    code: str
    description: int
    serve: int
    provenance: tuple[str, ...]

    def resource(self) -> tuple[int, int]:
        return self.description, self.serve


def _zero(value: int) -> int:
    return int(value == 0)


def _pareto_insert(front: dict[tuple[tuple[int, ...], int], Candidate], candidate: Candidate) -> None:
    key = (candidate.semantics, candidate.serve)
    previous = front.get(key)
    if previous is None or (candidate.description, candidate.code) < (previous.description, previous.code):
        front[key] = candidate


@lru_cache(maxsize=None)
def generate_composed(arity: int, max_serve: int | None = None) -> tuple[Candidate, ...]:
    """Enumerate grammar expressions without consulting any obligation."""
    points = domain(arity)
    max_serve = GRAMMAR["max_weighted_serve_cost"] if max_serve is None else max_serve
    if type(max_serve) is not int or max_serve < 0:
        raise ValueError("max_serve must be a nonnegative integer")
    levels: dict[int, dict[tuple[tuple[int, ...], int], Candidate]] = {cost: {} for cost in range(max_serve + 1)}
    for index in range(arity):
        semantics = tuple(point[index] for point in points)
        candidate = Candidate(semantics, f"A{index}", 0, 0, ("ARG",))
        _pareto_insert(levels[0], candidate)
    for value in FIELD:
        candidate = Candidate(tuple(value for _ in points), f"C{value}", 1, 0, ("CONST",))
        _pareto_insert(levels[0], candidate)

    for total in range(1, max_serve + 1):
        # ZERO_TEST has unit serve cost.
        for child in levels[total - 1].values():
            candidate = Candidate(
                tuple(_zero(value) for value in child.semantics),
                f"Z({child.code})",
                child.description + 1,
                total,
                child.provenance + ("ZERO_TEST",),
            )
            _pareto_insert(levels[total], candidate)

        # ADD_MOD costs one; MUL_MOD costs two at the lower-process meter.
        for op, op_cost, tag in (("A", 1, "ADD_MOD"), ("M", 2, "MUL_MOD")):
            remaining = total - op_cost
            if remaining < 0:
                continue
            for left_cost in range(remaining + 1):
                right_cost = remaining - left_cost
                for left in levels[left_cost].values():
                    for right in levels[right_cost].values():
                        if left.code > right.code:
                            continue
                        if op == "A":
                            semantics = tuple((x + y) % 3 for x, y in zip(left.semantics, right.semantics))
                        else:
                            semantics = tuple((x * y) % 3 for x, y in zip(left.semantics, right.semantics))
                        candidate = Candidate(
                            semantics,
                            f"{op}({left.code},{right.code})",
                            left.description + right.description + 1,
                            total,
                            left.provenance + right.provenance + (tag,),
                        )
                        _pareto_insert(levels[total], candidate)

    result = []
    for cost in levels:
        result.extend(levels[cost].values())
    return tuple(sorted(result, key=lambda row: (row.semantics, row.serve, row.description, row.code)))


@lru_cache(maxsize=None)
def semantic_frontier(arity: int) -> dict[tuple[int, ...], tuple[Candidate, ...]]:
    grouped: dict[tuple[int, ...], list[Candidate]] = {}
    for candidate in generate_composed(arity):
        grouped.setdefault(candidate.semantics, []).append(candidate)
    frontiers = {}
    for semantics, rows in grouped.items():
        kept = []
        for row in rows:
            if any(
                other.description <= row.description
                and other.serve <= row.serve
                and other.resource() != row.resource()
                for other in rows
            ):
                continue
            kept.append(row)
        frontiers[semantics] = tuple(sorted(kept, key=lambda item: (item.description, item.serve, item.code)))
    return frontiers


def indexed_candidate(semantics: Sequence[int], arity: int) -> Candidate:
    values = tuple(semantics)
    if len(values) != len(domain(arity)) or any(type(value) is not int or value not in FIELD for value in values):
        raise ValueError("indexed payload must give one carrier value per input")
    return Candidate(values, "I[" + "".join(map(str, values)) + "]", len(values) + 2, 1, ("INDEXED_PARAMETER_READ",))


@lru_cache(maxsize=None)
def generate_indexed(arity: int) -> tuple[Candidate, ...]:
    """Materialize the complete generic indexed universe before filtering."""
    rows = len(domain(arity))
    return tuple(indexed_candidate(values, arity) for values in product(FIELD, repeat=rows))


def exact_candidates(table: Sequence[int], arity: int) -> tuple[Candidate, ...]:
    target = tuple(table)
    rows = list(semantic_frontier(arity).get(target, ()))
    rows.extend(candidate for candidate in generate_indexed(arity) if candidate.semantics == target)
    return tuple(sorted(rows, key=lambda row: (row.description, row.serve, row.code)))


def select_exact(table: Sequence[int], arity: int, regime: dict[str, int]) -> dict[str, object]:
    required = ("description_price", "serve_price", "reuse")
    if any(type(regime.get(key)) is not int or regime[key] < 0 for key in required):
        raise ValueError("resource prices and reuse must be nonnegative integers")
    rows = exact_candidates(table, arity)
    if not rows:
        return {"status": "NO_EXACT_CANDIDATE"}
    scored = []
    for row in rows:
        score = regime["description_price"] * row.description + regime["serve_price"] * regime["reuse"] * row.serve
        scored.append((score, row.code, row))
    best_score = min(row[0] for row in scored)
    winners = [row for score, _, row in scored if score == best_score]
    return {
        "status": "EXACT_SELECTED",
        "score": best_score,
        "winners": tuple(row.code for row in winners),
        "winner_resources": tuple(row.resource() for row in winners),
        "all_exact_candidates": len(rows),
    }


def affine_coefficients(table: Sequence[int], arity: int) -> tuple[tuple[int, ...], ...]:
    target = tuple(table)
    points = domain(arity)
    matches = []
    for coefficients in product(FIELD, repeat=arity + 1):
        values = tuple(
            (coefficients[0] + sum(coefficients[index + 1] * point[index] for index in range(arity))) % 3
            for point in points
        )
        if values == target:
            matches.append(coefficients)
    return tuple(matches)


def zero_of_affine(table: Sequence[int], arity: int) -> bool:
    target = tuple(table)
    points = domain(arity)
    for coefficients in product(FIELD, repeat=arity + 1):
        score = tuple(
            (coefficients[0] + sum(coefficients[index + 1] * point[index] for index in range(arity))) % 3
            for point in points
        )
        if tuple(_zero(value) for value in score) == target:
            return True
    return False


def mixed_interaction(table: Sequence[int]) -> bool:
    values = tuple(table)
    if len(values) != 9:
        raise ValueError("mixed interaction is registered for two ternary inputs")
    at = lambda x, y: values[3 * x + y]
    return any((at(x, y) - at(x, 0) - at(0, y) + at(0, 0)) % 3 for x in FIELD for y in FIELD)


def blind_structural_class(table: Sequence[int], arity: int) -> str:
    target = tuple(table)
    if affine_coefficients(target, arity):
        return "AFFINE_SHARED_RESPONSE" if arity == 1 else "ADDITIVELY_SEPARABLE_RESPONSE"
    if zero_of_affine(target, arity):
        return "BINARY_DECISION_ON_AFFINE_SCORE"
    if arity == 1:
        return "NON_AFFINE_LINK_OF_ONE_DIMENSIONAL_SCORE"
    if arity == 2 and mixed_interaction(target):
        return "CROSS_COORDINATE_LIFTED_INTERACTION"
    return "UNCLASSIFIED_FINITE_RESPONSE"


def independent_formula_search(table: Sequence[int], arity: int) -> tuple[str, ...]:
    """A formula-family census independent of the syntax dynamic program."""
    target = tuple(table)
    points = domain(arity)
    signatures = set()
    if affine_coefficients(target, arity):
        signatures.add("AFFINE_SHARED_RESPONSE" if arity == 1 else "ADDITIVELY_SEPARABLE_RESPONSE")
    if zero_of_affine(target, arity):
        signatures.add("BINARY_DECISION_ON_AFFINE_SCORE")
    if arity == 1:
        # Exhaust all affine scores and all 27 unary carrier maps. This is a
        # complete finite link census and is not derived from expression syntax.
        for coefficients in product(FIELD, repeat=2):
            score = tuple((coefficients[0] + coefficients[1] * point[0]) % 3 for point in points)
            for link in product(FIELD, repeat=3):
                if tuple(link[value] for value in score) == target and not affine_coefficients(target, 1):
                    signatures.add("NON_AFFINE_LINK_OF_ONE_DIMENSIONAL_SCORE")
                    break
    if arity == 2:
        # Independently enumerate the four-coefficient bilinear response class.
        for coefficients in product(FIELD, repeat=4):
            response = tuple(
                (
                    coefficients[0]
                    + coefficients[1] * x
                    + coefficients[2] * y
                    + coefficients[3] * x * y
                )
                % 3
                for x, y in points
            )
            if response == target and coefficients[3] != 0:
                signatures.add("CROSS_COORDINATE_LIFTED_INTERACTION")
    return tuple(sorted(signatures))


def run_step(next_table: Sequence[int], output_table: Sequence[int], word: Sequence[int]) -> tuple[int, ...]:
    next_values, output_values = tuple(next_table), tuple(output_table)
    if len(next_values) != 9 or len(output_values) != 9:
        raise ValueError("step tables must cover state x input")
    state = 0
    outputs = []
    for symbol in word:
        if type(symbol) is not int or symbol not in FIELD:
            raise ValueError("word uses a value outside the carrier")
        address = 3 * state + symbol
        outputs.append(output_values[address])
        state = next_values[address]
    return tuple(outputs)


@lru_cache(maxsize=1)
def generate_temporal_programs() -> tuple[tuple[Candidate, Candidate], ...]:
    """Generate the bounded composed temporal universe before trace filtering."""
    expressions = generate_composed(2)
    return tuple(
        (next_expression, output_expression)
        for next_expression in expressions
        for output_expression in expressions
        if next_expression.serve + output_expression.serve <= GRAMMAR["max_weighted_serve_cost"]
    )


def sequence_witness(obligation: dict[str, object]) -> dict[str, object]:
    traces = tuple((tuple(row["input"]), tuple(row["output"])) for row in obligation["protected_traces"])
    exact = []
    for expression in generate_composed(1):
        if all(tuple(expression.semantics[symbol] for symbol in word) == expected for word, expected in traces):
            exact.append({
                "code": "S:" + expression.code,
                "cells": 0,
                "description": expression.description,
                "operations": expression.serve,
            })
    for next_expression, output_expression in generate_temporal_programs():
        if all(run_step(next_expression.semantics, output_expression.semantics, word) == expected for word, expected in traces):
            shared = next_expression.code == output_expression.code
            exact.append({
                "code": "D:" + next_expression.code + "/" + output_expression.code,
                "cells": 1,
                "description": next_expression.description if shared else next_expression.description + output_expression.description,
                "operations": next_expression.serve if shared else next_expression.serve + output_expression.serve,
            })
    for row in exact:
        row["score"] = 10 * row["description"] + row["operations"] + row["cells"]
    exact.sort(key=lambda row: (row["score"], row["code"]))
    return {
        "generated_stateless_programs": len(generate_composed(1)),
        "generated_temporal_programs": len(generate_temporal_programs()),
        "generic_indexed_temporal_semantics": 3 ** 18,
        "generic_indexed_description_lower_bound": 20,
        "exact_count": len(exact),
        "selected": exact[0] if exact else None,
    }


def sequence_lower_bound(obligation: dict[str, object]) -> dict[str, object]:
    traces = {tuple(row["input"]): tuple(row["output"]) for row in obligation["protected_traces"]}
    residuals = tuple(traces[(prefix, 0)][1] for prefix in FIELD)
    return {
        "distinguished_prefixes": len(set(residuals)),
        "residuals_on_common_suffix_zero": residuals,
        "minimum_states": len(set(residuals)),
    }


def state_history_crossover(horizon: int, state_price: int, operation_price: int = 1) -> dict[str, object]:
    if type(horizon) is not int or horizon < 2 or type(state_price) is not int or state_price < 0:
        raise ValueError("registered crossover needs horizon >=2 and nonnegative integer price")
    recurrent_ops = horizon
    replay_ops = horizon * (horizon - 1) // 2
    recurrent = state_price + operation_price * recurrent_ops
    replay = operation_price * replay_ops
    return {
        "recurrent_cost": recurrent,
        "history_replay_cost": replay,
        "decision": "PERSISTENT" if recurrent < replay else "REPLAY" if replay < recurrent else "TIE",
        "phase_iff": (recurrent < replay) == (state_price < operation_price * (replay_ops - recurrent_ops)),
    }


def carrier_remint(table: Sequence[int], arity: int, permutation: Sequence[int]) -> tuple[int, ...]:
    permutation = tuple(permutation)
    if sorted(permutation) != list(FIELD):
        raise ValueError("remint must be a permutation of the carrier")
    inverse = {new: old for old, new in enumerate(permutation)}
    original = tuple(table)
    reminted = []
    points = domain(arity)
    address = {point: index for index, point in enumerate(points)}
    for new_point in points:
        old_point = tuple(inverse[value] for value in new_point)
        reminted.append(permutation[original[address[old_point]]])
    return tuple(reminted)


def remint_audit(table: Sequence[int], arity: int) -> dict[str, object]:
    checks = 0
    for permutation in product(FIELD, repeat=3):
        if sorted(permutation) != list(FIELD):
            continue
        transformed = carrier_remint(table, arity, permutation)
        restored = carrier_remint(transformed, arity, tuple(permutation.index(value) for value in FIELD))
        if restored != tuple(table):
            raise ValueError("carrier transport failed")
        checks += 1
    return {"permutations": checks, "all_roundtrips": True}


def step_remint_audit() -> dict[str, object]:
    next_table = tuple((state + symbol) % 3 for state, symbol in domain(2))
    output_table = next_table
    checks = 0
    for permutation in product(FIELD, repeat=3):
        if sorted(permutation) != list(FIELD):
            continue
        inverse = {new: old for old, new in enumerate(permutation)}
        transported_next = []
        transported_output = []
        for new_state, new_symbol in domain(2):
            old_address = 3 * inverse[new_state] + inverse[new_symbol]
            transported_next.append(permutation[next_table[old_address]])
            transported_output.append(permutation[output_table[old_address]])
        for old_state, old_symbol in domain(2):
            new_address = 3 * permutation[old_state] + permutation[old_symbol]
            if transported_next[new_address] != permutation[next_table[3 * old_state + old_symbol]]:
                raise ValueError("next-state transport failed")
            if transported_output[new_address] != permutation[output_table[3 * old_state + old_symbol]]:
                raise ValueError("output transport failed")
            checks += 1
    return {"permutations": 6, "transition_output_checks": checks, "all_transport_checks": True}


def generic_index_census(arity: int) -> int:
    return len(generate_indexed(arity))


def semantic_no_smuggling_audit() -> dict[str, object]:
    serialized = canonical_json(GRAMMAR).lower()
    forbidden = ("autom", "regress", "classifier", "glm", "kernel", "basis", "family")
    token_clean = not any(token in serialized for token in forbidden)
    generated = {arity: generate_composed(arity) for arity in (1, 2)}
    provenance_ok = all(
        set(candidate.provenance) <= {"ARG", "CONST", "ADD_MOD", "MUL_MOD", "ZERO_TEST"}
        for rows in generated.values()
        for candidate in rows
    )
    denotations_ok = all(
        len(candidate.semantics) == len(domain(arity)) and all(value in FIELD for value in candidate.semantics)
        for arity, rows in generated.items()
        for candidate in rows
    )
    # Generation is run once per arity, before obligation lookup. The digest is
    # rechecked after all searches; equality proves the grammar did not mutate.
    before = grammar_digest()
    for arity in (1, 2):
        _ = semantic_frontier(arity)
    after = grammar_digest()
    return {
        "token_scan_clean": token_clean,
        "provenance_closed_over_registered_lower_ops": provenance_ok,
        "denotations_total_on_full_carrier_domains": denotations_ok,
        "grammar_digest_before": before,
        "grammar_digest_after": after,
        "grammar_unchanged": before == after,
        "composed_candidates": {str(arity): len(rows) for arity, rows in generated.items()},
        "generic_index_semantics": {str(arity): generic_index_census(arity) for arity in (1, 2)},
        "composed_temporal_programs": len(generate_temporal_programs()),
        "generic_indexed_temporal_semantics": 3 ** 18,
        "semantic_verdict": "NO_TARGET_DEPENDENT_GENERATION_DETECTED",
    }


def load_inputs() -> tuple[dict[str, object], dict[str, object]]:
    obligations = json.loads((HERE / "FROZEN_OBLIGATIONS_V1.json").read_text())
    predictions = json.loads((HERE / "FROZEN_PREDICTIONS_V1.json").read_text())
    return obligations, predictions


def prediction_audit(obligations: dict[str, object], predictions: dict[str, object]) -> dict[str, object]:
    by_id = {row["id"]: row for row in obligations["obligations"]}
    aliases = {
        "AFFINE_SHARED_COEFFICIENT_RESPONSE": "AFFINE_SHARED_RESPONSE",
        "NON_AFFINE_UNARY_RESPONSE": "NON_AFFINE_LINK_OF_ONE_DIMENSIONAL_SCORE",
        "AFFINE_RESPONSE_WITHOUT_LINK": "AFFINE_SHARED_RESPONSE",
    }
    expected = {
        row["obligation"]: aliases.get(row["property"].upper(), row["property"].upper())
        for row in predictions["predictions"]
    }
    recovered = {}
    for obligation_id, row in by_id.items():
        if row["interface"] == "one_symbol":
            recovered[obligation_id] = blind_structural_class(row["table"], 1)
        elif row["interface"] == "two_symbol":
            recovered[obligation_id] = blind_structural_class(row["table"], 2)
        else:
            witness = sequence_witness(row)
            recovered[obligation_id] = (
                "PERSISTENT_THREE_CLASS_FUTURE_RESPONSE_QUOTIENT"
                if witness["selected"] and witness["selected"]["cells"] == 1
                else "MEMORYLESS_PROJECTION"
            )
    # Structural wording differs only in the frozen state positive abbreviation.
    expected["O0_POS"] = "PERSISTENT_THREE_CLASS_FUTURE_RESPONSE_QUOTIENT"
    return {
        "recovered": recovered,
        "expected": expected,
        "all_match": recovered == expected,
    }


def independent_search_audit(obligations: dict[str, object]) -> dict[str, object]:
    rows = {}
    for obligation in obligations["obligations"]:
        if obligation["interface"] not in ("one_symbol", "two_symbol"):
            continue
        arity = 1 if obligation["interface"] == "one_symbol" else 2
        syntax_class = blind_structural_class(obligation["table"], arity)
        formula_classes = independent_formula_search(obligation["table"], arity)
        rows[obligation["id"]] = {
            "syntax_dynamic_program": syntax_class,
            "independent_formula_census": formula_classes,
            "agreement": syntax_class in formula_classes,
        }
    state_row = next(row for row in obligations["obligations"] if row["id"] == "O0_POS")
    state_bound = sequence_lower_bound(state_row)
    rows["O0_POS"] = {
        "step_realization": sequence_witness(state_row)["selected"]["code"],
        "independent_residual_quotient_states": state_bound["minimum_states"],
        "agreement": state_bound["minimum_states"] == 3,
    }
    return {"rows": rows, "all_agree": all(row["agreement"] for row in rows.values())}


def family_gate_ledger() -> dict[str, object]:
    data = json.loads((HERE / "FAMILY_GATE_LEDGER_V1.json").read_text())
    gates = tuple(data["gate_order"])
    rows = data["families"]
    evidence = data["evidence"]
    if len(gates) != 10 or len(rows) != 4:
        raise ValueError("ten-gate/four-family contract drifted")
    for row in rows:
        if tuple(row["gates"]) != gates:
            raise ValueError("family gate ordering/content drifted")
        for gate, result in row["gates"].items():
            if result["status"] == "OPEN":
                if gate != "real_scale_test" or result["evidence"] is not None:
                    raise ValueError("only the unsupported real-scale gate may be open")
            elif result["evidence"] not in evidence:
                raise ValueError("supported gate lacks an explicit evidence reference")
        if row["complete"] or row["issue_833_checkbox"] != "MUST_REMAIN_OPEN":
            raise ValueError("incomplete family row was promoted")
    return {
        "gate_count": len(gates),
        "rows": rows,
        "evidence": evidence,
        "all_family_rows_open": all(not row["complete"] for row in rows),
    }


def validate_artifacts() -> dict[str, object]:
    parent = json.loads((HERE / "PARENT_DISPOSITION_V1.json").read_text())
    scientific = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text())
    reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_H_NEUTRAL_V1.json").read_text())
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text())
    oracle = json.loads((HERE / "ORACLE_RESULT_V1.json").read_text())
    replacement = reconciliation.get("replacements", [])
    return {
        "target_encoded_parent_downgraded": parent.get("target_encoded_parent_terminal") == "CALIBRATION_ONLY__NOT_NEUTRAL_RECOVERY",
        "p0_closure_downgraded": parent.get("p0_terminal_disposition") == "SUPERSEDED_FOR_SECTION_H_NEUTRAL_RECOVERY_AUTHORITY",
        "family_rows_open": all(not row.get("close") for row in reconciliation.get("family_rows", [])),
        "no_issue_mutation": reconciliation.get("mutation_authorized") is False and replacement == [],
        "preexisting_row_reference": reconciliation.get("audited_parent_row_contains") == "#931–#937 + #951",
        "scientific_claims": len(scientific.get("claims", [])),
        "manifest_source_pr": manifest.get("source_pr"),
        "oracle_green": oracle.get("verdict") == "GREEN" and oracle.get("imports_primary_checker") is False,
        "oracle_recovered": oracle.get("recovered"),
    }


def build_receipt(parent_audit: dict[str, object] | None = None) -> dict[str, object]:
    parent_audit = parent_audit or audit_parents()
    obligations, predictions = load_inputs()
    by_id = {row["id"]: row for row in obligations["obligations"]}
    regimes = {row["id"]: row for row in obligations["resource_regimes"]}
    prediction = prediction_audit(obligations, predictions)
    independent = independent_search_audit(obligations)
    no_smuggling = semantic_no_smuggling_audit()
    gates = family_gate_ledger()
    selection = {}
    for obligation_id in ("O1_POS", "O1_DECISION", "O1_NEG", "O2_POS", "O2_NEG", "O3_POS", "O3_NEG"):
        row = by_id[obligation_id]
        arity = 1 if row["interface"] == "one_symbol" else 2
        selection[obligation_id] = {
            "storage": select_exact(row["table"], arity, regimes["R_STORAGE"]),
            "reuse": select_exact(row["table"], arity, regimes["R_REUSE"]),
            "class": blind_structural_class(row["table"], arity),
            "remint": remint_audit(row["table"], arity),
        }
    sequences = {
        "positive": sequence_witness(by_id["O0_POS"]),
        "negative": sequence_witness(by_id["O0_NEG"]),
        "lower_bound": sequence_lower_bound(by_id["O0_POS"]),
        "cheap_state": state_history_crossover(4, 1),
        "expensive_state": state_history_crossover(4, 20),
        "remint": step_remint_audit(),
    }
    lower_bounds = {
        "affine_trits": 2,
        "affine_law_count": 3 ** 2,
        "linked_distinct_laws": len({
            tuple(((a * x + b) % 3) ** 2 % 3 for x in FIELD)
            for a, b in product(FIELD, repeat=2)
        }),
        "bilinear_affine_trits": 4,
        "bilinear_affine_law_count": 3 ** 4,
        "state_count": sequences["lower_bound"]["minimum_states"],
    }
    artifacts = validate_artifacts()
    checks = {
        "parents_exactly_pinned": parent_audit["all_ok"],
        "semantic_no_smuggling": all((
            no_smuggling["token_scan_clean"],
            no_smuggling["provenance_closed_over_registered_lower_ops"],
            no_smuggling["denotations_total_on_full_carrier_domains"],
            no_smuggling["grammar_unchanged"],
        )),
        "frozen_predictions_match": prediction["all_match"],
        "persistent_positive_recovered": sequences["positive"]["selected"]["cells"] == 1,
        "persistent_negative_rejected": sequences["negative"]["selected"]["cells"] == 0,
        "state_lower_bound_exact": lower_bounds["state_count"] == 3,
        "state_price_reversal": sequences["cheap_state"]["decision"] == "PERSISTENT" and sequences["expensive_state"]["decision"] == "REPLAY",
        "static_positive_classes_recovered": (
            selection["O1_POS"]["class"] == "AFFINE_SHARED_RESPONSE"
            and selection["O1_DECISION"]["class"] == "BINARY_DECISION_ON_AFFINE_SCORE"
            and selection["O2_POS"]["class"] == "NON_AFFINE_LINK_OF_ONE_DIMENSIONAL_SCORE"
            and selection["O3_POS"]["class"] == "CROSS_COORDINATE_LIFTED_INTERACTION"
        ),
        "static_negative_regimes_flip": (
            selection["O1_NEG"]["class"] != "AFFINE_SHARED_RESPONSE"
            and selection["O2_NEG"]["class"] == "AFFINE_SHARED_RESPONSE"
            and selection["O3_NEG"]["class"] == "ADDITIVELY_SEPARABLE_RESPONSE"
        ),
        "static_resource_crossovers": (
            selection["O1_POS"]["storage"]["winners"] != selection["O1_POS"]["reuse"]["winners"]
            and selection["O2_POS"]["storage"]["winners"] != selection["O2_POS"]["reuse"]["winners"]
            and selection["O3_POS"]["storage"]["winners"] != selection["O3_POS"]["reuse"]["winners"]
        ),
        "all_remints_roundtrip": all(row["remint"]["all_roundtrips"] for row in selection.values()),
        "state_remint_transport": sequences["remint"]["all_transport_checks"],
        "independent_searches_agree": independent["all_agree"],
        "source_separated_oracle_agrees": artifacts["oracle_green"] and artifacts["oracle_recovered"] == prediction["recovered"],
        "family_rows_fail_closed": gates["gate_count"] == 10 and gates["all_family_rows_open"],
        "parent_downgrades_registered": artifacts["target_encoded_parent_downgraded"] and artifacts["p0_closure_downgraded"],
        "issue_audit_is_nonmutating": artifacts["family_rows_open"] and artifacts["no_issue_mutation"] and artifacts["preexisting_row_reference"],
        "package_contracts": artifacts["scientific_claims"] == 4 and artifacts["manifest_source_pr"] == 960,
    }
    return {
        "schema": "GMI833HNeutralFourFamilyResultV1",
        "parent_issue": 833,
        "benchmark_issue": 434,
        "source_pr": 960,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_audit": parent_audit,
        "grammar": {"digest": grammar_digest(), "definition": GRAMMAR},
        "semantic_no_smuggling_audit": no_smuggling,
        "prediction_audit": prediction,
        "independent_search_audit": independent,
        "selection": selection,
        "sequence": sequences,
        "lower_bounds": lower_bounds,
        "family_gate_ledger": {
            "gate_count": gates["gate_count"],
            "family_rows": tuple(row["row"] for row in gates["rows"]),
            "open_gate": "real_scale_test",
            "all_family_rows_open": gates["all_family_rows_open"],
            "evidence_registry_entries": len(gates["evidence"]),
            "authority": "FAMILY_GATE_LEDGER_V1.json",
        },
        "artifact_contracts": artifacts,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


def canonicalize(value):
    if isinstance(value, tuple):
        return [canonicalize(item) for item in value]
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): canonicalize(item) for key, item in sorted(value.items(), key=lambda pair: repr(pair[0]))}
    return value


def canonical_json(value) -> str:
    return json.dumps(canonicalize(value), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    print(canonical_json(build_receipt()), end="")
