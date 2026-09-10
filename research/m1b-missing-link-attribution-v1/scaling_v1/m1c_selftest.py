"""Hostile selftest for the M1C amortisation-scaling machinery (entry gate 4).

Toy worlds ONLY (every artifact stamped toy_selftest_only_NOT_SCORED_EVIDENCE);
runs on laptop billy BEFORE the scored scaling run, alongside the inherited
m1b_selftest (which must also be green).  Each hostile is asserted to fire
EXACTLY when it should -- a planted defect that goes undetected, or a control
alarm on clean data, fails the gate.

Hostiles (M1C-specific; the M1B core hostiles stay covered by m1b_selftest):
  (i)   DEV-COST GATE: a re-executed dev phase whose cost is not the frozen
        14,427,131 (real mode) halts as RECEIPT_BINDING_DEFECT before any serve.
  (ii)  ARM CHARGE BINDING: an arm whose recorded dev-charge entry diverges from
        the run ledger's own dev cost alarms at analyze (every mode).
  (iii) SERVE LEAKAGE: a serve target planted in a history stream trips the
        leakage guard.
  (iv)  CYCLIC BINDING: serve rows reordered off the frozen cyclic target list
        trip CYCLIC_TARGET_BINDING (and NOT the determinism guard).
  (v)   SERVE DETERMINISM: one mutated B value for a re-served target trips
        SERVE_DETERMINISM.
  (vi)  FAKE RESTART: a same-process serve is rejected (SAME_PROCESS_FAKE_RESTART)
        and a stripped child-pid receipt trips RESTART_EVIDENCE at analyze.
  (vii) NULL NO-ALARM: sign-flip + equal-n label-shuffle nulls stay unrejected on
        planted null data and reject on planted effect data.
  (viii) CHARGE PROFILES: net(T) closed-form checks -- primary charges DEV once at
        every T, DEV-CAL-4 charges min(T,30)*DEV/30, the two converge for T >= 30.
  (ix)  CLEAN LIFECYCLE (no-alarm control): the full four-arm toy lifecycle with
        real per-arm OS-process restarts produces a NON-HALTING terminal with zero
        guard alarms, honest toy stamping, and correct cyclic/obligation shape.

Exit codes: 0 clean | 15 internal | 30 dev-cost gate | 31 arm charge binding |
32 serve leakage | 33 cyclic binding | 34 serve determinism | 35 fake restart |
36 restart evidence | 37 null discipline | 38 charge profiles | 39 false alarm |
40 lifecycle defect.
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
sys.path.insert(0, str(HERE))                 # m1c_scaling_runner (this lane)
sys.path.insert(0, str(HERE.parent))          # m1b lane (runner, stats, selftest helpers)
sys.path.insert(0, str(HERE.parent.parent / "m1-native-acquisition"))

import m1_runner as R1                        # noqa: E402
import m1b_runner as B1                       # noqa: E402
import m1b_stats as S1                        # noqa: E402
import m1c_scaling_runner as C1               # noqa: E402  the machinery under test

EXIT = {"CLEAN": 0, "INTERNAL": 15, "DEV_COST_GATE_FAILED": 30,
        "ARM_CHARGE_BINDING_FAILED": 31, "SERVE_LEAKAGE_UNDETECTED": 32,
        "CYCLIC_UNDETECTED": 33, "DETERMINISM_UNDETECTED": 34,
        "FAKE_RESTART_UNDETECTED": 35, "RESTART_EVIDENCE_UNDETECTED": 36,
        "NULL_DISCIPLINE_FAILED": 37, "CHARGE_PROFILE_FAILED": 38,
        "FALSE_ALARM": 39, "LIFECYCLE_DEFECT": 40}

TOY_RUNGS = (4, 8, 16)      # toy ladder: prefixes of the t_max=16 toy serve list
TOY_T_MAX = 16
TOY_BUDGET = 4000


def toy_protected_n(document: dict) -> int:
    return min(12, len(document["streams"]["protected"]))


def toy_run_dir(base: Path, name: str, document: dict) -> Path:
    import m1b_selftest as SB
    run_dir = base / name
    run_dir.mkdir(parents=True)
    R1.write_json(R1.run_files(run_dir)["partitions"],
                  SB.trim(document, 6, 4, toy_protected_n(document)))
    return run_dir


def control_dev_cost_gate(base: Path, document: dict) -> bool:
    """(i) Real-mode dev-cost gate: a dev phase recording the WRONG cost halts as
    RECEIPT_BINDING_DEFECT naming the frozen number, before any serve runs."""
    run_dir = toy_run_dir(base, "devcost", document)
    real_phase_dev = B1.phase_dev

    def fake_phase_dev(rd, slots, expected_fingerprint):
        R1.write_json(R1.run_files(rd)["dev_state"],
                      {"candidates": {"fragments": [], "candidates_emitted": 0},
                       "traces": [], "generator_id": None})
        R1.ledger_update(rd, candidate_enumerations_dev=12345)

    C1.WORLDS_MODE["toy"] = False
    B1.WORLDS_MODE["toy"] = False
    try:
        B1.phase_dev = fake_phase_dev
        try:
            C1.phase_dev_scaling(run_dir, 4000)
            fired = False
        except SystemExit as exit_:
            fired = ("RECEIPT_BINDING_DEFECT" in str(exit_)
                     and str(C1.DEV_COST_FROZEN) in str(exit_))
    finally:
        B1.phase_dev = real_phase_dev
        C1.WORLDS_MODE["toy"] = True
        B1.WORLDS_MODE["toy"] = True
    return fired


def control_fake_restart(base: Path, document: dict) -> bool:
    """(vi-a) A same-process serve (no fresh OS process) is refused."""
    run_dir = toy_run_dir(base, "fakers", document)
    C1.phase_dev_scaling(run_dir, 4000)
    C1.phase_checkpoint_scaling(run_dir)
    try:
        C1.phase_serve(run_dir, "RESET", TOY_T_MAX, TOY_BUDGET)
        return False
    except (R1.AssayDefect, B1.AssayDefect, C1.AssayDefect) as defect:
        return "SAME_PROCESS_FAKE_RESTART" in str(defect)


def toy_lifecycle(base: Path, document: dict, name="life") -> tuple:
    """Full four-arm toy lifecycle with REAL per-arm OS-process restarts."""
    run_dir = toy_run_dir(base, name, document)
    C1.phase_dev_scaling(run_dir, 4000)
    C1.phase_checkpoint_scaling(run_dir)
    for arm in C1.SCALING_ARMS:
        C1.phase_restart_and_serve(run_dir, arm, TOY_T_MAX, TOY_BUDGET)
    summary = C1.phase_analyze(run_dir, rungs=TOY_RUNGS)
    return run_dir, summary


def _retamper(run_dir: Path, arm: str, mutate) -> dict:
    """Apply a mutation to one arm's sealed report, then re-analyze fail-closed."""
    report_path = R1.run_files(run_dir)["arms"] / f"{arm}.json"
    report = R1.load_json(report_path)
    mutate(report)
    R1.write_json(report_path, report)
    return C1.phase_analyze(run_dir, rungs=TOY_RUNGS)


