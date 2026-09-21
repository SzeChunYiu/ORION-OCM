"""Generic path evaluation and actual quotient constructor equations."""
import unittest
from support_v29 import core, fixture, oracle, presentation, exact
COVERAGE = {}


class PresentationTests(unittest.TestCase):
    def test_seven_paths_and_composition(self):
        category, mapping = fixture()
        paths = oracle.all_paths((3, oracle.EDGES))
        self.assertEqual(set(core.paths.enumerate_dag(mapping.graph)), set(paths))
        count = pairs = 0
        for path in paths:
            endpoint = oracle.path_endpoint(mapping.graph, path)
            expected = (path[0], endpoint, oracle.ENDPOINTS.index((path[0], endpoint)))
            exact(self, presentation.evaluate_path(mapping, path), expected)
            count += 1
            for other in paths:
                if endpoint != other[0]:
                    with self.assertRaises(ValueError):core.paths.compose(mapping.graph, path, other)
                else:
                    composed = core.paths.compose(mapping.graph, path, other)
                    exact(self, composed, (path[0], path[1] + other[1]))
                    last = oracle.path_endpoint(mapping.graph, other)
                    exact(self, presentation.evaluate_path(mapping, composed),
                          (path[0], last, oracle.ENDPOINTS.index((path[0], last))))
                pairs += 1
        self.assertEqual((count, pairs), (7, 49))
        COVERAGE.update(path_evaluations=count, path_pairs=pairs)

    def test_actual_quotient_and_inverse_functors(self):
        target, mapping = fixture()
        result = presentation.dag_presentation(mapping)
        presentation.verify_presentation(mapping, result)
        self.assertTrue(result.generates)
        self.assertEqual(set(result.paths), set(oracle.all_paths(mapping.graph)))
        expected = tuple(oracle.ENDPOINTS.index((s, oracle.path_endpoint(mapping.graph, (s,w))))
                         for s,w in result.paths)
        classes = tuple(dict.fromkeys(expected))
        exact(self, result.class_of, tuple(classes.index(x) for x in expected))
        exact(self, result.representatives,
              tuple(result.paths[expected.index(x)] for x in classes))
        exact(self, result.lower.arrow_map, classes)
        products = inverses = 0
        for arrow, endpoint in enumerate(classes):
            exact(self, (result.category.source[arrow], result.category.target[arrow]),
                  oracle.ENDPOINTS[endpoint])
            self.assertEqual(result.quote.arrow_map[result.lower.arrow_map[arrow]], arrow)
            self.assertEqual(result.lower.arrow_map[result.quote.arrow_map[arrow]], arrow)
            inverses += 2
            for other, other_endpoint in enumerate(classes):
                s,t = oracle.ENDPOINTS[endpoint]; u,v = oracle.ENDPOINTS[other_endpoint]
                product = classes.index(oracle.ENDPOINTS.index((s,v))) if t == u else None
                exact(self, result.category.table.rows[arrow][other], product)
                tree = ('seq', ('arrow', arrow), ('arrow', other))
                response = core.trees.typed_eval(result.category, tree)
                mapped_tree = core.functors.map_tree(result.lower, tree)
                exact(self, core.trees.typed_eval(target, mapped_tree),
                      core.functors.map_response(result.lower, response))
                exact(self, core.functors.map_tree(result.quote, mapped_tree), tree)
                products += 1
        self.assertEqual((products,inverses), (36,12))
        COVERAGE.update(quotient_products=products,inverse_arrow_equations=inverses,
                        valid_presentation_certificates=1)
