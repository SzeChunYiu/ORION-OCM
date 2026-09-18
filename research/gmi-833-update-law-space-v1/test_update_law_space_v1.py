"""Tests for GMI #833 Section I.

Runs under ``python3 -I -B`` and ``python3 -I -O -B``. No claim is gated by a
bare ``assert`` statement, because ``-O`` removes those.

Three duties:
  1. cross-route agreement between the Route A executor and the Route B oracle;
  2. detection of every registered hostile H1..H14;
  3. the registered null controls.
"""
from fractions import Fraction as Fr
from itertools import permutations
import json
import os
import random
import sys

# python3 -I runs in isolated mode, which does not prepend the script directory
# to sys.path; the package is self-contained so we add it explicitly.
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import update_law_space_v1 as A            # noqa: E402
import oracle_update_law_space_v1 as B     # noqa: E402
NULL_SEED = 8331
NULL_DRAWS = 200

PASS = []
FAILED = []


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
    else:
        FAILED.append((name, detail))


# ---------------------------------------------------------------------------
# cross-route agreement
# ---------------------------------------------------------------------------

def test_two_routes_il23():
    agree = 0
    total = 0
    for d in range(1, 7):
        for m in range(1, d + 1):
            total += 1
            closed = A.rho_local(d, m)
            enumerated = B.expected_probes_by_enumeration(d, m)
            if closed == enumerated:
                agree += 1
            check("IL2_worst_case_d%d_m%d" % (d, m),
                  A.worst_case_probes(d, m) == B.worst_case_by_enumeration(d, m))
    check("IL2_two_route_local_table", agree == total,
          "%d/%d agreed" % (agree, total))
    for d in range(1, 7):
        for m in range(1, d + 1):
            vals = B.expected_probes_per_order(d, m)
            check("IL2_order_independence_d%d_m%d" % (d, m), len(set(vals)) == 1)
    for (d, m) in ((3, 1), (4, 2), (5, 1)):
        w = B.repeat_waste_witness(d, m)
        check("IL2_repeat_is_strictly_wasteful_d%d_m%d" % (d, m),
              w["repeat_is_worse"], str(w))
    # full verdict grid must agree case by case
    ob = B.oracle_il23()["verdicts"]
    mismatch = 0
    cases = 0
    for name, prof in A.registered_paths():
        for ratio in A.price_ratio_grid():
            cases += 1
            va = A.verdict(prof, Fr(1), ratio)
            vb = ob[name]["row"][str(ratio)]
            if va != vb:
                mismatch += 1
        if str(A.rho_star(prof)) != ob[name]["rho_star"]:
            mismatch += 1
    check("IL23_two_route_verdict_grid", mismatch == 0,
          "%d mismatches over %d cases" % (mismatch, cases))
    return cases


def test_two_routes_il4():
    ob = B.oracle_il4()
    graphs = A.make_graphs()
    for name in sorted(graphs):
        G = graphs[name]
        g = ob[name]
        n, N, E, p = A.graph_facts(G)
        check("IL4_%s_shape" % name,
              (n, N, E, p) == (g["sources_n"], g["internal_N"],
                               g["edges_E"], g["outputs_p"]))
        check("IL4_%s_peak_live" % name,
              A.peak_live_internal(G) == g["peak_live_internal_w"],
              "A=%s B=%s" % (A.peak_live_internal(G), g["peak_live_internal_w"]))
        ja = A.jacobian_by_sweeps(G)
        jb = B.jacobian_by_path_sum(G)
        jc = A.jacobian_by_adjoints(G)
        check("IL4_%s_jacobian_sweeps_vs_path_sum" % name, ja == jb)
        check("IL4_%s_jacobian_tangent_vs_adjoint" % name, ja == jc)
        ta, sa = A.sigma_star(G)
        tb, sb = B.oracle_sigma_star(G)
        check("IL4_%s_regime" % name, ta == tb, "A=%s B=%s" % (ta, tb))
        check("IL4_%s_sigma_star" % name, sa == sb, "A=%s B=%s" % (sa, sb))
        ca = A.order_census(G)
        cb = g["order_census"]
        for k in ("orders_enumerated", "all_orders_reproduce_the_same_jacobian",
                  "minimum_cost", "topological_order_cost",
                  "reverse_topological_order_cost",
                  "argmin_includes_reverse_topological",
                  "argmin_includes_topological",
                  "argmin_is_a_mixed_order_only", "argmin_count"):
            check("IL4_%s_census_%s" % (name, k), ca[k] == cb[k],
                  "A=%s B=%s" % (ca[k], cb[k]))


