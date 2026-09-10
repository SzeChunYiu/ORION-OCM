"""Hostile selftest for the M1B missing-link-attribution machinery (entry gate).

Sub-second-ish on toy data (quick mode); --full runs the complete ten-arm toy
lifecycle including a real OS-process restart per arm.  Runs on the Mac mini as a
SELFTEST ONLY (toy worlds, stamped toy_selftest_only); the scored run happens on
laptop billy only, after every entry gate holds.

Required hostiles, each asserted to fire EXACTLY when it should:
  (i)    NO-OP SOLVER: a solver returning unchanged capability state must fail the
         positive control (M1 precedent).
  (ii)   FAKE RESTART: a same-process acquire must be rejected as ASSAY_DEFECT.
  (iii)  SEALED-LOG TAMPER: mutating a sealed log must fail summarize closed.
  (iv)   ANSWER-IN-HISTORY PLANT: a planted target in history trips LEAKAGE_ALARM.
  (v)    FORCED_FRAGMENT_NEGATIVE: a planted fragment leak into APPL_KO serving
         alarms; a clean KO does not (freeze negatives_to_invariants #1).
  (vi)   REFUSAL_CORRECTNESS: refusal is data -- refused-but-served alarms,
         refused-and-not-served is intact (freeze negatives_to_invariants #2).
  (vii)  NULL_INDETERMINACY: a null straddle is a legitimate INDETERMINATE verdict,
         never a defect; two determinate strata disagreeing IS a defect (freeze
         negatives_to_invariants #3).
  (viii) KO NON-COLLAPSE: a materially-recovering KO arm alarms the collapse check.
  (ix)   ADAPTER/NATIVE PARITY: adapter_solve with native timing+cost reproduces
         M.solve through GeneratorMethod exactly (status, program, slots, checked).

Exit codes: 0 clean | 10 no-op breach | 11 fake restart | 12 tamper | 13 leakage |
14 false alarm | 15 internal | 20 forced-fragment | 21 refusal | 22 null-indeterminacy
| 23 KO collapse | 24 adapter parity | 25 lifecycle defect.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "m1-native-acquisition"))

import m1_partitions as P  # noqa: E402
import m1_runner as R  # noqa: E402
import m1b_runner as b1  # noqa: E402
import m1b_stats as S  # noqa: E402

EXIT = {"CLEAN": 0, "NOOP_CONTROL_BREACH": 10, "FAKE_RESTART_UNDETECTED": 11,
        "TAMPER_UNDETECTED": 12, "LEAKAGE_UNDETECTED": 13, "FALSE_ALARM": 14,
        "INTERNAL": 15, "FORCED_FRAGMENT_FAILED": 20, "REFUSAL_FAILED": 21,
        "NULL_INDETERMINACY_FAILED": 22, "KO_COLLAPSE_FAILED": 23,
        "ADAPTER_PARITY_FAILED": 24, "LIFECYCLE_DEFECT": 25}

ALL_ARMS = b1.ARMS


def toy_document() -> dict:
    return P.emit(max_length=4, seed=P.FROZEN_SEED, per_stream=1)


def trim(document: dict, train_n: int, validation_n: int, protected_n: int) -> dict:
    trimmed = json.loads(json.dumps(document))
    trimmed["streams"]["train"] = trimmed["streams"]["train"][:train_n]
    trimmed["streams"]["validation"] = trimmed["streams"]["validation"][:validation_n]
    trimmed["streams"]["protected"] = trimmed["streams"]["protected"][:protected_n]
    return trimmed


def fresh_run_dir(base: Path, name: str, document: dict, train_n=6, validation_n=4, protected_n=4) -> Path:
    run_dir = base / name
    run_dir.mkdir(parents=True)
    R.write_json(R.run_files(run_dir)["partitions"], trim(document, train_n, validation_n, protected_n))
    return run_dir


def positive_control(dev_state: dict) -> bool:
    candidates = dev_state.get("candidates") or {}
    return candidates.get("candidates_emitted", 0) >= 1


# ------------------------------------------------------------------ lifecycle hostiles

def control_no_op_solver(base: Path, document: dict) -> bool:
    run_dir = fresh_run_dir(base, "noop", document, 4, 2, 4)
    real = R.M.learn_generator
    R.M.learn_generator = lambda training: R.M.GeneratorMethod()  # emits nothing, state unchanged
    try:
        try:
            b1.phase_dev(run_dir, slots=4000, expected_fingerprint=None)
        except SystemExit:
            pass  # INSUFFICIENT_HISTORY-class exits also fail a no-op solver
        dev_state = R.load_json(R.run_files(run_dir)["dev_state"])
    finally:
        R.M.learn_generator = real
    return not positive_control(dev_state)


def control_fake_restart(base: Path, document: dict) -> bool:
    run_dir = fresh_run_dir(base, "fake", document, 4, 2, 4)
    b1.phase_dev(run_dir, slots=4000, expected_fingerprint=None)
    b1.phase_checkpoint(run_dir)
    try:
        b1.phase_acquire(run_dir, "RESET", [4000], targets_n=1)
        return False
    except (R.AssayDefect, b1.AssayDefect) as defect:
        return "SAME_PROCESS_FAKE_RESTART" in str(defect)


def control_sealed_log_tamper(base: Path, document: dict) -> bool:
    run_dir = fresh_run_dir(base, "tamper", document, 3, 2, 2)
    b1.phase_dev(run_dir, slots=4000, expected_fingerprint=None)
    b1.phase_checkpoint(run_dir)
    log = run_dir / "events_dev.jsonl"
    log.write_bytes(log.read_bytes() + b'{"tampered": true}\n')
    try:
        b1.phase_summarize(run_dir)
        return False
    except SystemExit as exit_:
        return "SEAL_VERIFICATION_FAILED" in str(exit_)


def control_leakage_plant(base: Path, document: dict) -> bool:
    planted = json.loads(json.dumps(document))
    target = trim(document, 4, 2, 4)["streams"]["protected"][0]
    planted["streams"]["train"].append({**target, "task_id": "PLANTED:" + target["task_id"]})
    run_dir = base / "plant"
    run_dir.mkdir(parents=True)
    R.write_json(R.run_files(run_dir)["partitions"], planted)
    try:
        b1.phase_dev(run_dir, slots=4000, expected_fingerprint=None)
        return False
    except SystemExit as exit_:
        return str(exit_).startswith("LEAKAGE_ALARM")


# --------------------------------------------------------------------- unit hostiles

def control_forced_fragment() -> bool:
    base = {"capability_state": {"fragments_served": 0}, "acquisition_rows": []}
    clean = S.forced_fragment_check(base)
    planted = {"capability_state": {"fragments_served": 2},
               "acquisition_rows": [{"search_behavior": {"guided_checked": 3,
                                                         "retrieval_events": 3}}]}
    leaked = S.forced_fragment_check(planted)
    return clean["alarm_forced_fragment"] is False and clean["negative_confirmed"] is True \
        and leaked["alarm_forced_fragment"] is True and leaked["negative_confirmed"] is False


def control_refusal() -> bool:
    refused_clean = {"capability_state": {"refusal_reason": "NO_ADMITTED_GENERATOR"},
                     "acquisition_rows": [{"search_behavior": {"guided_checked": 0}}]}
    refused_served = {"capability_state": {"refusal_reason": "NO_ADMITTED_GENERATOR"},
                      "acquisition_rows": [{"search_behavior": {"guided_checked": 5}}]}
    served_clean = {"capability_state": {"refusal_reason": None},
                    "acquisition_rows": [{"search_behavior": {"guided_checked": 5}}]}
    a = S.refusal_correctness_check({"CONTINUED": refused_clean})
    b = S.refusal_correctness_check({"CONTINUED": refused_served})
    c = S.refusal_correctness_check({"CONTINUED": served_clean})
    return a["intact"] and c["intact"] and b["intact"] is False and b["alarm_refusal_tuned_away"]


def control_null_indeterminacy() -> bool:
    def keyed(diffs_by_rung):
        arm, reset = {}, {}
        i = 0
        for rung, diffs in diffs_by_rung.items():
            for d in diffs:
                key = f"t{i}@{rung}"
                arm[key], reset[key] = 100 - d, 100
                i += 1
        return {"ARM": arm, "RESET": reset}
    tiny = keyed({"1000": [1, -1, 2, -2, 1, -1], "4000": [-1, 1, -2, 2, 1, -1]})
    null_case = S.direction_tests(tiny, "ARM")
    conflict = keyed({"1000": [40, 42, 41, 43, 40, 42], "4000": [-40, -42, -41, -43, -40, -42]})
    conflict_case = S.direction_tests(conflict, "ARM")
    return null_case["verdict"] == "NULL_EFFECT_INDETERMINATE" \
        and conflict_case["verdict"] == "DIRECTION_CONFLICT_ASSAY_DEFECT"


def control_ko_collapse() -> bool:
    collapsed = S.ko_collapse_check({"material": False, "mean": 0.02}, {"n_pairs": 6})
    non_collapsed = S.ko_collapse_check({"material": True, "mean": 0.55}, {"n_pairs": 6})
    return collapsed["alarm_non_collapse"] is False and collapsed["collapsed"] is True \
        and non_collapsed["alarm_non_collapse"] is True and non_collapsed["collapsed"] is False


def control_adapter_parity(document: dict) -> bool:
    row = trim(document, 4, 2, 4)["streams"]["protected"][0]
    task = R.M.PolynomialTask(row["task_id"], row["coefficients"])
    budget = R.M.SearchBudget(slots=3000, max_length=6)
    fragments = (("double", "double"), ("square", "inc"), ("inc", "square"))
    native = R.M.solve(task, budget, R.M.GeneratorMethod(fragments, ()))
    mirrored = b1.adapter_solve(task, budget, fragments, b1.timing_native,
                                b1.cost_native, p_star=None, execution=True)
    return (native.status == mirrored[0].status
            and native.program == mirrored[0].program
            and native.slots == mirrored[0].slots
            and native.candidates_checked == mirrored[0].candidates_checked)


# ------------------------------------------------------------------- clean toy run

def clean_run(base: Path, document: dict, arms) -> dict:
    run_dir = fresh_run_dir(base, "clean", document, 6, 4, 4)
    b1.phase_dev(run_dir, slots=4000, expected_fingerprint=None)
    b1.phase_checkpoint(run_dir)
    for arm in arms:
        b1.phase_restart_and_acquire(run_dir, arm, [4000], targets_n=2)
    return b1.phase_summarize(run_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true",
                        help="run the complete ten-arm toy lifecycle (laptop gate)")
    parser.add_argument("--quick", action="store_true",
                        help="two-arm fast lifecycle (Mac sub-second gate)")
    args = parser.parse_args()
    started = time.perf_counter()
    counts = {"no_op_solver_control_fired": None, "fake_restart_control_fired": None,
              "sealed_log_tamper_control_fired": None, "leakage_plant_control_fired": None,
              "forced_fragment_control_fired": None, "refusal_control_fired": None,
              "null_indeterminacy_control_fired": None, "ko_collapse_control_fired": None,
              "adapter_parity_control_fired": None, "no_alarm_case_alarms": None,
              "real_restart_evidenced": None, "lifecycle_mechanics": None}
    base = Path(tempfile.mkdtemp(prefix="m1b_selftest_"))
    try:
        b1.WORLDS_MODE["toy"] = True  # toy worlds for EVERYTHING the selftest runs
        document = toy_document()
        assert document["disjointness_assertion"]["shared_normal_forms"] == 0
        counts["no_op_solver_control_fired"] = control_no_op_solver(base, document)
        counts["fake_restart_control_fired"] = control_fake_restart(base, document)
        counts["sealed_log_tamper_control_fired"] = control_sealed_log_tamper(base, document)
        counts["leakage_plant_control_fired"] = control_leakage_plant(base, document)
        counts["forced_fragment_control_fired"] = control_forced_fragment()
        counts["refusal_control_fired"] = control_refusal()
        counts["null_indeterminacy_control_fired"] = control_null_indeterminacy()
        counts["ko_collapse_control_fired"] = control_ko_collapse()
        counts["adapter_parity_control_fired"] = control_adapter_parity(document)
        arms = ALL_ARMS if args.full else ("RESET", "RETR_ORACLE", "APPL_KO")
        if args.quick:
            arms = ("RESET",)
        summary = clean_run(base, document, arms)
        alarms = int(summary["leakage_alarm"]) + int(summary["assay_defect"]) \
            + int(summary["insufficient_history"])
        counts["no_alarm_case_alarms"] = alarms
        report = R.load_json(R.run_files(base / "clean")["arms"] / f"{arms[-1]}.json")
        counts["real_restart_evidenced"] = bool(
            report["process"]["pid_changed"]
            and report["restart_receipt"]["child_pid"] != report["restart_receipt"]["parent_pid"])
        mechanics = []
        ko_path = R.run_files(base / "clean")["arms"] / "APPL_KO.json"
        if ko_path.exists():
            ko_report = R.load_json(ko_path)
            mechanics.append(all((r.get("search_behavior") or {}).get("guided_checked", 0) == 0
                                 for r in ko_report["acquisition_rows"]))
        retr_ko = R.load_json(R.run_files(base / "clean")["arms"] / "RETR_KO.json") \
            if (base / "clean" / "arms" / "RETR_KO.json").exists() else None
        if retr_ko is not None:
            mechanics.append(all((r.get("search_behavior") or {}).get("guided_checked", 0) == 0
                                 for r in retr_ko["acquisition_rows"]))
        counts["lifecycle_mechanics"] = all(mechanics) if mechanics else None
    except Exception as exc:  # noqa: BLE001  -- report the class, then exit 15
        print(json.dumps({"EXIT": "INTERNAL", "error": f"{type(exc).__name__}: {exc}"},
                         sort_keys=True))
        shutil.rmtree(base, ignore_errors=True)
        return EXIT["INTERNAL"]
    elapsed = round(time.perf_counter() - started, 3)
    verdict = {"elapsed_seconds": elapsed, "arms_run": list(arms), **counts}
    print(json.dumps(verdict, sort_keys=True))
    shutil.rmtree(base, ignore_errors=True)
    if counts["no_op_solver_control_fired"] is not True:
        return EXIT["NOOP_CONTROL_BREACH"]
    if counts["fake_restart_control_fired"] is not True:
        return EXIT["FAKE_RESTART_UNDETECTED"]
    if counts["sealed_log_tamper_control_fired"] is not True:
        return EXIT["TAMPER_UNDETECTED"]
    if counts["leakage_plant_control_fired"] is not True:
        return EXIT["LEAKAGE_UNDETECTED"]
    if counts["forced_fragment_control_fired"] is not True:
        return EXIT["FORCED_FRAGMENT_FAILED"]
    if counts["refusal_control_fired"] is not True:
        return EXIT["REFUSAL_FAILED"]
    if counts["null_indeterminacy_control_fired"] is not True:
        return EXIT["NULL_INDETERMINACY_FAILED"]
    if counts["ko_collapse_control_fired"] is not True:
        return EXIT["KO_COLLAPSE_FAILED"]
    if counts["adapter_parity_control_fired"] is not True:
        return EXIT["ADAPTER_PARITY_FAILED"]
    if counts["no_alarm_case_alarms"] != 0 or counts["real_restart_evidenced"] is not True:
        return EXIT["FALSE_ALARM"]
    if counts["lifecycle_mechanics"] is False:
        return EXIT["LIFECYCLE_DEFECT"]
    return EXIT["CLEAN"]


if __name__ == "__main__":
    sys.exit(main())
