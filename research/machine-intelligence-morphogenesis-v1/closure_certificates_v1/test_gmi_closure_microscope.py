from fractions import Fraction as F
from itertools import combinations, product
import unittest

import gmi_closure_microscope as g

class FrontierTests(unittest.TestCase):
    def test_original_displayed_premises_allow_common_winner(self):
        c = [[0, 1], [0, 0]]
        self.assertIn(0, g.epsilon_optimal_sets(c)[0])
        self.assertIn(1, g.epsilon_optimal_sets(c)[1])
        self.assertEqual(g.robust_candidates(c), {0})
        self.assertEqual(g.worst_case_error(c, [1, 0]), 0)

    def test_strict_flip(self):
        c = [[0, 1], [1, 0]]
        self.assertFalse(g.robust_candidates(c))
        self.assertEqual(g.deterministic_minimax_regret(c)[0], 1)
        self.assertEqual(g.worst_case_error(c, [F(1,2), F(1,2)]), F(1,2))

    def test_pairwise_intersection_does_not_suffice(self):
        c = [[0,0,1], [1,0,0], [0,1,0]]
        sets = g.epsilon_optimal_sets(c)
        self.assertTrue(all(a & b for a,b in combinations(sets,2)))
        self.assertFalse(g.robust_candidates(c))
        self.assertEqual(g.worst_case_error(c,[F(1,3)]*3),F(1,3))

    def test_epsilon_boundary_inclusive(self):
        self.assertEqual(g.robust_candidates([[0,2],[2,0]], 2), {0,1})
        self.assertFalse(g.robust_candidates([[0,2],[2,0]], F(3,2)))

    def test_all_tied(self):
        self.assertEqual(g.robust_candidates([[1,1,1],[0,0,0]]), {0,1,2})

    def test_single_candidate_regret(self):
        self.assertEqual(g.deterministic_minimax_regret([[10],[1]])[0],0)
        self.assertEqual(g.rectangular_worst_regret([(0,100)],0),0)

    def test_rectangle_all_endpoint_worlds(self):
        intervals = [(0,2),(1,4),(2,3)]
        worlds = list(product(*intervals))
        for i in range(3):
            self.assertEqual(g.rectangular_worst_regret(intervals,i),
                             max(row[i]-min(row) for row in worlds))

    def test_own_lower_endpoint_not_spurious_competitor(self):
        self.assertEqual(g.rectangular_worst_regret([(0,2),(3,5)],0),0)

    def test_correlated_rectangle_can_be_conservative(self):
        self.assertEqual(g.deterministic_minimax_regret([[0,1],[10,11]])[0],0)
        self.assertEqual(g.rectangular_worst_regret([(0,10),(1,11)],0),9)

    def test_invalid_empty(self):
        with self.assertRaises(ValueError): g.robust_candidates([])

    def test_invalid_ragged(self):
        with self.assertRaises(ValueError): g.robust_candidates([[0],[0,1]])

    def test_float_not_exact(self):
        with self.assertRaises(TypeError): g.robust_candidates([[0.0,1]])

    def test_bool_not_cost(self):
        with self.assertRaises(TypeError): g.robust_candidates([[False,1]])

    def test_bad_probability(self):
        with self.assertRaises(ValueError): g.worst_case_error([[0,1]],[1,1])

    def test_negative_epsilon(self):
        with self.assertRaises(ValueError): g.robust_candidates([[0,1]],-1)

    def test_candidate_permutation(self):
        c = [[0,2,3],[1,2,0]]
        d = [[row[2],row[0],row[1]] for row in c]
        self.assertEqual(g.deterministic_minimax_regret(c)[0],g.deterministic_minimax_regret(d)[0])

class MeasurementTests(unittest.TestCase):
    def test_finite_probe_collision_and_separation(self):
        n, pairs=g.finite_probe_witness([1,2,4,8])
        self.assertTrue(all(pairs[x][0]==pairs[x][1] for x in [1,2,4,8]))
        self.assertNotEqual(pairs[n+1][0],pairs[n+1][1])

    def test_full_rank_exact_polynomial(self):
        a=g.polynomial_design([1,2,4],2)
        theta=(F(2),F(3),F(5))
        y=[sum(x*t for x,t in zip(row,theta)) for row in a]
        self.assertEqual(g.recover_coefficients(a,y),theta)

    def test_all_small_quadratics(self):
        a=g.polynomial_design([1,2,4,8],2)
        for t in product(range(-2,3),repeat=3):
            y=[sum(x*b for x,b in zip(row,t)) for row in a]
            self.assertEqual(g.recover_coefficients(a,y),t)

    def test_confound_dimensions(self):
        with self.assertRaisesRegex(ValueError,"UNIDENTIFIABLE"):
            g.recover_coefficients([[1,1],[2,2],[4,4]],[2,4,8])

    def test_independently_varied_dimensions(self):
        self.assertEqual(g.recover_coefficients([[1,1],[2,1],[1,2]],[3,4,5]),(1,2))

    def test_model_mismatch(self):
        with self.assertRaisesRegex(ValueError,"MODEL_MISMATCH"):
            g.recover_coefficients([[1,1],[1,2],[1,3]],[1,2,100])

    def test_duplicate_nodes_rank_deficient(self):
        self.assertEqual(g.rank(g.polynomial_design([1,1,1],2)),1)

    def test_observation_count(self):
        with self.assertRaises(ValueError): g.recover_coefficients([[1,2]],[1,2])

    def test_rank_zero(self):
        self.assertEqual(g.rank([[0,0],[0,0]]),0)

    def test_alpha_spending_telescopes(self):
        n=1000
        self.assertEqual(sum(F(1,k*(k+1)) for k in range(1,n+1)),1-F(1,n+1))

    def test_radius_and_input_validation(self):
        self.assertGreater(g.anytime_hoeffding_radius(100,22,.05),0)
        self.assertLessEqual(g.anytime_hoeffding_radius(100,22,.05),1)
        for bad in [0,-1,True]:
            with self.assertRaises(ValueError): g.anytime_hoeffding_radius(bad,22,.05)

if __name__ == '__main__':
    unittest.main(verbosity=2)
