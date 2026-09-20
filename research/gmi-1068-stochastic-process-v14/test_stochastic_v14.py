"""Exhaustive finite calibration against independent path semantics."""
from fractions import Fraction as Q
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

core, oracle = load('stochastic_v14'), load('independent_oracle_v14')
COVERAGE = {}


class StochasticTests(unittest.TestCase):
    def test_all_kernels(self):
        arrows = [(a, core.Kernel(*a)) for a in oracle.kernels()]
        pairs = triples = units = outside = 0
        for a, actual in arrows:
            self.assertEqual(oracle.as_tuple(actual), a)
            self.assertEqual(core.compose_kernel(core.identity_kernel(a[0]), actual), actual)
            self.assertEqual(core.compose_kernel(actual, core.identity_kernel(a[1])), actual)
            self.assertEqual(oracle.as_tuple(core.support(actual)), oracle.positive_support(a))
            units += 2
            for b, next_arrow in arrows:
                if a[1] != b[0]:
                    continue
                composed = core.compose_kernel(actual, next_arrow)
                self.assertEqual(oracle.as_tuple(composed), oracle.path_sum((a, b)))
                self.assertEqual(core.support(composed), core.compose_relation(core.support(actual), core.support(next_arrow)))
                pairs += 1
                outside += any(value not in oracle.GRID for row in composed.rows for value in row)
                for c, last in arrows:
                    if b[1] != c[0]:
                        continue
                    left = core.compose_kernel(composed, last)
                    right = core.compose_kernel(actual, core.compose_kernel(next_arrow, last))
                    self.assertEqual(left, right)
                    self.assertEqual(oracle.as_tuple(left), oracle.path_sum((a, b, c)))
                    triples += 1
        self.assertGreater(outside, 0)
        COVERAGE.update(kernels=len(arrows), kernel_pairs=pairs, kernel_triples=triples,
                        kernel_unit_equations=units, support_composition_equations=pairs,
                        products_outside_input_grid=outside)

    def test_all_relations(self):
        arrows = [(a, core.Relation(*a)) for a in oracle.relations()]
        pairs = triples = units = 0
        for a, actual in arrows:
            self.assertEqual(oracle.as_tuple(actual), a)
            self.assertEqual(core.compose_relation(core.identity_relation(a[0]), actual), actual)
            self.assertEqual(core.compose_relation(actual, core.identity_relation(a[1])), actual)
            self.assertEqual(core.support(core.uniformize(actual)), actual)
            units += 2
            for b, next_arrow in arrows:
                if a[1] != b[0]:
                    continue
                composed = core.compose_relation(actual, next_arrow)
                self.assertEqual(oracle.as_tuple(composed), oracle.reachable((a, b)))
                pairs += 1
                for c, last in arrows:
                    if b[1] != c[0]:
                        continue
                    left = core.compose_relation(composed, last)
                    self.assertEqual(left, core.compose_relation(actual, core.compose_relation(next_arrow, last)))
                    self.assertEqual(oracle.as_tuple(left), oracle.reachable((a, b, c)))
                    triples += 1
        COVERAGE.update(relations=len(arrows), relation_pairs=pairs, relation_triples=triples,
                        relation_unit_equations=units, uniform_support_equations=len(arrows))

    def test_deterministic_embeddings(self):
        arrows = tuple(oracle.maps())
        pairs = faithful = units = triples = 0
        for a in arrows:
            kernel, relation = core.dirac(*a), core.graph(*a)
            self.assertEqual(oracle.as_tuple(kernel), oracle.deterministic_kernel(a))
            self.assertEqual(oracle.as_tuple(relation), oracle.deterministic_relation(a))
            self.assertEqual(core.support(kernel), relation)
            if a[0] == a[1] and a[2] == tuple(range(a[0])):
                self.assertEqual(kernel, core.identity_kernel(a[0]))
                self.assertEqual(relation, core.identity_relation(a[0]))
                units += 2
            for b in arrows:
                if a[:2] == b[:2]:
                    self.assertEqual(kernel == core.dirac(*b), a == b)
                    self.assertEqual(relation == core.graph(*b), a == b)
                    faithful += 2
                if a[1] == b[0]:
                    composed = oracle.compose_maps(a, b)
                    self.assertEqual(core.compose_kernel(kernel, core.dirac(*b)), core.dirac(*composed))
                    self.assertEqual(core.compose_relation(relation, core.graph(*b)), core.graph(*composed))
                    pairs += 2
                    for c in arrows:
                        if b[1] != c[0]:
                            continue
                        expected = oracle.compose_maps(composed, c)
                        self.assertEqual(oracle.compose_maps(a, oracle.compose_maps(b, c)), expected)
                        self.assertEqual(core.compose_kernel(core.compose_kernel(kernel, core.dirac(*b)), core.dirac(*c)), core.dirac(*expected))
                        self.assertEqual(core.compose_relation(core.compose_relation(relation, core.graph(*b)), core.graph(*c)), core.graph(*expected))
                        triples += 2
        COVERAGE.update(embedding_triple_equations=triples, deterministic_maps=len(arrows), embedding_composition_equations=pairs,
                        embedding_faithfulness_equations=faithful, embedding_identity_equations=units)

    def test_closed_rational_witness(self):
        identity, flip = core.identity_kernel(2), core.dirac(2, 2, (1, 0))
        constants = [core.Kernel(2, 2, ((1-p, p), (1-p, p))) for p in oracle.GRID]
        arrows = [identity, flip] + constants
        self.assertEqual(len(set(arrows)), 7)
        pairs = triples = 0
        for a, b in product(arrows, repeat=2):
            composed = core.compose_kernel(a, b)
            self.assertIn(composed, arrows)
            self.assertEqual(oracle.as_tuple(composed), oracle.path_sum((oracle.as_tuple(a), oracle.as_tuple(b))))
            pairs += 1
            for c in arrows:
                self.assertEqual(core.compose_kernel(composed, c), core.compose_kernel(a, core.compose_kernel(b, c)))
                triples += 1
        for p, a in zip(oracle.GRID, constants):
            self.assertEqual(core.compose_kernel(a, flip), constants[oracle.GRID.index(1-p)])
            self.assertEqual(core.compose_kernel(flip, a), a)
            for b in constants:
                self.assertEqual(core.compose_kernel(a, b), b)
        self.assertEqual(core.compose_kernel(flip, flip), identity)
        self.assertEqual(core.support(constants[1]), core.support(constants[3]))
        self.assertEqual(constants[1].rows[0][1], Q(1, 3))
        self.assertEqual(constants[3].rows[0][1], Q(2, 3))
        self.assertNotEqual(constants[1].rows[0][1], constants[3].rows[0][1])
        self.assertEqual(sum(all(sum(v > 0 for v in row) == 1 for row in a.rows) for a in arrows), 4)
        COVERAGE.update(closed_witness_arrows=len(arrows), closed_witness_pairs=pairs,
                        closed_witness_triples=triples, probability_loss_witnesses=1)


if __name__ == '__main__':
    program = unittest.main(exit=False, verbosity=2)
    print(json.dumps(COVERAGE, sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
