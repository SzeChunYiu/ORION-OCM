"""Strict malformed input rejection, including semantically hidden late descendants."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unittest
from support_v26 import core,oracle,actual,make
import oracle_resource_v26 as independent
import functors_v26 as functors
import restrictions_v26 as restrictions
import resource_v26 as resource
COVERAGE={}


class HostileTests(unittest.TestCase):
    def test_tree_path_response_hostiles(self):
        c=next(c for c in oracle.models(2) if c[0]==((0,None),(None,1)))
        cat=actual(c);f=functors.Functor(cat,cat,(0,1),(0,1))
        base,costs=independent.chain();model=resource.ResourceLift(make(base),costs,2)
        invalid=(None,(),[],('unknown',0),('arrow',),('arrow',0,1),('empty',),('seq',('arrow',0)),
                 ('seq',('arrow',0),('arrow',0),('arrow',0)),('arrow',True),('arrow',0.0),('arrow',-1),
                 ('arrow',2),('empty',False),('empty',1.0),('empty',-1),('empty',2),['arrow',0])
        fail=('seq',('empty',0),('empty',1));count=0
        for bad in invalid:
            for tree in (bad,('seq',fail,bad),('seq',bad,fail)):
                for call in (lambda:functors.map_tree(f,tree),lambda:core.trees.typed_eval(cat,tree)):
                    with self.assertRaises(ValueError):call()
                    count+=1
        paths=(None,(),[],(0,), (0,(),0),(True,()),(0.0,()),(-1,()),(2,()),(0,[]),(0,(True,)),
               (0,(1.0,)),(0,(-1,)),(0,(2,)),(0,(1,True)),(0,(0,1,2)))
        path_count=0
        for bad in paths:
            for call in (lambda:functors.path_response(cat,bad),lambda:functors.map_path(f,bad)):
                with self.assertRaises(ValueError):call()
                path_count+=1
        for bad in (None,(),(0,), (0,[]),(False,()),(3,()),(0,(1,True)),(0,(4,6)),(0,(2,False))):
            with self.assertRaises(ValueError):resource.lift_path(model,bad,0)
            path_count+=1
        response_count=0
        for bad in ((),[],(0,0),(0,0,0,0),(False,0,0),(0.0,0,0),(0,0,True),(0,0,0.0),
                    (0,0,-1),(0,0,2),(1,0,0),(0,1,0)):
            with self.assertRaises(ValueError):functors.map_response(f,bad)
            response_count+=1
        self.assertIsNone(functors.path_response(cat,(0,(1,))))
        self.assertIsNone(functors.map_response(f,None))
        self.assertEqual(functors.path_response(cat,(1,())),(1,1,1))
        self.assertEqual(functors.map_path(f,(0,(1,))),(0,(1,)))
        COVERAGE.update(malformed_tree_rejections=count,malformed_path_rejections=path_count,
                        malformed_response_rejections=response_count,valid_failure_controls=4)

    def test_constructor_and_unused_data_hostiles(self):
        cat=actual(oracle.models(1)[0]);empty=actual(oracle.models(0)[0])
        discrete=actual(next(c for c in oracle.models(2) if c[0]==((0,None),(None,1))))
        invalid=(None,[],(),(True,),(0.0,),(-1,),(1,),(0,0))
        count=0
        for bad in invalid:
            for call in (lambda:functors.Functor(cat,cat,bad,(0,)),lambda:functors.Functor(cat,cat,(0,),bad)):
                with self.assertRaises(ValueError):call()
                count+=1
        for bad in (None,object(),core.Table(((0,),))):
            for call in (lambda:functors.Functor(bad,cat,(),()),lambda:functors.Functor(cat,bad,(0,),(0,)),
                         lambda:restrictions.admission_laws(bad,()),lambda:restrictions.wide_restriction(bad,()),
                         lambda:functors.path_response(bad,(0,())),lambda:resource.ResourceLift(bad,(),0)):
                with self.assertRaises(ValueError):call()
                count+=1
        unlawful=core.Typed(2,(0,1),(0,1),(0,1),core.Table(((0,0),(None,1))))
        with self.assertRaises(ValueError):functors.Functor(unlawful,discrete,(0,1),(0,1))
        count+=1
        for bad in ((0,True),(0,1.0),(0,2),(0,-1)):
            for call in (lambda:functors.Functor(discrete,discrete,(0,1),bad),
                         lambda:functors.Functor(discrete,discrete,bad,(0,1))):
                with self.assertRaises(ValueError):call()
                count+=1
        for bad in (None,[],{0},(0,0),(True,),(0.0,),(-1,),(1,)):
            for call in (lambda:restrictions.admission_laws(cat,bad),lambda:restrictions.wide_restriction(cat,bad)):
                with self.assertRaises(ValueError):call()
                count+=1
        c,costs=independent.chain();base=make(c)
        for bad in (None,list(costs),costs[:-1],(0,1,1,0,1,0),(1,1,2,0,1,0),
                    (0,1,2,0,1,False),(0,1,2,0,1,0.0),(0,1,2,0,1,-1)):
            with self.assertRaises(ValueError):resource.ResourceLift(base,bad,2)
            count+=1
        for bad in (None,True,2.0,-1):
            with self.assertRaises(ValueError):resource.ResourceLift(base,costs,bad)
            count+=1
        model=resource.ResourceLift(base,costs,2)
        for bad in (None,True,1.0,-1,3):
            with self.assertRaises(ValueError):resource.lift_path(model,(0,()),bad)
            count+=1
        f=functors.Functor(cat,cat,(0,),(0,))
        for bad in (None,cat,object()):
            for call in (lambda:functors.object_injective(bad),lambda:functors.map_tree(bad,('arrow',0)),
                         lambda:functors.map_path(bad,(0,())),lambda:functors.map_response(bad,None),
                         lambda:resource.lift_path(bad,(0,()),0)):
                with self.assertRaises(ValueError):call()
                count+=1
        self.assertTrue(functors.object_injective(functors.Functor(empty,cat,(),())))
        self.assertEqual(resource.ResourceLift(empty,(),0).object_labels,())
        self.assertEqual(functors.map_tree(f,('empty',0)),('empty',0))
        COVERAGE.update(malformed_constructor_rejections=count,valid_constructor_controls=3)