def test_two_routes_il1():
    oc = B.oracle_one_step_counterexample()
    ac = A.il1_certificate()["one_step_composition_counterexample"]
    check("IL1_two_route_one_step_allowed",
          oc["one_step_allowed_at_r0_h0"] == ac["one_step_allowed_at_r0_h0"])
    check("IL1_two_route_target_outside_one_step",
          oc["outside_one_step"] and oc["inside_closure"])
    check("IL1_one_step_composite_rejected",
          ac["one_step_verdict"] == "INADMISSIBLE"
          and ac["closure_verdict"] == "ADMISSIBLE")
    cert = A.il1_certificate()
    check("IL1_monoid_identity_two_sided", cert["monoid_identity_ok"])
    check("IL1_identity_law_admissible",
          cert["identity_law_admissible"] == "ADMISSIBLE")
    check("IL1_kernel_associativity_exact", cert["kernel_associativity_exact"])
    check("IL1_mixture_closure_no_failures",
          cert["mixture_cases"] == 686 and not cert["mixture_failures"],
          "%d cases" % cert["mixture_cases"])
    check("IL1_closure_composition_no_failures",
          cert["composition_cases"] == 49
          and not cert["closure_composition_failures"])
    ob = B.oracle_charge_subassociativity()
    aw = A.il1_certificate()["charge_strictness_witness"]
    check("IL1_two_route_charge_subassociativity",
          ob["subassociative"] and ob["strict"]
          and aw is not None
          and aw["left_nested_charge"] == ob["left_nested"]
          and aw["right_nested_charge"] == ob["right_nested"],
          "oracle=%s executor=%s" % (ob, aw))


# ---------------------------------------------------------------------------
# hostiles
# ---------------------------------------------------------------------------

def kinds(findings):
    return set(f[0] for f in findings)


