#!/usr/bin/env python3
"""Materialize the exact aggregate semantic histogram from chained receipts."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import argparse
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_primary():
    path = HERE / "hundred_million_census_v1.py"
    spec = importlib.util.spec_from_file_location("gmi833_hm_materializer_parent", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load receipt validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def materialize(receipts_dir: Path, result_path: Path, output_path: Path) -> dict[str, object]:
    primary = load_primary()
    result = json.loads(result_path.read_bytes())
    previous = "00" * 32
    histogram: Counter[str] = Counter()
    count = 0
    receipt_count = 0
    for receipt_path in sorted(receipts_dir.glob("*.json")):
        receipt = json.loads(receipt_path.read_bytes())
        parsed = primary.verify_receipt(receipt, previous)
        previous = receipt["chain_sha256"]
        histogram.update({str(key): int(value) for key, value in parsed["histogram"].items()})
        count += int(parsed["count"])
        receipt_count += 1
    if previous != result["execution"]["terminal_chunk_chain_sha256"]:
        raise RuntimeError("terminal receipt chain disagrees with result")
    if count != result["execution"]["candidate_count"] or sum(histogram.values()) != count:
        raise RuntimeError("materialized histogram total disagrees with result")
    exact_histogram = dict(sorted(histogram.items()))
    histogram_sha = sha256(primary.canonical_bytes(exact_histogram)).hexdigest()
    if histogram_sha != result["semantic_coverage"]["complete_semantic_histogram_sha256"]:
        raise RuntimeError("materialized histogram digest disagrees with result")
    artifact = {
        "schema": "GMI833HundredMillionSemanticHistogramV1",
        "source_issue": 1008,
        "source_pr": 1009,
        "scope": "G0-fin-v1; cumulative B=(5,1); inputs (), (0,), (1,); step cap 6",
        "candidate_count": count,
        "semantic_class_count": len(exact_histogram),
        "receipt_count": receipt_count,
        "terminal_chunk_chain_sha256": previous,
        "histogram_sha256": histogram_sha,
        "packed_key_schema": "three colon-separated injective protected-observation integers; see independent_oracle_v1.py",
        "histogram": exact_histogram,
    }
    output_path.write_bytes(json.dumps(artifact, indent=2, sort_keys=True).encode("ascii") + b"\n")
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = materialize(args.receipts, args.result, args.output)
    print(json.dumps({key: artifact[key] for key in ("candidate_count", "semantic_class_count", "receipt_count", "histogram_sha256")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
