#!/usr/bin/env python3
"""Source-separated exhaustive small-budget oracle for the 116M census."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import argparse
import json
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent


class OracleError(RuntimeError):
    pass


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def alphabet_size(labels: int) -> int:
    if type(labels) is not int or labels < 1:
        raise OracleError("labels must be a positive exact integer")
    return 1 + 3 * labels + labels * labels


def decode_instruction(digit: int, labels: int) -> tuple[str, int, int]:
    if 0 <= digit < labels:
        return ("READ", digit, -1)
    if labels <= digit < 2 * labels:
        return ("INC", digit - labels, -1)
    if 2 * labels <= digit < 2 * labels + labels * labels:
        offset = digit - 2 * labels
        return ("DECJZ", offset // labels, offset % labels)
    if 2 * labels + labels * labels <= digit < 3 * labels + labels * labels:
        return ("EMIT", digit - (2 * labels + labels * labels), -1)
    if digit == 3 * labels + labels * labels:
        return ("HALT", -1, -1)
    raise OracleError("instruction digit outside independent alphabet")


def decode_program(rank: int, labels: int) -> tuple[tuple[str, int, int], ...]:
    q = alphabet_size(labels)
    if type(rank) is not int or not 0 <= rank < q**labels:
        raise OracleError("rank outside independent stratum")
    digits = [0] * labels
    residual = rank
    for index in range(labels - 1, -1, -1):
        residual, digits[index] = divmod(residual, q)
    if residual:
        raise OracleError("independent decoder retained residual")
    program = tuple(decode_instruction(digit, labels) for digit in digits)
    rebuilt = 0
    for digit in digits:
        rebuilt = rebuilt * q + digit
    if rebuilt != rank:
        raise OracleError("independent rank round trip failed")
    return program


def observe(program: tuple[tuple[str, int, int], ...], word: tuple[int, ...]) -> tuple[int, tuple[int, ...]]:
    register = 0
    pc = 0
    input_position = 0
    output: list[int] = []
    for _ in range(6):
        op, first, second = program[pc]
        if op == "HALT":
            return (0, tuple(output))
        if op == "READ":
            if input_position == len(word):
                return (1, tuple(output))
            register = word[input_position]
            input_position += 1
            pc = first
        elif op == "INC":
            register += 1
            pc = first
        elif op == "DECJZ":
            if register:
                register -= 1
                pc = first
            else:
                pc = second
        elif op == "EMIT":
            output.append(register)
            pc = first
        else:  # pragma: no cover
            raise OracleError("independent instruction became unknown")
    return (2, tuple(output))


def pack_observation(observation: tuple[int, tuple[int, ...]]) -> int:
    terminal, output = observation
    if len(output) > 6 or any(not 0 <= value <= 6 for value in output):
        raise OracleError("observation outside frozen packing domain")
    packed = terminal * 7 + len(output)
    for index in range(6):
        packed = packed * 8 + (output[index] + 1 if index < len(output) else 0)
    return packed


def semantic_token(program: tuple[tuple[str, int, int], ...]) -> str:
    packed = [pack_observation(observe(program, word)) for word in ((), (0,), (1,))]
    return ":".join(map(str, packed))


def census_stratum(labels: int) -> dict[str, object]:
    q = alphabet_size(labels)
    population = q**labels
    histogram: Counter[str] = Counter()
    rank_sum = 0
    rank_square_sum = 0
    for rank in range(population):
        histogram[semantic_token(decode_program(rank, labels))] += 1
        rank_sum += rank
        rank_square_sum += rank * rank
    if sum(histogram.values()) != population:
        raise OracleError("independent histogram lost candidates")
    raw = canonical_bytes(dict(sorted(histogram.items())))
    return {
        "labels": labels,
        "alphabet_size": q,
        "candidate_count": population,
        "rank_sum": rank_sum,
        "rank_square_sum": rank_square_sum,
        "semantic_class_count": len(histogram),
        "semantic_histogram_sha256": sha256(raw).hexdigest(),
        "histogram": dict(sorted(histogram.items())),
    }


def verify_result(result_path: Path, output_path: Path) -> dict[str, object]:
    result = json.loads(result_path.read_bytes())
    if result.get("verdict") != "EXACT_116570467_CANDIDATE_CENSUS_COMPLETE_AT_REGISTERED_FINITE_SCOPE":
        raise OracleError("primary result is not at its positive terminal")
    primary_by_labels = {int(row["labels"]): row for row in result["strata"]}
    rows: list[dict[str, object]] = []
    for labels in range(1, 5):
        oracle = census_stratum(labels)
        primary = primary_by_labels.get(labels)
        if primary is None:
            raise OracleError("primary result omitted an oracle stratum")
        compared_fields = (
            "alphabet_size",
            "candidate_count",
            "rank_sum",
            "rank_square_sum",
            "semantic_class_count",
            "semantic_histogram_sha256",
        )
        agreement = all(primary.get(field) == oracle[field] for field in compared_fields)
        if not agreement:
            raise OracleError(f"independent disagreement at labels={labels}")
        rows.append({key: value for key, value in oracle.items() if key != "histogram"} | {"agreement": True})

    total = int(result["execution"]["candidate_count"])
    if total != sum((1 + 3 * labels + labels * labels) ** labels for labels in range(1, 6)):
        raise OracleError("full-scope closed-form total disagrees")
    for labels, row in primary_by_labels.items():
        population = (1 + 3 * labels + labels * labels) ** labels
        if int(row["candidate_count"]) != population:
            raise OracleError("full-scope stratum count disagrees")
        expected_sum = population * (population - 1) // 2
        expected_squares = population * (population - 1) * (2 * population - 1) // 6
        if int(row["rank_sum"]) != expected_sum or int(row["rank_square_sum"]) != expected_squares:
            raise OracleError("full-scope rank moments disagree")

    semantic = result["semantic_coverage"]
    effective = Fraction(total * total, int(semantic["sum_squared_multiplicities"]))
    if semantic["inverse_simpson_effective_semantic_count_exact"] != f"{effective.numerator}/{effective.denominator}":
        raise OracleError("effective semantic count arithmetic disagrees")
    receipt = {
        "schema": "GMI833HundredMillionIndependentCheckV1",
        "source_issue": 1008,
        "source_pr": 1009,
        "primary_result_sha256": sha256(result_path.read_bytes()).hexdigest(),
        "source_separated": True,
        "imports_primary_implementation": False,
        "complete_small_budget_rows": rows,
        "full_scope_structural_checks": {
            "all_five_closed_form_stratum_counts": True,
            "all_five_closed_form_rank_sums": True,
            "all_five_closed_form_rank_square_sums": True,
            "candidate_total": total,
        },
        "effective_count_arithmetic_check": True,
        "verdict": "INDEPENDENT_SMALL_SCOPE_SEMANTIC_AND_FULL_SCOPE_STRUCTURAL_CHECK_GREEN",
    }
    output_path.write_bytes(json.dumps(receipt, indent=2, sort_keys=True).encode("ascii") + b"\n")
    return receipt


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    receipt = verify_result(args.result, args.output)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
