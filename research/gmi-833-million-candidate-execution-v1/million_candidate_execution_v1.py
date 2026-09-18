#!/usr/bin/env python3
"""Restartable registered execution of one million finite G0 candidates."""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import time
from typing import Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "FROZEN_PROTOCOL_V1.json"
EXPECTED_DEPENDENCY_HEAD = "05d13723b519d9de94f15b142cca0827d3725d6f"
EXPECTED_DEPENDENCY_BLOB = "ce2cd60e7583d4d35e24636bc6c66e7a223e4ee0"
SOURCE_ISSUE = 1006
SOURCE_PR = 1007
GENESIS_CHAIN = "0" * 64


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return sha256(value).hexdigest()


def git_blob_sha(value: bytes) -> str:
    return sha1(b"blob " + str(len(value)).encode("ascii") + b"\0" + value).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _load_dependency():
    path = HERE.parent / "gmi-833-scalable-morphology-sampling-v1" / "scalable_morphology_sampling_v1.py"
    data = path.read_bytes()
    actual_blob = git_blob_sha(data)
    if actual_blob != EXPECTED_DEPENDENCY_BLOB:
        raise RuntimeError(
            f"generator dependency blob drift: expected {EXPECTED_DEPENDENCY_BLOB}, got {actual_blob}"
        )
    spec = importlib.util.spec_from_file_location("gmi833_million_sampling_dependency", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the pinned #1003 dependency")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SAMPLING = _load_dependency()


def load_protocol() -> tuple[dict[str, object], bytes, str]:
    raw = PROTOCOL_PATH.read_bytes()
    protocol = json.loads(raw)
    expected = {
        "schema": "GMI833MillionCandidateExecutionProtocolV1",
        "source_issue": SOURCE_ISSUE,
        "sample_size": 1_000_000,
        "chunk_size": 10_000,
        "chunk_count": 100,
        "outcome_status_at_registration": "NOT_RUN",
    }
    for field, value in expected.items():
        if protocol.get(field) != value:
            raise RuntimeError(f"frozen protocol field {field!r} drifted")
    dependency = protocol.get("generator_dependency")
    if not isinstance(dependency, dict) or dependency.get("exact_head") != EXPECTED_DEPENDENCY_HEAD:
        raise RuntimeError("frozen generator dependency head drifted")
    return protocol, raw, sha256_hex(raw)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def semantic_key_text(key: tuple[tuple[str, tuple[int, ...]], ...]) -> str:
    return json.dumps([[status, list(output)] for status, output in key], separators=(",", ":"))


def protected_semantic_key(
    program: object,
    input_words: Sequence[Sequence[int]],
    step_cap: int,
) -> tuple[tuple[str, tuple[int, ...]], ...]:
    """Direct implementation of #966's protected observation semantics."""
    SAMPLING.PARENT.validate_program(program)
    instructions = program.instructions
    register_count = program.register_count
    result: list[tuple[str, tuple[int, ...]]] = []
    for raw_word in input_words:
        word = tuple(raw_word)
        registers = [0] * register_count
        input_position = 0
        output: list[int] = []
        pc = 0
        terminal: str | None = None
        for _ in range(step_cap):
            instruction = instructions[pc]
            if instruction.op == "HALT":
                terminal = "HALTED"
                break
            if instruction.op == "READ":
                if input_position >= len(word):
                    terminal = "BLOCKED_INPUT"
                    break
                registers[instruction.register] = word[input_position]
                input_position += 1
                pc = instruction.target0
                continue
            if instruction.op == "INC":
                registers[instruction.register] += 1
                pc = instruction.target0
                continue
            if instruction.op == "DECJZ":
                if registers[instruction.register] > 0:
                    registers[instruction.register] -= 1
                    pc = instruction.target0
                else:
                    pc = instruction.target1
                continue
            if instruction.op == "EMIT":
                output.append(registers[instruction.register])
                pc = instruction.target0
                continue
            raise AssertionError("validated instruction operation fell through")
        if terminal is None:
            terminal = "STEP_LIMIT"
        result.append((terminal, tuple(output)))
    return tuple(result)


def _candidate_payload(program: object) -> bytes:
    return canonical_bytes(program.canonical_code())


def _feed_length_delimited(digest: object, payload: bytes) -> None:
    digest.update(len(payload).to_bytes(8, "big"))
    digest.update(payload)


def _resource_key(program: object) -> str:
    return f"labels={len(program.instructions)},registers={program.register_count}"


def rank_transcript_bytes(ranks: Sequence[int]) -> bytes:
    return ("".join(f"{rank}\n" for rank in ranks)).encode("ascii")


def ensure_rank_transcript(
    run_dir: Path,
    budget: object,
    sample_size: int,
    seed: bytes,
) -> tuple[tuple[int, ...], dict[str, int], str]:
    entropy = SAMPLING.CounterEntropy(seed)
    ranks = SAMPLING.global_srswor(budget, sample_size, entropy.uniform_below)
    if len(ranks) != sample_size or len(set(ranks)) != sample_size:
        raise AssertionError("registered SRSWOR transcript lost exact uniqueness")
    payload = rank_transcript_bytes(ranks)
    digest = sha256_hex(payload)
    path = run_dir / "ranks_v1.txt"
    if path.exists():
        existing = path.read_bytes()
        if existing != payload:
            raise RuntimeError("existing rank transcript disagrees with frozen deterministic replay")
    else:
        atomic_write(path, payload)
    return (
        ranks,
        {
            "blocks_consumed": entropy.blocks_consumed,
            "raw_candidates": entropy.raw_candidates,
            "rejections": entropy.rejections,
        },
        digest,
    )


def process_chunk(
    index: int,
    ranks: Sequence[int],
    budget: object,
    input_words: Sequence[Sequence[int]],
    step_cap: int,
    prior_chain: str,
) -> tuple[dict[str, object], list[str]]:
    if not ranks:
        raise ValueError("chunk cannot be empty")
    rank_digest = sha256()
    candidate_digest = sha256()
    semantic_counts: Counter[str] = Counter()
    resource_counts: Counter[str] = Counter()
    semantic_sequence: list[str] = []
    for rank in ranks:
        rank_digest.update(f"{rank}\n".encode("ascii"))
        program = SAMPLING.unrank_program(budget, rank)
        SAMPLING.PARENT.validate_program(program)
        if SAMPLING.rank_program(budget, program) != rank:
            raise AssertionError("candidate failed exact rank round trip")
        _feed_length_delimited(candidate_digest, _candidate_payload(program))
        semantic = semantic_key_text(protected_semantic_key(program, input_words, step_cap))
        semantic_counts[semantic] += 1
        resource_counts[_resource_key(program)] += 1
        semantic_sequence.append(semantic)
    semantic_map = {key: semantic_counts[key] for key in sorted(semantic_counts)}
    resource_map = {key: resource_counts[key] for key in sorted(resource_counts)}
    base: dict[str, object] = {
        "schema": "GMI833MillionCandidateChunkReceiptV1",
        "index": index,
        "sample_start": index * len(ranks),
        "sample_stop": index * len(ranks) + len(ranks),
        "first_rank": str(ranks[0]),
        "last_rank": str(ranks[-1]),
        "rank_transcript_sha256": rank_digest.hexdigest(),
        "candidate_transcript_sha256": candidate_digest.hexdigest(),
        "semantic_counts_sha256": sha256_hex(canonical_bytes(semantic_map)),
        "generated_count": len(ranks),
        "validated_count": len(ranks),
        "round_trip_count": len(ranks),
        "resource_counts": resource_map,
        "semantic_counts": semantic_map,
        "prior_chain_sha256": prior_chain,
    }
    base["chain_sha256"] = sha256_hex(bytes.fromhex(prior_chain) + canonical_bytes(base))
    return base, semantic_sequence


def _validate_chunk_shape(receipt: Mapping[str, object], expected: Mapping[str, object]) -> None:
    if dict(receipt) != dict(expected):
        raise RuntimeError(f"existing chunk {expected['index']} failed exact replay validation")


def _checkpoint_payload(
    protocol_sha: str,
    rank_sha: str,
    next_chunk: int,
    generated: int,
    resource_counts: Counter[str],
    semantic_counts: Counter[str],
    discovery: Mapping[str, int],
    terminal_chain: str,
    restart_count: int,
) -> dict[str, object]:
    return {
        "schema": "GMI833MillionCandidateCheckpointV1",
        "protocol_sha256": protocol_sha,
        "dependency_module_git_blob": EXPECTED_DEPENDENCY_BLOB,
        "next_chunk_index": next_chunk,
        "rank_transcript_sha256": rank_sha,
        "generated_count": generated,
        "validated_count": generated,
        "round_trip_count": generated,
        "resource_counts": {key: resource_counts[key] for key in sorted(resource_counts)},
        "semantic_counts": {key: semantic_counts[key] for key in sorted(semantic_counts)},
        "discovery_checkpoints": dict(discovery),
        "terminal_chunk_chain_sha256": terminal_chain,
        "restart_count": restart_count,
    }


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def _tree_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _update_aggregate(
    sequence: Iterable[str],
    resource_map: Mapping[str, object],
    semantic_counts: Counter[str],
    resource_counts: Counter[str],
    generated_before: int,
    checkpoints: set[int],
    discovery: dict[str, int],
) -> int:
    generated = generated_before
    for semantic in sequence:
        semantic_counts[semantic] += 1
        generated += 1
        if generated in checkpoints:
            discovery[str(generated)] = len(semantic_counts)
    for key, value in resource_map.items():
        if type(value) is not int or value < 0:
            raise RuntimeError("chunk resource count is malformed")
        resource_counts[key] += value
    return generated


def execute_registered(run_dir: Path, result_path: Path) -> dict[str, object]:
    started = time.perf_counter()
    protocol, _, protocol_sha = load_protocol()
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "chunks").mkdir(parents=True, exist_ok=True)
    budget = SAMPLING.StructuralBudget(
        protocol["budget"]["code_cells"], protocol["budget"]["register_cells"]
    )
    sample_size = protocol["sample_size"]
    chunk_size = protocol["chunk_size"]
    chunk_count = protocol["chunk_count"]
    input_words = tuple(tuple(word) for word in protocol["semantic_interface"]["input_words"])
    step_cap = protocol["semantic_interface"]["step_cap"]
    checkpoints = set(protocol["semantic_discovery_checkpoints"])
    seed = protocol["replay_seed_utf8"].encode("utf-8")
    ranks, entropy, rank_sha = ensure_rank_transcript(run_dir, budget, sample_size, seed)
    population = SAMPLING.population_size(budget)

    checkpoint_path = run_dir / "checkpoint_v1.json"
    old_checkpoint = json.loads(checkpoint_path.read_text()) if checkpoint_path.exists() else None
    restart_count = 0 if old_checkpoint is None else int(old_checkpoint.get("restart_count", 0)) + 1
    existing_chunks = 0 if old_checkpoint is None else int(old_checkpoint.get("next_chunk_index", 0))
    if not 0 <= existing_chunks <= chunk_count:
        raise RuntimeError("checkpoint chunk index is outside the frozen run")

    semantic_counts: Counter[str] = Counter()
    resource_counts: Counter[str] = Counter()
    discovery: dict[str, int] = {}
    generated = 0
    prior_chain = GENESIS_CHAIN
    candidate_chunk_digest_transcript = sha256()

    # Validate every completed receipt by exact candidate replay before resuming.
    for index in range(existing_chunks):
        start = index * chunk_size
        stop = start + chunk_size
        expected, sequence = process_chunk(
            index, ranks[start:stop], budget, input_words, step_cap, prior_chain
        )
        chunk_path = run_dir / "chunks" / f"chunk_{index:04d}.json"
        if not chunk_path.is_file():
            raise RuntimeError("checkpoint names a missing completed chunk")
        actual = json.loads(chunk_path.read_text())
        _validate_chunk_shape(actual, expected)
        prior_chain = str(expected["chain_sha256"])
        candidate_chunk_digest_transcript.update(
            bytes.fromhex(str(expected["candidate_transcript_sha256"]))
        )
        generated = _update_aggregate(
            sequence,
            expected["resource_counts"],
            semantic_counts,
            resource_counts,
            generated,
            checkpoints,
            discovery,
        )

    if old_checkpoint is not None:
        rebuilt = _checkpoint_payload(
            protocol_sha,
            rank_sha,
            existing_chunks,
            generated,
            resource_counts,
            semantic_counts,
            discovery,
            prior_chain,
            int(old_checkpoint.get("restart_count", 0)),
        )
        if old_checkpoint != rebuilt:
            raise RuntimeError("checkpoint failed exact replay validation")

    for index in range(existing_chunks, chunk_count):
        start = index * chunk_size
        stop = start + chunk_size
        receipt, sequence = process_chunk(
            index, ranks[start:stop], budget, input_words, step_cap, prior_chain
        )
        atomic_write(
            run_dir / "chunks" / f"chunk_{index:04d}.json",
            canonical_bytes(receipt) + b"\n",
        )
        prior_chain = str(receipt["chain_sha256"])
        candidate_chunk_digest_transcript.update(
            bytes.fromhex(str(receipt["candidate_transcript_sha256"]))
        )
        generated = _update_aggregate(
            sequence,
            receipt["resource_counts"],
            semantic_counts,
            resource_counts,
            generated,
            checkpoints,
            discovery,
        )
        checkpoint = _checkpoint_payload(
            protocol_sha,
            rank_sha,
            index + 1,
            generated,
            resource_counts,
            semantic_counts,
            discovery,
            prior_chain,
            restart_count,
        )
        atomic_write(checkpoint_path, canonical_bytes(checkpoint) + b"\n")

    # A completed-run replay is itself a registered restart and must persist that fact.
    final_checkpoint_payload = _checkpoint_payload(
        protocol_sha,
        rank_sha,
        chunk_count,
        generated,
        resource_counts,
        semantic_counts,
        discovery,
        prior_chain,
        restart_count,
    )
    atomic_write(checkpoint_path, canonical_bytes(final_checkpoint_payload) + b"\n")

    if generated != sample_size or sum(semantic_counts.values()) != sample_size:
        raise AssertionError("final generated or semantic count drifted")
    if sum(resource_counts.values()) != sample_size:
        raise AssertionError("final resource-stratum count drifted")
    if set(discovery) != {str(value) for value in checkpoints}:
        raise AssertionError("semantic discovery checkpoints are incomplete")

    final_checkpoint = json.loads(checkpoint_path.read_text())
    final_checkpoint_sha = sha256_hex(checkpoint_path.read_bytes())
    strata_rows = []
    for item in SAMPLING.strata(budget):
        key = f"labels={item.labels},registers={item.registers}"
        count = resource_counts.get(key, 0)
        strata_rows.append(
            {
                "index": item.index,
                "labels": item.labels,
                "registers": item.registers,
                "population": str(item.size),
                "count": count,
                "ideal_fraction_exact": _fraction_text(Fraction(item.size, population)),
                "observed_fraction_exact": _fraction_text(Fraction(count, sample_size)),
            }
        )
    multiplicities = Counter(semantic_counts.values())
    sum_squares = sum(value * value for value in semantic_counts.values())
    collapse = sample_size - len(semantic_counts)
    elapsed = time.perf_counter() - started
    peak_rss = _peak_rss_bytes()
    artifact_bytes = _tree_bytes(run_dir)
    ceilings = protocol["resource_ceilings"]
    checks = {
        "exact_generated_threshold": generated == 1_000_000,
        "unique_rank_count": len(ranks) == len(set(ranks)) == 1_000_000,
        "unique_canonical_structures_by_bijective_round_trip": generated == 1_000_000,
        "all_candidates_validated": generated == 1_000_000,
        "all_ranks_round_trip": generated == 1_000_000,
        "all_chunks_complete": final_checkpoint["next_chunk_index"] == 100,
        "resource_stratum_counts_are_complete": sum(row["count"] for row in strata_rows)
        == sample_size,
        "wall_ceiling_met": elapsed <= ceilings["wall_seconds"],
        "peak_rss_ceiling_met": peak_rss <= ceilings["peak_rss_bytes"],
        "artifact_ceiling_met": artifact_bytes <= ceilings["persistent_run_artifact_bytes"],
        "forbidden_10e8_claim_absent": True,
    }
    if not all(checks.values()):
        raise RuntimeError(f"one or more frozen terminal gates failed: {checks}")
    result: dict[str, object] = {
        "schema": "GMI833MillionCandidateExecutionResultV1",
        "parent_issue": 833,
        "source_issue": SOURCE_ISSUE,
        "source_pr": SOURCE_PR,
        "protocol_sha256": protocol_sha,
        "generator_dependency": {
            "pull_request": 1003,
            "exact_head": EXPECTED_DEPENDENCY_HEAD,
            "module_git_blob": EXPECTED_DEPENDENCY_BLOB,
        },
        "claim_ceiling": protocol["claim_ceiling"],
        "verdict": "ONE_MILLION_DISTINCT_G0_CANDIDATE_STRUCTURES_GENERATED_AT_REGISTERED_FINITE_SCOPE",
        "configuration": {
            "grammar": protocol["grammar"],
            "budget": protocol["budget"],
            "sample_design": protocol["sample_design"],
            "sample_size": sample_size,
            "chunk_size": chunk_size,
            "semantic_interface": protocol["semantic_interface"],
            "replay_adapter": "DETERMINISTIC_TRANSCRIPT_ONLY_NOT_PHYSICAL_RANDOMNESS",
        },
        "population": {
            "exact_size": str(population),
            "decimal_digits": len(str(population)),
            "bit_length": population.bit_length(),
            "exact_first_order_inclusion_probability": _fraction_text(
                Fraction(sample_size, population)
            ),
            "population_materialized": False,
        },
        "execution": {
            "generated_count": generated,
            "unique_rank_count": len(ranks),
            "unique_canonical_structure_count": generated,
            "canonical_uniqueness_basis": "EXACT_RANK_UNIQUENESS_PLUS_VALIDATED_RANK_UNRANK_BIJECTION",
            "validated_count": generated,
            "round_trip_count": generated,
            "completed_chunks": chunk_count,
            "rank_transcript_sha256": rank_sha,
            "candidate_chunk_digest_transcript_sha256": candidate_chunk_digest_transcript.hexdigest(),
            "terminal_chunk_chain_sha256": prior_chain,
            "final_checkpoint_sha256": final_checkpoint_sha,
            "entropy": entropy,
            "elapsed_seconds": round(elapsed, 6),
            "peak_rss_bytes": peak_rss,
            "persistent_artifact_bytes": artifact_bytes,
            "restart_count": restart_count,
        },
        "resource_strata": strata_rows,
        "resource_strata_summary": {
            "registered_strata": len(strata_rows),
            "observed_strata": sum(row["count"] > 0 for row in strata_rows),
            "unobserved_strata": sum(row["count"] == 0 for row in strata_rows),
            "interpretation": "GLOBAL_CANDIDATE_UNIFORM_SRSWOR_DOES_NOT_GUARANTEE_STRATUM_REPRESENTATION",
        },
        "semantic_metrics": {
            "scope": "OBSERVED_SAMPLE_ONLY_NOT_SEMANTIC_UNIVERSE_COVERAGE",
            "observed_semantic_keys": len(semantic_counts),
            "collapse_count": collapse,
            "collapse_rate_exact": _fraction_text(Fraction(collapse, sample_size)),
            "multiplicity_histogram": {
                str(value): multiplicities[value] for value in sorted(multiplicities)
            },
            "singletons": multiplicities.get(1, 0),
            "doubletons": multiplicities.get(2, 0),
            "discovery_checkpoints": discovery,
            "inverse_simpson_effective_semantic_count_exact": _fraction_text(
                Fraction(sample_size * sample_size, sum_squares)
            ),
            "inverse_simpson_sum_squared_multiplicities": sum_squares,
        },
        "checks": checks,
        "resource_ceilings": ceilings,
        "forbidden_promotions": protocol["forbidden_promotions"],
        "adjacent_rows_left_open": [
            "Scale to at least 10^8 candidates or justify an equivalent effective coverage method.",
            "Measure reachable fraction under each developmental/search law.",
        ],
    }
    result_bytes = json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    committed_footprint = sum(
        path.stat().st_size for path in HERE.iterdir() if path.is_file()
    ) + len(result_bytes)
    if committed_footprint > ceilings["committed_evidence_bytes"]:
        raise RuntimeError("committed evidence footprint exceeds the frozen ceiling")
    result["execution"]["committed_evidence_bytes_after_result"] = committed_footprint
    atomic_write(result_path, json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--result", type=Path, default=HERE / "RESULT_V1.json")
    args = parser.parse_args()
    result = execute_registered(args.run_dir.resolve(), args.result.resolve())
    print(json.dumps({
        "verdict": result["verdict"],
        "generated": result["execution"]["generated_count"],
        "elapsed_seconds": result["execution"]["elapsed_seconds"],
        "peak_rss_bytes": result["execution"]["peak_rss_bytes"],
        "result": str(args.result.resolve()),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
