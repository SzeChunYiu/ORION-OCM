"""Fixed native command dispatch. A successful process is not a checked proof."""
import base64
import math
from pathlib import Path
import time
from env_inputs import (artifact_diagnostics, canonical, digest, file_record, inventory, parse_json, snapshot,
                        verify_file, write_bytes, write_json)
from env_runtime import execute, source_inventory, verify_runtime

OPERATIONS = {
    "inspect": {"source_packet"},
    "prepare": {"source_packet", "policy", "primitive_packet", "registered_target_packet"},
    "check": {"permitted_packet", "target_packet", "registration", "primitive_packet", "candidate_packet"},
}
TERMINALS = {"inspect": {"INSPECTED", "REJECTED", "CANNOT_CHECK"},
             "prepare": {"PREPARED", "REJECTED", "CANNOT_CHECK"},
             "check": {"KERNEL_PASS", "REJECTED", "CANNOT_CHECK"}}
PREPARED_FILES = {"permitted.ndjson", "target.ndjson", "registration.json", "inventory.json", "result.json"}


def native_result(process, directory, operation):
    if (process["terminal"] != "COMPLETED" or process["returncode"] != 0 or
            process["timed_out"] or process["output_truncated"] or
            process["cleanup"]["reaped"] is not True or process["cleanup"]["group_absent"] is not True):
        raise ValueError("native process did not complete within its qualified envelope")
    files = inventory(directory)
    if base64.b64decode(process["stderr_base64"], validate=True) != b"":
        raise ValueError("unexpected native stderr")
    result = parse_json((directory / "result.json").read_bytes())
    stdout = parse_json(base64.b64decode(process["stdout_base64"], validate=True))
    required = {"schema", "operation", "terminal", "stage", "reason", "stats", "dependencies", "axioms", "files"}
    if type(result) is not dict or set(result) != required:
        raise ValueError("native result schema differs")
    if canonical(stdout) != canonical(result): raise ValueError("native stdout/result disagreement")
    if result["schema"] != "ocm.proof-environment.result.v1" or result["operation"] != operation:
        raise ValueError("native result operation differs")
    if result["terminal"] not in TERMINALS[operation]: raise ValueError("unexpected native terminal")
    if any(type(result[k]) is not str for k in ("stage", "reason")):
        raise ValueError("native explanation fields invalid")
    for key in ("dependencies", "axioms", "files"):
        items = result[key]
        if type(items) is not list or any(type(x) is not str for x in items) or len(set(items)) != len(items):
            raise ValueError("invalid native " + key)
    if type(result["stats"]) is not dict or any(type(k) is not str or type(v) not in (int, float) or
            (type(v) is float and not math.isfinite(v)) or v < 0 for k, v in result["stats"].items()):
        raise ValueError("invalid native counters")
    expected = PREPARED_FILES if result["terminal"] == "PREPARED" else {"result.json"}
    if operation == "prepare" and result["terminal"] in {"CANNOT_CHECK", "REJECTED"}:
        if "result.json" not in files or not set(files) <= PREPARED_FILES:
            raise ValueError("unexpected partial preparation files")
        expected = set(files)
    if set(files) != expected or set(result["files"]) != expected:
        raise ValueError("unexpected/missing native output files")
    return result


