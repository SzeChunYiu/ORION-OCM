#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for gmi-833-developmental-reuse-v1.

Runnable under both `python3 -I -B` and `python3 -I -O -B`; every check uses
`unittest` assertions, never the bare `assert` statement (which `-O` strips).
Stdlib only.
"""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import developmental_reuse_v1 as A          # noqa: E402
import independent_oracle_v1 as B           # noqa: E402

with open(os.path.join(HERE, "FROZEN_FIXTURES_V1.json"), "r") as _fh:
    FX = json.load(_fh)

BASE = FX["base_tokens"]
KAPPA = FX["kappa_primary"]

# computed once; the SD census is the expensive part
_CENSUS = A.sd_census(FX)
_REP1 = A.rep1_census(FX)
_SD1 = A.sd_matrix(FX, _CENSUS)
_SD2 = A.sd_mechanism(FX, _CENSUS)
_SD2["SD_2d_target_independence"] = A.sd_target_independence(FX)
_SD2["SD_2e_mut_objective_invariance"] = A.sd_mut_objective_invariance(_CENSUS)
_SD2["SD_2b_scaling"] = A.sd2b_scaling(FX)
_SD3 = A.sd_nas_and_meta(FX, _CENSUS)
_REP3P = A.rep3_instance(FX["rep3"]["primary"]["word"], FX["rep3"]["library"], BASE)
_REP3N = A.rep3_instance(FX["rep3"]["near_miss_hostile"]["word"],
                         FX["rep3"]["library"], BASE)
_LIB = dict((k, tuple(v)) for k, v in FX["rep2"]["library"].items())
_HP = A.rep2_portfolio(FX["rep2"]["heldout_reuse_positive"], _LIB, BASE, KAPPA)
_HM = A.rep2_portfolio(FX["rep2"]["heldout_unrelated_control"], _LIB, BASE, KAPPA)
_ALL = A.rep2_portfolio(
    FX["rep2"]["heldout_reuse_positive"] + FX["rep2"]["heldout_unrelated_control"],
    _LIB, BASE, KAPPA)
_HOST = A.hostiles(FX, _ALL, _REP3P, _REP3N)


class TestSubstrate(unittest.TestCase):
    """Exactness of the inherited burden machinery."""

    def test_no_float_anywhere_in_the_committed_receipts(self):
        import ci_gate_v1
        for name in ("RESULT_V1.json", "ORACLE_RESULT_V1.json"):
            path = os.path.join(HERE, name)
            if not os.path.exists(path):
                self.skipTest(name + " not yet produced")
            with open(path, "r") as fh:
                blob = json.load(fh)
            self.assertEqual(ci_gate_v1.find_floats(blob), [], name)

    def test_no_float_in_the_live_computation(self):
        import ci_gate_v1
        for label, node in (("rep1", _REP1), ("rep3", _REP3P), ("rep2", _ALL),
                            ("sd1", _SD1), ("sd2", _SD2), ("sd3", _SD3)):
            self.assertEqual(ci_gate_v1.find_floats(node), [], label)

    def test_phi_matches_geometric_closed_form(self):
        for n in (2, 3, 4, 5):
            for ell in range(0, 10):
                self.assertEqual(A.phi(n, ell), B.phi_closed(n, ell))

    def test_burden_bracket_holds_for_every_registered_target(self):
        g1 = A.Grammar(BASE, A._macro_list(_LIB))
        for t in FX["rep2"]["heldout_reuse_positive"]:
            w = tuple(t)
            ell, _p = A.min_length_and_lex_least(w, g1)
            b = A.burden(w, g1)
            self.assertLessEqual(A.phi(g1.n, ell - 1) + 1, b)
            self.assertLessEqual(b, A.phi(g1.n, ell))

    def test_route_b_enumeration_agrees_with_route_a_closed_form(self):
        g0 = A.Grammar(BASE, [])
        g1 = A.Grammar(BASE, A._macro_list(_LIB))
        for t in (FX["rep2"]["heldout_reuse_positive"]
                  + FX["rep2"]["heldout_unrelated_control"]):
            w = tuple(t)
            self.assertEqual(A.burden(w, g0),
                             B.burden_by_enumeration(w, BASE, {}), t)
            self.assertEqual(A.burden(w, g1),
                             B.burden_by_enumeration(w, BASE, _LIB), t)


class TestRep1(unittest.TestCase):
    """REP-1 and the REP-1b refinement."""

    def test_bands_are_mutually_exclusive(self):
        self.assertEqual(_REP1["band_disjointness_violations"], [])

    def test_bands_are_monotone_in_compression_depth(self):
        self.assertEqual(_REP1["monotonicity_in_compression_depth_violations"], [])

    def test_guaranteed_bands_survive_the_extreme_rank_check(self):
        ora = B.rep1_extreme_rank_check(FX)
        self.assertEqual(ora["extreme_rank_violations"], [])
        self.assertTrue(ora["frozen_guaranteed_bands_never_assert_a_wrong_strict_sign"])

    def test_refinement_only_ever_splits_rank_decided(self):
        self.assertEqual(_REP1["refinement_conflicts_with_frozen_guaranteed_bands"], [])
        self.assertEqual(len(_REP1["REP_1b_boundary_cells_resolved_by_refinement"]), 4)

    def test_route_b_finds_exactly_the_same_boundary_cells(self):
        ora = B.rep1_extreme_rank_check(FX)
        b_cells = sorted(tuple(c[1:5]) for c in
                         ora["weak_boundary_cells_frozen_rule_leaves_in_RANK_DECIDED"])
        a_cells = sorted(tuple(c[:4]) for c in
                         _REP1["REP_1b_boundary_cells_resolved_by_refinement"])
        self.assertEqual(a_cells, b_cells)

    def test_band_counts_agree_across_routes(self):
        ora = B.rep1_extreme_rank_check(FX)
        self.assertEqual(_REP1["counts"], ora["counts"])


class TestRep3Boundary(unittest.TestCase):
    """The EARNED-BY-COUNTEREXAMPLE boundary."""

    def test_primary_uses_the_macro_and_shortens_the_description(self):
        self.assertTrue(_REP3P["macro_used_by_hit_program"])
        self.assertLess(_REP3P["ell1"], _REP3P["ell0"])

    def test_primary_burden_strictly_increases_anyway(self):
        self.assertTrue(_REP3P["burden_increases"])
        self.assertGreater(_REP3P["B_G1"], _REP3P["B_G0"])

    def test_primary_separation_is_rank_free(self):
        self.assertEqual(_REP3P["band"], A.BAND_INCREASE)
        self.assertTrue(_REP3P["rank_free_separation"])
        self.assertGreater(_REP3P["B_G1_floor"], _REP3P["B_G0_ceiling"])

    def test_near_miss_hostile_is_refused_as_a_boundary(self):
        self.assertEqual(_REP3N["band"], A.BAND_RANK)
        self.assertLess(_REP3N["B_G1_floor"], _REP3N["B_G0_ceiling"])

    def test_route_b_reproduces_both_instances_by_enumeration(self):
        ora = B.rep3_by_enumeration(FX)
        self.assertEqual(ora["primary"]["B_G0_enumerated"], _REP3P["B_G0"])
        self.assertEqual(ora["primary"]["B_G1_enumerated"], _REP3P["B_G1"])
        self.assertEqual(ora["near_miss_hostile"]["B_G0_enumerated"], _REP3N["B_G0"])
        self.assertEqual(ora["near_miss_hostile"]["B_G1_enumerated"], _REP3N["B_G1"])


class TestRep2Portfolio(unittest.TestCase):
    """REP-2 and the CAPITAL-1 boundary."""

    def test_decomposition_is_exact(self):
        for res in (_HP, _HM, _ALL):
            self.assertEqual(res["dNet_direct"], res["dNet_decomposed"])

    def test_parent_integers_reproduced(self):
        exp = FX["rep2"]["parent_published_integers_to_reproduce"]
        self.assertEqual(_HP["burden_G0_total"], exp["hplus_burden_g0"])
        self.assertEqual(_HP["burden_G1_total"], exp["hplus_burden_g1"])
        self.assertEqual(_HP["K_total"], exp["k_total"])
        self.assertEqual(_HP["dNet_direct"], exp["hplus_net"])
        self.assertEqual(_HM["burden_G0_total"], exp["hminus_burden_g0"])
        self.assertEqual(_HM["burden_G1_total"], exp["hminus_burden_g1"])
        self.assertEqual(_HM["dNet_direct"], exp["hminus_net"])

    def test_tax_is_strictly_positive_on_the_control(self):
        self.assertGreater(_HM["Tax_T_zero"], 0)
        self.assertEqual(_HM["Saving_T_plus"], 0)

    def test_criterion_sign_matches_the_verdict(self):
        for res in (_HP, _HM, _ALL):
            self.assertEqual(res["criterion_reduces_expected_cost"],
                             res["verdict"] == "REDUCES")

    def test_capital_boundary_separates_capital_from_policy(self):
        h = [x for x in _HOST["battery"] if x["id"] == "H-CAPITAL"][0]
        self.assertTrue(h["detected"])
        self.assertLess(h["single_target_dNet"], 0)
        self.assertGreater(h["portfolio_dNet"], 0)


class TestNovelty(unittest.TestCase):
    """NOV-1 (impossibility) and NOV-2 (non-monotone reachability)."""

    def test_growth_adds_zero_expressive_power(self):
        nov1 = A.nov1_expressive_closure(
            BASE,
            [dict((k, tuple(v)) for k, v in d.items())
             for d in FX["nov1"]["libraries_checked"]],
            [dict((k, tuple(v)) for k, v in d.items())
             for d in FX["nov1"]["cycle_hostiles"]],
            FX["nov1"]["expressibility_check_lmax"])
        self.assertTrue(nov1["all_libraries_add_zero_expressive_power"])
        self.assertTrue(nov1["all_cycle_hostiles_detected"])

    def test_route_b_confirms_zero_expressive_power(self):
        ora = B.nov1_by_construction(FX)
        self.assertTrue(ora["all_add_zero_expressive_power"])
        self.assertTrue(ora["all_cycle_hostiles_detected"])

    def test_reachability_is_non_monotone_under_growth(self):
        nov2 = A.nov2_reachability_census(
            BASE, dict((k, tuple(v)) for k, v in FX["nov2"]["library"].items()),
            FX["nov2"]["lmax"], FX["nov2"]["budget_grid"])
        self.assertTrue(nov2["ADDED_nonempty_at_some_budget"])
        self.assertTrue(nov2["REMOVED_nonempty_at_some_budget"])
        self.assertTrue(nov2["reachability_non_monotone_under_growth"])

    def test_routes_agree_on_the_reachability_census(self):
        a = A.nov2_reachability_census(
            BASE, dict((k, tuple(v)) for k, v in FX["nov2"]["library"].items()),
            FX["nov2"]["lmax"], FX["nov2"]["budget_grid"])
        b = B.nov2_by_enumeration(FX)
        for ra, rb in zip(a["rows"], b["rows"]):
            self.assertEqual(ra["budget"], rb["budget"])
            self.assertEqual(ra["reach_G0"], rb["reach_G0"])
            self.assertEqual(ra["reach_G1"], rb["reach_G1"])
            self.assertEqual(ra["added_count"], rb["added_count"])
            self.assertEqual(ra["removed_count"], rb["removed_count"])


class TestSearchDynamics(unittest.TestCase):
    """SD-1/SD-2/SD-3 in the common charged frame."""

    def test_frame_charges_every_evaluation(self):
        for cell in _SD1["illustrative_single_instance"]["cells"]:
            self.assertTrue(cell["charging_consistent"], cell)

    def test_no_dynamic_is_best_in_every_ecology(self):
        self.assertEqual(_SD1["dynamics_best_in_every_ecology"], [])
        self.assertTrue(_SD1["no_dominance"])

    def test_any_uniformly_worst_dynamic_is_explained(self):
        # FREEZE_V1.md section 3 allows this half "with the exception recorded
        # exactly"; a uniformly-worst dynamic must be NAS, whose sign REP-2
        # predicted for every pool library before it ran.
        for dyn in _SD1["dynamics_worst_in_every_ecology"]:
            self.assertEqual(dyn, "NAS")
            self.assertTrue(_SD3["NAS"]["REP2_prediction_matches_measurement"])
            self.assertTrue(_SD3["NAS"]["all_pool_libraries_lose"])

    def test_every_row_named_dynamic_is_in_the_census(self):
        for dyn in ("MUT", "LS", "GP", "EVO", "GRAD", "NAS", "META"):
            self.assertIn(dyn, A.SD_CENSUS_DYNAMICS)
            for eco in _CENSUS["ecologies"]:
                self.assertIn(eco + "/" + dyn, _CENSUS["aggregate"])

    def test_census_dynamics_match_the_frozen_list(self):
        frozen = set(FX["sd_frame"]["dynamics"])
        census = set(A.SD_CENSUS_DYNAMICS) - set(["RAND"])
        self.assertEqual(frozen, census)

    def test_sd2a_enumeration_attains_the_expected_bound(self):
        self.assertTrue(_SD2["SD_2a"]["enum_attains_bound"])
        self.assertTrue(_SD2["SD_2a"]["enum_hits_all"])
        self.assertTrue(_SD2["SD_2a"]["no_dynamic_matches_enum_coverage"])

    def test_sd2a_agrees_with_route_b_exact_summation(self):
        ora = B.sd2a_exact(FX)
        self.assertTrue(ora["agrees_with_closed_form"])
        # cross-multiply: Route A reduces the Fraction, Route B does not
        self.assertEqual(ora["closed_form_num"] * _SD2["SD_2a"]["bound_den"],
                         _SD2["SD_2a"]["bound_num"] * ora["closed_form_den"])
        self.assertEqual(ora["mean_num"] * _SD2["SD_2a"]["enum_closed_form_mean_den"],
                         _SD2["SD_2a"]["enum_closed_form_mean_num"] * ora["mean_den"])

    def test_sd2b_bound_respected_on_the_sample(self):
        self.assertTrue(_SD2["SD_2b"]["measured_hits_all"])
        self.assertLessEqual(_SD2["SD_2b"]["measured_worst"],
                             _SD2["SD_2b"]["derived_worst_case"])

    def test_sd2b_bound_respected_exhaustively_by_route_b(self):
        ora = B.sd2b_exhaustive(FX)
        self.assertTrue(ora["all_swept_bounds_respected"])
        self.assertEqual(ora["primary"]["misses"], 0)
        self.assertEqual(ora["primary"]["start_points_swept"],
                         3 ** FX["sd_frame"]["ell_primary"])
        swept = [r for r in ora["rows"] if "bound_respected" in r]
        self.assertGreaterEqual(len(swept), 2)

    def test_sd2b_scaling_covers_every_registered_ell(self):
        sc = _SD2["SD_2b_scaling"]
        self.assertEqual([r["ell"] for r in sc["rows"]],
                         FX["sd_frame"]["ell_scaling"])
        self.assertTrue(sc["separation_grows_with_ell"])
        for r in sc["rows"]:
            self.assertEqual(r["GRAD_worst_case_closed_form"],
                             1 + r["ell"] * (len(BASE) - 1))
            # Fraction reduces (X+1)/2, so compare by cross-multiplication
            self.assertEqual(r["ENUM_expected_num"] * 2,
                             (r["space_size"] + 1) * r["ENUM_expected_den"])
            self.assertEqual(
                r["separation_factor_floor"],
                (r["space_size"] + 1) // (2 * r["GRAD_worst_case_closed_form"]))

    def test_sd2c_every_deceptive_hit_is_a_restart_accident(self):
        self.assertTrue(_SD2["SD_2c"]["every_hit_explained"])
        self.assertEqual(_SD2["SD_2c"]["LS_unexplained"], [])
        self.assertEqual(_SD2["SD_2c"]["GRAD_unexplained"], [])
        self.assertTrue(_SD2["SD_2c"]["guided_collapse"])
        self.assertTrue(_SD2["SD_2c"]["enum_unaffected_by_deception"])

    def test_sd2c_characterisation_is_exhaustively_exact(self):
        ora = B.sd2c_exhaustive(FX)
        self.assertTrue(ora["characterisation_exact"])
        self.assertEqual(ora["hit_start_points"], ora["predicted_start_points"])

    def test_sd2d_opaque_queries_are_target_independent(self):
        ti = _SD2["SD_2d_target_independence"]
        self.assertTrue(ti["all_target_independent"])
        self.assertFalse(ti["any_vacuous_comparison"])
        for row in ti["rows"]:
            self.assertGreater(row["compared_prefix_length"], 0, row["dynamic"])

    def test_sd2e_mutation_row_is_ecology_invariant(self):
        self.assertTrue(_SD2["SD_2e_mut_objective_invariance"]["invariant"])

    def test_graded_null_is_beaten(self):
        self.assertTrue(_SD2["null_two_sided"]["GRADED_guided_beats_null"])

    def test_frozen_opaque_null_disposition_is_reported_verbatim(self):
        disp = _SD2["null_two_sided"]["freeze_criterion_disposition"]
        self.assertIn("RAND", disp["as_frozen"])
        self.assertTrue(disp["original_result_reported_verbatim"])
        self.assertIn("RAND", disp["measured"])
        # the frozen criterion is reported whichever way it fell; the package
        # must not depend on it, only on the stronger replacement test.
        self.assertIsInstance(disp["met_as_specified"], bool)

    def test_nas_outcome_was_predicted_by_rep2(self):
        self.assertTrue(_SD3["NAS"]["REP2_prediction_matches_measurement"])

    def test_meta_coverage_dilution(self):
        self.assertTrue(_SD3["META"]["meta_never_matches_enum_in_OPAQUE"])
        self.assertEqual(_SD3["META"]["enum_guarantee_fraction_den"],
                         len(_SD3["META"]["arms"]))


class TestHostiles(unittest.TestCase):
    """Every registered hostile must be detected; clean data must not alarm."""

    def test_every_hostile_detected(self):
        for h in _HOST["battery"]:
            self.assertTrue(h["detected"], h)
        self.assertTrue(_HOST["all_detected"])

    def test_all_registered_hostile_ids_present(self):
        seen = set(h["id"] for h in _HOST["battery"])
        for hid in FX["frame_hostiles"]:
            self.assertIn(hid, seen)

    def test_no_alarm_on_clean_instances(self):
        for key, val in _HOST["no_alarm_on_clean_instances"].items():
            self.assertTrue(val, key)

    def test_cycle_library_leaves_the_grammar_unchanged(self):
        lib = dict((k, tuple(v)) for k, v in FX["nov1"]["cycle_hostiles"][1].items())
        g = A.Grammar(BASE, A._macro_list(lib))
        self.assertFalse(g.is_acyclic())
        try:
            g.expansions()
            raised = None
        except ValueError as exc:
            raised = str(exc)
        self.assertEqual(raised, A.RECURSIVE_LIBRARY_CYCLE)


class TestRouteIndependenceChecker(unittest.TestCase):
    """Validate the checker itself: recall on planted positives, no false alarm.

    The first real run of the earlier substring-grep version failed the build on
    the oracle's own docstring, which names the Route A module in order to say it
    must not be imported. A checker that cries wolf on its first real run gets
    switched off, so both directions are asserted here.
    """

    def setUp(self):
        import ci_gate_v1
        self.G = ci_gate_v1

    def test_real_oracle_is_independent_and_raises_no_alarm(self):
        ok, mods = self.G.route_b_is_independent()
        self.assertTrue(ok, sorted(mods))
        self.assertNotIn(self.G.ROUTE_A_MODULE, mods)

    def test_docstring_mention_is_not_a_violation(self):
        src = '"""this file must not import developmental_reuse_v1"""\nimport json\n'
        self.assertNotIn(self.G.ROUTE_A_MODULE, self.G.imported_modules(src))

    def test_planted_plain_import_is_detected(self):
        src = "import developmental_reuse_v1 as A\n"
        self.assertIn(self.G.ROUTE_A_MODULE, self.G.imported_modules(src))

    def test_planted_from_import_is_detected(self):
        src = "from developmental_reuse_v1 import phi\n"
        self.assertIn(self.G.ROUTE_A_MODULE, self.G.imported_modules(src))

    def test_planted_dynamic_import_is_detected(self):
        src = ("import importlib\n"
               "m = importlib.import_module('developmental_reuse_v1')\n")
        self.assertIn(self.G.ROUTE_A_MODULE, self.G.imported_modules(src))

    def test_unresolvable_dynamic_import_fails_closed(self):
        src = "import importlib\nm = importlib.import_module(name)\n"
        self.assertIn("<DYNAMIC_IMPORT>", self.G.imported_modules(src))


class TestScopeDiscipline(unittest.TestCase):
    """The package must not overreach its own freeze."""

    def test_two_rows_are_declared_open(self):
        with open(os.path.join(HERE, "FREEZE_V1.md"), "r") as fh:
            freeze = fh.read()
        self.assertIn("Predict evolvability on genuinely future task families.", freeze)
        self.assertIn("Validate developmental predictions on continual-learning systems.",
                      freeze)
        self.assertIn("LEFT OPEN", freeze)
        self.assertIn("No neighboring row is earned here.", freeze)

    def test_reconciliation_touches_only_the_three_scoped_rows(self):
        path = os.path.join(HERE, "ISSUE_833_RECONCILIATION_DEVELOPMENTAL_REUSE_V1.json")
        if not os.path.exists(path):
            self.skipTest("reconciliation not yet written")
        with open(path, "r") as fh:
            rec = json.load(fh)
        self.assertEqual(rec["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(len(rec["replacements"]), 3)
        allowed = set([
            "- [ ] Derive representation changes that reduce future search cost.",
            "- [ ] Compare mutation, local search, GP/CGP, evolutionary, gradient, "
            "NAS-like, and meta-search dynamics.",
            "- [ ] Test whether P4 recursive grammar growth discovers mechanisms "
            "absent from `G0`.",
        ])
        for rep in rec["replacements"]:
            self.assertIn(rep["old"], allowed)
            self.assertEqual(rep["anchor"],
                             "# L. Development, morphogenesis, and evolvability")
            self.assertTrue(rep["new"].startswith("- [x] "))

    def test_forbidden_promotions_are_pinned(self):
        path = os.path.join(HERE, "MANIFEST_V1.json")
        if not os.path.exists(path):
            self.skipTest("manifest not yet written")
        with open(path, "r") as fh:
            man = json.load(fh)
        self.assertIn("forbidden_promotions", man)
        joined = " ".join(man["forbidden_promotions"]).lower()
        for needle in ("gradient", "open-ended", "no-free-lunch", "expressive"):
            self.assertIn(needle, joined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
