"""Hostile, exact finite checks for round E; run normally and with python -O."""

import unittest
from fractions import Fraction as Q
from itertools import product

from foundation_v5 import admissible_subcategory, aggregates, budget_paths
from independent_oracle_v5 import (
    cyclic_three, powerset, reference_admissibility, reference_aggregates,
    resource_category, walking_arrow,
)


COVERAGE = {
    "category_subsets": 1114, "aggregation_cases": 405,
    "fixed_weight_vectors": 152, "c3_corruptions": 27,
    "malformed_ambient": 14, "malformed_aggregation": 14,
    "malformed_budgets": 5, "noninteger_aliases": 5,
}


class CategoryTests(unittest.TestCase):
    def test_exhaustive_subsets_match_independent_closure(self):
        presentations = [cyclic_three(), walking_arrow()]
        presentations += [resource_category(n)[1] for n in range(4)]
        checked = 0
        for n, identities, compose in presentations:
            for allowed in powerset(range(n)):
                with self.subTest(n=n, identities=identities, allowed=allowed):
                    actual = admissible_subcategory(n, identities, compose, allowed)
                    self.assertEqual(actual,
                                     reference_admissibility(identities, compose, allowed))
                    checked += 1
        self.assertEqual(checked, COVERAGE["category_subsets"])

    def test_identity_and_composition_are_separate_obligations(self):
        n, identities, compose = cyclic_three()
        self.assertEqual(admissible_subcategory(n, identities, compose, set()),
                         {"identities": False, "composition": True, "subcategory": False})
        self.assertEqual(admissible_subcategory(n, identities, compose, {0, 1}),
                         {"identities": True, "composition": False, "subcategory": False})
        n, identities, compose = walking_arrow()
        # A genuine non-wide subcategory exists on A alone; the API fixes objects.
        self.assertEqual(admissible_subcategory(n, identities, compose, {0}),
                         {"identities": False, "composition": True, "subcategory": False})

    def test_resource_lift_uses_typed_join(self):
        labels, (n, identities, compose) = resource_category(3)
        self.assertEqual(tuple(budget_paths(3)), labels)
        lookup = {pair: i for i, pair in enumerate(labels)}
        self.assertNotIn((lookup[0, 1], lookup[0, 1]), compose)
        self.assertEqual(compose[lookup[0, 1], lookup[1, 3]], lookup[0, 3])
        self.assertTrue(admissible_subcategory(n, identities, compose, range(n))["subcategory"])
        # Deleting the composite breaks closure even though each one-step cost fits.
        self.assertFalse(admissible_subcategory(n, identities, compose,
                         set(range(n)) - {lookup[0, 3]})["composition"])
        for limit in range(4):
            self.assertEqual(tuple(budget_paths(limit)), resource_category(limit)[0])

    def test_infinite_natural_cost_cutoff_has_finite_witness_only(self):
        # N,+ is an infinite one-object category. {0,1,2} is merely a sample;
        # it must never be passed off as a finite composition table for N.
        allowed = {0, 1}
        sampled = {(a, b): a + b for a, b in product(allowed, repeat=2)}
        self.assertEqual(sampled[1, 1], 2)
        self.assertNotIn(sampled[1, 1], allowed)
        self.assertFalse(reference_admissibility((0,), sampled, allowed)["composition"])
        with self.assertRaises(ValueError):
            admissible_subcategory(3, (0,), sampled, allowed)

    def test_malformed_ambient_presentations_rejected(self):
        n, units, table = cyclic_three()
        broken_associativity = {(a, b): [[0, 1, 2], [1, 2, 0], [2, 0, 2]][a][b]
                                for a, b in product(range(3), repeat=2)}
        cases = [
            (0, (), {}, ()), (-1, (), {}, ()), (True, (0,), {(0, 0): 0}, (0,)),
            (n, (), table, ()), (n, (0, 0), table, (0,)),
            (n, (0, 9), table, (0,)), (n, (1,), table, (0,)),
            (n, units, {}, (0,)),
            (n, units, {**table, (1, 2): 9}, (0,)),
            (n, units, {**table, (3, 0): 0}, (0,)),
            (n, units, table, (3,)), (n, units, table, (-1,)),
            (n, units, broken_associativity, range(n)),
        ]
        self.assertEqual(len(cases) + 1, COVERAGE["malformed_ambient"])
        for args in cases:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    admissible_subcategory(*args)
        n, units, table = walking_arrow()
        # A fake join between incompatible object types cannot be made legal.
        with self.assertRaises(ValueError):
            admissible_subcategory(n, units, {**table, (2, 2): 2}, range(n))

    def test_every_single_entry_c3_corruption_rejected(self):
        n, units, table = cyclic_three()
        corruptions = []
        for pair, original in table.items():
            missing = dict(table)
            del missing[pair]
            corruptions.append(missing)
            for wrong in set(range(n)) - {original}:
                corruptions.append({**table, pair: wrong})
        self.assertEqual(len(corruptions), COVERAGE["c3_corruptions"])
        for table in corruptions:
            with self.subTest(table=table), self.assertRaises(ValueError):
                admissible_subcategory(n, units, table, range(n))

    def test_noninteger_aliases_rejected_before_deduplication(self):
        n, units, table = cyclic_three()
        cases = ([0, False], [1, True], [0, 0.0], [1, 1.0], [1, Q(1)])
        self.assertEqual(len(cases), COVERAGE["noninteger_aliases"])
        for allowed in cases:
            with self.subTest(allowed=allowed), self.assertRaises(ValueError):
                admissible_subcategory(n, units, table, allowed)

    def test_malformed_budget_rejected(self):
        cases = (-1, True, 1.5, "2", None)
        self.assertEqual(len(cases), COVERAGE["malformed_budgets"])
        for limit in cases:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                budget_paths(limit)


