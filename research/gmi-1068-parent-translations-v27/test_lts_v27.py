"""Actual fixed-label path maps and all lifts against independent state walks."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from itertools import product
import unittest
from support_v27 import lts as c, oracle as o
COVERAGE = {}


class LTSTests(unittest.TestCase):
    def test_primary_maps_paths_and_lifts(self):
        counts = dict(candidate_maps=0, forward_maps=0, back_maps=0, hom_maps=0,
                      mapped_source_paths=0, path_composition_pairs=0,
                      target_path_queries=0, source_lifts=0)
        for n, m in product(range(3), repeat=2):
            for source in o.systems(n):
                for target in o.systems(m):
                    a, b = c.LTS(*source), c.LTS(*target)
                    for mapping in product(range(m), repeat=n):
                        counts['candidate_maps'] += 1
                        forward, back = o.clauses(source, target, mapping)
                        self.assertIs(c.forward(a, b, mapping), forward)
                        self.assertIs(c.back(a, b, mapping), back)
                        self.assertIs(c.hom(a, b, mapping), forward and back)
                        for key, flag in (('forward_maps', forward), ('back_maps', back),
                                          ('hom_maps', forward and back)):
                            counts[key] += flag
                        for state in range(n):
                            self.assertEqual(c.successors(a, state),
                                             tuple((label, t) for s, label, t in source[2] if s == state))
                        if not forward:
                            continue
                        paths = o.paths(source)
                        for path in paths:
                            expected = o.mapped(source, target, mapping, path)
                            o.certify(c.map_path(a, b, mapping, path), expected)
                            self.assertEqual(c.endpoint(a, path), o.endpoint(source, path))
                            self.assertEqual(c.endpoint(b, expected), mapping[o.endpoint(source, path)])
                            self.assertEqual(c.labels(a, path), o.path_labels(source, path))
                            self.assertEqual(c.labels(b, expected), c.labels(a, path))
                            counts['mapped_source_paths'] += 1
                            for second in paths:
                                if len(path[1]) + len(second[1]) > 3 or o.endpoint(source, path) != second[0]:
                                    continue
                                joined = path[0], path[1] + second[1]
                                o.certify(c.compose_paths(a, path, second), joined)
                                self.assertEqual(c.map_path(a, b, mapping, joined),
                                    c.compose_paths(b, expected, c.map_path(a, b, mapping, second)))
                                counts['path_composition_pairs'] += 1
                        if back:
                            for state in range(n):
                                for path in o.paths(target):
                                    if path[0] != mapping[state]:
                                        continue
                                    expected = o.lifts(source, target, mapping, state, path)
                                    self.assertTrue(expected)
                                    o.certify(c.lift_path(a, b, mapping, state, path), expected)
                                    counts['target_path_queries'] += 1
                                    counts['source_lifts'] += len(expected)
        self.assertEqual(counts['candidate_maps'], 1143)
        COVERAGE.update(counts)

    def test_named_observation_boundaries(self):
        count = 0
        for source, target, mapping in (((1,1,()), (1,1,((0,0,0),)), (0,)),
              ((1,1,((0,0,0),)), (2,1,((0,0,0),(0,0,1))), (0,))):
            a,b=c.LTS(*source),c.LTS(*target)
            self.assertTrue(c.forward(a,b,mapping));self.assertFalse(c.back(a,b,mapping))
            self.assertFalse(c.hom(a,b,mapping))
            with self.assertRaises(ValueError):c.lift_path(a,b,mapping,0,(0,()))
            count+=1
        a=c.LTS(1,2,((0,0,0),));b=c.LTS(1,2,((0,1,0),))
        self.assertFalse(c.forward(a,b,(0,)));count+=1
        renamed=c.LTS(1,2,tuple((s,1-label,t) for s,label,t in a.edges))
        self.assertTrue(c.hom(renamed,b,(0,)))
        self.assertEqual(c.map_path(renamed,b,(0,),(0,(0,0))), (0,(0,0)));count+=1
        left=(4,3,((0,0,1),(1,1,2),(1,2,3)))
        right=(5,3,((0,0,1),(0,0,2),(1,1,3),(2,2,4)))
        a,b=c.LTS(*left),c.LTS(*right)
        traces=lambda raw,model:{c.labels(model,p) for p in o.paths(raw) if p[0]==0}
        self.assertEqual(traces(left,a), traces(right,b))
        self.assertFalse(o.bisimilar(left,right));count+=1
        COVERAGE['lts_named_controls']=count
