"""Malformed table, typed-category and common-query boundaries."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import partial_v19 as partial
import categories_v19 as category
from responses_v19 import Query,observe
COVERAGE={}


class HostileTests(unittest.TestCase):
    def reject(self,cases):
        count=0
        for fn,args in cases:
            with self.subTest(function=fn.__name__,args=args),self.assertRaises(ValueError):fn(*args)
            count+=1
        return count

    def test_table_and_raw_query_validation(self):
        table=partial.Table(((0,None),(None,1)))
        cases=[(partial.Table,(rows,)) for rows in (None,[],[()],((0,),()),([0],),
            ((True,),),((0.0,),),((-1,),),((1,),),((0,1),(1,2)))]
        duck=type('Duck',(),{'rows':((0,),)})()
        for invalid in (None,duck,((0,),)):
            cases.extend((fn,args) for fn,args in (
                (partial.units,(invalid,)),(partial.laws,(invalid,)),(partial.validate,(invalid,)),
                (partial.word,(invalid,(0,))),(partial.empty,(invalid,0)),(partial.relabel,(invalid,(0,)))))
        cases += [(partial.word,(table,arrows)) for arrows in ((),[],[0],(True,),(0.0,),(-1,),
                  (2,),(0,1,True),(0,1,2),None)]
        cases += [(partial.empty,(table,anchor)) for anchor in (True,0.0,-1,2,None)]
        cases += [(partial.relabel,(table,p)) for p in ((),[0,1],(0,0),(0,True),(0,2),None)]
        cases += [(Query,(kind,payload)) for kind,payload in ((True,(0,)),('bad',(0,)),
            ('word',()),('word',[0]),('word',(True,)),('word',(-1,)),('empty',True),
            ('empty',-1),('empty',(0,)),('empty',0.0))]
        cases += [(observe,(table,None)),(observe,(table,Query('word',(2,)))),
                  (observe,(table,Query('empty',2))),(partial.word,(partial.Table(()),())),
                  (partial.empty,(partial.Table(()),0))]
        COVERAGE['table_query_malformed_rejections']=self.reject(cases)
        self.assertIsNone(observe(table,Query('word',(0,1))))
        self.assertEqual(observe(table,Query('word',(0,))),0)
        self.assertIsNone(partial.empty(partial.Table(((None,),)),0))
        COVERAGE['tagged_failure_controls']=3

    def test_typed_structure_and_law_validation(self):
        table=partial.Table(((0,None),(None,1)))
        cat=category.Typed(2,(0,1),(0,1),(0,1),table)
        category.validate_category(cat)
        cases=[(category.Typed,(n,(0,1),(0,1),(0,1),table)) for n in (True,-1,2.0,None)]
        cases += [(category.Typed,(2,s,t,ids,tab)) for s,t,ids,tab in (
            ([0,1],(0,1),(0,1),table),((0,True),(0,1),(0,1),table),
            ((0,1),(0,2),(0,1),table),((0,),(0,1),(0,1),table),
            ((0,1),(0,1),[0,1],table),((0,1),(0,1),(0,),table),
            ((0,1),(0,1),(0,True),table),((0,1),(0,1),(0,2),table),
            ((0,1),(0,1),(0,1),None))]
        malformed=(category.Typed(2,(0,1),(0,1),(1,0),table),
                   category.Typed(1,(0,0),(0,0),(0,),table),
                   category.Typed(1,(0,),(0,),(0,),partial.Table(((None,),))),
                   category.Typed(1,(0,0,0),(0,0,0),(0,),partial.Table(((0,1,2),(1,2,0),(2,0,2)))))
        for bad in malformed:
            cases += [(category.validate_category,(bad,)),(category.flatten,(bad,)),(category.bundles,(bad,))]
        for fn in (category.validate_category,category.flatten,category.bundles,category.reconstruct):
            cases.append((fn,(None,)))
        arrow=(0,0,0)
        cases += [(category.bundled_product,(cat,bad,arrow)) for bad in
                  ([0,0,0],(0,0),(True,0,0),(0,0,False),(0,0,2),(1,0,0),None)]
        COVERAGE['typed_category_malformed_rejections']=self.reject(cases)
        empty=category.Typed(0,(),(),(),partial.Table(()))
        category.validate_category(empty)
        self.assertEqual(category.bundles(empty),())
        self.assertEqual(category.reconstruct(category.flatten(empty)),empty)
        COVERAGE['empty_category_controls']=1


if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
