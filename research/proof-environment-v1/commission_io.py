"""Durable host-driver logs. Native cleanup authority remains in the returned receipt."""
import base64
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import env_inputs as I

HERE = Path(__file__).resolve().parent


def record(path): return {"path": str(Path(path)), **I.file_record(path)}


def launch(operation, freeze, output, matrix, log_root):
    runtime = matrix["runtime"]; log_root.mkdir()
    argv = [sys.executable, "-I", "-S", str(HERE / "environment.py"), operation,
            "--freeze", freeze["path"], "--freeze-sha256", freeze["sha256"],
            "--runtime", runtime["path"], "--runtime-sha256", runtime["sha256"],
            "--output", str(output), "--timeout-s", str(matrix["timeout_s"]),
            "--max-output-bytes", str(matrix["max_output_bytes"])]
    started = time.monotonic(); process = None; interrupted = None; error = None
    with (log_root / "stdout.bin").open("xb") as stdout, (log_root / "stderr.bin").open("xb") as stderr:
        try:
            process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True)
            process.wait()
        except (KeyboardInterrupt, SystemExit) as exc: interrupted = exc
        except Exception as exc: error = type(exc).__name__ + ": " + str(exc)
        finally:
            if process is not None:
                try: os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                process.wait()
    group_absent = None
    if process is not None:
        try: os.killpg(process.pid, 0); group_absent = False
        except ProcessLookupError: group_absent = True
    envelope = {"argv": argv, "returncode": process.returncode if process else None,
                "pid": process.pid if process else None, "wall_s": time.monotonic() - started,
                "error": error, "interrupted": interrupted is not None,
                "cleanup": {"reaped": process is not None, "group_absent": group_absent},
                "scope": "Host driver group only. Native cleanup needs returned receipt; CPU/RSS unmeasured."}
    for key in ("stdout", "stderr"):
        path = log_root / (key + ".bin"); envelope[key] = record(path)
        envelope[key + "_base64"] = base64.b64encode(path.read_bytes()).decode()
    result = None; binding = None
    try:
        path = output / ("check.json" if operation == "check" else "receipt.json")
        raw = I.regular(path).read_bytes(); result = I.parse_json(raw)
        if type(result) is not dict: raise ValueError("host receipt must be an object")
        binding = {"path": str(path), "sha256": I.digest(raw), "bytes": len(raw)}
        I.verify_file(binding)
    except Exception as exc:
        result = None; binding = None; envelope["receipt_error"] = type(exc).__name__ + ": " + str(exc)
    I.write_json(log_root / "process.json", envelope)
    if interrupted is not None: raise interrupted
    return result, envelope, binding
