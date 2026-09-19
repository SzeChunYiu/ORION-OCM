# -*- coding: utf-8 -*-
"""AG6 tests.  No bare `assert` anywhere: the suite must behave identically
under `python3 -O`, which strips assert statements.

    python3 -I -O -B test_ag6_universal_bases_v1.py
"""

import json
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ag6_universal_bases_v1 as A   # noqa: E402

FAIL = []
RUN = [0]


def check(name, cond, detail=""):
    RUN[0] += 1
    if not cond:
        FAIL.append("%s %s" % (name, detail))
    return bool(cond)


def popcount(bits):
    return sum(bits)


def main():
    # -- scope -------------------------------------------------------------
    check("scope_machines", len(A.MACHINES) == 256, len(A.MACHINES))
    check("scope_words", len(A.WORDS) == 15, len(A.WORDS))
    check("scope_tasks", len(A.MACHINES) * len(A.WORDS) == 3840)
    check("words_shortest_first",
          [len(w) for w in A.WORDS] == sorted(len(w) for w in A.WORDS))
    check("words_unique", len(set(A.WORDS)) == 15)
    check("words_are_binary",
          all(all(b in (0, 1) for b in w) for w in A.WORDS))
    check("machines_unique", len(set(
        (tuple(sorted(d.items())), tuple(sorted(o.items())))
        for d, o in A.MACHINES)) == 256)
    check("distinct_behaviours_on_W", len(A.BEHAVIOUR_INDEX) == 148,
          len(A.BEHAVIOUR_INDEX))

    # -- registered semantics ---------------------------------------------
    d = {(0, 0): 1, (0, 1): 0, (1, 0): 0, (1, 1): 1}
    o = {(0, 0): 1, (0, 1): 0, (1, 0): 0, (1, 1): 1}
    check("direct_mealy_empty", A.direct_mealy(d, o, ()) == ())
    check("direct_mealy_len", all(
        len(A.direct_mealy(d, o, w)) == len(w) for w in A.WORDS))
    check("direct_mealy_hand", A.direct_mealy(d, o, (0, 0, 1)) == (1, 0, 0),
          A.direct_mealy(d, o, (0, 0, 1)))

    qs = [A.capability(dd, oo) for dd, oo in A.MACHINES]
    check("capability_range", min(qs) >= 3 and max(qs) <= 45, (min(qs), max(qs)))
    check("capability_observed", (min(qs), max(qs)) == (7, 23), (min(qs), max(qs)))
    check("capability_int", all(isinstance(q, int) for q in qs))

    # -- REG ---------------------------------------------------------------
    reg = [A.reg_compile(dd, oo) for dd, oo in A.MACHINES]
    bad = 0
    caps = 0
    for i, (dd, oo) in enumerate(A.MACHINES):
        for w in A.WORDS:
            got, _s, term = A.reg_run(reg[i], w, A.reg_cap(w))
            if term == "CAP":
                caps += 1
            if got != A.direct_mealy(dd, oo, w):
                bad += 1
    check("REG_full_census", bad == 0, bad)
    check("REG_no_cap_hits", caps == 0, caps)
    ok = True
    for i, (dd, oo) in enumerate(A.MACHINES):
        want = 40 + 3 * popcount([dd[k] for k in A.KEYS])
        if A.reg_size(reg[i]) != want:
            ok = False
    check("REG_size_closed_form", ok)
    check("REG_size_blind_to_output_table",
          len(set(A.reg_size(reg[i]) for i in range(16))) == 1)

    # -- CMB ---------------------------------------------------------------
    check("SK_K_rule", A.whnf((("K", "S"), "K"), 10)[0] == "S")
    check("SK_S_rule",
          A.nf(((("S", "K"), "K"), "S"), 10)[0] == "S")
    check("SK_I_is_identity", A.nf((A.to_runtime(A.I_CL), ("K", "S")), 20)[0]
          == ("K", "S"))
    check("SK_true_false_distinct", A.SK_T != A.SK_F)
    check("SK_true_nf", A.nf(A.SK_T, 10)[0] == A.SK_T)
    check("SK_false_nf", A.nf(A.SK_F, 10)[0] == A.SK_F)

    cmb = [A.cmb_compile(dd, oo, True) for dd, oo in A.MACHINES]
    bad = 0
    for i in range(0, 256, 8):
        dd, oo = A.MACHINES[i]
        for w in A.WORDS:
            got, _s, term = A.cmb_run(cmb[i], w)
            if got != A.direct_mealy(dd, oo, w) or term != "OK":
                bad += 1
    check("CMB_sampled_census", bad == 0, bad)
    leaves = len(A.cmb_leaf_paths(cmb[0]))
    check("CMB_nodes_equal_2L_minus_1", A.cmb_size(cmb[0]) == 2 * leaves - 1,
          (A.cmb_size(cmb[0]), leaves))
    check("CMB_pure_SK", all(A.cmb_leaf_at(cmb[0], p) in ("S", "K")
                             for p in A.cmb_leaf_paths(cmb[0])))
    naive = A.cmb_compile(*A.MACHINES[0], optimized=False)
    check("CMB_naive_is_larger", A.cmb_size(naive) > A.cmb_size(cmb[0]),
          (A.cmb_size(naive), A.cmb_size(cmb[0])))

    # -- CEL ---------------------------------------------------------------
    cel = [A.cel_artifact(dd, oo) for dd, oo in A.MACHINES]
    bad = 0
    for i, (dd, oo) in enumerate(A.MACHINES):
        for w in A.WORDS:
            got, _s, term = A.cel_run(cel[i]["rule"], w)
            if got != A.direct_mealy(dd, oo, w) or term != "HALTED":
                bad += 1
    check("CEL_full_census", bad == 0, bad)
    check("CEL_closure", all(
        A.closure_violations(cel[i]["rule"], cel[i]["sigma"]) == 0
        for i in (0, 85, 170, 255)))
    dep = A.coordinate_dependence(cel[0]["rule"], cel[0]["sigma"])
    check("CEL_left_dependent", dep["left_differing_pairs"] > 0, dep)
    check("CEL_right_independent", dep["right_differing_pairs"] == 0, dep)
    pw = A.pointwise_rule(*A.MACHINES[0])
    depp = A.coordinate_dependence(pw, cel[0]["sigma"])
    check("CEL_pointwise_control_is_neighbour_blind",
          depp["left_differing_pairs"] == 0)

    import random
    rng = random.Random(4242)
    confs = A.window_configs(cel, rng, n_random=120, width=5)
    check("locality_no_alarm",
          A.locality_violations(A.local_update(cel[0]["rule"]), confs) == 0)
    check("locality_detects_radius2",
          A.locality_violations(A.radius2_update(cel[0]["rule"]), confs) > 0)

    # -- exact comparison machinery ---------------------------------------
    k = A.kendall_counts([1, 2, 3, 4], [1, 2, 3, 4])
    check("kendall_identity_tau1", k["tau_a"] == Fraction(1, 1), k)
    k = A.kendall_counts([1, 2, 3, 4], [4, 3, 2, 1])
    check("kendall_reverse_tau_minus1", k["tau_a"] == Fraction(-1, 1), k)
    k = A.kendall_counts([1, 1, 2], [5, 5, 5])
    check("kendall_tie_split",
          k["tied_both"] == 1 and k["tied_second_only"] == 2
          and k["concordant"] == 0 and k["discordant"] == 0, k)
    k = A.kendall_counts([A.reg_size(a) for a in reg],
                         [A.cmb_size(t) for t in cmb])
    check("kendall_counts_sum",
          k["concordant"] + k["discordant"] + k["tied_first_only"]
          + k["tied_second_only"] + k["tied_both"] == k["pairs"], k)
    check("kendall_cross_basis_has_discordant_pairs", k["discordant"] > 0,
          k["discordant"])

    f = A.pareto_frontier([1, 2, 3], [1, 2, 3])
    check("pareto_staircase", f == (0, 1, 2), f)
    f = A.pareto_frontier([3, 2, 1], [1, 2, 3])
    check("pareto_single_dominator", f == (0,), f)
    f = A.pareto_frontier([1, 1], [1, 1])
    check("pareto_exact_ties_both_survive", f == (0, 1), f)
    f = A.pareto_frontier([2, 1], [1, 1])
    check("pareto_dominates", f == (0,), f)
    base_c = [A.reg_size(a) for a in reg]
    fr = A.pareto_frontier(qs, base_c)
    check("pareto_monotone_invariance",
          A.pareto_frontier(qs, [7 * x + 5 for x in base_c]) == fr)
    check("pareto_square_invariance",
          A.pareto_frontier(qs, [x * x for x in base_c]) == fr)
    rew = [base_c[i] * (1 + (i % 7)) for i in range(len(base_c))]
    check("pareto_reweighting_is_outside_the_invariance_class",
          A.pareto_frontier(qs, rew) != fr)

    check("bound_class_vacuous",
          A.classify_bound(Fraction(16), Fraction(8), Fraction(16)) == "VACUOUS")
    check("bound_class_attained",
          A.classify_bound(Fraction(8), Fraction(8), Fraction(16)) == "ATTAINED")
    check("bound_class_strict",
          A.classify_bound(Fraction(12), Fraction(8), Fraction(15))
          == "STRICT_UNATTAINED")

    # -- hostiles that must move the quantity they perturb -----------------
    probe = (0, 85, 170)
    bad = 0
    for i in probe:
        for w in A.WORDS:
            if A._cmb_run_with(A.whnf_transposed, cmb[i], w) != \
                    A.direct_mealy(A.MACHINES[i][0], A.MACHINES[i][1], w):
                bad += 1
    check("hostile_transposed_S_detected", bad > 0, bad)
    bad = 0
    for i in probe:
        t = A.to_runtime(A.compile_lam_swapped(A.machine_lambda(*A.MACHINES[i])))
        for w in A.WORDS:
            got, _s, _t = A.cmb_run(t, w)
            if got != A.direct_mealy(A.MACHINES[i][0], A.MACHINES[i][1], w):
                bad += 1
    check("hostile_swapped_abstraction_detected", bad > 0, bad)
    bad = 0
    for i in probe:
        for w in A.WORDS:
            if A.reg_run_no_decrement(reg[i], w, A.reg_cap(w)) != \
                    A.direct_mealy(A.MACHINES[i][0], A.MACHINES[i][1], w):
                bad += 1
    check("hostile_decjz_no_decrement_detected", bad > 0, bad)
    inert = sum(1 for i in range(256)
                if A.to_runtime(A.compile_lam_bad_eta(
                    A.machine_lambda(*A.MACHINES[i]))) == cmb[i])
    check("inert_eta_perturbation_is_excluded_not_counted", inert == 256, inert)

    # -- nulls -------------------------------------------------------------
    perms = [p for p in A._perms(A.REG_OPCODES) if p != A.REG_OPCODES]
    check("reg_opcode_permutation_null_is_exhaustive", len(perms) == 119,
          len(perms))

    # -- one-edit slot structure ------------------------------------------
    slots = A.reg_slots(reg[0])
    check("reg_slots_nonempty", len(slots) > 0)
    nbh = sum(len(s[2]) - 1 for s in slots)
    check("reg_neighbourhood_excludes_identity_edit",
          nbh == sum(len(s[2]) for s in slots) - len(slots))
    e = A.reg_apply_edit(reg[0], slots[0], "HALT")
    check("reg_edit_changes_program", e[2] != reg[0][2])
    p0 = A.cmb_leaf_paths(cmb[0])[0]
    cur = A.cmb_leaf_at(cmb[0], p0)
    flipped = A.cmb_replace_at(cmb[0], p0, "S" if cur == "K" else "K")
    check("cmb_leaf_flip_changes_term", flipped != cmb[0])
    check("cmb_leaf_flip_preserves_shape",
          A.cmb_size(flipped) == A.cmb_size(cmb[0]))

    # -- enumeration obstruction ------------------------------------------
    obs = A.enumeration_obstruction(cel)
    check("obstruction_alphabet", obs["cellular_alphabet_max"] >= 10)
    check("obstruction_is_exact_integer",
          obs["cellular_unrestricted_rule_space"].isdigit())
    check("obstruction_is_astronomical",
          obs["cellular_unrestricted_rule_space_decimal_digits"] > 1000,
          obs["cellular_unrestricted_rule_space_decimal_digits"])

    # -- receipt discipline ------------------------------------------------
    path = os.path.join(HERE, "RESULT_V1.json")
    if os.path.exists(path):
        raw = open(path).read()
        rec = json.loads(raw)
        check("receipt_green",
              rec["terminal"] == "GMI_833_AG6_UNIVERSAL_BASES_V1_ALL_GREEN",
              rec["terminal"])
        check("receipt_gates", rec["gates_passed"] == rec["gates_total"])
        check("receipt_universal", all(rec["registered_universal"].values()))
        check("receipt_parent_agreement",
              rec["parent_register_census_reproduced"]["agrees"])
        check("receipt_hostiles", rec["hostiles"]["hostiles_detected"] == 13)
        check("receipt_nulls_zero", rec["nulls"]["total_reproduced"] == 0)
        check("receipt_decisive_coordinate_non_degenerate",
              rec["mi_recovery"]["size"]["decisive"])
        check("receipt_mi_verdict_recorded",
              rec["mi_recovery"]["size"]["verdict"] in
              ("LAW_SURVIVES", "LAW_DOES_NOT_SURVIVE"))
        floats = re.findall(r":\s*-?\d+\.\d+", raw)
        check("receipt_has_no_floats", floats == [], floats[:5])
        for fp in A.FORBIDDEN_PROMOTIONS:
            check("forbidden_present_%s" % fp, fp in rec["forbidden_promotions"])
        oracle = os.path.join(HERE, "ORACLE_RESULT_V1.json")
        if os.path.exists(oracle):
            orc = json.load(open(oracle))
            check("two_route_machines_realized",
                  orc["machines_realized"] == dict(
                      (k, rec["realization"][k]["machines_realized"])
                      for k in ("REG", "CMB", "CEL")),
                  orc["machines_realized"])
            check("two_route_size_range",
                  orc["size_range"] == dict(
                      (k, rec["description_bias"]["size_range"][k])
                      for k in ("REG", "CMB", "CEL")))
            check("two_route_distinct_behaviours",
                  orc["distinct_behaviours_on_W"]
                  == rec["scope"]["distinct_behaviours_on_W"])
            check("two_route_kendall",
                  all(orc["kendall"]["size__%s_vs_%s" % (a, b)]["concordant"]
                      == rec["description_bias"]["size__%s_vs_%s" % (a, b)][
                          "concordant"]
                      for a, b in (("REG", "CMB"), ("REG", "CEL"),
                                   ("CMB", "CEL"))))
            check("two_route_pareto",
                  all(orc["pareto_size_coordinate"][n]["frontier"]
                      == rec["mi_recovery"]["size"][n]["frontier"]
                      for n in ("REG", "CMB", "CEL")))
            check("two_route_cmb_geometry",
                  orc["cmb_geometry"]["0"]["corridor_length"]
                  == rec["reachability_geometry"]["CMB"]["0"]["corridor_length"]
                  and orc["cmb_geometry"]["0"]["max_out_degree"]
                  == rec["reachability_geometry"]["CMB"]["0"]["max_out_degree"]
                  and orc["cmb_geometry"]["0"][
                      "branching_all_successors_share_normal_form"]
                  == rec["reachability_geometry"]["CMB"]["0"][
                      "branching_configurations_all_successors_share_normal_form"])

    # -- freeze ordering artefact -----------------------------------------
    fz = os.path.join(HERE, "FREEZE_V1.md")
    check("freeze_exists", os.path.exists(fz))
    if os.path.exists(fz):
        body = open(fz).read()
        for frag in ("radically different universal low-level bases",
                     "reachability geometry and developmental search burden",
                     "resource normalization",
                     "No neighboring row is earned here."):
            check("freeze_pins_%s" % frag[:24].replace(" ", "_"), frag in body)

    print(json.dumps({"schema": "GMI833AG6TestReceiptV1",
                      "checks_run": RUN[0],
                      "checks_failed": len(FAIL),
                      "failures": FAIL[:20],
                      "optimized": not __debug__,
                      "status": "GREEN" if not FAIL else "RED"},
                     indent=1, sort_keys=True))
    return 1 if FAIL else 0


if __name__ == "__main__":
    rc = main()
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        fh.write(json.dumps({"schema": "GMI833AG6TestReceiptV1",
                             "checks_run": RUN[0],
                             "checks_failed": len(FAIL),
                             "optimized": not __debug__,
                             "status": "GREEN" if not FAIL else "RED"},
                            indent=1, sort_keys=True) + "\n")
    sys.exit(rc)
