import json
import math
import sys
import unittest
from fractions import Fraction
from itertools import product
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pareto_topology_v1 import (
    CLAIM_CEILING,
    ParetoError,
    _fixture,
    budget_ball,
    choice,
    compose,
    finite_ball_basis_certificate,
    finite_certificate,
    grid_frontiers,
    make_vec,
    pareto,
    path_closure,
    scalar_distance,
    scalar_triangle_violations,
    zero_frontier,
)


class ParetoTopologyTests(unittest.TestCase):
    def test_exhaustive_small_frontier_universe_has_expected_size(self):
        fronts = grid_frontiers(2, 2)
        self.assertEqual(len(fronts), 20)
        self.assertIn((), fronts)
        self.assertIn(zero_frontier(2), fronts)

    def test_choice_and_composition_identities(self):
        a = pareto((make_vec((1, 4)), make_vec((4, 1)), make_vec((5, 5))))
        z = zero_frontier(2)
        self.assertEqual(choice(a, ()), a)
        self.assertEqual(compose(a, z), a)
        self.assertEqual(compose(z, a), a)
        self.assertEqual(compose(a, ()), ())

    def test_multiobjective_closure_and_unreachable(self):
        nodes, edges = _fixture()
        h = path_closure(nodes, edges, 2)
        self.assertEqual(
            h[("A", "C")],
            pareto((make_vec((0, 5)), make_vec((1, 1)), make_vec((5, 0)))),
        )
        self.assertEqual(h[("A", "D")], ())
        self.assertEqual(h[("D", "A")], ())

    def test_scalar_projection_is_directed_and_triangle_safe(self):
        nodes, edges = _fixture()
        h = path_closure(nodes, edges, 2)
        w = make_vec((1, 1))
        self.assertEqual(scalar_triangle_violations(nodes, h, w), [])
        self.assertEqual(scalar_distance(h[("A", "B")], w), 0)
        self.assertEqual(scalar_distance(h[("B", "A")], w), 14)
        self.assertTrue(math.isinf(scalar_distance(h[("A", "D")], w)))

    def test_forward_budget_basis_certificate(self):
        nodes, edges = _fixture()
        h = path_closure(nodes, edges, 2)
        budgets = tuple(make_vec(p) for p in product(range(1, 9), repeat=2))
        result = finite_ball_basis_certificate(nodes, h, budgets)
        self.assertGreater(result["basis_condition_cases"], 0)
        self.assertEqual(result["generated_open_sets"], 12)
        self.assertIn("B", budget_ball(nodes, h, "A", make_vec((1, 1))))
        self.assertNotIn("A", budget_ball(nodes, h, "B", make_vec((1, 1))))

    def test_scalarization_loses_frontier_information(self):
        f1 = pareto((make_vec((1, 4)), make_vec((4, 1))))
        f2 = pareto((make_vec((1, 4)), make_vec((2, 3))))
        self.assertNotEqual(f1, f2)
        self.assertEqual(scalar_distance(f1, make_vec((1, 1))), 5)
        self.assertEqual(scalar_distance(f2, make_vec((1, 1))), 5)
        self.assertEqual(scalar_distance(f1, make_vec((1, 4))), 8)
        self.assertEqual(scalar_distance(f2, make_vec((1, 4))), 14)

    def test_invalid_negative_or_nonpositive_inputs_fail_closed(self):
        with self.assertRaisesRegex(ParetoError, "NEGATIVE_BURDEN"):
            make_vec((-1, 0))
        with self.assertRaisesRegex(ParetoError, "NONPOSITIVE_SCALAR_WEIGHT"):
            scalar_distance(pareto((make_vec((1, 1)),)), make_vec((1, 0)))

    def test_receipt_green(self):
        r = finite_certificate()
        self.assertEqual(r["claim_ceiling"], CLAIM_CEILING)
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))
        self.assertEqual(r["counts"]["distinct_grid_frontiers"], 20)
        json.dumps(r, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    unittest.main()
