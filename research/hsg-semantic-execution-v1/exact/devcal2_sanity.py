#!/usr/bin/env python3
"""DEV-CAL-2 sanity assay + checker (#323; DEV_CAL_2_KNOCKOUT_PROTOCOL_FREEZE_V1
checker_requirements 0-6, terminals.ASSAY_DEFECT).

--selftest (sub-second, tiny synthetic fixtures + two real worlds; NO world
sweep, NO scored run) validates every checker the freeze demands, each with a
CLEAN no-alarm case AND a PLANTED HOSTILE that must trip:
  class 10 adapter verifier   clean KO arm records pass; PLANTED (a) a record
                              granting REPRESENTATION+RETRIEVAL under the
                              KO-1 arm fails closed (component error, and the
                              stale-digest variant trips the drift error)
  class 11 anchor reproduction committed DEVCAL1 CIs reproduce (overlap>0);
                              PLANTED (b) a re-run mean drifted 3x CI-width
                              beyond the committed CI -> defect
  class 12 per-arm controls   clean fixture: A fires, C/D silent; PLANTED (c)
                              a cell-D reduction >= threshold -> ALARM defect
  class 13 purity re-check    hostile_and_clean_controls fire/stay silent
  class 14 cost completeness  all HDI-14 families + adapter digest bound;
                              planted missing-family row -> defect
  class 15 null/draw-inv.     shuffle-equal-n null silent (signflip on the
                              SHUFFLED control, DC1 construction) + per-seed
                              direction agrees; planted recovering SHUFFLED
                              -> null ALARM
  class 16 live serve path    run_ko_arm on build_cell("B",0)/("D",0):
                              KO-1 key silent in B, KO-2 matches + recovers,
                              KO-4 serve identical to KO-3 (accounting only),
                              LOO_MINUS_REPRESENTATION degrades recorded,
                              D stays key-silent, bit-identical re-run
Exit codes: 0 PASS (all clean silent AND all hostiles tripped); 10..16 the
class that failed to behave; 20+k a planted hostile FAILED TO TRIP (a checker
that cannot fail is worthless); 2 usage; --report reads the scored run.
"""
from __future__ import annotations

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

EXIT_BY_CLASS = {
    "adapter": 10, "anchor": 11, "controls": 12, "purity": 13,
    "ledger": 14, "null": 15, "serve": 16,
}


def _fail(clazz, msg):
    print("SANITY FAIL [%s]: %s" % (clazz, msg))
    return EXIT_BY_CLASS[clazz]


def _hostile_failed_to_trip(clazz, msg):
    print("SANITY FAIL [hostile-%s]: %s" % (clazz, msg))
    return 20 + EXIT_BY_CLASS[clazz]


def _ok(msg):
    print("  ok:", msg)


# ------------------------------------------------------ synthetic fixtures ----
def _row(arm, cell, wid, seed, work, adapter_sha=None, total=None,
         drop_family=None, anchor=False):
    ledger = {"acquisition": 50 if adapter_sha else 0,
              "storage_bytes": 120, "retrieval": 7, "rejected_candidates": 3,
              "verification": 5, "adaptation": 10}
    if drop_family:
        ledger.pop(drop_family)
    row = {"status": "OK", "arm": arm, "cell": cell,
           "world_id": "%s-%02d" % (cell, wid), "seed": seed,
           "m_star_in_history": False,
           "recorded_before_solution_discovery": {
               "work_to_first_verified_success": work},
           "total_burden_incl_acquisition": total if total is not None
           else work + ledger["acquisition"],
           "cost_ledger": ledger}
    if adapter_sha:
        row["adapter"] = {"adapter_sha256": adapter_sha}
    if anchor:
        row["run_role"] = "ANCHOR_RERUN"   # as the shard writer tags them
    return row