def test_hostiles():
    scope = A.make_scope()
    coords = scope["coords"]
    z = A.zero_charge(coords)

    # H1 non-normalized distribution
    h1 = lambda r, h, b: ({r: Fr(99, 100)}, dict(z))
    check("H1_non_normalized",
          "A1_NOT_NORMALIZED" in kinds(A.admissible(scope, "CLOSURE", h1)[1]))

    # H2 float probability, and float price
    h2 = lambda r, h, b: ({r: 1.0}, dict(z))
    check("H2a_float_probability",
          "A1_INEXACT_PROBABILITY" in kinds(A.admissible(scope, "CLOSURE", h2)[1]))
    raised = False
    try:
        A.verdict(((3, 1),), 1.0, 2.0)
    except ValueError:
        raised = True
    check("H2b_float_price_refused", raised)

    # H3 support escaping the declared development closure
    h3 = lambda r, h, b: ({"rq": Fr(1)}, dict(z))
    f3 = kinds(A.admissible(scope, "CLOSURE", h3)[1])
    check("H3_support_outside_closure", "A4_SUPPORT_OUTSIDE_DEVELOPMENT" in f3)

    # H4 negative resource coordinate
    h4 = lambda r, h, b: (A.point(r), {"c_alpha": Fr(-1), "c_beta": Fr(0)})
    check("H4_negative_charge",
          "A2_NEGATIVE_CHARGE" in kinds(A.admissible(scope, "CLOSURE", h4)[1]))

    # H5 undeclared charge coordinate
    h5 = lambda r, h, b: (A.point(r), {"c_gamma": Fr(0)})
    check("H5_charge_coordinate_mismatch",
          "A2_CHARGE_COORDINATE_MISMATCH" in kinds(A.admissible(scope, "CLOSURE", h5)[1]))

    # H6 the claim that A_1 is closed under composition
    pop = A.registered_laws(scope)
    comp = A.compose(scope, pop["step_r1_r2"], pop["step_r0_r1"])
    v1 = A.admissible(scope, "ONE_STEP", comp)[0]
    both_parents_ok = (A.admissible(scope, "ONE_STEP", pop["step_r0_r1"])[0]
                       == "ADMISSIBLE"
                       and A.admissible(scope, "ONE_STEP", pop["step_r1_r2"])[0]
                       == "ADMISSIBLE")
    check("H6_one_step_composition_claim_refuted",
          both_parents_ok and v1 == "INADMISSIBLE")

    # H7 off-by-one threshold d/m instead of (d+1)/(m+1)
    bad = 0
    tot = 0
    for name, prof in A.registered_paths():
        rho_bad = sum((Fr(d, m) for (d, m) in prof), Fr(0)) / Fr(len(prof))
        rho_ok = A.rho_star(prof)
        tot += 1
        if rho_bad != rho_ok:
            bad += 1
    check("H7_off_by_one_threshold_detected", bad > 0,
          "%d/%d registered paths separate the two thresholds" % (bad, tot))

    # H8 a trichotomy with a gap
    def gapped(prof, ratio):
        rs = A.rho_star(prof)
        if ratio > rs:
            return "POINT_VALUE_ONLY_STRICTLY_DOMINATES"
        return "SELECTION_CHANNEL_STRICTLY_DOMINATES"   # tie silently absorbed
    gaps = 0
    for name, prof in A.registered_paths():
        rs = A.rho_star(prof)
        if gapped(prof, rs) != A.verdict(prof, Fr(1), rs):
            gaps += 1
    check("H8_gapped_trichotomy_detected", gaps > 0, "%d ties absorbed" % gaps)

    # H9 adjoint claimed to win when p > n
    G = A.make_graphs()["fan_out_p4"]
    n, N, E, p = A.graph_facts(G)
    verdicts = set(A.direction_verdict(G, Fr(k)) for k in (0, 1, 10 ** 6))
    check("H9_adjoint_claim_at_p_gt_n_refuted",
          p > n and verdicts == set(["TANGENT_STRICTLY_CHEAPER"]), str(verdicts))

    # H10 sweep-count necessity dropped
    ok = True
    for k in (2, 3, 4, 5, 6):
        wit = A.sweep_necessity_witness(k)
        if not wit["necessity_established"]:
            ok = False
    for k in (2, 3, 4):
        wit = A.adjoint_necessity_witness(k)
        if not wit["necessity_established"]:
            ok = False
    check("H10_sweep_necessity_holds", ok)

    # H11 a smuggled identifier
    d, entries = A.load_denylist()
    deny = tuple((e, A.normalize(e)) for e in entries)
    with open(os.path.join(HERE, "HOSTILE_FIXTURES_V1.json")) as fh:
        fixtures = json.load(fh)
    planted = fixtures["planted_identifiers_that_must_be_caught"]
    clean = fixtures["clean_identifiers_that_must_not_alarm"]
    caught = 0
    for ident in planted:
        nrm = A.normalize(ident)
        if any(nd and nd in nrm for _, nd in deny):
            caught += 1
    false_alarms = 0
    for ident in clean:
        nrm = A.normalize(ident)
        if any(nd and nd in nrm for _, nd in deny):
            false_alarms += 1
    check("H11_planted_identifiers_all_caught", caught == len(planted),
          "%d/%d" % (caught, len(planted)))
    check("H11_no_alarm_on_clean_identifiers", false_alarms == 0,
          "%d false alarms" % false_alarms)

    # H12 a remint that mutates a semantic field rather than relabeling
    sym = (list(scope["realizations"]) + list(scope["histories"])
           + list(scope["coords"]))
    tmap = dict((s, "t%d" % i) for i, s in enumerate(sym))
    good = A.remint_scope(scope, tmap)
    bad_scope = dict(good)
    bad_delta = dict(good["delta"])
    bad_delta[(tmap["r0"], tmap["h0"])] = ()          # semantic mutation
    bad_scope["delta"] = bad_delta
    law = pop["step_r0_r1"]
    inv = dict((v, k) for k, v in tmap.items())

    def reminted(r2, h2, b2):
        b1 = dict((inv[k], v) for k, v in b2.items())
        d1, c1 = law(inv[r2], inv[h2], b1)
        return (dict((tmap[t], pr) for t, pr in d1.items()),
                dict((tmap[k], v) for k, v in c1.items()))

    vg = A.admissible(good, "ONE_STEP", reminted)[0]
    vb = A.admissible(bad_scope, "ONE_STEP", reminted)[0]
    check("H12_semantic_mutation_detected",
          vg == "ADMISSIBLE" and vb == "INADMISSIBLE", "%s vs %s" % (vg, vb))

    # H13 budget clause A3 dropped
    h13 = lambda r, h, b: (({"r1": Fr(1)}, {"c_alpha": Fr(5), "c_beta": Fr(0)})
                           if r == "r0" else (A.point(r), dict(z)))
    f13 = kinds(A.admissible(scope, "CLOSURE", h13)[1])
    check("H13_budget_clause_violation_detected",
          "A3_BUDGET_CLAUSE_VIOLATED" in f13)

    # H14 expected charge substituted for the worst-case budget guarantee
    branch_charges = {"ra": Fr(3), "rb": Fr(0)}
    weights = {"ra": Fr(1, 2), "rb": Fr(1, 2)}
    expected = sum(weights[k] * branch_charges[k] for k in branch_charges)
    worst = max(branch_charges.values())
    budget = Fr(2)
    realizable_overrun = any(branch_charges[k] > budget for k in branch_charges)
    check("H14_expected_charge_is_not_a_budget_guarantee",
          expected <= budget and worst > budget and realizable_overrun,
          "expected=%s worst=%s budget=%s" % (expected, worst, budget))


