#!/usr/bin/env python3
"""Independent artifact checker for the frozen one-million-candidate run.

This module intentionally does not import ``million_candidate_execution_v1`` or
the rank/unrank implementation from PR #1003.  It re-derives the mixed-radix
codec, the counter-based replay stream, and the protected G0 semantics from the
frozen protocol.  Agreement therefore provides an implementation-independent
check rather than a second call through the system under test.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha1, sha256
import json
import math
from pathlib import Path
import sys
from typing import Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "FROZEN_PROTOCOL_V1.json"
REGISTERED_PROTOCOL_SHA256 = "779cb22a0572aa5be9f1d9fca1e0dd4424ec220d45485080ab0462dddd8b27db"
GENESIS_CHAIN_SHA256 = "0" * 64
CHECKER_SCHEMA = "GMI833MillionCandidateIndependentCheckV1"


class VerificationError(ValueError):
    """Raised when a frozen contract or run artifact fails closed."""


def _exact_natural(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise VerificationError(f"{label} must be an exact natural number")
    return value


def _exact_positive(value: object, label: str) -> int:
    value = _exact_natural(value, label)
    if value == 0:
        raise VerificationError(f"{label} must be positive")
    return value


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or any(type(key) is not str for key in value):
        raise VerificationError(f"{label} must be a string-keyed JSON object")
    return value


def _count_mapping(value: object, label: str) -> Mapping[str, int]:
    mapping = _mapping(value, label)
    for key, count in mapping.items():
        _exact_natural(count, f"{label}[{key!r}]")
    return mapping  # type: ignore[return-value]


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_hex(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return sha1(header + payload).hexdigest()


def load_registered_protocol(path: Path = PROTOCOL_PATH) -> dict[str, object]:
    raw = path.read_bytes()
    if sha256_hex(raw) != REGISTERED_PROTOCOL_SHA256:
        raise VerificationError("frozen protocol byte hash drift")
    try:
        protocol = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError("frozen protocol is not valid UTF-8 JSON") from exc
    if not isinstance(protocol, dict):
        raise VerificationError("frozen protocol root must be an object")
    expected_scalars = {
        "schema": "GMI833MillionCandidateExecutionProtocolV1",
        "parent_issue": 833,
        "source_issue": 1006,
        "source_pr": None,
        "registration_source_main": "73309593ef7340c3f616b59bf73d2c9598bc9435",
        "target_row": "Generate at least 10^6 architecture-neutral candidates.",
        "grammar": "G0-fin-v1",
        "sample_design": "EXACT_GLOBAL_SRSWOR_FLOYD_VIA_PR_1003",
        "sample_size": 1_000_000,
        "replay_seed_utf8": "gmi-833-f-million-candidate-execution-v1-registered-replay",
        "chunk_size": 10_000,
        "chunk_count": 100,
        "rank_transcript_format": "SORTED_NEWLINE_DELIMITED_DECIMAL_UTF8",
        "receipt_schema": "GMI833MillionCandidateExecutionResultV1",
        "chunk_receipt_schema": "GMI833MillionCandidateChunkReceiptV1",
        "checkpoint_schema": "GMI833MillionCandidateCheckpointV1",
        "claim_ceiling": "GMI_833_ONE_MILLION_DISTINCT_G0_CANDIDATES_GENERATED_AT_REGISTERED_FINITE_SCOPE",
        "outcome_status_at_registration": "NOT_RUN",
    }
    for key, expected in expected_scalars.items():
        if protocol.get(key) != expected:
            raise VerificationError(f"frozen protocol field {key!r} drift")
    if protocol.get("budget") != {"code_cells": 8, "register_cells": 4}:
        raise VerificationError("registered budget drift")
    if protocol.get("semantic_interface") != {
        "input_words": [[], [0], [1]],
        "step_cap": 6,
    }:
        raise VerificationError("registered semantic interface drift")
    if protocol.get("semantic_discovery_checkpoints") != [1000, 10000, 100000, 1000000]:
        raise VerificationError("registered discovery checkpoints drift")
    if protocol["sample_size"] != protocol["chunk_size"] * protocol["chunk_count"]:
        raise VerificationError("sample/chunk arithmetic is inconsistent")
    dependency = _mapping(protocol.get("generator_dependency"), "generator dependency")
    if dependency != {
        "pull_request": 1003,
        "exact_head": "05d13723b519d9de94f15b142cca0827d3725d6f",
        "module": "research/gmi-833-scalable-morphology-sampling-v1/scalable_morphology_sampling_v1.py",
    }:
        raise VerificationError("registered generator dependency drift")
    return protocol


@dataclass(frozen=True)
class IndependentStratum:
    labels: int
    registers: int
    alphabet_size: int
    size: int
    offset: int

    @property
    def stop(self) -> int:
        return self.offset + self.size


InstructionCode = tuple[str, int, int, int]
ProgramCode = tuple[int, tuple[InstructionCode, ...]]


def instruction_alphabet_size(labels: int, registers: int) -> int:
    labels = _exact_positive(labels, "labels")
    registers = _exact_positive(registers, "registers")
    return 1 + 3 * registers * labels + registers * labels * labels


def independent_strata(code_cells: int, register_cells: int) -> tuple[IndependentStratum, ...]:
    code_cells = _exact_positive(code_cells, "code cells")
    register_cells = _exact_positive(register_cells, "register cells")
    result: list[IndependentStratum] = []
    offset = 0
    for registers in range(1, register_cells + 1):
        for labels in range(1, code_cells + 1):
            alphabet = instruction_alphabet_size(labels, registers)
            size = alphabet**labels
            result.append(IndependentStratum(labels, registers, alphabet, size, offset))
            offset += size
    return tuple(result)


def independent_population_size(code_cells: int, register_cells: int) -> int:
    table = independent_strata(code_cells, register_cells)
    return table[-1].stop


def independent_digit_decode(digit: int, labels: int, registers: int) -> InstructionCode:
    digit = _exact_natural(digit, "instruction digit")
    alphabet = instruction_alphabet_size(labels, registers)
    if digit >= alphabet:
        raise VerificationError("instruction digit outside registered alphabet")
    rectangular = registers * labels
    if digit < rectangular:
        register, target = divmod(digit, labels)
        return ("READ", register, target, -1)
    digit -= rectangular
    if digit < rectangular:
        register, target = divmod(digit, labels)
        return ("INC", register, target, -1)
    digit -= rectangular
    branching = registers * labels * labels
    if digit < branching:
        register, residual = divmod(digit, labels * labels)
        nonzero_target, zero_target = divmod(residual, labels)
        return ("DECJZ", register, nonzero_target, zero_target)
    digit -= branching
    if digit < rectangular:
        register, target = divmod(digit, labels)
        return ("EMIT", register, target, -1)
    if digit == rectangular:
        return ("HALT", -1, -1, -1)
    raise AssertionError("independent digit partition fell through")


def independent_digit_encode(code: InstructionCode, labels: int, registers: int) -> int:
    if type(code) is not tuple or len(code) != 4:
        raise VerificationError("instruction code must be a four-tuple")
    op, register, target0, target1 = code
    rectangular = registers * labels
    if op == "HALT":
        if (register, target0, target1) != (-1, -1, -1):
            raise VerificationError("HALT carries operands")
        return 3 * rectangular + registers * labels * labels
    if type(register) is not int or not 0 <= register < registers:
        raise VerificationError("instruction register outside carrier")
    if type(target0) is not int or not 0 <= target0 < labels:
        raise VerificationError("instruction target outside carrier")
    if op in {"READ", "INC", "EMIT"}:
        if target1 != -1:
            raise VerificationError("single-target instruction carries second target")
        base = {"READ": 0, "INC": rectangular, "EMIT": 2 * rectangular + registers * labels * labels}[op]
        return base + register * labels + target0
    if op == "DECJZ":
        if type(target1) is not int or not 0 <= target1 < labels:
            raise VerificationError("DECJZ zero target outside carrier")
        return 2 * rectangular + register * labels * labels + target0 * labels + target1
    raise VerificationError("unknown instruction operation")


def independent_unrank(
    code_cells: int, register_cells: int, rank: int
) -> ProgramCode:
    rank = _exact_natural(rank, "global rank")
    table = independent_strata(code_cells, register_cells)
    if rank >= table[-1].stop:
        raise VerificationError("global rank outside registered population")
    item = next(stratum for stratum in table if rank < stratum.stop)
    local = rank - item.offset
    digits = [0] * item.labels
    for index in range(item.labels - 1, -1, -1):
        local, digits[index] = divmod(local, item.alphabet_size)
    if local:
        raise AssertionError("independent unrank left a residual")
    return (
        item.registers,
        tuple(independent_digit_decode(value, item.labels, item.registers) for value in digits),
    )


def independent_rank(code_cells: int, register_cells: int, program: ProgramCode) -> int:
    if type(program) is not tuple or len(program) != 2:
        raise VerificationError("program code must be a pair")
    registers, instructions = program
    registers = _exact_positive(registers, "program registers")
    if type(instructions) is not tuple or not instructions:
        raise VerificationError("program instruction table must be a nonempty tuple")
    labels = len(instructions)
    if labels > code_cells or registers > register_cells:
        raise VerificationError("program outside registered budget")
    alphabet = instruction_alphabet_size(labels, registers)
    local = 0
    for instruction in instructions:
        local = local * alphabet + independent_digit_encode(instruction, labels, registers)
    item = independent_strata(code_cells, register_cells)[(registers - 1) * code_cells + labels - 1]
    rank = item.offset + local
    if rank >= item.stop:
        raise AssertionError("independent rank escaped its stratum")
    return rank


def program_jsonable(program: ProgramCode) -> list[object]:
    return [program[0], [list(instruction) for instruction in program[1]]]


def canonical_candidate_bytes(program: ProgramCode) -> bytes:
    return canonical_json_bytes(program_jsonable(program))


def candidate_transcript_digest(programs: Iterable[ProgramCode]) -> str:
    digest = sha256()
    for program in programs:
        payload = canonical_candidate_bytes(program)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def independent_observation(
    program: ProgramCode, input_word: Sequence[int], step_cap: int
) -> tuple[str, tuple[int, ...]]:
    registers_count, instructions = program
    if type(input_word) not in (list, tuple) or any(type(value) is not int or value < 0 for value in input_word):
        raise VerificationError("input word must contain exact natural numbers")
    step_cap = _exact_positive(step_cap, "step cap")
    registers = [0] * registers_count
    input_position = 0
    output: list[int] = []
    pc = 0
    steps = 0
    while True:
        if steps >= step_cap:
            return ("STEP_LIMIT", tuple(output))
        op, register, target0, target1 = instructions[pc]
        steps += 1
        if op == "HALT":
            return ("HALTED", tuple(output))
        if op == "READ":
            if input_position >= len(input_word):
                return ("BLOCKED_INPUT", tuple(output))
            registers[register] = input_word[input_position]
            input_position += 1
            pc = target0
        elif op == "INC":
            registers[register] += 1
            pc = target0
        elif op == "DECJZ":
            if registers[register] > 0:
                registers[register] -= 1
                pc = target0
            else:
                pc = target1
        elif op == "EMIT":
            output.append(registers[register])
            pc = target0
        else:  # pragma: no cover - the decoder cannot emit this
            raise AssertionError("independent decoder emitted an unknown operation")


def independent_semantic_key(
    program: ProgramCode, input_words: Sequence[Sequence[int]], step_cap: int
) -> str:
    observations = [
        [status, list(output)]
        for status, output in (
            independent_observation(program, word, step_cap) for word in input_words
        )
    ]
    return canonical_json_bytes(observations).decode("ascii")


class IndependentCounterEntropy:
    """Independent reconstruction of the registered deterministic replay adapter."""

    def __init__(self, seed: bytes):
        if type(seed) is not bytes or not seed:
            raise VerificationError("replay seed must be nonempty exact bytes")
        self.seed = seed
        self.counter = 0
        self.raw_candidates = 0
        self.rejections = 0

    def _block(self) -> bytes:
        if self.counter >= 2**128:
            raise VerificationError("replay counter exhausted")
        block = sha256(self.seed + self.counter.to_bytes(16, "big")).digest()
        self.counter += 1
        return block

    def uniform_below(self, upper: int) -> int:
        upper = _exact_positive(upper, "uniform upper bound")
        bits = (upper - 1).bit_length()
        count = max(1, (bits + 7) // 8)
        mask = (1 << bits) - 1 if bits else 0
        while True:
            self.raw_candidates += 1
            payload = bytearray()
            while len(payload) < count:
                payload.extend(self._block())
            candidate = int.from_bytes(payload[:count], "big") & mask
            if candidate < upper:
                return candidate
            self.rejections += 1


def independent_floyd_sample(population: int, sample_size: int, seed: bytes) -> tuple[tuple[int, ...], IndependentCounterEntropy]:
    population = _exact_positive(population, "population")
    sample_size = _exact_positive(sample_size, "sample size")
    if sample_size > population:
        raise VerificationError("sample exceeds population")
    entropy = IndependentCounterEntropy(seed)
    selected: set[int] = set()
    for upper in range(population - sample_size, population):
        draw = entropy.uniform_below(upper + 1)
        selected.add(upper if draw in selected else draw)
    if len(selected) != sample_size:
        raise AssertionError("independent Floyd replay uniqueness failure")
    return tuple(sorted(selected)), entropy


def parse_rank_transcript(
    payload: bytes, *, expected_count: int, population: int
) -> tuple[int, ...]:
    if not payload or not payload.endswith(b"\n"):
        raise VerificationError("rank transcript must be nonempty and newline terminated")
    lines = payload.splitlines()
    if len(lines) != expected_count:
        raise VerificationError("rank transcript count mismatch")
    ranks: list[int] = []
    previous = -1
    for index, line in enumerate(lines):
        if not line or any(byte < 48 or byte > 57 for byte in line):
            raise VerificationError(f"rank line {index} is not unsigned decimal ASCII")
        if len(line) > 1 and line.startswith(b"0"):
            raise VerificationError(f"rank line {index} has a leading zero")
        rank = int(line)
        if rank >= population:
            raise VerificationError(f"rank line {index} is outside the population")
        if rank <= previous:
            raise VerificationError("rank transcript must be strictly increasing")
        ranks.append(rank)
        previous = rank
    return tuple(ranks)


def chunk_rank_bytes(ranks: Sequence[int]) -> bytes:
    return b"".join(f"{rank}\n".encode("ascii") for rank in ranks)


def deterministic_spot_indices(length: int, count: int = 256) -> tuple[int, ...]:
    """Select reproducible transcript positions without claiming physical randomness."""
    length = _exact_positive(length, "spot-replay transcript length")
    count = _exact_positive(count, "spot-replay count")
    if count > length:
        raise VerificationError("spot-replay count exceeds transcript length")
    selected = {0, length - 1}
    counter = 0
    seed = bytes.fromhex(REGISTERED_PROTOCOL_SHA256)
    while len(selected) < count:
        block = sha256(seed + b"independent-spot-v1" + counter.to_bytes(8, "big")).digest()
        selected.add(int.from_bytes(block, "big") % length)
        counter += 1
    return tuple(sorted(selected))


def deterministic_spot_replay(
    ranks: Sequence[int],
    *,
    code_cells: int,
    register_cells: int,
    input_words: Sequence[Sequence[int]],
    step_cap: int,
    count: int = 256,
) -> tuple[int, str]:
    """Independently decode, re-rank, and observe a registered set of positions."""
    digest = sha256()
    indices = deterministic_spot_indices(len(ranks), count)
    for index in indices:
        rank = ranks[index]
        program = independent_unrank(code_cells, register_cells, rank)
        if independent_rank(code_cells, register_cells, program) != rank:
            raise VerificationError("deterministic spot rank round trip mismatch")
        semantic = independent_semantic_key(program, input_words, step_cap).encode("ascii")
        candidate = canonical_candidate_bytes(program)
        for payload in (
            index.to_bytes(8, "big"),
            str(rank).encode("ascii"),
            candidate,
            semantic,
        ):
            digest.update(len(payload).to_bytes(8, "big"))
            digest.update(payload)
    return len(indices), digest.hexdigest()


def chunk_chain_hash(prior_chain_sha256: str, chunk_without_chain: Mapping[str, object]) -> str:
    if type(prior_chain_sha256) is not str or len(prior_chain_sha256) != 64:
        raise VerificationError("prior chain hash must be 64 hexadecimal characters")
    try:
        prior = bytes.fromhex(prior_chain_sha256)
    except ValueError as exc:
        raise VerificationError("prior chain hash is not hexadecimal") from exc
    return sha256_hex(prior + canonical_json_bytes(dict(chunk_without_chain)))


def verify_chunk_receipt(
    receipt: Mapping[str, object],
    ranks: Sequence[int],
    *,
    expected_index: int,
    prior_chain_sha256: str,
    code_cells: int,
    register_cells: int,
    input_words: Sequence[Sequence[int]],
    step_cap: int,
) -> tuple[str, Counter[str], Counter[str], tuple[str, ...]]:
    receipt = _mapping(receipt, "chunk receipt")
    expected_fields = {
        "schema", "index", "sample_start", "sample_stop", "first_rank", "last_rank",
        "rank_transcript_sha256", "candidate_transcript_sha256", "semantic_counts_sha256",
        "generated_count", "validated_count", "round_trip_count", "resource_counts",
        "semantic_counts", "prior_chain_sha256", "chain_sha256",
    }
    if set(receipt) != expected_fields:
        raise VerificationError("chunk receipt field set mismatch")
    if receipt.get("schema") != "GMI833MillionCandidateChunkReceiptV1":
        raise VerificationError("chunk receipt schema mismatch")
    if receipt.get("index") != expected_index:
        raise VerificationError("chunk receipt index mismatch")
    sample_start = _exact_natural(receipt.get("sample_start"), "chunk sample_start")
    sample_stop = _exact_positive(receipt.get("sample_stop"), "chunk sample_stop")
    expected_start = expected_index * len(ranks)
    if sample_start != expected_start or sample_stop != expected_start + len(ranks):
        raise VerificationError("chunk receipt interval length mismatch")
    if (
        not ranks
        or receipt.get("first_rank") != str(ranks[0])
        or receipt.get("last_rank") != str(ranks[-1])
    ):
        raise VerificationError("chunk boundary ranks mismatch")
    count = len(ranks)
    for field in ("generated_count", "validated_count", "round_trip_count"):
        if receipt.get(field) != count:
            raise VerificationError(f"chunk {field} mismatch")
    rank_bytes = chunk_rank_bytes(ranks)
    if receipt.get("rank_transcript_sha256") != sha256_hex(rank_bytes):
        raise VerificationError("chunk rank transcript hash mismatch")

    programs = tuple(independent_unrank(code_cells, register_cells, rank) for rank in ranks)
    if any(independent_rank(code_cells, register_cells, program) != rank for rank, program in zip(ranks, programs)):
        raise VerificationError("independent rank round trip mismatch")
    if receipt.get("candidate_transcript_sha256") != candidate_transcript_digest(programs):
        raise VerificationError("chunk candidate transcript hash mismatch")

    resource_counts = Counter(f"labels={len(program[1])},registers={program[0]}" for program in programs)
    receipt_resources = _count_mapping(receipt.get("resource_counts"), "chunk resource_counts")
    if dict(sorted(resource_counts.items())) != receipt_resources:
        raise VerificationError("chunk resource strata mismatch")

    semantic_sequence = tuple(
        independent_semantic_key(program, input_words, step_cap) for program in programs
    )
    semantic_counts = Counter(semantic_sequence)
    receipt_semantics = _count_mapping(receipt.get("semantic_counts"), "chunk semantic_counts")
    if dict(sorted(semantic_counts.items())) != receipt_semantics:
        raise VerificationError("chunk semantic counts mismatch")
    if receipt.get("semantic_counts_sha256") != sha256_hex(canonical_json_bytes(receipt_semantics)):
        raise VerificationError("chunk semantic-count hash mismatch")

    if receipt.get("prior_chain_sha256") != prior_chain_sha256:
        raise VerificationError("chunk prior-chain link mismatch")
    without_chain = dict(receipt)
    claimed_chain = without_chain.pop("chain_sha256", None)
    expected_chain = chunk_chain_hash(prior_chain_sha256, without_chain)
    if claimed_chain != expected_chain:
        raise VerificationError("chunk chain hash mismatch")
    return expected_chain, resource_counts, semantic_counts, semantic_sequence


def _load_json_file(path: Path, label: str) -> tuple[dict[str, object], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read valid {label} JSON") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"{label} JSON root must be an object")
    return value, raw


def verify_checkpoint(
    checkpoint: Mapping[str, object],
    *,
    protocol_sha256: str,
    dependency_blob: str,
    rank_transcript_sha256: str,
    expected_chunks: int,
    expected_count: int,
    terminal_chain_sha256: str,
    resource_counts: Mapping[str, int],
    semantic_counts: Mapping[str, int],
    discovery_checkpoints: Mapping[str, int],
) -> None:
    expected_fields = {
        "schema", "protocol_sha256", "dependency_module_git_blob", "next_chunk_index",
        "rank_transcript_sha256", "generated_count", "validated_count", "round_trip_count",
        "resource_counts", "semantic_counts", "discovery_checkpoints",
        "terminal_chunk_chain_sha256", "restart_count",
    }
    if set(checkpoint) != expected_fields:
        raise VerificationError("checkpoint field set mismatch")
    expected_scalars = {
        "schema": "GMI833MillionCandidateCheckpointV1",
        "protocol_sha256": protocol_sha256,
        "dependency_module_git_blob": dependency_blob,
        "next_chunk_index": expected_chunks,
        "rank_transcript_sha256": rank_transcript_sha256,
        "generated_count": expected_count,
        "validated_count": expected_count,
        "round_trip_count": expected_count,
        "terminal_chunk_chain_sha256": terminal_chain_sha256,
    }
    for key, expected in expected_scalars.items():
        if checkpoint.get(key) != expected:
            raise VerificationError(f"checkpoint field {key!r} mismatch")
    checkpoint_resources = _count_mapping(checkpoint.get("resource_counts"), "checkpoint resource counts")
    if checkpoint_resources != dict(sorted(resource_counts.items())):
        raise VerificationError("checkpoint resource counts mismatch")
    checkpoint_semantics = _count_mapping(checkpoint.get("semantic_counts"), "checkpoint semantic counts")
    if checkpoint_semantics != dict(sorted(semantic_counts.items())):
        raise VerificationError("checkpoint semantic counts mismatch")
    _exact_natural(checkpoint.get("restart_count"), "checkpoint restart count")
    discovery = _mapping(checkpoint.get("discovery_checkpoints"), "checkpoint discovery checkpoints")
    for key, value in discovery.items():
        if not key.isdigit():
            raise VerificationError("checkpoint discovery checkpoint key is not decimal")
        _exact_natural(value, f"checkpoint discovery checkpoint {key}")
    if discovery != dict(discovery_checkpoints):
        raise VerificationError("checkpoint discovery checkpoints mismatch")


def verify_run_artifacts(
    run_directory: Path,
    result_path: Path,
    *,
    replay_registered_sample: bool = True,
) -> dict[str, object]:
    """Fail-closed verification of a completed frozen run.

    ``replay_registered_sample=False`` skips only the expensive independent
    million-draw Floyd reconstruction.  It still checks every rank, candidate,
    protected semantic observation, receipt, and chain link.
    """

    protocol = load_registered_protocol()
    budget = _mapping(protocol["budget"], "budget")
    code_cells = _exact_positive(budget["code_cells"], "code cells")
    register_cells = _exact_positive(budget["register_cells"], "register cells")
    population = independent_population_size(code_cells, register_cells)
    sample_size = _exact_positive(protocol["sample_size"], "sample size")
    chunk_size = _exact_positive(protocol["chunk_size"], "chunk size")
    chunk_count = _exact_positive(protocol["chunk_count"], "chunk count")
    interface = _mapping(protocol["semantic_interface"], "semantic interface")
    input_words = interface["input_words"]
    if type(input_words) is not list:
        raise VerificationError("semantic input words malformed")
    step_cap = _exact_positive(interface["step_cap"], "semantic step cap")

    ranks_payload = (run_directory / "ranks_v1.txt").read_bytes()
    ranks = parse_rank_transcript(ranks_payload, expected_count=sample_size, population=population)
    rank_transcript_sha256 = sha256_hex(ranks_payload)
    spot_count, spot_digest = deterministic_spot_replay(
        ranks,
        code_cells=code_cells,
        register_cells=register_cells,
        input_words=input_words,
        step_cap=step_cap,
    )
    if replay_registered_sample:
        replayed, entropy = independent_floyd_sample(
            population, sample_size, str(protocol["replay_seed_utf8"]).encode("utf-8")
        )
        if replayed != ranks:
            raise VerificationError("rank transcript differs from independent registered replay")
    else:
        entropy = None

    dependency_path = HERE.parent.parent / str(_mapping(protocol["generator_dependency"], "generator dependency")["module"])
    dependency_blob = git_blob_sha1(dependency_path.read_bytes())
    aggregate_resources: Counter[str] = Counter()
    aggregate_semantics: Counter[str] = Counter()
    discovery_expected: dict[str, int] = {}
    discovery_positions = set(protocol["semantic_discovery_checkpoints"])
    generated = 0
    chunk_digests = sha256()
    prior_chain = GENESIS_CHAIN_SHA256
    for index in range(chunk_count):
        chunk_path = run_directory / "chunks" / f"chunk_{index:04d}.json"
        chunk, chunk_raw = _load_json_file(chunk_path, f"chunk {index}")
        if chunk_raw != canonical_json_bytes(chunk) + b"\n":
            raise VerificationError(f"chunk {index} is not canonical newline-terminated JSON")
        start = index * chunk_size
        stop = start + chunk_size
        prior_chain, resources, semantics, semantic_sequence = verify_chunk_receipt(
            chunk,
            ranks[start:stop],
            expected_index=index,
            prior_chain_sha256=prior_chain,
            code_cells=code_cells,
            register_cells=register_cells,
            input_words=input_words,
            step_cap=step_cap,
        )
        aggregate_resources.update(resources)
        for semantic in semantic_sequence:
            aggregate_semantics[semantic] += 1
            generated += 1
            if generated in discovery_positions:
                discovery_expected[str(generated)] = len(aggregate_semantics)
        chunk_digests.update(bytes.fromhex(str(chunk["candidate_transcript_sha256"])))

    checkpoint, checkpoint_raw = _load_json_file(run_directory / "checkpoint_v1.json", "checkpoint")
    if checkpoint_raw != canonical_json_bytes(checkpoint) + b"\n":
        raise VerificationError("checkpoint is not canonical newline-terminated JSON")
    verify_checkpoint(
        checkpoint,
        protocol_sha256=REGISTERED_PROTOCOL_SHA256,
        dependency_blob=dependency_blob,
        rank_transcript_sha256=rank_transcript_sha256,
        expected_chunks=chunk_count,
        expected_count=sample_size,
        terminal_chain_sha256=prior_chain,
        resource_counts=aggregate_resources,
        semantic_counts=aggregate_semantics,
        discovery_checkpoints=discovery_expected,
    )

    result, result_raw = _load_json_file(result_path, "result")
    if result.get("schema") != protocol["receipt_schema"]:
        raise VerificationError("result schema mismatch")
    if result.get("protocol_sha256") != REGISTERED_PROTOCOL_SHA256:
        raise VerificationError("result protocol hash mismatch")
    if result.get("claim_ceiling") != protocol["claim_ceiling"]:
        raise VerificationError("result claim ceiling mismatch")
    expected_identity = {
        "parent_issue": 833,
        "source_issue": 1006,
        "source_pr": 1007,
        "verdict": "ONE_MILLION_DISTINCT_G0_CANDIDATE_STRUCTURES_GENERATED_AT_REGISTERED_FINITE_SCOPE",
    }
    for key, expected in expected_identity.items():
        if result.get(key) != expected:
            raise VerificationError(f"result identity field {key!r} mismatch")
    if result.get("generator_dependency") != {
        "pull_request": 1003,
        "exact_head": "05d13723b519d9de94f15b142cca0827d3725d6f",
        "module_git_blob": dependency_blob,
    }:
        raise VerificationError("result generator dependency mismatch")
    if result.get("configuration") != {
        "grammar": protocol["grammar"],
        "budget": protocol["budget"],
        "sample_design": protocol["sample_design"],
        "sample_size": sample_size,
        "chunk_size": chunk_size,
        "semantic_interface": protocol["semantic_interface"],
        "replay_adapter": "DETERMINISTIC_TRANSCRIPT_ONLY_NOT_PHYSICAL_RANDOMNESS",
    }:
        raise VerificationError("result configuration mismatch")
    from fractions import Fraction
    population_receipt = _mapping(result.get("population"), "result population")
    expected_population_scalars = {
        "exact_size": str(population),
        "decimal_digits": len(str(population)),
        "bit_length": population.bit_length(),
        "population_materialized": False,
    }
    for key, expected in expected_population_scalars.items():
        if population_receipt.get(key) != expected:
            raise VerificationError(f"result population field {key!r} mismatch")
    try:
        inclusion = Fraction(str(population_receipt.get("exact_first_order_inclusion_probability")))
    except (ValueError, ZeroDivisionError) as exc:
        raise VerificationError("result inclusion probability is malformed") from exc
    if inclusion != Fraction(sample_size, population):
        raise VerificationError("result inclusion probability mismatch")
    execution = _mapping(result.get("execution"), "result execution")
    expected_execution = {
        "generated_count": sample_size,
        "unique_rank_count": sample_size,
        "unique_canonical_structure_count": sample_size,
        "validated_count": sample_size,
        "round_trip_count": sample_size,
        "completed_chunks": chunk_count,
        "rank_transcript_sha256": rank_transcript_sha256,
        "candidate_chunk_digest_transcript_sha256": chunk_digests.hexdigest(),
        "terminal_chunk_chain_sha256": prior_chain,
        "final_checkpoint_sha256": sha256_hex(checkpoint_raw),
    }
    for key, expected in expected_execution.items():
        if execution.get(key) != expected:
            raise VerificationError(f"result execution field {key!r} mismatch")
    if execution.get("canonical_uniqueness_basis") != "EXACT_RANK_UNIQUENESS_PLUS_VALIDATED_RANK_UNRANK_BIJECTION":
        raise VerificationError("result canonical-uniqueness basis mismatch")
    if entropy is not None:
        entropy_receipt = _mapping(execution.get("entropy"), "execution entropy")
        entropy_expected = {
            "blocks_consumed": entropy.counter,
            "raw_candidates": entropy.raw_candidates,
            "rejections": entropy.rejections,
        }
        for key, expected in entropy_expected.items():
            if entropy_receipt.get(key) != expected:
                raise VerificationError(f"result entropy field {key!r} mismatch")
    elapsed = execution.get("elapsed_seconds")
    if type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0:
        raise VerificationError("result elapsed_seconds must be a nonnegative number")
    for field in ("peak_rss_bytes", "persistent_artifact_bytes", "restart_count"):
        _exact_natural(execution.get(field), f"result {field}")

    resource_strata = result.get("resource_strata")
    expected_strata = independent_strata(code_cells, register_cells)
    if type(resource_strata) is not list or len(resource_strata) != len(expected_strata):
        raise VerificationError("result resource-strata table length mismatch")
    for index, (row, item) in enumerate(zip(resource_strata, expected_strata)):
        row = _mapping(row, f"resource stratum {index}")
        key = f"labels={item.labels},registers={item.registers}"
        exact_count = aggregate_resources.get(key, 0)
        expected_row = {
            "index": index,
            "labels": item.labels,
            "registers": item.registers,
            "population": str(item.size),
            "count": exact_count,
            "ideal_fraction_exact": f"{item.size}/{population}",
            "observed_fraction_exact": f"{exact_count}/{sample_size}",
        }
        # Receipt fractions are reduced; compare their exact numeric values below.
        for field in ("index", "labels", "registers", "population", "count"):
            if row.get(field) != expected_row[field]:
                raise VerificationError(f"resource stratum {index} field {field!r} mismatch")
        for field in ("index", "labels", "registers", "count"):
            _exact_natural(row.get(field), f"resource stratum {index} {field}")
        try:
            if Fraction(str(row.get("ideal_fraction_exact"))) != Fraction(item.size, population):
                raise VerificationError(f"resource stratum {index} ideal fraction mismatch")
            if Fraction(str(row.get("observed_fraction_exact"))) != Fraction(exact_count, sample_size):
                raise VerificationError(f"resource stratum {index} observed fraction mismatch")
        except (ValueError, ZeroDivisionError) as exc:
            raise VerificationError(f"resource stratum {index} has malformed exact fraction") from exc
    observed_strata = sum(count > 0 for count in aggregate_resources.values())
    if result.get("resource_strata_summary") != {
        "registered_strata": len(expected_strata),
        "observed_strata": observed_strata,
        "unobserved_strata": len(expected_strata) - observed_strata,
        "interpretation": "GLOBAL_CANDIDATE_UNIFORM_SRSWOR_DOES_NOT_GUARANTEE_STRATUM_REPRESENTATION",
    }:
        raise VerificationError("resource-strata summary mismatch")

    semantic_metrics = _mapping(result.get("semantic_metrics"), "semantic metrics")
    observed = len(aggregate_semantics)
    for field in ("observed_semantic_keys", "collapse_count", "singletons", "doubletons"):
        _exact_natural(semantic_metrics.get(field), f"semantic metric {field}")
    if semantic_metrics.get("observed_semantic_keys") != observed:
        raise VerificationError("observed semantic-key count mismatch")
    if semantic_metrics.get("collapse_count") != sample_size - observed:
        raise VerificationError("semantic collapse count mismatch")
    multiplicities = Counter(aggregate_semantics.values())
    expected_histogram = {str(value): count for value, count in sorted(multiplicities.items())}
    histogram = _count_mapping(semantic_metrics.get("multiplicity_histogram"), "semantic multiplicity histogram")
    if histogram != expected_histogram:
        raise VerificationError("semantic multiplicity histogram mismatch")
    if semantic_metrics.get("singletons") != multiplicities.get(1, 0):
        raise VerificationError("semantic singleton count mismatch")
    if semantic_metrics.get("doubletons") != multiplicities.get(2, 0):
        raise VerificationError("semantic doubleton count mismatch")
    inverse_denominator = sum(count * count for count in aggregate_semantics.values())
    if semantic_metrics.get("inverse_simpson_sum_squared_multiplicities") != inverse_denominator:
        raise VerificationError("inverse-Simpson squared-multiplicity sum mismatch")
    try:
        inverse_exact = Fraction(str(semantic_metrics.get("inverse_simpson_effective_semantic_count_exact")))
        collapse_exact = Fraction(str(semantic_metrics.get("collapse_rate_exact")))
    except (ValueError, ZeroDivisionError) as exc:
        raise VerificationError("semantic exact-rational metric is malformed") from exc
    if inverse_exact != Fraction(sample_size * sample_size, inverse_denominator):
        raise VerificationError("inverse-Simpson effective semantic count mismatch")
    if collapse_exact != Fraction(sample_size - observed, sample_size):
        raise VerificationError("semantic collapse rate mismatch")
    if semantic_metrics.get("discovery_checkpoints") != checkpoint.get("discovery_checkpoints"):
        raise VerificationError("result/checkpoint discovery checkpoints mismatch")

    checks = _mapping(result.get("checks"), "result checks")
    expected_check_fields = {
        "exact_generated_threshold", "unique_rank_count",
        "unique_canonical_structures_by_bijective_round_trip", "all_candidates_validated",
        "all_ranks_round_trip", "all_chunks_complete", "resource_stratum_counts_are_complete",
        "wall_ceiling_met", "peak_rss_ceiling_met", "artifact_ceiling_met",
        "forbidden_10e8_claim_absent",
    }
    if set(checks) != expected_check_fields or not all(value is True for value in checks.values()):
        raise VerificationError("result contains a missing or negative check")
    if result.get("resource_ceilings") != protocol["resource_ceilings"]:
        raise VerificationError("result resource ceilings mismatch")
    ceilings = _mapping(protocol["resource_ceilings"], "resource ceilings")
    if elapsed > ceilings["wall_seconds"]:
        raise VerificationError("reported wall time exceeds frozen ceiling")
    if execution["peak_rss_bytes"] > ceilings["peak_rss_bytes"]:
        raise VerificationError("reported peak RSS exceeds frozen ceiling")
    if execution["persistent_artifact_bytes"] > ceilings["persistent_run_artifact_bytes"]:
        raise VerificationError("reported run artifact bytes exceed frozen ceiling")
    actual_artifact_bytes = sum(
        path.stat().st_size for path in run_directory.rglob("*") if path.is_file()
    )
    if execution["persistent_artifact_bytes"] != actual_artifact_bytes:
        raise VerificationError("reported persistent artifact bytes mismatch current run tree")
    committed_bytes = _exact_natural(
        execution.get("committed_evidence_bytes_after_result"),
        "committed evidence bytes",
    )
    if committed_bytes > ceilings["committed_evidence_bytes"]:
        raise VerificationError("reported committed evidence exceeds frozen ceiling")
    if result.get("forbidden_promotions") != protocol["forbidden_promotions"]:
        raise VerificationError("result forbidden-promotion boundary mismatch")
    if result.get("adjacent_rows_left_open") != [
        "Scale to at least 10^8 candidates or justify an equivalent effective coverage method.",
        "Measure reachable fraction under each developmental/search law.",
    ]:
        raise VerificationError("result adjacent-row boundary mismatch")
    return {
        "schema": CHECKER_SCHEMA,
        "verdict": "INDEPENDENT_CHECKS_PASS",
        "protocol_sha256": REGISTERED_PROTOCOL_SHA256,
        "dependency_module_git_blob": dependency_blob,
        "population": str(population),
        "sample_size": sample_size,
        "chunks_verified": chunk_count,
        "rank_transcript_sha256": rank_transcript_sha256,
        "terminal_chunk_chain_sha256": prior_chain,
        "observed_semantic_keys": observed,
        "registered_sample_replayed": replay_registered_sample,
        "deterministic_spot_replay_count": spot_count,
        "deterministic_spot_replay_sha256": spot_digest,
        "final_checkpoint_sha256": sha256_hex(checkpoint_raw),
        "result_sha256": sha256_hex(result_raw),
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) not in (2, 3):
        print("usage: independent_checker_v1.py RUN_DIRECTORY RESULT_V1.json [--skip-sample-replay]", file=sys.stderr)
        return 2
    skip = len(args) == 3
    if skip and args[2] != "--skip-sample-replay":
        print("only optional flag is --skip-sample-replay", file=sys.stderr)
        return 2
    try:
        receipt = verify_run_artifacts(Path(args[0]), Path(args[1]), replay_registered_sample=not skip)
    except (OSError, VerificationError) as exc:
        print(f"INDEPENDENT_CHECK_FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
