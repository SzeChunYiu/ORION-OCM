"""Tests for #833 Section Z subsection Z4 (rows 2, 3, 5 only).

Runs under `python3 -I -B` and `python3 -I -O -B`; every assertion raises
explicitly so `-O` cannot strip it.  Stdlib only.
"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
A_PY = os.path.join(HERE, "z4_universality_v1.py")
B_PY = os.path.join(HERE, "independent_universality_oracle_v1.py")
RES = os.path.join(HERE, "RESULT_V1.json")
ORA = os.path.join(HERE, "ORACLE_RESULT_V1.json")


def need(c, m):
    if not c:
        raise AssertionError(m)


def load(path, regen):
    if not os.path.exists(path):
        r = subprocess.run([sys.executable, "-I", "-B", regen],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        need(r.returncode == 0,
             "%s failed: %s" % (regen, r.stderr.decode()[-2000:]))
    with open(path) as fh:
        return json.load(fh)


class Z4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = load(RES, A_PY)
        cls.b = load(ORA, B_PY)

    # ------------------------------------------------------------ two routes
    def test_01_routes_agree_on_the_class_structure(self):
        r = self.a["row2_resource_response_classes"]
        need(r["classes"] == self.b["resource_response_classes"],
             "class count disagreement: %r vs %r"
             % (r["classes"], self.b["resource_response_classes"]))
        need(r["behaviour_classes_at_L3"] == self.b["behaviour_classes_at_L3"],
             "behaviour class count disagreement")
        need(r["class_size_min"] == self.b["class_size_min"], "min size")
        need(r["class_size_max"] == self.b["class_size_max"], "max size")
        need(r["singleton_classes"] == self.b["singleton_classes"],
             "singleton count")

    def test_02_routes_agree_on_every_frontier(self):
        fa = self.a["row3_frontiers_and_exponents"]["frontier_by_block"]
        fb = self.b["block_frontiers"]
        need(set(fa) == set(fb), "block key sets differ")
        for k in fa:
            need(fa[k] == fb[k], "block %s: %r vs %r" % (k, fa[k], fb[k]))
        ga = self.a["row3_frontiers_and_exponents"]["frontier_by_family"]
        gb = self.b["family_frontiers_L3"]
        for k in gb:
            need(ga[k]["frontier_L3"] == gb[k],
                 "family %s frontier: %r vs %r" % (k, ga[k]["frontier_L3"],
                                                   gb[k]))

    def test_03_routes_agree_on_every_distinction(self):
        da = self.a["row5_irreducible_distinctions"]["detail"]
        db = self.b["distinctions"]
        need(set(da) == set(db), "distinction key sets differ")
        for k in da:
            need(da[k]["IRREDUCIBLE"] == db[k]["IRREDUCIBLE"],
                 "%s irreducibility disagreement" % k)
            need(da[k]["clause1_semantic_quotient"] == db[k]["clause1"],
                 "%s clause 1 disagreement" % k)

    def test_04_analytic_form_matches_the_enumeration(self):
        need(self.b["analytic_matches_enumeration"],
             "Route B's analytic stateless minimum disagrees with enumeration")
        need(self.a["row3_frontiers_and_exponents"]
             ["U7_closed_form_holds_at_every_rung"], "U7 failed")

    # ----------------------------------------------------------- the rows
    def test_05_row2_class_definition_is_non_degenerate(self):
        r = self.a["row2_resource_response_classes"]
        need(r["U1_non_degenerate"], "the class definition is degenerate")
        need(r["U2_between_behaviour_classes_and_families"], "U2 failed")
        need(r["singleton_classes"] == 0,
             "singleton classes appeared: %d" % r["singleton_classes"])
        need(r["class_size_max"] < self.a["universe_candidates"],
             "one class holds the whole universe")
        need(r["rename_invariant"],
             "the resource-response profile is not rename-invariant")

    def test_06_row3_refuses_exponents_with_the_rung_count_stated(self):
        f = self.a["row3_frontiers_and_exponents"]
        need(f["exponent_verdict"] == "NOT_IDENTIFIED", "an exponent was reported")
        g = f["exponent_guard"]
        need(g["state_bit_axis_rungs"] == 2 and g["sequence_length_axis_rungs"] == 3,
             "rung counts moved: %r" % g)
        need(not g["state_bit_axis_identifiable"], "2 rungs accepted")
        need(not g["sequence_length_axis_identifiable"], "3 rungs accepted")
        need(g["synthetic_five_rung_axis_identifiable"],
             "the guard refuses even at 5 rungs, so it is a constant")
        need(f["U11_exponent_guard_refuses_and_accepts"], "U11 failed")

    def test_07_row3_frontier_separation_is_real(self):
        f = self.a["row3_frontiers_and_exponents"]
        need(f["U8_moore_and_mealy_frontiers_differ"], "U8 failed")
        need(f["frontier_by_family"]["F_MOORE"]["frontier_L3"] == [[8, 0]],
             "Moore frontier moved")
        need(f["frontier_by_family"]["F_MEALY_PURE"]["frontier_L3"] == [[0, 0]],
             "Mealy frontier moved")
        need(f["frontier_soundness"], "a frontier contains a dominated point")
        need(f["N3_frontier_invariant_under_shuffle"],
             "the frontier depends on traversal order")

    def test_08_row5_verdict_and_its_refutations(self):
        r = self.a["row5_irreducible_distinctions"]
        need(r["distinctions_tested"] == 16,
             "distinction count moved: %d" % r["distinctions_tested"])
        need(r["irreducible"] == ["F_DEAD_TABLE_vs_F_MOORE"],
             "irreducible set moved: %r" % r["irreducible"])
        need(r["U3_bits_split_irreducible"] is False,
             "U3 refutation not recorded")
        need(r["U4_moore_mealy_irreducible"] is False,
             "U4 refutation not recorded")
        need(r["U5_naive_all_pairs_irreducible"] is False,
             "U5 refutation not recorded")
        need(r["U6_some_family_separation_fails_clause1"], "U6 failed")
        need(len(r["fail_clause1_semantic_quotient"]) == 13,
             "clause-1 failure count moved: %d"
             % len(r["fail_clause1_semantic_quotient"]))

    def test_09_clause_two_does_real_work(self):
        r = self.a["row5_irreducible_distinctions"]
        need(r["clause1_only_verdict"] != r["irreducible"],
             "the clause-1-only verdict equals the two-clause verdict, so "
             "clause 2 is decorative")
        need(r["clause1_only_verdict_count"] == 3,
             "clause-1-only count moved: %d" % r["clause1_only_verdict_count"])
        need(r["U10_clause2_rejects_something_clause1_admits"], "U10 failed")

    # ------------------------------------------------------------ the nulls
    def test_10_nulls(self):
        n = self.a["nulls"]
        need(n["N1_random_partitions_respecting_behaviour"] == 0,
             "%d random partitions respect the behaviour quotient"
             % n["N1_random_partitions_respecting_behaviour"])
        need(n["N4_behaviour_respecting_bipartitions"] == 200,
             "N4 size moved")
        need(n["N4_behaviour_respecting_bipartitions_irreducible"] == 0,
             "%d behaviour-respecting bipartitions are irreducible, so the "
             "criterion is cheap"
             % n["N4_behaviour_respecting_bipartitions_irreducible"])
        need("inert" in n["N2_note"],
             "N2's inertness must be recorded, not glossed")

    # --------------------------------------------------------- the hostiles
    def test_11_every_hostile_fires(self):
        r2 = self.a["row2_resource_response_classes"]
        r3 = self.a["row3_frontiers_and_exponents"]
        r5 = self.a["row5_irreducible_distinctions"]
        need(r2["HS1_index_keyed_definition_detected"],
             "an index-keyed class definition was not detected")
        need(r3["HS2_dominated_point_detected"],
             "a dominated point injected into a frontier was not detected")
        need(r5["HS3_planted_clause1_only_verdict_detected"], "HS3 failed")
        need(r3["HS4_exponent_from_short_ladder_blocked"], "HS4 failed")
        need(r2["HS5_planted_degenerate_definitions_detected"], "HS5 failed")
        v = r2["HS5_vacuity_verdicts"]
        need(v["registered_definition"] == "NON_DEGENERATE", "HS5 false alarm")
        need(v["planted_constant_profile"] == "DEGENERATE", "HS5 miss")
        need(v["planted_index_keyed_profile"] == "DEGENERATE", "HS5 miss")

    # ------------------------------------------------------- bookkeeping
    def test_12_rows_1_and_4_are_not_touched(self):
        need(self.a["rows_in_scope"] == [2, 3, 5], "scope moved")
        need(self.a["rows_deliberately_left_open"] == [1, 4],
             "rows 1 and 4 must stay open")
        with open(os.path.join(HERE, "MANIFEST_V1.json")) as fh:
            man = json.load(fh)
        need("Z4_ROW1_OR_ROW4_EARNED" in man["forbidden_promotions"],
             "the row-1/row-4 forbidden promotion is missing")
        need(set(man["rows_deliberately_left_open"]) == set(["1", "4"]),
             "the manifest does not name both left-open rows")

    def test_13_no_float_and_ceiling_present(self):
        blob = json.dumps(self.a) + json.dumps(self.b)
        for tok in (".0,", ".0}", "e-0", "e+0"):
            need(tok not in blob, "float-looking token %r in a receipt" % tok)
        need(self.a["claim_ceiling"].startswith("GMI_833_Z4_"),
             "claim ceiling missing")
        need(self.a["ladder"]["ladder_cells"] ==
             self.a["ladder"]["state_bit_rungs"] *
             self.a["ladder"]["sequence_length_rungs"],
             "ladder bookkeeping does not close")


if __name__ == "__main__":
    unittest.main(verbosity=2)
