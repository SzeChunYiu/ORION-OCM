"""Strict malformed inputs, missing premises and empty-dimension controls."""
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prefix_v18 as prefix
import measures_v18 as measures
import resources_v18 as resources
import interaction_v18 as interaction
COVERAGE = {}


class HostileTests(unittest.TestCase):
    def reject(self,cases):
        rejected = 0
        for fn,args in cases:
            with self.subTest(function=fn.__name__,args=args),self.assertRaises(ValueError):
                fn(*args)
            rejected += 1
        return rejected

    def test_prefix_validation(self):
        empty = prefix.Book(2,())
        cases = [(prefix.Book,(n,())) for n in (True,-1,2.0,None)]
        cases += [(prefix.Book,(2,rows)) for rows in ([],None,(((False,),),),
            (((False,),0,1),),(([False],0),),(((0,),0),),(((False,),True),),
            (((False,),2),),(((False,),-1),),(((False,),0.0),),
            (((False,),0),((False,),1)),(((),0),((True,),1)),
            (((False,True),1),((False,),0)))]
        cases += [(prefix.Wrapped,(empty,target,2)) for target in (True,-1,2,0.0,None)]
        cases += [(prefix.Wrapped,(empty,0,pad)) for pad in (True,0,-1,2.0,None)]
        cases += [(prefix.Wrapped,(None,0,2)),(prefix.decode,(None,())),
                  (prefix.compiled,(empty,)),(prefix.shortest,(None,)),(prefix.weights,(None,))]
        cases += [(prefix.decode,(empty,program)) for program in ('0',[False],(0,),(1,),None)]
        cases += [(prefix.score,(empty,values)) for values in ((),[F(0),F(1)],(F(0),0),
            (F(0),True),(F(0),0.5),(F(-1),F(0)),(F(0),F(2)),None)]
        cases += [(prefix.Book,(0,(((),0),)))]
        COVERAGE['prefix_malformed_rejections'] = self.reject(cases)
        zero = prefix.Book(0,())
        self.assertEqual(prefix.score(zero,()),0)
        self.assertEqual(prefix.weights(zero),{})
        self.assertIsNone(prefix.decode(zero,()))
        COVERAGE['empty_output_alphabet_controls'] = 1

    def test_probability_context_and_conditioning_validation(self):
        valid = (F(1,2),F(1,2))
        family = (valid,)
        cases = [(measures.expectation,(weight,(F(0),F(1)))) for weight in
                 ((),[F(1,2),F(1,2)],(F(-1),F(2)),(F(0),F(0)),(F(1),F(1)),
                  (0,F(1)),(True,F(0)),(0.5,0.5),None)]
        cases += [(measures.lower,(prior,(F(0),F(1)))) for prior in
                  ((),[],None,((),),(valid,valid),(valid,(F(1),)),((0.5,0.5),))]
        cases += [(measures.expectation,(valid,value)) for value in
                  ((),(F(0),),[F(0),F(1)],(F(0),1),(F(0),True),(F(-1),F(0)),(F(0),F(2)),None)]
        cases += [(measures.expectation_context,(p,values,valid)) for p,values in
                  (([True],((F(0),F(0)),)),((1,),((F(0),F(0)),)),
                   ((True,),()),((True,),[None]),((False,),((F(0),F(2)),)))]
        cases += [(measures.lower_context,((False,),((F(0),2),),family))]
        cases += [(measures.conditional,(valid,event)) for event in
                  ((),[],(True,),(0,0),(2,),(-1,),None)]
        cases += [(measures.conditional,((F(1),F(0)),(1,)))]
        cases += [(measures.recursive_lower,(family,(F(0),F(1)),partition)) for partition in
                  ((),[],((0,),),((0,),(0,1)),((True,),(1,)),((0,),()),((0,),(2,)),None)]
        cases += [(measures.recursive_lower,(((F(1),F(0)),),(F(0),F(1)),((0,),(1,))))]
        COVERAGE['measure_malformed_rejections'] = self.reject(cases)
        self.assertEqual(measures.expectation_context((),(),valid).context.n,0)
        self.assertEqual(measures.lower_context((),(),family).context.n,0)
        COVERAGE['empty_history_measure_controls'] = 2

    def test_resource_and_interaction_validation(self):
        relation = ((True,True),(False,True))
        bad_relations = (None,[],((True,),()),((1,),),((False,),),
                        ((True,True,False),(False,True,True),(False,False,True)))
        cases = [(resources.signatures,(bad,)) for bad in bad_relations]
        cases += [(resources.converts,(relation,a,b)) for a,b in
                  ((True,0),(0,False),(-1,0),(0,2),(0.0,0),(None,0))]
        cases += [(resources.resource_context,(p,states,relation,target)) for p,states,target in
                  (([True],(0,),0),((1,),(0,),0),((True,),[0],0),((True,),(),0),
                   ((False,),(True,),0),((False,),(2,),0),((True,),(0,),True),((True,),(0,),2))]
        cases += [(resources.resource_context,((),(),(),0))]
        cases += [(interaction.reward,(target,())) for target in (True,-1,2,0.0,None)]
        cases += [(interaction.reward,(0,actions)) for actions in
                  ([0],(True,),(False,),(2,),(-1,),(0.0,),None)]
        COVERAGE['resource_interaction_malformed_rejections'] = self.reject(cases)
        self.assertEqual(resources.signatures(()),())
        COVERAGE['empty_resource_controls'] = 1


if __name__ == '__main__':
    result = unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
