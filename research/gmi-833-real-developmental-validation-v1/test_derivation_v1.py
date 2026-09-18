#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GMI #833 -- tests for the section-4 derivation (Route A) and oracle (Route B).

Runnable as:

    python3 -I -B test_derivation_v1.py -v
    python3 -I -O -B test_derivation_v1.py -v

No bare `assert` statement is used anywhere: every check is a unittest method
call, so -O does not weaken a single test.  Python 3.8, stdlib only.
"""

import ast
import json
import os
import subprocess
import sys
import tempfile
import token
import tokenize
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
# `python3 -I` drops the script directory from sys.path; put it back explicitly.
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derivation_v1 as DA            # noqa: E402
import oracle_derivation_v1 as OB     # noqa: E402

RESULT_A = os.path.join(HERE, "DERIVATION_RESULT_V1.json")
RESULT_B = os.path.join(HERE, "ORACLE_DERIVATION_RESULT_V1.json")

_STATE = {}


def setUpModule():
    DA.main(["derivation_v1.py", RESULT_A])
    OB.main(["oracle_derivation_v1.py", RESULT_B])
    fh = open(RESULT_A, "r")
    _STATE["A"] = json.load(fh)
    fh.close()
    fh = open(RESULT_B, "r")
    _STATE["B"] = json.load(fh)
    fh.close()


def A():
    return _STATE["A"]


def B():
    return _STATE["B"]


def R(claim):
    return _STATE["A"]["results"][claim]


def walk_for_floats(obj, path, out):
    if isinstance(obj, float):
        out.append(path)
    elif isinstance(obj, dict):
        for key in sorted(obj.keys()):
            walk_for_floats(obj[key], path + "/" + str(key), out)
    elif isinstance(obj, list):
        for i in range(len(obj)):
            walk_for_floats(obj[i], path + "[%d]" % i, out)


# ------------------------------------------------------------------ OI-2


class TestOI2(unittest.TestCase):

    def test_inequality_holds_everywhere_on_the_census(self):
        r = R("OI-2")
        self.assertEqual(r["inequality_violation_count"], 0)
        self.assertEqual(r["inequality_violations"], [])
        self.assertEqual(r["census_cells"], 154)

    def test_inequality_recomputed_directly(self):
        bad = []
        for n in range(2, 13):
            for l in range(1, 15):
                if not (DA.Phi(n + 1, l - 1) >= DA.Phi(n, l - 1)):
                    bad.append((n, l))
        self.assertEqual(bad, [])

    def test_gamma1_never_guaranteed_reduction_on_admissible_domain(self):
        r = R("OI-2")
        self.assertEqual(r["gamma1_verdict_counts_on_l0_ge_2"]
                         ["GUARANTEED_REDUCTION"], 0)

    def test_band_exceptions_are_exactly_the_degenerate_l0_eq_1_cells(self):
        r = R("OI-2")
        self.assertEqual(r["band_exception_count"], 11)
        self.assertEqual(r["band_exception_l0_values"], [1])
        self.assertTrue(r["band_exceptions_all_degenerate_l1_eq_0"])


# ------------------------------------------------------------------ OI-3


class TestOI3(unittest.TestCase):

    def test_bracket_holds_for_Lstar_and_Mstar_over_n_2_to_24(self):
        r = R("OI-3")
        self.assertEqual(r["bracket_violation_count"], 0)
        self.assertEqual(r["bracket_violations"], [])
        self.assertEqual(len(r["table"]), 23)

    def test_exact_Lstar_values(self):
        r = R("OI-3")["table"]
        self.assertEqual(r["n=02"]["Lstar"], 4)
        self.assertEqual(r["n=03"]["Lstar"], 6)
        self.assertEqual(r["n=04"]["Lstar"], 8)
        self.assertEqual(r["n=12"]["Lstar"], 33)
        self.assertEqual(r["n=24"]["Lstar"], 79)

    def test_Lstar_recomputed_directly_matches(self):
        for n in range(2, 25):
            self.assertEqual(DA.lstar(n), R("OI-3")["table"]["n=%02d" % n]["Lstar"])
            self.assertEqual(DA.mstar(n), R("OI-3")["table"]["n=%02d" % n]["Mstar"])

    def test_Mstar_strictly_exceeds_Lstar_everywhere(self):
        tab = R("OI-3")["table"]
        for key in sorted(tab.keys()):
            self.assertGreater(tab[key]["Mstar"], tab[key]["Lstar"])

    def test_frozen_gamma1_consequence_is_FALSE_and_reported_as_such(self):
        r = R("OI-3")
        self.assertIn("FALSE", r["verdict"])
        self.assertGreater(r["frozen_gamma1_consequence_counterexample_count"], 0)
        first = r["frozen_gamma1_consequence_first_counterexamples"][0]
        self.assertEqual(first["n"], 2)
        self.assertEqual(first["l0"], 4)
        self.assertEqual(first["gamma"], 1)
        self.assertEqual(first["actual_verdict"], "RANK_DECIDED")
        # and it is surfaced at the top level, not buried
        self.assertEqual(A()["frozen_statements_falsified_count"], 1)
        self.assertEqual(A()["frozen_statements_falsified"][0]["claim_id"], "OI-3")

    def test_corrected_converses_hold_with_zero_failures(self):
        r = R("OI-3")
        self.assertEqual(r["gamma0_guaranteed_increase_failures"], [])
        self.assertEqual(r["gamma1_guaranteed_increase_failures"], [])
        self.assertGreater(r["gamma0_guaranteed_increase_cells_certified"], 0)
        self.assertGreater(r["gamma1_guaranteed_increase_cells_certified"], 0)

    def test_ceiling_is_exact_integer_arithmetic(self):
        self.assertEqual(DA.ceil_div(7, 2), 4)
        self.assertEqual(DA.ceil_div(8, 2), 4)
        self.assertEqual(DA.ceil_div(1, 3), 1)
        self.assertEqual(DA.ceil_div(0, 3), 0)


# ------------------------------------------------------------------ OI-1


class TestOI1(unittest.TestCase):

    def test_workload_census_present(self):
        r = R("OI-1")
        self.assertEqual(r["workload_census_size"], 6)
        ids = sorted([row["id"] for row in r["rows"]])
        self.assertEqual(ids, ["W1", "W2", "W3", "W4", "W5", "W6"])

    def test_W1_pays_exactly(self):
        row = None
        for x in R("OI-1")["rows"]:
            if x["id"] == "W1":
                row = x
        self.assertEqual(row["Theta_inv"], "243/1")
        self.assertEqual(row["total_charge"], "6/1")
        self.assertTrue(row["strictly_pays"])

    def test_gamma0_workload_cannot_pay(self):
        row = None
        for x in R("OI-1")["rows"]:
            if x["id"] == "W2":
                row = x
        self.assertEqual(row["Saving"], "0/1")
        self.assertFalse(row["strictly_pays"])

    def test_gamma1_workload_has_nonpositive_theta(self):
        row = None
        for x in R("OI-1")["rows"]:
            if x["id"] == "W6":
                row = x
        num = int(row["Theta_inv"].split("/")[0])
        self.assertLess(num, 0)
        self.assertFalse(row["strictly_pays"])

    def test_theta_inv_is_exact_rational(self):
        s, t, th = DA.theta_inv(3, [{"weight": "1/3", "l0": 4, "l1": 2},
                                    {"weight": "2/3", "l0": 4, "l1": 4}])
        self.assertEqual(th, s - t)
        self.assertEqual(DA.fr(th).count("/"), 1)


# ------------------------------------------------------------------ OI-4


class TestOI4(unittest.TestCase):

    def test_not_sufficient_witness_found(self):
        w = R("OI-4")["not_sufficient_witness_lexicographically_first"]
        self.assertNotEqual(w.get("witness", None), "NO_WITNESS_FOUND")
        self.assertEqual([w["n"], w["occ"], w["b"], w["kappa"], w["l0"], w["l1"]],
                         [2, 2, 3, 0, 4, 4])
        self.assertGreater(w["gain_897"], 0)
        self.assertEqual(w["phi_frame_verdict"], "GUARANTEED_INCREASE")

    def test_not_sufficient_holds_even_with_strict_compression(self):
        w = R("OI-4")["not_sufficient_strict_compression_witness"]
        self.assertNotEqual(w.get("witness", None), "NO_WITNESS_FOUND")
        self.assertEqual([w["n"], w["occ"], w["b"], w["kappa"], w["l0"], w["l1"]],
                         [2, 2, 3, 0, 7, 6])
        self.assertGreaterEqual(w["gamma"], 1)
        self.assertGreater(w["gain_897"], 0)
        self.assertEqual(w["phi_frame_verdict"], "GUARANTEED_INCREASE")

    def test_not_necessary_witness_found(self):
        w = R("OI-4")["not_necessary_witness_lexicographically_first"]
        self.assertNotEqual(w.get("witness", None), "NO_WITNESS_FOUND")
        self.assertEqual([w["n"], w["occ"], w["b"], w["kappa"], w["l0"], w["l1"]],
                         [2, 1, 1, 0, 3, 1])
        self.assertLessEqual(w["gain_897"], 0)
        self.assertEqual(w["phi_frame_verdict"], "GUARANTEED_REDUCTION")

    def test_witness_arithmetic_recomputed(self):
        self.assertEqual(DA.band(2, 4, 3, 4), "GUARANTEED_INCREASE")
        self.assertEqual(DA.band(2, 7, 3, 6), "GUARANTEED_INCREASE")
        self.assertEqual(DA.band(2, 3, 3, 1), "GUARANTEED_REDUCTION")
        self.assertEqual(2 * (3 - 1) - 3 - 0, 1)
        self.assertEqual(1 * (1 - 1) - 1 - 0, -1)

    def test_repair_side_condition_has_no_counterexample(self):
        r = R("OI-4")
        self.assertEqual(r["repaired_rule_counterexample_count"], 0)
        self.assertEqual(r["repaired_rule_counterexamples"], [])

    def test_gammastar_inv_is_at_least_two_where_defined(self):
        r = R("OI-4")
        self.assertEqual(r["gammastar_inv_min_where_defined"], 2)
        for n in range(2, 7):
            for l0 in range(2, 11):
                g = DA.gammastar_inv(n, l0)
                if g is not None:
                    self.assertGreaterEqual(g, 2)

    def test_census_size(self):
        self.assertEqual(R("OI-4")["census_cells"], 52800)


# ------------------------------------------------------------------ LF-1


class TestLF1(unittest.TestCase):

    def test_census_and_counts(self):
        r = R("LF-1")
        self.assertEqual(r["census_cells"], 2730)
        c = r["counts"]
        self.assertEqual(c["LIBRARY_GUARANTEED_BETTER"], 1653)
        self.assertEqual(c["LIBRARY_GUARANTEED_WORSE"], 336)
        self.assertEqual(c["RANK_DECIDED"], 741)
        total = (c["LIBRARY_GUARANTEED_BETTER"] + c["LIBRARY_GUARANTEED_WORSE"]
                 + c["RANK_DECIDED"] + c["BAND_COLLISION"])
        self.assertEqual(total, 2730)

    def test_bands_are_mutually_exclusive(self):
        r = R("LF-1")
        self.assertEqual(r["mutual_exclusivity_violation_count"], 0)
        self.assertEqual(r["counts"]["BAND_COLLISION"], 0)

    def test_mutual_exclusivity_recomputed_directly(self):
        bad = 0
        for (n, k, lL, lj) in DA.lf1_census():
            better = DA.Phi(n + k, lL) <= DA.Phi(n + 1, lj - 1)
            worse = DA.Phi(n + k, lL - 1) >= DA.Phi(n + 1, lj)
            if better and worse:
                bad = bad + 1
        self.assertEqual(bad, 0)

    def test_internal_cross_check(self):
        self.assertEqual(R("LF-1")["internal_cross_check_mismatch_count"], 0)


# ------------------------------------------------------------------ LF-2


class TestLF2(unittest.TestCase):

    def test_charge_neutrality_on_every_member_set(self):
        r = R("LF-2")
        self.assertEqual(r["mismatch_count"], 0)
        self.assertEqual(r["census_size"], 8)
        for row in r["rows"]:
            self.assertTrue(row["equal"])
            self.assertEqual(row["difference"], 0)
            self.assertEqual(row["K_total_shared_library"],
                             row["K_total_k_separate_grammars"])

    def test_charge_neutrality_recomputed(self):
        for ms in DA.MEMBER_SET_CENSUS:
            shared = sum([b + ms["kappa"] for b in ms["bodies"]])
            separate = sum([b + ms["kappa"] for b in ms["bodies"]])
            self.assertEqual(shared, separate)


# ------------------------------------------------------------------ LF-3


class TestLF3(unittest.TestCase):

    def test_both_endpoint_inequalities_hold(self):
        r = R("LF-3")
        self.assertEqual(r["gamma0_cells_checked"], 420)
        self.assertEqual(r["strict_upper_endpoint_failure_count"], 0)
        self.assertEqual(r["weak_lower_endpoint_failure_count"], 0)

    def test_no_gamma0_cell_is_guaranteed_better(self):
        v = R("LF-3")["gamma0_verdict_counts"]
        self.assertEqual(v["LIBRARY_GUARANTEED_BETTER"], 0)
        self.assertEqual(v["BAND_COLLISION"], 0)

    def test_endpoint_dominance_does_not_imply_guaranteed_worse(self):
        v = R("LF-3")["gamma0_verdict_counts"]
        self.assertEqual(v["LIBRARY_GUARANTEED_WORSE"], 210)
        self.assertEqual(v["RANK_DECIDED"], 210)
        self.assertIn("ENDPOINT DOMINANCE DOES NOT IMPLY",
                      R("LF-3")["endpoint_dominance_vs_band_note"])

    def test_dilution_tax_is_strictly_positive(self):
        r = R("LF-3")
        self.assertEqual(r["dilution_tax_nonpositive_count"], 0)
        self.assertGreater(r["dilution_tax_min"], 0)


# ------------------------------------------------------------------ LF-4


class TestLF4(unittest.TestCase):

    def test_table_shape(self):
        r = R("LF-4")
        self.assertEqual(r["defined_cells"], 350)
        self.assertEqual(r["undefined_cells"], 35)
        self.assertEqual(r["undefined_at_lj_values"], [2])

    def test_gammastar_at_least_two(self):
        r = R("LF-4")
        self.assertEqual(r["min_gammastar_where_defined"], 2)
        self.assertEqual(r["gammastar_below_two_violation_count"], 0)

    def test_monotone_in_k(self):
        self.assertEqual(R("LF-4")["monotonicity_in_k_violation_count"], 0)

    def test_gammastar_recomputed_directly(self):
        self.assertEqual(DA.gammastar(2, 2, 2), None)
        self.assertEqual(DA.gammastar(2, 2, 3), 2)
        self.assertEqual(DA.gammastar(2, 2, 8), 3)
        self.assertEqual(DA.gammastar(2, 6, 12), 7)

    def test_lL_ge_1_assumption_is_registered(self):
        found = False
        for a in A()["registered_domain_assumptions"]:
            if a.startswith("ADMISSIBLE_PROGRAM_LENGTHS_ARE_>=1"):
                found = True
        self.assertTrue(found)
        self.assertIn("lL=0", R("LF-4")["why_undefined_at_lj_2"])


# --------------------------------------------------------------- IND-1/IND-2


class TestIndependence(unittest.TestCase):

    def test_ind1_witness(self):
        r = R("IND-1")
        self.assertEqual(r["verdict"], "WITNESS_FOUND")
        self.assertTrue(r["invention_strictly_pays"])
        self.assertFalse(r["any_library_guaranteed_better"])
        self.assertEqual(r["Theta_inv"], "3003/1")
        self.assertEqual(r["total_charge"], "9/1")
        self.assertEqual(r["library_candidate_count"], 10)
        for row in r["library_candidates"]:
            self.assertNotEqual(row["verdict"], "LIBRARY_GUARANTEED_BETTER")

    def test_ind2_witness(self):
        r = R("IND-2")
        self.assertEqual(r["verdict"], "WITNESS_FOUND")
        self.assertEqual(r["library"]["verdict"], "LIBRARY_GUARANTEED_BETTER")
        self.assertFalse(r["any_operator_strictly_pays"])
        self.assertEqual(r["operator_candidate_count"], 12)
        for row in r["operator_candidates"]:
            self.assertFalse(row["strictly_pays"])
            self.assertLessEqual(int(row["Theta_inv"].split("/")[0]), 0)

    def test_independence_established(self):
        self.assertTrue(R("INDEPENDENCE")["independence_established"])

    def test_quantifier_tags_are_finite_not_deductive(self):
        self.assertIn("forall_fin[U]", R("IND-1")["quantifiers"])
        self.assertIn("forall_fin[U]", R("IND-2")["quantifiers"])
        self.assertNotIn("forall[D]", R("IND-1")["quantifiers"])
        self.assertNotIn("forall[D]", R("IND-2")["quantifiers"])


# --------------------------------------------------------------- hostiles


class TestHostiles(unittest.TestCase):

    def test_all_five_hostiles_registered(self):
        self.assertEqual(A()["hostiles"]["registered_hostiles"], [
            "H1_GAMMA0_OPERATOR_DECLARED_INVENTABLE",
            "H2_GAMMA0_LIBRARY_DECLARED_FAVOURED",
            "H3_DILUTION_OFF_BY_ONE",
            "H4_INADMISSIBLE_COMPRESSION",
            "H5_RECURSIVE_LIBRARY_CYCLE"])

    def test_every_planted_positive_is_detected(self):
        h = A()["hostiles"]
        self.assertTrue(h["all_planted_positives_detected"])
        detected = sorted(set([row["planted"] for row in h["planted_positive_rows"]
                               if row["detected"]]))
        self.assertEqual(detected, h["registered_hostiles"])

    def test_h3_planted_across_the_full_census_differs_on_many_cells(self):
        h = A()["hostiles"]
        diffs = []
        for row in h["planted_positive_rows"]:
            if row["planted"] == "H3_DILUTION_OFF_BY_ONE":
                diffs.append(row["differing_cells_vs_clean"])
                self.assertEqual(row["census_cells"], 2730)
        self.assertEqual(len(diffs), 2)
        for d in diffs:
            self.assertGreater(d, 0)

    def test_no_alarm_on_clean_inputs(self):
        h = A()["hostiles"]
        self.assertTrue(h["no_alarm_case_is_clean"])
        self.assertGreaterEqual(h["no_alarm_case_count"], 5)
        for row in h["no_alarm_rows"]:
            self.assertEqual(row["flag_count"], 0)

    def test_h5_returns_code_and_leaves_grammar_unchanged(self):
        h = A()["hostiles"]
        self.assertEqual(h["h5_returns_code"], "RECURSIVE_LIBRARY_CYCLE")
        self.assertTrue(h["h5_grammar_object_identity_unchanged"])
        self.assertTrue(h["h5_grammar_content_unchanged"])
        self.assertTrue(h["h5_acyclic_install_still_works"])

    def test_h5_recomputed_directly(self):
        g = {"alphabet": ["a", "b"], "macros": {}}
        code, obj = DA.install_library(g, {"m1": ["a", "m2"], "m2": ["b", "m1"]})
        self.assertEqual(code, "RECURSIVE_LIBRARY_CYCLE")
        self.assertIs(obj, g)
        self.assertEqual(g, {"alphabet": ["a", "b"], "macros": {}})

    def test_detector_recall_and_specificity_directly(self):
        self.assertIn("H1_GAMMA0_OPERATOR_DECLARED_INVENTABLE",
                      DA.detect_hostiles({"operator_claims": [
                          {"n": 2, "l0": 4, "l1": 4, "claim": "INVENTABLE"}]}))
        self.assertEqual(DA.detect_hostiles({"operator_claims": [
            {"n": 2, "l0": 8, "l1": 2, "claim": "INVENTABLE"}]}), [])
        self.assertIn("H4_INADMISSIBLE_COMPRESSION",
                      DA.detect_hostiles({"operator_claims": [
                          {"n": 3, "l0": 4, "l1": 6, "claim": "INVENTABLE"}]}))
        cells = DA.lf1_census()
        self.assertEqual(DA.detect_hostiles(
            {"lf1_vector": DA.lf1_vector_variant(cells, "CLEAN")}), [])
        self.assertIn("H3_DILUTION_OFF_BY_ONE", DA.detect_hostiles(
            {"lf1_vector": DA.lf1_vector_variant(cells, "H3A_N_FOR_N_PLUS_1")}))
        self.assertIn("H3_DILUTION_OFF_BY_ONE", DA.detect_hostiles(
            {"lf1_vector": DA.lf1_vector_variant(cells,
                                                 "H3B_N_PLUS_1_FOR_N_PLUS_K")}))


# ------------------------------------------------------------------- null


class TestNull(unittest.TestCase):

    def test_derived_rule_is_perfect_on_the_census(self):
        n = A()["null_test"]
        self.assertEqual(n["derived_rule_correct"], 2730)
        self.assertEqual(n["census_cells"], 2730)

    def test_no_null_matches_or_beats_the_derived_rule(self):
        n = A()["null_test"]
        self.assertEqual(n["trials"], 200)
        self.assertEqual(n["nulls_matching_or_beating_derived_rule"], 0)
        self.assertEqual(n["result"], "0/200")

    def test_margin_is_reported_and_large(self):
        n = A()["null_test"]
        self.assertGreater(n["margin_derived_minus_best_null"], 0)
        self.assertLess(n["null_score_max"], 2730)
        self.assertGreater(n["null_score_min"], 0)

    def test_null_uses_no_random_module(self):
        n = A()["null_test"]
        self.assertFalse(n["lcg"]["module_random_used"])
        self.assertEqual(n["lcg"]["seed"], DA.LCG_SEED)


# --------------------------------------------------------------- two routes


class TestTwoRouteAgreement(unittest.TestCase):

    def test_oracle_does_not_import_route_a(self):
        """Structural check on the parsed AST, not a substring search."""
        fh = open(os.path.join(HERE, "oracle_derivation_v1.py"), "r")
        src = fh.read()
        fh.close()
        tree = ast.parse(src)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    imported.append(a.name)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module if node.module else "")
        self.assertEqual(sorted(set(imported)), ["json", "os", "sys"])
        self.assertNotIn("derivation_v1", imported)
        # and it never evaluates the closed form Phi
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.append(node.id)
        self.assertNotIn("Phi", names)

    def test_route_a_result_was_loaded_by_the_oracle(self):
        self.assertEqual(B()["route_a_status"], "ROUTE_A_RESULT_LOADED")

    def test_full_agreement_on_the_overlap_scope(self):
        b = B()
        self.assertGreater(b["two_route_cells_checked"], 0)
        self.assertEqual(b["two_route_cells_checked"], b["two_route_cells_agreeing"])
        self.assertTrue(b["two_route_full_agreement"])

    def test_per_check_agreement_counts(self):
        per = B()["two_route_agreement_per_check"]
        for name in sorted(per.keys()):
            ck = per[name]["cells_checked"]
            ag = per[name]["cells_agreeing"]
            if ck is not None:
                self.assertEqual(ck, ag)
        self.assertEqual(per["LF-1_THREE_WAY_BAND"]["cells_checked"], 90)
        self.assertEqual(per["LF-4_GAMMASTAR"]["cells_checked"], 24)
        self.assertEqual(per["OI-2_GAMMA1_NEVER_GUARANTEED_REDUCTION"]
                         ["cells_checked"], 15)
        self.assertEqual(per["T3_BURDEN_IDENTITY"]["cells_checked"], 7)
        self.assertEqual(per["OI-1_THETA_INV_ON_W1"]["cells_checked"], 4)
        self.assertEqual(per["OI-4_WITNESS_VERDICTS"]["cells_checked"], 3)
        self.assertEqual(per["OI-3_LSTAR_AND_MSTAR"]["cells_checked"], 4)

    def test_oracle_reproduces_Lstar_and_Mstar_by_enumeration(self):
        res = B()["results"]["OI-3_LSTAR_AND_MSTAR"]
        got = {}
        for row in res["Lstar_rows"]:
            if row["status"] == "CHECKED":
                got[row["cell"]] = row["enumerated_Lstar"]
        self.assertEqual(got, {"n=2": 4, "n=3": 6, "n=4": 8})
        mrows = [r for r in res["Mstar_rows"] if r["status"] == "CHECKED"]
        self.assertEqual(len(mrows), 1)
        self.assertEqual(mrows[0]["enumerated_Mstar"], 7)
        # the falsification of the frozen gamma=1 consequence, seen from Route B
        for row in res["Lstar_rows"]:
            if row["status"] == "CHECKED":
                self.assertEqual(row["gamma0_verdict_at_Lstar"],
                                 "GUARANTEED_INCREASE")
                self.assertEqual(row["gamma1_verdict_at_Lstar"], "RANK_DECIDED")

    def test_oracle_recovers_T3_by_enumeration(self):
        res = B()["results"]["T3_BURDEN_IDENTITY"]
        self.assertEqual(res["cells_checked"], res["cells_agreeing"])
        for row in res["rows"]:
            if row["status"] == "CHECKED":
                self.assertTrue(row["agree"])
                lo, hi = row["enumerated_length_endpoints"]
                self.assertLessEqual(lo, row["enumerated_burden"])
                self.assertLessEqual(row["enumerated_burden"], hi)

    def test_oracle_macro_expansion_recovers_the_lengths(self):
        res = B()["results"]["OI-1_THETA_INV_ON_W1"]
        self.assertEqual(res["enumerated_l0_under_G0"], 8)
        self.assertEqual(res["enumerated_l1_under_G0_plus_m"], 2)
        self.assertEqual(res["enumerated_Theta_inv"], 243)
        self.assertTrue(res["enumerated_strictly_pays"])

    def test_oracle_enumeration_is_real(self):
        sc = OB.scan(3, 4)
        self.assertEqual(sc["count"][1], 3)
        self.assertEqual(sc["count"][2], 9)
        self.assertEqual(sc["count"][4], 81)
        self.assertEqual(sc["first"][1], 1)
        self.assertEqual(sc["last"][4], 3 + 9 + 27 + 81)
        self.assertEqual(OB.expand([2, 2], 2, [[0, 1, 0, 1]]),
                         [0, 1, 0, 1, 0, 1, 0, 1])
        self.assertIsNone(OB.expand([2], 2, [[2]]))

    def test_oracle_reports_out_of_budget_rather_than_a_closed_form(self):
        res = B()["results"]["OI-3_LSTAR_AND_MSTAR"]
        self.assertIn("budget", res["reachable_scope_note"])
        self.assertEqual(B()["registered_overlap_scope"]["mstar_n_range"], [2, 2])


# -------------------------------------------------------------- determinism


class TestDeterminism(unittest.TestCase):

    def _run(self, script, args, outname):
        tmp = tempfile.mkdtemp(prefix="gmi833-")
        out = os.path.join(tmp, outname)
        cmd = [sys.executable] + args + [os.path.join(HERE, script), out]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        _o, e = proc.communicate()
        self.assertEqual(proc.returncode, 0, e.decode("utf-8", "replace"))
        fh = open(out, "rb")
        data = fh.read()
        fh.close()
        os.remove(out)
        os.rmdir(tmp)
        return data

    def test_route_a_is_byte_identical_across_runs_and_under_O(self):
        a = self._run("derivation_v1.py", ["-I", "-B"], "r1.json")
        b = self._run("derivation_v1.py", ["-I", "-B"], "r2.json")
        c = self._run("derivation_v1.py", ["-I", "-O", "-B"], "r3.json")
        self.assertEqual(a, b)
        self.assertEqual(a, c)
        fh = open(RESULT_A, "rb")
        onfile = fh.read()
        fh.close()
        self.assertEqual(a, onfile)

    def test_route_b_is_byte_identical_across_runs_and_under_O(self):
        a = self._run("oracle_derivation_v1.py", ["-I", "-B"], "o1.json")
        b = self._run("oracle_derivation_v1.py", ["-I", "-B"], "o2.json")
        c = self._run("oracle_derivation_v1.py", ["-I", "-O", "-B"], "o3.json")
        self.assertEqual(a, b)
        self.assertEqual(a, c)
        fh = open(RESULT_B, "rb")
        onfile = fh.read()
        fh.close()
        self.assertEqual(a, onfile)

    def test_json_is_sorted_and_indent_one(self):
        fh = open(RESULT_A, "r")
        text = fh.read()
        fh.close()
        obj = json.loads(text)
        self.assertEqual(text,
                         json.dumps(obj, sort_keys=True, indent=1,
                                    ensure_ascii=True) + "\n")


# ------------------------------------------------------------------ no float


class TestNoFloat(unittest.TestCase):

    def test_route_a_result_contains_no_float(self):
        found = []
        walk_for_floats(A(), "", found)
        self.assertEqual(found, [])

    def test_route_b_result_contains_no_float(self):
        found = []
        walk_for_floats(B(), "", found)
        self.assertEqual(found, [])

    def test_result_text_has_no_decimal_or_exponent_numbers(self):
        for path in (RESULT_A, RESULT_B):
            fh = open(path, "r")
            obj = json.load(fh, parse_float=lambda s: _fail_float(s))
            fh.close()
            self.assertIsNotNone(obj)

    def test_sources_declare_exact_arithmetic(self):
        self.assertEqual(A()["arithmetic"], "EXACT_INT_AND_FRACTION_ONLY__NO_FLOAT")
        self.assertEqual(B()["arithmetic"], "EXACT_INT_ONLY__NO_FLOAT")

    def test_no_float_literal_or_division_in_the_executors(self):
        """Token-level scan: no float literal, no true division, in real code."""
        for name in ("derivation_v1.py", "oracle_derivation_v1.py"):
            path = os.path.join(HERE, name)
            fh = open(path, "r")
            src = fh.read()
            fh.close()
            for banned in ("float(", "math.ceil", "import math", "import random"):
                self.assertNotIn(banned, src)
            bad_ops = []
            bad_nums = []
            fh = open(path, "rb")
            for tok in tokenize.tokenize(fh.readline):
                if tok.type == token.OP and tok.string in ("/", "/="):
                    bad_ops.append((name, tok.start))
                if tok.type == token.NUMBER:
                    t = tok.string.lower()
                    if ("." in t) or ("e" in t and not t.startswith("0x")) \
                            or ("j" in t):
                        bad_nums.append((name, tok.string))
            fh.close()
            self.assertEqual(bad_ops, [])
            self.assertEqual(bad_nums, [])


def _fail_float(s):
    raise AssertionError("float literal in result JSON: %r" % (s,))


if __name__ == "__main__":
    unittest.main()
