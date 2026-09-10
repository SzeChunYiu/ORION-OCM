"""M1 six-arm native-acquisition lifecycle runner (machinery only; no scored run).

Implements the 8-step lifecycle of M1_NATIVE_ACQUISITION_PROTOCOL_FREEZE_V1.json by
BINDING the registered learner src/ocm/learning/methods.py AS-IS (import and drive;
never copy or modify). Phases compose as shards for the scored run on laptop billy:

  dev            solve developmental tasks (retain success AND failure traces),
                 mine candidates via the learner's registered operators, test each
                 candidate on ACQUIRING fresh validation targets (never replay),
                 admit through the learner's own admission path with a cost ledger.
  checkpoint     persist the actual runtime state to disk, seal the event log,
                 record pre-restart process identity.
  acquire --arm  MUST run in a FRESH OS process: it loads the persisted state,
                 rejects a same-process "restart" (pid evidence), acquires a
                 protected fresh target needing target-specific information, has
                 the acquired object checked by CHECKER_C as an INDEPENDENT unit
                 (fresh interpreter + methods.py digest), then evaluates the
                 acquired object on fresh obligations. Developmental state updates
                 only from permitted streams.
  restart-and-acquire --arm   spawns `acquire` in a fresh interpreter and waits.
  summarize      deterministic: verifies every seal (fail closed), aggregates
                 paired B(M,T,q) work counts, refusal rates, censoring, and maps
                 the terminal with the frozen precedence.

Arms (freeze lifecycle_runner/checkpoint_clones): RESET, LIBRARY_ONLY, CONTINUED,
CONTINUED_WITH_LEARNING_STATE_REMOVED, ORDINARY_ADAPTIVE_PARENT (outside OCM
bookkeeping), KNOWN_STRUCTURE_ORACLE (calibration only, never a headline comparator).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from ocm.learning import methods as M  # noqa: E402  registered learner, bound AS-IS
from ocm.runtime.ocm_runtime import OCMRuntime  # noqa: E402

ARMS = ("RESET", "LIBRARY_ONLY", "CONTINUED", "CONTINUED_WITH_LEARNING_STATE_REMOVED",
        "ORDINARY_ADAPTIVE_PARENT", "KNOWN_STRUCTURE_ORACLE")
CALIBRATION_ONLY_ARMS = ("KNOWN_STRUCTURE_ORACLE",)


class AssayDefect(Exception):
    """Raised when the assay itself is broken (e.g. fake same-process restart)."""


def run_files(run_dir: Path):
    return {"partitions": run_dir / "partitions.json", "ledger": run_dir / "ledger.json",
            "dev_state": run_dir / "dev_state.json", "checkpoint": run_dir / "checkpoint.json",
            "ordinary": run_dir / "ordinary_store.json", "ocm_root": run_dir / "ocm",
            "arms": run_dir / "arms", "seals": run_dir / "seals", "summary": run_dir / "summary.json"}


def load_json(path: Path, default=None):
    if not path.exists():
        if default is not None:
            return default
        raise SystemExit(f"MISSING_INPUT: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def events_append(run_dir: Path, phase: str, kind: str, payload: dict) -> None:
    with (run_dir / f"events_{phase}.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"phase": phase, "kind": kind,
                                 "wall_ns": time.monotonic_ns(), "payload": payload},
                                sort_keys=True) + "\n")


def seal_phase(run_dir: Path, phase: str) -> dict:
    """Seal a phase event log with sha256 + line count; summarize fails closed on mismatch."""
    log = run_dir / f"events_{phase}.jsonl"
    data = log.read_bytes() if log.exists() else b""
    seal = {"file": log.name, "sha256": hashlib.sha256(data).hexdigest(),
            "lines": data.count(b"\n"), "sealed_by_phase": phase}
    write_json(run_dir / "seals" / f"{phase}.json", seal)
    return seal


def verify_seals(run_dir: Path) -> dict:
    seals_dir = run_dir / "seals"
    if not seals_dir.is_dir():
        raise SystemExit("SEAL_VERIFICATION_FAILED: no seals directory")
    checked = {}
    for seal_file in sorted(seals_dir.glob("*.json")):
        seal = json.loads(seal_file.read_text(encoding="utf-8"))
        log = run_dir / seal["file"]
        data = log.read_bytes() if log.exists() else b""
        ok = (hashlib.sha256(data).hexdigest() == seal["sha256"] and data.count(b"\n") == seal["lines"])
        if not ok:
            raise SystemExit(f"SEAL_VERIFICATION_FAILED: {seal['file']} tampered (fail closed)")
        checked[seal["file"]] = seal["sha256"]
    return checked


def ledger_update(run_dir: Path, **fields) -> dict:
    paths = run_files(run_dir)
    ledger = load_json(paths["ledger"], default={"wall_seconds": {}, "interpreter_restarts": 0,
                                                 "candidate_enumerations": 0, "verification_calls": 0})
    for key, value in fields.items():
        if key == "phase_wall_seconds":
            continue
        if key == "phase":
            ledger["wall_seconds"][value] = ledger["wall_seconds"].get(value, 0.0) + fields["phase_wall_seconds"]
        else:
            ledger[key] = ledger.get(key, 0) + value
    write_json(paths["ledger"], ledger)
    return ledger


def tasks_of(stream_rows):
    return [M.PolynomialTask(row["task_id"], row["coefficients"]) for row in stream_rows]


def budget_of(partitions: dict, slots: int) -> M.SearchBudget:
    return M.SearchBudget(slots=slots, max_length=partitions["grammar"]["max_program_length"])


# --------------------------------------------------------------------------- phase: dev (steps 1-4)

def phase_dev(run_dir: Path, slots: int) -> None:
    started = time.perf_counter()
    paths = run_files(run_dir)
    partitions = load_json(paths["partitions"])
    protected = {row["normal_form_digest"] for row in partitions["streams"]["protected"]}
    dev_digests = {row["normal_form_digest"] for stream in ("train", "validation")
                   for row in partitions["streams"][stream]}
    leakage = protected & dev_digests
    if leakage:
        events_append(run_dir, "dev", "LEAKAGE_ALARM", {"shared": sorted(leakage)})
        write_json(paths["dev_state"], {"terminal": "LEAKAGE_ALARM", "shared": sorted(leakage)})
        raise SystemExit(f"LEAKAGE_ALARM: developmental stream contains {len(leakage)} protected normal forms")
    budget = budget_of(partitions, slots)
    traces, verified, verification_calls, enumerations = [], [], 0, 0
    for task in tasks_of(partitions["streams"]["train"]):
        result = M.solve(task, budget)
        verification_calls += 1
        ok = M.verify_solution(task, result)
        enumerations += result.candidates_checked
        if ok:
            verified.append((task, result))
        traces.append({"task": task.fingerprint, "status": result.status,
                       "program": list(result.program) if result.program else None, "slots": result.slots,
                       "candidates_checked": result.candidates_checked,
                       "outcome": "SUCCESS" if ok else "FAILURE",
                       "typed_failure_reason": None if ok else f"SOLVER_{result.status}"})
    state = {"schema": "OCM_M1_DEV_STATE", "traces": traces, "terminal": None,
             "candidates": None, "admission": None, "refusal_reason": None, "generator_id": None}
    if len(verified) < 2:
        state["terminal"] = "INSUFFICIENT_HISTORY"
        state["typed_reason"] = f"only {len(verified)} verified developmental tasks (learner needs >= 2)"
        write_json(paths["dev_state"], state)
        events_append(run_dir, "dev", "INSUFFICIENT_HISTORY", {"verified": len(verified)})
        raise SystemExit("INSUFFICIENT_HISTORY: developmental phase cannot mine candidates")
    method = M.learn_generator(verified)  # registered operator: fragment mining, support>=2, top 16
    state["candidates"] = {"fragments": [list(f) for f in method.fragments],
                           "fingerprint": method.fingerprint, "candidates_emitted": len(method.fragments)}
    events_append(run_dir, "dev", "CANDIDATES_EMITTED",
                  {"count": len(method.fragments), "fingerprint": method.fingerprint})
    validation = tasks_of(partitions["streams"]["validation"])
    acquisition_rows = []
    for task in validation:  # candidates tested on ACQUIRING fresh targets, never on replay
        row = M.solve(task, budget, method)
        baseline = M.solve(task, budget)
        verification_calls += 1
        enumerations += row.candidates_checked + baseline.candidates_checked
        acquisition_rows.append({"task": task.fingerprint, "status": row.status,
                                 "slots": row.slots, "candidates_checked": row.candidates_checked,
                                 "baseline_slots": baseline.slots,
                                 "acquired": M.verify_solution(task, row)})
    state["validation_acquisition"] = acquisition_rows
    runtime = OCMRuntime(paths["ocm_root"])
    for task, result in verified:  # library of solved objects via the registered admission path
        M.admit_solution(runtime, task, result)
    try:
        admission = M.admit_generator(runtime, verified, validation, budget)
        state["admission"] = {"generator_id": admission["generator_id"],
                              "validation_evidence": admission["validation_evidence"],
                              "accepted": True}
        state["generator_id"] = admission["generator_id"]
        events_append(run_dir, "dev", "ADMITTED", {"generator_id": admission["generator_id"]})
    except ValueError as exc:  # the learner's own registered refusal (no-slowdown rule)
        state["refusal_reason"] = f"REFUSED_TO_DEPLOY_LEARNED_METHOD: {exc}"
        events_append(run_dir, "dev", "REFUSED_TO_DEPLOY_LEARNED_METHOD", {"detail": str(exc)})
    runtime.persist()
    write_json(paths["ordinary"], {"kind": "ordinary-adaptive-parent.v1",  # outside OCM bookkeeping
                                   "fragments": [list(f) for f in method.fragments],
                                   "fingerprint": method.fingerprint,
                                   "training_tasks": sorted(t.fingerprint for t, _ in verified)})
    state["terminal"] = "DEV_COMPLETE"
    write_json(paths["dev_state"], state)
    ledger_update(run_dir, phase="dev", phase_wall_seconds=time.perf_counter() - started,
                  interpreter_restarts=0, candidate_enumerations=enumerations,
                  verification_calls=verification_calls)


# --------------------------------------------------------------------------- phase: checkpoint (step 5)

def phase_checkpoint(run_dir: Path) -> dict:
    started = time.perf_counter()
    paths = run_files(run_dir)
    dev_state = load_json(paths["dev_state"])
    if dev_state.get("terminal") == "LEAKAGE_ALARM":
        raise SystemExit("CHECKPOINT_REFUSED: dev phase ended in LEAKAGE_ALARM")
    runtime = OCMRuntime(paths["ocm_root"])  # replays persisted ledger (state loads from disk)
    runtime.persist()
    seal = seal_phase(run_dir, "dev")
    checkpoint = {"schema": "OCM_M1_CHECKPOINT", "pre_restart_pid": os.getpid(),
                  "interpreter": sys.executable, "python_version": sys.version,
                  "boot_token": uuid.uuid4().hex,
                  "kso_state_hash": runtime.state.kso_state_hash,
                  "dev_terminal": dev_state.get("terminal"),
                  "dev_seal": seal["sha256"], "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    write_json(paths["checkpoint"], checkpoint)
    events_append(run_dir, "checkpoint", "CHECKPOINT_WRITTEN",
                  {"pre_restart_pid": checkpoint["pre_restart_pid"], "boot_token": checkpoint["boot_token"]})
    seal_phase(run_dir, "checkpoint")
    ledger_update(run_dir, phase="checkpoint", phase_wall_seconds=time.perf_counter() - started,
                  interpreter_restarts=0)
    return checkpoint


# ------------------------------------------------------- CHECKER_C: independent external unit

CHECKER_SCRIPT = """
import hashlib, json, sys
sys.path.insert(0, sys.argv[1])
from ocm.learning import methods as M
payload = json.loads(sys.stdin.read())
task = M.PolynomialTask("checker_C", payload["coefficients"])
program = tuple(payload["program"])
print(json.dumps({"verdict": "IDENTICAL" if M.normal_form(program) == task.coefficients else "MISMATCH",
                  "checker": M.CHECKER, "pid": __import__("os").getpid(),
                  "methods_sha256": hashlib.sha256(open(sys.argv[2], "rb").read()).hexdigest()}))
