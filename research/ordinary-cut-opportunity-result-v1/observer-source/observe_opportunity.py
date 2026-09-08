"""One root-bound training opportunity audit; no native checker is invoked here."""
from pathlib import Path
import hashlib
import json
import os
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ROOT = Path("/home/billy/orion-director-work/20260908/ordinary-cut-opportunity-v1/consumer-v3")
RUN = ROOT / "prospective-run-01"
REQUEST = RUN / "REQUEST-PROSPECTIVE.json"
GATE = RUN / "ROOT-OPPORTUNITY-GATE.json"
OUTPUT = RUN / "opportunity-01"
OBSERVATION = RUN / "observation-01"
CONTRACT = HERE / "OBSERVER-CONTRACT.json"
PYTHON = Path("/home/billy/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11")
EXPECTED_PYTHON = {"bytes":21334200,"sha256":"edca1fc80dbd58182c849c13707fb6bfb522b0d7049adc408225f7c69b124d3b"}
EXPECTED_REQUEST = {"bytes":4584,"sha256":"0e3b85d6fda159c653d46f9e7104eea4869a29d911a7aec18f64297fdf96b564"}


def byte_identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def identity(path):
    return byte_identity(path.read_bytes())


def write(path, data):
    with path.open("x") as stream:
        json.dump(data, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def run():
    measured_start = time.perf_counter()
    assert Path(sys.executable) == PYTHON
    assert sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode and not sys.flags.optimize
    request_raw = REQUEST.read_bytes()
    assert byte_identity(request_raw) == EXPECTED_REQUEST
    request = json.loads(request_raw)
    gate_raw = GATE.read_bytes()
    gate = json.loads(gate_raw)
    contract_raw = CONTRACT.read_bytes()
    contract = json.loads(contract_raw)
    assert gate["authorization"] == "ROOT_TRAINING_OPPORTUNITY_GATE"
    assert gate["request"] == EXPECTED_REQUEST and gate["max_runs"] == 1
    assert type(gate["outer_wall_s"]) is int and gate["outer_wall_s"] == 180
    assert gate["observer"] == identity(Path(__file__).resolve())
    assert gate["observer_contract"] == byte_identity(contract_raw)
    assert request["gate_path"] == str(GATE)
    assert request["schema"] == "ordinary.training-opportunity-request.v3"
    assert request["max_wall_s"] == 60 and request["max_token_states"] == 2000000
    assert gate["output"] == str(OUTPUT) and gate["observation"] == str(OBSERVATION)
    argv = [str(PYTHON), "-I", "-S", "-B", str(ROOT / "run_opportunity.py"), str(REQUEST), str(OUTPUT)]
    assert gate["argv"] == argv and gate["cwd"] == str(ROOT)
    assert gate["runtime"] == {"path": str(PYTHON), **EXPECTED_PYTHON}
    assert contract["request"] == {"path": str(REQUEST), **EXPECTED_REQUEST}
    assert contract["sources"] == request["sources"] and len(request["sources"]) == 18
    pins = {}

    def pin(path, value):
        value = {k: value[k] for k in ("bytes", "sha256")}
        assert path not in pins or pins[path] == value, "conflicting pin: " + path
        pins[path] = value

    for name, value in request["sources"].items():
        pin(str(ROOT / name), value)
    pin(str(REQUEST), EXPECTED_REQUEST)
    pin(str(PYTHON), EXPECTED_PYTHON)
    pin(str(CONTRACT), byte_identity(contract_raw))
    pin(str(Path(__file__).resolve()), gate["observer"])
    pin(str(HERE / "output_contract.py"), contract["output_contract"])
    pin(contract["source_freeze"]["path"], contract["source_freeze"])
    for key in ("P0_contracts", "training_packet", "release_receipt", "P1_inventory",
                "qualified_native_trace_authority", "registry_scope"):
        assert request[key] == contract["inputs"][key]
        pin(request[key]["path"], request[key])
    for key in ("qualified_native_trace_authority", "P1_inventory", "training_packet"):
        assert gate[key] == request[key]
    for value in contract["implicit_registry_inputs"].values():
        pin(value["path"], value)
    assert set(gate["accepted_reviews"]) == {"native_outcome", "consumer_source", "observer_source"}
    for value in gate["accepted_reviews"].values():
        assert set(value) == {"path", "bytes", "sha256"}
        pin(value["path"], value)
    for path, value in gate["review_bindings"].items():
        pin(path, value)
    for path, value in pins.items():
        assert identity(Path(path)) == value, path
    from output_contract import inspect_outputs
    assert not OUTPUT.exists() and OUTPUT.name not in {p.name for p in RUN.iterdir()}
    assert not OBSERVATION.exists() and OBSERVATION.name not in {p.name for p in RUN.iterdir()}
    OBSERVATION.mkdir()
    write(OBSERVATION / "START.json", {"observer_pid": os.getpid(), "observer_parent_pid": os.getppid(),
        "gate": byte_identity(gate_raw), "request": EXPECTED_REQUEST, "pins": pins, "argv": argv,
        "runtime": gate["runtime"], "observer_argv": sys.argv})
    process_start = time.perf_counter()
    timed_out = False
    child, pid, status, usage, process_error = None, None, None, None, None
    try:
        with (OBSERVATION / 'stdout.log').open('xb') as out, (OBSERVATION / 'stderr.log').open('xb') as err:
            child = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}, start_new_session=True)
            while True:
                pid, status, usage = os.wait4(child.pid, os.WNOHANG)
                if pid:
                    break
                if time.perf_counter() - process_start > gate['outer_wall_s']:
                    timed_out = True
                    break
                time.sleep(0.02)
    except BaseException as error:
        process_error = repr(error)
    finally:
        if child is not None and pid != child.pid:
            try:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # The child may have exited between wait and kill.
                pid, status, usage = os.wait4(child.pid, 0)
            except BaseException as error:
                process_error = str(process_error) + '; cleanup: ' + repr(error)
        if child is not None and pid == child.pid:
            child.returncode = os.waitstatus_to_exitcode(status)
    process_wall = time.perf_counter() - process_start
    unchanged, read_errors = {}, {}
    if process_error is not None:
        read_errors["process"] = process_error
    for path, value in pins.items():
        try:
            unchanged[path] = identity(Path(path)) == value
        except OSError as error:
            unchanged[path] = False
            read_errors[path] = repr(error)
    try:
        unchanged[str(GATE)] = GATE.read_bytes() == gate_raw
    except OSError as error:
        unchanged[str(GATE)] = False
        read_errors["gate"] = repr(error)
    reaped = child is not None and pid == child.pid
    exit_code = child.returncode if reaped else None
    try:
        outputs = inspect_outputs(OUTPUT, child.pid if child else None, EXPECTED_REQUEST, request)
    except BaseException as error:
        outputs = {"files": {}, "entries": [], "population_ok": False, "completed_contract": False,
                   "errors": [type(error).__name__ + ": " + str(error)]}
    successful = (reaped and exit_code == 0 and all(unchanged.values()) and not timed_out
        and not read_errors and outputs["population_ok"] and outputs["completed_contract"] and not outputs["errors"])
    receipt = {"schema": "ordinary.opportunity.outer-process.v1", "observer_pid": os.getpid(),
        "observer_parent_pid": os.getppid(), "pid": child.pid if child else None,
        "child_parent_pid": os.getpid() if child else None,
        "reaped": reaped, "exit_code": exit_code, "signal": -exit_code if exit_code is not None and exit_code < 0 else None,
        "timeout": timed_out, "argv": argv, "cwd": str(ROOT), "process_wall_s": process_wall,
        "user_cpu_s": usage.ru_utime if usage else None, "system_cpu_s": usage.ru_stime if usage else None,
        "rss_kib": usage.ru_maxrss if usage else None, "inputs_unchanged": unchanged,
        "read_errors": read_errors, "outputs": outputs,
        "stdout": identity(OBSERVATION / "stdout.log") if (OBSERVATION / "stdout.log").is_file() else None,
        "stderr": identity(OBSERVATION / "stderr.log") if (OBSERVATION / "stderr.log").is_file() else None,
        "measured_outer_wall_s": time.perf_counter() - measured_start,
        "measurement_scope": "Observer run entry through post-run input/output checks; excludes interpreter/import startup, source preparation, root review and final receipt serialization. Child wall is nested, not additive. Not lifetime cost.",
        "terminal": "OPPORTUNITY_PROCESS_COMPLETED" if successful else "OPPORTUNITY_PROCESS_FAILED",
        "scope": "Once-only training opportunity recording; no native admission, serving utility, held-out result or novelty follows."}
    write(OBSERVATION / "PROCESS.json", receipt)
    print(json.dumps({"terminal": receipt["terminal"], "pid": receipt["pid"], "exit_code": exit_code,
        "receipt": str(OBSERVATION / "PROCESS.json")}))
    return 0 if successful else 1


if __name__ == "__main__":
    raise SystemExit(run())
