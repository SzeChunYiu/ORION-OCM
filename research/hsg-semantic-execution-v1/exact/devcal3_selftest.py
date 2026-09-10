#!/usr/bin/env python3
"""DEV-CAL-3 hostile selftest (freeze entry gate 3: must pass on the run
host BEFORE any recomputation is reported).

Six hostiles, fixtures derived from the REAL sealed V2 receipts wherever
feasible (one cell-B world, all 11 arms, seed 0 -- 11 real rows replayed
through the unchanged machinery; plus a real-slice copy of every sealed
input for the binding hostiles):

  a  planted AS_IS drift           a drifted scored number must fire
                                   ASSAY_DEFECT naming the drifted field;
                                   a last-bit (1e-14 relative) drift binds
                                   within the registered tolerance and a
                                   1e-6 relative drift still fires
  b  no-alarm pristine control     untampered inputs bind ALL_MATCH; the
                                   staged pipeline (replay -> acquisition
                                   checks -> 5 semantics totals ->
                                   event preservation -> direction ->
                                   evaluate_semantics) runs with ZERO
                                   violations on the real slice
  c  wrong sha256                  a tampered shard copy AND a tampered
                                   results-file copy must each raise
                                   RECEIPT_BINDING_DEFECT; a silently
                                   ungated score-bearing input is itself a
                                   binding defect (fail-closed gate check)
  d  event preservation            every semantics preserves the event
                                   multiset on the real slice; a planted
                                   digest change, a planted event drop and
                                   a planted task-set drop each trip
  e  direction sanity              every authorised reform leaves every
                                   row's total burden <= its AS_IS total on
                                   the real slice; a planted charge-adding
                                   reform trips
  f  terminal decision             decide_terminal covers NONE / single
                                   carrier / MULTIPLE; holm reproduces the
                                   exact step-down adjusted p-values; the
                                   one-sided signflip p is deterministic
                                   and directionally sane

Usage:  python3 -m exact.devcal3_selftest
Exit 0 all hostiles behave as planted; 1 any hostile failed.
Sub-second-class by design (real-slice fixtures, never the full ledger).
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))

import exact.devcal3_charging_attribution as M
import exact.devcal2_adapters as A

FIXTURE_WORLD = "B-07"
FIXTURE_SEED = 0


# ------------------------------------------------------------- fixtures -------
def _fixture_rows():
    rows = M.load_shard_rows()
    arms = list(A.ALL_KO_ARMS) + ["ORACLE_HISTORY", "RESET",
                                  "SHUFFLED_HISTORY"]
    want = {(arm, FIXTURE_WORLD, FIXTURE_SEED) for arm in arms}
    sel = [r for r in rows if (r.get("arm"), r.get("world_id"),
                               r.get("seed")) in want
           and r.get("status") == "OK"]
    return rows, sel


def _fixture_data_dir():
    """Flat copy of every sealed input bind_inputs reads (tamperable)."""
    d = tempfile.mkdtemp(prefix="dc3_selftest_")
    srcs = [M.SCORED_V2, M.SCORED_V1, M.RESULTS_V2, M.HOST_RECEIPT_V2] + \
        list(M.SHARD_V2)
    for p in srcs:
        shutil.copyfile(p, os.path.join(d, os.path.basename(p)))
    return d


def _mini_arm():
    """One structurally complete per-arm readout block (KO-2 tier)."""
    def seed_block(mean, lo, hi):
        return {"mean": mean, "ci": [lo, hi], "n_pairs": 90,
                "threshold_met": True}
    return {
        "recovery_share_cell_B": seed_block(1.0, 1.0, 1.0),
        "recovery_share_cell_B_total_burden": seed_block(0.9991, 0.9776,
                                                         1.0205),
        "shuffle_null_cell_B": {"non_alarm": True, "p_signflip": 0.7944},
        "shuffle_null_cell_B_total_burden": {"non_alarm": False,
                                             "p_signflip": 0.0},
        "draw_invariance_cell_B": {
            "classification": "AGREE_DETERMINATE", "direction_agrees": True,
            "n_determinate": 3,
            "per_seed": {s: {"mean_reduction": 0.97, "null_band_95": 0.32,
                             "determinate": True} for s in ("0", "1", "2")}},
        "controls": {"A_fired": True, "C_silent": True, "D_silent": True},
        "purity": {"n": 360, "n_pure": 360, "n_impure": 0,
                   "n_cannot_check": 0},
        "adapter_sha256": "x" * 64,
    }


def _mini_scored(per_arm):
    return {"per_arm": per_arm,
            "ladder_state": {"KO-2_PLUS_RETRIEVAL": {"primary": True,
                                                     "secondary": False}},
            "verdict": "AMORTISATION_DOMINATED"}


# ------------------------------------------------------------- hostiles ------
def hostile_a_planted_as_is_drift():
    arm = "KO-2_PLUS_RETRIEVAL"
    per_arm = {arm: _mini_arm()}
    ladder = {"KO-2_PLUS_RETRIEVAL": {"primary": True, "secondary": False}}
    verdict = "AMORTISATION_DOMINATED"

    # pristine: zero defects, everything exact (no tolerance, no absence)
    defects, stats = M.compare_as_is(per_arm, ladder, verdict,
                                     _mini_scored(copy.deepcopy(per_arm)))
    assert defects == [], defects
    assert stats["fields_exact"] == stats["fields_compared"], stats
    assert not stats["fields_within_float_tolerance"], stats

    # macro drift (+0.5 on the primary mean): must fire and NAME the field
    drifted = copy.deepcopy(per_arm)
    drifted[arm]["recovery_share_cell_B"]["mean"] += 0.5
    defects, _ = M.compare_as_is(per_arm, ladder, verdict,
                                 _mini_scored(drifted))
    assert defects and "KO-2_PLUS_RETRIEVAL.recovery_share_cell_B.mean" \
        in defects[0], defects[:2]

    # last-bit drift (1e-14 relative): binds within the registered
    # tolerance and is NAMED, never silent
    ulp = copy.deepcopy(per_arm)
    ulp[arm]["recovery_share_cell_B"]["mean"] *= (1.0 + 1e-14)
    defects, stats = M.compare_as_is(per_arm, ladder, verdict,
                                     _mini_scored(ulp))
    assert defects == [], defects
    assert stats["fields_within_float_tolerance"] == \
        ["KO-2_PLUS_RETRIEVAL.recovery_share_cell_B.mean"], stats

    # beyond-tolerance drift (1e-6 relative): must still fire
    micro = copy.deepcopy(per_arm)
    micro[arm]["recovery_share_cell_B"]["mean"] *= (1.0 + 1e-6)
    defects, _ = M.compare_as_is(per_arm, ladder, verdict,
                                 _mini_scored(micro))
    assert defects, "1e-6 relative drift escaped the AS_IS gate"
    return "planted drift fires (macro + 1e-6); 1e-14 binds named"


def hostile_b_no_alarm_pristine(tmp_rows, sel_rows, worlds, ctx, adapters,
                                raw_acq):
    # (1) untampered input copy: every gate matches, zero binding defects
    d = _fixture_data_dir()
    try:
        bindings, docs, expected = M.bind_inputs(d)
        assert len(bindings) == 9, len(bindings)
        gated = sum(1 for base in expected
                    if base in {os.path.basename(b) for b in bindings})
        assert gated >= 5, "score-bearing inputs not gated: %s" % \
            sorted(expected)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # (2) staged pipeline on the REAL slice: replay exact, acquisition
    # rules exact, all five semantics event-preserving, direction sane,
    # evaluate_semantics completes
    decomp = M.decompose_rows(tmp_rows, worlds, ctx, adapters, raw_acq,
                              keys={(k["arm"], k["world_id"], k["seed"])
                                    for k in sel_rows})
    assert len(decomp) == 11, len(decomp)
    assert not M.acquisition_charge_checks(decomp, ctx)
    asis = M.semantics_totals(decomp, "AS_IS", raw_acq)
    for sem in M.SEMANTICS_ARMS:
        tot = M.semantics_totals(decomp, sem, raw_acq, mco_n=10,
                                 r_failed=0.0)
        assert M.event_preservation(decomp, tot) == [], sem
        assert M.direction_sanity(asis, tot, sem) == [], sem
    ev = M.evaluate_semantics(sel_rows, asis)
    assert "ko2_primary_intact" in ev and "p_one_sided" in ev
    return "11/11 real rows replay exact; 5 semantics clean; pipeline runs"


def hostile_c_wrong_sha256():
    # tampered shard: hash changes -> RECEIPT_BINDING_DEFECT
    d = _fixture_data_dir()
    try:
        with open(os.path.join(d, "DEVCAL2_receipts_shard1_V2.jsonl"),
                  "a") as f:
            f.write("\n")
        try:
            M.bind_inputs(d)
            raise AssertionError("tampered shard was NOT detected")
        except M.BindingDefect as e:
            assert "shard1" in str(e), e
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # tampered results file (bound by BOTH committed sources): defect
    d = _fixture_data_dir()
    try:
        p = os.path.join(d, "DEVCAL2_RESULTS_V2.json")
        doc = json.load(open(p))
        doc["tampered"] = True
        with open(p, "w") as f:
            json.dump(doc, f)
        try:
            M.bind_inputs(d)
            raise AssertionError("tampered results file was NOT detected")
        except M.BindingDefect as e:
            assert "DEVCAL2_RESULTS_V2" in str(e), e
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # fail-closed gate check: a digest source that stops binding a
    # score-bearing input is ITSELF a defect (no silent ungating)
    d = _fixture_data_dir()
    try:
        p = os.path.join(d, "DEVCAL2_HOST_RECEIPT_billy_V2.json")
        host = json.load(open(p))
        host["output_bindings"] = {
            k: v for k, v in host["output_bindings"].items()
            if k != "DEVCAL2_RESULTS_V2.json"}
        with open(p, "w") as f:
            json.dump(host, f)
        # host no longer gates the results file and its own sha changed --
        # the scored source still gates it; the file itself is intact, so
        # the only defect class available is the fail-closed ungating guard
        try:
            M.bind_inputs(d)
            raise AssertionError("ungated score-bearing input NOT detected")
        except M.BindingDefect as e:
            assert "failed to gate" in str(e), e
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return "tampered shard / tampered results / silent ungating all trip"


def hostile_d_event_preservation(tmp_rows, worlds, ctx, adapters, raw_acq,
                                 sel_rows):
    keys = {(k["arm"], k["world_id"], k["seed"]) for k in sel_rows}
    decomp = M.decompose_rows(tmp_rows, worlds, ctx, adapters, raw_acq,
                              keys=keys)
    tot = M.semantics_totals(decomp, "NO_FAILURE_CHARGE", raw_acq)
    k0 = sorted(tot)[0]

    # planted identity-digest change
    bad = copy.deepcopy(tot)
    bad[k0]["event_digest"] = "0" * 64
    viol = M.event_preservation(decomp, bad)
    assert viol and "identity digest changed" in viol[0], viol

    # planted event drop (leakage rule: no event may be dropped)
    short = {k: copy.deepcopy(v) for k, v in decomp.items()}
    short[k0]["events"] = short[k0]["events"][:-1]
    viol = M.event_preservation(short, tot)
    assert any("event count" in v for v in viol), viol

    # planted task-set drop (a row removed under the reform)
    dropped = {k: v for k, v in tot.items() if k != k0}
    viol = M.event_preservation(decomp, dropped)
    assert viol and "task-set mismatch" in viol[0], viol
    return "digest change / event drop / task-set drop all trip"


def hostile_e_direction_sanity(tmp_rows, worlds, ctx, adapters, raw_acq,
                               sel_rows):
    keys = {(k["arm"], k["world_id"], k["seed"]) for k in sel_rows}
    decomp = M.decompose_rows(tmp_rows, worlds, ctx, adapters, raw_acq,
                              keys=keys)
    asis = M.semantics_totals(decomp, "AS_IS", raw_acq)
    for sem in M.SEMANTICS_ARMS:
        tot = M.semantics_totals(decomp, sem, raw_acq, mco_n=25,
                                 r_failed=0.3)
        viol = M.direction_sanity(asis, tot, sem)
        assert viol == [], (sem, viol[:3])

    # planted charge-adding reform (+100 on one row's total)
    bad = copy.deepcopy(asis)
    k0 = sorted(bad)[0]
    bad[k0]["total"] += 100
    viol = M.direction_sanity(asis, bad, "PLANTED")
    assert viol and "PLANTED" in viol[0], viol
    return "all reforms <= AS_IS on real slice; charge-adding reform trips"


def hostile_f_terminal_decision():
    none_flips = {sem: False for sem in M.SEMANTICS_ARMS}
    t, c = M.decide_terminal(none_flips)
    assert t == "CHARGE_CARRIER_NONE" and c == [], (t, c)

    single = dict(none_flips, NO_MINING_CHARGE=True)
    t, c = M.decide_terminal(single)
    assert t == "CHARGE_CARRIER_MINING" and c == ["NO_MINING_CHARGE"], (t, c)

    multi = dict(none_flips, NO_FAILURE_CHARGE=True, SALVAGE_MODEL=True)
    t, c = M.decide_terminal(multi)
    assert t == "CHARGE_CARRIER_MULTIPLE" and sorted(c) == \
        ["NO_FAILURE_CHARGE", "SALVAGE_MODEL"], (t, c)

    # holm step-down, hand-checked: p a=0.01 c=0.03 b=0.04, m=3 ->
    # adj a=0.03 (reject), c=0.06, b=0.06 (no reject)
    adj, rej = M.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert abs(adj["a"] - 0.03) < 1e-12 and abs(adj["c"] - 0.06) < 1e-12 \
        and abs(adj["b"] - 0.06) < 1e-12, adj
    assert rej == {"a": True, "b": False, "c": False}, rej

    # one-sided signflip: deterministic + directionally sane
    strong = [0.9 + 0.01 * i for i in range(20)]
    noise = [0.0] * 20
    p1 = M.one_sided_signflip_p(strong, "selftest")
    p2 = M.one_sided_signflip_p(strong, "selftest")
    pn = M.one_sided_signflip_p(noise, "selftest")
    assert p1 == p2, (p1, p2)
    assert p1 is not None and p1 <= 1.0 / M.PERM_N, p1
    assert pn is not None and 0.2 <= pn <= 1.0, pn
    return "NONE/single/MULTIPLE + holm exact + signflip deterministic"


# ---------------------------------------------------------------- driver ------
def main():
    t0 = time.time()
    rows, sel = _fixture_rows()
    worlds, ctx = M._world_cache()
    adapters = {a: A.make_adapter(a) for a in A.ALL_KO_ARMS}
    raw_acq = M.raw_acquisition_by_world(rows)
    shared = (rows, sel, worlds, ctx, adapters, raw_acq)

    hostiles = [
        ("a_planted_as_is_drift", lambda: hostile_a_planted_as_is_drift()),
        ("b_no_alarm_pristine",
         lambda: hostile_b_no_alarm_pristine(rows, sel, worlds, ctx,
                                             adapters, raw_acq)),
        ("c_wrong_sha256", lambda: hostile_c_wrong_sha256()),
        ("d_event_preservation",
         lambda: hostile_d_event_preservation(rows, worlds, ctx, adapters,
                                              raw_acq, sel)),
        ("e_direction_sanity",
         lambda: hostile_e_direction_sanity(rows, worlds, ctx, adapters,
                                            raw_acq, sel)),
        ("f_terminal_decision", lambda: hostile_f_terminal_decision()),
    ]
    failed = []
    for name, fn in hostiles:
        try:
            note = fn()
            print("PASS %-26s %s" % (name, note))
        except Exception as e:                     # hostile misbehaved
            failed.append(name)
            print("FAIL %-26s %s: %s" % (name, type(e).__name__, e))
    wall = time.time() - t0
    print("devcal3 selftest: %d/%d hostiles correct, %.2fs" %
          (len(hostiles) - len(failed), len(hostiles), wall))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
