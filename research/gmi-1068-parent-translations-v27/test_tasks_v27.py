"""Declared interfaces against literal relation composition, with physical premises separate."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from itertools import product
import unittest
from support_v27 import tasks as c, oracle as o, core
COVERAGE={}


class TaskTests(unittest.TestCase):
    def test_relations_pairs_triples_and_interfaces(self):
        raw=o.relations();actual=tuple(c.from_relation(2,r) for r in raw)
        relations=pairs=triples=regular=adjacent=bridges=0
        for r,t in zip(raw,actual):
            o.certify(c.decode(t),r)
            self.assertEqual((t.source,t.target),(o.domain(r),o.image(r)))
            rel=c.as_relation(t)
            decoded=tuple((t.source[i],t.target[j]) for i,row in enumerate(rel.rows) for j in sorted(row))
            self.assertEqual(decoded,r)
            self.assertEqual(c.typed_compose(c.identity_task(2,t.source),t),t)
            self.assertEqual(c.typed_compose(t,c.identity_task(2,t.target)),t);relations+=1
        for i,a in enumerate(actual):
            for j,b in enumerate(actual):
                expected=o.relation_product(raw[i],raw[j]);ok=set(a.target)<=set(b.source)
                self.assertIs(c.regular(a,b),ok);pairs+=1
                joined=c.regular_compose(a,b)
                if ok:
                    o.certify(c.decode(joined),expected)
                    self.assertEqual((joined.source,joined.target),(a.source,b.target))
                    bridge=c.inclusion(a,b)
                    self.assertEqual(bridge.pairs,tuple((x,x) for x in a.target))
                    self.assertEqual(c.typed_compose(c.typed_compose(a,bridge),b),joined)
                    regular+=1;bridges+=1
                else:self.assertIsNone(joined)
                for k,d in enumerate(actual):
                    self.assertEqual(o.relation_product(expected,raw[k]),
                                     o.relation_product(raw[i],o.relation_product(raw[j],raw[k])))
                    triples+=1
                    if ok and set(b.target)<=set(d.source):
                        left=c.regular_compose(joined,d)
                        right=c.regular_compose(a,c.regular_compose(b,d))
                        self.assertEqual(left,right)
                        o.certify(c.decode(left),o.relation_product(expected,raw[k]));adjacent+=1
        self.assertEqual((relations,pairs,triples),(16,256,4096))
        COVERAGE.update(task_relations=relations,task_pairs=pairs,task_triples=triples,
                        regular_task_pairs=regular,adjacent_regular_triples=adjacent,
                        typed_inclusion_bridges=bridges)

    def test_possibility_and_declared_range_control(self):
        funcs=tuple(product(range(2),repeat=2))
        table=tuple(tuple(funcs.index(tuple(g[f[x]] for x in range(2))) for g in funcs) for f in funcs)
        category=core.Typed(1,(0,)*4,(0,)*4,(funcs.index((0,1)),),core.Table(table))
        core.core26.checked_category(category)
        checks=admissible=0
        for mask in range(16):
            allowed=tuple(i for i in range(4) if mask>>i&1)
            closed=True
            for i,j in product(range(4),repeat=2):
                composite=tuple(funcs[j][funcs[i][x]] for x in range(2))
                self.assertEqual(table[i][j],funcs.index(composite))
                if i in allowed and j in allowed and funcs.index(composite) not in allowed:closed=False
                checks+=1
            expected=(1 in allowed,closed)
            self.assertEqual(core.restrictions.admission_laws(category,allowed),expected)
            if all(expected):
                restricted,inclusion=core.restrictions.wide_restriction(category,allowed)
                self.assertEqual(inclusion.arrow_map,allowed)
                self.assertEqual(restricted.object_count,1);admissible+=1
            else:
                with self.assertRaises(ValueError):core.restrictions.wide_restriction(category,allowed)
        self.assertEqual(checks,256)
        self.assertEqual(core.restrictions.admission_laws(category,(0,1,2)),(True,False))
        self.assertEqual(core.restrictions.admission_laws(category,(1,)),(True,True))
        self.assertEqual(table[2][2],1)
        r,s,t=(c.from_relation(5,v) for v in (((0,1),),((1,2),(3,4)),((2,2),)))
        rs=c.regular_compose(r,s)
        self.assertEqual(rs.target,(2,4));self.assertEqual(rs.pairs,((0,2),))
        self.assertIsNone(c.regular_compose(rs,t));self.assertIsNone(c.regular_compose(s,t))
        shrunk=c.from_relation(5,rs.pairs)
        self.assertEqual(c.regular_compose(shrunk,t).pairs,((0,2),))
        self.assertNotEqual(shrunk.target,rs.target)
        COVERAGE.update(possibility_pair_checks=checks,admissible_possibility_subsets=admissible,
                        task_named_controls=3)
