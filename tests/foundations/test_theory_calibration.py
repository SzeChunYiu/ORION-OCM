"""Exact finite counterexamples and reference arithmetic; not empirical OCM evidence."""
import importlib.util
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("foundation_calibration", ROOT / "research/foundations-closure-v1/calibration.py")
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)


class TheoryCalibrationTests(unittest.TestCase):
    def test_entropy_endpoints_and_symmetry(self):
        self.assertEqual(c.binary_entropy(0), 0)
        self.assertEqual(c.binary_entropy(1), 0)
        self.assertEqual(c.binary_entropy(.5), 1)
        self.assertAlmostEqual(c.binary_entropy(.2), c.binary_entropy(.8))

    def test_entropy_invalid(self):
        for x in (-1, 1.1, math.nan, math.inf, True):
            with self.assertRaises(ValueError): c.binary_entropy(x)

    def test_fano_numerical_reproduction(self):
        self.assertAlmostEqual(c.fano_information(30, .05), 4.37759458531834)
        self.assertEqual([c.fano_probe_bound(30, .05, b) for b in (.1, .25, .5, 1, 2)], [44,18,9,5,3])

    def test_expected_horizon_is_not_rounded_up(self):
        actual = c.fano_probe_bound(30, .05, 2, fixed_horizon=False)
        self.assertGreater(actual, 2)
        self.assertLess(actual, 3)
        self.assertNotEqual(actual, math.ceil(actual))

    def test_zero_information_and_blind_error(self):
        self.assertEqual(c.fano_probe_bound(2, 0, 0), math.inf)
        self.assertEqual(c.fano_probe_bound(2, .5, 0), 0)
        self.assertEqual(c.fano_information(2, 1), 0)
        self.assertEqual(c.fano_information(8, 0), 3)

    def test_fano_invalid(self):
        for m, eps, b in ((1,.1,1),(True,.1,1),(2,-.1,1),(2,1.1,1),(2,.1,-1),(2,.1,math.nan)):
            with self.assertRaises(ValueError): c.fano_probe_bound(m,eps,b)

    def test_xor_refutes_marginal_information_cap(self):
        self.assertEqual(c.xor_information(), {"first_marginal_bits":0, "second_marginal_bits":0,
                                               "joint_bits":1, "second_given_first_bits":1})

    def test_joint_probability_validation(self):
        for joint in ({}, {(0,0):F(1,2)}, {(0,0):-1,(1,1):2}):
            with self.assertRaises(ValueError): c.mutual_information(joint)

    def test_rare_tail_entropy_is_not_search_cost(self):
        row = c.rare_tail_example(20)
        self.assertLess(row["entropy_effective_count"], 2.5)
        self.assertEqual(F(row["optimal_expected_unit_cost_guesses"]), F(1048617,40))
        self.assertGreater(row["optimal_expected_unit_cost_guesses_float"], 26000)

    def test_rare_tail_matches_small_explicit_enumeration(self):
        for exponent in range(2, 7):
            m, eps = 2**exponent, F(1, exponent)
            p = (1-eps,) + (eps/m,)*m
            self.assertEqual(c.expected_repair_cost(p, (1,)*(m+1), tuple(range(m+1))),
                             F(c.rare_tail_example(exponent)["optimal_expected_unit_cost_guesses"]))

    def test_cost_aware_order_differs_from_probability_order(self):
        p,cost = (F(3,5),F(2,5)), (100,1)
        order = c.optimal_repair_order(p,cost)
        self.assertEqual(order,(1,0))
        self.assertEqual(c.expected_repair_cost(p,cost,order),61)
        self.assertEqual(c.expected_repair_cost(p,cost,(0,1)),F(502,5))

    def test_ratio_order_is_optimal_in_finite_exhaustion(self):
        cases = 0
        for weights in itertools.product((1,2,3), repeat=3):
            p = tuple(F(w,sum(weights)) for w in weights)
            for costs in itertools.product((1,2,5), repeat=3):
                chosen = c.expected_repair_cost(p,costs,c.optimal_repair_order(p,costs))
                self.assertEqual(chosen, min(c.expected_repair_cost(p,costs,order)
                                            for order in itertools.permutations(range(3))))
                cases += 1
        self.assertEqual(cases,729)

    def test_repair_validation_and_zero_probability(self):
        self.assertEqual(c.optimal_repair_order((0,1),(1,1)),(1,0))
        for p,cost in (((1,),()), ((F(1,2),),(1,)), ((1,),(0,)), ((-1,2),(1,1))):
            with self.assertRaises(ValueError): c.optimal_repair_order(p,cost)
        for order in ((0,0),(True,0),(0,),(0,2)):
            with self.assertRaises(ValueError): c.expected_repair_cost((F(1,2),)*2,(1,1),order)

    def test_lifetime_closed_form_matches_explicit_finite_sum(self):
        for h in range(11):
            for s in (F(0),F(1,4),F(1,2),F(1)):
                expected = sum((2*s**i for i in range(h)), F(0)) - 10 - 3*(1-s**h)
                self.assertEqual(c.geometric_surplus(h,s,2,10,3),expected)

    def test_drift_erases_payback_and_strict_boundary(self):
        self.assertGreater(c.geometric_surplus(10,1,2,10),0)
        self.assertLess(c.geometric_surplus(10,F(1,2),2,10),0)
        self.assertEqual(c.strict_payback_horizon(10,2),6)
        self.assertEqual(c.strict_payback_horizon(0,2),1)
        self.assertIsNone(c.strict_payback_horizon(10,0))
        self.assertIsNone(c.strict_payback_horizon(10,-1))

    def test_lifetime_input_validation(self):
        for args in ((True,1,2,10),(-1,1,2,10),(2,F(3,2),2,10),(2,1,2,-1)):
            with self.assertRaises(ValueError): c.geometric_surplus(*args)

    def test_alpha_spending_telescopes(self):
        for n in (1,2,10,100):
            self.assertEqual(sum((F(1,i*(i+1)) for i in range(1,n+1)), F(0)),F(n,n+1))

    def test_radius_monotonic_parameters(self):
        radius = c.hoeffding_radius(1000,.05)
        self.assertGreater(c.hoeffding_radius(100,.05),radius)
        self.assertGreater(c.hoeffding_radius(1000,.01),radius)
        self.assertGreater(c.hoeffding_radius(1000,.05,comparisons=4),radius)
        self.assertAlmostEqual(c.hoeffding_radius(1000,.05,lower=0,upper=1), radius/2)

    def test_hoeffding_budget_identity(self):
        n,k,delta=100,4,.05
        w=c.hoeffding_radius(n,delta,comparisons=k)
        self.assertAlmostEqual(2*math.exp(-2*n*w*w/4),delta/(k*n*(n+1)))

    def test_radius_rejects_invalid_parameters(self):
        for args in ((0,.05),(True,.05),(10,0),(10,1),(10,math.nan)):
            with self.assertRaises(ValueError): c.hoeffding_radius(*args)
        with self.assertRaises(ValueError): c.hoeffding_radius(10,.05,comparisons=0)
        with self.assertRaises(ValueError): c.hoeffding_radius(10,.05,lower=1,upper=1)

    def test_zero_failures_is_not_zero_risk(self):
        bound=c.zero_failures_upper(100,.05)
        self.assertGreater(bound,0)
        self.assertAlmostEqual((1-bound)**100,.05)
        self.assertLess(c.zero_failures_upper(1000,.05),bound)
        with self.assertRaises(ValueError): c.zero_failures_upper(0,.05)

    def test_new_operator_invalidates_old_quotient(self):
        obs={"x":0,"y":0,"z":1}; blocks={"x":"A","y":"A","z":"B"}
        old={"stay":{state:state for state in obs}}
        self.assertIsNone(c.quotient_witness(obs,blocks,old))
        new={**old,"new":{"x":"z","y":"y","z":"z"}}
        self.assertEqual(c.quotient_witness(obs,blocks,new)["kind"],"TRANSITION")

    def test_quotient_preserves_registered_observations(self):
        self.assertEqual(c.quotient_witness({"x":0,"y":1},{"x":"A","y":"A"},{})["kind"],"OBSERVATION")
        with self.assertRaises(ValueError): c.quotient_witness({"x":0},{"x":"A"},{"bad":{}})
        with self.assertRaises(ValueError): c.quotient_witness({"x":0},{"x":"A"},{"bad":{"x":"z"}})

    def test_report_is_strict_json_and_reproduces_committed_report(self):
        actual = json.loads(json.dumps(c.report(),allow_nan=False))
        committed = json.loads((ROOT / "research/foundations-closure-v1/CALIBRATION.json").read_text())
        def compare(left, right):
            if isinstance(right, float):
                self.assertTrue(math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12))
            elif isinstance(right, dict):
                self.assertEqual(set(left), set(right))
                for key in right: compare(left[key], right[key])
            elif isinstance(right, list):
                self.assertEqual(len(left), len(right))
                for a, b in zip(left, right): compare(a, b)
            else:
                self.assertEqual(left, right)
        compare(actual, committed)


if __name__ == "__main__":
    unittest.main()