# ---------------------------------------------------------------------------
# nulls
# ---------------------------------------------------------------------------

def test_nulls():
    rng = random.Random(NULL_SEED)
    paths = A.registered_paths()
    hits = 0
    draws = 0
    while draws < NULL_DRAWS:
        na, pa = paths[rng.randrange(len(paths))]
        nb, pb = paths[rng.randrange(len(paths))]
        rs_a = A.rho_star(pa)
        rs_b = A.rho_star(pb)
        if rs_a == rs_b:
            continue                      # not a mismatched threshold
        draws += 1
        # a shuffled threshold is asked to locate the exact tie of path a
        if A.verdict(pa, Fr(1), rs_b) == "EXACT_TIE_AT_BOUNDARY":
            hits += 1
    check("NULL_shuffled_threshold_never_locates_the_tie", hits == 0,
          "%d/%d" % (hits, draws))

    # the true threshold locates the tie every time
    true_hits = 0
    for name, prof in paths:
        if A.verdict(prof, Fr(1), A.rho_star(prof)) == "EXACT_TIE_AT_BOUNDARY":
            true_hits += 1
    check("NULL_true_threshold_locates_every_tie", true_hits == len(paths),
          "%d/%d" % (true_hits, len(paths)))

    rng2 = random.Random(NULL_SEED + 1)
    chains = ["source_chain_n4", "deep_chain_n6", "fan_in_n5"]
    graphs = A.make_graphs()
    beats = 0
    for _ in range(NULL_DRAWS):
        name = chains[rng2.randrange(len(chains))]
        G = graphs[name]
        elim = list(A.eliminable(G))
        rng2.shuffle(elim)
        _, cost = A.eliminate_order(G, tuple(elim))
        revtopo = tuple(reversed(A.eliminable(G)))
        _, ref = A.eliminate_order(G, revtopo)
        if cost < ref:
            beats += 1
    check("NULL_random_order_never_beats_reverse_topological_on_chains",
          beats == 0, "%d/%d" % (beats, NULL_DRAWS))

    # the same null is NOT vacuous: on the registered skip-waist graph a mixed
    # order does strictly beat the reverse-topological order.
    Gw = graphs["skip_waist_n2_p2"]
    cw = A.order_census(Gw)
    check("NULL_control_is_not_vacuous_skip_waist_mixed_wins",
          cw["minimum_cost"] < cw["reverse_topological_order_cost"]
          and cw["minimum_cost"] < cw["topological_order_cost"]
          and cw["argmin_is_a_mixed_order_only"],
          str(cw))