def clean_fixture_rows():
    """Deterministic tiny fixture: 6 worlds x 3 seeds x 4 cells; anchors +
    one KO arm.  A fires (~97% reduction), B recovers (~96%), C/D silent,
    SHUFFLED == RESET (null silent), per-seed direction agrees."""
    import exact.devcal2_adapters as A
    ko2 = A.make_adapter("KO-2_PLUS_RETRIEVAL")["adapter_sha256"]
    rows = []
    for wid in range(6):
        for seed in (0, 1, 2):
            base = 1000 + 10 * seed + wid
            rows.append(_row("RESET", "B", wid, seed, base, anchor=True))
            rows.append(_row("ORACLE_HISTORY", "B", wid, seed, 30 + seed,
                             total=30 + seed + 50, anchor=True))
            off = 4 if (wid + seed) % 2 == 0 else -4  # symmetric overhead:
            # the shuffle-equal-n null arm must be mean-zero vs RESET (a
            # constant offset is exactly what the signflip null detects)
            rows.append(_row("SHUFFLED_HISTORY", "B", wid, seed, base + off,
                             total=base + off + 50, anchor=True))
            rows.append(_row("KO-2_PLUS_RETRIEVAL", "B", wid, seed,
                             40 + seed, adapter_sha=ko2,
                             total=40 + seed + 50))
            rows.append(_row("RESET", "A", wid, seed, base, anchor=True))
            rows.append(_row("KO-2_PLUS_RETRIEVAL", "A", wid, seed,
                             25 + seed, adapter_sha=ko2,
                             total=25 + seed + 50))
            rows.append(_row("RESET", "C", wid, seed, base, anchor=True))
            rows.append(_row("KO-2_PLUS_RETRIEVAL", "C", wid, seed,
                             base + 10 + seed, adapter_sha=ko2,
                             total=base + 10 + seed + 50))
            rows.append(_row("RESET", "D", wid, seed, base, anchor=True))
            rows.append(_row("KO-2_PLUS_RETRIEVAL", "D", wid, seed,
                             base + 5 + seed, adapter_sha=ko2,
                             total=base + 5 + seed + 50))
    return rows


# ------------------------------------------------------------ check sections --
def check_adapter():
    import exact.devcal2_adapters as A
    for arm in A.ALL_KO_ARMS:
        ok, errs = A.verify_adapter(A.make_adapter(arm))
        if not ok:
            return _fail("adapter", "clean %s rejected: %s" % (arm, errs))
    ok, errs = A.verify_adapter_suite([A.make_adapter(a) for a in A.LADDER],
                                      list(A.LADDER))
    if not ok:
        return _fail("adapter", "clean ladder suite rejected: %s" % errs)
    _ok("clean adapter records + suite verify (%d arms)" % len(A.ALL_KO_ARMS))
    # PLANTED HOSTILE (a): REPRESENTATION+RETRIEVAL granted under KO-1
    hostile = A.make_adapter("KO-1_REPRESENTATION")
    hostile["components_granted"] = ["REPRESENTATION", "RETRIEVAL_KEYING"]
    hostile["adapter_sha256"] = A.adapter_digest(hostile)  # digest RE-BOUND:
    # the defect must be caught by the COMPONENT check, not digest drift
    ok, errs = A.verify_adapter(hostile)
    comp_errs = [e for e in errs if "components_granted" in e]
    if ok or not comp_errs:
        return _hostile_failed_to_trip(
            "adapter", "multi-component KO-1 record accepted (%s)" % errs)
    _ok("hostile (a) multi-component KO-1 trips: %d component error(s)"
        % len(comp_errs))
    stale = A.make_adapter("KO-1_REPRESENTATION")
    stale["components_granted"] = ["REPRESENTATION", "TRANSPORT_MAP"]
    ok, errs = A.verify_adapter(stale)  # digest NOT rebound -> drift path
    if ok or not any("drift" in e for e in errs):
        return _hostile_failed_to_trip(
            "adapter", "post-hoc edited record not caught as drift (%s)"
            % errs)
    _ok("hostile (a') post-hoc edit trips the sha256-drift check")
    return 0


