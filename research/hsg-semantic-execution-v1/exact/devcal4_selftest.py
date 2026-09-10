#!/usr/bin/env python3
"""DEV-CAL-4 hostile selftest (freeze entry gate 3: must pass on the run
host BEFORE any recomputation is reported or any real receipt touched).

Six hostiles, planted-defect alarm AND no-alarm control BOTH asserted:

  a  N derivation        pristine real sealed rows -> N=30 uniform (120
                         worlds, U distribution {'30': 120}); one planted
                         use-row drop moves the min to 29 and names exactly
                         that world; RESET-only and empty row sets fire the
                         registered CANNOT_CHECK guards (never a silent zero)
  b  frozen-N gate       exact match silent; planted mismatch (tampered
                         freeze copy carrying n_frozen=29 vs re-derived 30)
                         halts naming BOTH numbers -- no hardcoded N
                         anywhere; a freeze with n_frozen null / string /
                         float / bool / 0 is itself a RECEIPT_BINDING_DEFECT
  c  N=10 block control  pristine recomputed block binds the recorded copy
                         exactly (zero diffs); planted drift in a secondary
                         field, a scalar (p_one_sided), a WORK field (adapter
                         digest) and a contradicting recorded flip_pre_holm
                         each fire AND name the field; a last-bit (1e-14
                         relative) drift binds within the registered
                         tolerance and is NAMED
  d  work invariance     MCO at another N with identical work fields but a
                         moved secondary mean: silent on work, every moved
                         secondary field EXPLAINED as
                         acquisition_redistribution with both ledger totals;
                         a planted work-field change (purity) trips as
                         UNEXPLAINED; an arm absent at N_FROZEN trips
  e  terminal decision   threshold_met + primary intact + no conflict ->
                         POSITIVE_RECOVERY_UNDER_FROZEN_SEMANTICS; secondary
                         not met / draw-invariance conflict on a recovering
                         tier / primary broken -> each PERSISTENT_NON_RECOVERY
                         with the blocking reason recorded
  f  binding hostiles    pristine flat copy of every sealed input binds (12
                         digests, n_frozen=30); tampered shard, tampered
                         DEV-CAL-3 receipt (sha vs the invariants' recorded
                         source_results_sha256), tampered invariants terminal
                         and a missing freeze each raise
                         RECEIPT_BINDING_DEFECT fail-closed

Usage:  python3 -m exact.devcal4_selftest
Exit 0 all hostiles behave as planted; 1 any hostile failed.
Run host: laptop billy (freeze `hosts`).
"""
from __future__ import annotations

import contextlib
import copy
import json
import os
import shutil
import sys
import tempfile
import time

import exact.devcal3_charging_attribution as M
import exact.devcal4_acquisition_charging as D4

FIXTURE_WORLD = "B-07"
ARM = "KO-2_PLUS_RETRIEVAL"
_REAL_PATHS = {a: getattr(D4, a) for a in
               ("FREEZE4_PATH", "DC3_RECEIPT", "DC3_INVARIANTS")}


# ------------------------------------------------------------- fixtures -------
def _flat_input_copy():
    """Flat copy of every sealed input M.bind_inputs reads (tamperable)."""
    d = tempfile.mkdtemp(prefix="dc4_selftest_")
    srcs = [M.SCORED_V2, M.SCORED_V1, M.RESULTS_V2, M.HOST_RECEIPT_V2] + \
        list(M.SHARD_V2)
    for p in srcs:
        shutil.copyfile(p, os.path.join(d, os.path.basename(p)))
    return d


@contextlib.contextmanager
def _patched_path(attr, mutate):
    """Redirect one D4 control-file path to a mutated temp copy."""
    source = _REAL_PATHS[attr]
    with open(source, encoding="utf-8") as f:
        doc = json.load(f)
    mutate(doc)
    tmp = tempfile.mkdtemp(prefix="dc4_patch_")
    p = os.path.join(tmp, os.path.basename(source))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
    old = getattr(D4, attr)
    setattr(D4, attr, p)
    try:
        yield p
    finally:
        setattr(D4, attr, old)
        shutil.rmtree(tmp, ignore_errors=True)


def _patched_freeze(**changes):
    def mutate(doc):
        doc.setdefault("N_derivation_rule", {}).update(changes)
    return _patched_path("FREEZE4_PATH", mutate)