def control_arm_charge_binding(base: Path, life_dir: Path, document: dict) -> bool:
    """(ii) An arm whose dev-charge entry diverges from the run ledger alarms."""
    run_dir = base / "t_charge"
    shutil.copytree(life_dir, run_dir)

    def mutate(report):
        report["cost_ledger_hdi14"]["dev_enumeration_slots"] += 1
    summary = _retamper(run_dir, C1.GATE_ARM, mutate)
    return (summary["terminal"] == "RECEIPT_BINDING_DEFECT"
            and any("dev entry" in d for d in summary["guards"]["receipt_binding_defects"]))


def control_serve_leakage(base: Path, life_dir: Path, document: dict) -> bool:
    """(iii) A serve target planted from the train stream trips the leakage guard."""
    run_dir = base / "t_leak"
    shutil.copytree(life_dir, run_dir)
    planted = json.loads(json.dumps(document["streams"]["train"][0]))

    def mutate(report):
        report["serve_rows"][0]["target"] = planted["normal_form_digest"]
    summary = _retamper(run_dir, C1.GATE_ARM, mutate)
    return (summary["terminal"] == "ASSAY_DEFECT"
            and any(str(g).startswith("LEAKAGE") for g in summary["guards"]["assay_defects"]))


def control_cyclic_binding(base: Path, life_dir: Path, document: dict) -> bool:
    """(iv) Reordered serve rows trip CYCLIC_TARGET_BINDING and NOT determinism."""
    run_dir = base / "t_cyclic"
    shutil.copytree(life_dir, run_dir)

    def mutate(report):
        rows = sorted(report["serve_rows"], key=lambda r: r["serve_index"])
        if rows[0]["target"] == rows[1]["target"]:
            return False                       # identical targets: swap is invisible
        rows[0]["serve_index"], rows[1]["serve_index"] = rows[1]["serve_index"], rows[0]["serve_index"]
    summary = _retamper(run_dir, C1.GATE_ARM, mutate)
    markers = [str(g) for g in summary["guards"]["assay_defects"]]
    return (summary["terminal"] == "ASSAY_DEFECT"
            and any(g == "CYCLIC_TARGET_BINDING" for g in markers)
            and not any(g.startswith("SERVE_DETERMINISM") for g in markers))


