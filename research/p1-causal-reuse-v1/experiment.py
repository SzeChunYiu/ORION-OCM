"""P1 tiny causal reuse: G2 macro serving + OS-process restart.

Issue #165 remaining P1 boxes:

    admit scoped learned method; restart; fresh task; actual use witness;
    measurable benefit; method-removal ablation; strongest persistent parent.

Serving is the existing G2 MACRO-token grammar in
``research/g2-macro-operator-v1``. Restart is a separate Python OS process
(``subprocess.run``). ``research/g2-process-restart-v1`` is not on this base, so
the spawn is implemented here. In-process ``OCMRuntime`` reconstruction is
recorded and is not the restart witness.

Pinned production source: ``src/ocm/learning/methods.py`` blob
``50323a33418b8ef8bb6500ddeba4b9d1f795e9e3``. No ``src/`` edits.

Claim ceiling: these P1 boxes at this small exact polynomial microscope. Not
G2.4-complete. Not an unscoped CAUSAL_METHOD_REUSE_SUPPORTED close. Not an OCM
architecture residual versus ordinary persistent library search.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
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
MACRO_PATH = REPO / "research" / "g2-macro-operator-v1" / "experiment.py"
sys.path.insert(0, str(SRC))

from ocm.kso.ids import content_hash  # noqa: E402
from ocm.kso.warrant import Liveness  # noqa: E402
from ocm.learning import methods as M  # noqa: E402
from ocm.runtime.ocm_runtime import OCMRuntime  # noqa: E402

SPEC = importlib.util.spec_from_file_location("g2_macro_operator", MACRO_PATH)
G2 = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(G2)

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
SCHEMA = "ocm.p1.causal-reuse.result.v1"
MAX_LEN = 4
BUDGET = M.SearchBudget(slots=1000, max_length=MAX_LEN)
TRAIN_PROGRAMS = (("inc", "square", "inc"), ("inc", "square", "double"))
ADMIT_PROGRAMS = (("inc", "square", "dec"), ("inc", "square", "square"))
FRESH_PROGRAMS = (("inc", "square", "inc", "inc"), ("inc", "square", "double", "dec"))
SCOPE_NAME = "polynomial-macro-operator.v1"

P1_BOXES = (
    "P1/005-admit_scoped_learned_method",
    "P1/006-restart",
    "P1/007-fresh_task",
    "P1/008-actual_use_witness",
    "P1/009-measurable_benefit",
    "P1/010-method_removal_ablation",
    "P1/011-strongest_persistent_parent",
)


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def pin_methods() -> str:
    blob = git_blob_sha1(SRC / "ocm" / "learning" / "methods.py")
    if blob != METHOD_BLOB:
        raise RuntimeError(f"methods.py blob {blob} != pinned {METHOD_BLOB}")
    if G2.METHOD_BLOB != METHOD_BLOB:
        raise RuntimeError("G2 macro capsule pins a different methods.py blob")
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


def jsonable_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "task": row["task"],
        "enumeration_attempts": row["enumeration_attempts"],
        "unique_candidates_checked": row["unique_candidates_checked"],
        "token_word": list(row["token_word"]),
        "program": list(row["program"]),
        "macro_used": bool(row["macro_used"]),
        "verified": bool(row["verified"]),
    }


def evaluate_macro(tasks: tuple[M.PolynomialTask, ...], macro: tuple[str, ...] | None) -> tuple[list[dict[str, Any]], int]:
    index = G2.build_search_index(macro, MAX_LEN)
    rows, attempts, _checks = G2.evaluate_index(tasks, index)
    return [jsonable_row(row) for row in rows], attempts


def select_macro(training_rows: tuple[tuple[M.PolynomialTask, M.SearchResult], ...],
                 admit_tasks: tuple[M.PolynomialTask, ...]) -> dict[str, Any]:
    candidates, support = G2.candidate_pool(training_rows)
    primitive_rows, primitive_attempts = evaluate_macro(admit_tasks, None)
    evaluations = []
    for candidate in candidates:
        rows, attempts = evaluate_macro(admit_tasks, candidate)
        evaluations.append({
            "fragment": list(candidate),
            "support": support[candidate],
            "aggregate_enumeration_attempts": attempts,
            "baseline_aggregate_enumeration_attempts": primitive_attempts,
            "saving": primitive_attempts - attempts,
            "macro_used_tasks": sum(1 for row in rows if row["macro_used"]),
            "rows": rows,
        })
    if not evaluations:
        return {
            "accepted": False,
            "selected": None,
            "candidates": [],
            "primitive_attempts": primitive_attempts,
            "primitive_rows": primitive_rows,
        }
    selected = min(
        enumerate(evaluations),
        key=lambda item: (item[1]["aggregate_enumeration_attempts"], item[0]),
    )[1]
    accepted = selected["aggregate_enumeration_attempts"] < primitive_attempts
    return {
        "accepted": accepted,
        "selected": selected if accepted else None,
        "candidates": [{"fragment": e["fragment"], "support": e["support"],
                        "aggregate_enumeration_attempts": e["aggregate_enumeration_attempts"]}
                       for e in evaluations],
        "primitive_attempts": primitive_attempts,
        "primitive_rows": primitive_rows,
    }


def load_live_macro(runtime: OCMRuntime, atom_id: str) -> tuple[str, ...]:
    atom = runtime.state.ks.atom_map().get(atom_id)
    if atom is None or atom.liveness(runtime.state.revoked) is not Liveness.LIVE:
        raise ValueError("macro is missing or its support is not live")
    stored = dict(atom.meta)
    if atom.atom_type != "procedure" or stored.get("kind") != "macro.operator.v1":
        raise ValueError("macro data identity mismatch")
    if atom.content_ref != content_hash(stored):
        raise RuntimeError("macro content identity mismatch")
    loaded = tuple(stored["macro"])
    if content_hash({"macro": loaded}) != stored["fingerprint"]:
        raise RuntimeError("macro fingerprint mismatch")
    contexts = getattr(atom.scope, "contexts", None)
    if not contexts or SCOPE_NAME not in contexts:
        raise RuntimeError(f"macro scope {atom.scope!r} is not {SCOPE_NAME}")
    return loaded


def persist_ledgers(
    root: Path,
    macro: tuple[str, ...],
    training_receipt: dict[str, Any],
    utility_receipt: dict[str, Any],
) -> dict[str, Any]:
    live_root = root / "ocm-live"
    revoked_root = root / "ocm-revoked"
    empty_root = root / "ocm-empty"
    live_root.mkdir()
    revoked_root.mkdir()
    empty_root.mkdir()

    loaded, atom_id, training_evidence, utility_evidence = G2.admit_macro(
        live_root, macro, training_receipt, utility_receipt, revoke=False
    )
    if tuple(loaded) != macro:
        raise RuntimeError("admitted macro drifted")
    G2.ordinary_persist(live_root / "library.json", macro)

    _dead, revoked_atom_id, _rte, _rue = G2.admit_macro(
        revoked_root, macro, training_receipt, utility_receipt, revoke=True
    )
    if revoked_atom_id != atom_id:
        raise RuntimeError("revoked atom id drifted from live admission")

    empty = OCMRuntime(empty_root)
    empty.persist()
    return {
        "atom_id": atom_id,
        "training_evidence": training_evidence,
        "utility_evidence": utility_evidence,
        "live_root": live_root,
        "revoked_root": revoked_root,
        "empty_root": empty_root,
        "kso_state_hash": OCMRuntime(live_root).state.kso_state_hash,
        "scope": SCOPE_NAME,
    }


def in_process_reconstruction(root: Path, atom_id: str) -> dict[str, Any]:
    """G2.admit_macro / PR #192 mechanism. Same interpreter. Not P1/006."""
    replay = OCMRuntime(root)
    try:
        macro = load_live_macro(replay, atom_id)
        status = "LIVE"
        error = None
    except ValueError as exc:
        macro = ()
        status = "MISSING_OR_DEAD"
        error = str(exc)
    return {
        "pid": os.getpid(),
        "mechanism": "IN_PROCESS_OCMRUNTIME_RECONSTRUCTION",
        "sufficient_for_p1_restart": False,
        "atom_id": atom_id,
        "load_status": status,
        "macro": list(macro),
        "kso_state_hash": replay.state.kso_state_hash,
        "error": error,
    }


