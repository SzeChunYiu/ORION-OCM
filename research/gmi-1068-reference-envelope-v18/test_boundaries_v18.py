"""Operational timing, conditional inconsistency and explicit scope boundaries."""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v18 as oracle
import measures_v18 as measure
import prefix_v18 as prefix
import interaction_v18 as interaction
COVERAGE = {}


class BoundaryTests(unittest.TestCase):
    def test_actual_one_shot_environment(self):
        cases = 0
        for target in range(2):
            for size in range(7):
                for actions in product(range(2),repeat=size):
                    expected = int(size==1 and actions[0]==target)
                    self.assertEqual(interaction.reward(target,actions),expected)
                    total = sum(interaction.reward(target,actions[:n]) for n in range(size+1))
                    self.assertEqual(total,int(size>0 and actions[0]==target))
                    self.assertLessEqual(total,1)
                    cases += 1
        policies = tuple(tuple(F(interaction.reward(target,(action,))) for target in range(2))
                         for action in range(2))
        self.assertEqual(policies,((F(1),F(0)),(F(0),F(1))))
        base = prefix.Book(3,(((False,False),0),((False,True),1),((True,),2)))
        reversals = 0
        for tail0,tail1 in product((F(0),F(1,2),F(1)),repeat=2):
            x,y = policies[0]+(tail0,),policies[1]+(tail1,)
            self.assertGreater(prefix.score(prefix.Wrapped(base,0,2),x),prefix.score(prefix.Wrapped(base,0,2),y))
            self.assertLess(prefix.score(prefix.Wrapped(base,1,2),x),prefix.score(prefix.Wrapped(base,1,2),y))
            reversals += 1
        self.assertEqual((cases,reversals),(254,9))
        COVERAGE.update(environment_history_checks=cases,actual_policy_reversals=reversals)

    def test_nonrectangular_and_rectangular_repair(self):
        family = ((F(1,2),F(0),F(0),F(1,2)),(F(0),F(1,2),F(1,2),F(0)))
        payoff,constant = (F(1),F(0),F(1),F(0)),(F(1,4),)*4
        partition = ((0,1),(2,3))
        rectangles = tuple(tuple(F(1,2) if i in (a,b) else F(0) for i in range(4))
                           for a,b in product((0,1),(2,3)))
        conditionals = 0
        for priors in (family,rectangles):
            for weights in priors:
                for branch in partition:
                    self.assertEqual(measure.conditional(weights,branch),oracle.conditional(weights,branch))
                    conditionals += 1
        ex_ante = oracle.lower(family,payoff)
        branch_values = tuple(min(oracle.inner(oracle.conditional(w,event),tuple(payoff[i] for i in event))
                                  for w in family) for event in partition)
        recursive = oracle.inner((F(1,2),F(1,2)),branch_values)
        self.assertEqual((ex_ante,recursive),(F(1,2),F(0)))
        self.assertEqual(measure.lower(family,payoff),ex_ante)
        self.assertEqual(measure.recursive_lower(family,payoff,partition),recursive)
        self.assertGreater(measure.lower(family,payoff),measure.lower(family,constant))
        self.assertLess(measure.recursive_lower(family,payoff,partition),
                        measure.recursive_lower(family,constant,partition))
        self.assertEqual(measure.lower(rectangles,payoff),0)
        self.assertEqual(measure.recursive_lower(rectangles,payoff,partition),0)
        self.assertEqual(measure.recursive_lower(rectangles,constant,partition),F(1,4))
        self.assertEqual(conditionals,12)
        COVERAGE.update(conditional_probability_checks=conditionals,nonrectangular_reversal_controls=1,
                        rectangular_repair_controls=1)

    def test_common_bound_is_needed(self):
        cases = 0
        base = prefix.Book(2,(((),1),))
        for padding in (2,3,4,100):
            wrapped = prefix.Wrapped(base,0,padding)
            unbounded = (F(0),F(2**padding))
            self.assertEqual(oracle.inner((F(1,2),F(1,2**padding)),unbounded),1)
            with self.assertRaises(ValueError):
                prefix.score(wrapped,unbounded)
            cases += 1
        COVERAGE['common_bound_controls'] = cases


if __name__ == '__main__':
    result = unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