"""


def checker_C(coefficients, program) -> dict:
    """Frozen polynomial identity checker invoked as an INDEPENDENT unit: a fresh
    interpreter process with its own pid and its own digest of methods.py.
    Internal replay inside the runtime under test never counts."""
    methods_path = REPO / "src" / "ocm" / "learning" / "methods.py"
    proc = subprocess.run([sys.executable, "-c", CHECKER_SCRIPT, str(REPO / "src"), str(methods_path)],
                          input=json.dumps({"coefficients": [str(c) for c in coefficients],
                                            "program": list(program)}),
                          capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise AssayDefect(f"CHECKER_C_FAILED: {proc.stderr.strip()[:300]}")
    return json.loads(proc.stdout)


# --------------------------------------------------------------------------- phase: acquire (steps 6-8)

def clone_ocm_root(run_dir: Path, arm: str) -> Path:
    """Checkpoint clones: every arm loads its OWN copy of the checkpointed runtime
    state, so one arm's revocation can never leak into another arm's ledger."""
    import shutil
    source = run_files(run_dir)["ocm_root"]
    dest = run_dir / "ocm_clones" / arm
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if arm == "RESET":
        dest.mkdir()  # no learned history: empty runtime root, not a clone
    elif source.exists():
        shutil.copytree(source, dest)
    else:
        dest.mkdir()
    return dest


def arm_method(arm: str, run_dir: Path, dev_state: dict) -> dict:
    """Arm-specific capability state, reconstructed by the fresh process from the
    arm's own checkpoint clone."""
    paths = run_files(run_dir)
    info = {"arm": arm, "learned_history": False, "fragments_served": 0,
            "carrier_report": None, "refusal_reason": None, "method": M.GeneratorMethod()}
    if arm == "RESET":
        clone_ocm_root(run_dir, arm)
        info["note"] = "no learned history; fresh empty runtime"
    elif arm == "LIBRARY_ONLY":
        runtime = OCMRuntime(clone_ocm_root(run_dir, arm))  # solved objects replay from the clone
        info["learned_history"] = True
        info["library_atoms"] = len(runtime.state.ks.ids)
        info["note"] = ("accumulated solved objects present; learning/search-control state frozen "
                        "(generator atom exists on disk but is NOT served)")
        info["carrier_report"] = ("separable atoms: proof atoms (library) vs generator procedure atom "
                                  "(search control) are distinct KSO objects in this learner")
    elif arm == "CONTINUED":
        runtime = OCMRuntime(clone_ocm_root(run_dir, arm))
        info["learned_history"] = True
        if dev_state.get("generator_id"):
            method = M.load_generator(runtime, dev_state["generator_id"])  # support-sensitive reload
            info["method"] = method
            info["fragments_served"] = len(method.fragments)
        else:
            info["refusal_reason"] = "NO_ADMITTED_GENERATOR (learner refused deployment at dev time)"
    elif arm == "CONTINUED_WITH_LEARNING_STATE_REMOVED":
        runtime = OCMRuntime(clone_ocm_root(run_dir, arm))
        info["learned_history"] = True
        proofs_before = set(runtime.state.ks.ids)
        removed = False
        if dev_state.get("admission"):
            runtime.revoke([dev_state["admission"]["validation_evidence"]])
            try:
                M.load_generator(runtime, dev_state["generator_id"])
            except ValueError:
                removed = True
            proofs_live = proofs_before <= set(runtime.state.ks.ids)
            info["carrier_report"] = ("SURGICAL: generator warrant dead, solved proof atoms live"
                                      if removed and proofs_live else
                                      "JOINT: revoking the generator admission also disabled solved "
                                      "content; joint carrier recorded, no surgical independence claimed")
        info["note"] = "solved content preserved; learned-fragment/admission carrier revoked"
        if not dev_state.get("admission"):
            info["carrier_report"] = ("NO_ADMITTED_GENERATOR: nothing to revoke (the learner refused "
                                      "deployment at dev time); recorded honestly instead of claiming "
                                      "surgical removal")
    elif arm == "ORDINARY_ADAPTIVE_PARENT":
        ordinary = load_json(paths["ordinary"])  # plain JSON, no OCM bookkeeping
        if ordinary.get("fingerprint") != M.GeneratorMethod(
                tuple(tuple(f) for f in ordinary["fragments"]), tuple(ordinary["training_tasks"])).fingerprint:
            raise AssayDefect("ORDINARY_PARENT_PERSISTENCE_IDENTITY_MISMATCH")
        info["method"] = M.GeneratorMethod(tuple(tuple(f) for f in ordinary["fragments"]),
                                           tuple(ordinary["training_tasks"]))
        info["fragments_served"] = len(info["method"].fragments)
        info["note"] = ("outside OCM bookkeeping: same history and persistence, plain JSON store; "
                        "receives the identical mined fragments WITHOUT the admission gate (serves even "
                        "where the learner's no-slowdown rule refuses), without evidence supports, "
                        "revocation or support-sensitive reload")
    elif arm == "KNOWN_STRUCTURE_ORACLE":
        info["note"] = ("CALIBRATION ONLY, never a headline comparator; declared information advantage: "
                        "the target's structural class (true minimum primitive length) is given; "
                        "enumeration pruned to that length")
    else:
        raise SystemExit(f"UNKNOWN_ARM: {arm}")
    return info


