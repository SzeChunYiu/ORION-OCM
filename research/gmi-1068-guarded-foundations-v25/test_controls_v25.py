"""Actual survivor-law failures and information-preserving encoding revivals."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v25 as o
import core_v25 as c
import trees_v25 as t
import presentations_v25 as p
import named_v25 as named
import information_v25 as info
import syntax_v25 as syntax
import transports_v25 as transport
COVERAGE={}
A=lambda x:('arrow',x)
E=lambda x:('empty',x)
S=lambda x,y:('seq',x,y)

class ControlTests(unittest.TestCase):
    def test_survivor_laws(self):
        count=0
        discrete=c.Table(((0,None),(None,1)));join=c.Table(((0,1),(1,1)))
        fill=lambda table:tuple(tuple(1 if x is None else x for x in row) for row in table.rows)
        self.assertEqual(fill(discrete),fill(join))
        o.certify(t.raw_table_eval(discrete,S(A(0),A(1))),None)
        o.certify(t.raw_table_eval(join,S(A(0),A(1))),1);count+=1
        groups=(c.Table(tuple(tuple((i+j)%4 for j in range(4)) for i in range(4))),
                c.Table(tuple(tuple(i^j for j in range(4)) for i in range(4))))
        for table,wanted in zip(groups,(2,0)):
            c.old_partial.validate(table);self.assertEqual(c.old_partial.units(table),(0,))
            o.certify(t.raw_table_eval(table,S(A(1),A(1))),wanted)
            o.certify(c.old_partial.word(table,(1,1)),wanted)
        count+=1
        for rows,triple,flags in ((((0,1,2),(1,2,0),(2,0,2)),(1,1,2),(False,True,True)),
                                  (((0,None,2),(None,1,2),(2,None,2)),(0,1,2),(False,True,True))):
            self.assertEqual(o.laws(rows),flags);x,y,z=triple;table=c.Table(rows)
            left=S(S(A(x),A(y)),A(z));right=S(A(x),S(A(y),A(z)))
            expected=(o.raw(rows,tuple(range(3)),o.units(rows),left),o.raw(rows,tuple(range(3)),o.units(rows),right))
            self.assertNotEqual(*expected);o.certify((t.raw_table_eval(table,left),t.raw_table_eval(table,right)),expected)
            with self.assertRaises(ValueError):c.old_categories.reconstruct(table)
            count+=1
        coherence=c.Table(((0,1),(1,None)));self.assertEqual(o.laws(coherence.rows),(True,True,False))
        o.certify(t.raw_table_eval(coherence,S(A(1),A(1))),None)
        with self.assertRaises(ValueError):c.old_categories.reconstruct(coherence)
        count+=1
        for rows in (((0,0),(0,0)),((0,0),(1,1)),((0,1),(0,1))):
            self.assertEqual(o.laws(rows),(True,False,True));self.assertEqual(o.units(rows),())
            table=c.Table(rows);o.certify(t.raw_table_eval(table,E(0)),None)
            # These designated candidates are not assumed to be genuine units.
            self.assertTrue(t.raw_table_eval(table,S(A(0),A(1)))!=1 or t.raw_table_eval(table,S(A(1),A(0)))!=1)
            with self.assertRaises(ValueError):c.old_categories.reconstruct(table)
            count+=1
        COVERAGE['survivor_law_controls']=count

    def test_anchored_categories(self):
        checks=0
        discrete=c.old_categories.reconstruct(c.Table(((0,None),(None,1))))
        o.certify(t.typed_eval(discrete,S(E(0),E(1))),None)
        o.certify(t.typed_eval(discrete,S(E(0),E(0))),(0,0,0))
        o.certify(t.encode_typed(discrete,S(E(0),E(1))),(0,1))
        self.assertEqual(o.encoding(S(E(0),E(1)),(0,1)),(0,1));checks+=1
        # Naive deletion sends BOTH distinct-empty and same-empty trees to [].
        drop=lambda node:() if node[0]=='empty' else (node[1],) if node[0]=='arrow' else drop(node[1])+drop(node[2])
        self.assertEqual(drop(S(E(0),E(1))),drop(S(E(0),E(0))));checks+=1
        rows=((0,None,2),(None,1,None),(None,2,None))
        walking=c.Typed(2,(0,1,0),(0,1,1),(0,1),c.Table(rows));c.old_categories.validate_category(walking)
        for tree in (S(E(0),S(A(2),E(1))),S(S(E(0),A(2)),E(1))):
            o.certify(t.typed_eval(walking,tree),(0,1,2));o.certify(t.typed_word(walking,tree),(0,1,2));checks+=1
        for tree in (S(E(1),A(2)),S(A(2),E(0)),S(E(0),S(A(2),E(0)))):
            o.certify(t.typed_eval(walking,tree),None);self.assertEqual(drop(tree),(2,));checks+=1
        singleton=c.old_categories.reconstruct(c.Table(((0,),)))
        for tree in (A(0),E(0),S(E(0),S(A(0),E(0)))):
            o.certify(t.typed_eval(singleton,tree),(0,0,0));checks+=1
        empty=c.old_categories.reconstruct(c.Table(()));self.assertEqual(empty.object_count,0);checks+=1
        COVERAGE['anchored_category_controls']=checks

    def test_carrier_and_names(self):
        checks=0
        empty=p.Presented(1,(),c.Table(()));singleton=p.Presented(1,(0,),c.Table(((0,),)))
        o.certify((p.raw_eval(empty,A(0)),p.raw_eval(singleton,A(0))),(None,0))
        o.certify(c.old_partial.word(p.padded(empty),(0,)),0)
        o.certify(p.guarded_word(empty,A(0)),None)
        self.assertFalse(info.core_recoverable((empty,singleton),(0,0)));checks+=1
        left=p.Presented(2,(0,),c.Table(((0,),)));right=p.Presented(2,(1,),c.Table(((0,),)))
        self.assertEqual(left.table,right.table);self.assertNotEqual(p.padded(left),p.padded(right))
        o.certify((p.raw_eval(left,A(0)),p.raw_eval(right,A(0))),(0,None));checks+=1
        model=p.Presented(2,(0,1),c.Table(((0,None),(None,1))))
        first=named.NamedPresented(model,(0,1));second=named.NamedPresented(model,(1,0))
        self.assertEqual(p.padded(first.model),p.padded(second.model))
        o.certify((named.named_eval(first,E(0)),named.named_eval(second,E(0))),(0,1))
        self.assertFalse(named.named_recoverable((first,second),(0,0)))
        self.assertTrue(named.named_recoverable((first,second),(0,1)));checks+=1
        for tree in o.trees(2,2,2):
            mapped=o.rename(tree,(1,0),(0,1))
            o.certify(named.named_eval(second,mapped),named.named_eval(first,tree));checks+=1
        model=p.Presented(3,(0,2),c.Table(((0,None),(None,1))));am=(1,2,0)
        moved=transport.relabel_presented(model,am)
        o.certify(moved.labels,(0,1))
        for tree in o.trees(3,3,3):
            expected=o.raw(o.pad(3,model.labels,model.table.rows),model.labels,model.labels,tree)
            o.certify(p.raw_eval(moved,o.rename(tree,am,am)),None if expected is None else am[expected]);checks+=1
        COVERAGE['carrier_name_controls']=checks

if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2).result
    print(json.dumps(COVERAGE,sort_keys=True));raise SystemExit(not result.wasSuccessful())
