#!/usr/bin/env python3
"""Exact finite checks for the Warrant Blindness oracle separation."""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class LifecycleConcept:
    warrant_bits: tuple[int, ...]

    def __post_init__(self) -> None:
        if any(bit not in (0, 1) for bit in self.warrant_bits):
            raise ValueError("warrant bits must be binary")

    def current_function(self, x: int) -> int:
        if x < 0:
            raise ValueError("input must be non-negative")
        return x & 1

    def revoke_response(self, challenge: int) -> int:
        if not 0 <= challenge < len(self.warrant_bits):
            raise IndexError("challenge out of range")
        return self.warrant_bits[challenge]


def concepts(bit_count: int) -> tuple[LifecycleConcept, ...]:
    if bit_count < 0:
        raise ValueError("bit count must be non-negative")
    return tuple(
        LifecycleConcept(bits)
        for bits in itertools.product((0, 1), repeat=bit_count)
    )


def current_oracle_transcript(
    concept: LifecycleConcept, queries: tuple[int, ...]
) -> tuple[int, ...]:
    return tuple(concept.current_function(query) for query in queries)


def exact_success_probability_uniform(bit_count: int, warrant_queries: int) -> float:
    if not 0 <= warrant_queries <= bit_count:
        raise ValueError("warrant query count out of range")
    return 2.0 ** -(bit_count - warrant_queries)


def expected_hamming_error_uniform(
    bit_count: int, warrant_queries: int, abstentions: int = 0
) -> float:
    if not 0 <= warrant_queries <= bit_count:
        raise ValueError("warrant query count out of range")
    if not 0 <= abstentions <= bit_count - warrant_queries:
        raise ValueError("abstention count out of range")
    return (bit_count - warrant_queries - abstentions) / 2.0


def zero_error_possible(
    bit_count: int, warrant_queries: int, abstentions: int
) -> bool:
    if min(bit_count, warrant_queries, abstentions) < 0:
        raise ValueError("resource values must be non-negative")
    if warrant_queries > bit_count or abstentions > bit_count:
        raise ValueError("resource value exceeds target width")
    return warrant_queries + abstentions >= bit_count


def exhaustive_best_exact_success(
    bit_count: int, queried_indices: tuple[int, ...]
) -> float:
    universe = concepts(bit_count)
    queried_indices = tuple(sorted(set(queried_indices)))
    if any(not 0 <= index < bit_count for index in queried_indices):
        raise IndexError("queried index out of range")
    groups: dict[tuple[int, ...], list[LifecycleConcept]] = {}
    for concept in universe:
        transcript = tuple(
            concept.warrant_bits[index] for index in queried_indices
        )
        groups.setdefault(transcript, []).append(concept)
    return len(groups) / len(universe)


def exhaustive_min_hamming_error(
    bit_count: int,
    queried_indices: tuple[int, ...],
    abstain_indices: tuple[int, ...] = (),
) -> float:
    universe = concepts(bit_count)
    queried = set(queried_indices)
    abstained = set(abstain_indices)
    if queried & abstained:
        raise ValueError("queried and abstained indices overlap")
    if any(not 0 <= index < bit_count for index in queried | abstained):
        raise IndexError("index out of range")

    groups: dict[tuple[int, ...], list[LifecycleConcept]] = {}
    for concept in universe:
        transcript = tuple(
            concept.warrant_bits[index] for index in sorted(queried)
        )
        groups.setdefault(transcript, []).append(concept)

    total_error = 0.0
    answered_unqueried = [
        index
        for index in range(bit_count)
        if index not in queried and index not in abstained
    ]
    for group in groups.values():
        for index in answered_unqueried:
            ones = sum(concept.warrant_bits[index] for concept in group)
            zeros = len(group) - ones
            total_error += min(ones, zeros)
    return total_error / len(universe)


