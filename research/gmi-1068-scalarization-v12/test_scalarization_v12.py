"""Exact exhaustive order/weight grids, witnesses, and finite minimizer checks."""
from fractions import Fraction
import importlib.util
from itertools import combinations
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


class ScalarizationTests(unittest.TestCase):
    def test_exhaustive_grids(self):
        dimensions = vectors_seen = pairs = dots = permutations = separators = incomparables = 0
        weighted = {"positive": 0, "nonnegative": 0}
        weights_seen = {"positive": 0, "nonnegative": 0}
        monotone = strict = normalizations = 0
        for dimension, vectors, positive, nonnegative in oracle.grids():
            dimensions += 1
            vectors_seen += len(vectors)
            families = []
            for name, weights in (("positive", positive), ("nonnegative", nonnegative)):
                weights_seen[name] += len(weights)
                tables = []
                for weight in weights:
                    actual = tuple(core.dot(weight, x) for x in vectors)
                    expected = tuple(oracle.score(weight, x) for x in vectors)
                    self.assertEqual(actual, expected)
                    for x, value in zip(vectors, actual):
                        self.assertEqual(core.dot(weight[::-1], x[::-1]), value)
                        permutations += 1
                    dots += len(vectors)
                    tables.append((weight, actual, expected))
                families.append((name, tables))
            for xi, x in enumerate(vectors):
                for yi, y in enumerate(vectors):
                    relation = oracle.relation(x, y)
                    self.assertEqual(core.dominates(x, y), relation["le"])
                    self.assertEqual(core.strict_dominates(x, y), relation["strict"])
                    self.assertEqual(core.dominates(x[::-1], y[::-1]), relation["le"])
                    pairs += 1
                    for name, tables in families:
                        for weight, actual, expected in tables:
                            self.assertEqual(actual[xi] <= actual[yi], expected[xi] <= expected[yi])
                            weighted[name] += 1
                            if relation["le"]:
                                self.assertLessEqual(actual[xi], actual[yi])
                                monotone += 1
                                supported = any(weight[k] > 0 for k in relation["negative"])
                                self.assertEqual(actual[xi] < actual[yi], supported)
                                strict += supported
                    for k in relation["positive"]:
                        weight = core.separator(x, y, k)
                        self.assertTrue(oracle.check_separator(x, y, weight))
                        independent = oracle.separating_weights(x, y, k)
                        self.assertGreater(core.dot(independent, x), core.dot(independent, y))
                        # The registered division-free construction is checked separately.
                        delta = oracle.differences(x, y)
                        self.assertEqual(weight[k], 1 + sum(abs(v) for i, v in enumerate(delta) if i != k))
                        self.assertTrue(all(w == delta[k] for i, w in enumerate(weight) if i != k))
                        separators += 1
                    if relation["incomparable"]:
                        up, down = core.reversing_weights(x, y)
                        for weight, sign in ((up, 1), (down, -1)):
                            self.assertTrue(oracle.check_separator(x, y, weight, sign))
                            normalized = oracle.normalized(weight)
                            self.assertEqual(sum(normalized), 1)
                            self.assertTrue(oracle.check_separator(x, y, normalized, sign))
                            normalizations += 1
                        incomparables += 1
        self.assertEqual(dimensions, 5)
        self.assertEqual(vectors_seen, 121)
        self.assertEqual(pairs, 7381)
        self.assertEqual(dots, 14762)
        self.assertEqual(weights_seen, {"positive": 121, "nonnegative": 121})
        self.assertEqual(weighted, {"positive": 551881, "nonnegative": 551881})
        self.assertEqual(separators, 9534)
        COVERAGE.update(dimensions=dimensions, vectors=vectors_seen, ordered_pairs=pairs,
                        independent_dot_checks=dots, permutation_dot_checks=permutations,
                        positive_weights=weights_seen["positive"], nonnegative_weights=weights_seen["nonnegative"],
                        positive_pair_weight_checks=weighted["positive"], nonnegative_pair_weight_checks=weighted["nonnegative"],
                        dominated_weight_checks=monotone, strict_improvement_checks=strict,
                        separating_coordinates=separators, incomparable_pairs=incomparables,
                        normalized_separator_checks=normalizations)

    def test_finite_minimizers(self):
        points = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1))
        weights = tuple((a, b) for a in (1, 2, 3) for b in (1, 2, 3))
        sets = searches = selections = 0
        for size in range(len(points) + 1):
            for chosen in combinations(points, size):
                expected = oracle.frontier(chosen)
                self.assertEqual(core.pareto_minima(chosen), expected)
                sets += 1
                if not chosen:
                    continue
                for weight in weights:
                    scores = tuple(oracle.score(weight, point) for point in chosen)
                    minimum = min(scores)
                    for index, score in enumerate(scores):
                        if score == minimum:
                            self.assertIn(index, expected)
                            selections += 1
                    searches += 1
        self.assertEqual(sets, 512)
        self.assertEqual(searches, 4599)
        COVERAGE.update(feasible_sets=sets, positive_minimizer_searches=searches,
                        efficient_minimizer_checks=selections)

    def test_exact_rational_witnesses(self):
        cases = 0
        for dimension in range(2, 10):
            x = tuple(Fraction((-1) ** i * (i + 1), 2 * i + 3) for i in range(dimension))
            y = tuple(Fraction(0) for _ in range(dimension))
            up, down = core.reversing_weights(x, y)
            self.assertTrue(oracle.check_separator(x, y, up))
            self.assertTrue(oracle.check_separator(x, y, down, -1))
            for weight in (up, down, oracle.normalized(up), oracle.normalized(down)):
                self.assertEqual(core.dot(weight, x), oracle.score(weight, x))
                cases += 1
        self.assertEqual(cases, 32)
        COVERAGE["rational_dot_checks"] = cases


if __name__ == "__main__":
    unittest.main()
