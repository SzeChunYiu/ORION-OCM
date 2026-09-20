"""Named losses of identity, provenance, frontier and common-plan information."""
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v24 as o
import af_model_v24 as af
import profiles_v24 as p
import preferences_v24 as pref
import plans_v24 as plan
from test_profiles_v24 import certify
COVERAGE={}

class ControlTests(unittest.TestCase):
    def test_profile_boundaries(self):
        checks=0
        def graph(rows,tags):return af.AFGraph(rows,tuple(tags.items()))
        # Same action and terminal: old projection agrees, full edge identities differ.
        g=graph(((('a',2),('a',2)),(),(),()),{'a':(o.OBS,)})
        certify(g,0,2,3,self)
        full=p.full_profiles(g,0,2,1)
        self.assertEqual(full[1][1],full[2][1]);self.assertNotEqual(full[1][0],full[2][0]);checks+=1
        # Same action word, different terminals: no function from words to edge paths.
        g=graph(((('a',1),('a',2)),(),(),()),{'a':(o.OBS,)})
        certify(g,0,2,3,self)
        full=p.full_profiles(g,0,2,1)
        self.assertEqual(full[1][1]['history'],full[2][1]['history'])
        self.assertNotEqual(full[1][1]['machine'],full[2][1]['machine']);checks+=1
        g=graph(((None,('a',2)),(),(),()),{'a':(o.COMPUTE,)})
        certify(g,0,2,3,self);self.assertEqual(p.edge_histories(g,0,1)[1][1],((0,1),));checks+=1
        # Queue ordering is observable through the saved action and provenance.
        g=graph(((('a',2),('b',2)),(),(),()),{'a':(o.OBS,),'b':(o.ORACLE,)})
        r=graph((tuple(reversed(g.rows[0])),(),(),()),dict(g.provenance))
        certify(g,0,2,3,self);certify(r,0,2,3,self)
        self.assertNotEqual(p.selected_profiles(g,0,2),p.selected_profiles(r,0,2));checks+=1
        # A loop repeats event occurrences, but old resource coordinates are indicators.
        g=graph(((('a',0),),(),(),()),{'a':(o.OBS,o.OBS)})
        certify(g,0,0,3,self)
        loop=p.profile_for(g,0,0,((0,0),(0,0),(0,0)))
        self.assertEqual(loop['resources']['external_observations'],1)
        self.assertEqual(loop['resources']['development_steps'],3)
        self.assertEqual(len(p.selected_profiles(g,0,0)),1)
        self.assertEqual(len(p.full_profiles(g,0,0,3)),4);checks+=1
        g=graph(((('a',2),),(),(),()),{'a':(o.COMPUTE,)})
        self.assertEqual(len(p.full_profiles(g,0,2,0)),1)
        self.assertEqual(len(p.selected_profiles(g,0,2)),2);checks+=1
        COVERAGE['profile_boundary_controls']=checks

    def test_preference_boundaries(self):
        checks=0
        rows=(('z',(F(0),F(0)),True,True),('a',(F(0),F(0)),True,True),
              ('u',(F(0),F(1)),True,False))
        c=pref.Candidates(tuple(r[0] for r in rows),tuple(r[1] for r in rows),
                          tuple(r[2] for r in rows),tuple(r[3] for r in rows),2)
        self.assertEqual(pref.preference(c,(F(1),F(1)))['scalar_argmin'],['a','z']);checks+=1
        self.assertEqual(o.preference(rows,(F(1),F(0)),False)['scalar_argmin'],['a','u','z']);checks+=1
        self.assertEqual(o.preference(rows,(F(1),F(-1)),False)['scalar_argmin'],['u']);checks+=1
        crossing=(('a',(F(0),F(1)),True,True),('b',(F(1),F(0)),True,True))
        self.assertNotIn((F(0),F(0)),tuple(r[1] for r in crossing))
        self.assertEqual(o.preference(crossing,(F(1),F(1)),True)['pareto_front'],['a','b']);checks+=1
        hidden=pref.Candidates(('x',),((F(0),F(0)),),(True,),(False,),2)
        self.assertEqual(pref.preference(hidden,(F(1),F(1)))['terminal'],'NO_VIABLE_MORPHOLOGY')
        self.assertEqual(pref.preference(hidden,(F(1),F(1)),False)['scalar_argmin'],['x']);checks+=1
        COVERAGE['preference_boundary_controls']=checks

    def test_plan_boundaries(self):
        checks=0
        ids=('c','a','b');admit=((False,True,True),(True,False,True),(True,True,False))
        t=plan.PlanTable(ids,admit,((True,)*3,)*3,((F(0),)*3,)*3)
        for pair in ((0,1),(0,2),(1,2)):self.assertTrue(plan.common_plans(t,pair,F(0)));checks+=1
        self.assertEqual(plan.common_plans(t,(0,1,2),F(0)),());checks+=1
        self.assertEqual(plan.common_plans(t,(),F(0)),('a','b','c'));checks+=1
        t=plan.PlanTable(('a','b'),((True,False),(False,True)),((True,True),)*2,((F(0),F(0)),)*2)
        self.assertEqual(plan.common_plans(t,(0,1),F(0)),())
        self.assertEqual(tuple(x[1] for x in plan.plan_context(t,0)[1]),tuple(x[1] for x in plan.plan_context(t,1)[1]));checks+=1
        rename={'a':'Z','b':'Y'}
        mapped=plan.PlanTable(tuple(rename[x] for x in t.ids),t.admitted,t.defined,t.losses)
        for selected in o.subsets((0,1)):
            self.assertEqual(plan.common_plans(mapped,selected,F(0)),tuple(sorted(rename[x] for x in plan.common_plans(t,selected,F(0)))));checks+=1
        self.assertNotIn('unused',plan.common_plans(mapped,(),F(0)));checks+=1
        empty=plan.PlanTable((),(),(),());self.assertEqual(plan.common_plans(empty,(),F(0)),());checks+=1
        COVERAGE['plan_boundary_controls']=checks

if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2).result
    print(json.dumps(COVERAGE,sort_keys=True));raise SystemExit(not result.wasSuccessful())
