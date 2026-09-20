"""Actual history controls and explicit boundaries of positive permission incidence."""
from pathlib import Path
import importlib.util
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v22 as o
import core_v22 as core
import execution_v22 as e
import contexts_v22 as c
import families_v22 as f
COVERAGE={}


class ControlTests(unittest.TestCase):
    def test_execution_and_history(self):
        base=core.LegacyMachine((None,1),(((7,2,1),(7,2,1)),((7,2,0),None)))
        req=(((0,),(1,)),((1,),None));spec=core.PermissionMachine(base,2,req)
        checks=0
        from itertools import product
        for n in range(5):
            for word in product(range(2),repeat=n):
                for enabled in o.subsets(range(2)):
                    trace,result=o.execute(base.observations,base.transitions,req,0,word,enabled)
                    self.assertEqual(core.legacy.run(e.gate(spec,enabled),0,word),trace)
                    checks+=1
        self.assertEqual(e.support(spec,0,(0,0,0)),(1,(0,1)))
        self.assertEqual(e.support(spec,0,(1,)),(1,(1,)))
        loop=core.PermissionMachine(core.LegacyMachine((0,),(((9,3,0),),)),1,(((0,),),))
        histories=((0,()),(0,(0,)),(0,(0,0)))
        context=core.Context(3,2,(True,True,True),(True,True,True),(0,0,1),((True,False),(False,True)))
        records=c.target_witnesses(loop,context,histories,(0,1,2),(1,))
        self.assertEqual(records,((2,(0,)),))
        self.assertEqual(c.attained(c.restricted_context(loop,(0,),context,histories,(0,1,2))),(0,1))
        self.assertEqual(c.target_witnesses(loop,context,histories,(0,),(1,)),())
        # Fixed affordability P selects only first two histories (cost <=3).
        fixed=core.Context(3,2,(True,True,False),context.defined,context.values,context.order)
        self.assertEqual(c.target_witnesses(loop,fixed,histories,(0,1,2),(1,)),())
        self.assertEqual(core.legacy.run(e.gate(loop,(0,)),0,(0,),budget=3),core.legacy.run(loop.base,0,(0,),budget=3))
        COVERAGE.update(branch_trace_checks=checks,history_roster_entries=len(histories))

    def test_family_boundaries(self):
        and_family=((0,(0,1)),);or_family=((0,(0,)),(1,(1,)))
        self.assertEqual(f.minimal_additions(and_family,(),(0,1),2),((0,1),))
        self.assertEqual(f.minimal_additions(or_family,(),(0,1),2),((0,),(1,)))
        self.assertEqual(f.minimal_blockers(or_family,(0,1),2),((0,1),))
        unequal=((0,(0,)),(1,(1,2)))
        candidates=f.minimal_additions(unequal,(),(0,1,2),3)
        self.assertEqual(candidates,((0,),(1,2)))
        self.assertEqual(min(candidates,key=len),(0,))
        self.assertEqual(min(candidates,key=lambda d:sum((9,1,1)[i] for i in d)),(1,2))
        self.assertIsNone(f.blocker_certificate(or_family,(0,1),(0,),2))
        self.assertIsNone(f.blocker_certificate(or_family,(0,1),(),2))
        self.assertEqual(f.blocker_certificate((),(0,1),(),2),())
        self.assertEqual(f.minimal_blockers(((0,()),),(0,1),2),())
        self.assertEqual(f.minimal_additions(((0,(1,)),),(),(0,),2),())
        duplicate=((9,(0,)),(2,(0,)),(5,(0,1)))
        self.assertEqual(f.minimal_supports(duplicate,2),(((0,),(2,9)),))
        self.assertEqual(f.survivors(duplicate,(0,1),2),(2,5,9))
        self.assertEqual(f.blocker_certificate(duplicate,(0,1),(0,),2),((0,2),))
        self.assertEqual(f.minimal_additions(or_family,(0,),(0,1),2),((),))
        # Restricted feasible additions change the optimization domain.
        permitted=((0,1),)
        restricted=tuple(d for d in permitted if o.survivors(((0,(0,)),),d))
        self.assertEqual(restricted,((0,1),))
        self.assertNotEqual(restricted,f.minimal_additions(((0,(0,)),),(),(0,1),2))
        # These explicitly changed contexts violate fixed positive incidence.
        negative={};overhead={};model_count=0
        for enabled in o.subsets(range(2)):
            neg=core.Context(1,1,(0 in enabled and 1 not in enabled,),(True,),(0,),((True,),))
            charged=core.Context(1,1,(2+len(enabled)<=2,),(True,),(0,),((True,),))
            negative[enabled]=c.attained(neg);overhead[enabled]=c.attained(charged)
            model_count+=2
        self.assertEqual(negative[(0,)],(0,));self.assertEqual(negative[(0,1)],())
        self.assertEqual(overhead[()],(0,));self.assertEqual(overhead[(0,)],())
        COVERAGE['nonmonotone_context_models']=model_count
        # Same baseline image cannot determine which distinct permission is missing.
        self.assertEqual(o.survivors(((0,(0,)),),()),o.survivors(((0,(1,)),),()))
        self.assertNotEqual(f.minimal_additions(((0,(0,)),),(),(0,1),2),f.minimal_additions(((0,(1,)),),(),(0,1),2))
        COVERAGE['family_boundary_replays']=COVERAGE.get('family_boundary_replays',0)+1

    def test_original_relief(self):
        path=Path(__file__).resolve().parents[1]/'gmi-1068-r3-contextual-attainability-v1/check_r3.py'
        spec=importlib.util.spec_from_file_location('_v22_actual_original_r3',path)
        old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
        self.assertEqual(old.VALUES,{'h0':(0,0),'h1':(1,2),'h2':(2,5),'h3':(2,3),'h4':(2,3),'hU':None})
        expected=tuple(sorted(h for h in old.FULL-old.BUDGET if old.VALUES[h] is not None and old.VALUES[h][0]>=old.TARGET_PERFORMANCE))
        self.assertEqual(old.one_step_relief_witnesses(old.BUDGET,old.FULL,old.TARGET_PERFORMANCE),expected)
        self.assertEqual(expected,('h2','h3','h4'))
        # Generic history admission only: no assertion that this is graph edge gating.
        missing=tuple(sorted(old.FULL-old.BUDGET));ids={h:i for i,h in enumerate(sorted(old.FULL))}
        records=tuple((ids[h],(missing.index(h),)) for h in expected)
        additions=f.minimal_additions(records,(),tuple(range(len(missing))),len(missing))
        self.assertEqual(tuple(missing[d[0]] for d in additions),expected)
        self.assertEqual(len({old.VALUES[h] for h in expected}),2)
        self.assertEqual(len(records),3)
        COVERAGE.update(original_fixture_replays=1,original_history_witnesses=len(records))


if __name__=='__main__':
    import json
    r=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not r.result.wasSuccessful())
