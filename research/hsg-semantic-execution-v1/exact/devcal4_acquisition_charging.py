#!/usr/bin/env python3
"""DEV-CAL-4 acquisition-charging recomputation (#323; freeze
DEV_CAL_4_ACQUISITION_CHARGING_FREEZE_V1.json -- every clause binding).

Parent terminal: DEV-CAL-3 CHARGE_CARRIER_MULTIPLE (PR #353, 88a66321) --
the DEV-CAL-2 V2 AMORTISATION_DOMINATED non-amortisation is carried by the
acquisition (mining) charge in its full-charge no-retirement form; failures,
verification and salvage are exonerated (standing invariants).  This study
evaluates EXACTLY ONE charging change: the amortised acquisition charge with
retirement-after-N_FROZEN, where N_FROZEN was fixed by the pre-registered
derivation rule (freeze `N_derivation_rule`, rule-only pre-registration
commit cb4d1e74) BEFORE the count was taken: N = min over worlds of the
observed asset-use count U(w) (OK rows per world in the canonical use order;
RESET never a use), computed ONLY from the sealed V2 receipt shards.
Measured: 120 worlds, uniform U(w)=30 -> N_FROZEN=30 (the widest amortisation
under which every world still pays its raw acquisition exactly once; NOT in
the DEV-CAL-3 sensitivity grid {5,10,25}).

Method (freeze `method.kind` = ANALYTICAL_RECOMPUTATION_OVER_SEALED_RECEIPTS):
no new worlds, seeds, arms-at-runtime, or scored execution.  The semantics is
the UNCHANGED DEV-CAL-3 MARGINAL_COST_ONLY implementation (imported from
exact.devcal3_charging_attribution -- this lane edits NO machinery file):
per-world raw acquisition = the sealed ORACLE anchor row's cost_ledger
acquisition; each of the first N uses in the registered canonical use order
charges raw/N; uses after N charge zero; RESET zero; work never touched.

Controls (freeze `controls`, in order, all halting on failure):
  1 AS_IS exact-equality       every DEV_CAL_2_SCORED_RESULTS_V2 comparable
                               field recomputed exactly (registered 1e-12
                               float-bind tolerance, named fields) -- the
                               identical DEV-CAL-3 stage-1 gate
  2 machinery control at N=10  this lane's recompute at N=10 must reproduce
                               the recorded DEV_CAL_3_ATTRIBUTION_RESULTS_V1
                               charge_semantics.MARGINAL_COST_ONLY block
                               field-for-field (the Holm-family `flip` field
                               is inherited from the sealed receipt, not
                               recomputed; flip_pre_holm is recomputed and
                               compared), plus the marginal_cost_sensitivity
                               entries at N in {5,25}
  3 frozen-N readout           MARGINAL_COST_ONLY at N_FROZEN=30 recomputed
                               fresh; N_FROZEN not in {5,10,25} -> every
                               field differing from the recorded N=10 block
                               is listed and explained field-by-field; all
                               work-derived fields must be IDENTICAL
                               (freeze `controls.work_readout_invariance`)
  4 leakage + direction        event preservation (identity digests) and
                               direction sanity under the frozen semantics

Endpoint (freeze `endpoint_and_stats`): KO-2_PLUS_RETRIEVAL secondary
(total_burden_incl_acquisition) recovery in cell B at N_FROZEN (mean >= 0.25
inherited threshold with CI + null non-alarm + draw-invariance no-conflict)
while the KO-2 primary transfer stays intact; single pre-registered
hypothesis, one-sided signflip (PERM_N=10000, frozen seed tag) at alpha=0.05.
Holm is not applicable to a single hypothesis (the DEV-CAL-3 five-arm Holm
result stands as parent context).

Terminals (freeze `terminals.precedence`):
POSITIVE_RECOVERY_UNDER_FROZEN_SEMANTICS > PERSISTENT_NON_RECOVERY >
RECEIPT_BINDING_DEFECT > ASSAY_DEFECT > CANNOT_CHECK_<reason>.
RECEIPT_BINDING_DEFECT / ASSAY_DEFECT halt BEFORE any frozen-semantics
number is reported.

Claim ceiling (freeze `claim_ceiling`): scoped ONLY to the sealed V2 task
stream under the frozen semantics; no horizon generalisation, no new-stream
claim, no economics claim, no new DEV-CAL-2 terminal.

HOST RULES (freeze `hosts`): recompute + selftest on laptop billy ONLY --
never Mac mini.  Forbidden (freeze `forbidden`): touching any other charge
component; a second charging change; new scored runs; editing sealed
receipts, the DEV-CAL-3 receipt or the invariants file; outcome-motivated N
selection (N_FROZEN is read from the merged freeze and re-derived; a
mismatch halts); editing devcal3/run_devcal2/devcal2_adapters machinery.

Usage:
  python3 -m exact.devcal4_acquisition_charging --run [--out PATH] [--data DIR]
Exit codes: 0 completed; 4 ASSAY_DEFECT; 5 RECEIPT_BINDING_DEFECT;
3 CANNOT_CHECK setup.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys
import time

import exact.devcal3_charging_attribution as M

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
RECEIPTS = os.path.join(HERE, "receipts")
FREEZE4_PATH = os.path.join(HERE, "DEV_CAL_4_ACQUISITION_CHARGING_FREEZE_V1.json")
DC3_RECEIPT = os.path.join(RESULTS, "DEV_CAL_3_ATTRIBUTION_RESULTS_V1.json")
DC3_INVARIANTS = os.path.join(RESULTS,
                              "DEV_CAL_3_EXONERATED_COMPONENT_INVARIANTS_V1.json")

# the arms whose rows are USES of the world asset (freeze
# `N_derivation_rule.rule`); RESET rows are never uses
USE_SEEDS = (0, 1, 2)

HOLM_NOTE = ("Holm-Bonferroni is not applicable to this single pre-registered "
             "hypothesis; the DEV-CAL-3 five-arm family Holm result (reject "
             "MARGINAL_COST_ONLY, adjusted p=0.0) stands as parent context")
SIGNFLIP_ALPHA = 0.05

EXIT_OK, EXIT_ASSAY_DEFECT, EXIT_CANNOT_CHECK, EXIT_BINDING_DEFECT = 0, 4, 3, 5


class BindingDefect(Exception):
    """Sealed-input sha256 mismatch / freeze inconsistency."""


class AssayDefect(Exception):
    """Control failure (AS_IS, N=10 machinery, invariance, leakage)."""


class CannotCheck(Exception):
    """Registered guard (e.g. N-derivation degenerate) fired."""


def _sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ------------------------------------------------------- input binding -----
def bind_inputs4(data_dir=None):
    """Record sha256 of every sealed input BEFORE any recomputation.

    Extends the unchanged DEV-CAL-3 binding set (gated against BOTH committed
    digest sources via M.bind_inputs) with this study's own sealed controls:
    the DEV-CAL-4 freeze, the DEV-CAL-3 analysis receipt (gated against the
    exonerated-component invariants' recorded source_results_sha256), and the
    invariants file itself.  Fail-closed everywhere."""
    bindings, docs, expected = M.bind_inputs(data_dir)
    extra = {
        "freeze/DEV_CAL_4_ACQUISITION_CHARGING_FREEZE_V1.json": FREEZE4_PATH,
        "results/DEV_CAL_3_ATTRIBUTION_RESULTS_V1.json": DC3_RECEIPT,
        "results/DEV_CAL_3_EXONERATED_COMPONENT_INVARIANTS_V1.json":
            DC3_INVARIANTS,
    }
    for rel, p in sorted(extra.items()):
        if not os.path.exists(p):
            raise BindingDefect("sealed input missing: %s (%s)" % (rel, p))
        bindings[rel] = _sha256_file(p)

    with open(FREEZE4_PATH, encoding="utf-8") as f:
        freeze4 = json.load(f)
    with open(DC3_RECEIPT, encoding="utf-8") as f:
        dc3 = json.load(f)
    with open(DC3_INVARIANTS, encoding="utf-8") as f:
        invariants = json.load(f)

    # gate the DEV-CAL-3 receipt against the invariants' recorded digest
    want = invariants.get("source_results_sha256")
    if want != bindings["results/DEV_CAL_3_ATTRIBUTION_RESULTS_V1.json"]:
        raise BindingDefect(
            "DEV_CAL_3_ATTRIBUTION_RESULTS_V1.json sha %s != invariants' "
            "recorded source_results_sha256 %s" % (
                bindings["results/DEV_CAL_3_ATTRIBUTION_RESULTS_V1.json"], want))
    # gate the invariants' own recorded target (the DEV-CAL-3 terminal stands)
    if invariants.get("terminal") != dc3.get("terminal"):
        raise BindingDefect("invariants terminal %r != DEV-CAL-3 receipt "
                            "terminal %r" % (invariants.get("terminal"),
                                             dc3.get("terminal")))
    # the freeze must be registered with a computed N (never null) and must
    # authorise exactly one charging change
    rule = freeze4.get("N_derivation_rule") or {}
    if rule.get("n_frozen") is None:
        raise BindingDefect("DEV-CAL-4 freeze carries no computed n_frozen")
    n_frozen = rule["n_frozen"]
    if isinstance(n_frozen, bool) or not isinstance(n_frozen, int) \
            or n_frozen < 1:
        raise BindingDefect("freeze n_frozen %r is not a positive integer"
                            % (n_frozen,))
    docs["freeze4"] = freeze4
    docs["dc3_receipt"] = dc3
    docs["dc3_invariants"] = invariants
    return bindings, docs, expected, n_frozen


# ------------------------------------------------------- N derivation -----
def derive_n(rows):
    """The registered rule VERBATIM (freeze `N_derivation_rule.rule`):
    N = min over worlds w of U(w); U(w) = OK rows for world w whose (arm,
    seed) lies in the canonical use order (arm in {ORACLE_HISTORY,
    SHUFFLED_HISTORY} union ALL_KO_ARMS, seed in {0,1,2}); RESET is never a
    use; zero-use worlds are excluded from the min.  Outcome-blind: reads
    ONLY row identity fields, never any results/readout document."""
    import exact.devcal2_adapters as A
    use_arms = {"ORACLE_HISTORY", "SHUFFLED_HISTORY"} | set(A.ALL_KO_ARMS)
    counts = collections.Counter()
    for r in rows:
        if r.get("status") != "OK":
            continue
        if r.get("arm") in use_arms and r.get("seed") in USE_SEEDS:
            counts[r.get("world_id")] += 1
    used = {w: c for w, c in counts.items() if c >= 1}
    if not used:
        raise CannotCheck("N_DERIVATION_NO_USED_WORLDS: no world with a "
                          "single use row")
    n = min(used.values())
    if n < 1:
        raise CannotCheck("N_DERIVATION_DEGENERATE: min U(w) = %d" % n)
    dist = collections.Counter(used.values())
    return {"n": n, "per_world_U": dict(sorted(used.items())),
            "u_distribution": {str(k): v for k, v in sorted(dist.items())},
            "n_worlds_with_uses": len(used),
            "n_worlds_zero_uses": len(counts) - len(used)}


# --------------------------------------------- recorded-block comparison -----
WORK_DERIVED_PER_ARM = ("recovery_share_cell_B", "shuffle_null_cell_B",
                        "draw_invariance_cell_B", "controls", "purity",
                        "adapter_sha256")
SECONDARY_PER_ARM = ("recovery_share_cell_B_total_burden",
                     "shuffle_null_cell_B_total_burden")


def _named_diffs(label, got, want, diffs, tol_used):
    """Recursive exact-first comparison (registered 1e-12 float-bind via
    M._bind_eq); every tolerance-bound field is NAMED, every mismatch is a
    defect line.  Mirrors the DEV-CAL-3 compare_as_is discipline."""
    if got == want:
        return
    if isinstance(got, bool) or isinstance(want, bool):
        if got != want:
            diffs.append("%s: recomputed %r != recorded %r" % (label, got,
                                                               want))
        return
    if isinstance(got, (int, float)) and isinstance(want, (int, float)):
        if M._bind_eq(got, want):
            tol_used.append(label)
        else:
            diffs.append("%s: recomputed %r != recorded %r" % (label, got,
                                                              want))
        return
    if isinstance(got, list) and isinstance(want, list):
        if len(got) != len(want):
            diffs.append("%s: length %d != %d" % (label, len(got), len(want)))
            return
        for i, (g, w) in enumerate(zip(got, want)):
            _named_diffs("%s[%d]" % (label, i), g, w, diffs, tol_used)
        return
    if isinstance(got, dict) and isinstance(want, dict):
        for k in sorted(set(got) | set(want)):
            if k not in got:
                diffs.append("%s.%s: recomputed absent" % (label, k))
            elif k not in want:
                diffs.append("%s.%s: recorded absent" % (label, k))
            else:
                _named_diffs("%s.%s" % (label, k), got[k], want[k], diffs,
                             tol_used)
        return
    diffs.append("%s: recomputed %r != recorded %r" % (label, got, want))


def compare_block(got_ev, want_ev):
    """Full-block comparison against the recorded DEV-CAL-3 MCO readout.
    Compares every field the recorded block carries EXCEPT the Holm-family
    `flip` (inherited from the sealed receipt -- this study has one arm, no
    five-arm family) and the note fields."""
    diffs, tol_used = [], []
    for field in ("verdict_if_this_were_the_model", "recovering_tiers",
                  "draw_invariance_conflict_tiers", "ko2_primary_intact",
                  "evidence_arm", "p_one_sided", "flip_pre_holm"):
        if field in ("flip_pre_holm",):
            got = bool(got_ev.get("recovering_tiers") and
                       got_ev.get("ko2_primary_intact") and
                       not got_ev.get("draw_invariance_conflict_tiers"))
        else:
            got = got_ev.get(field)
        _named_diffs(field, got, want_ev.get(field), diffs, tol_used)
    for arm in sorted(set(got_ev.get("per_arm") or {}) |
                      set(want_ev.get("per_arm") or {})):
        ga = (got_ev.get("per_arm") or {}).get(arm)
        wa = (want_ev.get("per_arm") or {}).get(arm)
        if ga is None or wa is None:
            diffs.append("per_arm.%s: %s side absent" % (
                arm, "recomputed" if ga is None else "recorded"))
            continue
        for field in WORK_DERIVED_PER_ARM + SECONDARY_PER_ARM:
            _named_diffs("per_arm.%s.%s" % (arm, field), ga.get(field),
                         wa.get(field), diffs, tol_used)
    _named_diffs("ladder_state", got_ev.get("ladder_state"),
                 want_ev.get("ladder_state"), diffs, tol_used)
    return diffs, tol_used


def work_invariance_defects(ev_frozen, want_ev):
    """Freeze `controls.work_readout_invariance`: under MARGINAL_COST_ONLY at
    ANY N every work-derived per-arm field must equal the recorded values
    (MCO never touches work and never touches events).  Returns defect
    lines (empty = invariant holds)."""
    diffs, tol = [], []
    for arm, wa in sorted((want_ev.get("per_arm") or {}).items()):
        ga = (ev_frozen.get("per_arm") or {}).get(arm)
        if ga is None:
            diffs.append("per_arm.%s: recomputed absent at N_FROZEN" % arm)
            continue
        for field in WORK_DERIVED_PER_ARM:
            _named_diffs("N_FROZEN.per_arm.%s.%s" % (arm, field),
                         ga.get(field), wa.get(field), diffs, tol)
    return diffs


def acquisition_accounting(decomp, raw_acq, n):
    """Per-arm acquisition charge accounting at retirement-after-n (the
    field-by-field explanation backbone): canonical positions covered,
    per-world and ledger-total acquisition by arm."""
    import exact.devcal2_adapters as A
    use_pos = M._use_order()
    per_arm = collections.defaultdict(lambda: {"worlds": 0, "acq_total": 0.0,
                                               "positions_covered": set()})
    for key, d in sorted(decomp.items()):
        row = d["row"]
        if row["arm"] == "RESET":
            continue
        pos = use_pos.get((row["arm"], row["seed"]))
        e = per_arm[row["arm"]]
        if pos and pos <= n:
            e["worlds"] += 1
            e["acq_total"] += raw_acq[row["world_id"]] / n
            e["positions_covered"].add(pos)
    return {arm: {"n_rows_paying": v["worlds"],
                  "acq_ledger_total": v["acq_total"],
                  "positions_covered": sorted(v["positions_covered"]),
                  "n_positions_covered": len(v["positions_covered"])}
            for arm, v in sorted(per_arm.items())}


def explain_field_diffs(ev_frozen, want_ev, acct_frozen, acct_recorded):
    """Freeze `controls.frozen_N_readout` (N_FROZEN not in the grid): every
    field that differs from the recorded N=10 block is listed and explained
    field-by-field.  Expected difference class: acquisition-charge
    redistribution across arms (secondary/total-burden fields only)."""
    out = {"fields_identical": [], "fields_differing": []}
    for arm in sorted((want_ev.get("per_arm") or {})):
        wa = (want_ev.get("per_arm") or {}).get(arm) or {}
        ga = (ev_frozen.get("per_arm") or {}).get(arm) or {}
        for field in WORK_DERIVED_PER_ARM + SECONDARY_PER_ARM:
            label = "per_arm.%s.%s" % (arm, field)
            same = ga.get(field) == wa.get(field) or M._bind_eq(
                ga.get(field), wa.get(field))
            if same:
                out["fields_identical"].append(label)
                continue
            acq_delta = None
            if field in SECONDARY_PER_ARM:
                af = acct_frozen.get(arm, {}).get("acq_ledger_total")
                ar = acct_recorded.get(arm, {}).get("acq_ledger_total")
                acq_delta = {"at_N_FROZEN": af, "at_recorded_N10": ar}
            out["fields_differing"].append({
                "field": label, "class": (
                    "acquisition_redistribution" if field in SECONDARY_PER_ARM
                    else "UNEXPLAINED_work_derived_field_moved"),
                "acquisition_ledger_total": acq_delta,
                "at_N_FROZEN": ga.get(field), "recorded_N10": wa.get(field)})
    for field in ("recovering_tiers", "draw_invariance_conflict_tiers",
                  "ko2_primary_intact", "evidence_arm", "p_one_sided",
                  "verdict_if_this_were_the_model", "ladder_state"):
        same = (ev_frozen.get(field) == want_ev.get(field)) or M._bind_eq(
            ev_frozen.get(field), want_ev.get(field))
        (out["fields_identical"] if same else
         out["fields_differing"]).append(field)
    fp_got = bool(ev_frozen.get("recovering_tiers") and
                  ev_frozen.get("ko2_primary_intact") and
                  not ev_frozen.get("draw_invariance_conflict_tiers"))
    (out["fields_identical"] if fp_got == want_ev.get("flip_pre_holm") else
     out["fields_differing"]).append("flip_pre_holm")
    unexplained = [d for d in out["fields_differing"]
                   if isinstance(d, dict) and d["class"].startswith(
                       "UNEXPLAINED")]
    return out, unexplained


def frozen_n_gate(derived_n, bound_n):
    """The run()-stage gate: the N re-derived from the sealed rows must equal
    the n_frozen recorded in the merged freeze (freeze `forbidden`: outcome-
    motivated N selection voids the study; a mismatch halts BEFORE any
    frozen-semantics number is reported)."""
    if derived_n != bound_n:
        raise BindingDefect("N re-derivation %d != frozen n_frozen %d" %
                            (derived_n, bound_n))


def decide_terminal4(ev_frozen):
    """Freeze `endpoint_and_stats.decision_rule`."""
    pa = ev_frozen["per_arm"]
    ko2 = pa.get("KO-2_PLUS_RETRIEVAL") or {}
    sec = (ko2.get("recovery_share_cell_B_total_burden") or {})
    primary_intact = bool(ev_frozen.get("ladder_state", {}).get(
        "KO-2_PLUS_RETRIEVAL", {}).get("primary"))
    conflicts = ev_frozen.get("draw_invariance_conflict_tiers") or []
    recovering = ev_frozen.get("recovering_tiers") or []
    conflict_free = not [t for t in recovering if t in conflicts]
    positive = bool(sec.get("threshold_met") and primary_intact and
                    conflict_free)
    return {
        "positive": positive,
        "ko2_secondary_threshold_met": bool(sec.get("threshold_met")),
        "ko2_primary_intact": primary_intact,
        "draw_invariance_conflict_on_recovering_tiers":
            [t for t in recovering if t in conflicts],
        "terminal": ("POSITIVE_RECOVERY_UNDER_FROZEN_SEMANTICS" if positive
                     else "PERSISTENT_NON_RECOVERY"),
    }


# ---------------------------------------------------------------- driver ------
def run(data_dir=None, out_path=None, host_label=None):
    """Full DEV-CAL-4 analysis over the sealed V2 ledgers.  Exit-code
    contract: 0 completed; 4 ASSAY_DEFECT; 5 RECEIPT_BINDING_DEFECT; 3
    CANNOT_CHECK."""
    import exact.devcal2_adapters as A
    out_path = out_path or os.path.join(
        RESULTS, "DEV_CAL_4_ACQUISITION_CHARGING_RESULTS_V1.json")
    receipt = {"schema": "OCM_DEV_CAL_4_ACQUISITION_CHARGING_RESULTS",
               "version": "V1", "study":
               "DEV-CAL-4 acquisition charging under frozen semantics",
               "protocol": "DEV_CAL_4_ACQUISITION_CHARGING_FREEZE_V1",
               "owner_issue": 323, "parent_verdict":
               "DEV-CAL-3 CHARGE_CARRIER_MULTIPLE (PR #353, 88a66321)",
               "host": host_label or os.uname().nodename, "cannot_check": []}
    t0 = time.time()

    def _halt(terminal, key, detail):
        receipt["terminal"] = terminal
        receipt[key] = detail[:2000]
        _write(receipt, out_path)
        print("DEV-CAL-4 terminal:", terminal)
        print("  ", detail[:400])
        return {"RECEIPT_BINDING_DEFECT": EXIT_BINDING_DEFECT,
                "ASSAY_DEFECT": EXIT_ASSAY_DEFECT,
                }.get(terminal, EXIT_CANNOT_CHECK)

    # 1 -- bind every sealed input BEFORE any recomputation (freeze method)
    try:
        bindings, docs, expected, n_frozen = bind_inputs4(data_dir)
    except M.BindingDefect as e:
        return _halt("RECEIPT_BINDING_DEFECT", "binding_defect", str(e))
    except BindingDefect as e:
        return _halt("RECEIPT_BINDING_DEFECT", "binding_defect", str(e))
    receipt["input_bindings_recorded_before_recomputation"] = bindings
    receipt["binding_verification"] = {
        "gated_against": ["DEV_CAL_2_SCORED_RESULTS_V2.json output_bindings",
                          "DEVCAL2_HOST_RECEIPT_billy_V2.json "
                          "output_bindings",
                          "DEV_CAL_3_EXONERATED_COMPONENT_INVARIANTS_V1.json "
                          "source_results_sha256"],
        "verdict": "ALL_MATCH"}
    freeze4 = docs["freeze4"]
    dc3 = docs["dc3_receipt"]
    if n_frozen != freeze4["N_derivation_rule"]["n_frozen"]:
        return _halt("RECEIPT_BINDING_DEFECT", "binding_defect",
                     "freeze n_frozen %r != bound value %r" % (
                         freeze4["N_derivation_rule"]["n_frozen"], n_frozen))
    receipt["frozen_semantics"] = dict(freeze4["frozen_semantics"])
    receipt["n_derivation_recomputed"] = None

    # 2 -- sealed rows + full event-ledger replay (unchanged machinery)
    rows = M.load_shard_rows(data_dir)
    worlds, ctx = M._world_cache()
    adapters = {a: A.make_adapter(a) for a in A.ALL_KO_ARMS}
    raw_acq = M.raw_acquisition_by_world(rows)
    try:
        decomp = M.decompose_rows(rows, worlds, ctx, adapters, raw_acq)
    except M.AssayDefect as e:
        return _halt("ASSAY_DEFECT", "assay_defect",
                     "replay divergence: %s" % e)
    receipt["n_rows_replayed_and_verified"] = len(decomp)
    acq_defects = M.acquisition_charge_checks(decomp, ctx)
    if acq_defects:
        return _halt("ASSAY_DEFECT", "assay_defect",
                     "acquisition charging: %s" % "; ".join(acq_defects[:10]))

    # 3 -- AS_IS exact-equality control (freeze controls.as_is_exact_equality)
    per_arm_asis, ladder_asis, verdict_asis = M.recompute_per_arm(rows)
    asis_defects, asis_stats = M.compare_as_is(per_arm_asis, ladder_asis,
                                               verdict_asis,
                                               docs["scored_v2"])
    if asis_defects:
        return _halt("ASSAY_DEFECT", "assay_defect",
                     "AS_IS mismatch: %s" % "; ".join(asis_defects[:10]))
    receipt["as_is_control"] = {
        "verdict": "EXACT_EQUALITY_WITH_DEV_CAL_2_SCORED_V2",
        "bind_stats": asis_stats, "recomputed_verdict": verdict_asis,
        "n_arms": len(per_arm_asis)}

    # 4 -- N re-derivation on the bound rows; must equal the frozen N
    try:
        nder = derive_n(rows)
    except CannotCheck as e:
        return _halt("CANNOT_CHECK", "cannot_check", str(e))
    receipt["n_derivation_recomputed"] = nder
    try:
        frozen_n_gate(nder["n"], n_frozen)
    except BindingDefect as e:
        return _halt("RECEIPT_BINDING_DEFECT", "binding_defect", str(e))

    # 5 -- machinery control: N=10 (+ {5,25} sensitivity) exact equality vs
    #      the recorded DEV-CAL-3 MCO readout
    asis_totals = M.semantics_totals(decomp, "AS_IS", raw_acq)
    recorded_mco = (dc3.get("charge_semantics") or {}).get(
        "MARGINAL_COST_ONLY") or {}
    recorded_sens = dc3.get("marginal_cost_sensitivity") or {}
    m10, m525 = {}, {}
    for n in (5, 10, 25):
        totals = M.semantics_totals(decomp, "MARGINAL_COST_ONLY", raw_acq,
                                    mco_n=n)
        viol = M.event_preservation(decomp, totals)
        dviol = M.direction_sanity(asis_totals, totals,
                                   "MARGINAL_COST_ONLY(N=%d)" % n)
        if viol or dviol:
            return _halt("ASSAY_DEFECT", "assay_defect",
                         "leakage/direction violation at N=%d: %s" %
                         (n, "; ".join((viol + dviol)[:5])))
        ev = M.evaluate_semantics(rows, totals)
        if n == 10:
            diffs, tol = compare_block(ev, recorded_mco)
            if diffs:
                return _halt("ASSAY_DEFECT", "assay_defect",
                             "N=10 machinery control mismatch: %s" %
                             "; ".join(diffs[:10]))
            m10 = {"verdict": "EXACT_EQUALITY_WITH_RECORDED_MCO_N10",
                   "fields_tolerance_bound_named": tol}
        else:
            rec = recorded_sens.get(str(n)) or {}
            d = []
            if ev["recovering_tiers"] != rec.get("recovering_tiers"):
                d.append("recovering_tiers %r != %r" % (
                    ev["recovering_tiers"], rec.get("recovering_tiers")))
            if ev["ko2_primary_intact"] != rec.get("ko2_primary_intact"):
                d.append("ko2_primary_intact %r != %r" % (
                    ev["ko2_primary_intact"], rec.get("ko2_primary_intact")))
            if not M._bind_eq(ev["p_one_sided"], rec.get("p_one_sided")):
                d.append("p_one_sided %r != %r" % (
                    ev["p_one_sided"], rec.get("p_one_sided")))
            if d:
                return _halt("ASSAY_DEFECT", "assay_defect",
                             "N=%d sensitivity control mismatch: %s" %
                             (n, "; ".join(d)))
            m525[str(n)] = "EXACT_EQUALITY_WITH_RECORDED_SENSITIVITY"
    receipt["machinery_control"] = {"N10": m10, "sensitivity": m525}

    # 6 -- the frozen-N readout (the single authorised charging change)
    totals30 = M.semantics_totals(decomp, "MARGINAL_COST_ONLY", raw_acq,
                                  mco_n=n_frozen)
    viol = M.event_preservation(decomp, totals30)
    dviol = M.direction_sanity(asis_totals, totals30,
                               "MARGINAL_COST_ONLY(N=%d)" % n_frozen)
    if viol or dviol:
        return _halt("ASSAY_DEFECT", "assay_defect",
                     "leakage/direction violation at N_FROZEN=%d: %s" %
                     (n_frozen, "; ".join((viol + dviol)[:5])))
    ev30 = M.evaluate_semantics(rows, totals30)
    winv = work_invariance_defects(ev30, recorded_mco)
    if winv:
        return _halt("ASSAY_DEFECT", "assay_defect",
                     "work-readout invariance breach at N_FROZEN: %s" %
                     "; ".join(winv[:10]))
    acct30 = acquisition_accounting(decomp, raw_acq, n_frozen)
    acct10 = acquisition_accounting(decomp, raw_acq, 10)
    explained, unexplained = explain_field_diffs(ev30, recorded_mco,
                                                 acct30, acct10)
    if unexplained:
        return _halt("ASSAY_DEFECT", "assay_defect",
                     "UNEXPLAINED work-derived field differences at "
                     "N_FROZEN: %s" % "; ".join(
                         [str(u.get("field")) for u in unexplained[:10]]))
    decision = decide_terminal4(ev30)
    receipt["frozen_N_readout"] = {
        "N_FROZEN": n_frozen,
        "n_in_recorded_grid": n_frozen in (5, 10, 25),
        "per_arm": ev30["per_arm"], "ladder_state": ev30["ladder_state"],
        "recovering_tiers": ev30["recovering_tiers"],
        "draw_invariance_conflict_tiers":
            ev30["draw_invariance_conflict_tiers"],
        "ko2_primary_intact": ev30["ko2_primary_intact"],
        "evidence_arm": ev30["evidence_arm"],
        "p_one_sided": ev30["p_one_sided"],
        "verdict_if_this_were_the_model":
            ev30["verdict_if_this_were_the_model"],
        "holm_note": HOLM_NOTE,
        "signflip_alpha": SIGNFLIP_ALPHA}
    receipt["work_readout_invariance"] = {
        "verdict": "ALL_WORK_DERIVED_FIELDS_IDENTICAL_TO_RECORDED_N10",
        "n_fields_identical": len(explained["fields_identical"])}
    receipt["field_by_field_explanation"] = explained
    receipt["acquisition_accounting"] = {
        "at_N_FROZEN": acct30, "at_recorded_N10": acct10}

    # 7 -- terminal (freeze endpoint decision rule)
    receipt["terminal_decision"] = decision
    receipt["terminal"] = decision["terminal"]
    ko2_sec = (ev30["per_arm"]["KO-2_PLUS_RETRIEVAL"]
               ["recovery_share_cell_B_total_burden"])
    receipt["terminal_evidence"] = (
        "under MARGINAL_COST_ONLY with N_FROZEN=%d (measured break-even "
        "horizon: min over worlds of observed uses), KO-2 secondary "
        "recovery_share = %.4f CI %s threshold_met=%s, KO-2 primary intact="
        "%s, recovering tiers=%s, draw-invariance conflicts=%s, one-sided "
        "signflip p=%s" % (n_frozen, ko2_sec["mean"], ko2_sec["ci"],
                           ko2_sec["threshold_met"],
                           decision["ko2_primary_intact"],
                           ev30["recovering_tiers"],
                           decision["draw_invariance_conflict_on_recovering_"
                                    "tiers"], ev30["p_one_sided"]))
    receipt["claim_ceiling"] = freeze4["claim_ceiling"]
    receipt["generated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                             time.gmtime())
    receipt["wall_s"] = round(time.time() - t0, 1)
    receipt["run_role"] = "ANALYTICAL_RECOMPUTATION_OVER_SEALED_RECEIPTS"
    _write(receipt, out_path)
    print("DEV-CAL-4 terminal:", receipt["terminal"])
    print("  ", receipt["terminal_evidence"])
    print("   wall_s", receipt["wall_s"], "->", out_path)
    return EXIT_OK


def _write(doc, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--data", default=None,
                    help="directory holding sealed inputs (selftest only)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    if args.run:
        return run(data_dir=args.data, out_path=args.out)
    print("use --run", file=sys.stderr)
    return EXIT_CANNOT_CHECK


if __name__ == "__main__":
    sys.exit(main())
