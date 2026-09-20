"""Scope falsifiers and actual continuation revival, independently observed."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unittest
from itertools import product
import oracle_v20 as oracle
import frontier_v20 as frontier
import maps_v20 as maps
import simulation_v20 as simulation

COVERAGE={'revival_controls':0,'scope_controls':0,'guarded_composition_cases':0}
CHAIN=((True,True),(False,True))
ALL=((True,True),(True,True))

class ControlTests(unittest.TestCase):
    def test_revival_and_scope(self):
        count=0
        for base,rows,states in ((CHAIN,((1,),(None,)),(0,1)),
                                (CHAIN,((1,),(0,)),(0,1)),
                                (ALL,((0,),(None,)),(1,0))):
            machine=simulation.Machine(base,rows,1)
            raw=frontier.representatives(base,states)
            repaired=simulation.prune(machine,states)
            original=tuple(sorted({oracle.run(rows,x,(0,)) for x in states
                                  if oracle.run(rows,x,(0,)) is not None}))
            lost=simulation.endpoints(machine,raw,(0,))
            revived=simulation.endpoints(machine,repaired,(0,))
            self.assertNotEqual(oracle.downset(base,original),oracle.downset(base,lost))
            self.assertEqual(oracle.downset(base,original),oracle.downset(base,revived))
            self.assertFalse(maps.guarded(base,base,tuple(row[0] for row in rows)))
            count+=1
        COVERAGE['revival_controls']=count
        controls=0
        self.assertEqual(frontier.maximal(ALL,(1,0)),(1,0))
        self.assertEqual(frontier.representatives(ALL,(1,0)),(1,))
        self.assertEqual(frontier.representatives(ALL,(0,1)),(0,));controls+=1
        equality=((True,False),(False,True))
        self.assertFalse(frontier.cofinal(equality,(0,1),(1,)))
        self.assertFalse(frontier.cofinal(CHAIN,(0,),(1,)))
        self.assertTrue(frontier.cofinal((),(),()));controls+=1
        # Lawful pruning preserves upward goals, but loses the singleton {0}.
        self.assertTrue(maps.guarded(CHAIN,CHAIN,(0,1)))
        self.assertIn(0,(0,1));self.assertNotIn(0,frontier.representatives(CHAIN,(0,1)));controls+=1
        # Same existential goal via different action labels is insufficient.
        base=((True,True,True),(True,True,True),(False,False,True))
        machine=simulation.Machine(base,((2,None),(None,2),(None,None)),2)
        self.assertEqual(simulation.run(machine,0,(0,)),simulation.run(machine,1,(1,)))
        self.assertFalse(simulation.greatest(machine)[0][1]);controls+=1
        # p-a->r(b,c); q-a->{b-only,c-only}: all traces equal, no matching successor.
        rows=(((2,),(),()),((3,4),(),()),((),(5,),(5,)),
              ((),(5,),()),((),(),(5,)),((),(),()))
        expected={() ,(0,),(0,1),(0,2)}
        self.assertEqual(oracle.nondeterministic_language(rows,0,6),expected)
        self.assertEqual(oracle.nondeterministic_language(rows,1,6),expected)
        self.assertTrue(all(any(rows[2][a] and not rows[t][a] for a in (1,2)) for t in (3,4)))
        controls+=1
        for n in range(4):
            for base in oracle.preorders(n):
                machine=simulation.Machine(base,tuple(() for _ in range(n)),0)
                self.assertEqual(simulation.refine(machine),(base,1,0))
                self.assertEqual(simulation.endpoints(machine,tuple(range(n)),()),tuple(range(n)))
                controls+=1
        COVERAGE['scope_controls']=controls
        self.assertEqual((count,controls),(3,40))

    def test_guarded_composition(self):
        count=0
        for source,middle,target in product(oracle.preorders(2),repeat=3):
            for f,g in product(tuple(oracle.assignments(2,2)),repeat=2):
                if not (oracle.guarded(source,middle,f) and oracle.guarded(middle,target,g)):continue
                composition=tuple(None if v is None else g[v] for v in f)
                self.assertTrue(maps.guarded(source,target,composition))
                for selected in oracle.subsets((0,1)):
                    self.assertEqual(maps.image(composition,selected,2),oracle.image(g,oracle.image(f,selected)))
                count+=1
        COVERAGE['guarded_composition_cases']=count
        self.assertGreater(count,0)

if __name__=='__main__':unittest.main()