def oracle_solve(task: M.PolynomialTask, budget: M.SearchBudget, declared_min_length: int) -> M.SearchResult:
    """Calibration arm search: identical grammar order, honest slot accounting,
    but every program whose length differs from the declared class is pruned."""
    from itertools import product
    checked = slots = 0
    for length in range(budget.max_length + 1):
        for program in product(M.PRIMITIVES, repeat=length):
            if length != declared_min_length:
                continue  # declared information advantage: structural pruning, not free verification
            slots += 1
            if slots > budget.slots:
                return M.SearchResult(task.fingerprint, "oracle", "BUDGET_EXHAUSTED", None,
                                      budget.slots, checked, (0,), budget.max_length)
            checked += 1
            if M.normal_form(program) == task.coefficients:
                return M.SearchResult(task.fingerprint, "oracle", "VERIFIED_POLYNOMIAL_IDENTITY",
                                      program, slots, checked, (0,), budget.max_length)
    return M.SearchResult(task.fingerprint, "oracle", "EXHAUSTED_DECLARED_GRAMMAR", None,
                          slots, checked, (0,), budget.max_length)


def phase_acquire(run_dir: Path, arm: str, slots_ladder, targets_n: int) -> dict:
    started = time.perf_counter()
    paths = run_files(run_dir)
    checkpoint = load_json(paths["checkpoint"])
    if checkpoint["pre_restart_pid"] == os.getpid():
        raise AssayDefect("SAME_PROCESS_FAKE_RESTART: acquire must run in a fresh OS process "
                          "(pid unchanged -- a function call in one long-lived process does not "
                          "satisfy lifecycle step 6)")
    partitions = load_json(paths["partitions"])
    dev_state = load_json(paths["dev_state"])
    protected_rows = partitions["streams"]["protected"]
    target_rows, obligation_rows = protected_rows[:targets_n], protected_rows[targets_n:]
    info = arm_method(arm, run_dir, dev_state)
    rows, obligations, verification_calls = [], [], 0
    for row in target_rows:  # step 7: acquire protected fresh target (target-specific information)
        task = M.PolynomialTask(row["task_id"], row["coefficients"])
        observations = [{"x": x, "value": str(M.evaluate_polynomial(task.coefficients, x))} for x in (0, 1, 2)]
        for slots in slots_ladder:
            budget = budget_of(partitions, slots)
            if arm == "KNOWN_STRUCTURE_ORACLE":
                result = oracle_solve(task, budget, row["min_primitive_length"])
            else:
                result = M.solve(task, budget, info["method"])
            verification_calls += 1
            verdict = None
            if result.program is not None:
                verdict = checker_C(row["coefficients"], result.program)  # independent unit, own pid+digest
                verification_calls += 1
            rows.append({"arm": arm, "target": row["normal_form_digest"], "budget_slots": slots,
                         "B_slots": result.slots, "B_candidates_checked": result.candidates_checked,
                         "status": result.status, "observations": len(observations),
                         "checker_verdict": verdict["verdict"] if verdict else None,
                         "checker_pid": verdict["pid"] if verdict else None,
                         "checker_methods_sha256": verdict["methods_sha256"] if verdict else None,
                         "verified_external": bool(verdict and verdict["verdict"] == "IDENTICAL"),
                         "refused": bool(info["refusal_reason"]), "censored": False})
    for row in obligation_rows:  # step 8: acquired object evaluated on fresh obligations
        task = M.PolynomialTask(row["task_id"], row["coefficients"])
        budget = budget_of(partitions, slots_ladder[-1])
        result = oracle_solve(task, budget, row["min_primitive_length"]) if arm == "KNOWN_STRUCTURE_ORACLE" \
            else M.solve(task, budget, info["method"])
        verdict = checker_C(row["coefficients"], result.program) if result.program is not None else None
        verification_calls += 1 + (1 if verdict else 0)
        obligations.append({"arm": arm, "target": row["normal_form_digest"],
                            "B_slots": result.slots, "B_candidates_checked": result.candidates_checked,
                            "status": result.status,
                            "verified_external": bool(verdict and verdict["verdict"] == "IDENTICAL"),
                            "censored": False})
    report = {"schema": "OCM_M1_ARM_REPORT", "arm": arm,
              "calibration_only": arm in CALIBRATION_ONLY_ARMS,
              "process": {"pid": os.getpid(), "pre_restart_pid": checkpoint["pre_restart_pid"],
                          "pid_changed": os.getpid() != checkpoint["pre_restart_pid"],
                          "boot_token_inherited": checkpoint["boot_token"]},
              "capability_state": {k: v for k, v in info.items() if k != "method"},
              "acquisition_rows": rows, "obligation_rows": obligations,
              "refusal_rate": (sum(1 for r in rows if r["refused"]) / len(rows)) if rows else None,
              "refusal_reason": info["refusal_reason"]}
    write_json(paths["arms"] / f"{arm}.json", report)
    events_append(run_dir, f"acquire_{arm}", "ARM_REPORT",
                  {"arm": arm, "rows": len(rows), "obligations": len(obligations),
                   "refusal_rate": report["refusal_rate"]})
    seal_phase(run_dir, f"acquire_{arm}")
    ledger_update(run_dir, phase=f"acquire_{arm}", phase_wall_seconds=time.perf_counter() - started,
                  interpreter_restarts=1,
                  candidate_enumerations=sum(r["B_candidates_checked"] for r in rows + obligations),
                  verification_calls=verification_calls)
    return report