def spawn_restart_consumer(
    root: Path,
    atom_id: str,
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
            "--atom-id", atom_id,
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


def run_restart_consumer(root: Path, atom_id: str, tasks_path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "pid": os.getpid(),
        "ppid": os.getppid(),
        "interpreter": sys.executable,
        "root": str(root),
        "atom_id": atom_id,
        "load_status": "MISSING_OR_DEAD",
        "kso_state_hash": None,
        "macro": [],
        "ordinary_library_matches": False,
        "rows": [],
        "fallback": None,
    }
    tasks = tuple(task_from_json(row) for row in json.loads(tasks_path.read_text(encoding="utf-8")))
    runtime = OCMRuntime(root)
    payload["kso_state_hash"] = runtime.state.kso_state_hash
    try:
        macro = load_live_macro(runtime, atom_id)
    except ValueError as exc:
        payload["error"] = str(exc)
        rows, attempts = evaluate_macro(tasks, None)
        payload["fallback"] = "primitive"
        payload["rows"] = rows
        payload["aggregate_enumeration_attempts"] = attempts
        return payload
    library_path = root / "library.json"
    if library_path.is_file():
        ordinary = G2.ordinary_load(library_path)
        payload["ordinary_library_matches"] = ordinary == macro
    rows, attempts = evaluate_macro(tasks, macro)
    payload.update({
        "load_status": "LIVE",
        "macro": list(macro),
        "rows": rows,
        "aggregate_enumeration_attempts": attempts,
        "fallback": None,
    })
    return payload


def rows_match(a_rows: list[dict[str, Any]], b_rows: list[dict[str, Any]]) -> bool:
    if len(a_rows) != len(b_rows):
        return False
    return all(
        a["task"] == b["task"]
        and a["enumeration_attempts"] == b["enumeration_attempts"]
        and a["unique_candidates_checked"] == b["unique_candidates_checked"]
        and list(a["program"]) == list(b["program"])
        and list(a["token_word"]) == list(b["token_word"])
        and bool(a["macro_used"]) == bool(b["macro_used"])
        for a, b in zip(a_rows, b_rows)
    )


def decide(payload: dict[str, Any]) -> tuple[str, dict[str, bool], dict[str, Any]]:
    child = payload["os_process"]
    reconstruction = payload["in_process_reconstruction"]
    revoked = payload["revoked_os_process"]
    empty = payload["empty_os_process"]
    primitive = payload["primitive_fresh"]
    ordinary = payload["ordinary_fresh"]
    rows = child.get("rows") or []
    used = bool(rows) and all(row.get("macro_used") and row.get("verified") for row in rows)
    cheaper = bool(rows) and all(
        row["enumeration_attempts"] < prim["enumeration_attempts"]
        for row, prim in zip(rows, primitive)
    )
    pid_ok = (
        child["pid"] != payload["process"]["pid"]
        and child["ppid"] == payload["process"]["pid"]
        and child["pid"] != reconstruction["pid"]
        and reconstruction["pid"] == payload["process"]["pid"]
    )
    revoked_ablation = (
        revoked.get("load_status") == "MISSING_OR_DEAD"
        and revoked.get("fallback") == "primitive"
        and rows_match(revoked.get("rows") or [], primitive)
        and not any(row.get("macro_used") for row in (revoked.get("rows") or []))
    )
    empty_ablation = (
        empty.get("load_status") == "MISSING_OR_DEAD"
        and rows_match(empty.get("rows") or [], primitive)
    )
    parent_parity = (
        rows_match(rows, ordinary)
        and child.get("ordinary_library_matches") is True
        and all(row.get("macro_used") for row in ordinary)
    )
    criteria = {
        "methods_blob_pinned": payload["methods_blob"] == METHOD_BLOB,
        "admitted_scoped_macro": payload["admission"]["accepted"] and payload["admission"]["scope"] == SCOPE_NAME,
        "fresh_disjoint_from_acquisition": payload["partition"]["fresh_disjoint"],
        "os_child_pid_differs": pid_ok,
        "child_reloaded_live_macro": child.get("load_status") == "LIVE",
        "child_kso_matches_parent": child.get("kso_state_hash") == payload["parent_kso_state_hash"],
        "fresh_verified": bool(rows) and all(row.get("verified") for row in rows),
        "actual_macro_use": used,
        "measurable_enumeration_saving": cheaper,
        "in_process_reconstruction_same_pid": reconstruction["pid"] == payload["process"]["pid"],
        "in_process_reconstruction_not_the_witness": not reconstruction["sufficient_for_p1_restart"],
        "revoked_ablation_equals_primitive": revoked_ablation,
        "empty_ledger_cannot_serve_macro": empty_ablation,
        "ordinary_persistent_parent_parity": parent_parity,
        "answer_cache_excluded": payload["answer_cache_excluded"],
    }
    boxes = {
        "P1/005-admit_scoped_learned_method": {
            "earned": bool(criteria["admitted_scoped_macro"] and criteria["methods_blob_pinned"]),
            "witness": "G2.admit_macro wrote a scoped procedure atom polynomial-macro-operator.v1",
        },
        "P1/006-restart": {
            "earned": bool(criteria["os_child_pid_differs"] and criteria["child_reloaded_live_macro"]),
            "witness": "subprocess Python OS process reloaded the persisted OCM ledger",
            "rejected_witness": "in-process OCMRuntime reconstruction (G2.admit_macro / PR #192)",
        },
        "P1/007-fresh_task": {
            "earned": bool(criteria["fresh_disjoint_from_acquisition"] and criteria["answer_cache_excluded"] and criteria["fresh_verified"]),
            "witness": "fresh fingerprints disjoint from train and admission holdout",
        },
        "P1/008-actual_use_witness": {
            "earned": bool(criteria["actual_macro_use"]),
            "witness": "every fresh solve has macro_used=true after OS reload",
        },
        "P1/009-measurable_benefit": {
            "earned": bool(criteria["measurable_enumeration_saving"]),
            "witness": "fresh enumeration_attempts strictly below the primitive parent",
        },
        "P1/010-method_removal_ablation": {
            "earned": bool(criteria["revoked_ablation_equals_primitive"] and criteria["empty_ledger_cannot_serve_macro"]),
            "witness": "revoking training evidence makes the child fall back to primitive search",
        },
        "P1/011-strongest_persistent_parent": {
            "earned": bool(criteria["ordinary_persistent_parent_parity"]),
            "witness": "ordinary atomic JSON library persist matches OCM live task-by-task",
            "residual_vs_ordinary": "none",
        },
    }
    if all(criteria.values()) and all(box["earned"] for box in boxes.values()):
        return "P1_CAUSAL_REUSE_SUPPORTED_AT_POLYNOMIAL_MICROSCOPE", criteria, boxes
    if not pid_ok or child.get("load_status") != "LIVE":
        return "NO_OS_PROCESS_RESTART", criteria, boxes
    if not used:
        return "NO_ACTUAL_MACRO_USE", criteria, boxes
    if not cheaper:
        return "NO_MEASURABLE_BENEFIT", criteria, boxes
    if not revoked_ablation:
        return "CANNOT_CHECK_METHOD_REMOVAL_ABLATION", criteria, boxes
    if not parent_parity:
        return "CANNOT_CHECK_ORDINARY_PARENT_PARITY", criteria, boxes
    return "P1_CAUSAL_REUSE_INCOMPLETE", criteria, boxes


def run() -> dict[str, Any]:
    blob = pin_methods()
    parent_pid = os.getpid()
    tasks = frozen_tasks()
    training = tuple((task, M.solve(task, BUDGET)) for task in tasks["train"])
    for task, result in training:
        if not M.verify_solution(task, result):
            raise RuntimeError(f"training solve failed: {task.task_id}")
    gate = select_macro(training, tasks["admit"])
    if not gate["accepted"]:
        return {
            "schema": SCHEMA,
            "methods_blob": blob,
            "terminal": "MACRO_TOURNAMENT_SELECTS_NO_METHOD",
            "criteria": {"admitted_scoped_macro": False},
            "p1_boxes": {box: {"earned": False} for box in P1_BOXES},
            "tournament": gate,
            "claim_ceiling": (
                "No scoped method was admitted. P1 remaining boxes are not earned."
            ),
        }
    macro = tuple(gate["selected"]["fragment"])
    training_receipt = {
        "schema": "p1.macro.training.v1",
        "source_blob": METHOD_BLOB,
        "training_ids": [task.fingerprint for task, _result in training],
        "training_programs": [list(result.program) for _task, result in training],
        "selected_macro": list(macro),
    }
    utility_receipt = {
        "schema": "p1.macro.utility.v1",
        "accepted": True,
        "baseline_attempts": gate["primitive_attempts"],
        "selected_attempts": gate["selected"]["aggregate_enumeration_attempts"],
        "admit_ids": [task.fingerprint for task in tasks["admit"]],
        "selected": {"fragment": list(macro), "support": gate["selected"]["support"]},
    }
    with tempfile.TemporaryDirectory(prefix="ocm-p1-causal-reuse-") as temp:
        roots = persist_ledgers(Path(temp), macro, training_receipt, utility_receipt)
        reconstruction = in_process_reconstruction(roots["live_root"], roots["atom_id"])
        out_dir = Path(temp) / "child-out"
        out_dir.mkdir()
        live_child = spawn_restart_consumer(
            roots["live_root"], roots["atom_id"], tasks["fresh"], out_dir / "live.json"
        )
        revoked_child = spawn_restart_consumer(
            roots["revoked_root"], roots["atom_id"], tasks["fresh"], out_dir / "revoked.json"
        )
        empty_child = spawn_restart_consumer(
            roots["empty_root"], roots["atom_id"], tasks["fresh"], out_dir / "empty.json"
        )
        primitive_fresh, primitive_total = evaluate_macro(tasks["fresh"], None)
        ordinary_macro = G2.ordinary_load(roots["live_root"] / "library.json")
        ordinary_fresh, ordinary_total = evaluate_macro(tasks["fresh"], ordinary_macro)
        payload = {
            "schema": SCHEMA,
            "methods_blob": blob,
            "claim_ceiling": (
                "P1 remaining boxes at this small polynomial microscope using G2 "
                "MACRO-token serving and an OS-process restart. Not G2.4-complete. "
                "Not CAUSAL_METHOD_REUSE_SUPPORTED. Ordinary persistent JSON is the "
                "executed strongest persistent parent; OCM live matches it."
            ),
            "process": {"pid": parent_pid, "interpreter": sys.executable},
            "parent_kso_state_hash": roots["kso_state_hash"],
            "atom_id": roots["atom_id"],
            "learned_macro": list(macro),
            "admission": {
                "accepted": True,
                "scope": SCOPE_NAME,
                "kind": "macro.operator.v1",
                "training_evidence": roots["training_evidence"],
                "utility_evidence": roots["utility_evidence"],
                "atom_id": roots["atom_id"],
                "mechanism": "G2.admit_macro",
            },
            "tournament": {
                "accepted": True,
                "candidates": gate["candidates"],
                "selected": gate["selected"],
                "primitive_admit_attempts": gate["primitive_attempts"],
            },
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
                "max_length": MAX_LEN,
            },
            "answer_cache_excluded": all(
                t.fingerprint not in {x.fingerprint for x in tasks["train"] + tasks["admit"]}
                for t in tasks["fresh"]
            ),
            "in_process_reconstruction": reconstruction,
            "os_process": live_child,
            "revoked_os_process": revoked_child,
            "empty_os_process": empty_child,
            "primitive_fresh": primitive_fresh,
            "ordinary_fresh": ordinary_fresh,
            "primitive_fresh_attempts": primitive_total,
            "ordinary_fresh_attempts": ordinary_total,
            "g2_macro_source": "research/g2-macro-operator-v1/experiment.py",
            "g24_complete": False,
        }
        terminal, criteria, boxes = decide(payload)
        payload["terminal"] = terminal
        payload["criteria"] = criteria
        payload["p1_boxes"] = boxes
        payload["p1_boxes_earned"] = [box for box, row in boxes.items() if row["earned"]]
        payload["p1_already_checked_on_issue"] = [
            "P1/001-use_exact_formal_procedural_task_families",
            "P1/002-identify_repeated_experience_structure",
            "P1/003-strong_abstraction_donors_first",
            "P1/004-eliminate_primitive_aliases",
        ]
        return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "RESULT.json")
    parser.add_argument("--restart-consumer", action="store_true")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--atom-id", dest="atom_id")
    parser.add_argument("--tasks", type=Path)
    args = parser.parse_args()
    if args.restart_consumer:
        if args.root is None or args.atom_id is None or args.tasks is None:
            raise SystemExit("--root, --atom-id and --tasks are required for --restart-consumer")
        pin_methods()
        result = run_restart_consumer(args.root, args.atom_id, args.tasks)
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
        "p1_boxes_earned": result.get("p1_boxes_earned"),
        "parent_pid": result.get("process", {}).get("pid"),
        "child_pid": (result.get("os_process") or {}).get("pid"),
        "reconstruction_pid": (result.get("in_process_reconstruction") or {}).get("pid"),
        "load_status": (result.get("os_process") or {}).get("load_status"),
        "macro": result.get("learned_macro"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
