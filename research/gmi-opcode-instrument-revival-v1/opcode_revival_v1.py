#!/usr/bin/env python3
"""Four registered fresh-process opcode controls; no benchmark entry point."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from opcode_sources_v1 import (COMMIT, PARENT, PARENT_SHA, collector, collector_source,
                               parent, require_interpreter, sha)
from opcode_witness_v1 import expectation, inspect_calls

FREEZE = HERE / "OPCODE_REVIVAL_FREEZE_V1.json"
CELLS = [(variant, order) for variant in ("original", "repaired")
         for order in ("forward", "reverse")]
CONTROLS = ("opcode_sources_v1.py", "opcode_witness_v1.py", "opcode_revival_v1.py",
            "opcode_audit_v1.py", "test_opcode_revival_v1.py", "PREREGISTRATION_V1.md",
            "raw/frozen_parent_v5.py")


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def exclusive(path, data):
    with Path(path).open("x") as out:
        json.dump(data, out, sort_keys=True, indent=2)
        out.write("\n")


def environment():
    return {"python": sys.version, "executable": str(Path(sys.executable).resolve()),
            "binary_sha256": sha(sys.executable), "platform": platform.platform(),
            "machine_id_sha256": sha("/etc/machine-id")}


def freeze():
    require_interpreter()
    parent()  # Definitions/imports only; no candidate calls.
    record = {"schema": "opcode-revival-freeze-v1", "registered_utc": utc(),
              "upstream_commit": COMMIT, "upstream_harness_sha256": PARENT_SHA,
              "environment": environment(), "cells": CELLS,
              "source_sha256": {name: sha(HERE / name) for name in CONTROLS},
              "collector_sha256": {v: hashlib.sha256(
                  collector_source(v == "repaired").encode()).hexdigest()
                  for v in ("original", "repaired")},
              "pass_orders": "initial declared order, then its reverse",
              "candidate_invocations_per_cell": 64,
              "benchmark_or_timing_calls": 0}
    exclusive(FREEZE, record)
    return record


def verify_freeze():
    require_interpreter()
    record = json.loads(FREEZE.read_text())
    for name in CONTROLS:
        if record["source_sha256"].get(name) != sha(HERE / name):
            raise ValueError("registered source changed: " + name)
    if record["environment"]["binary_sha256"] != sha(sys.executable):
        raise ValueError("registered interpreter changed")
    if record["cells"] != [list(cell) for cell in CELLS]:
        raise ValueError("registered schedule changed")
    return record


def child(variant, initial):
    verify_freeze()
    module = parent()
    ids = list(module.CANDIDATES)
    if initial == "reverse":
        ids.reverse()
    trace = collector(module, variant)
    # Disassembly inspects definitions; it does not execute candidate bodies.
    expected = {cid: expectation(row["fn"]) for cid, row in module.CANDIDATES.items()}
    rows = []
    for pass_index, order in enumerate((ids, list(reversed(ids)))):
        for position, cid in enumerate(order):
            row = {"pass_index": pass_index, "position": position, "candidate": cid}
            try:
                row["calls"] = trace(module.CANDIDATES[cid]["fn"])
                row["validation"] = inspect_calls(row["calls"], expected[cid], module.INPUTS)
            except Exception as exc:
                row["exception"] = {"type": type(exc).__name__, "message": str(exc)}
            rows.append(row)  # Never discard an invalid first pass or stop at its failure.
    return {"schema": "opcode-revival-cell-v1", "variant": variant, "initial_order": initial,
            "pid": os.getpid(), "environment": environment(), "freeze_sha256": sha(FREEZE),
            "inputs": module.INPUTS, "expectations": expected, "rows": rows,
            "benchmark_or_timing_calls": 0}


def run():
    verify_freeze()
    for variant, order in CELLS:
        stem = f"{variant}_{order}"
        # Exclusive reservation precedes invocation; no successful or failed retry overwrite.
        exclusive(HERE / "raw" / f"{stem}_attempt.json",
                  {"schema": "opcode-revival-attempt-v1", "variant": variant,
                   "initial_order": order, "reserved_utc": utc(), "freeze_sha256": sha(FREEZE)})
        command = [str(Path(sys.executable).resolve()), "-I", "-B", str(Path(__file__).resolve()),
                   "--child", variant, order]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        output = {"command": command, "returncode": result.returncode,
                  "stdout": result.stdout, "stderr": result.stderr, "finished_utc": utc()}
        # Raw stdout includes every frame's offset list, even when validation fails.
        exclusive(HERE / "raw" / f"{stem}_execution.json", output)
    return {"raw_execution_packets": 4, "benchmark_or_timing_calls": 0}


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--run", action="store_true")
    group.add_argument("--child", nargs=2, choices=("original", "repaired", "forward", "reverse"))
    args = parser.parse_args()
    if args.freeze:
        result = freeze()
    elif args.run:
        result = run()
    else:
        if tuple(args.child) not in CELLS:
            raise ValueError("invalid cell")
        result = child(*args.child)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
