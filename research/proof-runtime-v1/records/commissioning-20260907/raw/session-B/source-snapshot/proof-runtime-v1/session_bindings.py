"""Canonical fixed-task, source and artifact custody for a trusted host session."""
from hashlib import sha256
import json
from pathlib import Path
import session_dependencies as D

HERE = Path(__file__).resolve().parent
LIMITS = {"max_application_depth": 5, "max_terms": 5000, "max_steps": 20000,
          "max_intro": 32, "max_nodes": 4096, "max_normalize": 20000}


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def digest(value): return sha256(value).hexdigest()
def detached(value): return json.loads(canonical(value))


def write_bytes(path, value):
    with Path(path).open("xb") as stream: stream.write(value)


def write_json(path, value): write_bytes(path, canonical(value))


def fixed_task(task=None):
    expected = detached(D.f0_fixture())
    if task is None: return expected
    # JSON canonicalization must not silently equate booleans with integers.
    if type(task) is not dict or set(task) - {"goal", "constants", "limits"}:
        raise ValueError("unregistered task fields")
    constants = task.get("constants")
    if type(constants) is not dict or not constants:
        raise ValueError("fixed signature registry required")
    if any(type(k) is not str or k not in expected["constants"] for k in constants):
        raise ValueError("unregistered constant identity")
    if "0" not in constants or any(canonical(v) != canonical(expected["constants"][k]) for k, v in constants.items()):
        raise ValueError("fixed constant signatures differ")
    if canonical(task.get("goal")) != canonical(expected["goal"]):
        raise ValueError("fixed formal task goal differs")
    limits = task.get("limits", {})
    if type(limits) is not dict or set(limits) - set(LIMITS):
        raise ValueError("unregistered limit fields")
    for key, value in limits.items():
        if type(value) is not int or not (0 if key == "max_application_depth" else 1) <= value <= LIMITS[key]:
            raise ValueError("limit exceeds registered commissioning envelope")
    return detached(task)


def source_paths():
    result = {"mechanical-proof-v1/" + n: D.MECHANICAL / n
              for n in sorted({name + ".py" for name in D.NAMES} | set(D.WORKER_FILES) | {"Target.lean"})}
    result["proof-replay-v1/Foundation.lean"] = D.MECHANICAL.parent / "proof-replay-v1/Foundation.lean"
    for name in ("closed_session.py", "session_dependencies.py", "session_bindings.py", "session_dispatch.py"):
        result["proof-runtime-v1/" + name] = HERE / name
    return result


def source_inventory():
    result = {}
    for name, path in source_paths().items():
        if path.is_symlink() or not path.is_file(): raise ValueError("source missing or linked")
        result[name] = D.file_hash(path)
    return result


def inventory(root):
    result = {}
    for path in sorted(Path(root).rglob("*")):
        if path.is_symlink(): raise ValueError("artifact link not permitted")
        if path.is_file(): result[path.relative_to(root).as_posix()] = D.file_hash(path)
        elif not path.is_dir(): raise ValueError("nonregular artifact")
    return result


def runtime_check(runtime):
    # The manifest is externally pinned; mounts must match its exact file inventory.
    libs = runtime["shared_libraries"]
    expected = [[data["source"], guest] for guest, data in sorted(libs["files"].items())]
    if libs["mounts"] != expected: raise ValueError("shared mounts differ from registered files")
    for source, guest in expected:
        if not guest.startswith(("/lib/", "/lib64/")) or not Path(source).is_file():
            raise ValueError("shared-library mount is not a registered library file")
    D.verify_runtime(runtime)