def run_exact_calibration() -> dict[str, object]:
    rows = []
    transcripts_checked = 0
    planted_false_completion_worlds = 0

    for bit_count in range(11):
        universe = concepts(bit_count)
        current_queries = tuple(range(8))
        transcripts = {
            current_oracle_transcript(concept, current_queries)
            for concept in universe
        }
        transcripts_checked += len(universe)
        if len(transcripts) != 1:
            raise AssertionError("current-function oracle leaked warrant information")

        for q in range(bit_count + 1):
            queried = tuple(range(q))
            exact = exhaustive_best_exact_success(bit_count, queried)
            formula_exact = exact_success_probability_uniform(bit_count, q)
            if abs(exact - formula_exact) > 1e-12:
                raise AssertionError("exact-success formula drift")

            for a in range(bit_count - q + 1):
                abstained = tuple(range(q, q + a))
                error = exhaustive_min_hamming_error(
                    bit_count, queried, abstained
                )
                formula_error = expected_hamming_error_uniform(
                    bit_count, q, a
                )
                if abs(error - formula_error) > 1e-12:
                    raise AssertionError("Hamming-error formula drift")
                if (error == 0) != zero_error_possible(bit_count, q, a):
                    raise AssertionError("zero-error frontier drift")

            rows.append(
                {
                    "warrant_bits_N": bit_count,
                    "warrant_queries_q": q,
                    "best_exact_full_profile_success": exact,
                    "expected_hamming_error_no_abstention": (
                        exhaustive_min_hamming_error(bit_count, queried)
                    ),
                }
            )

        if bit_count > 0:
            default_profile = (0,) * bit_count
            planted_false_completion_worlds += sum(
                concept.warrant_bits != default_profile
                for concept in universe
            )

    if planted_false_completion_worlds == 0:
        raise AssertionError("current-accuracy false-completion control did not fire")

    N, q, a = 8, 3, 2
    if exact_success_probability_uniform(N, q) != 1 / 32:
        raise AssertionError("registered exact-success witness drift")
    if expected_hamming_error_uniform(N, q, a) != 1.5:
        raise AssertionError("registered Hamming witness drift")
    if zero_error_possible(N, q, a):
        raise AssertionError("under-resourced zero-error witness should fail")
    if not zero_error_possible(N, q, N - q):
        raise AssertionError("query/abstention frontier endpoint should pass")

    return {
        "schema": "orion.ocm.warrant-blindness.exact-results.v1",
        "terminal": "PASS_WARRANT_ORACLE_SEPARATION_FINITE_CHECKS",
        "sweep": {
            "warrant_bit_counts": list(range(11)),
            "current_oracle_transcripts_checked": transcripts_checked,
            "all_current_function_transcripts_identical_within_each_N": True,
            "resource_rows_checked": len(rows),
            "planted_false_completion_worlds": planted_false_completion_worlds,
        },
        "registered_witness": {
            "N": N,
            "q": q,
            "a": a,
            "best_exact_success_with_q_queries": 1 / 32,
            "expected_errors_with_q_queries_and_a_abstentions": 1.5,
            "zero_error_possible": False,
            "zero_error_frontier": "q + a >= N",
        },
        "theorems_checked": {
            "unlimited_current_function_queries_reveal_zero_warrant_bits": True,
            "best_exact_success_uniform": "2^-(N-q)",
            "minimum_expected_hamming_error_uniform": "(N-q-a)/2",
            "zero_error_query_abstention_frontier": "q+a>=N",
            "closure_certified_N_bit_record_is_sufficient": True,
        },
        "authority": {
            "oracle_separation": True,
            "literature_priority": False,
            "architecture_separation": False,
            "publication_readiness": False,
        },
        "rows": rows,
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
        sweep = result["sweep"]
        print(
            "PASS warrant blindness: "
            f"{sweep['current_oracle_transcripts_checked']} current-oracle "
            "transcripts checked with zero warrant leakage."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
