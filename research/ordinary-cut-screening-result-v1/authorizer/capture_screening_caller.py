"""Create-only custody recorder for one separately gated observer invocation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def identity(path):
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")


def main():
    observer, output = map(Path, sys.argv[1:])
    observer = observer.resolve(strict=True)
    python = Path(sys.executable).resolve(strict=True)
    assert sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode
    assert not sys.flags.optimize
    assert not output.exists() and output.name not in {p.name for p in output.parent.iterdir()}
    pins = {str(p): identity(p) for p in (observer, python, Path(__file__).resolve())}
    argv = [str(python), "-I", "-S", "-B", str(observer)]
    output.mkdir()
    write(output / "START.json", {"pid": os.getpid(), "argv": argv, "cwd": "/tmp", "pins": pins})
    started = time.perf_counter()
    with (output / "stdout.log").open("xb") as stdout, (output / "stderr.log").open("xb") as stderr:
        child = subprocess.Popen(argv, cwd="/tmp", stdin=subprocess.DEVNULL,
                                 stdout=stdout, stderr=stderr,
                                 env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
        pid, status, usage = os.wait4(child.pid, 0)
        child.returncode = os.waitstatus_to_exitcode(status)
    elapsed = time.perf_counter() - started
    unchanged = {p: identity(Path(p)) == pin for p, pin in pins.items()}
    result = {"schema": "ordinary.screening-caller-process.v1", "caller_pid": os.getpid(),
              "pid": child.pid, "reaped": pid == child.pid, "exit_code": child.returncode,
              "argv": argv, "cwd": "/tmp", "process_wall_s": elapsed,
              "user_cpu_s": usage.ru_utime, "system_cpu_s": usage.ru_stime,
              "rss_kib": usage.ru_maxrss, "source_pins_unchanged": unchanged,
              "stdout": identity(output / "stdout.log"), "stderr": identity(output / "stderr.log"),
              "measurement_scope": "One observer Popen through wait4 and log closure; includes nested child work. Setup, final custody and receipt serialization excluded. No automatic retry; no lifetime-cost claim."}
    write(output / "PROCESS.json", result)
    print(json.dumps({"caller_receipt": str(output / "PROCESS.json"), "pid": child.pid,
                      "exit_code": child.returncode, "reaped": pid == child.pid}))
    return 0 if child.returncode == 0 and pid == child.pid and all(unchanged.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
