#!/usr/bin/env python3
"""Execute the fixed engineering gates into a new immutable run, then select it."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import uuid
import engineering_receipts as E

ROOT = Path(__file__).resolve().parents[1]


def execute_gate(argv, root, env, log):
    return subprocess.run([sys.executable, *argv[1:]], executable=sys.executable, cwd=root, env=env,
                          stdout=log, stderr=subprocess.STDOUT)


def record(root=ROOT):
    root = Path(root)
    predecessor = E.P.verify(root)
    inventory = E.V4.source_inventory(root)
    E.archive_current(root, inventory)
    run = E.DIRECTORY + "/runs/" + E.source_id(inventory) + "/" + uuid.uuid4().hex[:16]
    output = root / run
    output.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    env["PYTHONPATH"] = str(root / "src")
    env.pop("PYTEST_ADDOPTS", None)
    executions = []
    started = datetime.now(timezone.utc).isoformat()
    for label, spec in E.gates(root, run).items():
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        start = time.perf_counter()
        with (root / spec["log_path"]).open("xb") as log:
            proc = execute_gate(spec["argv"], root, env, log)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        executions.append({"label": label, "argv": spec["argv"], "artifact_path": spec["artifact_path"],
            "log_path": spec["log_path"], "exit_code": proc.returncode, "actual_executable": sys.executable,
            "wall_seconds": time.perf_counter() - start,
            "child_cpu_user_seconds": after.ru_utime - before.ru_utime,
            "child_cpu_system_seconds": after.ru_stime - before.ru_stime})
        print(f"{label}: exit {proc.returncode}, log {spec['log_path']}", flush=True)
        reason = "nonzero gate exit" if proc.returncode else None
        if reason is None:
            try: E._junit(root, spec)
            except (E.V4.ReceiptError, OSError, ValueError) as exc: reason = str(exc)
        if reason is not None:
            failure = {"status": "ENGINEERING_VALIDATION_FAILED", "reason": reason,
                       "executions": executions, "source_inventory_before": inventory,
                       "started_at": started, "current_selection_updated": False,
                       "scientific_promotion": "NOT_ESTABLISHED"}
            with (output / "FAILED.json").open("xb") as f: f.write(E.P.encoded(failure))
            return 1
    if inventory != E.V4.source_inventory(root):
        with (output / "SOURCE_DRIFT.json").open("xb") as f:
            f.write(E.P.encoded({"status": "SOURCE_CHANGED_DURING_EXECUTION", "executions": executions,
                "source_inventory_before": inventory, "source_inventory_after": E.V4.source_inventory(root)}))
        print("Current source changed during execution; no receipt selected")
        return 1
    receipt = E.build_record(root, run, inventory, executions, predecessor)
    receipt["execution_environment"] = {"python": sys.version, "executable": sys.executable,
        "runtime_source": str(root / "src"), "started_at": started,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "unmeasured": ["energy", "environment installation and development costs"]}
    path = run + "/RECEIPT.json"
    with (root / path).open("xb") as f: f.write(E.P.encoded(receipt))
    result = E.select(root, path)
    print("Selected immutable engineering receipt:", result["receipt_path"])
    return 0


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    raise SystemExit(record())
