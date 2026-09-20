"""Independent common-ID intersections and actual partial loss contexts."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v24 as o
import core_v24 as core
import plans_v24 as p
COVERAGE={}


def certify(test,table,history,threshold):
    context,decoder=p.plan_context(table,history)
    n=len(table.ids);values=table.losses[history];admitted=table.admitted[history];defined=table.defined[history]
    test.assertEqual((context.n,context.m),(n,n));test.assertEqual(decoder,tuple(zip(table.ids,values)))
    test.assertTrue(all(type(loss) is F for _,loss in decoder))
    test.assertEqual((context.admitted,context.defined),(admitted,defined))
    test.assertEqual(context.values,tuple(i if defined[i] else None for i in range(n)))
    test.assertEqual(context.order,tuple(tuple(y<=x for y in values) for x in values))
    o.verify_context(context,decoder,admitted,defined,tuple(tuple(y<=x for y in values) for x in values),tuple(zip(table.ids,values)))
    for i in range(n):
        expected=('ILLEGAL',None) if not admitted[i] else ('UNDEFINED',None) if not defined[i] else ('VALUE',i)
        test.assertEqual(core.observe(context,i),expected)
    expected=o.feasible(table.ids,admitted,defined,values,threshold)
    o.verify_plan_ids(p.feasible_ids(table,history,threshold),expected)
    return expected


class PlanTests(unittest.TestCase):
    def test_boolean_relations(self):
        counts=dict(relations=0,subfamily_cases=0,feasible_contexts=0,decoded_observations=0)
        for h in range(4):
            for n in range(4):
                ids=tuple(f'p{i}' for i in range(n))
                for bits in product((False,True),repeat=h*n):
                    matrix=tuple(tuple(bits[row*n:(row+1)*n]) for row in range(h))
                    table=p.PlanTable(ids,matrix,tuple((True,)*n for _ in range(h)),tuple((F(0),)*n for _ in range(h)))
                    sets=tuple(tuple(ids[i] for i in range(n) if matrix[row][i]) for row in range(h))
                    for row in range(h):
                        self.assertEqual(certify(self,table,row,F(0)),sets[row])
                        counts['feasible_contexts']+=1;counts['decoded_observations']+=n
                    for selected in o.subsets(range(h)):
                        o.verify_plan_ids(p.common_plans(table,selected,F(0)),o.common(ids,sets,selected))
                        counts['subfamily_cases']+=1
                    counts['relations']+=1
        self.assertEqual((counts['relations'],counts['subfamily_cases']),(689,5054))
        COVERAGE.update({'relation_'+k:v for k,v in counts.items()})

    def test_partial_loss_tables(self):
        counts=dict(tables=0,threshold_cases=0,subfamily_cases=0,feasible_contexts=0,decoded_observations=0,feasible_ids=0)
        options=tuple(product((False,True),(False,True),(F(0),F(1))))
        for h in range(3):
            for n in range(3):
                ids=tuple(f'p{i}' for i in range(n))
                for cells in product(options,repeat=h*n):
                    fields=tuple(tuple(tuple(cells[row*n+i][field] for i in range(n)) for row in range(h)) for field in range(3))
                    table=p.PlanTable(ids,*fields);counts['tables']+=1
                    for threshold in (F(0),F(1)):
                        sets=[]
                        for row in range(h):
                            result=certify(self,table,row,threshold);sets.append(result)
                            counts['feasible_contexts']+=1;counts['decoded_observations']+=n;counts['feasible_ids']+=len(result)
                        for selected in o.subsets(range(h)):
                            o.verify_plan_ids(p.common_plans(table,selected,threshold),o.common(ids,sets,selected));counts['subfamily_cases']+=1
                        counts['threshold_cases']+=1
        self.assertEqual((counts['tables'],counts['threshold_cases']),(4237,8474))
        COVERAGE.update({'partial_'+k:v for k,v in counts.items()})


if __name__=='__main__':
    import json
    run=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not run.result.wasSuccessful())
