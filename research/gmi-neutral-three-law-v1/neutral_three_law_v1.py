#!/usr/bin/env python3
"""Exact bounded neutral learning-law rediscovery for #768.

The searcher is target-family blind.  Target formulas appear only in the independent oracle
constructor; search receives opaque exact truth tables and one frozen grammar/cost protocol.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import hashlib
import json
from typing import Iterable

VALUES = (Fraction(-1), Fraction(0), Fraction(1))
VARIABLES = ("w", "x", "y", "r")
POINTS = tuple(product(VALUES, repeat=4))
OPERATORS = ("add", "sub", "mul", "half")
COST_CAP = 6
TIE_RULE = "minimum_cost_then_lexicographic_syntax"
CLAIM_CEILING = "NEUTRAL_THREE_LAW_REDISCOVERY_AT_REGISTERED_FINITE_GRAMMAR_SCOPE"


class ProtocolError(ValueError):
    pass


@dataclass(frozen=True)
class Protocol:
    variables: tuple[str, ...]
    constants: tuple[int, ...]
    operators: tuple[str, ...]
    cost_cap: int
    tie_rule: str

    def canonical(self) -> dict:
        return {
            "variables": list(self.variables),
            "constants": list(self.constants),
            "operators": list(self.operators),
            "cost_cap": self.cost_cap,
            "tie_rule": self.tie_rule,
            "universe_values": [-1, 0, 1],
            "universe_arity": 4,
        }


FROZEN_PROTOCOL = Protocol(
    variables=VARIABLES,
    constants=(-1, 0, 1),
    operators=OPERATORS,
    cost_cap=COST_CAP,
    tie_rule=TIE_RULE,
)
FROZEN_PROTOCOL_JSON = json.dumps(FROZEN_PROTOCOL.canonical(), sort_keys=True, separators=(",", ":"))
FROZEN_PROTOCOL_SHA256 = hashlib.sha256(FROZEN_PROTOCOL_JSON.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SemanticRecord:
    cost: int
    syntax: str
    table: tuple[Fraction, ...]


def activate_protocol(candidate: Protocol | None = None) -> str:
    """Return the frozen fingerprint or fail closed on any confirmatory-protocol mutation."""
    candidate = FROZEN_PROTOCOL if candidate is None else candidate
    payload = json.dumps(candidate.canonical(), sort_keys=True, separators=(",", ":"))
    fingerprint = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    if fingerprint != FROZEN_PROTOCOL_SHA256:
        raise ProtocolError("FROZEN_PROTOCOL_MUTATION")
    return fingerprint


def _leaf_tables(variables: Iterable[str], constants: Iterable[int]) -> dict[str, tuple[Fraction, ...]]:
    enabled = set(variables)
    tables: dict[str, tuple[Fraction, ...]] = {}
    for index, name in enumerate(VARIABLES):
        if name in enabled:
            tables[name] = tuple(point[index] for point in POINTS)
    for constant in constants:
        tables[str(constant)] = tuple(Fraction(constant) for _ in POINTS)
    return tables


def _binary(op: str, left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    if op == "add":
        return tuple(a + b for a, b in zip(left, right))
    if op == "sub":
        return tuple(a - b for a, b in zip(left, right))
    if op == "mul":
        return tuple(a * b for a, b in zip(left, right))
    raise ValueError(f"unsupported binary operator: {op}")


def enumerate_semantic_quotient(protocol: Protocol) -> tuple[dict[tuple[Fraction, ...], SemanticRecord], dict[int, dict[tuple[Fraction, ...], str]]]:
    """Exhaust every semantic table generated at cost <= cap, one canonical min-cost syntax each."""
    if protocol.cost_cap < 1:
        raise ValueError("cost cap must be positive")
    unknown = set(protocol.operators) - {"add", "sub", "mul", "half"}
    if unknown:
        raise ValueError(f"unsupported operators: {sorted(unknown)}")
    if not set(protocol.variables).issubset(VARIABLES):
        raise ValueError("unknown variable")

    layers: dict[int, dict[tuple[Fraction, ...], str]] = {
        cost: {} for cost in range(1, protocol.cost_cap + 1)
    }
    best: dict[tuple[Fraction, ...], SemanticRecord] = {}

    for syntax, table in sorted(_leaf_tables(protocol.variables, protocol.constants).items()):
        previous = layers[1].get(table)
        if previous is None or syntax < previous:
            layers[1][table] = syntax
    for table, syntax in layers[1].items():
        best[table] = SemanticRecord(1, syntax, table)

    binary_ops = tuple(op for op in ("add", "sub", "mul") if op in protocol.operators)
    has_half = "half" in protocol.operators

    for cost in range(2, protocol.cost_cap + 1):
        candidates: dict[tuple[Fraction, ...], str] = {}

        def offer(table: tuple[Fraction, ...], syntax: str) -> None:
            if table in best:
                return
            previous = candidates.get(table)
            if previous is None or syntax < previous:
                candidates[table] = syntax

        if has_half:
            for child_table, child_syntax in layers[cost - 1].items():
                offer(tuple(value / 2 for value in child_table), f"half({child_syntax})")

        for left_cost in range(1, cost - 1):
            right_cost = cost - 1 - left_cost
            if right_cost < 1:
                continue
            for left_table, left_syntax in layers[left_cost].items():
                for right_table, right_syntax in layers[right_cost].items():
                    for op in binary_ops:
                        offer(
                            _binary(op, left_table, right_table),
                            f"{op}({left_syntax},{right_syntax})",
                        )

        layers[cost] = dict(sorted(candidates.items(), key=lambda item: item[1]))
        for table, syntax in layers[cost].items():
            best[table] = SemanticRecord(cost, syntax, table)

    return best, layers


def frozen_target_tables() -> dict[str, tuple[Fraction, ...]]:
    """Independent oracle construction; search itself never receives formulas."""
    output: dict[str, tuple[Fraction, ...]] = {}

    def target_a(point: tuple[Fraction, Fraction, Fraction, Fraction]) -> Fraction:
        w, _x, y, _r = point
        return (w + y) / 2

    def target_b(point: tuple[Fraction, Fraction, Fraction, Fraction]) -> Fraction:
        w, x, y, _r = point
        return w + (x * y) / 2

    def target_c(point: tuple[Fraction, Fraction, Fraction, Fraction]) -> Fraction:
        w, x, _y, r = point
        return w + (r * x) / 2

    for opaque_id, fn in (
        ("OPAQUE_A", target_a),
        ("OPAQUE_B", target_b),
        ("OPAQUE_C", target_c),
    ):
        output[opaque_id] = tuple(fn(point) for point in POINTS)
    return output


def recover_opaque_targets(
    opaque_tables: dict[str, tuple[Fraction, ...]],
    protocol: Protocol | None = None,
) -> dict[str, SemanticRecord]:
    """Family-blind exact recovery: IDs are used only as output keys, never as search branches."""
    protocol = FROZEN_PROTOCOL if protocol is None else protocol
    activate_protocol(protocol)
    quotient, _layers = enumerate_semantic_quotient(protocol)
    recovered: dict[str, SemanticRecord] = {}
    for opaque_id in sorted(opaque_tables):
        table = opaque_tables[opaque_id]
        record = quotient.get(table)
        if record is None:
            raise LookupError(f"NO_EXACT_MATCH:{opaque_id}")
        recovered[opaque_id] = record
    return recovered


def dependency_signature(table: tuple[Fraction, ...]) -> tuple[tuple[str, ...], dict[str, dict[str, object]]]:
    """Return exact finite semantic dependency signature and first witness per required variable."""
    point_to_index = {point: index for index, point in enumerate(POINTS)}
    required: list[str] = []
    detail: dict[str, dict[str, object]] = {}

    for variable_index, variable in enumerate(VARIABLES):
        witness = None
        all_invariant = True
        for point in POINTS:
            for replacement in VALUES:
                if replacement == point[variable_index]:
                    continue
                other = list(point)
                other[variable_index] = replacement
                other_point = tuple(other)
                left = table[point_to_index[point]]
                right = table[point_to_index[other_point]]
                if left != right:
                    all_invariant = False
                    if witness is None:
                        witness = {
                            "left": [int(v) for v in point],
                            "right": [int(v) for v in other_point],
                            "left_output": format_fraction(left),
                            "right_output": format_fraction(right),
                        }
        if not all_invariant:
            required.append(variable)
            detail[variable] = {"required": True, "witness": witness}
        else:
            detail[variable] = {"required": False, "all_matched_pairs_invariant": True}

    return tuple(required), detail


def format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def table_sha256(table: tuple[Fraction, ...]) -> str:
    payload = "|".join(format_fraction(value) for value in table)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def no_half_ablation() -> dict[str, object]:
    protocol = Protocol(
        variables=VARIABLES,
        constants=(-1, 0, 1),
        operators=("add", "sub", "mul"),
        cost_cap=COST_CAP,
        tie_rule=TIE_RULE,
    )
    quotient, layers = enumerate_semantic_quotient(protocol)
    targets = frozen_target_tables()
    return {
        "quotient_size": len(quotient),
        "layer_sizes": [len(layers[cost]) for cost in range(1, COST_CAP + 1)],
        "target_recovered": {opaque_id: table in quotient for opaque_id, table in targets.items()},
        "all_quotient_values_integral": all(
            value.denominator == 1 for table in quotient for value in table
        ),
        "each_target_has_half_integer": {
            opaque_id: any(value.denominator == 2 for value in table)
            for opaque_id, table in targets.items()
        },
    }


def required_variable_ablations() -> dict[str, dict[str, object]]:
    targets = frozen_target_tables()
    result: dict[str, dict[str, object]] = {}
    for opaque_id, table in targets.items():
        signature, _detail = dependency_signature(table)
        per_target: dict[str, object] = {}
        for variable in signature:
            protocol = Protocol(
                variables=tuple(name for name in VARIABLES if name != variable),
                constants=(-1, 0, 1),
                operators=OPERATORS,
                cost_cap=COST_CAP,
                tie_rule=TIE_RULE,
            )
            quotient, layers = enumerate_semantic_quotient(protocol)
            per_target[variable] = {
                "recovered": table in quotient,
                "quotient_size": len(quotient),
                "layer_sizes": [len(layers[cost]) for cost in range(1, COST_CAP + 1)],
            }
        result[opaque_id] = per_target
    return result


def equivalent_syntax_control() -> dict[str, object]:
    leaves = _leaf_tables(VARIABLES, (-1, 0, 1))
    left = _binary("add", leaves["w"], leaves["y"])
    right = _binary("add", leaves["y"], leaves["w"])
    quotient, _layers = enumerate_semantic_quotient(FROZEN_PROTOCOL)
    return {
        "add_w_y_equals_add_y_w": left == right,
        "semantic_table_present_once": left in quotient,
        "canonical_representative": quotient[left].syntax if left in quotient else None,
    }


def perturbed_target_control(recovered: dict[str, SemanticRecord]) -> dict[str, object]:
    targets = frozen_target_tables()
    original = targets["OPAQUE_A"]
    perturbed = list(original)
    perturbed[0] = perturbed[0] + 1
    recovered_table = recovered["OPAQUE_A"].table
    return {
        "row_index": 0,
        "original_output": format_fraction(original[0]),
        "perturbed_output": format_fraction(perturbed[0]),
        "previous_representative_still_exact": recovered_table == tuple(perturbed),
    }


def build_receipt() -> dict[str, object]:
    fingerprint = activate_protocol()
    targets = frozen_target_tables()
    quotient, layers = enumerate_semantic_quotient(FROZEN_PROTOCOL)
    recovered = recover_opaque_targets(targets)

    expected_costs = {"OPAQUE_A": 4, "OPAQUE_B": 6, "OPAQUE_C": 6}
    target_rows: dict[str, object] = {}
    for opaque_id in sorted(targets):
        record = recovered[opaque_id]
        signature, detail = dependency_signature(targets[opaque_id])
        target_rows[opaque_id] = {
            "target_sha256": table_sha256(targets[opaque_id]),
            "minimum_cost": record.cost,
            "expected_minimum_cost": expected_costs[opaque_id],
            "minimum_cost_matches_freeze": record.cost == expected_costs[opaque_id],
            "representative": record.syntax,
            "exact_match": record.table == targets[opaque_id],
            "dependency_signature": list(signature),
            "dependency_detail": detail,
        }

    no_half = no_half_ablation()
    variable_ablations = required_variable_ablations()
    variable_ablations_all_fail = all(
        not row["recovered"]
        for target in variable_ablations.values()
        for row in target.values()
    )

    receipt = {
        "schema": "GMI_NEUTRAL_THREE_LAW_RECEIPT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "protocol_sha256": fingerprint,
        "universe_points": len(POINTS),
        "cost_cap": COST_CAP,
        "quotient_size": len(quotient),
        "layer_sizes": [len(layers[cost]) for cost in range(1, COST_CAP + 1)],
        "targets": target_rows,
        "signatures_pairwise_distinct": len({tuple(row["dependency_signature"]) for row in target_rows.values()}) == 3,
        "required_variable_ablations": variable_ablations,
        "required_variable_ablations_all_fail": variable_ablations_all_fail,
        "no_half_ablation": no_half,
        "equivalent_syntax_control": equivalent_syntax_control(),
        "perturbed_target_control": perturbed_target_control(recovered),
        "terminal": CLAIM_CEILING,
    }
    return receipt


def main() -> None:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
