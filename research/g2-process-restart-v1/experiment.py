"""G2.4 OS-process restart: subprocess reloads persisted ledger and solves holdout.

PR #192 reconstructed OCMRuntime in-process. That is not a machine process
restart. This capsule spawns a separate Python OS process.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

from ocm.learning import methods as M  # noqa: E402
from ocm.runtime.ocm_runtime import OCMRuntime  # noqa: E402

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
SCHEMA = "ocm.g2.process-restart.result.v1"
BUDGET = M.SearchBudget(slots=1000, max_length=4)
TRAIN_PROGRAMS = (("inc", "square", "inc"), ("inc", "square", "double"))
ADMIT_PROGRAMS = (("inc", "square", "dec"), ("inc", "square", "square"))
FRESH_PROGRAMS = (("inc", "square", "inc", "inc"), ("inc", "square", "double", "dec"))
EXPECTED_FRAGMENT = ("inc", "square")


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def pin_methods() -> str:
    blob = git_blob_sha1(SRC / "ocm" / "learning" / "methods.py")
    if blob != METHOD_BLOB:
        raise RuntimeError(f"methods.py blob {blob} != pinned {METHOD_BLOB}")
    return blob


def task_from_program(name: str, program: tuple[str, ...]) -> M.PolynomialTask:
    return M.PolynomialTask(name, M.normal_form(program))


def frozen_tasks() -> dict[str, tuple[M.PolynomialTask, ...]]:
    train = tuple(task_from_program(f"train-{i}", p) for i, p in enumerate(TRAIN_PROGRAMS))
    admit = tuple(task_from_program(f"admit-{i}", p) for i, p in enumerate(ADMIT_PROGRAMS))
    fresh = tuple(task_from_program(f"fresh-{i}", p) for i, p in enumerate(FRESH_PROGRAMS))
    ids = [t.fingerprint for t in train + admit + fresh]
    if len(ids) != len(set(ids)):
        raise RuntimeError("train/admit/fresh fingerprint overlap")
    return {"train": train, "admit": admit, "fresh": fresh}


def task_to_json(task: M.PolynomialTask) -> dict[str, Any]:
    return {"task_id": task.task_id, "coefficients": [str(c) for c in task.coefficients]}


def task_from_json(payload: dict[str, Any]) -> M.PolynomialTask:
    return M.PolynomialTask(payload["task_id"], tuple(Fraction(c) for c in payload["coefficients"]))


def ordinary_persist(path: Path, method: M.GeneratorMethod) -> None:
    payload = {
        "fragments": [list(p) for p in method.fragments],
        "training_tasks": list(method.training_tasks),
        "fingerprint": method.fingerprint,
    }
    temp = path.with_suffix(".tmp")
    with temp.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def ordinary_load(path: Path) -> M.GeneratorMethod:
    payload = json.loads(path.read_text(encoding="utf-8"))
    method = M.GeneratorMethod(
        tuple(tuple(p) for p in payload["fragments"]),
        tuple(payload["training_tasks"]),
    )
    if method.fingerprint != payload["fingerprint"]:
        raise RuntimeError("ordinary library fingerprint mismatch")
    return method


class StreamTrace:
    def __init__(self) -> None:
        self.events: list[tuple[str, tuple[str, ...]]] = []

    def solve(self, task: M.PolynomialTask, method: M.GeneratorMethod) -> tuple[M.SearchResult, str | None]:
        orig_primitive = M._primitive_programs
        orig_guided = M._guided_programs

        def primitive(max_length):
            for program in orig_primitive(max_length):
                self.events.append(("primitive", tuple(program)))
                yield program

        def guided(given_method, max_length):
            for program in orig_guided(given_method, max_length):
                self.events.append(("guided", tuple(program)))
                yield program

        M._primitive_programs = primitive
        M._guided_programs = guided
        try:
            result = M.solve(task, BUDGET, method)
        finally:
            M._primitive_programs = orig_primitive
            M._guided_programs = orig_guided
        origin = None
        if result.program is not None:
            target = tuple(result.program)
            for source, program in self.events:
                if program == target:
                    origin = source
                    break
        return result, origin


def solve_row(task: M.PolynomialTask, method: M.GeneratorMethod) -> dict[str, Any]:
    result, origin = StreamTrace().solve(task, method)
    program = tuple(result.program) if result.program is not None else ()
    fragment_used = any(
        program[i:i + len(EXPECTED_FRAGMENT)] == EXPECTED_FRAGMENT
        for i in range(0, max(0, len(program) - len(EXPECTED_FRAGMENT) + 1))
    )
    return {
        "task": task.fingerprint,
        "task_id": task.task_id,
        "status": result.status,
        "verified": M.verify_solution(task, result),
        "slots": result.slots,
        "program": list(program),
        "origin": origin,
        "fragment_used": fragment_used,
        "method_fingerprint": method.fingerprint,
    }


def persist_live_and_revoked(
    root: Path,
    training: tuple[tuple[M.PolynomialTask, M.SearchResult], ...],
    admit: tuple[M.PolynomialTask, ...],
) -> dict[str, Any]:
    live_root = root / "ocm-live"
    revoked_root = root / "ocm-revoked"
    empty_root = root / "ocm-empty"
    live_root.mkdir()
    revoked_root.mkdir()
    empty_root.mkdir()

    live = OCMRuntime(live_root)
    receipt = M.admit_generator(live, training, admit, BUDGET)
    live.persist()
    method = M.load_generator(live, receipt["generator_id"])
    ordinary_persist(live_root / "library.json", method)

    revoked = OCMRuntime(revoked_root)
    revoked_receipt = M.admit_generator(revoked, training, admit, BUDGET)
    revoked.revoke((revoked_receipt["training"][0]["evidence_id"],))
    revoked.persist()

    OCMRuntime(empty_root)
    return {
        "receipt": receipt,
        "method": method,
        "live_root": live_root,
        "revoked_root": revoked_root,
        "empty_root": empty_root,
        "kso_state_hash": live.state.kso_state_hash,
    }


def in_process_reconstruction(root: Path, generator_id: str) -> dict[str, Any]:
    """PR #192 mechanism: new OCMRuntime in the same interpreter. Not G2.4/002."""
    replay = OCMRuntime(root)
    method = M.load_generator(replay, generator_id)
    return {
        "pid": os.getpid(),
        "mechanism": "IN_PROCESS_OCMRUNTIME_RECONSTRUCTION",
        "sufficient_for_g24_002": False,
        "generator_id": generator_id,
        "method_fingerprint": method.fingerprint,
        "kso_state_hash": replay.state.kso_state_hash,
        "fragments": [list(p) for p in method.fragments],
    }


