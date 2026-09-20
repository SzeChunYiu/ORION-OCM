"""Every labelled test and paired outcome, including zero-probability events."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fractions import Fraction as F
import unittest
from support_v27 import events as e, tests as c, oracle as o, test_data
COVERAGE={}


class LabelledTests(unittest.TestCase):
    def test_all_labelled_tests_and_pairs(self):
        raw=o.tests()
        actual=tuple(c.Test(n,m,tuple((label,e.Event(*event)) for label,event in outcomes))
                     for n,m,outcomes in raw)
        tests=pairs=components=controls=0
        for item,expected in zip(actual,raw):
            o.certify(test_data(item),expected)
            self.assertEqual(c.aggregate(item).rows,o.aggregate(expected));tests+=1
        for i,a in enumerate(actual):
            for j,b in enumerate(actual):
                if a.m!=b.n:continue
                joined=c.compose_test(a,b)
                expected=tuple(((x,y),(a.n,b.m,o.trajectory((u,v))))
                               for x,u in raw[i][2] for y,v in raw[j][2])
                o.certify(test_data(joined),(a.n,b.m,expected))
                self.assertEqual(c.aggregate(joined).rows,o.trajectory(
                    ((a.n,a.m,o.aggregate(raw[i])),(b.n,b.m,o.aggregate(raw[j])))))
                pairs+=1;components+=len(joined.outcomes)
        self.assertEqual((tests,pairs,components),(125,12271,49084))
        zero=e.Event(1,1,((F(0),),));one=e.identity_event(1);half=e.Event(1,1,((F(1,2),),))
        a=c.Test(1,1,((0,one),(1,zero)));b=c.Test(1,1,((0,half),(1,half)))
        self.assertEqual(c.aggregate(a),c.aggregate(b));self.assertNotEqual(a,b);controls+=1
        self.assertEqual(tuple(x for x,_ in c.compose_test(a,a).outcomes),((0,0),(0,1),(1,0),(1,1)));controls+=1
        left=c.compose_test(c.compose_test(a,a),a);right=c.compose_test(a,c.compose_test(a,a))
        self.assertNotEqual(tuple(x for x,_ in left.outcomes),tuple(x for x,_ in right.outcomes))
        self.assertEqual(tuple((((i,j),k),v) for (i,(j,k)),v in right.outcomes),left.outcomes);controls+=1
        self.assertEqual(c.aggregate(c.Test(0,2,())).rows,());controls+=1
        with self.assertRaises(ValueError):c.Test(1,1,())
        controls+=1
        COVERAGE.update(labelled_tests=tests,test_pairs=pairs,paired_outcome_events=components,
                        labelled_test_controls=controls)