def control_serve_determinism(base: Path, life_dir: Path, document: dict) -> bool:
    """(v) One mutated B value for a multi-served target trips SERVE_DETERMINISM."""
    run_dir = base / "t_det"
    shutil.copytree(life_dir, run_dir)

    def mutate(report):
        rows = sorted(report["serve_rows"], key=lambda r: r["serve_index"])
        multi = [d for d in {r["target"] for r in rows}
                 if sum(1 for r in rows if r["target"] == d) >= 2]
        if not multi:
            return False
        for row in rows:                        # bump ONE serve of a multi-served target
            if row["target"] == multi[0]:
                row["B_slots"] = row["B_slots"] + 1
                break
    summary = _retamper(run_dir, C1.GATE_ARM, mutate)
    return (summary["terminal"] == "ASSAY_DEFECT"
            and any(str(g).startswith("SERVE_DETERMINISM")
                    for g in summary["guards"]["assay_defects"]))


def control_restart_evidence(base: Path, life_dir: Path, document: dict) -> bool:
    """(vi-b) A stripped child-pid receipt trips RESTART_EVIDENCE at analyze."""
    run_dir = base / "t_restart"
    shutil.copytree(life_dir, run_dir)

    def mutate(report):
        report["restart_receipt"]["child_pid"] = None
    summary = _retamper(run_dir, C1.GATE_ARM, mutate)
    return (summary["terminal"] == "ASSAY_DEFECT"
            and any(g == "RESTART_EVIDENCE" for g in summary["guards"]["assay_defects"]))


def _synthetic(t_max: int, per_target: int, gate_delta: int) -> dict:
    """Synthetic serve arrays: RESET B=1000 at every serve, GATE = 1000 - delta;
    `per_target` serves share one target (the cyclic reality)."""
    arrays = {"RESET": [1000] * t_max, C1.GATE_ARM: [1000 - gate_delta] * t_max}
    clusters = []
    for start in range(0, t_max, per_target):
        clusters.append({"digest": f"toy{start}", "serve_indices": list(
            range(start, min(start + per_target, t_max)))})
    return arrays, clusters


def control_null_discipline() -> bool:
    """(vii) No-alarm on planted null data; rejection on planted effect data."""
    arrays_null, clusters_null = _synthetic(16, 4, 0)
    p_sf_null = S1.signflip_p([arrays_null["RESET"][i] - arrays_null[C1.GATE_ARM][i]
                               for i in range(16)], seed=S1.FROZEN_SEED)
    p_sh_null = C1._equal_n_label_shuffle_p(clusters_null, arrays_null, 16)
    arrays_eff, clusters_eff = _synthetic(16, 4, 400)
    p_sf_eff = S1.signflip_p([arrays_eff["RESET"][i] - arrays_eff[C1.GATE_ARM][i]
                              for i in range(16)], seed=S1.FROZEN_SEED)
    p_sh_eff = C1._equal_n_label_shuffle_p(clusters_eff, arrays_eff, 16)
    return (p_sf_null is not None and p_sf_null > 0.05
            and p_sh_null is not None and p_sh_null > 0.05
            and p_sf_eff is not None and p_sf_eff < 0.05
            and p_sh_eff is not None and p_sh_eff < 0.05)


