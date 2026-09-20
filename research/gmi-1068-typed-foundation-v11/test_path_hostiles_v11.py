"""Cyclic paths, typed interpretations, quotient congruence, and hostile inputs."""
import unittest
import independent_paths_v11 as oracle
import paths_v11 as core

COVERAGE = {}


class PathHostiles(unittest.TestCase):
    def test_cycles_and_mutations(self):
        chain = (4, ((0, 1), (1, 2), (2, 3)))
        good = (0, (0, 1, 2))
        self.assertEqual(core.endpoint(chain, good), 3)
        bad_paths = ((0, (0, 2)), (0, (2, 1, 0)), (0, (0, 0, 1, 2)), (1, (0, 1, 2)))
        for path in bad_paths:
            for evaluator in (core.endpoint, oracle.vertices):
                with self.assertRaises(ValueError):
                    evaluator(chain, path)
        self.assertNotEqual(core.endpoint(chain, (0, (0, 1))), core.endpoint(chain, good))
        parallel = (2, ((0, 1), (0, 1)))
        paths = set(core.enumerate_dag(parallel))
        self.assertIn((0, (0,)), paths)
        self.assertIn((0, (1,)), paths)
        self.assertEqual(len(paths), 4)
        loop = (1, ((0, 0), (0, 0)))
        self.assertNotEqual((0, (0,)), core.identity(loop, 0))
        self.assertNotEqual((0, (0, 0)), core.identity(loop, 0))
        long_paths = 0
        for length in (257, 1024, 2049):
            p, q, r = (0, (0,) * length), (0, (1,) * length), (0, (0, 1) * length)
            self.assertEqual(core.endpoint(loop, r), oracle.vertices(loop, r)[-1])
            expected = oracle.concatenate(loop, oracle.concatenate(loop, p, q), r)
            self.assertEqual(core.compose(loop, core.compose(loop, p, q), r), expected)
            self.assertEqual(core.compose(loop, p, core.compose(loop, q, r)), expected)
            self.assertEqual(len(expected[1]), 4 * length)
            long_paths += 1
        for graph in (loop, (3, ((0, 1), (1, 2), (2, 0)))):
            for enumerator in (core.enumerate_dag, oracle.complete_dag_paths):
                with self.assertRaises(ValueError):
                    enumerator(graph)
        # A length-one restriction has units but loses closure on the loop.
        short = lambda p: len(p[1]) <= 1
        edge = (0, (0,))
        self.assertTrue(short(core.identity(loop, 0)) and short(edge))
        self.assertFalse(short(core.compose(loop, edge, edge)))
        lift = (2, ((0, 1),))
        self.assertEqual(set(core.enumerate_dag(lift)), {(0, ()), (1, ()), (0, (0,))})
        with self.assertRaises(ValueError):
            core.compose(lift, edge, edge)
        COVERAGE.update(structural_path_mutations=5, long_cyclic_paths=long_paths,
                        cyclic_enumeration_rejections=4, admission_cutoff_and_lift=1)

    def test_interpretation_boundaries(self):
        cases = 0
        loop = (1, ((0, 0), (0, 0)))
        maps = ((1, 0), (0, 0))
        for word, expected in (((0, 1), (0, 0)), ((1, 0), (1, 1)),
                               ((0, 0), (0, 1)), ((), (0, 1))):
            self.assertEqual(core.interpret(loop, (0, word), (2,), maps), expected)
            self.assertEqual(oracle.concrete_evaluation(loop, (0, word), (2,), maps), expected)
            cases += 1
        # A nonidentity involution exists in the target, not as a free-path inverse.
        self.assertNotEqual((0, (0, 0)), (0, ()))
        # Nonfaithfulness is legitimate: distinct generators may share an identity map.
        for generator in (0, 1):
            self.assertEqual(core.interpret(loop, (0, (generator,)), (2,), ((0, 1), (0, 1))), (0, 1))
            cases += 1
        graph = (2, ((0, 1),))
        for domains, maps in (((0, 2), ((),)), ((0, 0), ((),)), ((2, 3), ((2, 0),))):
            for path in ((0, ()), (1, ()), (0, (0,))):
                self.assertEqual(core.interpret(graph, path, domains, maps),
                                 oracle.concrete_evaluation(graph, path, domains, maps))
                cases += 1
        for domains, maps in (((2, 0), ((0, 0),)), ((2, 3), ((0,),)), ((2, 3), ((0, 3),))):
            with self.assertRaises(ValueError):
                core.interpret(graph, (0, ()), domains, maps)
            cases += 1
        self.assertEqual(core.enumerate_dag((0, ())), ())
        self.assertEqual(oracle.complete_dag_paths((0, ())), set())
        self.assertEqual(core.quotient_dag((0, ()), {}), {"identities": (), "arrows": {}, "composition": {}})
        with self.assertRaises(ValueError):
            core.identity((0, ()), 0)
        self.assertNotEqual(core.identity(graph, 0), core.identity(graph, 1))
        with self.assertRaises(ValueError):
            core.compose(graph, core.identity(graph, 0), core.identity(graph, 1))
        self.assertEqual(cases, 18)
        COVERAGE["interpretation_boundary_cases"] = cases

    def test_quotient_controls(self):
        graph = (3, ((0, 1), (0, 1), (1, 2)))
        paths = sorted(oracle.complete_dag_paths(graph))
        labels = {p: i for i, p in enumerate(paths)}
        valid = core.quotient_dag(graph, labels)
        self.assertEqual(len(valid["arrows"]), len(paths))
        noncongruence = dict(labels)
        noncongruence[(0, (1,))] = noncongruence[(0, (0,))]
        with self.assertRaises(ValueError):
            core.quotient_dag(graph, noncongruence)
        noncongruence[(0, (1, 2))] = noncongruence[(0, (0, 2))]
        self.assertEqual(len(core.quotient_dag(graph, noncongruence)["arrows"]), len(paths) - 2)
        corruptions = []
        cross_hom = dict(labels)
        cross_hom[(1, ())] = cross_hom[(0, ())]
        corruptions.append(cross_hom)
        for value in (True, -1, 0.0):
            bad = dict(labels)
            bad[(0, ())] = value
            corruptions.append(bad)
        missing = dict(labels)
        del missing[(0, ())]
        corruptions.extend([missing, {**labels, (2, (0,)): 99}])
        for original, alias in (((0, ()), (False, ())), ((0, (0,)), (0, (False,))),
                                ((0, ()), (0.0, ()))):
            bad = dict(labels)
            value = bad.pop(original)
            bad[alias] = value
            corruptions.append(bad)
        for bad in corruptions:
            with self.assertRaises(ValueError):
                core.quotient_dag(graph, bad)
        COVERAGE["quotient_rejections"] = len(corruptions) + 1

    def test_malformed_inputs(self):
        invalid_graphs = (None, (), (-1, ()), (True, ()), (0, ((0, 0),)),
                          (1, ((False, 0),)), (1, ((0, 1),)), (1, ((0,),)))
        count = 0
        for graph in invalid_graphs:
            for validate in (core.validate, oracle.graph_data):
                with self.assertRaises(ValueError):
                    validate(graph)
                count += 1
        graph = (2, ((0, 1),))
        for path in (None, (), (False, ()), (2, ()), (0, (False,)), (0, (1,)), (0, "0")):
            for evaluator in (core.endpoint, oracle.vertices):
                with self.assertRaises(ValueError):
                    evaluator(graph, path)
                count += 1
        for allowed in ({True}, {-1}, {1}, [0], {0.0}):
            with self.assertRaises(ValueError):
                core.admitted(graph, (0, ()), allowed)
            count += 1
        for domains, maps in (((True, 1), ((0,),)), ((1, 1), ((True,),)), ((1,), ((0,),)),
                               ((1, 1), ()), ((1, 1), ((0.0,),))):
            for evaluator in (core.interpret, oracle.concrete_evaluation):
                with self.assertRaises(ValueError):
                    evaluator(graph, (0, ()), domains, maps)
                count += 1
        self.assertEqual(count, 45)
        COVERAGE["malformed_input_rejections"] = count


if __name__ == "__main__":
    unittest.main()
