"""Named failure mechanisms distinguish signature erasure from information loss."""
from itertools import product
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v19 as oracle
import partial_v19 as partial
import categories_v19 as category
COVERAGE={}


class WitnessTests(unittest.TestCase):
    def test_law_independence_and_definedness(self):
        coherence=((0,1),(1,None))
        self.assertEqual(oracle.laws(coherence),(True,True,False,True))
        self.assertEqual(partial.laws(partial.Table(coherence)),
                         {'associativity':True,'local_units':True,'coherence':False})
        self.assertIsNone(coherence[coherence[1][0]][1])
        nonassoc=((0,1,2),(1,2,0),(2,0,2))
        self.assertEqual(oracle.laws(nonassoc)[:3],(False,True,True))
        self.assertNotEqual(nonassoc[nonassoc[1][1]][2],nonassoc[1][nonassoc[1][2]])
        weak=((0,None,2),(None,1,2),(2,None,2))
        self.assertEqual(oracle.laws(weak),(False,True,True,True))
        self.assertEqual(oracle.units(weak),(0,1))
        self.assertIsNone(oracle.typed_reconstruction(weak))
        self.assertIsNone(weak[0][1])
        self.assertEqual(weak[0][weak[1][2]],2)
        for rows in (coherence,nonassoc,weak):
            with self.assertRaises(ValueError):category.reconstruct(partial.Table(rows))
        projections=0
        for rows,expected in ((((0,0),(1,1)),((),(0,1))),(((0,1),(0,1)),((0,1),()))):
            left=tuple(e for e in range(2) if all(rows[e][x]==x for x in range(2)))
            right=tuple(e for e in range(2) if all(rows[x][e]==x for x in range(2)))
            self.assertEqual((left,right),expected)
            self.assertEqual(oracle.laws(rows)[:3],(True,False,True))
            self.assertEqual(partial.units(partial.Table(rows)),())
            projections+=1
        COVERAGE.update(coherence_isolation_controls=1,associativity_isolation_controls=1,
                        weak_definedness_isolation_controls=1,one_sided_identity_controls=projections)

    def test_minimal_nonassociative_unital_size(self):
        tables=unital=0
        for n in range(3):
            for flat in product(range(n),repeat=n*n):
                rows=tuple(tuple(flat[i*n+j] for j in range(n)) for i in range(n))
                tables+=1
                if oracle.units(rows):
                    self.assertTrue(oracle.laws(rows)[0])
                    self.assertTrue(partial.laws(partial.Table(rows))['associativity'])
                    unital+=1
        self.assertEqual((tables,unital),(18,5))
        COVERAGE.update(small_total_magmas=tables,small_unital_associative_magmas=unital)

    def test_information_loss_and_nonunital_morphism(self):
        discrete=partial.Table(((0,None),(None,1)))
        monoid=partial.Table(((0,1),(1,1)))
        filled=lambda table:tuple(tuple(1 if x is None else x for x in row) for row in table.rows)
        self.assertEqual(filled(discrete),filled(monoid))
        self.assertEqual((category.reconstruct(discrete).object_count,category.reconstruct(monoid).object_count),(2,1))
        self.assertIsNone(partial.word(discrete,(0,1)))
        self.assertEqual(partial.word(monoid,(0,1)),1)
        tagged=lambda table:tuple(tuple(('NONE',) if x is None else ('SOME',x) for x in row) for row in table.rows)
        self.assertNotEqual(tagged(discrete),tagged(monoid))
        cyclic=partial.Table(tuple(tuple((x+y)%4 for y in range(4)) for x in range(4)))
        klein=partial.Table(tuple(tuple(x^y for y in range(4)) for x in range(4)))
        for table in (cyclic,klein):
            partial.validate(table)
            self.assertEqual(partial.units(table),(0,))
            self.assertTrue(all(x is not None for row in table.rows for x in row))
        self.assertEqual((partial.word(cyclic,(1,1)),partial.word(klein,(1,1))),(2,0))
        source=partial.Table(((0,),))
        image=lambda _:1
        self.assertEqual(image(source.rows[0][0]),monoid.rows[image(0)][image(0)])
        self.assertNotIn(image(partial.units(source)[0]),partial.units(monoid))
        COVERAGE.update(filled_definedness_collision_controls=1,fresh_bottom_retention_controls=1,
                        composite_value_loss_controls=1,nonunital_multiplicative_map_controls=1)


if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
