"""Independent exact simplex and lower-envelope calibration."""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v18 as oracle
import measures_v18 as core
from core_v18 import decoded
COVERAGE = {}


class MeasureTests(unittest.TestCase):
    def test_profiles_simplex_and_lower_envelopes(self):
        count = dict(profiles=0,profile_pairs=0,pair_weight_checks=0,
                     probability_vectors=0,constant_expectations=0,prior_families=0,
                     profile_family_values=0,pair_family_checks=0,constant_lower_values=0)
        for n in range(4):
            profiles,weights = oracle.profiles(n),oracle.simplex(n)
            count['profiles'] += len(profiles)
            count['probability_vectors'] += len(weights)
            for weight in weights:
                for constant in (F(0),F(1,2),F(1)):
                    self.assertEqual(core.expectation(weight,(constant,)*n),constant)
                    count['constant_expectations'] += 1
            for x,y in product(profiles,repeat=2):
                pointwise = all(a<=b for a,b in zip(x,y))
                comparisons = []
                for weight in weights:
                    sx,sy = core.expectation(weight,x),core.expectation(weight,y)
                    self.assertEqual(sx,oracle.inner(weight,x))
                    self.assertEqual(sy,oracle.inner(weight,y))
                    comparisons.append(sx<=sy)
                    count['pair_weight_checks'] += 1
                self.assertEqual(all(comparisons),pointwise)
                count['profile_pairs'] += 1
        profiles = oracle.profiles(2)
        for family in oracle.families(oracle.simplex(2)):
            count['prior_families'] += 1
            for profile in profiles:
                self.assertEqual(core.lower(family,profile),oracle.lower(family,profile))
                if len(family)==1:
                    self.assertEqual(core.lower(family,profile),core.expectation(family[0],profile))
                count['profile_family_values'] += 1
            for x,y in product(profiles,repeat=2):
                sx,sy = core.lower(family,x),core.lower(family,y)
                if all(a<=b for a,b in zip(x,y)):
                    self.assertLessEqual(sx,sy)
                self.assertEqual(sx<=sy,oracle.lower(family,x)<=oracle.lower(family,y))
                count['pair_family_checks'] += 1
            for constant in (F(0),F(1,2),F(1)):
                self.assertEqual(core.lower(family,(constant,)*2),constant)
                count['constant_lower_values'] += 1
        self.assertEqual(count,dict(profiles=40,profile_pairs=820,pair_weight_checks=11349,
            probability_vectors=21,constant_expectations=63,prior_families=31,
            profile_family_values=279,pair_family_checks=2511,constant_lower_values=93))
        COVERAGE.update(count)

    def test_actual_partial_contexts_and_missing_premises(self):
        p = (True,True,True,False,False)
        contexts = observations = 0
        for n in range(1,4):
            x,y = (F(0),)*n,(F(1),)*n
            values = (None,x,y,None,x)
            for weight in oracle.simplex(n):
                encoded = core.expectation_context(p,values,weight)
                self.assertEqual(encoded.context.admitted,p)
                self.assertEqual(encoded.context.defined,(False,True,True,False,True))
                expected = (('UNDEFINED',None),('VALUE',F(0)),('VALUE',F(1)),
                            ('ILLEGAL',None),('ILLEGAL',None))
                self.assertEqual(tuple(decoded(encoded,h) for h in range(5)),expected)
                contexts += 1
                observations += 5
        for family in oracle.families(oracle.simplex(2)):
            values = (None,(F(0),F(0)),(F(1),F(1)),None,(F(0),F(1)))
            encoded = core.lower_context(p,values,family)
            self.assertEqual(encoded.context.admitted,p)
            self.assertEqual(encoded.context.defined,(False,True,True,False,True))
            self.assertEqual(tuple(decoded(encoded,h) for h in range(5)),expected)
            contexts += 1
            observations += 5
        x,y = (F(1),F(0)),(F(0),F(0))
        self.assertEqual(core.expectation((F(0),F(1)),x),core.expectation((F(0),F(1)),y))
        self.assertFalse(all(a<=b for a,b in zip(x,y)))
        family = ((F(1),F(0)),(F(0),F(1)))
        e1,e2 = family
        self.assertEqual(core.lower(family,e1)+core.lower(family,e2),0)
        self.assertEqual(core.lower(family,(F(1),F(1))),1)
        self.assertEqual((contexts,observations),(52,260))
        COVERAGE.update(actual_measure_contexts=contexts,context_observations=observations,
                        omitted_coordinate_controls=1,nonlinear_lower_controls=1)


if __name__ == '__main__':
    result = unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
