#!/usr/bin/env python3
"""Hostile candidate expansion: exact parity-3, frozen V3.

The preregistration is NN_NONNN_POINT_PARITY3_PREREG_V3.json. This harness uses
only the Python standard library. It emits a complete JSON measurement packet.

Scope warning: any derived family terminal is only about the four frozen candidates,
the executed CPython 3.12 hosted-runner scope, and the registered resource coordinates.
"""

from __future__ import annotations

import argparse
import ast
import gc
import dis
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from time import perf_counter_ns, process_time_ns

HERE = Path(__file__).resolve().parent
PREREG = HERE / "NN_NONNN_POINT_PARITY3_PREREG_V3.json"
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


def neural_sum_threshold_parity3(x: tuple[int, int, int]) -> int:
    """Three shared-sum hidden thresholds, output weights (1, -1, 1)."""
    a, b, c = x
    s = a + b + c
    h1 = int(s >= 1)
    h2 = int(s >= 2)
    h3 = int(s >= 3)
    return int(h1 - h2 + h3 >= 1)


def non_neural_lookup_parity3(x: tuple[int, int, int]) -> int:
    """Exact table indexed by the three-bit input word."""
    a, b, c = x
    return (0, 1, 1, 0, 1, 0, 0, 1)[(a << 2) | (b << 1) | c]


CANDIDATES = {
    "N_THRESHOLD_DNF4_V1": {
        "family": "NEURAL",
        "fn": neural_threshold_parity3,
    },
    "X_XOR2_V1": {
        "family": "NON_NEURAL",
        "fn": non_neural_xor_parity3,
    },
    "N_SUM_THRESHOLD3_V3": {
        "family": "NEURAL",
        "fn": neural_sum_threshold_parity3,
    },
    "X_LOOKUP8_V3": {
        "family": "NON_NEURAL",
        "fn": non_neural_lookup_parity3,
    },
}