def _mini_arm(secondary_mean=0.9991):
    def seed_block(mean, lo, hi):
        return {"mean": mean, "ci": [lo, hi], "n_pairs": 90,
                "threshold_met": True}
    return {
        "recovery_share_cell_B": seed_block(1.0, 1.0, 1.0),
        "recovery_share_cell_B_total_burden": seed_block(secondary_mean,
                                                         0.9776, 1.0205),
        "shuffle_null_cell_B": {"non_alarm": True, "p_signflip": 0.7944},
        "shuffle_null_cell_B_total_burden": {"non_alarm": True,
                                             "p_signflip": 0.3},
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


def _mini_ev(secondary_mean=0.9991, threshold_met=True):
    recovering = [ARM] if threshold_met else []
    return {
        "per_arm": {ARM: _mini_arm(secondary_mean)},
        "ladder_state": {ARM: {"primary": True, "secondary": threshold_met}},
        "verdict_if_this_were_the_model": (
            "CARRIER_IDENTIFIED_TIER_2" if threshold_met
            else "AMORTISATION_DOMINATED"),
        "recovering_tiers": recovering,
        "draw_invariance_conflict_tiers": [],
        "ko2_primary_intact": True,
        "evidence_arm": ARM,
        "p_one_sided": 0.0001,
        "flip_pre_holm": bool(recovering),
    }


def _expect_binding_defect(fn, needle):
    try:
        fn()
        raise AssertionError("planted binding defect NOT detected (%s)"
                             % needle)
    except (D4.BindingDefect, M.BindingDefect) as e:
        assert needle in str(e), (needle, e)


# ------------------------------------------------------------- hostiles ------
def hostile_a_n_derivation(rows):
    # no-alarm: the registered rule over the real sealed rows
    d = D4.derive_n(rows)
    assert d["n"] == 30, d
    assert d["u_distribution"] == {"30": 120}, d
    assert d["n_worlds_with_uses"] == 120 and d["n_worlds_zero_uses"] == 0, d
    # planted: one dropped use row moves min U to 29 for that world only
    victim = next(r for r in rows
                  if r.get("world_id") == FIXTURE_WORLD
                  and r.get("arm") != "RESET" and r.get("status") == "OK")
    dropped = [r for r in rows if r is not victim]
    d2 = D4.derive_n(dropped)
    assert d2["n"] == 29, d2
    assert d2["per_world_U"][FIXTURE_WORLD] == 29, d2
    assert d2["u_distribution"] == {"29": 1, "30": 119}, d2
    # guards: no use rows at all -> CANNOT_CHECK, never a silent zero
    resets = [r for r in rows if r.get("arm") == "RESET"]
    for bad in (resets, []):
        try:
            D4.derive_n(bad)
            raise AssertionError("empty min-set guard did not fire")
        except D4.CannotCheck as e:
            assert "N_DERIVATION_NO_USED_WORLDS" in str(e), e
    return "pristine N=30 uniform; planted drop -> 29 named; guards fire"


def hostile_b_frozen_n_gate(rows):
    # no-alarm: exact match is silent
    D4.frozen_n_gate(30, 30)
    # planted mismatch halts naming BOTH numbers
    try:
        D4.frozen_n_gate(30, 29)
        raise AssertionError("frozen-N mismatch did not halt")
    except D4.BindingDefect as e:
        assert "30" in str(e) and "29" in str(e), e
    d = _flat_input_copy()
    try:
        # a tampered freeze copy carrying n_frozen=29 binds, is READ as 29,
        # and the re-derivation gate halts on the pair (no hardcoded N)
        with _patched_freeze(n_frozen=29):
            _, _, _, n_frozen = D4.bind_inputs4(d)
            assert n_frozen == 29, n_frozen
            try:
                D4.frozen_n_gate(D4.derive_n(rows)["n"], n_frozen)
                raise AssertionError("tampered freeze N escaped the gate")
            except D4.BindingDefect as e:
                assert "30" in str(e) and "29" in str(e), e
        # null: the freeze no longer carries a computed N at all
        with _patched_freeze(n_frozen=None):
            try:
                D4.bind_inputs4(d)
                raise AssertionError("null n_frozen accepted")
            except D4.BindingDefect as e:
                assert "no computed n_frozen" in str(e), e
        # non-int / bool / zero values are binding defects, never coerced
        for bad in ("30", 30.0, True, 0):
            with _patched_freeze(n_frozen=bad):
                try:
                    D4.bind_inputs4(d)
                    raise AssertionError("invalid n_frozen %r accepted"
                                         % (bad,))
                except D4.BindingDefect as e:
                    assert "positive integer" in str(e), e
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return "match silent; tampered-N + invalid-N halt fail-closed"


def hostile_c_compare_block():
    got = _mini_ev()
    # no-alarm: pristine recomputed block binds the recorded copy exactly
    diffs, tol = D4.compare_block(got, copy.deepcopy(got))
    assert diffs == [] and tol == [], (diffs, tol)
    # planted secondary drift fires AND names the field
    want = copy.deepcopy(got)
    want["per_arm"][ARM]["recovery_share_cell_B_total_burden"]["mean"] += 0.5
    diffs, _ = D4.compare_block(got, want)
    assert any("per_arm.%s.recovery_share_cell_B_total_burden.mean" % ARM
               in x for x in diffs), diffs[:3]
    # planted scalar drift (p_one_sided) names the scalar
    want = copy.deepcopy(got)
    want["p_one_sided"] = 0.5
    diffs, _ = D4.compare_block(got, want)
    assert diffs and diffs[0].startswith("p_one_sided"), diffs[:2]
    # planted WORK-field drift (adapter digest) also fires at N=10
    want = copy.deepcopy(got)
    want["per_arm"][ARM]["adapter_sha256"] = "y" * 64
    diffs, _ = D4.compare_block(got, want)
    assert any("adapter_sha256" in x for x in diffs), diffs[:3]
    # recorded flip_pre_holm contradicting the recomputed components fires
    want = copy.deepcopy(got)
    want["flip_pre_holm"] = False
    diffs, _ = D4.compare_block(got, want)
    assert any(x.startswith("flip_pre_holm") for x in diffs), diffs[:3]
    # last-bit drift binds within the registered tolerance and is NAMED
    want = copy.deepcopy(got)
    want["per_arm"][ARM]["recovery_share_cell_B_total_burden"]["mean"] *= \
        (1.0 + 1e-14)
    diffs, tol = D4.compare_block(got, want)
    assert diffs == [], diffs
    assert any(".mean" in t for t in tol), tol
    return "pristine exact; 4 planted drifts fire named; ULP binds named"


def hostile_d_work_invariance_and_explanation():
    want = _mini_ev()
    frozen = _mini_ev(secondary_mean=0.55)   # work fields identical by
    #                                            construction, secondary moved
    diffs = D4.work_invariance_defects(frozen, want)
    assert diffs == [], diffs                # no-alarm: MCO never moves work
    acct_f = {ARM: {"acq_ledger_total": 123.4}}
    acct_r = {ARM: {"acq_ledger_total": 370.2}}
    explained, unexplained = D4.explain_field_diffs(frozen, want, acct_f,
                                                    acct_r)
    assert unexplained == [], unexplained
    moved = [x for x in explained["fields_differing"] if isinstance(x, dict)]
    assert moved and all(x["class"] == "acquisition_redistribution"
                         for x in moved), moved
    assert moved[0]["acquisition_ledger_total"] == {
        "at_N_FROZEN": 123.4, "at_recorded_N10": 370.2}, moved[0]
    # planted: a WORK field moves under MCO -> trips AND is unexplained
    bad = _mini_ev(secondary_mean=0.55)
    bad["per_arm"][ARM]["purity"]["n_pure"] = 300
    diffs = D4.work_invariance_defects(bad, want)
    assert any("purity" in x for x in diffs), diffs[:3]
    _, unexplained = D4.explain_field_diffs(bad, want, acct_f, acct_r)
    assert unexplained and any("purity" in str(u.get("field"))
                               for u in unexplained), unexplained
    # an arm absent at N_FROZEN trips (never silently skipped)
    gone = _mini_ev(secondary_mean=0.55)
    gone["per_arm"] = {}
    diffs = D4.work_invariance_defects(gone, want)
    assert any("recomputed absent at N_FROZEN" in x for x in diffs), diffs[:3]
    return "work invariant; secondary moves explained; work drift trips"


def hostile_e_terminal_decision():
    pos = D4.decide_terminal4(_mini_ev(threshold_met=True))
    assert pos["terminal"] == "POSITIVE_RECOVERY_UNDER_FROZEN_SEMANTICS" \
        and pos["positive"] and pos["ko2_secondary_threshold_met"], pos
    neg = D4.decide_terminal4(_mini_ev(threshold_met=False))
    assert neg["terminal"] == "PERSISTENT_NON_RECOVERY" and not neg["positive"]
    assert neg["ko2_secondary_threshold_met"] is False \
        and neg["ko2_primary_intact"] and neg[
            "draw_invariance_conflict_on_recovering_tiers"] == [], neg
    conf = _mini_ev(threshold_met=True)
    conf["draw_invariance_conflict_tiers"] = [ARM]
    c = D4.decide_terminal4(conf)
    assert c["terminal"] == "PERSISTENT_NON_RECOVERY", c
    assert c["draw_invariance_conflict_on_recovering_tiers"] == [ARM], c
    brok = _mini_ev(threshold_met=True)
    brok["ladder_state"][ARM]["primary"] = False
    b = D4.decide_terminal4(brok)
    assert b["terminal"] == "PERSISTENT_NON_RECOVERY" \
        and not b["ko2_primary_intact"], b
    return "POSITIVE / threshold-miss / conflict / primary-broken decide"


def hostile_f_binding():
    # no-alarm: pristine flat copy of every sealed input binds, 12 digests
    d = _flat_input_copy()
    try:
        bindings, docs, expected, n_frozen = D4.bind_inputs4(d)
        assert len(bindings) == 12, sorted(bindings)
        assert n_frozen == 30, n_frozen
        assert docs["freeze4"]["N_derivation_rule"]["n_frozen"] == 30
        assert docs["dc3_invariants"]["terminal"] == "CHARGE_CARRIER_MULTIPLE"
        # tampered shard -> fail-closed at the parent gate (both sources)
        with open(os.path.join(d, "DEVCAL2_receipts_shard1_V2.jsonl"),
                  "a") as f:
            f.write("\n")
        _expect_binding_defect(lambda: D4.bind_inputs4(d), "shard1")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # tampered DEV-CAL-3 receipt: sha no longer matches the invariants'
    # recorded source_results_sha256 -> RECEIPT_BINDING_DEFECT
    d = _flat_input_copy()
    try:
        with _patched_path("DC3_RECEIPT",
                           lambda doc: doc.update({"terminal": "TAMPERED"})):
            _expect_binding_defect(lambda: D4.bind_inputs4(d),
                                   "source_results_sha256")
        # tampered invariants terminal: disagrees with the DEV-CAL-3 receipt
        with _patched_path(
                "DC3_INVARIANTS",
                lambda doc: doc.update({"terminal": "CHARGE_CARRIER_NONE"})):
            _expect_binding_defect(lambda: D4.bind_inputs4(d),
                                   "invariants terminal")
        # missing freeze -> sealed-input-missing, fail-closed
        old = D4.FREEZE4_PATH
        gone_dir = tempfile.mkdtemp(prefix="dc4_gone_")
        D4.FREEZE4_PATH = os.path.join(gone_dir, "gone.json")
        try:
            _expect_binding_defect(lambda: D4.bind_inputs4(d),
                                   "sealed input missing")
        finally:
            D4.FREEZE4_PATH = old
            shutil.rmtree(gone_dir, ignore_errors=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return "pristine 12/12 binds; shard/receipt/invariants/missing all trip"


# ---------------------------------------------------------------- driver ------
def main():
    t0 = time.time()
    rows = M.load_shard_rows()
    hostiles = [
        ("a_n_derivation", lambda: hostile_a_n_derivation(rows)),
        ("b_frozen_n_gate", lambda: hostile_b_frozen_n_gate(rows)),
        ("c_compare_block", lambda: hostile_c_compare_block()),
        ("d_work_invariance", lambda:
         hostile_d_work_invariance_and_explanation()),
        ("e_terminal_decision", lambda: hostile_e_terminal_decision()),
        ("f_binding_hostiles", lambda: hostile_f_binding()),
    ]
    failed = []
    for name, fn in hostiles:
        try:
            note = fn()
            print("PASS %-22s %s" % (name, note))
        except Exception as e:                     # hostile misbehaved
            failed.append(name)
            print("FAIL %-22s %s: %s" % (name, type(e).__name__, e))
    print("devcal4 selftest: %d/%d hostiles correct, %.2fs" %
          (len(hostiles) - len(failed), len(hostiles), time.time() - t0))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
