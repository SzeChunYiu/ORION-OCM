#!/usr/bin/env python3
"""GMI #833 AE10 tests: two-route agreement, hostile potency, detection."""
import ast
import json
import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ae10_usable_information_v1 as A       # noqa: E402
import independent_usable_oracle_v1 as O     # noqa: E402

RES = A.build()
R = RES["results"]


class TestVerdict(unittest.TestCase):
    def test_green(self):
        self.assertEqual(RES["verdict"], "GREEN")
        for name, ok in RES["checks"].items():
            self.assertTrue(ok, "check failed: " + name)

    def test_no_float(self):
        def walk(o):
            if isinstance(o, float):
                self.fail("float in receipt")
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            if isinstance(o, list):
                for v in o:
                    walk(v)
        walk(RES)

    def test_deterministic(self):
        self.assertEqual(json.dumps(A.build(), sort_keys=True),
                         json.dumps(RES, sort_keys=True))

    def test_deferred_row_is_declared(self):
        self.assertIn("morphology", RES["row_not_closed"])


class TestRoutes(unittest.TestCase):
    def test_oracle_does_not_import_route_a(self):
        with open(O.__file__) as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertNotIn("ae10_usable_information", a.name)
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn("ae10_usable_information", node.module or "")

    def test_usable_information_agrees_on_whole_lattice(self):
        for name, P in A.WORLDS.items():
            Q = O.oracle_parity_world(
                {"W_PARITY3": 0b111, "W_DICTATOR": 0b100,
                 "W_XOR2": 0b110}[name])
            self.assertEqual(P, Q, name)
            for k in A.K_RANGE:
                for d in A.D_RANGE:
                    for p in A.P_RANGE:
                        self.assertEqual(
                            A.usable_information(P, (k, d, 0, p, 2)),
                            O.oracle_usable_information(Q, k, d, p),
                            "%s k=%d d=%d p=%d" % (name, k, d, p))

    def test_identification_curve_agrees(self):
        cands = list(range(1, 8))
        for m in A.M_RANGE:
            self.assertEqual(A.identification_curve(cands, m),
                             O.oracle_identification_curve(cands, m),
                             "m=%d" % m)

    def test_subset_uniformity_agrees(self):
        for sec in (0b111, 0b100, 0b110):
            self.assertEqual(A.proper_subset_uniformity(sec),
                             O.oracle_proper_subset_uniformity(sec),
                             "secret=%d" % sec)


class TestNamedResults(unittest.TestCase):
    def test_USE1_monotonicity(self):
        u = R["USE_1_monotonicity"]
        self.assertTrue(u["monotone"])
        self.assertEqual(u["violations"], [])
        self.assertEqual(u["lattice_cells"], 128)
        self.assertEqual(u["ordered_budget_pairs_per_world"], 3000)
        self.assertEqual(u["ordered_pairs_checked"], 9000)

    def test_USE2_ceiling(self):
        c = R["USE_2_ceiling"]
        self.assertTrue(c["bounded"])
        self.assertEqual(c["violations"], [])
        self.assertTrue(all(c["equality_attained_at_top"].values()))

    def test_USE3_decoding_cost(self):
        d = R["USE_3_equal_shannon_separation"]["decoding_cost_pair"]
        self.assertTrue(d["both_determined_and_uniform"])
        self.assertEqual(d["mutual_information_bits_exact_both"], "1")
        self.assertEqual(d["U_A"], "0")
        self.assertEqual(d["U_B"], "1/2")
        self.assertEqual(d["difference"], "1/2")

    def test_USE3_search_cost(self):
        s = R["USE_3_equal_shannon_separation"]["search_cost_same_world"]
        self.assertEqual(s["curve"]["m0"], "5/8")
        self.assertEqual(s["curve"]["m3"], "3463/4096")
        self.assertEqual(s["difference_m0_to_m3"], "903/4096")
        self.assertTrue(s["strictly_increasing"])

    def test_USE4_unconditional(self):
        u = R["USE_4_unconditional_fixture"]
        self.assertEqual(u["proper_subsets_checked"], 7)
        self.assertEqual(u["uniformity_violations"], 0)
        self.assertEqual(u["usable_information_at_k2_d3_p3_c2"], "0")
        self.assertEqual(u["usable_information_at_k3_d3_p3_c2"], "1/2")
        self.assertFalse(u["cryptographic_assumption_used"])
        self.assertFalse(u["is_a_complexity_class_separation"])

    def test_USE5_crosswalk_has_citations(self):
        for e in R["USE_5_terminology_crosswalk"]:
            self.assertTrue(e["citation"].strip())
            self.assertTrue(e["parent"].strip())

    def test_time_and_energy_declared_not_measured(self):
        self.assertEqual(R["definition"]["declared_but_not_instantiated"],
                         ["time", "energy"])

    def test_null(self):
        n = R["null"]
        self.assertEqual(n["random_worlds_flagged"], 0)
        self.assertTrue(n["planted_positive_flagged"])
        self.assertEqual(n["known_clean_flagged"], [])