class AggregationTests(unittest.TestCase):
    def test_exhaustive_rational_profile_grid(self):
        count = 0
        for profile in product((Q(-1), Q(0), Q(1)), repeat=3):
            for numerators in product(range(5), repeat=3):
                if sum(numerators) != 4:
                    continue
                weights = tuple(Q(n, 4) for n in numerators)
                actual = aggregates(profile, weights)
                self.assertEqual(actual, reference_aggregates(profile, weights))
                self.assertLessEqual(actual["min"], actual["weighted"])
                self.assertLessEqual(actual["weighted"], actual["max"])
                count += 1
        self.assertEqual(count, COVERAGE["aggregation_cases"])

    def test_exact_fraction_and_degenerate_profile(self):
        self.assertEqual(aggregates((Q(1, 3), Q(2, 7)), (Q(2, 5), Q(3, 5))),
                         {"min": Q(2, 7), "max": Q(1, 3), "weighted": Q(32, 105)})
        self.assertEqual(aggregates((7,), (1,)),
                         {"min": Q(7), "max": Q(7), "weighted": Q(7)})

    def test_min_and_max_not_forced_fixed_weight_means(self):
        # Analytic proof: min(e1)=min(e2)=0 forces both weights to zero,
        # contradicting normalization. Grid checks corroborate, not prove it.
        count = 0
        for denominator in range(1, 17):
            for numerator in range(denominator + 1):
                count += 1
                w = (Q(numerator, denominator), 1 - Q(numerator, denominator))
                pair = [aggregates(profile, w) for profile in ((1, 0), (0, 1))]
                self.assertEqual(sum(item["weighted"] for item in pair), 1)
                self.assertEqual(sum(item["min"] for item in pair), 0)
                self.assertEqual(sum(item["max"] for item in pair), 2)
                self.assertTrue(any(item["min"] != item["weighted"] for item in pair))
                self.assertTrue(any(item["max"] != item["weighted"] for item in pair))
        self.assertEqual(count, COVERAGE["fixed_weight_vectors"])

    def test_pareto_incomparability_survives_choice_of_aggregator(self):
        first, second = (1, 0), (0, 1)
        self.assertFalse(all(a >= b for a, b in zip(first, second)))
        self.assertFalse(all(b >= a for a, b in zip(first, second)))
        self.assertGreater(aggregates(first, (1, 0))["weighted"],
                           aggregates(second, (1, 0))["weighted"])
        self.assertLess(aggregates(first, (0, 1))["weighted"],
                        aggregates(second, (0, 1))["weighted"])

    def test_malformed_profiles_and_weights_rejected(self):
        cases = [((), ()), ((1, 2), (1,)), ((1,), (1, 0)), ((1,), (0,)),
                 ((1, 2), (-1, 2)), ((1, 2), (1, 1)),
                 ((1.0,), (1,)), ((True,), (1,)), (("1",), (1,)),
                 ((None,), (1,)), ((1,), (1.0,)), ((1,), (True,)),
                 ((1,), ("1",)), ((1,), (None,))]
        self.assertEqual(len(cases), COVERAGE["malformed_aggregation"])
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                aggregates(*args)


if __name__ == "__main__":
    unittest.main()
