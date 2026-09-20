"""Invalid unused fields and independent certificates against coherent output edits."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import af_model_v24 as af
import profiles_v24 as p
import preferences_v24 as pref
import plans_v24 as plan
import oracle_v24 as o
COVERAGE={}

class HostileTests(unittest.TestCase):
    def test_input_rejections(self):
        blank=((),)*4;tags=(('a',(o.COMPUTE,)),)
        graph=af.AFGraph(((('a',0),None),(),(),()),tags)
        c=pref.Candidates(('a',),((F(0),F(1)),),(True,),(True,),2)
        t=plan.PlanTable(('a',),((True,),),((True,),),((F(0),),))
        cases=[]
        for rows in (None,[],(),((),)*3,([],(),(),()),((),(),(),(('a',True),)),
                     ((),(),(),(('a',4),)),((),(),(),(('',0),)),((),(),(),(['a',0],))):
            cases.append(lambda rows=rows:af.AFGraph(rows,tags))
        for provenance in (None,[],(('a',()),),(('a',['ENDOGENOUS_COMPUTE']),),
                           (('a',(o.COMPUTE,)),('a',(o.OBS,))),
                           (('unused',('UNKNOWN',)),),(('',(o.COMPUTE,)),),((True,(o.COMPUTE,)),)):
            cases.append(lambda provenance=provenance:af.AFGraph(blank,provenance))
        cases.append(lambda:af.AFGraph(((('missing',0),),(),(),()),()))
        for bad in (True,0.0,-1,4,None):
            cases.extend((lambda bad=bad:p.selected_profiles(graph,bad,0),lambda bad=bad:p.selected_context(graph,0,bad)))
        for bad in (True,1.0,-1,None):cases.append(lambda bad=bad:p.edge_histories(graph,0,bad))
        for path in ([],((0,1),),((0,True),),((True,0),),((0,0),(1,0)),((0,0),('x',0)),((0,0),(0,9))):
            cases.append(lambda path=path:p.profile_for(graph,0,0,path))
        for bad in (None,SimpleNamespace(rows=blank,provenance=())):
            cases.append(lambda bad=bad:p.full_context(bad,0,0,0))
        for ids in ([],('',),('x','x'),(True,)):
            cases.append(lambda ids=ids:pref.Candidates(ids,(),(),(),2))
            cases.append(lambda ids=ids:plan.PlanTable(ids,(),(),()))
        for bad in (True,2.0,0,-1,None):cases.append(lambda bad=bad:pref.Candidates((),(),(),(),bad))
        for resources in (([F(0),F(1)],),((F(0),),),((0,F(1)),),((False,F(1)),),((0.0,F(1)),),((F(-1),F(1)),)):
            cases.append(lambda resources=resources:pref.Candidates(('a',),resources,(False,),(False,),2))
        for flags in ((1,),(None,),[True],()):
            cases.append(lambda flags=flags:pref.Candidates(('a',),((F(0),F(0)),),flags,(False,),2))
        for weights in ([],(),(F(0),F(1)),(F(-1),F(1)),(1,F(1)),(True,F(1)),(1.0,F(1))):
            cases.extend((lambda weights=weights:pref.preference(c,weights),
                          lambda weights=weights:pref.preference(pref.Candidates((),(),(),(),2),weights)))
        for bad in (0,1,None):cases.append(lambda bad=bad:pref.resource_context(c,bad))
        for bad in (True,0.0,None):cases.append(lambda bad=bad:plan.feasible_ids(t,0,bad))
        for histories in ([],(0,0),(True,),(1,),(0,False)):
            cases.append(lambda histories=histories:plan.common_plans(t,histories,F(0)))
        for losses in (((0,),),((False,),),((0.0,),),([F(0)],),()):
            cases.append(lambda losses=losses:plan.PlanTable(('a',),((False,),),((False,),),losses))
        cases.extend((lambda:plan.PlanTable(('a',),((1,),),((True,),),((F(0),),)),
                      lambda:plan.common_plans(plan.PlanTable((),(),(),()),(),0),
                      lambda:plan.plan_context(t,True),lambda:plan.feasible_ids(None,0,F(0)),
                      lambda:pref.preference(None,(F(1),F(1)))))
        rejected=0
        for number,call in enumerate(cases):
            with self.subTest(number=number),self.assertRaises(ValueError):call()
            rejected+=1
        COVERAGE['malformed_input_rejections']=rejected

    def test_independent_semantic_certificates(self):
        expected=o.profile('ID',('a',),{'a':(o.OBS,)},'ID')
        g=af.AFGraph(((('a',2),),(),(),()),(('a',(o.OBS,)),))
        self.assertTrue(o.verify_raw(p.profile_for(g,0,2,((0,0),)),expected));rejected=0;valid=1
        changes=(('machine','C0'),('history',['b']),('history',[]),('provenance',[o.INITIAL]),
                 ('capability',{'ID_TASK':'0'}),('resources',{'development_steps':1,'external_observations':0,'oracle_queries':0}),
                 ('resources',{'development_steps':True,'external_observations':1,'oracle_queries':0}))
        for key,value in changes:
            bad=deepcopy(expected);bad[key]=value
            with self.assertRaises(ValueError):o.verify_raw(bad,expected)
            rejected+=1
        bad=deepcopy(expected);bad['history']=['b'];bad['provenance']=[o.INITIAL,o.ORACLE]
        bad['resources'].update(external_observations=0,oracle_queries=1)
        with self.assertRaises(ValueError):o.verify_raw(bad,expected)
        rejected+=1
        for bad in ((),('a',),('a','b','c'),['a','b'],('a','a')):
            with self.assertRaises(ValueError):o.verify_plan_ids(bad,('a','b'))
            rejected+=1
        names=('C0','C1','ID','NOT');rows=((None,('a','ID')),(),(),())
        self.assertTrue(o.validate_path(names,rows,'C0',(('C0',1),),'ID',('a',)));valid+=1
        for edges,terminal,actions in (((('C0',0),),'ID',('a',)),((('C0',1),),'C0',('a',)),
                                      ((('C0',1),),'ID',('b',)),((('C0',True),),'ID',('a',))):
            with self.assertRaises(ValueError):o.validate_path(names,rows,'C0',edges,terminal,actions)
            rejected+=1
        c=pref.Candidates(('a','b'),((F(0),F(0)),)*2,(True,True),(True,True),2)
        context,decoder=pref.resource_context(c,True);order=((True,True),)*2
        def cert(ctx,dec):return o.verify_context(ctx,dec,(True,True),(True,True),order,decoder)
        self.assertTrue(cert(context,decoder));valid+=1
        fields={k:getattr(context,k) for k in ('n','m','admitted','defined','values','order')}
        for key,value in (('admitted',(True,False)),('defined',(True,False)),('values',(0,0)),
                          ('order',((True,False),(False,True))),('n',2.0)):
            bad=SimpleNamespace(**dict(fields,**{key:value}))
            with self.assertRaises(ValueError):cert(bad,decoder)
            rejected+=1
        for bad in (decoder[:1],tuple(reversed(decoder)),(('a',(0,0)),('b',(F(0),F(0))))):
            with self.assertRaises(ValueError):cert(context,bad)
            rejected+=1
        expected_selection=o.preference((('a',(F(0),F(0)),True,True),('b',(F(0),F(0)),True,True)),(F(1),F(1)),True)
        self.assertTrue(o.verify_raw(pref.preference(c,(F(1),F(1))),expected_selection));valid+=1
        for key,value in (('pareto_front',['a']),('scalar_argmin',['b']),('terminal','NO_VIABLE_MORPHOLOGY')):
            bad=deepcopy(expected_selection);bad[key]=value
            with self.assertRaises(ValueError):o.verify_raw(bad,expected_selection)
            rejected+=1
        table=plan.PlanTable(('a','b'),((True,True),),((True,False),),((F(0),F(0)),))
        self.assertTrue(o.verify_plan_ids(plan.feasible_ids(table,0,F(0)),('a',)));valid+=1
        COVERAGE.update(valid_certificate_controls=valid,semantic_mutation_rejections=rejected)

if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2).result
    print(json.dumps(COVERAGE,sort_keys=True));raise SystemExit(not result.wasSuccessful())
