#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check suite -- GMI #833 Section I update-law regimes.

Runs BOTH routes in-process, cross-checks every registered claim, screens the
JSON files that do not exist when the executor runs, and prints ALL GREEN or
the failing checks.  No claim is gated by a bare `assert`, which `-O` erases:
every check appends to an explicit list and the exit code is derived from it.

    python3 -I -B  test_update_law_regimes_v1.py
    python3 -I -O -B test_update_law_regimes_v1.py
"""

import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import update_law_regimes_v1 as A          # noqa: E402
import oracle_update_law_regimes_v1 as B   # noqa: E402

CHECKS = []


def ck(name, ok, detail=""):
    CHECKS.append({"name": name, "ok": bool(ok), "detail": str(detail)[:400]})


def main():
    # ---- 0. scope fingerprints must agree BEFORE any agreement is read ----
    a_envs = A.derivation_environments()
    b_envs = B.derivation_set()
    fa = A.scope_fingerprint(a_envs)
    fb = B.fingerprint(b_envs)
    ck("scope_fingerprint_agreement", fa == fb, "%s vs %s" % (fa, fb))
    a_hold = A.heldout_environments()
    b_hold = B.heldout_set()
    ck("heldout_fingerprint_agreement",
       A.scope_fingerprint(a_hold) == B.fingerprint(b_hold))
    if fa != fb:
        report()
        return

    # ---- 1. invariants, coefficient vectors and thresholds, both routes ----
    inv_pairs = []
    for ea, eb in zip(a_envs, b_envs):
        ia = A.invariants(ea)
        ib = B.invariants(eb)
        va = A.coefficient_vectors(ea, ia)
        vb = B.vectors(eb, ib)
        inv_pairs.append((ea, ia, va, eb, ib, vb))
        eid = ia["env"]
        for k in ("M", "T", "nq", "K", "k0", "Mprime", "r", "alpha_gain", "mu",
                  "Dmin", "Dmin_L", "disc", "cover", "Bmin", "Tsteps",
                  "max_degree", "unimodal", "Vloc", "Vglob", "target_in_H",
                  "local_optima", "point_summary_index"):
            ck("%s.invariant.%s" % (eid, k), ia[k] == ib[k],
               "%r vs %r" % (ia[k], ib[k]))
        for rid in list(A.REGIME_IDS) + [A.BASELINE_ID]:
            x, y = va.get(rid), vb.get(rid)
            ck("%s.vector.%s" % (eid, rid),
               (x is None and y is None) or (x is not None and
                                             tuple(x) == tuple(y)),
               "%r vs %r" % (x, y))
        ta = A.thresholds(ea, ia, va)
        # route B derives its thresholds by outward scan + bracket, never from
        # the closed form the executor uses
        if vb["SIG-R"] is not None:
            cs = B.threshold_by_scan(vb["SIG-X"], vb["SIG-R"],
                                     B.COORDS.index("p_store"))
            cf = ta["chi_star"].get("value")
            ok = (cf is not None and cs is not None and F(cf) == cs) or \
                 (cf is not None and F(cf) <= 0 and cs is None)
            ck("%s.chi_star_two_routes" % eid, ok, "%s vs %s" % (cf, cs))
        ck("%s.beta_star_two_routes" % eid,
           ta["beta_star"]["value"] ==
           str(F(ib["alpha_gain"], (ib["M"] - 1) * ib["T"])))
        den = (ib["Bmin"] - 1) * ib["Tsteps"]
        pv = F(0) if den == 0 else (F(ib["Vglob"]) - F(ib["Vloc"])) / den
        ck("%s.pistar_two_routes" % eid,
           ta["pistar_star"]["value"] == str(pv))
        ck("%s.tau_two_routes" % eid,
           ta["tau_star"]["value"] ==
           str(F(ib["r"] * ib["T"] * (ib["K"] - ib["k0"]),
                 ib["Mprime"] * ib["K"])))

        # ---- 2. the unconditional converses -------------------------------
        if ia["alpha_gain"] <= 0:
            bad = [p for p in A.JOINT_PRICES
                   if A.charge(va["SIG-W"], p) <=
                   A.charge(va[A.BASELINE_ID], p)]
            ck("%s.UL2_converse_unconditional" % eid, not bad,
               "%d violations" % len(bad))
        if ia["unimodal"]:
            tuples, meta = A.neutral_grammar(ia)
            viol = 0
            for g in tuples:
                if g[3] < 2:
                    continue
                g1 = (g[0], g[1], g[2], 1, g[4], g[5])
                x = A.tuple_vector(ea, ia, g)
                y = A.tuple_vector(ea, ia, g1)
                if any(A.charge(x, p) <= A.charge(y, p)
                       for p in A.JOINT_PRICES[:81]):
                    viol += 1
            ck("%s.UL6_converse_unconditional" % eid, viol == 0,
               "%d breadth tuples not strictly dearer" % viol)
        red = A.reduction_at_zero_relatedness(ea, ia)
        redb = B.zero_relatedness(eb, ib)
        ck("%s.UL7_reduction_two_routes" % eid,
           red.get("behaviourally_identical") ==
           redb.get("behaviourally_identical") and
           red.get("applicable") == redb.get("applicable"))
        if red.get("applicable"):
            ck("%s.UL7_reduction_at_r0" % eid,
               red["behaviourally_identical"] and
               red["pointwise_inputs_checked"] > 0,
               "checked %d inputs, %d mismatches" %
               (red["pointwise_inputs_checked"], len(red["mismatches"])))
        # UL-8: SIG-S is strictly dearer than its comparator at every price
        bad = [p for p in A.JOINT_PRICES
               if A.charge(va["SIG-S"], p) <= A.charge(va[A.BASELINE_ID], p)]
        ck("%s.UL8_selection_collapse" % eid, not bad,
           "%d prices where the successor-set change is not strictly dearer"
           % len(bad))
        ck("%s.UL8_s_star_zero" % eid,
           ta["s_star"]["value"] == "0", ta["s_star"]["value"])

        # ---- 3. the argmin-cell partition ---------------------------------
        cen = A.joint_census(va)
        cb = B.cell_census(vb)
        ck("%s.census_two_routes" % eid,
           cen["strict_cells"] == cb["strict_cells"] and
           cen["tie_cases"] == cb["tie_cases"],
           "%r vs %r" % (cen["strict_cells"], cb["strict_cells"]))
        ck("%s.partition_no_failures" % eid,
           cen["partition_failures"] == 0, cen["partition_failures"])
        anch = A.anchored_prices(va)
        acen = A.census_over(va, anch)
        ck("%s.anchored_partition_no_failures" % eid,
           acen["partition_failures"] == 0, acen["partition_failures"])
        ck("%s.anchored_grid_nonempty" % eid, len(anch) > 0, len(anch))
        # every case is exactly one of: a strict cell, a tie, or undetermined
        ck("%s.trichotomy_exhaustive" % eid,
           sum(acen["strict_cells"].values()) + acen["tie_cases"] +
           acen["undetermined_cases"] == len(anch))

        # ---- 4. selector totality and soundness ---------------------------
        snd = A.selector_soundness_census(ia, va, anch)
        ck("%s.selector_total" % eid, snd["totality_verified"])
        ck("%s.selector_sound" % eid, not snd["soundness_violations"],
           len(snd["soundness_violations"]))
        ck("%s.selector_hull_sound" % eid, not snd["hull_violations"],
           len(snd["hull_violations"]))
        v = A.select({"M": None}, va, A.unit_price())
        ck("%s.selector_abstains_underdetermined" % eid,
           v["kind"] == "ABSTAIN_UNDERDETERMINED")
        v = A.select(ia, va, (1.0,) + tuple([F(1)] * 7))
        # STEP 1 precedes STEP 2 in the frozen table, so on an environment whose
        # invariants are incomplete the underdetermined abstention fires first;
        # both are typed abstentions and neither is a silent failure.
        ck("%s.selector_abstains_ill_typed" % eid,
           v["kind"] in ("ABSTAIN_ILL_TYPED", "ABSTAIN_UNDERDETERMINED"),
           v["kind"])

        # ---- 5. neutral recovery ------------------------------------------
        nr = A.neutral_recovery_census(ea, ia, va, anch)
        nb = B.recovery(eb, ib, vb)
        ck("%s.recovery_no_disagreement" % eid,
           not nr["regime_disagreements"],
           "%d disagreements" % len(nr["regime_disagreements"]))
        ck("%s.recovery_two_routes_space" % eid,
           nr["tuples_enumerated"] == nb["space_size"],
           "%d vs %d" % (nr["tuples_enumerated"], nb["space_size"]))

    # ---- 6. compatibility matrix is reported as a matrix, not a partition --
    cm = A.compatibility_matrix()
    cb = B.compatibility()
    ck("compatibility_two_routes",
       cm["compatible"] == cb["compatible"] and
       cm["exclusive"] == cb["exclusive"],
       "%r vs %r" % (cm["compatible"], cb["compatible"]))
    ck("compatibility_is_not_claimed_a_partition",
       cm["is_a_partition"] is False and cm["compatible"] > 0,
       "%d compatible pairs" % cm["compatible"])
    ck("compatibility_pairs_21", cm["pairs"] == 21, cm["pairs"])

    # ---- 7. hostiles -------------------------------------------------------
    recs = [(ea, ia, va) for (ea, ia, va, eb, ib, vb) in inv_pairs]
    host = A.hostiles(recs)
    missed = [h["id"] for h in host if h["detected"] is False]
    na = [h["id"] for h in host if h["detected"] is None]
    ck("hostiles_none_missed", not missed, missed)
    ck("hostiles_none_inapplicable", not na, na)
    ck("hostiles_count_14", len(host) == 14, len(host))

    # ---- 8. nulls ----------------------------------------------------------
    nl = A.nulls(recs)
    ck("null_i_true_beats_all",
       nl["null_i"]["nulls_at_or_above_true"] == 0 and
       nl["null_i"]["true_hits"] > 0,
       json.dumps(nl["null_i"]))
    ck("null_i_non_vacuous", nl["null_i"]["non_vacuous"])
    ck("null_ii_no_hits", nl["null_ii"]["hits"] == 0,
       json.dumps(nl["null_ii"]))
    ck("null_ii_non_vacuous", nl["null_ii"]["non_vacuous"])

    # ---- 9. held-out predictions ------------------------------------------
    ho = A.heldout_evaluation()
    for k in ("HO_P1", "HO_P2", "HO_P3", "HO_P4"):
        ck("heldout_%s_evaluated" % k, ho[k]["verdict"] in ("HIT", "MISS"),
           ho[k]["verdict"])
    ck("heldout_P1_hit", ho["HO_P1"]["verdict"] == "HIT",
       json.dumps(ho["HO_P1"])[:200])
    ck("heldout_P3_hit", ho["HO_P3"]["verdict"] == "HIT")
    ck("heldout_P4_hit", ho["HO_P4"]["verdict"] == "HIT")

    # ---- 10. the JSON files, which do not exist when the executor runs ----
    scr = A.name_freedom_screen((".json",))
    ck("json_screen_clean", scr["verdict"] == "CLEAN_AT_REGISTERED_AUDIT_SCOPE",
       json.dumps(scr["unmatched_hits"])[:300])
    scr2 = A.name_freedom_screen((".py", ".md"))
    ck("py_md_screen_clean",
       scr2["verdict"] == "CLEAN_AT_REGISTERED_AUDIT_SCOPE",
       json.dumps(scr2["unmatched_hits"])[:300])
    strict = ("update_law_regimes_v1.py", "oracle_update_law_regimes_v1.py",
              "test_update_law_regimes_v1.py", "CORE.md")
    for f in strict:
        pth = os.path.join(HERE, f)
        if not os.path.exists(pth):
            ck("strictly_clean_%s_present" % f, False, "missing")
            continue
        txt = A.python_screen_text(pth) if f.endswith(".py") else \
            open(pth, "r").read()
        hits = A.denylist_hits_in_text(txt)
        ck("strictly_clean_%s" % f, not hits, hits)

    # ---- 11. exact arithmetic discipline ----------------------------------
    ok = True
    for (ea, ia, va, eb, ib, vb) in inv_pairs:
        for rid, vec in va.items():
            if vec is None:
                continue
            for x in vec:
                if not isinstance(x, int):
                    ok = False
    ck("coefficients_are_exact_integers", ok)
    ck("prices_are_exact_rationals",
       all(isinstance(x, F) for p in A.JOINT_PRICES for x in p))
    ck("eps_is_exact", isinstance(A.EPS, F) and A.EPS == F(1, 4))

    # ---- 12. receipts, if present -----------------------------------------
    rp = os.path.join(HERE, "RESULT_V1.json")
    if os.path.exists(rp):
        r = json.load(open(rp))
        ck("receipt_freeze_commit_pinned",
           r.get("freeze_commit", "").startswith("6e42ccd2"))
        ck("receipt_claim_ceiling",
           "REGIME_CONDITIONS_AND_PROSPECTIVE_SELECTOR" in
           r.get("claim_ceiling", ""))
        ck("receipt_fingerprint_matches_route_B",
           r["scope_fingerprint"] == fb)
    op = os.path.join(HERE, "ORACLE_RESULT_V1.json")
    if os.path.exists(op):
        o = json.load(open(op))
        ck("oracle_receipt_fingerprint", o["scope_fingerprint"] == fa)

    report()


def report():
    bad = [c for c in CHECKS if not c["ok"]]
    for c in bad:
        print("FAIL  %s  %s" % (c["name"], c["detail"]))
    print("%d checks, %d green, %d red" % (len(CHECKS),
                                           len(CHECKS) - len(bad), len(bad)))
    if not bad:
        print("ALL GREEN")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
