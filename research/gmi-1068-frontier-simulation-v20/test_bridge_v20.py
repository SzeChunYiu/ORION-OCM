"""Actual V8 residual-resource and V15 partial-evaluator integration."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unittest
from itertools import product
import core_v20 as core
import bridge_v20 as bridge
import simulation_v20 as simulation
import frontier_v20 as frontier
import oracle_v20 as oracle

COVERAGE={'budget_models':0,'budget_word_checks':0,'budget_revival_controls':0,
          'endpoint_contexts':0,'endpoint_context_rejections':0,'trace_scope_controls':0}

class BridgeTests(unittest.TestCase):
    def test_actual_budget_lift(self):
        models=words=0
        for cost,budget in product(range(3),repeat=2):
            old=core.LegacyMachine((0,),(((7,cost,0),),))
            n=budget+1;base=tuple(tuple(True for _ in range(n)) for _ in range(n))
            machine=bridge.from_v8(old,base,budget)
            expected=tuple((b-cost if b>=cost else None,) for b in range(n))
            self.assertEqual(machine.transitions,expected)
            for b in range(n):
                for length in range(5):
                    word=(0,)*length
                    dest=b-length*cost if b>=length*cost else None
                    self.assertEqual(simulation.run(machine,b,word),dest)
                    self.assertEqual(oracle.run(expected,b,word),dest);words+=1
            models+=1
        old=core.LegacyMachine((0,),(((7,1,0),),))
        machine=bridge.from_v8(old,((True,True),(True,True)),1)
        raw=frontier.representatives(machine.base,(0,1));repaired=simulation.prune(machine,(0,1))
        self.assertEqual(raw,(0,));self.assertEqual(repaired,(1,))
        self.assertEqual(simulation.endpoints(machine,raw,(0,)),())
        self.assertEqual(simulation.endpoints(machine,repaired,(0,)),(0,))
        COVERAGE.update(budget_models=models,budget_word_checks=words,budget_revival_controls=1)
        self.assertEqual((models,words),(9,90))
        # Endpoint-only projection may identify machines with different visible edges.
        another=core.LegacyMachine((0,),(((99,1,0),),))
        self.assertEqual(bridge.from_v8(another,machine.base,1),machine)
        self.assertNotEqual(core.legacy.run(old,0,(0,),budget=1),core.legacy.run(another,0,(0,),budget=1))
        COVERAGE['trace_scope_controls']=1

    def test_actual_endpoint_context(self):
        accepted=rejected=0
        base=((True,True),(False,True))
        machine=simulation.Machine(base,((0,),(1,)),1)
        for order in oracle.preorders(2):
            for p in product((False,True),repeat=2):
                for values in oracle.assignments(2,2):
                    context=core.Context(2,2,p,tuple(x is not None for x in values),values,order)
                    active=tuple(values[x] if p[x] else None for x in range(2))
                    if oracle.guarded(base,order,active):
                        for states in oracle.subsets((0,1)):
                            self.assertEqual(bridge.valued_endpoints(machine,context,states,(0,)),oracle.image(active,states))
                        accepted+=1
                    else:
                        with self.assertRaises(ValueError):bridge.valued_endpoints(machine,context,(0,1),(0,))
                        rejected+=1
        # Two independent missing premises: undefined upper state and reversed value.
        for values in ((0,None),(1,0)):
            context=core.Context(2,2,(True,True),tuple(v is not None for v in values),values,base)
            with self.assertRaises(ValueError):bridge.valued_endpoints(machine,context,(0,1),())
            rejected+=1
        COVERAGE.update(endpoint_contexts=accepted,endpoint_context_rejections=rejected)
        self.assertEqual(accepted+rejected,146)

if __name__=='__main__':unittest.main()
