"""All small preorder maps, actual transport semantics and duality."""
from itertools import product
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import oracle_v17 as oracle
import ops_v17 as ops
from core_v17 import Context,observe,compare,domain
COVERAGE={}


def contexts(order):
    for admitted,values in oracle.assignments(tuple(range(len(order))),2):
        yield Context(2,len(order),admitted,tuple(v is not None for v in values),values,order)


class MapTests(unittest.TestCase):
    def test_all_maps_and_transports(self):
        orders=tuple(order for n in range(4) for order in oracle.preorders(n))
        candidates=monotone=reflecting=injective=transports=observations=comparisons=0
        small=[]
        for source in orders:
            original=tuple(contexts(source))
            for target in orders:
                for mapping in product(range(len(target)),repeat=len(source)):
                    expected=oracle.properties(source,target,mapping)
                    self.assertEqual(ops.map_properties(source,target,mapping),expected)
                    candidates+=1
                    monotone+=expected[0];reflecting+=expected[1];injective+=expected[2]
                    if not expected[0]:continue
                    if len(source)<=2 and len(target)<=2:small.append((source,target,mapping))
                    for context in original:
                        changed=ops.postcompose(context,target,mapping)
                        self.assertEqual((changed.admitted,changed.defined),(context.admitted,context.defined))
                        self.assertEqual(changed.values,tuple(None if v is None else mapping[v] for v in context.values))
                        for h in range(2):
                            tag,value=observe(context,h)
                            self.assertEqual(observe(changed,h),(tag,mapping[value] if tag=='VALUE' else None))
                            observations+=1
                        for a,b in product(domain(context),repeat=2):
                            before,after=compare(context,a,b),compare(changed,a,b)
                            self.assertEqual(after,target[mapping[context.values[a]]][mapping[context.values[b]]])
                            self.assertTrue(not before or after)
                            if expected[1]:self.assertEqual(before,after)
                            comparisons+=1
                        transports+=1
        self.assertEqual(candidates,24907)
        compositions=0
        for source,middle,first in small:
            c=Context(2,len(source),(True,True),(bool(source),)*2,
                      tuple(i%len(source) if source else None for i in range(2)),source)
            for middle2,target,second in small:
                if middle!=middle2:continue
                combined=tuple(second[x] for x in first)
                self.assertEqual(ops.postcompose(ops.postcompose(c,middle,first),target,second),
                                 ops.postcompose(c,target,combined))
                compositions+=1
        COVERAGE.update(map_candidates=candidates,monotone_maps=monotone,reflecting_maps=reflecting,
                        injective_maps=injective,transport_contexts=transports,transport_observations=observations,
                        transport_comparisons=comparisons,map_composition_equations=compositions)

    def test_duals_identity_and_missing_premises(self):
        duals=comparisons=0
        for n in range(4):
            for order in oracle.preorders(n):
                for context in contexts(order):
                    reversed_context=ops.dual(context)
                    self.assertEqual(ops.dual(reversed_context),context)
                    self.assertEqual(ops.postcompose(context,order,tuple(range(n))),context)
                    self.assertEqual((reversed_context.admitted,reversed_context.defined,reversed_context.values),
                                     (context.admitted,context.defined,context.values))
                    for a,b in product(domain(context),repeat=2):
                        self.assertEqual(compare(reversed_context,a,b),compare(context,b,a))
                        comparisons+=1
                    duals+=1
        discrete=((True,False),(False,True))
        chain=((True,True),(False,True))
        self.assertEqual(ops.map_properties(discrete,chain,(0,1)),(True,False,True))
        self.assertEqual(ops.map_properties(chain,((True,),),(0,0)),(True,False,False))
        ranked=Context(2,2,(True,True),(True,True),(0,1),chain)
        inverted=ops.map_values(ranked,chain,(1,0))
        self.assertEqual((inverted.admitted,inverted.defined),(ranked.admitted,ranked.defined))
        self.assertTrue(compare(ranked,0,1));self.assertFalse(compare(inverted,0,1))
        self.assertEqual(tuple(observe(inverted,h) for h in range(2)),(('VALUE',1),('VALUE',0)))
        empty_active=Context(1,2,(True,),(False,),(None,),chain)
        with self.assertRaises(ValueError):ops.postcompose(empty_active,chain,(1,0))
        ambient=Context(2,2,(False,True),(True,False),(1,None),chain)
        mapped=ops.postcompose(ambient,((True,),),(0,0))
        self.assertEqual(mapped.values,(0,None))
        self.assertEqual(observe(mapped,0),('ILLEGAL',None))
        malformed=[]
        for mapping in ((True,),(0.0,),(),(1,),[0],None):
            malformed.append(lambda m=mapping:ops.map_properties(((True,),),((True,),),m))
        for order in (((False,),),((1,),),((1.0,),),((True,False),),[],None):
            malformed.append(lambda o=order:ops.map_properties(o,((True,),),(0,)))
        for i,call in enumerate(malformed):
            with self.subTest(case=i),self.assertRaises(ValueError):call()
        COVERAGE.update(dual_contexts=duals,dual_comparison_equations=comparisons,
                        missing_reflection_controls=2,empty_active_nonmonotone_rejections=1,
                        ambient_transport_controls=1,map_malformed_rejections=len(malformed),unrestricted_map_reversal_controls=1)


if __name__=='__main__':
    program=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
