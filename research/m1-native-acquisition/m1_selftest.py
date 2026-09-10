"""Hostile selftest for the M1 native-acquisition machinery (entry gate (c)).

Runs sub-second on toy data on the Mac mini (no scored run here; scored execution
happens on laptop billy only, after gates (a)-(d) all hold).

Required hostiles, each asserted to fire EXACTLY when it should:
  (i)   NO-OP SOLVER: a solver that returns unchanged capability state without
        emitting a candidate MUST FAIL the positive control (gap-1 decisive check).
  (ii)  FAKE RESTART: a same-process function-call "restart" (pid unchanged) must
        be detected as an ASSAY_DEFECT-class error.
  (iii) SEALED-LOG TAMPER: mutating a sealed event log must make summarize fail
        closed.
  (iv)  ANSWER-IN-HISTORY PLANT: a history record containing the target's exact
        normal form must trip LEAKAGE_ALARM (history-constructor purity).
  (v)   NO-ALARM CASE: a clean toy run (real OS-process restart included) produces
        zero alarms.

Distinct exit codes per failure class:
  0 clean | 10 no-op control breach | 11 fake-restart undetected | 12 tamper
  undetected | 13 leakage undetected | 14 false alarm in clean run | 15 internal.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import m1_partitions as P  # noqa: E402
import m1_runner as R  # noqa: E402

EXIT = {"CLEAN": 0, "NOOP_CONTROL_BREACH": 10, "FAKE_RESTART_UNDETECTED": 11,
        "TAMPER_UNDETECTED": 12, "LEAKAGE_UNDETECTED": 13, "FALSE_ALARM": 14, "INTERNAL": 15}


def positive_control(dev_state: dict) -> bool:
    """The dev phase is load-bearing only if registered operators emitted candidates."""
    candidates = dev_state.get("candidates") or {}
    return candidates.get("candidates_emitted", 0) >= 1


def trim(document: dict, train_n: int, validation_n: int, protected_n: int) -> dict:
    """Shrink toy streams for speed only; disjointness and class structure are untouched."""
    import json
    trimmed = json.loads(json.dumps(document))
    trimmed["streams"]["train"] = trimmed["streams"]["train"][:train_n]
    trimmed["streams"]["validation"] = trimmed["streams"]["validation"][:validation_n]
    trimmed["streams"]["protected"] = trimmed["streams"]["protected"][:protected_n]
    return trimmed


def write_partitions(path: Path, document: dict) -> None:
    path.write_text(__import__("json").dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def toy_partitions(out: Path, per_stream: int) -> dict:
    document = P.emit(max_length=4, seed=P.FROZEN_SEED, per_stream=per_stream)
    out.write_text(__import__("json").dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return document


def control_no_op_solver(base: Path, document: dict) -> bool:
    """(i) Inject a solver that returns unchanged capability state, emitting nothing."""
    run_dir = base / "noop"
    run_dir.mkdir(parents=True)
    write_partitions(R.run_files(run_dir)["partitions"], trim(document, 4, 2, 4))
    real = R.M.learn_generator
    R.M.learn_generator = lambda training: R.M.GeneratorMethod()  # no candidate emitted, state unchanged
    try:
        try:
            R.phase_dev(run_dir, slots=4000)
        except SystemExit:
            pass  # INSUFFICIENT_HISTORY-class exits are also acceptable failures of a no-op solver
        dev_state = R.load_json(R.run_files(run_dir)["dev_state"])
    finally:
        R.M.learn_generator = real
    return not positive_control(dev_state)  # control fires iff positive control FAILED


def control_fake_restart(base: Path, document: dict) -> bool:
    """(ii) A same-process acquire (function call, pid unchanged) must be rejected."""
    run_dir = base / "fake"
    run_dir.mkdir(parents=True)
    write_partitions(R.run_files(run_dir)["partitions"], trim(document, 4, 2, 4))
    R.phase_dev(run_dir, slots=4000)
    R.phase_checkpoint(run_dir)
    try:
        R.phase_acquire(run_dir, "RESET", [4000], targets_n=1)
        return False  # same-process restart sailed through: control FAILED to fire
    except R.AssayDefect as defect:
        return "SAME_PROCESS_FAKE_RESTART" in str(defect)


def control_sealed_log_tamper(base: Path, document: dict) -> bool:
    """(iii) Mutating a sealed log must make summarize fail closed."""
    run_dir = base / "tamper"
    run_dir.mkdir(parents=True)
    write_partitions(R.run_files(run_dir)["partitions"], trim(document, 3, 2, 2))
    R.phase_dev(run_dir, slots=4000)
    R.phase_checkpoint(run_dir)
    log = run_dir / "events_dev.jsonl"
    log.write_bytes(log.read_bytes() + b'{"tampered": true}\n')
    try:
        R.phase_summarize(run_dir)
        return False
    except SystemExit as exit_:
        return "SEAL_VERIFICATION_FAILED" in str(exit_)


def control_leakage_plant(base: Path, document: dict) -> bool:
    """(iv) A history record containing the target's exact normal form trips LEAKAGE_ALARM."""
    planted = __import__("json").loads(__import__("json").dumps(document))
    target = planted["streams"]["protected"][0]
    planted["streams"]["train"].append({**target, "task_id": "PLANTED:" + target["task_id"]})
    run_dir = base / "plant"
    run_dir.mkdir(parents=True)
    R.write_json(R.run_files(run_dir)["partitions"], planted)
    try:
        R.phase_dev(run_dir, slots=4000)
        return False
    except SystemExit as exit_:
        return str(exit_).startswith("LEAKAGE_ALARM")