def check_anchor():
    import exact.run_devcal2 as R2
    with open(os.path.join(RESULTS, "DEVCAL1_RESULTS.json"),
              encoding="utf-8") as f:
        committed = json.load(f)
    rerun = {cell: {k: committed["per_cell"][cell][k] for k in
                    ("oracle_vs_reset_reduction", "shuffled_vs_reset_reduction")}
             for cell in ("A", "B", "C", "D")}
    defects = R2.anchor_reproduction(committed, rerun, "clean")
    if defects:
        return _fail("anchor", "committed-vs-committed flagged: %s" % defects)
    _ok("clean anchor reproduction: 0 defects over %d comparisons"
        % (4 * 2))
    hostile = copy.deepcopy(rerun)
    b_ci = committed["per_cell"]["B"]["oracle_vs_reset_reduction"]["ci"]
    shift = 3 * (b_ci[1] - b_ci[0])  # drift 3x the committed CI width
    hostile["B"]["oracle_vs_reset_reduction"] = {
        "mean": committed["per_cell"]["B"]["oracle_vs_reset_reduction"]
        ["mean"] + shift,
        "ci": [b_ci[0] + shift, b_ci[1] + shift]}
    defects = R2.anchor_reproduction(committed, hostile, "drift")
    if len(defects) < 1 or "B ORACLE anchor drift" not in defects[0]:
        return _hostile_failed_to_trip(
            "anchor", "3x-CI-width drift not flagged (%s)" % defects)
    _ok("hostile (b) anchor drift trips: %d defect(s), e.g. %r"
        % (len(defects), defects[0][:60]))
    return 0


def check_controls():
    import exact.run_devcal2 as R2
    rows = clean_fixture_rows()
    arm = "KO-2_PLUS_RETRIEVAL"
    defects = R2.arm_control_defects(rows, arm)
    if defects:
        return _fail("controls", "clean fixture alarmed: %s" % defects)
    a = R2.reduction_stats(rows, "A", arm)
    if not (a["threshold_met"] and a["burden_cis_nonoverlapping"]):
        return _fail("controls", "cell-A positive control silent on fixture")
    _ok("clean controls: A fires (mean=%.3f), C and D silent" % a["mean"])
    hostile = [r for r in rows if not (r["cell"] == "D" and r["arm"] == arm)]
    for wid in range(6):
        for seed in (0, 1, 2):
            hostile.append(_row(arm, "D", wid, seed, 40 + seed,
                                adapter_sha="x" * 64, total=90 + seed))
    defects = R2.arm_control_defects(hostile, arm)
    alarm = [d for d in defects if "cell-D control ALARMED" in d]
    if not alarm:
        return _hostile_failed_to_trip(
            "controls", "planted cell-D recovery not flagged (%s)" % defects)
    _ok("hostile (c) cell-D alarm trips: %d defect(s)" % len(alarm))
    return 0


def check_purity():
    import exact.devcal1_certificates as C
    receipts = C.hostile_and_clean_controls()
    n_fire = n_silent = 0
    for name, ctl in receipts.items():
        key = "fired" if "fired" in ctl else "silent"
        if not ctl[key]:
            return _fail("purity", "checker control %s failed to %s"
                         % (name, key))
        n_fire += key == "fired"
        n_silent += key == "silent"
    _ok("purity/checker controls: %d fire, %d silent (unchanged DC1 checkers)"
        % (n_fire, n_silent))
    return 0


def check_ledger():
    import exact.run_devcal2 as R2
    rows = clean_fixture_rows()
    defects = R2.ledger_defects(rows)
    if defects:
        return _fail("ledger", "complete ledgers flagged: %s" % defects[:2])
    _ok("clean cost completeness: %d rows, all HDI-14 families + adapter "
        "digest bound" % len(rows))
    hostile = rows[:-1] + [_row("KO-2_PLUS_RETRIEVAL", "B", 0, 0, 40,
                                adapter_sha="y" * 64, drop_family="retrieval")]
    defects = R2.ledger_defects(hostile)
    if not any("retrieval" in d for d in defects):
        return _hostile_failed_to_trip(
            "ledger", "missing retrieval family not flagged (%s)" % defects)
    bare = rows + [_row("KO-2_PLUS_RETRIEVAL", "B", 1, 1, 41)]
    defects = R2.ledger_defects(bare)
    if not any("adapter digest" in d for d in defects):
        return _hostile_failed_to_trip(
            "ledger", "KO row without adapter digest not flagged")
    _ok("hostile (d) missing-family + unbound-adapter rows trip (%d defects)"
        % len(defects))
    return 0


