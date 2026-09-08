"""Finite mathematical controls, NOT observations of OCM task performance."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import unittest

from benefit_certificate import (
    Certificate, Countercycle, Edge, InvalidModel, Model,
    path_bound, rational, synthesize, verify, verify_countercycle,
)


def edge(name, source, target, signed_gain, demands=1):
    g = F(signed_gain)
    return Edge(name, source, target, (max(g, F(0)),), (max(-g, F(0)),), demands)


def stable():
    return Model("cold", ("cold", "warm"), ("counted_work",), (
        Edge("discover", "cold", "warm", (10,), (16,)),
        Edge("reuse", "warm", "warm", (10,), (3,)),
    ), "AUTHORED_MATHEMATICAL_CONTROL_NOT_OCM_MEASUREMENT")


def dwell(k):
    """At least k warm reuses before invalidation. Model restriction, not prediction."""
    if type(k) is not int or k < 0:
        raise ValueError("nonnegative dwell required")
    states = ("cold",) + tuple(f"warm{i}" for i in range(k + 1))
    edges = [edge("discover", "cold", "warm0", -6)]
    edges += [edge(f"reuse{i}", f"warm{i}", f"warm{i+1}", 7) for i in range(k)]
    edges += [edge("reuse_more", f"warm{k}", f"warm{k}", 7),
              edge("invalidate", f"warm{k}", "cold", -2, 0)]
    return Model("cold", states, ("counted_work",), tuple(edges),
                 "AUTHORED_DWELL_ASSUMPTION_NOT_RUNTIME_ESTIMATE")


class BenefitTests(unittest.TestCase):
    def test_stable_exact_break_even(self):
        model = stable()
        cert = synthesize(model, [1], 7)
        self.assertIsInstance(cert, Certificate)
        bound = verify(model, cert)
        self.assertEqual(bound["debt"], "13")
        self.assertEqual(bound["first_guaranteed_strict_benefit_demand_count"], 2)
        self.assertEqual(path_bound(model, cert, ["discover"])["gain"], "-6")
        self.assertEqual(path_bound(model, cert, ["discover", "reuse"])["gain"], "1")

    def test_zero_cost_startup_is_not_assumed(self):
        model = stable()
        cert = synthesize(model, [1], 7)
        bound = verify(model, cert, fixed_overhead="10/3")
        self.assertEqual(bound["debt"], "49/3")
        self.assertEqual(bound["first_guaranteed_strict_benefit_demand_count"], 3)

    def test_immediate_invalidation_refutes_nonnegative_rate(self):
        model = dwell(0)
        bad = synthesize(model, [1], 0)
        self.assertIsInstance(bad, Countercycle)
        result = verify_countercycle(model, bad)
        self.assertEqual(result["cycle_gain"], "-8")
        self.assertEqual(result["cycle_demands"], 1)

    def test_one_reuse_is_still_insufficient(self):
        bad = synthesize(dwell(1), [1], 0)
        self.assertIsInstance(bad, Countercycle)
        self.assertEqual(verify_countercycle(dwell(1), bad)["cycle_gain"], "-1")

    def test_two_reuses_give_uniform_rate_two(self):
        model = dwell(2)
        self.assertIsInstance(synthesize(model, [1], 2), Certificate)
        self.assertIsInstance(synthesize(model, [1], "200000000000000000001/100000000000000000000"), Countercycle)

    def test_stronger_parent_erases_gain(self):
        model = Model("cold", ("cold", "warm"), ("work",), (
            Edge("discover", "cold", "warm", (16,), (17,)),
            Edge("reuse", "warm", "warm", (3,), (4,))), "matched_parent_same_learner")
        self.assertIsInstance(synthesize(model, [1], 0), Countercycle)

    def test_mandatory_no_reuse_monitoring_cost_matters(self):
        model = Model("s", ("s",), ("work",), (Edge("direct", "s", "s", (10,), (11,)),), "monitor")
        self.assertIsInstance(synthesize(model, [1], 0), Countercycle)

    def test_local_savings_do_not_add_through_interference(self):
        # Each separate mechanism saves 4. Together the interaction costs 9.
        for a in (6, 6):
            m = Model("s", ("s",), ("work",), (Edge("query", "s", "s", (10,), (a,)),), "single")
            self.assertIsInstance(synthesize(m, [1], 4), Certificate)
        m = Model("s", ("s",), ("work",), (Edge("query", "s", "s", (10,), (11,)),), "joint")
        self.assertIsInstance(synthesize(m, [1], 0), Countercycle)

    def test_zero_demand_negative_cycle_cannot_hide(self):
        m = Model("s", ("s",), ("work",), (edge("restart", "s", "s", -1, 0),), "zero_demand")
        self.assertIsInstance(synthesize(m, [1], -1000), Countercycle)

    def test_zero_demand_neutral_stop_does_not_force_zero_per_query_rate(self):
        m = replace(stable(), edges=stable().edges + (edge("idle", "warm", "warm", 0, 0),))
        self.assertIsInstance(synthesize(m, [1], 7), Certificate)

    def test_unreachable_loss_is_not_a_counterexample(self):
        m = replace(stable(), states=("cold", "warm", "unreachable"),
                    edges=stable().edges + (edge("bad", "unreachable", "unreachable", -1000),))
        cert = synthesize(m, [1], 7)
        self.assertIsInstance(cert, Certificate)
        self.assertNotIn("unreachable", dict(cert.potentials))

    def test_terminal_graph(self):
        m = Model("s", ("s",), ("work",), (), "empty_terminal")
        cert = synthesize(m, [1], 7)
        self.assertIsInstance(cert, Certificate)
        self.assertEqual(path_bound(m, cert, ())["demands"], 0)

    def test_exact_numeric_validation(self):
        for bad in (True, False, 1.0, float("nan"), float("inf"), "nan", "1/0"):
            with self.assertRaises(InvalidModel):
                rational(bad)
        self.assertEqual(rational("1/100000000000000000000"), F(1, 10**20))

    def test_nonnegative_complete_vectors(self):
        for bad in ((), (-1,), (True,)):
            with self.assertRaises(InvalidModel):
                Edge("e", "s", "s", bad, (1,))
        with self.assertRaises(InvalidModel):
            Model("s", ("s",), ("work",), (Edge("e", "s", "s", (1, 2), (1,)),), "x")

    def test_invalid_progress_counts(self):
        for d in (-1, True, 0.5):
            with self.assertRaises(InvalidModel):
                Edge("e", "s", "s", (1,), (0,), d)

    def test_prices_registered_and_nonzero(self):
        for prices in ((0,), (-1,), (1, 1), (1.0,)):
            with self.assertRaises(InvalidModel):
                synthesize(stable(), prices)

    def test_unsupported_state_or_duplicate_edge(self):
        for m in (
            lambda: Model("x", ("s",), ("work",), (), "x"),
            lambda: Model("s", ("s", "s"), ("work",), (), "x"),
            lambda: Model("s", ("s",), ("work",), (edge("e", "s", "q", 1),), "x"),
            lambda: Model("s", ("s",), ("work",), (edge("e", "s", "s", 1), edge("e", "s", "s", 2)), "x"),
        ):
            with self.assertRaises(InvalidModel):
                m()

    def test_iterator_inputs_are_materialized_once(self):
        original = stable()
        m = Model(original.start, iter(original.states), iter(original.coordinates), iter(original.edges), original.binding)
        self.assertEqual(m.fingerprint(), original.fingerprint())
        self.assertIsInstance(synthesize(m, iter([1]), 7), Certificate)

    def test_stale_source_binding_rejected(self):
        cert = synthesize(stable(), [1], 7)
        with self.assertRaises(InvalidModel):
            verify(replace(stable(), binding="new_implementation"), cert)

    def test_omitted_potential_and_duplicate_rejected(self):
        cert = synthesize(stable(), [1], 7)
        for phi in (cert.potentials[:1], cert.potentials + cert.potentials[:1]):
            with self.assertRaises(InvalidModel):
                verify(stable(), replace(cert, potentials=phi))

    def test_forged_rate_or_potential_rejected(self):
        cert = synthesize(stable(), [1], 7)
        for modified in (replace(cert, rate=F(8)), replace(cert, potentials=(("cold", F(0)), ("warm", F(0))))):
            with self.assertRaises(InvalidModel):
                verify(stable(), modified)

    def test_countercycle_must_be_closed_and_negative(self):
        bad = synthesize(dwell(0), [1], 0)
        with self.assertRaises(InvalidModel):
            verify_countercycle(dwell(0), replace(bad, edges=("discover",)))
        with self.assertRaises(InvalidModel):
            verify_countercycle(dwell(0), replace(bad, edges=("missing",)))
        with self.assertRaises(InvalidModel):
            verify_countercycle(dwell(0), replace(bad, rate=F(-100)))

    def test_price_tradeoff_not_universal_dominance(self):
        m = Model("s", ("s",), ("work", "written_bytes"),
                  (Edge("q", "s", "s", (10, 0), (5, 10)),), "tradeoff")
        self.assertIsInstance(synthesize(m, [1, 0], 5), Certificate)
        self.assertIsInstance(synthesize(m, [0, 1], 0), Countercycle)
        self.assertIsInstance(synthesize(m, [2, 1], 0), Certificate)

    def test_all_paths_bound_through_six_transitions(self):
        m = dwell(2)
        cert = synthesize(m, [1], 2)
        paths = [(m.start, ())]
        for _ in range(6):
            paths = [(e.target, path + (e.name,)) for state, path in paths for e in m.edges if e.source == state]
            for _, path in paths:
                path_bound(m, cert, path, fixed_overhead=3)

    def test_all_625_complete_two_state_graphs_match_independent_cycle_formula(self):
        # Only three simple cycles exist: each self-loop and the two-edge cycle.
        for a, b, c, d in product(range(-2, 3), repeat=4):
            m = Model("s", ("s", "t"), ("work",), (
                edge("ss", "s", "s", a), edge("st", "s", "t", b),
                edge("ts", "t", "s", c), edge("tt", "t", "t", d)), "exhaustive_math")
            minimum = min(F(a), F(d), F(b+c, 2))
            good = synthesize(m, [1], minimum)
            self.assertIsInstance(good, Certificate)
            verify(m, good)
            bad = synthesize(m, [1], minimum + F(1, 100))
            self.assertIsInstance(bad, Countercycle)
            verify_countercycle(m, bad)

    def test_math_certificate_never_claims_architecture_success(self):
        result = verify(stable(), synthesize(stable(), [1], 7))
        self.assertFalse(result["software_correspondence_verified"])
        self.assertFalse(result["architecture_net_benefit_established"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
