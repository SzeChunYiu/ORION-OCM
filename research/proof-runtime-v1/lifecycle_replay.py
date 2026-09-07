"""Source-bound, data-only restart observation. Trusted host, not a Python sandbox."""
import hashlib
import base64
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


# Preserve incumbent OCM JSON encoding, including declared infinite resource bounds.
def raw(value): return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_bytes())


def save(path, value):
    with Path(path).open("xb") as f: f.write(raw(value)); f.flush(); os.fsync(f.fileno())
    fd = os.open(Path(path).parent, os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def source_files(repo):
    repo = Path(repo); here = repo / "research/proof-runtime-v1"
    paths = [p for p in (repo / "src/ocm").rglob("*") if p.suffix in (".py", ".json")]
    for folder in (here, repo / "research/mechanical-proof-v1"):
        paths += [p for p in folder.glob("*.py") if not p.name.startswith("test_")]
    paths += [here / "requirements-engineering.txt", repo / "research/mechanical-proof-v1/Target.lean",
              repo / "research/proof-replay-v1/Foundation.lean"]
    if any(p.is_symlink() or not p.is_file() for p in paths): raise ValueError("linked or absent frozen source")
    return {str(p.resolve()): sha(p) for p in sorted(paths)}


def python_files(executable):
    binary = Path(executable).resolve(); prefix = binary.parent.parent
    library = prefix / "lib/python3.11"
    if not library.is_dir(): raise ValueError("registered CPython 3.11 standard library absent")
    paths = [binary] + [p for p in library.rglob("*") if p.suffix in (".py", ".so", ".zip")
                       and not {"site-packages", "__pycache__"}.intersection(p.parts)]
    return {str(p.resolve()): sha(p) for p in sorted(paths)}


def make_freeze(repo, manifest, expected_sha, directory, executable):
    from session_bindings import fixed_task
    repo, manifest, directory = map(lambda p: Path(p).resolve(), (repo, manifest, directory))
    if manifest.is_symlink() or sha(manifest) != expected_sha: raise ValueError("runtime manifest freeze mismatch")
    sources = source_files(repo); snapshot = directory / "source-snapshot"; snapshot.mkdir()
    bindings = {str(manifest): expected_sha}
    for name, digest in sources.items():
        path = Path(name)
        # A source outside the repository is useful only as a mocked test sentinel.
        relative = path.relative_to(repo) if path.is_relative_to(repo) else Path("external") / path.name
        target = snapshot / relative; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes()); bindings[str(target)] = digest
    copied = directory / "runtime-manifest.json"; copied.write_bytes(manifest.read_bytes())
    bindings[str(copied)] = expected_sha
    task = directory / "registered-task.json"; save(task, fixed_task()); bindings[str(task)] = sha(task)
    value = {"schema": "ocm.proof-runtime-lifecycle-freeze.v1", "repo": str(repo), "directory": str(directory),
             "runtime_manifest": str(manifest), "runtime_sha256": expected_sha, "sources": sources,
             "python_executable": str(Path(executable).resolve()), "python": python_files(executable),
             "inputs_and_snapshot": bindings, "task_sha256": sha(task),
             "scope": "Source/input/manifest and host Python identities; ProofSession separately verifies full native runtime trees around dispatch."}
    target = directory / "freeze.json"; save(target, value); digest = sha(target)
    verify_freeze(target, digest); return target, digest


def verify_freeze(path, expected_sha):
    if sha(path) != expected_sha: raise ValueError("freeze record changed")
    value = read(path)
    if source_files(value["repo"]) != value["sources"]: raise ValueError("source freeze changed")
    if python_files(value["python_executable"]) != value["python"]: raise ValueError("Python freeze changed")
    for name, digest in value["inputs_and_snapshot"].items():
        if not Path(name).is_file() or sha(name) != digest: raise ValueError("input/snapshot freeze changed: " + name)
    return value


def activity(directory):
    directory = Path(directory)
    paths = [p for root in directory.glob("session-*") for p in root.rglob("*") if p.is_file()]
    return {str(p.relative_to(directory)): sha(p) for p in sorted(paths)}


def persistent_files(directory):
    paths = [p for name in ("ocm", "issuer") for p in (Path(directory) / name).rglob("*") if p.is_file()]
    return {str(p): sha(p) for p in sorted(paths)}


