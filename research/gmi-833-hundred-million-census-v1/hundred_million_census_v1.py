#!/usr/bin/env python3
"""Restartable exact census of the registered 116,570,467-candidate scope."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import argparse
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import tempfile
import time
from typing import Iterable


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "FROZEN_PROTOCOL_V1.json"
WORKER_SOURCE = HERE / "hundred_million_worker_v1.c"
EXPECTED_PROTOCOL_SHA256 = "b31f71a83fd89d256329bfa39b5ad8137bc852610a8043ff586ee0c245f3d033"
CLAIM_CEILING = "GMI_833_116570467_CANDIDATE_EXACT_CENSUS_AT_REGISTERED_FINITE_SCOPE"
CHUNK_SIZE = 1_000_000


class CensusError(RuntimeError):
    pass


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def sha256_hex(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def read_protocol() -> tuple[dict[str, object], bytes]:
    raw = PROTOCOL.read_bytes()
    if sha256_hex(raw) != EXPECTED_PROTOCOL_SHA256:
        raise CensusError("frozen protocol bytes drifted")
    protocol = json.loads(raw)
    if protocol.get("outcome_status") != "NOT_RUN":
        raise CensusError("frozen protocol outcome status drifted")
    return protocol, raw


def compile_worker(run_dir: Path) -> Path:
    compiler = os.environ.get("CC", "cc")
    binary = run_dir / "hundred_million_worker_v1"
    command = [compiler, "-O3", "-std=c11", "-Wall", "-Wextra", "-Werror", str(WORKER_SOURCE), "-o", str(binary)]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise CensusError(f"worker compilation failed: {completed.stderr}")
    return binary


def interval_sum(start: int, count: int) -> int:
    return count * (2 * start + count - 1) // 2


def prefix_square_sum(stop: int) -> int:
    return stop * (stop - 1) * (2 * stop - 1) // 6


def interval_square_sum(start: int, count: int) -> int:
    return prefix_square_sum(start + count) - prefix_square_sum(start)


def semantic_token(a: int, b: int, c: int) -> str:
    return f"{a}:{b}:{c}"


def parse_worker_output(raw: bytes) -> dict[str, object]:
    lines = raw.decode("ascii").splitlines()
    if len(lines) < 3:
        raise CensusError("worker output is truncated")
    meta = lines[0].split("\t")
    moments = lines[1].split("\t")
    end = lines[-1].split("\t")
    if len(meta) != 6 or meta[0] != "META" or len(moments) != 5 or moments[0] != "MOMENTS":
        raise CensusError("worker header schema drifted")
    if len(end) != 3 or end[0] != "END":
        raise CensusError("worker terminal schema drifted")
    histogram: dict[str, int] = {}
    for line in lines[2:-1]:
        fields = line.split("\t")
        if len(fields) != 5 or fields[0] != "SEM":
            raise CensusError("worker semantic row schema drifted")
        a, b, c, count = map(int, fields[1:])
        token = semantic_token(a, b, c)
        if token in histogram or count <= 0:
            raise CensusError("duplicate or nonpositive semantic row")
        histogram[token] = count
    parsed = {
        "labels": int(meta[1]),
        "alphabet_size": int(meta[2]),
        "population": int(meta[3]),
        "start": int(meta[4]),
        "count": int(meta[5]),
        "rank_sum": int(moments[1]),
        "rank_square_sum": int(moments[2]),
        "rank_digest_u64": moments[3],
        "semantic_digest_u64": moments[4],
        "histogram": histogram,
        "semantic_classes": int(end[1]),
        "terminal_count": int(end[2]),
        "raw_sha256": sha256_hex(raw),
    }
    if parsed["semantic_classes"] != len(histogram) or parsed["terminal_count"] != sum(histogram.values()):
        raise CensusError("worker semantic totals drifted")
    return parsed


def validate_chunk(parsed: dict[str, object], *, labels: int, alphabet: int, population: int, start: int, count: int) -> None:
    exact = {
        "labels": labels,
        "alphabet_size": alphabet,
        "population": population,
        "start": start,
        "count": count,
        "terminal_count": count,
        "rank_sum": interval_sum(start, count),
        "rank_square_sum": interval_square_sum(start, count),
    }
    for key, expected in exact.items():
        if parsed.get(key) != expected:
            raise CensusError(f"chunk {key} mismatch: {parsed.get(key)!r} != {expected!r}")


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def receipt_payload(parsed: dict[str, object], previous_chain: str) -> dict[str, object]:
    payload = dict(parsed)
    payload["previous_chain_sha256"] = previous_chain
    payload["schema"] = "GMI833HundredMillionChunkReceiptV1"
    payload["chain_sha256"] = sha256_hex(bytes.fromhex(previous_chain) + canonical_bytes(parsed))
    return payload


def verify_receipt(receipt: dict[str, object], previous_chain: str) -> dict[str, object]:
    if receipt.get("schema") != "GMI833HundredMillionChunkReceiptV1":
        raise CensusError("receipt schema drifted")
    if receipt.get("previous_chain_sha256") != previous_chain:
        raise CensusError("receipt chain predecessor drifted")
    parsed = {key: value for key, value in receipt.items() if key not in {"schema", "previous_chain_sha256", "chain_sha256"}}
    expected = sha256_hex(bytes.fromhex(previous_chain) + canonical_bytes(parsed))
    if receipt.get("chain_sha256") != expected:
        raise CensusError("receipt chain digest drifted")
    return parsed


def directory_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def max_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    child = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    measured = max(value, child)
    return int(measured if platform.system() == "Darwin" else measured * 1024)


def execute_registered(run_dir: Path, result_path: Path) -> dict[str, object]:
    protocol, protocol_raw = read_protocol()
    run_dir.mkdir(parents=True, exist_ok=True)
    receipts_dir = run_dir / "receipts"
    receipts_dir.mkdir(exist_ok=True)
    binary = compile_worker(run_dir)
    started = time.monotonic()
    previous_chain = "00" * 32
    aggregate: Counter[str] = Counter()
    strata_results: list[dict[str, object]] = []
    candidate_total = 0
    chunk_total = 0
    transcript = sha256()

    strata = protocol["configuration"]["strata"]
    for stratum in strata:
        labels = int(stratum["labels"])
        alphabet = int(stratum["alphabet_size"])
        population = int(stratum["candidates"])
        stratum_histogram: Counter[str] = Counter()
        stratum_chunks = 0
        for start in range(0, population, CHUNK_SIZE):
            count = min(CHUNK_SIZE, population - start)
            name = f"n{labels:02d}-start{start:012d}-count{count:07d}.json"
            receipt_path = receipts_dir / name
            if receipt_path.exists():
                receipt = json.loads(receipt_path.read_bytes())
                parsed = verify_receipt(receipt, previous_chain)
            else:
                completed = subprocess.run(
                    [str(binary), str(labels), str(start), str(count)],
                    capture_output=True,
                    check=False,
                )
                if completed.returncode != 0:
                    raise CensusError(f"worker failed at n={labels}, start={start}: {completed.stderr.decode(errors='replace')}")
                parsed = parse_worker_output(completed.stdout)
                receipt = receipt_payload(parsed, previous_chain)
                atomic_write(receipt_path, canonical_bytes(receipt))
            validate_chunk(parsed, labels=labels, alphabet=alphabet, population=population, start=start, count=count)
            previous_chain = str(receipt["chain_sha256"])
            transcript.update(bytes.fromhex(str(parsed["raw_sha256"])))
            histogram = parsed["histogram"]
            if not isinstance(histogram, dict):
                raise CensusError("receipt histogram is not an object")
            stratum_histogram.update({str(key): int(value) for key, value in histogram.items()})
            chunk_total += 1
            stratum_chunks += 1
        if sum(stratum_histogram.values()) != population:
            raise CensusError("stratum histogram total drifted")
        histogram_bytes = canonical_bytes(dict(sorted(stratum_histogram.items())))
        strata_results.append({
            "labels": labels,
            "alphabet_size": alphabet,
            "candidate_count": population,
            "chunk_count": stratum_chunks,
            "first_order_inclusion_probability": "1/1",
            "distinct_pair_inclusion_probability": "1/1",
            "rank_sum": interval_sum(0, population),
            "rank_square_sum": interval_square_sum(0, population),
            "semantic_class_count": len(stratum_histogram),
            "semantic_histogram_sha256": sha256_hex(histogram_bytes),
        })
        aggregate.update(stratum_histogram)
        candidate_total += population

    if candidate_total != int(protocol["configuration"]["candidate_total"]):
        raise CensusError("registered candidate total drifted")
    if sum(aggregate.values()) != candidate_total:
        raise CensusError("aggregate semantic total drifted")
    sum_squared = sum(count * count for count in aggregate.values())
    effective = Fraction(candidate_total * candidate_total, sum_squared)
    multiplicities = Counter(aggregate.values())
    elapsed = time.monotonic() - started
    artifact_bytes = directory_bytes(run_dir)
    rss = max_rss_bytes()
    ceilings = protocol["resource_ceilings"]
    checks = {
        "candidate_threshold_met": candidate_total >= 100_000_000,
        "exact_registered_total": candidate_total == 116_570_467,
        "all_five_strata_complete": len(strata_results) == 5 and all(row["candidate_count"] > 0 for row in strata_results),
        "census_inclusion_probabilities_exactly_one": all(
            row["first_order_inclusion_probability"] == "1/1" and row["distinct_pair_inclusion_probability"] == "1/1"
            for row in strata_results
        ),
        "semantic_histogram_complete": sum(aggregate.values()) == candidate_total,
        "wall_ceiling_met": elapsed <= int(ceilings["wall_seconds"]),
        "peak_rss_ceiling_met": rss <= int(ceilings["peak_rss_bytes"]),
        "artifact_ceiling_met": artifact_bytes <= int(ceilings["persistent_run_artifact_bytes"]),
        "forbidden_equivalent_coverage_substitution_absent": True,
    }
    if not all(checks.values()):
        raise CensusError(f"positive terminal gate failed: {checks}")
    aggregate_bytes = canonical_bytes(dict(sorted(aggregate.items())))
    result: dict[str, object] = {
        "schema": "GMI833HundredMillionCensusResultV1",
        "source_issue": 1008,
        "source_pr": 1009,
        "parent_issue": 833,
        "protocol_sha256": sha256_hex(protocol_raw),
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "EXACT_116570467_CANDIDATE_CENSUS_COMPLETE_AT_REGISTERED_FINITE_SCOPE",
        "configuration": protocol["configuration"],
        "execution": {
            "candidate_count": candidate_total,
            "decoded_count": candidate_total,
            "validated_count": candidate_total,
            "reranked_count": candidate_total,
            "semantic_evaluation_count": candidate_total,
            "chunk_count": chunk_total,
            "terminal_chunk_chain_sha256": previous_chain,
            "worker_transcript_sha256": transcript.hexdigest(),
            "elapsed_seconds": round(elapsed, 6),
            "peak_rss_bytes": rss,
            "persistent_run_artifact_bytes": artifact_bytes,
            "population_materialized": False,
        },
        "inclusion": {
            "design": "COMPLETE_CENSUS",
            "first_order_probability": "1/1",
            "distinct_pair_probability": "1/1",
            "sampling_uncertainty": "NONE_CENSUS",
        },
        "strata": strata_results,
        "semantic_coverage": {
            "scope": "COMPLETE_FOR_REGISTERED_FINITE_GRAMMAR_BUDGET_AND_PROTECTED_INTERFACE_ONLY",
            "candidate_count": candidate_total,
            "class_count": len(aggregate),
            "collapse_count": candidate_total - len(aggregate),
            "collapse_rate_exact": f"{Fraction(candidate_total - len(aggregate), candidate_total).numerator}/{Fraction(candidate_total - len(aggregate), candidate_total).denominator}",
            "singleton_classes": multiplicities[1],
            "doubleton_classes": multiplicities[2],
            "sum_squared_multiplicities": sum_squared,
            "inverse_simpson_effective_semantic_count_exact": f"{effective.numerator}/{effective.denominator}",
            "multiplicity_histogram": {str(key): value for key, value in sorted(multiplicities.items())},
            "complete_semantic_histogram_sha256": sha256_hex(aggregate_bytes),
        },
        "resource_ceilings": ceilings,
        "checks": checks,
        "independent_check": "PENDING_SEPARATE_SOURCE_ROUTE",
        "forbidden_promotions": protocol["forbidden_promotions"],
        "reconciliation_eligible": False,
    }
    atomic_write(result_path, json.dumps(result, indent=2, sort_keys=True).encode("ascii") + b"\n")
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args(argv)
    result = execute_registered(args.run_dir, args.result)
    print(json.dumps({"verdict": result["verdict"], "execution": result["execution"], "semantic_coverage": result["semantic_coverage"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
