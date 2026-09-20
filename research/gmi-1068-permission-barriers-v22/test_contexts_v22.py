"""All declared tiny actual partial Contexts, preserving raw history IDs."""
from itertools import product
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v22 as o
import core_v22 as core
import contexts_v22 as c
import families_v22 as f
COVERAGE={}


class ContextTests(unittest.TestCase):
    def test_exhaustive(self):
        counts=dict(context_instances=0,selectors=0,enabled_images=0,target_incidence=0,
                    observation_checks=0,relative_analyses=0,witness_ids=0,nested_images=0)
        for n in range(3):
            histories=tuple((0,(i,)) for i in range(n))
            machines=o.machines(1,n,2) if n else [(((None,),),((None,),))]
            for rows,requirements in machines:
                spec=core.PermissionMachine(core.LegacyMachine((0,),rows),2,requirements)
                for m in range(3):
                    order=tuple(tuple(i==j for j in range(m)) for i in range(m))
                    for p in product((False,True),repeat=n):
                        for values in product((None,)+tuple(range(m)),repeat=n):
                            context=core.Context(n,m,p,tuple(v is not None for v in values),values,order)
                            counts['context_instances']+=1
                            for selected in o.subsets(range(n)):
                                counts['selectors']+=1
                                images={}
                                for enabled in o.subsets(range(2)):
                                    actual=c.restricted_context(spec,enabled,context,histories,selected)
                                    p2,tags,image=o.context_expected((0,),rows,requirements,histories,p,values,selected,enabled)
                                    self.assertEqual(actual.admitted,p2)
                                    self.assertEqual((actual.defined,actual.values,actual.order),(context.defined,values,order))
                                    self.assertEqual(c.attained(actual),image)
                                    images[enabled]=image
                                    for i in range(n):
                                        self.assertEqual(core.observe(actual,i),tags[i]);counts['observation_checks']+=1
                                    counts['enabled_images']+=1
                                    for target in o.subsets(range(m)):
                                        records=o.witnesses((0,),rows,requirements,histories,p,values,selected,target)
                                        self.assertEqual(c.target_witnesses(spec,context,histories,selected,target),records)
                                        self.assertEqual(bool(set(image)&set(target)),bool(o.survivors(records,enabled)))
                                        self.assertEqual(f.survivors(records,enabled,2),o.survivors(records,enabled))
                                        self.assertEqual(f.minimal_additions(records,enabled,(0,1),2),o.additions(records,enabled,(0,1)))
                                        self.assertEqual(f.minimal_blockers(records,enabled,2),o.blockers(records,enabled))
                                        counts['target_incidence']+=1;counts['relative_analyses']+=2
                                        counts['witness_ids']+=len(records)
                                for small in images:
                                    for large in images:
                                        if set(small)<=set(large):
                                            self.assertLessEqual(set(images[small]),set(images[large]))
                                            counts['nested_images']+=1
        self.assertEqual(tuple(counts[k] for k in ('context_instances','selectors','enabled_images','target_incidence')),(1463,5723,22892,73388))
        COVERAGE.update(counts)


if __name__=='__main__':
    import json
    r=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not r.result.wasSuccessful())