def clean_run(base: Path, document: dict, arms) -> dict:
    run_dir = base / "clean"
    run_dir.mkdir(parents=True)
    write_partitions(R.run_files(run_dir)["partitions"], trim(document, 6, 4, 4))
    R.phase_dev(run_dir, slots=4000)
    R.phase_checkpoint(run_dir)
    for arm in arms:
        R.phase_restart_and_acquire(run_dir, arm, [4000], targets_n=2)
    return R.phase_summarize(run_dir)


def mechanism_carrier_removal(base: Path) -> bool:
    """Full-mode mechanism check: where the registered learner DOES admit a generator,
    the REMOVED arm must revoke the carrier honestly (SURGICAL or JOINT, never silent),
    and CONTINUED must serve fragments through the support-sensitive reload."""
    import json
    from itertools import product
    budget_slots = 8000
    budget = R.M.SearchBudget(slots=budget_slots, max_length=6)
    prefix = ("double", "double")
    train, seen = [], set()
    for length in (3, 4, 5):
        for suffix in product(R.M.PRIMITIVES, repeat=length - 2):
            task = R.M.PolynomialTask(f"carrier{length}", R.M.normal_form(prefix + suffix))
            if task.fingerprint in seen:
                continue
            seen.add(task.fingerprint)
            result = R.M.solve(task, budget)
            if R.M.verify_solution(task, result):
                train.append((task, result))
            if len(train) >= 6:
                break
        if len(train) >= 6:
            break
    method = R.M.learn_generator(train)
    accepted_task, protected_tasks, tried = None, [], 0
    for length in range(3, 6):
        for program in product(R.M.PRIMITIVES, repeat=length):
            task = R.M.PolynomialTask(f"carrierval{length}", R.M.normal_form(program))
            if task.fingerprint in seen:
                continue
            if accepted_task is None:
                tried += 1
                if tried > 600:
                    break
                if R.M.validate_generator(method, [task], budget)["accepted"]:
                    accepted_task = task
                continue
            if len(protected_tasks) < 2 and R.M.verify_solution(task, R.M.solve(task, budget)):
                protected_tasks.append(task)
        if accepted_task is not None and len(protected_tasks) >= 2:
            break
    if accepted_task is None or len(protected_tasks) < 2:
        return False  # fixture failed to build; NOT a pass
    def row(task_id, task):
        return {"task_id": task_id, "coefficients": [str(c) for c in task.coefficients],
                "normal_form_digest": task.fingerprint, "min_primitive_length": 3,
                "semantic_class": {"fixture": True}}
    document = {"schema": "OCM_M1_PARTITIONS", "version": "V1", "frozen_seed": "carrier-fixture",
                "grammar": {"primitives": list(R.M.PRIMITIVES), "max_program_length": 6,
                            "checker": R.M.CHECKER},
                "streams": {"train": [row(f"t{i}", t) for i, (t, _r) in enumerate(train)],
                            "validation": [row("v0", accepted_task)],
                            "test": [row("s0", accepted_task)],
                            "protected": [row(f"c{i}", t) for i, t in enumerate(protected_tasks)]},
                "protected_set_sha256": "fixture", "disjointness_assertion": {"checked": False}}
    run_dir = base / "carrier"
    run_dir.mkdir(parents=True)
    R.write_json(R.run_files(run_dir)["partitions"], document)
    R.phase_dev(run_dir, slots=budget_slots)
    dev_state = R.load_json(R.run_files(run_dir)["dev_state"])
    if not dev_state.get("admission"):
        return False
    R.phase_checkpoint(run_dir)
    removed = R.phase_restart_and_acquire(run_dir, "CONTINUED_WITH_LEARNING_STATE_REMOVED", [budget_slots], 1)
    continued = R.phase_restart_and_acquire(run_dir, "CONTINUED", [budget_slots], 1)
    return (removed["capability_state"]["carrier_report"] is not None
            and continued["capability_state"]["fragments_served"] > 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true",
                        help="run all six arms (not required for the sub-second gate)")
    args = parser.parse_args()
    started = time.perf_counter()
    counts = {"no_op_solver_control_fired": None, "fake_restart_control_fired": None,
              "sealed_log_tamper_control_fired": None, "leakage_plant_control_fired": None,
              "no_alarm_case_alarms": None, "real_restart_evidenced": None,
              "carrier_removal_mechanism_fired": None}
    base = Path(tempfile.mkdtemp(prefix="m1_selftest_"))
    try:
        partitions = base / "partitions.toy.json"
        document = toy_partitions(partitions, per_stream=1)
        assert document["disjointness_assertion"]["shared_normal_forms"] == 0
        counts["no_op_solver_control_fired"] = control_no_op_solver(base, document)
        counts["fake_restart_control_fired"] = control_fake_restart(base, document)
        counts["sealed_log_tamper_control_fired"] = control_sealed_log_tamper(base, document)
        counts["leakage_plant_control_fired"] = control_leakage_plant(base, document)
        arms = R.ARMS if args.full else ("RESET", "CONTINUED")
        summary = clean_run(base, document, arms)
        alarms = int(summary["leakage_alarm"]) + int(summary["assay_defect"]) \
            + int(summary["insufficient_history"])
        counts["no_alarm_case_alarms"] = alarms
        report = R.load_json(R.run_files(base / "clean")["arms"] / f"{arms[-1]}.json")
        counts["real_restart_evidenced"] = bool(report["process"]["pid_changed"]
                                                and report["restart_receipt"]["child_pid"] != report["restart_receipt"]["parent_pid"])
        if args.full:  # outside the sub-second gate; exercises the revocation path
            counts["carrier_removal_mechanism_fired"] = mechanism_carrier_removal(base)
    except Exception as exc:  # noqa: BLE001  -- report the class, then exit 15
        print(f"INTERNAL_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT["INTERNAL"]
    finally:
        shutil.rmtree(base, ignore_errors=True)
    verdict = EXIT["CLEAN"]
    if counts["no_op_solver_control_fired"] is not True:
        verdict = EXIT["NOOP_CONTROL_BREACH"]
    elif counts["fake_restart_control_fired"] is not True:
        verdict = EXIT["FAKE_RESTART_UNDETECTED"]
    elif counts["sealed_log_tamper_control_fired"] is not True:
        verdict = EXIT["TAMPER_UNDETECTED"]
    elif counts["leakage_plant_control_fired"] is not True:
        verdict = EXIT["LEAKAGE_UNDETECTED"]
    elif counts["no_alarm_case_alarms"] != 0 or counts["real_restart_evidenced"] is not True:
        verdict = EXIT["FALSE_ALARM"]
    elif args.full and counts["carrier_removal_mechanism_fired"] is not True:
        verdict = EXIT["FALSE_ALARM"]
    print("M1_SELFTEST " + ("PASS" if verdict == 0 else "FAIL")
          + " " + __import__("json").dumps(counts, sort_keys=True)
          + f" wall_seconds={time.perf_counter() - started:.3f}")
    return verdict


if __name__ == "__main__":
    sys.exit(main())