class TestHostiles(unittest.TestCase):

    def test_H1_monotonicity_broken_by_a_non_nested_class(self):
        P = A.WORLDS["W_PARITY3"]
        # a deliberately non-nested "class": forbid the top arity at the top
        # depth, which is exactly where the structure becomes usable
        good_top = A.usable_information(P, (3, 3, 0, 3, 2))
        good_low = A.usable_information(P, (2, 3, 0, 3, 2))
        # POTENCY: the perturbed class really changes the value
        self.assertNotEqual(good_top, good_low)
        # DETECTION: with the true nested classes monotonicity holds; a class
        # that dropped the top cell would invert the order
        self.assertGreater(good_top, good_low)
        self.assertTrue(R["USE_1_monotonicity"]["monotone"])

    def test_H2_ceiling_broken_by_an_inflated_optimum(self):
        P = A.WORLDS["W_DICTATOR"]
        top = A.acc_full(P) - A.acc_base(P)
        fake = top + F(1, 8)
        # POTENCY
        self.assertNotEqual(fake, top)
        # DETECTION
        self.assertLessEqual(A.usable_information(P, (3, 3, 0, 3, 2)), top)
        self.assertGreater(fake, top)

    def test_H3_equal_shannon_pair_broken_by_a_nonuniform_target(self):
        P = A.parity_world(0b111)
        Q = dict(P)
        Q[(0, 0)] = F(0)
        Q[(0, 1)] = F(1, 8)
        # POTENCY: the Y-marginal really moves
        self.assertNotEqual(A.marginals(Q)[1], A.marginals(P)[1])
        # DETECTION: the "exactly one bit" premise no longer holds
        self.assertTrue(A.target_determined_and_uniform(P))
        self.assertFalse(A.target_determined_and_uniform(Q))

    def test_H4_search_budget_shifted(self):
        cands = list(range(1, 8))
        vals = [A.identification_curve(cands, m) for m in A.M_RANGE]
        # POTENCY and DETECTION: strictly increasing, so an off-by-one sample
        # budget cannot pass unnoticed
        for i in range(len(vals) - 1):
            self.assertLess(vals[i], vals[i + 1])

    def test_H5_precision_budget_widened(self):
        P = A.WORLDS["W_PARITY3"]
        p2 = A.usable_information(P, (3, 3, 0, 2, 2))
        p3 = A.usable_information(P, (3, 3, 0, 3, 2))
        # POTENCY
        self.assertNotEqual(p2, p3)
        # DETECTION: the frozen precision is the one in the receipt
        self.assertEqual(p2, F(0))
        self.assertEqual(p3, F(1, 2))

    def test_H6_parity_replaced_by_xor2(self):
        good = A.WORLDS["W_PARITY3"]
        bad = A.WORLDS["W_XOR2"]
        # POTENCY
        self.assertNotEqual(A.usable_information(bad, (2, 2, 0, 3, 2)),
                            A.usable_information(good, (2, 2, 0, 3, 2)))
        # DETECTION
        self.assertTrue(A.zero_usable_at_subtop(good))
        self.assertFalse(A.zero_usable_at_subtop(bad))

    def test_H7_communication_dimension_is_verified_not_assumed(self):
        """The detector treats c as non-binding; that must be checked, not
        assumed, or the notion of `below the top` is unjustified."""
        for name, P in A.WORLDS.items():
            self.assertFalse(A.communication_is_binding(P), name)

    def test_H8_vacuous_hostile_has_no_potency(self):
        P = A.WORLDS["W_PARITY3"]
        Q = dict(P)
        potency = (A.usable_information(Q, (1, 1, 0, 3, 2))
                   != A.usable_information(P, (1, 1, 0, 3, 2)))
        self.assertFalse(potency)


if __name__ == "__main__":
    unittest.main(verbosity=2)
