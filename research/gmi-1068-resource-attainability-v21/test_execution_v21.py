"""Registered unary/two-action corpora against literal cumulative-prefix traversal."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v21 as oracle
import core_v21 as core
import execution_v21 as execution
COVERAGE={}


class ExecutionTests(unittest.TestCase):
    def corpus(self,label,actions,outputs,costs,length,max_budget,expected):
        counts={k:0 for k in ('machines','physical_histories','budget_cases','successful_budget_runs',
            'failed_budget_runs','raw_trace_checks','lift_trace_checks','endpoint_residual_checks',
            'weighted_cut_checks','residual_cut_checks','cumulative_prefix_checks','nested_success_checks')}
        words=oracle.words(actions,length)
        for observations,rows in oracle.machines(actions,outputs,costs):
            machine=core.LegacyMachine(observations,rows)
            lifts=tuple(core.budget_lift(machine,b) for b in range(max_budget+1))
            for start in range(len(rows)):
                for word in words:
                    raw,expected_run,prefixes=oracle.execute(observations,rows,start,word)
                    self.assertEqual(execution.weighted_run(machine,start,word),expected_run)
                    self.assertEqual(core.legacy.run(machine,start,word),raw)
                    counts['physical_histories']+=1;counts['raw_trace_checks']+=1
                    for cut in range(len(word)+1):
                        first=execution.weighted_run(machine,start,word[:cut])
                        if first is None:composed=None
                        else:
                            second=execution.weighted_run(machine,first[0],word[cut:])
                            composed=None if second is None else (second[0],first[1]+second[1])
                        self.assertEqual(composed,expected_run);counts['weighted_cut_checks']+=1
                    previous=None
                    for budget,lift in enumerate(lifts):
                        trace,result,prefixes=oracle.execute(observations,rows,start,word,budget)
                        expected_endpoint=None if result is None else (result[0],budget-result[1])
                        actual=execution.budget_endpoint(machine,start,word,budget)
                        self.assertEqual(actual,expected_endpoint)
                        self.assertEqual(core.legacy.run(machine,start,word,budget=budget),trace)
                        lifted_start=start*(budget+1)+budget
                        self.assertEqual(core.legacy.run(lift,lifted_start,word),trace)
                        _,lifted,_=oracle.execute(lift.observations,lift.transitions,lifted_start,word)
                        self.assertEqual(None if lifted is None else divmod(lifted[0],budget+1),expected_endpoint)
                        if result is not None:
                            self.assertEqual(trace,raw)
                            self.assertEqual(result,expected_run)
                            self.assertLessEqual(result[1],budget)
                            counts['successful_budget_runs']+=1
                        else:counts['failed_budget_runs']+=1
                        if previous is not None:
                            self.assertEqual(actual,(previous[0],previous[1]+1))
                            counts['nested_success_checks']+=1
                        previous=actual
                        for cut in range(len(word)+1):
                            first=execution.budget_endpoint(machine,start,word[:cut],budget)
                            composed=None if first is None else execution.budget_endpoint(machine,first[0],word[cut:],first[1])
                            self.assertEqual(composed,expected_endpoint)
                            counts['residual_cut_checks']+=1
                        counts['budget_cases']+=1;counts['raw_trace_checks']+=1
                        counts['lift_trace_checks']+=1;counts['endpoint_residual_checks']+=1
                        counts['cumulative_prefix_checks']+=len(prefixes)
            counts['machines']+=1
        self.assertEqual((counts['machines'],counts['physical_histories'],counts['budget_cases']),expected)
        self.assertEqual(counts['successful_budget_runs']+counts['failed_budget_runs'],counts['budget_cases'])
        COVERAGE.update({label+'_'+k:v for k,v in counts.items()})

    def test_a_unary_costs(self):
        self.corpus('a',1,2,3,4,8,(1542,15315,137835))

    def test_b_two_actions(self):
        self.corpus('b',2,1,2,3,3,(5652,169155,676620))


if __name__=='__main__':
    import json
    r=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not r.result.wasSuccessful())
