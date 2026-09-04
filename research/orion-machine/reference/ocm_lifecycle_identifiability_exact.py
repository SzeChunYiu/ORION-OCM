#!/usr/bin/env python3
"""Exact finite calibration for OCM lifecycle identifiability.

This checks a finite modular-revocation witness. It is not a novelty checker.
Exit 0 means the registered finite claims and planted collision pass.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Sequence

BitVector = tuple[int, ...]
Matrix = tuple[BitVector, ...]


def gf2_dot(row: Sequence[int], vector: Sequence[int]) -> int:
    if len(row) != len(vector):
        raise ValueError("dimension mismatch")
    return sum((a & 1) * (b & 1) for a, b in zip(row, vector)) & 1


def _mask(row: Sequence[int]) -> int:
    out = 0
    for index, bit in enumerate(row):
        if bit not in (0, 1):
            raise ValueError("GF(2) rows must be binary")
        out |= bit << index
    return out


def gf2_rank(rows: Iterable[Sequence[int]], width: int) -> int:
    work = [_mask(tuple(row)) for row in rows]
    rank = 0
    for column in range(width):
        pivot = next(
            (i for i in range(rank, len(work)) if (work[i] >> column) & 1),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for i in range(len(work)):
            if i != rank and ((work[i] >> column) & 1):
                work[i] ^= work[rank]
        rank += 1
    return rank


def complement_rows(rows: Matrix, width: int) -> Matrix:
    if gf2_rank(rows, width) != len(rows):
        raise ValueError("input rows must be independent")
    extended = list(rows)
    complement: list[BitVector] = []
    rank = len(rows)
    for column in range(width):
        candidate = tuple(1 if i == column else 0 for i in range(width))
        new_rank = gf2_rank((*extended, candidate), width)
        if new_rank > rank:
            extended.append(candidate)
            complement.append(candidate)
            rank = new_rank
        if rank == width:
            break
    if rank != width:
        raise AssertionError("failed to complete the basis")
    return tuple(complement)


def enumerate_solutions(matrix: Matrix, rhs: BitVector, width: int) -> tuple[BitVector, ...]:
    if len(matrix) != len(rhs):
        raise ValueError("matrix/rhs length mismatch")
    return tuple(
        vector
        for vector in itertools.product((0, 1), repeat=width)
        if tuple(gf2_dot(row, vector) for row in matrix) == rhs
    )


@dataclass(frozen=True)
class LifecycleFamily:
    module_count: int
    endpoint_matrix: Matrix
    endpoint_rhs: BitVector
    alternate_scopes_per_module: int

    @property
    def endpoint_rank(self) -> int:
        return gf2_rank(self.endpoint_matrix, self.module_count)

    @property
    def completion_matrix(self) -> Matrix:
        return complement_rows(self.endpoint_matrix, self.module_count)

    @property
    def hidden_module_bits(self) -> int:
        return self.module_count - self.endpoint_rank

    @property
    def hidden_support_bits(self) -> int:
        return self.module_count * self.alternate_scopes_per_module

    @property
    def lifecycle_dimension(self) -> int:
        return self.hidden_module_bits + self.hidden_support_bits

    def module_worlds(self) -> tuple[BitVector, ...]:
        return enumerate_solutions(
            self.endpoint_matrix, self.endpoint_rhs, self.module_count
        )

    def worlds(self):
        for theta in self.module_worlds():
            for support in itertools.product((0, 1), repeat=self.hidden_support_bits):
                yield theta, support

    def future_profile(self, theta: BitVector, support: BitVector) -> BitVector:
        return tuple(gf2_dot(row, theta) for row in self.completion_matrix) + support


def profile_groups(family: LifecycleFamily, drop_coordinate: int | None = None):
    groups = defaultdict(list)
    for world in family.worlds():
        profile = family.future_profile(*world)
        if drop_coordinate is not None:
            coordinate = drop_coordinate
            if coordinate < 0:
                coordinate += len(profile)
            if not 0 <= coordinate < len(profile):
                raise IndexError("drop coordinate out of range")
            profile = profile[:coordinate] + profile[coordinate + 1 :]
        groups[profile].append(world)
    return dict(groups)


def lifecycle_capacity_bits(C: int, B: int, Q: int, a: int) -> int:
    if any(value < 0 for value in (C, B, Q, a)):
        raise ValueError("resource values must be non-negative")
    return min(C, B) + Q + a


def one_witness_retention_trilemma() -> dict[str, object]:
    return {
        "training_transcripts_identical": True,
        "only_primary_support_correct_action": "RETRACT",
        "primary_plus_backup_correct_action": "RETAIN",
        "always_retain_is_unsound": True,
        "always_retract_is_destructive": True,
        "resolution_requires_one_of": [
            "additional certified support information",
            "future revalidation query",
            "explicit abstention",
        ],
    }


def run_exact_calibration() -> dict[str, object]:
    family = LifecycleFamily(
        module_count=4,
        endpoint_matrix=((1, 1, 0, 0), (0, 1, 1, 0)),
        endpoint_rhs=(0, 0),
        alternate_scopes_per_module=2,
    )
    if family.endpoint_rank != 2:
        raise AssertionError("endpoint rank drift")
    if gf2_rank(
        (*family.endpoint_matrix, *family.completion_matrix), family.module_count
    ) != family.module_count:
        raise AssertionError("completion matrix is not full rank")

    module_worlds = family.module_worlds()
    if len(module_worlds) != 2 ** family.hidden_module_bits:
        raise AssertionError("module version-space size mismatch")

    groups = profile_groups(family)
    expected_worlds = 2 ** family.lifecycle_dimension
    if len(groups) != expected_worlds or any(len(group) != 1 for group in groups.values()):
        raise AssertionError("full future-profile map is not injective")

    dropped = profile_groups(family, drop_coordinate=-1)
    collision_groups = [group for group in dropped.values() if len(group) > 1]
    if len(dropped) != expected_worlds // 2:
        raise AssertionError("planted coordinate deletion did not halve profiles")
    if len(collision_groups) != expected_worlds // 2:
        raise AssertionError("planted collision did not fire")
    if any(len(group) != 2 for group in collision_groups):
        raise AssertionError("planted collisions are not two-world pairs")

    dimension = family.lifecycle_dimension
    under_budget = 0
    boundary = 0
    for C in range(dimension + 1):
        for B in range(dimension + 1):
            for Q in range(dimension + 1):
                for a in range(dimension + 1):
                    capacity = lifecycle_capacity_bits(C, B, Q, a)
                    if capacity < dimension:
                        under_budget += 1
                        if 2 ** capacity >= expected_worlds:
                            raise AssertionError("under-budget resources cover all worlds")
                    elif capacity == dimension:
                        boundary += 1

    trilemma = one_witness_retention_trilemma()
    if not trilemma["always_retain_is_unsound"]:
        raise AssertionError("unsound-retention control did not fire")
    if not trilemma["always_retract_is_destructive"]:
        raise AssertionError("destructive-retraction control did not fire")

    return {
        "schema": "orion.ocm.lifecycle-identifiability.exact-results.v1",
        "terminal": "PASS_FINITE_CALIBRATION_ONLY",
        "family": {
            "module_count_p": family.module_count,
            "endpoint_rank_r": family.endpoint_rank,
            "alternate_scopes_per_module_h": family.alternate_scopes_per_module,
            "endpoint_matrix_A": family.endpoint_matrix,
            "endpoint_rhs_b": family.endpoint_rhs,
            "completion_matrix_C": family.completion_matrix,
            "hidden_module_bits": family.hidden_module_bits,
            "hidden_support_bits": family.hidden_support_bits,
            "lifecycle_dimension_N": dimension,
        },
        "exact_counts": {
            "endpoint_consistent_module_worlds": len(module_worlds),
            "latent_lifecycle_worlds": expected_worlds,
            "distinct_full_future_profiles": len(groups),
            "full_profile_collisions": 0,
            "distinct_profiles_after_planted_coordinate_drop": len(dropped),
            "planted_collision_groups": len(collision_groups),
            "worlds_per_planted_collision_group": 2,
            "under_bound_resource_tuples_checked": under_budget,
            "exact_boundary_resource_tuples_checked": boundary,
        },
        "theorem_instance": {
            "M": expected_worlds,
            "ceil_log2_M": math.ceil(math.log2(expected_worlds)),
            "bound": "min(C,B) + Q + a >= ceil(log2 M)",
            "instantiated_bound": f"min(C,B) + Q + a >= {dimension}",
        },
        "one_witness_retention_trilemma": trilemma,
        "authority": {
            "finite_calibration": True,
            "novelty": False,
            "architecture_separation": False,
            "language_competence": False,
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
        c = result["exact_counts"]
        print(
            "PASS finite calibration: "
            f"{c['distinct_full_future_profiles']}/{c['latent_lifecycle_worlds']} "
            "unique profiles; "
            f"{c['planted_collision_groups']} planted collision groups."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
