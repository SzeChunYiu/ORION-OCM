"""Sign/strictness boundaries, unsupported Pareto points, and rejected aliases."""
from decimal import Decimal
from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


oracle, core = load("independent_oracle_v12"), load("scalarization_v12")
COVERAGE = {}


class ScalarizationHostiles(unittest.TestCase):
    def test_sign_strictness_and_frontier(self):
        self.assertTrue(core.strict_dominates((0,), (1,)))
        self.assertGreater(core.dot((-1,), (0,)), core.dot((-1,), (1,)))
        self.assertTrue(core.strict_dominates((0, 0), (1, 0)))
        self.assertEqual(core.dot((0, 1), (0, 0)), core.dot((0, 1), (1, 0)))
        self.assertTrue(core.dominates((), ()))
        self.assertFalse(core.strict_dominates((), ()))
        self.assertEqual(core.dot((), ()), 0)
        self.assertEqual(core.pareto_minima([]), ())
        self.assertEqual(core.pareto_minima([(), (), ()]), (0, 1, 2))
        self.assertEqual(core.pareto_minima([(0, 0), (0, 0), (1, 1)]), (0, 1))
        x, y = (1, 0), (0, 1)
        self.assertFalse(core.dominates(x, y) or core.dominates(y, x))
        reflection_failures = 0
        # Trichotomy includes the tied scalar case, which still cannot reflect order.
        for score_x, score_y in ((0, 1), (1, 0), (0, 0)):
            self.assertTrue((score_x <= score_y and not core.dominates(x, y)) or
                            (score_y <= score_x and not core.dominates(y, x)))
            reflection_failures += 1
        points = ((0, 3), (2, 2), (3, 0))
        self.assertEqual(core.pareto_minima(points), (0, 1, 2))
        self.assertEqual(oracle.frontier(points), (0, 1, 2))
        # Candidate-minus-competitor rows add to a strictly positive vector.
        # If both score gaps were <=0, their positive weighted sum could not be >0.
        rows = tuple(oracle.differences(points[1], points[i]) for i in (0, 2))
        certificate = tuple(sum(row[j] for row in rows) for j in range(2))
        self.assertTrue(all(component > 0 for component in certificate))
        searches = 0
        for a in range(1, 8):
            for b in range(1, 8):
                weight = (Fraction(a, 3), Fraction(b, 5))
                scores = tuple(core.dot(weight, point) for point in points)
                self.assertGreater(scores[1], min(scores))
                self.assertGreater(oracle.score(weight, certificate), 0)
                self.assertEqual(sum(oracle.score(weight, row) for row in rows),
                                 oracle.score(weight, certificate))
                searches += 1
        self.assertEqual(searches, 49)
        COVERAGE.update(scalar_reflection_failure_cases=reflection_failures,
                        unsupported_frontier_certificates=1, unsupported_weight_checks=searches)

    def test_separator_mutations(self):
        x, y = (1, 0), (0, 1)
        up, down = core.reversing_weights(x, y)
        self.assertTrue(oracle.check_separator(x, y, up))
        self.assertTrue(oracle.check_separator(x, y, down, -1))
        mutations = [down, (1, 1), (0, 0), (-1, 1), (2,), (True, 1),
                     (1.0, 1), (3, 0), (0, 3), (), (1, 2, 3)]
        rejected = 0
        for weight in mutations:
            with self.assertRaises(ValueError):
                oracle.check_separator(x, y, weight)
            rejected += 1
        with self.assertRaises(ValueError):
            oracle.check_separator(y, x, up)
        rejected += 1
        for sign in (True, 0, 2, 1.0):
            with self.assertRaises(ValueError):
                oracle.check_separator(x, y, up, sign)
            rejected += 1
        self.assertEqual(rejected, 16)
        COVERAGE["separator_mutation_rejections"] = rejected

    def test_malformed_inputs(self):
        class IntAlias(int):
            pass
        invalid = (None, True, 0, "1", {0: 1}, [True], [0.0], [complex(1)],
                   [float("inf")], [Decimal(1)], [IntAlias(1)])
        rejected = 0
        for value in invalid:
            for validator in (core.validate_vector, oracle.vector):
                with self.assertRaises(ValueError):
                    validator(value)
                rejected += 1
        for function in (core.dot, core.dominates, core.strict_dominates,
                         core.reversing_weights, oracle.score, oracle.relation):
            with self.assertRaises(ValueError):
                function((1,), (1, 2))
            rejected += 1
        for coordinate in (True, -1, 2, 0.0, "0", 1):
            for separator in (core.separator, oracle.separating_weights):
                with self.assertRaises(ValueError):
                    separator((1, 0), (0, 1), coordinate)
                rejected += 1
        for first, second in (((), ()), ((0,), (0,))):
            for separator in (core.separator, oracle.separating_weights):
                with self.assertRaises(ValueError):
                    separator(first, second, 0)
                rejected += 1
        for first, second in (((), ()), ((1,), (1,)), ((0,), (1,)), ((1,), (0,))):
            with self.assertRaises(ValueError):
                core.reversing_weights(first, second)
            rejected += 1
        for points in (None, "12", [(1,), (1, 2)], [[True]], [[0.5]]):
            for frontier in (core.pareto_minima, oracle.frontier):
                with self.assertRaises(ValueError):
                    frontier(points)
                rejected += 1
        for weights in ((), (0,), (-1,), (True,), (0.5,)):
            with self.assertRaises(ValueError):
                oracle.normalized(weights)
            rejected += 1
        self.assertEqual(core.validate_vector([1, Fraction(1, 3)]), (1, Fraction(1, 3)))
        self.assertEqual(core.dot([Fraction(1, 2)], [Fraction(-2, 3)]), Fraction(-1, 3))
        self.assertEqual(rejected, 63)
        COVERAGE["malformed_input_rejections"] = rejected


if __name__ == "__main__":
    unittest.main()
