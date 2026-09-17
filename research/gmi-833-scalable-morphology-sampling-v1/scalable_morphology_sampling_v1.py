#!/usr/bin/env python3
"""Exact scalable probability designs over the finite G0 morphology space."""

from __future__ import annotations

from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import importlib.util
import json
from math import comb
from pathlib import Path
import sys
from typing import Callable, Iterable, Sequence


HERE = Path(__file__).resolve().parent
SOURCE_MAIN = "324614bfc95a0f923d6dbaffd0fb2cbbbc4869b0"
FREEZE_COMMIT = "be5b19e50e337c23cd9159d5ceaf664c9205dda6"
SOURCE_ISSUE = 1002
SOURCE_PR = 1003
CLAIM_CEILING = (
    "GMI_833_SCALABLE_LARGE_BUDGET_PROBABILITY_SAMPLING_DESIGN_"
    "AT_REGISTERED_G0_SCOPE"
)
FORBIDDEN_PROMOTIONS = (
    "UNBOUNDED_SAMPLING",
    "UNIQUE_OR_UNBIASED_GRAMMAR",
    "SEMANTIC_UNIFORMITY",
    "PHYSICAL_RANDOMNESS_FROM_FIXED_SEED",
    "MILLION_SCALE_GENERATION_EXECUTED",
    "HUNDRED_MILLION_SCALE_GENERATION_EXECUTED",
    "EQUIVALENT_10E8_EFFECTIVE_COVERAGE",
    "QD_OR_OPEN_ENDED_SEARCH_RESULT",
    "KNOWN_FAMILY_RECOVERY",
    "COMPLETE_GMI",
)