def control_charge_profiles() -> bool:
    """(viii) Closed-form net(T): primary charges DEV once at every T; DEV-CAL-4
    charges min(T, N_FROZEN)*DEV/N_FROZEN; the two converge for T >= 30."""
    t_max, dev = 64, 30000
    arrays = {"RESET": [1000] * t_max, C1.GATE_ARM: [0] * t_max}
    primary = C1._cumulative_net(arrays, t_max, dev, charge_profile=None)
    devcal4 = C1._cumulative_net(arrays, t_max, dev, charge_profile="devcal4")
    ok = all(primary[i] == (i + 1) * 1000 - dev for i in range(t_max))
    nf = C1.N_FROZEN
    ok = ok and all(devcal4[i] == (i + 1) * 1000 - min(i + 1, nf) * dev / nf
                    for i in range(t_max))
    ok = ok and all(primary[i] == devcal4[i] for i in range(nf - 1, t_max))
    crossing = next(i + 1 for i, v in enumerate(primary) if v > 0)
    crossing4 = next(i + 1 for i, v in enumerate(devcal4) if v > 0)
    return ok and crossing == 31 and crossing4 == 31 and devcal4[29] == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", action="store_true",
                        help="keep the toy run dirs for inspection")
    args = parser.parse_args()
    started = time.perf_counter()
    counts = {"dev_cost_gate_fired": None, "fake_restart_refused": None,
              "arm_charge_binding_fired": None, "serve_leakage_fired": None,
              "cyclic_binding_fired": None, "serve_determinism_fired": None,
              "restart_evidence_fired": None, "null_discipline_ok": None,
              "charge_profiles_ok": None, "clean_lifecycle_ok": None}
    base = Path(tempfile.mkdtemp(prefix="m1c_selftest_"))
    try:
        import m1b_selftest as SB
        C1.WORLDS_MODE["toy"] = True          # toy worlds for EVERYTHING here
        B1.WORLDS_MODE["toy"] = True
        document = SB.toy_document()
        assert document["disjointness_assertion"]["shared_normal_forms"] == 0
        counts["null_discipline_ok"] = control_null_discipline()
        counts["charge_profiles_ok"] = control_charge_profiles()
        counts["dev_cost_gate_fired"] = control_dev_cost_gate(base, document)
        counts["fake_restart_refused"] = control_fake_restart(base, document)
        life_dir, _life_summary = toy_lifecycle(base, document, "clean")
        counts["clean_lifecycle_ok"], details = control_clean_lifecycle_from(life_dir, document)
        counts["arm_charge_binding_fired"] = control_arm_charge_binding(base, life_dir, document)
        counts["serve_leakage_fired"] = control_serve_leakage(base, life_dir, document)
        counts["cyclic_binding_fired"] = control_cyclic_binding(base, life_dir, document)
        counts["serve_determinism_fired"] = control_serve_determinism(base, life_dir, document)
        counts["restart_evidence_fired"] = control_restart_evidence(base, life_dir, document)
    except Exception as exc:  # noqa: BLE001  -- report class + message, then exit 15
        print(json.dumps({"EXIT": "INTERNAL", "error": f"{type(exc).__name__}: {exc}"},
                         sort_keys=True))
        if not args.keep:
            shutil.rmtree(base, ignore_errors=True)
        return EXIT["INTERNAL"]
    elapsed = round(time.perf_counter() - started, 3)
    verdict = {"elapsed_seconds": elapsed, "toy_protected_n": toy_protected_n(document),
               "freeze_sha256": C1.FREEZE_SHA256, "devcal4_n_frozen": C1.N_FROZEN,
               "clean_lifecycle": details, **counts}
    print(json.dumps(verdict, sort_keys=True))
    if not args.keep:
        shutil.rmtree(base, ignore_errors=True)
    if counts["dev_cost_gate_fired"] is not True:
        return EXIT["DEV_COST_GATE_FAILED"]
    if counts["fake_restart_refused"] is not True:
        return EXIT["FAKE_RESTART_UNDETECTED"]
    if counts["arm_charge_binding_fired"] is not True:
        return EXIT["ARM_CHARGE_BINDING_FAILED"]
    if counts["serve_leakage_fired"] is not True:
        return EXIT["SERVE_LEAKAGE_UNDETECTED"]
    if counts["cyclic_binding_fired"] is not True:
        return EXIT["CYCLIC_UNDETECTED"]
    if counts["serve_determinism_fired"] is not True:
        return EXIT["DETERMINISM_UNDETECTED"]
    if counts["restart_evidence_fired"] is not True:
        return EXIT["RESTART_EVIDENCE_UNDETECTED"]
    if counts["null_discipline_ok"] is not True:
        return EXIT["NULL_DISCIPLINE_FAILED"]
    if counts["charge_profiles_ok"] is not True:
        return EXIT["CHARGE_PROFILE_FAILED"]
    if counts["clean_lifecycle_ok"] is not True:
        return EXIT["LIFECYCLE_DEFECT"]
    return EXIT["CLEAN"]


