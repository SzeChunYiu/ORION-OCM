"""Guarded preservation versus every cofinal subset; actual partial postcomposition."""
from itertools import product
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v20 as oracle
import maps_v20 as core
import frontier_v20 as frontier
from core_v20 import Context,observe
COVERAGE={}


class MapTests(unittest.TestCase):
    def test_all_partial_maps_and_cofinal_pairs(self):
        maps=candidates=cofinal_checks=guarded_count=0
        for n,m in product(range(4),repeat=2):
            subsets=oracle.subsets(tuple(range(n)))
            for source,target in product(oracle.preorders(n),oracle.preorders(m)):
                pairs=tuple((a,c,oracle.cofinal(source,a,c)) for a in subsets for c in oracle.subsets(a))
                for mapping in oracle.assignments(n,m):
                    preserves=True
                    for a,c,is_cofinal in pairs:
                        candidates+=1
                        if not is_cofinal:continue
                        whole,retained=core.image(mapping,a,m),core.image(mapping,c,m)
                        self.assertEqual(whole,oracle.image(mapping,a))
                        self.assertEqual(retained,oracle.image(mapping,c))
                        equality=frontier.downset(target,whole)==frontier.downset(target,retained)
                        self.assertEqual(equality,oracle.downset(target,whole)==oracle.downset(target,retained))
                        preserves=preserves and equality
                        cofinal_checks+=1
                    expected=oracle.guarded(source,target,mapping)
                    self.assertEqual(core.guarded(source,target,mapping),expected)
                    self.assertEqual(expected,preserves)
                    guarded_count+=int(expected);maps+=1
        self.assertEqual((maps,candidates),(59403,1563467))
        COVERAGE.update(partial_maps=maps,map_subset_candidates=candidates,
                        cofinal_image_equations=cofinal_checks,guarded_maps=guarded_count)

    def test_actual_partial_postcomposition(self):
        contexts=selectors=observations=0
        for n,s,t in product(range(3),repeat=3):
            for source,target in product(oracle.preorders(s),oracle.preorders(t)):
                for p in product((False,True),repeat=n):
                    for values in oracle.assignments(n,s):
                        original=Context(n,s,p,tuple(v is not None for v in values),values,source)
                        for mapping in oracle.assignments(s,t):
                            result=core.postcompose(original,target,mapping)
                            expected=tuple(None if v is None else mapping[v] for v in values)
                            self.assertEqual(result.admitted,p)
                            self.assertEqual(result.defined,tuple(v is not None for v in expected))
                            self.assertEqual(result.values,expected)
                            for h in range(n):
                                self.assertEqual(observe(result,h),oracle.observation(p,expected,h));observations+=1
                            for histories in oracle.subsets(tuple(range(n))):
                                self.assertEqual(frontier.attained(result,histories),
                                    oracle.image(mapping,oracle.attained(p,values,histories)))
                                selectors+=1
                            contexts+=1
        self.assertEqual((contexts,selectors,observations),(7409,26969,13392))
        COVERAGE.update(postcomposition_contexts=contexts,postcomposition_selectors=selectors,
                        postcomposition_observations=observations)


if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
