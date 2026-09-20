"""Actual evaluator values and declared orders, independent of encoding indices."""
from itertools import product
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import oracle_v17 as oracle
import specializations_v17 as core
from core_v17 import compare,domain,Context
COVERAGE={}


class SpecializationTests(unittest.TestCase):
    def test_actual_specialization_corpus(self):
        vectors=tuple(product((-1,0,1),repeat=2))
        costs=tuple(product((0,1,2),repeat=2))
        sets=tuple(x for x in oracle.powerset(3) if x)
        families=(('utility',(-1,0,1),3,core.utility,lambda a,b:a<=b),
                  ('acceptance',(False,True),3,core.acceptance,lambda a,b:not a or b),
                  ('vector',vectors,2,lambda p,v:core.vector(p,v,2),lambda a,b:oracle.product_order(a,b)),
                  ('cost',costs,2,lambda p,v:core.vector(p,v,2,prefer_lower=True),lambda a,b:oracle.product_order(a,b,True)),
                  ('confidence',sets,2,lambda p,v:core.confidence(p,v,3),lambda a,b:b<=a))
        total=observations=comparisons=numeric=0
        for name,carrier,n,constructor,le in families:
            count=0
            for admitted,values in oracle.assignments(carrier,n):
                encoded=constructor(admitted,values)
                self.assertIs(type(encoded.context),Context)
                self.assertEqual(encoded.context.admitted,admitted)
                self.assertEqual(encoded.context.defined,tuple(v is not None for v in values))
                for h in range(n):
                    self.assertEqual(core.decoded(encoded,h),oracle.observe(admitted,values,h))
                    if values[h] is not None:
                        self.assertEqual(encoded.labels[encoded.context.values[h]],values[h])
                    observations+=1
                for a,b in product(domain(encoded.context),repeat=2):
                    self.assertEqual(compare(encoded.context,a,b),le(values[a],values[b]))
                    comparisons+=1
                if name=='acceptance':
                    embedded=core.acceptance_numeric(admitted,values)
                    for h in range(n):
                        tag,value=oracle.observe(admitted,values,h)
                        expected=(tag,int(value) if tag=='VALUE' else None)
                        self.assertEqual(core.decoded(embedded,h),expected)
                        if tag=='VALUE':self.assertIs(type(core.decoded(embedded,h)[1]),int)
                    for a,b in product(domain(encoded.context),repeat=2):
                        self.assertEqual(compare(encoded.context,a,b),compare(embedded.context,a,b))
                        numeric+=1
                total+=1;count+=1
            COVERAGE[name+'_contexts']=count
        self.assertEqual(total,512)
        COVERAGE.update(specialization_contexts=total,specialization_observations=observations,
                        semantic_comparisons=comparisons,acceptance_embedding_comparisons=numeric)

    def test_orientation_partiality_and_malformed_values(self):
        vector=core.vector((True,True),((0,1),(1,0)),2)
        self.assertFalse(compare(vector.context,0,1));self.assertFalse(compare(vector.context,1,0))
        cost=core.vector((True,True),((0,0),(1,1)),2,prefer_lower=True)
        self.assertFalse(compare(cost.context,0,1));self.assertTrue(compare(cost.context,1,0))
        confidence=core.confidence((True,True),(frozenset((0,)),frozenset((1,))),2)
        self.assertFalse(compare(confidence.context,0,1));self.assertFalse(compare(confidence.context,1,0))
        zero=core.vector((True,True),((),None),0)
        self.assertEqual(core.decoded(zero,0),('VALUE',()))
        self.assertEqual(core.decoded(zero,1),('UNDEFINED',None))
        ambient=(core.utility((False,True),(7,None)),core.acceptance((False,True),(False,None)),
                 core.vector((False,True),((1,2),None),2),
                 core.confidence((False,True),(frozenset((0,)),None),1))
        for encoded in ambient:
            self.assertTrue(encoded.context.defined[0])
            self.assertEqual(core.decoded(encoded,0),('ILLEGAL',None))
            self.assertEqual(core.decoded(encoded,1),('UNDEFINED',None))
        invalid=[]
        for value in (True,1.0,'1'):
            invalid.append(lambda v=value:core.utility((True,),(v,)))
        for value in (0,1,0.0,'yes'):
            invalid.append(lambda v=value:core.acceptance((True,),(v,)))
        for values in (((True,0),),((0.0,0),),((0,),),([0,1],)):
            invalid.append(lambda v=values:core.vector((True,),v,2))
        for dimension in (-1,True,2.0):
            invalid.append(lambda d=dimension:core.vector((True,),((0,0),),d))
        for value in (frozenset(),{0},frozenset((True,)),frozenset((0.0,)),frozenset((-1,)),frozenset((2,))):
            invalid.append(lambda v=value:core.confidence((True,),(v,),2))
        for hypotheses in (-1,True,2.0):
            invalid.append(lambda h=hypotheses:core.confidence((True,),(frozenset((0,)),),h))
        invalid.extend((lambda:core.utility((1,),(0,)),lambda:core.utility((True,),()),
                        lambda:core.utility([True],(0,)),lambda:core.utility((True,),[0]),
                        lambda:core.vector((True,),((0,0),),2,prefer_lower=1)))
        for i,call in enumerate(invalid):
            with self.subTest(case=i),self.assertRaises(ValueError):call()
        COVERAGE.update(incomparability_controls=2,cost_orientation_controls=1,zero_vector_domain_controls=1,
                        ambient_specialization_controls=len(ambient),specialization_malformed_rejections=len(invalid))


if __name__=='__main__':
    program=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
