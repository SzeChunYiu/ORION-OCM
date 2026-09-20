"""Registered A/B: all small tables and independently bracketed response trees."""
from itertools import product
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v25 as o
import core_v25 as c
import trees_v25 as t
COVERAGE={}

class TableTests(unittest.TestCase):
    def test_a_typed_trees(self):
        counts=dict(tables=0,accepted=0,endpoint_certificates=0,typed_trees=0,failed_trees=0,encoded_leaves=0)
        patterns={''.join(bits):0 for bits in product('01',repeat=3)}
        for n in range(4):
            accepted=[];total=0;expected_trees=0
            for rows in o.tables(n):
                flags=o.laws(rows);table=c.Table(rows);counts['tables']+=1;total+=1
                actual=c.old_partial.laws(table)
                self.assertEqual(actual,dict(zip(('associativity','local_units','coherence'),flags)))
                patterns[''.join(str(int(v)) for v in flags)]+=1
                if not all(flags):
                    with self.assertRaises(ValueError):c.old_categories.reconstruct(table)
                    continue
                accepted.append(rows);counts['accepted']+=1
                solutions=o.endpoints(rows);self.assertEqual(len(solutions),1);counts['endpoint_certificates']+=1
                source,target,identities=solutions[0];cat=c.old_categories.reconstruct(table)
                o.certify((cat.source,cat.target,cat.identities),(source,target,identities))
                q=n+len(identities);expected_trees+=q+q*q+2*q**3+5*q**4;actual_trees=0
                for tree in o.trees(n,len(identities),4):
                    expected=o.typed(rows,source,target,identities,tree)
                    o.certify(t.typed_eval(cat,tree),expected);o.certify(t.typed_word(cat,tree),expected)
                    word=o.encoding(tree,identities);o.certify(t.encode_typed(cat,tree),word)
                    raw=c.old_responses.observe(c.old_categories.flatten(cat),c.old_responses.Query('word',word))
                    o.certify(raw,None if expected is None else expected[2])
                    actual_trees+=1;counts['failed_trees']+=expected is None;counts['encoded_leaves']+=len(word)
                self.assertEqual(actual_trees,q+q*q+2*q**3+5*q**4)
                counts['typed_trees']+=actual_trees
            self.assertEqual(tuple(accepted),o.catalog(n))
            COVERAGE[f'a_tables_n{n}']=total;COVERAGE[f'a_accepted_n{n}']=len(accepted)
            COVERAGE[f'a_tree_formula_n{n}']=expected_trees
        self.assertEqual(counts['tables'],262228)
        COVERAGE.update({'a_'+k:v for k,v in counts.items()})
        COVERAGE.update({'a_laws_'+k:v for k,v in patterns.items()})

    def test_b_weakened_tables(self):
        counts=dict(tables=0,raw_trees=0,associative_trees=0,failed_trees=0,nonassoc_witnesses=0)
        for n in range(3):
            for rows in o.tables(n):
                table=c.Table(rows);neutral=o.units(rows);assoc=o.laws(rows)[0];counts['tables']+=1
                for tree in o.trees(n,n,4):
                    expected=o.raw(rows,tuple(range(n)),neutral,tree)
                    o.certify(t.raw_table_eval(table,tree),expected)
                    encoded=o.encoding(tree,tuple(range(n)));guard=o.guard(tree,tuple(range(n)),neutral)
                    o.certify(t.raw_table_encoding(table,tree),(encoded,guard))
                    if assoc:
                        o.certify(t.raw_table_word(table,tree),expected);counts['associative_trees']+=1
                    counts['raw_trees']+=1;counts['failed_trees']+=expected is None
                if not assoc:
                    for x,y,z in product(range(n),repeat=3):
                        left=('seq',('seq',('arrow',x),('arrow',y)),('arrow',z))
                        right=('seq',('arrow',x),('seq',('arrow',y),('arrow',z)))
                        a=o.raw(rows,tuple(range(n)),neutral,left);b=o.raw(rows,tuple(range(n)),neutral,right)
                        if a!=b:
                            o.certify(t.raw_table_eval(table,left),a);o.certify(t.raw_table_eval(table,right),b)
                            self.assertNotEqual(a,b);counts['nonassoc_witnesses']+=1;break
                    else:self.fail('missing associativity witness')
        self.assertEqual((counts['tables'],counts['raw_trees']),(84,115872))
        COVERAGE.update({'b_'+k:v for k,v in counts.items()})

if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2).result
    print(json.dumps(COVERAGE,sort_keys=True));raise SystemExit(not result.wasSuccessful())
