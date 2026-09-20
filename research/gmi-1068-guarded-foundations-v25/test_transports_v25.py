"""Registered C: both alphabets and actual output bundles commute separately."""
from itertools import permutations
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v25 as o
import core_v25 as c
import syntax_v25 as syntax
import trees_v25 as trees
import transports_v25 as transport
COVERAGE={}

class TransportTests(unittest.TestCase):
    def test_c_separate_permutations(self):
        counts=dict(categories=0,arrow_permutations=0,object_permutations=0,query_comparisons=0,inverse_queries=0,inverse_categories=0)
        formula=0
        for n in range(4):
            for rows in o.catalog(n):
                cat=c.old_categories.reconstruct(c.Table(rows));source,target,identities=o.endpoints(rows)[0]
                k=len(identities);q=n+k;counts['categories']+=1
                maps=[(am,tuple(range(k)),'arrow') for am in permutations(range(n))]
                maps += [(tuple(range(n)),om,'object') for om in permutations(range(k))]
                for am,om,kind in maps:
                    counts[kind+'_permutations']+=1;formula+=q+q*q
                    mapped=transport.relabel_category(cat,am,om)
                    expected_rows=o.relabel(rows,am);a_inverse=tuple(am.index(i) for i in range(n))
                    o_inverse=tuple(om.index(i) for i in range(k))
                    expected_source=tuple(om[source[a_inverse[i]]] for i in range(n))
                    expected_target=tuple(om[target[a_inverse[i]]] for i in range(n))
                    expected_ids=tuple(am[identities[o_inverse[i]]] for i in range(k))
                    o.certify((mapped.table.rows,mapped.source,mapped.target,mapped.identities),
                              (expected_rows,expected_source,expected_target,expected_ids))
                    restored=transport.relabel_category(mapped,a_inverse,o_inverse)
                    o.certify((restored.table.rows,restored.source,restored.target,restored.identities),(rows,source,target,identities))
                    counts["inverse_categories"]+=1
                    for tree in o.trees(n,k,2):
                        renamed=o.rename(tree,om,am);o.certify(syntax.map_tree(tree,om,am),renamed)
                        expected=o.typed(rows,source,target,identities,tree)
                        shifted=None if expected is None else (om[expected[0]],om[expected[1]],am[expected[2]])
                        o.certify(transport.map_response(cat,expected,am,om),shifted)
                        o.certify(trees.typed_eval(mapped,renamed),shifted)
                        o.certify(trees.typed_word(mapped,renamed),shifted)
                        o.certify(syntax.map_tree(renamed,o_inverse,a_inverse),tree)
                        counts['query_comparisons']+=1;counts['inverse_queries']+=1
        self.assertEqual(counts['query_comparisons'],formula)
        COVERAGE.update(counts)

if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2).result
    print(json.dumps(COVERAGE,sort_keys=True));raise SystemExit(not result.wasSuccessful())
