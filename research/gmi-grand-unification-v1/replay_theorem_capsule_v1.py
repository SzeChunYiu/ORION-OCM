#!/usr/bin/env python3
"""Replay the registered finite checks; this is not a proof of Grand GMI.

The inventory is reviewed evidence, not a trust root against a malicious change to
both code and its inventory. It binds the checker sources, their local JSON inputs,
and frozen complete outputs so that a stale green label cannot pass as a replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
INVENTORY = "THEOREM_REPLAY_INVENTORY_V1.json"
SCHEMA = "grand-gmi-theorem-replay-inventory-v1"
CLAIM_CEILING = "registered finite executable checks only; no universal theorem or empirical closure"
EXTERNAL_DOCUMENT_DEPENDENCIES = {
    "grand_gmi_operational_reachability_checks_v1.py": (
        "research/machine-intelligence-morphogenesis-v1/GMI_OPERATIONAL_COMPLETENESS_THEOREM_V1.md",
    ),
    "grand_gmi_interactive_cut_scope_checks_v1.py": (
        "research/machine-intelligence-morphogenesis-v1/GMI_OPERATIONAL_COMPLETENESS_THEOREM_V1.md",
    ),
}
EXTERNAL_CONTROL_DEPENDENCIES = {
    "nn_nonnn_point_parity3_experiment_v4.py": (
        ".github/workflows/grand-gmi-nn-nonnn-point-parity3-v4.yml",
    ),
    "nn_nonnn_point_parity3_experiment_v3.py": (
        ".github/workflows/grand-gmi-nn-nonnn-point-parity3-v3.yml",
    ),
    "replay_theorem_capsule_v1.py": (
        ".github/workflows/grand-gmi-theorem-capsule.yml",
    ),
    "nn_nonnn_point_parity3_experiment_v1.py": (
        ".github/workflows/grand-gmi-nn-nonnn-point-parity3.yml",
    ),
    "nn_nonnn_point_parity3_experiment_v2.py": (
        ".github/workflows/grand-gmi-nn-nonnn-point-parity3-v2.yml",
    ),
}


class ReplayError(ValueError):
    """The registered capsule cannot be reproduced without changing evidence."""


def require(condition, message):
    if not condition:
        raise ReplayError(message)


def strict_json(text, label="JSON"):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"{label}: duplicate key {key!r}")
            result[key] = value
        return result

    def constant(value):
        raise ReplayError(f"{label}: non-finite value {value}")

    try:
        result = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, TypeError) as exc:
        raise ReplayError(f"{label}: invalid JSON: {exc}") from exc
    require(type(result) is dict, f"{label}: expected an object")
    # This also catches an overflowing exponent (for example 1e999).
    canonical(result)
    return result


def canonical(data):
    try:
        return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise ReplayError(f"not finite JSON: {exc}") from exc


def file_path(root, name):
    require(type(name) is str and name != "", "empty or non-string path")
    path = Path(name)
    require(not path.is_absolute() and all(x not in (".", "..") for x in path.parts),
            f"non-local path: {name}")
    require(path.as_posix() == name, f"non-canonical path: {name}")
    target = root / path
    require(target.is_file(), f"missing file: {name}")
    require(all(not parent.is_symlink() for parent in (target, *target.parents)
                if parent != root.parent), f"symlink in capsule path: {name}")
    require(target.resolve().is_relative_to(root.resolve()), f"escaped capsule path: {name}")
    return target


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind_file(root, name, digest):
    require(type(digest) is str and len(digest) == 64 and
            all(c in "0123456789abcdef" for c in digest), f"bad digest for {name}")
    path = file_path(root, name)
    require(sha256(path) == digest, f"source or evidence changed: {name}")
    return path


def load_inventory(root):
    root = Path(root).resolve()
    data = strict_json(file_path(root, INVENTORY).read_text(encoding="utf-8"), INVENTORY)
    require(data.get("schema") == SCHEMA, "unsupported replay inventory schema")
    require(data.get("claim_ceiling") == CLAIM_CEILING, "replay claim ceiling changed")
    entries = data.get("checkers")
    require(type(entries) is list and bool(entries), "missing checker inventory")
    names = [row.get("checker") for row in entries if type(row) is dict]
    require(len(names) == len(entries) and all(type(x) is str for x in names),
            "malformed checker entry")
    require(len(set(names)) == len(names), "duplicate checker entry")
    discovered = {p.name for p in root.glob("grand_gmi*checks*.py")}
    require(set(names) == discovered,
            f"checker coverage changed: missing={sorted(discovered-set(names))}, "
            f"unknown={sorted(set(names)-discovered)}")
    aggregate = [r for r in entries if r.get("kind") == "aggregate"]
    aggregate_names = {r["checker"] for r in aggregate}
    require(aggregate_names == ({"grand_gmi_master_checks_v1.py"} & discovered),
            "only the master checker may be classified as aggregate")
    for row in entries:
        require(row.get("kind") in ("finite_check", "aggregate"), "unknown checker kind")
        require(type(row.get("terminal")) is str and bool(row["terminal"]), "missing terminal")
        require(type(row.get("historical_receipts")) is list, "missing historical receipt classification")
    controls = data.get("control_sources")
    inputs = data.get("inputs")
    records = data.get("non_replayed_records")
    require(type(controls) is dict and type(inputs) is dict and type(records) is list,
            "missing control, input, or non-replayed record inventory")
    discovered_controls = {p.name for p in root.glob("*.py")
                           if p.name not in names and not p.name.startswith("test_")}
    require(set(controls) == discovered_controls, "unclassified or missing control source")
    receipt_names = set()
    for row in entries:
        active = row.get("receipt")
        require(type(active) is str and active not in receipt_names, "duplicate active receipt")
        receipt_names.add(active)
        for old in row["historical_receipts"]:
            require(type(old) is dict and old.get("status") == "HISTORICAL_SUPERSEDED_FOR_REPLAY"
                    and type(old.get("reason")) is str and bool(old["reason"]),
                    "historical receipt lacks an explicit supersession reason")
            require(old.get("path") not in receipt_names, "duplicate historical receipt")
            receipt_names.add(old["path"])
    for row in records:
        require(type(row) is dict and row.get("status") == "PREREGISTRATION_ONLY_NOT_MEASUREMENT"
                and type(row.get("reason")) is str and bool(row["reason"]),
                "non-replayed record lacks a bounded classification")
        require(row.get("path") not in receipt_names, "duplicate non-replayed receipt")
        receipt_names.add(row["path"])
    discovered_receipts = {p.relative_to(root).as_posix() for p in root.rglob("*RECEIPT*.json")}
    require(receipt_names == discovered_receipts, "unclassified or missing frozen receipt")
    discovered_inputs = {p.name for pattern in ("*.json", "*.md") for p in root.glob(pattern)
                         if p.name not in receipt_names and p.name != INVENTORY}
    require(set(inputs) == discovered_inputs, "unclassified or missing local document/JSON input")
    for name, digest in {**controls, **inputs}.items():
        bind_file(root, name, digest)
    external = data.get("external_documents", {})
    expected_external = {name for checker in names
                         for name in EXTERNAL_DOCUMENT_DEPENDENCIES.get(checker, ())}
    require(type(external) is dict and set(external) == expected_external,
            "unclassified or missing external normative document")
    repository = root.parent.parent
    for name, digest in external.items():
        require(Path(name).suffix == ".md", "external dependency must be normative Markdown")
        bind_file(repository, name, digest)
    external_controls = data.get("external_controls", {})
    expected_controls = {name for source in controls
                         for name in EXTERNAL_CONTROL_DEPENDENCIES.get(source, ())}
    require(type(external_controls) is dict and set(external_controls) == expected_controls,
            "unclassified or missing external control workflow")
    for name, digest in external_controls.items():
        bind_file(repository, name, digest)
    for row in entries:
        bind_file(root, row["checker"], row.get("source_sha256"))
        for old in row["historical_receipts"]:
            bind_file(root, old["path"], old.get("sha256"))
    for row in records:
        record_path = bind_file(root, row["path"], row.get("sha256"))
        record = strict_json(record_path.read_text(encoding="utf-8"), row["path"])
        require(record.get("terminal") == "GRAND_GMI_NN_NONNN_POINT_PARITY3_PREREGISTRATION_FROZEN"
                and record.get("protected_resource_measurement_executed_in_frozen_receipt") is False
                and record.get("protected_resource_measurement_executed", False) is False,
                "non-replayed record is not a preregistration-only receipt")
    return data


def execute_checker(root, row, timeout=60):
    source = bind_file(root, row["checker"], row["source_sha256"])
    try:
        # -I ignores PYTHONOPTIMIZE and Python path injection. No -O is inherited
        # from the parent: legacy finite assertions must actually execute. -B
        # alone still reads ambient .pyc files. An empty private cache prefix
        # makes imported local modules execute the pinned source bytes instead.
        with tempfile.TemporaryDirectory(prefix="grand-gmi-replay-pycache-") as cache:
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-X", f"pycache_prefix={cache}", str(source)],
                cwd=root, capture_output=True, text=True, timeout=timeout,
            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReplayError(f"checker did not complete: {row['checker']}: {exc}") from exc
    require(result.returncode == 0,
            f"checker failed: {row['checker']} (exit {result.returncode}): {result.stderr[-1000:]}")
    require(result.stderr == "", f"checker emitted stderr: {row['checker']}")
    bind_file(root, row["checker"], row["source_sha256"])
    observed = strict_json(result.stdout, row["checker"])
    require(observed.get("terminal") == row["terminal"], f"wrong terminal: {row['checker']}")
    return observed


def replay(root=HERE, include_aggregate=True):
    root = Path(root).resolve()
    data = load_inventory(root)
    observed = {}
    payload_hashes = {}
    for row in data["checkers"]:
        if row["kind"] == "aggregate" and not include_aggregate:
            continue
        frozen = bind_file(root, row["receipt"], row.get("receipt_sha256"))
        expected = strict_json(frozen.read_text(encoding="utf-8"), row["receipt"])
        require(expected.get("terminal") == row["terminal"], f"wrong frozen terminal: {row['receipt']}")
        # The aggregate executes all leaves sequentially; it needs its own total
        # budget while each individual finite checker retains the 60-second cap.
        current = execute_checker(root, row, timeout=300 if row["kind"] == "aggregate" else 60)
        require(canonical(current) == canonical(expected),
                f"full receipt differs from fresh checker output: {row['receipt']}")
        bind_file(root, row["receipt"], row["receipt_sha256"])
        observed[row["receipt"]] = current["terminal"]
        payload_hashes[row["checker"]] = hashlib.sha256(canonical(current).encode()).hexdigest()
    require(canonical(load_inventory(root)) == canonical(data), "inventory changed during replay")
    # A later checker must not invalidate an earlier frozen receipt after that
    # entry passed. Rebind the whole selected receipt set before returning green.
    for row in data["checkers"]:
        if row["kind"] != "aggregate" or include_aggregate:
            bind_file(root, row["receipt"], row["receipt_sha256"])
    return {
        "receipts": len(observed),
        "terminals": observed,
        "fresh_payload_sha256": payload_hashes,
        "all_green": True,
        "verification": "FULL_PAYLOAD_SOURCE_BOUND_REPLAY",
        "claim_ceiling": CLAIM_CEILING,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HERE)
    args = parser.parse_args()
    try:
        result = replay(args.root)
    except (ReplayError, OSError) as exc:
        print(f"THEOREM_CAPSULE_REPLAY_FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"terminal": "GRAND_GMI_FINITE_CAPSULE_REPLAY_ALL_GREEN", **result},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
