"""Every small labelled resource roster with actual historical and context frontiers."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v24 as o
import core_v24 as core
import preferences_v24 as p
COVERAGE={}


def certify_context(test,rows,mode,context,decoder,weights=None):
    n=len(rows);active=tuple(viable and (reachable or not mode) for _,_,viable,reachable in rows)
    wanted=tuple((label,vector if weights is None else sum((x*w for x,w in zip(vector,weights)),F(0))) for label,vector,_,_ in rows)
    test.assertEqual(decoder,wanted);test.assertEqual((context.n,context.m),(n,n))
    test.assertEqual(context.admitted,active);test.assertEqual(context.defined,(True,)*n)
    test.assertEqual(context.values,tuple(range(n)))
    if weights is None:order=tuple(tuple(all(y<=x for x,y in zip(v,w)) for _,w in wanted) for _,v in wanted)
    else:order=tuple(tuple(w<=v for _,w in wanted) for _,v in wanted)
    o.verify_context(context,decoder,active,(True,)*n,order,wanted)
    test.assertEqual(context.order,order)
    for i in range(n):test.assertEqual(core.observe(context,i),('VALUE',i) if active[i] else ('ILLEGAL',None))
    indices=tuple(i for i in range(n) if active[i])
    test.assertEqual(core.frontier.attained(context,tuple(range(n))),indices)
    maxima=core.frontier.maximal(order,indices)
    return tuple(sorted(decoder[i][0] for i in maxima))


class PreferenceTests(unittest.TestCase):
    def test_exhaustive(self):
        counts=dict(rosters=0,selection_calls=0,parent_function_calls=0,context_instances=0,context_observations=0,pareto_ids=0,scalar_ids=0)
        vectors=tuple(product((F(0),F(1)),repeat=2));options=tuple(product(vectors,(False,True),(False,True)))
        prices=tuple(product((F(1),F(2)),repeat=2))
        for n in range(4):
            for chosen in product(options,repeat=n):
                rows=tuple((f'i{i}',v,a,b) for i,(v,a,b) in enumerate(chosen));counts['rosters']+=1
                model=p.Candidates(tuple(x[0] for x in rows),tuple(x[1] for x in rows),tuple(x[2] for x in rows),tuple(x[3] for x in rows),2)
                old=tuple(core.old_choice.Candidate(*row) for row in rows)
                for mode in (False,True):
                    active=core.old_choice.viable_set(old,reachable_only=mode);counts['parent_function_calls']+=1
                    context,decoder=p.resource_context(model,mode)
                    frontier=certify_context(self,rows,mode,context,decoder)
                    self.assertEqual(frontier,core.old_choice.pareto_front(active));counts['parent_function_calls']+=1
                    counts['context_instances']+=1;counts['context_observations']+=n
                    for weights in prices:
                        expected=o.preference(rows,weights,mode)
                        actual=p.preference(model,weights,mode);o.verify_raw(actual,expected)
                        o.verify_raw(core.old_choice.selection_record(old,weights,reachable_only=mode),expected)
                        counts['parent_function_calls']+=1
                        self.assertEqual(core.old_choice.scalar_argmin(active,weights),tuple(expected['scalar_argmin']))
                        counts['parent_function_calls']+=1
                        scalar_ctx,scalar_decoder=p.scalar_context(model,weights,mode)
                        winners=certify_context(self,rows,mode,scalar_ctx,scalar_decoder,weights)
                        self.assertEqual(winners,tuple(expected['scalar_argmin']));self.assertLessEqual(set(winners),set(frontier))
                        self.assertEqual(tuple(expected['pareto_front']),frontier)
                        counts['selection_calls']+=1;counts['context_instances']+=1;counts['context_observations']+=n
                        counts['pareto_ids']+=len(frontier);counts['scalar_ids']+=len(winners)
        self.assertEqual((counts['rosters'],counts['selection_calls']),(4369,34952))
        COVERAGE.update(counts)


if __name__=='__main__':
    import json
    run=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not run.result.wasSuccessful())
