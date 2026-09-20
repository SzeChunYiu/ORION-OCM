"""Independent cycles and all postfixed subsets, never a horizon-only oracle."""
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import oracle_v17 as oracle
import viability_v17 as core
from specializations_v17 import decoded

COVERAGE={}


class ViabilityTests(unittest.TestCase):
    def test_all_relations_and_safe_sets(self):
        cases=memberships=candidates=trace_steps=contexts=0
        for relation,safe in oracle.viability_cases():
            expected=oracle.cycle_survivors(relation,safe)
            actual=core.viability(relation,safe)
            self.assertEqual(actual,expected)
            union=set()
            for candidate in oracle.safe_candidates(safe):
                if oracle.postfixed(relation,safe,candidate):
                    self.assertLessEqual(candidate,actual)
                    union.update(candidate)
                candidates+=1
            self.assertEqual(actual,frozenset(union))
            self.assertTrue(oracle.postfixed(relation,safe,actual))
            self.assertEqual(actual,frozenset(i for i in safe if any(relation[i][j] for j in actual)))
            trace=core.survivor_trace(relation,safe)
            self.assertEqual(trace[0],safe)
            self.assertEqual(trace[-1],actual)
            self.assertLessEqual(len(trace),len(relation)+1)
            for previous,current in zip(trace,trace[1:]):
                self.assertLess(current,previous)
                self.assertEqual(current,frozenset(i for i in safe if any(relation[i][j] for j in previous)))
                trace_steps+=1
            context=core.viability_context((True,)*len(relation),tuple(range(len(relation))),relation,safe)
            for i in range(len(relation)):
                self.assertEqual(i in actual,i in expected)
                self.assertEqual(decoded(context,i),('VALUE',i in expected))
                memberships+=1
            cases+=1
            contexts+=1
        self.assertEqual((cases,memberships,candidates),(4165,12420,13975))
        COVERAGE.update(viability_cases=cases,state_memberships=memberships,safe_subset_candidates=candidates,
                        strict_deletion_steps=trace_steps,actual_viability_contexts=contexts)

    def test_deadend_adversarial_and_type_boundaries(self):
        dead=((False,),)
        self.assertEqual(core.viability(dead,frozenset((0,))),frozenset())
        relation=((True,True),(False,False))
        safe=frozenset((0,1))
        self.assertEqual(core.viability(relation,safe),frozenset((0,)))
        # The branch to the deadend prevents universal infinite survival.
        universal=safe
        while True:
            new=frozenset(i for i in safe if any(relation[i]) and all(not edge or j in universal
                                                                   for j,edge in enumerate(relation[i])))
            if new==universal:break
            universal=new
        self.assertEqual(universal,frozenset())
        self.assertEqual(core.viability(((False,True),(False,True)),frozenset((0,))),frozenset())
        ctx=core.viability_context((False,True,True),(0,None,0),((True,),),frozenset((0,)))
        self.assertEqual(tuple(decoded(ctx,i) for i in range(3)),
                         (('ILLEGAL',None),('UNDEFINED',None),('VALUE',True)))
        self.assertTrue(ctx.context.defined[0])
        invalid=[]
        for relation in ([],((1,),),((0.0,),),((True,False),),(('yes',),),None):
            invalid.append(lambda r=relation:core.viability(r,frozenset()))
        for safe in ({0},(0,),frozenset((True,)),frozenset((0.0,)),frozenset((-1,)),frozenset((1,)),None):
            invalid.append(lambda s=safe:core.viability(((True,),),s))
        invalid.extend((lambda:core.viability_context((True,),(True,),((True,),),frozenset((0,))),
                        lambda:core.viability_context((True,),(1,),((True,),),frozenset((0,)))))
        for i,call in enumerate(invalid):
            with self.subTest(case=i),self.assertRaises(ValueError):call()
        COVERAGE.update(deadend_controls=1,existential_adversarial_controls=1,unsafe_path_controls=1,
                        viability_observation_controls=1,viability_malformed_rejections=len(invalid))


if __name__=='__main__':
    program=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