def spawn_restart_consumer(
    root: Path,
    generator_id: str,
    tasks: tuple[M.PolynomialTask, ...],
    out_path: Path,
) -> dict[str, Any]:
    tasks_path = out_path.with_name(out_path.stem + "-tasks.json")
    tasks_path.write_text(
        json.dumps([task_to_json(t) for t in tasks], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable, "-B", str(HERE / "experiment.py"),
            "--restart-consumer",
            "--root", str(root),
            "--generator-id", generator_id,
            "--tasks", str(tasks_path),
            "--out", str(out_path),
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO),
        check=False,
    )
    if proc.returncode != 0 or not out_path.is_file():
        raise RuntimeError(
            f"restart consumer failed rc={proc.returncode}: {proc.stderr[-2000:]} {proc.stdout[-2000:]}"
        )
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    payload["returncode"] = proc.returncode
    payload["parent_pid"] = os.getpid()
    payload["stdout"] = proc.stdout.strip()
    return payload


def run_restart_consumer(root: Path, generator_id: str, tasks_path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "pid": os.getpid(),
        "ppid": os.getppid(),
        "interpreter": sys.executable,
        "root": str(root),
        "generator_id": generator_id,
        "load_status": "MISSING_OR_DEAD",
        "kso_state_hash": None,
        "method_fingerprint": None,
        "fragments": [],
        "ordinary_library_matches": False,
        "rows": [],
    }
    try:
        runtime = OCMRuntime(root)
        method = M.load_generator(runtime, generator_id)
    except ValueError as exc:
        payload["error"] = str(exc)
        payload["kso_state_hash"] = None if "runtime" not in locals() else runtime.state.kso_state_hash
        return payload
    library_path = root / "library.json"
    if library_path.is_file():
        ordinary = ordinary_load(library_path)
        payload["ordinary_library_matches"] = ordinary.fingerprint == method.fingerprint
    tasks = tuple(task_from_json(row) for row in json.loads(tasks_path.read_text(encoding="utf-8")))
    payload.update({
        "load_status": "LIVE",
        "kso_state_hash": runtime.state.kso_state_hash,
        "method_fingerprint": method.fingerprint,
        "fragments": [list(p) for p in method.fragments],
        "rows": [solve_row(task, method) for task in tasks],
    })
    return payload