def phase_restart_and_acquire(run_dir: Path, arm: str, slots_ladder, targets_n: int) -> dict:
    """REAL OS-PROCESS RESTART: spawn a fresh interpreter that loads persisted state."""
    child = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--run-dir", str(run_dir),
                            "--phase", "acquire", "--arm", arm,
                            "--slots-ladder", ",".join(str(s) for s in slots_ladder),
                            "--targets", str(targets_n)],
                           capture_output=True, text=True, timeout=600)
    receipt = {"arm": arm, "parent_pid": os.getpid(),
               "child_pid": None,  # filled from the child's own report below
               "child_returncode": child.returncode, "child_stderr_tail": child.stderr[-400:]}
    report_path = run_files(run_dir)["arms"] / f"{arm}.json"
    if child.returncode != 0 or not report_path.exists():
        write_json(run_files(run_dir)["arms"] / f"{arm}.json",
                   {"schema": "OCM_M1_ARM_REPORT", "arm": arm, "censored_whole_arm": True,
                    "restart_receipt": receipt, "acquisition_rows": [], "obligation_rows": [],
                    "refusal_rate": None, "censor_reason": f"child exited {child.returncode}"})
        raise SystemExit(f"ARM_CENSORED: {arm} child exit {child.returncode}: {child.stderr[-300:]}")
    report = load_json(report_path)
    report["restart_receipt"] = {**receipt, "child_pid": report["process"]["pid"]}
    write_json(report_path, report)
    if report["process"]["pid"] == os.getpid():
        raise AssayDefect("RESTART_EVIDENCE_FAILED: child pid equals parent pid")
    return report


