#!/usr/bin/env python3
"""Prospective Grand-GMI NN/non-NN point experiment: exact parity-3.

The preregistration is NN_NONNN_POINT_PARITY3_PREREG_V1.json. This harness uses
only the Python standard library. It emits a complete JSON measurement packet.

Scope warning: any derived family terminal is only about the two frozen candidates,
the executed CPython 3.12 hosted-runner scope, and the registered resource coordinates.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from time import perf_counter_ns, process_time_ns

HERE = Path(__file__).resolve().parent
PREREG = HERE / "NN_NONNN_POINT_PARITY3_PREREG_V1.json"
INPUTS = tuple((a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1))
EXPECTED = tuple(a ^ b ^ c for a, b, c in INPUTS)


def neural_threshold_parity3(x: tuple[int, int, int]) -> int:
    """Four hidden affine-threshold minterm detectors plus one threshold output."""
    a, b, c = x
    h001 = int((-a - b + c) >= 1)
    h010 = int((-a + b - c) >= 1)
    h100 = int((a - b - c) >= 1)
    h111 = int((a + b + c) >= 3)
    return int((h001 + h010 + h100 + h111) >= 1)


def non_neural_xor_parity3(x: tuple[int, int, int]) -> int:
    """Direct non-neural Boolean program: two XOR operations."""
    a, b, c = x
    return (a ^ b) ^ c


CANDIDATES = {
    "N_THRESHOLD_DNF4_V1": {
        "family": "NEURAL",
        "fn": neural_threshold_parity3,
    },
    "X_XOR2_V1": {
        "family": "NON_NEURAL",
        "fn": non_neural_xor_parity3,
    },
}


def outputs(fn):
    return tuple(fn(x) for x in INPUTS)


def capability_record(candidate_id: str) -> dict:
    fn = CANDIDATES[candidate_id]["fn"]
    got = outputs(fn)
    correct = sum(int(a == b) for a, b in zip(got, EXPECTED))
    return {
        "candidate_id": candidate_id,
        "family": CANDIDATES[candidate_id]["family"],
        "outputs": list(got),
        "expected": list(EXPECTED),
        "correct": correct,
        "total": len(EXPECTED),
        "exact_gate_pass": correct == len(EXPECTED),
    }


def constant_zero_null_record() -> dict:
    got = tuple(0 for _ in INPUTS)
    correct = sum(int(a == b) for a, b in zip(got, EXPECTED))
    return {"outputs": list(got), "correct": correct, "total": len(EXPECTED)}


def count_candidate_opcodes(fn) -> int:
    """Count CPython opcode events inside exactly the candidate function frame."""
    target_code = fn.__code__
    count = 0

    def tracer(frame, event, arg):
        nonlocal count
        if event == "call" and frame.f_code is target_code:
            frame.f_trace_opcodes = True
            return tracer
        if event == "opcode" and frame.f_code is target_code:
            count += 1
        return tracer

    previous = sys.gettrace()
    if previous is not None:
        raise RuntimeError("refuse opcode measurement while another trace function is active")
    sys.settrace(tracer)
    try:
        for x in INPUTS:
            fn(x)
    finally:
        sys.settrace(None)
    return count


def warmup(fn, sweeps: int) -> int:
    checksum = 0
    for _ in range(sweeps):
        for x in INPUTS:
            checksum += fn(x)
    return checksum


def timed_block(fn, sweeps: int) -> dict:
    expected_checksum = sweeps * sum(EXPECTED)
    checksum = 0
    p0 = process_time_ns()
    w0 = perf_counter_ns()
    for _ in range(sweeps):
        for x in INPUTS:
            checksum += fn(x)
    w1 = perf_counter_ns()
    p1 = process_time_ns()
    if checksum != expected_checksum:
        raise AssertionError(f"timed block capability drift: {checksum=} {expected_checksum=}")
    return {
        "wall_block_ns": w1 - w0,
        "process_block_ns": p1 - p0,
        "checksum": checksum,
    }


def observed_box(opcodes: int, blocks: list[dict]) -> dict:
    walls = [row["wall_block_ns"] for row in blocks]
    procs = [row["process_block_ns"] for row in blocks]
    return {
        "python_opcode_count_per_full_domain_sweep": [opcodes, opcodes],
        "wall_block_ns": [min(walls), max(walls)],
        "process_block_ns": [min(procs), max(procs)],
    }


def robustly_dominates(box_a: dict, box_b: dict) -> bool:
    keys = (
        "python_opcode_count_per_full_domain_sweep",
        "wall_block_ns",
        "process_block_ns",
    )
    weak = all(box_a[k][1] <= box_b[k][0] for k in keys)
    strict = any(box_a[k][1] < box_b[k][0] for k in keys)
    return weak and strict


def adjudicate(boxes: dict) -> tuple[str, str]:
    n = boxes["N_THRESHOLD_DNF4_V1"]
    x = boxes["X_XOR2_V1"]
    x_over_n = robustly_dominates(x, n)
    n_over_x = robustly_dominates(n, x)
    if x_over_n and not n_over_x:
        return "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE", "X_XOR2_V1"
    if n_over_x and not x_over_n:
        return "DERIVED_NEURAL_AT_REGISTERED_SCOPE", "N_THRESHOLD_DNF4_V1"
    return "UNDECIDED_FROM_CURRENT_EVIDENCE", "NONE"


def harness_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def environment_record() -> dict:
    return {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "python_version_info": list(sys.version_info[:3]),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "github_sha": os.getenv("GITHUB_SHA"),
        "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "runner_os": os.getenv("RUNNER_OS"),
        "runner_arch": os.getenv("RUNNER_ARCH"),
        "harness_sha256": harness_sha256(),
    }


def protocol_environment_valid() -> tuple[bool, list[str]]:
    failures = []
    if platform.python_implementation() != "CPython":
        failures.append("python_implementation_not_cpython")
    if sys.version_info[:2] != (3, 12):
        failures.append("python_version_not_3_12")
    if os.getenv("GITHUB_ACTIONS") != "true":
        failures.append("not_github_actions_hosted_execution")
    if os.getenv("RUNNER_OS") != "Linux":
        failures.append("runner_os_not_linux")
    return not failures, failures


def deterministic_self_test() -> dict:
    prereg = json.loads(PREREG.read_text())
    assert prereg["status"] == "PREREGISTERED_NOT_EXECUTED"
    assert len(INPUTS) == 8
    assert sum(EXPECTED) == 4
    n = capability_record("N_THRESHOLD_DNF4_V1")
    x = capability_record("X_XOR2_V1")
    null = constant_zero_null_record()
    assert n["exact_gate_pass"]
    assert x["exact_gate_pass"]
    assert n["outputs"] == x["outputs"] == list(EXPECTED)
    assert null["correct"] == 4
    assert prereg["measurement_schedule"]["timed_blocks"] == 31
    assert prereg["measurement_schedule"]["sweeps_per_block"] == 20000
    return {
        "terminal": "PARITY3_PREREG_DETERMINISTIC_SELF_TEST_GREEN",
        "neural_exact": True,
        "non_neural_exact": True,
        "null_correct_of_8": 4,
        "protected_resource_measurement_executed": False,
    }


def run_experiment() -> dict:
    prereg = json.loads(PREREG.read_text())
    valid_env, env_failures = protocol_environment_valid()
    capabilities = {cid: capability_record(cid) for cid in CANDIDATES}
    all_capable = all(r["exact_gate_pass"] for r in capabilities.values())

    packet = {
        "schema": "NN_NONNN_POINT_PARITY3_RESULT_V1",
        "experiment_id": prereg["experiment_id"],
        "preregistration_status_seen": prereg["status"],
        "environment": environment_record(),
        "environment_gate_pass": valid_env,
        "environment_gate_failures": env_failures,
        "capability": capabilities,
        "null_baseline": constant_zero_null_record(),
        "measurement_schedule": prereg["measurement_schedule"],
        "candidate_universe": [
            {"candidate_id": cid, "family": CANDIDATES[cid]["family"]}
            for cid in CANDIDATES
        ],
        "candidate_expansion_attack": "NOT_YET_RUN",
        "claim_ceiling": prereg["claim_ceiling"],
    }

    if not valid_env or not all_capable:
        packet.update({
            "terminal": "INVALID_RECEIPT_OR_PROTOCOL_VIOLATION",
            "winner_candidate_id": "NONE",
            "prospective_prediction_passed": False,
            "protected_resource_measurement_executed": False,
        })
        return packet

    schedule = prereg["measurement_schedule"]
    warmup_sweeps = schedule["warmup_sweeps_per_candidate"]
    blocks_n = schedule["timed_blocks"]
    sweeps = schedule["sweeps_per_block"]

    expected_warmup_checksum = warmup_sweeps * sum(EXPECTED)
    for cid in CANDIDATES:
        got = warmup(CANDIDATES[cid]["fn"], warmup_sweeps)
        if got != expected_warmup_checksum:
            raise AssertionError(f"warmup capability drift for {cid}")

    opcode_counts = {
        cid: count_candidate_opcodes(CANDIDATES[cid]["fn"])
        for cid in CANDIDATES
    }

    measurements = {cid: [] for cid in CANDIDATES}
    gc_was_enabled = gc.isenabled()
    if gc_was_enabled:
        gc.disable()
    try:
        for block_index in range(blocks_n):
            order = (
                ("N_THRESHOLD_DNF4_V1", "X_XOR2_V1")
                if block_index % 2 == 0
                else ("X_XOR2_V1", "N_THRESHOLD_DNF4_V1")
            )
            for order_index, cid in enumerate(order):
                row = timed_block(CANDIDATES[cid]["fn"], sweeps)
                row.update({
                    "block_index": block_index,
                    "order_index": order_index,
                    "candidate_id": cid,
                })
                measurements[cid].append(row)
    finally:
        if gc_was_enabled:
            gc.enable()

    boxes = {
        cid: observed_box(opcode_counts[cid], measurements[cid])
        for cid in CANDIDATES
    }
    terminal, winner = adjudicate(boxes)

    packet.update({
        "opcode_counts": opcode_counts,
        "measurements": measurements,
        "resource_boxes": boxes,
        "robust_domination": {
            "non_neural_over_neural": robustly_dominates(
                boxes["X_XOR2_V1"], boxes["N_THRESHOLD_DNF4_V1"]
            ),
            "neural_over_non_neural": robustly_dominates(
                boxes["N_THRESHOLD_DNF4_V1"], boxes["X_XOR2_V1"]
            ),
        },
        "terminal": terminal,
        "winner_candidate_id": winner,
        "prospective_prediction": prereg["prospective_prediction"],
        "prospective_prediction_passed": terminal == "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE",
        "protected_resource_measurement_executed": True,
        "resource_uncertainty_semantics": "finite observed block envelope for this registered run; no population-confidence or cross-run generalization claim",
    })
    return packet


def write_packet(packet: dict, path: str | None) -> None:
    text = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if path:
        Path(path).write_text(text)
    print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()

    if args.self_test:
        write_packet(deterministic_self_test(), args.out)
        return 0

    packet = run_experiment()
    write_packet(packet, args.out)
    return 0 if packet["terminal"] != "INVALID_RECEIPT_OR_PROTOCOL_VIOLATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