def _load_parent():
    path = HERE.parent / "gmi-833-finite-candidate-space-v1" / "finite_candidate_space_v1.py"
    spec = importlib.util.spec_from_file_location("gmi833_finite_parent_for_sampling", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the pinned finite-candidate parent")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = _load_parent()
StructuralBudget = PARENT.StructuralBudget
Instruction = PARENT.Instruction
CandidateProgram = PARENT.CandidateProgram


def _positive_int(value: object, label: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{label} must be a positive exact integer")
    return value


def _natural(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be an exact natural number")
    return value


@dataclass(frozen=True)
class Stratum:
    index: int
    labels: int
    registers: int
    alphabet_size: int
    size: int
    offset: int

    @property
    def stop(self) -> int:
        return self.offset + self.size


def instruction_alphabet_size(labels: int, registers: int) -> int:
    labels = _positive_int(labels, "labels")
    registers = _positive_int(registers, "registers")
    return 1 + 3 * registers * labels + registers * labels * labels


@lru_cache(maxsize=16)
def strata(budget: StructuralBudget) -> tuple[Stratum, ...]:
    if not isinstance(budget, StructuralBudget):
        raise ValueError("budget must be a StructuralBudget")
    result: list[Stratum] = []
    offset = 0
    for registers in range(1, budget.register_cells + 1):
        for labels in range(1, budget.code_cells + 1):
            alphabet = instruction_alphabet_size(labels, registers)
            size = alphabet**labels
            result.append(
                Stratum(
                    index=len(result),
                    labels=labels,
                    registers=registers,
                    alphabet_size=alphabet,
                    size=size,
                    offset=offset,
                )
            )
            offset += size
    return tuple(result)


def population_size(budget: StructuralBudget) -> int:
    table = strata(budget)
    return table[-1].stop


def instruction_to_digit(instruction: Instruction, labels: int, registers: int) -> int:
    PARENT.validate_instruction(instruction, labels, registers)
    rn = registers * labels
    if instruction.op == "READ":
        return instruction.register * labels + instruction.target0
    if instruction.op == "INC":
        return rn + instruction.register * labels + instruction.target0
    if instruction.op == "DECJZ":
        return (
            2 * rn
            + instruction.register * labels * labels
            + instruction.target0 * labels
            + instruction.target1
        )
    if instruction.op == "EMIT":
        return 2 * rn + registers * labels * labels + instruction.register * labels + instruction.target0
    if instruction.op == "HALT":
        return 3 * rn + registers * labels * labels
    raise AssertionError("validated instruction operation fell through")


def digit_to_instruction(digit: int, labels: int, registers: int) -> Instruction:
    digit = _natural(digit, "digit")
    q = instruction_alphabet_size(labels, registers)
    if digit >= q:
        raise ValueError("instruction digit is outside the registered alphabet")
    rn = registers * labels
    if digit < rn:
        register, target = divmod(digit, labels)
        return Instruction("READ", register, target)
    digit -= rn
    if digit < rn:
        register, target = divmod(digit, labels)
        return Instruction("INC", register, target)
    digit -= rn
    decjz_count = registers * labels * labels
    if digit < decjz_count:
        register, remainder = divmod(digit, labels * labels)
        nonzero, zero = divmod(remainder, labels)
        return Instruction("DECJZ", register, nonzero, zero)
    digit -= decjz_count
    if digit < rn:
        register, target = divmod(digit, labels)
        return Instruction("EMIT", register, target)
    if digit == rn:
        return Instruction("HALT")
    raise AssertionError("instruction digit partition fell through")


def local_rank(program: CandidateProgram) -> int:
    PARENT.validate_program(program)
    labels = len(program.instructions)
    registers = program.register_count
    q = instruction_alphabet_size(labels, registers)
    rank = 0
    for instruction in program.instructions:
        rank = rank * q + instruction_to_digit(instruction, labels, registers)
    return rank


def local_unrank(labels: int, registers: int, rank: int) -> CandidateProgram:
    labels = _positive_int(labels, "labels")
    registers = _positive_int(registers, "registers")
    rank = _natural(rank, "rank")
    q = instruction_alphabet_size(labels, registers)
    size = q**labels
    if rank >= size:
        raise ValueError("local rank is outside the registered stratum")
    digits = [0] * labels
    residual = rank
    for index in range(labels - 1, -1, -1):
        residual, digits[index] = divmod(residual, q)
    if residual != 0:
        raise AssertionError("mixed-radix unrank left a residual")
    program = CandidateProgram(
        register_count=registers,
        instructions=tuple(digit_to_instruction(digit, labels, registers) for digit in digits),
    )
    PARENT.validate_program(program)
    return program


def rank_program(budget: StructuralBudget, program: CandidateProgram) -> int:
    if not isinstance(budget, StructuralBudget):
        raise ValueError("budget must be a StructuralBudget")
    PARENT.validate_program(program)
    labels = len(program.instructions)
    registers = program.register_count
    if labels > budget.code_cells or registers > budget.register_cells:
        raise ValueError("program is outside the declared structural budget")
    index = (registers - 1) * budget.code_cells + (labels - 1)
    stratum = strata(budget)[index]
    rank = stratum.offset + local_rank(program)
    if not stratum.offset <= rank < stratum.stop:
        raise AssertionError("rank escaped its stratum")
    return rank


def unrank_program(budget: StructuralBudget, rank: int) -> CandidateProgram:
    rank = _natural(rank, "rank")
    table = strata(budget)
    total = table[-1].stop
    if rank >= total:
        raise ValueError("global rank is outside the registered population")
    stops = tuple(item.stop for item in table)
    index = bisect_right(stops, rank)
    item = table[index]
    return local_unrank(item.labels, item.registers, rank - item.offset)


class FiniteDrawSource:
    """Finite exact draw transcript used by exhaustive distribution oracles."""

    def __init__(self, values: Iterable[int]):
        self._values = iter(values)

    def uniform_below(self, upper: int) -> int:
        upper = _positive_int(upper, "upper")
        try:
            value = next(self._values)
        except StopIteration as exc:
            raise RuntimeError("entropy transcript exhausted") from exc
        value = _natural(value, "draw")
        if value >= upper:
            raise ValueError("draw transcript value is outside its requested range")
        return value


class CounterEntropy:
    """Deterministic replay adapter; not a claim of physical randomness."""

    def __init__(self, seed: bytes):
        if type(seed) is not bytes or not seed:
            raise ValueError("seed must be nonempty exact bytes")
        self._seed = seed
        self._counter = 0
        self.raw_candidates = 0
        self.rejections = 0

    def _bytes(self, count: int) -> bytes:
        count = _positive_int(count, "byte count")
        output = bytearray()
        while len(output) < count:
            if self._counter >= 2**128:
                raise RuntimeError("counter entropy stream exhausted")
            output.extend(
                sha256(self._seed + self._counter.to_bytes(16, "big")).digest()
            )
            self._counter += 1
        return bytes(output[:count])

    def uniform_below(self, upper: int) -> int:
        upper = _positive_int(upper, "upper")
        bits = (upper - 1).bit_length()
        byte_count = max(1, (bits + 7) // 8)
        mask = (1 << bits) - 1 if bits else 0
        while True:
            self.raw_candidates += 1
            candidate = int.from_bytes(self._bytes(byte_count), "big") & mask
            if candidate < upper:
                return candidate
            self.rejections += 1

    @property
    def blocks_consumed(self) -> int:
        return self._counter


DrawBelow = Callable[[int], int]


def floyd_srswor(population: int, sample: int, draw_below: DrawBelow) -> tuple[int, ...]:
    population = _positive_int(population, "population")
    sample = _positive_int(sample, "sample")
    if sample > population:
        raise ValueError("sample cannot exceed population")
    if not callable(draw_below):
        raise ValueError("draw_below must be callable")
    selected: set[int] = set()
    for upper_value in range(population - sample, population):
        draw = draw_below(upper_value + 1)
        if type(draw) is not int or not 0 <= draw <= upper_value:
            raise ValueError("draw_below violated its exact range contract")
        selected.add(upper_value if draw in selected else draw)
    if len(selected) != sample:
        raise AssertionError("Floyd sampler uniqueness invariant failed")
    return tuple(sorted(selected))


def global_srswor(
    budget: StructuralBudget,
    sample: int,
    draw_below: DrawBelow,
) -> tuple[int, ...]:
    return floyd_srswor(population_size(budget), sample, draw_below)


def global_inclusion_probabilities(population: int, sample: int) -> tuple[Fraction, Fraction]:
    population = _positive_int(population, "population")
    sample = _positive_int(sample, "sample")
    if sample > population:
        raise ValueError("sample cannot exceed population")
    first = Fraction(sample, population)
    second = Fraction(0, 1) if sample == 1 else Fraction(sample * (sample - 1), population * (population - 1))
    return first, second


def global_design_terms(population: int, sample: int) -> tuple[Fraction, Fraction, Fraction]:
    """Return exact first-order, pair, and Horvitz--Thompson terms."""
    first, second = global_inclusion_probabilities(population, sample)
    return first, second, Fraction(population, sample)


def hamilton_positive_allocation(sizes: Sequence[int], sample: int) -> tuple[int, ...]:
    if type(sizes) not in (tuple, list) or not sizes:
        raise ValueError("sizes must be a nonempty finite sequence")
    normalized = tuple(_positive_int(value, "stratum size") for value in sizes)
    sample = _positive_int(sample, "sample")
    population = sum(normalized)
    strata_count = len(normalized)
    if sample < strata_count:
        raise ValueError("positive stratified allocation requires at least one draw per stratum")
    if sample > population:
        raise ValueError("sample cannot exceed population")
    allocation = [1] * strata_count
    remaining = sample - strata_count
    if remaining == 0:
        return tuple(allocation)
    capacities = tuple(size - 1 for size in normalized)
    total_capacity = sum(capacities)
    floor_extras = [(remaining * capacity) // total_capacity for capacity in capacities]
    for index, extra in enumerate(floor_extras):
        allocation[index] += extra
    residual = remaining - sum(floor_extras)
    order = sorted(
        range(strata_count),
        key=lambda index: (-(remaining * capacities[index] % total_capacity), index),
    )
    for index in order[:residual]:
        allocation[index] += 1
    if sum(allocation) != sample:
        raise AssertionError("Hamilton allocation total drift")
    if any(not 1 <= draws <= size for draws, size in zip(allocation, normalized)):
        raise AssertionError("Hamilton allocation violated a stratum capacity")
    return tuple(allocation)


@dataclass(frozen=True)
class StratifiedSample:
    ranks: tuple[int, ...]
    allocation: tuple[int, ...]


def positive_stratified_srswor(
    budget: StructuralBudget,
    sample: int,
    draw_below: DrawBelow,
) -> StratifiedSample:
    table = strata(budget)
    allocation = hamilton_positive_allocation(tuple(item.size for item in table), sample)
    ranks: list[int] = []
    for item, draws in zip(table, allocation):
        ranks.extend(item.offset + local for local in floyd_srswor(item.size, draws, draw_below))
    if len(ranks) != sample or len(set(ranks)) != sample:
        raise AssertionError("stratified sample count or uniqueness drift")
    return StratifiedSample(tuple(ranks), allocation)


def stratum_inclusion_probabilities(size: int, draws: int) -> tuple[Fraction, Fraction, Fraction]:
    size = _positive_int(size, "stratum size")
    draws = _positive_int(draws, "stratum draws")
    if draws > size:
        raise ValueError("stratum draws cannot exceed stratum size")
    first = Fraction(draws, size)
    second = Fraction(0, 1) if draws == 1 else Fraction(draws * (draws - 1), size * (size - 1))
    ht_weight = Fraction(size, draws)
    return first, second, ht_weight


def miss_probability(population: int, qualifying: int, sample: int) -> Fraction:
    population = _positive_int(population, "population")
    qualifying = _natural(qualifying, "qualifying")
    sample = _positive_int(sample, "sample")
    if qualifying > population or sample > population:
        raise ValueError("qualifying and sample must not exceed population")
    if sample > population - qualifying:
        return Fraction(0, 1)
    return Fraction(comb(population - qualifying, sample), comb(population, sample))


def stratified_miss_probability(
    sizes: Sequence[int], qualifying: Sequence[int], allocation: Sequence[int]
) -> Fraction:
    """Exact probability that independent within-stratum SRSWOR misses a predicate."""
    if not (type(sizes) in (tuple, list) and type(qualifying) in (tuple, list) and type(allocation) in (tuple, list)):
        raise ValueError("stratified arguments must be finite tuples or lists")
    if not sizes or len(sizes) != len(qualifying) or len(sizes) != len(allocation):
        raise ValueError("stratified arguments must be nonempty and have equal length")
    probability = Fraction(1, 1)
    for raw_size, raw_qualifying, raw_draws in zip(sizes, qualifying, allocation):
        size = _positive_int(raw_size, "stratum size")
        members = _natural(raw_qualifying, "qualifying stratum members")
        draws = _positive_int(raw_draws, "stratum draws")
        if members > size or draws > size:
            raise ValueError("qualifying members and draws must not exceed stratum size")
        if draws > size - members:
            return Fraction(0, 1)
        probability *= Fraction(comb(size - members, draws), comb(size, draws))
    return probability


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def hostile_input_audit() -> dict[str, bool]:
    """Replay fail-closed boundaries without treating exceptions as scientific evidence."""
    checks: dict[str, bool] = {}

    def rejects(name: str, operation: Callable[[], object]) -> None:
        try:
            operation()
        except (ValueError, RuntimeError):
            checks[name] = True
        else:
            checks[name] = False

    rejects("nonexact_budget", lambda: StructuralBudget(True, 1))
    rejects("zero_budget", lambda: StructuralBudget(0, 1))
    rejects("negative_rank", lambda: unrank_program(StructuralBudget(1, 1), -1))
    rejects("out_of_range_rank", lambda: unrank_program(StructuralBudget(1, 1), population_size(StructuralBudget(1, 1))))
    rejects(
        "malformed_program",
        lambda: rank_program(
            StructuralBudget(1, 1),
            CandidateProgram(1, (Instruction("READ", 2, 0),)),
        ),
    )
    rejects("oversampling", lambda: floyd_srswor(2, 3, lambda upper: 0))
    rejects("underfunded_positive_allocation", lambda: hamilton_positive_allocation((2, 3), 1))
    rejects("exhausted_entropy", lambda: floyd_srswor(3, 1, FiniteDrawSource(()).uniform_below))
    rejects("invalid_draw_contract", lambda: floyd_srswor(3, 1, lambda upper: upper))
    rejects("empty_replay_seed", lambda: CounterEntropy(b""))
    return checks


def exact_floyd_distribution_oracle(population: int = 5, sample: int = 2) -> dict[tuple[int, ...], int]:
    """Exhaust all ideal draw traces independently of the replay adapter."""
    population = _positive_int(population, "population")
    sample = _positive_int(sample, "sample")
    if sample > population:
        raise ValueError("sample cannot exceed population")
    limits = tuple(range(population - sample + 1, population + 1))
    counts: Counter[tuple[int, ...]] = Counter()

    def visit(depth: int, transcript: list[int]) -> None:
        if depth == len(limits):
            chosen: set[int] = set()
            for upper_value, draw in zip(range(population - sample, population), transcript):
                chosen.add(upper_value if draw in chosen else draw)
            counts[tuple(sorted(chosen))] += 1
            return
        for value in range(limits[depth]):
            transcript.append(value)
            visit(depth + 1, transcript)
            transcript.pop()

    visit(0, [])
    return dict(sorted(counts.items()))


def _program_digest(program: CandidateProgram) -> str:
    payload = json.dumps(program.canonical_code(), separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def build_result() -> dict[str, object]:
    budget = StructuralBudget(64, 32)
    total = population_size(budget)
    table = strata(budget)
    probes = (
        ("0", 0),
        ("1", 1),
        ("first_stratum_stop-1", table[0].stop - 1),
        ("floor(M/2)", total // 2),
        ("M-2", total - 2),
        ("M-1", total - 1),
    )
    probe_records = []
    for rank_expression, rank in probes:
        program = unrank_program(budget, rank)
        returned = rank_program(budget, program)
        if returned != rank:
            raise AssertionError("large-budget probe round trip failed")
        probe_records.append(
            {
                "rank_expression": rank_expression,
                "labels": len(program.instructions),
                "registers": program.register_count,
                "program_sha256": _program_digest(program),
            }
        )
    entropy = CounterEntropy(b"gmi-833-f-scalable-sampling-v1-registered-replay")
    sampled = positive_stratified_srswor(budget, 4096, entropy.uniform_below)
    sampled_program_digests = []
    for rank in sampled.ranks:
        program = unrank_program(budget, rank)
        if rank_program(budget, program) != rank:
            raise AssertionError("sampled rank round trip failed")
        sampled_program_digests.append(_program_digest(program))
    rank_payload = "\n".join(str(value) for value in sampled.ranks).encode("ascii")
    program_payload = "\n".join(sampled_program_digests).encode("ascii")
    oracle = exact_floyd_distribution_oracle()
    expected_subsets = comb(5, 2)
    if len(oracle) != expected_subsets or len(set(oracle.values())) != 1:
        raise AssertionError("independent Floyd oracle is not uniform")
    global_first, global_second, global_weight = global_design_terms(total, 4096)
    dominant = max(table, key=lambda item: item.size)
    dominant_draws = sampled.allocation[dominant.index]
    dominant_first, dominant_second, dominant_weight = stratum_inclusion_probabilities(
        dominant.size, dominant_draws
    )
    singleton_miss = miss_probability(total, 1, 4096)
    allocation_histogram = Counter(sampled.allocation)
    hostile_checks = hostile_input_audit()
    if not all(hostile_checks.values()):
        raise AssertionError("one or more hostile inputs did not fail closed")
    result: dict[str, object] = {
        "schema": "GMI833ScalableMorphologySamplingResultV1",
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "source_issue": SOURCE_ISSUE,
        "source_pr": SOURCE_PR,
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "SCALABLE_PROBABILITY_SAMPLING_DESIGN_IMPLEMENTED_AT_REGISTERED_G0_SCOPE",
        "registered_large_budget": {
            "code_cells": budget.code_cells,
            "register_cells": budget.register_cells,
            "strata": len(table),
            "population": str(total),
            "population_decimal_digits": len(str(total)),
            "population_bit_length": total.bit_length(),
            "population_materialized": False,
        },
        "large_budget_probe_round_trips": probe_records,
        "registered_stratified_replay": {
            "sample_size": len(sampled.ranks),
            "unique_ranks": len(set(sampled.ranks)),
            "covered_strata": sum(draws > 0 for draws in sampled.allocation),
            "minimum_stratum_allocation": min(sampled.allocation),
            "maximum_stratum_allocation": max(sampled.allocation),
            "allocation_histogram": {
                str(draws): allocation_histogram[draws]
                for draws in sorted(allocation_histogram)
            },
            "rank_transcript_sha256": sha256(rank_payload).hexdigest(),
            "program_transcript_sha256": sha256(program_payload).hexdigest(),
            "entropy_adapter": "DETERMINISTIC_REPLAY_ONLY_NOT_PHYSICAL_RANDOMNESS",
            "entropy_blocks_consumed": entropy.blocks_consumed,
            "entropy_raw_candidates": entropy.raw_candidates,
            "entropy_rejections": entropy.rejections,
        },
        "ideal_design_probabilities": {
            "global_first_order_exact": _fraction_text(global_first),
            "global_second_order_exact": _fraction_text(global_second),
            "global_ht_weight_exact": _fraction_text(global_weight),
            "stratified_first_order": "m_h/H_h",
            "stratified_second_order": "m_h(m_h-1)/(H_h(H_h-1))",
            "cross_stratum_second_order": "(m_h/H_h)*(m_g/H_g)",
            "stratified_ht_weight": "H_h/m_h",
            "subset_miss": "C(M-A,k)/C(M,k)",
            "stratified_subset_miss": "product_h C(H_h-A_h,m_h)/C(H_h,m_h)",
        },
        "coverage_diagnostics": {
            "tiny_singleton_global_miss_exact": _fraction_text(singleton_miss),
            "tiny_singleton_warning": "A candidate-uniform design can still miss a rare scientific niche.",
            "dominant_stratum": {
                "labels": dominant.labels,
                "registers": dominant.registers,
                "population_members": str(dominant.size),
                "population_fraction_exact": _fraction_text(Fraction(dominant.size, total)),
                "global_expected_sample_count_exact": _fraction_text(Fraction(4096 * dominant.size, total)),
                "positive_stratified_allocation": dominant_draws,
                "positive_stratified_first_order_exact": _fraction_text(dominant_first),
                "positive_stratified_second_order_exact": _fraction_text(dominant_second),
                "positive_stratified_ht_weight_exact": _fraction_text(dominant_weight),
            },
            "all_strata_guaranteed_represented": all(draws >= 1 for draws in sampled.allocation),
            "global_design_guarantees_every_stratum": False,
            "positive_stratification_changes_candidate_inclusion_probabilities": True,
        },
        "small_distribution_oracle": {
            "population": 5,
            "sample": 2,
            "draw_traces": sum(oracle.values()),
            "subsets": len(oracle),
            "traces_per_subset": next(iter(oracle.values())),
        },
        "resource_bounds": {
            "registered_stratum_table_entries": len(table),
            "registered_returned_ranks": len(sampled.ranks),
            "stratum_table_time_and_memory": "O(NR) big integers; bit cost depends on log(M)",
            "rank_time": "O(NR+n) big-integer work with the current cached table construction",
            "unrank_time": "O(NR+n) big-integer work; no O(M) scan",
            "global_floyd_draw_oracle_calls": "exactly k",
            "global_floyd_working_memory": "O(k)",
            "global_floyd_time_with_sorted_output": "expected O(k log k) under ordinary hash-set accounting",
            "positive_stratified_time": "O(NR log(NR)+k log k) including deterministic allocation/output ordering",
            "candidate_materialization": "O(sum sampled label counts)",
            "population_enumeration_required": False,
        },
        "hostile_input_checks": hostile_checks,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "adjacent_issue_833_rows_left_open": [
            "Generate at least 10^6 architecture-neutral candidates.",
            "Scale to at least 10^8 candidates or justify an equivalent effective coverage method.",
        ],
    }
    return result


def canonical_result_bytes() -> bytes:
    return (json.dumps(build_result(), indent=2, sort_keys=True) + "\n").encode("utf-8")


if __name__ == "__main__":
    sys.stdout.buffer.write(canonical_result_bytes())
