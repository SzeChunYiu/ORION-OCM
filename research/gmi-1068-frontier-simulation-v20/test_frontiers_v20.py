"""Minimum cofinal covers and actual admitted/evaluated context images."""
from itertools import permutations
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v20 as oracle
import frontier_v20 as core
from core_v20 import Context,observe
COVERAGE={}


class FrontierTests(unittest.TestCase):
    def test_all_small_frontier_minima(self):
        count=dict(frontier_preorders=0,attained_subsets=0,cofinal_subset_candidates=0,
                   minimum_cover_checks=0,enumeration_choices=0)
        for n in range(4):
            for relation in oracle.preorders(n):
                count['frontier_preorders']+=1
                for a in oracle.subsets(tuple(range(n))):
                    covers=oracle.minimum_covers(relation,a)
                    maximal=set().union(*map(set,covers))
                    self.assertEqual(set(core.maximal(relation,a)),maximal)
                    reps=core.representatives(relation,a)
                    self.assertIn(reps,covers)
                    self.assertEqual(core.downset(relation,a),oracle.downset(relation,a))
                    self.assertEqual(core.downset(relation,reps),oracle.downset(relation,a))
                    for c in oracle.subsets(a):
                        expected=oracle.cofinal(relation,a,c)
                        self.assertEqual(core.cofinal(relation,a,c),expected)
                        if expected:
                            self.assertLessEqual(len(reps),len(c));count['minimum_cover_checks']+=1
                        count['cofinal_subset_candidates']+=1
                    for enumeration in permutations(a):
                        selected=core.representatives(relation,enumeration)
                        self.assertIn(set(selected),list(map(set,covers)))
                        for representative in selected:
                            equivalent=[x for x in enumeration if relation[x][representative] and relation[representative][x]]
                            self.assertEqual(representative,equivalent[0])
                        count['enumeration_choices']+=1
                    count['attained_subsets']+=1
        self.assertEqual((count['frontier_preorders'],count['attained_subsets'],count['cofinal_subset_candidates']),(35,251,823))
        COVERAGE.update(count)

    def test_actual_context_images(self):
        contexts=selectors=observations=0
        for n,m,relation,p,values in oracle.contexts():
            context=Context(n,m,p,tuple(v is not None for v in values),values,relation)
            for h in range(n):
                self.assertEqual(observe(context,h),oracle.observation(p,values,h));observations+=1
            for histories in oracle.subsets(tuple(range(n))):
                expected=oracle.attained(p,values,histories)
                actual=core.attained(context,histories)
                self.assertEqual(actual,expected)
                reps=core.representatives(relation,actual)
                self.assertIn(reps,oracle.minimum_covers(relation,expected))
                selectors+=1
            contexts+=1
        self.assertEqual((contexts,selectors),(18101,134911))
        COVERAGE.update(actual_contexts=contexts,context_selectors=selectors,ambient_observations=observations)


if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