def decide_terminal(payload: dict[str, Any]) -> tuple[str, dict[str, bool]]:
    child = payload["os_process"]
    reconstruction = payload["in_process_reconstruction"]
    revoked = payload["revoked_os_process"]
    empty = payload["empty_os_process"]
    primitive = payload["primitive_fresh"]
    rows = child.get("rows") or []
    invoked = all(row.get("origin") == "guided" and row.get("fragment_used") for row in rows)
    verified = bool(rows) and all(row.get("verified") for row in rows)
    cheaper = bool(rows) and all(
        row["slots"] < prim["slots"] for row, prim in zip(rows, primitive)
    )
    pid_ok = (
        child["pid"] != payload["process"]["pid"]
        and child["ppid"] == payload["process"]["pid"]
        and child["pid"] != reconstruction["pid"]
        and reconstruction["pid"] == payload["process"]["pid"]
    )
    criteria = {
        "methods_blob_pinned": payload["methods_blob"] == METHOD_BLOB,
        "admitted_before_fresh_task": True,
        "fresh_disjoint_from_acquisition": payload["partition"]["fresh_disjoint"],
        "os_child_pid_differs": pid_ok,
        "child_reloaded_live_generator": child.get("load_status") == "LIVE",
        "child_kso_matches_parent": child.get("kso_state_hash") == payload["parent_kso_state_hash"],
        "held_out_verified": verified,
        "learned_object_invoked": invoked,
        "material_slot_saving": cheaper,
        "in_process_reconstruction_same_pid": reconstruction["pid"] == payload["process"]["pid"],
        "in_process_reconstruction_not_the_witness": not reconstruction["sufficient_for_g24_002"],
        "revoked_child_cannot_load": revoked.get("load_status") == "MISSING_OR_DEAD",
        "empty_child_cannot_load": empty.get("load_status") == "MISSING_OR_DEAD",
        "answer_cache_excluded": payload["answer_cache_excluded"],
        "ordinary_library_matches_ledger": child.get("ordinary_library_matches") is True,
    }
    if all(criteria.values()):
        return "OS_PROCESS_RESTART_HELD_OUT_SOLVE_SUPPORTED", criteria
    if reconstruction["pid"] == payload["process"]["pid"] and child.get("pid") == payload["process"]["pid"]:
        return "IN_PROCESS_RECONSTRUCTION_ONLY", criteria
    if not pid_ok or child.get("load_status") != "LIVE":
        return "NO_OS_PROCESS_RESTART", criteria
    return "HELD_OUT_SOLVE_FAILED", criteria