def invoke(operation, records, root, runtime_path, runtime_sha256, *, candidate_root=None,
           timeout_s=60, max_output_bytes=1048576, verify_issuer=None):
    """Caller has independently authorized records. Persist every attempted dispatch."""
    started = time.monotonic(); root = Path(root); interrupted = None
    receipt = {"schema": "ocm.proof-environment.receipt.v1", "operation": operation,
               "terminal": "CANNOT_CHECK", "stage": "custody", "reason": "",
               "runtime_sha256": runtime_sha256, "inputs": records, "native": None, "process": None}
    try:
        if operation not in OPERATIONS or set(records) != OPERATIONS[operation]:
            raise ValueError("fixed operation input roles differ")
        authorization = file_record(root / "freeze.json")
        receipt["authorization_sha256"] = authorization["sha256"]
        if type(timeout_s) not in (int, float) or not math.isfinite(timeout_s) or timeout_s <= 0:
            raise ValueError("positive execution bound required")
        if type(max_output_bytes) is not int or max_output_bytes < 1:
            raise ValueError("positive output bound required")
        if operation == "check" and (type(candidate_root) is not int or candidate_root < 0):
            raise ValueError("candidate expression root must be a natural number")
        if operation != "check" and candidate_root is not None: raise ValueError("unexpected candidate root")
        runtime, mounts = verify_runtime(runtime_path, runtime_sha256)
        sources = source_inventory(); receipt["driver_sources"] = sources
        write_bytes(root / "runtime.json", Path(runtime_path).read_bytes())
        if file_record(root / "runtime.json")["sha256"] != runtime_sha256:
            raise ValueError("runtime snapshot differs from authorization")
        staging = root / "inputs"; staging.mkdir(); work = root / "execution"; work.mkdir()
        request = {"schema": "ocm.proof-environment.request.v1", "operation": operation}
        copied = {}; input_mounts = []
        for role, record in sorted(records.items()):
            suffix = ".json" if role in {"policy", "registration"} else ".ndjson"
            name = role + suffix; copied[role] = snapshot(record, staging / name)
            request[role] = "/inputs/" + name
            input_mounts.append((copied[role]["path"], request[role]))
        if operation == "check": request["candidate_root"] = candidate_root
        write_json(root / "request.json", request)
        receipt["request_sha256"] = file_record(root / "request.json")["sha256"]
        before = inventory(staging); runtime_copy = file_record(root / "runtime.json")
        process = execute(runtime, mounts, root / "request.json", work, input_mounts,
                          timeout_s=timeout_s, max_output_bytes=max_output_bytes)
        receipt["process"] = process
        # Validate custody even when the subprocess rejects or fails.
        verify_runtime(runtime_path, runtime_sha256)
        if source_inventory() != sources or inventory(staging) != before:
            raise ValueError("driver or staged input custody changed")
        if file_record(root / "runtime.json") != runtime_copy:
            raise ValueError("runtime record custody changed")
        if file_record(root / "freeze.json") != authorization:
            raise ValueError("authorization snapshot custody changed")
        if file_record(root / "request.json")["sha256"] != receipt["request_sha256"]:
            raise ValueError("native request custody changed")
        for record in records.values(): verify_file(record)
        native = native_result(process, work / "native", operation)
        if verify_issuer is not None: verify_issuer()
        receipt.update(native=native, terminal=native["terminal"], stage=native["stage"], reason=native["reason"])
        if operation == "prepare" and native["terminal"] == "PREPARED":
            receipt["environment_id"] = digest(canonical({
                "runtime": runtime_sha256, "inputs": {k: v["sha256"] for k, v in copied.items()},
                "outputs": inventory(work / "native")}))
    except (OSError, ValueError, TypeError, KeyError, RecursionError, ImportError, OverflowError) as exc:
        receipt.update(terminal="CANNOT_CHECK", stage="custody_or_process", reason=type(exc).__name__ + ": " + str(exc))
    except (KeyboardInterrupt, SystemExit) as exc:
        interrupted = exc
        receipt.update(terminal="CANNOT_CHECK", stage="interrupted", reason=type(exc).__name__,
                       evidence_complete=False,
                       evidence_scope="Surviving artifacts only; helper-local raw process envelope was not returned. No work/cleanup claim.")
    receipt["wall_s"] = time.monotonic() - started
    receipt["cost_scope"] = ("Driver validation, copying, invocation and cleanup before final inventory/serialization. "
                             "Outer recorder must charge sealing, export, build and acquisition separately. CPU/RSS unmeasured.")
    try: receipt["files"] = inventory(root)
    except (OSError, ValueError) as exc:
        receipt.update(terminal="CANNOT_CHECK", evidence_complete=False, files=None,
                       artifact_error=type(exc).__name__ + ": " + str(exc),
                       artifact_diagnostics=artifact_diagnostics(root))
    write_json(root / "receipt.json", receipt)
    if interrupted is not None: raise interrupted
    return receipt
