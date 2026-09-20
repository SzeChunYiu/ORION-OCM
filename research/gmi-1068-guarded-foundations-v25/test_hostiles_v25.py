"""Full-tree validation, unused encoder fields and independent semantic corruption checks."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v25 as o
import core_v25 as c
import syntax_v25 as syntax
import trees_v25 as trees
import presentations_v25 as p
import transports_v25 as tr
import information_v25 as info
import named_v25 as named
COVERAGE={}
A=lambda x:('arrow',x)
E=lambda x:('empty',x)
S=lambda a,b:('seq',a,b)

class HostileTests(unittest.TestCase):
    def test_all_descendants_and_inputs(self):
        table=c.Table(((0,None),(None,1)));cat=c.old_categories.reconstruct(table)
        model=p.Presented(2,(0,1),table);nm=named.NamedPresented(model,(0,1))
        methods=(lambda t:syntax.validate_tree(t,2,2),lambda t:trees.typed_eval(cat,t),lambda t:trees.typed_word(cat,t),
                 lambda t:trees.encode_typed(cat,t),lambda t:trees.raw_table_eval(table,t),lambda t:trees.raw_table_word(table,t),
                 lambda t:trees.raw_table_encoding(table,t),lambda t:p.raw_eval(model,t),lambda t:p.guarded_word(model,t),
                 lambda t:named.named_eval(nm,t),lambda t:named.named_word(nm,t))
        malformed=(None,(),[],['arrow',0],('BAD',0),(True,0),('arrow',),('arrow',0,1),('seq',A(0)),
                   ('seq',A(0),A(1),A(0)),A(True),A(0.0),A(-1),A(2),E(True),E(2),E(None))
        rejected=0
        for index,bad in enumerate(malformed):
            for method in methods:
                for tree in (bad,S(S(A(0),A(1)),bad)):
                    with self.subTest(case=index),self.assertRaises(ValueError):method(tree)
                    rejected+=1
        COVERAGE['malformed_tree_rejections']=rejected
        cases=[]
        for bad in (True,2.0,-1,None):
            cases.extend((lambda bad=bad:p.Presented(bad,(),c.Table(())),lambda bad=bad:syntax.validate_tree(A(0),bad,2)))
        for labels in ([0,1],(1,0),(0,0),(0,True),(0,2),(-1,1)):
            cases.append(lambda labels=labels:p.Presented(2,labels,table))
        for raw in (None,SimpleNamespace(rows=table.rows),c.Table(()),c.Table(((0,0),(0,0))),c.Table(((0,1),(1,None)))):
            cases.append(lambda raw=raw:p.Presented(2,(0,1),raw))
        for values in ([0,1],(),(0,),(0,0),(0,True),(0,2),(-1,1)):
            cases.append(lambda values=values:named.NamedPresented(model,values))
        joined=p.Presented(2,(0,1),c.Table(((0,1),(1,1))))
        cases.append(lambda:named.NamedPresented(joined,(0,1)))
        for bad in (None,SimpleNamespace(ambient_size=2,labels=(0,1),table=table)):
            for function in (p.padded,p.carrier_from_table,p.core_signature):cases.append(lambda f=function,b=bad:f(b))
            cases.extend((lambda bad=bad:p.raw_eval(bad,A(0)),lambda bad=bad:p.guarded_word(bad,A(0)),
                          lambda bad=bad:named.NamedPresented(bad,()),lambda bad=bad:trees.typed_eval(bad,A(0))))
        for bad in (None,cat,model):cases.append(lambda bad=bad:named.named_eval(bad,E(0)))
        for mapping in ([0,1],(),(0,0),(True,1),(0,2),(0,1.0)):
            cases.extend((lambda m=mapping:syntax.map_tree(E(0),m,(0,1)),
                          lambda m=mapping:tr.relabel_category(cat,(0,1),m),
                          lambda m=mapping:tr.relabel_category(cat,m,(0,1)),
                          lambda m=mapping:tr.relabel_presented(model,m),
                          lambda m=mapping:tr.map_response(cat,None,m,(0,1))))
        for response in ((),[0,0,0],(False,0,0),(0,1,0),(0,0,2)):
            cases.append(lambda response=response:tr.map_response(cat,response,(0,1),(0,1)))
        for codes in ([0],(),(True,),(0.0,),(-1,),(None,)):
            cases.extend((lambda codes=codes:info.core_recoverable((model,),codes),
                          lambda codes=codes:info.table_recoverable((model,),codes),
                          lambda codes=codes:named.named_recoverable((nm,),codes)))
        singleton=p.Presented(1,(0,),c.Table(((0,),)))
        cases.extend((lambda:info.core_recoverable((model,singleton),(0,1)),
                      lambda:info.table_recoverable([model],(0,)),
                      lambda:named.named_recoverable((nm,named.NamedPresented(joined,(0,))),(0,1)),
                      lambda:info.core_recoverable((model,None),(0,1)),
                      lambda:named.named_recoverable((nm,None),(0,1))))
        rejected=0
        for index,call in enumerate(cases):
            with self.subTest(input=index),self.assertRaises(ValueError):call()
            rejected+=1
        COVERAGE['malformed_model_encoder_rejections']=rejected

    def test_semantic_certificates(self):
        cat=c.old_categories.reconstruct(c.Table(((0,None),(None,1))))
        good=S(E(0),E(0));expected=o.typed(cat.table.rows,cat.source,cat.target,cat.identities,good)
        self.assertTrue(o.certify(trees.typed_eval(cat,good),expected));valid=1;rejected=0
        for bad in (None,(1,1,1),(False,0,0),[0,0,0]):
            with self.assertRaises(ValueError):o.certify(bad,expected)
            rejected+=1
        failure=S(E(0),E(1));self.assertTrue(o.certify(trees.typed_eval(cat,failure),None));valid+=1
        for bad in (0,False,(0,0,0)):
            with self.assertRaises(ValueError):o.certify(bad,None)
            rejected+=1
        word=o.encoding(failure,cat.identities);self.assertTrue(o.certify(trees.encode_typed(cat,failure),word));valid+=1
        for bad in ((),(0,),(1,0),(False,1)):
            with self.assertRaises(ValueError):o.certify(bad,word)
            rejected+=1
        expected_bridge=(word,None)
        self.assertTrue(o.certify((trees.encode_typed(cat,failure),trees.typed_eval(cat,failure)),expected_bridge));valid+=1
        for changed in (E(0),S(E(1),E(0)),S(E(0),E(0))):
            bad=(trees.encode_typed(cat,changed),trees.typed_eval(cat,changed))
            with self.assertRaises(ValueError):o.certify(bad,expected_bridge)
            rejected+=1
        model=p.Presented(2,(0,),c.Table(((0,),)));pad=o.pad(2,(0,),((0,),))
        self.assertTrue(o.certify(p.core_signature(model),((0,),pad)));valid+=1
        for bad in (((),pad),((0,1),pad),((0,),((0,0),(0,0)))):
            with self.assertRaises(ValueError):o.certify(bad,((0,),pad))
            rejected+=1
        full=p.Presented(2,(0,1),cat.table);first=named.NamedPresented(full,(0,1));other=named.NamedPresented(full,(1,0))
        expected=tuple(o.raw(cat.table.rows,(0,1),(0,1),t,(0,1)) for t in o.basis(2,2))
        self.assertTrue(o.certify(tuple(named.named_eval(first,t) for t in o.basis(2,2)),expected));valid+=1
        with self.assertRaises(ValueError):o.certify(tuple(named.named_eval(other,t) for t in o.basis(2,2)),expected)
        rejected+=1
        for function in (info.core_recoverable,info.table_recoverable,named.named_recoverable):
            o.certify(function((),()),True);valid+=1
        COVERAGE.update(valid_semantic_certificates=valid,semantic_mutation_rejections=rejected)

if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2).result
    print(json.dumps(COVERAGE,sort_keys=True));raise SystemExit(not result.wasSuccessful())