def run() -> dict[str, Any]:
    blob = pin_methods()
    parent_pid = os.getpid()
    tasks = frozen_tasks()
    training = tuple((task, M.solve(task, BUDGET)) for task in tasks["train"])
    for task, result in training:
        if not M.verify_solution(task, result):
            raise RuntimeError(f"training solve failed: {task.task_id}")
    with tempfile.TemporaryDirectory(prefix="ocm-g2-process-restart-") as temp:
        roots = persist_live_and_revoked(Path(temp), training, tasks["admit"])
        reconstruction = in_process_reconstruction(roots["live_root"], roots["receipt"]["generator_id"])
        out_dir = Path(temp) / "child-out"
        out_dir.mkdir()
        live_child = spawn_restart_consumer(
            roots["live_root"],
            roots["receipt"]["generator_id"],
            tasks["fresh"],
            out_dir / "live.json",
        )
        revoked_child = spawn_restart_consumer(
            roots["revoked_root"],
            roots["receipt"]["generator_id"],
            tasks["fresh"],
            out_dir / "revoked.json",
        )
        empty_child = spawn_restart_consumer(
            roots["empty_root"],
            roots["receipt"]["generator_id"],
            tasks["fresh"],
            out_dir / "empty.json",
        )
        primitive_fresh = [solve_row(task, M.GeneratorMethod()) for task in tasks["fresh"]]
        payload = {
            "schema": SCHEMA,
            "methods_blob": blob,
            "claim_ceiling": (
                "G2.4/002 machine process restarts at this small polynomial microscope. "
                "Not CAUSAL_METHOD_REUSE_SUPPORTED. Not a close of the remaining G2.4 boxes."
            ),
            "process": {"pid": parent_pid, "interpreter": sys.executable},
            "parent_kso_state_hash": roots["kso_state_hash"],
            "generator_id": roots["receipt"]["generator_id"],
            "learned_fragments": [list(p) for p in roots["method"].fragments],
            "partition": {
                "train_n": len(tasks["train"]),
                "admit_n": len(tasks["admit"]),
                "fresh_n": len(tasks["fresh"]),
                "train_ids": [t.fingerprint for t in tasks["train"]],
                "admit_ids": [t.fingerprint for t in tasks["admit"]],
                "fresh_ids": [t.fingerprint for t in tasks["fresh"]],
                "train_programs": [list(p) for p in TRAIN_PROGRAMS],
                "admit_programs": [list(p) for p in ADMIT_PROGRAMS],
                "fresh_programs": [list(p) for p in FRESH_PROGRAMS],
                "fresh_disjoint": True,
            },
            "answer_cache_excluded": all(
                t.fingerprint not in roots["method"].training_tasks for t in tasks["fresh"]
            ),
            "in_process_reconstruction": reconstruction,
            "os_process": live_child,
            "revoked_os_process": revoked_child,
            "empty_os_process": empty_child,
            "primitive_fresh": primitive_fresh,
            "pr192_defect": (
                "research/g2-macro-operator-v1/experiment.py admit_macro constructs "
                "OCMRuntime(root) in the same process after persist; that is reconstruction."
            ),
        }
        terminal, criteria = decide_terminal(payload)
        payload["terminal"] = terminal
        payload["criteria"] = criteria
        payload["g24_002_machine_process_restarts"] = {
            "earned": terminal == "OS_PROCESS_RESTART_HELD_OUT_SOLVE_SUPPORTED",
            "box": "G2.4/002-machine_process_restarts",
            "witness": "subprocess Python OS process reloaded persisted OCM ledger and solved held-out tasks",
            "rejected_witness": "in-process OCMRuntime reconstruction (PR #192)",
        }
        payload["g24_complete"] = False
        return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "RESULT.json")
    parser.add_argument("--restart-consumer", action="store_true")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--generator-id", dest="generator_id")
    parser.add_argument("--tasks", type=Path)
    args = parser.parse_args()
    if args.restart_consumer:
        if args.root is None or args.generator_id is None or args.tasks is None:
            raise SystemExit("--root, --generator-id and --tasks are required for --restart-consumer")
        pin_methods()
        result = run_restart_consumer(args.root, args.generator_id, args.tasks)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({
            "pid": result["pid"],
            "ppid": result["ppid"],
            "load_status": result["load_status"],
        }, sort_keys=True))
        return
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "terminal": result["terminal"],
        "g24_002_earned": result["g24_002_machine_process_restarts"]["earned"],
        "parent_pid": result["process"]["pid"],
        "child_pid": result["os_process"]["pid"],
        "reconstruction_pid": result["in_process_reconstruction"]["pid"],
        "load_status": result["os_process"]["load_status"],
        "fragments": result["learned_fragments"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