# --------------------------------------------------------------------------- phase: summarize (deterministic)

def map_terminal(summary: dict) -> str:
    """Frozen precedence: ASSAY_DEFECT > LEAKAGE_ALARM > INSUFFICIENT_HISTORY > outcomes."""
    if summary["assay_defect"]:
        return "ASSAY_DEFECT"
    if summary["leakage_alarm"]:
        return "LEAKAGE_ALARM"
    if summary["insufficient_history"]:
        return "INSUFFICIENT_HISTORY"
    paired = summary["paired_B"]
    cont, reset = paired.get("CONTINUED"), paired.get("RESET")
    if not cont or not reset:
        return "CANNOT_CHECK_MISSING_ARM_DATA"
    censored = summary["censored_rows"]
    if censored:
        return f"CANNOT_CHECK_CENSORED_ROWS({censored})"
    improved = any(w["continued_B"] < w["reset_B"] for w in cont["common_with_RESET"])
    if not improved:
        return "NO_NATIVE_EFFECT"
    parent = paired.get("ORDINARY_ADAPTIVE_PARENT")
    if parent and all(w["parent_B"] == w["continued_B"] for w in parent["common_with_CONTINUED"]):
        return "PARENT_EQUIVALENT"
    return "NATIVE_ACQUISITION_DEMONSTRATED"