def check_null():
    import exact.run_devcal2 as R2
    rows = clean_fixture_rows()
    arm = "KO-2_PLUS_RETRIEVAL"
    null = R2.shuffle_null(rows, "B")
    nshare = R2.null_arm_share(rows, "B")
    if not null["non_alarm"]:
        return _fail("null", "clean shuffle-equal-n null alarmed (p=%.3f)"
                     % null["p_signflip"])
    if not nshare["non_alarm"]:
        return _fail("null", "clean SHUFFLED anchor showed material recovery")
    di = R2.draw_invariance(rows, "B", arm)
    if not di["direction_agrees"]:
        return _fail("null", "clean fixture failed draw-invariance")
    rec = R2.recovery_share_stats(rows, "B", arm)
    if not rec["threshold_met"]:
        return _fail("null", "clean recovering arm not detected (mean=%.3f)"
                     % (rec["mean"] or float("nan")))
    _ok("clean null silent (p=%.2f), null-arm share %.3f, draw-invariant, "
        "recovery detected (mean=%.3f)" % (null["p_signflip"],
                                           nshare["mean"], rec["mean"]))
    hostile = [r for r in rows
               if not (r["arm"] == "SHUFFLED_HISTORY" and r["cell"] == "B")]
    for wid in range(6):          # PLANTED: the SHUFFLED arm itself recovers
        for seed in (0, 1, 2):
            hostile.append(_row("SHUFFLED_HISTORY", "B", wid, seed,
                                40 + seed, total=40 + seed + 50))
    if R2.null_arm_share(hostile, "B")["non_alarm"]:
        return _hostile_failed_to_trip(
            "null", "recovering SHUFFLED anchor not flagged")
    _ok("hostile (e) recovering shuffle-equal-n arm trips the null")
    return 0


def check_serve():
    """Live serve path on two REAL worlds (no scored run; 6 receipts)."""
    import exact.devcal1_worlds as W
    import exact.devcal1_search as S
    import exact.devcal2_adapters as A
    import exact.run_devcal2 as R2
    worlds = W.all_worlds()
    cert_rows = [R2.C_check_structural(w) for w in worlds]
    by_cd = {}
    for w, rel in zip(worlds, cert_rows):
        by_cd["%s-%02d" % (w["cell"], w["world_index"])] = (w, rel)

    def run(arm, wid, seed=0):
        w, rel = by_cd[wid]
        ctx = R2.world_context(w, cert_rows)
        acq = S.source_acquisition_cost(w, 0)["work"]
        rec = R2.run_ko_arm(A.make_adapter(arm), w, seed, acq, ctx)
        if rec.get("status") != "OK":
            raise SystemExit("serve-path row %s/%s failed: %s"
                             % (arm, wid, rec.get("status")))
        return rec

    k1 = run("KO-1_REPRESENTATION", "B-00")
    if k1["adapter"]["retrieval_key_match"]:
        return _fail("serve", "KO-1 surface key MATCHED in reminted cell B")
    k2 = run("KO-2_PLUS_RETRIEVAL", "B-00")
    if not k2["adapter"]["retrieval_key_match"]:
        return _fail("serve", "KO-2 certificate key failed to match in B")
    if not (k2["recorded_before_solution_discovery"]
            ["work_to_first_verified_success"]
            < k1["recorded_before_solution_discovery"]
            ["work_to_first_verified_success"]):
        return _fail("serve", "KO-2 does not recover vs silent KO-1 in B")
    k3 = run("KO-3_PLUS_TRANSPORT", "B-00")
    k4 = run("KO-4_PLUS_CHARGING", "B-00")
    w3 = k3["recorded_before_solution_discovery"]
    ["work_to_first_verified_success"]
    w4 = k4["recorded_before_solution_discovery"]
    ["work_to_first_verified_success"]
    if w3 != w4:
        return _fail("serve", "KO-4 serve path differs from KO-3 (%s vs %s)"
                     % (w3, w4))
    if not k4["adapter"]["charge_rule_applied"].startswith(
            "CERT_FAMILY_AMORTISATION"):
        return _fail("serve", "KO-4 charge rule not amortised")
    if k4["cost_ledger"]["acquisition"] > k2["cost_ledger"]["acquisition"]:
        return _fail("serve", "amortised acquisition exceeds raw acquisition")
    loo = run("LOO_MINUS_REPRESENTATION", "B-00")
    if not loo["adapter"]["component_degradations"]:
        return _fail("serve", "LOO_MINUS_REPRESENTATION degraded silently")
    if loo["adapter"]["keying_rule_applied"] != "SURFACE_SIGNATURE_V1":
        return _fail("serve", "degraded keying did not fall back to surface")
    d = run("KO-2_PLUS_RETRIEVAL", "D-00")
    if d["adapter"]["retrieval_key_match"]:
        return _fail("serve", "KO-2 key MATCHED in latent_different cell D")
    r1 = run("KO-2_PLUS_RETRIEVAL", "B-00", seed=1)
    r2 = run("KO-2_PLUS_RETRIEVAL", "B-00", seed=1)
    if (r1["m_star_digest"], r1["recorded_before_solution_discovery"]
            ["work_to_first_verified_success"]) != (
            r2["m_star_digest"], r2["recorded_before_solution_discovery"]
            ["work_to_first_verified_success"]):
        return _fail("serve", "serve path not deterministic under fixed seed")
    _ok("live serve path: 9 real receipts; KO-1 silent/KO-2 recovers in B, "
        "KO-4==KO-3 serve, LOO degradations recorded, D key-silent, "
        "bit-deterministic")
    return 0


