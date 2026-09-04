#!/usr/bin/env python3
"""Exact checker for Warranted Parity Learning with distinct proof paths.

The current function is a parity concept. Future warrant depends on optional,
scope-bound mixed equations that are distinct from the revoked primary record.
This validates the registered finite claims; it is not a novelty checker.
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
        selected = (
            row for coefficient, row in zip(coefficients, rows) if coefficient
        )
        if xor_vectors(selected, len(target)) == target:
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

    def active_in(self, scope: int, revoked_ids: frozenset[str]) -> bool:
        return self.record_id not in revoked_ids and (
            self.scope is None or self.scope == scope
        )


@dataclass(frozen=True)
class WarrantedParityWorld:
    theta: Vector
    contexts_per_coordinate: int
    backup_bits: Vector

    def __post_init__(self) -> None:
        if len(self.theta) < 2:
            raise ValueError("distinct proof paths require dimension at least two")
        expected = len(self.theta) * self.contexts_per_coordinate
        if len(self.backup_bits) != expected:
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

    def scope_id(self, coordinate: int, context: int) -> int:
        self.backup_bit(coordinate, context)
        return coordinate * self.contexts_per_coordinate + context

    def bridge_coordinate(self, coordinate: int, context: int) -> int:
        self.backup_bit(coordinate, context)
        others = [index for index in range(self.dimension) if index != coordinate]
        return others[context % len(others)]

    def backup_vector(self, coordinate: int, context: int) -> Vector:
        bridge = self.bridge_coordinate(coordinate, context)
        return xor_vectors(
            (
                standard_basis(self.dimension, coordinate),
                standard_basis(self.dimension, bridge),
            ),
            self.dimension,
        )

    def ledger(self) -> tuple[CertifiedEquation, ...]:
        records: list[CertifiedEquation] = []
        for coordinate in range(self.dimension):
            primary_vector = standard_basis(self.dimension, coordinate)
            records.append(
                CertifiedEquation(
                    f"P:{coordinate}",
                    primary_vector,
                    self.theta[coordinate],
                    None,
                    True,
                )
            )
            for context in range(self.contexts_per_coordinate):
                if self.backup_bit(coordinate, context):
                    backup = self.backup_vector(coordinate, context)
                    records.append(
                        CertifiedEquation(
                            f"B:{coordinate}:{context}",
                            backup,
                            dot(backup, self.theta),
                            self.scope_id(coordinate, context),
                            False,
                        )
                    )
        return tuple(records)

    def surviving_records(
        self, scope: int, revoked_ids: frozenset[str]
    ) -> tuple[CertifiedEquation, ...]:
        return tuple(
            record
            for record in self.ledger()
            if record.active_in(scope, revoked_ids)
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
        raise AssertionError("row-space and nullspace alternatives both failed")
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


def enumerate_worlds(p: int, h: int) -> tuple[WarrantedParityWorld, ...]:
    if p < 2 or h < 0:
        raise ValueError("p must be at least two and h non-negative")
    return tuple(
        WarrantedParityWorld(theta, h, backups)
        for theta in itertools.product((0, 1), repeat=p)
        for backups in itertools.product((0, 1), repeat=p * h)
    )


def current_function_transcript(
    world: WarrantedParityWorld, queries: tuple[Vector, ...]
) -> Vector:
    return tuple(world.current_label(query) for query in queries)


def lifecycle_profile(world: WarrantedParityWorld) -> Vector:
    return world.theta + world.backup_bits


def query_complexity(p: int, h: int) -> dict[str, int]:
    if p < 0 or h < 0:
        raise ValueError("parameters must be non-negative")
    return {
        "current_function_queries": p,
        "additional_warrant_queries": p * h,
        "lifecycle_queries": p * (h + 1),
    }


def run_exact_calibration() -> dict[str, object]:
    p, h = 3, 2
    worlds = enumerate_worlds(p, h)
    if len(worlds) != 512:
        raise AssertionError("world-count drift")

    basis_queries = tuple(standard_basis(p, index) for index in range(p))
    all_queries = tuple(itertools.product((0, 1), repeat=p))
    theta_groups: dict[Vector, list[WarrantedParityWorld]] = {}
    profiles = set()
    challenge_checks = positive_checks = negative_checks = 0
    false_retain_controls = false_retract_controls = 0

    for world in worlds:
        theta_groups.setdefault(world.theta, []).append(world)
        profiles.add(lifecycle_profile(world))
        if current_function_transcript(world, basis_queries) != world.theta:
            raise AssertionError("basis queries did not identify theta")

        for coordinate in range(p):
            query = standard_basis(p, coordinate)
            for context in range(h):
                scope = world.scope_id(coordinate, context)
                records = world.surviving_records(
                    scope, frozenset({f"P:{coordinate}"})
                )
                decision = warranted_prediction(records, query)
                challenge_checks += 1
                if world.backup_bit(coordinate, context):
                    positive_checks += 1
                    false_retract_controls += 1
                    if decision["status"] != "WARRANTED":
                        raise AssertionError("distinct backup was not retained")
                    if decision["label"] != world.theta[coordinate]:
                        raise AssertionError("warranted label drift")
                    coefficients = tuple(
                        decision["positive_certificate_coefficients"]
                    )
                    if not verify_positive_certificate(
                        records, query, int(decision["label"]), coefficients
                    ):
                        raise AssertionError("positive certificate failed")
                    backup_id = f"B:{coordinate}:{context}"
                    bridge_id = f"P:{world.bridge_coordinate(coordinate, context)}"
                    used = set(decision["positive_certificate_record_ids"])
                    if backup_id not in used or bridge_id not in used:
                        raise AssertionError("certificate skipped the bridge proof path")
                    backup_record = next(
                        record for record in records if record.record_id == backup_id
                    )
                    if backup_record.vector == query:
                        raise AssertionError("backup duplicated the primary equation")
                else:
                    negative_checks += 1
                    false_retain_controls += 1
                    if decision["status"] != "ABSTAIN":
                        raise AssertionError("unsupported coordinate was retained")
                    if not verify_disagreement_witness(
                        records,
                        query,
                        tuple(decision["negative_disagreement_witness"]),
                    ):
                        raise AssertionError("negative disagreement witness failed")

    if len(profiles) != len(worlds):
        raise AssertionError("lifecycle profiles are not injective")
    for group in theta_groups.values():
        if len(group) != 64:
            raise AssertionError("warrant worlds per function drift")
        transcripts = {
            current_function_transcript(world, all_queries) for world in group
        }
        if len(transcripts) != 1:
            raise AssertionError("full current oracle leaked warrant")
    if not (positive_checks and negative_checks):
        raise AssertionError("both warrant outcomes were not exercised")
    if not (false_retain_controls and false_retract_controls):
        raise AssertionError("degenerate-policy controls did not fire")

    vectors = tuple(itertools.product((0, 1), repeat=p))
    linear_checks = warranted_cases = abstain_cases = 0
    matrix_count = 0
    for row_count in range(4):
        for rows in itertools.product(vectors, repeat=row_count):
            matrix_count += 1
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
                    linear_checks += 1
                    if in_span:
                        warranted_cases += 1
                        if result["status"] != "WARRANTED":
                            raise AssertionError("row-space iff warrant failed")
                        if not verify_positive_certificate(
                            records,
                            tuple(query),
                            int(result["label"]),
                            tuple(result["positive_certificate_coefficients"]),
                        ):
                            raise AssertionError("linear positive certificate failed")
                    else:
                        abstain_cases += 1
                        if result["status"] != "ABSTAIN":
                            raise AssertionError("non-row-space query was warranted")
                        if not verify_disagreement_witness(
                            records,
                            tuple(query),
                            tuple(result["negative_disagreement_witness"]),
                        ):
                            raise AssertionError("linear negative witness failed")

    resources = query_complexity(p, h)
    if resources != {
        "current_function_queries": 3,
        "additional_warrant_queries": 6,
        "lifecycle_queries": 9,
    }:
        raise AssertionError("query-complexity drift")
    if linear_checks != 37440:
        raise AssertionError("linear theorem denominator drift")

    return {
        "schema": "orion.ocm.warranted-parity-distinct-paths.exact-results.v2",
        "terminal": "PASS_NATURAL_CLASS_DISTINCT_PROOF_PATHS",
        "family": {
            "dimension_p": p,
            "contexts_h": h,
            "current_functions": 2**p,
            "warrant_profiles_per_function": 2 ** (p * h),
            "lifecycle_concepts": len(worlds),
        },
        "query_complexity": resources,
        "current_function_blindness": {
            "function_fibers": len(theta_groups),
            "worlds_per_function": 64,
            "full_current_oracle_leaks_warrant": False,
        },
        "distinct_proof_paths": {
            "challenge_checks": challenge_checks,
            "positive_bridge_certificates": positive_checks,
            "negative_disagreement_certificates": negative_checks,
            "backup_vectors_equal_to_primary": 0,
            "false_retain_controls": false_retain_controls,
            "false_retract_controls": false_retract_controls,
        },
        "linear_warrant_theorem": {
            "binary_matrices_zero_to_three_rows": matrix_count,
            "matrix_theta_query_checks": linear_checks,
            "warranted_cases": warranted_cases,
            "abstain_cases": abstain_cases,
        },
        "authority": {
            "natural_class": True,
            "distinct_proof_paths": True,
            "exact_query_complexity": True,
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
        print("PASS Warranted Parity V2: distinct scoped proof paths verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
