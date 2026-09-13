"""Reserve one attempt before invoking the immutable V5 measurement process."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

from frozen_contract_v1 import (AuditError, GRAND, HARNESS, HERE, PARENT, PREREG,
    canonical, frozen, implementation_bindings, require, runtime_identity, sha,
    strict_json, write_new)


def machine_identity():
    path = Path("/etc/machine-id")
    require(path.is_file() and bool(path.read_text().strip()), "stable Linux machine-id required")
    return sha(path.read_bytes().strip())


def utc():
    return datetime.now(timezone.utc).isoformat()


def canonical_identity(machine, runtime):
    # Display labels, cwd, execution surface, and executable aliases cannot open a retry.
    return {"experiment": "NN_NONNN_POINT_PARITY3_V5_PORTABLE_REPLICATION",
            "machine_identity_sha256": machine,
            "python_implementation": runtime["python_implementation"],
            "python_version": runtime["python_version"]}


def reserve(registry, identity):
    registry = Path(registry).resolve()
    registry.mkdir(parents=True, exist_ok=True)
    key = sha(canonical(identity).encode())
    attempt = registry / key
    attempt.mkdir()  # Exclusive atomic mkdir: collision occurs before any invocation.
    fd = os.open(registry, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return attempt


def _invoke(command, stdout, stderr):
    with stdout.open("xb") as out, stderr.open("xb") as err:
        return subprocess.run(command, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                              check=False).returncode


def run_attempt(registry, host_label, source_base=GRAND):
    require(platform.system() == "Linux", "measurement execution is Linux-only; never run on Mac")
    require(platform.python_implementation() == "CPython" and sys.version_info >= (3, 11),
            "launcher requires explicit CPython >=3.11")
    require(re.fullmatch(r"[a-z][a-z0-9-]{0,63}", host_label) is not None,
            "host label must be canonical lowercase ASCII")
    runtime = runtime_identity()
    identity = canonical_identity(machine_identity(), runtime)
    attempt = reserve(registry, identity)
    expected = strict_json((HERE / "FROZEN_INPUTS_V1.json").read_bytes())
    record = {"schema": "PARITY3_FIRST_ATTEMPT_CUSTODY_V1", "identity": identity,
        "host_label": host_label, "runtime": runtime, "started_utc": utc(),
        "sources": {name: expected["sources"][name] for name in (HARNESS, PREREG, PARENT)},
        "source_commit": expected["source_commit"], "implementation": implementation_bindings(),
        "execution_command_policy": "same explicit interpreter; -I -B; immutable V5 snapshot",
        "scope": "first attempt within the declared persistent registry; no host attestation",
        "accounting": "V5 deployment coordinates exclude source construction and custody overhead"}
    write_new(attempt / "ATTEMPT.json", record)
    try:
        frozen(source_base)
        sources = attempt / "sources"
        sources.mkdir()
        for name in (HARNESS, PREREG, PARENT):
            with (sources / name).open("xb") as stream:
                stream.write((source_base / name).read_bytes())
        frozen(sources)
        command = [str(Path(sys.executable).resolve()), "-I", "-B", str(sources / HARNESS),
                   "--host-label", host_label, "--out", str(attempt / "packet.json")]
        code = _invoke(command, attempt / "stdout.json", attempt / "stderr.txt")
        frozen(sources)
        require(runtime_identity() == runtime, "interpreter binary changed during attempt")
        result = {"state": "PROCESS_EXITED", "returncode": code}
    except Exception as exc:
        result = {"state": "LAUNCH_OR_CUSTODY_FAILED",
                  "error_type": type(exc).__name__, "error": str(exc)}
    result.update({"schema": "PARITY3_ATTEMPT_RESULT_V1", "completed_utc": utc(),
                   "attempt_sha256": sha((attempt / "ATTEMPT.json").read_bytes()),
                   "files": {name: sha((attempt / name).read_bytes())
                       for name in ("packet.json", "stdout.json", "stderr.txt")
                       if (attempt / name).is_file()}})
    write_new(attempt / "RESULT.json", result)
    return attempt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True,
                        help="one persistent registry shared by all checkouts on this host")
    parser.add_argument("--host-label", required=True)
    parser.add_argument("--execute-first-attempt", action="store_true", required=True)
    args = parser.parse_args()
    try:
        attempt = run_attempt(args.registry, args.host_label)
        print(attempt)
        result = strict_json((attempt / "RESULT.json").read_bytes())
        return 0 if result["state"] == "PROCESS_EXITED" and result["returncode"] == 0 else 2
    except (AuditError, FileExistsError) as exc:
        print("PARITY3_LAUNCH_REFUSED: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
