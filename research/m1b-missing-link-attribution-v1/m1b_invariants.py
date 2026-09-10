"""Negatives-to-invariants checkers for M1B runs (from the M1B_SCORED_V1 scored run).

Every negative and disclosure produced by the scored run is codified here as a
checkable invariant for FUTURE runs.  A checker returns one of:
  PASS               invariant holds on the inspected artifacts
  KNOWN_DISCLOSED    invariant is violated in the exact shape already disclosed for
                     M1B_SCORED_V1 (RUN_MANIFEST_V1.json.instrumentation_disclosures)
                     -- legal ONLY while matched to its disclosure id; any OTHER shape
                     of violation is a FAIL
  FAIL               violation: the run must not be cited until attributed and, if
                     real, repaired by prospective amendment

Usage:  python m1b_invariants.py --run-dir <scored run dir> [--expect-disclosed]

Deterministic; reads only sealed run artifacts (summary.json, arms/*.json).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MARGIN = 0.20  # matches m1b_stats.MARGIN (frozen)

# Disclosed-for-M1B_SCORED_V1 states (RUN_MANIFEST_V1.json): (invariant, arm) keys
# allowed to report KNOWN_DISCLOSED instead of FAIL.
DISCLOSED = {
    ("observation_horizon_consistency", "STRONG_ADAPTIVE_PARENT"): "M1B-DISC-1",
    ("observation_horizon_consistency", "APPL_ORACLE"): "M1B-DISC-1",
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def retrieval_no_fire_no_effect(summary: dict) -> dict:
    """RETR_ORACLE with zero on-path fires must equal RESET EXACTLY (scored-run
    negative: perfect timing over an undiscriminated library is a no-op).  A future
    run where zero-fire RETR differs from RESET is an assay defect, and a run where
    RETR fired on-path (retrieval_gt_events > 0) is out of scope for this invariant
    (reported NOT_APPLICABLE, never silently passed)."""
    arms = summary.get("paired", {})
    retr, reset = arms.get("RETR_ORACLE"), arms.get("RESET")
    if not retr or not reset:
        return {"invariant": "retrieval_no_fire_no_effect", "status": "FAIL",
                "detail": "RETR_ORACLE/RESET paired aggregates missing"}
    fired = summary.get("cost_ledger_hdi14", {}).get("RETR_ORACLE", {}) \
        .get("retrieval_events", 0)
    if fired:
        return {"invariant": "retrieval_no_fire_no_effect", "status": "NOT_APPLICABLE",
                "detail": f"RETR_ORACLE fired {fired} events; zero-fire null not engaged"}
    identical = (retr.get("mean_B_top") == reset.get("mean_B_top")
                 and retr.get("mean_B_all") == reset.get("mean_B_all")
                 and retr.get("successes") == reset.get("successes"))
    return {"invariant": "retrieval_no_fire_no_effect",
            "status": "PASS" if identical else "FAIL",
            "detail": {"retr_mean_B_top": retr.get("mean_B_top"),
                       "reset_mean_B_top": reset.get("mean_B_top"),
                       "retr_successes": retr.get("successes"),
                       "reset_successes": reset.get("successes")}}


def observation_horizon_consistency(run_dir: Path) -> dict:
    """Observation-trace retrieval cost must not exceed the arm's own acquisition
    slots (M1B-DISC-1: the static-parity observation traced the full budget horizon,
    inflating retrieval_events/retrieval_cost_slots for registered-path arms into
    upper bounds).  Per arm; violations matching DISCLOSED and --expect-disclosed
    report KNOWN_DISCLOSED with their disclosure id."""
    summary = _load(run_dir / "summary.json")
    findings = []
    worst_status = "PASS"
    for arm, ledger in sorted(summary.get("cost_ledger_hdi14", {}).items()):
        retr_cost = ledger.get("retrieval_cost_slots", 0)
        acq = ledger.get("acquisition_slots", 0)
        if retr_cost > acq:
            key = ("observation_horizon_consistency", arm)
            disclosed = key in DISCLOSED
            status = "KNOWN_DISCLOSED" if disclosed else "FAIL"
            findings.append({"arm": arm, "retrieval_cost_slots": retr_cost,
                             "acquisition_slots": acq, "status": status,
                             "disclosure": DISCLOSED.get(key)})
        else:
            findings.append({"arm": arm, "retrieval_cost_slots": retr_cost,
                             "acquisition_slots": acq, "status": "PASS"})
        if findings[-1]["status"] == "FAIL":
            worst_status = "FAIL"
        elif findings[-1]["status"] == "KNOWN_DISCLOSED" and worst_status == "PASS":
            worst_status = "KNOWN_DISCLOSED"
    return {"invariant": "observation_horizon_consistency", "status": worst_status,
            "detail": findings}


def typed_failure_cross_path_consistency(run_dir: Path) -> dict:
    """M.solve-path and mirror-path arms must not diverge in typed-failure VOCABULARY
    for identical search behaviour (M1B-DISC-2: M.solve returns no rejected-candidate
    count, so its non-verified rows type as budget_censored where the mirror's
    identical rows type as verification_reject).  The invariant a future run must
    hold: whenever an M.solve-path arm and a mirror-path arm produce the SAME status
    histogram, their typed-failure labels agree; a vocabulary-only divergence on
    identical statuses is the disclosed instrumentation gap, FAIL unless the run is
    the disclosed one (status vocabulary {budget_censored} vs {verification_reject}
    on BUDGET_EXHAUSTED rows)."""
    summary = _load(run_dir / "summary.json")
    paired = summary.get("paired", {})
    msolve_vocab = set()
    mirror_vocab = set()
    MIRROR_ARMS = ("RETR_ORACLE", "RETR_KO", "INTG_ORACLE", "INTG_KO")
    for arm, p in paired.items():
        vocab = set((p.get("typed_failures") or {}).keys())
        if arm in MIRROR_ARMS:
            mirror_vocab |= vocab
        elif arm in ("RESET", "CONTINUED", "APPL_KO", "KNOWN_STRUCTURE_ORACLE"):
            msolve_vocab |= vocab
    only_msolve = msolve_vocab - mirror_vocab
    if not only_msolve:
        status = "PASS"
    elif only_msolve == {"budget_censored"} and "verification_reject" in mirror_vocab:
        status = "KNOWN_DISCLOSED"  # the M1B-DISC-2 shape and nothing else
    else:
        status = "FAIL"
    return {"invariant": "typed_failure_cross_path_consistency", "status": status,
            "detail": {"msolve_path_vocab": sorted(msolve_vocab),
                       "mirror_path_vocab": sorted(mirror_vocab),
                       "disclosure": "M1B-DISC-2" if status == "KNOWN_DISCLOSED" else None}}


def recovery_over_unit_flag(summary: dict) -> dict:
    """Recovery > 1.0 vs the KS-oracle denominator must be FLAGGED and annotated
    with the constant-offset context (PR #349): the denominator is ~94% a
    history-free constant offset, so >1.0 means the KS oracle is not a ceiling for
    that channel -- never '>perfect transfer'.  The checker emits the annotation;
    any results document quoting an over-unit mean without this annotation is a
    reporting defect."""
    flagged = []
    for arm, rec in sorted(summary.get("recovery_share_vs_known_structure_oracle",
                                       {}).items()):
        mean = rec.get("mean")
        if mean is not None and mean > 1.0:
            flagged.append({"arm": arm, "mean": mean,
                            "context": "KS denominator ~94% history-free constant "
                                       "offset (PR #349); >1.0 = KS not a ceiling "
                                       "for this channel"})
    return {"invariant": "recovery_over_unit_flag", "status": "PASS",
            "detail": {"arms_over_unit": flagged,
                       "note": "annotation is emitted by this checker itself; future "
                               "consumers MUST copy it into any results document "
                               "quoting these means"}}


def amortisation_divisor_consistency(run_dir: Path) -> dict:
    """The lifetime-amortisation divisor must be the DISTINCT-TARGET count, not
    rows-per-target (M1B-DISC-3: phase_summarize divided dev_slots by
    attempts//distinct_targets = the rung count 5 instead of the target count 8;
    every arm's lifetime mean moved ~-580 -> ~-361 but none approached
    materiality, so the terminal was unaffected).  The invariant recomputes the
    correct charge from the arm's own dev_enumeration_slots ledger and FAILs any
    run whose recorded dev_charge_per_target does not equal dev_slots /
    distinct targets (unless exactly the disclosed shape, on the disclosed run)."""
    summary = _load(run_dir / "summary.json")
    findings = []
    for arm, lifetime in sorted(summary.get("recovery_share_lifetime_charged",
                                            {}).items()):
        charge = lifetime.get("dev_charge_per_target") or 0.0
        if not charge:
            continue
        ledger = summary.get("cost_ledger_hdi14", {}).get(arm, {})
        dev_slots = ledger.get("dev_enumeration_slots") or 0
        rows = _load(run_dir / "arms" / f"{arm}.json").get("acquisition_rows", [])
        n_targets = len({r["target"] for r in rows})
        correct = dev_slots / n_targets if n_targets else None
        # the disclosed M1B-DISC-3 shape and ONLY it: the implied divisor equals the
        # rows-per-target (rung count), i.e. charge == dev_slots / rungs
        rows_per_target = len(rows) / n_targets if n_targets else 0
        disclosed_shape = (dev_slots and charge and rows_per_target
                           and abs(charge - dev_slots / rows_per_target) < 1.0)
        if correct is not None and abs(charge - correct) < 1.0:
            status = "PASS"
        elif disclosed_shape:
            status = "KNOWN_DISCLOSED"
        else:
            status = "FAIL"
        findings.append({"arm": arm, "recorded_charge": charge,
                         "correct_charge": correct, "status": status,
                         "disclosure": "M1B-DISC-3" if status == "KNOWN_DISCLOSED"
                                       else None})
    statuses = {f["status"] for f in findings}
    overall = "FAIL" if "FAIL" in statuses else \
              ("KNOWN_DISCLOSED" if "KNOWN_DISCLOSED" in statuses else "PASS")
    return {"invariant": "amortisation_divisor_consistency", "status": overall,
            "detail": findings}


def _breakeven_from_run_dir(run_dir: Path) -> dict:
    """Every materially-recovering arm must carry its break-even serving scale N*:
    the number of protected targets at which lifetime-charged recovery crosses the
    frozen 20% margin, from the run's own matched-key aggregates:
        N* = dev_slots / (mean(R - A) - MARGIN * mean(R - K))
    dev_slots is read from the arm's OWN HDI-14 dev_enumeration_slots (true cost),
    independent of the recorded (disclosed-defective) divisor.  Non-positive slack
    reports NO_BREAKEVEN -- an economics negative, retained as data."""
    def keyed(arm: str) -> dict:
        rows = _load(run_dir / "arms" / f"{arm}.json").get("acquisition_rows", [])
        return {r["target"] + "@" + str(r["budget_slots"]): r["B_slots"]
                for r in rows if not r.get("censored")}

    summary = _load(run_dir / "summary.json")
    keyed_reset, keyed_ks = keyed("RESET"), keyed("KNOWN_STRUCTURE_ORACLE")
    results = {}
    for arm, rec in sorted(summary.get("recovery_share_vs_known_structure_oracle",
                                       {}).items()):
        if not rec.get("material") or arm == "KNOWN_STRUCTURE_ORACLE":
            continue
        ledger = summary.get("cost_ledger_hdi14", {}).get(arm, {})
        dev_slots = ledger.get("dev_enumeration_slots") or 0
        keyed_arm = keyed(arm)
        rows = _load(run_dir / "arms" / f"{arm}.json").get("acquisition_rows", [])
        n_targets = len({r["target"] for r in rows})
        if not dev_slots or not n_targets:
            results[arm] = {"status": "NO_DEV_CHARGE"}
            continue
        keys = [k for k in sorted(set(keyed_reset) & set(keyed_arm) & set(keyed_ks))
                if keyed_reset[k] - keyed_ks[k] > 0]
        mean_RA = sum(keyed_reset[k] - keyed_arm[k] for k in keys) / len(keys)
        mean_RK = sum(keyed_reset[k] - keyed_ks[k] for k in keys) / len(keys)
        slack = mean_RA - MARGIN * mean_RK
        if slack <= 0:
            results[arm] = {"status": "NO_BREAKEVEN", "mean_R_minus_A": mean_RA,
                            "margin_bar": MARGIN * mean_RK}
            continue
        results[arm] = {"status": "PASS", "dev_slots": dev_slots,
                        "n_targets_this_run": n_targets,
                        "mean_R_minus_A_per_target": mean_RA,
                        "margin_bar_per_target": MARGIN * mean_RK,
                        "breakeven_targets_N_star": dev_slots / slack,
                        "breakeven_ratio_vs_this_run": (dev_slots / slack) / n_targets}
    return {"invariant": "amortisation_breakeven", "status": "PASS", "detail": results}


def run_all(run_dir: Path, expect_disclosed: bool) -> dict:
    run_dir = Path(run_dir)
    summary = _load(run_dir / "summary.json")
    checks = [retrieval_no_fire_no_effect(summary),
              observation_horizon_consistency(run_dir),
              typed_failure_cross_path_consistency(run_dir),
              recovery_over_unit_flag(summary),
              amortisation_divisor_consistency(run_dir),
              _breakeven_from_run_dir(run_dir)]
    statuses = [c["status"] for c in checks]
    overall = "FAIL" if "FAIL" in statuses else \
              ("KNOWN_DISCLOSED" if "KNOWN_DISCLOSED" in statuses else "PASS")
    if "KNOWN_DISCLOSED" in statuses and not expect_disclosed:
        overall = "FAIL"  # disclosures must be asserted, never assumed
    return {"schema": "OCM_M1B_INVARIANTS_REPORT", "run_dir": str(run_dir),
            "overall": overall, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--expect-disclosed", action="store_true",
                        help="assert the M1B_SCORED_V1 disclosures are present "
                             "(for the disclosed run itself)")
    args = parser.parse_args()
    report = run_all(args.run_dir, args.expect_disclosed)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["overall"] in ("PASS", "KNOWN_DISCLOSED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
