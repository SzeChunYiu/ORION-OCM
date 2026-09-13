#!/usr/bin/env python3
"""Portable static replay; frozen V1 experiment and records remain unchanged."""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from opcode_sources_v1 import parent, sha
from opcode_revival_v1 import CELLS, FREEZE, verify_freeze
from opcode_witness_v1 import expectation, inspect_calls


def audit():
    frozen = verify_freeze()
    module = parent()
    expected = {cid: expectation(row["fn"]) for cid, row in module.CANDIDATES.items()}
    evidence, totals = [], {v: {"frames": 0, "complete": 0, "events": 0} for v in ("original", "repaired")}
    defects, pids = [], set()
    first_use_pattern = True
    recorded_script = None
    for variant, initial in CELLS:
        stem = f"{variant}_{initial}"
        packet_path = HERE / "raw" / f"{stem}_execution.json"
        execution = json.loads(packet_path.read_text())
        attempt = json.loads((HERE / "raw" / f"{stem}_attempt.json").read_text())
        if (attempt["variant"], attempt["initial_order"]) != (variant, initial):
            raise ValueError("attempt identity mismatch")
        if attempt["freeze_sha256"] != sha(FREEZE):
            raise ValueError("attempt freeze mismatch")
        if execution["returncode"] != 0:
            raise ValueError(f"{stem}: child failed: {execution['stderr']}")
        command = execution["command"]
        if type(command) is not list or len(command) != 7 or not isinstance(command[3], str):
            raise ValueError("malformed recorded child command")
        script = Path(command[3])
        if not script.is_absolute() or script.name != "opcode_revival_v1.py":
            raise ValueError("unexpected recorded script path")
        if recorded_script is None:
            recorded_script = str(script)
        if str(script) != recorded_script:
            raise ValueError("cells used different recorded script paths")
        expected_command = [frozen["environment"]["executable"], "-I", "-B",
                            recorded_script, "--child", variant, initial]
        if command != expected_command:
            raise ValueError("unexpected child command")
        packet = json.loads(execution["stdout"])
        if packet["pid"] in pids:
            raise ValueError("fresh process identities are not distinct")
        pids.add(packet["pid"])
        if packet["environment"] != frozen["environment"]:
            raise ValueError("recorded host/interpreter envelope differs")
        if packet["benchmark_or_timing_calls"] != 0:
            raise ValueError("outside registered no-timing scope")
        if (packet["variant"], packet["initial_order"]) != (variant, initial):
            raise ValueError("cell identity mismatch")
        if (packet["freeze_sha256"] != sha(FREEZE) or
                packet["environment"]["binary_sha256"] != frozen["environment"]["binary_sha256"]):
            raise ValueError("cell provenance mismatch")
        if packet["expectations"] != expected or packet["inputs"] != [list(x) for x in module.INPUTS]:
            raise ValueError("native disassembly/input witness mismatch")
        ids = list(module.CANDIDATES)
        if initial == "reverse":
            ids.reverse()
        scheduled = [(p, j, cid) for p, order in enumerate((ids, list(reversed(ids))))
                     for j, cid in enumerate(order)]
        if [(r["pass_index"], r["position"], r["candidate"]) for r in packet["rows"]] != scheduled:
            raise ValueError("missing/reordered pass rows")
        for row in packet["rows"]:
            if "exception" in row:
                raise ValueError(f"{stem}: recorded collector exception: {row['exception']}")
            result = inspect_calls(row["calls"], expected[row["candidate"]], module.INPUTS)
            if result != row["validation"]:
                raise ValueError("declared validation differs from recomputation")
            if variant == "original":
                if row["pass_index"] == 0:
                    first = row["calls"][0]
                    first_use_pattern &= (result["errors"] == ["frame 0: offset sequence"]
                                          and first["opcode_offsets"] == [])
                else:
                    first_use_pattern &= not result["errors"]
            totals[variant]["frames"] += len(row["calls"])
            totals[variant]["complete"] += result["complete_frames"]
            totals[variant]["events"] += result["events"]
            if result["errors"]:
                defects.append({"cell": stem, "pass": row["pass_index"],
                                "candidate": row["candidate"], "errors": result["errors"]})
        evidence.append({"cell": stem, "execution_sha256": sha(packet_path),
                         "attempt_sha256": sha(HERE / "raw" / f"{stem}_attempt.json")})
    repaired_ok = totals["repaired"]["complete"] == totals["repaired"]["frames"] == 128
    original_loss = totals["original"]["complete"] < totals["original"]["frames"] == 128
    return {"schema": "opcode-instrument-revival-v2", "freeze_sha256": sha(FREEZE),
            "terminal": ("REGISTERED_OPCODE_REPAIR_GREEN" if repaired_ok and original_loss
                         else "REGISTERED_OPCODE_REVIVAL_NOT_ESTABLISHED"),
            "totals": totals, "original_or_repaired_failures": defects, "evidence": evidence,
            "original_fresh_code_first_call_only_loss": bool(first_use_pattern),
            "scope": "registered exact interpreter, four frozen straight-line candidate bodies",
            "static_audit_source_sha256": sha(Path(__file__).resolve()),
            "historical_receipt_sha256": sha(HERE / "OPCODE_REVIVAL_RECEIPT_V1.json"),
            "recorded_execution_script": recorded_script,
            "benchmark_or_timing_calls": 0}


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, sort_keys=True, indent=2))
    if result["terminal"] != "REGISTERED_OPCODE_REPAIR_GREEN":
        raise SystemExit(2)
