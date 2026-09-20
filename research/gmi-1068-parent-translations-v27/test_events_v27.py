"""Exact event trajectories, units, and coefficient-observation boundaries."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fractions import Fraction as F
import unittest
from support_v27 import events as c, oracle as o, event_data
COVERAGE = {}


class EventTests(unittest.TestCase):
    def test_all_events_pairs_triples(self):
        raw=o.events();actual=tuple(c.Event(*e) for e in raw)
        pairs={};event_count=pair_count=triple_count=0
        for e in actual:
            self.assertEqual(c.compose_event(c.identity_event(e.n),e),e)
            self.assertEqual(c.compose_event(e,c.identity_event(e.m)),e)
            self.assertTrue(all(sum(row)<=1 for row in e.rows));event_count+=1
        for i,a in enumerate(actual):
            for j,b in enumerate(actual):
                if a.m != b.n:continue
                value=c.compose_event(a,b);pairs[i,j]=value
                o.certify(event_data(value),(a.n,b.m,o.trajectory((raw[i],raw[j]))))
                pair_count+=1
        for i,a in enumerate(actual):
            for j,b in enumerate(actual):
                if a.m != b.n:continue
                for k,d in enumerate(actual):
                    if b.m != d.n:continue
                    left=c.compose_event(pairs[i,j],d)
                    right=c.compose_event(a,pairs[j,k])
                    o.certify(event_data(left),(a.n,d.m,o.trajectory((raw[i],raw[j],raw[k]))))
                    self.assertEqual(left,right);triple_count+=1
        self.assertEqual((event_count,pair_count,triple_count),(59,2117,79401))
        COVERAGE.update(events=event_count,event_pairs=pair_count,event_triples=triple_count)

    def test_basis_and_normalized_boundaries(self):
        normalized=basis=controls=0
        for raw in o.events():
            e=c.Event(*raw);is_normal=all(sum(row)==1 for row in raw[2])
            self.assertIs(c.normalized(e),is_normal)
            if is_normal:
                k=c.to_kernel(e)
                self.assertEqual(c.from_kernel(k),e);normalized+=1
            else:
                with self.assertRaises(ValueError):c.to_kernel(e)
            for i in range(e.n):
                prep=c.Event(1,e.n,(tuple(F(j==i) for j in range(e.n)),))
                for j in range(e.m):
                    effect=c.Event(e.m,1,tuple((F(k==j),) for k in range(e.m)))
                    self.assertEqual(c.compose_event(c.compose_event(prep,e),effect).rows,((e.rows[i][j],),))
                    basis+=1
        half=c.Event(1,1,((F(1,2),),))
        self.assertEqual(c.compose_event(half,half).rows,((F(1,4),),));controls+=1
        self.assertNotEqual(half,c.identity_event(1));controls+=1
        self.assertEqual(c.Event(1,0,((),)).rows,((),));controls+=1
        self.assertEqual(c.to_kernel(c.Event(0,2,())).m,2);controls+=1
        COVERAGE.update(normalized_events=normalized,basis_extractions=basis,event_boundary_controls=controls)