CHECKS = (("adapter", check_adapter), ("anchor", check_anchor),
          ("controls", check_controls), ("purity", check_purity),
          ("ledger", check_ledger), ("null", check_null),
          ("serve", check_serve))

REQ_MAP = (
    "checker_requirements enforcement map: "
    "[0] single-component verifier -> devcal2_adapters.verify_adapter (class "
    "10); [1] adapter sha256 binding -> adapter_digest + ledger_defects "
    "(classes 10/14); [2] anchor reproduction -> run_devcal2."
    "anchor_reproduction vs committed DEVCAL1_RESULTS (class 11); [3] "
    "fail-closed structural checker unchanged -> shard digest check vs "
    "committed freeze table + class 13 controls; [4] purity checker unchanged "
    "-> class 13 (hostile_and_clean_controls, both directions); [5] cost "
    "completeness incl. adapter storage -> ledger_defects (class 14); [6] "
    "shuffle null + draw-invariance + per-arm controls -> classes 12/15."
)


def report():
    path = os.path.join(RESULTS, "DEVCAL2_RESULTS.json")
    if not os.path.exists(path):
        print("no DEVCAL2_RESULTS.json (scored run not merged yet)")
        return 3
    with open(path, encoding="utf-8") as f:
        res = json.load(f)
    print("DEV-CAL-2 terminal:", res["terminal"])
    for arm, s in sorted(res.get("per_arm", {}).items()):
        p = s["recovery_share_cell_B"]
        print("  %-24s share=%.4f ci=%s met=%s"
              % (arm, p["mean"] or float("nan"), p["ci"], p["threshold_met"]))
    for d in res.get("terminal_defects", [])[:20]:
        print("  defect:", d)
    return 0 if res["terminal"] != "ASSAY_DEFECT" else 4


def main():
    if len(sys.argv) < 2:
        print("usage: devcal2_sanity.py --selftest | --report",
              file=sys.stderr)
        return 2
    if sys.argv[1] == "--report":
        return report()
    if sys.argv[1] != "--selftest":
        print("unknown mode %r" % sys.argv[1], file=sys.stderr)
        return 2
    import time
    t0 = time.time()
    failed = 0
    for name, fn in CHECKS:
        rc = fn()
        if rc:
            print("class %s FAILED (exit %d)" % (name, rc))
            failed = rc
            break
    print(REQ_MAP)
    print("selftest %s in %.1fs (exit %d)"
          % ("PASS" if not failed else "FAIL", time.time() - t0,
             failed or 0))
    return failed or 0


if __name__ == "__main__":
    sys.exit(main())