def phase_summarize(run_dir: Path) -> dict:
    started = time.perf_counter()
    paths = run_files(run_dir)
    seals = verify_seals(run_dir)  # fail closed on any tampered sealed log
    partitions = load_json(paths["partitions"])
    dev_state = load_json(paths["dev_state"])
    protected_digests = {row["normal_form_digest"] for row in partitions["streams"]["protected"]}
    history_digests = {row["normal_form_digest"] for stream in ("train", "validation", "test")
                       for row in partitions["streams"][stream]}
    history_digests |= {t["task"] for t in dev_state.get("traces", [])}
    leakage = sorted(history_digests & protected_digests)
    arms = {}
    for arm_file in sorted(paths["arms"].glob("*.json")):
        report = json.loads(arm_file.read_text(encoding="utf-8"))
        arms[report["arm"]] = report
    assay_defect = any(r.get("assay_defect") for r in arms.values())
    paired = {}
    for arm, report in arms.items():
        rows = [r for r in report.get("acquisition_rows", []) if not r.get("censored")]
        paired[arm] = {"mean_B": (sum(r["B_slots"] for r in rows) / len(rows)) if rows else None,
                       "successes": sum(1 for r in rows if r.get("verified_external")),
                       "attempts": len(rows), "refusal_rate": report.get("refusal_rate"),
                       "rows": rows}
    for a, b in (("CONTINUED", "RESET"), ("ORDINARY_ADAPTIVE_PARENT", "CONTINUED")):
        if a in paired and b in paired:
            bmap = {r["target"] + "@" + str(r["budget_slots"]): r["B_slots"] for r in paired[b]["rows"]}
            amap = {r["target"] + "@" + str(r["budget_slots"]): r["B_slots"] for r in paired[a]["rows"]}
            key = "common_with_" + b
            paired[a][key] = [{"key": k, "a_B": amap[k], "b_B": bmap[k]}
                              for k in sorted(set(amap) & set(bmap))]
    paired["CONTINUED"]["common_with_RESET"] = [
        {"continued_B": w["a_B"], "reset_B": w["b_B"]} for w in paired["CONTINUED"].get("common_with_RESET", [])]
    if "ORDINARY_ADAPTIVE_PARENT" in paired:
        paired["ORDINARY_ADAPTIVE_PARENT"]["common_with_CONTINUED"] = [
            {"parent_B": w["a_B"], "continued_B": w["b_B"]}
            for w in paired["ORDINARY_ADAPTIVE_PARENT"].get("common_with_CONTINUED", [])]
    not_applicable = sum(1 for report in arms.values()
                         if report.get("censored_whole_arm") or report.get("censor_reason"))
    summary = {
        "schema": "OCM_M1_SUMMARY", "deterministic": True, "seals_verified": seals,
        "leakage_alarm": bool(leakage), "leakage_shared": leakage,
        "insufficient_history": dev_state.get("terminal") == "INSUFFICIENT_HISTORY",
        "assay_defect": assay_defect,
        "paired_B": paired,
        "censored_rows": sum(1 for report in arms.values()
                             for r in report.get("acquisition_rows", []) + report.get("obligation_rows", [])
                             if r.get("censored")) + not_applicable,
        "p_not_applicable": (not_applicable / len(arms)) if arms else None,
        "cost_ledger": load_json(paths["ledger"]),
        "calibration_reference_ONLY": {a: paired[a] for a in CALIBRATION_ONLY_ARMS if a in paired},
        "claim_ceiling": "mechanism claim at this scope ONLY; economics/OCM-residual are M3; "
                         "open-endedness never claimable from finite success",
    }
    summary["terminal"] = map_terminal(summary)
    write_json(paths["summary"], summary)
    ledger_update(run_dir, phase="summarize", phase_wall_seconds=time.perf_counter() - started)
    print(json.dumps({"terminal": summary["terminal"], "arms": sorted(arms),
                      "p_not_applicable": summary["p_not_applicable"]}, sort_keys=True))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--phase", required=True,
                        choices=["dev", "checkpoint", "acquire", "restart-and-acquire", "summarize"])
    parser.add_argument("--arm", choices=ARMS)
    parser.add_argument("--slots", type=int, default=2000)
    parser.add_argument("--slots-ladder", default="2000")
    parser.add_argument("--targets", type=int, default=2, help="protected targets used as acquisition tasks")
    args = parser.parse_args()
    ladder = [int(s) for s in args.slots_ladder.split(",") if s]
    run_dir: Path = args.run_dir
    if args.phase == "dev":
        phase_dev(run_dir, args.slots)
    elif args.phase == "checkpoint":
        phase_checkpoint(run_dir)
    elif args.phase == "acquire":
        try:
            phase_acquire(run_dir, args.arm, ladder, args.targets)
        except AssayDefect as defect:
            raise SystemExit(f"ASSAY_DEFECT: {defect}")
    elif args.phase == "restart-and-acquire":
        phase_restart_and_acquire(run_dir, args.arm, ladder, args.targets)
    elif args.phase == "summarize":
        phase_summarize(run_dir)


if __name__ == "__main__":
    main()
