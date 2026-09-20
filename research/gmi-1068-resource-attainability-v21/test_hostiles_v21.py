"""Invalid suffixes, unused data and strict empty-family validation."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import core_v21 as core
import execution_v21 as execution
import images_v21 as images
import resources_v21 as resources
COVERAGE={}


class HostileTests(unittest.TestCase):
    def test_execution_and_images(self):
        machine=core.LegacyMachine((0,),((None,),))
        context=core.Context(2,1,(False,False),(True,True),(0,0),((True,),))
        histories=((0,()),(0,(0,)))
        cases=[]
        for word in ([],None,(0,True),(0,0.0),(0,1),(0,-1)):
            cases.append(lambda w=word:execution.weighted_run(machine,0,w))
            cases.append(lambda w=word:execution.budget_endpoint(machine,0,w,0))
        for start in (True,0.0,-1,1,None):
            cases.append(lambda s=start:execution.weighted_run(machine,s,()))
            cases.append(lambda s=start:execution.budget_endpoint(machine,s,(),0))
        for budget in (True,0.0,-1,None):
            cases.append(lambda b=budget:execution.budget_endpoint(machine,0,(),b))
            cases.append(lambda b=budget:images.attained_at((),b))
            cases.append(lambda b=budget:images.capability((),b,()))
            if budget is not None:cases.append(lambda b=budget:images.restrict(context,histories,machine,b,()))
        for bad in (None,object(),{'observations':(0,)}):
            cases.append(lambda b=bad:execution.weighted_run(b,0,()))
            cases.append(lambda b=bad:execution.budget_endpoint(b,0,(),0))
            cases.append(lambda b=bad:images.joint(context,histories,b,()))
            cases.append(lambda b=bad:images.attained(b))
        bad_histories=(None,[],((0,()),),((0,()),(0,())),((0,()),[0,(0,)]),
                       ((0,()),(True,())),((0,()),(0,(0,True))),((0,()),(0,(0,1))))
        for roster in bad_histories:
            cases.append(lambda h=roster:images.restrict(context,h,machine,0,()))
            cases.append(lambda h=roster:images.joint(context,h,machine,()))
            cases.append(lambda h=roster:images.threshold_witness(context,h,machine,(),()))
        for selected in ([],None,(True,),(0.0,),(-1,),(2,),(0,0)):
            cases.append(lambda s=selected:images.restrict(context,histories,machine,None,s))
            cases.append(lambda s=selected:images.joint(context,histories,machine,s))
            cases.append(lambda s=selected:images.threshold_witness(context,histories,machine,s,()))
        for pairs in ([],None,((0,),),([0,0],),((True,0),),((0,0.0),),((-1,0),),((0,0),(0,0))):
            cases.append(lambda j=pairs:images.attained_at(j,0))
            cases.append(lambda j=pairs:images.capability(j,0,()))
            cases.append(lambda j=pairs:images.threshold(j,()))
        for target in ([],None,(True,),(0.0,),(-1,),(0,0)):
            cases.append(lambda t=target:images.threshold((),t))
            cases.append(lambda t=target:images.capability((),0,t))
            cases.append(lambda t=target:images.threshold_witness(context,histories,machine,(),t))
        for rho in ([],None,(True,),(0.0,),(0,-1)):
            cases.append(lambda r=rho:images.projection((),r))
        for values in ([],None,(True,),(0.0,),(-1,),(1,),(0,0)):
            cases.append(lambda v=values:images.projection(v,(0,)))
        cases.append(lambda:images.threshold_witness(context,histories,machine,(),(1,)))
        for i,call in enumerate(cases):
            with self.subTest(case=i),self.assertRaises(ValueError):call()
        self.assertIsNone(images.threshold((),(99,)))
        self.assertFalse(images.capability((),0,(99,)))
        self.assertEqual(images.projection((),()),())
        COVERAGE['execution_image_rejections']=len(cases)
        COVERAGE['empty_generic_target_controls']=3

    def test_resource_types_and_later_costs(self):
        cases=[]
        for kind in ('unknown',None,True,0):
            cases.extend((lambda k=kind:resources.identity(k),lambda k=kind:resources.prefix_fold(k,(),0,0),
                          lambda k=kind:resources.combine(k,0,0),lambda k=kind:resources.le(k,0,0)))
        for kind in ('nat','peak','signed'):
            bads=(True,0.0,None,(),[0]) + (() if kind=='signed' else (-1,))
            for bad in bads:
                cases.append(lambda k=kind,b=bad:resources.combine(k,0,b))
                cases.append(lambda k=kind,b=bad:resources.le(k,b,0))
                cases.append(lambda k=kind,b=bad:resources.prefix_fold(k,(2,b),0,0))
                cases.append(lambda k=kind,b=bad:resources.prefix_fold(k,(),b,0))
                cases.append(lambda k=kind,b=bad:resources.prefix_fold(k,(),0,b))
        for kind in ('vector','mixed'):
            for bad in (None,[],(0,),[0,0],(True,0),(0.0,0),(0,-1),(0,0,0)):
                cases.append(lambda k=kind,b=bad:resources.combine(k,(0,0),b))
                cases.append(lambda k=kind,b=bad:resources.le(k,b,(0,0)))
                cases.append(lambda k=kind,b=bad:resources.prefix_fold(k,((2,2),b),(0,0),(0,0)))
                cases.append(lambda k=kind,b=bad:resources.prefix_fold(k,(),b,(0,0)))
                cases.append(lambda k=kind,b=bad:resources.prefix_fold(k,(),(0,0),b))
        for bad in ([],None,''):
            cases.append(lambda b=bad:resources.prefix_fold('nat',b,0,0))
        for i,call in enumerate(cases):
            with self.subTest(case=i),self.assertRaises(ValueError):call()
        COVERAGE['resource_input_rejections']=len(cases)


if __name__=='__main__':
    import json
    r=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not r.result.wasSuccessful())
