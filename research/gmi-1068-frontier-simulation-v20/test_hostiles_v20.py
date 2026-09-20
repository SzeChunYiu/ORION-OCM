"""Strict malformed-data rejection, including unused values and hidden suffixes."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unittest
import core_v20 as core
import frontier_v20 as frontier
import maps_v20 as maps
import simulation_v20 as simulation
import bridge_v20 as bridge

COVERAGE={'malformed_api_rejections':0,'relation_scope_controls':0}
R=((True,True),(False,True))

class HostileTests(unittest.TestCase):
    def test_malformed_and_scope(self):
        machine=simulation.Machine(R,((None,),(0,)),1)
        context=core.Context(2,2,(True,False),(True,True),(0,1),R)
        old=core.LegacyMachine((0,),(((0,1,0),),))
        cases=[]
        for bad in (None,[],((1,True),(False,True)),((True,True),(False,False)),
                    ((True,),),((True,False,True),(True,True,False),(False,True,True))):
            for f in (frontier.maximal,frontier.representatives,frontier.downset):
                cases.append(lambda f=f,bad=bad:f(bad,(0,1)))
            cases.append(lambda bad=bad:maps.guarded(bad,R,(0,1)))
            cases.append(lambda bad=bad:simulation.Machine(bad,((None,),(0,)),1))
        for selected in ([],(True,),(0.0,),(2,),(-1,),(0,0),None):
            for f in (frontier.maximal,frontier.representatives,frontier.downset):
                cases.append(lambda f=f,s=selected:f(R,s))
            cases.append(lambda s=selected:frontier.cofinal(R,(0,1),s))
            cases.append(lambda s=selected:frontier.attained(context,s))
            cases.append(lambda s=selected:simulation.prune(machine,s))
            cases.append(lambda s=selected:simulation.endpoints(machine,s,()))
        for values in ([],(0,True),(0,1.0),(None,2),(0,),None):
            cases.append(lambda v=values:maps.guarded(R,R,v))
            if values!=(0,):cases.append(lambda v=values:maps.image(v,(),2))
            cases.append(lambda v=values:maps.postcompose(context,R,v))
        for actions in (True,1.0,-1,None):cases.append(lambda a=actions:simulation.Machine(R,((None,),(0,)),a))
        for rows in ([],((0,),),((0,),[0]),((0,),(True,)),((0,),(1.0,)),((None,),(2,))):
            cases.append(lambda rows=rows:simulation.Machine(R,rows,1))
        for word in ([],(0,True),(0,1.0),(0,1),(0,-1),None):
            cases.append(lambda w=word:simulation.run(machine,0,w))
            cases.append(lambda w=word:simulation.endpoints(machine,(),w))
        for state in (True,0.0,-1,2,None):cases.append(lambda s=state:simulation.run(machine,s,()))
        for bad in (None,object(),{'base':R}):
            cases.extend((lambda b=bad:simulation.run(b,0,()),lambda b=bad:simulation.refine(b),
                          lambda b=bad:simulation.is_simulation(b,R),lambda b=bad:simulation.prune(b,()),
                          lambda b=bad:simulation.endpoints(b,(),()),lambda b=bad:frontier.attained(b,()),
                          lambda b=bad:maps.postcompose(b,R,(0,1)),lambda b=bad:bridge.from_v8(b,R,1)))
        for candidate in ([],((1,False),(False,True)),((True,),),None):
            cases.append(lambda c=candidate:simulation.is_simulation(machine,c))
        for bad in (True,1.0,-1,None):
            cases.append(lambda b=bad:bridge.from_v8(old,R,b))
            cases.append(lambda b=bad:maps.image((),(),b))
        cases.extend((lambda:bridge.from_v8(old,((True,),),1),
                      lambda:bridge.valued_endpoints(machine,core.Context(0,0,(),(),(),()),(),()),
                      lambda:maps.image((0,1),(),True)))
        for index,call in enumerate(cases):
            with self.subTest(index=index):
                with self.assertRaises(ValueError):call()
        COVERAGE['malformed_api_rejections']=len(cases)
        # Arbitrary candidate relations are allowed: simulation need not be reflexive.
        empty=((False,False),(False,False))
        self.assertTrue(simulation.is_simulation(machine,empty))
        self.assertFalse(simulation.is_simulation(machine,((True,True),(True,True))))
        self.assertEqual(simulation.endpoints(machine,(),()),())
        self.assertIsNone(simulation.run(machine,0,(0,0)))
        self.assertEqual(maps.postcompose(context,(),(None,None)).defined,(False,False))
        COVERAGE['relation_scope_controls']=5

if __name__=='__main__':unittest.main()
