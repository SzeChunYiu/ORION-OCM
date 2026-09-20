"""Actual group folds, same nonconstant parity context and different kernels."""
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

core,oracle = load('algebra_v16'),load('oracle_v16')
COVERAGE = {}


class AlgebraTests(unittest.TestCase):
    def test_all_words_and_actual_laws(self):
        models = (core.c4(),core.v4())
        operations = (oracle.c4_product,oracle.v4_product)
        products = associative = units = homomorphisms = words = folds = 0
        lengths = {i:0 for i in range(7)}
        for model,operation in zip(models,operations):
            self.assertEqual(model.identity,0)
            for a in range(4):
                self.assertEqual(model.table[0][a],a)
                self.assertEqual(model.table[a][0],a)
                units += 2
            for a,b in product(range(4),repeat=2):
                self.assertEqual(model.table[a][b],operation((a,b)))
                products += 1
                self.assertEqual(model.table[a][b] % 2,(a % 2+b % 2) % 2)
                homomorphisms += 1
                for c in range(4):
                    self.assertEqual(model.table[model.table[a][b]][c],model.table[a][model.table[b][c]])
                    associative += 1
        seen = set()
        for word in oracle.words(6):
            expected = oracle.parity(word)
            for model,operation in zip(models,operations):
                self.assertEqual(core.fold(model,word),operation(word))
                self.assertEqual(core.context(model,word),expected)
                folds += 1
            self.assertEqual(core.context(models[0],word),core.context(models[1],word))
            words += 1
            lengths[len(word)] += 1
            seen.add(expected)
        self.assertEqual(words,5461)
        self.assertEqual(seen,{0,1})
        self.assertNotEqual(models[0].table[1][1],models[1].table[1][1])
        self.assertEqual(core.fold(models[0],(1,1)),core.fold(models[0],(2,)))
        self.assertNotEqual(core.fold(models[1],(1,1)),core.fold(models[1],(2,)))
        COVERAGE.update(group_products=products,group_associativity=associative,group_unit_equations=units,
                        parity_homomorphisms=homomorphisms,words=words,independent_folds=folds,
                        nonconstant_context_controls=1,different_quotient_kernel_controls=1)
        COVERAGE.update({'words_length_'+str(k):v for k,v in lengths.items()})

    def test_algebra_hostiles(self):
        model = core.c4()
        invalid = []
        for table in ((),[],((0,1),),((True,),),((0.0,),),((-1,),),((1,),),([0],)):
            invalid.append(lambda t=table:core.Monoid(t,0))
        for identity in (-1,4,True,0.0,None):
            invalid.append(lambda i=identity:core.Monoid(model.table,i))
        invalid += [lambda:core.Monoid(((0,1,2),(1,2,0),(2,0,0)),0),
                    lambda:core.Monoid(((1,0),(0,1)),0)]
        for word in ([0],(True,),(0.0,),(-1,),(4,),None,'12'):
            invalid.append(lambda w=word:core.fold(model,w))
        invalid.append(lambda:core.fold(None,()))
        for i,call in enumerate(invalid):
            with self.subTest(case=i),self.assertRaises(ValueError):
                call()
        # Reindexing one multiplication without the observation changes the claim.
        rename = (0,2,1,3)
        table = tuple(tuple(rename[model.table[rename[a]][rename[b]]] for b in range(4)) for a in range(4))
        changed = core.Monoid(table,0)
        self.assertNotEqual(core.context(changed,(2,2)),core.context(core.v4(),(2,2)))
        self.assertNotEqual(0,core.context(model,(1,)))
        self.assertNotEqual(core.context(model,(1,)),core.fold(model,(2,)) % 2)
        COVERAGE.update(algebra_malformed_rejections=len(invalid),unmatched_label_controls=1,
                        constant_selector_rejections=1,wrong_fold_context_rejections=1)


if __name__ == '__main__':
    program = unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
