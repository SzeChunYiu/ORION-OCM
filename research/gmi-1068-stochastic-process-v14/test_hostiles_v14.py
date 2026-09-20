"""Scope boundaries, actual countermodels and malformed-input rejection."""
from fractions import Fraction as Q
import importlib.util
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


class HostileTests(unittest.TestCase):
    def test_malformed_inputs(self):
        calls = []
        for constructor in (core.Kernel, core.Relation):
            for bad in (-1, True, 1.0, '1', None):
                calls += [lambda c=constructor, b=bad: c(b, 0, ()),
                          lambda c=constructor, b=bad: c(0, b, ())]
            for rows in ({}, '', iter(()), None):
                calls.append(lambda c=constructor, r=rows: c(0, 0, r))
            calls += [lambda c=constructor: c(1, 1, ()),
                      lambda c=constructor: c(0, 1, ((0,),)),
                      lambda c=constructor: c(1, 0, ((),)),
                      lambda c=constructor: c(1, 1, ('bad',))]
        for rows in (((True,),), ((1.0,),), ((-1,),), ((Q(1,2),),),
                     ((1, 0),), ((),), ({0: 1},), ((None,),), (('1',),)):
            calls.append(lambda r=rows: core.Kernel(1, 1, r))
        for rows in (((True,),), ((0.0,),), ((-1,),), ((1,),),
                     ((),), ({0: 1},), ((None,),), (('0',),)):
            calls.append(lambda r=rows: core.Relation(1, 1, r))
        for constructor in (core.dirac, core.graph):
            for targets in ((True,), (0.0,), (-1,), (1,), (), (None,), '0', {0}, iter((0,))):
                calls.append(lambda c=constructor, t=targets: c(1, 1, t))
            calls.append(lambda c=constructor: c(0, 0, (0,)))
        for identity in (core.identity_kernel, core.identity_relation):
            for bad in (-1, True, 1.0):
                calls.append(lambda f=identity, b=bad: f(b))
        calls += [lambda: core.compose_kernel(core.identity_kernel(1), core.identity_kernel(2)),
                  lambda: core.compose_relation(core.identity_relation(1), core.identity_relation(2)),
                  lambda: core.support(core.identity_relation(1)),
                  lambda: core.uniformize(core.identity_kernel(1))]
        for i, call in enumerate(calls):
            with self.subTest(case=i), self.assertRaises(ValueError):
                call()
        COVERAGE['malformed_input_rejections'] = len(calls)

    def test_empty_and_exact_boundaries(self):
        count = 0
        for m in range(3):
            kernel, relation = core.Kernel(0, m, []), core.Relation(0, m, [])
            self.assertEqual((kernel.n, kernel.m, kernel.rows), (0, m, ()))
            self.assertEqual((relation.n, relation.m, relation.rows), (0, m, ()))
            self.assertEqual(core.support(kernel), relation)
            self.assertEqual(core.uniformize(relation), kernel)
            count += 1
        self.assertNotEqual(core.Kernel(0, 0, ()), core.Kernel(0, 1, ()))
        self.assertNotEqual(core.Relation(0, 0, ()), core.Relation(0, 1, ()))
        tiny = Q(1, 10**400)
        kernel = core.Kernel(1, 2, [[tiny, 1-tiny]])
        self.assertEqual(core.support(kernel).rows, (frozenset((0, 1)),))
        self.assertEqual(kernel.rows[0][0], tiny)
        self.assertEqual(core.Relation(1, 2, [[0, 0, 1]]).rows, (frozenset((0,1)),))
        self.assertEqual(core.Relation(1, 2, [{0,1}]), core.Relation(1, 2, [(0,1)]))
        COVERAGE.update(empty_source_cases=count, tiny_positive_support_cases=1,
                        accepted_container_cases=3)

    def test_assumption_and_functor_countermodels(self):
        first = core.Relation(1, 2, ((0,1),))
        second = core.Relation(2, 3, ((0,), (1,2)))
        sequential = core.compose_kernel(core.uniformize(first), core.uniformize(second))
        direct = core.uniformize(core.compose_relation(first, second))
        self.assertEqual(sequential.rows, ((Q(1,2), Q(1,4), Q(1,4)),))
        self.assertEqual(direct.rows, ((Q(1,3),)*3,))
        self.assertNotEqual(sequential, direct)
        reset = core.dirac(2, 2, (0,0))
        flip = core.dirac(2, 2, (1,0))
        self.assertNotEqual(core.compose_kernel(reset, flip), core.compose_kernel(flip, reset))
        self.assertEqual(core.compose_kernel(reset, flip).rows, ((0,1), (0,1)))
        # Real nonzero entries can cancel when the nonnegativity premise is dropped.
        signed = ((1, 2, ((Q(1), Q(-1)),)), (2, 1, ((Q(1),), (Q(1),))))
        self.assertEqual(oracle.path_sum(signed)[2], ((Q(0),),))
        self.assertTrue(any(signed[0][2][0][j] != 0 and signed[1][2][j][0] != 0 for j in range(2)))
        # Row normalization alone cannot repair signed cancellation.
        normalized = ((1, 2, ((Q(1,2), Q(1,2)),)),
                      (2, 2, ((Q(1), Q(0)), (Q(-1), Q(2)))))
        self.assertTrue(all(sum(row) == 1 for arrow in normalized for row in arrow[2]))
        self.assertEqual(oracle.path_sum(normalized)[2], ((Q(0), Q(1)),))
        self.assertTrue(any(normalized[0][2][0][j] != 0 and normalized[1][2][j][0] != 0
                            for j in range(2)))
        # Coordinatewise N×N is zero-sum-free, yet has zero divisors.
        a, b, zero = (1, 0), (0, 1), (0, 0)
        self.assertNotEqual(a, zero)
        self.assertNotEqual(b, zero)
        self.assertEqual(tuple(x*y for x,y in zip(a,b)), zero)
        self.assertEqual(tuple(x+y for x,y in zip(a,b)), (1,1))
        # Nonzero factors need not have nonzero product in a ring with zero divisors.
        self.assertNotEqual(2 % 4, 0)
        self.assertEqual((2 * 2) % 4, 0)
        # A transposed/reversed product and thresholded support both change actual witnesses.
        self.assertNotEqual(oracle.path_sum((oracle.as_tuple(reset), oracle.as_tuple(flip))),
                            oracle.path_sum((oracle.as_tuple(flip), oracle.as_tuple(reset))))
        tiny = core.Kernel(1, 2, ((Q(1,10**400), 1-Q(1,10**400)),))
        self.assertNotEqual(core.support(tiny).rows,
                            tuple(frozenset(j for j,v in enumerate(row) if float(v)>0) for row in tiny.rows))
        COVERAGE.update(uniformization_counterexamples=1, reversed_order_counterexamples=1,
                        missing_assumption_counterexamples=4, corrupt_semantics_controls=2)


if __name__ == '__main__':
    program = unittest.main(exit=False, verbosity=2)
    print(json.dumps(COVERAGE, sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
