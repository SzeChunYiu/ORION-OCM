"""Separate proposal and exact-kernel phases, with unchanged commissioned primitives."""
from pathlib import Path
import json
import session_dependencies as D
from session_bindings import LIMITS, canonical, digest, write_bytes, write_json


def propose(raw, runtime, destination, source_files, timeout_s):
    app, inputs = destination / "app", destination / "input"
    app.mkdir(); inputs.mkdir()
    for name in D.WORKER_FILES:
        data = (D.MECHANICAL / name).read_bytes()
        if digest(data) != source_files["mechanical-proof-v1/" + name]:
            raise ValueError("worker source changed before dispatch")
        write_bytes(app / name, data)
    write_bytes(inputs / "task.json", raw)
    python = runtime["python"]
    process = D.run_isolated(["/python/bin/python3.11", "-I", "-S", "-B", "/app/worker.py", "/input/task.json"],
        read_only=[(Path(python["directory"]), "/python"), (app, "/app"), (inputs, "/input"),
                   *runtime["shared_libraries"]["mounts"]],
        executable_sha256=python["python_sha256"], env={"LANG": "C.UTF-8"},
        timeout_s=timeout_s, max_output_bytes=1048576)
    write_json(destination / "worker-process.json", process)
    if (process["terminal"] != "COMPLETED" or process["returncode"] != 0 or process["stderr"].strip() or
            type(process.get("pid")) is not int or process["pid"] <= 0 or
            process.get("cleanup", {}).get("reaped") is not True or
            process.get("cleanup", {}).get("group_absent") is not True):
        raise ValueError("learner environment/process unavailable or incomplete: " + process.get("reason", ""))
    record = D.validate_worker(json.loads(process["stdout"]))
    if set(record) != {"status", "candidate", "reason", "counters", "limits", "used_constants", "worker_audit"}:
        raise ValueError("unregistered worker result fields")
    expected_limits = dict(LIMITS, **json.loads(raw).get("limits", {}))
    if canonical(record["limits"]) != canonical(expected_limits) or type(record["reason"]) is not str:
        raise ValueError("worker did not report registered limits/reason")
    if (inputs / "task.json").read_bytes() != raw:
        raise ValueError("input changed during dispatch")
    for name in D.WORKER_FILES:
        if D.file_hash(app / name) != source_files["mechanical-proof-v1/" + name]:
            raise ValueError("worker source changed during dispatch")
    return record


def check(candidate, runtime, destination, timeout_s):
    stage = D.stage_candidate(candidate, destination / "checker")
    write_json(destination / "stage.json", stage)
    checked = D.check_staged(stage, runtime["lean_root"], runtime["shared_libraries"]["mounts"], timeout_s=timeout_s)
    write_json(destination / "kernel-result.json", checked)
    if checked.get("terminal") == "KERNEL_PASS":
        D.MODULES["kernel_check"]._source_check(stage)
        if (checked.get("fresh_kernel_replay") is not True or type(checked.get("axioms")) is not list or
                checked.get("stage") != stage or
                checked.get("compiled_proof_sha256") != D.file_hash(Path(stage["directory"]) / "Candidate.olean")):
            raise ValueError("incomplete native kernel acceptance record")
    elif checked.get("terminal") not in {"REJECTED", "CANNOT_CHECK"}:
        raise ValueError("unregistered checker terminal")
    return checked
