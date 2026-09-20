"""Declared ordered-resource folds versus independent cumulative prefixes."""
from itertools import product
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v21 as oracle
import resources_v21 as resources
COVERAGE={}


class ResourceTests(unittest.TestCase):
    def test_registered_resource_words(self):
        pairs=tuple(product((0,1),repeat=2))
        families=(('nat',(0,1,2),tuple(range(7)),0,280),
                  ('vector',pairs,tuple(product(range(4),repeat=2)),(0,0),1360),
                  ('peak',(0,1,2),(0,1,2),0,120),
                  ('mixed',pairs,tuple(product(range(4),(0,1))),(0,0),680),
                  ('signed',(-2,-1,0,1,2),(-1,0,1,2,3),0,780))
        for kind,alphabet,capacities,zero,expected_count in families:
            count=cuts=nesting=failures=0
            self.assertEqual(resources.identity(kind),zero)
            for a,b,c in product(alphabet,repeat=3):
                self.assertEqual(resources.combine(kind,resources.combine(kind,a,b),c),
                                 oracle.resource(kind,a,oracle.resource(kind,b,c)))
            for length in range(4):
                for word in product(alphabet,repeat=length):
                    prefixes=oracle.prefixes(kind,word,zero);results={}
                    for capacity in capacities:
                        expected=all(oracle.below(spent,capacity) for spent in prefixes)
                        actual=resources.prefix_fold(kind,word,zero,capacity)
                        self.assertEqual(actual,(prefixes,expected));results[capacity]=actual[1]
                        final=oracle.below(prefixes[-1],capacity)
                        if kind=='signed':
                            self.assertEqual(expected,max(prefixes)<=capacity)
                            failures+=int(final!=expected)
                        else:self.assertEqual(final,expected)
                        for cut in range(length+1):
                            first=resources.prefix_fold(kind,word[:cut],zero,capacity)
                            second=resources.prefix_fold(kind,word[cut:],first[0][-1],capacity)
                            self.assertEqual(first[0]+second[0][1:],prefixes)
                            self.assertEqual(first[1] and second[1],expected);cuts+=1
                        count+=1
                    for low,high in product(capacities,repeat=2):
                        self.assertEqual(resources.le(kind,low,high),oracle.below(low,high))
                        if oracle.below(low,high):
                            self.assertTrue(not results[low] or results[high]);nesting+=1
            self.assertEqual(count,expected_count)
            COVERAGE.update({kind+'_prefix_cases':count,kind+'_cut_checks':cuts,
                             kind+'_nesting_checks':nesting,kind+'_final_only_failures':failures})
        self.assertGreater(COVERAGE['signed_final_only_failures'],0)

    def test_noncommutative_positive_costs(self):
        identity=((1,0,0),(0,1,0),(0,0,1))
        a=((1,1,0),(0,1,0),(0,0,1));b=((1,0,0),(0,1,1),(0,0,1))
        multiply=oracle.matrix_product
        ab,ba=multiply(a,b),multiply(b,a)
        self.assertNotEqual(ab,ba)
        below=lambda x,y:all(x[i][j]<=y[i][j] for i,j in product(range(3),repeat=2))
        self.assertTrue(below(identity,a) and below(identity,b))
        self.assertTrue(below(ba,ab));self.assertFalse(below(ab,ba))
        count=0
        for x,y,z in product((identity,a,b,ab,ba),repeat=3):
            self.assertEqual(multiply(multiply(x,y),z),multiply(x,multiply(y,z)))
            self.assertEqual(multiply(identity,x),x);self.assertEqual(multiply(x,identity),x)
            if below(x,y):
                self.assertTrue(below(multiply(z,x),multiply(z,y)))
                self.assertTrue(below(multiply(x,z),multiply(y,z)))
            count+=1
        COVERAGE['noncommutative_matrix_law_cases']=count
        self.assertEqual(count,125)


if __name__=='__main__':
    import json
    r=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not r.result.wasSuccessful())
