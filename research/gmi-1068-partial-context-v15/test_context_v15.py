"""Exhaustive partial-context and fixed-full-process reversal calibration."""
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name+'.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

core, oracle = load('context_v15'), load('independent_oracle_v15')
COVERAGE = {}


class ContextTests(unittest.TestCase):
    def test_all_partial_contexts(self):
        counts = dict(contexts=0, observations=0, comparisons=0, reflexivity=0,
                      transitivity=0, equivalence_equations=0, representative_equations=0,
                      quotient_reflexivity=0, quotient_transitivity=0,
                      quotient_antisymmetry=0, quotient_comparison_equations=0, empty_domains=0,
                      equivalence_reflexivity=0, equivalence_symmetry=0, equivalence_transitivity=0)
        orders = tuple(oracle.preorders(3))
        self.assertEqual(len(orders), 29)
        for model in oracle.corpus():
            context = core.Context(3, 3, *model)
            domain, rel = oracle.domain(model), oracle.relation(model)
            groups, order = core.quotient(context)
            self.assertEqual(core.domain(context), domain)
            self.assertEqual((groups, order), oracle.quotient(model))
            counts['contexts'] += 1
            counts['empty_domains'] += not domain
            for h in range(3):
                self.assertEqual(core.observe(context,h), oracle.observation(model,h))
                counts['observations'] += 1
            equivalent = lambda a,b: (a,b) in rel and (b,a) in rel
            for a in domain:
                self.assertTrue(core.compare(context,a,a))
                counts['reflexivity'] += 1
                self.assertTrue(equivalent(a,a))
                counts['equivalence_reflexivity'] += 1
            for a,b in product(domain, repeat=2):
                self.assertEqual(core.compare(context,a,b), (a,b) in rel)
                counts['comparisons'] += 1
                self.assertEqual(equivalent(a,b),equivalent(b,a))
                counts['equivalence_symmetry'] += 1
                self.assertEqual(any(a in group and b in group for group in groups),
                                 (a,b) in rel and (b,a) in rel)
                counts['equivalence_equations'] += 1
            for a,b,c in product(domain, repeat=3):
                self.assertTrue(not ((a,b) in rel and (b,c) in rel) or (a,c) in rel)
                counts['transitivity'] += 1
                self.assertTrue(not (equivalent(a,b) and equivalent(b,c)) or equivalent(a,c))
                counts['equivalence_transitivity'] += 1
            for a,b,c,d in product(domain, repeat=4):
                if (a,c) in rel and (c,a) in rel and (b,d) in rel and (d,b) in rel:
                    self.assertEqual(core.compare(context,a,b), core.compare(context,c,d))
                    counts['representative_equations'] += 1
            for i,left in enumerate(groups):
                self.assertTrue(order[i][i])
                counts['quotient_reflexivity'] += 1
                for j,right in enumerate(groups):
                    self.assertTrue(not (order[i][j] and order[j][i]) or i == j)
                    counts['quotient_antisymmetry'] += 1
                    for a,b in product(left,right):
                        self.assertEqual(order[i][j], core.compare(context,a,b))
                        counts['quotient_comparison_equations'] += 1
                    for k in range(len(groups)):
                        self.assertTrue(not (order[i][j] and order[j][k]) or order[i][k])
                        counts['quotient_transitivity'] += 1
        self.assertEqual(counts['contexts'], 3625)
        COVERAGE.update(preorders=len(orders), **counts)

    def test_all_opposite_evaluators(self):
        reversals = formula_equations = 0
        for model in oracle.corpus():
            context = core.Context(3, 3, *model)
            domain = oracle.domain(model)
            for lo,hi in product(range(3), repeat=2):
                if not (model[3][lo][hi] and not model[3][hi][lo]):
                    continue
                for a,b in product(domain, repeat=2):
                    if a == b:
                        continue
                    first, second = core.opposite(context,a,b,lo,hi,lambda _: True)
                    expected = oracle.opposite_values(model,a,lo,hi)
                    self.assertEqual(first.values,expected[0])
                    self.assertEqual(second.values,expected[1])
                    formula_equations += 2
                    for changed in (first,second):
                        self.assertEqual((changed.n,changed.m,changed.admitted,changed.defined,changed.order),
                                         (context.n,context.m,context.admitted,context.defined,context.order))
                        self.assertEqual(oracle.relation(oracle.context_tuple(changed)),
                                         frozenset((x,y) for x,y in product(domain,repeat=2)
                                                   if core.compare(changed,x,y)))
                    self.assertTrue(core.compare(first,a,b))
                    self.assertFalse(core.compare(first,b,a))
                    self.assertFalse(core.compare(second,a,b))
                    self.assertTrue(core.compare(second,b,a))
                    self.assertNotEqual(first.values, second.values)
                    reversals += 1
        COVERAGE['opposite_evaluator_pairs'] = reversals
        COVERAGE['opposite_formula_equations'] = formula_equations

    def test_complete_process_is_fixed(self):
        process = oracle.cyclic_process()
        table, unit = process['composition'], process['identities'][0]
        laws = 0
        for a in range(3):
            self.assertEqual(table[unit][a],a)
            self.assertEqual(table[a][unit],a)
            laws += 2
            for b in range(3):
                self.assertEqual(process['arrows'][table[a][b]], (0,0))
                laws += 1
                for c in range(3):
                    self.assertEqual(table[table[a][b]][c], table[a][table[b][c]])
                    laws += 1
        context = core.Context(3,2,process['admitted'],(True,)*3,(0,0,0),((True,True),(False,True)))
        first,second = core.opposite(context,1,2,0,1,lambda _:True)
        models = ((process,first),(process,second))
        self.assertIs(models[0][0], models[1][0])
        self.assertEqual(models[0][0], oracle.cyclic_process())
        self.assertEqual(set(process), {'objects','arrows','identities','composition','admitted'})
        self.assertNotEqual(core.compare(first,1,2), core.compare(second,1,2))
        self.assertNotEqual(first.values,second.values)
        COVERAGE.update(full_process_law_equations=laws, full_process_collisions=1)


if __name__ == '__main__':
    program = unittest.main(exit=False, verbosity=2)
    print(json.dumps(COVERAGE, sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
