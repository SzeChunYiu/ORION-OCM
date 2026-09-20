"""Real diagram/codec no-alarm controls and semantic/input corruptions."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v23 as o
import core_v23 as core
import regimes_v23 as r
import contexts_v23 as c
from test_diagrams_v23 import family
from test_controls_v23 import rows
COVERAGE={}


class HostileTests(unittest.TestCase):
    def test_diagram_corruptions(self):
        data=rows(((0,1),(1,-1),(F(2,5),0)));lo,hi=F(0),F(1)
        baseline=r.diagram(family(data),lo,hi);o.verify_diagram(data,lo,hi,baseline)
        cases=[]
        def edit(key,value):
            result=deepcopy(baseline);result[key]=value;cases.append((data,result))
        edit('boundaries',baseline['boundaries'][1:])
        edit('cells',baseline['cells'][1:])
        edit('possible',('i0','i1'));edit('universal',('i0',));edit('unique_everywhere','i0')
        edit('boundaries',baseline['boundaries']+(baseline['boundaries'][-1],))
        edit('cells',tuple((a,b,F(0),ids) for a,b,mid,ids in baseline['cells']))
        edit('boundaries',tuple((t,ids[:1]) for t,ids in baseline['boundaries']))
        edit('cells',tuple((a,b,mid,('i0',)) for a,b,mid,ids in baseline['cells']))
        edit('cells',list(baseline['cells']))
        edit('boundaries',((0,baseline['boundaries'][0][1]),)+baseline['boundaries'][1:])
        for key in baseline:
            bad=deepcopy(baseline);del bad[key];cases.append((data,bad))
        bad=deepcopy(baseline);bad['extra']=True;cases.append((data,bad))
        def rebuild(source,points):
            result=r.diagram(family(source),lo,hi)
            result['boundaries']=tuple((t,o.winners(source,t)) for t in points)
            result['cells']=tuple((a,b,(a+b)/2,o.winners(source,(a+b)/2)) for a,b in zip(points,points[1:]))
            return result
        # Correct midpoint labels still cannot certify a cell across a real regime.
        cases.append((data,rebuild(data,(lo,hi))))
        cases.append((data,rebuild(data,(lo,F(1,5),F(2,5),F(1,2),F(3,5),hi))))
        cases.append((data,rebuild(data,(lo,F(1,3),F(1,2),F(3,5),hi))))
        isolated=rows(((F(-1,3),1),(F(1,3),-1),(0,0)))
        bad=r.diagram(family(isolated),lo,hi)
        bad['boundaries']=tuple((t,tuple(x for x in ids if x!='i2')) for t,ids in bad['boundaries'])
        bad['possible']=('i0','i1');cases.append((isolated,bad))
        duplicate=rows(((0,0),(0,0)));bad=r.diagram(family(duplicate),lo,hi)
        bad['boundaries']=tuple((t,('i0',)) for t,_ in bad['boundaries']);bad['cells']=((lo,hi,F(1,2),('i0',)),)
        bad.update(possible=('i0',),universal=('i0',),unique_everywhere='i0');cases.append((duplicate,bad))
        nonwinning=rows(((0,0),(2,1),(3,-1)))
        # Missing root1/2 has entirely correct winner labels and summaries.
        cases.append((nonwinning,rebuild(nonwinning,(lo,hi))))
        count=0
        for source,bad in cases:
            with self.subTest(index=count),self.assertRaises(ValueError):o.verify_diagram(source,lo,hi,bad)
            count+=1
        self.assertEqual(o.intervals(rows(((0,0),(0,1))),F(-1),F(1)),{'i0':(F(0),F(1)),'i1':(F(-1),F(0))})
        COVERAGE.update(diagram_mutation_rejections=count,valid_diagram_certificates=1)

    def test_codec_corruptions(self):
        data=(('a',F(0),F(1),True,True),('b',F(2),F(0),False,True))
        encoded=c.at(family(data),F(1));o.verify_codec(data,F(1),encoded.context,encoded.decoder)
        fields={key:getattr(encoded.context,key) for key in ('n','m','admitted','defined','values','order')}
        mutations=[('n',True),('admitted',(True,True)),('defined',(True,False)),('values',(0,None)),
                   ('values',(True,1)),('values',(1,0)),('admitted',(1,False)),
                   ('order',tuple(tuple(encoded.context.order[j][i] for j in range(2)) for i in range(2)))]
        count=0
        for key,value in mutations:
            changed=dict(fields);changed[key]=value
            with self.assertRaises(ValueError):o.verify_codec(data,F(1),SimpleNamespace(**changed),encoded.decoder)
            count+=1
        for decoder in ((('a',F(9)),('b',F(2))),(('b',F(1)),('a',F(2))),
                        (('a',1),('b',F(2))),encoded.decoder[:1],list(encoded.decoder)):
            with self.assertRaises(ValueError):o.verify_codec(data,F(1),encoded.context,decoder)
            count+=1
        COVERAGE.update(codec_mutation_rejections=count,valid_codec_certificates=1)

    def test_malformed_inputs(self):
        valid=(('a',),(F(0),),(F(1),),(True,),(True,))
        good=core.AffineFamily(*valid);empty=family(());inactive=core.AffineFamily(('a',),(F(0),),(F(1),),(False,),(False,))
        checks=[]
        for index in range(5):
            for value in (None,[],{},'bad',()):
                fields=list(valid);fields[index]=value
                checks.append(lambda fields=fields:core.AffineFamily(*fields))
        for index in (1,2):
            for value in (True,False,0,1,0.0,'0',None):
                fields=list(valid);fields[index]=(value,);fields[3]=(False,);fields[4]=(False,)
                checks.append(lambda fields=fields:core.AffineFamily(*fields))
        for index in (3,4):
            for value in (0,1,None,'True'):
                fields=list(valid);fields[index]=(value,)
                checks.append(lambda fields=fields:core.AffineFamily(*fields))
        for ids in (('',),(True,),(0,)):
            checks.append(lambda ids=ids:core.AffineFamily(ids,*valid[1:]))
        checks.append(lambda:core.AffineFamily(('a','a'),(F(0),F(0)),(F(0),F(0)),(True,True),(True,True)))
        for model in (good,empty,inactive):
            for value in (True,False,0,0.0,None,'0'):
                checks.extend([lambda m=model,x=value:r.diagram(m,x,F(1)),lambda m=model,x=value:r.diagram(m,F(0),x),
                               lambda m=model,x=value:r.winner_ids(m,x),lambda m=model,x=value:c.at(m,x)])
            checks.append(lambda m=model:r.diagram(m,F(1),F(0)))
        for bad in (None,(),object()):
            checks.extend([lambda x=bad:r.diagram(x,F(0),F(1)),lambda x=bad:c.at(x,F(0)),lambda x=bad:r.score(x,0,F(0))])
        encoded=c.at(good,F(0))
        for index in (True,False,0.0,-1,1,None):
            checks.extend([lambda x=index:r.score(good,x,F(0)),lambda x=index:c.decoded(encoded,x)])
        for decoder in (None,[],(),(('a',0),),(('a',F(0)),('b',F(1)))):
            checks.append(lambda d=decoder:c.Encoded(encoded.context,d))
        checks.extend([lambda:c.Encoded(None,(('a',F(0)),)),lambda:c.decoded(None,0)])
        count=0
        for check in checks:
            with self.subTest(index=count),self.assertRaises(ValueError):check()
            count+=1
        COVERAGE['malformed_input_rejections']=count


if __name__=='__main__':
    import json
    run=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not run.result.wasSuccessful())
