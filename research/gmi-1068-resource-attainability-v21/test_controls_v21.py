"""Concrete failed abstractions and their declared resource/history repairs."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import core_v21 as core
import execution_v21 as execution
import images_v21 as images
import resources_v21 as resources
COVERAGE={}
ONE=((True,),)


class ControlTests(unittest.TestCase):
    def test_resource_and_information_revivals(self):
        count=0
        machine=core.LegacyMachine((0,),(((0,1,0),),))
        self.assertEqual(execution.budget_endpoint(machine,0,(0,),1),(0,0))
        self.assertIsNone(execution.budget_endpoint(machine,0,(0,0),1))
        self.assertIsNone(execution.budget_endpoint(machine,0,(0,),0))
        self.assertEqual(execution.budget_endpoint(machine,0,(0,0),2),(0,0));count+=1
        prefixes,ok=resources.prefix_fold('signed',(2,-2),0,1)
        self.assertFalse(ok);self.assertLessEqual(prefixes[-1],1)
        self.assertEqual(prefixes,(0,2,0));self.assertEqual(max(prefixes),2)
        self.assertTrue(resources.prefix_fold('signed',(2,-2),0,2)[1]);count+=1
        self.assertTrue(resources.prefix_fold('peak',(5,5),0,5)[1])
        self.assertFalse(resources.prefix_fold('nat',(5,5),0,5)[1]);count+=1
        j=((0,0),(1,1));opposite=((0,1),(1,0))
        self.assertEqual(images.attained_at(j,1),images.attained_at(opposite,1))
        self.assertEqual({c for c,v in j},{c for c,v in opposite})
        self.assertEqual((images.threshold(j,(1,)),images.threshold(opposite,(1,))),(1,0));count+=1
        self.assertEqual((images.threshold(j,(0,)),images.threshold(j,(1,))),(0,1))
        self.assertEqual(images.projection((0,1),(0,0)),(0,))
        self.assertEqual(images.projection((0,1),(0,1)),(0,1));count+=1
        context=core.Context(3,1,(True,)*3,(False,False,True),(None,None,0),ONE)
        histories=((0,()),(0,(0,)),(0,(0,0)))
        self.assertEqual(tuple(execution.weighted_run(machine,*h)[0] for h in histories),(0,0,0))
        self.assertEqual(images.threshold_witness(context,histories,machine,(0,1,2),(0,)),(2,2))
        self.assertIsNone(images.threshold_witness(context,histories,machine,(0,),(0,)))
        self.assertEqual(images.attained(images.restrict(context,histories,machine,2,(0,1,2))),(0,));count+=1
        costs=((1,0),(0,1))
        self.assertFalse(resources.le('vector',costs[0],costs[1]))
        self.assertFalse(resources.le('vector',costs[1],costs[0]))
        capable=lambda b:any(resources.le('vector',c,b) for c in costs)
        self.assertTrue(capable((1,0)) and capable((0,1)))
        self.assertFalse(capable((0,0)));count+=1
        # Fixed endpoint, changing evaluator breaks set nesting; fixed evaluator repairs it.
        order=((True,True),(False,True));histories=((0,()),)
        low=core.Context(1,2,(True,),(True,),(0,),order)
        high=core.Context(1,2,(True,),(True,),(1,),order)
        a=set(images.attained(images.restrict(low,histories,machine,0,(0,))))
        b=set(images.attained(images.restrict(high,histories,machine,1,(0,))))
        self.assertFalse(a<=b)
        fixed=set(images.attained(images.restrict(low,histories,machine,1,(0,))))
        self.assertLessEqual(a,fixed);count+=1
        self.assertFalse(set(images.attained(low))<=set(images.attained(core.Context(1,2,(False,),(True,),(0,),order))))
        count+=1
        self.assertEqual(resources.prefix_fold('nat',(),2,1),((2,),False))
        self.assertEqual(resources.prefix_fold('signed',(),0,-1),((0,),False));count+=1
        COVERAGE['scope_and_revival_controls']=count
        self.assertEqual(count,10)

    def test_distinct_failure_layers(self):
        machine=core.LegacyMachine((None,),((None,),))
        self.assertEqual(execution.weighted_run(machine,0,()),(0,0))
        self.assertEqual(core.legacy.run(machine,0,()),(('OBS',None),))
        self.assertIsNone(execution.weighted_run(machine,0,(0,)))
        self.assertEqual(core.legacy.run(machine,0,(0,)),(('OBS',None),('ILLEGAL',)))
        histories=((0,()),(0,(0,)))
        context=core.Context(2,1,(True,True),(False,True),(None,0),ONE)
        restricted=images.restrict(context,histories,machine,0,(0,1))
        self.assertEqual(core.observe(restricted,0),('UNDEFINED',None))
        self.assertEqual(core.observe(restricted,1),('ILLEGAL',None))
        self.assertEqual(restricted.values,(None,0));self.assertEqual(images.attained(restricted),())
        COVERAGE['failure_layer_controls']=4


if __name__=='__main__':
    import json
    r=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not r.result.wasSuccessful())