def bound_imports(frozen):
    imports = {n: str(Path(m.__file__).resolve()) for n, m in sorted(sys.modules.items())
               if getattr(m, "__file__", None)}
    allowed = frozen["sources"] | frozen["python"]
    if any(path not in allowed or sha(path) != allowed[path] for path in imports.values()):
        raise ValueError("unbound imported module origin")
    return imports


def state_mark(view):
    from ocm.store.canonical import canonical_bytes
    return {"events": [e.event_hash for e in view.rt.events],
            "evidence": hashlib.sha256(canonical_bytes(view.rt.state.evidence.as_dict())).hexdigest(),
            "issuer": [e.entry_hash for e in view.journal.entries()], "activity": activity(view.root.parent),
            "persistent": persistent_files(view.root.parent), "state": view.rt.state.snapshot()}


def observe(view):
    before = state_mark(view); status = view.proof_status(); after = state_mark(view)
    if before != after: raise ValueError("status mutated state or dispatched")
    return status


def restore_status(directory, freeze_path, freeze_sha):
    frozen = verify_freeze(freeze_path, freeze_sha); directory = Path(directory).resolve()
    if str(directory) != frozen["directory"]: raise ValueError("restart directory differs from freeze")
    from ocm.runtime.ocm_runtime import OCMRuntime
    from adapter import ProofRuntimeView
    before = (activity(directory), persistent_files(directory))
    view = ProofRuntimeView.restore(OCMRuntime(directory / "ocm"), directory / "issuer")
    status = observe(view)
    result = {"status": status, "session_bound": view.session is not None,
              "host_operators": sorted(view.rt._host_operators),
              "executable_operators": sorted(view.rt.state.operators.operators),
              "read_only": before == (activity(directory), persistent_files(directory)), "pid": os.getpid(),
              "imports": bound_imports(frozen), "imports_bound": True, "python_version": sys.version}
    if result["session_bound"] or result["host_operators"] or result["executable_operators"] or not result["read_only"]:
        raise ValueError("restart rebound executable code or dispatched")
    verify_freeze(freeze_path, freeze_sha)
    return result


def replay(directory, freeze_path, freeze_sha, executable):
    frozen = verify_freeze(freeze_path, freeze_sha)
    if str(Path(executable).resolve()) != frozen["python_executable"]: raise ValueError("replay interpreter changed")
    argv = [str(executable), "-I", "-S", "-B", str(Path(__file__).resolve()),
            str(Path(directory).resolve()), str(freeze_path), freeze_sha]
    env = {"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}; started = time.monotonic()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                            cwd="/", start_new_session=True)
    terminal = "COMPLETED"; reason = None; stdout = stderr = b""
    try: stdout, stderr = proc.communicate(timeout=60)
    except BaseException as exc:
        terminal = "TIMEOUT" if isinstance(exc, subprocess.TimeoutExpired) else "INTERRUPTED"
        reason = type(exc).__name__ + ": " + str(exc)
    finally:
        try: os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        if terminal != "COMPLETED":
            try: stdout, stderr = proc.communicate(timeout=5)
            except BaseException as exc:
                reason += "; drain: " + type(exc).__name__ + ": " + str(exc)
        if proc.poll() is None: proc.wait(timeout=5)
        try: os.killpg(proc.pid, 0); group_absent = False
        except ProcessLookupError: group_absent = True
    record = {"argv": argv, "environment": env, "pid": proc.pid, "returncode": proc.returncode,
              "terminal": terminal, "reason": reason, "stdout": stdout.decode("utf-8", "replace"),
              "stderr": stderr.decode("utf-8", "replace"), "stdout_base64": base64.b64encode(stdout).decode(),
              "stderr_base64": base64.b64encode(stderr).decode(), "wall_s": time.monotonic() - started,
              "cleanup": {"reaped": proc.poll() is not None, "group_absent": group_absent},
              "cpu_s": None, "peak_rss_bytes": None}
    try: record["result"] = json.loads(stdout)
    except (ValueError, UnicodeDecodeError): record["result"] = None
    return record


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    # These host code roots come from this bound entrypoint, never the saved ledger.
    sys.path[:0] = [str(root / "src"), str(Path(__file__).resolve().parent)]
    try:
        result = restore_status(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
        sys.stdout.buffer.write(raw(result))
    except Exception as exc:
        sys.stderr.write(type(exc).__name__ + ": " + str(exc) + "\n"); raise SystemExit(1)
