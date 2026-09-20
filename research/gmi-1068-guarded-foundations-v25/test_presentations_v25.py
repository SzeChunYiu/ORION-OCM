"""Registered D: absent ambient labels and genuine subtype units remain observable."""
from math import comb
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v25 as o
import core_v25 as c
import presentations_v25 as p
COVERAGE={}

class PresentationTests(unittest.TestCase):
    def test_d_ambient_trees(self):
        counts=dict(models=0,padded_cells=0,ambient_trees=0,successful_trees=0,guarded_subtype_folds=0,absent_singletons=0)
        for n in range(4):
            models=queries=0
            for labels,rows in o.presented(n):
                model=p.Presented(n,labels,c.Table(rows));pad=o.pad(n,labels,rows)
                neutral=tuple(labels[i] for i in o.units(rows));models+=1;counts['models']+=1
                o.certify(p.padded(model).rows,pad);counts['padded_cells']+=n*n
                o.certify(p.core_signature(model),(labels,pad))
                o.certify(p.carrier_from_table(model),tuple(i for i,row in enumerate(pad) if any(x is not None for x in row)))
                self.assertEqual(labels,p.carrier_from_table(model));self.assertEqual(o.units(pad),neutral)
                for x in range(n):
                    actual=p.raw_eval(model,('arrow',x));o.certify(actual,x if x in labels else None)
                    counts['absent_singletons']+=x not in labels
                for tree in o.trees(n,n,3):
                    expected=o.raw(pad,labels,neutral,tree)
                    o.certify(p.raw_eval(model,tree),expected);o.certify(p.guarded_word(model,tree),expected)
                    if o.guard(tree,labels,neutral):
                        localword=tuple(labels.index(x) for x in o.encoding(tree,tuple(range(n))))
                        value=c.old_partial.word(model.table,localword)
                        o.certify(None if value is None else labels[value],expected)
                        counts['guarded_subtype_folds']+=1
                    counts['successful_trees']+=expected is not None
                    queries+=1;counts['ambient_trees']+=1
            formula=sum(comb(n,s)*len(o.catalog(s)) for s in range(n+1))
            self.assertEqual(models,formula);self.assertEqual(queries,models*(2*n+(2*n)**2+2*(2*n)**3))
            COVERAGE[f'models_n{n}']=models;COVERAGE[f'trees_n{n}']=queries
        COVERAGE.update(counts)

if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2).result
    print(json.dumps(COVERAGE,sort_keys=True));raise SystemExit(not result.wasSuccessful())