def control_clean_lifecycle_from(run_dir: Path, document: dict) -> tuple:
    """No-alarm assertions over an ALREADY-RUN clean lifecycle dir."""
    summary = R1.load_json(R1.run_files(run_dir)["summary"])
    guards = summary["guards"]
    reports = {a: R1.load_json(R1.run_files(run_dir)["arms"] / f"{a}.json")
               for a in C1.SCALING_ARMS}
    partitions = R1.load_json(R1.run_files(run_dir)["partitions"])
    prot_rows = partitions["streams"]["protected"]
    restarts_real = all(r["restart_receipt"]["child_pid"] not in
                        (None, r["restart_receipt"]["parent_pid"])
                        and r["process"]["pid_changed"] for r in reports.values())
    cyclic_expected = [prot_rows[i % len(prot_rows)]["normal_form_digest"]
                       for i in range(TOY_T_MAX)]
    cyclic_actual = [r["target"] for r in sorted(
        reports[C1.GATE_ARM]["serve_rows"], key=lambda r: r["serve_index"])]
    expected_obligations = prot_rows[C1.OBLIGATION_SLICE[0]:C1.OBLIGATION_SLICE[1]]
    details = {"terminal": summary["terminal"],
               "guard_alarms": guards["assay_defects"] + guards["receipt_binding_defects"],
               "toy_stamp": summary["toy_selftest_only_NOT_SCORED_EVIDENCE"] is True,
               "four_arms": sorted(reports) == sorted(C1.SCALING_ARMS),
               "restarts_real": restarts_real,
               "cyclic_ok": cyclic_actual == cyclic_expected,
               "obligations_ok": all(len(r["obligation_rows"]) == len(expected_obligations)
                                     for r in reports.values()),
               "reset_zero_dev": reports["RESET"]["cost_ledger_hdi14"]["dev_enumeration_slots"] == 0,
               "holm_keys": sorted(summary["primary"]["holm_family"]),
               "secondary_n_frozen": summary["secondary"]["n_frozen"],
               "invariants": {k: v["status"] for k, v in summary["m1b_invariants"].items()}}
    fired = (summary["terminal"] not in ("RECEIPT_BINDING_DEFECT", "ASSAY_DEFECT")
             and not summary["terminal"].startswith("CANNOT_CHECK")
             and not details["guard_alarms"] and details["toy_stamp"]
             and details["four_arms"] and details["restarts_real"]
             and details["cyclic_ok"] and details["obligations_ok"]
             and details["reset_zero_dev"]
             and details["holm_keys"] == [f"T{t}" for t in TOY_RUNGS]
             and details["secondary_n_frozen"] == 30
             and all(s in ("PASS", "KNOWN_DISCLOSED", "NOT_APPLICABLE")
                     for s in details["invariants"].values()))
    return fired, details


if __name__ == "__main__":
    sys.exit(main())