def candidate_order(block_index):
    ids = list(CANDIDATES)
    if (block_index // 4) % 2:
        ids.reverse()
    offset = block_index % 4
    return ids[offset:] + ids[:offset]


def candidate_ast_hashes():
    nodes = {n.name: n for n in ast.parse(Path(__file__).read_text()).body
             if isinstance(n, ast.FunctionDef)}
    return {cid: hashlib.sha256(ast.dump(nodes[row["fn"].__name__],
                include_attributes=False).encode()).hexdigest()
            for cid, row in CANDIDATES.items()}



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


class MeasurementIntegrityError(ValueError):
    """No family verdict may be made with an invalid instrument witness."""


def require(condition, message):
    if not condition:
        raise MeasurementIntegrityError(message)


def expected_opcode_offsets(fn):
    """Complete straight-line instruction sequence for these frozen candidates.

    RESUME is not a sys.settrace opcode event on registered CPython 3.12.
    CACHE entries are excluded by dis.get_instructions' default. Reject control
    flow: this validator does not pretend static order describes arbitrary code.
    """
    instructions = list(dis.get_instructions(fn, adaptive=False, show_caches=False))
    require(not any(i.opcode in dis.hasjabs or i.opcode in dis.hasjrel
                    or i.opname in ("RETURN_GENERATOR", "YIELD_VALUE") for i in instructions),
            "instrument validator requires the frozen straight-line candidates")
    offsets = [i.offset for i in instructions if i.opname != "RESUME"]
    require(bool(offsets), "empty opcode expectation")
    return offsets


def validate_opcode_witness(fn, calls):
    expected = expected_opcode_offsets(fn)
    require(type(calls) is list and len(calls) == len(INPUTS), "missing candidate calls")
    for index, row in enumerate(calls):
        require(type(row) is dict, "malformed call witness")
        offsets = row.get("opcode_offsets")
        require(type(offsets) is list and all(type(v) is int for v in offsets)
                and offsets == expected, "incomplete or reordered opcode events")
        require(type(row.get("output")) is int and row["output"] == EXPECTED[index],
                "traced candidate capability drift")
        require(row.get("returned") is True, "candidate return event missing")
    count = sum(len(row["opcode_offsets"]) for row in calls)
    require(type(count) is int and count > 0, "nonpositive opcode count")
    return count


def trace_candidate_opcodes(fn):
    """Prearm CPython 3.12 tracing and validate each complete candidate frame."""
    require(sys.gettrace() is None, "refuse measurement while another trace is active")
    calls = []
    target_code = fn.__code__

    def tracer(frame, event, arg):
        if frame.f_code is not target_code:
            return None
        if event == "call":
            calls.append({"opcode_offsets": [], "returned": False})
            frame.f_trace_opcodes = True
            frame.f_trace_lines = False
        elif event == "opcode":
            calls[-1]["opcode_offsets"].append(frame.f_lasti)
        elif event == "return":
            calls[-1]["returned"] = True
            calls[-1]["output"] = arg
        return tracer

    # In 3.12 a frame must request opcodes BEFORE settrace enables its machinery.
    # Setting the target frame flag only in the call event makes the first
    # measurement silently zero. Restore the caller's flag even on exceptions.
    current = sys._getframe()
    previous_opcodes = current.f_trace_opcodes
    current.f_trace_opcodes = True
    try:
        sys.settrace(tracer)
        for x in INPUTS:
            fn(x)
    finally:
        sys.settrace(None)
        current.f_trace_opcodes = previous_opcodes
    return {"count": validate_opcode_witness(fn, calls), "calls": calls}


def count_candidate_opcodes(fn):
    return trace_candidate_opcodes(fn)["count"]


def instrumentation_preflight():
    forward = {cid: trace_candidate_opcodes(row["fn"]) for cid, row in CANDIDATES.items()}
    reverse = {cid: trace_candidate_opcodes(CANDIDATES[cid]["fn"])
               for cid in reversed(CANDIDATES)}
    require(forward == reverse, "candidate-order-dependent opcode instrument")
    return {
        "status": "COMPLETE_OPCODE_WITNESSES_AND_ORDER_INVARIANCE_GREEN",
        "opcode_counts": {cid: row["count"] for cid, row in forward.items()},
        "forward_witnesses": forward,
        "reverse_witnesses": reverse,
    }


def validate_preregistration(prereg):
    require(prereg.get("schema") == "NN_NONNN_POINT_PARITY3_PREREG_V3", "wrong prereg schema")
    require(prereg.get("status") == "PREREGISTERED_NOT_EXECUTED", "wrong prereg freeze status")
    require(prereg.get("measurement_schedule") == {
        "warmup_sweeps_per_candidate": 5000, "timed_blocks": 32,
        "sweeps_per_block": 20000, "inputs_per_sweep": 8,
        "calls_per_block_per_candidate": 160000,
        "candidate_order": "rotate base order by block modulo 4; reverse base order on odd groups of 4",
    }, "registered timing schedule changed")
    require([x["candidate_id"] for x in prereg["candidates"]] == list(CANDIDATES),
            "registered candidate universe changed")
    require({x["candidate_id"]: x["ast_sha256"] for x in prereg["candidates"]}
            == candidate_ast_hashes(), "registered candidate source changed")
    require(all(x["family"] == CANDIDATES[x["candidate_id"]]["family"]
                and x["implementation"] == CANDIDATES[x["candidate_id"]]["fn"].__name__
                for x in prereg["candidates"]), "candidate identity mismatch")
    require([x["name"] for x in prereg["registered_resource_coordinates"]] == [
        "python_opcode_count_per_full_domain_sweep", "wall_block_ns", "process_block_ns"
    ], "registered resources changed")
    require(prereg.get("independent_prospective_prediction") is False,
            "V3 must disclose that V1 and V2 outcomes were read")


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


def adjudicate(boxes: dict) -> dict:
    require(set(boxes) == set(CANDIDATES), "incomplete candidate universe")
    keys = {"python_opcode_count_per_full_domain_sweep", "wall_block_ns", "process_block_ns"}
    for box in boxes.values():
        require(type(box) is dict and set(box) == keys, "resource dimension mismatch")
        for interval in box.values():
            require(type(interval) is list and len(interval) == 2
                    and all(type(v) is int and v > 0 for v in interval)
                    and interval[0] <= interval[1], "invalid positive integer resource interval")
    dominators = {cid: [other for other in CANDIDATES if other != cid
                       and robustly_dominates(boxes[other], boxes[cid])]
                  for cid in CANDIDATES}
    frontier = [cid for cid in CANDIDATES if not dominators[cid]]
    require(bool(frontier), "empty finite robust frontier")
    families = sorted({CANDIDATES[cid]["family"] for cid in frontier})
    terminal = {("NEURAL",): "DERIVED_NEURAL_AT_REGISTERED_SCOPE",
                ("NON_NEURAL",): "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE"}.get(
                    tuple(families), "UNDECIDED_FROM_CURRENT_EVIDENCE")
    return {"terminal": terminal, "frontier_candidate_ids": frontier,
            "frontier_families": families, "dominated_by": dominators,
            "winner_candidate_id": frontier[0] if len(frontier) == 1 else "NONE"}


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
        "github_event_name": os.getenv("GITHUB_EVENT_NAME"),
        "github_ref": os.getenv("GITHUB_REF"),
        "candidate_ast_sha256": candidate_ast_hashes(),
        "runner_os": os.getenv("RUNNER_OS"),
        "runner_arch": os.getenv("RUNNER_ARCH"),
        "harness_sha256": harness_sha256(),
        "preregistration_sha256": hashlib.sha256(PREREG.read_bytes()).hexdigest(),
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
    for key, expected in (("GITHUB_REF", "refs/heads/main"),
                          ("GITHUB_EVENT_NAME", "push"), ("GITHUB_RUN_ATTEMPT", "1")):
        if os.getenv(key) != expected:
            failures.append(key.lower() + "_outside_first_main_push")
    if not os.getenv("GITHUB_SHA") or not os.getenv("GITHUB_RUN_ID"):
        failures.append("missing_execution_identity")
    return not failures, failures


def deterministic_self_test() -> dict:
    prereg = json.loads(PREREG.read_text())
    validate_preregistration(prereg)
    require(platform.python_implementation() == "CPython" and sys.version_info[:2] == (3, 12),
            "instrument self-test requires registered CPython 3.12")
    for cid in CANDIDATES:
        require(capability_record(cid)["exact_gate_pass"], "candidate capability failed")
    require(constant_zero_null_record()["correct"] == 4, "null baseline changed")
    instrument = instrumentation_preflight()
    return {
        "terminal": "PARITY3_V3_INSTRUMENT_SELF_TEST_GREEN",
        "opcode_counts": instrument["opcode_counts"],
        "opcode_instrument_diagnostics_executed": True,
        "protected_timing_measurement_executed": False,
        "full_registered_experiment_executed": False,
        "independent_prospective_prediction": False,
    }


def run_experiment() -> dict:
    prereg = json.loads(PREREG.read_text())
    validate_preregistration(prereg)
    valid_env, env_failures = protocol_environment_valid()
    capabilities = {cid: capability_record(cid) for cid in CANDIDATES}
    all_capable = all(r["exact_gate_pass"] for r in capabilities.values())

    packet = {
        "schema": "NN_NONNN_POINT_PARITY3_RESULT_V3",
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
        "candidate_expansion_attack": "FOUR_CANDIDATES_REGISTERED",
        "claim_ceiling": prereg["claim_ceiling"],
        "independent_prospective_prediction": False,
        "expansion_lineage": prereg["expansion_lineage"],
    }

    if not valid_env or not all_capable:
        packet.update({
            "terminal": "INVALID_RECEIPT_OR_PROTOCOL_VIOLATION",
            "winner_candidate_id": "NONE",
            "expansion_expectation_passed": False,
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

    try:
        instrument = instrumentation_preflight()
    except (MeasurementIntegrityError, RuntimeError) as exc:
        packet.update({
            "terminal": "INVALID_RECEIPT_OR_PROTOCOL_VIOLATION",
            "winner_candidate_id": "NONE",
            "expansion_expectation_passed": False,
            "protected_resource_measurement_executed": False,
            "protected_timing_measurement_executed": False,
            "instrumentation_gate_pass": False,
            "instrumentation_gate_failure": str(exc),
        })
        return packet
    opcode_counts = instrument["opcode_counts"]

    measurements = {cid: [] for cid in CANDIDATES}
    gc_was_enabled = gc.isenabled()
    if gc_was_enabled:
        gc.disable()
    try:
        for block_index in range(blocks_n):
            order = candidate_order(block_index)
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
    verdict = adjudicate(boxes)
    require(packet["environment"]["harness_sha256"] == harness_sha256()
            and packet["environment"]["preregistration_sha256"]
            == hashlib.sha256(PREREG.read_bytes()).hexdigest(), "source changed during measurement")

    packet.update({
        "opcode_counts": opcode_counts,
        "instrumentation_gate_pass": True,
        "instrumentation": instrument,
        "protected_timing_measurement_executed": True,
        "measurements": measurements,
        "resource_boxes": boxes,
        **verdict,
        "candidate_expansion_attack": "EXECUTED_AT_REGISTERED_FOUR_CANDIDATE_SCOPE",
        "registered_expansion_expectation": prereg["registered_expansion_expectation"],
        "expansion_expectation_passed": verdict["terminal"] == "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE",
        "protected_resource_measurement_executed": True,
        "resource_uncertainty_semantics": "finite observed block envelope for this registered run; no population-confidence or cross-run generalization claim",
    })
    return packet


def write_packet(packet: dict, path: str | None) -> None:
    text = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if path:
        with Path(path).open("x") as stream:
            stream.write(text)
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
