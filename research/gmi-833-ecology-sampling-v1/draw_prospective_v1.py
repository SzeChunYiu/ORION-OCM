#!/usr/bin/env python3
"""Create or verify the frozen prospective SRSWOR draw for Issue #982."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import secrets
from typing import Any, Dict, List, Mapping, Sequence


HERE = Path(__file__).resolve().parent
DRAW_PATH = HERE / "PROSPECTIVE_DRAW_V1.json"
POPULATION_SIZE = 1 << 17
SAMPLE_SIZE = 1 << 12
ISSUE = 982
SOURCE_PR = 985
FREEZE_COMMIT = "18615590d16af8c0e69e7e259dc2b96abe479832"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, separators=(",", ": ")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def reconstruct_ranks(offsets: Sequence[int], population_size: int = POPULATION_SIZE) -> List[int]:
    """Replay sparse partial Fisher--Yates from its exact offset transcript."""
    if type(population_size) is not int or population_size <= 0:
        raise ValueError("population_size must be a positive exact integer")
    if len(offsets) > population_size:
        raise ValueError("draw is larger than population")
    virtual: Dict[int, int] = {}
    ranks: List[int] = []
    for i, offset in enumerate(offsets):
        remaining = population_size - i
        if type(offset) is not int or offset < 0 or offset >= remaining:
            raise ValueError("draw offset is outside its frozen carrier")
        j = i + offset
        selected = virtual.get(j, j)
        virtual[j] = virtual.get(i, i)
        ranks.append(selected)
    if len(ranks) != len(set(ranks)):
        raise AssertionError("partial Fisher--Yates emitted a duplicate")
    return ranks


def create_receipt() -> Mapping[str, Any]:
    offsets = [secrets.randbelow(POPULATION_SIZE - i) for i in range(SAMPLE_SIZE)]
    ranks = reconstruct_ranks(offsets)
    return {
        "schema": "ProspectiveRegisteredEcologySRSWORV1",
        "issue": ISSUE,
        "source_pr": SOURCE_PR,
        "freeze_commit": FREEZE_COMMIT,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "entropy_source": "Python secrets.randbelow backed by the host operating-system CSPRNG",
        "entropy_boundary": "provenance statement; host entropy quality is not cryptographically proved here",
        "algorithm": "sparse_partial_fisher_yates_offsets_v1",
        "population_size": POPULATION_SIZE,
        "sample_size": SAMPLE_SIZE,
        "offsets": offsets,
        "sampled_ranks": ranks,
        "offsets_sha256": digest(offsets),
        "sampled_ranks_sha256": digest(ranks),
    }


def validate_receipt(receipt: Mapping[str, Any]) -> Mapping[str, Any]:
    required = {
        "schema",
        "issue",
        "source_pr",
        "freeze_commit",
        "generated_at_utc",
        "entropy_source",
        "entropy_boundary",
        "algorithm",
        "population_size",
        "sample_size",
        "offsets",
        "sampled_ranks",
        "offsets_sha256",
        "sampled_ranks_sha256",
    }
    if set(receipt) != required:
        raise ValueError("draw receipt fields differ from the frozen schema")
    if receipt["schema"] != "ProspectiveRegisteredEcologySRSWORV1":
        raise ValueError("wrong draw schema")
    if receipt["issue"] != ISSUE or receipt["source_pr"] != SOURCE_PR:
        raise ValueError("wrong issue or pull-request binding")
    if receipt["freeze_commit"] != FREEZE_COMMIT:
        raise ValueError("wrong freeze binding")
    if receipt["algorithm"] != "sparse_partial_fisher_yates_offsets_v1":
        raise ValueError("wrong sampling algorithm")
    if type(receipt["population_size"]) is not int or receipt["population_size"] != POPULATION_SIZE:
        raise ValueError("wrong population size")
    if type(receipt["sample_size"]) is not int or receipt["sample_size"] != SAMPLE_SIZE:
        raise ValueError("wrong sample size")
    offsets = receipt["offsets"]
    ranks = receipt["sampled_ranks"]
    if not isinstance(offsets, list) or not isinstance(ranks, list):
        raise ValueError("draw vectors must be lists")
    if len(offsets) != SAMPLE_SIZE or len(ranks) != SAMPLE_SIZE:
        raise ValueError("wrong draw-vector length")
    replayed = reconstruct_ranks(offsets)
    if replayed != ranks:
        raise ValueError("draw transcript does not replay")
    if any(type(rank) is not int or rank < 0 or rank >= POPULATION_SIZE for rank in ranks):
        raise ValueError("sample rank is outside the population")
    if digest(offsets) != receipt["offsets_sha256"] or digest(ranks) != receipt["sampled_ranks_sha256"]:
        raise ValueError("draw-vector digest mismatch")
    return {
        "valid": True,
        "population_size": POPULATION_SIZE,
        "sample_size": SAMPLE_SIZE,
        "distinct_ranks": len(set(ranks)),
        "offsets_sha256": receipt["offsets_sha256"],
        "sampled_ranks_sha256": receipt["sampled_ranks_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.generate == args.verify:
        parser.error("choose exactly one of --generate or --verify")
    if args.generate:
        if DRAW_PATH.exists():
            raise SystemExit("refusing to redraw or overwrite the prospective receipt")
        receipt = create_receipt()
        DRAW_PATH.write_bytes(canonical(receipt))
        print(json.dumps(validate_receipt(receipt), sort_keys=True))
        return 0
    receipt = json.loads(DRAW_PATH.read_text(encoding="utf-8"))
    print(json.dumps(validate_receipt(receipt), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
