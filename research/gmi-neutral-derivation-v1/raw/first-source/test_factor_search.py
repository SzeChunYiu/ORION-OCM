"""Finite order completeness, ties, unfavorable orders and search accounting."""

import itertools
import math
import unittest

from factor_cases import make_case
from factor_compile import eliminate
from factor_search import search_orders


class FactorSearchTests(unittest.TestCase):
    def test_search_contains_every_order_with_all_minimizers(self):
        sizes, factors, algebra = make_case(dict(graph="chain", variables=4,
                                                 domain_size=2), "rational")
        result = search_orders(sizes, factors, algebra)
        expected = {order: eliminate(sizes, factors, algebra, order)["profile"]
                    for order in itertools.permutations(range(4))}
        key = lambda p: (p["work"], p["peak_table_entries"])
        minimum = min(key(p) for p in expected.values())
        winners = sorted(order for order, profile in expected.items()
                         if key(profile) == minimum)
        self.assertEqual(result["ties"], winners)
        self.assertEqual(result["best"]["order"], winners[0])
        self.assertEqual({tuple(row["order"]) for row in result["candidates"]},
                         set(expected))
        self.assertEqual(result["search"]["scalar_work"],
                         sum(p["work"] for p in expected.values()))
        self.assertEqual(result["search"]["candidates"], math.factorial(4))
        self.assertEqual(result["search"]["score_comparisons"], 23)

    def test_clique_all_orders_tie_and_negative_order_star(self):
        sizes, factors, algebra = make_case(dict(graph="clique", variables=4,
                                                 domain_size=2), "boolean")
        result = search_orders(sizes, factors, algebra)
        self.assertEqual(len(result["ties"]), 24)
        self.assertEqual({p["width"] for p in result["candidates"]}, {3})
        sizes, factors, algebra = make_case(dict(graph="star", variables=4,
                                                 domain_size=2), "min_plus")
        first = eliminate(sizes, factors, algebra, (0, 1, 2, 3))
        last = eliminate(sizes, factors, algebra, (1, 2, 3, 0))
        self.assertEqual(first["profile"]["work"], 156)
        self.assertEqual(last["profile"]["work"], 52)
        self.assertEqual(first["value"], last["value"])
        self.assertEqual((first["profile"]["width"], last["profile"]["width"]), (3, 1))

    def test_width_upper_bound_every_order_on_varied_graphs(self):
        for graph in ("chain", "star", "cycle", "clique"):
            sizes, factors, algebra = make_case(dict(graph=graph, variables=4,
                                                     domain_size=2), "rational")
            result = search_orders(sizes, factors, algebra)
            for candidate in result["candidates"]:
                bound = (2 * len(factors) + 3 * 4) * 2 ** (candidate["width"] + 1)
                bound += 2 * (len(factors) + 4)
                self.assertLessEqual(candidate["work"], bound)


if __name__ == "__main__":
    unittest.main()
