"""Actual partial-context restrictions, joint fibers, targets and resource projections."""
from itertools import product
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v21 as oracle
import core_v21 as core
import images_v21 as images
COVERAGE={}


class ImageTests(unittest.TestCase):
    def test_all_context_fibers(self):
        counts={k:0 for k in ('context_models','selectors','budget_images','observation_checks',
            'target_cutoff_checks','threshold_witness_checks','coordinate_projections','selector_inclusions')}
        for n in range(4):
            histories=tuple((0,(i,)) for i in range(n));selected_sets=oracle.subsets(tuple(range(n)))
            for present in product((False,True),repeat=n):
                rows=(tuple((0,i,0) if present[i] else None for i in range(n)) or (None,),)
                machine=core.LegacyMachine((0,),rows)
                for m in range(3):
                    targets=oracle.subsets(tuple(range(m)))
                    for order in oracle.preorders(m):
                        for p in product((False,True),repeat=n):
                            for values in product((None,)+tuple(range(m)),repeat=n):
                                context=core.Context(n,m,p,tuple(v is not None for v in values),values,order)
                                attained={}
                                for selected in selected_sets:
                                    fibers=oracle.joint((0,),rows,histories,p,values,selected)
                                    expected_j=tuple(sorted({(cost,v) for _,cost,v in fibers}))
                                    joint=images.joint(context,histories,machine,selected)
                                    self.assertEqual(joint,expected_j)
                                    unrestricted=images.restrict(context,histories,machine,None,selected)
                                    self.assertEqual(unrestricted.admitted,tuple(p[h] and h in selected and present[h] for h in range(n)))
                                    self.assertEqual((unrestricted.defined,unrestricted.values,unrestricted.order),
                                                     (context.defined,context.values,context.order))
                                    full=oracle.image(fibers);attained[selected]=set(full)
                                    self.assertEqual(images.attained(unrestricted),full)
                                    for rho in product((0,1),repeat=m):
                                        expected=tuple(sorted({rho[v] for v in full}))
                                        self.assertEqual(images.projection(full,rho),expected)
                                        composed=core.Context(n,2,unrestricted.admitted,context.defined,
                                            tuple(None if v is None else rho[v] for v in values),((True,True),(True,True)))
                                        self.assertEqual(images.attained(composed),expected)
                                        counts['coordinate_projections']+=1
                                    earlier=set()
                                    for budget in range(3):
                                        restricted=images.restrict(context,histories,machine,budget,selected)
                                        admitted=tuple(p[h] and h in selected and present[h] and h<=budget for h in range(n))
                                        self.assertEqual(restricted.admitted,admitted)
                                        self.assertEqual((restricted.defined,restricted.values,restricted.order),
                                                         (context.defined,context.values,context.order))
                                        expected=oracle.image(fibers,budget)
                                        self.assertEqual(images.attained_at(joint,budget),expected)
                                        self.assertEqual(images.attained(restricted),expected)
                                        self.assertLessEqual(earlier,set(expected));self.assertLessEqual(set(expected),set(full))
                                        earlier=set(expected)
                                        for h in range(n):
                                            self.assertEqual(core.observe(restricted,h),oracle.observe(admitted,values,h))
                                            counts['observation_checks']+=1
                                        for target in targets:
                                            costs=tuple(cost for _,cost,v in fibers if v in target)
                                            cutoff=min(costs) if costs else None
                                            self.assertEqual(images.threshold(joint,target),cutoff)
                                            self.assertEqual(images.capability(joint,budget,target),cutoff is not None and cutoff<=budget)
                                            counts['target_cutoff_checks']+=1
                                        counts['budget_images']+=1
                                    self.assertEqual(earlier,set(full))
                                    for target in targets:
                                        candidates=tuple((cost,h) for h,cost,v in fibers if v in target)
                                        witness=images.threshold_witness(context,histories,machine,selected,target)
                                        if candidates:
                                            self.assertIn(witness,candidates)
                                            self.assertEqual(witness[0],min(c for c,h in candidates))
                                        else:self.assertIsNone(witness)
                                        counts['threshold_witness_checks']+=1
                                    counts['selectors']+=1
                                for selected in selected_sets:
                                    for smaller in oracle.subsets(selected):
                                        self.assertLessEqual(attained[smaller],attained[selected])
                                        counts['selector_inclusions']+=1
                                counts['context_models']+=1
        self.assertEqual((counts['context_models'],counts['selectors'],counts['budget_images']),(8210,62654,187962))
        COVERAGE.update(counts)


if __name__=='__main__':
    import json
    r=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not r.result.wasSuccessful())
