"""Strict complete-input checks and independently certified coherent output corruptions."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fractions import Fraction as F
import unittest
from support_v27 import lts as l, events as e, tests as t, tasks as k, oracle as o
from support_v27 import event_data,test_data
COVERAGE={}


class HostileTests(unittest.TestCase):
    def test_malformed_and_unused_inputs(self):
        cases=[]
        loop=l.LTS(1,1,((0,0,0),));one=e.identity_event(1)
        test=t.Test(1,1,((0,one),));task=k.identity_task(2,(0,1))
        for v in (True,False,1.0,-1,None,'1'):
            cases.extend((lambda v=v:l.LTS(v,1,()),lambda v=v:l.LTS(1,v,()),
                          lambda v=v:e.Event(v,0,()),lambda v=v:e.Event(0,v,()),
                          lambda v=v:k.Task(v,(),(),()),lambda v=v:t.Test(v,1,())))
        for container in ([],{},'x',None):
            cases.extend((lambda v=container:l.LTS(1,1,v),lambda v=container:e.Event(0,1,v),
                          lambda v=container:t.Test(0,1,v),lambda v=container:k.from_relation(1,v)))
        for edges in (((0,0,0),(0,0,0)),((0,0,0),(0,True,0)),((0,0,0),(0,0,1)),
                      ((0,0,0),()),((0,0,0),[0,0,0]),((0,0,0),(0,0,None))):
            cases.append(lambda v=edges:l.LTS(1,1,v))
        for mapping in ((True,),(1,),(),[0],(0,0),(None,)):
            for fn in (l.forward,l.back,l.hom):cases.append(lambda v=mapping,fn=fn:fn(loop,loop,v))
        cases.append(lambda:l.forward(loop,l.LTS(1,2,()),(0,)))
        for path in ((True,()),(1,()),(0,[0]),(0,(True,)),(0,(0,8)),(0,(0,None)),[0,()],()):
            for fn in (l.endpoint,l.labels):cases.append(lambda v=path,fn=fn:fn(loop,v))
        broken=l.LTS(2,1,((0,0,0),(1,0,1)))
        # Malformed suffix follows an already ill-typed edge; it is not hidden.
        cases.extend((lambda:l.endpoint(broken,(0,(1,True))),
                      lambda:l.compose_paths(loop,(0,()),(0,(0,None))),
                      lambda:l.map_path(loop,loop,(0,),(0,(0,True))),
                      lambda:l.lift_path(loop,loop,(0,),0,(0,(True,)))))
        for value in (0,1,True,0.5,None,F(-1),F(2)):
            cases.append(lambda v=value:e.Event(2,1,((F(0),),(v,))))
        for rows in (((),),((F(1),F(1)),),([F(1)],),()):
            cases.append(lambda v=rows:e.Event(1,1,v))
        for label in (True,False,0.0,-1,(),(0,),[0,1],(0,True),(0,(1,None))):
            cases.append(lambda v=label:t.Test(1,1,((v,one),)))
        cases.extend((lambda:t.Test(1,1,((0,one),(0,e.Event(1,1,((F(0),),))))),
                      lambda:t.Test(1,1,((0,one),(1,one))),lambda:t.Test(1,1,()),
                      lambda:t.Test(1,1,((0,e.identity_event(2)),)),
                      lambda:t.Test(1,1,((0,one),(1,None)))))
        for source,target,pairs in (((True,),(0,),((True,0),)),((0,0),(0,),((0,0),)),
                     ((0,),(0,0),((0,0),)),((0,),(0,),((0,0),(0,0))),
                     ((0,),(0,),()),((0,),(0,),((0,1),)),((),(),((0,0),)),
                     ((0,),(),()),((0,),(0,),((0,0),[0,0])),([0],(0,),((0,0),))):
            cases.append(lambda a=source,b=target,c=pairs:k.Task(2,a,b,c))
        cases.extend((lambda:e.compose_event(one,e.identity_event(2)),
                      lambda:t.compose_test(test,t.Test(2,2,((0,e.identity_event(2)),))),
                      lambda:k.typed_compose(task,k.identity_task(2,(0,))),
                      lambda:k.regular(task,k.identity_task(3,(0,1)))))
        for bad in (None,(),{},'duck'):
            cases.extend((lambda v=bad:l.endpoint(v,(0,())),lambda v=bad:e.normalized(v),
                          lambda v=bad:e.compose_event(one,v),lambda v=bad:e.from_kernel(v),
                          lambda v=bad:t.aggregate(v),lambda v=bad:t.compose_test(test,v),
                          lambda v=bad:k.decode(v),lambda v=bad:k.regular_compose(task,v)))
        rejected=0
        for i,call in enumerate(cases):
            with self.subTest(case=i),self.assertRaises(ValueError):call()
            rejected+=1
        self.assertEqual(l.endpoint(loop,(0,(0,0))),0)
        self.assertEqual(t.Test(0,2,()).outcomes,())
        self.assertEqual(k.Task(2,(),(0,1),()).target,(0,1))
        self.assertEqual(l.LTS(0,0,()).edges,())
        COVERAGE.update(malformed_input_rejections=rejected,valid_empty_and_typed_controls=4)

    def test_coherent_semantic_corruptions(self):
        rejected=valid=0
        def check(actual,expected,mutants):
            nonlocal rejected,valid
            o.certify(actual,expected);valid+=1
            for bad in mutants:
                with self.assertRaises(ValueError):o.certify(bad,expected)
                rejected+=1
        raw=(2,1,((0,0,0),(0,0,1),(1,0,0),(1,0,1)))
        source=l.LTS(*raw);target=l.LTS(1,1,((0,0,0),));mapping=(0,0)
        expected=o.lifts(raw,(1,1,((0,0,0),)),mapping,0,(0,(0,0)))
        actual=l.lift_path(source,target,mapping,0,(0,(0,0)))
        check(actual,expected,(expected[:-1],expected+expected[:1],tuple(reversed(expected))))
        expected_path=o.mapped(raw,raw,(0,1),(0,(1,)))
        check(l.map_path(source,source,(0,1),(0,(1,))),expected_path,((0,(0,)),(1,(1,)),(0,())))
        half=e.Event(1,1,((F(1,2),),));composed=e.compose_event(half,half)
        expected_event=(1,1,o.trajectory(((1,1,half.rows),(1,1,half.rows))))
        check(event_data(composed),expected_event,
              ((1,1,((F(1),),)),(1,1,((F(1,2),),)),(1,1,((0.25,),))))
        zero=e.Event(1,1,((F(0),),));a=t.Test(1,1,((0,e.identity_event(1)),(1,zero)))
        result=t.compose_test(a,a)
        expected_test=(1,1,tuple(((i,j),(1,1,o.trajectory(((1,1,u.rows),(1,1,v.rows)))))
                               for i,u in a.outcomes for j,v in a.outcomes))
        data=test_data(result)
        check(data,expected_test,((1,1,data[2][:1]),(1,1,tuple(reversed(data[2]))),
              (1,1,tuple((i,event) for i,(_,event) in enumerate(data[2])))))
        r=k.from_relation(5,((0,1),));s=k.from_relation(5,((1,2),(3,4)))
        joined=k.regular_compose(r,s);data=(joined.source,joined.target,joined.pairs)
        expected=((0,),(2,4),o.relation_product(r.pairs,s.pairs))
        check(data,expected,(((0,),(2,),((0,2),)),((1,),(2,4),((1,2),)),
                             ((0,),(2,4),((0,4),))))
        COVERAGE.update(semantic_certificate_baselines=valid,coherent_semantic_rejections=rejected)
