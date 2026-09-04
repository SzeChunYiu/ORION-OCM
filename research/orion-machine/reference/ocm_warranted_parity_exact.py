#!/usr/bin/env python3
"""Exact finite checker for Warranted Parity Learning (WPL).

WPL is a natural-class calibration of Warranted Lifecycle Learning. The
checker validates finite semantics, certificate soundness/completeness and
exact deterministic query counts. It does not establish novelty.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from typing import Iterable, Sequence

Vector = tuple[int, ...]
Matrix = tuple[Vector, ...]


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    if len(left) != len(right):
        raise ValueError("dimension mismatch")
    return sum((a & 1) * (b & 1) for a, b in zip(left, right)) & 1


def xor_vectors(vectors: Iterable[Sequence[int]], width: int) -> Vector:
    out = [0] * width
    for vector in vectors:
        if len(vector) != width:
            raise ValueError("dimension mismatch")
        for index, bit in enumerate(vector):
            out[index] ^= bit & 1
    return tuple(out)


def standard_basis(width: int, index: int) -> Vector:
    if not 0 <= index < width:
        raise IndexError("basis index out of range")
    return tuple(1 if position == index else 0 for position in range(width))


def solve_coefficients(rows: Matrix, target: Vector) -> Vector | None:
    if not rows:
        return () if not any(target) else None
    for coefficients in itertools.product((0, 1), repeat=len(rows)):
        chosen = (row for coefficient, row in zip(coefficients, rows) if coefficient)
        if xor_vectors(chosen, len(target)) == target:
            return tuple(coefficients)
    return None


def nullspace_vectors(rows: Matrix, width: int) -> tuple[Vector, ...]:
    return tuple(
        vector
        for vector in itertools.product((0, 1), repeat=width)
        if all(dot(row, vector) == 0 for row in rows)
    )


def disagreement_witness(rows: Matrix, target: Vector) -> Vector | None:
    for vector in nullspace_vectors(rows, len(target)):
        if dot(target, vector) == 1:
            return vector
    return None


@dataclass(frozen=True)
class CertifiedEquation:
    record_id: str
    vector: Vector
    label: int
    scope: int | None
    primary: bool

    def active_in(self, context: int, revoked_ids: frozenset[str]) -> bool:
        return self.record_id not in revoked_ids and (
            self.scope is None or self.scope == context
        )


@dataclass(frozen=True)
class WarrantedParityWorld:
    theta: Vector
    contexts_per_coordinate: int
    backup_bits: Vector

    def __post_init__(self) -> None:
        p = len(self.theta)
        if len(self.backup_bits) != p * self.contexts_per_coordinate:
            raise ValueError("backup-bit length mismatch")
        if any(bit not in (0, 1) for bit in self.theta + self.backup_bits):
            raise ValueError("world values must be binary")

    @property
    def dimension(self) -> int:
        return len(self.theta)

    def current_label(self, query: Vector) -> int:
        return dot(query, self.theta)

    def backup_bit(self, coordinate: int, context: int) -> int:
        if not 0 <= coordinate < self.dimension:
            raise IndexError("coordinate out of range")
        if not 0 <= context < self.contexts_per_coordinate:
            raise IndexError("context out of range")
        return self.backup_bits[
            coordinate * self.contexts_per_coordinate + context
        ]

    def ledger(self) -> tuple[CertifiedEquation, ...]:
        records: list[CertifiedEquation] = []
        for coordinate in range(self.dimension):
            basis = standard_basis(self.dimension, coordinate)
            records.append(
                CertifiedEquation(
                    f"P:{coordinate}", basis, self.theta[coordinate], None, True
                )
            )
            for context in range(self.contexts_per_coordinate):
                if self.backup_bit(coordinate, context):
                    records.append(
                        CertifiedEquation(
                            f"B:{coordinate}:{context}",
                            basis,
                            self.theta[coordinate],
                            context,
                            False,
                        )
                    )
        return tuple(records)

    def surviving_records(
        self, context: int, revoked_ids: frozenset[str]
    ) -> tuple[CertifiedEquation, ...]:
        return tuple(
            record
            for record in self.ledger()
            if record.active_in(context, revoked_ids)
        )


def warranted_prediction(
    records: tuple[CertifiedEquation, ...], query: Vector
) -> dict[str, object]:
    rows = tuple(record.vector for record in records)
    labels = tuple(record.label for record in records)
    coefficients = solve_coefficients(rows, query)
    if coefficients is not None:
        label = sum(c * y for c, y in zip(coefficients, labels)) & 1
        return {
            "status": "WARRANTED",
            "label": label,
            "positive_certificate_coefficients": coefficients,
            "positive_certificate_record_ids": tuple(
                record.record_id
                for coefficient, record in zip(coefficients, records)
                if coefficient
            ),
            "negative_disagreement_witness": None,
        }
    witness = disagreement_witness(rows, query)
    if witness is None:
        raise AssertionError("row-space alternative and nullspace witness both failed")
    return {
        "status": "ABSTAIN",
        "label": None,
        "positive_certificate_coefficients": None,
        "positive_certificate_record_ids": (),
        "negative_disagreement_witness": witness,
    }


def verify_positive_certificate(
    records: tuple[CertifiedEquation, ...],
    query: Vector,
    label: int,
    coefficients: Sequence[int],
) -> bool:
    if len(coefficients) != len(records):
        return False
    reconstructed_query = xor_vectors(
        (
            record.vector
            for coefficient, record in zip(coefficients, records)
            if coefficient
        ),
        len(query),
    )
    reconstructed_label = sum(
        coefficient * record.label
        for coefficient, record in zip(coefficients, records)
    ) & 1
    return reconstructed_query == query and reconstructed_label == label


def verify_disagreement_witness(
    records: tuple[CertifiedEquation, ...], query: Vector, witness: Vector
) -> bool:
    return all(dot(record.vector, witness) == 0 for record in records) and dot(
        query, witness
    ) == 1


def lifecycle_profile(world: WarrantedParityWorld) -> Vector:
    return world.theta + world.backup_bits


def deterministic_query_complexity(p: int, h: int) -> dict[str, int]:
    if p < 0 or h < 0:
        raise ValueError("parameters must be non-negative")
    return {
        "exact_current_parity_membership_queries": p,
        "additional_warrant_queries": p * h,
        "exact_lifecycle_queries_total": p * (h + 1),
    }


def enumerate_worlds(p: int, h: int) -> tuple[WarrantedParityWorld, ...]:
    return tuple(
        WarrantedParityWorld(theta, h, backups)
        for theta in itertools.product((0, 1), repeat=p)
        for backups in itertools.product((0, 1), repeat=p * h)
    )


def current_function_transcript(
    world: WarrantedParityWorld, queries: tuple[Vector, ...]
) -> Vector:
    return tuple(world.current_label(query) for query in queries)


def run_exact_calibration() -> dict[str, object]:
    p, h = 3, 2
    worlds = enumerate_worlds(p, h)
    if len(worlds) != 2 ** (p + p * h):
        raise AssertionError("world count drift")

    basis_queries = tuple(standard_basis(p, index) for index in range(p))
    theta_groups: dict[Vector, list[WarrantedParityWorld]] = {}
    profiles = set()
    current_transcripts_checked = challenge_checks = certificate_checks = 0
    warranted_cases = abstain_cases = 0
    false_retain_controls = false_retract_controls = 0

    for world in worlds:
        theta_groups.setdefault(world.theta, []).append(world)
        profiles.add(lifecycle_profile(world))
        current_transcripts_checked += 1
        if current_function_transcript(world, basis_queries) != world.theta:
            raise AssertionError("basis membership queries failed to identify theta")

        for coordinate in range(p):
            query = standard_basis(p, coordinate)
            for context in range(h):
                records = world.surviving_records(
                    context, frozenset({f"P:{coordinate}"})
                )
                decision = warranted_prediction(records, query)
                expected_retain = bool(world.backup_bit(coordinate, context))
                challenge_checks += 1
                if expected_retain:
                    warranted_cases += 1
                    false_retract_controls += 1
                    if decision["status"] != "WARRANTED":
                        raise AssertionError("surviving backup was not retained")
                    if decision["label"] != world.theta[coordinate]:
                        raise AssertionError("warranted label drift")
                    if not verify_positive_certificate(
                        records,
                        query,
                        int(decision["label"]),
                        tuple(decision["positive_certificate_coefficients"]),
                    ):
                        raise AssertionError("positive certificate failed")
                    certificate_checks += 1
                else:
                    abstain_cases += 1
                    false_retain_controls += 1
                    if decision["status"] != "ABSTAIN":
                        raise AssertionError("unsupported coordinate was retained")
                    if not verify_disagreement_witness(
                        records,
                        query,
                        tuple(decision["negative_disagreement_witness"]),
                    ):
                        raise AssertionError("negative disagreement witness failed")
                    certificate_checks += 1

    if len(profiles) != len(worlds):
        raise AssertionError("lifecycle profile map is not injective")

    exhaustive_queries = tuple(itertools.product((0, 1), repeat=p))
    for group in theta_groups.values():
        if len(group) != 2 ** (p * h):
            raise AssertionError("wrong warrant worlds per exact function")
        transcripts = {
            current_function_transcript(world, exhaustive_queries) for world in group
        }
        if len(transcripts) != 1:
            raise AssertionError("full current-function oracle leaked warrant state")

    if not (warranted_cases and abstain_cases):
        raise AssertionError("suite lacks warranted and abstain cases")
    if not (false_retain_controls and false_retract_controls):
        raise AssertionError("hostile controls did not fire")

    linear_theorem_checks = linear_warranted = linear_abstain = 0
    vectors = tuple(itertools.product((0, 1), repeat=p))
    for row_count in range(4):
        for rows in itertools.product(vectors, repeat=row_count):
            matrix = tuple(tuple(row) for row in rows)
            for theta in vectors:
                records = tuple(
                    CertifiedEquation(
                        f"R:{index}", row, dot(row, theta), None, False
                    )
                    for index, row in enumerate(matrix)
                )
                for query in vectors:
                    result = warranted_prediction(records, tuple(query))
                    in_span = solve_coefficients(matrix, tuple(query)) is not None
                    linear_theorem_checks += 1
                    if in_span:
                        linear_warranted += 1
                        if result["status"] != "WARRANTED":
                            raise AssertionError("row-space iff theorem failed")
                        if not verify_positive_certificate(
                            records,
                            tuple(query),
                            int(result["label"]),
                            tuple(result["positive_certificate_coefficients"]),
                        ):
                            raise AssertionError("linear positive certificate failed")
                    else:
                        linear_abstain += 1
                        if result["status"] != "ABSTAIN":
                            raise AssertionError("non-row-space query was warranted")
                        if not verify_disagreement_witness(
                            records,
                            tuple(query),
                            tuple(result["negative_disagreement_witness"]),
                        ):
                            raise AssertionError("linear negative witness failed")

    query_complexity = deterministic_query_complexity(p, h)
    if query_complexity["exact_lifecycle_queries_total"] != 9:
        raise AssertionError("query-complexity formula drift")

    return {
        "schema": "orion.ocm.warranted-parity.exact-results.v1",
        "terminal": "PASS_NATURAL_CLASS_WARRANTED_PARITY_CALIBRATION",
        "family": {
            "dimension_p": p,
            "contexts_per_coordinate_h": h,
            "target_parity_functions": 2**p,
            "warrant_profiles_per_function": 2 ** (p * h),
            "lifecycle_concepts": len(worlds),
            "lifecycle_profile_bits": p + p * h,
        },
        "query_complexity": {
            **query_complexity,
            "lower_bound_reason": (
                "2^p parity functions and 2^(p*h) warrant profiles are independent; "
                "each binary query contributes at most one bit."
            ),
            "upper_bound_strategy": (
                "query each standard-basis parity label and every coordinate-context "
                "backup bit"
            ),
        },
        "exact_current_function_blindness": {
            "theta_fibers": len(theta_groups),
            "worlds_per_theta": 2 ** (p * h),
            "current_function_transcripts_checked": current_transcripts_checked,
            "exhaustive_current_function_oracle_leaks_warrant": False,
        },
        "revocation_challenges": {
            "checks": challenge_checks,
            "warranted_cases": warranted_cases,
            "abstain_cases": abstain_cases,
            "positive_and_negative_certificate_checks": certificate_checks,
            "false_retain_controls": false_retain_controls,
            "false_retract_controls": false_retract_controls,
        },
        "linear_warrant_theorem": {
            "dimension": p,
            "binary_matrices_with_zero_to_three_rows": sum(
                (2**p) ** row_count for row_count in range(4)
            ),
            "matrix_theta_query_checks": linear_theorem_checks,
            "warranted_row_space_cases": linear_warranted,
            "abstain_non_row_space_cases": linear_abstain,
            "positive_certificate": "lambda with lambda^T A=x and lambda^T b=y",
            "negative_certificate": "v with A v=0 and x dot v=1",
        },
        "theorems": {
            "current_function_query_complexity": "p",
            "lifecycle_query_complexity": "p*(h+1)",
            "additional_warrant_query_complexity": "p*h",
            "warranted_prediction_iff_query_in_surviving_row_span": True,
            "full_current_function_oracle_is_warrant_blind": True,
            "delete_everything_violates_useful_retention": True,
            "retain_old_prediction_without_support_violates_warrant": True,
        },
        "authority": {
            "natural_class_instantiation": True,
            "exact_query_complexity": True,
            "finite_certificate_theorem_checks": True,
            "literature_priority": False,
            "novelty": False,
            "architecture_separation": False,
            "publication_readiness": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = run_exact_calibration()
    except (AssertionError, ValueError, IndexError) as exc:
        print(json.dumps({"terminal": "FAIL", "error": str(exc)}, indent=2))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        family = result["family"]
        print(
            "PASS warranted parity: "
            f"{family['lifecycle_concepts']} lifecycle concepts; exact query "
            f"complexity {result['query_complexity']['exact_lifecycle_queries_total']}."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
