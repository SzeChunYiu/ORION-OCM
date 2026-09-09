"""Cold-process ordinary goal search through the existing native proof boundary.

This is experiment infrastructure, not a new solver, proof authority, OCM runtime,
or security sandbox for arbitrary hostile native code. Each source-reviewed worker
receives only an immutable library, goal tasks, and a pinned eligibility state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import sysconfig
import tarfile
import time
import uuid
from typing import Any

SCHEMA = "ordinary.goal-lifecycle.v1"
MODES = ("enabled", "resident-disabled", "restored")
BUNDLE_NAMES = ("base.mm", "joined.mm", "manifest.json", "receipt.json")
HERE = Path(__file__).resolve().parent


def require(value: bool, reason: str) -> None:
    if not value:
        raise ValueError(reason)


def encoded(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def raw_id(raw: bytes) -> dict[str, Any]:
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def identity(value: Any) -> dict[str, Any]:
    return raw_id(encoded(value))


def read_json(path: Path) -> Any:
    def unique(pairs):
        out = {}
        for k, v in pairs:
            require(k not in out, "duplicate JSON key")
            out[k] = v
        return out
    def nonfinite(value):
        raise ValueError("nonfinite JSON constant: " + value)
    return json.loads(path.read_bytes(), object_pairs_hook=unique,
                      parse_constant=nonfinite)


def write_new(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def checked_file(path: Path, expected: dict[str, Any]) -> bytes:
    require(not path.is_symlink() and path.is_file(), "regular input file required")
    raw = path.read_bytes()
    require(raw_id(raw) == expected, "input/source identity mismatch: " + str(path))
    return raw


def relative(root: Path, name: str) -> Path:
    require(type(name) is str and bool(name), "relative path required")
    p = Path(name)
    require(not p.is_absolute() and ".." not in p.parts, "path escape")
    q = root / p
    require(q.resolve().is_relative_to(root.resolve()), "resolved path escape")
    return q


def validate_population(tasks: Any) -> list[dict[str, Any]]:
    require(type(tasks) is list and 0 < len(tasks) <= 128, "nonempty bounded task population")
    require(all(type(t) is dict and set(t) == {"schema", "query", "premises", "context", "limits"}
                for t in tasks), "goal-only input fields")
    pins = [identity(t) for t in tasks]
    require(len({p["sha256"] for p in pins}) == len(pins), "duplicate task identity")
    require(len(encoded(tasks)) <= 2_000_000, "task population byte bound")
    return pins


def runtime_inventory() -> dict[str, Any]:
    """Pin the local interpreter, ordinary stdlib (including bytecode), and maps.

    Site packages are excluded. This is a concrete run binding, not a portable
    Python-version guarantee or a proof of all possible future dynamic loads.
    """
    stdlib = Path(sysconfig.get_path("stdlib")).resolve()
    paths = {Path(sys.executable).resolve()}
    for root, dirs, files in os.walk(stdlib):
        dirs[:] = [d for d in dirs if d not in {"site-packages", "dist-packages", "test", "tests", "idlelib", "tkinter", "turtledemo", "ensurepip"}]
        for name in files:
            p = Path(root) / name
            if p.suffix in {".py", ".pyc", ".so"}:
                paths.add(p.resolve())
    maps = Path("/proc/self/maps")
    if maps.exists():
        for line in maps.read_text().splitlines():
            fields = line.split(maxsplit=5)
            if len(fields) == 6 and fields[5].startswith("/"):
                p = Path(fields[5])
                if p.is_file():
                    paths.add(p.resolve())
    files = {str(p): raw_id(p.read_bytes()) for p in sorted(paths) if p.is_file()}
    return {"python_version": sys.version, "python": str(Path(sys.executable).resolve()),
            "stdlib": str(stdlib), "files": files}


def stage_engine(repo: Path, target: Path) -> dict[str, Any]:
    pins = read_json(HERE / "DEPENDENCIES.json")
    target.mkdir(parents=True, exist_ok=False)
    for dest, entry in pins["files"].items():
        raw = checked_file(relative(repo, entry["path"]), entry["identity"])
        write_new(relative(target, dest), raw)
    archive = pins["lark_archive"]
    raw = checked_file(relative(repo, archive["path"]), archive["identity"])
    import io
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as stream:
        for m in stream.getmembers():
            require(m.isfile(), "runtime archive regular files only")
            require(m.name.startswith("lark-runtime/"), "runtime archive prefix")
            name = m.name.removeprefix("lark-runtime/")
            f = stream.extractfile(m)
            require(f is not None, "runtime member missing")
            write_new(relative(target / "runtime", name), f.read())
    write_new(target / "worker.py", Path(__file__).read_bytes())
    files = {p.relative_to(target).as_posix(): raw_id(p.read_bytes())
             for p in sorted(target.rglob("*")) if p.is_file()}
    source = {"schema": SCHEMA + ".source", "files": files,
              "runtime": runtime_inventory(), "dependencies": identity(pins)}
    write_new(target / "SOURCE.json", encoded(source) + b"\n")
    return source


def audit_boundary(reads: set[str], output: Path) -> tuple[list[dict[str, str]], Any]:
    """Constrain reviewed Python code; no claim of hostile-native-code containment."""
    output = output.resolve()
    directories = {str(parent) for name in reads for parent in Path(name).parents}
    blocked: list[dict[str, str]] = []
    def reject(event: str, detail: Any) -> None:
        blocked.append({"event": event, "detail": str(detail)[:500]})
        raise PermissionError("UNREGISTERED_EXECUTION: " + event)
    def path_of(value):
        if isinstance(value, int):
            return None
        return Path(os.fsdecode(value)).resolve()
    def hook(event, args):
        if event.startswith("socket.") or event in {
            "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.fork",
            "os.forkpty", "ctypes.dlopen", "os.symlink", "os.link", "os.truncate"
        }:
            reject(event, args[:1])
        if event == "open":
            p = path_of(args[0])
            if p is None:
                return
            mode, flags = args[1], args[2]
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or bool(
                flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing and not p.is_relative_to(output):
                reject(event, p)
            if not writing and str(p) not in reads and not p.is_relative_to(output):
                reject(event, p)
        elif event in {"os.mkdir", "os.remove", "os.rmdir", "os.chmod"}:
            p = path_of(args[0])
            if p is not None and not p.is_relative_to(output):
                reject(event, p)
        elif event in {"os.rename", "os.replace"}:
            for value in args[:2]:
                p = path_of(value)
                if p is not None and not p.is_relative_to(output):
                    reject(event, p)
        elif event in {"os.listdir", "os.scandir"}:
            p = path_of(args[0])
            if p is not None and str(p) not in directories and not p.is_relative_to(output):
                reject(event, p)
    return blocked, hook


def _worker(request_path: Path, request_hash: str) -> int:
    started = time.perf_counter()
    request_raw = request_path.read_bytes()
    require(hashlib.sha256(request_raw).hexdigest() == request_hash, "issued request identity")
    request = read_json(request_path)
    require(set(request) == {"schema", "occurrence", "stage", "source", "inputs", "state", "tasks", "output", "limits"}, "request fields")
    require(request["schema"] == SCHEMA + ".request", "request schema")
    stage, output = Path(request["stage"]).resolve(), Path(request["output"]).resolve()
    require(not output.exists(), "fresh worker output required")
    output.mkdir(parents=True)
    lim = request["limits"]
    require(type(lim["memory_bytes"]) is int and lim["memory_bytes"] > 0, "memory bound")
    require(type(lim["cpu_seconds"]) is int and lim["cpu_seconds"] > 0, "cpu bound")
    resource.setrlimit(resource.RLIMIT_AS, (lim["memory_bytes"], lim["memory_bytes"]))
    resource.setrlimit(resource.RLIMIT_CPU, (lim["cpu_seconds"], lim["cpu_seconds"] + 1))
    resource.setrlimit(resource.RLIMIT_FSIZE, (128_000_000, 128_000_000))
    source_raw = checked_file(stage / "SOURCE.json", request["source"])
    source = json.loads(source_raw)
    reads = {str(request_path.resolve()), str(stage / "SOURCE.json")}
    for name, pin in source["files"].items():
        p = relative(stage, name)
        checked_file(p, pin)
        reads.add(str(p.resolve()))
    for name, pin in source["runtime"]["files"].items():
        checked_file(Path(name), pin)
        reads.add(str(Path(name).resolve()))
    require(str(Path(sys.executable).resolve()) == source["runtime"]["python"], "interpreter binding")
    for item in request["inputs"].values():
        p = Path(item["path"]).resolve()
        checked_file(p, item["identity"])
        reads.add(str(p))
    tasks = read_json(Path(request["inputs"]["tasks"]["path"]))
    require(validate_population(tasks) == request["tasks"], "complete issued population")
    state = read_json(Path(request["inputs"]["state"]["path"]))
    require(identity(state) == request["state"] and state["mode"] in MODES, "issued eligibility state")
    require(state["revision"] == MODES.index(state["mode"]), "eligibility revision")
    # -B suppresses bytecode writes, not reads. Enforce source-only loading rather
    # than allow undeclared .pyc probes or count ordinary cache misses as breaches.
    import importlib.machinery
    def source_only(loader, fullname):
        filename = loader.get_filename(fullname)
        return compile(loader.get_data(filename), filename, "exec",
                       dont_inherit=True, optimize=sys.flags.optimize)
    importlib.machinery.SourceFileLoader.get_code = source_only
    blocked, hook = audit_boundary(reads, output)
    sys.addaudithook(hook)
    sys.path[:0] = [str(stage / "engine"), str(stage / "engine/vendor"), str(stage / "runtime")]
    import goal_library as GL
    import goal_solve as GS
    import goal_native as GN
    bundle = {n: Path(request["inputs"][n]["path"]).read_bytes() for n in BUNDLE_NAMES}
    manifest = json.loads(bundle["manifest.json"])
    library = GL.Library(bundle["base.mm"], bundle["joined.mm"], manifest,
                         GL.identity(manifest), bundle["receipt.json"], GL.raw_identity(bundle["receipt.json"]))
    require(state["library"] == library.pin, "state/library binding")
    require(state["eligible"] == ([] if state["mode"] == "resident-disabled" else library.cohort_labels), "exact cohort eligibility")
    native_sources = {k: {"path": str(stage / "engine/vendor" / name),
                         **GL.raw_identity((stage / "engine/vendor" / name).read_bytes())}
                      for k, name in {"index": "trace_source.py", "adapter": "trace_adapter.py", "verifier": "mmverify.py"}.items()}
    rows = []
    for i, task in enumerate(tasks):
        row_started = time.perf_counter()
        result = GS.solve(task, library, state["mode"])
        native = None
        if result["terminal"] == "GENERATED_PROOF_PENDING_NATIVE":
            native = GN.execute(task, result, GL.identity(result), library,
                                "issued-goal-" + str(i), ["issued-hyp-" + str(i) + "-" + str(j) for j in range(len(task["premises"]))],
                                Path(request["inputs"]["joined.mm"]["path"]), output / ("native-" + str(i)), native_sources)
        row = {"index": i, "task": identity(task), "solve": result, "native": native,
               "wall_seconds": time.perf_counter() - row_started}
        write_new(output / ("row-" + str(i) + ".json"), encoded(row) + b"\n")
        rows.append(row)
    imports = {n: {"path": str(Path(m.__file__).resolve()),
                   "identity": raw_id(Path(m.__file__).resolve().read_bytes())}
               for n, m in sorted(sys.modules.items()) if getattr(m, "__file__", None)
               and Path(m.__file__).is_file()}
    # Explicitly include file-loaded donors that intentionally do not register in sys.modules.
    for n, m in (("FS.C", GS.FS.C), ("FS.M", GS.FS.M), ("FS.T", GS.FS.T), ("FS.M.T", GS.FS.M.T)):
        p = Path(m.__file__).resolve()
        imports[n] = {"path": str(p), "identity": raw_id(p.read_bytes())}
    require(all(row["path"] in reads for row in imports.values()), "undeclared imported module")
    for name, pin in source["files"].items():
        checked_file(relative(stage, name), pin)
    for name, pin in source["runtime"]["files"].items():
        checked_file(Path(name), pin)
    for item in request["inputs"].values():
        checked_file(Path(item["path"]), item["identity"])
    usage = resource.getrusage(resource.RUSAGE_SELF)
    report = {"schema": SCHEMA + ".worker", "occurrence": request["occurrence"],
              "request": raw_id(request_raw), "source": request["source"], "state": request["state"],
              "pid": os.getpid(), "parent_pid": os.getppid(), "mode": state["mode"],
              "population": request["tasks"], "rows": rows, "blocked_events": blocked,
              "imports": imports, "library_costs": library.costs,
              "resources": {"wall_seconds": time.perf_counter() - started,
                            "user_cpu_seconds": usage.ru_utime, "system_cpu_seconds": usage.ru_stime,
                            "peak_rss_kib_linux": usage.ru_maxrss},
              "terminal": "COMPLETE_ENGINEERING_INVOCATION" if not blocked else "CANNOT_CHECK_EXECUTION_BOUNDARY"}
    write_new(output / "WORKER.json", encoded(report) + b"\n")
    print(json.dumps({"terminal": report["terminal"], "tasks": len(rows), "pid": os.getpid()}), flush=True)
    return 0 if not blocked else 2


def validate_row(task: dict[str, Any], row: dict[str, Any], mode: str) -> None:
    """Check self-consistency; proof authority still comes from the observed checker.

    This does not infer validity from JSON alone. The parent separately binds each
    row and native receipt to the files emitted by its exact successful child.
    """
    require(row["task"] == identity(task), "row task identity")
    solved = row["solve"]
    require(solved.get("task") == identity(task) and solved.get("mode") == mode,
            "solver task/mode binding")
    native = row["native"]
    if native is None:
        require(solved["terminal"] != "GENERATED_PROOF_PENDING_NATIVE", "missing native attempt")
        return
    require(solved["terminal"] == "GENERATED_PROOF_PENDING_NATIVE", "native without generated proof")
    if native["terminal"] != "GENERATED_PROOF_NATIVE_VERIFIED":
        return
    require(native["generated_result"] == identity(solved), "native/generated result identity")
    require(native["library"] == solved["library"], "native library identity")
    claim = native["issued_claim"]
    require(claim["query"] == task["query"] and claim["premises"] == task["premises"],
            "native goal/premise identity")
    require(len(claim["holes"]) == len(task["premises"]), "native hole population")
    mapping = {"search-hyp-" + str(i): h for i, h in enumerate(claim["holes"])}
    require(claim["proof"] == [mapping.get(x, x) for x in solved["generated_proof"]],
            "native emitted proof identity")
    require(claim["parameters"] == [{k: p[k] for k in ("type", "variable", "floating_label")}
                                    for p in task["context"]["parameters"]], "native frame identity")
    native_result = native["native_result"]
    require(native_result["terminal"] == "NATIVE_VERIFIED" and native_result["native_calls"] == 1
            and native_result["error"] is None and native["native_calls"] == 1, "current checker success")
    require(native_result["claims_sha256"] == identity([claim])["sha256"], "native claims identity")
    trace = native["trace"]
    require(native_result["traces"] == {claim["label"]: trace}
            and trace["source"]["proof"] == claim["proof"]
            and trace["source"]["statement"] == task["query"], "current trace identity")
    require(native_result["contracts"] == native["used_contracts"], "current USED identity")
    consumed = [x for x in claim["proof"] if x in solved["resident_cohort"]]
    require(native["selected_cohort_labels"] == consumed
            and set(native["used_contracts"]) & set(solved["resident_cohort"]) == set(consumed),
            "consumption proof/trace identity")
    require(mode != "resident-disabled" or not consumed, "disabled native method use")


def verify_retained_outputs(output: Path, tasks: list[dict[str, Any]], report: dict[str, Any],
                            manifest: dict[str, Any]) -> dict[str, Any]:
    """Bind all rows, requests, logs and databases without rerunning native proofs."""
    observed = {}
    prefix = (output.parent.parent / "inputs/joined.mm").read_bytes()
    expected_prefix = manifest["joined_prefix"]
    require(raw_id(prefix) == expected_prefix, "persisted prefix changed")
    expected_proofs = [r["label"] for r in manifest["joined_proofs"]]
    expected_axioms = [r["label"] for r in manifest["axioms"]]
    require(len(report["rows"]) == len(tasks), "retained complete population")
    for i, (task, row) in enumerate(zip(tasks, report["rows"])):
        validate_row(task, row, report["mode"])
        path = output / ("row-" + str(i) + ".json")
        require(path.read_bytes() == encoded(row) + b"\n", "retained row differs")
        observed[path.name] = raw_id(path.read_bytes())
        native = row["native"]
        if native is None or "native_result" not in native:
            continue
        directory = output / ("native-" + str(i))
        receipt = native["native_result"]
        require((directory / "result.json").read_bytes() == encoded(receipt) + b"\n",
                "retained native receipt differs")
        request = read_json(directory / "request.json")
        require(request["claims"] == [native["issued_claim"]]
                and request["sources"] == native["sources"]
                and request["authority"]["prefix"] == expected_prefix,
                "retained native request differs")
        for name in ("request.json", "result.json", "native.log", "suffix.mm"):
            observed[(directory / name).relative_to(output).as_posix()] = raw_id((directory / name).read_bytes())
        require(raw_id((directory / "native.log").read_bytes()) == receipt["log"], "retained checker log differs")
        require(raw_id((directory / "suffix.mm").read_bytes()) == receipt["suffix"], "retained suffix differs")
        if native["terminal"] == "GENERATED_PROOF_NATIVE_VERIFIED":
            database = (directory / "database.mm").read_bytes()
            require(database == prefix + b"\n" + (directory / "suffix.mm").read_bytes(), "retained database differs")
            require(receipt["database"] == {"path": str(directory / "database.mm"), **raw_id(database)}, "database receipt differs")
            require(receipt["verified_labels"] == expected_proofs + [native["issued_claim"]["label"]]
                    and receipt["trusted_assertions"] == expected_axioms, "full proof/trust population")
            observed[(directory / "database.mm").relative_to(output).as_posix()] = raw_id(database)
    return observed


def reconcile(tasks: list[dict[str, Any]], reports: list[dict[str, Any]]) -> dict[str, Any]:
    wanted = validate_population(tasks)
    require(type(reports) is list and len(reports) == 3, "complete three-arm population")
    occurrences = set()
    source_ids = set()
    for mode, report in zip(MODES, reports):
        require(report["mode"] == mode and report["terminal"] == "COMPLETE_ENGINEERING_INVOCATION", "complete ordered worker modes")
        require(report["population"] == wanted and not report["blocked_events"], "worker population/boundary")
        require(report["occurrence"] not in occurrences, "invocation occurrence collision")
        occurrences.add(report["occurrence"])
        source_ids.add(report["source"]["sha256"])
        require(len(report["rows"]) == len(wanted), "truncated worker rows")
        require([r["index"] for r in report["rows"]] == list(range(len(wanted))), "row order/duplicates")
        require([r["task"] for r in report["rows"]] == wanted, "task row binding")
    require(len(source_ids) == 1, "cross-arm source identity")
    rows = []
    for i, pin in enumerate(wanted):
        arms = [r["rows"][i] for r in reports]
        for mode, arm in zip(MODES, arms):
            validate_row(tasks[i], arm, mode)
        solved = [r["native"] is not None and r["native"]["terminal"] == "GENERATED_PROOF_NATIVE_VERIFIED" for r in arms]
        shared = ("bank_identity", "grounded_actions_identity", "emission_syntax_identity", "library")
        parity = all(all(k in r["solve"] for r in arms) and arms[0]["solve"][k] == arms[1]["solve"][k] == arms[2]["solve"][k] for k in shared)
        e, d, r = (a["solve"] for a in arms)
        restored = solved[0] == solved[2] and all(e.get(k) == r.get(k) for k in ("terminal", "generated_proof", "decision_count", "selected_cohort_labels"))
        consumed = arms[0]["native"].get("selected_cohort_labels", []) if solved[0] else []
        require(not (arms[1]["native"] or {}).get("selected_cohort_labels", []), "disabled native method use")
        # Wall time is reported, never used to make a causal speed claim in one ordered run.
        bounded_absence = (d.get("terminal") == "NO_PROOF_IN_REGISTERED_FINITE_BANK"
                           and d.get("parent_scope_complete") is True
                           and d.get("work", {}).get("exhausted") is False
                           and arms[1]["native"] is None)
        effect = solved[0] and (bounded_absence or (solved[1] and
                 e.get("decision_count", math.inf) < d.get("decision_count", math.inf)))
        supported = bool(parity and restored and all((solved[0], solved[2])) and consumed and effect)
        rows.append({"index": i, "task": pin, "native_verified": solved,
                     "preparation_parity": parity, "restored_result": restored,
                     "selected_cohort_labels": consumed, "causal_decision_witness": supported,
                     "decision_counts": [a["solve"].get("decision_count") for a in arms],
                     "terminals": [(a["native"] or a["solve"])["terminal"] for a in arms]})
    return {"schema": SCHEMA + ".comparison", "rows": rows,
            "causal_decision_witnesses": sum(r["causal_decision_witness"] for r in rows),
            "checked_cohort_use_tasks": sum(bool(r["selected_cohort_labels"]) for r in rows),
            "all_preparation_parity": all(r["preparation_parity"] for r in rows),
            "all_restored": all(r["restored_result"] for r in rows),
            "scope": "Ordinary parent only; no OCM architectural comparison, scientific admission, or lifetime payback claim."}


def run(repo: Path, bundle: Path, tasks_path: Path, output: Path, hard_wall: float = 300.0) -> dict[str, Any]:
    started = time.perf_counter()
    require(math.isfinite(hard_wall) and hard_wall > 0, "hard wall bound")
    tasks = read_json(tasks_path)
    task_pins = validate_population(tasks)
    require(not output.exists(), "fresh run directory required")
    output.mkdir(parents=True)
    source = stage_engine(repo, output / "stage")
    stage = (output / "stage").resolve()
    inputs = output / "inputs"
    for n in BUNDLE_NAMES:
        write_new(inputs / n, (bundle / n).read_bytes())
    write_new(inputs / "tasks.json", encoded(tasks) + b"\n")
    manifest = read_json(inputs / "manifest.json")
    library_pin = identity(manifest)
    cohort = [r["label"] for r in manifest["cohort"]]
    source_pin = raw_id((stage / "SOURCE.json").read_bytes())
    reports = []
    prior = None
    observations = []
    for revision, mode in enumerate(MODES):
        state = {"schema": SCHEMA + ".eligibility", "revision": revision, "mode": mode,
                 "previous": prior, "library": library_pin,
                 "eligible": [] if mode == "resident-disabled" else cohort}
        state_path = (output / "states" / (str(revision) + ".json")).resolve()
        write_new(state_path, encoded(state) + b"\n")
        temporary = output / "CURRENT.tmp"
        write_new(temporary, encoded(state) + b"\n")
        os.replace(temporary, output / "CURRENT.json")
        fd = os.open(output, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        prior = identity(state)
        request_inputs = {n: {"path": str((inputs / n).resolve()), "identity": raw_id((inputs / n).read_bytes())} for n in BUNDLE_NAMES}
        request_inputs.update(tasks={"path": str((inputs / "tasks.json").resolve()), "identity": raw_id((inputs / "tasks.json").read_bytes())},
                              state={"path": str(state_path), "identity": raw_id(state_path.read_bytes())})
        arm = output / ("arm-" + str(revision))
        arm.mkdir()
        request = {"schema": SCHEMA + ".request", "occurrence": uuid.uuid4().hex,
                   "stage": str(stage), "source": source_pin, "inputs": request_inputs,
                   "state": prior, "tasks": task_pins, "output": str((arm / "output").resolve()),
                   "limits": {"memory_bytes": 2_000_000_000, "cpu_seconds": max(1, math.ceil(hard_wall))}}
        request_path = (arm / "REQUEST.json").resolve()
        write_new(request_path, encoded(request) + b"\n")
        argv = [sys.executable, "-I", "-S", "-B", str(stage / "worker.py"), "--worker", str(request_path), hashlib.sha256(request_path.read_bytes()).hexdigest()]
        tick = time.perf_counter()
        with (arm / "stdout.txt").open("xb") as stdout, (arm / "stderr.txt").open("xb") as stderr:
            child = subprocess.Popen(argv, cwd=arm, env={"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"},
                                     stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True)
            timed_out = False
            try:
                returncode = child.wait(timeout=hard_wall)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                returncode = child.wait()
        observation = {"mode": mode, "occurrence": request["occurrence"], "pid": child.pid,
                       "parent_pid": os.getpid(), "argv": argv, "cwd": str(arm.resolve()),
                       "returncode": returncode, "timed_out": timed_out,
                       "wall_seconds": time.perf_counter() - tick,
                       "request": raw_id(request_path.read_bytes()),
                       "stdout": raw_id((arm / "stdout.txt").read_bytes()),
                       "stderr": raw_id((arm / "stderr.txt").read_bytes())}
        write_new(arm / "PROCESS.json", encoded(observation) + b"\n")
        observations.append(observation)
        if returncode != 0:
            break
        report = read_json(arm / "output/WORKER.json")
        require(report["pid"] == child.pid and report["parent_pid"] == os.getpid(), "actual child identity")
        require(report["request"] == observation["request"] and report["occurrence"] == request["occurrence"], "current invocation binding")
        require(report["source"] == source_pin and report["state"] == prior, "worker source/state binding")
        require((output / "CURRENT.json").read_bytes() == state_path.read_bytes(), "concurrent eligibility change")
        retained = verify_retained_outputs(arm / "output", tasks, report, manifest)
        write_new(arm / "RECONCILIATION.json", encoded({"request": observation["request"],
                  "worker": raw_id((arm / "output/WORKER.json").read_bytes()), "files": retained}) + b"\n")
        reports.append(report)
    comparison = reconcile(tasks, reports) if len(reports) == 3 else None
    result = {"schema": SCHEMA, "terminal": "COMPLETE_THREE_ARM_ENGINEERING_RUN" if comparison else "CANNOT_CHECK_INCOMPLETE_WORKER_SEQUENCE",
              "source": source_pin, "population": task_pins, "observations": observations,
              "comparison": comparison, "wall_seconds": time.perf_counter() - started,
              "source_staging_bytes": sum(p["bytes"] for p in source["files"].values()),
              "runtime_pin_bytes": sum(p["bytes"] for p in source["runtime"]["files"].values()),
              "input_bytes": sum(p.stat().st_size for p in inputs.iterdir()),
              "scope": "Recorded cold-process ordinary-parent comparison; historical acquisition and engineering costs are not claimed paid back."}
    write_new(output / "RESULT.json", encoded(result) + b"\n")
    return result


def main() -> int:
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        return _worker(Path(sys.argv[2]), sys.argv[3])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hard-wall", type=float, default=300.0)
    args = parser.parse_args()
    result = run(args.repo.resolve(), args.bundle.resolve(), args.tasks.resolve(), args.output.resolve(), args.hard_wall)
    print(json.dumps({"terminal": result["terminal"], "comparison": result["comparison"]}, sort_keys=True))
    return 0 if result["comparison"] is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