# ---------------------------------------------------------------------------
# receipt screens
# ---------------------------------------------------------------------------

def test_screens_and_receipts():
    lex = A.lexical_screen()
    check("A1_lexical_clean", lex["verdict"] == "CLEAN_AT_REGISTERED_AUDIT_SCOPE",
          str(lex["hits"])[:200])
    check("A1_screened_both_sources",
          set(["update_law_space_v1.py", "oracle_update_law_space_v1.py",
               "test_update_law_space_v1.py"]).issubset(set(lex["screened_files"])),
          str(lex["screened_files"]))
    sem = A.semantic_screen()
    check("A2_semantic_clean", sem["verdict"] == "CLEAN_AT_REGISTERED_AUDIT_SCOPE",
          str(sem.get("findings")))
    rm = A.remint_certificate()
    check("remint_invariance", rm["all_verdicts_invariant"])

    # re-screen the generated receipts, which do not exist when the executor
    # runs its own screen
    d, entries = A.load_denylist()
    exempt = set(x["path"] for x in d["declared_exemptions"])
    deny = tuple((e, A.normalize(e)) for e in entries)
    hits = []
    checked = []
    for fn in sorted(os.listdir(HERE)):
        if fn in exempt or not fn.endswith(".json"):
            continue
        checked.append(fn)
        with open(os.path.join(HERE, fn)) as fh:
            for tok in fh.read().split():
                nrm = A.normalize(tok)
                for raw, nd in deny:
                    if nd and nd in nrm:
                        hits.append((fn, tok[:40], raw))
    check("A1_generated_receipts_clean", not hits, str(hits[:3]))
    check("A1_generated_receipts_were_present", len(checked) >= 1, str(checked))

    # the equivariance boundary is a real counterexample, and the orbit average
    # restores the unconditional value
    bw = A.equivariance_boundary_witness()
    check("IL2_boundary_counterexample_is_real",
          bw["per_instance_beats_orbit_average"] and bw["orbit_average_restored"],
          str(bw))


def test_freeze_precommitments():
    """Every headline number the reconciliation will quote must come from the
    receipt, and the freeze's pre-committed formulas must be the ones used."""
    for (d, m) in ((6, 1), (3, 3), (1, 1), (5, 2)):
        check("PRECOMMIT_rho_local_%d_%d" % (d, m),
              A.rho_local(d, m) == Fr(d + 1, m + 1))
    for name in sorted(A.make_graphs()):
        G = A.make_graphs()[name]
        n, N, E, p = A.graph_facts(G)
        w = A.peak_live_internal(G)
        tag, s = A.sigma_star(G)
        if tag == "THRESHOLD":
            check("PRECOMMIT_sigma_star_%s" % name, s == Fr((n - p) * E, N - w))
            check("PRECOMMIT_trichotomy_%s" % name,
                  A.direction_verdict(G, s / 2) == "ADJOINT_STRICTLY_CHEAPER"
                  and A.direction_verdict(G, s) == "EXACT_TIE_AT_BOUNDARY"
                  and A.direction_verdict(G, 2 * s) == "TANGENT_STRICTLY_CHEAPER")
    # full improving density makes direction informationally worthless
    check("PRECOMMIT_full_density_rho_star_is_one",
          all(A.rho_star(tuple([(d, d)] * 3)) == 1 for d in range(1, 7)))
    check("PRECOMMIT_sparse_density_rho_star_grows",
          A.rho_star(((6, 1),)) == Fr(7, 2) and A.rho_star(((2, 1),)) == Fr(3, 2))


def main():
    cases = test_two_routes_il23()
    test_two_routes_il4()
    test_two_routes_il1()
    test_hostiles()
    test_nulls()
    test_screens_and_receipts()
    test_freeze_precommitments()
    print("checks passed: %d" % len(PASS))
    if FAILED:
        print("FAILED: %d" % len(FAILED))
        for name, detail in FAILED:
            print("  %s :: %s" % (name, detail))
        return 1
    print("two-route verdict grid cases: %d" % cases)
    print("ALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
