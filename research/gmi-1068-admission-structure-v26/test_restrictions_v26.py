"""B: every lawful small ambient table and every admission subset, with actual inclusions."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unittest
from support_v26 import core,oracle,actual,unpack
import functors_v26 as functors
import restrictions_v26 as api
COVERAGE={}


class RestrictionTests(unittest.TestCase):
    def test_all_subsets(self):
        counts=dict(ambient_categories=0,admission_cases=0,pattern_00=0,pattern_01=0,pattern_10=0,pattern_11=0,
                    missing_identity_witnesses=0,missing_composite_witnesses=0,restricted_trees=0,
                    restricted_identity_checks=0,restricted_pair_checks=0,proper_wide_subcategories=0)
        for n in range(4):
            for c in oracle.models(n):
                category=actual(c);counts['ambient_categories']+=1
                for mask in range(1<<n):
                    allowed=tuple(f for f in range(n) if mask>>f&1);flags=oracle.admission(c,allowed)
                    counts['admission_cases']+=1;counts['pattern_'+''.join(str(int(b)) for b in flags)]+=1
                    oracle.certify(api.admission_laws(category,allowed),flags)
                    if not all(flags):
                        with self.assertRaises(ValueError):api.wide_restriction(category,allowed)
                        if not flags[0]:
                            self.assertTrue(any(e not in allowed for e in c[3]));counts['missing_identity_witnesses']+=1
                        if not flags[1]:
                            self.assertTrue(any(c[0][f][g] is not None and c[0][f][g] not in allowed
                                                for f in allowed for g in allowed));counts['missing_composite_witnesses']+=1
                        continue
                    expected=oracle.restriction(c,allowed);restricted,inclusion=api.wide_restriction(category,allowed)
                    oracle.certify(unpack(restricted),expected)
                    self.assertEqual(restricted.object_count,category.object_count)
                    oracle.certify(inclusion.object_map,tuple(range(len(c[3]))));oracle.certify(inclusion.arrow_map,allowed)
                    self.assertEqual(inclusion.source,restricted);self.assertEqual(inclusion.target,category)
                    core.old_categories.validate_category(restricted)
                    counts['proper_wide_subcategories']+=len(allowed)<n
                    for o,e in enumerate(expected[3]):
                        self.assertEqual(allowed[e],c[3][o]);counts['restricted_identity_checks']+=1
                    for f in range(len(allowed)):
                        for g in range(len(allowed)):
                            result=expected[0][f][g]
                            self.assertEqual(None if result is None else allowed[result],c[0][allowed[f]][allowed[g]])
                            counts['restricted_pair_checks']+=1
                    for tree in oracle.trees(len(allowed),len(c[3])):
                        expected_response=oracle.evaluate(expected,tree)
                        mapped=oracle.map_tree(tree,inclusion.object_map,allowed)
                        projected=oracle.map_response(expected_response,inclusion.object_map,allowed)
                        oracle.certify(core.trees.typed_eval(restricted,tree),expected_response)
                        oracle.certify(functors.map_tree(inclusion,tree),mapped)
                        oracle.certify(core.trees.typed_eval(category,mapped),projected)
                        counts['restricted_trees']+=1
        self.assertEqual(counts['ambient_categories'],59);self.assertEqual(counts['admission_cases'],439)
        self.assertEqual(sum(counts['pattern_'+p] for p in ('00','01','10','11')),439)
        self.assertGreater(counts['missing_identity_witnesses'],0);self.assertGreater(counts['missing_composite_witnesses'],0)
        COVERAGE.update(counts)
